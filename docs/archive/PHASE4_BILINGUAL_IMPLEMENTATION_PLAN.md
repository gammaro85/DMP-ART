# Phase 4: Bilingual PL/EN Comment Switcher - Implementation Plan

**Priority:** URGENT (per user request)
**Date:** 2025-11-17
**Status:** In Progress

---

## Objective

Add Polish/English language switcher for comments ONLY (not the entire UI). Users should be able to toggle between Polish and English versions of category comments and quick comments.

---

## Current Structure Analysis

### Category Comments (newcomer.json, mising.json, ready.json)

**Current Format:**
```json
{
  "newcomer": {
    "1.1": [
      "English comment text here...",
      "Another English comment..."
    ],
    "1.2": [...]
  }
}
```

**Target Format:**
```json
{
  "newcomer": {
    "1.1": [
      {
        "en": "English comment text here...",
        "pl": "Polski tekst komentarza tutaj..."
      },
      {
        "en": "Another English comment...",
        "pl": "Inny polski komentarz..."
      }
    ],
    "1.2": [...]
  }
}
```

### Quick Comments (quick_comments.json)

**Current Format:**
```json
{
  "quick_comments": [
    {
      "name": "minor adjustments",
      "text": "The plan is very good, just need to add some information."
    }
  ]
}
```

**Target Format:**
```json
{
  "quick_comments": [
    {
      "name": "minor adjustments",
      "text": {
        "en": "The plan is very good, just need to add some information.",
        "pl": "Plan jest bardzo dobry, wystarczy dodać kilka informacji."
      }
    }
  ]
}
```

---

## Implementation Steps

### Step 1: Migration Script (migrate_to_bilingual.py)

Create a Python script to convert existing JSON files to bilingual format:

- **For each category file** (newcomer.json, mising.json, ready.json):
  - Read current structure
  - For each comment (string), convert to: `{"en": original_string, "pl": original_string}`
  - Save backup of original file as `{filename}_backup.json`
  - Write new bilingual structure

- **For quick_comments.json**:
  - Convert `"text"` field from string to `{"en": string, "pl": string}`
  - Initially use same text for both languages (can be translated later)

### Step 2: Backend Updates (app.py)

**No changes needed!** The backend just loads JSON and passes it to frontend. The frontend will handle language selection.

### Step 3: Frontend Updates (review.html)

#### 3.1 Language State Management

Add to JavaScript:
```javascript
// Language preference (stored in localStorage)
let currentLanguage = localStorage.getItem('dmp-art-comment-language') || 'en';

function setCommentLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('dmp-art-comment-language', lang);
    updateLanguageUI();
    refreshComments();
}
```

#### 3.2 Language Switcher UI

Add language toggle button in sidebar:
```html
<div class="language-switcher">
    <button id="lang-en-btn" class="lang-btn active">EN</button>
    <button id="lang-pl-btn" class="lang-btn">PL</button>
</div>
```

Style:
```css
.language-switcher {
    margin-bottom: 15px;
    display: flex;
    gap: 5px;
}

.lang-btn {
    flex: 1;
    padding: 8px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    cursor: pointer;
    border-radius: 4px;
}

.lang-btn.active {
    background: var(--primary-color);
    color: white;
    font-weight: bold;
}
```

#### 3.3 Comment Loading Logic

Update functions that insert comments:

**For Quick Comments:**
```javascript
// OLD:
commentDiv.textContent = comment.text;

// NEW:
const commentText = typeof comment.text === 'string'
    ? comment.text  // Backward compatibility
    : comment.text[currentLanguage];
commentDiv.textContent = commentText;
```

**For Category Comments:**
```javascript
// OLD:
commentItem.textContent = comment;

// NEW:
const commentText = typeof comment === 'string'
    ? comment  // Backward compatibility
    : comment[currentLanguage];
commentItem.textContent = commentText;
```

### Step 4: Template Editor Updates (template_editor.html)

#### 4.1 Quick Comments Editor

Change from single textarea to dual textareas:

**OLD:**
```html
<textarea id="quick-comment-text-{index}" placeholder="Comment text">{text}</textarea>
```

**NEW:**
```html
<label>English:</label>
<textarea id="quick-comment-text-en-{index}" placeholder="English comment text">{text.en}</textarea>

<label>Polish (PL):</label>
<textarea id="quick-comment-text-pl-{index}" placeholder="Polski tekst komentarza">{text.pl}</textarea>
```

#### 4.2 Category Comments Editor

Change from single textarea to dual textareas:

**OLD:**
```html
<textarea class="category-comment-textarea">{comment}</textarea>
```

**NEW:**
```html
<div class="bilingual-comment-editor">
    <div class="lang-field">
        <label>EN:</label>
        <textarea class="category-comment-textarea-en">{comment.en}</textarea>
    </div>
    <div class="lang-field">
        <label>PL:</label>
        <textarea class="category-comment-textarea-pl">{comment.pl}</textarea>
    </div>
</div>
```

#### 4.3 Save Logic

Update save functions to collect both language versions:

```javascript
// For quick comments
quickComments.push({
    name: name,
    text: {
        en: document.getElementById(`quick-comment-text-en-${i}`).value,
        pl: document.getElementById(`quick-comment-text-pl-${i}`).value
    }
});

// For category comments
categoryData[sectionId].push({
    en: textarea.querySelector('.category-comment-textarea-en').value,
    pl: textarea.querySelector('.category-comment-textarea-pl').value
});
```

---

## Testing Plan

### 1. Migration Testing
- ✅ Run migration script
- ✅ Verify backup files created
- ✅ Validate new JSON structure
- ✅ Test with sample category file

### 2. Frontend Testing
- Test language switcher (EN ↔ PL)
- Verify localStorage persistence
- Test quick comment insertion in both languages
- Test category comment dropdown in both languages
- Test citation feature with bilingual comments
- Test compiled feedback panel with bilingual comments

### 3. Template Editor Testing
- Test viewing existing bilingual comments
- Test editing both EN and PL versions
- Test adding new bilingual comments
- Test deleting bilingual comments
- Test saving and reloading

### 4. Backward Compatibility Testing
- Test loading old-format JSON files (if not migrated)
- Verify fallback to English if PL missing
- Verify graceful handling of mixed formats

---

## Rollback Plan

If issues arise:
1. Restore backup files: `cp config/*_backup.json config/`
2. Revert frontend changes in review.html
3. Revert template editor changes in template_editor.html

---

## Translation Strategy

**Initial approach:** Use same text for both EN and PL (migration script)

**Future translation options:**
1. Manual translation by domain expert (recommended for quality)
2. Semi-automated: Use translation service, then manual review
3. Collaborative: Create translation spreadsheet for contributors

**Priority translations:**
- Quick comments (7 items - quick to translate)
- Ready category (smaller, commonly used)
- Newcomer category (large but highest value)
- Missing category (medium priority)

---

## UI/UX Considerations

### Language Switcher Placement
**Option 1:** Top of sidebar (always visible) ← RECOMMENDED
**Option 2:** Near quick comments section
**Option 3:** As dropdown in navbar

### Visual Feedback
- Active language button highlighted
- Show current language with icon or badge
- Consider flag icons (🇬🇧/🇵🇱) for clarity

### User Preferences
- Save language preference in localStorage
- Persist across sessions
- Default to 'en' for new users

---

## Success Criteria

- ✅ Users can switch between EN and PL comments with one click
- ✅ Language preference persists across sessions
- ✅ All comments support both languages
- ✅ Template editor allows editing both versions
- ✅ Backward compatible with single-language comments
- ✅ No performance degradation
- ✅ UI language (buttons, labels) remains English

---

## Timeline

1. **Migration Script:** 30 minutes ← CURRENT
2. **Frontend Language Switcher:** 1 hour
3. **Comment Loading Logic:** 1 hour
4. **Template Editor Updates:** 2 hours
5. **Testing:** 1 hour
6. **Translation (Optional):** 3-5 hours (separate task)

**Total Estimated Time:** 5-6 hours

---

## Notes

- User specified: "1 - urgent" for bilingual comments
- Only comments switch language, not the entire UI
- English remains the default/fallback language
- Polish translations can be added gradually
- Consider adding translation UI in template editor later

---

**Next Action:** Create and run migration script to convert existing JSON files to bilingual format.
