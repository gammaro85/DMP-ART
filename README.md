# DMP ART - Data Management Plan Assessment and Response Tool
<img width="8534" height="4572" alt="dmp-art-logo-main-dark" src="https://github.com/user-attachments/assets/c0d95fcd-9a2a-42a0-b9b0-9538fe7d49b8" />


**DMP ART** - Twój inteligentny asystent do oceny Planów Zarządzania Danymi (DMP) w wnioskach NCN.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![Version](https://img.shields.io/badge/version-0.8.1-brightgreen.svg)](https://github.com/gammaro85/DMP-ART)
[![Success Rate](https://img.shields.io/badge/success_rate-94.1%25-success)](FINAL_TEST_RESULTS.md)
[![OCR](https://img.shields.io/badge/OCR-supported-blue)](INSTALLATION.md#ocr-setup)

## Dla Data Stewardów 🎯

Jesteś data stewardem oceniającym DMP naukowców? DMP-ART oszczędza **75% czasu** i podnosi jakość recenzji:

### Twój Workflow

```
📥 Wgrywasz wniosek NCN (PDF/DOCX)
    ↓ 5-30 sekund
📄 System wyciąga DMP i dzieli na 14 sekcji
    ↓ 20-30 minut recenzji
✅ Klikasz gotowe komentarze + piszesz unikalne uwagi
    ↓ 5 minut
📊 Kompilujesz recenzję → automatyczny eksport
    ↓
💾 Pliki zapisane: outputs/DMP_*.docx + feedback/feedback_*.txt
```

**Zamiast 2h/wniosek → tylko 30min/wniosek** ⚡

### Co Wyróżnia DMP-ART?

✅ **Automatyczna ekstrakcja** - System znajduje DMP w 80-stronicowym wniosku
✅ **94.1% sukcesu** - Przetwarza nawet skanowane PDF (OCR)
✅ **Gotowe komentarze** - Kategorie dla typowych przypadków (Ready, Missing, Concerns)
✅ **Pełna konfiguracja** - Dostosuj strukturę DMP i komentarze do swoich potrzeb
✅ **Estetyczny UI** - Spójny ciemny motyw, nowoczesny design
✅ **Powiązane pliki** - DMP i recenzja automatycznie nazwane i pogrupowane

📖 **[Pełny przewodnik dla Data Stewardów →](USER_GUIDE_DATA_STEWARD.md)**

---

## Purpose

This tool supports **data stewards**, research administrators, and grant officers at Polish institutions by:

- **Automated Extraction**: Intelligently extracts DMP section from full grant proposals (PDF/DOCX)
- **Smart Structuring**: Divides content into 14 Science Europe DMP elements (1.1-6.2)
- **One-Click Comments**: Pre-configured feedback templates for common review scenarios
- **Custom Feedback**: Mix ready-made comments with unique, situation-specific remarks
- **Full Customization**: Configure DMP structure and comment library per element
- **Organized Export**: Linked DMP files and reviews in separate, organized folders
- **75% Time Savings**: From 2 hours to 30 minutes per proposal

## Key Features

### Document Processing

- **Multi-format Support**: PDF and DOCX files (up to 16MB)
- **OCR Support**: Automatic processing of scanned PDFs with Tesseract (100% success rate on scans)
- **94.1% Success Rate**: Tested on 17 real-world NCN proposals
- **Bilingual Support**: Polish and English DMPs with automatic detection
- **Table Extraction**: Advanced table content recognition
- **Section Recognition**: Automatic DMP section identification (1.1-6.2)
- **Smart Fallback**: 4-tier detection strategy for non-standard formats

### Review Interface - Your Daily Tool

- **Section-by-Section Review**: Navigate through 14 DMP elements (1.1-6.2)
- **Quick Comments Sidebar**: One-click insertion of pre-configured feedback
- **Category System**: Multiple feedback categories (Ready, Missing, Concerns, Custom)
- **Per-Element Configuration**: Different comment sets for each of 14 sections
- **Text Citations**: Select and cite problematic fragments from researcher's text
- **Character Counter**: Track feedback length and word count
- **Auto-Save**: Never lose your progress (saves every 30 seconds)
- **Visual Progress**: See which sections have feedback at a glance

### Template Editor - Full Customization

- **DMP Structure Editor**: Configure all 14 section questions
- **Quick Comments Library**: Create reusable comment templates
- **Dynamic Categories**: Create unlimited custom feedback categories
- **Per-Element Comments**: Customize feedback options for each section independently
- **Real-time Updates**: Changes immediately available in review interface
- **Import/Export**: Share configurations between institutions

### Export & File Organization

- **Linked Files**: DMP and review automatically named and paired
- **Dual Folders**: `outputs/` for DMPs, `feedback/` for reviews
- **Smart Naming**: `DMP_Surname_I_Competition_Edition_Date.docx`
- **Feedback Compilation**: Generate comprehensive review reports
- **Multiple Formats**: TXT export (DOCX/PDF coming soon)
- **Progress Saving**: Save and resume review sessions anytime

### User Experience - Modern & Aesthetic

- **Dark Theme**: Elegant, eye-friendly dark mode by default
- **Light Theme**: Switch to light mode with one click
- **Consistent Design**: Unified color scheme across all pages
- **Responsive Layout**: Works on desktop, tablet, mobile
- **Fixed Sidebar**: Quick comments always visible while reviewing
- **Smooth Animations**: Professional transitions and interactions
- **Keyboard Shortcuts**: Navigate faster with hotkeys

## Technical Stack

### Backend

- **Python 3.8+**: Core application logic
- **Flask 3.1.0**: Web framework
- **PyPDF2 3.0.1**: PDF processing
- **python-docx 1.1.2**: DOCX processing
- **Werkzeug 3.1.3**: WSGI utilities
- **Pillow 11.0.0**: Image processing
- **pytesseract** (optional): OCR engine interface
- **pdf2image** (optional): PDF to image conversion for OCR
- **Tesseract OCR 5.3+** (optional): OCR engine with Polish and English support

### Frontend

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid/Flexbox
- **JavaScript ES6+**: Interactive functionality
- **Responsive Design**: Mobile-first approach

### Data Storage

- **JSON**: Configuration files, templates, and data storage
- **Local File System**: Uploaded documents and generated reports
- **In-Memory Processing**: Real-time document analysis
- **Cache System**: Extracted content caching with unique identifiers

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- 512MB RAM minimum (1GB+ recommended)
- Internet connection for Font Awesome icons

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-repo/dmp-art.git
   cd dmp-art
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install OCR support** (optional but recommended for scanned PDFs)

   **Linux/Ubuntu:**
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng poppler-utils
   pip install pytesseract pdf2image
   ```

   **macOS:**
   ```bash
   brew install tesseract tesseract-lang poppler
   pip install pytesseract pdf2image
   ```

   **Windows:** See [INSTALLATION.md](INSTALLATION.md#ocr-setup) for detailed instructions.

   **Verify OCR:**
   ```bash
   tesseract --version  # Should show version 5.3+
   ```

4. **Verify configuration files**

   ```bash
   ls config/  # Should show JSON configuration files
   ```

5. **Create necessary directories**

   ```bash
   mkdir -p uploads outputs
   ```

6. **Start the application**

   ```bash
   python app.py
   ```

7. **Access the application**
   ```
   Open your browser and navigate to: http://localhost:5000
   ```

**For detailed installation including OCR setup, troubleshooting, and verification, see [INSTALLATION.md](INSTALLATION.md).**

## Usage Guide

### Step 1: Upload Document

- Drag & drop or click to select your NCN grant proposal file
- Supported formats: PDF, DOCX (max 16MB)
- Wait for processing completion (usually 10-30 seconds)

### Step 2: Review Extracted Content

- Check extracted sections (1.1, 1.2, 2.1, etc.)
- Review identified key phrases and tags
- Note any extraction issues in "Unconnected Text"

### Step 3: Customize Templates (Optional)

- Click "Template Editor" to configure feedback templates
- Edit DMP structure, quick comments, and categories
- Create custom feedback categories as needed

### Step 4: Provide Feedback

- Navigate between sections using quick navigation
- Select appropriate feedback category
- Use quick comments from sidebar
- Add custom feedback text as needed

### Step 5: Generate Report

- Click "Compile Feedback Report" when complete
- Review the generated summary
- Export in preferred format (TXT, HTML)
- Download for submission

## Project Structure

```
dmp-extractor/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── README.md                 # This file
├── config/                   # Configuration files
│   ├── dmp_structure.json   # DMP section definitions
│   ├── quick_comments.json  # Quick comment templates
│   └── *.json              # Category-specific templates
├── templates/               # HTML templates
│   ├── index.html          # Main upload page
│   ├── review.html         # Review interface
│   ├── template_editor.html # Template management
│   └── documentation.html  # Documentation page
├── static/                  # Static assets
│   ├── css/style.css       # Main stylesheet
│   ├── js/dark-mode.js     # Theme functionality
│   └── images/             # Logos and icons
├── utils/                   # Core processing modules
│   ├── extractor.py        # Document processing logic
│   └── dmp_comments.py     # Comment management
├── uploads/                 # Temporary upload storage
└── outputs/                 # Generated reports and cache
```

## Configuration

### DMP Structure

Edit `config/dmp_structure.json` to customize:

- Section hierarchy (1, 1.1, 1.2, 2, 2.1, etc.)
- Section questions and descriptions
- Bilingual content mapping

### Quick Comments

Edit `config/quick_comments.json` to customize:

- Reusable comment templates
- Institution-specific feedback phrases
- Common review responses

### Categories

Create custom category files in `config/` directory:

- Each category gets its own JSON file
- Categories appear as tabs in Template Editor
- Used for organized feedback in review interface

## Customization

### Themes

- Customize CSS variables in `static/css/style.css`
- Modify color schemes for institutional branding
- Adjust layout and typography as needed

### Languages

- Extend bilingual support in `utils/extractor.py`
- Add new section mappings and key phrases
- Modify regex patterns for content recognition

### Templates

- Use the Template Editor interface for most customizations
- Direct file editing available for advanced users
- JSON structure allows flexible configuration

## Limitations

### Document Processing

- **NCN/OSF Specific**: Optimized for Polish NCN proposals via OSF system
- **File Size Limit**: Maximum 16MB upload size
- **Format Dependencies**: Best results with standard OSF-exported documents
- **Complex Layouts**: May struggle with heavily formatted layouts

### Technical

- **Single User**: No multi-user collaboration features
- **Local Storage**: Files stored locally on server
- **Session Based**: No user accounts or persistent login
- **Browser Compatibility**: Requires modern browser with JavaScript

### Known Issues

- Some text may appear in "Unconnected Text" section
- Complex table structures may not extract perfectly
- Section detection may miss non-standard formats
- Manual verification always recommended

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Testing

- Test with various NCN document formats
- Verify theme functionality across browsers
- Check responsive design on mobile devices
- Validate extraction accuracy with known documents

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What You Can Do

- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

### Requirements

- Include copyright notice
- Include license text

### Third-Party Licenses

- **Flask**: BSD-3-Clause License
- **PyPDF2**: BSD License
- **python-docx**: MIT License
- **Werkzeug**: BSD-3-Clause License
- **Pillow**: HPND License
- **Font Awesome**: Font Awesome Free License

## Attribution

When using or redistributing DMP ART, please include:

```
DMP ART - Data Management Plan Assessment and Response Tool
Copyright (c) 2025 DMP ART Contributors
Licensed under the MIT License
```

## Support

### Documentation

- Complete documentation available at `/documentation` route
- Step-by-step user guide included
- Technical architecture details provided

### Issues

- Report bugs via GitHub Issues
- Request features via GitHub Issues
- Ask questions in GitHub Discussions

### Best Practices

- Use high-quality PDF exports from OSF
- Always verify extracted content manually
- Save progress frequently during reviews
- Use updated browsers for best compatibility

## Recent Updates

### Version 0.8.1 - Optimization Release (2025-11-18) 🚀

**Major breakthrough in extraction accuracy and performance!**

#### OCR Support for Scanned PDFs ✨

- **100% Success Rate**: All scanned PDFs now process correctly with Tesseract OCR
- **Automatic Detection**: System detects scanned PDFs and applies OCR automatically
- **Bilingual**: Polish + English language pack support
- **Processing Time**: ~25s per scanned PDF (one-time cost, excellent results)

#### Performance Optimizations ⚡

- **99.9% Faster**: Text similarity calculations (0.0003ms vs 0.5ms)
- **80% Faster**: Section detection (0.024ms vs 0.12ms)
- **78% Faster**: Text filtering (0.039ms vs 0.18ms)
- **Pre-compiled Regex**: All patterns compiled at initialization
- **LRU Caching**: Smart caching for repeated calculations

#### Extraction Improvements 🎯

- **94.1% Success Rate**: Tested on 17 real-world NCN proposals (target: 93%)
- **4-Tier Fallback Detection**: Multiple strategies for non-standard formats
- **Enhanced Section Detection**: Better handling of formatted headers (BOLD:, UNDERLINED:)
- **Improved Content Assignment**: Smarter text-to-section mapping

#### Documentation 📚

- **[FINAL_TEST_RESULTS.md](FINAL_TEST_RESULTS.md)**: Complete optimization report (600+ lines)
- **[OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md)**: Technical performance analysis
- **[USER_GUIDE_DATA_STEWARD.md](USER_GUIDE_DATA_STEWARD.md)**: Comprehensive guide for data stewards
- **[INSTALLATION.md](INSTALLATION.md)**: Detailed setup with OCR instructions

#### Test Suite 🧪

- **21 Unit Tests**: 90% passing (19/21)
- **4 Performance Benchmarks**: All passing with excellent metrics
- **Real File Testing**: Comprehensive test on 17 actual NCN proposals
- **Automated Testing**: `test_extractor_optimization.py` and `test_real_files.py`

**See [FINAL_TEST_RESULTS.md](FINAL_TEST_RESULTS.md) for complete details.**

---

### Version 0.8 - Foundation Release

#### Template Editor
- **Dynamic Category Management**: Create, edit, and delete custom feedback categories
- **Per-Element Configuration**: Customize comments for each of 14 DMP sections
- **Auto-loading**: Automatically loads existing JSON configuration files
- **Real-time Saving**: Changes immediately available in review interface

#### Theme System
- **Dark Mode**: Elegant dark theme as default
- **Light Mode**: Switchable with one click
- **Fixed Toggle**: Theme toggle in top-left corner on all pages
- **Persistent Settings**: Theme preference saved in localStorage

#### Document Processing
- **Bilingual Support**: Polish and English DMPs with automatic detection
- **Table Extraction**: Advanced table content recognition
- **Section Recognition**: Automatic identification of 14 DMP elements

---

**DMP ART** - Making DMP assessment efficient, consistent, and comprehensive.
