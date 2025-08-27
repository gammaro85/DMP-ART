#!/usr/bin/env python3
"""
Test script for the DMP extractor to validate improvements
"""

import os
import sys
from datetime import datetime
from utils.extractor import DMPExtractor

def test_extractor_on_samples():
    """Test the extractor on all sample files"""
    extractor = DMPExtractor()
    samples_dir = "test_samples"
    
    if not os.path.exists(samples_dir):
        print(f"Error: {samples_dir} directory not found")
        return
    
    pdf_files = [f for f in os.listdir(samples_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {samples_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to test:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    print("\n" + "="*80)
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\nTEST {i}/{len(pdf_files)}: {pdf_file}")
        print("-" * 60)
        
        file_path = os.path.join(samples_dir, pdf_file)
        
        try:
            # Extract content
            print("Starting extraction...")
            result = extractor.process_file(file_path, "outputs")
            
            print(f"Extraction completed!")
            print(f"Success: {result.get('success', False)}")
            
            if result.get('success'):
                sections = result.get('sections', {})
                print(f"Sections found: {len(sections)}")
                
                # Print summary of findings
                for section_name, section_data in sections.items():
                    print(f"\n  Section: {section_name}")
                    if isinstance(section_data, dict):
                        for subsection_name, subsection_data in section_data.items():
                            if isinstance(subsection_data, dict) and subsection_data.get('found', False):
                                content_count = len(subsection_data.get('content', []))
                                raw_text_length = len(subsection_data.get('raw_text', ''))
                                print(f"    ✓ {subsection_name}: {content_count} items, {raw_text_length} chars")
                                
                                # Show if "nie dotyczy" was found
                                content = subsection_data.get('content', [])
                                if any('nie dotyczy' in str(item).lower() for item in content):
                                    print(f"      → Contains 'nie dotyczy'")
                
                # Check for unassigned content
                unassigned = result.get('unassigned', [])
                if unassigned:
                    print(f"\n  Unassigned content: {len(unassigned)} items")
            
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Exception during extraction: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80)
    
    print("\nTesting completed!")

if __name__ == "__main__":
    test_extractor_on_samples()