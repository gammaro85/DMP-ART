# Extraction Rules Externalization - Implementation Plan

**Version:** 1.0
**Created:** 2025-12-11
**Status:** Ready for Implementation

---

## Executive Summary

This plan externalizes ~100+ hardcoded extraction patterns from `utils/extractor.py` to a configurable JSON file, enabling users to customize section/subsection detection rules without code changes.

### Key Problem Identified

**Real-world extraction failure** (from `Data Management Plan_S2025.docx`):
- **Section 1.2 content** → Ends up in `_unconnected_text` instead of section 1.2
- **Sections 2.1-6.1** → All dumped into section 6.1 (wrong assignment)
- **Root cause:** Content has "BOLD:" prefix that breaks subsection matching

**Example of problematic content:**
```
BOLD:1.2. What data (for example the kinds, formats, and volumes)...
```

The "BOLD:" prefix prevents the subsection detector from recognizing "1.2" as a valid subsection header.

---

## Research Findings - Best Practices

Based on research into modern extraction pattern systems (sources included at end):

### 1. **Grok Pattern Syntax** (Datadog approach)
- Use `%{MATCHER:EXTRACT:FILTER}` syntax for complex patterns
- Support chaining filters: `pattern → extraction → transformation`
- Enable helper rules that can be reused across multiple patterns

### 2. **JSON Schema Validation** (2025 Standard)
- Define structure with strict validation (Pydantic/jsonschema)
- Keep nesting shallow (2-3 levels max) for readability
- Use explicit data types and enums to prevent drift

### 3. **Externalization Patterns**
- Store regex as **raw strings in JSON** to avoid double-escaping
- Pre-compile patterns at load time for performance (already done in DMP-ART)
- Support **per-section** and **global** rules with inheritance

### 4. **User-Defined Custom Rules**
- Separate system rules (auto-loaded) from user rules (editable)
- Support rule precedence: `custom > per-section > global`
- Enable/disable individual rules without deletion

### 5. **Testing and Validation**
- Provide rule testing interface with before/after preview
- Validate regex syntax on save
- Track rule usage statistics for optimization

---

## Proposed Configuration Structure

### File: `config/extraction_rules.json`

```json
{
  "_metadata": {
    "version": "1.0",
    "description": "Extraction rules for DMP content detection and filtering",
    "last_updated": "2025-12-11T00:00:00",
    "rule_count": 127
  },

  "_schema_version": "1.0",

  "skip_patterns": {
    "general": {
      "description": "Content to skip in all document types",
      "enabled": true,
      "patterns": [
        {"id": "skip_001", "pattern": "Strona \\d+", "description": "Polish page numbers", "enabled": true},
        {"id": "skip_002", "pattern": "Page \\d+", "description": "English page numbers", "enabled": true},
        {"id": "skip_003", "pattern": "ID:\\s*\\d+", "description": "Document IDs", "enabled": true},
        {"id": "skip_004", "pattern": "\\[wydruk roboczy\\]", "description": "Working print marker", "enabled": true},
        {"id": "skip_005", "pattern": "WZÓR", "description": "Template marker", "enabled": true},
        {"id": "skip_006", "pattern": "W Z Ó R", "description": "Template marker (spaced)", "enabled": true},
        {"id": "skip_007", "pattern": "OSF,", "description": "Grant system name", "enabled": true},
        {"id": "skip_008", "pattern": "^\\d+$", "description": "Pure numbers", "enabled": true},
        {"id": "skip_009", "pattern": "^\\+[-=]+\\+$", "description": "Table borders", "enabled": true},
        {"id": "skip_010", "pattern": "^\\|[\\s\\|]*\\|$", "description": "Table separators", "enabled": true},
        {"id": "skip_011", "pattern": "Dół formularza", "description": "Form bottom (Polish)", "enabled": true},
        {"id": "skip_012", "pattern": "Początek formularza", "description": "Form top (Polish)", "enabled": true}
      ]
    },

    "pdf_specific": {
      "description": "Skip patterns only for PDF files",
      "enabled": true,
      "patterns": [
        {"id": "pdf_skip_001", "pattern": "wydruk roboczy", "description": "Working print", "enabled": true},
        {"id": "pdf_skip_002", "pattern": "Strona \\d+ z \\d+", "description": "Page X of Y", "enabled": true},
        {"id": "pdf_skip_003", "pattern": "TAK\\s*NIE\\s*$", "description": "YES NO checkbox", "enabled": true},
        {"id": "pdf_skip_004", "pattern": "^\\s*[✓✗×]\\s*$", "description": "Checkmarks", "enabled": true},
        {"id": "pdf_skip_005", "pattern": "^\\s*\\[\\s*[Xx]?\\s*\\]\\s*$", "description": "Checkbox brackets", "enabled": true},
        {"id": "pdf_skip_006", "pattern": "^\\s*_{3,}\\s*$", "description": "Form field underscores", "enabled": true},
        {"id": "pdf_skip_007", "pattern": "^\\.{3,}$", "description": "Form field dots", "enabled": true},
        {"id": "pdf_skip_008", "pattern": "^\\s*data\\s*:\\s*$", "description": "Date label", "enabled": true},
        {"id": "pdf_skip_009", "pattern": "^\\s*podpis\\s*:\\s*$", "description": "Signature label", "enabled": true},
        {"id": "pdf_skip_010", "pattern": "\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}", "description": "Timestamps", "enabled": true}
      ]
    },

    "docx_specific": {
      "description": "Skip patterns only for DOCX files",
      "enabled": true,
      "patterns": []
    }
  },

  "prefix_strip_rules": {
    "description": "Remove prefixes from content before processing",
    "enabled": true,
    "global_rules": [
      {"id": "strip_001", "pattern": "^BOLD:", "description": "Remove BOLD: prefix", "enabled": true},
      {"id": "strip_002", "pattern": "^ITALIC:", "description": "Remove ITALIC: prefix", "enabled": true},
      {"id": "strip_003", "pattern": "^UNDERLINED:", "description": "Remove UNDERLINED: prefix", "enabled": true},
      {"id": "strip_004", "pattern": "^UNDERLINE:", "description": "Remove UNDERLINE: prefix", "enabled": true}
    ],
    "per_section_rules": {
      "1.1": [
        {"id": "strip_1.1_001", "pattern": "^Odpowiedź:\\s*", "description": "Remove 'Answer:' prefix", "enabled": true}
      ],
      "1.2": [
        {"id": "strip_1.2_001", "pattern": "^Dane:\\s*", "description": "Remove 'Data:' prefix", "enabled": true}
      ]
    }
  },

  "suffix_strip_rules": {
    "description": "Remove suffixes from content before processing",
    "enabled": true,
    "global_rules": [],
    "per_section_rules": {}
  },

  "inline_strip_rules": {
    "description": "Remove inline patterns from content (footnote references, etc.)",
    "enabled": true,
    "global_rules": [
      {"id": "inline_001", "pattern": "\\[\\d+\\]", "description": "Footnote references [1], [2]", "enabled": true},
      {"id": "inline_002", "pattern": "\\(\\d+\\)", "description": "Footnote references (1), (2)", "enabled": true},
      {"id": "inline_003", "pattern": "⁰|¹|²|³|⁴|⁵|⁶|⁷|⁸|⁹", "description": "Superscript numbers", "enabled": true}
    ],
    "per_section_rules": {}
  },

  "boundary_markers": {
    "description": "Markers indicating start/end of DMP section",
    "start_markers": [
      {"pattern": "DATA MANAGEMENT PLAN", "language": "en", "enabled": true},
      {"pattern": "DATA MANAGEMENT PLAN \\[in English\\]", "language": "en", "enabled": true},
      {"pattern": "PLAN ZARZĄDZANIA DANYMI", "language": "pl", "enabled": true}
    ],
    "end_markers": [
      {"pattern": "ADMINISTRATIVE DECLARATIONS", "language": "en", "enabled": true},
      {"pattern": "OŚWIADCZENIA ADMINISTRACYJNE", "language": "pl", "enabled": true}
    ]
  },

  "section_detection": {
    "description": "Rules for detecting main sections (1, 2, 3, 4, 5, 6)",
    "tier_1_pdf_form_patterns": {
      "description": "Used only for PDF files - detect form-style sections",
      "enabled": true,
      "patterns": [
        {"pattern": "PLAN\\s+ZARZĄDZANIA\\s+DANYMI", "language": "pl"},
        {"pattern": "DATA\\s+MANAGEMENT\\s+PLAN", "language": "en"},
        {"pattern": "Opis\\s+danych\\s+oraz\\s+pozyskiwanie", "language": "pl"},
        {"pattern": "Dokumentacja\\s+i\\s+jakość\\s+danych", "language": "pl"},
        {"pattern": "Przechowywanie\\s+i\\s+tworzenie\\s+kopii", "language": "pl"},
        {"pattern": "Wymogi\\s+prawne", "language": "pl"},
        {"pattern": "Udostępnianie\\s+i\\s+długotrwałe", "language": "pl"},
        {"pattern": "Zadania\\s+związane\\s+z\\s+zarządzaniem", "language": "pl"}
      ]
    },
    "tier_2_numbered_sections": {
      "description": "Detect numbered sections like '1. Section title'",
      "enabled": true,
      "pattern": "^\\s*(\\d+)\\.\\s*(.*?)$",
      "similarity_threshold": 0.5
    },
    "tier_3_title_matching": {
      "description": "Direct section title matching with bilingual mapping",
      "enabled": true,
      "similarity_threshold": 0.6
    },
    "tier_4_subsection_fallback": {
      "description": "Fallback to subsection detection",
      "enabled": true
    }
  },

  "subsection_detection": {
    "description": "Rules for detecting subsections (1.1, 1.2, 2.1, etc.)",
    "numbered_pattern": {
      "description": "Detect numbered subsections like '1.1', '1.2'",
      "enabled": true,
      "pattern": "^\\s*(\\d+\\.\\d+)",
      "variants": [
        "^\\s*(\\d+\\.\\d+)\\.",
        "^\\s*(\\d+\\.\\d+)\\s+",
        "^\\s*(\\d+\\.\\d+)[^\\d]"
      ]
    },
    "english_match": {
      "description": "Direct English subsection text matching",
      "enabled": true,
      "similarity_threshold": 0.8
    },
    "polish_match": {
      "description": "Polish subsection text matching with bilingual mapping",
      "enabled": true,
      "similarity_threshold": 0.4
    },
    "word_based_match": {
      "description": "Word-based matching for fuzzy detection",
      "enabled": true,
      "min_word_count": 3,
      "similarity_ratio": 0.15
    },
    "question_indicators": {
      "description": "Polish question patterns for PDF detection",
      "enabled": true,
      "patterns": [
        "sposób.*?danych",
        "jak.*?będą",
        "jakie.*?dane",
        "gdzie.*?przechowywane",
        "kto.*?odpowiedzialny",
        "środki.*?przeznaczone"
      ],
      "similarity_threshold": 0.2
    }
  },

  "thresholds": {
    "description": "Similarity and confidence thresholds",
    "section_title_similarity": 0.6,
    "english_subsection_similarity": 0.8,
    "polish_subsection_similarity": 0.4,
    "numbered_section_similarity": 0.5,
    "word_match_ratio": 0.15,
    "word_match_min_count": 3,
    "pdf_question_similarity": 0.2,
    "scanned_pdf_chars_per_page": 50,
    "ascii_ratio_garbled": 0.5,
    "max_header_length": 200,
    "long_text_header": 120,
    "short_text_header": 15,
    "header_component_min_matches": 3,
    "max_sentence_length_title": 100
  },

  "header_footer_detection": {
    "description": "Detect and remove grant system headers/footers",
    "enabled": true,
    "component_patterns": {
      "osf": {"pattern": "OSF,?\\s*", "description": "Grant system identifier"},
      "opus": {"pattern": "OPUS-\\d+", "description": "Competition type"},
      "page": {"pattern": "Strona\\s+\\d+", "description": "Page number"},
      "id": {"pattern": "ID:\\s*\\d+", "description": "Document ID"},
      "date": {"pattern": "\\d{4}-\\d{2}-\\d{2}", "description": "Date"},
      "time": {"pattern": "\\d{2}:\\d{2}:\\d{2}", "description": "Time"},
      "timestamp": {"pattern": "\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}", "description": "Full timestamp"}
    },
    "full_patterns": [
      {"pattern": "(OSF|OPUS).{0,50}(Strona|ID).{0,50}\\d{4}-\\d{2}-\\d{2}", "description": "Complex header format 1"},
      {"pattern": "ID:\\s*\\d+.{0,30}\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}", "description": "Complex header format 2"},
      {"pattern": "OPUS-\\d+.{0,50}ID:\\s*\\d+", "description": "OPUS with ID"},
      {"pattern": "^.{0,100}(OSF|OPUS|ID:|Strona).{0,100}(OSF|OPUS|ID:|Strona).{0,100}$", "description": "Multi-component header"}
    ]
  },

  "metadata_extraction": {
    "description": "Patterns for extracting metadata from documents",
    "competition_name": {
      "filename_patterns": [
        "(OPUS|opus)[\\s_-]*(\\d+)?",
        "(PRELUDIUM|preludium|Preludium)[\\s_-]*(\\d+)?",
        "(SONATA|sonata|Sonata)[\\s_-]*(\\d+)?",
        "(SYMFONIA|symfonia|Symfonia)[\\s_-]*(\\d+)?",
        "(MAESTRO|maestro|Maestro)[\\s_-]*(\\d+)?",
        "(HARMONIA|harmonia|Harmonia)[\\s_-]*(\\d+)?",
        "(MINIATURA|miniatura|Miniatura)[\\s_-]*(\\d+)?"
      ],
      "text_patterns": [
        "(?:konkurs|competition|grant)[\\s:]*(?:NCN[\\s:]*)?(OPUS|PRELUDIUM|SONATA|SYMFONIA|MAESTRO|HARMONIA|MINIATURA)[\\s-]*(\\d+)?",
        "(OPUS|PRELUDIUM|SONATA|SYMFONIA|MAESTRO|HARMONIA|MINIATURA)[\\s-]*(\\d+)",
        "ID:\\s*\\d+\\s*,?\\s*(OPUS|PRELUDIUM|SONATA|SYMFONIA|MAESTRO|HARMONIA|MINIATURA)[\\s-]*(\\d+)?"
      ]
    },
    "researcher_name": {
      "filename_patterns": [
        "([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)[-_]([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)",
        "([A-Z][a-z]+)[-_]([A-Z][a-z]+)"
      ],
      "text_patterns": [
        "Kierownik\\s+projektu[:\\s]+(?:dr\\.?|prof\\.?)?\\s*(?:hab\\.?|inż\\.?)?\\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)\\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)",
        "Wykonawca[:\\s]+(?:dr\\.?|prof\\.?)?\\s*(?:hab\\.?|inż\\.?)?\\s*([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)\\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)",
        "Principal\\s+Investigator[:\\s]+(?:Dr\\.?|Prof\\.?)?\\s*([A-Z][a-z]+)\\s+([A-Z][a-z]+)",
        "Researcher[:\\s]+(?:Dr\\.?|Prof\\.?)?\\s*([A-Z][a-z]+)\\s+([A-Z][a-z]+)",
        "(?:^|\\n)([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,})\\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,})\\s*(?:\\n|$)"
      ]
    },
    "date_patterns": [
      "(\\d{2})[-.](\\ d{2})[-. ](\\d{4})",
      "(\\d{4})[-. ](\\d{2})[-. ](\\d{2})"
    ]
  },

  "user_custom_rules": {
    "description": "User-defined custom rules (editable via UI)",
    "enabled": true,
    "rules": []
  }
}
```

---

## Implementation Steps

### Phase 1: Configuration File Creation (Priority: HIGH)

**Step 1.1: Create `config/extraction_rules.json`**
- Location: `c:\VSCode\DMP-ART\DMP-ART\config\extraction_rules.json`
- Copy structure from above
- Migrate all patterns from `extractor.py` lines 274-326
- **Files to modify:** None (new file creation)

**Step 1.2: Create validation schema**
- Use `jsonschema` library for validation
- Add schema validation in `utils/extractor.py`
- Validate on load with clear error messages
- **Files to modify:** `utils/extractor.py` (add validation method)

**Step 1.3: Add to git and documentation**
- Add `config/extraction_rules.json` to version control
- Update `.claude/CLAUDE.md` with new config file documentation
- **Files to modify:** `.claude/CLAUDE.md`

---

### Phase 2: Extractor.py Refactoring (Priority: HIGH)

**Step 2.1: Add rule loading method**

Add new method to `DMPExtractor.__init__()`:

```python
def _load_extraction_rules(self, rules_path='config/extraction_rules.json'):
    """Load extraction rules from JSON configuration file"""
    default_rules_path = os.path.join(os.path.dirname(__file__), '..', rules_path)

    if not os.path.exists(default_rules_path):
        raise FileNotFoundError(f"Extraction rules file not found: {default_rules_path}")

    with open(default_rules_path, 'r', encoding='utf-8') as f:
        rules = json.load(f)

    # Validate schema
    self._validate_rules_schema(rules)

    # Update metadata
    rules['_metadata']['last_loaded'] = datetime.now().isoformat()

    return rules
```

**Location:** Insert after line 93 in `extractor.py`
**Files to modify:** `utils/extractor.py`

**Step 2.2: Replace hardcoded patterns with rule loading**

Replace initialization code (lines 274-326):

```python
# OLD (DELETE):
self.skip_patterns_compiled = [
    re.compile(r"Strona \d+", re.IGNORECASE),
    # ... etc
]

# NEW (REPLACE WITH):
self.extraction_rules = self._load_extraction_rules()

# Compile skip patterns from rules
self.skip_patterns_compiled = self._compile_skip_patterns(
    self.extraction_rules['skip_patterns']['general']['patterns']
)
self.pdf_skip_patterns_compiled = self._compile_skip_patterns(
    self.extraction_rules['skip_patterns']['pdf_specific']['patterns']
)
```

**Location:** Lines 274-326 in `extractor.py`
**Files to modify:** `utils/extractor.py`

**Step 2.3: Add prefix/suffix stripping logic**

Add new method:

```python
def _apply_strip_rules(self, text, section_id=None):
    """Apply prefix, suffix, and inline strip rules to text"""
    rules = self.extraction_rules

    # Apply global prefix strip rules
    if rules['prefix_strip_rules']['enabled']:
        for rule in rules['prefix_strip_rules']['global_rules']:
            if rule['enabled']:
                text = re.sub(rule['pattern'], '', text, flags=re.IGNORECASE)

        # Apply per-section prefix rules
        if section_id and section_id in rules['prefix_strip_rules']['per_section_rules']:
            for rule in rules['prefix_strip_rules']['per_section_rules'][section_id]:
                if rule['enabled']:
                    text = re.sub(rule['pattern'], '', text, flags=re.IGNORECASE)

    # Apply inline strip rules (footnotes, etc.)
    if rules['inline_strip_rules']['enabled']:
        for rule in rules['inline_strip_rules']['global_rules']:
            if rule['enabled']:
                text = re.sub(rule['pattern'], '', text)

    # Apply suffix strip rules
    if rules['suffix_strip_rules']['enabled']:
        for rule in rules['suffix_strip_rules']['global_rules']:
            if rule['enabled']:
                text = re.sub(rule['pattern'] + '$', '', text, flags=re.IGNORECASE)

    return text.strip()
```

**Location:** Insert after `_compile_regex_patterns()` method (after line 326)
**Files to modify:** `utils/extractor.py`

**Step 2.4: Integrate strip rules into extraction pipeline**

Modify `detect_subsection_from_text()` to apply strip rules:

```python
def detect_subsection_from_text(self, text, current_section=None):
    """Detect subsection with strip rules applied first"""

    # NEW: Apply strip rules before detection
    cleaned_text = self._apply_strip_rules(text, section_id=current_section)

    # Rest of existing logic with cleaned_text instead of text
    # ... (existing implementation)
```

**Location:** Line 1207 in `extractor.py` (method start)
**Files to modify:** `utils/extractor.py`

**Step 2.5: Update threshold loading**

Replace hardcoded thresholds with rule-based:

```python
# Load thresholds from rules
thresholds = self.extraction_rules['thresholds']
self.section_similarity_threshold = thresholds['section_title_similarity']
self.english_subsection_threshold = thresholds['english_subsection_similarity']
# ... etc
```

**Location:** Lines in `detect_section_from_text()` and `detect_subsection_from_text()`
**Files to modify:** `utils/extractor.py`

---

### Phase 3: API Endpoints (Priority: MEDIUM)

**Step 3.1: Add extraction rules loading endpoint**

Add to `app.py`:

```python
@app.route('/api/extraction-rules', methods=['GET'])
def load_extraction_rules():
    """Load extraction rules configuration"""
    try:
        rules_path = os.path.join('config', 'extraction_rules.json')
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        return jsonify({'success': True, 'rules': rules})
    except Exception as e:
        app.logger.error(f'Error loading extraction rules: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Location:** After existing config endpoints (around line 1050)
**Files to modify:** `app.py`

**Step 3.2: Add extraction rules saving endpoint**

```python
@app.route('/api/extraction-rules', methods=['POST'])
def save_extraction_rules():
    """Save extraction rules configuration"""
    try:
        data = request.json
        rules_path = os.path.join('config', 'extraction_rules.json')

        # Validate structure
        required_keys = ['skip_patterns', 'prefix_strip_rules', 'section_detection']
        if not all(key in data for key in required_keys):
            return jsonify({'success': False, 'message': 'Invalid rules structure'}), 400

        # Update metadata
        data['_metadata']['last_updated'] = datetime.now().isoformat()
        data['_metadata']['rule_count'] = _count_rules(data)

        # Save with backup
        if os.path.exists(rules_path):
            backup_path = rules_path.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            shutil.copy(rules_path, backup_path)

        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': 'Extraction rules saved successfully'})
    except Exception as e:
        app.logger.error(f'Error saving extraction rules: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Location:** After GET endpoint (around line 1070)
**Files to modify:** `app.py`

**Step 3.3: Add rule testing endpoint**

```python
@app.route('/api/test-extraction-rules', methods=['POST'])
def test_extraction_rules():
    """Test extraction rules on a cached file"""
    try:
        data = request.json
        cache_id = data.get('cache_id')
        test_rules = data.get('rules')  # Optional: test with custom rules

        # Load cached file
        cache_path = os.path.join('outputs', 'cache', f'cache_{cache_id}.json')
        if not os.path.exists(cache_path):
            return jsonify({'success': False, 'message': 'Cache file not found'}), 404

        # Re-run extraction with test rules
        # ... (implementation)

        return jsonify({
            'success': True,
            'before': original_extraction,
            'after': new_extraction,
            'diff': diff_summary
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Location:** After save endpoint (around line 1100)
**Files to modify:** `app.py`

---

### Phase 4: UI Implementation (Priority: MEDIUM)

**Step 4.1: Rename Template Editor to Configuration**

Update `templates/template_editor.html`:

```html
<!-- OLD: -->
<title>Template Editor - DMP-ART</title>
<h1>Template Editor</h1>

<!-- NEW: -->
<title>Configuration - DMP-ART</title>
<h1>Configuration</h1>
```

**Location:** Lines 3, 15 in `template_editor.html`
**Files to modify:** `templates/template_editor.html`

Update navigation links in all templates:

```html
<!-- OLD: -->
<a href="/template_editor">Template Editor</a>

<!-- NEW: -->
<a href="/template_editor">Configuration</a>
```

**Location:** `templates/index.html`, `templates/review.html`, `templates/documentation.html`
**Files to modify:** Multiple template files

**Step 4.2: Add Extraction Rules tab**

Add new tab to `template_editor.html`:

```html
<div class="tabs">
    <button class="tab-btn active" data-tab="templates">DMP Templates</button>
    <button class="tab-btn" data-tab="quick-comments">Quick Comments</button>
    <button class="tab-btn" data-tab="categories">Categories</button>
    <button class="tab-btn" data-tab="extraction-rules">Extraction Rules</button> <!-- NEW -->
</div>

<div id="extraction-rules" class="tab-content">
    <h2>Extraction Rules Configuration</h2>
    <p>Customize how DMP content is detected and extracted from documents.</p>

    <!-- Accordion sections -->
    <div class="rule-accordion">
        <div class="rule-section">
            <h3 class="accordion-header">Skip Patterns</h3>
            <div class="accordion-content">
                <!-- Skip pattern editor -->
            </div>
        </div>

        <div class="rule-section">
            <h3 class="accordion-header">Prefix Strip Rules</h3>
            <div class="accordion-content">
                <!-- Prefix strip rule editor -->
            </div>
        </div>

        <!-- More sections... -->
    </div>

    <button id="save-extraction-rules" class="btn btn-primary">Save Extraction Rules</button>
</div>
```

**Location:** After existing tabs (around line 180)
**Files to modify:** `templates/template_editor.html`

**Step 4.3: Create extraction rules editor component**

Add JavaScript in `static/js/template_editor.js`:

```javascript
// Load extraction rules
function loadExtractionRules() {
    fetch('/api/extraction-rules')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderExtractionRulesEditor(data.rules);
            }
        });
}

// Render rules editor
function renderExtractionRulesEditor(rules) {
    const container = document.querySelector('#extraction-rules .rule-accordion');
    container.innerHTML = '';

    // Render skip patterns
    container.appendChild(createSkipPatternsEditor(rules.skip_patterns));

    // Render prefix strip rules
    container.appendChild(createPrefixStripEditor(rules.prefix_strip_rules));

    // Render user custom rules (most important for users)
    container.appendChild(createCustomRulesEditor(rules.user_custom_rules));
}

// Create custom rules editor (user-editable section)
function createCustomRulesEditor(customRules) {
    const section = document.createElement('div');
    section.className = 'rule-section';
    section.innerHTML = `
        <h3 class="accordion-header">Custom Rules</h3>
        <div class="accordion-content">
            <p>Add your own extraction rules to handle specific document formats.</p>
            <button id="add-custom-rule" class="btn btn-secondary">Add Custom Rule</button>
            <div id="custom-rules-list"></div>
        </div>
    `;

    // Populate existing rules
    const rulesList = section.querySelector('#custom-rules-list');
    customRules.rules.forEach((rule, index) => {
        rulesList.appendChild(createCustomRuleItem(rule, index));
    });

    return section;
}

// Save extraction rules
document.getElementById('save-extraction-rules').addEventListener('click', () => {
    const rules = collectExtractionRulesFromUI();

    fetch('/api/extraction-rules', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(rules)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Extraction rules saved successfully', 'success');
        } else {
            showToast(data.message, 'error');
        }
    });
});
```

**Location:** End of `static/js/template_editor.js` (around line 1000)
**Files to modify:** `static/js/template_editor.js`

---

### Phase 5: Testing and Validation (Priority: HIGH)

**Step 5.1: Test with problematic file**

Create test script: `test_extraction_rules.py`

```python
import json
from utils.extractor import DMPExtractor

# Test with Data Management Plan_S2025.docx (known issue: section 1.2 in unconnected)
extractor = DMPExtractor()
result = extractor.process_file('uploads/Data Management Plan_S2025.docx', 'outputs')

# Load cache
cache_path = f"outputs/cache/{result['cache_file']}"
with open(cache_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check if section 1.2 is correctly assigned
print("Section 1.2 content:", data['1.2']['paragraphs'])
print("Unconnected text:", data['_unconnected_text'])

# Validate: section 1.2 should have content, not "Not answered"
assert data['1.2']['paragraphs'][0] != "Not answered in the source document.", "Section 1.2 still in unconnected text!"
print("✓ Test passed: Section 1.2 correctly assigned")
```

**Location:** New file `c:\VSCode\DMP-ART\DMP-ART\test_extraction_rules.py`
**Files to modify:** None (new file)

**Step 5.2: Create before/after comparison**

```python
# Compare old vs new extraction
def compare_extractions(old_cache_id, new_cache_id):
    with open(f'outputs/cache/cache_{old_cache_id}.json') as f:
        old = json.load(f)
    with open(f'outputs/cache/cache_{new_cache_id}.json') as f:
        new = json.load(f)

    differences = {}
    for section_id in old.keys():
        if section_id.startswith('_'):
            continue
        old_text = ' '.join(old[section_id]['paragraphs'])
        new_text = ' '.join(new[section_id]['paragraphs'])
        if old_text != new_text:
            differences[section_id] = {
                'old': old_text[:200] + '...',
                'new': new_text[:200] + '...'
            }

    return differences
```

**Step 5.3: Validate regex patterns on save**

Add validation method:

```python
def validate_regex_pattern(pattern):
    """Validate regex pattern syntax"""
    try:
        re.compile(pattern)
        return True, "Valid pattern"
    except re.error as e:
        return False, f"Invalid regex: {str(e)}"
```

Use in save endpoint:

```python
# In save_extraction_rules():
for rule in data['skip_patterns']['general']['patterns']:
    valid, message = validate_regex_pattern(rule['pattern'])
    if not valid:
        return jsonify({'success': False, 'message': f"Rule {rule['id']}: {message}"}), 400
```

---

## File Modification Summary

| File | Changes | Lines Modified | New/Modify |
|------|---------|----------------|------------|
| `config/extraction_rules.json` | Create new config file | N/A | NEW |
| `utils/extractor.py` | Add rule loading, strip logic | ~200 lines | MODIFY |
| `app.py` | Add API endpoints | ~150 lines | MODIFY |
| `templates/template_editor.html` | Rename, add tab | ~100 lines | MODIFY |
| `static/js/template_editor.js` | Add rules editor | ~300 lines | MODIFY |
| `.claude/CLAUDE.md` | Update documentation | ~50 lines | MODIFY |
| `test_extraction_rules.py` | Create test script | ~100 lines | NEW |

**Total estimated changes:** ~900 lines across 7 files

---

## Testing Plan

### Test Case 1: Prefix Strip (BOLD:)

**Problem:** Section 1.2 content with "BOLD:1.2." prefix ends up in unconnected text

**Expected behavior:**
- "BOLD:" prefix stripped before subsection detection
- "1.2" correctly recognized as subsection 1.2
- Content assigned to section 1.2, not unconnected text

**Test file:** `uploads/Data Management Plan_S2025.docx`

**Validation:**
```python
assert data['1.2']['paragraphs'][0] != "Not answered in the source document."
assert len(data['_unconnected_text']) == 0 or '1.2' not in data['_unconnected_text'][0]['text']
```

### Test Case 2: Section Assignment

**Problem:** Sections 2.1-6.1 all dumped into section 6.1

**Expected behavior:**
- Each section (2.1, 2.2, 3.1, etc.) gets its own content
- Section 6.1 only contains 6.1 content, not 2.1-5.4

**Test file:** `uploads/Data Management Plan_S2025.docx`

**Validation:**
```python
assert 'BOLD:2.1' not in ' '.join(data['6.1']['paragraphs'])
assert 'BOLD:2.1' in ' '.join(data['2.1']['paragraphs'])
```

### Test Case 3: Skip Patterns

**Problem:** Page numbers, form markers appearing in extracted content

**Expected behavior:**
- "Strona 1", "Page 2" removed from content
- "Dół formularza", "Początek formularza" removed

**Test files:** All PDF files in `uploads/`

**Validation:**
```python
for section in data.values():
    if isinstance(section, dict) and 'paragraphs' in section:
        for para in section['paragraphs']:
            assert 'Strona ' not in para
            assert 'Dół formularza' not in para
```

### Test Case 4: Custom User Rule

**User scenario:** User wants to remove "Odpowiedź:" prefix from all sections

**Steps:**
1. Open Configuration page
2. Navigate to "Custom Rules" tab
3. Click "Add Custom Rule"
4. Fill: Pattern = `^Odpowiedź:\s*`, Description = "Remove Answer prefix"
5. Save rules
6. Upload test file with "Odpowiedź:" prefix
7. Verify prefix removed in cache file

**Expected behavior:**
- Custom rule saved to `config/extraction_rules.json` under `user_custom_rules`
- Prefix stripped during extraction
- Content correctly assigned

---

## Performance Considerations

### Current Performance (Baseline)

From `extractor.py` existing optimizations:
- Pre-compiled regex patterns (99.9% faster than inline compilation)
- LRU caching for text similarity checks
- Pre-computed subsection word index

**Existing performance:** ~2-5 seconds per document (based on `FINAL_TEST_RESULTS.md`)

### Expected Performance Impact

**Rule loading:** +0.1-0.2 seconds (one-time at initialization)
**Strip rule application:** +0.05-0.1 seconds per document (minimal overhead)
**Net impact:** ~+5% processing time (acceptable)

### Optimization Strategy

1. **Pre-compile all patterns** at `__init__()` time
2. **Cache compiled patterns** in instance variables
3. **Apply rules in order** of frequency (most common patterns first)
4. **Skip disabled rules** entirely (no regex compilation)

```python
# Efficient pattern compilation
def _compile_skip_patterns(self, pattern_list):
    """Compile only enabled patterns"""
    return [
        re.compile(p['pattern'], re.IGNORECASE)
        for p in pattern_list
        if p.get('enabled', True)  # Skip disabled rules
    ]
```

---

## Rollback Plan

If issues occur after implementation:

### Quick Rollback (Emergency)

1. **Revert extractor.py** to use hardcoded patterns:
   ```bash
   git checkout HEAD~1 utils/extractor.py
   ```

2. **Keep config file** for future use (no harm in having it)

3. **Restart application:**
   ```bash
   python app.py
   ```

### Partial Rollback (Keep UI changes)

1. **Add fallback logic** in `_load_extraction_rules()`:
   ```python
   def _load_extraction_rules(self):
       try:
           # Try to load from file
           return self._load_from_file()
       except:
           # Fall back to hardcoded patterns
           app.logger.warning("Using hardcoded extraction rules (fallback)")
           return self._get_hardcoded_rules()
   ```

2. **Keep UI** for future configuration

---

## Migration Path for Existing Deployments

For users upgrading from version without `extraction_rules.json`:

### Step 1: Auto-create default config

Add to `app.py` startup:

```python
def ensure_extraction_rules_exist():
    """Create default extraction_rules.json if missing"""
    rules_path = 'config/extraction_rules.json'
    if not os.path.exists(rules_path):
        app.logger.info("Creating default extraction_rules.json...")
        default_rules = generate_default_extraction_rules()
        with open(rules_path, 'w', encoding='utf-8') as f:
            json.dump(default_rules, f, ensure_ascii=False, indent=2)

# Call at startup
ensure_extraction_rules_exist()
```

### Step 2: Migration notice

Show banner in UI:

```html
<div class="migration-notice">
    <strong>New Feature:</strong> Extraction rules are now configurable!
    Visit <a href="/template_editor#extraction-rules">Configuration → Extraction Rules</a> to customize.
</div>
```

---

## Documentation Updates Required

### 1. Update `.claude/CLAUDE.md`

Add section:

```markdown
## Extraction Rules Configuration

**Location:** `config/extraction_rules.json`

**Purpose:** Defines patterns for section detection, content filtering, and text cleanup

**User-editable sections:**
- `user_custom_rules`: Add custom extraction rules
- `prefix_strip_rules.per_section_rules`: Per-section prefix removal
- `inline_strip_rules.per_section_rules`: Per-section inline removal

**System sections (edit with caution):**
- `skip_patterns`: Content to skip during extraction
- `section_detection`: Rules for finding DMP sections
- `subsection_detection`: Rules for finding subsections
- `thresholds`: Similarity thresholds for fuzzy matching

**Editing:**
- Via UI: Configuration → Extraction Rules tab
- Via file: Edit `config/extraction_rules.json` directly
- Automatic backup created on save
```

### 2. Update `README.md`

Add to Features section:

```markdown
- ✅ **Configurable Extraction Rules** - Customize section detection and content filtering
```

### 3. Create user guide

File: `docs/extraction_rules_guide.md`

```markdown
# Extraction Rules User Guide

## What are Extraction Rules?

Extraction rules control how DMP-ART finds and extracts content from your documents...

## How to Add a Custom Rule

1. Open Configuration page
2. Click "Extraction Rules" tab
3. Scroll to "Custom Rules" section
4. Click "Add Custom Rule"
5. Fill in pattern and description
6. Save changes

## Common Use Cases

### Remove unwanted prefix from section

Pattern: `^Prefix:\s*`

### Remove footnote references

Pattern: `\[\d+\]`

...
```

---

## Success Criteria

### Must Have (v1.0)

- ✅ Config file created with all existing patterns migrated
- ✅ Extractor.py loads rules from config (no more hardcoded patterns)
- ✅ Prefix strip rules fix section 1.2 assignment issue
- ✅ UI tab added to Configuration page
- ✅ User can add/edit/delete custom rules via UI
- ✅ Regex validation on save
- ✅ Automatic backup on save
- ✅ Test script confirms section 1.2 fix

### Should Have (v1.1)

- ✅ Rule testing endpoint (before/after preview)
- ✅ Rule usage statistics
- ✅ Import/export rules
- ✅ Rule templates library

### Nice to Have (v2.0)

- ✅ Visual regex builder
- ✅ Pattern highlighting in UI
- ✅ Machine learning pattern suggestions
- ✅ Community rule sharing

---

## Timeline Estimate

**Phase 1 (Config Creation):** 2-3 hours
**Phase 2 (Extractor Refactoring):** 4-5 hours
**Phase 3 (API Endpoints):** 2-3 hours
**Phase 4 (UI Implementation):** 3-4 hours
**Phase 5 (Testing):** 2-3 hours

**Total estimated time:** 13-18 hours

**Recommended sprints:**
- Sprint 1: Phases 1-2 (config + extractor)
- Sprint 2: Phase 3 (API)
- Sprint 3: Phases 4-5 (UI + testing)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Regex pattern errors break extraction | Medium | High | Validation on save, try-catch fallback |
| Performance degradation | Low | Medium | Pre-compile patterns, benchmark tests |
| User breaks config file with invalid JSON | Medium | Medium | JSON schema validation, auto-backup |
| Existing cached files become incompatible | Low | Low | Cache format unchanged, backward compatible |
| Rule changes not applied until restart | High | Low | Add "Reload Rules" button in UI |

---

## Research Sources

Based on best practices research:

- [Complete JSON Guide 2025: Syntax, Best Practices & Real Examples](https://jsonconsole.com/blog/complete-guide-json-everything-you-need-know-2025)
- [Datadog Parsing Documentation](https://docs.datadoghq.com/logs/log_configuration/parsing/) - Grok patterns
- [KIANMENG.ORG: Storing and Using Regex in External Config File for Python](https://www.kianmeng.org/2021/09/storing-and-using-regex-in-external.html)
- [Working with Python Configuration Files: Tutorial & Best Practices - Configu](https://configu.com/blog/working-with-python-configuration-files-tutorial-best-practices/)
- [Docparser Documentation](https://help.docparser.com/) - Document parsing patterns

---

## Next Steps

Once this plan is approved:

1. Create `config/extraction_rules.json` with all migrated patterns
2. Refactor `extractor.py` to load rules from config
3. Test with problematic file (`Data Management Plan_S2025.docx`)
4. Implement API endpoints
5. Build UI in Configuration page
6. Full regression testing with all 16 files in `uploads/`
7. Update documentation
8. Deploy and monitor

---

**Plan Status:** ✅ READY FOR IMPLEMENTATION
**Approval Required:** Yes (user confirmation)
**Estimated Completion:** 2-3 days (with testing)
