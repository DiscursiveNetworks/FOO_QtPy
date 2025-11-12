#!/usr/bin/env python3
"""
PDF OCR Tool for Image-Only PDFs
Supports multiple OCR engines and output formats
"""

import os
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# PDF handling
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

# OCR engines
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# Additional imports
import numpy as np
import cv2


class PDFOCRProcessor:
    """Main class for processing image-only PDFs with OCR"""
    
    def __init__(self, pdf_path, output_dir="output", ocr_engine="tesseract", language="eng"):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.ocr_engine = ocr_engine
        self.language = language
        self.extracted_text = {}
        
        # Initialize OCR engine
        if ocr_engine == "easyocr" and EASYOCR_AVAILABLE:
            self.reader = easyocr.Reader([language])
        
    def extract_images_pymupdf(self):
        """Extract images from PDF using PyMuPDF"""
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF not installed. Install with: pip install PyMuPDF")
        
        images = []
        pdf_document = fitz.open(self.pdf_path)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            # Get the page as an image
            mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.pil_tobytes(format="PNG")
            img = Image.open(io.BytesIO(img_data))
            images.append((page_num + 1, img))
            
        pdf_document.close()
        return images
    
    def extract_images_pdf2image(self, dpi=300):
        """Extract images from PDF using pdf2image"""
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError("pdf2image not installed. Install with: pip install pdf2image")
        
        images = convert_from_path(self.pdf_path, dpi=dpi)
        return [(i+1, img) for i, img in enumerate(images)]
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert PIL Image to numpy array
        if isinstance(image, Image.Image):
            img = np.array(image)
        else:
            img = image
        
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        # Apply thresholding to get better OCR results
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Deskew image
        coords = np.column_stack(np.where(denoised > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Rotate image
            if abs(angle) > 0.5:
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h),
                                         flags=cv2.INTER_CUBIC,
                                         borderMode=cv2.BORDER_REPLICATE)
        
        return denoised
    
    def ocr_with_tesseract(self, image, page_num):
        """Perform OCR using Tesseract"""
        if not TESSERACT_AVAILABLE:
            raise ImportError("pytesseract not installed. Install with: pip install pytesseract")
        
        # Preprocess image
        processed_img = self.preprocess_image(image)
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6'
        
        # Perform OCR
        text = pytesseract.image_to_string(processed_img, 
                                         lang=self.language, 
                                         config=custom_config)
        
        # Also get detailed data
        data = pytesseract.image_to_data(processed_img, 
                                        output_type=pytesseract.Output.DICT,
                                        lang=self.language,
                                        config=custom_config)
        
        # Calculate confidence
        confidences = [float(conf) for conf in data['conf'] if float(conf) > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'text': text,
            'confidence': avg_confidence,
            'details': data
        }
    
    def ocr_with_easyocr(self, image, page_num):
        """Perform OCR using EasyOCR"""
        if not EASYOCR_AVAILABLE:
            raise ImportError("easyocr not installed. Install with: pip install easyocr")
        
        # Convert PIL Image to numpy array if needed
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        # Perform OCR
        results = self.reader.readtext(img_array)
        
        # Extract text and calculate confidence
        text_parts = []
        confidences = []
        
        for (bbox, text, prob) in results:
            text_parts.append(text)
            confidences.append(prob)
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'text': full_text,
            'confidence': avg_confidence,
            'details': results
        }
    
    def process_pdf(self, use_preprocessing=True, save_images=False):
        """Main method to process the entire PDF"""
        print(f"Processing PDF: {self.pdf_path}")
        print(f"Using OCR engine: {self.ocr_engine}")
        
        # Extract images from PDF
        try:
            if PYMUPDF_AVAILABLE:
                images = self.extract_images_pymupdf()
            else:
                images = self.extract_images_pdf2image()
        except Exception as e:
            print(f"Error extracting images: {e}")
            return None
        
        print(f"Extracted {len(images)} pages")
        
        # Process each page
        for page_num, image in images:
            print(f"\nProcessing page {page_num}/{len(images)}...")
            
            # Save image if requested
            if save_images:
                image_path = self.output_dir / f"page_{page_num:03d}.png"
                image.save(image_path)
            
            # Perform OCR
            try:
                if self.ocr_engine == "tesseract":
                    result = self.ocr_with_tesseract(image, page_num)
                elif self.ocr_engine == "easyocr":
                    result = self.ocr_with_easyocr(image, page_num)
                else:
                    raise ValueError(f"Unknown OCR engine: {self.ocr_engine}")
                
                self.extracted_text[page_num] = result
                print(f"Page {page_num} - Confidence: {result['confidence']:.2f}%")
                
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                self.extracted_text[page_num] = {
                    'text': '',
                    'confidence': 0,
                    'error': str(e)
                }
        
        return self.extracted_text
    
    def save_results(self, format="all"):
        """Save OCR results in various formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{self.pdf_path.stem}_ocr_{timestamp}"
        
        # Save as plain text
        if format in ["text", "all"]:
            text_path = self.output_dir / f"{base_name}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                for page_num in sorted(self.extracted_text.keys()):
                    f.write(f"\n{'='*60}\n")
                    f.write(f"Page {page_num}\n")
                    f.write(f"{'='*60}\n")
                    f.write(self.extracted_text[page_num]['text'])
                    f.write("\n")
            print(f"Saved text to: {text_path}")
        
        # Save as JSON with metadata
        if format in ["json", "all"]:
            json_path = self.output_dir / f"{base_name}.json"
            json_data = {
                'source_pdf': str(self.pdf_path),
                'ocr_engine': self.ocr_engine,
                'language': self.language,
                'timestamp': timestamp,
                'pages': {}
            }
            
            for page_num, data in self.extracted_text.items():
                json_data['pages'][page_num] = {
                    'text': data['text'],
                    'confidence': data['confidence']
                }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            print(f"Saved JSON to: {json_path}")
        
        # Save as Markdown
        if format in ["markdown", "all"]:
            md_path = self.output_dir / f"{base_name}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# OCR Results for {self.pdf_path.name}\n\n")
                f.write(f"- **OCR Engine**: {self.ocr_engine}\n")
                f.write(f"- **Language**: {self.language}\n")
                f.write(f"- **Processed**: {timestamp}\n\n")
                
                for page_num in sorted(self.extracted_text.keys()):
                    data = self.extracted_text[page_num]
                    f.write(f"\n## Page {page_num}\n\n")
                    f.write(f"*Confidence: {data['confidence']:.2f}%*\n\n")
                    f.write(data['text'])
                    f.write("\n\n---\n")
            print(f"Saved Markdown to: {md_path}")


def check_dependencies():
    """Check and report available dependencies"""
    print("Checking dependencies...")
    print(f"PyMuPDF (fitz): {'✓' if PYMUPDF_AVAILABLE else '✗'}")
    print(f"pdf2image: {'✓' if PDF2IMAGE_AVAILABLE else '✗'}")
    print(f"Tesseract: {'✓' if TESSERACT_AVAILABLE else '✗'}")
    print(f"EasyOCR: {'✓' if EASYOCR_AVAILABLE else '✗'}")
    
    if TESSERACT_AVAILABLE:
        try:
            langs = pytesseract.get_languages()
            print(f"Tesseract languages: {', '.join(langs[:5])}{'...' if len(langs) > 5 else ''}")
        except:
            print("Tesseract installed but not configured properly")
    
    print()


def main():
    parser = argparse.ArgumentParser(description="OCR for image-only PDFs")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    parser.add_argument("-e", "--engine", choices=["tesseract", "easyocr"], 
                       default="tesseract", help="OCR engine to use")
    parser.add_argument("-l", "--language", default="eng", 
                       help="Language for OCR (e.g., eng, fra, deu)")
    parser.add_argument("-f", "--format", choices=["text", "json", "markdown", "all"],
                       default="all", help="Output format")
    parser.add_argument("--save-images", action="store_true", 
                       help="Save extracted page images")
    parser.add_argument("--check-deps", action="store_true",
                       help="Check dependencies and exit")
    
    args = parser.parse_args()
    
    if args.check_deps:
        check_dependencies()
        return
    
    # Check if file exists
    if not Path(args.pdf_path).exists():
        print(f"Error: File not found: {args.pdf_path}")
        return
    
    # Process PDF
    processor = PDFOCRProcessor(
        args.pdf_path,
        output_dir=args.output,
        ocr_engine=args.engine,
        language=args.language
    )
    
    results = processor.process_pdf(save_images=args.save_images)
    
    if results:
        processor.save_results(format=args.format)
        print("\nOCR processing completed!")
    else:
        print("\nOCR processing failed!")


if __name__ == "__main__":
    # Add missing import
    import io
    main()
