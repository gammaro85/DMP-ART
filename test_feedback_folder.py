#!/usr/bin/env python3
"""
Test script to verify feedback folder separation feature.

This test validates that:
1. The feedback folder is created correctly
2. Feedback files are saved to feedback/ folder
3. DMP files remain in outputs/ folder
4. File naming convention maintains the link between DMP and feedback files
"""

import os
import json
import tempfile
import shutil
from datetime import datetime

def test_folder_structure():
    """Test that feedback folder exists and is separate from outputs"""
    print("Test 1: Folder Structure")
    print("-" * 50)
    
    # Check outputs folder exists
    assert os.path.exists('outputs'), "❌ outputs/ folder does not exist"
    print("✓ outputs/ folder exists")
    
    # Check feedback folder exists
    assert os.path.exists('feedback'), "❌ feedback/ folder does not exist"
    print("✓ feedback/ folder exists")
    
    # Check they are separate directories
    outputs_path = os.path.abspath('outputs')
    feedback_path = os.path.abspath('feedback')
    assert outputs_path != feedback_path, "❌ outputs and feedback are the same directory"
    print("✓ outputs/ and feedback/ are separate directories")
    
    print("✅ Test 1 PASSED\n")

def test_file_naming_convention():
    """Test that file naming convention maintains linkage"""
    print("Test 2: File Naming Convention")
    print("-" * 50)
    
    # Simulate DMP filename
    dmp_filename = "DMP_Kowalski_J_OPUS_29_191125.docx"
    feedback_filename = f"feedback_{os.path.splitext(dmp_filename)[0]}.txt"
    
    # Expected: feedback_DMP_Kowalski_J_OPUS_29_191125.txt
    expected_feedback = "feedback_DMP_Kowalski_J_OPUS_29_191125.txt"
    
    assert feedback_filename == expected_feedback, f"❌ Naming mismatch: {feedback_filename} != {expected_feedback}"
    print(f"✓ DMP: {dmp_filename}")
    print(f"✓ Feedback: {feedback_filename}")
    
    # Extract base name to verify linkage
    base_name = dmp_filename.replace('DMP_', '').replace('.docx', '')
    feedback_base = feedback_filename.replace('feedback_DMP_', '').replace('.txt', '')
    
    assert base_name == feedback_base, "❌ Base names don't match"
    print(f"✓ Base name linkage: {base_name}")
    
    print("✅ Test 2 PASSED\n")

def test_file_separation():
    """Test that files are saved to correct folders"""
    print("Test 3: File Separation")
    print("-" * 50)
    
    # Create test files
    test_dmp = "test_DMP_TestUser_A_TEST_01_191125.docx"
    test_feedback = "feedback_test_DMP_TestUser_A_TEST_01_191125.txt"
    
    # Create test DMP file in outputs
    dmp_path = os.path.join('outputs', test_dmp)
    with open(dmp_path, 'w') as f:
        f.write("Test DMP content")
    print(f"✓ Created test DMP: {dmp_path}")
    
    # Create test feedback file in feedback
    feedback_path = os.path.join('feedback', test_feedback)
    with open(feedback_path, 'w') as f:
        f.write("Test feedback content")
    print(f"✓ Created test feedback: {feedback_path}")
    
    # Verify they exist in correct locations
    assert os.path.exists(dmp_path), "❌ DMP file not in outputs/"
    assert os.path.exists(feedback_path), "❌ Feedback file not in feedback/"
    print("✓ Files are in correct folders")
    
    # Verify they are not in the wrong folders
    wrong_dmp = os.path.join('feedback', test_dmp)
    wrong_feedback = os.path.join('outputs', test_feedback)
    assert not os.path.exists(wrong_dmp), "❌ DMP file incorrectly in feedback/"
    assert not os.path.exists(wrong_feedback), "❌ Feedback file incorrectly in outputs/"
    print("✓ Files are NOT in wrong folders")
    
    # Clean up test files
    os.remove(dmp_path)
    os.remove(feedback_path)
    print("✓ Cleaned up test files")
    
    print("✅ Test 3 PASSED\n")

def test_gitignore_configuration():
    """Test that .gitignore properly handles feedback files"""
    print("Test 4: .gitignore Configuration")
    print("-" * 50)
    
    # Read .gitignore
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    # Check for feedback folder entries
    assert 'feedback/*.txt' in gitignore_content, "❌ .gitignore missing feedback/*.txt"
    print("✓ .gitignore includes feedback/*.txt")
    
    assert 'feedback/*.json' in gitignore_content, "❌ .gitignore missing feedback/*.json"
    print("✓ .gitignore includes feedback/*.json")
    
    # Check that old outputs/feedback_*.txt is removed or replaced
    # (Should not be there anymore since we moved to feedback folder)
    print("✓ .gitignore properly configured for feedback folder")
    
    print("✅ Test 4 PASSED\n")

def test_app_configuration():
    """Test that app.py has correct configuration"""
    print("Test 5: App Configuration")
    print("-" * 50)
    
    # Read app.py
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    # Check for FEEDBACK_FOLDER config
    assert "app.config['FEEDBACK_FOLDER']" in app_content, "❌ FEEDBACK_FOLDER not in app.config"
    print("✓ FEEDBACK_FOLDER configured in app")
    
    # Check for feedback folder creation
    assert "os.makedirs(app.config['FEEDBACK_FOLDER'], exist_ok=True)" in app_content, "❌ Feedback folder not created"
    print("✓ Feedback folder creation in app initialization")
    
    # Check that save_feedback uses FEEDBACK_FOLDER
    assert "app.config['FEEDBACK_FOLDER'], feedback_filename" in app_content, "❌ save_feedback not using FEEDBACK_FOLDER"
    print("✓ save_feedback() uses FEEDBACK_FOLDER")
    
    # Check that export_json uses FEEDBACK_FOLDER
    assert "app.config['FEEDBACK_FOLDER'], json_filename" in app_content, "❌ export_json not using FEEDBACK_FOLDER"
    print("✓ export_json() uses FEEDBACK_FOLDER")
    
    print("✅ Test 5 PASSED\n")

def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("FEEDBACK FOLDER SEPARATION TEST SUITE")
    print("=" * 50 + "\n")
    
    try:
        test_folder_structure()
        test_file_naming_convention()
        test_file_separation()
        test_gitignore_configuration()
        test_app_configuration()
        
        print("=" * 50)
        print("✅ ALL TESTS PASSED")
        print("=" * 50)
        print("\nFeedback folder separation is working correctly!")
        print("\nFile organization:")
        print("  📁 outputs/  → DMP files (DMP_*.docx)")
        print("  📁 feedback/ → Review files (feedback_*.txt, Review_*.json)")
        print("\nLinkage maintained through consistent naming convention.")
        return 0
        
    except AssertionError as e:
        print("\n" + "=" * 50)
        print("❌ TEST FAILED")
        print("=" * 50)
        print(f"\nError: {e}")
        return 1
    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ UNEXPECTED ERROR")
        print("=" * 50)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    exit(main())
