#!/usr/bin/env python3
"""
Convert a text file to PDF
Usage: python text_to_pdf.py input.txt output.pdf
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import sys

def text_to_pdf(input_file, output_file):
    """Convert a text file to PDF with proper formatting"""
    
    # Read the text file
    with open(input_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Create PDF
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    
    # Set up formatting
    margin = 0.75 * inch
    y_position = height - margin
    line_height = 14
    max_width = width - (2 * margin)
    
    # Set font
    c.setFont("Helvetica", 10)
    
    # Split text into lines
    lines = text_content.split('\n')
    
    for line in lines:
        # Handle empty lines
        if not line.strip():
            y_position -= line_height
            if y_position < margin:
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - margin
            continue
        
        # Wrap long lines
        words = line.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if c.stringWidth(test_line, "Helvetica", 10) <= max_width:
                current_line = test_line
            else:
                # Draw the current line
                if current_line:
                    c.drawString(margin, y_position, current_line.rstrip())
                    y_position -= line_height
                    
                    if y_position < margin:
                        c.showPage()
                        c.setFont("Helvetica", 10)
                        y_position = height - margin
                
                current_line = word + " "
        
        # Draw remaining text
        if current_line:
            c.drawString(margin, y_position, current_line.rstrip())
            y_position -= line_height
            
            if y_position < margin:
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = height - margin
    
    # Save the PDF
    c.save()
    print(f"PDF created successfully: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python text_to_pdf.py input.txt output.pdf")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        text_to_pdf(input_file, output_file)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)