# DMP-ART — Copilot/Claude Onboarding

**Version:** 0.9.1+ | **Last Validated:** 2026-03-11 | **Success Rate:** 94.1%

For full context, read `.claude/CLAUDE.md` first. This file is a quick onboarding reference.

---

## What This Project Is

Single-user Flask web app for Polish data stewards reviewing NCN grant proposal DMPs.
Upload PDF/DOCX → auto-extract 14 Science Europe sections → write feedback → export TXT.

**Stack:** Python 3.8+ / Flask 3.1.1 / PyPDF2 / python-docx / Vanilla JS / JSON storage (no DB)

---

## Installation

```bash
# On Debian/Ubuntu: use --ignore-installed blinker to avoid system package conflict
pip install --ignore-installed blinker -r requirements.txt

mkdir -p uploads outputs/cache outputs/dmp outputs/reviews

python app.py   # http://localhost:5000
```

Optional OCR for scanned PDFs:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng poppler-utils
pip install pytesseract pdf2image
```

---

## Critical Files

| File | Purpose |
|------|---------|
| `app.py` (~1,550 lines) | All Flask routes |
| `utils/extractor.py` (2,101 lines) | Core DMP extraction engine |
| `templates/review.html` (2,341 lines) | Main review UI |
| `static/css/style.css` (1,596 lines) | Dark/light theme CSS |
| `static/js/script.js` (42KB) | Main app JS |
| `static/js/dark-mode.js` (4KB) | Theme management |
| `config/dmp_structure.json` | 14-section DMP structure (do not delete) |
| `config/ai/ai_config.json` | AI module settings & API keys |

---

## Key Patterns

**Documentation rule — NEVER create new `.md` files:**
```
❌ FORBIDDEN: EXTRACTION_ANALYSIS.md, *_REPORT.md, *_PLAN.md, *_SUMMARY.md, *_NOTES.md
✅ INSTEAD: Update .claude/CLAUDE.md (for patterns/findings) or HISTORY.md (for changes)
```

**Flask route standard:**
```python
@app.route('/api/endpoint', methods=['POST'])
def function_name():
    try:
        data = request.json
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**CSS hidden elements — CRITICAL:**
```css
.hidden { display: none !important; }
```
Always use `classList.add/remove('hidden')`, never `element.style.display`.

**Nav header structure (all pages):**
```html
<nav class="header-nav">
    <div class="header-left-controls">  <!-- theme toggle + lang switcher -->
        <button class="theme-toggle">...</button>
    </div>
    <div class="nav-links">  <!-- margin-left: auto → right-aligned -->
        <a href="/settings" class="nav-item" data-page="settings">Settings</a>
        ...
    </div>
</nav>
```

---

## Main Routes

- `GET /` — upload page
- `POST /upload` — file processing
- `GET /review/<filename>` — review interface
- `GET /settings` — unified settings page (templates, comments, AI, general)
- `GET /documentation` — user docs
- `GET /api/discover-categories` — list categories
- `POST /api/ai/suggest` — AI review suggestions
- `GET/POST /api/settings/general` — upload size and general config

---

## Testing

No pytest configuration currently — runnable scripts plus some `unittest` modules:
```bash
python tests/validate_all_requirements.py
python tests/test_feedback_folder.py
python tests/test_integration_workflow.py
python tests/test_extractor_optimization.py   # performance benchmarks
# tests/test_real_files.py and tests/test_pzd_extraction.py require local data in tests/pzd/
# both diagnostics are non-interactive and exit gracefully when the dataset is absent
```

Manual checklist after changes:
1. Upload PDF/DOCX → extraction completes
2. Review page shows all 14 sections
3. Theme toggle persists
4. Quick comments load in dropdowns
5. Export TXT works

---

## Desktop-Only

No mobile/responsive design. Target users work on desktop. Do not add mobile breakpoints.

---

## Known Issues

- `pip install` fails with "Cannot uninstall blinker" → add `--ignore-installed blinker`
- Scanned PDFs produce no text without Tesseract
- `tests/test_real_files.py` and `tests/test_pzd_extraction.py` skip gracefully without `tests/pzd/`
- Upload size limit is configurable via `/settings` (default 16 MB)
