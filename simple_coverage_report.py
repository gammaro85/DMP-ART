#!/usr/bin/env python3
"""
Simple coverage analysis report
"""

import os
from utils.extractor import DMPExtractor

def simple_coverage_analysis():
    """Simple analysis of coverage"""
    extractor = DMPExtractor()
    samples_dir = "test_samples"
    
    # Expected structure
    expected_subsections = [
        "How will new data be collected or produced and/or how will existing data be re-used?",
        "What data (for example the types, formats, and volumes) will be collected or produced?",
        "What metadata and documentation (for example methodology or data collection and way of organising data) will accompany data?",
        "What data quality control measures will be used?",
        "How will data and metadata be stored and backed up during the research process?",
        "How will data security and protection of sensitive data be taken care of during the research?",
        "If personal data are processed, how will compliance with legislation on personal data and on data security be ensured?",
        "How will other legal issues, such as intelectual property rights and ownership, be managed? What legislation is applicable?",
        "How and when will data be shared? Are there possible restrictions to data sharing or embargo reasons?",
        "How will data for preservation be selected, and where will data be preserved long-term (for example a data repository or archive)?",
        "What methods or software tools will be needed to access and use the data?",
        "How will the application of a unique and persistent identifier (such us a Digital Object Identifier (DOI)) to each data set be ensured?",
        "Who (for example role, position, and institution) will be responsible for data management (i.e the data steward)?",
        "What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?"
    ]
    
    total_expected = len(expected_subsections)
    pdf_files = [f for f in os.listdir(samples_dir) if f.endswith('.pdf')]
    
    print("SIMPLE COVERAGE ANALYSIS")
    print("=" * 50)
    print(f"Expected subsections: {total_expected}")
    print()
    
    results = {}
    
    for pdf_file in pdf_files:
        print(f"File: {pdf_file}")
        file_path = os.path.join(samples_dir, pdf_file)
        
        try:
            result = extractor.process_file(file_path, "outputs")
            
            if result.get('success'):
                found_count = 0
                missing_list = []
                
                # Count found subsections using hierarchical extraction
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    raw_text = ""
                    for page in pdf_reader.pages:
                        raw_text += page.extract_text() + "\\n"
                
                # Look for DMP section
                start_pos = -1
                for start_mark in extractor.start_marks:
                    pos = raw_text.find(start_mark)
                    if pos != -1:
                        start_pos = pos
                        break
                
                if start_pos != -1:
                    end_pos = len(raw_text)
                    for end_mark in extractor.end_marks:
                        pos = raw_text.find(end_mark, start_pos)
                        if pos != -1:
                            end_pos = pos
                            break
                    
                    dmp_text = raw_text[start_pos:end_pos]
                    lines = [line.strip() for line in dmp_text.split('\\n') if line.strip()]
                    hierarchical_result = extractor.extract_hierarchical_content(lines, is_pdf=True)
                    
                    for subsection_name in expected_subsections:
                        found = False
                        for section in hierarchical_result['sections']:
                            section_data = hierarchical_result['sections'][section]
                            if subsection_name in section_data and section_data[subsection_name].get('found', False):
                                found = True
                                break
                        
                        if found:
                            found_count += 1
                        else:
                            # Get short name (first few words)
                            short_name = ' '.join(subsection_name.split()[:4]) + "..."
                            missing_list.append(short_name)
                
                coverage_percent = (found_count / total_expected) * 100
                print(f"  Found: {found_count}/{total_expected} ({coverage_percent:.1f}%)")
                
                if missing_list:
                    print(f"  Missing: {len(missing_list)} subsections")
                    if len(missing_list) <= 5:  # Show all if 5 or fewer
                        for missing in missing_list:
                            print(f"    - {missing}")
                    else:  # Show first 3
                        for missing in missing_list[:3]:
                            print(f"    - {missing}")
                        print(f"    ... and {len(missing_list)-3} more")
                
                results[pdf_file] = {'found': found_count, 'total': total_expected, 'coverage': coverage_percent}
            
            else:
                print(f"  ERROR: Failed to process")
                results[pdf_file] = {'found': 0, 'total': total_expected, 'coverage': 0.0}
        
        except Exception as e:
            print(f"  EXCEPTION: {str(e)[:50]}...")
            results[pdf_file] = {'found': 0, 'total': total_expected, 'coverage': 0.0}
        
        print()
    
    # Summary
    print("SUMMARY")
    print("=" * 50)
    total_found = sum(r['found'] for r in results.values())
    total_possible = len(results) * total_expected
    overall_coverage = (total_found / total_possible) * 100 if total_possible > 0 else 0
    
    print(f"Overall coverage: {total_found}/{total_possible} ({overall_coverage:.1f}%)")
    print(f"Average per file: {total_found/len(results):.1f} subsections")
    
    best_file = max(results.keys(), key=lambda x: results[x]['found'])
    worst_file = min(results.keys(), key=lambda x: results[x]['found'])
    
    print(f"Best performance: {best_file} ({results[best_file]['found']}/{total_expected})")
    print(f"Worst performance: {worst_file} ({results[worst_file]['found']}/{total_expected})")

if __name__ == "__main__":
    simple_coverage_analysis()