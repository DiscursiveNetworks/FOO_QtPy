#!/usr/bin/env python3
"""
Grant Proposal OCR Tool
Optimized for NIH and other grant proposals
Handles multi-column layouts, headers, and special formatting
"""

import os
import sys
import re
from pathlib import Path
import json
from datetime import datetime

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
except ImportError:
    print("Missing required libraries!")
    print("Install with: pip install pdf2image pytesseract opencv-python numpy pillow")
    sys.exit(1)


class GrantProposalOCR:
    """Specialized OCR for grant proposals"""
    
    # Common grant proposal sections
    SECTION_PATTERNS = {
        'specific_aims': r'(?i)specific\s*aims?',
        'significance': r'(?i)significance',
        'innovation': r'(?i)innovation',
        'approach': r'(?i)approach',
        'research_strategy': r'(?i)research\s*strategy',
        'background': r'(?i)background',
        'preliminary_data': r'(?i)preliminary\s*(data|studies|results)',
        'methods': r'(?i)methods',
        'bibliography': r'(?i)(bibliography|references|literature\s*cited)',
        'budget': r'(?i)budget',
        'personnel': r'(?i)personnel',
        'facilities': r'(?i)facilities'
    }
    
    def __init__(self, pdf_path, output_dir="output"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.sections = {}
        self.metadata = {
            'filename': self.pdf_path.name,
            'processed_date': datetime.now().isoformat(),
            'sections_found': []
        }
        
    def preprocess_grant_image(self, image):
        """Specialized preprocessing for grant documents"""
        # Convert PIL to numpy array
        if isinstance(image, Image.Image):
            img = np.array(image)
        else:
            img = image
            
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
            
        # Remove noise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding for better text recognition
        thresh = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Detect and fix skew
        coords = np.column_stack(np.where(thresh < 255))
        if len(coords) > 100:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            if abs(angle) > 0.5 and abs(angle) < 10:  # Only fix small skews
                (h, w) = thresh.shape
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                thresh = cv2.warpAffine(
                    thresh, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(thresh)
        
        return enhanced
    
    def detect_sections(self, text):
        """Detect grant proposal sections in text"""
        found_sections = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Check each section pattern
            for section_key, pattern in self.SECTION_PATTERNS.items():
                if re.match(pattern, line_clean) and len(line_clean) < 50:
                    found_sections.append({
                        'section': section_key,
                        'line': i,
                        'title': line_clean
                    })
                    
        return found_sections
    
    def extract_page_structure(self, image):
        """Extract structured information from a page"""
        # Preprocess
        processed = self.preprocess_grant_image(image)
        
        # Get detailed OCR data
        custom_config = r'--oem 3 --psm 3'  # Automatic page segmentation
        data = pytesseract.image_to_data(
            processed, 
            output_type=pytesseract.Output.DICT,
            config=custom_config
        )
        
        # Extract text with position information
        n_boxes = len(data['text'])
        structured_text = []
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 30:  # Confidence threshold
                text = data['text'][i].strip()
                if text:
                    structured_text.append({
                        'text': text,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': data['conf'][i]
                    })
        
        return structured_text
    
    def process_grant_proposal(self):
        """Process the grant proposal with section detection"""
        print(f"Processing grant proposal: {self.pdf_path.name}")
        
        # Convert PDF to images
        print("Converting PDF to images...")
        images = convert_from_path(self.pdf_path, dpi=300)
        print(f"Found {len(images)} pages")
        
        all_text = []
        current_section = "preamble"
        self.sections[current_section] = []
        
        # Process each page
        for page_num, image in enumerate(images, 1):
            print(f"Processing page {page_num}/{len(images)}...")
            
            # Preprocess and OCR
            processed_img = self.preprocess_grant_image(image)
            text = pytesseract.image_to_string(processed_img, config='--psm 6')
            
            # Detect sections
            found_sections = self.detect_sections(text)
            
            # Update current section if new section found
            if found_sections:
                for section_info in found_sections:
                    current_section = section_info['section']
                    if current_section not in self.sections:
                        self.sections[current_section] = []
                        self.metadata['sections_found'].append(current_section)
                    print(f"  Found section: {section_info['title']}")
            
            # Add page text to current section
            self.sections[current_section].append({
                'page': page_num,
                'text': text
            })
            
            # Also keep full text
            all_text.append(f"\n{'='*60}")
            all_text.append(f"Page {page_num}")
            if current_section != "preamble":
                all_text.append(f"Section: {current_section.replace('_', ' ').title()}")
            all_text.append(f"{'='*60}\n")
            all_text.append(text)
        
        # Save results
        self.save_results(all_text)
        
        return self.sections
    
    def save_results(self, all_text):
        """Save OCR results in multiple formats"""
        base_name = self.pdf_path.stem
        
        # Save full text
        text_file = self.output_dir / f"{base_name}_full.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_text))
        print(f"\nSaved full text to: {text_file}")
        
        # Save structured sections
        sections_file = self.output_dir / f"{base_name}_sections.json"
        sections_data = {
            'metadata': self.metadata,
            'sections': {}
        }
        
        for section_name, pages in self.sections.items():
            sections_data['sections'][section_name] = {
                'page_count': len(pages),
                'pages': pages
            }
        
        with open(sections_file, 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
        print(f"Saved structured sections to: {sections_file}")
        
        # Save individual section files
        sections_dir = self.output_dir / f"{base_name}_sections"
        sections_dir.mkdir(exist_ok=True)
        
        for section_name, pages in self.sections.items():
            if pages:  # Skip empty sections
                section_file = sections_dir / f"{section_name}.txt"
                with open(section_file, 'w', encoding='utf-8') as f:
                    f.write(f"SECTION: {section_name.replace('_', ' ').upper()}\n")
                    f.write(f"{'='*60}\n\n")
                    for page_data in pages:
                        f.write(f"\n[Page {page_data['page']}]\n")
                        f.write(page_data['text'])
                        f.write("\n")
                        
        print(f"Saved individual sections to: {sections_dir}")
        
        # Save summary report
        report_file = self.output_dir / f"{base_name}_summary.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Grant Proposal OCR Summary\n\n")
            f.write(f"**File**: {self.pdf_path.name}\n")
            f.write(f"**Date**: {self.metadata['processed_date']}\n")
            f.write(f"**Total Pages**: {len(all_text) // 4}\n\n")  # Rough estimate
            
            f.write("## Sections Found\n\n")
            for section in self.metadata['sections_found']:
                page_count = len(self.sections[section])
                f.write(f"- **{section.replace('_', ' ').title()}**: {page_count} pages\n")
            
            f.write("\n## Section Details\n\n")
            for section_name, pages in self.sections.items():
                if pages:
                    f.write(f"### {section_name.replace('_', ' ').title()}\n")
                    f.write(f"Pages: {', '.join(str(p['page']) for p in pages)}\n")
                    
                    # First few words of section
                    first_text = pages[0]['text'][:200].replace('\n', ' ')
                    f.write(f"Preview: {first_text}...\n\n")
                    
        print(f"Saved summary report to: {report_file}")
        
    def extract_specific_aims_only(self):
        """Extract only the Specific Aims section (usually most important)"""
        if 'specific_aims' in self.sections:
            aims_file = self.output_dir / f"{self.pdf_path.stem}_specific_aims_only.txt"
            with open(aims_file, 'w', encoding='utf-8') as f:
                f.write("SPECIFIC AIMS\n")
                f.write("="*60 + "\n\n")
                for page_data in self.sections['specific_aims']:
                    f.write(page_data['text'])
                    f.write("\n")
            print(f"Saved Specific Aims to: {aims_file}")
            return True
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Grant Proposal OCR Tool")
        print("="*50)
        print("\nUsage:")
        print("  python grant_ocr.py <pdf_file> [output_dir]")
        print("\nExample:")
        print("  python grant_ocr.py R01_proposal.pdf ./output")
        print("\nFeatures:")
        print("  - Automatic section detection")
        print("  - Structured output by section")
        print("  - Optimized for grant proposal layouts")
        print("  - Specific Aims extraction")
        return
    
    pdf_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "grant_ocr_output"
    
    # Check file exists
    if not Path(pdf_file).exists():
        print(f"Error: File not found: {pdf_file}")
        return
    
    # Process grant proposal
    processor = GrantProposalOCR(pdf_file, output_dir)
    sections = processor.process_grant_proposal()
    
    # Try to extract Specific Aims separately
    processor.extract_specific_aims_only()
    
    print("\nOCR processing complete!")
    print(f"Found {len(processor.metadata['sections_found'])} sections")
    
    # Provide grant_review.py compatible output
    review_file = Path(output_dir) / f"{Path(pdf_file).stem}_for_review.txt"
    print(f"\nFor grant_review.py, use: {review_file}")


if __name__ == "__main__":
    # Example:
    # python grant_ocr.py ..\grants\raw\prince_k99_app.pdf ..\grants\processed
    main()
