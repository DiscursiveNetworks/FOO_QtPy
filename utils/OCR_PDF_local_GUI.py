#!/usr/bin/env python3
"""
PDF OCR GUI - Graphical Interface for PDF OCR
Simple GUI for converting image-only PDFs to text
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
import sys

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Missing Dependencies", 
                        "Required libraries not found!\n\n"
                        "Please install:\n"
                        "pip install pdf2image pytesseract pillow")
    sys.exit(1)


class PDFOCRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF OCR Converter")
        self.root.geometry("600x500")
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.language = tk.StringVar(value="eng")
        self.processing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create GUI elements"""
        # Title
        title_label = tk.Label(self.root, text="PDF to Text OCR Converter", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # PDF Selection Frame
        pdf_frame = tk.LabelFrame(self.root, text="Select PDF File", padx=10, pady=10)
        pdf_frame.pack(fill="x", padx=20, pady=10)
        
        self.pdf_label = tk.Label(pdf_frame, textvariable=self.pdf_path, 
                                 anchor="w", relief="sunken")
        self.pdf_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(pdf_frame, text="Browse", 
                 command=self.select_pdf).pack(side="right")
        
        # Output Frame
        output_frame = tk.LabelFrame(self.root, text="Output File", padx=10, pady=10)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        self.output_label = tk.Label(output_frame, textvariable=self.output_path,
                                    anchor="w", relief="sunken")
        self.output_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(output_frame, text="Browse",
                 command=self.select_output).pack(side="right")
        
        # Options Frame
        options_frame = tk.LabelFrame(self.root, text="Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(options_frame, text="Language:").pack(side="left", padx=(0, 10))
        
        languages = ["eng", "spa", "fra", "deu", "ita", "por", "chi_sim", "jpn"]
        self.lang_combo = ttk.Combobox(options_frame, textvariable=self.language,
                                       values=languages, width=10)
        self.lang_combo.pack(side="left")
        
        # Progress Frame
        progress_frame = tk.LabelFrame(self.root, text="Progress", padx=10, pady=10)
        progress_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Status Text
        self.status_text = tk.Text(progress_frame, height=10, wrap="word")
        self.status_text.pack(fill="both", expand=True)
        
        # Scrollbar for status text
        scrollbar = tk.Scrollbar(self.status_text)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)
        
        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.process_btn = tk.Button(button_frame, text="Start OCR", 
                                    command=self.start_ocr, width=15,
                                    bg="#4CAF50", fg="white", font=("Arial", 12))
        self.process_btn.pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Clear", command=self.clear_all,
                 width=15).pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Exit", command=self.root.quit,
                 width=15).pack(side="left", padx=5)
        
    def select_pdf(self):
        """Select PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            # Auto-set output filename
            output = str(Path(filename).with_suffix('')) + "_ocr.txt"
            self.output_path.set(output)
            
    def select_output(self):
        """Select output file"""
        filename = filedialog.asksaveasfilename(
            title="Save OCR Text As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
            
    def log_message(self, message):
        """Add message to status text"""
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.root.update()
        
    def clear_all(self):
        """Clear all fields"""
        self.pdf_path.set("")
        self.output_path.set("")
        self.status_text.delete(1.0, tk.END)
        
    def start_ocr(self):
        """Start OCR process in separate thread"""
        if not self.pdf_path.get():
            messagebox.showwarning("No PDF Selected", 
                                 "Please select a PDF file first!")
            return
            
        if not self.output_path.get():
            messagebox.showwarning("No Output File", 
                                 "Please specify an output file!")
            return
            
        if self.processing:
            messagebox.showinfo("Processing", 
                              "OCR is already in progress!")
            return
            
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_ocr)
        thread.start()
        
    def process_ocr(self):
        """Process OCR (runs in separate thread)"""
        self.processing = True
        self.process_btn.config(state="disabled")
        self.progress_bar.start()
        
        try:
            pdf_file = self.pdf_path.get()
            output_file = self.output_path.get()
            language = self.language.get()
            
            self.log_message(f"Starting OCR process...")
            self.log_message(f"PDF: {Path(pdf_file).name}")
            self.log_message(f"Language: {language}")
            
            # Convert PDF to images
            self.log_message("Converting PDF to images...")
            images = convert_from_path(pdf_file, dpi=300)
            self.log_message(f"Found {len(images)} pages")
            
            # Process each page
            all_text = []
            for i, image in enumerate(images, 1):
                self.log_message(f"Processing page {i}/{len(images)}...")
                
                # Perform OCR
                text = pytesseract.image_to_string(image, lang=language)
                
                # Add to results
                all_text.append(f"\n{'='*50}")
                all_text.append(f"Page {i}")
                all_text.append(f"{'='*50}\n")
                all_text.append(text)
                
            # Save results
            self.log_message("Saving results...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(all_text))
                
            self.log_message(f"Success! Saved to: {output_file}")
            messagebox.showinfo("Success", 
                              f"OCR completed successfully!\n\n"
                              f"Text saved to:\n{output_file}")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"OCR failed:\n\n{str(e)}")
            
        finally:
            self.processing = False
            self.process_btn.config(state="normal")
            self.progress_bar.stop()
            
            
def check_tesseract():
    """Check if Tesseract is installed"""
    try:
        pytesseract.get_tesseract_version()
        return True
    except:
        return False


def main():
    """Main function"""
    root = tk.Tk()
    
    # Check Tesseract installation
    if not check_tesseract():
        messagebox.showwarning(
            "Tesseract Not Found",
            "Tesseract OCR engine not found!\n\n"
            "Please install Tesseract:\n"
            "- Windows: Download from GitHub\n"
            "- Mac: brew install tesseract\n"
            "- Linux: apt install tesseract-ocr"
        )
    
    app = PDFOCRGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
