# DMP-ART Web Client Extraction & UX Unification Plan

## Executive Summary

This document outlines the comprehensive plan to extract the web client from the DMP-ART Flask application, unify the design system, and improve UX/accessibility. Based on detailed architecture analysis, this plan addresses 106 `!important` declarations, inconsistent styling, tight server coupling, and accessibility gaps.

---

## Current State Analysis

### Application Overview
- **Total Lines of Code**: ~6,000 lines (HTML/CSS/JS combined)
- **Templates**: 4 HTML files (index, review, template_editor, documentation)
- **JavaScript**: ~2,700 lines (script.js, dark-mode.js, inline scripts)
- **CSS**: 1,067 lines (style.css) + 678 lines inline in review.html

### Critical Issues Identified

1. **CSS Technical Debt**
   - 106 `!important` declarations in review.html inline styles
   - 678 lines of inline CSS in review.html
   - Hardcoded colors not using CSS variables
   - Incomplete/orphaned CSS rules

2. **Inconsistent Design System**
   - Header structure varies across pages (4 different implementations)
   - Footer positioning inconsistent (fixed vs relative)
   - Body padding-top: 70px (default), 90px (index), 100px (review)
   - 6+ button class variants with overlapping styles
   - Mixed typography (multiple font families, inconsistent sizes)

3. **Responsive Design Issues**
   - Conflicting breakpoints (768 vs 900, 1199 vs 1200)
   - Review sidebar has TWO conflicting responsive rules
   - Z-index: 999999 (excessive, now fixed to 1002)
   - Mobile sidebar behavior broken <1200px

4. **Accessibility Gaps**
   - Missing ARIA landmarks (role="navigation", role="main")
   - Some focus indicators removed by custom styles
   - Citation highlight color may not meet WCAG AA contrast
   - No skip-to-content link

5. **Server-Client Coupling**
   - All pages server-rendered with Jinja2
   - No client-side routing
   - No API-first architecture
   - Review data embedded in HTML instead of fetched via API

---

## Fixes Completed ✅

### Sprint 1: Critical Bug Fixes (Completed)

1. **Fixed Broken CSS Rule** ([review.html:124](c:\Users\kraje\OneDrive\Pulpit\dmp-extractor\templates\review.html#L124))
   - **Issue**: Incomplete CSS rule `float: none !important;` without selector
   - **Fix**: Removed orphaned CSS code
   - **Impact**: Eliminates console errors, improves CSS validity

2. **Consolidatedall CSS Variables**
   - **Issue**: Hardcoded colors `#2d5016`, `#4a7c59`, `orange` not using variables
   - **Fixes**:
     - Added `--section-title-color: #2d5016` (light mode)
     - Added `--subsection-title-color: #4a7c59` (light mode)
     - Added `--section-title-color: #86efac` (dark mode)
     - Added `--subsection-title-color: #6ee7b7` (dark mode)
     - Updated `index.html` border: `var(--warning-color)` instead of `orange`
     - Updated `review.html` titles to use CSS variables
   - **Files Modified**:
     - `static/css/style.css` (added 4 new variables)
     - `templates/index.html` (line 50)
     - `templates/review.html` (lines 141, 148)
   - **Impact**: Consistent theming, easier maintenance, proper dark mode support

3. **Fixed Critical Z-Index Issue** ([review.html:76](c:\Users\kraje\OneDrive\Pulpit\dmp-extractor\templates\review.html#L76))
   - **Issue**: Sidebar z-index: 999999 (excessive)
   - **Fix**: Reduced to z-index: 1002 (above header:1000, theme-toggle:1001)
   - **Impact**: Proper stacking context, maintainable z-index hierarchy

4. **Fixed Incomplete Navigation** ([template_editor.html:56](c:\Users\kraje\OneDrive\Pulpit\dmp-extractor\templates\template_editor.html#L56))
   - **Issue**: Alert placeholder `onclick="alert('...')"`for Review link
   - **Fix**: Changed to disabled span with tooltip
   - **Impact**: Better UX, no jarring alerts, accessible tooltip

---

## Remaining Work (Prioritized)

### Phase 1: Design System Unification (High Priority)

#### 1.1 Header Standardization

**Current State:**
- **index.html**: "Customize Templates" + "Documentation" + Theme toggle
- **review.html**: Split nav (left: Home/Templates/Docs | right: subtitle + Theme toggle)
- **template_editor.html**: Home + disabled Review + Template Editor + Theme toggle
- **documentation.html**: Home + Customize Templates + Theme toggle

**Proposed Standard:**
```html
<!-- Standard header for all pages except index -->
<header class="fixed-header">
    <nav class="header-nav">
        <a href="/" class="nav-item">Home</a>
        <a href="/template_editor" class="nav-item">Template Editor</a>
        <a href="/documentation" class="nav-item">Documentation</a>
        <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
            <i class="fas fa-moon"></i>
        </button>
    </nav>
</header>

<!-- Index page (no Home link since we're on home) -->
<header class="fixed-header">
    <nav class="header-nav">
        <a href="/template_editor" class="nav-item">Template Editor</a>
        <a href="/documentation" class="nav-item">Documentation</a>
        <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">
            <i class="fas fa-moon"></i>
        </button>
    </nav>
</header>
```

**Implementation Tasks:**
- [ ] Update `index.html` header (add consistent class names)
- [ ] Update `template_editor.html` header (simplify navigation)
- [ ] Update `documentation.html` header (add missing links)
- [ ] Review page keeps custom split header (unique requirement)
- [ ] Add active state styling: `.nav-item.active`

#### 1.2 Footer Standardization

**Current State:**
- Index/Documentation: `position: fixed`, bottom: 0
- Review: `position: relative`, z-index: 1001
- Template Editor: `position: relative`, z-index: 1

**Proposed Standard:**
```css
.site-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 100; /* Below header (1000) but above content */
}
```

**Implementation Tasks:**
- [ ] Standardize footer positioning in `style.css`
- [ ] Remove inline footer styles from templates
- [ ] Test footer doesn't cover content on all pages

#### 1.3 Typography System

**Current Issues:**
- Mixed font sizes: `.85rem`, `16px`, `clamp(1rem, 1.5vw, 1.4rem)`, `.8rem`
- Inconsistent heading scales
- No defined type ramp

**Proposed System:**
```css
:root {
    /* Base */
    --font-size-base: 1rem; /* 16px */

    /* Type Scale (1.25 ratio) */
    --font-size-xs: 0.75rem;   /* 12px */
    --font-size-sm: 0.875rem;  /* 14px */
    --font-size-md: 1rem;      /* 16px */
    --font-size-lg: 1.125rem;  /* 18px */
    --font-size-xl: 1.25rem;   /* 20px */
    --font-size-2xl: 1.5rem;   /* 24px */
    --font-size-3xl: 1.875rem; /* 30px */
    --font-size-4xl: 2.25rem;  /* 36px */

    /* Headings */
    --h1-size: var(--font-size-4xl);
    --h2-size: var(--font-size-3xl);
    --h3-size: var(--font-size-2xl);
    --h4-size: var(--font-size-xl);
    --h5-size: var(--font-size-lg);
    --h6-size: var(--font-size-md);

    /* Font Families */
    --font-family-base: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --font-family-mono: "Consolas", "Menlo", "Monaco", monospace;
}
```

**Implementation Tasks:**
- [ ] Add typography variables to `style.css`
- [ ] Update all font-size declarations to use variables
- [ ] Create consistent heading styles (h1-h6)
- [ ] Document typography usage in style guide

#### 1.4 Spacing Scale System

**Current Issues:**
- Mixed spacing units: `1.5em`, `2em`, `clamp()`, `8px`, `16px`
- No consistent spacing rhythm
- Hard to maintain alignment

**Proposed System (8px base):**
```css
:root {
    --spacing-1: 0.25rem;  /* 4px */
    --spacing-2: 0.5rem;   /* 8px */
    --spacing-3: 0.75rem;  /* 12px */
    --spacing-4: 1rem;     /* 16px */
    --spacing-5: 1.5rem;   /* 24px */
    --spacing-6: 2rem;     /* 32px */
    --spacing-8: 3rem;     /* 48px */
    --spacing-10: 4rem;    /* 64px */
}
```

**Implementation Tasks:**
- [ ] Add spacing variables to `style.css`
- [ ] Replace hardcoded margins/padding with variables
- [ ] Update clamp() functions to use spacing scale
- [ ] Test spacing consistency across pages

#### 1.5 Button System Consolidation

**Current Issues:**
- 6+ button classes: `.primary-btn`, `.secondary-btn`, `.action-btn`, `.btn`, `.button`, `.save-btn`, `.add-btn`
- Duplicate CSS rules (lines 436-589)
- Inconsistent hover/focus states

**Proposed System (BEM naming):**
```css
/* Base button */
.btn {
    padding: var(--spacing-3) var(--spacing-5);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-md);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

/* Variants */
.btn--primary {
    background: var(--primary-color);
    color: white;
}

.btn--secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-light);
}

.btn--danger {
    background: var(--error-color);
    color: white;
}

.btn--ghost {
    background: transparent;
    color: var(--primary-color);
    border: 1px solid var(--primary-color);
}

/* States */
.btn:hover { /* hover styles */ }
.btn:focus { /* focus styles */ }
.btn:active { /* active styles */ }
.btn:disabled { /* disabled styles */ }
```

**Implementation Tasks:**
- [ ] Create new button system in `style.css`
- [ ] Update all button usages in templates
- [ ] Remove old button classes (`.primary-btn`, etc.)
- [ ] Test all button states (hover, focus, active, disabled)

#### 1.6 Responsive Breakpoints

**Current Issues:**
- Inconsistent breakpoints: 480px, 768px, 900px, 1199px, 1200px
- Conflicting media queries (1199 vs 1200)

**Proposed Standard:**
```css
/* Mobile First Approach */
:root {
    --breakpoint-sm: 30rem;    /* 480px - Mobile landscape */
    --breakpoint-md: 48rem;    /* 768px - Tablet */
    --breakpoint-lg: 64rem;    /* 1024px - Desktop */
    --breakpoint-xl: 80rem;    /* 1280px - Large desktop */
}

/* Usage */
@media (min-width: 48rem) { /* Tablet+ */ }
@media (min-width: 64rem) { /* Desktop+ */ }
@media (min-width: 80rem) { /* Large desktop+ */ }
```

**Implementation Tasks:**
- [ ] Consolidate all breakpoints to 4 standard values
- [ ] Update review.html sidebar responsive rules
- [ ] Fix conflicting 1199px/1200px breakpoints
- [ ] Test responsive behavior at all breakpoints

---

### Phase 2: CSS Refactoring (High Priority)

#### 2.1 Extract Inline CSS from review.html

**Scope**: 678 lines of inline CSS → Move to `style.css`

**Strategy:**
1. **Group related rules** (sidebar, question cards, typography, responsive)
2. **Remove !important** by using proper CSS specificity
3. **Use page-specific selectors** when needed: `body[data-page="review"]`
4. **Consolidate duplicate rules**

**Implementation Plan:**
```css
/* In style.css - Review Page Specific Styles */

/* Layout */
body[data-page="review"] .review-layout {
    display: block;
    gap: 0;
    max-width: none;
    margin: 0;
    padding: 20px;
    position: relative;
}

/* Sidebar (no !important needed with proper specificity) */
body[data-page="review"] aside.right-sidebar {
    position: fixed;
    top: 80px;
    right: 20px;
    bottom: 60px;
    width: 250px;
    background-color: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 15px;
    overflow-y: auto;
    z-index: 1002;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    display: block;
}

/* ... rest of review styles */
```

**Tasks:**
- [ ] Create `/* REVIEW PAGE STYLES */` section in style.css
- [ ] Copy inline styles from review.html
- [ ] Remove !important by increasing specificity
- [ ] Test review page appearance unchanged
- [ ] Delete inline `<style>` block from review.html
- [ ] Verify no regressions

**Expected Impact:**
- ✅ Zero !important declarations
- ✅ Maintainable CSS in one location
- ✅ Faster page load (no inline styles blocking)
- ✅ Better caching (external stylesheet)

---

### Phase 3: Client-Server Separation (Medium Priority)

#### 3.1 Create REST API Layer

**New Endpoints to Implement:**

```python
# app.py - New API routes

@app.route('/api/v1/dmp/<cache_id>', methods=['GET'])
def get_dmp_content(cache_id):
    """Get extracted DMP content by cache ID"""
    # Return JSON instead of rendering HTML
    pass

@app.route('/api/v1/categories', methods=['GET'])
def list_categories():
    """List all available feedback categories"""
    pass

@app.route('/api/v1/categories/<name>', methods=['GET'])
def get_category(name):
    """Get specific category details"""
    pass

@app.route('/api/v1/reviews/<cache_id>/feedback', methods=['POST'])
def save_review_feedback(cache_id):
    """Save feedback for a review session"""
    pass

@app.route('/api/v1/reviews/<cache_id>/export', methods=['GET'])
def export_review(cache_id):
    """Export review in various formats (JSON, TXT, DOCX)"""
    pass

@app.route('/api/v1/quick-comments', methods=['GET', 'POST'])
def manage_quick_comments():
    """Get or update quick comments"""
    pass
```

**Tasks:**
- [ ] Implement API endpoints in `app.py`
- [ ] Add proper error handling (404, 500)
- [ ] Add request validation
- [ ] Add API documentation (Swagger/OpenAPI)
- [ ] Test all endpoints with Postman/curl

#### 3.2 Refactor Upload Page (SPA Approach)

**Current Flow:**
1. Upload file → Server processes → Redirect to review page
2. Review page server-renders with data embedded in HTML

**Proposed Flow:**
1. Upload file → Server processes → Return JSON with cache_id
2. Client fetches `/api/v1/dmp/<cache_id>` → Renders review interface

**Implementation:**
```javascript
// In script.js - Updated upload handler

async function handleUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Upload and process
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // Instead of redirecting, fetch data via API
            const cacheId = result.cache_id;
            const dmpData = await fetch(`/api/v1/dmp/${cacheId}`).then(r => r.json());

            // Client-side navigation
            window.history.pushState({ cacheId }, '', `/review?cache_id=${cacheId}`);

            // Render review interface
            renderReviewPage(dmpData);
        }
    } catch (error) {
        showError(error.message);
    }
}
```

**Tasks:**
- [ ] Update upload handler to use fetch API
- [ ] Implement client-side review rendering
- [ ] Add loading states during processing
- [ ] Handle errors gracefully
- [ ] Test upload → review flow

#### 3.3 Client-Side State Management

**Options:**
1. **Vanilla JS** (current approach, ~200 LOC for basic state)
2. **Lightweight library** (Zustand, Valtio - ~5KB)
3. **Full framework** (React + Redux - requires major refactoring)

**Recommended: Vanilla JS with simple state object**

```javascript
// state.js - Simple state management

const AppState = {
    currentReview: null,
    categories: {},
    quickComments: [],
    isDarkMode: false,

    // Getters
    getCurrentReview() {
        return this.currentReview;
    },

    // Setters
    setCurrentReview(data) {
        this.currentReview = data;
        this.notifyListeners('review');
    },

    // Observers
    listeners: {},
    subscribe(key, callback) {
        if (!this.listeners[key]) this.listeners[key] = [];
        this.listeners[key].push(callback);
    },
    notifyListeners(key) {
        if (this.listeners[key]) {
            this.listeners[key].forEach(cb => cb(this[key]));
        }
    }
};
```

**Tasks:**
- [ ] Create `static/js/state.js` module
- [ ] Implement state management
- [ ] Refactor review page to use state
- [ ] Add localStorage persistence
- [ ] Test state updates across components

---

### Phase 4: UX Enhancements (Medium Priority)

#### 4.1 Loading States

**Current Issues:**
- No visual feedback during file upload processing
- Category comments load via AJAX with no indicator
- Review page loads with no skeleton screens

**Implementation:**

```html
<!-- Loading spinner component -->
<div class="loading-spinner" style="display: none;">
    <div class="spinner"></div>
    <p>Processing document...</p>
</div>

<!-- Skeleton screen for review cards -->
<div class="skeleton-card">
    <div class="skeleton-title"></div>
    <div class="skeleton-text"></div>
    <div class="skeleton-text"></div>
</div>
```

```css
/* Spinner styles */
.loading-spinner {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 9999;
}

.spinner {
    border: 4px solid var(--border-light);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Skeleton screens */
.skeleton-card {
    background: var(--bg-card);
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

.skeleton-title,
.skeleton-text {
    height: 1rem;
    background: linear-gradient(
        90deg,
        var(--bg-secondary) 25%,
        var(--bg-tertiary) 50%,
        var(--bg-secondary) 75%
    );
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

.skeleton-title {
    height: 1.5rem;
    width: 60%;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

**Tasks:**
- [ ] Create loading spinner component
- [ ] Add skeleton screens for review page
- [ ] Show spinner during file upload
- [ ] Show skeleton while fetching categories
- [ ] Add progress bar for long operations (0-100%)

#### 4.2 Error Handling

**Current Issues:**
- Inconsistent error display (toast + inline messages)
- Network errors not handled gracefully
- No user-friendly error messages

**Proposed System:**

```javascript
// errors.js - Centralized error handling

class ErrorHandler {
    static show(message, type = 'error', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = message;

        document.body.appendChild(toast);

        // Auto-dismiss
        setTimeout(() => {
            toast.classList.add('toast--dismissing');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    static handleFetchError(error) {
        if (!navigator.onLine) {
            this.show('No internet connection. Please check your network.', 'error');
        } else if (error.message === 'Failed to fetch') {
            this.show('Unable to connect to server. Please try again.', 'error');
        } else {
            this.show(`Error: ${error.message}`, 'error');
        }
    }
}

// Usage
try {
    const response = await fetch('/api/endpoint');
    if (!response.ok) throw new Error(response.statusText);
    const data = await response.json();
} catch (error) {
    ErrorHandler.handleFetchError(error);
}
```

**Tasks:**
- [ ] Create centralized error handler
- [ ] Add toast notification system
- [ ] Handle network timeouts (add timeout to fetch)
- [ ] Show user-friendly error messages
- [ ] Add retry functionality for failed requests

#### 4.3 Autosave & Unsaved Changes

**Features to Implement:**
1. Auto-save feedback every 30 seconds
2. "Unsaved changes" indicator
3. Confirmation dialog before leaving with unsaved data

```javascript
// autosave.js

class AutoSave {
    constructor(saveCallback, interval = 30000) {
        this.saveCallback = saveCallback;
        this.interval = interval;
        this.timer = null;
        this.hasUnsavedChanges = false;
    }

    start() {
        this.timer = setInterval(() => {
            if (this.hasUnsavedChanges) {
                this.save();
            }
        }, this.interval);

        // Warn before leaving
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }

    markDirty() {
        this.hasUnsavedChanges = true;
        this.updateIndicator();
    }

    async save() {
        try {
            await this.saveCallback();
            this.hasUnsavedChanges = false;
            this.updateIndicator();
            this.showSaveConfirmation();
        } catch (error) {
            console.error('Autosave failed:', error);
        }
    }

    updateIndicator() {
        const indicator = document.getElementById('save-indicator');
        indicator.textContent = this.hasUnsavedChanges
            ? 'Unsaved changes'
            : 'All changes saved';
        indicator.className = this.hasUnsavedChanges
            ? 'save-indicator--unsaved'
            : 'save-indicator--saved';
    }
}

// Usage in review page
const autoSave = new AutoSave(async () => {
    const feedbackData = collectFeedback();
    await fetch('/save_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
    });
});

document.querySelectorAll('textarea').forEach(textarea => {
    textarea.addEventListener('input', () => autoSave.markDirty());
});

autoSave.start();
```

**Tasks:**
- [ ] Implement autosave class
- [ ] Add save indicator UI
- [ ] Add beforeunload warning
- [ ] Test autosave functionality
- [ ] Handle save conflicts (multiple tabs)

#### 4.4 Keyboard Navigation

**Current Issues:**
- Cite button not keyboard accessible
- Category dropdowns not keyboard navigable
- No skip-to-content link

**Implementation:**

```html
<!-- Skip to content link (hidden until focused) -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<main id="main-content">
    <!-- Page content -->
</main>
```

```css
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--primary-color);
    color: white;
    padding: 8px;
    text-decoration: none;
    z-index: 10000;
}

.skip-link:focus {
    top: 0;
}
```

**Keyboard Shortcuts:**
- `Ctrl+Shift+D`: Toggle dark mode (existing)
- `Ctrl+S`: Save feedback
- `Ctrl+K`: Open quick comments
- `/`: Focus search (if implemented)
- `Esc`: Close modals/dropdowns

**Tasks:**
- [ ] Add skip-to-content link
- [ ] Make cite button keyboard accessible (tabindex="0", keydown handler)
- [ ] Add keyboard navigation to category dropdowns
- [ ] Implement keyboard shortcuts
- [ ] Add shortcuts documentation modal (? key)
- [ ] Test with keyboard only (no mouse)

---

### Phase 5: Accessibility (WCAG 2.1 AA) (High Priority)

#### 5.1 ARIA Landmarks

**Implementation:**

```html
<!-- Before -->
<header class="fixed-header">...</header>
<div class="main-content">...</div>
<footer class="site-footer">...</footer>

<!-- After -->
<header class="fixed-header" role="banner">
    <nav role="navigation" aria-label="Main navigation">...</nav>
</header>

<main role="main" id="main-content">
    <aside role="complementary" aria-label="Quick navigation">...</aside>
    <article role="article">...</article>
</main>

<footer class="site-footer" role="contentinfo">...</footer>
```

**Tasks:**
- [ ] Add role="banner" to headers
- [ ] Add role="navigation" with aria-label to navs
- [ ] Add role="main" to main content areas
- [ ] Add role="complementary" to sidebars
- [ ] Add role="contentinfo" to footers
- [ ] Test with screen reader (NVDA/JAWS)

#### 5.2 Color Contrast

**Current Issues:**
- Citation highlight `#ffe066` on white may not meet 4.5:1 ratio
- Some button states have low contrast

**Color Contrast Requirements (WCAG AA):**
- Normal text: 4.5:1 minimum
- Large text (18pt+ or 14pt+ bold): 3:1 minimum

**Tools:**
- WebAIM Color Contrast Checker
- Chrome DevTools Lighthouse

**Tasks:**
- [ ] Audit all text/background combinations
- [ ] Fix citation highlight color if needed
- [ ] Ensure button states meet contrast requirements
- [ ] Test with color blindness simulator
- [ ] Document color usage guidelines

#### 5.3 Focus Management

**Implementation:**

```css
/* Visible focus indicators */
*:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Custom focus styles for buttons */
.btn:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(91, 188, 255, 0.25);
}

/* Focus trap for modals */
.modal[aria-modal="true"] {
    /* Implemented via JavaScript */
}
```

```javascript
// Focus trap implementation
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', (e) => {
        if (e.key !== 'Tab') return;

        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    });

    firstFocusable.focus();
}
```

**Tasks:**
- [ ] Restore focus indicators removed by custom styles
- [ ] Add custom focus styles for all interactive elements
- [ ] Implement focus trapping in modals
- [ ] Ensure focus visible on keyboard navigation
- [ ] Test tab order is logical

#### 5.4 Screen Reader Support

**Implementation:**

```html
<!-- Section navigation buttons with descriptive labels -->
<button class="nav-grid-btn" aria-label="Navigate to section 1.1: How will new data be collected?">
    1.1
</button>

<!-- Category buttons with aria-describedby -->
<button class="category-btn" aria-describedby="category-desc-newcomer">
    Newcomer Guidance
</button>
<span id="category-desc-newcomer" class="sr-only">
    Pre-configured feedback templates for common newcomer issues
</span>

<!-- Modal dialogs with aria-modal -->
<div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <h2 id="modal-title">Compiled Feedback</h2>
    <!-- Modal content -->
</div>

<!-- Live regions for dynamic content -->
<div aria-live="polite" aria-atomic="true" class="sr-only" id="status-messages"></div>
```

```css
/* Screen reader only class */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

**Tasks:**
- [ ] Add aria-label to all buttons with icons only
- [ ] Add aria-describedby for additional context
- [ ] Implement aria-modal for dialogs
- [ ] Add aria-live regions for status messages
- [ ] Create .sr-only utility class
- [ ] Test with NVDA screen reader

---

## Implementation Timeline

### Sprint 1: Foundation (3-5 days) - COMPLETED ✅
- [x] Fix critical CSS bugs
- [x] Consolidate CSS variables
- [x] Fix z-index hierarchy
- [x] Fix incomplete navigation

### Sprint 2: Design System (5-7 days) - IN PROGRESS
- [ ] Standardize headers
- [ ] Standardize footers
- [ ] Create typography system
- [ ] Create spacing scale
- [ ] Consolidate button system
- [ ] Fix responsive breakpoints

### Sprint 3: CSS Refactoring (3-5 days)
- [ ] Extract review.html inline styles
- [ ] Remove !important declarations
- [ ] Consolidate duplicate rules
- [ ] Test visual regression

### Sprint 4: UX Enhancements (5-7 days)
- [ ] Add loading states
- [ ] Implement error handling
- [ ] Add autosave
- [ ] Implement keyboard navigation

### Sprint 5: Accessibility (3-5 days)
- [ ] Add ARIA landmarks
- [ ] Fix color contrast
- [ ] Implement focus management
- [ ] Add screen reader support

### Sprint 6: API & Client Separation (7-10 days)
- [ ] Create REST API layer
- [ ] Refactor upload page (SPA)
- [ ] Client-side state management
- [ ] Update review page to use API

### Sprint 7: Testing & Documentation (3-5 days)
- [ ] Unit tests for JavaScript
- [ ] Integration tests for APIs
- [ ] E2E tests for critical flows
- [ ] Update documentation
- [ ] Performance audit

**Total Estimated Time**: 29-44 days (6-9 weeks)

---

## Success Metrics

### Technical Metrics
- ✅ Zero `!important` declarations (currently 106)
- ✅ <3s page load time
- ✅ Lighthouse score >90 (Performance, Accessibility, Best Practices)
- ✅ Zero console errors/warnings
- ✅ 80%+ test coverage

### Accessibility Metrics
- ✅ WCAG 2.1 AA compliance (100%)
- ✅ Keyboard navigation functional
- ✅ Screen reader compatible
- ✅ 4.5:1 color contrast ratio (all text)

### Code Quality Metrics
- ✅ CSS in external stylesheet (no inline styles)
- ✅ Consistent design tokens
- ✅ DRY (Don't Repeat Yourself) - no duplicate CSS
- ✅ Semantic HTML5
- ✅ BEM or consistent naming convention

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize features** based on business needs
3. **Set up development environment** (linters, testing framework)
4. **Create feature branches** for each sprint
5. **Begin Sprint 2** (Design System)

---

## Questions for Decision

1. **Framework Choice**: Stay vanilla JS or migrate to React/Vue for client separation?
2. **API Versioning**: Use `/api/v1/` prefix from start?
3. **State Management**: Vanilla JS, lightweight library (Zustand), or full Redux?
4. **Build Tools**: Add webpack/vite for module bundling?
5. **CSS Approach**: Keep vanilla CSS, adopt Tailwind, or use CSS-in-JS?
6. **Testing Framework**: Jest + Puppeteer or Playwright for E2E?

---

## Resources

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs - Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [A11y Project](https://www.a11yproject.com/)

### Tools
- [axe DevTools](https://www.deque.com/axe/devtools/) - Accessibility testing
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse) - Performance & accessibility audit

### References
- [DMP-ART CLAUDE.md](./CLAUDE.md) - Comprehensive architecture documentation
- [style.css](./static/css/style.css) - Main stylesheet
- [review.html](./templates/review.html) - Review page template

---

**Document Version**: 1.0
**Last Updated**: 2025-01-18
**Author**: Claude (Anthropic) - Architecture Analysis & Planning
**Status**: Sprint 1 Complete, Sprint 2 In Progress
