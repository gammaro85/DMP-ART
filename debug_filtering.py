#!/usr/bin/env python3
import sys
import os
import PyPDF2

# Add the utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from extractor import DMPExtractor

def debug_filtering():
    """Debug the filtering steps that lose the target content"""
    pdf_path = r"C:\Users\kraje\OneDrive\Pulpit\pzd\test\wydruk1733736559184.pdf"
    target_text = "Open Science Competence Centre"
    
    print("=== DEBUGGING CONTENT FILTERING ===")
    print(f"PDF: {pdf_path}")
    print(f"Target: {target_text}\n")
    
    # Initialize extractor
    extractor = DMPExtractor()
    
    # Extract DMP content like the extractor does
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return
    
    # Find DMP section
    start_pattern = "PLAN ZARZĄDZANIA DANYMI"
    end_pattern = "OŚWIADCZENIA ADMINISTRACYJNE"
    
    start_pos = all_text.find(start_pattern)
    end_pos = all_text.find(end_pattern, start_pos)
    
    if start_pos == -1 or end_pos == -1:
        print("Could not find DMP boundaries")
        return
    
    dmp_text = all_text[start_pos:end_pos]
    
    # Step 1: Split into lines
    lines = dmp_text.split("\n")
    print(f"Step 1 - Split into lines: {len(lines)} lines")
    
    target_in_lines = [i for i, line in enumerate(lines) if target_text.lower() in line.lower()]
    if target_in_lines:
        print(f"  Target found in lines: {target_in_lines}")
        for line_idx in target_in_lines[:3]:  # Show first 3 occurrences
            print(f"    Line {line_idx}: {lines[line_idx].strip()}")
    else:
        print(f"  Target NOT found in lines")
    
    # Step 2: extract_pdf_table_content
    structured_content = extractor.extract_pdf_table_content(lines)
    print(f"\nStep 2 - extract_pdf_table_content: {len(structured_content)} items")
    
    target_in_structured = [i for i, item in enumerate(structured_content) if target_text.lower() in item.lower()]
    if target_in_structured:
        print(f"  Target found in structured content: {target_in_structured}")
        for item_idx in target_in_structured[:3]:
            print(f"    Item {item_idx}: {structured_content[item_idx][:100]}")
    else:
        print(f"  Target NOT found in structured content")
    
    # Step 3: _filter_pdf_content_quality
    filtered_content = extractor._filter_pdf_content_quality(structured_content)
    print(f"\nStep 3 - _filter_pdf_content_quality: {len(filtered_content)} items")
    
    target_in_filtered = [i for i, item in enumerate(filtered_content) if target_text.lower() in item.lower()]
    if target_in_filtered:
        print(f"  Target found in filtered content: {target_in_filtered}")
        for item_idx in target_in_filtered[:3]:
            print(f"    Item {item_idx}: {filtered_content[item_idx][:100]}")
    else:
        print(f"  Target NOT found in filtered content")
    
    # Additional debug: Show items around where target should be
    print(f"\n=== CONTENT AROUND TARGET AREA ===")
    print("Looking for Polish section 6 questions...")
    
    for phase_name, content_list in [
        ("Lines", lines),
        ("Structured", structured_content), 
        ("Filtered", filtered_content)
    ]:
        print(f"\n{phase_name} content around section 6:")
        section6_indicators = ["zarządzaniem danymi", "data steward", "Zadania związane"]
        
        for i, item in enumerate(content_list):
            item_text = item.strip() if isinstance(item, str) else str(item).strip()
            if any(indicator.lower() in item_text.lower() for indicator in section6_indicators):
                # Show context around this item
                start_ctx = max(0, i-2)
                end_ctx = min(len(content_list), i+4)
                print(f"  Found section 6 indicator at index {i}:")
                for j in range(start_ctx, end_ctx):
                    marker = " >>> " if j == i else "     "
                    ctx_text = content_list[j].strip() if isinstance(content_list[j], str) else str(content_list[j]).strip()
                    print(f"{marker}{j}: {ctx_text[:80]}")
                print()

if __name__ == "__main__":
    debug_filtering()