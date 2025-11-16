# DMP-ART: Plan Rozwoju dla Data Stewardów

**Wersja:** 2.0 (Data Steward Focused)
**Data:** 2025-11-16
**Perspektywa:** Data Steward oceniający DMP naukowców
**Przewidywany czas realizacji:** 4 miesiące

---

## Spis Treści

1. [Kontekst i Potrzeby Data Stewarda](#kontekst-i-potrzeby-data-stewarda)
2. [Faza 1: Usprawnienia Workflow Recenzenta (2-3 tygodnie)](#faza-1-usprawnienia-workflow-recenzenta-2-3-tygodnie)
3. [Faza 2: Zaawansowane Funkcje Recenzji (1-1.5 miesiąca)](#faza-2-zaawansowane-funkcje-recenzji-1-15-miesiąca)
4. [Faza 3: Automatyzacja i Analityka (1.5-2 miesiące)](#faza-3-automatyzacja-i-analityka-15-2-miesiące)
5. [Faza 4: Współpraca i Integracje (2-3 miesiące)](#faza-4-współpraca-i-integracje-2-3-miesiące)
6. [Metryki Sukcesu](#metryki-sukcesu)

---

## Kontekst i Potrzeby Data Stewarda

### Kim jesteś jako użytkownik?
**Data Steward** w polskiej instytucji naukowej, oceniający plany zarządzania danymi (DMP) składane przez naukowców w ramach wniosków grantowych do NCN.

### Twój typowy dzień pracy:

1. **Otrzymujesz** wniosek grantowy (PDF/DOCX) zawierający DMP
2. **Wyciągasz** sekcję DMP z całego dokumentu
3. **Dzielisz** tekst na 14 elementów według struktury Science Europe
4. **Recenzujesz** każdy element:
   - Używasz gotowych sugestii dla typowych problemów ("jedno kliknięcie")
   - Piszesz unikalne komentarze dla specyficznych przypadków
   - Cytujesz fragmenty tekstu naukowca w komentarzach
5. **Kompilujesz** wszystkie komentarze w jedną spójną recenzję
6. **Eksportujesz** dwa pliki:
   - Wyekstrahowany DMP → folder `dmp_extracted/`
   - Recenzja → folder `reviews/`
7. **Archiwizujesz** powiązanie między DMP a recenzją

### Twoje główne bolączki w obecnej wersji (v0.8):

❌ **Brak organizacji plików** - wszystko w jednym folderze
❌ **Ograniczona personalizacja** - nie możesz dostosować sugestii dla każdego elementu osobno
❌ **Brak historii** - nie wiesz, które komentarze używasz najczęściej
❌ **Eksport tylko TXT** - potrzebujesz profesjonalnych raportów DOCX/PDF
❌ **Brak powiązań** - trudno znaleźć, która recenzja dotyczy którego DMP
❌ **Powtarzalność** - musisz wielokrotnie wpisywać te same komentarze

### Co chcesz osiągnąć:

✅ **Efektywność** - jedna recenzja w 15-20 minut zamiast 45-60 minut
✅ **Jakość** - spójne, profesjonalne recenzje z wykorzystaniem najlepszych praktyk
✅ **Organizacja** - czytelna struktura plików i łatwe wyszukiwanie
✅ **Personalizacja** - pełna kontrola nad strukturą DMP i sugestiami komentarzy
✅ **Estetyka** - przyjemny, nowoczesny interfejs ciemny/jasny
✅ **Automatyzacja** - system podpowiada często używane komentarze

---

## Faza 1: Usprawnienia Workflow Recenzenta (2-3 tygodnie)

**Priorytet:** 🔴 KRYTYCZNY
**Nakład pracy:** 60-80 godzin
**Cel:** v1.0 - Production Ready for Data Stewards

---

### Zadanie 1.1: Inteligentna Organizacja Plików

**Priorytet:** KRYTYCZNY
**Czas:** 8 godzin

#### Problem:
Obecnie wszystkie pliki trafiają do jednego folderu `outputs/`, co utrudnia zarządzanie dziesiątkami recenzji.

#### Rozwiązanie:
```
project/
├── outputs/
│   ├── extracted_dmps/           # Wyekstrahowane DMP
│   │   ├── 2025-11-16_GrantID_OPUS-12345_DMP.docx
│   │   └── 2025-11-16_GrantID_OPUS-12346_DMP.docx
│   │
│   ├── reviews/                   # Recenzje
│   │   ├── 2025-11-16_OPUS-12345_Review.docx
│   │   ├── 2025-11-16_OPUS-12345_Review.pdf
│   │   └── 2025-11-16_OPUS-12345_Review.txt
│   │
│   ├── cache/                     # Cache JSON
│   │   └── cache_<uuid>.json
│   │
│   └── archive/                   # Archiwum (>30 dni)
│       ├── 2025-10-01_OPUS-11111_DMP.docx
│       └── 2025-10-01_OPUS-11111_Review.docx
```

#### Implementacja:

```python
# config/file_organization.py
import os
from datetime import datetime
import json

class FileOrganizer:
    def __init__(self, base_dir='outputs'):
        self.base_dir = base_dir
        self.dirs = {
            'extracted': os.path.join(base_dir, 'extracted_dmps'),
            'reviews': os.path.join(base_dir, 'reviews'),
            'cache': os.path.join(base_dir, 'cache'),
            'archive': os.path.join(base_dir, 'archive')
        }

        # Create directories
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def generate_filename(self, grant_id, file_type, extension):
        """
        Generate standardized filename

        Args:
            grant_id: e.g., "OPUS-12345"
            file_type: "DMP" or "Review"
            extension: "docx", "pdf", "txt"

        Returns:
            "2025-11-16_OPUS-12345_Review.docx"
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{date_str}_{grant_id}_{file_type}.{extension}"

    def save_dmp(self, doc, grant_id, original_filename):
        """Save extracted DMP with metadata"""
        filename = self.generate_filename(grant_id, 'DMP', 'docx')
        filepath = os.path.join(self.dirs['extracted'], filename)

        doc.save(filepath)

        # Save metadata
        metadata = {
            'grant_id': grant_id,
            'original_filename': original_filename,
            'extracted_at': datetime.now().isoformat(),
            'dmp_path': filepath
        }

        meta_path = filepath.replace('.docx', '_metadata.json')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return filepath, metadata

    def save_review(self, content, grant_id, format='docx', link_to_dmp=None):
        """Save review with link to DMP"""
        filename = self.generate_filename(grant_id, 'Review', format)
        filepath = os.path.join(self.dirs['reviews'], filename)

        if format == 'docx':
            content.save(filepath)  # content is Document object
        elif format == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        elif format == 'pdf':
            # PDF generation (will implement in Phase 2)
            pass

        # Save link metadata
        if link_to_dmp:
            link_metadata = {
                'grant_id': grant_id,
                'review_path': filepath,
                'dmp_path': link_to_dmp,
                'created_at': datetime.now().isoformat()
            }

            link_path = filepath.replace(f'.{format}', '_link.json')
            with open(link_path, 'w', encoding='utf-8') as f:
                json.dump(link_metadata, f, indent=2, ensure_ascii=False)

        return filepath

    def find_linked_files(self, grant_id):
        """Find all files related to grant_id"""
        results = {
            'dmp': None,
            'reviews': [],
            'metadata': {}
        }

        # Search extracted DMPs
        for filename in os.listdir(self.dirs['extracted']):
            if grant_id in filename and filename.endswith('.docx'):
                results['dmp'] = os.path.join(self.dirs['extracted'], filename)

                # Load metadata
                meta_path = results['dmp'].replace('.docx', '_metadata.json')
                if os.path.exists(meta_path):
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        results['metadata'] = json.load(f)

        # Search reviews
        for filename in os.listdir(self.dirs['reviews']):
            if grant_id in filename and not filename.endswith('_link.json'):
                results['reviews'].append(os.path.join(self.dirs['reviews'], filename))

        return results

# Integracja w app.py
from config.file_organization import FileOrganizer

organizer = FileOrganizer()

@app.route('/upload', methods=['POST'])
def upload_file():
    # ... existing validation ...

    # Extract grant ID from document
    grant_id = extract_grant_id(file_path)  # New function

    # Process file
    result = extractor.process_file(file_path, organizer.dirs['extracted'])

    if result['success']:
        # Save with proper organization
        dmp_path, metadata = organizer.save_dmp(
            result['output_doc'],
            grant_id,
            file.filename
        )

        # Store metadata in session for review page
        session['current_grant_id'] = grant_id
        session['dmp_metadata'] = metadata

        return jsonify({
            'success': True,
            'grant_id': grant_id,
            'redirect': url_for('review_dmp',
                               filename=os.path.basename(dmp_path),
                               cache_id=result['cache_id'])
        })

@app.route('/export-review', methods=['POST'])
def export_review():
    grant_id = session.get('current_grant_id')
    feedback_data = request.json.get('feedback')
    format_type = request.json.get('format', 'docx')  # docx, txt, pdf

    # Generate review document
    if format_type == 'docx':
        review_doc = generate_review_docx(feedback_data, grant_id)
    elif format_type == 'txt':
        review_doc = generate_review_txt(feedback_data)

    # Find linked DMP
    linked_files = organizer.find_linked_files(grant_id)

    # Save review with link
    review_path = organizer.save_review(
        review_doc,
        grant_id,
        format_type,
        link_to_dmp=linked_files['dmp']
    )

    return send_file(review_path, as_attachment=True)

# Helper function
def extract_grant_id(file_path):
    """Extract grant ID from document (OPUS-12345, etc.)"""
    import re

    # Try to extract from filename first
    filename = os.path.basename(file_path)
    match = re.search(r'(OPUS|SONATA|PRELUDIUM|MAESTRO)-\d+', filename)
    if match:
        return match.group(0)

    # Try to extract from document content
    if file_path.endswith('.docx'):
        from docx import Document
        doc = Document(file_path)

        for para in doc.paragraphs[:20]:  # Check first 20 paragraphs
            match = re.search(r'(OPUS|SONATA|PRELUDIUM|MAESTRO)-\d+', para.text)
            if match:
                return match.group(0)

    # Fallback: generate from timestamp
    return f"UNKNOWN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
```

#### Frontend: File Browser

```html
<!-- Add to index.html or new page -->
<div class="file-browser">
    <h2>Twoje Recenzje</h2>

    <div class="search-bar">
        <input type="text" id="search-grant" placeholder="Szukaj po ID grantu (np. OPUS-12345)">
        <button onclick="searchGrant()">Szukaj</button>
    </div>

    <div id="search-results" class="results-grid">
        <!-- Dynamically populated -->
    </div>
</div>

<script>
async function searchGrant() {
    const grantId = document.getElementById('search-grant').value;

    const response = await fetch(`/api/search-files/${grantId}`);
    const data = await response.json();

    if (data.success) {
        displayResults(data.files);
    }
}

function displayResults(files) {
    const container = document.getElementById('search-results');
    container.innerHTML = '';

    if (files.dmp) {
        container.innerHTML += `
            <div class="file-card">
                <i class="fas fa-file-word"></i>
                <h4>Wyekstrahowany DMP</h4>
                <p>${files.metadata.original_filename}</p>
                <p class="date">${formatDate(files.metadata.extracted_at)}</p>
                <a href="/download/${encodeURIComponent(files.dmp)}" class="btn-download">
                    Pobierz DMP
                </a>
            </div>
        `;
    }

    files.reviews.forEach(review => {
        const ext = review.split('.').pop();
        const icon = ext === 'pdf' ? 'fa-file-pdf' : 'fa-file-word';

        container.innerHTML += `
            <div class="file-card">
                <i class="fas ${icon}"></i>
                <h4>Recenzja (.${ext})</h4>
                <a href="/download/${encodeURIComponent(review)}" class="btn-download">
                    Pobierz Recenzję
                </a>
            </div>
        `;
    });
}
</script>
```

#### Kryteria Sukcesu:
- [ ] Automatyczna organizacja plików w dedykowane foldery
- [ ] Standaryzowane nazewnictwo plików (data_grantID_typ)
- [ ] Powiązanie DMP ↔ Recenzja przez metadata JSON
- [ ] Wyszukiwanie po Grant ID
- [ ] Pobieranie powiązanych plików jednym kliknięciem

---

### Zadanie 1.2: Zaawansowana Personalizacja Komentarzy per Element

**Priorytet:** KRYTYCZNY
**Czas:** 12 godzin

#### Problem:
Obecny template editor pozwala na globalne kategorie, ale nie ma możliwości dostosowania sugestii **dla każdego z 14 elementów DMP osobno**.

#### Rozwiązanie:

```javascript
// Enhanced template editor - static/js/template_editor_v2.js

class PerSectionTemplateManager {
    constructor() {
        this.sections = [
            '1.1', '1.2', '2.1', '2.2', '3.1', '3.2',
            '4.1', '4.2', '5.1', '5.2', '6.1', '6.2'
        ];

        this.templates = {};  // {section_id: {category: [comments]}}
        this.load();
    }

    async load() {
        const response = await fetch('/api/templates/per-section');
        const data = await response.json();

        if (data.success) {
            this.templates = data.templates;
            this.render();
        }
    }

    render() {
        const container = document.getElementById('per-section-editor');
        container.innerHTML = '';

        // Create accordion for each section
        this.sections.forEach(sectionId => {
            const sectionDiv = this.createSectionEditor(sectionId);
            container.appendChild(sectionDiv);
        });
    }

    createSectionEditor(sectionId) {
        const div = document.createElement('div');
        div.className = 'section-template-editor';

        const question = DMP_QUESTIONS[sectionId];  // From config

        div.innerHTML = `
            <div class="section-header" onclick="toggleSection('${sectionId}')">
                <h3>
                    <i class="fas fa-chevron-down"></i>
                    Sekcja ${sectionId}: ${question.substring(0, 60)}...
                </h3>
                <span class="template-count">${this.getTemplateCount(sectionId)} szablonów</span>
            </div>

            <div class="section-content collapsed" id="section-${sectionId}-content">
                <!-- Categories for this section -->
                <div class="category-tabs">
                    <button class="category-tab active" data-category="common" data-section="${sectionId}">
                        Częste problemy
                    </button>
                    <button class="category-tab" data-category="missing" data-section="${sectionId}">
                        Braki
                    </button>
                    <button class="category-tab" data-category="excellent" data-section="${sectionId}">
                        Bardzo dobre
                    </button>
                    <button class="category-tab" data-category="custom" data-section="${sectionId}">
                        Własne
                    </button>
                </div>

                <div class="templates-list" id="templates-${sectionId}">
                    ${this.renderTemplates(sectionId, 'common')}
                </div>

                <button class="btn-add-template" onclick="addTemplate('${sectionId}')">
                    <i class="fas fa-plus"></i> Dodaj szablon
                </button>
            </div>
        `;

        return div;
    }

    renderTemplates(sectionId, category) {
        const templates = this.templates[sectionId]?.[category] || [];

        let html = '<div class="template-items">';

        templates.forEach((template, index) => {
            html += `
                <div class="template-item" data-id="${index}">
                    <div class="template-header">
                        <span class="usage-count" title="Użyto ${template.usage_count || 0} razy">
                            ${template.usage_count || 0}×
                        </span>
                        <input type="text" class="template-name" value="${template.name || ''}"
                               placeholder="Nazwa szablonu (opcjonalna)">
                        <button class="btn-delete" onclick="deleteTemplate('${sectionId}', '${category}', ${index})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>

                    <textarea class="template-text" rows="3"
                              onchange="updateTemplate('${sectionId}', '${category}', ${index}, this.value)">${template.text}</textarea>

                    <div class="template-tags">
                        <span class="tag">${sectionId}</span>
                        <span class="tag">${category}</span>
                        ${template.keywords ? template.keywords.map(k => `<span class="tag-keyword">${k}</span>`).join('') : ''}
                    </div>
                </div>
            `;
        });

        html += '</div>';
        return html;
    }

    getTemplateCount(sectionId) {
        if (!this.templates[sectionId]) return 0;

        return Object.values(this.templates[sectionId])
            .reduce((sum, category) => sum + category.length, 0);
    }

    async save() {
        const response = await fetch('/api/templates/per-section', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({templates: this.templates})
        });

        const data = await response.json();

        if (data.success) {
            showToast('Szablony zapisane pomyślnie', 'success');
        } else {
            showToast('Błąd zapisu: ' + data.message, 'error');
        }
    }
}

// Initialize
let templateManager;
document.addEventListener('DOMContentLoaded', () => {
    templateManager = new PerSectionTemplateManager();
});

function addTemplate(sectionId) {
    const category = document.querySelector('.category-tab.active').dataset.category;

    if (!templateManager.templates[sectionId]) {
        templateManager.templates[sectionId] = {};
    }

    if (!templateManager.templates[sectionId][category]) {
        templateManager.templates[sectionId][category] = [];
    }

    templateManager.templates[sectionId][category].push({
        name: '',
        text: '',
        usage_count: 0,
        keywords: []
    });

    templateManager.render();
}

function updateTemplate(sectionId, category, index, newText) {
    templateManager.templates[sectionId][category][index].text = newText;

    // Auto-save after 2 seconds
    clearTimeout(window.autoSaveTimer);
    window.autoSaveTimer = setTimeout(() => {
        templateManager.save();
    }, 2000);
}
```

#### Backend Support:

```python
# routes/templates.py
from flask import Blueprint, request, jsonify
import json
import os

templates_bp = Blueprint('templates', __name__, url_prefix='/api/templates')

TEMPLATES_FILE = 'config/per_section_templates.json'

@templates_bp.route('/per-section', methods=['GET'])
def get_per_section_templates():
    """Load templates organized by section and category"""
    try:
        if os.path.exists(TEMPLATES_FILE):
            with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                templates = json.load(f)
        else:
            # Initialize with empty structure
            templates = {
                section_id: {
                    'common': [],
                    'missing': [],
                    'excellent': [],
                    'custom': []
                }
                for section_id in ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2',
                                   '4.1', '4.2', '5.1', '5.2', '6.1', '6.2']
            }

        return jsonify({'success': True, 'templates': templates})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@templates_bp.route('/per-section', methods=['POST'])
def save_per_section_templates():
    """Save templates"""
    try:
        templates = request.json.get('templates', {})

        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@templates_bp.route('/usage/<section_id>/<category>/<int:index>', methods=['POST'])
def increment_usage(section_id, category, index):
    """Track template usage"""
    try:
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            templates = json.load(f)

        if section_id in templates and category in templates[section_id]:
            if index < len(templates[section_id][category]):
                template = templates[section_id][category][index]
                template['usage_count'] = template.get('usage_count', 0) + 1
                template['last_used'] = datetime.now().isoformat()

        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Register in app.py
from routes.templates import templates_bp
app.register_blueprint(templates_bp)
```

#### Kryteria Sukcesu:
- [ ] Każdy z 14 elementów ma osobne szablony komentarzy
- [ ] 4 kategorie per element: Częste, Braki, Bardzo dobre, Własne
- [ ] Licznik użycia każdego szablonu
- [ ] Auto-save po 2 sekundach
- [ ] Import/Export szablonów

---

### Zadanie 1.3: Nowoczesny Ciemny Interfejs - Refinement

**Priorytet:** WYSOKI
**Czas:** 10 godzin

#### Problem:
Obecny dark mode działa, ale brakuje spójności, płynnych animacji i nowoczesnych elementów UI.

#### Rozwiązanie:

```css
/* static/css/modern-dark-theme.css */

/* ===========================
   Modern Dark Theme Variables
   =========================== */

:root[data-theme="dark"] {
    /* Core Colors - Deep Blues & Purples */
    --bg-main: #0f1419;
    --bg-card: #1a1f2e;
    --bg-card-hover: #242938;
    --bg-elevated: #2d3142;

    /* Accent Colors */
    --primary: #6366f1;        /* Indigo */
    --primary-hover: #4f46e5;
    --secondary: #8b5cf6;      /* Purple */
    --accent: #06b6d4;         /* Cyan */

    /* Text */
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;

    /* Semantic Colors */
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --info: #3b82f6;

    /* Borders & Shadows */
    --border-color: #334155;
    --border-subtle: #1e293b;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    --shadow-glow: 0 0 15px rgba(99, 102, 241, 0.3);

    /* Spacing Scale */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;

    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;

    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===========================
   Light Theme
   =========================== */

:root[data-theme="light"] {
    --bg-main: #f8fafc;
    --bg-card: #ffffff;
    --bg-card-hover: #f1f5f9;
    --bg-elevated: #ffffff;

    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --secondary: #7c3aed;
    --accent: #0891b2;

    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;

    --success: #059669;
    --warning: #d97706;
    --error: #dc2626;
    --info: #2563eb;

    --border-color: #e2e8f0;
    --border-subtle: #f1f5f9;
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.15);
    --shadow-glow: 0 0 15px rgba(79, 70, 229, 0.2);
}

/* ===========================
   Base Styles
   =========================== */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg-main);
    color: var(--text-primary);
    line-height: 1.6;
    transition: background-color var(--transition-base),
                color var(--transition-base);
}

/* ===========================
   Modern Card Component
   =========================== */

.card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
}

.card:hover {
    background: var(--bg-card-hover);
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

.card-elevated {
    background: var(--bg-elevated);
    box-shadow: var(--shadow-lg);
}

/* ===========================
   Buttons - Modern Style
   =========================== */

.btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-sm);
    padding: var(--space-sm) var(--space-lg);
    border: none;
    border-radius: var(--radius-md);
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all var(--transition-fast);
    position: relative;
    overflow: hidden;
}

.btn::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: translate(-50%, -50%);
    transition: width var(--transition-base), height var(--transition-base);
}

.btn:active::before {
    width: 300px;
    height: 300px;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
    box-shadow: var(--shadow-glow), var(--shadow-md);
    transform: translateY(-2px);
}

.btn-secondary {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.btn-secondary:hover {
    background: var(--bg-card-hover);
    border-color: var(--primary);
}

.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
}

.btn-ghost:hover {
    background: var(--bg-card);
    color: var(--text-primary);
}

/* ===========================
   Input Fields - Modern
   =========================== */

.input,
textarea {
    width: 100%;
    padding: var(--space-sm) var(--space-md);
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 0.875rem;
    transition: all var(--transition-fast);
}

.input:focus,
textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

textarea {
    resize: vertical;
    min-height: 100px;
    line-height: 1.5;
}

/* ===========================
   Navigation Sidebar - Sticky
   =========================== */

.sidebar {
    position: sticky;
    top: var(--space-lg);
    height: fit-content;
    max-height: calc(100vh - 2 * var(--space-lg));
    overflow-y: auto;
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    box-shadow: var(--shadow-md);
}

.sidebar::-webkit-scrollbar {
    width: 6px;
}

.sidebar::-webkit-scrollbar-track {
    background: var(--bg-card);
    border-radius: var(--radius-sm);
}

.sidebar::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: var(--radius-sm);
}

.sidebar::-webkit-scrollbar-thumb:hover {
    background: var(--primary);
}

/* ===========================
   Section Cards - Review Page
   =========================== */

.section-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--primary);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    margin-bottom: var(--space-lg);
    transition: all var(--transition-base);
}

.section-card:hover {
    border-left-color: var(--accent);
    box-shadow: var(--shadow-lg);
}

.section-card.has-feedback {
    border-left-color: var(--success);
}

.section-card.incomplete {
    border-left-color: var(--warning);
}

/* ===========================
   Animations
   =========================== */

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.animate-slide-in {
    animation: slideIn var(--transition-base) ease-out;
}

.animate-fade-in {
    animation: fadeIn var(--transition-base) ease-out;
}

/* ===========================
   Toast Notifications
   =========================== */

.toast-container {
    position: fixed;
    top: var(--space-lg);
    right: var(--space-lg);
    z-index: 10000;
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
}

.toast {
    background: var(--bg-elevated);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-md) var(--space-lg);
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: center;
    gap: var(--space-sm);
    min-width: 300px;
    animation: slideIn var(--transition-base) ease-out;
}

.toast.success { border-left: 4px solid var(--success); }
.toast.error { border-left: 4px solid var(--error); }
.toast.warning { border-left: 4px solid var(--warning); }
.toast.info { border-left: 4px solid var(--info); }

/* ===========================
   Loading States
   =========================== */

.skeleton {
    background: linear-gradient(
        90deg,
        var(--bg-card) 0%,
        var(--bg-card-hover) 50%,
        var(--bg-card) 100%
    );
    background-size: 200% 100%;
    animation: loading 1.5s ease-in-out infinite;
    border-radius: var(--radius-sm);
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.spinner {
    border: 3px solid var(--border-color);
    border-top-color: var(--primary);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ===========================
   Responsive Design
   =========================== */

@media (max-width: 768px) {
    .sidebar {
        position: relative;
        top: 0;
        max-height: none;
        margin-bottom: var(--space-lg);
    }

    .section-card {
        padding: var(--space-lg);
    }
}
```

#### Kryteria Sukcesu:
- [ ] Spójny system kolorów (dark/light)
- [ ] Płynne animacje i przejścia
- [ ] Nowoczesne komponenty (karty, przyciski, inputy)
- [ ] Responsywny design
- [ ] Accessibility (WCAG 2.1 AA)

---

### Zadanie 1.4: Inteligentne Sugestie Komentarzy

**Priorytet:** WYSOKI
**Czas:** 8 godzin

#### Problem:
System nie podpowiada najczęściej używanych komentarzy ani nie uczy się z wzorców użytkownika.

#### Rozwiązanie:

```javascript
// Smart comment suggestions - static/js/smart-suggestions.js

class SmartCommentSuggester {
    constructor() {
        this.usageHistory = this.loadHistory();
        this.contextKeywords = this.buildKeywordIndex();
    }

    loadHistory() {
        const stored = localStorage.getItem('dmp-comment-history');
        return stored ? JSON.parse(stored) : {};
    }

    saveHistory() {
        localStorage.setItem('dmp-comment-history',
                            JSON.stringify(this.usageHistory));
    }

    trackUsage(sectionId, category, templateIndex) {
        const key = `${sectionId}:${category}:${templateIndex}`;

        if (!this.usageHistory[key]) {
            this.usageHistory[key] = {
                count: 0,
                lastUsed: null,
                section: sectionId
            };
        }

        this.usageHistory[key].count++;
        this.usageHistory[key].lastUsed = Date.now();

        this.saveHistory();

        // Send to server for global stats
        fetch('/api/templates/track-usage', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({sectionId, category, templateIndex})
        });
    }

    getSuggestions(sectionId, extractedText) {
        /**
         * Get smart suggestions based on:
         * 1. Usage frequency
         * 2. Recent usage
         * 3. Keyword matching with extracted text
         */

        const suggestions = [];

        // Get all templates for this section
        const templates = window.PER_SECTION_TEMPLATES[sectionId] || {};

        Object.entries(templates).forEach(([category, items]) => {
            items.forEach((template, index) => {
                const key = `${sectionId}:${category}:${index}`;
                const history = this.usageHistory[key] || {count: 0, lastUsed: 0};

                // Calculate relevance score
                const frequencyScore = history.count * 10;
                const recencyScore = this.getRecencyScore(history.lastUsed);
                const keywordScore = this.getKeywordScore(template.text, extractedText);

                const totalScore = frequencyScore + recencyScore + keywordScore;

                suggestions.push({
                    section: sectionId,
                    category: category,
                    index: index,
                    text: template.text,
                    name: template.name,
                    score: totalScore,
                    usageCount: history.count,
                    lastUsed: history.lastUsed
                });
            });
        });

        // Sort by score
        suggestions.sort((a, b) => b.score - a.score);

        return suggestions.slice(0, 5);  // Top 5
    }

    getRecencyScore(lastUsed) {
        if (!lastUsed) return 0;

        const daysSince = (Date.now() - lastUsed) / (1000 * 60 * 60 * 24);

        if (daysSince < 1) return 50;
        if (daysSince < 7) return 30;
        if (daysSince < 30) return 10;
        return 0;
    }

    getKeywordScore(templateText, extractedText) {
        if (!extractedText) return 0;

        const templateWords = this.extractKeywords(templateText.toLowerCase());
        const extractedWords = this.extractKeywords(extractedText.toLowerCase());

        let matches = 0;
        templateWords.forEach(word => {
            if (extractedWords.includes(word)) {
                matches++;
            }
        });

        return matches * 5;
    }

    extractKeywords(text) {
        const stopWords = ['i', 'a', 'the', 'to', 'of', 'in', 'for', 'on', 'with',
                          'że', 'i', 'w', 'na', 'do', 'z', 'dla', 'po'];

        return text
            .toLowerCase()
            .replace(/[^\w\s]/g, '')
            .split(/\s+/)
            .filter(word => word.length > 3 && !stopWords.includes(word));
    }

    buildKeywordIndex() {
        // Build index of keywords for faster matching
        // Implementation...
    }
}

// Initialize
const suggester = new SmartCommentSuggester();

// Add suggestions panel to review page
function showSuggestions(sectionId) {
    const extractedText = document.querySelector(`#section-${sectionId} .extracted-content`).textContent;
    const suggestions = suggester.getSuggestions(sectionId, extractedText);

    const panel = document.getElementById('suggestions-panel');
    panel.innerHTML = '<h4>Sugerowane komentarze:</h4>';

    if (suggestions.length === 0) {
        panel.innerHTML += '<p class="no-suggestions">Brak sugestii</p>';
        return;
    }

    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.innerHTML = `
            <div class="suggestion-header">
                <span class="suggestion-category">${suggestion.category}</span>
                <span class="suggestion-usage">${suggestion.usageCount}× użyto</span>
            </div>
            <div class="suggestion-text">${suggestion.text}</div>
            <button class="btn-use-suggestion" onclick="useSuggestion(${JSON.stringify(suggestion).replace(/"/g, '&quot;')})">
                Użyj
            </button>
        `;
        panel.appendChild(item);
    });
}

function useSuggestion(suggestion) {
    const textarea = document.querySelector(`#feedback-${suggestion.section}`);
    const currentValue = textarea.value;
    const separator = currentValue.trim() ? '\n\n' : '';

    textarea.value = currentValue + separator + suggestion.text;

    // Track usage
    suggester.trackUsage(suggestion.section, suggestion.category, suggestion.index);

    // Update UI
    updateCharacterCounter(suggestion.section);
    showToast('Komentarz dodany', 'success');
}
```

#### UI Enhancement in review.html:

```html
<div class="review-layout">
    <aside class="suggestions-sidebar">
        <div id="suggestions-panel" class="suggestions-container">
            <!-- Dynamically populated -->
        </div>

        <div class="suggestion-stats">
            <h4>Twoje statystyki</h4>
            <div class="stat-item">
                <span>Najczęściej używany</span>
                <p id="most-used-template">—</p>
            </div>
            <div class="stat-item">
                <span>Ostatnio użyty</span>
                <p id="recently-used-template">—</p>
            </div>
        </div>
    </aside>

    <main class="review-content">
        <!-- Section cards -->
    </main>
</div>
```

#### Kryteria Sukcesu:
- [ ] Top 5 sugestii dla każdej sekcji
- [ ] Scoring: frequency + recency + keyword matching
- [ ] Tracking użycia (local + server)
- [ ] Statystyki użytkownika
- [ ] Jedno kliknięcie = komentarz dodany

---

## Faza 2: Zaawansowane Funkcje Recenzji (1-1.5 miesiąca)

**Priorytet:** 🟡 WYSOKI
**Nakład pracy:** 100-120 godzin
**Cel:** v1.5 - Advanced Review Features

---

### Zadanie 2.1: Professional DOCX Export

**Priorytet:** KRYTYCZNY
**Czas:** 16 godzin

#### Rozwiązanie:

```python
# utils/review_exporter.py
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from datetime import datetime

class ProfessionalReviewExporter:
    def __init__(self):
        self.doc = Document()
        self.setup_styles()
        self.setup_page()

    def setup_page(self):
        """Configure page margins and size"""
        sections = self.doc.sections
        for section in sections:
            section.page_height = Inches(11.69)  # A4
            section.page_width = Inches(8.27)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)

    def setup_styles(self):
        """Create custom styles"""
        styles = self.doc.styles

        # Title style
        title_style = styles.add_style('CustomTitle', 1)
        title_font = title_style.font
        title_font.name = 'Calibri'
        title_font.size = Pt(22)
        title_font.bold = True
        title_font.color.rgb = RGBColor(31, 73, 125)

        # Section header style
        section_style = styles.add_style('SectionHeader', 1)
        section_font = section_style.font
        section_font.name = 'Calibri'
        section_font.size = Pt(14)
        section_font.bold = True
        section_font.color.rgb = RGBColor(68, 114, 196)

        # Question style
        question_style = styles.add_style('Question', 1)
        question_font = question_style.font
        question_font.name = 'Calibri'
        question_font.size = Pt(11)
        question_font.italic = True
        question_font.color.rgb = RGBColor(89, 89, 89)

    def generate_review(self, grant_data, feedback_data, metadata=None):
        """
        Generate professional review document

        Args:
            grant_data: {grant_id, title, pi_name, institution}
            feedback_data: {section_id: {question, text}}
            metadata: {reviewer_name, date, etc.}
        """

        # Header
        self.add_header(grant_data, metadata)

        # Table of contents
        self.add_toc()

        # Executive summary
        self.add_executive_summary(feedback_data)

        # Detailed feedback by section
        self.add_detailed_feedback(feedback_data)

        # Footer with metadata
        self.add_footer(metadata)

        return self.doc

    def add_header(self, grant_data, metadata):
        """Add document header"""
        # Title
        title = self.doc.add_heading('Recenzja Planu Zarządzania Danymi', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.runs[0]
        title_run.font.color.rgb = RGBColor(31, 73, 125)

        self.doc.add_paragraph()

        # Info table
        table = self.doc.add_table(rows=5, cols=2)
        table.style = 'Light Grid Accent 1'

        rows_data = [
            ('Grant ID:', grant_data.get('grant_id', 'N/A')),
            ('Tytuł projektu:', grant_data.get('title', 'N/A')),
            ('Kierownik:', grant_data.get('pi_name', 'N/A')),
            ('Instytucja:', grant_data.get('institution', 'N/A')),
            ('Data recenzji:', metadata.get('review_date', datetime.now().strftime('%Y-%m-%d')))
        ]

        for i, (label, value) in enumerate(rows_data):
            table.rows[i].cells[0].text = label
            table.rows[i].cells[1].text = value

            # Style cells
            for cell in table.rows[i].cells:
                cell.paragraphs[0].runs[0].font.size = Pt(10)

        self.doc.add_paragraph()

    def add_toc(self):
        """Add table of contents"""
        self.doc.add_heading('Spis treści', level=1)

        # Note: Word will auto-generate TOC when opened
        toc_para = self.doc.add_paragraph()
        toc_para.add_run('[Spis treści zostanie wygenerowany automatycznie]').italic = True

        self.doc.add_page_break()

    def add_executive_summary(self, feedback_data):
        """Add executive summary"""
        self.doc.add_heading('Podsumowanie', level=1)

        total_sections = 14
        completed_sections = sum(1 for f in feedback_data.values() if f.get('text', '').strip())

        summary_para = self.doc.add_paragraph()
        summary_para.add_run(
            f"Oceniono {completed_sections} z {total_sections} sekcji planu zarządzania danymi. "
        )

        if completed_sections == total_sections:
            summary_para.add_run("Plan jest kompletny i został szczegółowo zrecenzowany.").bold = True
        else:
            summary_para.add_run(
                f"{total_sections - completed_sections} sekcji nie wymagało komentarzy lub było puste."
            )

        self.doc.add_paragraph()

        # Overall assessment
        self.doc.add_heading('Ogólna ocena', level=2)

        # Calculate quality score (simplified)
        avg_length = sum(len(f.get('text', '')) for f in feedback_data.values()) / total_sections

        if avg_length < 50:
            assessment = "Plan wymaga znaczących poprawek."
            color = RGBColor(192, 0, 0)
        elif avg_length < 150:
            assessment = "Plan wymaga poprawek w kilku obszarach."
            color = RGBColor(255, 192, 0)
        else:
            assessment = "Plan jest dobrej jakości z drobnymi sugestiami."
            color = RGBColor(0, 176, 80)

        assessment_para = self.doc.add_paragraph()
        assessment_run = assessment_para.add_run(assessment)
        assessment_run.font.size = Pt(12)
        assessment_run.font.color.rgb = color
        assessment_run.bold = True

        self.doc.add_page_break()

    def add_detailed_feedback(self, feedback_data):
        """Add detailed feedback section by section"""
        self.doc.add_heading('Szczegółowe komentarze', level=1)

        # Group by main sections (1.x, 2.x, etc.)
        sections = {
            '1': 'Opis danych i ich pozyskiwanie',
            '2': 'Dokumentacja i jakość danych',
            '3': 'Przechowywanie i kopie zapasowe',
            '4': 'Wymogi prawne i etyczne',
            '5': 'Udostępnianie i archiwizacja',
            '6': 'Odpowiedzialność i zasoby'
        }

        for main_section, title in sections.items():
            self.doc.add_heading(f"{main_section}. {title}", level=2)

            # Get subsections
            subsections = sorted([k for k in feedback_data.keys() if k.startswith(main_section + '.')])

            for section_id in subsections:
                feedback = feedback_data[section_id]

                if not feedback.get('text', '').strip():
                    continue

                # Section ID and question
                self.doc.add_heading(f"Sekcja {section_id}", level=3)

                question_para = self.doc.add_paragraph(style='Question')
                question_para.add_run(feedback.get('question', ''))

                # Feedback text
                feedback_para = self.doc.add_paragraph()
                feedback_para.paragraph_format.left_indent = Inches(0.25)
                feedback_para.paragraph_format.space_after = Pt(12)
                feedback_para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

                # Parse feedback text (handle citations, bold, etc.)
                self.parse_and_add_formatted_text(feedback_para, feedback.get('text', ''))

                self.doc.add_paragraph()

    def parse_and_add_formatted_text(self, paragraph, text):
        """Parse text and add with formatting (citations, etc.)"""
        import re

        # Split by citation markers
        parts = re.split(r'(❝[^❞]+❞)', text)

        for part in parts:
            if part.startswith('❝') and part.endswith('❞'):
                # Citation - italic and indented
                citation_text = part[1:-1]  # Remove markers
                run = paragraph.add_run(f'"{citation_text}"')
                run.italic = True
                run.font.color.rgb = RGBColor(89, 89, 89)
            else:
                # Regular text
                run = paragraph.add_run(part)
                run.font.size = Pt(11)

    def add_footer(self, metadata):
        """Add footer with generation info"""
        self.doc.add_page_break()

        footer_para = self.doc.add_paragraph()
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        footer_run = footer_para.add_run(
            f"\nDokument wygenerowany przez DMP-ART\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Recenzent: {metadata.get('reviewer_name', 'System')}"
        )
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(127, 127, 127)
        footer_run.italic = True

# Route in app.py
from utils.review_exporter import ProfessionalReviewExporter

@app.route('/export-review/docx', methods=['POST'])
def export_review_docx():
    try:
        grant_id = session.get('current_grant_id')
        feedback_data = request.json.get('feedback')

        # Get grant data from extraction
        grant_data = {
            'grant_id': grant_id,
            'title': request.json.get('project_title', 'N/A'),
            'pi_name': request.json.get('pi_name', 'N/A'),
            'institution': request.json.get('institution', 'N/A')
        }

        metadata = {
            'reviewer_name': 'Data Steward',  # Will use actual user when auth implemented
            'review_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Generate review
        exporter = ProfessionalReviewExporter()
        doc = exporter.generate_review(grant_data, feedback_data, metadata)

        # Save with organization
        review_path = organizer.save_review(doc, grant_id, format='docx')

        return send_file(review_path, as_attachment=True,
                        download_name=f'{grant_id}_Review.docx')

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

#### Kryteria Sukcesu:
- [ ] Profesjonalny layout z nagłówkiem i stopką
- [ ] Spis treści auto-generowany
- [ ] Executive summary z ogólną oceną
- [ ] Formatowanie cytowań i pogrubień
- [ ] Export do `reviews/` z linkiem do DMP

---

### Zadanie 2.2: Keyboard Shortcuts & Quick Navigation

**Priorytet:** ŚREDNI
**Czas:** 6 godzin

```javascript
// Keyboard shortcuts for efficient workflow
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = {
            'ctrl+s': () => this.saveFeedback(),
            'ctrl+e': () => this.exportReview(),
            'ctrl+1': () => this.jumpToSection('1.1'),
            'ctrl+2': () => this.jumpToSection('1.2'),
            // ... up to ctrl+9
            'ctrl+shift+c': () => this.compileFeedback(),
            'ctrl+shift+s': () => this.showSuggestions(),
            'alt+n': () => this.nextSection(),
            'alt+p': () => this.previousSection()
        };

        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyCombo(e);

            if (this.shortcuts[key]) {
                e.preventDefault();
                this.shortcuts[key]();
            }
        });
    }

    getKeyCombo(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.shiftKey) parts.push('shift');
        if (e.altKey) parts.push('alt');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }

    jumpToSection(sectionId) {
        const section = document.getElementById(`section-${sectionId}`);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            const textarea = section.querySelector('textarea');
            if (textarea) textarea.focus();
        }
    }

    nextSection() {
        // Navigate to next section
    }

    previousSection() {
        // Navigate to previous section
    }

    saveFeedback() {
        document.getElementById('save-progress-btn').click();
    }

    exportReview() {
        document.getElementById('export-review-btn').click();
    }

    compileFeedback() {
        document.getElementById('compile-feedback-btn').click();
    }

    showSuggestions() {
        const currentSection = this.getCurrentSection();
        showSuggestions(currentSection);
    }

    getCurrentSection() {
        // Detect which section is in viewport
        const sections = document.querySelectorAll('[id^="section-"]');

        for (let section of sections) {
            const rect = section.getBoundingClientRect();
            if (rect.top >= 0 && rect.top <= window.innerHeight / 2) {
                return section.id.replace('section-', '');
            }
        }

        return '1.1';
    }
}

// Initialize
new KeyboardShortcuts();

// Show shortcuts help
function showShortcutsHelp() {
    const modal = document.createElement('div');
    modal.className = 'shortcuts-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Skróty klawiszowe</h2>

            <div class="shortcuts-grid">
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>S</kbd>
                    <span>Zapisz postęp</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>E</kbd>
                    <span>Eksportuj recenzję</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>1-9</kbd>
                    <span>Przeskocz do sekcji</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Alt</kbd> + <kbd>N</kbd>
                    <span>Następna sekcja</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Alt</kbd> + <kbd>P</kbd>
                    <span>Poprzednia sekcja</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd>
                    <span>Kompiluj recenzję</span>
                </div>
                <div class="shortcut-item">
                    <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>
                    <span>Pokaż sugestie</span>
                </div>
            </div>

            <button onclick="closeModal(this)">Zamknij</button>
        </div>
    `;

    document.body.appendChild(modal);
}
```

---

*(Kontynuacja w następnej wiadomości ze względu na długość...)*

---

## Podsumowanie Aktualizacji

Utworzyłem **nowy, zorientowany na data stewarda plan rozwoju** (`ACTION_PLAN_DATA_STEWARD.md`), który:

### ✅ **Kluczowe zmiany priorytetów:**

1. **Organizacja plików** (Faza 1) - osobne foldery dla DMP i recenzji z powiązaniami
2. **Personalizacja per element** (Faza 1) - każda z 14 sekcji ma własne szablony
3. **Nowoczesny UI** (Faza 1) - ciemny theme z płynnymi animacjami
4. **Smart suggestions** (Faza 1) - inteligentne podpowiadanie na podstawie historii
5. **Professional DOCX export** (Faza 2) - profesjonalne raporty z formatowaniem
6. **Keyboard shortcuts** (Faza 2) - workflow efficiency

### 📊 **Metryki sukcesu dla Data Stewarda:**

- ⏱️ **Czas recenzji: 45-60 min → 15-20 min** (60-70% redukcja)
- 📁 **100% plików zorganizowanych** automatycznie
- 🎯 **90%+ komentarzy z szablonów** (jedno kliknięcie)
- 🎨 **Pełna personalizacja** UI i szablonów
- 📈 **Tracking i analytics** użycia

Czy chcesz, żebym:
1. **Kontynuował** rozpisywanie Faz 2-4?
2. **Zaimplementował** któreś z zadań Fazy 1?
3. **Stworzył PR** z tym planem?