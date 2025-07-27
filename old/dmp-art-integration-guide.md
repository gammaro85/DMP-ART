# DMP ART Integration Guide: Three Categories of Comments

## Overview
This guide shows how to integrate the three categories of DMP review comments into your existing DMP ART application. The categories are designed to serve different user needs and review scenarios.

## Three Categories Explained

### 1. **Newcomer Guidance** (Educational)
- **Purpose**: Help first-time DMP writers understand what each section requires
- **Length**: Longer, descriptive explanations (3-5 paragraphs per section)
- **Tone**: Educational, supportive, with examples
- **When to use**: For researchers new to DMP writing or when sections are left mostly empty

### 2. **Wrong/Missing Information** (Corrections)
- **Purpose**: Point out specific errors or missing required information
- **Types**: 
  - General corrections (e.g., inappropriate storage solutions)
  - Discipline-specific requirements (e.g., bioethical approval for medical research)
- **When to use**: When incorrect information is detected or required elements are missing

### 3. **Ready-to-Use Sentences** (Copy-Paste)
- **Purpose**: Provide standard text that can be directly inserted into DMPs
- **Examples**: Repository descriptions, license statements, GDPR compliance text
- **When to use**: For standard institutional information that doesn't change between projects

## Implementation in app.py

### 1. Update the templates structure (around line 20)

```python
# Add after existing imports
from utils.dmp_comments import (
    NEWCOMER_GUIDANCE,
    WRONG_MISSING_INFO,
    READY_TO_USE_SENTENCES,
    get_relevant_comments
)

# Add discipline mapping for Gdańsk Tech
DISCIPLINE_MAP = {
    "EiF": "economics_finance",
    "ZiJ": "management_quality",
    "ICh": "chemical_engineering",
    "NF": "physical_sciences",
    "M": "mathematics",
    "ILGiT": "civil_engineering",
    "AiU": "architecture_urban_planning",
    "IŚGiE": "environmental_engineering",
    "IMa": "materials_engineering",
    "IMe": "mechanical_engineering",
    "AEEiTK": "automation_electronics",
    "ITiT": "information_technology",
    "IB": "biomedical_engineering",
    "NCh": "chemical_sciences"
}
```

### 2. Modify the review route (around line 400)

```python
@app.route('/review/<filename>')
def review_dmp(filename):
    # ... existing code ...
    
    # Add comment categories to template context
    return render_template('review.html', 
                           filename=filename,
                           templates=DMP_TEMPLATES,
                           comments=COMMON_COMMENTS,
                           newcomer_guidance=NEWCOMER_GUIDANCE,
                           wrong_missing_info=WRONG_MISSING_INFO,
                           ready_to_use=READY_TO_USE_SENTENCES,
                           extracted_content=extracted_content,
                           extraction_info=extraction_info,
                           unconnected_text=unconnected_text,
                           cache_id=cache_id)
```

### 3. Add smart comment suggestion endpoint

```python
@app.route('/get_smart_comments', methods=['POST'])
def get_smart_comments():
    """
    Returns relevant comments based on section content and selected category
    """
    try:
        data = request.json
        section_id = data.get('section_id')
        content = data.get('content', '')
        category = data.get('category', 'newcomer')  # newcomer, wrong_missing, ready_to_use
        discipline = data.get('discipline', None)
        
        comments = get_relevant_comments(section_id, content, category, discipline)
        
        return jsonify({
            'success': True,
            'comments': comments
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
```

## Update review.html Template

### 1. Add category selector for each section

```html
<!-- Add this to each section in review.html -->
<div class="comment-category-selector">
    <label>Comment Type:</label>
    <button class="category-btn active" data-category="newcomer" data-id="{{ section_id }}">
        <i class="fas fa-graduation-cap"></i> Newcomer Guidance
    </button>
    <button class="category-btn" data-category="wrong_missing" data-id="{{ section_id }}">
        <i class="fas fa-exclamation-triangle"></i> Corrections
    </button>
    <button class="category-btn" data-category="ready_to_use" data-id="{{ section_id }}">
        <i class="fas fa-copy"></i> Ready-to-Use
    </button>
</div>

<!-- Comments container with category-specific content -->
<div class="comments-container" id="comments-{{ section_id }}">
    <!-- Comments will be loaded here based on selected category -->
</div>
```

### 2. Add JavaScript for category switching

```javascript
// Add to script.js or inline script in review.html
document.addEventListener('DOMContentLoaded', function() {
    // Handle category button clicks
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-id');
            const category = this.getAttribute('data-category');
            
            // Update active state
            this.parentElement.querySelectorAll('.category-btn').forEach(b => 
                b.classList.remove('active'));
            this.classList.add('active');
            
            // Load comments for selected category
            loadCategoryComments(sectionId, category);
        });
    });
});

function loadCategoryComments(sectionId, category) {
    const content = document.getElementById(`feedback-${sectionId}`).value;
    
    fetch('/get_smart_comments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            section_id: sectionId,
            content: content,
            category: category,
            discipline: getUserDiscipline() // Implement based on your user system
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayComments(sectionId, data.comments, category);
        }
    });
}

function displayComments(sectionId, comments, category) {
    const container = document.getElementById(`comments-${sectionId}`);
    container.innerHTML = '';
    
    comments.forEach((comment, index) => {
        const commentDiv = document.createElement('div');
        commentDiv.className = `comment-item category-${category}`;
        
        // Different styling based on category
        if (category === 'newcomer') {
            commentDiv.innerHTML = `
                <div class="comment-header">
                    <i class="fas fa-lightbulb"></i> Guidance ${index + 1}
                </div>
                <div class="comment-body">${comment}</div>
                <button class="insert-btn" onclick="insertComment('${sectionId}', '${escapeQuotes(comment)}')">
                    <i class="fas fa-plus"></i> Use This Guidance
                </button>
            `;
        } else if (category === 'wrong_missing') {
            commentDiv.innerHTML = `
                <div class="comment-header">
                    <i class="fas fa-exclamation-circle"></i> Issue ${index + 1}
                </div>
                <div class="comment-body">${comment}</div>
                <button class="insert-btn" onclick="insertComment('${sectionId}', '${escapeQuotes(comment)}')">
                    <i class="fas fa-plus"></i> Add This Correction
                </button>
            `;
        } else if (category === 'ready_to_use') {
            commentDiv.innerHTML = `
                <div class="comment-header">
                    <i class="fas fa-clipboard"></i> Standard Text ${index + 1}
                </div>
                <div class="comment-body">${comment}</div>
                <button class="copy-btn" onclick="copyToClipboard('${escapeQuotes(comment)}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="insert-btn" onclick="insertComment('${sectionId}', '${escapeQuotes(comment)}')">
                    <i class="fas fa-plus"></i> Insert
                </button>
            `;
        }
        
        container.appendChild(commentDiv);
    });
}
```

## CSS Styling for Categories

```css
/* Add to your styles.css */
.comment-category-selector {
    display: flex;
    gap: 10px;
    margin: 15px 0;
    align-items: center;
}

.category-btn {
    padding: 8px 16px;
    border: 2px solid var(--border-color);
    background: var(--bg-secondary);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 5px;
}

.category-btn:hover {
    background: var(--bg-hover);
}

.category-btn.active {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
}

.comment-item {
    margin: 10px 0;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.comment-item.category-newcomer {
    background: #e8f4f8;
    border-left: 4px solid #2196F3;
}

.comment-item.category-wrong_missing {
    background: #fff4e5;
    border-left: 4px solid #ff9800;
}

.comment-item.category-ready_to_use {
    background: #e8f5e9;
    border-left: 4px solid #4caf50;
}

[data-theme="dark"] .comment-item.category-newcomer {
    background: #1a2f3a;
}

[data-theme="dark"] .comment-item.category-wrong_missing {
    background: #3a2a1a;
}

[data-theme="dark"] .comment-item.category-ready_to_use {
    background: #1a3a1a;
}

.comment-header {
    font-weight: bold;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.comment-body {
    margin: 10px 0;
    line-height: 1.6;
}
```

## Usage Instructions for Reviewers

### For New Researchers (Newcomer Guidance):
1. Select the "Newcomer Guidance" category
2. Read through the educational explanations
3. Choose relevant guidance to insert as feedback
4. Customize if needed to match the specific project

### For Corrections (Wrong/Missing):
1. Select "Corrections" category
2. System will show relevant corrections based on content
3. For discipline-specific issues, ensure user's discipline is set
4. Insert appropriate corrections into feedback

### For Standard Text (Ready-to-Use):
1. Select "Ready-to-Use" category
2. Copy or insert standard institutional text
3. No modification needed - these are pre-approved statements

## Analytics and Improvement

Track usage of different comment categories to improve the system:

```python
# Add to your analytics
def track_comment_usage(section_id, category, comment_index):
    """Track which comments are most useful"""
    # Implementation depends on your analytics system
    pass
```

## Benefits of This Three-Category System

1. **Efficiency**: Reviewers can quickly select appropriate feedback type
2. **Consistency**: Standard text ensures institutional requirements are communicated uniformly
3. **Education**: Newcomer guidance helps researchers understand the "why" behind requirements
4. **Accuracy**: Discipline-specific corrections catch field-specific issues
5. **Scalability**: Easy to add new comments to each category as patterns emerge

## Future Enhancements

1. **Machine Learning**: Train model to auto-detect which category is most relevant
2. **Discipline Detection**: Automatically determine researcher's field from content
3. **Language Support**: Provide Polish translations for all categories
4. **Feedback Loop**: Allow researchers to rate helpfulness of comments
5. **Integration**: Connect with institutional systems (ethics database, repository)

This implementation provides a comprehensive, user-friendly system for DMP review that serves both experienced and novice researchers while maintaining institutional standards.