# utils/extractor.py
import os
import re
from docx import Document
from datetime import datetime
import PyPDF2

class DMPExtractor:
    def __init__(self):
        # Define start and end markers for extraction
        self.start_marks = [
            "DATA MANAGEMENT PLAN [in English]",
            "PLAN ZARZĄDZANIA DANYMI"
        ]
        self.end_marks = [
            "ADMINISTRATIVE DECLARATIONS",
            "OŚWIADCZENIA ADMINISTRACYJNE"
        ]
        
        # Define the structure of DMP sections and questions
        self.dmp_structure = {
            "1. Data description and collection or re-use of existing data": [
                "How will new data be collected or produced and/or how will existing data be re-used?",
                "What data (for example the types, formats, and volumes) will be collected or produced?"
            ],
            "2. Documentation and data quality": [
                "What metadata and documentation (for example methodology or data collection and way of organising data) will accompany data?",
                "What data quality control measures will be used?"
            ],
            "3. Storage and backup during the research process": [
                "How will data and metadata be stored and backed up during the research process?",
                "How will data security and protection of sensitive data be taken care of during the research?"
            ],
            "4. Legal requirements, codes of conduct": [
                "If personal data are processed, how will compliance with legislation on personal data and on data security be ensured?",
                "How will other legal issues, such as intelectual property rights and ownership, be managed? What legislation is applicable?"
            ],
            "5. Data sharing and long-term preservation": [
                "How and when will data be shared? Are there possible restrictions to data sharing or embargo reasons?",
                "How will data for preservation be selected, and where will data be preserved long-term (for example a data repository or archive)?",
                "What methods or software tools will be needed to access and use the data?",
                "How will the application of a unique and persistent identifier (such us a Digital Object Identifier (DOI)) to each data set be ensured?"
            ],
            "6. Data management responsibilities and resources": [
                "Who (for example role, position, and institution) will be responsible for data mangement (i.e the data steward)?",
                "What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?"
            ]
        }
    
    def should_skip_text(self, text):
        """Determine if text should be skipped (headers, footers, etc.)"""
        skip_patterns = [
            r"Strona \d+",        # Polish page numbers
            r"Page \d+",          # English page numbers
            r"ID: \d+",           # Document ID
            r"\[wydruk roboczy\]", # Draft print marker
            r"WZÓR",              # Template marker
            r"W Z Ó R",           # Template marker with spaces
            r"OSF,",              # Document footer
            r"^\d+$"              # Just page numbers
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) is not None for pattern in skip_patterns)
    
    def extract_author_name(self, text):
        """Extract author name from the document text"""
        # Common patterns for author name in grant applications
        patterns = [
            r"dr\s+(?:inż\.|hab\.)?\s+([\w\s-]+)",  # Polish academic titles
            r"Principal\s+Investigator[:\s]+([\w\s-]+)",  # English PI designation
            r"Kierownik\s+projektu[:\s]+([\w\s-]+)"  # Polish PI designation
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def process_pdf(self, pdf_path, output_dir):
        """Process a PDF and extract DMP content"""
        try:
            print(f"Processing PDF: {pdf_path}")
            # Create a new Word document
            doc = Document()
            
            # Read the PDF
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract first few pages text for author detection
                first_pages_text = ""
                for i in range(min(3, len(reader.pages))):
                    first_pages_text += reader.pages[i].extract_text() + "\n"
                
                author_name = self.extract_author_name(first_pages_text)
                print(f"Author detected: {author_name}")
                
                # Find the DMP section
                all_text = ""
                all_pages_text = []
                
                # Extract text from all pages
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    all_pages_text.append(page_text)
                    all_text += page_text + "\n\n"
                    
                    # Print info about start/end marks found
                    for mark in self.start_marks:
                        if mark in page_text:
                            print(f"Found start mark '{mark}' on page {i+1}")
                    
                    for mark in self.end_marks:
                        if mark in page_text:
                            print(f"Found end mark '{mark}' on page {i+1}")
                
                # Find start and end positions
                start_pos = -1
                end_pos = len(all_text)
                
                for mark in self.start_marks:
                    pos = all_text.find(mark)
                    if pos != -1:
                        start_pos = pos + len(mark)
                        print(f"Found start mark at position {pos}")
                        break
                
                if start_pos == -1:
                    return {
                        "success": False,
                        "message": "Could not find the start marker in the document."
                    }
                
                for mark in self.end_marks:
                    pos = all_text.find(mark, start_pos)
                    if pos != -1 and pos < end_pos:
                        end_pos = pos
                        print(f"Found end mark at position {pos}")
                
                # Extract DMP content
                dmp_text = all_text[start_pos:end_pos]
                print(f"Extracted {len(dmp_text)} characters of DMP content")
                
                # Create document
                doc.add_heading("DATA MANAGEMENT PLAN", level=0)
                
                # Process the content by section
                section_content = {}
                for section in self.dmp_structure:
                    section_content[section] = {}
                    for subsection in self.dmp_structure[section]:
                        section_content[section][subsection] = []
                
                # Split the content into lines for processing
                lines = dmp_text.split("\n")
                current_section = None
                current_subsection = None
                
                # Simple processing to find sections and subsections
                for line in lines:
                    line = line.strip()
                    if not line or self.should_skip_text(line):
                        continue
                    
                    # Check if line contains a section number (e.g. "1.")
                    section_match = re.match(r'^\s*(\d+)\.', line)
                    if section_match:
                        section_num = section_match.group(1)
                        for section in self.dmp_structure:
                            if section.startswith(f"{section_num}."):
                                current_section = section
                                current_subsection = None
                                print(f"Found section: {current_section}")
                                break
                        continue
                        
                    # If we have a current section, check for subsection
                    if current_section:
                        for subsection in self.dmp_structure[current_section]:
                            # Check for key words from subsection
                            key_words = subsection.split()[:3]
                            if any(word in line for word in key_words):
                                current_subsection = subsection
                                print(f"Found subsection: {current_subsection[:20]}...")
                                break
                        
                        # Add content to appropriate subsection
                        if current_subsection and len(line) > 10:  # Avoid short lines
                            section_content[current_section][current_subsection].append(line)
                
                # Add content to document
                for section in self.dmp_structure:
                    doc.add_heading(section, level=1)
                    
                    for subsection in self.dmp_structure[section]:
                        doc.add_heading(subsection, level=2)
                        
                        content = section_content[section][subsection]
                        if content:
                            for text in content:
                                doc.add_paragraph(text)
                        else:
                            # Add blank paragraph for empty content
                            doc.add_paragraph("")
                
                # Generate output filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                
                if author_name:
                    # Clean author name to use in filename
                    clean_author = re.sub(r'[^a-zA-Z0-9]', '_', author_name.strip())
                    output_filename = f"DMP_{clean_author}_{timestamp}.docx"
                else:
                    output_filename = f"DMP_{base_name}_{timestamp}.docx"
                
                # Create safe filename
                output_filename = re.sub(r'[\\/*?:"<>|]', "_", output_filename)
                
                # Save the document
                output_path = os.path.join(output_dir, output_filename)
                doc.save(output_path)
                
                return {
                    "success": True,
                    "filename": output_filename,
                    "path": output_path,
                    "message": "DMP successfully extracted"
                }
                
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Error processing PDF: {str(e)}")
            print(traceback_str)
            return {
                "success": False,
                "message": f"Error processing PDF: {str(e)}"
            }