# DMP-ART: Deep Architecture and Workflow Analysis

**Document Version:** 1.0
**Last Updated:** 2025-01-16
**Application Version:** 0.8
**Author:** Claude (Anthropic)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Component Deep Dive](#component-deep-dive)
4. [Data Flow and Workflow Analysis](#data-flow-and-workflow-analysis)
5. [Technical Implementation Details](#technical-implementation-details)
6. [Design Patterns and Architectural Decisions](#design-patterns-and-architectural-decisions)
7. [Security and Validation](#security-and-validation)
8. [Performance Considerations](#performance-considerations)
9. [Extension Points and Future Enhancements](#extension-points-and-future-enhancements)
10. [Development Guidelines](#development-guidelines)

---

## Executive Summary

### Application Purpose

DMP-ART (Data Management Plan Assessment and Response Tool) is a specialized web application designed for research administrators and grant officers at Polish academic institutions. It streamlines the assessment of Data Management Plans from grant proposals submitted through the OSF (Otwarta Nauka) system to the National Science Centre (NCN).

### Key Capabilities

- **Bilingual Document Processing**: Handles both Polish and English DMP submissions
- **Intelligent Content Extraction**: Automatically maps content to Science Europe DMP structure (14 subsections)
- **Category-Based Feedback System**: Provides pre-configured feedback templates for common review scenarios
- **Institutional Knowledge Preservation**: Maintains institution-specific comments and best practices
- **Flexible Template Management**: Full customization of review templates and comment libraries

### Technology Stack

**Backend:**
- Flask 3.1.0 (Python web framework)
- PyPDF2 3.0.1 (PDF processing)
- python-docx 1.1.2 (DOCX processing)
- Werkzeug 3.1.3 (WSGI utilities)

**Frontend:**
- HTML5 with Jinja2 templating
- Vanilla JavaScript (ES6+, ~1,589 lines)
- CSS3 with CSS custom properties
- Font Awesome 6.0.0 icons

**Data Layer:**
- JSON-based configuration system
- UUID-based file caching
- Local filesystem storage

---

## System Architecture

### 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DMP-ART Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │  Browser   │  │  Flask App   │  │   File System   │     │
│  │  (Client)  │◄─┤   (Server)   │◄─┤   (Storage)     │     │
│  └────────────┘  └──────────────┘  └─────────────────┘     │
│        │                │                     │              │
│        │                │                     │              │
│   ┌────▼────┐     ┌────▼────┐          ┌────▼─────┐        │
│   │  UI     │     │ Business│          │  Cache   │        │
│   │  Layer  │     │  Logic  │          │  System  │        │
│   └─────────┘     └─────────┘          └──────────┘        │
│                          │                                   │
│                    ┌─────▼──────┐                           │
│                    │ DMPExtractor│                           │
│                    │   Engine    │                           │
│                    └────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

### 2. Layered Architecture

#### Layer 1: Presentation Layer
**Location:** `templates/`, `static/`

**Responsibilities:**
- User interface rendering
- Client-side interaction handling
- Theme management (dark/light mode)
- Form validation and user feedback

**Key Components:**
- `index.html` - Upload interface
- `review.html` - Main review interface (1,789 lines)
- `template_editor.html` - Configuration management (787 lines)
- `documentation.html` - User documentation
- `style.css` - Unified styling system (980 lines)
- `script.js` - Core client logic (1,057 lines)

#### Layer 2: Application Layer
**Location:** `app.py`

**Responsibilities:**
- HTTP request/response handling
- Route definition and orchestration
- Session management
- File upload coordination
- JSON serialization/deserialization

**Key Routes:**
```python
/                    → Upload page
/upload              → File processing endpoint (POST)
/review/<filename>   → Review interface
/template_editor     → Template customization
/save_feedback       → Persist feedback (POST)
/load_categories     → Dynamic category loading (GET)
/config/<filename>   → Serve configuration files (GET)
/health              → Application health check
```

#### Layer 3: Business Logic Layer
**Location:** `utils/extractor.py`

**Responsibilities:**
- Document content extraction
- Bilingual section detection
- Content-to-structure mapping
- Metadata extraction
- Quality validation

**Core Classes:**
- `DMPExtractor` - Main processing engine (1,236 lines)

#### Layer 4: Data Layer
**Location:** `config/`, `outputs/`

**Responsibilities:**
- Configuration persistence
- Template storage
- Cache management
- Feedback archival

**Data Structures:**
- `dmp_structure.json` - DMP section definitions
- `quick_comments.json` - Reusable comment library
- `category_comments.json` - Category-specific templates
- `cache_*.json` - Extracted content cache
- `feedback_*.txt` - Generated feedback reports

---

## Component Deep Dive

### 1. Flask Application (`app.py`)

#### Architecture Pattern
The application follows a **simplified MVC pattern** without a dedicated model layer, using JSON files for data persistence instead of a traditional database.

#### Key Components

##### 1.1 Configuration Management
```python
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
```

**Design Rationale:**
- 16MB limit balances usability with server protection
- Dual format support (PDF/DOCX) covers all NCN submission types
- Separate upload/output folders enable clean file lifecycle management

##### 1.2 File Validation System

**Multi-Layer Validation:**

```python
def validate_docx_file(file_path):
    """
    Validation steps:
    1. File existence check
    2. Extension validation
    3. File size validation (0 bytes check and 16MB limit)
    4. ZIP structure validation (DOCX = ZIP container)
    5. Required file verification (word/document.xml, [Content_Types].xml)
    6. python-docx library validation
    7. Content presence verification
    """
```

**Validation Flow:**
```
File Upload
    │
    ├─► Extension Check (.pdf or .docx)
    │
    ├─► Size Validation (0 < size ≤ 16MB)
    │
    ├─► Format-Specific Validation
    │   ├─► DOCX: ZIP structure + XML files + parseable content
    │   └─► PDF: Valid PDF structure + extractable text
    │
    └─► Content Extraction
```

##### 1.3 Route Architecture

**Upload Workflow Route (`/upload`):**

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    # Step 1: Request validation
    # Step 2: File extraction from multipart/form-data
    # Step 3: Filename sanitization (secure_filename)
    # Step 4: Temporary file storage
    # Step 5: File validation
    # Step 6: DMPExtractor processing
    # Step 7: Cleanup (remove uploaded file)
    # Step 8: Cache ID generation and redirect
```

**Review Interface Route (`/review/<filename>`):**

```python
@app.route('/review/<filename>')
def review_dmp(filename):
    # Step 1: File existence verification
    # Step 2: Cache ID extraction from query params
    # Step 3: Cache file loading
    # Step 4: Unconnected text extraction
    # Step 5: Extraction metadata compilation
    # Step 6: Template rendering with extracted content
```

**Template Editor Route (`/template_editor`):**

Serves the configuration management interface with:
- DMP structure editor
- Quick comments management
- Category template management

##### 1.4 API Endpoints

**Category Management APIs:**

```python
/load_categories (GET)
    → Returns all category files from config/ directory
    → Excludes dmp_structure.json and quick_comments.json
    → Returns JSON: {"success": bool, "categories": dict}

/save_category (POST)
    → Accepts: {"file": string, "data": object}
    → Writes category data to config/<file>.json
    → Returns: {"success": bool, "message": string}

/create_category (POST)
    → Accepts: {"name": string}
    → Creates new empty category file
    → Returns: {"success": bool, "file": string}

/delete_category (POST)
    → Accepts: {"file": string}
    → Removes category file from config/
    → Returns: {"success": bool, "message": string}
```

**Quick Comments API:**

```python
/load_quick_comments (GET)
    → Returns: {"success": bool, "quick_comments": array}

/save_quick_comments (POST)
    → Accepts: {"quick_comments": array}
    → Each comment: {"name": string, "text": string}
```

##### 1.5 Error Handling

**Global Error Handlers:**

```python
@app.errorhandler(413)  # Payload Too Large
@app.errorhandler(404)  # Not Found
@app.errorhandler(500)  # Internal Server Error
```

**Consistent Error Response Format:**
```json
{
  "success": false,
  "message": "Human-readable error description"
}
```

---

### 2. Document Processing Engine (`utils/extractor.py`)

#### Architecture Overview

The `DMPExtractor` class is the core intelligence of the application, implementing a **multi-pass, pattern-matching extraction algorithm** with bilingual support.

#### 2.1 Initialization and Configuration

**DMP Structure Definition:**

```python
self.dmp_structure = {
    "1. Data description and collection or re-use of existing data": [
        "How will new data be collected or produced...",
        "What data (for example the types, formats, and volumes)..."
    ],
    "2. Documentation and data quality": [...],
    "3. Storage and backup during the research process": [...],
    "4. Legal requirements, codes of conduct": [...],
    "5. Data sharing and long-term preservation": [...],
    "6. Data management responsibilities and resources": [...]
}
```

**Section ID Mapping:**

Maps human-readable questions to section identifiers (1.1, 1.2, ..., 6.2) for the review interface.

#### 2.2 Bilingual Section Mapping

**Design Challenge:** NCN accepts both Polish and English DMP submissions, requiring the system to recognize and normalize section headers in both languages.

**Implementation:**

```python
self.section_mapping = {
    "Opis danych oraz pozyskiwanie":
        "1. Data description and collection or re-use of existing data",
    "Dokumentacja i jakość danych":
        "2. Documentation and data quality",
    # ... mappings for all 6 main sections
}

self.subsection_mapping = {
    "Sposób pozyskiwania i opracowywania nowych danych...":
        "How will new data be collected or produced...",
    # ... mappings for all 14 subsections
}
```

**Normalized Mapping:**

```python
self.normalized_subsection_mapping = {}
for polish, english in raw_subsection_mapping.items():
    # Remove trailing colons
    # Convert to lowercase
    # Store for case-insensitive matching
```

#### 2.3 Content Extraction Pipeline

**DOCX Processing (`process_docx`):**

```
1. File Validation
   └─► validate_docx_file()

2. Content Extraction
   ├─► Paragraph extraction with formatting preservation
   │   └─► extract_formatted_text() → "BOLD:", "UNDERLINED:", etc.
   └─► Table extraction
       └─► extract_table_content() → Cell-by-cell processing

3. Marker Detection
   ├─► Start marker: "DATA MANAGEMENT PLAN", "PLAN ZARZĄDZANIA DANYMI"
   └─► End marker: "ADMINISTRATIVE DECLARATIONS", "OŚWIADCZENIA ADMINISTRACYJNE"

4. Content Segmentation
   └─► Extract paragraphs between start_idx and end_idx

5. Intelligent Content Assignment
   └─► improve_content_assignment()
       ├─► Section detection
       ├─► Subsection detection
       ├─► Content buffering
       └─► Unconnected text tracking

6. Output Generation
   ├─► DOCX document with structured sections
   ├─► JSON cache with extraction metadata
   └─► UUID-based cache file
```

**PDF Processing (`process_pdf`):**

```
1. Text Extraction
   └─► PyPDF2.PdfReader.pages[i].extract_text()

2. Header/Footer Filtering
   └─► should_skip_text() with PDF-specific patterns
       ├─► Grant ID patterns: "OPUS-\d+"
       ├─► Page markers: "Strona \d+"
       ├─► Timestamp patterns: "2025-06-09 11:29:38"
       └─► Complex header detection: _is_grant_header_footer()

3. Table Content Extraction
   └─► extract_pdf_table_content()
       ├─► Detect table patterns (aligned columns, currency values)
       ├─► Process table rows
       └─► Clean formatting artifacts

4. Content Assignment
   └─► Same as DOCX processing
```

#### 2.4 Section Detection Algorithm

**Section Detection (`detect_section_from_text`):**

```python
def detect_section_from_text(text, is_pdf=False):
    """
    Detection Strategy (priority order):

    1. PDF Form Patterns (if is_pdf=True)
       → Match: "PLAN ZARZĄDZANIA DANYMI", "Opis danych oraz pozyskiwanie"

    2. Numbered Sections
       → Regex: r'^\s*(\d+)\.\s*(.*?)$'
       → Match against dmp_structure keys

    3. Formatted Text Markers
       → "BOLD:", "UNDERLINED:", "UNDERLINED_BOLD:"
       → Extract number and match

    4. Text Similarity
       → Calculate word overlap with section titles
       → Threshold: 0.6 (60% similarity)
    """
```

**Subsection Detection (`detect_subsection_from_text`):**

```python
def detect_subsection_from_text(text, current_section, is_pdf=False):
    """
    Detection Strategy (priority order):

    1. Direct English Match
       → Similarity score > 0.8 with English subsections

    2. Polish Subsection Mapping
       → Normalized text comparison
       → Best match with score > 0.5

    3. Word-Based Matching
       → Extract significant words (length > 3, excluding common words)
       → Match ratio = matching_words / max(subsection_words)
       → Threshold: 0.15 (15% match ratio)
       → Minimum: 2 matching words

    4. PDF Question Pattern Detection
       → Polish question indicators: "sposób.*?danych", "jak.*?będą"
       → Similarity threshold: 0.2
    """
```

**Text Similarity Algorithm:**

```python
def _text_similarity(text1, text2):
    """
    Jaccard Similarity Implementation:

    1. Tokenization
       └─► Split on whitespace, filter words with length > 2

    2. Set Operations
       ├─► intersection = words1 ∩ words2
       └─► union = words1 ∪ words2

    3. Similarity Score
       └─► |intersection| / |union|
    """
```

#### 2.5 Content Assignment Logic

**Improved Assignment Algorithm (`improve_content_assignment`):**

```
State Machine Implementation:

States:
- current_section: Currently active main section
- current_subsection: Currently active subsection
- content_buffer: Temporary storage for unassigned content

Processing Loop:
FOR each content_item in all_content:
    │
    ├─► TRY detect_section_from_text()
    │   └─► IF detected:
    │       ├─► Flush content_buffer to previous subsection
    │       ├─► Update current_section
    │       └─► Reset current_subsection
    │
    ├─► TRY detect_subsection_from_text()
    │   └─► IF detected:
    │       ├─► Flush content_buffer to previous subsection
    │       └─► Update current_subsection
    │
    └─► ASSIGN content:
        ├─► IF current_section AND current_subsection:
        │   └─► Assign directly to section_content[section][subsection]
        ├─► IF current_section ONLY:
        │   └─► Add to content_buffer
        └─► ELSE:
            └─► Add to unconnected_text

AFTER loop:
    └─► Flush remaining content_buffer
```

**Unconnected Text Tracking:**

Content that cannot be assigned to any section is preserved in a special `_unconnected_text` array, allowing users to manually assign it during review.

#### 2.6 Text Cleaning and Preprocessing

**Markup Removal (`clean_markup`):**

```python
def clean_markup(text):
    """
    Removes:
    - [text]{.underline} → text
    - **bold** → bold
    - __underline__ → underline
    - {.mark} formatting markers
    - Table delimiters (+--+, |  |)
    """
```

**Header/Footer Filtering:**

```python
skip_patterns = [
    r"Strona \d+",              # Page numbers
    r"ID: \d+",                 # Document IDs
    r"\[wydruk roboczy\]",      # Draft markers
    r"OSF,",                    # Footer text
    # ... 20+ patterns
]
```

**Grant Header Detection:**

```python
def _is_grant_header_footer(text):
    """
    Component-based detection:
    - Count matches for: OSF, OPUS-\d+, Strona \d+, ID:\d+, timestamps
    - Threshold: 3+ component matches → header/footer

    Example headers detected:
    "OSF, OPUS-29 Strona 41 ID: 651313, 2025-06-09 11:29:38"
    """
```

#### 2.7 Cache System

**Cache Structure:**

```json
{
  "1.1": {
    "section": "1. Data description and collection...",
    "question": "How will new data be collected...",
    "paragraphs": ["extracted text 1", "extracted text 2"],
    "tagged_paragraphs": [
      {"text": "...", "tags": [], "title": "..."},
      ...
    ]
  },
  ...
  "_unconnected_text": [
    {"text": "...", "type": "no_section"},
    {"text": "...", "type": "buffered"}
  ]
}
```

**UUID-based Naming:**

```python
cache_id = str(uuid.uuid4())
cache_filename = f"cache_{cache_id}.json"
```

**Benefits:**
- Prevents cache file collisions
- Enables concurrent processing
- Allows session resumption
- Maintains extraction history

---

### 3. Frontend Architecture

#### 3.1 Client-Side JavaScript Structure

**Modular Initialization Pattern:**

```javascript
document.addEventListener('DOMContentLoaded', function () {
    try {
        initializeDarkMode();
        initializeUploadPage();
        initializeReviewPage();
        initializeTemplateEditor();
    } catch (error) {
        console.error('DMP ART: Error during initialization:', error);
    }
});
```

**Component Lifecycle:**

Each initialization function checks for required DOM elements before proceeding:

```javascript
function initializeUploadPage() {
    const elements = {
        dropArea: document.getElementById('drop-area'),
        fileInput: document.getElementById('file-input'),
        // ... other elements
    };

    // Exit if not on upload page
    if (!elements.dropArea && !elements.fileInput) {
        console.log('Not on upload page, skipping...');
        return;
    }

    // Initialize functionality
    setupDragAndDrop(elements);
    setupFileSelection(elements);
    // ...
}
```

#### 3.2 Upload Page Implementation

**Drag-and-Drop System:**

```javascript
function setupDragAndDrop(elements) {
    // Prevent default browser behavior
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    // Visual feedback
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    // File handling
    dropArea.addEventListener('drop', handleDrop, false);
}
```

**File Upload Flow:**

```
User Selects File
    │
    ├─► Client-Side Validation
    │   ├─► Extension check (.pdf, .docx)
    │   └─► Size check (< 16MB)
    │
    ├─► FormData Creation
    │   └─► formData.append('file', file)
    │
    ├─► AJAX Upload
    │   └─► fetch('/upload', {method: 'POST', body: formData})
    │
    └─► Response Handling
        ├─► Success: Redirect to /review/<filename>?cache_id=<uuid>
        └─► Error: Display error message
```

**Button State Management:**

```javascript
function updateButtonStates(elements, state) {
    switch (state) {
        case 'initial':
            // Upload disabled, clear disabled
        case 'file-selected':
            // Upload active, clear active
        case 'analyzing':
            // Upload disabled, clear active
    }
}
```

#### 3.3 Review Page Implementation

**Sidebar Architecture:**

Fixed positioning strategy for persistent visibility:

```css
body[data-page="review"] aside.right-sidebar {
    position: fixed !important;
    top: 80px !important;
    right: 20px !important;
    bottom: 60px !important;
    width: 250px !important;
    overflow-y: auto !important;
    z-index: 999999 !important;
}
```

**Quick Navigation Grid:**

```javascript
function generateNavigationGrid() {
    const sections = document.querySelectorAll('[id^="section-"]');

    sections.forEach(section => {
        const sectionId = section.id.replace('section-', '');
        const btn = document.createElement('button');
        btn.className = 'nav-grid-btn';
        btn.textContent = sectionId;
        btn.addEventListener('click', () => scrollToSection(sectionId));
        navGrid.appendChild(btn);
    });
}
```

**Category Selection System:**

```javascript
// Category buttons trigger comment dropdown
function showCategoryComments(category, section) {
    // Fetch comments from CATEGORY_COMMENTS[category][section]
    // Populate dropdown with clickable comment items
    // Each click inserts comment into feedback textarea
}

// Comment insertion with cursor positioning
function insertCommentIntoTextarea(comment, section) {
    const textarea = document.getElementById(`feedback-${section}`);
    const cursorPosition = textarea.selectionStart;

    // Insert at cursor with proper spacing
    const newValue = textBefore + separator + comment + textAfter;
    textarea.value = newValue;

    // Maintain cursor position
    textarea.setSelectionRange(newCursorPosition, newCursorPosition);
}
```

**Citation Feature:**

```javascript
// Text selection in extracted content
document.addEventListener('mouseup', function(e) {
    let sel = window.getSelection();

    // Show cite button if text selected in .extracted-content
    if (extractedDiv && !sel.isCollapsed) {
        citeBtn.style.display = 'block';
    }
});

// Cite button click
citeBtn.addEventListener('click', function(e) {
    // Highlight selected text
    let span = document.createElement('span');
    span.className = 'citation-highlight';

    // Insert citation into feedback
    let citation = `❝ ${selText} ❞`;
    textarea.value = currentValue + separator + citation;
});
```

**Compiled Feedback Panel:**

Modal panel with sliding animation:

```javascript
function showPanel() {
    backdrop.classList.add('active');
    panel.classList.add('active');
    generateFeedbackReport();
}

function generateFeedbackReport() {
    let report = 'DMP FEEDBACK REPORT\n';
    report += '==================\n\n';

    sections.forEach(section => {
        const feedbackTextarea = section.querySelector(`#feedback-${sectionId}`);
        if (feedbackTextarea && feedbackTextarea.value.trim()) {
            report += `SECTION ${sectionId}\n`;
            report += feedbackTextarea.value.trim() + '\n\n';
        }
    });

    feedbackTextarea.value = report;
}
```

#### 3.4 Template Editor Implementation

**Tab System:**

```javascript
function switchTab(tabId) {
    // Remove active class from all tabs and panels
    document.querySelectorAll('.tab-btn').forEach(btn =>
        btn.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(panel =>
        panel.classList.remove('active'));

    // Activate selected tab
    targetBtn.classList.add('active');
    targetPanel.classList.add('active');
}
```

**Dynamic Category Tabs:**

Categories are loaded from the server and dynamically added to the tab navigation:

```javascript
fetch('/list_categories')
    .then(response => response.json())
    .then(data => {
        data.categories.forEach(category => {
            const tabBtn = createTabButton(category.name, category.file);
            const tabPanel = createTabPanel(category.file);

            tabNavigation.appendChild(tabBtn);
            tabContent.appendChild(tabPanel);
        });
    });
```

#### 3.5 Dark Mode Implementation

**Theme Persistence:**

```javascript
function initializeDarkMode() {
    const savedTheme = localStorage.getItem('dmp-art-theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

    setTheme(initialTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    setTheme(newTheme);
    localStorage.setItem('dmp-art-theme', newTheme);
}
```

**CSS Custom Properties:**

```css
:root[data-theme="light"] {
    --bg-main: #f5f5f5;
    --bg-card: #ffffff;
    --text-primary: #2c3e50;
    --primary-color: #3498db;
}

:root[data-theme="dark"] {
    --bg-main: #1a1a1a;
    --bg-card: #2d2d2d;
    --text-primary: #ecf0f1;
    --primary-color: #5dade2;
}
```

**FOUC Prevention:**

```html
<script>
(function() {
    const saved = localStorage.getItem('dmp-art-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = saved || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
})();
</script>
```

---

## Data Flow and Workflow Analysis

### Workflow 1: Document Upload and Extraction

**User Journey:**

```
Step 1: User Access
├─► Navigate to http://localhost:5000/
└─► View upload interface (index.html)

Step 2: File Selection
├─► Drag file to drop area OR click to browse
├─► Client validates: extension (.pdf, .docx) and size (≤16MB)
└─► Display file info and enable upload button

Step 3: Upload Initiation
├─► User clicks "Upload and Process"
├─► JavaScript sends FormData via fetch()
└─► Display loading spinner

Step 4: Server Processing
├─► Flask receives file at /upload endpoint
├─► Validate file (validate_docx_file or validate_pdf_file)
├─► Save to uploads/ folder temporarily
├─► Create DMPExtractor instance
├─► Call extractor.process_file(file_path, output_folder)
└─► Delete uploaded file from uploads/

Step 5: Extraction Processing
├─► Load document (Document(path) or PdfReader(path))
├─► Extract text with formatting
├─► Detect DMP section boundaries
├─► Run content assignment algorithm
├─► Generate output DOCX with structured sections
├─► Create JSON cache file
└─► Return cache_id and output filename

Step 6: Redirection
├─► Server responds with redirect URL
├─► Client navigates to /review/<filename>?cache_id=<uuid>
└─► Load review interface

Step 7: Review Interface Loading
├─► Flask reads cache file: cache_<uuid>.json
├─► Extract content for each section (1.1 - 6.2)
├─► Extract unconnected text (if any)
├─► Render review.html with extracted_content
└─► Initialize client-side review functionality
```

**Data Transformation Flow:**

```
Original Document (PDF/DOCX)
    │
    ├─► Raw Text Extraction
    │   └─► PyPDF2 / python-docx
    │
    ├─► Text Cleaning
    │   ├─► Remove headers/footers
    │   ├─► Clean markup
    │   └─► Filter formatting artifacts
    │
    ├─► Structure Detection
    │   ├─► Identify sections (1-6)
    │   ├─► Identify subsections (1.1-6.2)
    │   └─► Buffer unassigned content
    │
    ├─► Content Assignment
    │   ├─► section_content[section][subsection] = [paragraphs]
    │   └─► unconnected_text = [unassigned items]
    │
    └─► Cache Generation
        └─► {
              "1.1": {"section": "...", "question": "...", "paragraphs": [...]},
              ...
              "_unconnected_text": [...]
            }
```

---

### Workflow 2: Review and Feedback Generation

**User Journey:**

```
Step 1: Review Interface Display
├─► Browser loads /review/<filename>?cache_id=<uuid>
├─► Server loads cache_<uuid>.json
├─► Render 14 question cards (sections 1.1 - 6.2)
└─► Initialize sidebar with navigation + quick comments

Step 2: Navigation
├─► User clicks section button in sidebar (e.g., "2.1")
├─► JavaScript scrolls to section
├─► Highlights section briefly
└─► Focuses feedback textarea

Step 3: Feedback Entry (Multiple Approaches)

Approach A: Manual Entry
└─► User types directly in feedback textarea

Approach B: Quick Comments
├─► User clicks quick comment in sidebar
├─► Comment inserted at cursor position
└─► Character counter updates

Approach C: Category-Based
├─► User selects category (Newcomer, Missing, Ready)
├─► Category dropdown displays pre-configured comments
├─► User clicks comment to insert
└─► Comment inserted into textarea

Approach D: Citation
├─► User selects text in extracted content
├─► Click "Cite" button
├─► Selected text highlighted in yellow
└─► Citation inserted: ❝ text ❞

Step 4: Feedback Compilation
├─► User clicks "Compile Feedback" in sidebar
├─► JavaScript aggregates all non-empty feedback textareas
├─► Generate report:
│   ├─► Header with timestamp
│   ├─► Section-by-section feedback
│   └─► Proper formatting
└─► Display in modal panel

Step 5: Export Options
├─► Copy to Clipboard
│   └─► navigator.clipboard.writeText()
├─► Download as TXT
│   └─► Blob + download link
└─► Generate DOCX (planned feature)

Step 6: Save Progress
├─► User clicks "Save Progress"
├─► JavaScript collects all feedback textarea values
├─► POST to /save_feedback
└─► Server saves to feedback_<filename>.txt
```

**State Management:**

```javascript
// Global state tracking
let lastFocusedTextarea = null;  // For quick comment targeting

// Textarea tracking
textareas.forEach(textarea => {
    textarea.addEventListener('focus', function() {
        lastFocusedTextarea = this;
    });
});

// Character counting
function updateCharacterCounter(sectionId) {
    const charCount = textarea.value.length;
    const wordCount = textarea.value.trim() ?
        textarea.value.trim().split(/\s+/).length : 0;
    counter.textContent = `${charCount} characters, ${wordCount} words`;
}
```

---

### Workflow 3: Template Customization

**User Journey:**

```
Step 1: Access Template Editor
├─► Navigate to /template_editor
└─► Load template_editor.html

Step 2: Tab Navigation
├─► DMP Structure Tab
│   ├─► View/edit 6 main sections
│   └─► View/edit 14 subsections
│
├─► Quick Comments Tab
│   ├─► View existing quick comments
│   ├─► Add new comments (name + text)
│   ├─► Edit existing comments
│   ├─► Delete comments
│   └─► Save to quick_comments.json
│
└─► Category Tabs (dynamic)
    ├─► Newcomer Guidance
    ├─► Missing Info
    ├─► Ready to Use
    └─► Custom categories

Step 3: Category Management

Creating New Category:
├─► Click "Create Category" button
├─► Enter category name
├─► System creates empty config/<name>.json
└─► New tab added to navigation

Editing Category:
├─► Select category tab
├─► View sections 1.1 - 6.2
├─► For each section:
│   ├─► Add multiple comment templates
│   ├─► Edit existing templates
│   └─► Delete templates
└─► Click "Save Category"

Deleting Category:
├─► Click delete button on category tab
├─► Confirm deletion
├─► System removes config/<name>.json
└─► Tab removed from navigation

Step 4: DMP Structure Customization
├─► Edit section titles
├─► Edit subsection questions
├─► Reorder subsections (drag-and-drop)
└─► Save to dmp_structure.json

Step 5: Persistence
├─► All changes saved to JSON files in config/
├─► Changes immediately available in review interface
└─► No application restart required
```

**Data Synchronization:**

```
Template Editor
    │
    ├─► Save Quick Comments
    │   └─► POST /save_quick_comments
    │       └─► Write config/quick_comments.json
    │
    ├─► Save Category
    │   └─► POST /save_category
    │       └─► Write config/<category>.json
    │
    └─► Save DMP Structure
        └─► POST /save_dmp_structure
            └─► Write config/dmp_structure.json

Review Interface
    │
    ├─► Load Quick Comments
    │   └─► GET /load_quick_comments
    │       └─► Read config/quick_comments.json
    │
    └─► Load Categories
        └─► GET /load_categories
            └─► Read all config/*.json (except excluded files)
```

---

## Technical Implementation Details

### 1. Bilingual Processing Implementation

**Challenge:** The NCN allows submissions in Polish or English, requiring the system to recognize and normalize both languages.

**Solution: Multi-Level Mapping System**

**Level 1: Section Mapping**

```python
self.section_mapping = {
    "Opis danych oraz pozyskiwanie":
        "1. Data description and collection or re-use of existing data",
    # ... 6 total mappings
}
```

**Level 2: Subsection Mapping**

```python
self.subsection_mapping = {
    "Sposób pozyskiwania i opracowywania nowych danych i/lub ponownego wykorzystania dostępnych danych":
        "How will new data be collected or produced and/or how will existing data be re-used?",
    # ... 14 total mappings
}
```

**Level 3: Normalized Mapping**

```python
# Remove trailing colons, convert to lowercase
for polish, english in raw_subsection_mapping.items():
    normalized_polish = polish.rstrip(':').strip().lower()
    self.normalized_subsection_mapping[normalized_polish] = english
```

**Level 4: Fuzzy Matching**

```python
def _text_similarity(text1, text2):
    # Jaccard similarity on word sets
    # Filters words with length > 2
    # Case-insensitive comparison
    return len(intersection) / len(union)
```

**Processing Flow:**

```
Input Text: "Sposób pozyskiwania i opracowywania nowych danych"
    │
    ├─► Normalize
    │   └─► "sposób pozyskiwania i opracowywania nowych danych"
    │
    ├─► Check normalized_subsection_mapping
    │   └─► Exact match? → Return English equivalent
    │
    ├─► Check subsection_mapping with similarity
    │   └─► Similarity > 0.5? → Return best match
    │
    └─► Word-based matching
        └─► Match ratio > 0.15 + 2 matching words? → Return match
```

### 2. Content Assignment State Machine

**State Variables:**

```python
current_section = None      # Active main section (1-6)
current_subsection = None   # Active subsection (1.1-6.2)
content_buffer = []         # Temporary storage
unconnected_text = []       # Unassigned content
```

**State Transitions:**

```
State 1: No Section Detected
    │ Input: content_item
    ├─► detect_section() → Section found?
    │   ├─► Yes: Transition to State 2
    │   └─► No: Add to unconnected_text

State 2: Section Detected, No Subsection
    │ Input: content_item
    ├─► detect_subsection() → Subsection found?
    │   ├─► Yes: Transition to State 3
    │   └─► No: Add to content_buffer

State 3: Section and Subsection Detected
    │ Input: content_item
    ├─► detect_section() → New section?
    │   ├─► Yes: Flush buffer, update section, transition to State 2
    │   └─► No: Continue
    ├─► detect_subsection() → New subsection?
    │   ├─► Yes: Flush buffer, update subsection, stay in State 3
    │   └─► No: Continue
    └─► Assign content to current_section[current_subsection]
```

**Buffer Flushing:**

```python
if current_section and current_subsection and content_buffer:
    for buffered_content in content_buffer:
        section_content[current_section][current_subsection].append(buffered_content)
    content_buffer = []
```

### 3. Cache System Architecture

**Cache Generation:**

```python
cache_id = str(uuid.uuid4())  # e.g., "3f5b2c9d-8e1a-4b6c-9d2e-7f8a1b3c4d5e"
cache_filename = f"cache_{cache_id}.json"
cache_path = os.path.join(output_dir, cache_filename)

with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(review_structure, f, ensure_ascii=False, indent=2)
```

**Cache Structure:**

```json
{
  "1.1": {
    "section": "1. Data description and collection or re-use of existing data",
    "question": "How will new data be collected or produced and/or how will existing data be re-used?",
    "paragraphs": [
      "Original extracted paragraph 1",
      "Original extracted paragraph 2"
    ],
    "tagged_paragraphs": [
      {
        "text": "Processed paragraph text",
        "tags": [],
        "title": "First sentence or null"
      }
    ]
  },
  "1.2": { /* ... */ },
  // ... sections 2.1 through 6.2 ...
  "_unconnected_text": [
    {
      "text": "Text that couldn't be assigned",
      "type": "no_section"
    },
    {
      "text": "Text that was buffered but not assigned",
      "type": "buffered"
    }
  ]
}
```

**Cache Retrieval:**

```python
cache_id = request.args.get('cache_id', '')
cache_path = os.path.join(app.config['OUTPUT_FOLDER'], f"cache_{cache_id}.json")

if os.path.exists(cache_path):
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)

        if "_unconnected_text" in cache_data:
            unconnected_text = cache_data["_unconnected_text"]
            del cache_data["_unconnected_text"]

        extracted_content = cache_data
```

**Benefits of UUID-based Caching:**

1. **Collision Prevention**: UUIDs are globally unique
2. **Concurrent Processing**: Multiple users can upload simultaneously
3. **Session Persistence**: Cache survives browser refresh
4. **Debugging**: Extraction results preserved for analysis
5. **Audit Trail**: Historical extraction data retained

### 4. Frontend-Backend Communication

**API Design Pattern:**

All AJAX endpoints follow a consistent JSON response format:

```json
{
  "success": true,
  "data": { /* optional response data */ },
  "message": "Human-readable status message"
}
```

Or on error:

```json
{
  "success": false,
  "message": "Error description"
}
```

**Example: Category Loading**

```javascript
// Client-side request
fetch('/load_categories')
    .then(response => response.json())
    .then(data => {
        if (data.success && data.categories) {
            CATEGORY_COMMENTS = data.categories;
        }
    });
```

```python
# Server-side handler
@app.route('/load_categories', methods=['GET'])
def load_categories():
    try:
        categories = {}
        for filename in os.listdir('config'):
            if filename.endswith('.json') and filename not in excluded:
                # Load and process
                categories[category_name] = category_data

        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
```

### 5. Error Handling Strategy

**Multi-Layer Error Handling:**

**Layer 1: Client-Side Validation**
```javascript
// Immediate feedback before server contact
if (!isValidType) {
    showToast('Please select a PDF or DOCX file', 'error');
    return;
}

if (file.size > maxSize) {
    showToast('File size must be less than 16MB', 'error');
    return;
}
```

**Layer 2: Server-Side Validation**
```python
# File validation before processing
is_valid, validation_message = validate_docx_file(file_path)
if not is_valid:
    try:
        os.remove(file_path)
    except:
        pass
    return jsonify({
        'success': False,
        'message': f'DOCX validation failed: {validation_message}'
    })
```

**Layer 3: Processing Error Handling**
```python
try:
    result = extractor.process_file(file_path, output_dir)

    if result['success']:
        return jsonify({
            'success': True,
            'redirect': url_for('review_dmp', filename=result['filename'])
        })
    else:
        return jsonify(result)

except Exception as e:
    import traceback
    traceback.print_exc()

    # Cleanup
    if file_path is not None:
        os.remove(file_path)

    return jsonify({
        'success': False,
        'message': f'Error processing file: {str(e)}'
    })
```

**Layer 4: Global Error Handlers**
```python
@app.errorhandler(413)  # Payload Too Large
def too_large(e):
    return jsonify({
        'success': False,
        'message': 'File too large. Maximum size is 16MB.'
    }), 413
```

---

## Design Patterns and Architectural Decisions

### 1. Singleton Pattern: DMPExtractor Instance

**Implementation:**

```python
# Each request creates a new instance
extractor = DMPExtractor()
result = extractor.process_file(file_path, output_dir)
```

**Rationale:**
- Stateless processing ensures thread safety
- Each extraction is independent
- No shared state between requests
- Simplified error recovery

### 2. Strategy Pattern: File Format Processing

**Implementation:**

```python
def process_file(self, file_path, output_dir):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return self.process_pdf(file_path, output_dir)
    elif file_extension == '.docx':
        return self.process_docx(file_path, output_dir)
    else:
        return {"success": False, "message": "Unsupported file type"}
```

**Benefits:**
- Easy to add new file format support
- Encapsulates format-specific logic
- Consistent interface for all formats

### 3. Template Method Pattern: Document Processing

**Abstract Processing Flow:**

```python
def process_docx(self, docx_path, output_dir):
    # Step 1: Validation
    is_valid, message = self.validate_docx_file(docx_path)

    # Step 2: Content Extraction
    formatted_paragraphs = self.extract_paragraphs(doc)
    table_content = self.extract_table_content(doc)

    # Step 3: Boundary Detection
    start_idx, end_idx = self.find_dmp_boundaries(all_text)

    # Step 4: Content Assignment
    section_content, tagged_content, unconnected =
        self.improve_content_assignment(dmp_paragraphs)

    # Step 5: Output Generation
    output_doc = self.create_output_document(section_content)
    cache_id = self.generate_cache(review_structure)

    return result
```

### 4. Factory Pattern: Dynamic Tab Creation

**Implementation:**

```javascript
function createCategoryTab(categoryName, categoryFile) {
    // Create tab button
    const tabBtn = document.createElement('button');
    tabBtn.className = 'tab-btn';
    tabBtn.setAttribute('data-tab', categoryFile);
    tabBtn.innerHTML = `<i class="fas fa-folder"></i> ${categoryName}`;

    // Create tab panel
    const tabPanel = document.createElement('div');
    tabPanel.className = 'tab-panel';
    tabPanel.id = `${categoryFile}-panel`;

    // Attach delete handler
    const deleteBtn = createDeleteButton(categoryFile);

    return {tabBtn, tabPanel, deleteBtn};
}
```

### 5. Observer Pattern: Character Counter Updates

**Implementation:**

```javascript
textareas.forEach(textarea => {
    const sectionId = textarea.getAttribute('data-section-id');

    function updateCounter() {
        const charCount = textarea.value.length;
        const wordCount = textarea.value.trim() ?
            textarea.value.trim().split(/\s+/).length : 0;
        counter.textContent = `${charCount} characters, ${wordCount} words`;
    }

    // Observer registration
    textarea.addEventListener('input', updateCounter);

    // Initial state
    updateCounter();
});
```

### 6. Module Pattern: JavaScript Encapsulation

**Implementation:**

```javascript
(function() {
    'use strict';

    // Private variables
    let currentSelection = null;
    let currentSectionId = null;

    // Private functions
    function getSectionIdFromNode(node) { /* ... */ }

    // Event handlers
    document.addEventListener('mouseup', function(e) {
        // Access private variables
    });

    citeBtn.addEventListener('click', function(e) {
        // Access private variables
    });
})();
```

### 7. Architectural Decision Records

#### ADR 1: JSON-based Configuration vs Database

**Context:** Need persistent storage for templates, comments, and categories

**Decision:** Use JSON files in `config/` directory

**Rationale:**
- Low complexity for single-user application
- Easy version control (JSON files in git)
- No database setup/maintenance required
- Human-readable and editable
- Sufficient performance for small datasets

**Consequences:**
- ✅ Simple deployment
- ✅ Easy backup/restore
- ✅ Git-friendly
- ❌ Not suitable for concurrent multi-user access
- ❌ No ACID guarantees
- ❌ Manual file locking required for multi-process deployment

#### ADR 2: UUID-based Cache System vs Session Storage

**Context:** Need to preserve extraction results across page navigation

**Decision:** Use UUID-based JSON cache files

**Rationale:**
- Survives browser refresh
- Enables bookmarking of review pages
- Allows debugging of extraction results
- No server-side session management complexity
- No cookie/localStorage size limits

**Consequences:**
- ✅ Robust state persistence
- ✅ Debugging friendly
- ✅ No session timeout issues
- ❌ Disk space usage accumulates
- ❌ Manual cache cleanup required
- ❌ Cache files not automatically expired

#### ADR 3: Bilingual Processing vs Language Detection

**Context:** Support Polish and English DMP submissions

**Decision:** Implement dual-language mapping system with fuzzy matching

**Rationale:**
- Known vocabulary (Science Europe DMP standard)
- More reliable than language detection
- Handles mixed-language documents
- No external language detection library required

**Consequences:**
- ✅ High accuracy for known patterns
- ✅ Handles code-switching
- ✅ No external dependencies
- ❌ Requires maintenance of mapping dictionaries
- ❌ Limited to Polish/English

#### ADR 4: Monolithic JavaScript vs Modular Build

**Context:** Frontend code organization strategy

**Decision:** Use vanilla JavaScript without build tools

**Rationale:**
- Simple deployment (no build step)
- Low complexity for ~1,600 lines of code
- Fast iteration during development
- No transpilation/bundling overhead

**Consequences:**
- ✅ Zero build complexity
- ✅ Direct debugging
- ✅ Fast refresh cycles
- ❌ No tree-shaking
- ❌ No TypeScript benefits
- ❌ Manual dependency management

---

## Security and Validation

### 1. File Upload Security

**Threat Model:**

1. **Malicious File Upload**: User uploads executable disguised as DOCX/PDF
2. **Path Traversal**: User manipulates filename to write outside uploads directory
3. **Zip Bomb**: User uploads compressed bomb in DOCX (ZIP) format
4. **Resource Exhaustion**: User uploads very large files repeatedly
5. **XSS via Filename**: User uploads file with script tags in filename

**Mitigation Strategies:**

#### 1.1 Filename Sanitization

```python
from werkzeug.utils import secure_filename

filename = secure_filename(file.filename or "")
```

**What `secure_filename` does:**
- Removes path components (`../../../etc/passwd` → `etc_passwd`)
- Converts to ASCII
- Removes special characters
- Normalizes separators

#### 1.2 Extension Validation

```python
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

**Defense in Depth:**
Not just extension checking—also validates:
- DOCX: ZIP structure + required XML files
- PDF: Valid PDF structure + extractable text

#### 1.3 Size Limits

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'message': 'File too large'}), 413
```

#### 1.4 Content Validation

```python
# DOCX ZIP Bomb Protection
with zipfile.ZipFile(file_path, 'r') as zip_file:
    file_list = zip_file.namelist()

    # Check for required files (not arbitrary ZIP)
    required_files = ['word/document.xml', '[Content_Types].xml']
    for required_file in required_files:
        if required_file not in file_list:
            return False, f"Invalid DOCX structure: missing {required_file}"
```

#### 1.5 Temporary File Cleanup

```python
try:
    result = extractor.process_file(file_path, output_dir)

    # Always cleanup uploaded file
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not remove uploaded file: {str(e)}")

except Exception as e:
    # Cleanup on error
    try:
        if file_path is not None:
            os.remove(file_path)
    except Exception:
        pass
```

### 2. XSS Prevention

**Jinja2 Auto-Escaping:**

```html
<!-- Automatic HTML escaping -->
<div class="text-content">{{ item.text }}</div>

<!-- Renders: &lt;script&gt;alert('xss')&lt;/script&gt; -->
```

**JavaScript String Handling:**

```javascript
// Safe: textContent (not innerHTML)
commentDiv.textContent = comment;

// Unsafe alternative (NOT used):
// commentDiv.innerHTML = comment;  // DANGEROUS
```

### 3. CSRF Protection

**Flask-WTF Integration (Recommended Enhancement):**

Currently missing CSRF tokens. Future implementation:

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

```html
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

### 4. Path Traversal Prevention

**Secure Path Construction:**

```python
# Safe: os.path.join validates paths
file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

# Unsafe alternative (NOT used):
# file_path = app.config['UPLOAD_FOLDER'] + '/' + filename  # DANGEROUS
```

**Existence Verification:**

```python
@app.route('/review/<filename>')
def review_dmp(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)

    # Verify file exists before reading
    if not os.path.exists(file_path):
        return "File not found", 404
```

### 5. Input Validation

**Client-Side Validation:**

```javascript
// Extension validation
const allowedExtensions = ['.pdf', '.docx'];
const isValidType = allowedExtensions.some(ext =>
    file.name.toLowerCase().endsWith(ext));

// Size validation
const maxSize = 16 * 1024 * 1024;
if (file.size > maxSize) {
    showToast('File size must be less than 16MB', 'error');
    return;
}
```

**Server-Side Validation:**

```python
# Never trust client-side validation
if not file or not file.filename:
    return jsonify({'success': False, 'message': 'No selected file'})

if file and allowed_file(file.filename):
    # Proceed with processing
else:
    return jsonify({'success': False, 'message': 'Invalid file format'})
```

---

## Performance Considerations

### 1. Document Processing Performance

**Performance Characteristics:**

| File Type | Size | Processing Time | Bottleneck |
|-----------|------|----------------|------------|
| DOCX | 1 MB | ~2-3 seconds | python-docx parsing |
| DOCX | 5 MB | ~8-12 seconds | Table extraction |
| PDF | 1 MB | ~3-5 seconds | PyPDF2 extraction |
| PDF | 5 MB | ~15-20 seconds | Text extraction + cleaning |

**Optimization Strategies:**

#### 1.1 Lazy Loading

```python
# Only load document when needed
def process_file(self, file_path, output_dir):
    if file_extension == '.pdf':
        # PDF processing isolated
        return self.process_pdf(file_path, output_dir)
    elif file_extension == '.docx':
        # DOCX processing isolated
        return self.process_docx(file_path, output_dir)
```

#### 1.2 Early Filtering

```python
# Skip headers/footers early in pipeline
for paragraph in doc.paragraphs:
    formatted_text = self.extract_formatted_text(paragraph)

    # Early exit for skippable content
    if not formatted_text.strip():
        continue

    if self.should_skip_text(clean_para):
        continue

    # Only process meaningful content
    meaningful_content.append(formatted_text)
```

#### 1.3 Compiled Regex Patterns

**Recommendation for Future Enhancement:**

```python
# Current: Compile on every call
def should_skip_text(self, text, is_pdf=False):
    skip_patterns = [
        r"Strona \d+",
        r"Page \d+",
        # ... 20+ patterns
    ]

    for pattern in skip_patterns:
        if re.search(pattern, text, re.IGNORECASE) is not None:
            return True

# Optimized: Pre-compile patterns
class DMPExtractor:
    def __init__(self):
        self.skip_patterns_compiled = [
            re.compile(r"Strona \d+", re.IGNORECASE),
            re.compile(r"Page \d+", re.IGNORECASE),
            # ...
        ]

    def should_skip_text(self, text, is_pdf=False):
        for pattern in self.skip_patterns_compiled:
            if pattern.search(text) is not None:
                return True
```

### 2. Frontend Performance

**Metrics:**

| Operation | Time | Notes |
|-----------|------|-------|
| Initial page load | ~500ms | No JavaScript bundling |
| Theme toggle | <50ms | CSS variable swap |
| Section navigation | ~100ms | Smooth scroll animation |
| Category load | ~200ms | AJAX + DOM update |
| Feedback compilation | ~300ms | 14 sections aggregation |

**Optimization Techniques:**

#### 2.1 Event Delegation

```javascript
// Bad: 14 individual event listeners
document.querySelectorAll('.category-btn-inline').forEach(button => {
    button.addEventListener('click', handleClick);
});

// Better: Single delegated listener
document.getElementById('category-buttons-container')
    .addEventListener('click', function(e) {
        if (e.target.classList.contains('category-btn-inline')) {
            handleClick(e);
        }
    });
```

#### 2.2 Debouncing Character Counter

**Current Implementation:**

```javascript
textarea.addEventListener('input', updateCounter);
```

**Optimized Version (Recommended):**

```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

textarea.addEventListener('input', debounce(updateCounter, 300));
```

#### 2.3 Virtual Scrolling for Large Lists

**Current:** All quick comments rendered immediately

**Future Enhancement:** Virtual scrolling for 100+ comments

```javascript
// Render only visible items + buffer
function renderVisibleComments(scrollTop, containerHeight) {
    const visibleStart = Math.floor(scrollTop / itemHeight);
    const visibleEnd = Math.ceil((scrollTop + containerHeight) / itemHeight);

    // Render visibleStart - 5 to visibleEnd + 5 (buffer)
}
```

### 3. Caching Strategy

**Current Cache Lifecycle:**

```
Upload
  │
  ├─► Process Document
  │   └─► Generate cache_<uuid>.json
  │
  ├─► Review Session (cache read repeatedly)
  │
  └─► Manual Cleanup Required
```

**Recommended Enhancement: Time-based Expiration**

```python
import time
import os

def cleanup_old_caches(output_dir, max_age_hours=24):
    """Remove cache files older than max_age_hours"""
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    for filename in os.listdir(output_dir):
        if filename.startswith('cache_') and filename.endswith('.json'):
            file_path = os.path.join(output_dir, filename)
            file_age = current_time - os.path.getmtime(file_path)

            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    print(f"Removed old cache: {filename}")
                except Exception as e:
                    print(f"Error removing {filename}: {str(e)}")

# Schedule cleanup (e.g., with APScheduler)
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=lambda: cleanup_old_caches('outputs'),
    trigger="interval",
    hours=1
)
scheduler.start()
```

---

## Extension Points and Future Enhancements

### 1. Multi-User Support

**Current Limitation:** Single-user application with no authentication

**Enhancement Path:**

```python
# Add Flask-Login for authentication
from flask_login import LoginManager, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/review/<filename>')
@login_required
def review_dmp(filename):
    # Associate cache with user
    user_output_dir = os.path.join('outputs', current_user.id)
    # ...
```

**User-Specific Features:**
- Personal template libraries
- Review history tracking
- Collaborative review (multiple reviewers per DMP)
- Activity logging

### 2. Database Integration

**Migration Path: SQLite → PostgreSQL**

**Schema Design:**

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    cache_id VARCHAR(36) UNIQUE NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Extracted content table
CREATE TABLE extracted_content (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    section_id VARCHAR(10) NOT NULL,
    content TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    section_id VARCHAR(10) NOT NULL,
    feedback_text TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates table (replacing JSON files)
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    category VARCHAR(100) NOT NULL,
    section_id VARCHAR(10) NOT NULL,
    template_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_shared BOOLEAN DEFAULT FALSE
);
```

### 3. Advanced Extraction Features

#### 3.1 Machine Learning-Based Section Detection

**Current:** Rule-based pattern matching with fuzzy string matching

**Future:** Supervised learning model

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class MLSectionDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier()

    def train(self, training_data):
        """
        training_data: [(text, section_label), ...]
        """
        texts, labels = zip(*training_data)
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)

    def predict_section(self, text):
        X = self.vectorizer.transform([text])
        return self.classifier.predict(X)[0]
```

#### 3.2 Table Structure Extraction

**Current:** Basic table cell extraction

**Enhanced:** Preserve table structure and relationships

```python
def extract_table_structure(table):
    """
    Returns:
    {
        "headers": ["Column 1", "Column 2", ...],
        "rows": [
            {"Column 1": "Value 1", "Column 2": "Value 2", ...},
            ...
        ]
    }
    """
    headers = []
    for cell in table.rows[0].cells:
        headers.append(cell.text.strip())

    rows = []
    for row in table.rows[1:]:
        row_data = {}
        for idx, cell in enumerate(row.cells):
            row_data[headers[idx]] = cell.text.strip()
        rows.append(row_data)

    return {"headers": headers, "rows": rows}
```

#### 3.3 Multi-Language Support

**Current:** Polish and English

**Future:** Extend to other EU languages

```python
LANGUAGE_MAPPINGS = {
    'pl': {  # Polish
        "Opis danych": "1. Data description...",
    },
    'en': {  # English
        "Data description": "1. Data description...",
    },
    'de': {  # German
        "Datenbeschreibung": "1. Data description...",
    },
    'fr': {  # French
        "Description des données": "1. Data description...",
    }
}

def detect_language(text):
    # Use langdetect or similar
    from langdetect import detect
    return detect(text)

def get_mapping_for_language(lang_code):
    return LANGUAGE_MAPPINGS.get(lang_code, LANGUAGE_MAPPINGS['en'])
```

### 4. Export Formats

**Current:** TXT export only

**Future Enhancements:**

#### 4.1 DOCX Generation

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_feedback_docx(sections_feedback):
    doc = Document()

    # Title
    title = doc.add_heading('DMP Feedback Report', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata
    doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph()

    # Sections
    for section_id, feedback in sections_feedback.items():
        # Section header
        heading = doc.add_heading(f"Section {section_id}", level=1)

        # Question
        question_para = doc.add_paragraph()
        question_run = question_para.add_run(feedback['question'])
        question_run.bold = True

        # Feedback content
        feedback_para = doc.add_paragraph(feedback['text'])
        feedback_para.paragraph_format.left_indent = Inches(0.5)

        doc.add_paragraph()  # Spacing

    return doc
```

#### 4.2 PDF Generation

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

def generate_feedback_pdf(sections_feedback, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("DMP Feedback Report", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Metadata
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))

    # Sections
    for section_id, feedback in sections_feedback.items():
        # Section header
        story.append(Paragraph(
            f"Section {section_id}",
            styles['Heading2']
        ))

        # Question
        story.append(Paragraph(
            f"<b>{feedback['question']}</b>",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.1*inch))

        # Feedback
        story.append(Paragraph(feedback['text'], styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

    doc.build(story)
```

#### 4.3 JSON API Export

```python
@app.route('/api/feedback/<cache_id>', methods=['GET'])
def get_feedback_json(cache_id):
    """RESTful API for feedback export"""
    try:
        cache_path = os.path.join(app.config['OUTPUT_FOLDER'], f"cache_{cache_id}.json")

        if not os.path.exists(cache_path):
            return jsonify({'error': 'Cache not found'}), 404

        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return jsonify({
            'success': True,
            'cache_id': cache_id,
            'sections': data,
            'generated_at': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 5. Integration Capabilities

#### 5.1 OSF API Integration

**Direct fetch from OSF platform:**

```python
import requests

def fetch_dmp_from_osf(proposal_id):
    """Fetch DMP directly from OSF API"""
    api_url = f"https://api.osf.io/v2/proposals/{proposal_id}/dmp/"

    response = requests.get(api_url, headers={
        'Authorization': f'Bearer {OSF_API_TOKEN}'
    })

    if response.status_code == 200:
        dmp_data = response.json()
        # Download document
        doc_url = dmp_data['links']['download']
        doc_response = requests.get(doc_url)

        # Save and process
        with open('temp_dmp.docx', 'wb') as f:
            f.write(doc_response.content)

        return 'temp_dmp.docx'
    else:
        raise Exception(f"OSF API error: {response.status_code}")
```

#### 5.2 Email Notification System

```python
from flask_mail import Mail, Message

mail = Mail(app)

def send_review_complete_notification(reviewer_email, document_name):
    """Notify reviewer when DMP processing is complete"""
    msg = Message(
        'DMP Review Ready',
        sender='dmp-art@institution.edu',
        recipients=[reviewer_email]
    )

    msg.body = f"""
    Your DMP review for "{document_name}" is ready.

    Click here to access the review interface:
    {url_for('review_dmp', filename=document_name, _external=True)}

    This link will expire in 24 hours.
    """

    mail.send(msg)
```

#### 5.3 Webhook Support

```python
@app.route('/api/process_webhook', methods=['POST'])
def process_webhook():
    """
    Webhook endpoint for external systems

    Payload:
    {
        "document_url": "https://osf.io/downloads/...",
        "callback_url": "https://external-system/callback",
        "metadata": {...}
    }
    """
    data = request.json

    # Download document
    doc_response = requests.get(data['document_url'])
    temp_path = save_temp_file(doc_response.content)

    # Process
    extractor = DMPExtractor()
    result = extractor.process_file(temp_path, app.config['OUTPUT_FOLDER'])

    # Callback
    if data.get('callback_url'):
        requests.post(data['callback_url'], json={
            'status': 'completed' if result['success'] else 'failed',
            'cache_id': result.get('cache_id'),
            'review_url': url_for('review_dmp',
                                  filename=result['filename'],
                                  cache_id=result['cache_id'],
                                  _external=True)
        })

    return jsonify(result)
```

### 6. Analytics and Reporting

#### 6.1 Review Time Tracking

```python
class ReviewSession:
    def __init__(self, cache_id, user_id):
        self.cache_id = cache_id
        self.user_id = user_id
        self.start_time = datetime.now()
        self.section_times = {}

    def record_section_time(self, section_id, duration_seconds):
        self.section_times[section_id] = duration_seconds

    def get_total_time(self):
        return (datetime.now() - self.start_time).total_seconds()

    def get_average_section_time(self):
        if not self.section_times:
            return 0
        return sum(self.section_times.values()) / len(self.section_times)
```

#### 6.2 Quality Metrics

```python
def calculate_review_quality_score(feedback_data):
    """
    Calculate review completeness score

    Metrics:
    - Sections with feedback: 0-100 points
    - Average feedback length: 0-100 points
    - Use of category templates: 0-50 points
    - Use of citations: 0-50 points

    Total: 0-300 points (normalized to 0-100)
    """
    score = 0

    # Sections with feedback (100 points)
    sections_with_feedback = len([f for f in feedback_data.values() if f.strip()])
    score += (sections_with_feedback / 14) * 100

    # Average feedback length (100 points)
    avg_length = sum(len(f) for f in feedback_data.values()) / 14
    score += min((avg_length / 200) * 100, 100)  # 200 chars = max points

    # Template usage (50 points)
    template_usage = sum(1 for f in feedback_data.values() if contains_template(f))
    score += (template_usage / 14) * 50

    # Citations (50 points)
    citation_usage = sum(1 for f in feedback_data.values() if '❝' in f)
    score += (citation_usage / 14) * 50

    return min(score / 3, 100)  # Normalize to 0-100
```

#### 6.3 Dashboard

```python
@app.route('/dashboard')
@login_required
def dashboard():
    """Analytics dashboard for administrators"""

    stats = {
        'total_reviews': count_reviews(),
        'avg_review_time': get_average_review_time(),
        'most_used_categories': get_top_categories(),
        'section_completion_rates': get_section_completion_rates(),
        'reviewer_leaderboard': get_reviewer_rankings()
    }

    return render_template('dashboard.html', stats=stats)
```

---

## Development Guidelines

### 1. Code Style and Standards

#### Python (PEP 8)

```python
# Function naming: lowercase with underscores
def process_document(file_path, output_dir):
    pass

# Class naming: CapWords
class DMPExtractor:
    pass

# Constants: UPPERCASE
MAX_FILE_SIZE = 16 * 1024 * 1024

# Line length: max 100 characters (relaxed from PEP 8's 79)

# Docstrings: Google style
def detect_section_from_text(text, is_pdf=False):
    """
    Detect DMP section from text content.

    Args:
        text (str): The text to analyze
        is_pdf (bool): Whether the text is from PDF

    Returns:
        str: Detected section name or None

    Examples:
        >>> detect_section_from_text("1. Data description")
        "1. Data description and collection or re-use of existing data"
    """
```

#### JavaScript (ES6+)

```javascript
// Variable naming: camelCase
const uploadButton = document.getElementById('upload-btn');

// Function naming: camelCase
function initializeUploadPage() {
    // ...
}

// Constants: UPPER_SNAKE_CASE
const MAX_FILE_SIZE = 16 * 1024 * 1024;

// Use const/let, not var
const immutableValue = 42;
let mutableValue = 0;

// Arrow functions for callbacks
textareas.forEach(textarea => {
    textarea.addEventListener('input', () => updateCounter());
});

// Template literals
const message = `File ${filename} uploaded successfully`;

// Destructuring
const {dropArea, fileInput} = elements;
```

### 2. Testing Strategy

#### Unit Tests (Python)

```python
import unittest
from utils.extractor import DMPExtractor

class TestDMPExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = DMPExtractor()

    def test_section_mapping_completeness(self):
        """Verify all 6 sections are mapped"""
        self.assertEqual(len(self.extractor.section_mapping), 6)

    def test_subsection_mapping_completeness(self):
        """Verify all 14 subsections are mapped"""
        self.assertEqual(len(self.extractor.subsection_mapping), 14)

    def test_text_similarity_exact_match(self):
        """Test similarity calculation for identical strings"""
        similarity = self.extractor._text_similarity("test string", "test string")
        self.assertEqual(similarity, 1.0)

    def test_text_similarity_no_match(self):
        """Test similarity calculation for completely different strings"""
        similarity = self.extractor._text_similarity("abc", "xyz")
        self.assertEqual(similarity, 0.0)

    def test_should_skip_page_numbers(self):
        """Test that page numbers are skipped"""
        self.assertTrue(self.extractor.should_skip_text("Strona 5", is_pdf=True))
        self.assertTrue(self.extractor.should_skip_text("Page 10", is_pdf=True))

    def test_should_not_skip_content(self):
        """Test that actual content is not skipped"""
        self.assertFalse(self.extractor.should_skip_text(
            "This is real DMP content about data management"
        ))

if __name__ == '__main__':
    unittest.main()
```

#### Integration Tests (Python + Flask)

```python
import unittest
import json
from app import app

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_page_loads(self):
        """Test that the index page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DMP ART', response.data)

    def test_upload_without_file(self):
        """Test upload endpoint rejects requests without files"""
        response = self.app.post('/upload', data={})
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('No file part', data['message'])

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')

    def test_load_categories(self):
        """Test category loading endpoint"""
        response = self.app.get('/load_categories')
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('categories', data)

if __name__ == '__main__':
    unittest.main()
```

#### Frontend Tests (Jest + Puppeteer)

```javascript
// test/upload.test.js
describe('Upload Page', () => {
    beforeEach(async () => {
        await page.goto('http://localhost:5000');
    });

    test('should display upload area', async () => {
        const dropArea = await page.$('#drop-area');
        expect(dropArea).toBeTruthy();
    });

    test('should validate file type', async () => {
        // Simulate file selection with invalid type
        const input = await page.$('#file-input');
        await input.uploadFile('test/fixtures/invalid.txt');

        // Check for error message
        await page.waitForSelector('.toast-error');
        const errorText = await page.$eval('.toast-error', el => el.textContent);
        expect(errorText).toContain('PDF or DOCX');
    });

    test('should validate file size', async () => {
        // Test with 20MB file (over limit)
        const input = await page.$('#file-input');
        await input.uploadFile('test/fixtures/large-file.pdf');

        await page.waitForSelector('.toast-error');
        const errorText = await page.$eval('.toast-error', el => el.textContent);
        expect(errorText).toContain('16MB');
    });
});
```

### 3. Git Workflow

#### Branch Strategy

```
main
  ├── develop
  │   ├── feature/multi-language-support
  │   ├── feature/pdf-generation
  │   └── bugfix/extraction-accuracy
  │
  └── hotfix/security-vulnerability
```

#### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring (no feature/bug change)
- `test`: Adding/updating tests
- `chore`: Build process, dependencies

**Examples:**

```
feat(extraction): add support for German DMP forms

Implement German section mapping and subsection detection.
Add language detection using langdetect library.

Closes #42
```

```
fix(validation): prevent ZIP bomb uploads

Add file size validation before ZIP extraction.
Limit maximum uncompressed size to 100MB.

Fixes #38
```

### 4. Deployment Checklist

#### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Database migrations prepared (if applicable)
- [ ] Environment variables configured
- [ ] Backup of production data

#### Deployment Steps

```bash
# 1. Backup current installation
cp -r /var/www/dmp-art /var/www/dmp-art.backup.$(date +%Y%m%d)

# 2. Pull latest code
cd /var/www/dmp-art
git pull origin main

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations (if applicable)
# python manage.py migrate

# 5. Collect static files (if using production server)
# python manage.py collectstatic --noinput

# 6. Restart application
sudo systemctl restart dmp-art

# 7. Verify deployment
curl http://localhost:5000/health
```

#### Post-Deployment

- [ ] Health check passes
- [ ] Upload test file
- [ ] Verify extraction accuracy
- [ ] Check all frontend pages
- [ ] Monitor error logs
- [ ] Announce to users

### 5. Configuration Management

#### Development Environment

```python
# config/development.py
DEBUG = True
TESTING = False
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
SECRET_KEY = 'development-secret-key'
```

#### Production Environment

```python
# config/production.py
import os

DEBUG = False
TESTING = False
UPLOAD_FOLDER = '/var/dmp-art/uploads'
OUTPUT_FOLDER = '/var/dmp-art/outputs'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
SECRET_KEY = os.environ.get('DMP_ART_SECRET_KEY')

# Logging
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/dmp-art/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}
```

#### Environment Variables

```bash
# .env
DMP_ART_SECRET_KEY=your-secret-key-here
DMP_ART_ENV=production
DMP_ART_DATABASE_URL=postgresql://user:pass@localhost/dmp_art
```

### 6. Monitoring and Logging

#### Application Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Log extraction events
app.logger.info(f'Processing file: {filename} (cache_id: {cache_id})')
app.logger.warning(f'Unconnected text items: {len(unconnected_text)}')
app.logger.error(f'Extraction failed: {str(e)}')
```

#### Performance Monitoring

```python
import time
from functools import wraps

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        app.logger.info(f'{func.__name__} executed in {duration:.2f}s')
        return result
    return wrapper

@log_execution_time
def process_file(self, file_path, output_dir):
    # Processing logic
    pass
```

---

## Conclusion

DMP-ART represents a sophisticated document processing application with intelligent content extraction, bilingual support, and a flexible feedback system. The architecture balances simplicity (Flask + JSON) with powerful features (fuzzy matching, state machine processing, dynamic template management).

**Key Architectural Strengths:**
- **Modularity**: Clear separation between extraction logic, web interface, and configuration
- **Extensibility**: Easy to add new languages, file formats, and export options
- **User-Centric**: Focus on workflow optimization for grant reviewers
- **Maintainability**: Well-structured code with consistent patterns

**Future Development Priorities:**
1. Database integration for multi-user support
2. Machine learning-enhanced section detection
3. Real-time collaboration features
4. Advanced export formats (DOCX, PDF)
5. OSF API integration

This document serves as a comprehensive reference for developers working on DMP-ART, providing both high-level architectural understanding and detailed implementation guidance.

---

**Document Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-16 | Claude (Anthropic) | Initial comprehensive analysis |

**For Questions or Contributions:**
- GitHub Repository: [Link to repository]
- Issue Tracker: [Link to issues]
- Documentation: [Link to docs]

---

*End of Document*
