#!/usr/bin/env python3
import sys
import os
import re
import PyPDF2

# Add the utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from extractor import DMPExtractor

def debug_section_61():
    """Debug why section 6.1 content is not being extracted"""
    pdf_path = r"C:\Users\kraje\OneDrive\Pulpit\pzd\test\wydruk1733736559184.pdf"
    
    print("=== DEBUGGING SECTION 6.1 EXTRACTION ===")
    print(f"PDF: {pdf_path}\n")
    
    # Initialize extractor
    extractor = DMPExtractor()
    
    # Extract raw PDF text using PyPDF2
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            raw_text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                raw_text += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return
    
    # Look for the expected 6.1 content in raw text
    target_content = "Open Science Competence Centre"
    print(f"=== SEARCHING FOR TARGET CONTENT: '{target_content}' ===")
    
    lines = raw_text.split('\n')
    found_lines = []
    for i, line in enumerate(lines):
        if target_content.lower() in line.lower():
            # Show context around the found line
            start_idx = max(0, i - 3)
            end_idx = min(len(lines), i + 4)
            print(f"\nFOUND at line {i}:")
            for j in range(start_idx, end_idx):
                marker = " >>> " if j == i else "     "
                print(f"{marker}{j}: {lines[j]}")
            found_lines.append((i, line))
    
    print(f"\nTotal occurrences found: {len(found_lines)}")
    
    # Now test the filtering
    print("\n=== TESTING SKIP PATTERNS ===")
    for line_num, line in found_lines:
        should_skip = extractor.should_skip_text(line, is_pdf=True)
        print(f"Line {line_num}: '{line.strip()}'")
        print(f"Should skip: {should_skip}")
        
        if should_skip:
            # Find which pattern matched
            print("Testing individual patterns:")
            
            # Test project ID pattern specifically
            if re.search(r'\d{6,}', line):
                print(f"  - Matches project ID pattern: {re.findall(r'\d{6,}', line)}")
            
            # Test the _is_grant_header_footer method
            is_header = extractor._is_grant_header_footer(line)
            print(f"  - Grant header/footer: {is_header}")
        print()
    
    # Test with longer context (potential multi-line content)
    print("\n=== TESTING MULTI-LINE CONTEXT ===")
    for line_num, line in found_lines:
        # Get surrounding context
        start_idx = max(0, line_num - 2)
        end_idx = min(len(lines), line_num + 3)
        context_lines = lines[start_idx:end_idx]
        multi_line_text = '\n'.join(context_lines)
        
        print(f"Multi-line context around line {line_num}:")
        print(f"'{multi_line_text}'")
        should_skip = extractor.should_skip_text(multi_line_text, is_pdf=True)
        print(f"Should skip multi-line: {should_skip}\n")

if __name__ == "__main__":
    debug_section_61()