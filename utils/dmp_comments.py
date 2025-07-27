# Simple comment system for DMP ART - Template Editor with Tabs
# This module provides basic structure for the new tab-based template editor

# Quick comments - not related to any specific question
# These appear in a floating window on the review page
QUICK_COMMENTS = [
    # Default empty - will be populated from template editor
]

# Template categories - managed through template editor
# Each category contains comments for specific DMP questions
TEMPLATE_CATEGORIES = {
    # Will be populated dynamically from template editor
    # Structure: "category_name": {"question_id": ["comment1", "comment2", ...]}
}

def get_quick_comments():
    """Returns all quick comments for the floating window"""
    return QUICK_COMMENTS

def get_category_comments(category_name, question_id):
    """Returns comments for a specific category and question"""
    return TEMPLATE_CATEGORIES.get(category_name, {}).get(question_id, [])

def get_all_categories():
    """Returns all available template categories"""
    return list(TEMPLATE_CATEGORIES.keys())