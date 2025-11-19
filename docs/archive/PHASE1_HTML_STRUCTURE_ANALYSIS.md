# Phase 1.1: HTML Structure Analysis

**Date:** 2025-11-16
**Status:** In Progress
**Document:** review.html DOM Structure & JavaScript Connections

---

## 1. Core DOM Elements

### 1.1 Page Structure
```
<body data-page="review">
  ├── Header (with navigation)
  ├── Main Content (.review-layout)
  │   └── Question Cards Container (.main-content)
  │       └── 14 Question Cards (sections 1.1 - 6.2)
  ├── Right Sidebar (fixed position)
  │   ├── Compile Feedback Button
  │   ├── Save Progress Button
  │   ├── Section Navigation Grid
  │   └── Quick Comments List
  ├── Unconnected Text Modal
  └── Compiled Feedback Panel
```

---

## 2. Question Card Structure (14 instances)

Each section (1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2) has:

```html
<div class="question-card" id="section-{{ section_id }}" data-id="{{ section_id }}">
    <!-- Section Title -->
    <h2>{{ section }}</h2>

    <!-- Question -->
    <h3>{{ question }}</h3>

    <!-- Extracted Content -->
    <div class="extracted-content">
        <div class="continuous-text">
            <!-- Extracted paragraphs from DMP -->
        </div>
    </div>

    <!-- Character Counter -->
    <div class="char-counter" id="char-counter-{{ section_id }}">
        0 characters
    </div>

    <!-- Category Selection -->
    <div class="category-selection" id="category-selection-{{ section_id }}">
        <label>Select Category:</label>
        <div class="category-buttons-inline">
            <button class="category-btn-inline"
                    data-category="newcomer"
                    data-section="{{ section_id }}">
                Newcomer Guidance
            </button>
            <button class="category-btn-inline"
                    data-category="missing"
                    data-section="{{ section_id }}">
                Missing Info
            </button>
            <button class="category-btn-inline"
                    data-category="ready"
                    data-section="{{ section_id }}">
                Ready to Use
            </button>
        </div>
    </div>

    <!-- Category Comments Dropdown (hidden by default) -->
    <div class="category-comments-dropdown"
         id="category-dropdown-{{ section_id }}"
         style="display: none;">
        <div class="category-comments-container">
            <div class="category-comments-list-inline"
                 id="category-comments-{{ section_id }}">
                <!-- Dynamically populated by JavaScript -->
            </div>
        </div>
    </div>

    <!-- Feedback Textarea -->
    <textarea class="feedback-text"
              id="feedback-{{ section_id }}"
              data-section-id="{{ section_id }}"
              placeholder="Enter your feedback...">
    </textarea>

    <!-- Action Buttons -->
    <div class="action-buttons">
        <button class="copy-btn"
                data-id="{{ section_id }}"
                title="Copy feedback to clipboard">
            Copy
        </button>
        <button class="reset-btn"
                data-id="{{ section_id }}"
                title="Reset to original template">
            Reset
        </button>
    </div>

    <!-- Completion Indicator -->
    <div class="completion-indicator" id="completion-{{ section_id }}">
        <!-- Status indicator -->
    </div>
</div>
```

---

## 3. Key ID Patterns

### 3.1 Section-Specific IDs
| Element Type | ID Pattern | Example |
|--------------|-----------|---------|
| Question Card | `section-{id}` | `section-1.1` |
| Feedback Textarea | `feedback-{id}` | `feedback-1.1` |
| Character Counter | `char-counter-{id}` | `char-counter-1.1` |
| Category Dropdown | `category-dropdown-{id}` | `category-dropdown-1.1` |
| Category Comments List | `category-comments-{id}` | `category-comments-1.1` |
| Completion Indicator | `completion-{id}` | `completion-1.1` |

### 3.2 Global IDs
| Element | ID |
|---------|---|
| Compile Feedback Button | `compile-feedback-btn` |
| Save Progress Button | `save-feedback-btn` |
| Section Navigation Grid | `section-nav-grid` |
| Quick Comments List | `quick-comments-list` |
| Compiled Feedback Panel | `compiled-feedback-container` |
| Compiled Feedback Textarea | `compiled-feedback` |
| Panel Backdrop | `panel-backdrop` |
| Close Compiled Button | `close-compiled-btn` |
| Copy Compiled Button | `copy-compiled-btn` |
| Download Feedback Button | `download-feedback-btn` |
| Generate DOCX Button | `generate-docx-btn` |
| Unconnected Text Modal | `unconnected-text-modal` |
| Unconnected Items Container | `unconnected-items` |
| Assign All Button | `assign-all-btn` |
| Skip All Button | `skip-all-btn` |
| Floating Cite Button | `cite-btn-float` |

---

## 4. Data Attributes

### 4.1 Section Data Attributes
```html
data-id="{{ section_id }}"           <!-- On question cards -->
data-section-id="{{ section_id }}"   <!-- On textareas -->
data-section="{{ section_id }}"      <!-- On category buttons -->
data-category="newcomer|missing|ready"  <!-- On category buttons -->
```

### 4.2 Usage Pattern
- `data-id`: Used for identifying the section in action buttons (copy, reset)
- `data-section-id`: Used for identifying which textarea to update
- `data-section`: Used for category button to know which section's dropdown to populate
- `data-category`: Identifies which category template to load

---

## 5. JavaScript Connections (script.js)

### 5.1 Character Counter Function
```javascript
function updateCharacterCounter(sectionId) {
    const textarea = document.getElementById(`feedback-${sectionId}`);
    const counter = document.getElementById(`char-counter-${sectionId}`);

    if (textarea && counter) {
        const charCount = textarea.value.length;
        const wordCount = textarea.value.trim() ?
            textarea.value.trim().split(/\s+/).length : 0;
        counter.textContent = `${charCount} characters, ${wordCount} words`;
    }
}
```

**Connection:** `textarea` → `counter`
- Reads from: `feedback-{id}`
- Writes to: `char-counter-{id}`

### 5.2 Category Button Click Handler
```javascript
// Event delegation on category buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('category-btn-inline')) {
        const category = e.target.getAttribute('data-category');
        const section = e.target.getAttribute('data-section');
        showCategoryComments(category, section);
    }
});
```

**Connection:** `category button` → `dropdown` → `comments list`
- Reads: `data-category`, `data-section`
- Shows: `category-dropdown-{section}`
- Populates: `category-comments-{section}`

### 5.3 Category Comment Insertion
```javascript
function insertCommentWithAnimation(id, comment) {
    const textarea = document.getElementById(`feedback-${id}`);
    // Insert comment at cursor position
    // Update character counter
    updateCharacterCounter(id);
}
```

**Connection:** `comment item click` → `textarea`
- Writes to: `feedback-{id}`
- Updates: `char-counter-{id}` via `updateCharacterCounter()`

### 5.4 Copy Button Handler
```javascript
// Copy button event listener
document.querySelectorAll('.copy-btn').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        const textarea = document.getElementById(`feedback-${id}`);
        // Copy to clipboard
    });
});
```

**Connection:** `copy button` → `textarea` → `clipboard`
- Reads: `data-id` attribute
- Copies from: `feedback-{id}`

### 5.5 Reset Button Handler
```javascript
// Reset button event listener
document.querySelectorAll('.reset-btn').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.getAttribute('data-id');
        const textarea = document.getElementById(`feedback-${id}`);
        // Reset to original template
        updateCharacterCounter(id);
    });
});
```

**Connection:** `reset button` → `textarea` → `counter`
- Reads: `data-id` attribute
- Resets: `feedback-{id}`
- Updates: `char-counter-{id}`

### 5.6 Navigation Grid
```javascript
// Section navigation buttons
document.querySelectorAll('.nav-grid-btn').forEach(button => {
    button.addEventListener('click', function() {
        const sectionId = this.textContent.trim(); // e.g., "1.1"
        const targetSection = document.getElementById(`section-${sectionId}`);
        targetSection.scrollIntoView({ behavior: 'smooth' });
    });
});
```

**Connection:** `nav button click` → `scroll to section`
- Scrolls to: `section-{id}`

### 5.7 Compile Feedback
```javascript
document.getElementById('compile-feedback-btn').addEventListener('click', function() {
    let compiledText = '';

    // Iterate through all sections 1.1 - 6.2
    ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2',
     '5.1', '5.2', '5.3', '5.4', '6.1', '6.2'].forEach(id => {
        const textarea = document.getElementById(`feedback-${id}`);
        if (textarea && textarea.value.trim()) {
            compiledText += `\n## Section ${id}\n${textarea.value.trim()}\n`;
        }
    });

    document.getElementById('compiled-feedback').value = compiledText;
    document.getElementById('compiled-feedback-container').classList.add('active');
    document.getElementById('panel-backdrop').classList.add('active');
});
```

**Connection:** `compile button` → `all textareas` → `compiled textarea` → `modal`
- Reads from: All `feedback-{id}` textareas
- Writes to: `compiled-feedback`
- Shows: `compiled-feedback-container` and `panel-backdrop`

---

## 6. CSS Positioning Strategy

### 6.1 Right Sidebar (Fixed Positioning)
```css
body[data-page="review"] aside.right-sidebar {
    position: fixed !important;
    top: 80px !important;
    right: 20px !important;
    bottom: 60px !important;
    width: 250px !important;
    overflow-y: auto !important;
    z-index: 999999 !important;
}
```

**Purpose:** Keeps navigation and quick actions always visible during scrolling

### 6.2 Main Content Margin
```css
.main-content {
    flex: 1 !important;
    margin-left: 40px !important;
    margin-right: 290px !important; /* Space for fixed sidebar */
}
```

**Purpose:** Prevents content from being hidden under fixed sidebar

---

## 7. Connection Verification Tests

### Test 1: Character Counter Updates
**Test:** Type in any feedback textarea
**Expected:** Character counter updates in real-time
**Connection:** `feedback-{id}` (input event) → `updateCharacterCounter()` → `char-counter-{id}`
**Status:** ✅ TO VERIFY

### Test 2: Category Button Shows Dropdown
**Test:** Click "Newcomer Guidance" for section 1.1
**Expected:** Dropdown appears with newcomer comments for section 1.1
**Connection:** `category-btn-inline[data-category="newcomer"][data-section="1.1"]` → `category-dropdown-1.1` (show) → populate `category-comments-1.1`
**Status:** ✅ TO VERIFY

### Test 3: Comment Insertion
**Test:** Click a comment from category dropdown
**Expected:** Comment inserted into correct textarea at cursor position
**Connection:** `comment item click` → `insertCommentWithAnimation(sectionId, comment)` → `feedback-{id}`
**Status:** ✅ TO VERIFY

### Test 4: Copy Button
**Test:** Click copy button for section 1.1
**Expected:** Feedback text copied to clipboard
**Connection:** `copy-btn[data-id="1.1"]` → read `feedback-1.1` → clipboard
**Status:** ✅ TO VERIFY

### Test 5: Navigation Grid
**Test:** Click "2.1" in navigation grid
**Expected:** Page scrolls to section 2.1
**Connection:** `nav-grid-btn` click → `section-2.1.scrollIntoView()`
**Status:** ✅ TO VERIFY

### Test 6: Quick Comments
**Test:** Click a quick comment in sidebar
**Expected:** Comment inserted into currently focused textarea
**Connection:** `quick-comment-item` click → `lastFocusedTextarea` → insert comment
**Status:** ✅ TO VERIFY

### Test 7: Compile Feedback
**Test:** Click "Compile Feedback"
**Expected:** Modal opens with all feedback combined
**Connection:** `compile-feedback-btn` → read all `feedback-{id}` → write to `compiled-feedback` → show modal
**Status:** ✅ TO VERIFY

### Test 8: Unconnected Text Assignment
**Test:** If unconnected text exists, assign to section
**Expected:** Dropdown allows selection, assignment updates cache
**Connection:** `section-select-{index}` → `assign-all-btn` → POST to `/assign_unconnected`
**Status:** ✅ TO VERIFY

---

## 8. Potential Issues to Check

### 8.1 ID Conflicts
- **Check:** Are all IDs unique?
- **Pattern:** Each section (1.1-6.2) should have unique suffixed IDs
- **Status:** ⚠️ NEEDS VERIFICATION

### 8.2 Data Attribute Consistency
- **Check:** Do all category buttons have both `data-category` and `data-section`?
- **Location:** Lines 796-798 in review.html
- **Status:** ⚠️ NEEDS VERIFICATION

### 8.3 Event Listener Attachment Timing
- **Check:** Are event listeners attached after DOM is fully loaded?
- **Pattern:** Should be inside `DOMContentLoaded` or at end of body
- **Status:** ⚠️ NEEDS VERIFICATION

### 8.4 Sidebar Visibility on Small Screens
- **Check:** Does fixed sidebar cause issues on tablets/small screens?
- **CSS:** Fixed width of 250px might overlap content
- **Status:** ⚠️ NEEDS RESPONSIVE TESTING

### 8.5 Character Counter Debouncing
- **Check:** Is character counter updated on every keystroke?
- **Performance:** Could cause lag with large feedback text
- **Suggestion:** Add debouncing (already mentioned in ACTION_PLAN)
- **Status:** ⚠️ OPTIMIZATION NEEDED

---

## 9. Data Flow Summary

### 9.1 Upload → Review Flow
```
User uploads DMP
    ↓
app.py /upload → DMPExtractor.process_file()
    ↓
Generate cache_{uuid}.json
    ↓
Redirect to /review/<filename>?cache_id=<uuid>
    ↓
app.py /review → Load cache file
    ↓
Render review.html with extracted_content
    ↓
JavaScript initializes:
    - Character counters
    - Category buttons
    - Navigation grid
    - Quick comments
    - Event listeners
```

### 9.2 Review → Feedback Flow
```
User reviews DMP content
    ↓
User selects category (e.g., "Newcomer")
    ↓
JavaScript loads category comments from CATEGORY_COMMENTS global
    ↓
User clicks comment
    ↓
Comment inserted into textarea
    ↓
Character counter updates
    ↓
User clicks "Compile Feedback"
    ↓
All feedback collected and displayed in modal
    ↓
User can:
    - Copy to clipboard
    - Download as TXT
    - Generate DOCX (if implemented)
```

### 9.3 Save Progress Flow
```
User clicks "Save Progress"
    ↓
JavaScript collects all feedback from textareas
    ↓
POST to /save_feedback with filename and feedback data
    ↓
app.py saves to feedback_{filename}.txt
    ↓
Success/failure message shown to user
```

---

## 10. Category Comments Loading

### 10.1 Global JavaScript Variable
```javascript
// Loaded in <script> block in review.html
var CATEGORY_COMMENTS = {
    "newcomer": {
        "1.1": ["comment 1", "comment 2", ...],
        "1.2": ["comment 1", "comment 2", ...],
        // ... for all sections
    },
    "missing": {
        "1.1": [...],
        // ...
    },
    "ready": {
        "1.1": [...],
        // ...
    }
};
```

### 10.2 Loading Process
```
Page load
    ↓
Flask renders template
    ↓
Jinja2 includes category data:
    {% for category in ['newcomer', 'missing', 'ready'] %}
        fetch('/config/{{ category }}.json')
    {% endfor %}
    ↓
JavaScript parses and stores in CATEGORY_COMMENTS
    ↓
Ready for use when category button clicked
```

---

## 11. Next Steps for Phase 1.1

- [x] Document DOM structure ✅
- [x] Map all ID patterns ✅
- [x] Document data attributes ✅
- [x] Map JavaScript connections ✅
- [x] Identify potential issues ✅
- [ ] **NEXT:** Run live verification tests
- [ ] **NEXT:** Test on actual browser
- [ ] **NEXT:** Document any broken connections
- [ ] **NEXT:** Create fix recommendations

---

## 12. Files Analyzed

- `/home/user/DMP-ART/templates/review.html` - Main review interface template
- `/home/user/DMP-ART/static/js/script.js` - Main JavaScript functionality
- `/home/user/DMP-ART/app.py` - Flask routes and backend logic

---

**Analysis Status:** COMPLETE - Ready for live testing
**Next Phase:** 1.2 - Existing Functions Inventory
**Date:** 2025-11-16
