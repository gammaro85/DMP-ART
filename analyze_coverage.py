#!/usr/bin/env python3
"""
Analyze DMP extraction coverage - check which sections/subsections were found
"""

import os
from utils.extractor import DMPExtractor

def analyze_extraction_coverage():
    """Analyze which sections and subsections were found in each test file"""
    extractor = DMPExtractor()
    samples_dir = "test_samples"
    
    # Expected structure (total counts)
    expected_structure = {
        "1. Data description and collection or re-use of existing data": 2,  # subsections 1.1, 1.2
        "2. Documentation and data quality": 2,  # subsections 2.1, 2.2
        "3. Storage and backup during the research process": 2,  # subsections 3.1, 3.2
        "4. Legal requirements, codes of conduct": 2,  # subsections 4.1, 4.2
        "5. Data sharing and long-term preservation": 4,  # subsections 5.1, 5.2, 5.3, 5.4
        "6. Data management responsibilities and resources": 2  # subsections 6.1, 6.2
    }
    
    total_expected = sum(expected_structure.values())  # Should be 14 total subsections
    
    pdf_files = [f for f in os.listdir(samples_dir) if f.endswith('.pdf')]
    
    print("DMP EXTRACTION COVERAGE ANALYSIS")
    print("=" * 60)
    print(f"Expected: 6 sections, {total_expected} subsections total")
    print()
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"FILE {i}: {pdf_file}")
        print("-" * 40)
        
        file_path = os.path.join(samples_dir, pdf_file)
        
        try:
            result = extractor.process_file(file_path, "outputs")
            
            if result.get('success'):
                # Analyze hierarchical result for better coverage info
                all_content = []
                if pdf_file.endswith('.pdf'):
                    # Get raw PDF content for analysis
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        raw_text = ""
                        for page in pdf_reader.pages:
                            raw_text += page.extract_text() + "\n"
                    
                    # Look for DMP section
                    start_pos = -1
                    end_pos = len(raw_text)
                    
                    for start_mark in extractor.start_marks:
                        pos = raw_text.find(start_mark)
                        if pos != -1:
                            start_pos = pos
                            break
                    
                    if start_pos != -1:
                        for end_mark in extractor.end_marks:
                            pos = raw_text.find(end_mark, start_pos)
                            if pos != -1:
                                end_pos = pos
                                break
                        
                        dmp_text = raw_text[start_pos:end_pos]
                        lines = [line.strip() for line in dmp_text.split('\n') if line.strip()]
                        all_content = lines
                
                # Run hierarchical extraction
                hierarchical_result = extractor.extract_hierarchical_content(all_content, is_pdf=True)
                
                sections_found = 0
                subsections_found = 0
                missing_subsections = []
                
                for section_name, expected_count in expected_structure.items():
                    section_data = hierarchical_result['sections'].get(section_name, {})
                    found_in_section = 0
                    
                    print(f"  {section_name}:")
                    
                    for subsection_name in extractor.dmp_structure[section_name]:
                        subsection_data = section_data.get(subsection_name, {})
                        is_found = subsection_data.get('found', False)
                        
                        if is_found:
                            found_in_section += 1
                            subsections_found += 1
                            content_count = len(subsection_data.get('content', []))
                            print(f"    [✓] {subsection_name[:60]}... ({content_count} items)")
                        else:
                            missing_subsections.append(f"{section_name} -> {subsection_name}")
                            print(f"    [X] {subsection_name[:60]}... (NOT FOUND)")
                    
                    if found_in_section > 0:
                        sections_found += 1
                    
                    print(f"    Found: {found_in_section}/{expected_count} subsections")
                    print()
                
                # Summary for this file
                coverage_percent = (subsections_found / total_expected) * 100
                print(f"SUMMARY:")
                print(f"  Sections with content: {sections_found}/6")
                print(f"  Subsections found: {subsections_found}/{total_expected}")
                print(f"  Coverage: {coverage_percent:.1f}%")
                
                if missing_subsections:
                    print(f"  Missing subsections: {len(missing_subsections)}")
                    # for missing in missing_subsections[:3]:  # Show first 3
                    #     print(f"    - {missing[:80]}...")
                
                # Check unassigned content
                unassigned = hierarchical_result.get('unassigned', [])
                if unassigned:
                    print(f"  Unassigned content: {len(unassigned)} items")
            
            else:
                print(f"  ERROR: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"  EXCEPTION: {str(e)}")
        
        print("=" * 60)
        print()

if __name__ == "__main__":
    analyze_extraction_coverage()