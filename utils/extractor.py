# utils/extractor.py
import os
import re
import json
import uuid
from docx import Document
from datetime import datetime
import PyPDF2

class DMPExtractor:
    def __init__(self):
        # Define paths to configuration files
        config_dir = 'config'
        key_phrases_file = os.path.join(config_dir, 'key_phrases.json')
        dmp_structure_file = os.path.join(config_dir, 'dmp_structure.json')
        
        # Define default configurations
        default_dmp_structure = {
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
                "Who (for example role, position, and institution) will be responsible for data management (i.e the data steward)?",
                "What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?"
            ]
        }
        
        default_key_phrases = {
            "methodology": ["methodology", "approach", "procedure", "process", "technique"],
            "data_format": ["format", "file type", "structure", "schema", "encoding"],
            "data_volume": ["volume", "size", "amount", "quantity", "gigabyte", "terabyte"],
            "metadata": ["metadata", "documentation", "description", "annotation"],
            "quality": ["quality", "validation", "verification", "accuracy", "precision"],
            "storage": ["storage", "repository", "database", "server", "cloud"],
            "backup": ["backup", "copy", "replicate", "redundancy"],
            "security": ["security", "protection", "encryption", "access control"],
            "personal_data": ["personal data", "privacy", "consent", "gdpr", "anonymization"],
            "license": ["license", "copyright", "intellectual property", "ownership", "rights"],
            "sharing": ["sharing", "distribution", "dissemination", "access", "availability"],
            "preservation": ["preservation", "archiving", "long-term", "curation"],
            "tools": ["software", "tools", "application", "program", "code"],
            "identifier": ["identifier", "doi", "persistent", "uuid", "orcid"],
            "responsibility": ["responsible", "manager", "steward", "oversight", "supervision"],
            "resources": ["resources", "budget", "funding", "cost", "allocation"]
        }
        
        # Load or use default configurations
        self.dmp_structure = self._load_config(dmp_structure_file, default_dmp_structure)
        self.key_phrases = self._load_config(key_phrases_file, default_key_phrases)
        
        # Generate section_ids mapping
        self.section_ids = self._generate_section_ids()
        
        # Define start and end markers for extraction
        self.start_marks = [
            "DATA MANAGEMENT PLAN [in English]",
            "PLAN ZARZĄDZANIA DANYMI"
        ]
        self.end_marks = [
            "ADMINISTRATIVE DECLARATIONS",
            "OŚWIADCZENIA ADMINISTRACYJNE"
        ]
    
    def _load_config(self, file_path, default_value):
        """Load configuration from file or use default if file doesn't exist"""
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
                return default_value
        else:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save default value to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_value, f, ensure_ascii=False, indent=2)
            
            return default_value
    
    def _generate_section_ids(self):
        """Generate section_ids mapping from dmp_structure"""
        section_ids = {}
        section_num = 1
        
        for section, questions in self.dmp_structure.items():
            for i, question in enumerate(questions, 1):
                section_id = f"{section_num}.{i}"
                section_ids[section_id] = question
            
            section_num += 1
        
        return section_ids
    
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
    
    def identify_key_phrases(self, text):
        """Identify key phrases in a paragraph and return relevant tags"""
        text_lower = text.lower()
        found_tags = []
        
        for tag, phrases in self.key_phrases.items():
            for phrase in phrases:
                if phrase in text_lower:
                    found_tags.append(tag)
                    break
        
        return found_tags
    
    def process_paragraph(self, paragraph):
        """Process a paragraph to extract key information"""
        tags = self.identify_key_phrases(paragraph)
        
        # Find lead sentence (first sentence or sentence with most key phrases)
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        if not sentences:
            return {
                "text": paragraph,
                "tags": tags,
                "title": None
            }
        
        # Use first sentence as title if it's reasonably short
        title = sentences[0] if len(sentences[0]) < 100 else None
        
        return {
            "text": paragraph,
            "tags": tags,
            "title": title
        }
    
    def map_section_to_id(self, section, subsection):
        """Map a section and subsection to a section ID"""
        # Try to find the matching ID
        for section_id, question in self.section_ids.items():
            if question == subsection:
                return section_id
        
        # Fallback: try to infer from section number
        section_num = re.match(r'(\d+)\.', section)
        if section_num:
            num = section_num.group(1)
            for section_id in self.section_ids.keys():
                if section_id.startswith(f"{num}."):
                    return section_id
        
        # If no match found, return a generated ID
        return f"section_{hash(section + subsection) % 10000}"
    
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
                tagged_content = {}
                
                for section in self.dmp_structure:
                    section_content[section] = {}
                    tagged_content[section] = {}
                    for subsection in self.dmp_structure[section]:
                        section_content[section][subsection] = []
                        tagged_content[section][subsection] = []
                
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
                        best_match = None
                        max_words = 0
                        
                        for subsection in self.dmp_structure[current_section]:
                            # Get important words from subsection and line
                            subsection_words = set(word.lower() for word in subsection.split() if len(word) > 3)
                            line_words = set(word.lower() for word in line.split() if len(word) > 3)
                            
                            # Count matching words
                            matching_words = len(subsection_words.intersection(line_words))
                            
                            # If we have a good match (at least 2 matching words or 30% of subsection words)
                            if matching_words >= 2 or (subsection_words and matching_words / len(subsection_words) >= 0.3):
                                if matching_words > max_words:
                                    max_words = matching_words
                                    best_match = subsection
                        
                        if best_match:
                            current_subsection = best_match
                            print(f"Found subsection: {current_subsection[:20]}...")
                        
                        # Add content to appropriate subsection
                        if current_subsection and len(line) > 10:  # Avoid short lines
                            try:
                                section_content[current_section][current_subsection].append(line)
                                
                                # Process and tag paragraph
                                processed = self.process_paragraph(line)
                                tagged_content[current_section][current_subsection].append(processed)
                            except KeyError as e:
                                print(f"Warning: KeyError when adding content to {current_section} - {current_subsection}: {str(e)}")
                                # Create missing subsection if needed
                                if current_subsection not in section_content[current_section]:
                                    section_content[current_section][current_subsection] = [line]
                                    tagged_content[current_section][current_subsection] = [self.process_paragraph(line)]
                                    print(f"Created missing subsection: {current_subsection}")
                
                # Add content to document
                for section in self.dmp_structure:
                    doc.add_heading(section, level=1)
                    
                    for subsection in self.dmp_structure[section]:
                        doc.add_heading(subsection, level=2)
                        
                        # Safely get content from the section/subsection
                        content = []
                        try:
                            content = section_content[section][subsection]
                        except KeyError:
                            print(f"Warning: Missing content for {section} - {subsection}")
                        
                        if content:
                            for text in content:
                                doc.add_paragraph(text)
                        else:
                            # Add blank paragraph for empty content
                            doc.add_paragraph("")
                
                # Create a structured representation for the review interface
                review_structure = {}
                
                for section in self.dmp_structure:
                    for subsection in self.dmp_structure[section]:
                        section_id = self.map_section_to_id(section, subsection)
                        
                        # Safely get paragraphs and tagged paragraphs
                        paragraphs = []
                        tagged_paragraphs = []
                        
                        try:
                            paragraphs = section_content[section][subsection]
                        except KeyError:
                            print(f"Warning: Missing paragraphs for {section} - {subsection}")
                        
                        try:
                            tagged_paragraphs = tagged_content[section][subsection]
                        except KeyError:
                            print(f"Warning: Missing tagged paragraphs for {section} - {subsection}")
                        
                        # Add to review structure
                        review_structure[section_id] = {
                            "section": section,
                            "question": subsection,
                            "paragraphs": paragraphs,
                            "tagged_paragraphs": tagged_paragraphs
                        }
                
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
                
                # Save review structure as JSON for the review interface
                cache_id = str(uuid.uuid4())
                cache_filename = f"cache_{cache_id}.json"
                cache_path = os.path.join(output_dir, cache_filename)
                
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(review_structure, f, ensure_ascii=False, indent=2)
                
                return {
                    "success": True,
                    "filename": output_filename,
                    "path": output_path,
                    "cache_id": cache_id,
                    "cache_file": cache_filename,
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
    
    def get_section_ids(self):
        """Return mapping of section IDs to questions"""
        return self.section_ids
    
    def get_key_phrases(self):
        """Return key phrases used for tagging"""
        return self.key_phrases