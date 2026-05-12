# DMP-ART - Data Management Plan Assessment and Response Tool

<img width="8534" height="4572" alt="dmp-art-logo-main-dark" src="https://github.com/user-attachments/assets/c0d95fcd-9a2a-42a0-b9b0-9538fe7d49b8" />

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![Version](https://img.shields.io/badge/version-0.9.1-brightgreen.svg)](https://github.com/gammaro85/DMP-ART)
[![Success Rate](https://img.shields.io/badge/success_rate-94.1%25-success)](HISTORY.md)
[![OCR](https://img.shields.io/badge/OCR-supported-blue)](.claude/CLAUDE.md)

---

## Overview

DMP-ART is a web application for Polish research administrators (data stewards) to review Data Management Plans in NCN grant proposals. It automates extraction and provides template-based feedback, reducing review time from **2 hours to 30 minutes** (75% reduction).

**Core Function:** Extract DMP section from grant proposal (PDF/DOCX) → Split into 14 Science Europe sections → Enable fast review with pre-configured comments

**Target Users:** Data stewards at Polish research institutions
**Success Metric:** 94.1% extraction accuracy on real NCN proposals (tested on 17 files)

---

## Key Features

- **Automated Extraction** - Intelligently extracts DMP from 80-page proposals (PDF/DOCX)
- **OCR Support** - Processes scanned PDFs with Tesseract (100% success rate)
- **Bilingual Support** - Polish and English DMPs with automatic detection
- **Template System** - Pre-configured feedback for common review scenarios
- **Dark/Light Theme** - Professional, eye-friendly interface
- **Real-Time Progress** - Live feedback during 15-60s processing
- **94.1% Success Rate** - Exceeds 93% target on real-world files
- **Organized Export** - Separate folders for DMPs and reviews with linked naming

---

## Technology Stack

**Backend:**
- Python 3.8+ with Flask 3.1.1
- PyPDF2 3.0.1 (PDF processing)
- python-docx 1.1.2 (DOCX processing)
- Tesseract OCR 5.3+ (scanned PDF support)
- Werkzeug 3.1.3, Pillow 11.0.0

**Frontend:**
- Vanilla JavaScript (modular: script.js, ai_assistant.js, dark-mode.js)
- HTML5 + CSS3 with custom properties
- Dark/Light theme system
- Server-Sent Events (SSE) for real-time updates

**Data Storage:**
- JSON files in `config/` directory
- UUID-based cache system in `outputs/`
- No database (intentionally simple for single-user deployment)

---

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/gammaro85/DMP-ART.git
cd DMP-ART

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install OCR support (optional but recommended)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng poppler-utils
# macOS:
brew install tesseract tesseract-lang poppler

# 4. Install Python OCR libraries
pip install pytesseract pdf2image Pillow

# 5. Create directories
mkdir -p uploads outputs

# 6. Start application
python app.py

# 7. Open browser
# Navigate to: http://localhost:5000
```

**For detailed setup, see** `.claude/CLAUDE.md` → Deployment Notes

---

## Project Structure

```
dmp-art/
├── app.py                     # Flask routes, upload handling, SSE
├── requirements.txt           # Python dependencies
├── config/                    # JSON configuration files
│   ├── dmp_structure.json    # 14 DMP section definitions
│   ├── quick_comments.json   # Reusable comment templates
│   └── *.json                # Category-specific templates
├── templates/                 # Jinja2 HTML templates
│   ├── index.html            # Upload page
│   ├── review.html           # Review interface (2,341 lines)
│   ├── settings.html         # Unified settings page
│   └── documentation.html    # Documentation page
├── static/                    # Static assets
│   ├── css/
│   │   ├── style.css         # Main stylesheet (1,596 lines)
│   │   └── review.css        # Review-specific styles (671 lines)
│   ├── js/
│   │   ├── script.js         # Main logic (42KB)
│   │   ├── ai_assistant.js   # AI assistant frontend
│   │   └── dark-mode.js      # Theme management (4KB)
│   └── images/               # Logos and assets
├── utils/                     # Core processing modules
│   ├── extractor.py          # DMP extraction engine (2,101 lines)
│   └── dmp-three-categories.py
├── uploads/                   # Temporary upload storage
├── outputs/                   # Generated DMP files and cache
│   ├── cache/                # JSON cache files
│   ├── dmp/                  # Extracted DMPs
│   └── reviews/              # Feedback files
└── [Documentation Files]     # See Documentation section below
```

---

## Documentation

**For AI Agents (Claude, Copilot, etc.):**

- **[.claude/CLAUDE.md](.claude/CLAUDE.md)** - Complete AI agent guide to codebase (~750 lines)
  - Codebase structure, code patterns, common tasks, testing guidelines
  - Performance optimizations, security considerations, deployment notes

- **[HISTORY.md](HISTORY.md)** - Chronological project history (~600 lines)
  - Version history, architecture evolution, performance optimizations
  - Feature development timeline, technical debt resolution

- **[.claude/DOCUMENTATION_GUIDELINES.md](.claude/DOCUMENTATION_GUIDELINES.md)** - Documentation standards (~400 lines)
  - Best practices for maintaining docs, update workflows
  - Anti-patterns to avoid, quality checklist

- **Testing status** - maintained in [HISTORY.md](HISTORY.md) and [.claude/CLAUDE.md](.claude/CLAUDE.md)
  - Active validation scripts, manual diagnostics, and archived debug probes

**Documentation Principles:**
1. **Single Source of Truth** - Each concept documented in ONE location only
2. **Modify, Don't Create** - Update existing docs rather than create new files
3. **Code References Over Prose** - Link to actual code with file:line references
4. **For AI Agents, Not Humans** - Optimized for code assistants, not end users

---

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

### Categories
Create custom category files in `config/` directory:
- Each category gets its own JSON file
- Categories appear in the unified Settings page
- Used for organized feedback in review interface

---

## Performance Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Extraction Success Rate** | 94.1% (16/17 files) | ✅ Exceeds 93% target |
| **Time Savings** | 75% (2h → 30min) | ✅ Meets target |
| **OCR Success** | 100% on scanned PDFs | ✅ |
| **Processing Speed** | 0.26s avg (DOCX/PDF), 23.6s (OCR) | ✅ |
| **Text Similarity** | 0.0003ms (99.9% faster) | ✅ |
| **Validation Scripts** | `tests/validate_all_requirements.py`, `tests/test_feedback_folder.py`, `tests/test_integration_workflow.py` | ✅ |

**See [HISTORY.md](HISTORY.md) and [.claude/CLAUDE.md](.claude/CLAUDE.md) for testing details and current validation guidance**

---

## Known Limitations

### Functional
- **Single-user only** - No multi-user collaboration or authentication
- **Export formats** - TXT only (DOCX/PDF export planned)
- **Edge cases** - Corrupted PDF encoding (5.9% of files), non-standard formats

### Technical
- **NCN/OSF Specific** - Optimized for Polish NCN proposals via OSF system
- **File Size Limit** - Maximum 16MB upload size
- **Browser Compatibility** - Requires modern browser with JavaScript
- **Local Storage** - Files stored locally on server (no cloud backup)

**See [.claude/CLAUDE.md → Known Limitations](.claude/CLAUDE.md) for details**

---

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Testing

```bash
# Run unit tests
python tests/test_extractor_optimization.py

# Run validation scripts
python tests/validate_all_requirements.py
python tests/test_feedback_folder.py
python tests/test_integration_workflow.py

# Test with local real files (if tests/pzd/ exists)
python tests/test_real_files.py
python tests/test_pzd_extraction.py

# Verify OCR
tesseract --version
```

### Key Development Files

- `app.py` (Flask routes, SSE, session management)
- `utils/extractor.py` (Core DMP extraction engine)
- `templates/review.html` (Main review interface)
- `static/js/script.js` (Main JavaScript logic)
- `static/css/style.css` (Unified styling)

**For code patterns and conventions, see [.claude/CLAUDE.md → Code Patterns](.claude/CLAUDE.md)**

---

## Version History

### v0.9.1 (2026-04-10) - Current Version ✅

**Major Changes:**
- Unified Settings Page (replaces separate template_editor and ai_settings)
- Dead code removal (~130 KB cleaned up)
- Upload progress bar bug fix
- Dynamic max upload size configuration

### v0.8.1 (2025-11-23)

**Major Changes:**
- JavaScript modularization (3 separate files)
- File organization (outputs/cache/, outputs/dmp/, outputs/reviews/)
- Dependency updates (Flask 3.1.1, Werkzeug 3.1.3, Pillow 11.0.0)

### v0.8.0 (2025-11-19)

**Features:**
- Category management UI (now consolidated into the unified Settings page)
- Dark/Light theme system
- Bilingual document processing

### v0.7.x (2025-11-18) - Optimization Phase

**Achievements:**
- **94.1% success rate** (exceeds 93% target)
- OCR support for scanned PDFs (100% success)
- Performance optimizations (99.9% faster text similarity)
- Enhanced section detection (4-tier fallback)

**See [HISTORY.md](HISTORY.md) for complete version history**

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Flask**: BSD-3-Clause License
- **PyPDF2**: BSD License
- **python-docx**: MIT License
- **Werkzeug**: BSD-3-Clause License
- **Pillow**: HPND License
- **Font Awesome**: Font Awesome Free License

---

## Support

**For Development/Integration:**
- **AI Agents:** See `.claude/CLAUDE.md` for complete codebase guide
- **Issues:** https://github.com/gammaro85/DMP-ART/issues
- **History:** See `HISTORY.md` for project evolution
- **Tests:** See `HISTORY.md` and `.claude/CLAUDE.md` for current test guidance

**Best Practices:**
- Use high-quality PDF exports from OSF
- Always verify extracted content manually
- Save progress frequently during reviews
- Use updated browsers for best compatibility

---

## Attribution

When using or redistributing DMP-ART, please include:

```
DMP-ART - Data Management Plan Assessment and Response Tool
Copyright (c) 2025 DMP-ART Contributors
Licensed under the MIT License
```

---

**DMP-ART** - Making DMP assessment efficient, consistent, and comprehensive.

**Current Version:** 0.9.1
**Success Rate:** 94.1%
**Time Savings:** 75%
**Target Users:** Data stewards at Polish research institutions
