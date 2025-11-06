# OCR Setup Guide for Image-Only PDFs

## Quick Start

For the simplest setup, use the `simple_pdf_ocr.py` script:

```bash
# Install basic requirements
pip install pdf2image pytesseract pillow

# Run OCR
python simple_pdf_ocr.py your_document.pdf
```

## Full Installation Guide

### 1. Install Python Dependencies

```bash
# Basic requirements
pip install pdf2image pytesseract pillow opencv-python numpy

# Additional OCR engines (optional)
pip install PyMuPDF  # For better PDF handling
pip install easyocr  # Alternative OCR engine

# All at once
pip install -r requirements.txt
```

### 2. Install Tesseract OCR Engine

Tesseract is the actual OCR engine that pytesseract uses. You need to install it separately:

#### Windows
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to PATH or set path in script:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

#### macOS
```bash
# Using Homebrew
brew install tesseract

# Install additional languages
brew install tesseract-lang
```

#### Linux (Ubuntu/Debian)
```bash
# Install Tesseract
sudo apt update
sudo apt install tesseract-ocr

# Install additional languages (optional)
sudo apt install tesseract-ocr-fra  # French
sudo apt install tesseract-ocr-deu  # German
sudo apt install tesseract-ocr-spa  # Spanish
```

#### Linux (Fedora/RHEL)
```bash
sudo dnf install tesseract
sudo dnf install tesseract-langpack-*  # All languages
```

### 3. Install Poppler (for pdf2image)

pdf2image requires poppler-utils:

#### Windows
1. Download from: https://blog.alivate.com.au/poppler-windows/
2. Extract to a folder (e.g., C:\poppler)
3. Add to PATH: C:\poppler\bin

#### macOS
```bash
brew install poppler
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install poppler-utils

# Fedora/RHEL
sudo dnf install poppler-utils
```

## Usage Examples

### Simple OCR (basic script)
```bash
# Basic usage
python simple_pdf_ocr.py scan.pdf

# Specify output file
python simple_pdf_ocr.py scan.pdf extracted_text.txt
```

### Advanced OCR (full script)
```bash
# Check dependencies
python pdf_ocr.py --check-deps

# Basic usage with Tesseract
python pdf_ocr.py document.pdf

# Use EasyOCR engine
python pdf_ocr.py document.pdf -e easyocr

# Specify language (e.g., Spanish)
python pdf_ocr.py document.pdf -l spa

# Save extracted images
python pdf_ocr.py document.pdf --save-images

# Output only as JSON
python pdf_ocr.py document.pdf -f json

# Full example
python pdf_ocr.py spanish_doc.pdf -o results -e tesseract -l spa -f all --save-images
```

## Troubleshooting

### "Tesseract not found"
- Make sure Tesseract is installed
- On Windows, add to PATH or set path in script
- Test with: `tesseract --version`

### "pdf2image error"
- Install poppler-utils
- On Windows, ensure poppler/bin is in PATH

### Poor OCR quality
1. Try preprocessing options in advanced script
2. Use higher DPI (default is 300)
3. Try different OCR engine (easyocr vs tesseract)
4. Check if PDF is truly image-only (not selectable text)

### Language issues
- Install language packs for Tesseract
- Use correct language code (eng, fra, deu, spa, etc.)
- List available languages: `tesseract --list-langs`

## Tips for Better OCR Results

1. **High Quality Scans**: Use 300 DPI or higher
2. **Clean Documents**: Avoid skewed or dirty scans
3. **Consistent Lighting**: For photographed documents
4. **Simple Layouts**: Works best with single-column text
5. **Clear Fonts**: Avoid decorative or handwritten text

## Performance Considerations

- Large PDFs may take several minutes
- EasyOCR is slower but sometimes more accurate
- Preprocessing improves accuracy but increases time
- Consider processing in batches for many files

## Additional Languages

### Tesseract Language Codes
- English: eng
- Spanish: spa
- French: fra
- German: deu
- Italian: ita
- Portuguese: por
- Chinese Simplified: chi_sim
- Chinese Traditional: chi_tra
- Japanese: jpn
- Arabic: ara

### Install Multiple Languages
```bash
# Tesseract
sudo apt install tesseract-ocr-all  # All languages (large!)

# EasyOCR automatically downloads needed languages
```
