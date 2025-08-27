#!/usr/bin/env python3
import sys
import os
import re
import PyPDF2

# Add the utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from extractor import DMPExtractor

def debug_boundaries():
    """Debug the boundary detection and content assignment"""
    pdf_path = r"C:\Users\kraje\OneDrive\Pulpit\pzd\test\wydruk1733736559184.pdf"
    
    print("=== DEBUGGING BOUNDARY DETECTION ===")
    print(f"PDF: {pdf_path}\n")
    
    # Initialize extractor
    extractor = DMPExtractor()
    
    # Extract and process PDF content like the extractor does
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
    
    if start_pos != -1 and end_pos != -1:
        dmp_content = all_text[start_pos:end_pos]
        print(f"Found DMP content: {len(dmp_content)} characters")
    else:
        print("Could not find DMP boundaries")
        return
    
    # Process like the extractor does
    lines = dmp_content.split('\n')
    processed_lines = []
    for line in lines:
        line = line.strip()
        if line and not extractor.should_skip_text(line, is_pdf=True):
            processed_lines.append(line)
    
    print(f"After filtering: {len(processed_lines)} lines")
    
    # Find boundaries like the extractor does
    boundaries = []
    for i, line in enumerate(processed_lines):
        # Check for subsection questions
        for question_key, question_text in extractor.section_ids.items():
            if extractor._text_similarity(line, question_text) > 0.7:
                boundaries.append({
                    'index': i,
                    'line': line,
                    'question': question_text,
                    'question_key': question_key
                })
                print(f"Boundary {len(boundaries)-1}: Index {i} -> {question_key}: {line[:80]}...")
    
    print(f"\nFound {len(boundaries)} boundaries")
    
    # Look for content around boundary 44 (section 6.1)
    target_text = "Open Science Competence Centre"
    print(f"\n=== LOOKING FOR '{target_text}' ===")
    
    for i, line in enumerate(processed_lines):
        if target_text.lower() in line.lower():
            print(f"Found at index {i}: {line}")
            
            # Show which boundary this falls between
            prev_boundary = None
            next_boundary = None
            
            for b in boundaries:
                if b['index'] <= i:
                    prev_boundary = b
                elif b['index'] > i and next_boundary is None:
                    next_boundary = b
                    break
            
            print(f"  Previous boundary: {prev_boundary['question_key'] if prev_boundary else 'None'}")
            print(f"  Next boundary: {next_boundary['question_key'] if next_boundary else 'None'}")
            
            # Show context
            start_ctx = max(0, i-3)
            end_ctx = min(len(processed_lines), i+4)
            print(f"  Context (lines {start_ctx}-{end_ctx}):")
            for j in range(start_ctx, end_ctx):
                marker = " >>> " if j == i else "     "
                print(f"{marker}{j}: {processed_lines[j]}")

if __name__ == "__main__":
    debug_boundaries()