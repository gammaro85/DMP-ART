# test_docx_processing.py
import os
import sys
sys.path.append('.')

from utils.extractor import DMPExtractor
from utils.docx_validator import DocxValidator

def test_docx_processing():
    """Test the enhanced DOCX processing"""
    
    # Test file validation
    test_file = "DMP_sheng4 final.docx"
    
    print("=== DOCX Validation Test ===")
    validator = DocxValidator()
    validation_result = validator.validate_file(test_file)
    
    print(f"File valid: {validation_result['is_valid']}")
    print(f"Errors: {validation_result['errors']}")
    print(f"Warnings: {validation_result['warnings']}")
    print(f"File info: {validation_result['file_info']}")
    
    if validation_result['is_valid']:
        print("\n=== DMP Extraction Test ===")
        extractor = DMPExtractor()
        result = extractor.process_file(test_file, "test_output")
        
        if result['success']:
            print(f"Extraction successful!")
            print(f"Cache ID: {result.get('cache_id', 'N/A')}")
            print(f"Output file: {result.get('filename', 'N/A')}")
        else:
            print(f"Extraction failed: {result['message']}")

if __name__ == "__main__":
    test_docx_processing()