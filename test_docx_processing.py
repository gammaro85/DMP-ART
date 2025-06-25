# test_docx_processing.py - FIXED
import os
import sys
sys.path.append('.')

from utils.extractor import DMPExtractor

def test_docx_processing():
    """Test the enhanced DOCX processing"""
    
    # Test file validation
    test_file = "DMP_sheng4 final.docx"
    
    print("=== DOCX Validation Test ===")
    # FIX: Use DMPExtractor instead of non-existent DocxValidator
    extractor = DMPExtractor()
    validation_result = extractor.validate_docx_file(test_file)
    
    print(f"File valid: {validation_result[0]}")
    print(f"Message: {validation_result[1]}")
    
    if validation_result[0]:  # If valid
        print("\n=== DMP Extraction Test ===")
        result = extractor.process_file(test_file, "test_output")
        
        if result['success']:
            print(f"Extraction successful!")
            print(f"Cache ID: {result.get('cache_id', 'N/A')}")
            print(f"Output file: {result.get('filename', 'N/A')}")
        else:
            print(f"Extraction failed: {result['message']}")

if __name__ == "__main__":
    test_docx_processing()