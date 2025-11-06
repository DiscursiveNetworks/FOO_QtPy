# PDF OCR Tools for Image-Only PDFs

A collection of Python tools to extract text from scanned/image-only PDFs using Optical Character Recognition (OCR).

## 📁 Files Included

### 1. **simple_pdf_ocr.py** - Beginner Friendly
- Simplest implementation
- Minimal dependencies
- Command-line interface
- Perfect for getting started

### 2. **pdf_ocr.py** - Advanced Features
- Multiple OCR engines (Tesseract, EasyOCR)
- Image preprocessing for better accuracy
- Multiple output formats (TXT, JSON, Markdown)
- Confidence scores
- Page-by-page processing

### 3. **batch_pdf_ocr.py** - Batch Processing
- Process multiple PDFs at once
- Parallel processing for speed
- Progress tracking
- Automatic report generation
- Skip already processed files

### 4. **pdf_ocr_gui.py** - Graphical Interface
- User-friendly GUI
- No command-line needed
- Real-time progress updates
- Language selection
- Visual feedback

### 5. **OCR_Setup_Guide.md** - Installation Guide
- Step-by-step setup instructions
- Platform-specific guidance
- Troubleshooting tips
- Performance optimization

## 🚀 Quick Start

### Basic Installation
```bash
# Install Python packages
pip install -r requirements.txt

# Install Tesseract (OS-specific - see Setup Guide)
# Ubuntu/Debian:
sudo apt install tesseract-ocr

# macOS:
brew install tesseract

# Windows: Download installer from GitHub
```

### Simple Usage
```bash
# Single PDF
python simple_pdf_ocr.py document.pdf

# With GUI
python pdf_ocr_gui.py

# Batch processing
python batch_pdf_ocr.py ./pdf_folder/
```

## 🎯 Which Tool to Use?

| Use Case | Recommended Script | Why |
|----------|-------------------|-----|
| First time user | `simple_pdf_ocr.py` | Easiest to understand |
| Single PDF, need accuracy | `pdf_ocr.py` | Advanced preprocessing |
| Many PDFs | `batch_pdf_ocr.py` | Parallel processing |
| Non-technical users | `pdf_ocr_gui.py` | No command line needed |
| Research/production | `pdf_ocr.py` | Most features & options |

## 📋 Features Comparison

| Feature | Simple | Advanced | Batch | GUI |
|---------|--------|----------|-------|-----|
| Basic OCR | ✅ | ✅ | ✅ | ✅ |
| Multiple languages | ❌ | ✅ | ✅ | ✅ |
| Image preprocessing | ❌ | ✅ | ❌ | ❌ |
| Multiple OCR engines | ❌ | ✅ | ❌ | ❌ |
| Progress tracking | ❌ | ✅ | ✅ | ✅ |
| Parallel processing | ❌ | ❌ | ✅ | ❌ |
| JSON/Markdown output | ❌ | ✅ | ❌ | ❌ |
| No command line needed | ❌ | ❌ | ❌ | ✅ |

## 💡 Examples

### Process a Spanish document with preprocessing
```bash
python pdf_ocr.py spanish_doc.pdf -l spa -o results/
```

### Batch process all PDFs in a folder
```bash
python batch_pdf_ocr.py invoices/ processed/ --workers 8
```

### Check OCR quality
```bash
python pdf_ocr.py document.pdf -f json
# Check confidence scores in the JSON output
```

## 🔧 Advanced Usage

### Using EasyOCR (better for some languages)
```bash
python pdf_ocr.py document.pdf -e easyocr
```

### Save extracted page images
```bash
python pdf_ocr.py document.pdf --save-images
```

### Process only specific pages (modify code)
```python
# In pdf_ocr.py, modify process_pdf():
for page_num, image in images[2:5]:  # Pages 3-5 only
    # ... process page
```

## 📊 Performance Tips

1. **DPI Settings**: Higher DPI (300+) = better accuracy but slower
2. **Preprocessing**: Improves accuracy by 10-20% but adds time
3. **Parallel Workers**: Set to CPU cores - 1 for optimal speed
4. **Language Models**: Install only needed languages to save space

## 🐛 Common Issues

### "No module named 'cv2'"
```bash
pip install opencv-python
```

### "Tesseract not found"
- See OCR_Setup_Guide.md for OS-specific installation

### Poor OCR results
1. Check if PDF has selectable text already (not image-only)
2. Try higher DPI: modify `dpi=300` to `dpi=600`
3. Use preprocessing: `pdf_ocr.py` instead of simple version
4. Try different language model if non-English

### Memory errors on large PDFs
- Process in batches
- Reduce DPI
- Use `pdf_ocr.py` which processes page-by-page

## 📝 Output Formats

### Text (.txt)
```
==================================================
Page 1
==================================================
Extracted text from page 1...

==================================================
Page 2
==================================================
Extracted text from page 2...
```

### JSON (.json)
```json
{
  "source_pdf": "document.pdf",
  "ocr_engine": "tesseract",
  "language": "eng",
  "pages": {
    "1": {
      "text": "Extracted text...",
      "confidence": 95.5
    }
  }
}
```

### Markdown (.md)
```markdown
# OCR Results for document.pdf

## Page 1
*Confidence: 95.5%*

Extracted text from page 1...
```

## 🌐 Language Support

Common Tesseract language codes:
- `eng` - English
- `spa` - Spanish  
- `fra` - French
- `deu` - German
- `ita` - Italian
- `por` - Portuguese
- `chi_sim` - Chinese Simplified
- `jpn` - Japanese
- `ara` - Arabic

Install languages:
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr-spa tesseract-ocr-fra

# See all available
apt search tesseract-ocr-
```

## 🤝 Contributing

Feel free to improve these tools! Some ideas:
- Add more OCR engines (Google Cloud Vision, AWS Textract)
- Implement automatic language detection
- Add PDF/A output support
- Create web interface
- Add automatic rotation detection

## 📄 License

Free to use and modify. Created for educational purposes.

## 🙏 Acknowledgments

- Tesseract OCR by Google
- pdf2image library
- PyMuPDF developers
- EasyOCR team

---

For detailed setup instructions, see **OCR_Setup_Guide.md**

For grant review OCR specifically, ensure high-quality scans (300+ DPI) and use the advanced script with preprocessing for best results.
