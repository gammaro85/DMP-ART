# Phase 2: High Priority UX Improvements
**Estimated Time:** 3-4 hours
**Risk Level:** MEDIUM
**Dependencies:** Phase 1 complete
**Prerequisites:** Fresh branch from Phase 1, all Phase 1 tests passing

---

## Objectives

Implement critical UX improvements: dynamic categories, sticky sidebar, file organization, modal for unconnected text, and unified fonts.

**Success Criteria:**
- [ ] Template editor loads categories dynamically from config/
- [ ] Can create, rename, delete categories via UI
- [ ] Right sidebar uses `position: sticky` (no !important)
- [ ] Unconnected text modal shows post-upload, before review
- [ ] Files organized into dmp/, reviews/, cache/ folders
- [ ] Single font stack across all templates
- [ ] All existing functionality preserved
- [ ] No regressions in extraction or review

---

## Pre-Implementation Analysis

### Run Phase 1 Validation:

```bash
# 1. Verify Phase 1 completion
python analyze_phase1.py
# All checks should pass

# 2. Record baseline metrics
python -c "
from utils.extractor import DMPExtractor
import time

ext = DMPExtractor()
test_file = 'tests/fixtures/DMP_SONATA20_MD.docx'

start = time.time()
result = ext.process_file(test_file, 'outputs/cache')
end = time.time()

print(f'Baseline extraction time: {end-start:.2f}s')
print(f'Baseline sections: {len(result.get(\"extracted_content\", {}))}')
" > phase2_baseline.txt

cat phase2_baseline.txt
```

### Check Current State:

```bash
# 1. List current categories
ls config/*.json | grep -v dmp_structure | grep -v quick_comments

# 2. Test template editor current behavior
curl -s http://localhost:5000/template_editor | grep -o 'tab-btn' | wc -l
# Note: current number of tabs

# 3. Check right sidebar CSS
grep -A 5 "right-sidebar" templates/review.html | grep "!important" | wc -l
# Note: current number of !important declarations

# 4. Verify file organization
ls -la outputs/
# Note: current structure
```

---

## Task 2.1: Dynamic Category Loading in Template Editor

**Priority:** HIGH
**Files:** `static/js/template_editor.js`, `templates/template_editor.html`, `app.py`

### Implementation:

#### Step 1: Update Backend - Category Discovery

**File:** `app.py`

Add new route to discover categories dynamically:

```python
@app.route('/api/discover-categories', methods=['GET'])
def discover_categories():
    """
    Discover all category JSON files in config/ directory.

    Returns JSON list of categories (excluding dmp_structure and quick_comments).
    """
    try:
        config_dir = 'config'
        categories = []

        if not os.path.exists(config_dir):
            return jsonify({
                'success': False,
                'message': 'Config directory not found'
            }), 404

        # List all JSON files
        for filename in os.listdir(config_dir):
            if not filename.endswith('.json'):
                continue

            # Skip system files
            if filename in ['dmp_structure.json', 'quick_comments.json']:
                continue

            # Skip backup files
            if '_backup_' in filename:
                continue

            # Extract category name (remove .json extension)
            category_name = filename.replace('.json', '')
            categories.append({
                'id': category_name,
                'filename': filename,
                'display_name': format_category_name(category_name)
            })

        # Sort alphabetically
        categories.sort(key=lambda x: x['display_name'])

        return jsonify({
            'success': True,
            'categories': categories,
            'count': len(categories)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def format_category_name(category_id):
    """
    Format category ID for display.

    Examples:
        'newcomer' -> 'Newcomer'
        'mising' -> 'Missing Info'
        'ready' -> 'Ready to Use'
        'my_custom_category' -> 'My Custom Category'
    """
    # Special cases
    special_names = {
        'newcomer': 'Newcomer',
        'mising': 'Missing Info',
        'ready': 'Ready to Use'
    }

    if category_id in special_names:
        return special_names[category_id]

    # Default: title case with underscores replaced
    return category_id.replace('_', ' ').title()
```

#### Step 2: Update Frontend - Dynamic Tab Generation

**File:** `static/js/template_editor.js`

Replace hardcoded category loading with dynamic:

```javascript
// Global state
let availableCategories = [];

// Load categories on page load
async function initializeCategories() {
    try {
        const response = await fetch('/api/discover-categories');
        const data = await response.json();

        if (data.success) {
            availableCategories = data.categories;
            renderCategoryTabs();
            console.log(`Loaded ${data.count} categories dynamically`);
        } else {
            console.error('Failed to load categories:', data.message);
            showToast('Failed to load categories', 'error');
        }
    } catch (error) {
        console.error('Error discovering categories:', error);
        showToast('Error loading categories', 'error');
    }
}

function renderCategoryTabs() {
    const tabNav = document.getElementById('tab-navigation');

    if (!tabNav) {
        console.error('Tab navigation element not found');
        return;
    }

    // Find add button (we'll re-add it at the end)
    const addBtn = tabNav.querySelector('.add-category-btn');

    // Remove existing category tabs (keep DMP Structure and Quick Comments)
    const existingTabs = tabNav.querySelectorAll('.tab-btn');
    existingTabs.forEach(tab => {
        const tabType = tab.getAttribute('data-tab');
        if (tabType !== 'dmp-structure' && tabType !== 'quick-comments') {
            tab.remove();
        }
    });

    // Add dynamic category tabs
    availableCategories.forEach(category => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.setAttribute('data-tab', category.id);
        btn.innerHTML = `
            <i class="fas fa-tags"></i>
            ${category.display_name}
            <button class="delete-category-btn" onclick="deleteCategoryConfirm('${category.id}', event)" title="Delete category">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Insert before add button
        if (addBtn) {
            tabNav.insertBefore(btn, addBtn);
        } else {
            tabNav.appendChild(btn);
        }
    });

    // Re-attach click handlers
    attachTabClickHandlers();
}

function attachTabClickHandlers() {
    const tabs = document.querySelectorAll('.tab-btn');

    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            // Don't trigger if clicking delete button
            if (e.target.closest('.delete-category-btn')) {
                return;
            }

            // Remove active from all tabs
            tabs.forEach(t => t.classList.remove('active'));

            // Add active to clicked tab
            this.classList.add('active');

            // Load tab content
            const tabType = this.getAttribute('data-tab');
            loadTabContent(tabType);
        });
    });
}

async function deleteCategoryConfirm(categoryId, event) {
    event.stopPropagation(); // Don't trigger tab click

    const category = availableCategories.find(c => c.id === categoryId);
    if (!category) return;

    const confirmed = confirm(
        `Delete category "${category.display_name}"?\n\n` +
        `This will delete the file: ${category.filename}\n` +
        `This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
        const response = await fetch(`/api/delete-category/${categoryId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Category "${category.display_name}" deleted`, 'success');

            // Reload categories
            await initializeCategories();

            // Switch to DMP Structure tab
            const dmpTab = document.querySelector('[data-tab="dmp-structure"]');
            if (dmpTab) dmpTab.click();
        } else {
            showToast(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        showToast('Error deleting category', 'error');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeCategories();
});
```

#### Step 3: Update HTML - Remove Hardcoded Tabs

**File:** `templates/template_editor.html`

Find the tab navigation section:

```html
<!-- BEFORE (remove these hardcoded category tabs): -->
<div class="tab-navigation" id="tab-navigation">
    <button class="tab-btn active" data-tab="dmp-structure">DMP Structure</button>
    <button class="tab-btn" data-tab="quick-comments">Quick Comments</button>
    <!-- DELETE any hardcoded category tabs here -->
    <button class="add-category-btn" id="add-category-btn">Create Category</button>
</div>

<!-- AFTER (clean, only system tabs): -->
<div class="tab-navigation" id="tab-navigation">
    <button class="tab-btn active" data-tab="dmp-structure">
        <i class="fas fa-list"></i> DMP Structure
    </button>
    <button class="tab-btn" data-tab="quick-comments">
        <i class="fas fa-comment"></i> Quick Comments
    </button>
    <!-- Categories will be injected here by JavaScript -->
    <button class="add-category-btn" id="add-category-btn">
        <i class="fas fa-plus"></i> Create Category
    </button>
</div>
```

#### Step 4: Add CSS for Delete Buttons

**File:** `static/css/style.css`

Add styles for delete button on category tabs:

```css
/* Delete button on category tabs */
.tab-btn {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.delete-category-btn {
    margin-left: auto;
    padding: 0.25rem;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: 4px;
    opacity: 0;
    transition: all 0.2s ease;
}

.tab-btn:hover .delete-category-btn {
    opacity: 1;
}

.delete-category-btn:hover {
    background: var(--error-color);
    color: white;
}
```

### Testing Task 2.1:

```bash
# 1. Test backend category discovery
curl -s http://localhost:5000/api/discover-categories | python -m json.tool

# Expected output:
# {
#   "success": true,
#   "categories": [
#     {"id": "mising", "filename": "mising.json", "display_name": "Missing Info"},
#     {"id": "newcomer", "filename": "newcomer.json", "display_name": "Newcomer"},
#     {"id": "ready", "filename": "ready.json", "display_name": "Ready to Use"}
#   ],
#   "count": 3
# }

# 2. Test template editor loads dynamically
# Open http://localhost:5000/template_editor
# Verify:
# - All existing categories appear as tabs
# - Each tab shows delete button on hover
# - Clicking tab loads content

# 3. Test create new category
# Click "Create Category" button
# Enter name: "test_category"
# Verify new tab appears
# Verify new file created: config/test_category.json

# 4. Test delete category
# Hover over "test_category" tab
# Click delete button (×)
# Confirm deletion
# Verify tab disappears
# Verify file deleted: config/test_category.json

# 5. Test special name formatting
python -c "
def format_category_name(category_id):
    special_names = {
        'newcomer': 'Newcomer',
        'mising': 'Missing Info',
        'ready': 'Ready to Use'
    }
    return special_names.get(category_id, category_id.replace('_', ' ').title())

test_cases = ['newcomer', 'mising', 'ready', 'my_custom', 'another_one']
for case in test_cases:
    print(f'{case:15} -> {format_category_name(case)}')
"

# Expected output:
# newcomer        -> Newcomer
# mising          -> Missing Info
# ready           -> Ready to Use
# my_custom       -> My Custom
# another_one     -> Another One
```

### Commit:
```bash
git add app.py static/js/template_editor.js templates/template_editor.html static/css/style.css
git commit -m "Implement dynamic category loading in template editor

- Added /api/discover-categories endpoint
- Categories now loaded from config/ directory dynamically
- Users can create/delete categories via UI
- Added format_category_name() for display names
- Added delete button on category tabs (hover to reveal)
- Removed hardcoded category tabs from HTML
- Categories auto-reload after create/delete operations"
```

---

## Task 2.2: Fix Right Sidebar Positioning

**Priority:** HIGH
**Files:** `templates/review.html`, `static/css/style.css`
**Goal:** Remove 12 !important declarations, use CSS Grid + sticky positioning

### Implementation:

#### Step 1: Backup Current Inline Styles

```bash
# Extract current sidebar styles for reference
grep -A 20 "right-sidebar" templates/review.html > /tmp/sidebar_old_styles.txt
```

#### Step 2: Update Review Page Layout

**File:** `templates/review.html`

Find the inline `<style>` block (around lines 22-100) and REMOVE all sidebar-specific styles:

```html
<!-- DELETE these from <style> section: -->
<style>
/* Remove this entire block: */
.review-layout {
    display: flex !important;
    /* ... all !important styles */
}
.main-content {
    margin-right: 290px !important;
    /* ... */
}
body[data-page="review"] aside.right-sidebar {
    position: fixed !important;
    /* ... all 12 !important styles */
}
</style>
```

**Replace the entire `.review-layout` and `.right-sidebar` sections with:**

```html
<style>
/* Minimal page-specific styles - move rest to style.css */
.results-container {
    background-color: var(--bg-card);
    color: var(--text-primary);
    max-width: 800px;
    margin: 0 auto;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-medium);
    transition: all 0.3s ease;
}
</style>
```

#### Step 3: Add Proper CSS in Stylesheet

**File:** `static/css/style.css`

Add this section (around line 500, after other layout rules):

```css
/* ============================================
   Review Page Layout - Grid + Sticky Sidebar
   ============================================ */

/* Review page container */
body[data-page="review"] {
    --sidebar-width: 300px;
    --header-height: 80px;
    --footer-height: 60px;
}

/* Grid layout for review page */
.review-layout {
    display: grid;
    grid-template-columns: 1fr var(--sidebar-width);
    gap: 2rem;
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem;
    padding-top: calc(var(--header-height) + 1rem);
    padding-bottom: calc(var(--footer-height) + 1rem);
}

/* Main content area */
.main-content {
    min-width: 0; /* Prevents grid blowout with long text */
    overflow-wrap: break-word;
}

/* Right sidebar - sticky positioning */
.right-sidebar {
    position: sticky;
    top: calc(var(--header-height) + 1rem);
    align-self: start;
    max-height: calc(100vh - var(--header-height) - 2rem);
    overflow-y: auto;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* Smooth scrolling for sidebar */
.right-sidebar {
    scroll-behavior: smooth;
    scrollbar-width: thin;
    scrollbar-color: var(--border-medium) transparent;
}

/* Webkit scrollbar styling */
.right-sidebar::-webkit-scrollbar {
    width: 6px;
}

.right-sidebar::-webkit-scrollbar-track {
    background: transparent;
}

.right-sidebar::-webkit-scrollbar-thumb {
    background: var(--border-medium);
    border-radius: 3px;
}

.right-sidebar::-webkit-scrollbar-thumb:hover {
    background: var(--primary-color);
}

/* Responsive: Stack on narrow screens */
@media (max-width: 1200px) {
    .review-layout {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .right-sidebar {
        position: static;
        max-height: none;
    }
}
```

#### Step 4: Verify No Z-Index Conflicts

```bash
# Check for z-index issues
grep -n "z-index" static/css/style.css templates/review.html

# Expected hierarchy:
# Header: z-index: 1000
# Theme toggle: z-index: 1001
# Modals: z-index: 2000
# Sidebar: no z-index needed (natural stacking)
```

### Testing Task 2.2:

```bash
# 1. Visual test - sidebar behavior
# Open http://localhost:5000/review/<filename>?cache_id=<id>
# Scroll down the page
# Verify:
# - Sidebar stays visible ("sticks" to top)
# - Sidebar doesn't overlap main content
# - Sidebar scrolls independently if content too tall
# - No gaps or misalignment

# 2. Count !important declarations
grep -c "!important" templates/review.html
# Expected: 0 (or very few, unrelated to sidebar)

grep "right-sidebar" templates/review.html | grep -c "!important"
# Expected: 0

# 3. Test on different screen sizes
# Resize browser window
# Verify sidebar behavior:
# - Wide (1920px): sidebar on right, sticky
# - Medium (1200px): sidebar on right, sticky
# - Narrow (<1200px): sidebar stacks below, not sticky

# 4. Test scrolling
# With long review page:
# - Scroll main content
# - Verify sidebar follows
# - Verify sidebar doesn't jump or flicker

# 5. Check CSS specificity
python -c "
import re

# Check for proper specificity without !important
specificity_ok = [
    'body[data-page=\"review\"] .review-layout',  # Good
    '.right-sidebar',  # Good
    'body[data-page=\"review\"]',  # Good
]

print('CSS Specificity Check:')
for selector in specificity_ok:
    if '!important' in selector:
        print(f'  ❌ {selector} - contains !important')
    else:
        print(f'  ✅ {selector} - clean specificity')
"
```

### Commit:
```bash
git add templates/review.html static/css/style.css
git commit -m "Fix right sidebar: remove !important, use CSS Grid + sticky

- Removed 12 !important declarations from inline styles
- Implemented CSS Grid layout for review page
- Changed sidebar from position:fixed to position:sticky
- Added smooth scrollbar styling
- Sidebar now scrolls with page, doesn't overlay content
- Responsive: stacks below on narrow screens (<1200px)
- Clean CSS specificity, no z-index conflicts"
```

---

## Task 2.3: File Organization - Separate Folders

**Priority:** HIGH
**Files:** `app.py`
**Goal:** Save DMPs to `outputs/dmp/`, reviews to `outputs/reviews/`, cache to `outputs/cache/`

### Implementation:

#### Step 1: Create Helper Function

**File:** `app.py`

Add near the top, after `load_dmp_structure()`:

```python
def get_organized_path(file_type, filename):
    """
    Get organized file path based on type.

    Args:
        file_type (str): 'dmp', 'review', or 'cache'
        filename (str): Base filename

    Returns:
        str: Full path in organized structure
    """
    base_folder = app.config['OUTPUT_FOLDER']

    folder_map = {
        'dmp': os.path.join(base_folder, 'dmp'),
        'review': os.path.join(base_folder, 'reviews'),
        'cache': os.path.join(base_folder, 'cache')
    }

    folder = folder_map.get(file_type, base_folder)

    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)

    return os.path.join(folder, filename)


def create_file_link_metadata(dmp_path, review_path, grant_id=None, metadata=None):
    """
    Create metadata file linking DMP and review.

    Args:
        dmp_path (str): Path to extracted DMP file
        review_path (str): Path to review file
        grant_id (str, optional): Grant identifier
        metadata (dict, optional): Additional metadata

    Returns:
        str: Path to metadata file
    """
    import json
    from datetime import datetime

    link_data = {
        'dmp_file': os.path.basename(dmp_path),
        'review_file': os.path.basename(review_path),
        'dmp_full_path': dmp_path,
        'review_full_path': review_path,
        'grant_id': grant_id,
        'linked_at': datetime.now().isoformat(),
        'metadata': metadata or {}
    }

    # Save link file alongside review
    link_filename = os.path.basename(review_path).replace('.txt', '_link.json')
    link_path = get_organized_path('review', link_filename)

    with open(link_path, 'w', encoding='utf-8') as f:
        json.dump(link_data, f, indent=2, ensure_ascii=False)

    return link_path
```

#### Step 2: Update Upload Route

**File:** `app.py`

Find the `/upload` route and update file saving:

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    # ... existing validation code ...

    try:
        # ... existing processing ...

        # CHANGE: Save to organized cache folder
        cache_filename = f'cache_{cache_id}.json'
        cache_path = get_organized_path('cache', cache_filename)

        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_content, f, ensure_ascii=False, indent=2)

        # ... rest of route ...

    except Exception as e:
        # ... error handling ...
```

#### Step 3: Update Save Feedback Route

**File:** `app.py`

Find the `/save_feedback` route:

```python
@app.route('/save_feedback', methods=['POST'])
def save_feedback():
    try:
        data = request.json
        feedback = data.get('feedback', {})
        cache_id = data.get('cache_id')

        if not cache_id:
            return jsonify({
                'success': False,
                'message': 'No cache_id provided'
            }), 400

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        feedback_filename = f'feedback_{cache_id}_{timestamp}.txt'

        # CHANGE: Save to organized reviews folder
        feedback_path = get_organized_path('review', feedback_filename)

        # Compile feedback text
        feedback_text = []
        for section_id in sorted(feedback.keys()):
            if section_id.startswith('_'):
                continue  # Skip metadata fields

            text = feedback[section_id]
            if text and text.strip():
                feedback_text.append(f"=== Section {section_id} ===\n")
                feedback_text.append(f"{text}\n\n")

        # Save feedback file
        with open(feedback_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(feedback_text))

        # Find corresponding DMP file
        cache_filename = f'cache_{cache_id}.json'
        cache_path = get_organized_path('cache', cache_filename)

        dmp_filename = None
        if os.path.exists(cache_path):
            # Extract original filename from cache
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                dmp_filename = cache_data.get('original_filename', f'DMP_{cache_id}.docx')

        # Create link metadata
        if dmp_filename:
            dmp_path = get_organized_path('dmp', dmp_filename)
            create_file_link_metadata(dmp_path, feedback_path, cache_id)

        return jsonify({
            'success': True,
            'message': 'Feedback saved successfully',
            'file_path': feedback_path
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

#### Step 4: Update Download Route

**File:** `app.py`

Update the `/download/<filename>` route to check all organized folders:

```python
@app.route('/download/<filename>')
def download_file(filename):
    """Download file from organized folders"""
    try:
        # Check each organized folder
        for file_type in ['dmp', 'review', 'cache']:
            file_path = get_organized_path(file_type, filename)

            if os.path.exists(file_path):
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename
                )

        # Fallback: check base output folder
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)

        return jsonify({
            'success': False,
            'message': 'File not found'
        }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

#### Step 5: Migrate Existing Files

Create migration script:

```python
# Save as migrate_files.py

import os
import shutil
import json
from datetime import datetime

def migrate_existing_files():
    """Migrate existing files to organized structure"""

    base_dir = 'outputs'
    organized_dirs = {
        'cache': os.path.join(base_dir, 'cache'),
        'dmp': os.path.join(base_dir, 'dmp'),
        'reviews': os.path.join(base_dir, 'reviews')
    }

    # Ensure directories exist
    for dir_path in organized_dirs.values():
        os.makedirs(dir_path, exist_ok=True)

    # Migrate files
    moved_count = {'cache': 0, 'dmp': 0, 'reviews': 0}

    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)

        # Skip if directory
        if os.path.isdir(file_path):
            continue

        # Determine file type and move
        if filename.startswith('cache_') and filename.endswith('.json'):
            dest = os.path.join(organized_dirs['cache'], filename)
            shutil.move(file_path, dest)
            moved_count['cache'] += 1
            print(f"Moved cache: {filename}")

        elif filename.startswith('DMP_'):
            dest = os.path.join(organized_dirs['dmp'], filename)
            shutil.move(file_path, dest)
            moved_count['dmp'] += 1
            print(f"Moved DMP: {filename}")

        elif filename.startswith('feedback_'):
            dest = os.path.join(organized_dirs['reviews'], filename)
            shutil.move(file_path, dest)
            moved_count['reviews'] += 1
            print(f"Moved review: {filename}")

    print("\n" + "=" * 50)
    print("MIGRATION COMPLETE")
    print("=" * 50)
    print(f"Cache files moved: {moved_count['cache']}")
    print(f"DMP files moved: {moved_count['dmp']}")
    print(f"Review files moved: {moved_count['reviews']}")
    print(f"Total: {sum(moved_count.values())}")

if __name__ == '__main__':
    migrate_existing_files()
```

Run migration:
```bash
python migrate_files.py
```

### Testing Task 2.3:

```bash
# 1. Test organized path function
python -c "
import sys
sys.path.insert(0, '.')
from app import get_organized_path

paths = {
    'cache': get_organized_path('cache', 'test.json'),
    'dmp': get_organized_path('dmp', 'test.docx'),
    'review': get_organized_path('review', 'test.txt')
}

for ftype, path in paths.items():
    print(f'{ftype:8} -> {path}')
"

# Expected output:
# cache    -> outputs/cache/test.json
# dmp      -> outputs/dmp/test.docx
# review   -> outputs/reviews/test.txt

# 2. Test file upload and organization
# Upload test file via web interface
# Check file locations:
ls -la outputs/cache/    # Should contain cache_*.json
ls -la outputs/dmp/      # Should contain DMP_*.docx
ls -la outputs/reviews/  # Should contain feedback_*.txt

# 3. Test link metadata creation
# After saving feedback, check for link file:
ls -la outputs/reviews/*_link.json

# Verify link content:
cat outputs/reviews/feedback_*_link.json | python -m json.tool

# Expected structure:
# {
#   "dmp_file": "DMP_....docx",
#   "review_file": "feedback_....txt",
#   "linked_at": "2025-11-19T...",
#   "grant_id": "..."
# }

# 4. Test download from organized folders
curl -I http://localhost:5000/download/<filename>
# Should find file in correct organized folder

# 5. Verify migration worked
python -c "
import os

counts = {
    'cache': len([f for f in os.listdir('outputs/cache') if f.endswith('.json')]),
    'dmp': len([f for f in os.listdir('outputs/dmp') if f.startswith('DMP_')]),
    'reviews': len([f for f in os.listdir('outputs/reviews') if f.startswith('feedback_')])
}

print('File counts:')
for folder, count in counts.items():
    print(f'  {folder:8}: {count} files')
"
```

### Commit:
```bash
git add app.py migrate_files.py
git commit -m "Implement file organization: separate dmp/, reviews/, cache/

- Added get_organized_path() helper function
- Added create_file_link_metadata() for DMP-review links
- Updated upload route to save cache to outputs/cache/
- Updated save_feedback to save reviews to outputs/reviews/
- Updated download route to check all organized folders
- Created migration script for existing files
- DMPs and reviews now linked via JSON metadata files"
```

---

## Task 2.4: Unconnected Text Modal (Post-Upload)

**Priority:** MEDIUM
**Files:** `templates/index.html`, `static/js/script.js`, `app.py`
**Goal:** Show modal for unconnected text assignment immediately after upload, before review

### Implementation:

#### Step 1: Add Modal HTML

**File:** `templates/index.html`

Add before the `</body>` tag:

```html
<!-- Unconnected Text Assignment Modal -->
<div id="unconnected-modal" class="modal" style="display: none;">
    <div class="modal-overlay" onclick="closeUnconnectedModal()"></div>
    <div class="modal-content large-modal">
        <div class="modal-header">
            <h2>
                <i class="fas fa-clipboard-list"></i>
                Assign Unconnected Text
            </h2>
            <button class="modal-close" onclick="closeUnconnectedModal()">
                <i class="fas fa-times"></i>
            </button>
        </div>

        <div class="modal-body">
            <p class="modal-description">
                Some text couldn't be automatically assigned to DMP sections.
                Please review and assign manually, or skip to continue.
            </p>

            <div id="unconnected-text-list">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <div class="modal-footer">
            <button class="btn-secondary" onclick="skipUnconnectedText()">
                <i class="fas fa-forward"></i>
                Skip for Now
            </button>
            <button class="btn-primary" onclick="saveAssignments()">
                <i class="fas fa-save"></i>
                Save Assignments
            </button>
            <button class="btn-success" onclick="proceedToReview()">
                <i class="fas fa-arrow-right"></i>
                Proceed to Review
            </button>
        </div>
    </div>
</div>
```

#### Step 2: Add Modal JavaScript

**File:** `static/js/script.js`

Add these functions:

```javascript
// Unconnected Text Modal Management
let currentCacheId = null;
let currentFilename = null;
let unconnectedTexts = [];

async function checkUnconnectedText(cacheId, filename) {
    """Check if there's unconnected text to assign"""
    currentCacheId = cacheId;
    currentFilename = filename;

    try {
        const response = await fetch(`/api/get-unconnected/${cacheId}`);
        const data = await response.json();

        if (data.success && data.has_unconnected) {
            unconnectedTexts = data.texts;
            showUnconnectedModal(data.texts);
        } else {
            // No unconnected text, go directly to review
            proceedToReview();
        }
    } catch (error) {
        console.error('Error checking unconnected text:', error);
        // On error, proceed to review anyway
        proceedToReview();
    }
}

function showUnconnectedModal(texts) {
    const modal = document.getElementById('unconnected-modal');
    const list = document.getElementById('unconnected-text-list');

    if (!modal || !list) return;

    // Clear existing content
    list.innerHTML = '';

    // Render each unconnected text block
    texts.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'unconnected-item';
        div.innerHTML = `
            <div class="unconnected-header">
                <span class="unconnected-index">#${index + 1}</span>
                <span class="unconnected-type">${item.type || 'no_section'}</span>
            </div>
            <div class="unconnected-text">
                ${escapeHtml(item.text.substring(0, 200))}${item.text.length > 200 ? '...' : ''}
            </div>
            <div class="unconnected-actions">
                <label>Assign to section:</label>
                <select class="section-select" data-index="${index}">
                    <option value="">-- Keep Unconnected --</option>
                    ${getSectionOptions()}
                </select>
            </div>
        `;
        list.appendChild(div);
    });

    // Show modal
    modal.style.display = 'flex';
}

function closeUnconnectedModal() {
    const modal = document.getElementById('unconnected-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function skipUnconnectedText() {
    """Skip assignment and proceed to review"""
    closeUnconnectedModal();
    proceedToReview();
}

async function saveAssignments() {
    """Save manual text assignments"""
    const selects = document.querySelectorAll('.section-select');
    const assignments = [];

    selects.forEach(select => {
        const index = parseInt(select.dataset.index);
        const sectionId = select.value;

        if (sectionId) {
            assignments.push({
                text_index: index,
                section_id: sectionId,
                text: unconnectedTexts[index].text
            });
        }
    });

    if (assignments.length === 0) {
        // No assignments made, just proceed
        proceedToReview();
        return;
    }

    try {
        const response = await fetch('/api/assign-unconnected', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                cache_id: currentCacheId,
                assignments: assignments
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Assigned ${assignments.length} text block(s)`, 'success');
            closeUnconnectedModal();
            proceedToReview();
        } else {
            showToast('Error saving assignments: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error saving assignments:', error);
        showToast('Error saving assignments', 'error');
    }
}

function proceedToReview() {
    """Navigate to review page"""
    if (currentFilename && currentCacheId) {
        window.location.href = `/review/${currentFilename}?cache_id=${currentCacheId}`;
    }
}

function getSectionOptions() {
    """Generate options for section select"""
    // Load from global DMP structure if available
    // For now, hardcoded sections
    const sections = [
        '1.1', '1.2', '2.1', '2.2', '3.1', '3.2',
        '4.1', '4.2', '5.1', '5.2', '6.1', '6.2'
    ];

    return sections.map(id => `<option value="${id}">${id}</option>`).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

#### Step 3: Update Upload Success Handler

**File:** `static/js/script.js`

Find the upload success handler and modify:

```javascript
// In uploadBtn click handler or wherever upload succeeds
if (data.success) {
    const filename = data.filename;
    const cacheId = data.cache_id;

    // CHANGE: Check for unconnected text before redirecting
    checkUnconnectedText(cacheId, filename);

    // REMOVE: Direct redirect
    // window.location.href = `/review/${filename}?cache_id=${cacheId}`;
}
```

#### Step 4: Add Backend API Endpoint

**File:** `app.py`

Add new routes:

```python
@app.route('/api/get-unconnected/<cache_id>', methods=['GET'])
def get_unconnected_text(cache_id):
    """Get unconnected text from cache"""
    try:
        cache_filename = f'cache_{cache_id}.json'
        cache_path = get_organized_path('cache', cache_filename)

        if not os.path.exists(cache_path):
            return jsonify({
                'success': False,
                'message': 'Cache file not found'
            }), 404

        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        unconnected = cache_data.get('_unconnected_text', [])

        return jsonify({
            'success': True,
            'has_unconnected': len(unconnected) > 0,
            'texts': unconnected,
            'count': len(unconnected)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/assign-unconnected', methods=['POST'])
def assign_unconnected_text():
    """Assign unconnected text to sections"""
    try:
        data = request.json
        cache_id = data.get('cache_id')
        assignments = data.get('assignments', [])

        if not cache_id:
            return jsonify({
                'success': False,
                'message': 'No cache_id provided'
            }), 400

        cache_filename = f'cache_{cache_id}.json'
        cache_path = get_organized_path('cache', cache_filename)

        if not os.path.exists(cache_path):
            return jsonify({
                'success': False,
                'message': 'Cache file not found'
            }), 404

        # Load cache
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Apply assignments
        unconnected = cache_data.get('_unconnected_text', [])

        for assignment in assignments:
            text_index = assignment['text_index']
            section_id = assignment['section_id']
            text = assignment['text']

            # Add to section
            if section_id not in cache_data:
                cache_data[section_id] = {
                    'paragraphs': [],
                    'tagged_paragraphs': []
                }

            cache_data[section_id]['paragraphs'].append(text)
            cache_data[section_id]['tagged_paragraphs'].append({
                'text': text,
                'tags': ['manually_assigned'],
                'title': ''
            })

            # Remove from unconnected (mark as assigned)
            if text_index < len(unconnected):
                unconnected[text_index]['assigned'] = True
                unconnected[text_index]['assigned_to'] = section_id

        # Update cache
        cache_data['_unconnected_text'] = unconnected

        # Save updated cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'message': 'Assignments saved',
            'assigned_count': len(assignments)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
```

#### Step 5: Add Modal CSS

**File:** `static/css/style.css`

Add modal styles:

```css
/* Unconnected Text Modal */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2000;
    justify-content: center;
    align-items: center;
}

.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
}

.modal-content {
    position: relative;
    background: var(--bg-card);
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    z-index: 2001;
}

.modal-content.large-modal {
    max-width: 800px;
}

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.modal-close {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--text-secondary);
    transition: color 0.2s;
}

.modal-close:hover {
    color: var(--error-color);
}

.modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
}

.modal-description {
    color: var(--text-secondary);
    margin-bottom: 1.5rem;
}

.modal-footer {
    padding: 1.5rem;
    border-top: 1px solid var(--border-light);
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
}

/* Unconnected Text Items */
.unconnected-item {
    background: var(--bg-secondary);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.unconnected-header {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem;
}

.unconnected-index {
    background: var(--primary-color);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.875rem;
}

.unconnected-type {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.unconnected-text {
    background: var(--bg-tertiary);
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    line-height: 1.5;
}

.unconnected-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.section-select {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid var(--border-medium);
    border-radius: 4px;
    background: var(--bg-card);
    color: var(--text-primary);
}
```

### Testing Task 2.4:

```bash
# 1. Test modal appears after upload
# Upload test file
# Verify:
# - Modal appears automatically
# - Shows unconnected text blocks
# - Has section assignment dropdowns

# 2. Test skip functionality
# Click "Skip for Now"
# Verify:
# - Modal closes
# - Proceeds to review page
# - Unconnected text still in "_unconnected_text"

# 3. Test assignment functionality
# Upload file again
# In modal:
# - Assign text block #1 to section 1.1
# - Assign text block #2 to section 2.1
# - Leave text block #3 unassigned
# Click "Save Assignments"
# Verify:
# - Toast shows "Assigned 2 text block(s)"
# - Proceeds to review page
# - Assigned texts appear in correct sections
# - Unassigned text still in "_unconnected_text"

# 4. Test API endpoints
curl -s http://localhost:5000/api/get-unconnected/<cache_id> | python -m json.tool

# Test assignment API
curl -X POST http://localhost:5000/api/assign-unconnected \
  -H "Content-Type: application/json" \
  -d '{
    "cache_id": "<cache_id>",
    "assignments": [
      {"text_index": 0, "section_id": "1.1", "text": "Test text"}
    ]
  }' | python -m json.tool

# 5. Test modal styling
# Verify:
# - Modal centered on screen
# - Overlay darkens background
# - Modal scrolls if content too tall
# - Buttons properly aligned
# - Responsive on different screen sizes
```

### Commit:
```bash
git add templates/index.html static/js/script.js static/css/style.css app.py
git commit -m "Add unconnected text assignment modal (post-upload)

- Added modal shown immediately after extraction
- Users assign unconnected text to sections before review
- Added /api/get-unconnected/<cache_id> endpoint
- Added /api/assign-unconnected POST endpoint
- Modal shows all unconnected text blocks
- Can skip or save assignments
- Assignments update cache file
- Better workflow: assign → review (not during review)"
```

---

## Task 2.5: Unify Font System

**Priority:** LOW
**Files:** `static/css/style.css`, all HTML templates
**Goal:** Single font stack across entire application

### Implementation:

#### Step 1: Define Font Variables

**File:** `static/css/style.css`

Add to `:root` section:

```css
:root {
    /* Typography */
    --font-family-primary: 'Segoe UI', -apple-system, BlinkMacSystemFont,
                           'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell',
                           'Helvetica Neue', Arial, sans-serif,
                           'Apple Color Emoji', 'Segoe UI Emoji';

    --font-family-monospace: 'SF Mono', 'Monaco', 'Cascadia Code',
                             'Roboto Mono', 'Courier New', monospace;

    /* Font sizes */
    --font-size-xs: 0.75rem;    /* 12px */
    --font-size-sm: 0.875rem;   /* 14px */
    --font-size-base: 1rem;     /* 16px */
    --font-size-lg: 1.125rem;   /* 18px */
    --font-size-xl: 1.25rem;    /* 20px */
    --font-size-2xl: 1.5rem;    /* 24px */
    --font-size-3xl: 1.875rem;  /* 30px */

    /* Font weights */
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;

    /* Line heights */
    --line-height-tight: 1.25;
    --line-height-normal: 1.5;
    --line-height-relaxed: 1.75;
}
```

#### Step 2: Apply to Base Elements

**File:** `static/css/style.css`

Update base typography:

```css
/* Base Typography */
body {
    font-family: var(--font-family-primary);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-normal);
    line-height: var(--line-height-normal);
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-family-primary);
    font-weight: var(--font-weight-semibold);
    line-height: var(--line-height-tight);
}

h1 { font-size: var(--font-size-3xl); }
h2 { font-size: var(--font-size-2xl); }
h3 { font-size: var(--font-size-xl); }
h4 { font-size: var(--font-size-lg); }
h5, h6 { font-size: var(--font-size-base); }

/* Form elements */
input, textarea, select, button {
    font-family: var(--font-family-primary);
    font-size: var(--font-size-base);
}

/* Code and preformatted text */
code, pre, .monospace {
    font-family: var(--font-family-monospace);
    font-size: var(--font-size-sm);
}
```

#### Step 3: Replace All font-family Declarations

```bash
# Find and replace existing font-family declarations
grep -n "font-family:" static/css/style.css

# Replace each with appropriate variable:
# - Regular text → var(--font-family-primary)
# - Code/monospace → var(--font-family-monospace)
```

### Testing Task 2.5:

```bash
# 1. Check font consistency
# Open each page:
# - http://localhost:5000/
# - http://localhost:5000/template_editor
# - http://localhost:5000/documentation
# - http://localhost:5000/review/<file>?cache_id=<id>

# Verify same font on all pages

# 2. Test font loading
python -c "
import re

with open('static/css/style.css', 'r') as f:
    css = f.read()

# Count font-family declarations
primary_count = css.count('var(--font-family-primary)')
mono_count = css.count('var(--font-family-monospace)')
hardcoded = len(re.findall(r'font-family:\s*[^v]', css))

print(f'Using primary font variable: {primary_count}')
print(f'Using monospace variable: {mono_count}')
print(f'Hardcoded fonts remaining: {hardcoded}')
print()
if hardcoded > 0:
    print('❌ Still have hardcoded fonts')
else:
    print('✅ All fonts use variables')
"

# 3. Visual inspection
# Check consistency of:
# - Headers
# - Body text
# - Buttons
# - Form inputs
# - Navigation
# - Sidebar
# - Modal text
```

### Commit:
```bash
git add static/css/style.css
git commit -m "Unify font system with CSS variables

- Added --font-family-primary variable
- Added --font-family-monospace variable
- Added font size scale (xs to 3xl)
- Added font weight scale
- Added line height scale
- Replaced all hardcoded font-family declarations
- Consistent typography across entire application"
```

---

## Phase 2 Completion Checklist

```bash
# Run comprehensive Phase 2 analysis
python -c "
import os
import subprocess
import json

print('=' * 60)
print('PHASE 2 POST-IMPLEMENTATION ANALYSIS')
print('=' * 60)

# 1. Check dynamic categories
print('\n1. DYNAMIC CATEGORIES:')
try:
    import requests
    resp = requests.get('http://localhost:5000/api/discover-categories')
    data = resp.json()
    if data['success']:
        print(f'  ✅ API works, {data[\"count\"]} categories found')
        for cat in data['categories'][:3]:
            print(f'     - {cat[\"display_name\"]}')
    else:
        print('  ❌ API failed')
except Exception as e:
    print(f'  ❌ Error: {e}')

# 2. Check !important count
print('\n2. !IMPORTANT DECLARATIONS:')
result = subprocess.run(
    ['grep', '-c', '!important', 'templates/review.html'],
    capture_output=True, text=True
)
count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
status = '✅' if count < 5 else '❌'
print(f'  {status} review.html: {count} instances')

# 3. Check file organization
print('\n3. FILE ORGANIZATION:')
folders = ['outputs/dmp', 'outputs/reviews', 'outputs/cache']
for folder in folders:
    exists = os.path.exists(folder)
    count = len(os.listdir(folder)) if exists else 0
    status = '✅' if exists else '❌'
    print(f'  {status} {folder}: {count} files')

# 4. Check modal exists
print('\n4. UNCONNECTED TEXT MODAL:')
with open('templates/index.html', 'r') as f:
    html = f.read()
modal_exists = 'unconnected-modal' in html
status = '✅' if modal_exists else '❌'
print(f'  {status} Modal HTML present')

# 5. Check font variables
print('\n5. FONT UNIFICATION:')
with open('static/css/style.css', 'r') as f:
    css = f.read()
has_primary = '--font-family-primary' in css
has_mono = '--font-family-monospace' in css
status = '✅' if has_primary and has_mono else '❌'
print(f'  {status} Font variables defined')

print('\n' + '=' * 60)
print('ANALYSIS COMPLETE')
print('=' * 60)
"
```

### Success Criteria Validation:

- [ ] `/api/discover-categories` returns categories
- [ ] Template editor shows all categories dynamically
- [ ] Can create new category via UI
- [ ] Can delete category via UI (with confirmation)
- [ ] Right sidebar uses `position: sticky`
- [ ] Review page has < 5 `!important` declarations
- [ ] Sidebar scrolls with page, doesn't overlay
- [ ] Files organized in dmp/, reviews/, cache/
- [ ] Unconnected text modal appears post-upload
- [ ] Can assign text to sections or skip
- [ ] Font variables defined and used consistently
- [ ] All existing functionality still works
- [ ] No regressions in extraction

---

## Debug Common Issues

### Issue: Categories not loading

```bash
# Check API
curl http://localhost:5000/api/discover-categories

# Check JSON files exist
ls -la config/*.json

# Check JavaScript console
# Should see: "Loaded N categories dynamically"
```

### Issue: Sidebar still overlays

```bash
# Check CSS was updated
grep "position: sticky" static/css/style.css

# Check for leftover !important
grep "right-sidebar" templates/review.html | grep "!important"

# Clear browser cache
```

### Issue: Files not organizing

```bash
# Check helper function
python -c "
from app import get_organized_path
print(get_organized_path('cache', 'test.json'))
"

# Check folders exist
ls -la outputs/
```

---

## Update Instructions for Phase 3

Based on Phase 2 results:

### If All Tests Pass:
✅ Proceed to Phase 3: Layout & Responsive Design

### If Category Loading Failed:
⚠️ Debug before Phase 3:
- Verify JSON files valid
- Check Flask route registered
- Test API endpoint directly

### If Sidebar Still Has Issues:
⚠️ Add to Phase 3:
- Fine-tune sticky positioning
- Adjust spacing and heights
- Test on more screen sizes

### If File Organization Incomplete:
⚠️ Complete before Phase 3:
- Run migration script
- Verify all routes updated
- Test upload/download cycle

---

**Phase 2 Complete - Ready for Phase 3** ✅
