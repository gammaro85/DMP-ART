# utils/extractor.py - Enhanced version with improved DOCX and PDF processing
import os
import re
import json
import uuid
import zipfile
from docx import Document
from datetime import datetime
import PyPDF2
import logging
from difflib import SequenceMatcher
from collections import Counter
import math

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
        # TODO: Implement author name extraction logic
        pass

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
        """Enhanced section detection with fuzzy matching and multiple algorithms"""
        # Clean the text of any markup
        original_text = text
        text = self.clean_markup(text)
        
        # Enhanced section patterns for PDFs with fuzzy matching
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
            
            # Enhanced matching with fuzzy similarity for section mapping
            best_match = self._find_best_section_match(section_title)
            if best_match:
                return best_match
        
        # Try bold/underlined section titles
        if any(text.startswith(prefix) for prefix in ["BOLD:", "UNDERLINED:", "UNDERLINED_BOLD:"]):
            clean_text = re.sub(r'^(BOLD:|UNDERLINED:|UNDERLINED_BOLD:)', '', text).strip()
            section_match = re.match(r'^\s*(\d+)\.\s*(.*?)$', clean_text)
            if section_match:
                section_num = section_match.group(1)
                section_title = section_match.group(2).strip()
                
                for section in self.dmp_structure:
                    if section.startswith(f"{section_num}."):
                        print(f"Formatted section matched: {section}")
                        return section
                
                # Fallback to fuzzy matching for formatted titles
                best_match = self._find_best_section_match(section_title)
                if best_match:
                    return best_match
        
        # Enhanced direct section title matching with fuzzy algorithms
        best_match = self._find_best_section_match(text)
        if best_match:
            return best_match
        
        return None
    
    def _find_best_section_match(self, text, threshold=0.4):
        """Find best section match using enhanced similarity algorithms"""
        best_match = None
        best_score = 0.0
        
        # Check against section mapping (Polish -> English)
        for polish, english in self.section_mapping.items():
            # Try all similarity methods
            similarity_scores = [
                self._text_similarity(polish.lower(), text.lower(), 'jaccard'),
                self._text_similarity(polish.lower(), text.lower(), 'cosine'),
                self._text_similarity(polish.lower(), text.lower(), 'sequence'),
                self._text_similarity(polish.lower(), text.lower(), 'combined')
            ]
            
            # Take the maximum similarity
            max_score = max(similarity_scores)
            
            if max_score > best_score and max_score > threshold:
                best_score = max_score
                best_match = english
                print(f"Section match: '{text}' ~ '{polish}' -> '{english}' (score: {max_score:.3f})")
        
        # Also check direct English section names
        for section in self.dmp_structure:
            similarity_scores = [
                self._text_similarity(section.lower(), text.lower(), 'jaccard'),
                self._text_similarity(section.lower(), text.lower(), 'cosine'),
                self._text_similarity(section.lower(), text.lower(), 'sequence'),
                self._text_similarity(section.lower(), text.lower(), 'combined')
            ]
            
            max_score = max(similarity_scores)
            
            if max_score > best_score and max_score > threshold:
                best_score = max_score
                best_match = section
                print(f"Direct English section match: '{text}' ~ '{section}' (score: {max_score:.3f})")
        
        return best_match if best_score > threshold else None
    
    def _text_similarity(self, text1, text2, method='combined'):
        """Enhanced text similarity with multiple algorithms"""
        if method == 'jaccard':
            return self._jaccard_similarity(text1, text2)
        elif method == 'cosine':
            return self._cosine_similarity(text1, text2)
        elif method == 'sequence':
            return self._sequence_similarity(text1, text2)
        elif method == 'combined':
            # Combine multiple similarity measures
            jaccard = self._jaccard_similarity(text1, text2)
            cosine = self._cosine_similarity(text1, text2)
            sequence = self._sequence_similarity(text1, text2)
            # Weighted combination favoring exact matches
            return (jaccard * 0.4 + cosine * 0.3 + sequence * 0.3)
        else:
            return self._jaccard_similarity(text1, text2)
    
    def _jaccard_similarity(self, text1, text2):
        """Jaccard similarity based on word sets"""
        words1 = set(word.lower() for word in re.findall(r'\w+', text1) if len(word) > 2)
        words2 = set(word.lower() for word in re.findall(r'\w+', text2) if len(word) > 2)
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _cosine_similarity(self, text1, text2):
        """Cosine similarity based on term frequency"""
        words1 = [word.lower() for word in re.findall(r'\w+', text1) if len(word) > 2]
        words2 = [word.lower() for word in re.findall(r'\w+', text2) if len(word) > 2]
        
        if not words1 or not words2:
            return 0.0
        
        # Create term frequency vectors
        counter1 = Counter(words1)
        counter2 = Counter(words2)
        
        # Get all unique terms
        terms = set(counter1.keys()).union(set(counter2.keys()))
        
        if not terms:
            return 0.0
        
        # Create vectors
        vec1 = [counter1.get(term, 0) for term in terms]
        vec2 = [counter2.get(term, 0) for term in terms]
        
        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _sequence_similarity(self, text1, text2):
        """Sequence similarity for exact substring matches"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def detect_subsection_from_text(self, text, current_section, is_pdf=False):
        """Enhanced subsection detection with improved fuzzy matching"""
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
        
        # Enhanced subsection matching with all similarity algorithms
        best_match = self._find_best_subsection_match(text, current_section, threshold=0.3)
        if best_match:
            return best_match
        
        # Fallback: Enhanced word-based matching for formatted text
        if (is_underlined or original_text.endswith(':') or 
            original_text.startswith("BOLD:") or len(text) > 20):
            
            word_match = self._find_word_based_subsection_match(text, current_section)
            if word_match:
                return word_match
        
        # PDF-specific subsection detection for form fields
        if is_pdf and len(text) > 10:
            pdf_match = self._find_pdf_question_match(text, current_section, normalized_text)
            if pdf_match:
                return pdf_match
        
        print(f"No subsection match found for: '{text}'")
        return None
    
    def _find_best_subsection_match(self, text, current_section, threshold=0.3):
        """Find best subsection match using enhanced similarity algorithms"""
        normalized_text = text.lower().rstrip(':')
        best_match = None
        best_score = 0.0
        
        # 1. Direct match with English subsections
        for subsection in self.dmp_structure.get(current_section, []):
            similarity_scores = [
                self._text_similarity(text.lower(), subsection.lower(), 'jaccard'),
                self._text_similarity(text.lower(), subsection.lower(), 'cosine'),
                self._text_similarity(text.lower(), subsection.lower(), 'sequence'),
                self._text_similarity(text.lower(), subsection.lower(), 'combined')
            ]
            
            max_score = max(similarity_scores)
            
            if max_score > best_score and max_score > threshold:
                best_score = max_score
                best_match = subsection
                print(f"English subsection match: '{text}' ~ '{subsection}' (score: {max_score:.3f})")
        
        # 2. Enhanced Polish subsection matching
        for polish, english in self.subsection_mapping.items():
            if current_section and english in self.dmp_structure.get(current_section, []):
                # Try all similarity methods
                similarity_scores = [
                    self._text_similarity(normalized_text, polish.lower(), 'jaccard'),
                    self._text_similarity(normalized_text, polish.lower(), 'cosine'),
                    self._text_similarity(normalized_text, polish.lower(), 'sequence'),
                    self._text_similarity(normalized_text, polish.lower(), 'combined')
                ]
                
                max_score = max(similarity_scores)
                
                # Boost score for exact matches or strong partial matches
                if normalized_text == polish.lower():
                    max_score = 1.0
                elif normalized_text in polish.lower() or polish.lower() in normalized_text:
                    max_score = max(max_score, 0.7)
                
                if max_score > best_score and max_score > threshold:
                    best_score = max_score
                    best_match = english
                    print(f"Polish mapping match: '{text}' ~ '{polish}' -> '{english}' (score: {max_score:.3f})")
        
        return best_match if best_score > threshold else None
    
    def _find_word_based_subsection_match(self, text, current_section):
        """Enhanced word-based matching for subsections"""
        best_word_match = None
        max_match_ratio = 0
        
        for subsection in self.dmp_structure.get(current_section, []):
            # Get important words from subsection and line
            subsection_words = set(word.lower() for word in re.findall(r'\w+', subsection) 
                                 if len(word) > 3 and word.lower() not in ['data', 'will', 'used', 'such', 'example', 'what', 'how', 'where', 'when'])
            line_words = set(word.lower() for word in re.findall(r'\w+', text) 
                           if len(word) > 3 and word.lower() not in ['data', 'będą', 'które', 'oraz', 'sposób', 'jakie', 'gdzie', 'kiedy'])
            
            if not subsection_words or not line_words:
                continue
            
            # Count matching words and calculate ratio
            matching_words = len(subsection_words.intersection(line_words))
            match_ratio = matching_words / max(len(subsection_words), 1)
            
            # Enhanced matching with lower threshold but require significant words
            if matching_words >= 2 and match_ratio > max_match_ratio:
                max_match_ratio = match_ratio
                best_word_match = subsection
                print(f"Word match candidate: '{text}' ~ '{subsection}' ({matching_words} words, {match_ratio:.3f} ratio)")
        
        if best_word_match and max_match_ratio > 0.12:  # Lower threshold for better coverage
            print(f"Best word match: '{text}' -> '{best_word_match}' (ratio: {max_match_ratio:.3f})")
            return best_word_match
        
        return None
    
    def _find_pdf_question_match(self, text, current_section, normalized_text):
        """Find PDF question pattern matches"""
        # Look for characteristic Polish question patterns
        question_indicators = [
            r"sposób.*?danych",
            r"jak.*?będą",
            r"jakie.*?dane",
            r"gdzie.*?przechowywane",
            r"kto.*?odpowiedzialny",
            r"środki.*?przeznaczone",
            r"metody.*?narzędzia",
            r"zgodność.*?przepisami",
            r"wyboru.*?danych",
            r"udostępnianie.*?dane"
        ]
        
        for indicator in question_indicators:
            if re.search(indicator, normalized_text, re.IGNORECASE):
                # Try to match with subsections in current section using enhanced similarity
                for subsection in self.dmp_structure.get(current_section, []):
                    similarity = self._text_similarity(normalized_text, subsection.lower(), 'combined')
                    if similarity > 0.15:  # Lower threshold for PDF questions
                        print(f"PDF question pattern match: '{text}' -> '{subsection}' (score: {similarity:.3f})")
                        return subsection
        
        return None
    
    def extract_pdf_table_content(self, text_lines):
        """Enhanced PDF text extraction with better preprocessing and structure detection"""
        # Preprocess lines to improve extraction quality
        preprocessed_lines = self._preprocess_pdf_lines(text_lines)
        
        table_content = []
        current_table = []
        in_table = False
        line_buffer = []  # Buffer to handle multi-line content
        
        for i, line in enumerate(preprocessed_lines):
            line = line.strip()
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
                    if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                        table_content.append(combined_line)
                    line_buffer = []
                continue
            
            # Enhanced table pattern detection
            is_table_line = self._is_table_line(line)
            is_form_field = self._is_form_field(line)
            is_continuation_line = self._is_continuation_line(line, preprocessed_lines, i)
            
            if is_table_line:
                if not in_table:
                    in_table = True
                    # Flush any buffered content first
                    if line_buffer:
                        combined_line = ' '.join(line_buffer).strip()
                        if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                            table_content.append(combined_line)
                        line_buffer = []
                
                current_table.append(line)
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
            elif is_continuation_line and line_buffer:
                # This line continues previous content
                line_buffer.append(line)
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
                        else:
                            # This line would contaminate the buffer, flush buffer first and add line separately
                            if line_buffer:
                                combined_line = ' '.join(line_buffer).strip()
                                if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                                    table_content.append(combined_line)
                                line_buffer = []
                            # Add current line directly since it passed individual skip test
                            table_content.append(line)
                    else:
                        table_content.append(line)
        
        # Process any remaining table
        if current_table:
            processed_table = self._process_table_rows(current_table)
            table_content.extend(processed_table)
        
        # Handle remaining buffered content
        if line_buffer:
            combined_line = ' '.join(line_buffer).strip()
            if combined_line and not self.should_skip_text(combined_line, is_pdf=True):
                table_content.append(combined_line)
        
        return self._post_process_content(table_content)
    
    def _preprocess_pdf_lines(self, text_lines):
        """Preprocess PDF text lines to improve extraction quality"""
        processed_lines = []
        
        for line in text_lines:
            # Remove excessive whitespace but preserve structure
            line = re.sub(r'\s+', ' ', line.strip())
            
            # Handle common PDF artifacts
            line = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', line)  # Control characters
            line = re.sub(r'\s*\|\s*', ' | ', line)  # Normalize table separators
            line = re.sub(r'_{5,}', '[____FIELD____]', line)  # Mark form fields
            line = re.sub(r'\.{5,}', '[....FIELD....]', line)  # Mark dotted fields
            
            if line:
                processed_lines.append(line)
        
        return processed_lines
    
    def _is_table_line(self, line):
        """Enhanced table line detection"""
        # Multiple columns separated by spaces (3+ spaces between words)
        if len(re.findall(r'\s{3,}', line)) > 1:
            return True
        
        # Currency/number patterns (budget tables)
        if re.search(r'\d+[,.]?\d*\s+(PLN|EUR|USD|zł|\d+)', line, re.IGNORECASE):
            return True
        
        # Aligned data with consistent spacing
        if re.search(r'^[^\s]+\s{4,}[^\s]+\s{4,}[^\s]+', line):
            return True
        
        # Table separators with pipes
        if line.count('|') >= 2:
            return True
        
        # Numeric data patterns (dates, IDs, etc.)
        if re.search(r'\d{2,}\s+\d{2,}\s+\d{2,}', line):
            return True
        
        return False
    
    def _is_form_field(self, line):
        """Detect form field lines"""
        # Form fields with underscores or dots
        if re.search(r'_{3,}|\.{3,}|\[____FIELD____\]|\[....FIELD....\]', line):
            return True
        
        # Checkbox patterns
        if re.search(r'\[\s*[Xx]?\s*\]\s+\w+', line):
            return True
        
        return False
    
    def _is_continuation_line(self, line, all_lines, current_index):
        """Detect if a line continues previous content"""
        # Lines that don't start with capital letter or number (likely continuation)
        if not re.match(r'^[A-ZĄĆĘŁŃÓŚŹŻ\d]', line):
            return True
        
        # Very short lines that might be fragments
        if len(line.split()) <= 3 and current_index > 0:
            prev_line = all_lines[current_index - 1].strip() if current_index > 0 else ''
            # If previous line doesn't end with punctuation, this might be continuation
            if prev_line and not re.search(r'[.!?:;]\s*$', prev_line):
                return True
        
        return False
    
    def _should_buffer_line(self, line):
        """Determine if a line should be buffered for potential combination"""
        # Lines that don't end with punctuation
        if not re.search(r'[.!?:;]\s*$', line):
            return True
        
        # Short lines that might be incomplete
        if len(line.split()) <= 5:
            return True
        
        return False
    
    def _process_form_field(self, line):
        """Process form field content"""
        # Replace field markers with placeholder text
        line = re.sub(r'\[____FIELD____\]', '[field]', line)
        line = re.sub(r'\[....FIELD....\]', '[field]', line)
        line = re.sub(r'_{3,}', '[field]', line)
        line = re.sub(r'\.{3,}', '[field]', line)
        
        return line.strip()
    
    def _post_process_content(self, content_list):
        """Post-process extracted content for better quality"""
        processed_content = []
        
        for content in content_list:
            # Skip very short or meaningless content
            if len(content.strip()) < 3:
                continue
            
            # Clean up common artifacts
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            content = re.sub(r'\|\s*\|', ' | ', content)  # Fix table separators
            content = re.sub(r'^\s*[|]\s*|\s*[|]\s*$', '', content)  # Remove leading/trailing pipes
            
            processed_content.append(content.strip())
        
        return processed_content
    
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
    
    def extract_hierarchical_content(self, all_content, is_pdf=False):
        """Hierarchical extraction based on section/subsection boundaries"""
        print(f"Starting hierarchical extraction from {len(all_content)} content items...")
        
        # Clean and preprocess content
        cleaned_content = self._clean_and_preprocess_content(all_content, is_pdf)
        
        # Find all section and subsection boundaries
        boundaries = self._find_content_boundaries(cleaned_content, is_pdf)
        
        # Extract content between boundaries
        extracted_content = self._extract_content_by_boundaries(cleaned_content, boundaries, is_pdf)
        
        return extracted_content
    
    def _clean_and_preprocess_content(self, content_list, is_pdf=False):
        """Enhanced content cleaning with better formatting preservation"""
        cleaned_content = []
        
        for item in content_list:
            if not item or not item.strip():
                continue
            
            # Remove footnotes and references first
            cleaned_item = self._remove_footnotes(item)
            
            # Remove other artifacts but preserve formatting
            cleaned_item = self._remove_text_artifacts(cleaned_item, is_pdf)
            
            # Special handling for very short content
            cleaned_stripped = cleaned_item.strip()
            
            # Keep "nie dotyczy" even if short
            if cleaned_stripped.lower() in ['nie dotyczy', 'n/a', 'not applicable', 'brak', '-']:
                cleaned_content.append('Nie dotyczy')
                continue
            
            # Skip if too short after cleaning (but keep substantial content)
            if len(cleaned_stripped) < 3:
                continue
            
            # Final cleanup and formatting
            cleaned_item = self._final_text_cleanup(cleaned_item)
            
            if cleaned_item.strip():
                cleaned_content.append(cleaned_item)
        
        print(f"Cleaned content: {len(content_list)} -> {len(cleaned_content)} items")
        return cleaned_content
    
    def _final_text_cleanup(self, text):
        """Final text cleanup and formatting"""
        # Remove excessive whitespace while preserving paragraph structure
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n[ \t]*\n', '\n\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up punctuation spacing
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([,.!?;:])([A-ZĄĆĘŁŃÓŚŹŻa-z])', r'\1 \2', text)  # Add space after punctuation
        
        # Fix common formatting issues
        text = re.sub(r'([a-ząćęłńóśźż])([A-ZĄĆĘŁŃÓŚŹŻ])', r'\1 \2', text)  # Add space between lowercase and uppercase
        
        # Ensure proper sentence endings
        if text and not text.endswith(('.', '!', '?', ':')):
            text = text.rstrip() + '.'
        
        return text.strip()
    
    def _remove_footnotes(self, text):
        """Enhanced footnote removal with improved patterns"""
        original_text = text
        
        # Remove footnote numbers (superscript style)
        text = re.sub(r'\^\d+|\[\d+\]|\(\d+\)', '', text)
        
        # Remove footnote references at end of sentences
        text = re.sub(r'\d+\s*$', '', text)
        text = re.sub(r'\s+\d+\s*$', '', text)  # Also with spaces
        
        # Remove common footnote patterns
        text = re.sub(r'\b(see|por\.|cf\.|ibid\.|op\.\s*cit\.)\s*\d+', '', text, re.IGNORECASE)
        
        # Remove bibliography references in brackets
        text = re.sub(r'\[[^\]]*\d{4}[^\]]*\]', '', text)
        
        # Remove author-year citations
        text = re.sub(r'\([A-Za-z]+[^\)]*\d{4}[^\)]*\)', '', text)
        
        # Enhanced Polish footnote patterns
        text = re.sub(r'\b(zob\.|patrz|por\.|tamże|ibidem)\s*\d+', '', text, re.IGNORECASE)
        
        # Remove numbered footnotes at the end of words (e.g., "stored15 in")
        text = re.sub(r'([a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ])\d+(\s)', r'\1\2', text)
        
        # Remove standalone numbers that look like footnote references
        text = re.sub(r'\s+\d{1,2}\s+', ' ', text)
        
        # Remove multiple footnote patterns like [1,2,3]
        text = re.sub(r'\[[\d,\s]+\]', '', text)
        
        # Remove footnotes with specific patterns like "1)" or "(1)"
        text = re.sub(r'\(\d+\)|\d+\)', '', text)
        
        # Remove numbered footnotes in format "1,2,3"
        text = re.sub(r'\d+(,\d+)*(?=\s|$)', '', text)
        
        # Remove DOI and URL patterns that might be footnotes
        text = re.sub(r'(doi:|http[s]?://)[^\s]+', '', text, re.IGNORECASE)
        
        # Clean up excessive spaces created by footnote removal
        text = re.sub(r'\s{2,}', ' ', text)
        
        return text.strip()
    
    def _remove_text_artifacts(self, text, is_pdf=False):
        """Enhanced text artifact removal with improved header/footer cleaning"""
        original_text = text
        
        # Remove excessive whitespace but preserve single spaces
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Preserve paragraph breaks
        
        # Enhanced header/footer removal patterns
        text = self._remove_headers_footers(text, is_pdf)
        
        # Handle bullet points - preserve but normalize them
        text = self._normalize_bullet_points(text)
        
        # Remove table artifacts
        text = re.sub(r'\|\s*\|', ' ', text)
        text = re.sub(r'^\s*\|', '', text, flags=re.MULTILINE)
        text = re.sub(r'\|\s*$', '', text, flags=re.MULTILINE)
        
        # Remove form field markers
        text = re.sub(r'\[field\]|\[____FIELD____\]|\[....FIELD....\]', '', text)
        text = re.sub(r'_{3,}|\.{3,}', '', text)
        
        # Clean up formatting markers from our processing
        text = re.sub(r'^(BOLD:|UNDERLINED:|UNDERLINED_BOLD:)', '', text).strip()
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{4,}', '...', text)  # Keep ... but remove longer sequences
        text = re.sub(r'[-]{4,}', '---', text)  # Keep --- but remove longer sequences
        
        # Handle "nie dotyczy" cases
        text = self._handle_nie_dotyczy(text)
        
        return text.strip()
    
    def _normalize_bullet_points(self, text):
        """Normalize bullet points to consistent format"""
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                processed_lines.append('')
                continue
            
            # Detect and normalize bullet points
            bullet_patterns = [
                r'^[\s]*([•·▪▫■□▲▼→←])\s+(.+)$',  # Unicode bullets
                r'^[\s]*[-*+]\s+(.+)$',  # ASCII bullets
                r'^[\s]*[\d]+[.):]\s+(.+)$',  # Numbered lists
                r'^[\s]*[a-zA-Z][.):]\s+(.+)$',  # Letter lists
                r'^[\s]*[ivxlcdm]+[.):]\s+(.+)$',  # Roman numerals
            ]
            
            is_bullet = False
            for pattern in bullet_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Normalize to consistent bullet format
                    if len(match.groups()) == 2:  # Unicode bullet with captured bullet and text
                        content = match.group(2)
                    else:  # Other patterns with just content
                        content = match.group(1)
                    
                    processed_lines.append(f'• {content}')
                    is_bullet = True
                    break
            
            if not is_bullet:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _remove_headers_footers(self, text, is_pdf=False):
        """Enhanced header and footer removal"""
        lines = text.split('\n')
        cleaned_lines = []
        
        # Common header/footer patterns (case-insensitive)
        header_footer_patterns = [
            r'^\s*strona\s+\d+\s*$',  # "strona X"
            r'^\s*page\s+\d+\s*$',   # "page X"
            r'^\s*\d+\s*/\s*\d+\s*$',  # "X / Y"
            r'^\s*\d+\s*$',          # standalone numbers
            r'^\s*data\s*management\s*plan\s*$',  # DMP title repeats
            r'^\s*plan\s*zarządzania\s*danymi\s*$',
            r'^\s*(politechnika|university|gdansk|gdańsk).*$',  # institution names
            r'^\s*\d{2}/\d{2}/\d{4}\s*$',  # dates
            r'^\s*\d{4}-\d{2}-\d{2}\s*$',  # ISO dates
            r'^\s*(draft|wersja|version).*$',  # version info
            r'^\s*confidential\s*$',
            r'^\s*poufne\s*$',
            r'^\s*(©|copyright).*$',  # copyright info
        ]
        
        for line in lines:
            line_clean = line.strip()
            
            # Skip very short lines that are likely artifacts
            if len(line_clean) <= 2:
                continue
                
            # Check if line matches header/footer patterns
            is_header_footer = False
            for pattern in header_footer_patterns:
                if re.match(pattern, line_clean, re.IGNORECASE):
                    is_header_footer = True
                    break
            
            # Skip repeated institutional info or common document headers
            if any(keyword in line_clean.lower() for keyword in [
                'politechnika gdańska', 'gdansk university', 'pg.edu.pl',
                'data management plan template', 'szablon planu zarządzania'
            ]):
                is_header_footer = True
            
            if not is_header_footer:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _handle_nie_dotyczy(self, text):
        """Handle 'nie dotyczy' cases appropriately"""
        # Clean the text first
        clean_text = re.sub(r'\s+', ' ', text.strip()).lower()
        
        # Patterns that indicate "nie dotyczy" or "not applicable"
        nie_dotyczy_patterns = [
            r'^\s*nie\s+dotyczy\s*[.]?\s*$',
            r'^\s*n/?a\s*[.]?\s*$',
            r'^\s*not\s+applicable\s*[.]?\s*$',
            r'^\s*brak\s*[.]?\s*$',
            r'^\s*-\s*$',
            r'^\s*nie\s*[.]?\s*$'
        ]
        
        for pattern in nie_dotyczy_patterns:
            if re.match(pattern, clean_text):
                return 'Nie dotyczy'  # Standardized format
        
        # Check if the content is mostly "nie dotyczy" with some artifacts
        if 'nie dotyczy' in clean_text and len(clean_text) < 20:
            return 'Nie dotyczy'
        
        return text
    
    def _find_content_boundaries(self, content_list, is_pdf=False):
        """Find all section and subsection boundaries in content with improved confidence thresholds"""
        boundaries = []
        
        for i, content_item in enumerate(content_list):
            # Check for section with higher confidence threshold
            section_confidence = self._calculate_section_confidence(content_item, is_pdf)
            if section_confidence['section'] and section_confidence['score'] > 0.7:  # Higher threshold for sections
                boundaries.append({
                    'index': i,
                    'type': 'section',
                    'title': section_confidence['section'],
                    'original_text': content_item,
                    'level': 1,
                    'confidence': section_confidence['score']
                })
                print(f"Found section boundary at {i}: {section_confidence['section']} (confidence: {section_confidence['score']:.3f})")
                continue
            
            # Check for subsection with improved logic
            subsection_match = self._find_best_subsection_boundary(content_item, is_pdf)
            if subsection_match and subsection_match['confidence'] > 0.5:  # Higher threshold for subsections
                boundaries.append({
                    'index': i,
                    'type': 'subsection',
                    'section': subsection_match['section'],
                    'title': subsection_match['subsection'],
                    'original_text': content_item,
                    'level': 2,
                    'confidence': subsection_match['confidence']
                })
                print(f"Found subsection boundary at {i}: {subsection_match['subsection']} (confidence: {subsection_match['confidence']:.3f})")
        
        # Sort boundaries by index
        boundaries.sort(key=lambda x: x['index'])
        
        # Assign parent sections to subsections
        current_section = None
        for boundary in boundaries:
            if boundary['type'] == 'section':
                current_section = boundary['title']
            elif boundary['type'] == 'subsection' and current_section:
                boundary['parent_section'] = current_section
        
        print(f"Found {len(boundaries)} boundaries: {len([b for b in boundaries if b['type'] == 'section'])} sections, {len([b for b in boundaries if b['type'] == 'subsection'])} subsections")
        return boundaries
    
    def _calculate_section_confidence(self, text, is_pdf=False):
        """Calculate confidence for section detection with improved Polish support"""
        # Check for numbered section patterns first (highest confidence)
        # Must be EXACTLY "X. " format, not "X.X" (that's a subsection)
        section_match = re.match(r'^\s*(\d+)\.\s+([^\d].*?)$', text)
        if section_match:
            section_num = section_match.group(1)
            section_title = section_match.group(2).strip()
            
            # Exclude if it looks like a subsection (contains another number)
            if re.search(r'\d+\.\d+', text):
                return {'section': None, 'score': 0.0}
            
            # Direct match with DMP structure
            for section in self.dmp_structure:
                if section.startswith(f"{section_num}."):
                    return {'section': section, 'score': 0.95}  # Very high confidence
            
            # Check Polish-English mapping with improved matching
            for polish, english in self.section_mapping.items():
                similarity = self._text_similarity(polish.lower(), section_title.lower(), 'combined')
                if similarity > 0.4:  # Lower threshold, let combined score decide
                    return {'section': english, 'score': 0.85}
        
        # Check for formatted section titles (BOLD, UNDERLINED)
        if any(text.startswith(prefix) for prefix in ['BOLD:', 'UNDERLINED:', 'UNDERLINED_BOLD:']):
            clean_text = re.sub(r'^(BOLD:|UNDERLINED:|UNDERLINED_BOLD:)', '', text).strip()
            return self._calculate_section_confidence(clean_text, is_pdf)  # Recursive call on clean text
        
        # Direct section name matching (lower confidence) - only for very high similarity
        best_match = self._find_best_section_match(text, threshold=0.8)  # Higher threshold
        if best_match:
            return {'section': best_match, 'score': 0.7}
        
        return {'section': None, 'score': 0.0}
    
    def _find_best_subsection_boundary(self, text, is_pdf=False):
        """Find best subsection boundary with improved Polish pattern recognition"""
        # More lenient check for subsection titles to catch more content
        if not self._looks_like_subsection_title(text) and len(text.strip()) < 10:
            return None
        
        # Special handling for numbered subsections (1.1, 1.2, etc.)
        numbered_match = re.match(r'^\s*(\d+)\.(\d+)[.\s]*(.+)', text)
        if numbered_match:
            section_num = int(numbered_match.group(1))
            subsection_num = int(numbered_match.group(2))
            subsection_text = numbered_match.group(3).strip()
            
            # Map to correct section based on section number
            target_section = None
            for section in self.dmp_structure:
                if section.startswith(f"{section_num}."):
                    target_section = section
                    break
            
            if target_section:
                # Try to match with subsections in that section using Polish mapping
                best_polish_match = None
                best_score = 0
                
                for polish, english in self.subsection_mapping.items():
                    if english in self.dmp_structure.get(target_section, []):
                        # Try different matching strategies
                        scores = [
                            self._text_similarity(subsection_text.lower(), polish.lower(), 'combined'),
                            self._text_similarity(text.lower(), polish.lower(), 'combined'),
                            # Check if key words match
                            self._calculate_keyword_similarity(subsection_text.lower(), polish.lower())
                        ]
                        max_score = max(scores)
                        
                        if max_score > best_score:
                            best_score = max_score
                            best_polish_match = english
                
                if best_polish_match and best_score > 0.3:
                    confidence = 0.8 + best_score * 0.2  # High confidence for numbered items
                    return {
                        'section': target_section,
                        'subsection': best_polish_match,
                        'confidence': confidence,
                        'similarity': best_score
                    }
        
        # Enhanced Polish subsection detection for non-numbered titles
        enhanced_match = self._detect_polish_subsection_patterns(text)
        if enhanced_match:
            return enhanced_match
        
        # Fallback to general matching
        potential_matches = []
        
        for section in self.dmp_structure:
            for subsection in self.dmp_structure[section]:
                # Direct similarity check
                similarity = self._text_similarity(text.lower(), subsection.lower(), 'combined')
                
                # Check Polish mapping with improved matching
                for polish, english in self.subsection_mapping.items():
                    if english == subsection:
                        polish_similarity = self._text_similarity(text.lower(), polish.lower(), 'combined')
                        keyword_similarity = self._calculate_keyword_similarity(text.lower(), polish.lower())
                        similarity = max(similarity, polish_similarity, keyword_similarity)
                
                if similarity > 0.25:  # Lower base threshold for better coverage
                    confidence = self._calculate_subsection_confidence(text, section, subsection)
                    potential_matches.append({
                        'section': section,
                        'subsection': subsection,
                        'confidence': confidence,
                        'similarity': similarity
                    })
        
        if potential_matches:
            # Return the best match
            best_match = max(potential_matches, key=lambda x: x['confidence'])
            if best_match['confidence'] > 0.35:  # Lower threshold for better coverage
                return best_match
        
        return None
    
    def _detect_polish_subsection_patterns(self, text):
        """Enhanced detection of Polish subsection patterns"""
        text_lower = text.lower()
        
        # Define enhanced Polish subsection patterns with their English mappings
        enhanced_patterns = [
            # Section 1 patterns
            {
                'patterns': ['sposób pozyskiwania', 'pozyskiwania i opracowywania', 'wykorzystania dostępnych'],
                'section': '1. Data description and collection or re-use of existing data',
                'subsection': 'How will new data be collected or produced and/or how will existing data be re-used?'
            },
            {
                'patterns': ['pozyskiwane lub opracowywane dane', 'rodzaj, format, ilość', 'dane (np. rodzaj'],
                'section': '1. Data description and collection or re-use of existing data', 
                'subsection': 'What data (for example the types, formats, and volumes) will be collected or produced?'
            },
            # Section 2 patterns
            {
                'patterns': ['metadane i dokumenty', 'metodologia lub pozyskiwanie', 'towarzyszące danym'],
                'section': '2. Documentation and data quality',
                'subsection': 'What metadata and documentation (for example methodology or data collection and way of organising data) will accompany data?'
            },
            {
                'patterns': ['stosowane środki kontroli', 'kontroli jakości danych', 'środki kontroli'],
                'section': '2. Documentation and data quality',
                'subsection': 'What data quality control measures will be used?'
            },
            # Section 3 patterns
            {
                'patterns': ['przechowywanie i tworzenie kopii', 'kopii zapasowych danych', 'metadanych podczas'],
                'section': '3. Storage and backup during the research process',
                'subsection': 'How will data and metadata be stored and backed up during the research process?'
            },
            {
                'patterns': ['sposób zapewnienia bezpieczeństwa', 'ochrony danych wrażliwych', 'bezpieczeństwa danych'],
                'section': '3. Storage and backup during the research process',
                'subsection': 'How will data security and protection of sensitive data be taken care of during the research?'
            },
            # Section 4 patterns
            {
                'patterns': ['zgodności z przepisami', 'danych osobowych i bezpieczeństwa', 'przepisami dotyczącymi'],
                'section': '4. Legal requirements, codes of conduct',
                'subsection': 'If personal data are processed, how will compliance with legislation on personal data and on data security be ensured?'
            },
            {
                'patterns': ['zarządzania innymi kwestiami', 'własnością intelektualną', 'kwestiami prawnymi'],
                'section': '4. Legal requirements, codes of conduct',
                'subsection': 'How will other legal issues, such as intelectual property rights and ownership, be managed? What legislation is applicable?'
            },
            # Section 5 patterns
            {
                'patterns': ['sposób i termin udostępnienia', 'udostępnienia danych', 'ograniczenia w udostępnianiu'],
                'section': '5. Data sharing and long-term preservation',
                'subsection': 'How and when will data be shared? Are there possible restrictions to data sharing or embargo reasons?'
            },
            {
                'patterns': ['wyboru danych przeznaczonych', 'długotrwałego przechowywania', 'repozytorium lub archiwum'],
                'section': '5. Data sharing and long-term preservation',
                'subsection': 'How will data for preservation be selected, and where will data be preserved long-term (for example a data repository or archive)?'
            },
            {
                'patterns': ['metody lub narzędzia programowe', 'dostęp do danych i korzystanie', 'narzędzia umożliwiające'],
                'section': '5. Data sharing and long-term preservation',
                'subsection': 'What methods or software tools will be needed to access and use the data?'
            },
            {
                'patterns': ['unikalnego i trwałego identyfikatora', 'identyfikatora (doi)', 'sposób zapewniający stosowanie'],
                'section': '5. Data sharing and long-term preservation',
                'subsection': 'How will the application of a unique and persistent identifier (such us a Digital Object Identifier (DOI)) to each data set be ensured?'
            },
            # Section 6 patterns
            {
                'patterns': ['osoba odpowiedzialna', 'odpowiedzialna za zarządzanie', 'data steward'],
                'section': '6. Data management responsibilities and resources',
                'subsection': 'Who (for example role, position, and institution) will be responsible for data management (i.e the data steward)?'
            },
            {
                'patterns': ['środki przeznaczone', 'finansowe i czasowe', 'zarządzania danymi i zapewnienia'],
                'section': '6. Data management responsibilities and resources',
                'subsection': 'What resources (for example financial and time) will be dedicated to data management and ensuring the data will be FAIR (Findable, Accessible, Interoperable, Re-usable)?'
            }
        ]
        
        # Find the best matching pattern
        best_match = None
        best_score = 0
        
        for pattern_def in enhanced_patterns:
            # Check how many patterns match
            pattern_matches = 0
            for pattern in pattern_def['patterns']:
                if pattern in text_lower:
                    pattern_matches += 1
            
            # Calculate match score
            match_score = pattern_matches / len(pattern_def['patterns'])
            
            # Also check overall similarity
            similarity_score = self._text_similarity(text_lower, ' '.join(pattern_def['patterns']), 'combined')
            
            # Combined score
            combined_score = (match_score * 0.7) + (similarity_score * 0.3)
            
            if combined_score > best_score and pattern_matches > 0:
                best_score = combined_score
                best_match = pattern_def
        
        if best_match and best_score > 0.3:
            confidence = 0.6 + (best_score * 0.3)  # Good confidence for pattern matches
            return {
                'section': best_match['section'],
                'subsection': best_match['subsection'],
                'confidence': confidence,
                'similarity': best_score
            }
        
        return None
    
    def _calculate_keyword_similarity(self, text1, text2):
        """Calculate similarity based on key words matching"""
        # Extract key words (longer than 4 characters, not common words)
        common_words = {'będą', 'dane', 'oraz', 'sposób', 'które', 'jako', 'przez', 'zostanie', 'będzie', 'jakie'}
        
        words1 = set(word for word in re.findall(r'\w+', text1.lower()) 
                    if len(word) > 4 and word not in common_words)
        words2 = set(word for word in re.findall(r'\w+', text2.lower()) 
                    if len(word) > 4 and word not in common_words)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _looks_like_subsection_title(self, text):
        """Determine if text looks like a subsection title with improved Polish support"""
        # Remove formatting markers
        clean_text = re.sub(r'^(BOLD:|UNDERLINED:|UNDERLINED_BOLD:)', '', text).strip()
        
        # PRIORITY 1: Check for numbered subsection patterns (e.g., "1.1", "2.3") - HIGHEST PRIORITY
        if re.match(r'^\s*\d+\.\d+[^\d]', clean_text):  # Must have something after the number
            return True
        
        # PRIORITY 2: Check for exact matches with known Polish subsection patterns
        polish_subsection_starters = [
            'sposób pozyskiwania',
            'pozyskiwane lub opracowywane dane', 
            'metadane i dokumenty',
            'stosowane środki kontroli',
            'przechowywanie i tworzenie kopii',
            'sposób zapewnienia bezpieczeństwa',
            'sposób zapewnienia zgodności',
            'sposób zarządzania innymi kwestiami',
            'sposób i termin udostępnienia',
            'sposób wyboru danych',
            'metody lub narzędzia programowe',
            'sposób zapewniający stosowanie',
            'osoba odpowiedzialna',
            'środki przeznaczone'
        ]
        
        clean_lower = clean_text.lower()
        for starter in polish_subsection_starters:
            if clean_lower.startswith(starter):
                return True
        
        # PRIORITY 3: Check for question patterns
        if '?' in clean_text:
            return True
        
        # PRIORITY 4: Check for characteristic question words
        question_words = ['how', 'what', 'where', 'when', 'who', 'which', 'why', 'will',
                         'jak', 'co', 'gdzie', 'kiedy', 'kto', 'który', 'dlaczego', 'czy', 'sposób']
        if any(word in clean_lower for word in question_words):
            # Additional check: must be reasonably long to be a real subsection
            if len(clean_text.split()) >= 4:
                return True
        
        # PRIORITY 5: Check if it's formatted as a title (BOLD/UNDERLINED)
        if any(text.startswith(prefix) for prefix in ['BOLD:', 'UNDERLINED:', 'UNDERLINED_BOLD:']):
            if len(clean_text.split()) >= 4:
                return True
        
        # PRIORITY 6: Length-based check for very long titles that might be subsections
        if len(clean_text.split()) >= 8:  # At least 8 words - likely a subsection
            return True
        
        return False
    
    def _calculate_subsection_confidence(self, text, section, subsection):
        """Calculate confidence score for subsection detection"""
        # Base similarity score
        confidence = self._text_similarity(text.lower(), subsection.lower(), 'combined')
        
        # Boost for formatting indicators
        if any(text.startswith(prefix) for prefix in ['BOLD:', 'UNDERLINED:', 'UNDERLINED_BOLD:']):
            confidence += 0.2
        
        # Boost for question-like patterns
        if '?' in text or any(word in text.lower() for word in ['how', 'what', 'where', 'when', 'who', 'jak', 'co', 'gdzie', 'kiedy', 'kto']):
            confidence += 0.1
        
        # Boost for numbered patterns
        if re.match(r'^\s*\d+\.\d+', text):
            confidence += 0.1
        
        return confidence
    
    def _extract_content_by_boundaries(self, content_list, boundaries, is_pdf=False):
        """Extract content between boundaries"""
        extracted_content = {
            'sections': {},
            'unassigned': [],
            'metadata': {
                'total_items': len(content_list),
                'boundaries_found': len(boundaries),
                'extraction_method': 'hierarchical_boundary_based'
            }
        }
        
        # Initialize section structure
        for section in self.dmp_structure:
            extracted_content['sections'][section] = {}
            for subsection in self.dmp_structure[section]:
                extracted_content['sections'][section][subsection] = {
                    'content': [],
                    'raw_text': '',
                    'found': False
                }
        # Process each boundary and extract content to next boundary
        for i, boundary in enumerate(boundaries):
            start_index = boundary['index'] + 1  # Start after the boundary title
            
            # Find end index (next boundary or end of content)
            end_index = len(content_list)
            if i + 1 < len(boundaries):
                end_index = boundaries[i + 1]['index']
            
            # Extract content between boundaries
            section_content = content_list[start_index:end_index]
            
            # Clean each content item more thoroughly
            cleaned_content = []
            for item in section_content:
                if not item or len(item.strip()) <= 2:
                    continue
                    
                cleaned_item = self._clean_content_item(item.strip())
                # Accept "nie dotyczy" even if short
                if cleaned_item and (len(cleaned_item) > 5 or self._is_nie_dotyczy(cleaned_item)):
                    cleaned_content.append(cleaned_item)
            
            section_content = cleaned_content
            
            if boundary['type'] == 'section':
                # For sections without specific subsections, assign to first subsection
                section_name = boundary['title']
                if section_name in self.dmp_structure and self.dmp_structure[section_name]:
                    first_subsection = self.dmp_structure[section_name][0]
                    self._assign_boundary_content(extracted_content, section_name, first_subsection, section_content, boundary)
            
            elif boundary['type'] == 'subsection':
                # Get parent section
                parent_section = boundary.get('parent_section')
                if not parent_section:
                    # Try to infer from detected section/subsection mapping
                    for section in self.dmp_structure:
                        if boundary['title'] in self.dmp_structure[section]:
                            parent_section = section
                            break
                
                if parent_section:
                    self._assign_boundary_content(extracted_content, parent_section, boundary['title'], section_content, boundary)
                else:
                    print(f"Warning: Could not determine parent section for subsection: {boundary['title']}")
        
        # Handle "nie dotyczy" cases - assign to previous subsection
        self._handle_nie_dotyczy_assignments(extracted_content, content_list)
        
        # Handle content before first boundary
        if boundaries:
            pre_boundary_content = content_list[:boundaries[0]['index']]
            if pre_boundary_content:
                print(f"Found {len(pre_boundary_content)} items before first boundary")
                extracted_content['unassigned'].extend([{
                    'text': item,
                    'type': 'pre_boundary',
                    'position': i
                } for i, item in enumerate(pre_boundary_content)])
        else:
            # No boundaries found - all content is unassigned
            extracted_content['unassigned'].extend([{
                'text': item,
                'type': 'no_boundaries',
                'position': i
            } for i, item in enumerate(content_list)])
        
        return extracted_content
    
    def _clean_content_item(self, item):
        """Additional cleaning for individual content items"""
        if not item:
            return ''
        
        # Remove remaining artifacts
        item = re.sub(r'^[\s\-_\.]+|[\s\-_\.]+$', '', item)  # Leading/trailing artifacts
        item = re.sub(r'\s{2,}', ' ', item)  # Multiple spaces
        
        # Skip if it's just formatting artifacts
        if re.match(r'^[\s\-_\.\|]+$', item):
            return ''
        
        # Skip typical header/footer content
        skip_patterns = [
            r'^\d+\s*$',  # Just a number
            r'^\d+\s*/\s*\d+$',  # Page numbers
            r'^strona\s+\d+$',  # Polish page indicator
            r'^page\s+\d+$',   # English page indicator
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, item.strip(), re.IGNORECASE):
                return ''
        
        return item.strip()
    
    def _is_nie_dotyczy(self, text):
        """Check if text represents 'nie dotyczy' (not applicable)"""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        nie_dotyczy_variants = [
            'nie dotyczy', 'nie dotyczy.', 'nieDotyczy',
            'n/a', 'not applicable', 'not applicable.', 
            'brak', 'brak.', '-', '—', '–'
        ]
        
        return text_lower in nie_dotyczy_variants or text_lower == 'nie dotyczy'
    
    def _handle_nie_dotyczy_assignments(self, extracted_content, content_list):
        """Handle special case where 'nie dotyczy' should be assigned to previous subsection"""
        # Find all 'nie dotyczy' items in content
        for i, item in enumerate(content_list):
            if self._is_nie_dotyczy(item.strip()):
                # Find the previous subsection that was assigned
                previous_subsection = self._find_previous_assigned_subsection(extracted_content, i)
                if previous_subsection:
                    section, subsection = previous_subsection
                    # Add "nie dotyczy" to that subsection
                    current_content = extracted_content['sections'][section][subsection]['content']
                    if 'Nie dotyczy' not in current_content:
                        current_content.append('Nie dotyczy')
                        extracted_content['sections'][section][subsection]['raw_text'] += ' Nie dotyczy'
                        print(f"Added 'Nie dotyczy' to {section} -> {subsection}")
    
    def _find_previous_assigned_subsection(self, extracted_content, current_index):
        """Find the most recently assigned subsection before current_index"""
        # This is a simplified approach - in practice you might want to track 
        # the order of processing better
        for section in extracted_content['sections']:
            for subsection in extracted_content['sections'][section]:
                if extracted_content['sections'][section][subsection]['found']:
                    return (section, subsection)
        return None
    
    def _assign_boundary_content(self, extracted_content, section, subsection, content_items, boundary):
        """Assign content items to a section/subsection"""
        if section not in extracted_content['sections']:
            print(f"Warning: Section '{section}' not found in structure")
            return
        
        if subsection not in extracted_content['sections'][section]:
            print(f"Warning: Subsection '{subsection}' not found in section '{section}'")
            return
        
        # Clean and filter content
        cleaned_items = []
        for item in content_items:
            cleaned_item = item.strip()
            if cleaned_item and len(cleaned_item) > 3:
                cleaned_items.append(cleaned_item)
        
        if cleaned_items:
            extracted_content['sections'][section][subsection]['content'] = cleaned_items
            extracted_content['sections'][section][subsection]['raw_text'] = ' '.join(cleaned_items)
            extracted_content['sections'][section][subsection]['found'] = True
            print(f"Assigned {len(cleaned_items)} items to {section} -> {subsection}")
        
        # Store boundary metadata
        extracted_content['sections'][section][subsection]['boundary_info'] = {
            'original_text': boundary['original_text'],
            'confidence': boundary.get('confidence', 0),
            'detection_type': boundary['type']
        }
    
    def improve_content_assignment(self, all_content, is_pdf=False):
        """Legacy method - now calls hierarchical extraction and converts format"""
        # Use new hierarchical extraction
        hierarchical_result = self.extract_hierarchical_content(all_content, is_pdf)
        
        # Convert to legacy format for compatibility
        section_content = {}
        tagged_content = {}
        unconnected_text = []
        
        # Initialize structures
        for section in self.dmp_structure:
            section_content[section] = {}
            tagged_content[section] = {}
            for subsection in self.dmp_structure[section]:
                section_content[section][subsection] = []
                tagged_content[section][subsection] = []
        
        # Fill from hierarchical results
        for section in hierarchical_result['sections']:
            for subsection in hierarchical_result['sections'][section]:
                subsection_data = hierarchical_result['sections'][section][subsection]
                if subsection_data['found']:
                    section_content[section][subsection] = subsection_data['content']
                    # Create tagged content
                    for content_item in subsection_data['content']:
                        tagged_content[section][subsection].append(self.process_paragraph(content_item))
        
        # Add unassigned content to unconnected_text
        for item in hierarchical_result['unassigned']:
            unconnected_text.append(item)
        
        return section_content, tagged_content, unconnected_text
    
    def _recover_orphaned_content(self, orphaned_content, section_content, tagged_content):
        """Attempt to recover orphaned content using various strategies"""
        recovered_items = []
        
        print(f"\n=== Content Recovery Phase: {len(orphaned_content)} items to recover ===")
        
        for item in orphaned_content:
            content_text = item['text']
            recovery_attempts = []
            
            # Strategy 1: Contextual analysis - look for keywords that suggest section/subsection
            context_match = self._analyze_content_context(content_text)
            recovery_attempts.append(f"Context analysis: {context_match}")
            
            if context_match:
                recovered_items.append({
                    'text': content_text,
                    'section': context_match['section'],
                    'subsection': context_match['subsection'],
                    'recovered': True,
                    'method': 'context_analysis',
                    'attempts': recovery_attempts
                })
                continue
            
            # Strategy 2: Semantic similarity with existing content
            similarity_match = self._find_similar_content_placement(content_text, section_content)
            recovery_attempts.append(f"Similarity match: {similarity_match}")
            
            if similarity_match:
                recovered_items.append({
                    'text': content_text,
                    'section': similarity_match['section'],
                    'subsection': similarity_match['subsection'],
                    'recovered': True,
                    'method': 'similarity_matching',
                    'attempts': recovery_attempts
                })
                continue
            
            # Strategy 3: Pattern-based assignment (fallback)
            pattern_match = self._assign_by_content_patterns(content_text)
            recovery_attempts.append(f"Pattern match: {pattern_match}")
            
            if pattern_match:
                recovered_items.append({
                    'text': content_text,
                    'section': pattern_match['section'],
                    'subsection': pattern_match['subsection'],
                    'recovered': True,
                    'method': 'pattern_matching',
                    'attempts': recovery_attempts
                })
                continue
            
            # No recovery possible
            recovered_items.append({
                'text': content_text,
                'recovered': False,
                'type': item.get('type', 'unrecoverable'),
                'attempts': recovery_attempts
            })
        
        recovery_stats = {
            'total': len(orphaned_content),
            'recovered': len([r for r in recovered_items if r.get('recovered')]),
            'unrecovered': len([r for r in recovered_items if not r.get('recovered')])
        }
        print(f"Recovery stats: {recovery_stats['recovered']}/{recovery_stats['total']} items recovered")
        
        return recovered_items
    
    def _analyze_content_context(self, content_text):
        """Analyze content for contextual clues about section/subsection"""
        # Define keyword patterns for different sections
        section_keywords = {
            "1. Data description and collection or re-use of existing data": [
                ['collect', 'collection', 'data', 'source', 'acquire', 'obtain'],
                ['type', 'format', 'volume', 'amount', 'size', 'dataset']
            ],
            "2. Documentation and data quality": [
                ['metadata', 'documentation', 'document', 'standard', 'schema'],
                ['quality', 'validation', 'check', 'verify', 'control', 'measure']
            ],
            "3. Storage and backup during the research process": [
                ['storage', 'store', 'backup', 'save', 'preserve', 'keep'],
                ['security', 'protection', 'encrypt', 'access', 'safe', 'secure']
            ],
            "4. Legal requirements, codes of conduct": [
                ['legal', 'law', 'regulation', 'compliance', 'gdpr', 'personal'],
                ['intellectual', 'property', 'copyright', 'license', 'ownership', 'rights']
            ],
            "5. Data sharing and long-term preservation": [
                ['share', 'sharing', 'publish', 'repository', 'archive', 'preserve'],
                ['identifier', 'doi', 'persistent', 'access', 'method', 'tool']
            ],
            "6. Data management responsibilities and resources": [
                ['responsible', 'responsibility', 'steward', 'manager', 'role'],
                ['resource', 'cost', 'budget', 'time', 'staff', 'fair']
            ]
        }
        
        content_lower = content_text.lower()
        best_section = None
        best_subsection = None
        best_score = 0
        
        for section, keyword_groups in section_keywords.items():
            section_score = 0
            
            # Check each subsection's keywords
            for i, subsection in enumerate(self.dmp_structure.get(section, [])):
                subsection_score = 0
                
                if i < len(keyword_groups):
                    keywords = keyword_groups[i]
                    for keyword in keywords:
                        if keyword in content_lower:
                            subsection_score += 1
                
                if subsection_score > best_score:
                    best_score = subsection_score
                    best_section = section
                    best_subsection = subsection
        
        if best_score >= 2:  # Require at least 2 keyword matches
            return {
                'section': best_section,
                'subsection': best_subsection,
                'score': best_score
            }
        
        return None
    
    def _find_similar_content_placement(self, content_text, section_content):
        """Find placement based on similarity to existing content"""
        best_section = None
        best_subsection = None
        best_similarity = 0
        
        for section, subsections in section_content.items():
            for subsection, content_list in subsections.items():
                if content_list:  # Only check sections with existing content
                    # Calculate average similarity to existing content
                    similarities = []
                    for existing_content in content_list[:5]:  # Check up to 5 items
                        sim = self._text_similarity(content_text.lower(), existing_content.lower(), 'combined')
                        similarities.append(sim)
                    
                    if similarities:
                        avg_similarity = sum(similarities) / len(similarities)
                        if avg_similarity > best_similarity and avg_similarity > 0.3:
                            best_similarity = avg_similarity
                            best_section = section
                            best_subsection = subsection
        
        if best_section:
            return {
                'section': best_section,
                'subsection': best_subsection,
                'similarity': best_similarity
            }
        
        return None
    
    def _assign_by_content_patterns(self, content_text):
        """Assign content based on common patterns"""
        # Define common patterns for different subsections
        pattern_mappings = [
            {
                'patterns': [r'\b(survey|questionnaire|interview|experiment)\b', r'\b(collect|gather|obtain)\b.*\bdata\b'],
                'section': "1. Data description and collection or re-use of existing data",
                'subsection': "How will new data be collected or produced and/or how will existing data be re-used?"
            },
            {
                'patterns': [r'\b(csv|json|xml|excel|database)\b', r'\b(format|type|volume)\b.*\bdata\b'],
                'section': "1. Data description and collection or re-use of existing data",
                'subsection': "What data (for example the types, formats, and volumes) will be collected or produced?"
            },
            {
                'patterns': [r'\b(backup|storage|server|cloud)\b', r'\bstore\b.*\bdata\b'],
                'section': "3. Storage and backup during the research process",
                'subsection': "How will data and metadata be stored and backed up during the research process?"
            },
            {
                'patterns': [r'\b(gdpr|privacy|personal|consent)\b', r'\b(legal|compliance|regulation)\b'],
                'section': "4. Legal requirements, codes of conduct",
                'subsection': "If personal data are processed, how will compliance with legislation on personal data and on data security be ensured?"
            },
            {
                'patterns': [r'\b(repository|archive|zenodo|figshare)\b', r'\b(publish|share|public)\b.*\bdata\b'],
                'section': "5. Data sharing and long-term preservation",
                'subsection': "How will data for preservation be selected, and where will data be preserved long-term (for example a data repository or archive)?"
            }
        ]
        
        content_lower = content_text.lower()
        
        for mapping in pattern_mappings:
            pattern_matches = 0
            for pattern in mapping['patterns']:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    pattern_matches += 1
            
            if pattern_matches >= 1:  # At least one pattern match
                return {
                    'section': mapping['section'],
                    'subsection': mapping['subsection'],
                    'matches': pattern_matches
                }
        
        return None
    
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
    
    def _filter_pdf_content_quality(self, content_list):
        """Filter and improve PDF content quality"""
        filtered_content = []
        
        for content in content_list:
            # Skip very short content
            if len(content.strip()) < 5:
                continue
            
            # Skip content that's mostly numbers or symbols
            text_chars = len(re.findall(r'[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', content))
            if text_chars < len(content) * 0.3:  # Less than 30% letters
                continue
            
            # Skip repetitive content
            words = content.split()
            if len(words) > 3 and len(set(words)) < len(words) * 0.5:  # More than 50% repeated words
                continue
            
            filtered_content.append(content)
        
        return filtered_content
    
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
                
                # Use enhanced PDF table extraction to better structure content
                structured_content = self.extract_pdf_table_content(lines)
                print(f"After enhanced PDF processing: {len(structured_content)} content items")
                
                # Additional content quality filtering for PDFs
                structured_content = self._filter_pdf_content_quality(structured_content)
                
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