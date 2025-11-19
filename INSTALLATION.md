# DMP-ART Installation Guide

**Version:** 0.8.1
**Last Updated:** 2025-11-18
**Status:** Active

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Install](#quick-install)
3. [Detailed Installation](#detailed-installation)
4. [OCR Setup](#ocr-setup)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 512 MB | 1 GB+ |
| **Disk Space** | 500 MB | 1 GB+ |
| **OS** | Linux, macOS, Windows | Ubuntu 20.04+, macOS 12+, Windows 10+ |

### Software Dependencies

- **Python 3.8 or higher** with pip
- **Modern web browser** (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Internet connection** (for Font Awesome icons and initial setup)
- **Tesseract OCR** (optional, for scanned PDF support)
- **Poppler** (optional, for PDF to image conversion)

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

Expected output: `Python 3.8.0` or higher

---

## Quick Install

**For users who just want to get started quickly:**

```bash
# 1. Clone repository
git clone https://github.com/gammaro85/DMP-ART.git
cd DMP-ART

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Create directories
mkdir -p uploads outputs

# 4. Run application
python app.py

# 5. Open browser
# Navigate to: http://localhost:5000
```

**That's it!** For OCR support (scanned PDFs), continue to [OCR Setup](#ocr-setup).

---

## Detailed Installation

### Step 1: Clone Repository

**Option A: HTTPS (Recommended)**
```bash
git clone https://github.com/gammaro85/DMP-ART.git
cd DMP-ART
```

**Option B: SSH**
```bash
git clone git@github.com:gammaro85/DMP-ART.git
cd DMP-ART
```

**Option C: Download ZIP**
1. Visit https://github.com/gammaro85/DMP-ART
2. Click "Code" → "Download ZIP"
3. Extract to your desired location
4. Open terminal in extracted folder

### Step 2: Create Virtual Environment (Recommended)

**Why use a virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Makes dependency management cleaner

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Your prompt should now show (venv)
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# If you get an execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Python Dependencies

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

**Expected packages installed:**
- Flask 3.1.0 (web framework)
- PyPDF2 3.0.1 (PDF processing)
- python-docx 1.1.2 (DOCX processing)
- Werkzeug 3.1.3 (WSGI utilities)
- Pillow 11.0.0 (image processing)

**Verify installation:**
```bash
pip list | grep -E "Flask|PyPDF2|python-docx"
```

### Step 4: Create Required Directories

```bash
# Create upload and output directories
mkdir -p uploads outputs

# Verify directory structure
ls -la
```

**Expected directories:**
```
DMP-ART/
├── uploads/    (temporary file storage)
├── outputs/    (processed files and cache)
├── config/     (configuration files)
├── templates/  (HTML templates)
├── static/     (CSS, JS, images)
└── utils/      (Python modules)
```

### Step 5: Verify Configuration Files

```bash
# Check that configuration files exist
ls -l config/

# Expected files:
# - dmp_structure.json
# - quick_comments.json
# - [category files].json
```

If files are missing, they should be in the repository. Re-clone or restore from git.

---

## OCR Setup

**OCR (Optical Character Recognition)** enables DMP-ART to process **scanned PDFs** that don't have extractable text.

### Why Install OCR?

Without OCR:
- ❌ Scanned PDFs fail with "no extractable text" error
- ❌ Image-based PDFs cannot be processed
- ❌ ~20% of NCN submissions may fail

With OCR:
- ✅ 100% success rate on scanned PDFs
- ✅ Automatic fallback when text extraction fails
- ✅ 94.1% overall success rate on real-world files

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt-get update

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr

# Install language packs (Polish + English)
sudo apt-get install -y tesseract-ocr-pol tesseract-ocr-eng

# Install Poppler (for PDF to image conversion)
sudo apt-get install -y poppler-utils

# Install Python OCR libraries
pip install pytesseract pdf2image Pillow

# Verify installation
tesseract --version
```

**Expected output:**
```
tesseract 5.3.4
 leptonica-1.82.0
 ...
```

### macOS (Homebrew)

```bash
# Install Homebrew if not already installed
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Tesseract with language packs
brew install tesseract tesseract-lang

# Install Poppler
brew install poppler

# Install Python OCR libraries
pip install pytesseract pdf2image Pillow

# Verify installation
tesseract --version
```

### Windows

**Method 1: Chocolatey (Recommended)**

```powershell
# Install Chocolatey if not already installed
# See: https://chocolatey.org/install

# Install Tesseract
choco install tesseract

# Install Poppler
choco install poppler

# Install Python OCR libraries
pip install pytesseract pdf2image Pillow
```

**Method 2: Manual Installation**

1. **Download Tesseract:**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download latest installer (e.g., `tesseract-ocr-w64-setup-5.3.4.exe`)
   - Run installer, **note the installation path** (e.g., `C:\Program Files\Tesseract-OCR`)

2. **Download Poppler:**
   - Visit: https://github.com/oschwartz10612/poppler-windows/releases
   - Download latest release (e.g., `poppler-24.02.0.zip`)
   - Extract to `C:\Program Files\poppler`

3. **Add to PATH:**
   ```powershell
   # Add Tesseract to PATH
   $env:Path += ";C:\Program Files\Tesseract-OCR"

   # Add Poppler to PATH
   $env:Path += ";C:\Program Files\poppler\Library\bin"

   # Make permanent (System Properties → Environment Variables)
   ```

4. **Install Python libraries:**
   ```powershell
   pip install pytesseract pdf2image Pillow
   ```

5. **Configure Tesseract path in Python:**

   Create `config_local.py` in project root:
   ```python
   # config_local.py
   TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### Verify OCR Installation

**Test Tesseract:**
```bash
tesseract --version
```

**Test Python integration:**
```bash
python -c "import pytesseract; from pdf2image import convert_from_path; print('OCR libraries OK')"
```

**Expected output:**
```
OCR libraries OK
```

**Test with sample file:**
```bash
# Test extraction on all PZD files
python test_real_files.py
```

---

## Verification

### Step 1: Start Application

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Start Flask application
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 2: Access Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

**You should see:**
- DMP-ART logo and title
- Upload area with drag & drop
- "Select File" and "Upload and Process" buttons
- Theme toggle in top-left corner

### Step 3: Test with Sample File

**Option A: Use Test File**
```bash
# If you have sample DMPs in pzd/ folder
# Upload one through the web interface
```

**Option B: Download Test File**
```bash
# Create a test DOCX file
echo "This is a test DMP document." > test.txt
# Upload through web interface
```

### Step 4: Verify Features

**Test Checklist:**

- [ ] Upload page loads correctly
- [ ] Dark/light theme toggle works
- [ ] File upload succeeds
- [ ] Extraction completes (redirects to review page)
- [ ] Review page displays sections
- [ ] Quick comments sidebar visible
- [ ] Category buttons work
- [ ] Feedback compilation works
- [ ] Template editor accessible
- [ ] OCR test (upload scanned PDF if available)

---

## Troubleshooting

### Common Installation Issues

#### Issue 1: "pip: command not found"

**Solution:**
```bash
# Use pip3 instead
pip3 install -r requirements.txt

# Or ensure pip is installed
python -m ensurepip --upgrade
```

#### Issue 2: "python: command not found"

**Solution:**
```bash
# Use python3 instead
python3 app.py

# Or create alias
alias python=python3
```

#### Issue 3: Permission errors during pip install

**Solution:**
```bash
# Option 1: Use --user flag
pip install --user -r requirements.txt

# Option 2: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue 4: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
# Virtual environment not activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Or install in current environment
pip install flask
```

### OCR-Specific Issues

#### Issue 5: "tesseract: command not found"

**Solution:**
```bash
# Linux: Install Tesseract
sudo apt-get install tesseract-ocr

# macOS: Install via Homebrew
brew install tesseract

# Windows: Add to PATH or set in code
# See Windows OCR setup above
```

#### Issue 6: "Unable to find Tesseract OCR"

**Solution (Windows):**

Create `config_local.py`:
```python
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Then in `utils/extractor.py`:
```python
try:
    from config_local import TESSERACT_PATH
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
except ImportError:
    pass  # Use default PATH
```

#### Issue 7: OCR is slow (> 60 seconds per page)

**Solution:**
- Normal for high-resolution scans
- Reduce DPI in pdf2image: `convert_from_path(pdf_path, dpi=200)`
- Use faster machine or cloud processing
- Consider pre-processing PDFs to lower resolution

### Application Issues

#### Issue 8: "Address already in use" when starting app

**Solution:**
```bash
# Kill process on port 5000
# Linux/macOS:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port
python app.py --port 5001
```

#### Issue 9: Static files not loading (CSS/JS)

**Solution:**
```bash
# Clear browser cache (Ctrl+Shift+R)
# Or verify static folder exists
ls static/css/style.css
ls static/js/script.js

# Check file permissions
chmod -R 755 static/
```

#### Issue 10: "TemplateNotFound" error

**Solution:**
```bash
# Verify templates exist
ls templates/index.html
ls templates/review.html

# Check current working directory
pwd  # Should be in DMP-ART root
```

### Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   # Run with verbose output
   export FLASK_ENV=development
   python app.py
   ```

2. **Run diagnostics:**
   ```bash
   # Test extractor
   python test_extractor_optimization.py

   # Test on real files
   python test_real_files.py
   ```

3. **Report issue:**
   - Visit: https://github.com/gammaro85/DMP-ART/issues
   - Include:
     - Operating system and version
     - Python version (`python --version`)
     - Error message (full traceback)
     - Steps to reproduce

---

## Next Steps

### For Users

1. **Read User Guide:**
   - See README.md for usage instructions
   - Visit `/documentation` route for in-app guide
   - Review TROUBLESHOOTING.md for common issues

2. **Test with Real Files:**
   - Upload NCN grant proposals
   - Verify extraction quality
   - Report any issues

3. **Customize Templates:**
   - Access Template Editor
   - Create custom feedback categories
   - Add institution-specific quick comments

### For Developers

1. **Review Architecture:**
   - Read `.claude/CLAUDE.md` for technical deep dive
   - Check `docs/API_REFERENCE.md` (if available)
   - Review code structure

2. **Run Tests:**
   ```bash
   # Unit tests
   python test_extractor_optimization.py

   # Integration tests
   python test_real_files.py
   ```

3. **Setup Development Environment:**
   ```bash
   # Enable debug mode
   export FLASK_ENV=development

   # Run with auto-reload
   export FLASK_DEBUG=1
   python app.py
   ```

### For Production Deployment

See **DEPLOYMENT.md** for production setup including:
- WSGI server configuration (Gunicorn/uWSGI)
- Nginx reverse proxy setup
- Security hardening
- Monitoring and logging
- Backup procedures

---

## Additional Resources

**Documentation:**
- [README.md](README.md) - Project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Developer API

**Test Reports:**
- [FINAL_TEST_RESULTS.md](FINAL_TEST_RESULTS.md) - Latest optimization (94.1% success)
- [OPTIMIZATION_REPORT.md](OPTIMIZATION_REPORT.md) - Performance analysis

**External Links:**
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Flask Documentation](https://flask.palletsprojects.com/) - Web framework
- [python-docx](https://python-docx.readthedocs.io/) - DOCX library
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF library

---

## Installation Checklist

Use this checklist to verify your installation:

### Basic Installation
- [ ] Python 3.8+ installed and verified
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Directories created (`uploads/`, `outputs/`)
- [ ] Configuration files present in `config/`
- [ ] Application starts without errors
- [ ] Web interface accessible at http://localhost:5000
- [ ] Can upload and process a DOCX file

### OCR Support (Optional but Recommended)
- [ ] Tesseract OCR installed
- [ ] Polish language pack installed
- [ ] English language pack installed
- [ ] Poppler/poppler-utils installed
- [ ] Python OCR libraries installed (`pytesseract`, `pdf2image`, `Pillow`)
- [ ] `tesseract --version` works
- [ ] Can process scanned PDFs successfully

### Verification
- [ ] Theme toggle works (dark/light mode)
- [ ] Upload and extraction successful
- [ ] Review interface displays correctly
- [ ] Quick comments sidebar functional
- [ ] Category system works
- [ ] Feedback compilation works
- [ ] Template editor accessible
- [ ] All tests pass (`test_extractor_optimization.py`)

---

**Installation Complete!** 🎉

You're ready to use DMP-ART. For usage instructions, see [README.md](README.md).

---

**Document Info:**
- **Version:** 1.0
- **Last Updated:** 2025-11-18
- **Maintained By:** DMP-ART Team
- **Status:** Active

For updates to this guide, check the GitHub repository.
