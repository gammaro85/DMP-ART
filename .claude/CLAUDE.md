# DMP-ART: AI Agent Development Guide

**Version:** 0.8.1
**Last Updated:** 2025-11-23
**Purpose:** Context and instructions for AI agents working on this codebase

---

## Project Overview

### What is DMP-ART?

DMP-ART (Data Management Plan Assessment and Response Tool) is a web application for Polish research administrators (data stewards) to review Data Management Plans in NCN grant proposals. It automates extraction and provides template-based feedback.

**Core Function:** Extract DMP section from grant proposal (PDF/DOCX) → Split into 14 Science Europe sections → Enable fast review with pre-configured comments

**Target Users:** Data stewards at Polish research institutions
**Success Metric:** Reduce review time from 2 hours to 30 minutes (75% reduction)
**Current Success Rate:** 94.1% on real NCN proposals (tested on 17 files)

### Technology Stack

**Backend:**
- Python 3.8+ with Flask 3.1.1
- PyPDF2 3.0.1 (PDF processing)
- python-docx 1.1.2 (DOCX processing)
- Werkzeug 3.1.3 (security utilities)
- Pillow 11.0.0 (image processing for OCR)
- pytesseract + Tesseract OCR 5.3+ (scanned PDF support)

**Frontend:**
- Vanilla JavaScript (no frameworks, but now organized in separate files)
- HTML5 + CSS3 with custom properties
- Dark/Light theme system with dedicated dark-mode.js
- Modular JS architecture (script.js, template_editor.js)

**Data Storage:**
- JSON files in `config/` directory
- UUID-based cache system in `outputs/`
- No database (intentionally simple for single-user deployment)

---

## Codebase Structure

### Critical Files (Edit These Most Often)

```
app.py                              # Flask routes, upload handling, main logic
utils/extractor.py                  # Core DMP extraction engine (2,101 lines)
templates/review.html               # Main review interface (2,341 lines)
static/css/style.css                # Unified styling (1,596 lines, dark/light themes)
static/js/script.js                 # Main JavaScript functionality (42KB)
static/js/template_editor.js        # Template editor logic (28KB)
static/js/dark-mode.js              # Theme management (4KB)
```

### Configuration Files (User-Editable)

```
config/
├── dmp_structure.json              # 14 DMP section definitions
├── quick_comments.json             # Reusable comment templates
├── newcomer.json                   # Category: Guidance for newcomers
├── mising.json                     # Category: Missing information
├── ready.json                      # Category: Ready to use feedback
└── [custom].json                   # User can create unlimited categories
```

### Key Directories

```
templates/                          # Jinja2 HTML templates
├── index.html                      # Upload page
├── review.html                     # Review interface (main UI)
├── template_editor.html            # Configuration management
├── documentation.html              # User documentation
└── test_categories.html            # Category testing interface

static/
├── css/style.css                   # Main stylesheet
├── js/
│   ├── script.js                   # Main application logic
│   ├── template_editor.js          # Template editor functionality
│   └── dark-mode.js                # Theme switching logic
└── images/                         # Logos and assets

utils/
├── extractor.py                    # DMPExtractor class
└── dmp-three-categories.py         # Category migration utility

uploads/                            # Temporary file storage (cleaned on processing)
outputs/
├── cache/                          # JSON cache files (cache_*.json)
├── dmp/                            # Extracted DMP files
└── reviews/                        # Feedback/review files
```

---

## Development Context

### Current State (v0.8.1)

**Completed Features:**
- ✅ PDF/DOCX upload and processing (max 16MB)
- ✅ OCR support for scanned PDFs (100% success rate)
- ✅ Bilingual Polish/English DMP detection
- ✅ 14-section Science Europe DMP structure extraction
- ✅ Template-based feedback system with categories
- ✅ Dark/Light theme with persistence
- ✅ Character counter, citation tool, quick comments
- ✅ Optimized performance (99.9% faster text similarity, LRU caching)
- ✅ 94.1% extraction success rate (target: 93%)

**Known Limitations:**
- Single-user only (no authentication)
- No multi-user collaboration
- Export only TXT (DOCX/PDF export planned)
- No database (JSON-based storage)
- OCR requires Tesseract installation
- Some complex table structures may not extract perfectly

**Active Development Priorities:**
1. Professional DOCX export for feedback reports
2. File organization (separate folders for DMPs vs reviews)
3. Per-section template customization
4. Smart comment suggestions based on usage history

---

## Code Patterns and Conventions

### Flask Route Pattern

All routes follow this pattern:

```python
@app.route('/endpoint', methods=['GET', 'POST'])
def function_name():
    try:
        # 1. Validate input
        # 2. Process data
        # 3. Return JSON response
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Consistent JSON Response:**
```json
{
  "success": true|false,
  "message": "Human-readable message",
  "data": { /* optional response data */ }
}
```

### DMPExtractor Usage Pattern

```python
from utils.extractor import DMPExtractor

extractor = DMPExtractor()
result = extractor.process_file(file_path, output_dir)

if result['success']:
    filename = result['filename']
    cache_id = result['cache_id']
    # Use cache_id to retrieve extracted content later
```

**Cache System:**
- Cache files: `outputs/cache/cache_{uuid}.json`
- Structure: `{"1.1": {section, question, paragraphs, tagged_paragraphs}, ...}`
- UUID ensures no collisions across concurrent uploads
- Organized folder structure: DMP files in `outputs/dmp/`, reviews in `outputs/reviews/`

### Frontend JavaScript Patterns

**No build tools** - JavaScript is now organized in separate files but served as vanilla JS without bundling

**File Organization:**
- `static/js/script.js` - Main application logic, AJAX handlers, UI interactions
- `static/js/template_editor.js` - Template editor specific functionality
- `static/js/dark-mode.js` - Theme management and persistence

**Common patterns:**
```javascript
// Theme management
localStorage.setItem('dmp-art-theme', 'dark');
document.documentElement.setAttribute('data-theme', 'dark');

// AJAX calls
fetch('/api/endpoint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    if (data.success) { /* handle success */ }
    else { showToast(data.message, 'error'); }
});

// Toast notifications
showToast(message, type); // type: 'success', 'error', 'info', 'warning'
```

### CSS Custom Properties (Theme System)

```css
:root[data-theme="dark"] {
    --bg-main: #1a1a1a;
    --bg-card: #2d2d2d;
    --text-primary: #ecf0f1;
    --primary-color: #5dade2;
}

:root[data-theme="light"] {
    --bg-main: #f5f5f5;
    --bg-card: #ffffff;
    --text-primary: #2c3e50;
    --primary-color: #3498db;
}

/* Use variables everywhere */
body {
    background: var(--bg-main);
    color: var(--text-primary);
}
```

---

## Common Development Tasks

### Adding a New Quick Comment

**1. Edit `config/quick_comments.json`:**
```json
[
  {
    "name": "Missing details",
    "text": "Please provide more specific details about..."
  }
]
```

**2. Changes automatically load** - No code changes needed!

### Adding a New Category

**1. Create `config/new_category.json`:**
```json
{
  "1.1": ["Comment for section 1.1", "Another comment"],
  "1.2": ["Comment for section 1.2"],
  ...
}
```

**2. Restart Flask** - Category appears in Template Editor and Review page

### Adding a New DMP Section

**1. Edit `config/dmp_structure.json`:**
```json
{
  "7. New Main Section": [
    "7.1 First subsection question?",
    "7.2 Second subsection question?"
  ]
}
```

**2. Update `utils/extractor.py`** - Add section mappings if bilingual

**3. Update `templates/review.html`** - Add section IDs to rendering logic

### Modifying Extraction Logic

**File:** `utils/extractor.py`

**Key methods:**
- `process_file()` - Entry point
- `process_docx()` - DOCX extraction
- `process_pdf()` - PDF extraction (with OCR fallback)
- `detect_section_from_text()` - Section detection (4-tier fallback)
- `detect_subsection_from_text()` - Subsection detection
- `improve_content_assignment()` - Content-to-section mapping

**Performance tip:** Pre-compile regex patterns in `__init__()`:
```python
self.skip_patterns_compiled = [
    re.compile(r"Strona \d+", re.IGNORECASE),
    re.compile(r"Page \d+", re.IGNORECASE),
    # ...
]
```

### Adding a New Route

```python
@app.route('/api/new-feature', methods=['POST'])
def new_feature():
    try:
        data = request.json
        # Process data
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        app.logger.error(f'Error in new_feature: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
```

### Current API Routes

**Main Routes:**
- `GET /` - Home/upload page
- `POST /upload` - File upload and processing
- `GET /review/<filename>` - Review interface for extracted DMP
- `GET /download/<filename>` - Download processed files
- `GET /documentation` - User documentation page
- `GET /template_editor` - Template configuration interface
- `GET /test_categories_page` - Category testing interface

**Template Management:**
- `POST /save_templates` - Save DMP question templates
- `POST /save_dmp_structure` - Update DMP structure configuration
- `POST /save_quick_comments` - Save quick comment templates
- `POST /save_category` - Save category configurations
- `POST /save_category_comments` - Save comments for specific category
- `GET /load_categories` - Retrieve available categories
- `GET /load_category_comments` - Get comments for specific category

**Category API:**
- `GET /api/discover-categories` - Discover all available categories
- `POST /api/create-category` - Create new category
- `DELETE /api/delete-category/<category_id>` - Delete category

**Review/Feedback:**
- `POST /save_feedback` - Save review feedback
- `POST /export_json` - Export data as JSON

**Note:** All POST endpoints follow the standard JSON response pattern with `{success: bool, message: string, data: object}` structure.

---

## Testing Guidelines

### Manual Testing Workflow

**1. Upload Test:**
```bash
python app.py
# Open http://localhost:5000
# Upload test file from old/debug_analyzer.py
# Verify: extraction completes without errors
```

**2. Review Page Test:**
```
- Check all 14 sections render
- Test quick comments insertion
- Test category dropdowns
- Verify character counter updates
- Test theme toggle
```

**3. Template Editor Test:**
```
- Edit quick comments → save → verify appears in review page
- Create new category → save → verify in review page
- Edit DMP structure → reload → verify changes
```

### Automated Testing

**Run unit tests:**
```bash
python -m pytest tests/unit/test_extractor.py -v
```

**Run performance benchmarks:**
```bash
python test_extractor_optimization.py
```

**Test real files:**
```bash
python test_real_files.py
# Requires test files in tests/fixtures/
```

### OCR Testing

**Verify OCR is working:**
```bash
tesseract --version  # Should show 5.3+
tesseract --list-langs  # Should include 'pol' and 'eng'
```

**Test scanned PDF:**
```python
from utils.extractor import DMPExtractor
extractor = DMPExtractor()
result = extractor.process_file('path/to/scanned.pdf', 'outputs')
# Check result['success'] and extracted text quality
```

---

## Common Issues and Solutions

### Issue: "No text could be extracted from PDF"

**Cause:** Scanned PDF without OCR
**Solution:**
1. Install Tesseract: `sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng`
2. Install Python packages: `pip install pytesseract pdf2image`
3. System will auto-detect scanned PDFs and apply OCR

### Issue: Section detection not working for non-standard format

**Cause:** Document doesn't follow OSF/NCN standard format
**Solution:** Use 4-tier fallback detection in `detect_section_from_text()`:
1. PDF form patterns (BOLD markers)
2. Numbered sections (regex `^\s*(\d+)\.\s*`)
3. Formatted text markers (BOLD:, UNDERLINED:)
4. Text similarity (Jaccard 0.6 threshold)

### Issue: Text appears in "Unconnected Text"

**Cause:** Content between sections or before DMP start marker
**Solution:** This is expected behavior - users can manually assign. To reduce:
1. Improve `find_dmp_boundaries()` start/end markers
2. Enhance section detection patterns
3. Add more bilingual mappings

### Issue: Upload fails with "File too large"

**Cause:** File > 16MB
**Solution:** Increase limit in `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

---

## Performance Optimizations

### Pre-compiled Regex (Implemented ✅)

**Before:** 0.5ms per similarity check
**After:** 0.0003ms (99.9% faster)

```python
class DMPExtractor:
    def __init__(self):
        # Compile patterns once
        self.skip_patterns_compiled = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in skip_patterns
        ]
```

### LRU Caching (Implemented ✅)

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def _text_similarity(self, text1, text2):
    # Cached for repeated comparisons
    # ...
```

### Lazy Loading (Recommended for Future)

```python
# Instead of loading all content at once:
for paragraph in doc.paragraphs:
    if should_process(paragraph):
        yield extract_formatted_text(paragraph)
```

---

## Security Considerations

### File Upload Security

**Implemented:**
- ✅ File extension validation (PDF/DOCX only)
- ✅ Size limit (16MB max)
- ✅ Secure filename sanitization (`werkzeug.secure_filename()`)
- ✅ DOCX ZIP structure validation
- ✅ Temporary file cleanup after processing

**Missing (not critical for single-user):**
- ❌ CSRF protection (add Flask-WTF for multi-user)
- ❌ Rate limiting
- ❌ User authentication

### XSS Prevention

**Jinja2 auto-escaping:** All variables escaped by default
**JavaScript:** Use `textContent` instead of `innerHTML` for user input

---

## Deployment Notes

### Production Checklist

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install OCR (optional but recommended)
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng poppler-utils

# 3. Create directories
mkdir -p uploads outputs

# 4. Set environment variables
export FLASK_ENV=production
export SECRET_KEY='your-secret-key-here'

# 5. Run with gunicorn (production server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment (Recommended)

```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng \
    poppler-utils
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## Quick Reference

### File Extensions and Processing

| Extension | Library | OCR Support | Success Rate |
|-----------|---------|-------------|--------------|
| .pdf      | PyPDF2  | Yes (Tesseract) | 94.1% |
| .docx     | python-docx | N/A | 94.1% |

### DMP Section IDs

```
1.1, 1.2  # Data description and collection
2.1, 2.2  # Documentation and quality
3.1, 3.2  # Storage and backup
4.1, 4.2  # Legal requirements
5.1, 5.2  # Data sharing and preservation
6.1, 6.2  # Responsibilities and resources
```

### Cache Structure

```json
{
  "1.1": {
    "section": "1. Data description...",
    "question": "How will new data be collected?",
    "paragraphs": ["extracted text", ...],
    "tagged_paragraphs": [
      {"text": "...", "tags": [], "title": "..."}
    ]
  },
  "_unconnected_text": [
    {"text": "...", "type": "no_section"}
  ]
}
```

### Common Git Commands for This Project

```bash
# Check current branch
git status
git branch

# After changes
git add .
git commit -m "Clear, descriptive message"
git push -u origin <branch-name>

# Note: Claude branches start with 'claude/' prefix
# Example: claude/feature-name-sessionid
```

---

## Future Roadmap (From Archived Plans)

**High Priority:**
1. Professional DOCX export for feedback reports
2. File organization (separate DMP/review folders)
3. Per-section template customization
4. Smart comment suggestions

**Medium Priority:**
1. Table structure preservation
2. Analytics and usage tracking
3. Keyboard shortcuts

**Low Priority:**
1. Multi-user support with authentication
2. Database migration (SQLite → PostgreSQL)
3. ML-based section detection
4. OSF API integration

---

## Key Design Decisions (ADRs)

### ADR 1: JSON-based Configuration vs Database

**Decision:** Use JSON files
**Rationale:** Simple deployment, version control friendly, sufficient for single user
**Trade-offs:** ❌ Not suitable for concurrent multi-user, ✅ Easy backup/restore

### ADR 2: UUID-based Cache vs Session Storage

**Decision:** Use UUID-based JSON cache files
**Rationale:** Survives browser refresh, enables bookmarking, debugging friendly
**Trade-offs:** ❌ Disk space accumulates, ✅ Robust state persistence

### ADR 3: Bilingual Processing vs Language Detection

**Decision:** Dual-language mapping with fuzzy matching
**Rationale:** Known vocabulary, more reliable than ML detection
**Trade-offs:** ❌ Manual mapping maintenance, ✅ High accuracy

### ADR 4: Vanilla JavaScript vs Framework

**Decision:** No build tools, vanilla JS
**Rationale:** Simple deployment, fast iteration, low complexity
**Trade-offs:** ❌ No tree-shaking, ✅ Zero build complexity

---

## Working with This Codebase - Best Practices

### Before Starting Work

1. **Understand the context:**
   ```bash
   # Review current state
   git status
   git log --oneline -10

   # Check test results
   cat FINAL_TEST_RESULTS.md
   ```

2. **Run the app:**
   ```bash
   python app.py
   # Open http://localhost:5000
   # Upload a test file, verify basic functionality
   ```

3. **Review relevant code:**
   - For extraction issues: `utils/extractor.py`
   - For UI changes: `templates/review.html` + `static/css/style.css`
   - For routes: `app.py`

### Making Changes

1. **Edit code** - Follow existing patterns
2. **Test locally** - Upload test file, verify changes
3. **Run tests** (if available): `python -m pytest tests/ -v`
4. **Commit with clear message**

### After Changes

1. **Verify functionality:**
   - Upload works
   - Extraction works
   - Review page renders
   - Theme toggle works
   - Comments load correctly

2. **Check for regressions:**
   - Test with known working file
   - Verify extraction accuracy
   - Check console for errors

3. **Document changes:**
   - Update comments if logic changed
   - Note any new dependencies
   - Update README if user-facing

---

## Documentation Structure

**For AI Agents (Primary Documentation):**
- **This file** (`.claude/CLAUDE.md`) - Complete AI agent guide to codebase
- **`HISTORY.md`** - Chronological project history with all major changes
- **`FINAL_TEST_RESULTS.md`** - Current test results and quality metrics
- **`.claude/DOCUMENTATION_GUIDELINES.md`** - Standards for maintaining documentation
- **`README.md`** - Project overview (simplified, GitHub-facing)

**Documentation Principles:**
1. **Single Source of Truth** - Each concept documented in ONE location only
2. **Modify, Don't Create** - Update existing docs rather than create new files
3. **Code References Over Prose** - Link to actual code with file:line references
4. **For AI Agents, Not Humans** - Optimized for code assistants, not end users
5. **Actionable Information** - Every section answers "What does an AI agent need to DO?"

**For Issues:**
- Check `FINAL_TEST_RESULTS.md` for known issues and test results
- Review `HISTORY.md` for historical context and evolution
- Follow patterns documented in this file
- Consult `.claude/DOCUMENTATION_GUIDELINES.md` for documentation best practices

**Remember:** This is a single-user tool optimized for Polish research administrators. Keep it simple, fast, and focused on the core use case.

---

**Last Updated:** 2025-11-23
**Codebase Version:** 0.8.1
**Extraction Success Rate:** 94.1% (tested on 17 real NCN proposals)
**Target Users:** Data stewards at Polish research institutions
**Core Value:** 75% time reduction in DMP review process

---

## Recent Changes (Since Last Update)

### 2025-11-23 Update

**Dependency Updates:**
- Flask upgraded from 3.1.0 to 3.1.1 (security patches)
- Werkzeug 3.1.3 added to dependencies
- Pillow 11.0.0 added for image processing

**Architecture Changes:**
- JavaScript refactored from embedded code to separate modular files:
  - `static/js/script.js` (42KB) - Main application logic
  - `static/js/template_editor.js` (28KB) - Template editor
  - `static/js/dark-mode.js` (4KB) - Theme management
- File organization improved with dedicated folders:
  - `outputs/cache/` for cache files
  - `outputs/dmp/` for extracted DMPs
  - `outputs/reviews/` for feedback files

**Codebase Growth:**
- `utils/extractor.py`: 1,236 → 2,101 lines (+70% more features)
- `templates/review.html`: 1,789 → 2,341 lines (+31% enhanced UI)
- `static/css/style.css`: 980 → 1,596 lines (+63% refined styling)

**New Features:**
- Test categories interface (`test_categories.html`)
- Enhanced category management system
- Improved file organization and naming conventions
