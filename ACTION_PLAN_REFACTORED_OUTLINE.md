# DMP-ART Refactored Action Plan - OUTLINE

**Version:** 2.0 (Refactored)
**Date:** 2025-11-16
**Focus:** Enhancement & Optimization (Keep all existing features)

---

## IMPORTANT NOTE
**We KEEP all existing functionality - we only ADD new features and optimize existing ones.**

---

## Phase 1: Analysis & Verification (Week 1)

### 1.1 HTML Structure Analysis
- Verify all DOM connections work correctly
- Test sidebar-main content communication
- Verify category buttons functionality
- Check textarea-feedback connections
- Document any broken connections

### 1.2 Existing Functions Inventory
- Map all current functions in script.js
- Map all routes in app.py
- Map all extractor methods
- Identify reusable patterns
- Create function dependency map

### 1.3 PZD Files Analysis
- Create /pzd folder with test files
- Test current extraction with PZD files
- Document extraction success rate
- Identify improvement areas

---

## Phase 2: Metadata Extraction & Smart Naming (Week 2-3)

### 2.1 Metadata Extraction from DMP
**Extract:**
- Researcher surname (Nazwisko)
- Researcher first name (Imię)
- Competition name (Nazwa konkursu: OPUS, PRELUDIUM, etc.)
- Competition edition (Edycja konkursu: 25, 26, etc.)
- Document creation date (Data utworzenia)

**Implementation:**
- Extend DMPExtractor class
- Add metadata detection patterns (Polish & English)
- Store in cache JSON

### 2.2 Intelligent Filename Generation
**Format:** `DMP_{Surname}_{FirstInitial}_{Competition}_{Edition}_{YYYYMMDD}.docx`
**Example:** `DMP_Kowalski_J_OPUS_25_20251116.docx`

**Same for reviews:** `Review_{Surname}_{FirstInitial}_{Competition}_{Edition}_{YYYYMMDD}.txt`

---

## Phase 3: JSON Export with Metadata (Week 3-4)

### 3.1 Structured JSON Export
**Structure:**
```json
{
  "metadata": {
    "researcher_surname": "Kowalski",
    "researcher_firstname": "Jan",
    "competition_name": "OPUS",
    "competition_edition": "25",
    "creation_date": "2025-11-16",
    "review_date": "2025-11-16",
    "reviewer": "system"
  },
  "dmp_content": {
    "1.1": "extracted text...",
    "1.2": "extracted text..."
  },
  "review_feedback": {
    "1.1": "reviewer comments...",
    "1.2": "reviewer comments..."
  }
}
```

### 3.2 Export Options
- Keep current: Copy to clipboard (text)
- Keep current: Download as TXT
- **NEW:** Download as JSON (structured)
- **NEW:** Download as DOCX (formatted - already planned, implement)

---

## Phase 4: Bilingual Comments Switcher (Week 4-5)

### 4.1 Dual Language Comment System
**Structure:**
```json
{
  "quick_comments": [
    {
      "name_en": "minor adjustments",
      "name_pl": "drobne poprawki",
      "text_en": "The plan is very good, just need to add some information.",
      "text_pl": "Plan jest bardzo dobry, wystarczy dodać kilka informacji."
    }
  ]
}
```

### 4.2 Language Switcher UI
- Add language toggle button (PL/EN flag icons)
- Store preference in localStorage
- Switch only comment text, NOT interface
- Interface stays English
- Category templates also bilingual

---

## Phase 5: File Format Optimization (Week 5-8)

### 5.1 DOCX Extraction Optimization
**Current issues to debug:**
- Table extraction accuracy
- Text formatting preservation
- Multi-column layouts
- Nested tables

**Improvements:**
- Better table structure detection
- Cell merging handling
- Enhanced formatting extraction
- Test with PZD files

### 5.2 PDF Extraction Optimization
**Current issues:**
- Limited to text-based PDFs only
- Header/footer filtering too aggressive?

**Improvements:**
- Better header/footer detection
- Form field extraction
- Multi-column layout handling

### 5.3 RTF Support (NEW)
**Implementation:**
- Add striprtf library
- Create RTF extractor method
- Convert RTF → plain text
- Apply same DMP detection logic

### 5.4 OCR Support (NEW)
**For files without text layer:**
- PDF images (scanned documents)
- DOCX with embedded images
- Direct image files (PNG, JPG)

**Tools:**
- Tesseract OCR
- pytesseract Python wrapper
- pdf2image for PDF → images
- pillow for image handling

**Implementation:**
- Detect if PDF has text layer
- If no text: convert to images → OCR
- For DOCX: extract images → OCR → combine with text
- For image files: direct OCR

---

## Phase 6: Testing & Validation (Week 8-9)

### 6.1 PZD Files Testing
- Test all file formats with PZD samples
- Measure extraction accuracy
- Document edge cases
- Create test report

### 6.2 HTML Connection Validation
- Test all UI interactions
- Verify sidebar functionality
- Test category comment insertion
- Verify feedback compilation
- Cross-browser testing

### 6.3 Integration Testing
- End-to-end workflow testing
- Metadata extraction accuracy
- JSON export validation
- Bilingual switching
- File format handling

---

## Phase 7: Documentation & Deployment (Week 9-10)

### 7.1 Update Documentation
- API documentation
- User guide updates
- Developer guide
- Configuration guide

### 7.2 Deployment
- Requirements update
- Environment setup
- Migration guide
- Release notes

---

## Technology Stack Additions

**New Dependencies:**
```
# OCR Support
pytesseract==0.3.10
pdf2image==1.16.3
Pillow==10.1.0

# RTF Support
striprtf==0.0.26

# System requirements:
# - Tesseract OCR (system package)
# - poppler-utils (for pdf2image)
```

---

## Priority Matrix

**HIGH Priority (Must Have):**
1. Metadata extraction
2. Smart filenames
3. JSON export
4. DOCX/PDF extraction optimization
5. HTML structure validation

**MEDIUM Priority (Should Have):**
1. Bilingual comments
2. RTF support
3. Basic OCR for PDFs

**LOW Priority (Nice to Have):**
1. OCR for images in DOCX
2. Direct image file OCR
3. Advanced table structure preservation

---

## Success Metrics

- [ ] All existing features still work
- [ ] Metadata extracted from 90%+ of DMPs
- [ ] Smart filenames generated correctly
- [ ] JSON export validated
- [ ] Bilingual comments working
- [ ] RTF files supported
- [ ] OCR works for scanned PDFs
- [ ] PZD files extraction tested
- [ ] HTML connections verified
- [ ] Zero regression in existing functionality

---

## Risk Assessment

**Low Risk:**
- Metadata extraction (additive)
- Filename generation (doesn't break existing)
- JSON export (new feature)

**Medium Risk:**
- OCR implementation (new dependencies)
- RTF support (new file type)
- Extraction optimization (could break existing)

**Mitigation:**
- Extensive testing with existing files
- Keep old extraction as fallback
- Feature flags for new functionality

---

## Next Steps

1. Review this outline with stakeholders
2. Prioritize phases
3. Set up development environment with new dependencies
4. Create test file repository (PZD folder)
5. Begin Phase 1: Analysis

---

**END OF OUTLINE**
