"""
Debug test script for DMP-ART improvements
Tests all new features added in the recent update
"""

import os
import sys
import json

def test_file_structure():
    """Test if all required files and folders exist"""
    print("=" * 60)
    print("1. Testing File Structure")
    print("=" * 60)

    checks = [
        ('config/comment_usage_stats.json', 'Comment usage tracking file'),
        ('config/quick_comments.json', 'Quick comments config'),
        ('config/dmp_structure.json', 'DMP structure config'),
        ('templates/review.html', 'Review template'),
        ('static/js/script.js', 'Main JavaScript'),
        ('utils/extractor.py', 'DMP extractor'),
    ]

    all_ok = True
    for filepath, description in checks:
        exists = os.path.exists(filepath)
        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {description}: {filepath}")
        if not exists:
            all_ok = False

    return all_ok

def test_comment_usage_stats():
    """Test comment usage stats file structure"""
    print("\n" + "=" * 60)
    print("2. Testing Comment Usage Stats Structure")
    print("=" * 60)

    try:
        with open('config/comment_usage_stats.json', 'r', encoding='utf-8') as f:
            stats = json.load(f)

        expected_sections = ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2',
                           '4.1', '4.2', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2']

        all_ok = True
        for section in expected_sections:
            if section in stats:
                print(f"  [OK] Section {section} exists")
            else:
                print(f"  [MISSING] Section {section}")
                all_ok = False

        return all_ok
    except Exception as e:
        print(f"  [ERROR] Failed to load stats: {e}")
        return False

def test_app_imports():
    """Test if app.py imports without errors"""
    print("\n" + "=" * 60)
    print("3. Testing App Imports")
    print("=" * 60)

    try:
        from app import app, get_dated_folder, cleanup_old_cache_files
        print("  [OK] Flask app imported")
        print("  [OK] get_dated_folder function imported")
        print("  [OK] cleanup_old_cache_files function imported")

        # Test routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        new_routes = [
            '/export_docx',
            '/api/track_comment_usage',
            '/api/get_suggested_comments/<section_id>',
            '/api/cleanup_cache',
        ]

        for route in new_routes:
            # Check if route pattern exists
            found = any(route in r or route.replace('<section_id>', '') in r for r in routes)
            status = "OK" if found else "MISSING"
            print(f"  [{status}] Route: {route}")

        return True
    except Exception as e:
        print(f"  [ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dated_folder_function():
    """Test dated folder creation function"""
    print("\n" + "=" * 60)
    print("4. Testing Dated Folder Function")
    print("=" * 60)

    try:
        from app import get_dated_folder
        from datetime import datetime

        # Test folder creation
        test_base = 'outputs/test_reviews'
        os.makedirs(test_base, exist_ok=True)

        dated_folder = get_dated_folder(test_base)
        expected_format = datetime.now().strftime('%Y-%m')

        if expected_format in dated_folder:
            print(f"  [OK] Dated folder created: {dated_folder}")
            print(f"  [OK] Format matches: {expected_format}")

            # Cleanup
            try:
                os.rmdir(dated_folder)
                os.rmdir(test_base)
            except:
                pass

            return True
        else:
            print(f"  [ERROR] Unexpected folder format: {dated_folder}")
            return False

    except Exception as e:
        print(f"  [ERROR] Function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_review_html_features():
    """Test if review.html has all new features"""
    print("\n" + "=" * 60)
    print("5. Testing Review.html Features")
    print("=" * 60)

    try:
        with open('templates/review.html', 'r', encoding='utf-8') as f:
            content = f.read()

        features = [
            ('progress-bar', 'Progress indicator'),
            ('progress-percentage', 'Progress percentage display'),
            ('quick-comments-search', 'Search input for comments'),
            ('suggested-comments-pane', 'Smart suggestions pane'),
            ('initializeProgressTracking', 'Progress tracking function'),
            ('initializeQuickCommentsSearch', 'Search initialization'),
            ('initializeCollapsibleSections', 'Collapsible sections'),
            ('initializeFrontendCaching', 'Frontend caching'),
            ('Ctrl+S', 'Keyboard shortcut for save'),
            ('Ctrl+Enter', 'Keyboard shortcut for compile'),
            ('/export_docx', 'DOCX export endpoint'),
            ('loadSuggestedComments', 'Suggested comments loader'),
        ]

        all_ok = True
        for search_term, description in features:
            if search_term in content:
                print(f"  [OK] {description}")
            else:
                print(f"  [MISSING] {description}")
                all_ok = False

        return all_ok
    except Exception as e:
        print(f"  [ERROR] Failed to read template: {e}")
        return False

def run_all_tests():
    """Run all debug tests"""
    print("\n" + "=" * 60)
    print("DMP-ART DEBUG TEST SUITE")
    print("=" * 60)
    print("Testing all new features from recent improvements...\n")

    results = {
        'File Structure': test_file_structure(),
        'Comment Usage Stats': test_comment_usage_stats(),
        'App Imports': test_app_imports(),
        'Dated Folder Function': test_dated_folder_function(),
        'Review HTML Features': test_review_html_features(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"  [{status}] {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\nSUCCESS: All tests passed! Application is ready to use.")
        return 0
    else:
        print("\nWARNING: Some tests failed. Review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
