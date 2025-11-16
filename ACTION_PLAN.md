# DMP-ART: Optimization and Development Action Plan

**Version:** 1.0
**Date:** 2025-11-16
**Status:** Planning Phase
**Estimated Total Timeline:** 6 months

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Quick Wins & Critical Fixes (1-2 weeks)](#phase-1-quick-wins--critical-fixes-1-2-weeks)
3. [Phase 2: Performance Optimization (2-4 weeks)](#phase-2-performance-optimization-2-4-weeks)
4. [Phase 3: Feature Enhancements (1-2 months)](#phase-3-feature-enhancements-1-2-months)
5. [Phase 4: Architecture & Scalability (2-3 months)](#phase-4-architecture--scalability-2-3-months)
6. [Phase 5: Advanced Features (3-6 months)](#phase-5-advanced-features-3-6-months)
7. [Success Metrics](#success-metrics)
8. [Risk Assessment](#risk-assessment)

---

## Executive Summary

This action plan provides a comprehensive roadmap for optimizing and enhancing DMP-ART from its current state (v0.8) to a production-ready, scalable application (v2.0). The plan is organized into 5 phases, each building on the previous one, with clear deliverables and success criteria.

**Key Objectives:**
- ✅ Improve application security and stability
- ✅ Enhance performance and user experience
- ✅ Add enterprise-ready features (auth, analytics, exports)
- ✅ Enable multi-user support and collaboration
- ✅ Implement advanced AI/ML capabilities

---

## Phase 1: Quick Wins & Critical Fixes (1-2 weeks)

**Priority:** 🔴 CRITICAL
**Estimated Effort:** 40-60 hours
**Target Version:** v0.9

### 1.1 Security Enhancements

#### Task 1.1.1: Implement CSRF Protection
**Priority:** CRITICAL
**Effort:** 4 hours

**Implementation:**
```python
# Add to requirements.txt
Flask-WTF==1.2.1

# Add to app.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.environ.get('DMP_ART_SECRET_KEY', 'dev-key-change-in-prod')
```

**Templates Update:**
```html
<!-- All forms need CSRF token -->
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

**Success Criteria:**
- [ ] All POST endpoints protected with CSRF tokens
- [ ] Forms in upload, review, and template editor include tokens
- [ ] Security audit passes

**Files to Modify:**
- `app.py`
- `requirements.txt`
- `templates/index.html`
- `templates/review.html`
- `templates/template_editor.html`

---

#### Task 1.1.2: Add Security Headers
**Priority:** HIGH
**Effort:** 2 hours

**Implementation:**
```python
# Add security headers middleware
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com"
    return response
```

**Success Criteria:**
- [ ] All security headers present in responses
- [ ] Security scanner (e.g., OWASP ZAP) shows no critical issues
- [ ] Application works correctly with CSP enabled

---

### 1.2 Testing Infrastructure

#### Task 1.2.1: Set Up Unit Testing Framework
**Priority:** HIGH
**Effort:** 8 hours

**Implementation:**
```bash
# Add to requirements.txt
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
```

**Create test structure:**
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── __init__.py
│   ├── test_extractor.py
│   └── test_utils.py
├── integration/
│   ├── __init__.py
│   ├── test_routes.py
│   └── test_upload_workflow.py
└── fixtures/
    ├── sample.pdf
    └── sample.docx
```

**Sample Test File:**
```python
# tests/unit/test_extractor.py
import pytest
from utils.extractor import DMPExtractor

class TestDMPExtractor:
    def test_text_similarity_exact_match(self):
        extractor = DMPExtractor()
        similarity = extractor._text_similarity("test", "test")
        assert similarity == 1.0

    def test_section_mapping_completeness(self):
        extractor = DMPExtractor()
        assert len(extractor.section_mapping) == 6
        assert len(extractor.subsection_mapping) == 14
```

**Success Criteria:**
- [ ] Test framework set up and running
- [ ] 20+ unit tests for DMPExtractor
- [ ] 10+ integration tests for Flask routes
- [ ] Code coverage > 60%
- [ ] CI/CD pipeline configured (GitHub Actions)

---

#### Task 1.2.2: Add GitHub Actions CI/CD
**Priority:** MEDIUM
**Effort:** 4 hours

**Create `.github/workflows/tests.yml`:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest --cov=utils --cov=app tests/

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

**Success Criteria:**
- [ ] CI runs on every push and PR
- [ ] Tests must pass before merge
- [ ] Coverage reports generated

---

### 1.3 Performance Quick Wins

#### Task 1.3.1: Compile Regex Patterns
**Priority:** HIGH
**Effort:** 3 hours

**Current Issue:** Regex patterns compiled on every call (performance.md reference)

**Implementation:**
```python
# In utils/extractor.py __init__
class DMPExtractor:
    def __init__(self):
        # Existing initialization...

        # Pre-compile all regex patterns
        self.skip_patterns_compiled = [
            re.compile(r"Strona \d+", re.IGNORECASE),
            re.compile(r"Page \d+", re.IGNORECASE),
            re.compile(r"ID: \d+", re.IGNORECASE),
            re.compile(r"\[wydruk roboczy\]", re.IGNORECASE),
            re.compile(r"OSF,", re.IGNORECASE),
            re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", re.IGNORECASE),
            # ... all 20+ patterns
        ]

        self.section_pattern = re.compile(r'^\s*(\d+)\.\s*(.*?)$')
        self.grant_header_pattern = re.compile(r'OPUS-\d+')

    def should_skip_text(self, text, is_pdf=False):
        for pattern in self.skip_patterns_compiled:
            if pattern.search(text):
                return True
        return False
```

**Expected Performance Improvement:**
- 15-20% faster document processing
- Reduced CPU usage during extraction

**Success Criteria:**
- [ ] All regex patterns pre-compiled
- [ ] Benchmark shows >15% speed improvement
- [ ] No regression in extraction accuracy

---

#### Task 1.3.2: Implement Cache Cleanup
**Priority:** HIGH
**Effort:** 6 hours

**Current Issue:** Cache files accumulate indefinitely (CLAUDE.md ADR 2)

**Implementation:**
```python
# Add to requirements.txt
APScheduler==3.10.4

# Create utils/cache_manager.py
import os
import time
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, output_dir, max_age_hours=24):
        self.output_dir = output_dir
        self.max_age_seconds = max_age_hours * 3600

    def cleanup_old_caches(self):
        """Remove cache files older than max_age_hours"""
        current_time = time.time()
        removed_count = 0

        for filename in os.listdir(self.output_dir):
            if filename.startswith('cache_') and filename.endswith('.json'):
                file_path = os.path.join(self.output_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)

                if file_age > self.max_age_seconds:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        print(f"Removed old cache: {filename}")
                    except Exception as e:
                        print(f"Error removing {filename}: {str(e)}")

        return removed_count

    def get_cache_stats(self):
        """Return statistics about cache files"""
        total_size = 0
        file_count = 0
        oldest_file = None
        oldest_time = time.time()

        for filename in os.listdir(self.output_dir):
            if filename.startswith('cache_') and filename.endswith('.json'):
                file_path = os.path.join(self.output_dir, filename)
                file_count += 1
                total_size += os.path.getsize(file_path)

                mtime = os.path.getmtime(file_path)
                if mtime < oldest_time:
                    oldest_time = mtime
                    oldest_file = filename

        return {
            'total_files': file_count,
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_file': oldest_file,
            'oldest_age_hours': (time.time() - oldest_time) / 3600 if oldest_file else 0
        }

# In app.py
from apscheduler.schedulers.background import BackgroundScheduler
from utils.cache_manager import CacheManager

cache_manager = CacheManager(app.config['OUTPUT_FOLDER'], max_age_hours=24)

# Schedule cleanup every hour
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=cache_manager.cleanup_old_caches,
    trigger="interval",
    hours=1
)
scheduler.start()

# Add cache stats endpoint
@app.route('/admin/cache-stats')
def cache_stats():
    stats = cache_manager.get_cache_stats()
    return jsonify(stats)
```

**Success Criteria:**
- [ ] Cache files automatically cleaned after 24 hours
- [ ] Admin endpoint shows cache statistics
- [ ] No impact on active review sessions
- [ ] Disk usage monitoring dashboard

---

### 1.4 Error Handling & Logging

#### Task 1.4.1: Comprehensive Logging System
**Priority:** HIGH
**Effort:** 5 hours

**Implementation:**
```python
# Add to requirements.txt
python-json-logger==2.0.7

# Create config/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

def setup_logging(app):
    """Configure structured logging"""

    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # JSON formatter for structured logs
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.INFO)

    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setFormatter(json_formatter)
    error_handler.setLevel(logging.ERROR)

    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)

    return app.logger

# In app.py
from config.logging_config import setup_logging

logger = setup_logging(app)

# Add logging to key operations
@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info('File upload initiated', extra={
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string
    })

    try:
        # ... existing code ...
        logger.info('File processed successfully', extra={
            'filename': filename,
            'cache_id': result.get('cache_id'),
            'processing_time': elapsed_time
        })
    except Exception as e:
        logger.error('File processing failed', extra={
            'filename': filename,
            'error': str(e),
            'traceback': traceback.format_exc()
        })
```

**Success Criteria:**
- [ ] Structured JSON logs for all operations
- [ ] Log rotation configured
- [ ] Error tracking with full context
- [ ] Integration with monitoring tools ready

---

### 1.5 Documentation Updates

#### Task 1.5.1: Add API Documentation
**Priority:** MEDIUM
**Effort:** 4 hours

**Create `docs/API.md`:**
```markdown
# DMP-ART API Documentation

## Endpoints

### POST /upload
Upload and process a DMP document.

**Request:**
- Content-Type: multipart/form-data
- Body: file (PDF or DOCX, max 16MB)

**Response:**
```json
{
  "success": true,
  "redirect": "/review/<filename>?cache_id=<uuid>"
}
```

### GET /review/<filename>
Display review interface for processed document.

... (full API documentation)
```

**Success Criteria:**
- [ ] All endpoints documented
- [ ] Request/response examples provided
- [ ] Error codes documented

---

## Phase 2: Performance Optimization (2-4 weeks)

**Priority:** 🟡 HIGH
**Estimated Effort:** 80-120 hours
**Target Version:** v1.0

### 2.1 Frontend Performance

#### Task 2.1.1: Debounce Character Counters
**Priority:** HIGH
**Effort:** 2 hours

**Current Issue:** Counter updates on every keystroke

**Implementation:**
```javascript
// Add to static/js/script.js
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Update character counter initialization
textareas.forEach(textarea => {
    const updateCounter = debounce(function() {
        const sectionId = this.getAttribute('data-section-id');
        const counter = document.querySelector(`#char-count-${sectionId}`);
        const charCount = this.value.length;
        const wordCount = this.value.trim() ?
            this.value.trim().split(/\s+/).length : 0;
        counter.textContent = `${charCount} characters, ${wordCount} words`;
    }, 300);

    textarea.addEventListener('input', updateCounter);
});
```

**Expected Improvement:**
- Reduced CPU usage during typing
- Smoother user experience
- Better battery life on laptops

**Success Criteria:**
- [ ] Counter updates debounced to 300ms
- [ ] No janky typing experience
- [ ] Performance metrics show improvement

---

#### Task 2.1.2: Event Delegation
**Priority:** MEDIUM
**Effort:** 4 hours

**Current Issue:** Individual listeners for each button

**Implementation:**
```javascript
// Replace individual button listeners with delegation
document.getElementById('sections-container').addEventListener('click', function(e) {
    // Category button handler
    if (e.target.classList.contains('category-btn-inline')) {
        const category = e.target.dataset.category;
        const section = e.target.dataset.section;
        showCategoryComments(category, section);
        return;
    }

    // Quick comment handler
    if (e.target.classList.contains('quick-comment-btn')) {
        const comment = e.target.dataset.comment;
        insertQuickComment(comment);
        return;
    }

    // Cite button handler
    if (e.target.classList.contains('cite-btn')) {
        handleCitation(e);
        return;
    }
});
```

**Success Criteria:**
- [ ] Event listeners reduced from 100+ to <10
- [ ] Memory usage decreased
- [ ] DOM manipulation faster

---

#### Task 2.1.3: Virtual Scrolling for Comments
**Priority:** MEDIUM
**Effort:** 8 hours

**Implementation:**
```javascript
// Create virtual scroll component for quick comments
class VirtualScroll {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleItems = [];
        this.init();
    }

    init() {
        this.container.style.height = `${this.items.length * this.itemHeight}px`;
        this.container.addEventListener('scroll', () => this.render());
        this.render();
    }

    render() {
        const scrollTop = this.container.scrollTop;
        const viewportHeight = this.container.clientHeight;

        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = Math.ceil((scrollTop + viewportHeight) / this.itemHeight);

        // Render only visible items + buffer
        const buffer = 5;
        const renderStart = Math.max(0, startIndex - buffer);
        const renderEnd = Math.min(this.items.length, endIndex + buffer);

        this.renderItems(renderStart, renderEnd);
    }

    renderItems(start, end) {
        // Implementation...
    }
}

// Use for quick comments with 100+ items
const virtualComments = new VirtualScroll(
    document.getElementById('quick-comments-list'),
    QUICK_COMMENTS,
    40 // item height
);
```

**Success Criteria:**
- [ ] Smooth scrolling with 500+ comments
- [ ] Initial render time < 100ms
- [ ] Memory usage stable

---

### 2.2 Backend Performance

#### Task 2.2.1: Optimize Document Parsing
**Priority:** HIGH
**Effort:** 12 hours

**Optimizations:**

1. **Early Filtering:**
```python
def extract_formatted_text(self, paragraph):
    # Quick exit for empty paragraphs
    if not paragraph.text or not paragraph.text.strip():
        return ""

    # Early skip check before expensive operations
    clean_text = self.clean_markup(paragraph.text)
    if self.should_skip_text(clean_text):
        return ""

    # Only process formatting for meaningful content
    formatted_text = self._extract_formatting(paragraph)
    return formatted_text
```

2. **Batch Processing:**
```python
def process_paragraphs_batch(self, paragraphs, batch_size=100):
    """Process paragraphs in batches to reduce memory pressure"""
    for i in range(0, len(paragraphs), batch_size):
        batch = paragraphs[i:i+batch_size]
        yield from self._process_batch(batch)
```

3. **Lazy Loading:**
```python
def process_docx(self, docx_path, output_dir):
    doc = Document(docx_path)

    # Don't load all paragraphs at once
    for paragraph in doc.paragraphs:
        if self._should_process(paragraph):
            yield self.extract_formatted_text(paragraph)
```

**Success Criteria:**
- [ ] 20%+ faster processing time
- [ ] 30%+ lower memory usage
- [ ] No regression in accuracy

---

#### Task 2.2.2: Add Caching for Repeated Operations
**Priority:** MEDIUM
**Effort:** 6 hours

**Implementation:**
```python
from functools import lru_cache

class DMPExtractor:
    @lru_cache(maxsize=128)
    def _text_similarity(self, text1, text2):
        """Cached text similarity calculation"""
        # Existing implementation...

    @lru_cache(maxsize=256)
    def normalize_text(self, text):
        """Cached text normalization"""
        return text.lower().strip().rstrip(':')
```

**Success Criteria:**
- [ ] Repeated similarity calculations cached
- [ ] 10-15% speed improvement
- [ ] Cache hit rate > 40%

---

### 2.3 Database Optimization Prep

#### Task 2.3.1: Add Database Abstraction Layer
**Priority:** MEDIUM
**Effort:** 10 hours

**Purpose:** Prepare for migration from JSON to database

**Implementation:**
```python
# Create data/storage.py
from abc import ABC, abstractmethod
import json
import os

class StorageBackend(ABC):
    @abstractmethod
    def save_category(self, name, data):
        pass

    @abstractmethod
    def load_category(self, name):
        pass

    @abstractmethod
    def list_categories(self):
        pass

class JSONStorage(StorageBackend):
    """Current JSON-based storage"""
    def __init__(self, config_dir='config'):
        self.config_dir = config_dir

    def save_category(self, name, data):
        path = os.path.join(self.config_dir, f"{name}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ... other methods

class DatabaseStorage(StorageBackend):
    """Future database storage"""
    def __init__(self, db_url):
        self.db = self._connect(db_url)

    # ... implementation

# Use abstraction in app.py
storage = JSONStorage(app.config['CONFIG_FOLDER'])
```

**Success Criteria:**
- [ ] All config access goes through storage layer
- [ ] Easy to swap JSON for database
- [ ] Tests pass with both backends

---

## Phase 3: Feature Enhancements (1-2 months)

**Priority:** 🟢 MEDIUM
**Estimated Effort:** 160-240 hours
**Target Version:** v1.5

### 3.1 Export Functionality

#### Task 3.1.1: DOCX Feedback Export
**Priority:** HIGH
**Effort:** 12 hours

**Implementation:**
```python
# Add to requirements.txt
python-docx==1.1.2  # Already present

# Create utils/export_docx.py
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

class DOCXExporter:
    def __init__(self):
        self.doc = Document()
        self._setup_styles()

    def _setup_styles(self):
        """Configure document styles"""
        styles = self.doc.styles

        # Title style
        title_style = styles['Heading 1']
        title_font = title_style.font
        title_font.name = 'Arial'
        title_font.size = Pt(24)
        title_font.color.rgb = RGBColor(44, 62, 80)

    def generate_feedback_report(self, sections_feedback, metadata=None):
        """Generate DOCX report from feedback data"""

        # Title
        title = self.doc.add_heading('DMP Feedback Report', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Metadata
        if metadata:
            self.doc.add_paragraph(f"Document: {metadata.get('filename', 'N/A')}")
            self.doc.add_paragraph(f"Reviewer: {metadata.get('reviewer', 'N/A')}")
        self.doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.doc.add_paragraph()

        # Sections
        for section_id in sorted(sections_feedback.keys()):
            feedback = sections_feedback[section_id]

            if not feedback.get('text', '').strip():
                continue

            # Section header
            heading = self.doc.add_heading(f"Section {section_id}", level=1)

            # Question
            question_para = self.doc.add_paragraph()
            question_run = question_para.add_run(feedback['question'])
            question_run.bold = True
            question_run.font.size = Pt(11)

            # Feedback content
            feedback_para = self.doc.add_paragraph(feedback['text'])
            feedback_para.paragraph_format.left_indent = Inches(0.5)
            feedback_para.paragraph_format.space_after = Pt(12)

            # Separator
            self.doc.add_paragraph('_' * 80)
            self.doc.add_paragraph()

        return self.doc

    def save(self, output_path):
        """Save document to file"""
        self.doc.save(output_path)

# Add route in app.py
@app.route('/export/docx/<cache_id>', methods=['POST'])
def export_docx(cache_id):
    try:
        # Get feedback data from request
        feedback_data = request.json.get('feedback', {})

        # Generate DOCX
        exporter = DOCXExporter()
        doc = exporter.generate_feedback_report(feedback_data, {
            'filename': request.json.get('filename'),
            'reviewer': 'System User'  # Will change with auth
        })

        # Save to temp file
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'feedback_{cache_id}.docx')
        exporter.save(output_path)

        # Return file
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f'DMP_Feedback_{cache_id[:8]}.docx'
        )

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Frontend Integration:**
```javascript
// Add to review page
async function exportAsDOCX() {
    const feedback = collectAllFeedback();

    const response = await fetch(`/export/docx/${CACHE_ID}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            feedback: feedback,
            filename: FILENAME
        })
    });

    if (response.ok) {
        const blob = await response.blob();
        downloadBlob(blob, `DMP_Feedback_${CACHE_ID.substring(0, 8)}.docx`);
    }
}
```

**Success Criteria:**
- [ ] Generate properly formatted DOCX reports
- [ ] Preserve formatting and structure
- [ ] Include metadata (date, reviewer, etc.)
- [ ] Download works in all browsers

---

#### Task 3.1.2: PDF Feedback Export
**Priority:** HIGH
**Effort:** 12 hours

**Implementation:**
```python
# Add to requirements.txt
reportlab==4.0.7

# Create utils/export_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PDFExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configure custom PDF styles"""
        self.styles.add(ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#3498db'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

    def generate_feedback_report(self, output_path, sections_feedback, metadata=None):
        """Generate PDF report"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Title
        story.append(Paragraph("DMP Feedback Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))

        # Metadata
        if metadata:
            meta_text = f"<b>Document:</b> {metadata.get('filename', 'N/A')}<br/>"
            meta_text += f"<b>Reviewer:</b> {metadata.get('reviewer', 'N/A')}<br/>"
            meta_text += f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(meta_text, self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Sections
        for section_id in sorted(sections_feedback.keys()):
            feedback = sections_feedback[section_id]

            if not feedback.get('text', '').strip():
                continue

            # Section header
            story.append(Paragraph(f"Section {section_id}", self.styles['SectionHeader']))

            # Question
            question_text = f"<b>{feedback['question']}</b>"
            story.append(Paragraph(question_text, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

            # Feedback
            story.append(Paragraph(feedback['text'], self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

        # Build PDF
        doc.build(story)

# Add route
@app.route('/export/pdf/<cache_id>', methods=['POST'])
def export_pdf(cache_id):
    # Similar to DOCX export...
```

**Success Criteria:**
- [ ] Professional-looking PDF reports
- [ ] Proper pagination
- [ ] Unicode support (Polish characters)
- [ ] File size < 500KB for typical report

---

### 3.2 Enhanced Extraction

#### Task 3.2.1: Table Structure Preservation
**Priority:** MEDIUM
**Effort:** 16 hours

**Current Issue:** Tables extracted as plain text, structure lost

**Implementation:**
```python
# Enhance utils/extractor.py
def extract_table_structure(self, table):
    """
    Extract table with preserved structure

    Returns:
        {
            'headers': ['Column 1', 'Column 2', ...],
            'rows': [
                {'Column 1': 'Value 1', 'Column 2': 'Value 2'},
                ...
            ],
            'metadata': {
                'row_count': int,
                'col_count': int,
                'has_header': bool
            }
        }
    """
    if not table.rows:
        return None

    # Detect if first row is header
    first_row = table.rows[0]
    has_header = self._is_header_row(first_row)

    # Extract headers
    headers = []
    start_idx = 0

    if has_header:
        for cell in first_row.cells:
            headers.append(cell.text.strip())
        start_idx = 1
    else:
        # Generate generic headers
        col_count = len(first_row.cells)
        headers = [f"Column {i+1}" for i in range(col_count)]

    # Extract rows
    rows = []
    for row in table.rows[start_idx:]:
        row_data = {}
        for idx, cell in enumerate(row.cells):
            if idx < len(headers):
                row_data[headers[idx]] = cell.text.strip()
        rows.append(row_data)

    return {
        'headers': headers,
        'rows': rows,
        'metadata': {
            'row_count': len(rows),
            'col_count': len(headers),
            'has_header': has_header
        }
    }

def _is_header_row(self, row):
    """Heuristic to detect header rows"""
    # Check if cells are bold or have different styling
    bold_count = 0
    for cell in row.cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                if run.bold:
                    bold_count += 1
                    break

    # If >50% of cells are bold, likely a header
    return bold_count > len(row.cells) / 2
```

**Cache Format Update:**
```json
{
  "1.1": {
    "section": "...",
    "question": "...",
    "paragraphs": [...],
    "tables": [
      {
        "headers": ["Budget Item", "Amount", "Year"],
        "rows": [
          {"Budget Item": "Equipment", "Amount": "50000", "Year": "2025"},
          {"Budget Item": "Personnel", "Amount": "120000", "Year": "2025"}
        ],
        "metadata": {"row_count": 2, "col_count": 3, "has_header": true}
      }
    ]
  }
}
```

**Frontend Display:**
```html
<!-- Enhanced review template -->
{% if section.tables %}
<div class="extracted-tables">
    <h4>Tables:</h4>
    {% for table in section.tables %}
    <table class="dmp-table">
        <thead>
            <tr>
                {% for header in table.headers %}
                <th>{{ header }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in table.rows %}
            <tr>
                {% for header in table.headers %}
                <td>{{ row[header] }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endfor %}
</div>
{% endif %}
```

**Success Criteria:**
- [ ] Tables displayed with proper structure
- [ ] Headers correctly identified
- [ ] Data searchable and citable
- [ ] Export includes table formatting

---

### 3.3 Analytics & Tracking

#### Task 3.3.1: Review Time Tracking
**Priority:** MEDIUM
**Effort:** 10 hours

**Implementation:**
```javascript
// Create static/js/analytics.js
class ReviewAnalytics {
    constructor(cacheId) {
        this.cacheId = cacheId;
        this.sessionStart = Date.now();
        this.sectionTimes = {};
        this.currentSection = null;
        this.sectionStartTime = null;

        this.init();
    }

    init() {
        // Track section focus
        document.querySelectorAll('[id^="section-"]').forEach(section => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.onSectionEnter(entry.target.id);
                    } else {
                        this.onSectionExit(entry.target.id);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(section);
        });

        // Track page visibility
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseTracking();
            } else {
                this.resumeTracking();
            }
        });

        // Save on page unload
        window.addEventListener('beforeunload', () => {
            this.save();
        });

        // Auto-save every 30 seconds
        setInterval(() => this.save(), 30000);
    }

    onSectionEnter(sectionId) {
        if (this.currentSection !== sectionId) {
            this.onSectionExit(this.currentSection);
            this.currentSection = sectionId;
            this.sectionStartTime = Date.now();
        }
    }

    onSectionExit(sectionId) {
        if (sectionId && this.sectionStartTime) {
            const duration = Date.now() - this.sectionStartTime;
            this.sectionTimes[sectionId] = (this.sectionTimes[sectionId] || 0) + duration;
        }
    }

    pauseTracking() {
        this.onSectionExit(this.currentSection);
        this.currentSection = null;
    }

    resumeTracking() {
        // Will resume when section becomes visible
    }

    getStats() {
        return {
            cache_id: this.cacheId,
            total_time: Date.now() - this.sessionStart,
            section_times: this.sectionTimes,
            timestamp: new Date().toISOString()
        };
    }

    async save() {
        const stats = this.getStats();

        try {
            await fetch('/api/analytics/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(stats)
            });
        } catch (error) {
            console.error('Failed to save analytics:', error);
        }
    }
}

// Initialize on review page
if (document.body.getAttribute('data-page') === 'review') {
    const analytics = new ReviewAnalytics(CACHE_ID);
}
```

**Backend Storage:**
```python
# Add route
@app.route('/api/analytics/save', methods=['POST'])
def save_analytics():
    try:
        data = request.json
        cache_id = data['cache_id']

        # Save to JSON file (later: database)
        analytics_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'analytics_{cache_id}.json'
        )

        with open(analytics_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Add analytics retrieval
@app.route('/api/analytics/<cache_id>')
def get_analytics(cache_id):
    analytics_path = os.path.join(
        app.config['OUTPUT_FOLDER'],
        f'analytics_{cache_id}.json'
    )

    if os.path.exists(analytics_path):
        with open(analytics_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)

    return jsonify({'error': 'Analytics not found'}), 404
```

**Success Criteria:**
- [ ] Accurate time tracking per section
- [ ] Handles page visibility changes
- [ ] Data persists across sessions
- [ ] Minimal performance impact

---

#### Task 3.3.2: Quality Metrics
**Priority:** LOW
**Effort:** 8 hours

**Implementation:**
```python
# Create utils/quality_metrics.py
class ReviewQualityAnalyzer:
    def __init__(self):
        self.max_score = 300

    def calculate_score(self, feedback_data, analytics_data=None):
        """
        Calculate review quality score (0-100)

        Metrics:
        - Completeness: 100 points
        - Depth: 100 points
        - Engagement: 50 points
        - Citations: 50 points
        """
        score = 0

        # 1. Completeness (100 points)
        total_sections = 14
        sections_with_feedback = sum(
            1 for f in feedback_data.values()
            if f.get('text', '').strip()
        )
        score += (sections_with_feedback / total_sections) * 100

        # 2. Depth (100 points)
        avg_feedback_length = sum(
            len(f.get('text', ''))
            for f in feedback_data.values()
        ) / total_sections

        # 200 chars = full points
        depth_score = min((avg_feedback_length / 200) * 100, 100)
        score += depth_score

        # 3. Engagement (50 points)
        if analytics_data:
            total_time = analytics_data.get('total_time', 0) / 1000  # to seconds
            # 30 minutes = full points
            engagement_score = min((total_time / 1800) * 50, 50)
            score += engagement_score

        # 4. Citations (50 points)
        citation_count = sum(
            f.get('text', '').count('❝')
            for f in feedback_data.values()
        )
        # 7 citations (50% of sections) = full points
        citation_score = min((citation_count / 7) * 50, 50)
        score += citation_score

        # Normalize to 0-100
        final_score = min(score / 3, 100)

        return {
            'overall_score': round(final_score, 2),
            'completeness': round((sections_with_feedback / total_sections) * 100, 2),
            'depth': round(depth_score, 2),
            'engagement': round(engagement_score, 2) if analytics_data else 0,
            'citations': round(citation_score, 2),
            'sections_completed': sections_with_feedback,
            'avg_feedback_length': round(avg_feedback_length, 2),
            'total_citations': citation_count
        }
```

**Success Criteria:**
- [ ] Meaningful quality metrics
- [ ] Helpful for self-assessment
- [ ] Displayed in review interface

---

## Phase 4: Architecture & Scalability (2-3 months)

**Priority:** 🟠 MEDIUM
**Estimated Effort:** 240-360 hours
**Target Version:** v2.0

### 4.1 Database Migration

#### Task 4.1.1: SQLite Implementation
**Priority:** HIGH
**Effort:** 24 hours

**Implementation:**
```python
# Add to requirements.txt
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5

# Create models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    documents = db.relationship('Document', backref='user', lazy=True)
    templates = db.relationship('Template', backref='user', lazy=True)

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    cache_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')
    file_size = db.Column(db.Integer)

    extracted_content = db.relationship('ExtractedContent', backref='document', lazy=True, cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='document', lazy=True, cascade='all, delete-orphan')

class ExtractedContent(db.Model):
    __tablename__ = 'extracted_content'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    section_id = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text)
    tables = db.Column(db.JSON)  # Store table structures
    extracted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_document_section', 'document_id', 'section_id'),
    )

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    section_id = db.Column(db.String(10), nullable=False)
    feedback_text = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Template(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.String(10), nullable=False)
    template_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.Index('idx_category_section', 'category', 'section_id'),
    )

class Analytics(db.Model):
    __tablename__ = 'analytics'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    session_data = db.Column(db.JSON)
    total_time = db.Column(db.Integer)  # seconds
    completed_at = db.Column(db.DateTime)

    document = db.relationship('Document', backref='analytics')

# Update app.py
from models import db, User, Document, ExtractedContent, Feedback

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dmp_art.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
```

**Migration Script:**
```python
# scripts/migrate_json_to_db.py
import json
import os
from app import app, db
from models import Template, User

def migrate_templates():
    """Migrate JSON templates to database"""

    # Create system user
    system_user = User(
        username='system',
        email='system@dmp-art.local',
        password_hash='not-used',
        is_admin=True
    )
    db.session.add(system_user)
    db.session.commit()

    config_dir = 'config'

    # Migrate category files
    for filename in os.listdir(config_dir):
        if not filename.endswith('.json'):
            continue

        if filename in ['dmp_structure.json', 'quick_comments.json']:
            continue

        category_name = filename.replace('.json', '')
        filepath = os.path.join(config_dir, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Migrate each section's templates
        for section_id, templates in data.items():
            if isinstance(templates, list):
                for template_text in templates:
                    template = Template(
                        user_id=system_user.id,
                        category=category_name,
                        section_id=section_id,
                        template_text=template_text,
                        is_shared=True
                    )
                    db.session.add(template)

    db.session.commit()
    print("Migration complete!")

if __name__ == '__main__':
    with app.app_context():
        migrate_templates()
```

**Success Criteria:**
- [ ] All JSON data migrated to SQLite
- [ ] Database queries functional
- [ ] Performance maintained or improved
- [ ] Migration script tested and documented

---

### 4.2 User Authentication

#### Task 4.2.1: Implement Flask-Login
**Priority:** HIGH
**Effort:** 20 hours

**Implementation:**
```python
# Add to requirements.txt
Flask-Login==0.6.3
bcrypt==4.1.2

# Update models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    # ... existing fields ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Update app.py
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validation
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'})

        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'})

        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))

        return jsonify({'success': False, 'message': 'Invalid credentials'})

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Protect routes
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    # ... existing code ...
    # Associate document with current_user
    doc = Document(
        user_id=current_user.id,
        filename=filename,
        original_filename=file.filename
    )
    db.session.add(doc)
    db.session.commit()
```

**Create Templates:**
```html
<!-- templates/login.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Login - DMP ART</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="auth-container">
        <h1>Login to DMP ART</h1>

        <form method="POST" id="login-form">
            {{ csrf_token() }}

            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>

            <button type="submit">Login</button>
        </form>

        <p>Don't have an account? <a href="{{ url_for('register') }}">Register</a></p>
    </div>
</body>
</html>
```

**Success Criteria:**
- [ ] User registration functional
- [ ] Login/logout working
- [ ] Password hashing secure
- [ ] Session management robust
- [ ] Protected routes enforced

---

### 4.3 Admin Dashboard

#### Task 4.3.1: Create Analytics Dashboard
**Priority:** MEDIUM
**Effort:** 24 hours

**Implementation:**
```python
# Create routes/admin.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, Document, Analytics

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return "Access denied", 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_documents': Document.query.count(),
        'documents_today': Document.query.filter(
            Document.uploaded_at >= datetime.now().date()
        ).count(),
        'avg_review_time': db.session.query(
            db.func.avg(Analytics.total_time)
        ).scalar() or 0,
        'completion_rate': calculate_completion_rate(),
        'top_reviewers': get_top_reviewers(),
        'recent_activity': get_recent_activity()
    }

    return render_template('admin/dashboard.html', stats=stats)

def calculate_completion_rate():
    """Calculate percentage of documents with complete reviews"""
    total = Document.query.count()
    if total == 0:
        return 0

    completed = Document.query.filter_by(status='completed').count()
    return round((completed / total) * 100, 2)

def get_top_reviewers(limit=10):
    """Get users with most completed reviews"""
    return db.session.query(
        User.username,
        db.func.count(Document.id).label('review_count')
    ).join(Document).group_by(User.id).order_by(
        db.desc('review_count')
    ).limit(limit).all()

def get_recent_activity(limit=20):
    """Get recent document uploads"""
    return Document.query.order_by(
        Document.uploaded_at.desc()
    ).limit(limit).all()

# Register blueprint in app.py
from routes.admin import admin_bp
app.register_blueprint(admin_bp)
```

**Dashboard Template:**
```html
<!-- templates/admin/dashboard.html -->
{% extends "base.html" %}

{% block content %}
<div class="admin-dashboard">
    <h1>Admin Dashboard</h1>

    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Users</h3>
            <p class="stat-value">{{ stats.total_users }}</p>
        </div>

        <div class="stat-card">
            <h3>Total Documents</h3>
            <p class="stat-value">{{ stats.total_documents }}</p>
        </div>

        <div class="stat-card">
            <h3>Documents Today</h3>
            <p class="stat-value">{{ stats.documents_today }}</p>
        </div>

        <div class="stat-card">
            <h3>Avg Review Time</h3>
            <p class="stat-value">{{ (stats.avg_review_time / 60) | round(1) }} min</p>
        </div>

        <div class="stat-card">
            <h3>Completion Rate</h3>
            <p class="stat-value">{{ stats.completion_rate }}%</p>
        </div>
    </div>

    <div class="dashboard-section">
        <h2>Top Reviewers</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Username</th>
                    <th>Reviews</th>
                </tr>
            </thead>
            <tbody>
                {% for reviewer in stats.top_reviewers %}
                <tr>
                    <td>{{ reviewer.username }}</td>
                    <td>{{ reviewer.review_count }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="dashboard-section">
        <h2>Recent Activity</h2>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>User</th>
                    <th>Uploaded</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for doc in stats.recent_activity %}
                <tr>
                    <td>{{ doc.original_filename }}</td>
                    <td>{{ doc.user.username }}</td>
                    <td>{{ doc.uploaded_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td><span class="status-badge status-{{ doc.status }}">{{ doc.status }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

**Success Criteria:**
- [ ] Dashboard displays key metrics
- [ ] Real-time data updates
- [ ] Performance charts visible
- [ ] User activity tracking

---

## Phase 5: Advanced Features (3-6 months)

**Priority:** 🔵 LOW
**Estimated Effort:** 360-480 hours
**Target Version:** v2.5+

### 5.1 Machine Learning Integration

#### Task 5.1.1: ML-Based Section Detection
**Priority:** MEDIUM
**Effort:** 40 hours

**Implementation:**
```python
# Add to requirements.txt
scikit-learn==1.3.2
joblib==1.3.2

# Create ml/section_classifier.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

class SectionClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 3))
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, training_data):
        """
        Train classifier on labeled data

        Args:
            training_data: [(text, section_label), ...]
        """
        if not training_data:
            raise ValueError("Training data cannot be empty")

        texts, labels = zip(*training_data)

        # Vectorize
        X = self.vectorizer.fit_transform(texts)

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42
        )

        # Train
        self.classifier.fit(X_train, y_train)

        # Evaluate
        accuracy = self.classifier.score(X_test, y_test)
        print(f"Classifier accuracy: {accuracy:.2%}")

        self.is_trained = True
        return accuracy

    def predict(self, text):
        """Predict section for given text"""
        if not self.is_trained:
            return None

        X = self.vectorizer.transform([text])
        prediction = self.classifier.predict(X)[0]
        proba = self.classifier.predict_proba(X)[0]

        # Get confidence
        max_proba = max(proba)

        return {
            'section': prediction,
            'confidence': max_proba
        }

    def save(self, model_dir='ml/models'):
        """Save trained model"""
        os.makedirs(model_dir, exist_ok=True)

        joblib.dump(self.vectorizer, os.path.join(model_dir, 'vectorizer.pkl'))
        joblib.dump(self.classifier, os.path.join(model_dir, 'classifier.pkl'))

    def load(self, model_dir='ml/models'):
        """Load trained model"""
        vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
        classifier_path = os.path.join(model_dir, 'classifier.pkl')

        if os.path.exists(vectorizer_path) and os.path.exists(classifier_path):
            self.vectorizer = joblib.load(vectorizer_path)
            self.classifier = joblib.load(classifier_path)
            self.is_trained = True
            return True

        return False

# Training script
# scripts/train_classifier.py
from ml.section_classifier import SectionClassifier
import json

def load_training_data():
    """Load labeled examples from cache files"""
    training_data = []

    # Load from verified cache files
    cache_dir = 'training_data'

    for filename in os.listdir(cache_dir):
        if not filename.startswith('cache_') or not filename.endswith('.json'):
            continue

        with open(os.path.join(cache_dir, filename), 'r', encoding='utf-8') as f:
            cache = json.load(f)

        # Extract labeled paragraphs
        for section_id, content in cache.items():
            if section_id.startswith('_'):
                continue

            section = content['section']
            for paragraph in content.get('paragraphs', []):
                training_data.append((paragraph, section))

    return training_data

if __name__ == '__main__':
    classifier = SectionClassifier()

    print("Loading training data...")
    training_data = load_training_data()
    print(f"Loaded {len(training_data)} examples")

    print("Training classifier...")
    accuracy = classifier.train(training_data)

    print(f"Training complete. Accuracy: {accuracy:.2%}")

    classifier.save()
    print("Model saved!")
```

**Integration with Extractor:**
```python
# In utils/extractor.py
from ml.section_classifier import SectionClassifier

class DMPExtractor:
    def __init__(self, use_ml=False):
        # ... existing init ...

        self.use_ml = use_ml
        if use_ml:
            self.ml_classifier = SectionClassifier()
            if not self.ml_classifier.load():
                print("Warning: ML model not loaded, falling back to rule-based")
                self.use_ml = False

    def detect_section_from_text(self, text, is_pdf=False):
        # Try ML first if enabled
        if self.use_ml:
            prediction = self.ml_classifier.predict(text)
            if prediction and prediction['confidence'] > 0.7:
                return prediction['section']

        # Fallback to rule-based
        return self._detect_section_rule_based(text, is_pdf)
```

**Success Criteria:**
- [ ] Model achieves >85% accuracy
- [ ] Improves extraction for non-standard formats
- [ ] Graceful fallback to rule-based
- [ ] Retraining pipeline documented

---

### 5.2 OSF Integration

#### Task 5.2.1: OSF API Client
**Priority:** MEDIUM
**Effort:** 30 hours

**Implementation:**
```python
# Add to requirements.txt
requests==2.31.0

# Create integrations/osf_client.py
import requests
from typing import Optional, Dict
import os

class OSFClient:
    def __init__(self, api_token=None):
        self.base_url = 'https://api.osf.io/v2'
        self.api_token = api_token or os.environ.get('OSF_API_TOKEN')
        self.session = requests.Session()

        if self.api_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_token}'
            })

    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Fetch proposal data from OSF"""
        try:
            response = self.session.get(f'{self.base_url}/proposals/{proposal_id}/')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching proposal: {e}")
            return None

    def get_dmp_file(self, proposal_id: str) -> Optional[bytes]:
        """Download DMP file from proposal"""
        try:
            # Get proposal
            proposal = self.get_proposal(proposal_id)
            if not proposal:
                return None

            # Get DMP file link
            dmp_link = proposal.get('data', {}).get('links', {}).get('dmp')
            if not dmp_link:
                return None

            # Download file
            response = self.session.get(dmp_link)
            response.raise_for_status()

            return response.content

        except requests.RequestException as e:
            print(f"Error downloading DMP: {e}")
            return None

    def search_proposals(self, filters: Dict) -> Optional[Dict]:
        """Search for proposals with filters"""
        try:
            response = self.session.get(
                f'{self.base_url}/proposals/',
                params=filters
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error searching proposals: {e}")
            return None

# Add route in app.py
from integrations.osf_client import OSFClient

@app.route('/osf/import/<proposal_id>', methods=['POST'])
@login_required
def import_from_osf(proposal_id):
    try:
        osf = OSFClient()

        # Download DMP
        dmp_content = osf.get_dmp_file(proposal_id)
        if not dmp_content:
            return jsonify({
                'success': False,
                'message': 'Failed to download DMP from OSF'
            })

        # Save to temp file
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'osf_{proposal_id}.docx')
        with open(temp_path, 'wb') as f:
            f.write(dmp_content)

        # Process
        extractor = DMPExtractor()
        result = extractor.process_file(temp_path, app.config['OUTPUT_FOLDER'])

        # Cleanup
        os.remove(temp_path)

        if result['success']:
            # Save document record
            doc = Document(
                user_id=current_user.id,
                filename=result['filename'],
                original_filename=f'OSF_{proposal_id}.docx',
                cache_id=result['cache_id']
            )
            db.session.add(doc)
            db.session.commit()

            return jsonify({
                'success': True,
                'redirect': url_for('review_dmp',
                                   filename=result['filename'],
                                   cache_id=result['cache_id'])
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Frontend Integration:**
```html
<!-- Add to index.html -->
<div class="import-section">
    <h2>Import from OSF</h2>

    <form id="osf-import-form">
        <div class="form-group">
            <label for="proposal-id">OSF Proposal ID</label>
            <input type="text" id="proposal-id" name="proposal_id" placeholder="e.g., 5f3k2h">
        </div>

        <button type="submit">Import DMP</button>
    </form>
</div>

<script>
document.getElementById('osf-import-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const proposalId = document.getElementById('proposal-id').value;

    const response = await fetch(`/osf/import/${proposalId}`, {
        method: 'POST'
    });

    const result = await response.json();

    if (result.success) {
        window.location.href = result.redirect;
    } else {
        showToast(result.message, 'error');
    }
});
</script>
```

**Success Criteria:**
- [ ] Successfully fetch DMPs from OSF
- [ ] Handle authentication
- [ ] Error handling for network issues
- [ ] Integration tested with real OSF data

---

### 5.3 Collaborative Features

#### Task 5.3.1: Multi-Reviewer Support
**Priority:** LOW
**Effort:** 36 hours

**Implementation:**
```python
# Add to models.py
class DocumentReviewer(db.Model):
    __tablename__ = 'document_reviewers'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), default='reviewer')  # owner, reviewer, viewer
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)

    __table_args__ = (
        db.UniqueConstraint('document_id', 'user_id', name='unique_document_user'),
    )

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    section_id = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # For threading

    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))

# Routes
@app.route('/document/<int:doc_id>/share', methods=['POST'])
@login_required
def share_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    # Check permissions
    if doc.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    email = request.json.get('email')
    role = request.json.get('role', 'reviewer')

    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})

    # Create reviewer relationship
    reviewer = DocumentReviewer(
        document_id=doc_id,
        user_id=user.id,
        role=role
    )
    db.session.add(reviewer)
    db.session.commit()

    # Send notification email
    # ... email code ...

    return jsonify({'success': True, 'message': 'Document shared successfully'})

@app.route('/document/<int:doc_id>/comments', methods=['GET', 'POST'])
@login_required
def document_comments(doc_id):
    doc = Document.query.get_or_404(doc_id)

    # Check access
    if not has_access(current_user, doc):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

    if request.method == 'POST':
        # Add comment
        comment = Comment(
            document_id=doc_id,
            section_id=request.json.get('section_id'),
            user_id=current_user.id,
            comment_text=request.json.get('text'),
            parent_id=request.json.get('parent_id')
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify({'success': True, 'comment_id': comment.id})

    # GET: Return all comments
    comments = Comment.query.filter_by(
        document_id=doc_id
    ).order_by(Comment.created_at).all()

    return jsonify({
        'success': True,
        'comments': [serialize_comment(c) for c in comments]
    })

def has_access(user, document):
    """Check if user has access to document"""
    if document.user_id == user.id:
        return True

    reviewer = DocumentReviewer.query.filter_by(
        document_id=document.id,
        user_id=user.id
    ).first()

    return reviewer is not None
```

**Success Criteria:**
- [ ] Multiple reviewers can access same document
- [ ] Comments threaded and real-time
- [ ] Permission system working
- [ ] Email notifications sent

---

## Success Metrics

### Phase 1 Metrics
- [ ] Test coverage > 60%
- [ ] All security vulnerabilities fixed
- [ ] Cache cleanup working
- [ ] Processing speed improved >15%

### Phase 2 Metrics
- [ ] Frontend performance improved >30%
- [ ] Backend processing >20% faster
- [ ] Memory usage reduced >25%

### Phase 3 Metrics
- [ ] DOCX/PDF export working
- [ ] Table extraction >90% accurate
- [ ] Analytics tracking all sessions

### Phase 4 Metrics
- [ ] Database migration complete
- [ ] User authentication functional
- [ ] Admin dashboard operational
- [ ] Multi-user support working

### Phase 5 Metrics
- [ ] ML model accuracy >85%
- [ ] OSF integration working
- [ ] Collaborative features functional

---

## Risk Assessment

### High Risk Items
1. **Database Migration** - Data loss risk
   - Mitigation: Comprehensive backups, testing on copies

2. **ML Model Performance** - May not improve accuracy
   - Mitigation: Keep rule-based fallback, extensive testing

3. **OSF API Changes** - External dependency
   - Mitigation: Version locking, error handling

### Medium Risk Items
1. **Performance Optimization** - May introduce bugs
   - Mitigation: Comprehensive testing, gradual rollout

2. **Authentication System** - Security vulnerabilities
   - Mitigation: Use established libraries, security audit

### Low Risk Items
1. **Export Features** - Limited impact if delayed
2. **Analytics** - Nice-to-have, not critical

---

## Next Steps

1. **Immediate (This Week):**
   - Set up testing framework
   - Implement CSRF protection
   - Add logging system

2. **Short Term (This Month):**
   - Compile regex patterns
   - Add cache cleanup
   - Implement debouncing

3. **Medium Term (Next Quarter):**
   - DOCX/PDF export
   - Table extraction
   - Analytics tracking

4. **Long Term (Next 6 Months):**
   - Database migration
   - User authentication
   - ML integration

---

**Last Updated:** 2025-11-16
**Next Review:** 2025-12-01
