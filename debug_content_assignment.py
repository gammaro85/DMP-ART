#!/usr/bin/env python3
import sys
import os

# Add the utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from extractor import DMPExtractor

class DebugExtractor(DMPExtractor):
    """Extended extractor with debug output"""
    
    def _extract_content_by_boundaries(self, content_list, boundaries, is_pdf=False):
        """Debug version of content extraction"""
        print(f"\n=== DEBUG CONTENT ASSIGNMENT ===")
        print(f"Total content items: {len(content_list)}")
        print(f"Total boundaries: {len(boundaries)}")
        
        # Show all content items
        print(f"\n=== ALL CONTENT ITEMS ===")
        for i, item in enumerate(content_list):
            item_text = item.get('text', str(item))[:80] if isinstance(item, dict) else str(item)[:80]
            print(f"{i:2}: {item_text}")
        
        # Show all boundaries  
        print(f"\n=== ALL BOUNDARIES ===")
        for i, boundary in enumerate(boundaries):
            print(f"Boundary {i}: Index {boundary['index']}, Type: {boundary['type']}")
            print(f"  Title: {boundary['title'][:80]}")
            print(f"  Parent: {boundary.get('parent_section', 'None')}")
        
        # Process each boundary and show what content would be assigned
        print(f"\n=== CONTENT ASSIGNMENT SIMULATION ===")
        target_text = "Open Science Competence Centre"
        
        for i, boundary in enumerate(boundaries):
            start_index = boundary['index'] + 1  # Start after the boundary title
            
            # Find end index (next boundary or end of content)
            end_index = len(content_list)
            if i + 1 < len(boundaries):
                end_index = boundaries[i + 1]['index']
            
            # Extract content between boundaries
            section_content = content_list[start_index:end_index]
            
            print(f"\nBoundary {i} ({boundary.get('question_key', 'Unknown')}):")
            print(f"  Range: {start_index} to {end_index}")
            print(f"  Content items: {len(section_content)}")
            
            # Check if target text is in this section
            contains_target = False
            for item in section_content:
                item_text = item.get('text', str(item)) if isinstance(item, dict) else str(item)
                if target_text.lower() in item_text.lower():
                    contains_target = True
                    print(f"  >>> CONTAINS TARGET: {item_text[:100]}")
            
            if not contains_target and len(section_content) > 0:
                print(f"  First item: {(section_content[0].get('text', str(section_content[0])) if isinstance(section_content[0], dict) else str(section_content[0]))[:60]}")
                if len(section_content) > 1:
                    print(f"  Last item: {(section_content[-1].get('text', str(section_content[-1])) if isinstance(section_content[-1], dict) else str(section_content[-1]))[:60]}")
        
        # Continue with original extraction
        return super()._extract_content_by_boundaries(content_list, boundaries, is_pdf)

def debug_content_assignment():
    """Debug the content assignment process"""
    pdf_path = r"C:\Users\kraje\OneDrive\Pulpit\pzd\test\wydruk1733736559184.pdf"
    
    print("=== DEBUGGING CONTENT ASSIGNMENT ===")
    print(f"PDF: {pdf_path}\n")
    
    # Initialize debug extractor
    extractor = DebugExtractor()
    
    # Run the extraction process (this will trigger our debug output)
    result = extractor.process_file(pdf_path, "outputs")
    
    print(f"\n=== FINAL RESULT ===")
    print(f"Success: {result.get('success', 'Unknown')}")
    print(f"Cache file: {result.get('cache_file', 'Unknown')}")

if __name__ == "__main__":
    debug_content_assignment()