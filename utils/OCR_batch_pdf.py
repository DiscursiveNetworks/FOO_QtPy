#!/usr/bin/env python3
"""
Batch PDF OCR Processor
Process multiple PDF files in a directory
"""

import os
import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from datetime import datetime

try:
    from pdf2image import convert_from_path
    import pytesseract
    from tqdm import tqdm
except ImportError:
    print("Missing required libraries!")
    print("Install with: pip install pdf2image pytesseract tqdm")
    sys.exit(1)


def process_single_pdf(pdf_path, output_dir, language='eng'):
    """Process a single PDF file"""
    try:
        start_time = time.time()
        pdf_name = Path(pdf_path).stem
        output_file = output_dir / f"{pdf_name}_ocr.txt"
        
        # Skip if already processed
        if output_file.exists():
            return f"Skipped {pdf_path.name} (already processed)"
        
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=300)
        
        # Process each page
        all_text = []
        for i, image in enumerate(images, 1):
            text = pytesseract.image_to_string(image, lang=language)
            all_text.append(f"\n{'='*50}\nPage {i}\n{'='*50}\n{text}")
        
        # Save text
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_text))
        
        elapsed = time.time() - start_time
        return f"Processed {pdf_path.name} ({len(images)} pages) in {elapsed:.1f}s"
        
    except Exception as e:
        return f"Error processing {pdf_path.name}: {str(e)}"


def batch_process_pdfs(input_dir, output_dir, pattern="*.pdf", 
                      language='eng', max_workers=4):
    """Process multiple PDFs in parallel"""
    
    # Setup directories
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find all PDFs
    pdf_files = list(input_path.glob(pattern))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    print(f"Output directory: {output_path}")
    print(f"Using {max_workers} parallel workers")
    print("-" * 50)
    
    # Create log file
    log_file = output_path / f"ocr_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Process PDFs in parallel
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_pdf = {
            executor.submit(process_single_pdf, pdf, output_path, language): pdf
            for pdf in pdf_files
        }
        
        # Process completed jobs
        with tqdm(total=len(pdf_files), desc="Processing PDFs") as pbar:
            for future in as_completed(future_to_pdf):
                pdf = future_to_pdf[future]
                result = future.result()
                results.append(result)
                print(result)
                pbar.update(1)
    
    # Save log
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"OCR Batch Processing Log\n")
        f.write(f"{'='*50}\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Input Directory: {input_path}\n")
        f.write(f"Output Directory: {output_path}\n")
        f.write(f"Total Files: {len(pdf_files)}\n")
        f.write(f"Language: {language}\n")
        f.write(f"{'='*50}\n\n")
        
        for result in results:
            f.write(f"{result}\n")
    
    print(f"\nProcessing complete! Log saved to {log_file}")


def create_report(output_dir):
    """Create a summary report of all OCR results"""
    output_path = Path(output_dir)
    txt_files = list(output_path.glob("*_ocr.txt"))
    
    if not txt_files:
        print("No OCR text files found")
        return
    
    report_file = output_path / f"ocr_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_file, 'w', encoding='utf-8') as report:
        report.write("# OCR Processing Summary\n\n")
        report.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"**Total Files**: {len(txt_files)}\n\n")
        
        for txt_file in sorted(txt_files):
            report.write(f"## {txt_file.stem}\n\n")
            
            # Get file info
            size = txt_file.stat().st_size
            report.write(f"- **File Size**: {size:,} bytes\n")
            
            # Count words and lines
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                words = len(content.split())
                lines = len(content.splitlines())
                
            report.write(f"- **Words**: {words:,}\n")
            report.write(f"- **Lines**: {lines:,}\n")
            
            # Extract first few lines
            first_lines = '\n'.join(content.splitlines()[:5])
            if first_lines.strip():
                report.write(f"\n**Preview**:\n```\n{first_lines}\n...\n```\n\n")
            
            report.write("---\n\n")
    
    print(f"Summary report saved to {report_file}")


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Batch PDF OCR Processor")
        print("="*50)
        print("\nUsage:")
        print("  python batch_pdf_ocr.py <input_dir> [output_dir] [options]")
        print("\nExamples:")
        print("  python batch_pdf_ocr.py ./pdfs")
        print("  python batch_pdf_ocr.py ./pdfs ./output")
        print("  python batch_pdf_ocr.py ./pdfs ./output --workers 8")
        print("  python batch_pdf_ocr.py ./pdfs ./output --lang spa")
        print("  python batch_pdf_ocr.py ./pdfs ./output --report")
        print("\nOptions:")
        print("  --workers N   : Number of parallel workers (default: 4)")
        print("  --lang CODE   : Language code (default: eng)")
        print("  --pattern PAT : File pattern (default: *.pdf)")
        print("  --report      : Generate summary report after processing")
        return
    
    # Parse arguments
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "./ocr_output"
    
    # Default options
    workers = 4
    language = 'eng'
    pattern = "*.pdf"
    create_report_flag = False
    
    # Parse options
    i = 2 if output_dir == sys.argv[2] else 1
    while i < len(sys.argv) - 1:
        if sys.argv[i] == '--workers' and i + 1 < len(sys.argv):
            workers = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--lang' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--pattern' and i + 1 < len(sys.argv):
            pattern = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--report':
            create_report_flag = True
            i += 1
        else:
            i += 1
    
    # Check if input directory exists
    if not Path(input_dir).is_dir():
        print(f"Error: Directory not found: {input_dir}")
        return
    
    # Process PDFs
    batch_process_pdfs(input_dir, output_dir, pattern, language, workers)
    
    # Create report if requested
    if create_report_flag:
        create_report(output_dir)


if __name__ == "__main__":
    main()
