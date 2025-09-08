# utils/extractor.py - Enhanced version with improved DOCX and PDF processing
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
        # Key phrases functionality removed
    
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
    
    def should_skip_text(self, text, is_pdf=False):
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
        
        # Additional PDF-specific patterns
        if is_pdf:
            pdf_patterns = [
                r"wydruk roboczy",     # Draft watermark
                r"\d{6,}",             # Project IDs (6+ digits)
                r"OPUS-\d+",           # Grant program markers
                r"Strona \d+ z \d+",   # Page indicators
                r"TAK\s*NIE\s*$",      # Checkbox patterns
                r"^\s*[✓✗×]\s*$",      # Checkbox symbols
                r"^\s*\[\s*[Xx]?\s*\]\s*$",  # Checkbox brackets
                r"^\s*_{3,}\s*$",      # Underline fields
                r"^\.{3,}$",           # Dotted lines
                r"^\s*data\s*:\s*$",   # Date fields
                r"^\s*podpis\s*:\s*$", # Signature fields
                # Complex header/footer pattern for grant applications
                r"OSF,?\s*OPUS-\d+\s*Strona\s+\d+\s*ID:\s*\d+,?\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",
                # More flexible patterns for parts of the header
                r"OSF,?\s*OPUS-\d+",   # OSF + OPUS markers
                r"ID:\s*\d{6,}",       # ID with 6+ digits
                r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}",  # Timestamp pattern
                # Combined pattern matching multiple elements (more flexible)
                r"(OSF|OPUS-\d+|Strona\s+\d+|ID:\s*\d+|20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}).*?(OSF|OPUS-\d+|Strona\s+\d+|ID:\s*\d+|20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
            ]
            skip_patterns.extend(pdf_patterns)
        
        # Check basic patterns first
        if any(re.search(pattern, text, re.IGNORECASE) is not None for pattern in skip_patterns):
            return True
        
        # Special handling for complex grant application headers/footers
        if is_pdf:
            return self._is_grant_header_footer(text)
        
        return False
    
    def _is_grant_header_footer(self, text):
        """Detect complex grant application header/footer patterns with variable elements"""
        # Clean the text for analysis
        clean_text = re.sub(r'\s+', ' ', text.strip())
        
        # Define the variable components that appear in grant headers/footers
        components = {
            'osf': r'OSF,?\s*',
            'opus': r'OPUS-\d+',
            'page': r'Strona\s+\d+',
            'id': r'ID:\s*\d+',
            'date': r'\d{4}-\d{2}-\d{2}',
            'time': r'\d{2}:\d{2}:\d{2}',
            'timestamp': r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # Combined date-time
            'project_id': r'\d{6,}',  # Long numeric IDs
        }
        
        # Count how many components are present
        component_matches = 0
        matched_components = []
        
        for name, pattern in components.items():
            if re.search(pattern, clean_text, re.IGNORECASE):
                component_matches += 1
                matched_components.append(name)
        
        # If we have 3 or more components, it's likely a header/footer
        if component_matches >= 3:
            print(f"Detected grant header/footer: '{clean_text}' (matched: {matched_components})")
            return True
        
        # Additional check for specific patterns that are clearly headers/footers
        header_indicators = [
            # Patterns that commonly appear in grant application headers
            r'(OSF|OPUS).{0,50}(Strona|ID).{0,50}\d{4}-\d{2}-\d{2}',
            r'ID:\s*\d+.{0,30}\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
            r'OPUS-\d+.{0,50}ID:\s*\d+',
            # Short lines with multiple technical identifiers
            r'^.{0,100}(OSF|OPUS|ID:|Strona).{0,100}(OSF|OPUS|ID:|Strona).{0,100}$',
        ]
        
        for pattern in header_indicators:
            if re.search(pattern, clean_text, re.IGNORECASE):
                print(f"Detected header via indicator pattern: '{clean_text}'")
                return True
        
        return False
    
    def test_skip_patterns(self):
        """Test method to verify skip patterns work correctly"""
        test_cases = [
            "OSF, OPUS-29 Strona 41 ID: 651313, 2025-06-09 11:29:38",
            "OSF OPUS-30 Strona 1 ID: 123456 2024-12-01 09:15:22",
            "OPUS-15 ID: 987654 Strona 25",
            "Regular content that should not be skipped",
            "Some research data about experiments"
        ]
        
        print("Testing skip patterns:")
        for test_case in test_cases:
            should_skip = self.should_skip_text(test_case, is_pdf=True)
            print(f"'{test_case}' -> Skip: {should_skip}")
        
        return True
    
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
    
    # Key phrases identification removed
    
    def process_paragraph(self, paragraph):
        """Process a paragraph to extract key information"""
        # Clean any markup in the paragraph
        clean_text = self.clean_markup(paragraph)
        tags = []  # Key phrases functionality removed
        
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
    
    def detect_section_from_text(self, text, is_pdf=False):
        """Detect section from text content, supporting multiple languages and PDF forms"""
        # Clean the text of any markup
        original_text = text
        text = self.clean_markup(text)
        
        # Enhanced section patterns for PDFs
        if is_pdf:
            # Look for form-style section headers
            form_patterns = [
                r"PLAN\s+ZARZĄDZANIA\s+DANYMI",
                r"DATA\s+MANAGEMENT\s+PLAN",
                r"Opis\s+danych\s+oraz\s+pozyskiwanie",
                r"Dokumentacja\s+i\s+jakość\s+danych",
                r"Przechowywanie\s+i\s+tworzenie\s+kopii",
                r"Wymogi\s+prawne",
                r"Udostępnianie\s+i\s+długotrwałe",
                r"Zadania\s+związane\s+z\s+zarządzaniem"
            ]
            
            for pattern in form_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Map to corresponding English section
                    for polish, english in self.section_mapping.items():
                        if re.search(pattern.replace("\\s+", "\\s*"), polish, re.IGNORECASE):
                            print(f"PDF form section detected: '{text}' -> '{english}'")
                            return english
        
        # Try numbered section (e.g. "1. Section title")
        section_match = re.match(r'^\s*(\d+)\.\s*(.*?)$', text)
        if section_match:
            section_num = section_match.group(1)
            section_title = section_match.group(2).strip()
            
            print(f"Numbered section detected: {section_num}. {section_title}")
            
            # Try to find matching section in dmp_structure
            for section in self.dmp_structure:
                if section.startswith(f"{section_num}."):
                    print(f"Matched to DMP structure: {section}")
                    return section
            
            # Try to find in section mapping if not found directly
            for polish, english in self.section_mapping.items():
                if self._text_similarity(polish.lower(), section_title.lower()) > 0.5:
                    print(f"Matched via section mapping: {polish} -> {english}")
                    return english
        
        # Try bold/underlined section titles
        if any(text.startswith(prefix) for prefix in ["BOLD:", "UNDERLINED:", "UNDERLINED_BOLD:"]):
            clean_text = re.sub(r'^(BOLD:|UNDERLINED:|UNDERLINED_BOLD:)', '', text).strip()
            section_match = re.match(r'^\s*(\d+)\.\s*(.*?)$', clean_text)
            if section_match:
                section_num = section_match.group(1)
                for section in self.dmp_structure:
                    if section.startswith(f"{section_num}."):
                        print(f"Formatted section matched: {section}")
                        return section
        
        # Try direct section title matching
        for polish, english in self.section_mapping.items():
            if self._text_similarity(polish.lower(), text.lower()) > 0.6:
                print(f"Direct title match: {polish} -> {english}")
                return english
        
        return None
    
    def _text_similarity(self, text1, text2):
        """Calculate simple text similarity based on word overlap"""
        words1 = set(word.lower() for word in text1.split() if len(word) > 2)
        words2 = set(word.lower() for word in text2.split() if len(word) > 2)
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_subsection_from_text(self, text, current_section, is_pdf=False):
        """Detect subsection from text content, supporting multiple languages and partial matching"""
        # Clean the text of any markup
        original_text = text
        text = self.clean_markup(text)
        
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
        print(f"Trying to match subsection: '{text}' (normalized: '{normalized_text}', section: {current_section})")
        
        if not current_section:
            print("No current section, skipping subsection detection")
            return None
        
        # 1. Check for direct match with English subsections (case insensitive)
        for subsection in self.dmp_structure.get(current_section, []):
            if self._text_similarity(text.lower(), subsection.lower()) > 0.8:
                print(f"High similarity English match: '{text}' ~ '{subsection}'")
                return subsection
        
        # 2. Try enhanced Polish subsection matching with similarity scoring
        best_match = None
        best_score = 0.0
        
        for polish, english in self.subsection_mapping.items():
            if current_section and english in self.dmp_structure.get(current_section, []):
                # Calculate similarity scores
                similarity = self._text_similarity(normalized_text, polish.lower())
                
                # Boost score for exact matches or strong partial matches
                if normalized_text == polish.lower():
                    similarity = 1.0
                elif normalized_text in polish.lower() or polish.lower() in normalized_text:
                    similarity = max(similarity, 0.7)
                
                if similarity > best_score and similarity > 0.3:
                    best_score = similarity
                    best_match = english
                    print(f"Polish mapping candidate: '{text}' ~ '{polish}' -> '{english}' (score: {similarity:.2f})")
        
        if best_match and best_score > 0.5:
            print(f"Best Polish match: '{text}' -> '{best_match}' (score: {best_score:.2f})")
            return best_match
        
        # 3. Enhanced word-based matching for formatted text
        if (is_underlined or original_text.endswith(':') or 
            original_text.startswith("BOLD:") or len(text) > 20):
            
            best_word_match = None
            max_match_ratio = 0
            
            for subsection in self.dmp_structure.get(current_section, []):
                # Get important words from subsection and line
                subsection_words = set(word.lower() for word in subsection.split() 
                                     if len(word) > 3 and word.lower() not in ['data', 'will', 'used', 'such', 'example'])
                line_words = set(word.lower() for word in text.split() 
                               if len(word) > 3 and word.lower() not in ['data', 'będą', 'które', 'oraz'])
                
                if not subsection_words or not line_words:
                    continue
                
                # Count matching words
                matching_words = len(subsection_words.intersection(line_words))
                match_ratio = matching_words / max(len(subsection_words), 1)
                
                # Lower threshold for better matching, but require at least 2 matching words
                if matching_words >= 2 and match_ratio > max_match_ratio:
                    max_match_ratio = match_ratio
                    best_word_match = subsection
                    print(f"Word match candidate: '{text}' ~ '{subsection}' ({matching_words} words, {match_ratio:.2f} ratio)")
            
            if best_word_match and max_match_ratio > 0.15:  # Lower threshold
                print(f"Best word match: '{text}' -> '{best_word_match}' (ratio: {max_match_ratio:.2f})")
                return best_word_match
        
        # 4. PDF-specific subsection detection for form fields
        if is_pdf and len(text) > 10:
            # Look for characteristic Polish question patterns
            question_indicators = [
                r"sposób.*?danych",
                r"jak.*?będą",
                r"jakie.*?dane",
                r"gdzie.*?przechowywane",
                r"kto.*?odpowiedzialny",
                r"środki.*?przeznaczone"
            ]
            
            for indicator in question_indicators:
                if re.search(indicator, normalized_text, re.IGNORECASE):
                    # Try to match with subsections in current section
                    for subsection in self.dmp_structure.get(current_section, []):
                        if self._text_similarity(normalized_text, subsection.lower()) > 0.2:
                            print(f"PDF question pattern match: '{text}' -> '{subsection}'")
                            return subsection
        
        print(f"No subsection match found for: '{text}' (best score: {best_score:.2f})")
        return None
    
    def extract_pdf_table_content(self, text_lines):
        """Extract and structure table-like content from PDF text lines"""
        table_content = []
        current_table = []
        in_table = False
        
        for line in text_lines:
            line = line.strip()
            if not line:
                if in_table and current_table:
                    # End of table, process it
                    processed_table = self._process_table_rows(current_table)
                    table_content.extend(processed_table)
                    current_table = []
                    in_table = False
                continue
            
            # Detect table patterns
            is_table_line = (
                # Multiple columns separated by spaces (3+ spaces between words)
                len(re.findall(r'\s{3,}', line)) > 1 or
                # Currency/number patterns (budget tables)
                re.search(r'\d+[,.]?\d*\s+(PLN|EUR|USD|\d+)', line) or
                # Aligned data with consistent spacing
                re.search(r'^[^\s]+\s{5,}[^\s]+\s{5,}[^\s]+', line) or
                # Form fields with underscores or dots
                re.search(r'_{3,}|\.{3,}', line)
            )
            
            if is_table_line:
                if not in_table:
                    in_table = True
                current_table.append(line)
            else:
                if in_table and current_table:
                    # Process completed table
                    processed_table = self._process_table_rows(current_table)
                    table_content.extend(processed_table)
                    current_table = []
                    in_table = False
                
                # Add non-table content normally
                if not self.should_skip_text(line, is_pdf=True):
                    table_content.append(line)
        
        # Process any remaining table
        if current_table:
            processed_table = self._process_table_rows(current_table)
            table_content.extend(processed_table)
        
        return table_content
    
    def _process_table_rows(self, table_rows):
        """Process table rows to extract meaningful content"""
        if not table_rows:
            return []
        
        processed = []
        for row in table_rows:
            # Clean up table formatting
            clean_row = re.sub(r'\s{2,}', ' | ', row)  # Replace multiple spaces with separator
            clean_row = re.sub(r'[_\.]{3,}', '[field]', clean_row)  # Replace field markers
            
            # Skip rows that are mostly formatting
            if not re.search(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', clean_row):
                continue
                
            processed.append(clean_row)
        
        return processed
    
    def improve_content_assignment(self, all_content, is_pdf=False):
        """Improved content assignment logic with better section/subsection detection"""
        # Initialize structures
        section_content = {}
        tagged_content = {}
        unconnected_text = []
        
        for section in self.dmp_structure:
            section_content[section] = {}
            tagged_content[section] = {}
            for subsection in self.dmp_structure[section]:
                section_content[section][subsection] = []
                tagged_content[section][subsection] = []
        
        current_section = None
        current_subsection = None
        content_buffer = []  # Buffer for content without clear assignment
        
        print(f"Processing {len(all_content)} content items...")
        
        for i, content_item in enumerate(all_content):
            if not content_item.strip():
                continue
            
            print(f"\n--- Processing item {i+1}: '{content_item[:100]}...'")
            
            # Try to detect section
            detected_section = self.detect_section_from_text(content_item, is_pdf=is_pdf)
            if detected_section:
                # Flush buffer to previous section/subsection
                if current_section and current_subsection and content_buffer:
                    print(f"Flushing {len(content_buffer)} buffered items to {current_section} -> {current_subsection}")
                    for buffered_content in content_buffer:
                        self._assign_content_safely(section_content, tagged_content, 
                                                  current_section, current_subsection, buffered_content)
                    content_buffer = []
                
                current_section = detected_section
                current_subsection = None
                print(f"Section changed to: {current_section}")
                continue
            
            # Try to detect subsection
            if current_section:
                detected_subsection = self.detect_subsection_from_text(content_item, current_section, is_pdf=is_pdf)
                if detected_subsection:
                    # Flush buffer to previous subsection
                    if current_subsection and content_buffer:
                        print(f"Flushing {len(content_buffer)} buffered items to {current_section} -> {current_subsection}")
                        for buffered_content in content_buffer:
                            self._assign_content_safely(section_content, tagged_content, 
                                                      current_section, current_subsection, buffered_content)
                        content_buffer = []
                    
                    current_subsection = detected_subsection
                    print(f"Subsection changed to: {current_subsection}")
                    continue
            
            # Handle regular content
            if current_section and current_subsection:
                # Direct assignment
                print(f"Assigning content to {current_section} -> {current_subsection}")
                self._assign_content_safely(section_content, tagged_content, 
                                          current_section, current_subsection, content_item)
            elif current_section:
                # Buffer content until we find a subsection
                print(f"Buffering content for section {current_section}")
                content_buffer.append(content_item)
            else:
                # No section identified yet
                print("Adding to unconnected text (no section)")
                unconnected_text.append({"text": content_item, "type": "no_section"})
        
        # Handle remaining buffered content
        if content_buffer:
            if current_section and current_subsection:
                print(f"Final flush: {len(content_buffer)} items to {current_section} -> {current_subsection}")
                for buffered_content in content_buffer:
                    self._assign_content_safely(section_content, tagged_content, 
                                              current_section, current_subsection, buffered_content)
            else:
                print(f"Moving {len(content_buffer)} buffered items to unconnected")
                for buffered_content in content_buffer:
                    unconnected_text.append({"text": buffered_content, "type": "buffered"})
        
        return section_content, tagged_content, unconnected_text
    
    def _assign_content_safely(self, section_content, tagged_content, section, subsection, content):
        """Safely assign content to section/subsection with error handling"""
        try:
            if section not in section_content:
                print(f"Warning: Section '{section}' not in structure")
                return
            if subsection not in section_content[section]:
                print(f"Warning: Subsection '{subsection}' not in section '{section}'")
                return
            
            section_content[section][subsection].append(content)
            tagged_content[section][subsection].append(self.process_paragraph(content))
            print(f"Successfully assigned content (length: {len(content)})")
            
        except Exception as e:
            print(f"Error assigning content: {str(e)}")
            # Don't fail completely, just log the error
    
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
            
            # Use improved content assignment logic
            print("Using improved content assignment for DOCX processing...")
            
            # Filter out meaningful content (skip formatting markers, headers, etc.)
            meaningful_content = []
            for para in dmp_paragraphs:
                if not para.strip():
                    continue
                    
                clean_para = para
                if "BOLD:" in para or "UNDERLINED:" in para or "UNDERLINED_BOLD:" in para:
                    clean_para = para.replace("BOLD:", "").replace("UNDERLINED:", "").replace("UNDERLINED_BOLD:", "").strip()
                
                # Skip paragraphs that should be skipped
                if self.should_skip_text(clean_para, is_pdf=False):
                    continue
                    
                # Only add substantial content
                if len(clean_para) > 5:
                    meaningful_content.append(para)  # Keep original formatting for detection
            
            # Use improved assignment logic
            section_content, tagged_content, unconnected_text = self.improve_content_assignment(
                meaningful_content, is_pdf=False
            )
            
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
            
            # Add unconnected text to review structure if present
            if unconnected_text:
                review_structure["_unconnected_text"] = unconnected_text
                print(f"Added {len(unconnected_text)} unconnected text items to review structure")
            
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
                
                # Split the content into lines and use improved table extraction
                lines = dmp_text.split("\n")
                print(f"Extracted {len(lines)} lines from PDF")
                
                # Use PDF table extraction to better structure content
                structured_content = self.extract_pdf_table_content(lines)
                print(f"After table processing: {len(structured_content)} content items")
                
                # Use improved content assignment logic
                section_content, tagged_content, unconnected_text = self.improve_content_assignment(
                    structured_content, is_pdf=True
                )
                
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
                        
                        # Safely get paragraphs
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
                
                # Add unconnected text to review structure if present
                if unconnected_text:
                    review_structure["_unconnected_text"] = unconnected_text
                    print(f"Added {len(unconnected_text)} unconnected text items to PDF review structure")
                
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
    
    # Key phrases functionality removed