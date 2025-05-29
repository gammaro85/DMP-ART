# utils/extractor.py - Enhanced version with improved DOCX processing
import os
import re
import json
import uuid
import zipfile
from docx import Document
from datetime import datetime
import PyPDF2

class DMPExtractor:
    def __init__(self):
        # Define start and end markers for extraction
        self.start_marks = [
            "DATA MANAGEMENT PLAN",
            "DATA MANAGEMENT PLAN [in English]",
            "PLAN ZARZĄDZANIA DANYMI",
            "MINIATURA 9 -- PLAN ZARZĄDZANIA DANYMI"
        ]
        self.end_marks = [
            "ADMINISTRATIVE DECLARATIONS",
            "OŚWIADCZENIA ADMINISTRACYJNE"
        ]
        
        # Bilingual section mapping
        self.section_mapping = {
            "Opis danych oraz pozyskiwanie": "1. Data description and collection or re-use of existing data",
            "Dokumentacja i jakość danych": "2. Documentation and data quality",
            "Przechowywanie i tworzenie kopii zapasowych": "3. Storage and backup during the research process", 
            "Wymogi prawne, kodeks postępowania": "4. Legal requirements, codes of conduct",
            "Udostępnianie i długotrwałe przechowywanie": "5. Data sharing and long-term preservation",
            "Zadania związane z zarządzaniem danymi": "6. Data management responsibilities and resources"
        }
        
        # Bilingual subsection mapping with exact Polish subsections
        raw_subsection_mapping = {
            # 1. Data description section
            "Sposób pozyskiwania i opracowywania nowych danych i/lub ponownego wykorzystania dostępnych danych": 
                "How will new data be collected or produced and/or how will existing data be re-used?",
            "Pozyskiwane lub opracowywane dane (np. rodzaj, format, ilość)": 
                "What data (for example the types, formats, and volumes) will be collected or produced?",
            
            # 2. Documentation and data quality
            "Metadane i dokumenty (np. metodologia lub pozyskiwanie danych oraz sposób porządkowania danych) towarzyszące danym": 
                "What metadata and documentation (for example methodology or data collection and way of organising data) will accompany data?",
            "Stosowane środki kontroli jakości danych": 
                "What data quality control measures will be used?",
            
            # 3. Storage and backup
            "Przechowywanie i tworzenie kopii zapasowych danych i metadanych podczas badań": 
                "How will data and metadata be stored and backed up during the research process?",
            "Sposób zapewnienia bezpieczeństwa danych oraz ochrony danych wrażliwych podczas badań": 
                "How will data security and protection of sensitive data be taken care of during the research?",
            
            # 4. Legal requirements
            "Sposób zapewnienia zgodności z przepisami dotyczącymi danych osobowych i bezpieczeństwa danych w przypadku przetwarzania danych osobowych": 
                "If personal data are processed, how will compliance with legislation on personal data and on data security be ensured?",
            "Sposób zarządzania innymi kwestiami prawnymi, np. prawami własności intelektualnej lub własnością. Obowiązujące przepisy": 
                "How will other legal issues, such as intelectual property rights and ownership, be managed? What legislation is applicable?",
            
            # 5. Data sharing and preservation
            "Sposób i termin udostępnienia danych. Ewentualne ograniczenia w udostępnianiu danych lub przyczyny embarga": 
                "How and when will data be shared? Are there possible restrictions to data sharing or embargo reasons?",
            "Sposób wyboru danych przeznaczonych do przechowania oraz miejsce długotrwałego przechowywania danych (np. repozytorium lub archiwum danych)": 
                "How will data for preservation be selected, and where will data be preserved long-term (for example a data repository or archive)?",
            "Metody lub narzędzia programowe umożliwiające dostęp do danych i korzystanie z danych": 
                "What methods or software tools will be needed to access and use the data?",
            "Sposób zapewniający stosowanie unikalnego i trwałego identyfikatora (np. cyfrowego identyfikatora obiektu (DOI)) dla każdego zestawu danych": 
                "How will the application of a unique and persistent identifier (such us a Digital Object Identifier (DOI)) to each data set be ensured?",
            
            # 6. Data management responsibilities
            "Osoba (np. funkcja, stanowisko i instytucja) odpowiedzialna za zarządzanie danymi (np. data steward)": 
                "Who (for example role, position, and institution) will be responsible for data management (i.e the data steward)?",
            "Środki (np. finansowe i czasowe) przeznaczone do zarządzania danymi i zapewnienia możliwości odnalezienia, dostępu, interoperacyjności i ponownego wykorzystania danych": 
                "What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?"
        }
        
        # Create normalized versions of subsection mapping
        self.normalized_subsection_mapping = {}
        self.subsection_mapping = raw_subsection_mapping.copy()
        
        for polish, english in raw_subsection_mapping.items():
            # Remove trailing colon if present
            normalized_polish = polish[:-1].strip() if polish.endswith(':') else polish.strip()
            # Convert to lowercase for case-insensitive matching
            normalized_polish = normalized_polish.lower()
            self.normalized_subsection_mapping[normalized_polish] = english
            
            # Also add versions with/without trailing colon to main mapping
            if not polish.endswith(':'):
                self.subsection_mapping[polish + ':'] = english
            else:
                self.subsection_mapping[polish[:-1].strip()] = english
        
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
                "Who (for example role, position, and institution) will be responsible for data management (i.e the data steward)?",
                "What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?"
            ]
        }
        
        # Map section numbers to IDs for the review interface
        self.section_ids = {
            "1.1": "How will new data be collected or produced and/or how will existing data be re-used?",
            "1.2": "What data (for example the types, formats, and volumes) will be collected or produced?",
            "2.1": "What metadata and documentation (for example methodology or data collection and way of organising data) will accompany data?",
            "2.2": "What data quality control measures will be used?",
            "3.1": "How will data and metadata be stored and backed up during the research process?",
            "3.2": "How will data security and protection of sensitive data be taken care of during the research?",
            "4.1": "If personal data are processed, how will compliance with legislation on personal data and on data security be ensured?",
            "4.2": "How will other legal issues, such as intelectual property rights and ownership, be managed? What legislation is applicable?",
            "5.1": "How and when will data be shared? Are there possible restrictions to data sharing or embargo reasons?",
            "5.2": "How will data for preservation be selected, and where will data be preserved long-term (for example a data repository or archive)?",
            "5.3": "What methods or software tools will be needed to access and use the data?",
            "5.4": "How will the application of a unique and persistent identifier (such us a Digital Object Identifier (DOI)) to each data set be ensured?",
            "6.1": "Who (for example role, position, and institution) will be responsible for data management (i.e the data steward)?",
            "6.2": "What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?"
        }
        
        # Define key phrases to identify and tag in paragraphs
        self.key_phrases = {
            "methodology": ["methodology", "approach", "procedure", "process", "technique"],
            "data_format": ["format", "file type", "structure", "schema", "encoding", "xlsx", "docx", "csv", "txt", "tiff", "png", "pdf"],
            "data_volume": ["volume", "size", "amount", "quantity", "gigabyte", "terabyte", "mb", "gb", "tb"],
            "metadata": ["metadata", "documentation", "description", "annotation", "readme"],
            "quality": ["quality", "validation", "verification", "accuracy", "precision", "control measures"],
            "storage": ["storage", "repository", "database", "server", "cloud", "catalogue", "hard drive", "stored"],
            "backup": ["backup", "copy", "replicate", "redundancy"],
            "security": ["security", "protection", "encryption", "access control", "password", "protected"],
            "personal_data": ["personal data", "privacy", "consent", "gdpr", "anonymization"],
            "license": ["license", "copyright", "intellectual property", "ownership", "rights", "creative commons"],
            "sharing": ["sharing", "distribution", "dissemination", "access", "availability", "open access", "open research"],
            "preservation": ["preservation", "archiving", "long-term", "curation"],
            "tools": ["software", "tools", "application", "program", "code", "matlab"],
            "identifier": ["identifier", "doi", "persistent", "uuid", "orcid"],
            "responsibility": ["responsible", "manager", "steward", "oversight", "supervision", "investigator", "pi"],
            "resources": ["resources", "budget", "funding", "cost", "allocation"]
        }
    
    def validate_docx_file(self, file_path):
        """Validate DOCX file integrity"""
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            if not file_path.lower().endswith('.docx'):
                return False, "File is not a DOCX file"
            
            # Check if it's a valid ZIP file (DOCX is ZIP-based)
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    if 'word/document.xml' not in file_list:
                        return False, "Invalid DOCX structure: missing document.xml"
            except zipfile.BadZipFile:
                return False, "File is not a valid ZIP archive"
            
            # Try to load with python-docx
            doc = Document(file_path)
            paragraph_count = len(doc.paragraphs)
            table_count = len(doc.tables)
            
            if paragraph_count == 0 and table_count == 0:
                return False, "Document appears to be empty"
            
            return True, "File is valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def clean_table_delimiters(self, text):
        """Remove table formatting artifacts"""
        # Remove table border characters
        text = re.sub(r'\+[-=]+\+', '', text)
        text = re.sub(r'\|[\s]*\|', '', text)
        text = re.sub(r'^\||\|$', '', text, flags=re.MULTILINE)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()
    
    def extract_table_content(self, doc):
        """Extract content from table structures in DOCX files"""
        table_content = []
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text and not self.should_skip_text(cell_text):
                        # Clean table delimiters
                        cell_text = self.clean_table_delimiters(cell_text)
                        
                        if not cell_text:
                            continue
                        
                        # Check for formatting in cell runs
                        is_bold = any(run.bold for paragraph in cell.paragraphs for run in paragraph.runs if run.bold)
                        is_underlined = any(run.underline for paragraph in cell.paragraphs for run in paragraph.runs if run.underline)
                        
                        if is_bold and is_underlined:
                            table_content.append(f"UNDERLINED_BOLD:{cell_text}")
                        elif is_bold:
                            table_content.append(f"BOLD:{cell_text}")
                        elif is_underlined:
                            table_content.append(f"UNDERLINED:{cell_text}")
                        else:
                            table_content.append(cell_text)
        
        return table_content
    
    def process_file(self, file_path, output_dir):
        """Process a file and extract DMP content based on file type"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.process_pdf(file_path, output_dir)
        elif file_extension == '.docx':
            return self.process_docx(file_path, output_dir)
        else:
            return {
                "success": False,
                "message": f"Unsupported file type: {file_extension}"
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
            r"^\d+$",             # Just page numbers
            r"^\+[-=]+\+$",       # Table borders
            r"^\|[\s\|]*\|$"      # Table separators
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

    def clean_markup(self, text):
        """Remove common markup from text"""
        # Remove underline markup
        text = re.sub(r'\[([^]]+)\]\{\.underline\}', r'\1', text)
        # Remove bold markup
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        # Remove other common markup
        text = re.sub(r'__([^_]+)__', r'\1', text)
        # Remove mark formatting
        text = re.sub(r'\{\.mark\}', '', text)
        # Clean table delimiters
        text = self.clean_table_delimiters(text)
        return text
    
    def extract_formatted_text(self, paragraph):
        """Extract text with formatting information from a DOCX paragraph"""
        text = paragraph.text.strip()
        if not text:
            return text
            
        is_underlined = False
        is_bold = False
        
        # Check if any runs in the paragraph are underlined or bold
        for run in paragraph.runs:
            if run.underline:
                is_underlined = True
            if run.bold:
                is_bold = True
        
        # Clean the text
        text = self.clean_markup(text)
        
        # Return text with formatting info
        if is_underlined and is_bold:
            return f"UNDERLINED_BOLD:{text}"
        elif is_underlined:
            return f"UNDERLINED:{text}"
        elif is_bold:
            return f"BOLD:{text}"
        else:
            return text
    
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
        # Clean any markup in the paragraph
        clean_text = self.clean_markup(paragraph)
        tags = self.identify_key_phrases(clean_text)
        
        # Find lead sentence (first sentence or sentence with most key phrases)
        sentences = re.split(r'(?<=[.!?])\s+', clean_text)
        
        if not sentences:
            return {
                "text": clean_text,
                "tags": tags,
                "title": None
            }
        
        # Use first sentence as title if it's reasonably short
        title = sentences[0] if len(sentences[0]) < 100 else None
        
        return {
            "text": clean_text,
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
    
    def detect_section_from_text(self, text):
        """Detect section from text content, supporting multiple languages"""
        # Clean the text of any markup
        text = self.clean_markup(text)
        
        # Try numbered section (e.g. "1. Section title")
        section_match = re.match(r'^\s*(\d+)\.\s*(.*?)$', text)
        if section_match:
            section_num = section_match.group(1)
            section_title = section_match.group(2).strip()
            
            # Try to find matching section in dmp_structure
            for section in self.dmp_structure:
                if section.startswith(f"{section_num}."):
                    return section
            
            # Try to find in section mapping if not found directly
            for polish, english in self.section_mapping.items():
                if polish.lower() in section_title.lower():
                    return english
        
        # Try bold section titles
        if text.startswith("BOLD:"):
            clean_text = text.replace("BOLD:", "").strip()
            section_match = re.match(r'^\s*(\d+)\.\s*(.*?)$', clean_text)
            if section_match:
                section_num = section_match.group(1)
                for section in self.dmp_structure:
                    if section.startswith(f"{section_num}."):
                        return section
        
        return None
    
    def detect_subsection_from_text(self, text, current_section):
        """Detect subsection from text content, supporting multiple languages and partial matching"""
        # Clean the text of any markup
        text = self.clean_markup(text)
        original_text = text
        
        # Check if this is an underlined text which is often a subsection header
        is_underlined = text.startswith("UNDERLINED:")
        if is_underlined:
            text = text.replace("UNDERLINED:", "").strip()
        
        # Check if this is bold text
        if text.startswith("BOLD:"):
            text = text.replace("BOLD:", "").strip()
        
        # Normalize text - remove trailing colon and convert to lowercase
        normalized_text = text.lower()
        if normalized_text.endswith(':'):
            normalized_text = normalized_text[:-1].strip()
        
        # Debug output
        print(f"Trying to match subsection: '{text}' (normalized: '{normalized_text}')")
        
        # 1. Check for direct match with English subsections (case insensitive)
        if current_section:
            for subsection in self.dmp_structure.get(current_section, []):
                if text.lower() == subsection.lower():
                    print(f"Direct English match: '{text}' == '{subsection}'")
                    return subsection
        
        # 2. Try direct match with normalized Polish subsections
        if normalized_text in self.normalized_subsection_mapping:
            english = self.normalized_subsection_mapping[normalized_text]
            if current_section and english in self.dmp_structure.get(current_section, []):
                print(f"Direct Polish match: '{normalized_text}' -> '{english}'")
                return english
        
        # 3. Try the regular subsection mapping (with/without colons)
        for polish, english in self.subsection_mapping.items():
            # Case insensitive comparison
            if text.lower() == polish.lower() or text.lower() == polish.lower() + ':':
                if current_section and english in self.dmp_structure.get(current_section, []):
                    print(f"Regular mapping match: '{text}' ~ '{polish}'")
                    return english
        
        # 4. Try to match on the first part of subsection (prefix matching)
        for polish, english in self.subsection_mapping.items():
            # Find the shorter of the two strings for safe comparison
            min_length = min(len(normalized_text), len(polish.lower()), 30)
            # Compare the beginnings ignoring case
            if (normalized_text.startswith(polish.lower()[:min_length]) or 
                polish.lower().startswith(normalized_text[:min_length])) and min_length > 10:
                if current_section and english in self.dmp_structure.get(current_section, []):
                    print(f"Prefix match: '{normalized_text[:min_length]}' ~ '{polish.lower()[:min_length]}'")
                    return english
        
        # 5. Try substring matching for longer keys
        if len(normalized_text) > 10:  # Only for reasonably long strings
            for polish, english in self.subsection_mapping.items():
                polish_lower = polish.lower()
                
                # Skip very short strings
                if len(polish_lower) < 10:
                    continue
                    
                # Look for significant overlap
                if (normalized_text in polish_lower or polish_lower in normalized_text):
                    # Verify this subsection belongs to current section
                    if current_section and english in self.dmp_structure.get(current_section, []):
                        print(f"Substring match: '{normalized_text}' ~ '{polish_lower}'")
                        return english
        
        # 6. For formatted text or text ending with colon, try word-based matching
        if is_underlined or original_text.endswith(':') or original_text.startswith("BOLD:"):
            if current_section:
                best_match = None
                max_words = 0
                max_match_ratio = 0
                
                for subsection in self.dmp_structure.get(current_section, []):
                    # Get important words from subsection and line (length > 3)
                    subsection_words = set(word.lower() for word in subsection.split() if len(word) > 3)
                    line_words = set(word.lower() for word in text.split() if len(word) > 3)
                    
                    # Skip if no significant words
                    if not subsection_words or not line_words:
                        continue
                    
                    # Count matching words
                    matching_words = len(subsection_words.intersection(line_words))
                    match_ratio = matching_words / max(len(subsection_words), 1)
                    
                    # If we have a good match (at least 2 matching words or 20% of subsection words)
                    if matching_words >= 2 or match_ratio >= 0.2:
                        if matching_words > max_words or match_ratio > max_match_ratio:
                            max_words = matching_words
                            max_match_ratio = match_ratio
                            best_match = subsection
                            print(f"Word match: '{text}' ~ '{subsection}' ({matching_words} words, {match_ratio:.2f} ratio)")
                
                return best_match
        
        print(f"No subsection match found for: '{text}'")
        return None
    
    def process_docx(self, docx_path, output_dir):
        """Process a DOCX file and extract DMP content with enhanced table support"""
        try:
            print(f"Processing DOCX: {docx_path}")
            
            # Validate the DOCX file first
            is_valid, validation_message = self.validate_docx_file(docx_path)
            if not is_valid:
                return {
                    "success": False,
                    "message": f"DOCX validation failed: {validation_message}"
                }
            
            # Create a new Word document for output
            output_doc = Document()
            
            # Load the input document
            doc = Document(docx_path)
            
            # Extract text from both paragraphs and tables
            formatted_paragraphs = []
            
            # Process paragraphs
            for paragraph in doc.paragraphs:
                formatted_text = self.extract_formatted_text(paragraph)
                if formatted_text.strip():  # Only add non-empty paragraphs
                    formatted_paragraphs.append(formatted_text)
            
            # Process tables
            table_content = self.extract_table_content(doc)
            formatted_paragraphs.extend(table_content)
            
            # Join paragraphs for author detection and searching for markers
            all_text = "\n".join([p.replace("UNDERLINED:", "").replace("BOLD:", "").replace("UNDERLINED_BOLD:", "") 
                                 for p in formatted_paragraphs])
            
            # Extract author name
            author_name = self.extract_author_name(all_text)
            print(f"Author detected: {author_name}")
            
            # Find start and end positions in the formatted paragraphs list
            start_idx = -1
            end_idx = len(formatted_paragraphs)
            
            # Find start marker
            for i, para in enumerate(formatted_paragraphs):
                clean_para = para.replace("UNDERLINED:", "").replace("BOLD:", "").replace("UNDERLINED_BOLD:", "").strip()
                for mark in self.start_marks:
                    if mark in clean_para:
                        start_idx = i + 1  # Start from the next paragraph
                        print(f"Found start mark '{mark}' at paragraph {i}")
                        break
                if start_idx != -1:
                    break
            
            if start_idx == -1:
                # Try a more flexible approach - look for any paragraph that might be a section header
                for i, para in enumerate(formatted_paragraphs):
                    clean_para = para.replace("UNDERLINED:", "").replace("BOLD:", "").replace("UNDERLINED_BOLD:", "").strip()
                    if re.match(r'^\s*1\.\s+', clean_para):  # Look for "1. " at the start
                        start_idx = i
                        print(f"Fallback: Found potential section 1 at paragraph {i}")
                        break
            
            if start_idx == -1:
                return {
                    "success": False,
                    "message": "Could not find the start marker or section 1 in the document."
                }
            
            # Find end marker
            for i in range(start_idx, len(formatted_paragraphs)):
                clean_para = formatted_paragraphs[i].replace("UNDERLINED:", "").replace("BOLD:", "").replace("UNDERLINED_BOLD:", "").strip()
                for mark in self.end_marks:
                    if mark in clean_para:
                        end_idx = i
                        print(f"Found end mark '{mark}' at paragraph {i}")
                        break
                if i == end_idx:
                    break
            
            # Extract DMP content (paragraphs between start and end markers)
            dmp_paragraphs = formatted_paragraphs[start_idx:end_idx]
            print(f"Extracted {len(dmp_paragraphs)} paragraphs of DMP content")
            
            # Create document
            output_doc.add_heading("DATA MANAGEMENT PLAN", level=0)
            
            # Process the content by section
            section_content = {}
            tagged_content = {}
            
            for section in self.dmp_structure:
                section_content[section] = {}
                tagged_content[section] = {}
                for subsection in self.dmp_structure[section]:
                    section_content[section][subsection] = []
                    tagged_content[section][subsection] = []
            
            current_section = None
            current_subsection = None
            first_section_content = []  # Content before any section is identified
            pending_content = []  # Content after section but before subsection
            
            # Second pass: process paragraphs and identify sections/subsections
            for para in dmp_paragraphs:
                # Skip empty paragraphs
                if not para.strip():
                    continue
                
                clean_para = para
                if "BOLD:" in para or "UNDERLINED:" in para or "UNDERLINED_BOLD:" in para:
                    clean_para = para.replace("BOLD:", "").replace("UNDERLINED:", "").replace("UNDERLINED_BOLD:", "").strip()
                
                # Skip paragraphs that should be skipped
                if self.should_skip_text(clean_para):
                    continue
                
                # Try to identify section
                detected_section = self.detect_section_from_text(para)
                if detected_section:
                    # If we find a new section, flush any pending content
                    if current_section and current_subsection and pending_content:
                        for p in pending_content:
                            try:
                                section_content[current_section][current_subsection].append(p)
                                tagged_content[current_section][current_subsection].append(self.process_paragraph(p))
                            except KeyError:
                                print(f"Warning: Could not add content to {current_section} - {current_subsection}")
                        pending_content = []
                    
                    current_section = detected_section
                    current_subsection = None
                    print(f"Found section: {current_section}")
                    continue
                
                # If we don't have a section yet, collect content in first_section_content
                if not current_section:
                    if len(clean_para) > 5:  # Avoid very short lines
                        first_section_content.append(clean_para)
                    continue
                
                # Try to identify subsection if we have a current section
                detected_subsection = self.detect_subsection_from_text(para, current_section)
                if detected_subsection:
                    # If we find a new subsection, flush any pending content to the previous subsection
                    if current_subsection and pending_content:
                        for p in pending_content:
                            try:
                                section_content[current_section][current_subsection].append(p)
                                tagged_content[current_section][current_subsection].append(self.process_paragraph(p))
                            except KeyError:
                                print(f"Warning: Could not add content to {current_section} - {current_subsection}")
                        pending_content = []
                    
                    current_subsection = detected_subsection
                    print(f"Found subsection: {current_subsection[:50]}...")
                    continue
                
                # Handle content based on current context
                if current_section and current_subsection:
                    # If it's a meaningful paragraph (not a header or marker), add to content
                    if len(clean_para) > 5 and not para.startswith("UNDERLINED:") and not para.startswith("BOLD:") and not para.startswith("UNDERLINED_BOLD:"):
                        try:
                            section_content[current_section][current_subsection].append(clean_para)
                            tagged_content[current_section][current_subsection].append(self.process_paragraph(clean_para))
                        except KeyError as e:
                            print(f"Warning: KeyError when adding content: {str(e)}")
                            # Create missing subsection if needed
                            if current_subsection not in section_content[current_section]:
                                section_content[current_section][current_subsection] = [clean_para]
                                tagged_content[current_section][current_subsection] = [self.process_paragraph(clean_para)]
                    elif not para.startswith("UNDERLINED:") and not para.startswith("BOLD:") and not para.startswith("UNDERLINED_BOLD:") and len(clean_para) > 5:
                        # Add to pending content for non-header paragraphs
                        pending_content.append(clean_para)
                elif current_section:
                    # We have a section but no subsection yet
                    if len(clean_para) > 5:
                        pending_content.append(clean_para)
            
            # Handle content collected before any section was identified
            if first_section_content and len(self.dmp_structure) > 0:
                # Get the first section and subsection
                first_section = list(self.dmp_structure.keys())[0]
                if len(self.dmp_structure[first_section]) > 0:
                    first_subsection = self.dmp_structure[first_section][0]
                    for p in first_section_content:
                        section_content[first_section][first_subsection].append(p)
                        tagged_content[first_section][first_subsection].append(self.process_paragraph(p))
                    print(f"Added {len(first_section_content)} paragraphs of content before first section to {first_section} - {first_subsection}")
            
            # Flush any remaining pending content
            if current_section and current_subsection and pending_content:
                for p in pending_content:
                    try:
                        section_content[current_section][current_subsection].append(p)
                        tagged_content[current_section][current_subsection].append(self.process_paragraph(p))
                    except KeyError:
                        print(f"Warning: Could not add final content to {current_section} - {current_subsection}")
            elif current_section and pending_content:
                # If we have content for a section but no subsection was identified,
                # assign to the first subsection of that section
                if len(self.dmp_structure[current_section]) > 0:
                    first_subsection = self.dmp_structure[current_section][0]
                    for p in pending_content:
                        try:
                            section_content[current_section][first_subsection].append(p)
                            tagged_content[current_section][first_subsection].append(self.process_paragraph(p))
                        except KeyError:
                            print(f"Warning: Could not add content to {current_section} - {first_subsection}")
            
            # Add content to document
            for section in self.dmp_structure:
                output_doc.add_heading(section, level=1)
                
                for subsection in self.dmp_structure[section]:
                    output_doc.add_heading(subsection, level=2)
                    
                    # Safely get content
                    content = []
                    try:
                        content = section_content[section][subsection]
                    except KeyError:
                        print(f"Warning: Missing content for {section} - {subsection}")
                    
                    if content:
                        for text in content:
                            output_doc.add_paragraph(text)
                    else:
                        # Add blank paragraph for empty content
                        output_doc.add_paragraph("")
            
            # Create review structure
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
            base_name = os.path.splitext(os.path.basename(docx_path))[0]
            
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
            output_doc.save(output_path)
            
            # Save review structure as JSON
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
                "message": "DMP successfully extracted from DOCX with table support"
            }
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Error processing DOCX: {str(e)}")
            print(traceback_str)
            return {
                "success": False,
                "message": f"Error processing DOCX: {str(e)}"
            }
    
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
                    # Try fallback - look for Section 1
                    match = re.search(r'1\.\s+[\w\s]+', all_text)
                    if match:
                        start_pos = match.start()
                        print(f"Fallback: Found potential section 1 at position {start_pos}")
                    else:
                        return {
                            "success": False,
                            "message": "Could not find the start marker or section 1 in the document."
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
                first_section_content = []  # Content before any section is identified
                pending_content = []  # Content after section but before subsection
                
                # Process lines to find sections and subsections
                for line in lines:
                    line = line.strip()
                    if not line or self.should_skip_text(line):
                        continue
                    
                    # Try to identify section
                    detected_section = self.detect_section_from_text(line)
                    if detected_section:
                        # If we find a new section, flush any pending content
                        if current_section and current_subsection and pending_content:
                            for p in pending_content:
                                try:
                                    section_content[current_section][current_subsection].append(p)
                                    tagged_content[current_section][current_subsection].append(self.process_paragraph(p))
                                except KeyError:
                                    print(f"Warning: Could not add content to {current_section} - {current_subsection}")
                            pending_content = []
                        
                        current_section = detected_section
                        current_subsection = None
                        print(f"Found section: {current_section}")
                        continue
                    
                    # If we don't have a section yet, collect content in first_section_content
                    if not current_section:
                        if len(line) > 5:  # Avoid very short lines
                            first_section_content.append(line)
                        continue
                    
                    # Try to identify subsection if we have a current section
                    detected_subsection = self.detect_subsection_from_text(line, current_section)
                    if detected_subsection:
                        # If we find a new subsection, flush any pending content to the previous subsection
                        if current_subsection and pending_content:
                            for p in pending_content:
                                try:
                                    section_content[current_section][current_subsection].append(p)
                                    tagged_content[current_section][current_subsection].append(self.process_paragraph(p))
                                except KeyError:
                                    print(f"Warning: Could not add content to {current_section} - {current_subsection}")
                            pending_content = []
                        
                        current_subsection = detected_subsection
                        print(f"Found subsection: {current_subsection[:30]}...")
                        continue
                    
                    # Add content to appropriate subsection or pending content
                    if current_section and current_subsection:
                        if len(line) > 5:  # Avoid short lines
                            try:
                                section_content[current_section][current_subsection].append(line)
                                tagged_content[current_section][current_subsection].append(self.process_paragraph(line))
                            except KeyError as e:
                                print(f"Warning: KeyError when adding content: {str(e)}")
                                # Create missing subsection if needed
                                if current_subsection not in section_content[current_section]:
                                    section_content[current_section][current_subsection] = [line]
                                    tagged_content[current_section][current_subsection] = [self.process_paragraph(line)]
                    elif current_section and len(line) > 5:
                        # Add to pending content
                        pending_content.append(line)
                
                # Handle content collected before any section was identified
                if first_section_content and len(self.dmp_structure) > 0:
                    # Get the first section and subsection
                    first_section = list(self.dmp_structure.keys())[0]
                    if len(self.dmp_structure[first_section]) > 0:
                        first_subsection = self.dmp_structure[first_section][0]
                        for p in first_section_content:
                            section_content[first_section][first_subsection].append(p)
                            tagged_content[first_section][first_subsection].append(self.process_paragraph(p))
                        print(f"Added {len(first_section_content)} paragraphs of content before first section to {first_section} - {first_subsection}")
                
                # Flush any remaining pending content
                if current_section and current_subsection and pending_content:
                    for p in pending_content:
                        try:
                            section_content[current_section][current_subsection].append(p)
                            tagged_content[current_section][current_subsection].append(self.process_paragraph(p))
                        except KeyError:
                            print(f"Warning: Could not add final content to {current_section} - {current_subsection}")
                elif current_section and pending_content:
                    # If we have content for a section but no subsection was identified,
                    # assign to the first subsection of that section
                    if len(self.dmp_structure[current_section]) > 0:
                        first_subsection = self.dmp_structure[current_section][0]
                        for p in pending_content:
                            try:
                                section_content[current_section][first_subsection].append(p)
                                tagged_content[current_section][first_subsection].append(self.process_paragraph(p))
                            except KeyError:
                                print(f"Warning: Could not add content to {current_section} - {first_subsection}")
                
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
                
                                        
                        # Add to review structure
                        review_structure[section_id] = {
                            "section": section,
                            "question": subsection,
                            "paragraphs": paragraphs,
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
                    "message": "DMP successfully extracted from PDF"
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