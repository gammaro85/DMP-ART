# DMP-ART - Build Instructions

## 📦 Standalone Executable (Recommended for End Users)

### Quick Build

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run build script (automated)
python build_standalone.py
```

**Output:** `DMP-ART-Standalone.zip` (~50-150 MB depending on platform)

### What Gets Created

```
DMP-ART-Standalone.zip
└── DMP-ART/
    ├── DMP-ART.exe          # Main executable (Windows) or DMP-ART (Linux/Mac)
    ├── _internal/           # Python runtime and dependencies
    ├── input/               # User files directory
    ├── output/              # Results directory
    │   ├── dmp/
    │   ├── reviews/
    │   └── cache/
    ├── config/              # Template configurations
    └── INSTRUKCJA.txt       # Polish user guide
```

### Manual Build (Advanced)

```bash
# 1. Clean previous builds
rm -rf build/ dist/

# 2. Build with PyInstaller
pyinstaller DMP-ART.spec --clean

# 3. Create folder structure
mkdir -p dist/DMP-ART/{input,output/{dmp,reviews,cache},config}

# 4. Copy config files
cp config/*.json dist/DMP-ART/config/

# 5. Create documentation
# (Manual or use build_standalone.py)

# 6. Package to ZIP
cd dist
zip -r ../DMP-ART-Standalone.zip DMP-ART/
```

---

## 🐳 Docker Container (Alternative)

### Build Docker Image

```bash
# Build image
docker build -t dmp-art:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/input:/app/uploads \
  -v $(pwd)/output:/app/outputs \
  --name dmp-art \
  dmp-art:latest

# Access: http://localhost:5000
```

### Docker Compose (Easier)

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f
```

---

## 🔧 Build Requirements

### System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows 10+, Linux (Ubuntu 20.04+), macOS 10.15+
- **RAM:** 4 GB minimum (8 GB recommended for build)
- **Disk:** 2 GB free space for build artifacts

### Python Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `Flask==3.1.1` - Web framework
- `PyInstaller==6.3.0` - Executable builder
- `PyPDF2==3.0.1` - PDF processing
- `python-docx==1.1.2` - DOCX processing
- `Pillow==11.0.0` - Image processing
- `pytesseract==0.3.10` - OCR wrapper (requires Tesseract)

### Optional: Tesseract OCR

**For scanned PDF support:**

**Windows:**
```powershell
# Download installer from:
https://github.com/UB-Mannheim/tesseract/wiki
# Run installer and add to PATH
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Note:** Standalone builds do NOT bundle Tesseract. Users must install it separately for OCR functionality.

---

## 🚀 Platform-Specific Builds

### Windows (x64)

```bash
# Build on Windows
python build_standalone.py

# Output: DMP-ART.exe (Windows executable)
```

**Tested on:**
- Windows 10 (1909+)
- Windows 11

### Linux (x64)

```bash
# Build on Linux
python3 build_standalone.py

# Output: DMP-ART (ELF executable)
# Make executable: chmod +x dist/DMP-ART/DMP-ART
```

**Tested on:**
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Debian 11

### macOS (Intel & Apple Silicon)

```bash
# Build on macOS
python3 build_standalone.py

# Output: DMP-ART (Mach-O executable)
```

**Tested on:**
- macOS 11 Big Sur (Intel)
- macOS 12 Monterey (Apple Silicon M1/M2)

**Note:** On macOS, you may need to allow the app in Security & Privacy settings on first run.

---

## 🧪 Testing the Build

### Quick Test

```bash
# Extract ZIP
unzip DMP-ART-Standalone.zip
cd DMP-ART

# Run executable
./DMP-ART.exe          # Windows
./DMP-ART              # Linux/Mac

# Browser should open at: http://localhost:5000
```

### Full Test Workflow

1. **Upload test file:**
   - Copy sample PDF/DOCX to `input/` folder
   - Upload via web interface

2. **Verify extraction:**
   - Check if 14 sections are detected
   - Verify content is properly split

3. **Test features:**
   - Quick comments dropdown
   - Category selection
   - Text editing
   - Save feedback
   - Export to file

4. **Check outputs:**
   - `output/dmp/` - Extracted DMP
   - `output/reviews/` - Saved review
   - `output/cache/` - Cache files

---

## 🐛 Troubleshooting Build Issues

### PyInstaller Not Found

```bash
pip install --upgrade pyinstaller
```

### Missing Hidden Imports

Edit `DMP-ART.spec` and add to `hiddenimports`:
```python
hiddenimports = [
    'flask',
    'werkzeug',
    # Add missing module here
]
```

### Large Executable Size

**Normal sizes:**
- Windows: 50-80 MB
- Linux: 40-60 MB
- macOS: 60-90 MB

**To reduce:**
- Use `--exclude-module` in spec file for unused packages
- Enable UPX compression (already enabled in spec)

### Runtime Errors

**Check console output:**
```bash
# Run with console to see errors
./DMP-ART.exe
```

**Common fixes:**
- Ensure all templates/static files are in spec `datas`
- Check file paths use `sys._MEIPASS` for bundled resources
- Verify config files exist in `config/` folder

---

## 📊 Build Performance

**Typical build times:**
- Clean build: 2-5 minutes
- Incremental: 1-2 minutes

**Output sizes:**
- Uncompressed: 150-250 MB
- ZIP compressed: 50-100 MB

---

## 🔐 Code Signing (Optional)

### Windows

```bash
# Sign with certificate
signtool sign /f cert.pfx /p password /t http://timestamp.digicert.com dist/DMP-ART/DMP-ART.exe
```

### macOS

```bash
# Sign and notarize
codesign --sign "Developer ID Application" dist/DMP-ART/DMP-ART
xcrun notarytool submit DMP-ART-Standalone.zip --apple-id ... --team-id ...
```

**Note:** Signing is optional but recommended for production distribution to avoid security warnings.

---

## 📝 Build Checklist

Before releasing:

- [ ] Version number updated in code
- [ ] All dependencies in requirements.txt
- [ ] Config files copied to dist
- [ ] Documentation (INSTRUKCJA.txt) included
- [ ] Tested on target platform
- [ ] OCR functionality tested (if Tesseract available)
- [ ] No hardcoded paths in code
- [ ] README files in input/output folders
- [ ] ZIP archive created
- [ ] Archive size reasonable (<150 MB)
- [ ] Executable runs without console errors
- [ ] All 14 DMP sections extract correctly

---

## 🆘 Support

**Build issues?**
- Check logs: `build/DMP-ART/warn-DMP-ART.txt`
- Open issue: https://github.com/gammaro85/DMP-ART/issues
- Include: OS, Python version, error messages

---

**Last updated:** 2024-12-03
**Build script version:** 1.0
**PyInstaller version:** 6.3.0
