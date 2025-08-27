#!/usr/bin/env python3
import sys
import os

# Add the utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from extractor import DMPExtractor

class DetailedDebugExtractor(DMPExtractor):
    """Extractor with detailed line-by-line debug output"""
    
    def extract_pdf_table_content(self, text_lines):
        """Debug version that traces every line"""
        target_text = "Open Science Competence Centre"
        
        print(f"\n=== DETAILED LINE PROCESSING DEBUG ===")
        print(f"Processing {len(text_lines)} input lines")
        
        # Preprocess lines to improve extraction quality
        preprocessed_lines = self._preprocess_pdf_lines(text_lines)
        print(f"After preprocessing: {len(preprocessed_lines)} lines")
        
        # Find target line in preprocessed
        target_lines = []
        for i, line in enumerate(preprocessed_lines):
            if target_text.lower() in line.lower():
                target_lines.append(i)
                print(f"Target found in preprocessed line {i}: {line}")
        
        table_content = []
        current_table = []
        in_table = False
        line_buffer = []  # Buffer to handle multi-line content
        
        for i, line in enumerate(preprocessed_lines):
            line = line.strip()
            
            # Debug target line processing
            is_target_line = i in target_lines
            if is_target_line:
                print(f"\n>>> PROCESSING TARGET LINE {i}: '{line}'")
            
            if not line:
                # Handle empty lines - they might separate content blocks
                if in_table and current_table:
                    # End of table, process it
                    processed_table = self._process_table_rows(current_table)
                    table_content.extend(processed_table)
                    current_table = []
                    in_table = False
                
                # Flush line buffer
                if line_buffer:
                    combined_line = ' '.join(line_buffer).strip()
                    if is_target_line:
                        print(f"  Empty line - flushing buffer with {len(line_buffer)} items")
                        print(f"  Combined: '{combined_line}'")
                        print(f"  Skip test: {self.should_skip_text(combined_line, is_pdf=True)}")
                    
                    if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                        table_content.append(combined_line)
                    line_buffer = []
                continue
            
            # Enhanced table pattern detection
            is_table_line = self._is_table_line(line)
            is_form_field = self._is_form_field(line)
            is_continuation_line = self._is_continuation_line(line, preprocessed_lines, i)
            
            if is_target_line:
                print(f"  is_table_line: {is_table_line}")
                print(f"  is_form_field: {is_form_field}")
                print(f"  is_continuation_line: {is_continuation_line}")
                print(f"  should_skip_text: {self.should_skip_text(line, is_pdf=True)}")
                print(f"  _should_buffer_line: {self._should_buffer_line(line) if not self.should_skip_text(line, is_pdf=True) else 'N/A'}")
            
            if is_table_line:
                if not in_table:
                    in_table = True
                    # Flush any buffered content first
                    if line_buffer:
                        combined_line = ' '.join(line_buffer).strip()
                        if is_target_line:
                            print(f"  Table start - flushing buffer")
                        if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                            table_content.append(combined_line)
                        line_buffer = []
                
                current_table.append(line)
                if is_target_line:
                    print(f"  Added to current_table")
                    
            elif is_form_field:
                # Form fields are treated as special content
                if in_table and current_table:
                    processed_table = self._process_table_rows(current_table)
                    table_content.extend(processed_table)
                    current_table = []
                    in_table = False
                
                # Process form field
                processed_field = self._process_form_field(line)
                if processed_field and not self.should_skip_text(processed_field, is_pdf=True):
                    table_content.append(processed_field)
                if is_target_line:
                    print(f"  Processed as form field: '{processed_field}'")
                    
            elif is_continuation_line and line_buffer:
                # This line continues previous content
                line_buffer.append(line)
                if is_target_line:
                    print(f"  Added to line_buffer (continuation), buffer now has {len(line_buffer)} items")
                    
            else:
                if in_table and current_table:
                    # Process completed table
                    processed_table = self._process_table_rows(current_table)
                    table_content.extend(processed_table)
                    current_table = []
                    in_table = False
                
                # Flush any buffered content
                if line_buffer:
                    combined_line = ' '.join(line_buffer).strip()
                    if is_target_line:
                        print(f"  Flushing buffer before processing current line")
                    if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                        table_content.append(combined_line)
                    line_buffer = []
                
                # Add current line to buffer or directly
                if not self.should_skip_text(line, is_pdf=True):
                    if self._should_buffer_line(line):
                        # Test if adding this line to buffer would create a combination that gets filtered
                        test_combination = ' '.join(line_buffer + [line]).strip()
                        if not self.should_skip_text(test_combination, is_pdf=True):
                            line_buffer.append(line)
                            if is_target_line:
                                print(f"  Added to line_buffer, buffer now has {len(line_buffer)} items")
                        else:
                            # This line would contaminate the buffer, flush buffer first and add line separately
                            if line_buffer:
                                combined_line = ' '.join(line_buffer).strip()
                                if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                                    table_content.append(combined_line)
                                line_buffer = []
                            # Add current line directly since it passed individual skip test
                            table_content.append(line)
                            if is_target_line:
                                print(f"  Added directly to table_content (would contaminate buffer)")
                    else:
                        table_content.append(line)
                        if is_target_line:
                            print(f"  Added directly to table_content (no buffering needed)")
                else:
                    if is_target_line:
                        print(f"  SKIPPED due to should_skip_text check!")
        
        # Process any remaining table
        if current_table:
            processed_table = self._process_table_rows(current_table)
            table_content.extend(processed_table)
        
        # Handle remaining buffered content
        if line_buffer:
            combined_line = ' '.join(line_buffer).strip()
            target_in_buffer = any(target_text.lower() in item.lower() for item in line_buffer)
            if target_in_buffer:
                print(f"\nFinal buffer flush contains target:")
                print(f"  Buffer items: {line_buffer}")
                print(f"  Combined: '{combined_line}'")
                print(f"  Skip test: {self.should_skip_text(combined_line, is_pdf=True)}")
            
            if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                table_content.append(combined_line)
        
        # Check final result
        target_in_result = [i for i, item in enumerate(table_content) if target_text.lower() in item.lower()]
        print(f"\nFinal result: {len(table_content)} items")
        if target_in_result:
            print(f"Target found in final result at indices: {target_in_result}")
            for idx in target_in_result:
                print(f"  {idx}: {table_content[idx][:100]}")
        else:
            print("Target NOT found in final result")
        
        return self._post_process_content(table_content)

def debug_line_processing():
    """Debug the line-by-line processing"""
    pdf_path = r"C:\Users\kraje\OneDrive\Pulpit\pzd\test\wydruk1733736559184.pdf"
    
    print("=== DEBUGGING LINE PROCESSING ===")
    print(f"PDF: {pdf_path}\n")
    
    # Initialize debug extractor
    extractor = DetailedDebugExtractor()
    
    # Extract DMP content manually to test just the table extraction
    import PyPDF2
    
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
    lines = dmp_text.split("\n")
    
    # Run the debug version
    result = extractor.extract_pdf_table_content(lines)

if __name__ == "__main__":
    debug_line_processing()