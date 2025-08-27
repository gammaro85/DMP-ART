#!/usr/bin/env python3
import sys
import os
import re
import PyPDF2

# Add the utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from extractor import DMPExtractor

def debug_extraction_flow():
    """Debug the full extraction flow for section 6.1"""
    pdf_path = r"C:\Users\kraje\OneDrive\Pulpit\pzd\test\wydruk1733736559184.pdf"
    
    print("=== DEBUGGING FULL EXTRACTION FLOW ===")
    print(f"PDF: {pdf_path}\n")
    
    # Initialize extractor
    extractor = DMPExtractor()
    
    # Run the full extraction process
    result = extractor.process_file(pdf_path, "outputs")
    
    print("=== RESULT STRUCTURE ===")
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    print("\n=== CHECKING SECTION 6.1 RESULT ===")
    if isinstance(result, dict) and '6.1' in result:
        print(f"Section 6.1 paragraphs: {result['6.1']['paragraphs']}")
        print(f"Section 6.1 tagged_paragraphs: {result['6.1']['tagged_paragraphs']}")
    else:
        print("Section 6.1 not found in result or result is not a dict")
        if isinstance(result, dict):
            print("Available keys:", list(result.keys()))
    
    # Load from the cached JSON file instead
    import glob
    import json
    cache_files = glob.glob('outputs/cache_*.json')
    if cache_files:
        newest = max(cache_files, key=os.path.getmtime)
        print(f"\n=== LOADING FROM CACHE: {newest} ===")
        with open(newest, 'r', encoding='utf-8') as f:
            cached_result = json.load(f)
        
        print(f"\n=== CHECKING FOR CONTENT IN CACHED SECTIONS ===")
        target_text = "Open Science Competence Centre"
        
        for section_id, section_data in cached_result.items():
            if section_id.startswith('_'):
                continue
                
            try:
                found_in_paragraphs = any(target_text.lower() in p.lower() for p in section_data['paragraphs'])
                found_in_tagged = any(target_text.lower() in tp['text'].lower() for tp in section_data['tagged_paragraphs'])
                
                if found_in_paragraphs or found_in_tagged:
                    print(f"Found '{target_text}' in section {section_id}")
                    if found_in_paragraphs:
                        matching_paragraphs = [p for p in section_data['paragraphs'] if target_text.lower() in p.lower()]
                        print(f"  In paragraphs: {matching_paragraphs}")
                    if found_in_tagged:
                        matching_tagged = [tp['text'] for tp in section_data['tagged_paragraphs'] if target_text.lower() in tp['text'].lower()]
                        print(f"  In tagged paragraphs: {matching_tagged}")
            except Exception as e:
                print(f"Error processing section {section_id}: {e}")
                print(f"Section data type: {type(section_data)}")
    
    print("\n=== CHECKING UNCONNECTED TEXT ===")
    if '_unconnected_text' in result:
        unconnected = result['_unconnected_text']
        for item in unconnected:
            if target_text.lower() in item['text'].lower():
                print(f"Found in unconnected text: {item}")

if __name__ == "__main__":
    debug_extraction_flow()