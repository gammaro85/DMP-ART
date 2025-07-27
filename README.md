# DMP ART - Data Management Plan Assessment and Response Tool

![DMP ART Logo](static/images/dmp-art-logo-main-light.png)

**DMP ART** is a specialized web application designed to streamline the assessment process of Data Management Plans (DMPs) from grant proposals submitted to the National Science Centre (NCN) through the OSF (Otwarta Nauka) system.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![Version](https://img.shields.io/badge/version-1.0-brightgreen.svg)](https://github.com/your-repo/dmp-art)

 Purpose

This tool supports research administrators, grant officers, and academic institutions in Poland by:

- Automated Extraction**: Processing PDF and DOCX documents exported from OSF system
- Content Analysis**: Identifying and structuring DMP sections according to NCN requirements  
- Standardized Review**: Providing consistent feedback templates and assessment frameworks
- Efficient Workflow**: Reducing manual work and improving review quality

## Key Features

###  Document Processing
- **Multi-format Support**: PDF and DOCX files (up to 16MB)
- **Table Extraction**: Advanced table content recognition
- **Formatting Preservation**: Bold, underlined text detection
- **Bilingual Processing**: Polish and English content

###  Content Analysis  
- **Section Recognition**: Automatic DMP section identification (1.1-6.2)
- **Key Phrase Detection**: 165+ DMP-related terms
- **Author Extraction**: Document metadata recognition
- **Content Tagging**: Methodology, data formats, security tags

###  Review Interface
- **Structured Feedback**: Section-by-section review system
- **Quick Comments**: Customizable quick-insert comments
- **Progress Tracking**: Visual progress indicators
- **Category System**: Multiple feedback categories (Ready, Missing, Newcomer)

###  Template Editor
- **DMP Structure Management**: Configure section hierarchy
- **Quick Comments Editor**: Add/edit/delete quick comments
- **Dynamic Categories**: Create custom feedback categories
- **Real-time Preview**: See changes immediately

###  Export & Reports
- **Feedback Compilation**: Generate comprehensive feedback reports
- **Multiple Formats**: TXT, HTML export options
- **Progress Saving**: Save and resume review sessions
- **Document Comparison**: Original vs. extracted content

###  User Experience
- **Dark/Light Theme**: Automatic system detection with toggle button
- **Responsive Design**: Works on desktop, tablet, mobile
- **Keyboard Shortcuts**: Ctrl+Shift+D for theme toggle
- **Accessibility**: Screen reader friendly, proper ARIA labels

##  Technical Stack

### Backend
- **Python 3.8+**: Core application logic
- **Flask 3.1.0**: Web framework
- **PyPDF2 3.0.1**: PDF processing
- **python-docx 1.1.2**: DOCX processing
- **Werkzeug 3.1.3**: WSGI utilities
- **Pillow 11.0.0**: Image processing

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid/Flexbox
- **JavaScript ES6+**: Interactive functionality
- **Font Awesome 6.0**: Icon library
- **Responsive Design**: Mobile-first approach

### Data Storage
- **JSON**: Configuration files, templates, and data storage
- **Local File System**: Uploaded documents and generated reports
- **In-Memory Processing**: Real-time document analysis
- **Cache System**: Extracted content caching with unique identifiers

##  Quick Start

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

3. **Verify configuration files**
   ```bash
   ls config/  # Should show JSON configuration files
   ```

4. **Create necessary directories**
   ```bash
   mkdir -p uploads outputs
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   ```
   Open your browser and navigate to: http://localhost:5000
   ```

##  Usage Guide

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

##  Project Structure

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

##  Configuration

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

##  Customization

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

##  Limitations

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

##  Development

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

##  License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What You Can Do
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution  
- ✅ Private use

### Requirements
-  Include copyright notice
-  Include license text

### Third-Party Licenses
- **Flask**: BSD-3-Clause License
- **PyPDF2**: BSD License
- **python-docx**: MIT License
- **Werkzeug**: BSD-3-Clause License
- **Pillow**: HPND License
- **Font Awesome**: Font Awesome Free License

##  Attribution

When using or redistributing DMP ART, please include:

```
DMP ART - Data Management Plan Assessment and Response Tool
Copyright (c) 2025 DMP ART Contributors
Licensed under the MIT License
```

##  Support

### Documentation
-  Complete documentation available at `/documentation` route
- Step-by-step user guide included
-  Technical architecture details provided

### Issues
-  Report bugs via GitHub Issues
-  Request features via GitHub Issues
-  Ask questions in GitHub Discussions

### Best Practices
-  Use high-quality PDF exports from OSF
-  Always verify extracted content manually
-  Save progress frequently during reviews
-  Use updated browsers for best compatibility

##  Recent Updates

### Version 1.0 Features
- **Enhanced Template Editor**: Dynamic category management with real-time editing
- **Improved Theme System**: Fixed theme toggle with proper sun/moon icons in top-left corner
- **Better Document Processing**: Enhanced DOCX and PDF extraction with table support
- **Comprehensive Documentation**: Complete user guide and technical documentation
- **MIT License**: Open source with permissive licensing
- **Responsive Design**: Mobile-friendly interface with dark/light theme support

### Template Editor Improvements
- **Permanent Tabs**: DMP Structure and Quick Comments tabs are always available
- **Dynamic Categories**: Create, edit, and delete custom feedback categories
- **Auto-loading**: Automatically loads existing JSON configuration files as tabs
- **Real-time Saving**: Save changes directly from the interface
- **Consistent Layout**: Matches design patterns across all pages

### Theme System Fixes
- **Fixed Position Toggle**: Theme toggle now appears in top-left corner on all pages
- **Correct Icons**: Moon icon in light mode, sun icon in dark mode
- **Consistent Behavior**: Works reliably across all pages and browsers
- **Persistent Settings**: Theme preference saved in localStorage

---

**DMP ART** - Making DMP assessment efficient, consistent, and comprehensive.
