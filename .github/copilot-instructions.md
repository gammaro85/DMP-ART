# Claude Copilot Instructions for DMP-ART

## Project Overview
DMP-ART is a **single-user Flask web application** for Polish research administrators to review Data Management Plans (DMPs) in NCN grant proposals. It extracts DMPs from PDF/DOCX files, splits them into 14 Science Europe sections, and provides template-based feedback. **Success rate: 94.1%** on real proposals.

**Tech Stack:** Python 3.8+ (tested on 3.11), Flask 3.1.1, PyPDF2 3.0.1, python-docx 1.1.2, Vanilla JavaScript (no frameworks), JSON-based storage (no database).

**Project Size:** ~200KB codebase, 2,101-line extractor, 2,341-line review UI, 42KB main JS file.

## Critical Setup Requirements

### Installation (ALWAYS follow this order)
```bash
# 1. Install Python dependencies (REQUIRED before running app)
pip install --ignore-installed blinker -r requirements.txt

# 2. Create required directories (app will crash without these)
mkdir -p uploads outputs outputs/cache outputs/dmp outputs/reviews

# 3. Verify imports work
python -c "from utils.extractor import DMPExtractor; print('OK')"
python -c "import flask; print('OK')"

# 4. Run application
python app.py
# Opens on http://localhost:5000
```

**CRITICAL:** Always run `pip install` with `--ignore-installed blinker` flag due to Debian system package conflict. Without this, installation fails with "Cannot uninstall blinker 1.7.0".

### Optional OCR Support
OCR is NOT required for basic functionality but enables scanned PDF processing (100% success rate on scanned files). Installation:
```bash
# Ubuntu/Debian (tested working):
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng poppler-utils
pip install pytesseract pdf2image

# Verify:
tesseract --version  # Should show 5.3+
```

## Architecture & File Layout

### Critical Files (Edit These Most Often)
- `app.py` (48KB, 1,396 lines) - All Flask routes, SSE progress, file upload
- `utils/extractor.py` (97KB, 2,101 lines) - **Core DMP extraction engine** with 4-tier fallback detection
- `templates/review.html` (99KB, 2,341 lines) - Main review interface
- `static/css/style.css` (38KB, 1,596 lines) - Unified dark/light theme CSS
- `static/js/script.js` (42KB) - Main app logic, AJAX, UI interactions
- `static/js/template_editor.js` (28KB) - Template editor functionality
- `static/js/dark-mode.js` (4.5KB) - Theme management with localStorage

### Configuration Files (User-Editable JSON)
```
config/
├── dmp_structure.json       # 14 DMP section definitions (DO NOT delete)
├── quick_comments.json       # Reusable comment templates
├── newcomer.json            # Category: Guidance for newcomers (44KB)
├── mising.json              # Category: Missing information (17KB)
├── ready.json               # Category: Ready feedback (6KB)
└── [custom].json            # Users can create unlimited categories
```

**IMPORTANT:** Changes to `config/*.json` files are auto-loaded. NO code changes needed when editing templates.

### Directory Structure
```
DMP-ART/
├── app.py                   # Flask entry point, all routes
├── requirements.txt         # 5 core dependencies
├── utils/
│   ├── extractor.py        # DMPExtractor class (main processing logic)
│   └── dmp-three-categories.py  # Category migration utility
├── static/
│   ├── js/                 # 3 modular JS files (no build tools)
│   ├── css/                # style.css + review.css
│   └── images/             # Logos and assets
├── templates/              # 5 Jinja2 HTML templates
│   ├── index.html          # Upload page
│   ├── review.html         # Main review interface (LARGEST file)
│   ├── template_editor.html
│   ├── documentation.html
│   └── test_categories.html
├── config/                 # JSON configs (version controlled)
├── outputs/
│   ├── cache/              # cache_*.json files (gitignored)
│   ├── dmp/                # Extracted DMP files
│   └── reviews/            # Feedback files
├── uploads/                # Temporary storage (cleaned after processing)
└── tests/fixtures/         # Test files (not included in repo)
```

## Build, Test & Validation

### Running the Application
```bash
# Development mode (auto-reload enabled)
python app.py

# Production mode (use gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**No build step required** - Vanilla JS served directly, no webpack/bundling.

### Testing
**No pytest/unittest** - Tests use custom Python scripts:

```bash
# Test extractor performance (requires test files)
python test_extractor_optimization.py

# Test real files (requires /pzd directory with test PDFs)
python test_real_files.py
# NOTE: This WILL FAIL if /pzd directory missing - this is expected

# Test integration workflow
python test_integration_workflow.py

# Validate all requirements
python validate_all_requirements.py
```

**Test file location:** Tests expect files in `/pzd` directory (not included in repo). When testing, create test files manually or skip file-based tests.

### Manual Validation Checklist
After making changes, ALWAYS verify:
1. **Upload works:** Navigate to http://localhost:5000, upload PDF/DOCX
2. **Extraction succeeds:** Check extraction completes without errors (15-60s)
3. **Review page renders:** All 14 sections visible with content
4. **Theme toggle works:** Switch dark/light mode, verify persistence
5. **Templates load:** Quick comments appear in dropdowns
6. **Export works:** Download feedback as TXT file

## Common Development Patterns

### Flask Routes (Standard Pattern)
```python
@app.route('/api/endpoint', methods=['POST'])
def function_name():
    try:
        data = request.json
        # 1. Validate input
        # 2. Process data
        # 3. Return consistent JSON
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
```

**ALL API routes return:** `{success: bool, message: string, data: object}`

### JavaScript Patterns (No Build Tools)
```javascript
// Theme management (localStorage persisted)
localStorage.setItem('dmp-art-theme', 'dark');
document.documentElement.setAttribute('data-theme', 'dark');

// AJAX calls (always use fetch, not XMLHttpRequest)
fetch('/api/endpoint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
})
.then(r => r.json())
.then(data => {
    if (data.success) { /* handle */ }
    else { showToast(data.message, 'error'); }
});
```

### CSS Theme System
```css
/* Use CSS custom properties - defined in :root[data-theme] */
:root[data-theme="dark"] {
    --bg-main: #1a1a1a;
    --text-primary: #ecf0f1;
}
/* Apply variables everywhere */
body { background: var(--bg-main); }
```

## Common Tasks & Solutions

### Adding New Quick Comment
1. Edit `config/quick_comments.json`
2. Save file
3. **Done** - No restart needed, auto-loaded

### Adding New Category
1. Create `config/new_category.json` with section structure
2. Restart Flask app
3. Category appears in Template Editor and Review page

### Modifying Extraction Logic
Edit `utils/extractor.py` methods:
- `process_file()` - Entry point
- `detect_section_from_text()` - 4-tier fallback (BOLD markers → numbered sections → formatted text → text similarity)
- `improve_content_assignment()` - Content-to-section mapping

**Performance tip:** Pre-compile regex in `__init__()` for 99.9% speedup.

### Troubleshooting Extraction Issues
**"Unconnected Text" appearing:**
- Expected behavior for content before DMP start
- Improve `find_dmp_boundaries()` markers in extractor.py

**Section detection failing:**
- Check 4-tier fallback in `detect_section_from_text()`
- Add bilingual mappings for non-standard formats
- Current Jaccard similarity threshold: 0.6

## Known Issues & Workarounds

### Issue: pip install fails with "Cannot uninstall blinker"
**Solution:** Use `pip install --ignore-installed blinker -r requirements.txt`

### Issue: test_real_files.py fails with FileNotFoundError
**Solution:** Expected - test requires `/pzd` directory with test files (not in repo)

### Issue: "No module named 'flask'" after installation
**Cause:** Dependencies not installed
**Solution:** Run `pip install --ignore-installed blinker -r requirements.txt`

### Issue: OCR not working on scanned PDFs
**Cause:** Tesseract not installed (optional dependency)
**Solution:** Install Tesseract: `sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng`

### Issue: Upload fails with "File too large"
**Cause:** File > 16MB
**Solution:** Edit `app.py`: `app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024`

## Git Workflow for Claude Branches

**CRITICAL:** All Claude agent branches MUST:
- Start with `claude/` prefix
- End with matching session ID
- Example: `claude/feature-name-01QEfmPE2X21dJZYq87g62QS`

```bash
# Check current branch (should be claude/*)
git status
git branch

# Standard commit workflow
git add .
git commit -m "Clear, descriptive message"
git push -u origin <claude-branch-name>

# Note: Push fails with 403 if branch name doesn't match pattern
```

## Key API Routes

**Main Routes:**
- `GET /` - Upload page
- `POST /upload` - File processing (returns cache_id)
- `GET /review/<filename>` - Review interface
- `GET /download/<filename>` - Download files

**Template Management:**
- `POST /save_templates` - Save DMP templates
- `POST /save_quick_comments` - Save quick comments
- `POST /save_category` - Save category config
- `GET /load_categories` - Get categories list

**Category API:**
- `GET /api/discover-categories` - List all categories
- `POST /api/create-category` - Create new category
- `DELETE /api/delete-category/<id>` - Delete category

## Performance & Optimization

**Implemented optimizations (DO NOT remove):**
- Pre-compiled regex patterns (99.9% faster text similarity)
- LRU caching with `@lru_cache(maxsize=128)` on similarity checks
- UUID-based cache system (enables concurrent uploads)

**Processing time:** 15-60 seconds for 80-page proposals

## Trust These Instructions

This file contains **validated, working commands**. When following these instructions:
- **DO NOT search for alternative approaches** unless instructions fail
- **DO NOT modify working patterns** without clear reason
- **ALWAYS run pip install** with `--ignore-installed blinker` flag
- **ALWAYS create directories** before first run
- **Trust the 4-tier fallback** in extractor.py - it's battle-tested on 17 real proposals

For detailed implementation guidance, see `.claude/CLAUDE.md` (comprehensive AI agent guide).

**Last Validated:** 2025-11-23 | **Version:** 0.8.1 | **Python:** 3.11.14 | **Success Rate:** 94.1%
