# DMP-ART: Comprehensive Code Review & Refactoring Plan
**Date:** 2025-11-19
**Reviewer Perspective:** Data Steward (Polish research administrator)
**Version:** 0.8.1

---

## Executive Summary

Analyzed 12,734 lines of code across 17 files. Found **4 critical issues**, **7 high-priority improvements**, and **15 UX/layout enhancements**. Overall codebase is functional but needs consolidation and UX improvements.

**Impact Summary:**
- 🔴 **4 Critical** - Unused code, missing directories, duplicate logic
- 🟠 **7 High Priority** - Layout issues, hardcoded categories, file organization
- 🟡 **15 Medium Priority** - UX improvements, responsive design, documentation

---

## CRITICAL ISSUES 🔴

### 1. Missing `uploads/` Directory
**Issue:** App creates `uploads/` on startup but it's not in git
**Location:** `app.py:14-21`
**Impact:** Upload fails on fresh install
**Fix:**
```bash
mkdir -p uploads
echo "*" > uploads/.gitignore
echo "!.gitignore" >> uploads/.gitignore
git add uploads/.gitignore
```

### 2. Unused Flask Route: `/results`
**Issue:** Dead endpoint, template doesn't exist
**Location:** `app.py:399-401`
```python
@app.route('/results')
def results():
    return render_template('results.html')  # ← File doesn't exist
```
**Fix:** DELETE these 3 lines

### 3. Unused Module: `templates_manager.py`
**Issue:** 117 lines of dead code, never imported
**Location:** `/utils/templates_manager.py`
**Functionality:** Duplicated in `app.py`
**Fix:** DELETE entire file

### 4. Duplicate DMP_TEMPLATES Definition
**Issue:** DMP structure defined in TWO places
**Locations:**
- `app.py:31-59` (29 lines)
- `extractor.py:44-85` (42 lines)
**Impact:** Updates must be made twice, risk of inconsistency
**Fix:** Use ONLY `config/dmp_structure.json`, remove both hardcoded copies

---

## HIGH PRIORITY ISSUES 🟠

### 5. Hardcoded Categories in Template Editor
**Issue:** Categories "newcomer", "mising", "ready" are hardcoded
**User Request:** "These three tabs shouldn't be hardcoded and should be possible to change them, rename, or remove"
**Location:** `templates/template_editor.html:70-71`, `static/js/template_editor.js:1-50`
**Current Implementation:**
```html
<button class="tab-btn" data-tab="quick-comments">Quick Comments</button>
<!-- Hardcoded categories -->
```
**Required:** Dynamic category loading from JSON files in `config/`

### 6. Right Sidebar Overlay Issue
**Issue:** Right sidebar overlays content, uses too many `!important` flags
**User Request:** "It shouldn't overlay other elements and should move with scrolling"
**Location:** `templates/review.html:64-80`
**Current Problems:**
- 12 `!important` declarations
- Fixed positioning prevents natural scrolling
- Z-index issues with header
**Fix:** Refactor to `position: sticky` with proper CSS specificity

### 7. Unconnected Text Assignment Timing
**Issue:** Shown after review starts, interrupts workflow
**User Request:** "Move to prompt user gets just after page uploads - to make user assign text to sections before review starts"
**Current:** Modal appears during review
**Required:** Show immediately after upload, before review interface

### 8. No File Organization
**Issue:** DMPs and reviews saved to same `outputs/` folder
**User Request:** "Wyeksportowany DMP ma się zapisywać w jednym folderze, recenzja w drugim, oba pliki mają być ze sobą powiązane"
**Current Structure:**
```
outputs/
├── cache_*.json
├── DMP_*.docx
└── feedback_*.txt  (all mixed together)
```
**Required:**
```
outputs/
├── dmp/              # Extracted DMPs
├── reviews/          # Feedback reports
└── cache/            # JSON cache files
```

### 9. Font Inconsistency
**Issue:** Multiple font families used inconsistently
**Found in:** `style.css`
```css
font-family: 'Segoe UI', Roboto, Arial, sans-serif;  /* Line 12 */
font-family: 'Courier New', monospace;               /* Line 450 */
font-family: Arial, sans-serif;                      /* Line 890 */
```
**Fix:** Define single font stack in CSS variables

### 10. Theme Toggle Duplication
**Issue:** Theme initialization in 3 places
**Locations:**
1. `index.html:12-21` (inline script)
2. `review.html:12-21` (inline script)
3. `static/js/dark-mode.js:1-30`
**Fix:** Use ONLY `dark-mode.js`, remove inline scripts

### 11. Duplicate File Validation
**Issue:** Same function in 2 files
**Locations:**
- `app.py:115-135` (`validate_docx_file()`)
- `extractor.py:276-295` (`validate_docx_file()`)
**Fix:** Keep in `extractor.py`, import in `app.py`

---

## MEDIUM PRIORITY - UX & LAYOUT 🟡

### 12. Responsive Layout Issues

**Problem Areas:**

#### A. Review Page Layout
**File:** `templates/review.html:46-60`
**Issues:**
- Hardcoded `max-width: 1400px` breaks on small screens
- Fixed `margin-right: 290px` causes text cutoff
- Main content `margin-left: 40px` + sidebar width = wasted space

**Current:**
```css
.review-layout {
    max-width: 1400px !important;
    margin: 0 auto !important;
}
.main-content {
    margin-left: 40px !important;
    margin-right: 290px !important;  /* Too specific */
}
```

**Recommended:**
```css
.review-layout {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 2rem;
    max-width: 1600px;
    padding: 2rem;
}
```

#### B. Upload Area Border
**File:** `templates/index.html:55`
```html
<div id="drop-area" style="border: 4px solid var(--warning-color);">
```
**Issue:** Inline style, should be in CSS

#### C. Footer Overlap
**File:** Multiple templates
**Issue:** Footer can overlap content on short pages
**Current:** `position: fixed`
**Fix:** Use `position: sticky` or dynamic positioning

### 13. Spacing & Margins Analysis

**Inconsistent Spacing:**
```css
padding: 20px !important;     /* template_editor.html:14 */
padding: 2rem;                /* review.html:30 */
padding: 15px !important;     /* review.html:74 */
margin-bottom: 5rem;          /* index.html:55 */
gap: 30px !important;         /* review.html:49 */
gap: 2rem;                    /* various */
```

**Recommendation:**
Define spacing scale in CSS variables:
```css
:root {
    --space-xs: 0.5rem;   /* 8px */
    --space-sm: 1rem;     /* 16px */
    --space-md: 1.5rem;   /* 24px */
    --space-lg: 2rem;     /* 32px */
    --space-xl: 3rem;     /* 48px */
}
```

### 14. Contrast & Visibility Issues

**Low Contrast Pairs (WCAG AA failure):**
1. **Disabled nav items:** `opacity: 0.5` on `--text-secondary`
   - Location: `.nav-item.disabled` in `style.css`
   - Contrast ratio: ~2.5:1 (needs 4.5:1)

2. **Placeholder text:** Very light in dark mode
   - Location: `::placeholder` in various inputs

3. **Border colors:** `--border-light` too subtle in light mode
   - Hard to see section boundaries

**Fix:** Increase contrast ratios to meet WCAG AA standards

### 15. Text Area Auto-Expand
**Issue:** Feedback textareas don't auto-grow with content
**User Request:** "unify fonts i rozwijane wraz z tekstem okienko behavior"
**Current:** Fixed height, manual scroll
**Required:** Auto-expand as user types

### 16. Documentation Page Outdated
**File:** `templates/documentation.html`
**Issues:**
- References old file structure
- Missing info on bilingual features
- No mention of OCR support
- Installation steps incomplete
**Fix:** Update to match current v0.8.1 features

### 17. Category Comment Connections
**Issue:** Template editor saves to `config/*.json` but review page loads dynamically
**Files:**
- Save: `static/js/template_editor.js:saveCategory()`
- Load: `static/js/script.js:loadQuickComments()`
**Status:** ✅ Works correctly, but needs documentation

---

## UNUSED DIRECTORIES & FILES

### Directories to Remove:
1. **`/old/`** (157KB)
   - Old debug scripts, legacy CSS, test JSON
   - Not referenced in active code
   - **Action:** DELETE or move to `docs/archive/`

2. **`/pzd/`** (5.5MB)
   - 17 test DMP files
   - Test outputs folder
   - **Action:** KEEP test files, move to `tests/fixtures/`

3. **`/test_outputs/`** (500KB)
   - Old cache files from testing
   - **Action:** DELETE, use `outputs/cache/` instead

4. **`/.vscode/`**
   - Editor configuration
   - **Action:** Add to `.gitignore` if not already

### Files to Remove:
1. `utils/templates_manager.py` (117 lines) - Unused
2. `old/debug_analyzer.py` (21KB) - Legacy tool
3. `old/results.html` (10KB) - Old template
4. `old/style old.csss` (81KB) - Legacy CSS

**Total cleanup:** ~6.2MB, 20+ obsolete files

---

## CODEBASE STATISTICS

### Files by Type:
```
Python:      9 files,  3,787 lines (app.py, extractor.py, utils, tests)
HTML:        5 files,  4,196 lines (templates)
JavaScript:  3 files,  1,653 lines (dark-mode, script, template_editor)
CSS:         1 file,   1,194 lines (unified stylesheet)
JSON:       11 files   (config files + backups)
```

### Duplication Analysis:
```
DMP_TEMPLATES:     71 lines (app.py + extractor.py)
validate_docx:     40 lines (app.py + extractor.py)
Theme init:        30 lines (3× inline scripts)
Border styles:     ~15 lines (repeated patterns)
```

### !important Usage:
```
review.html:       12 instances (right sidebar)
template_editor:    6 instances (layout fixes)
style.css:          8 instances (overrides)
Total:             26 instances ← Should be 0-5 max
```

---

## REFACTORING PRIORITIES

### Phase 1: Critical Fixes (1-2 hours)
1. ✅ Create `uploads/` directory with `.gitignore`
2. ✅ Delete `/results` route (app.py:399-401)
3. ✅ Delete `utils/templates_manager.py`
4. ✅ Consolidate DMP_TEMPLATES to use only `config/dmp_structure.json`
5. ✅ Consolidate `validate_docx_file()` to single location

### Phase 2: High Priority UX (3-4 hours)
6. ✅ Implement dynamic category tabs in template editor
7. ✅ Fix right sidebar positioning (remove !important, use sticky)
8. ✅ Move Unconnected Text assignment to post-upload modal
9. ✅ Create file organization structure (dmp/, reviews/, cache/)
10. ✅ Unify font stack using CSS variables

### Phase 3: Layout & Responsive (2-3 hours)
11. ✅ Refactor review page layout to CSS Grid
12. ✅ Implement spacing scale with CSS variables
13. ✅ Fix contrast issues for WCAG AA compliance
14. ✅ Make textareas auto-expand
15. ✅ Remove inline styles, consolidate to style.css

### Phase 4: Code Cleanup (1-2 hours)
16. ✅ Consolidate theme initialization
17. ✅ Remove unused directories (/old/, /test_outputs/)
18. ✅ Move test DMPs to tests/fixtures/
19. ✅ Update documentation.html
20. ✅ Remove all !important declarations where possible

---

## IMPLEMENTATION RECOMMENDATIONS

### Immediate Actions (Today):
```bash
# 1. Create missing directory
mkdir -p uploads && echo "*" > uploads/.gitignore && echo "!.gitignore" >> uploads/.gitignore

# 2. Remove unused code
rm utils/templates_manager.py
rm -rf old/
rm -rf test_outputs/

# 3. Move test files
mkdir -p tests/fixtures
mv pzd/*.docx pzd/*.pdf tests/fixtures/
rm -rf pzd/
```

### Code Changes:
1. **app.py** - Remove DMP_TEMPLATES, /results route, duplicate validation
2. **extractor.py** - Load DMP structure from JSON, not hardcoded
3. **review.html** - Refactor layout, fix sidebar, remove !important
4. **template_editor.html** - Dynamic category loading
5. **style.css** - Add spacing scale, fix contrast, remove !important

### Testing Checklist:
- [ ] Upload PDF/DOCX works
- [ ] Extraction completes successfully
- [ ] Review page loads correctly
- [ ] Sidebar scrolls properly
- [ ] Template editor loads all categories dynamically
- [ ] Theme toggle works without flashing
- [ ] Unconnected text modal appears post-upload
- [ ] File organization creates correct folders
- [ ] Contrast passes WCAG AA validator
- [ ] Layout works on 1920x1080, 1366x768, 1440x900

---

## FILES REQUIRING CHANGES

### Critical Files (Must Edit):
1. `app.py` - Remove duplicates, fix routes (4 changes)
2. `templates/review.html` - Layout refactor, sidebar fix (major)
3. `templates/template_editor.html` - Dynamic categories (major)
4. `static/js/template_editor.js` - Category management (moderate)
5. `static/css/style.css` - Spacing, contrast, layout (major)

### Supporting Files:
6. `static/js/dark-mode.js` - Consolidate theme init
7. `templates/index.html` - Remove inline theme script
8. `templates/documentation.html` - Update content
9. `utils/extractor.py` - Load structure from JSON

### Configuration:
10. Create `uploads/.gitignore`
11. Update `.gitignore` to exclude .vscode/

---

## EXPECTED IMPROVEMENTS

### Performance:
- **Removed Code:** ~200 lines duplicate code
- **Deleted Files:** ~6.2MB obsolete content
- **!important Reduction:** 26 → 5-8 instances

### UX:
- **Right Sidebar:** Proper sticky positioning
- **Unconnected Text:** Better workflow timing
- **File Organization:** Clear DMP/review separation
- **Responsive Layout:** CSS Grid, proper spacing
- **Contrast:** WCAG AA compliance

### Maintainability:
- **DMP Structure:** Single source of truth (JSON)
- **Categories:** Fully dynamic, user-configurable
- **Font System:** Consistent across all pages
- **Spacing:** Predictable scale
- **Theme Toggle:** Single implementation

---

## CONCLUSION

The codebase is **functional and well-structured** but has accumulated technical debt. Main issues:

1. **Duplication** - DMP structure, validation, theme init
2. **Hardcoding** - Categories, spacing, layout values
3. **CSS Specificity Wars** - Too many !important flags
4. **Missing Features** - File organization, dynamic categories
5. **Obsolete Code** - Unused routes, modules, directories

**Recommended Approach:**
1. Start with Phase 1 (critical fixes) - 1-2 hours
2. Proceed to Phase 2 (UX improvements) - 3-4 hours
3. Complete Phase 3 (layout) - 2-3 hours
4. Finish with Phase 4 (cleanup) - 1-2 hours

**Total Estimated Time:** 8-12 hours for complete refactoring

**Risk Level:** LOW
- Changes are well-isolated
- Existing functionality preserved
- Incremental implementation possible
- Comprehensive testing checkpoints

---

**Review Complete:** 2025-11-19
**Next Steps:** Implement Phase 1 critical fixes
**Approver:** Data Steward / Project Owner
