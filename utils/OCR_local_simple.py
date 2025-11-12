#!/usr/bin/env python3
"""
Simple PDF OCR Tool - Beginner Friendly Version
Converts image-only PDFs to text using OCR
"""

import sys
from pathlib import Path

# Try to import required libraries
try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
except ImportError as e:
    print("Missing required libraries!")
    print("Please install them using:")
    print("pip install pdf2image pytesseract pillow")
    sys.exit(1)


def pdf_to_text(pdf_path, output_file="output.txt"):
    """
    Convert a PDF with images to text file
    
    Args:
        pdf_path: Path to the PDF file
        output_file: Name of the output text file
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Convert PDF pages to images
    print("Converting PDF pages to images...")
    try:
        # Convert PDF to list of images
        images = convert_from_path(pdf_path, dpi=300)
        print(f"Found {len(images)} pages")
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return False
    
    # Process each page
    all_text = []
    for i, image in enumerate(images, 1):
        print(f"Processing page {i}/{len(images)}...")
        
        try:
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            
            # Add page header and text
            all_text.append(f"\n{'='*50}")
            all_text.append(f"Page {i}")
            all_text.append(f"{'='*50}\n")
            all_text.append(text)
            
        except Exception as e:
            print(f"Error processing page {i}: {e}")
            all_text.append(f"\n[Error processing page {i}]\n")
    
    # Save all text to file
    print(f"\nSaving text to {output_file}...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_text))
        print(f"Success! Text saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def main():
    """Main function to handle command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python simple_pdf_ocr.py <pdf_file> [output_file]")
        print("Example: python simple_pdf_ocr.py document.pdf output.txt")
        return
    
    pdf_path = sys.argv[1]
    
    # Check if PDF exists
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        return
    
    # Get output filename (optional)
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        # Use PDF name for output
        output_file = Path(pdf_path).stem + "_ocr.txt"
    
    # Process the PDF
    pdf_to_text(pdf_path, output_file)


if __name__ == "__main__":
    main()
