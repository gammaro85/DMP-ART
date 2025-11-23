# Documentation Guidelines for AI Agents

**Version:** 1.0
**Last Updated:** 2025-11-23
**Purpose:** Standards for maintaining and updating DMP-ART documentation

---

## Core Principles

### 1. **Documentation is for AI Agents, Not Humans**

This project's documentation is optimized for AI code assistants (Claude, Copilot, etc.), not end users.

**DO:**
- Focus on codebase structure, patterns, and conventions
- Include technical implementation details
- Provide context for design decisions
- Document edge cases and gotchas
- Include code examples with file references

**DON'T:**
- Write user guides or tutorials
- Include installation instructions for end users
- Create marketing/sales content
- Add screenshots or visual tutorials
- Write beginner-friendly explanations

### 2. **Single Source of Truth**

Every piece of information should exist in exactly ONE location.

**Pattern:**
```
Question: "What is the DMP structure?"
Answer Location: config/dmp_structure.json
Documentation Reference: .claude/CLAUDE.md:559-568
```

**Anti-Pattern:**
```
❌ DMP structure defined in:
   - config/dmp_structure.json
   - app.py (DMP_TEMPLATES constant)
   - utils/extractor.py (DMP_TEMPLATES constant)
   - README.md (hardcoded example)
```

### 3. **Modify Existing Files, Don't Create New Ones**

When updating documentation:

✅ **DO:**
- Update `.claude/CLAUDE.md` with new patterns
- Add to `HISTORY.md` for historical changes
- Modify `FINAL_TEST_RESULTS.md` with new test data
- Update `README.md` for project overview changes

❌ **DON'T:**
- Create `NEW_FEATURE_DOCS.md`
- Create `OPTIMIZATION_REPORT_V2.md`
- Create `IMPLEMENTATION_SUMMARY_FINAL_FINAL.md`
- Create `GUIDE_TO_X.md`

### 4. **Code References Over Prose**

Show, don't tell. Reference actual code locations.

**Good:**
```markdown
Flask routes follow this pattern (app.py:139-146):

```python
@app.route('/endpoint', methods=['POST'])
def function_name():
    try:
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Bad:**
```markdown
Flask routes should return JSON with success and error handling.
They should try-except and return appropriate status codes.
```

### 5. **Actionable Information Only**

Every section should answer: "What does an AI agent need to DO?"

**Good:**
```markdown
## Adding a New Route

1. Open app.py
2. Add route after line 384 (maintain alphabetical order)
3. Follow pattern from app.py:139-146
4. Return standardized JSON response
5. Add error logging with app.logger.error()
```

**Bad:**
```markdown
## Adding a New Route

Routes are important in Flask. They handle HTTP requests and
return responses to the client. You should think about REST
principles when designing routes...
```

---

## Documentation Structure

### Primary Files (AI Agent Focus)

#### `.claude/CLAUDE.md` - Main Reference
**Purpose:** Complete AI agent guide to codebase
**Length:** ~750 lines
**Updates:** When patterns change, new features added, architecture evolves

**Required Sections:**
1. Project Overview (what, why, who, metrics)
2. Technology Stack (versions, dependencies)
3. Codebase Structure (critical files, directories)
4. Code Patterns (Flask routes, DMPExtractor, Frontend JS, CSS)
5. Common Development Tasks (with code examples)
6. Testing Guidelines (commands, procedures)
7. Common Issues and Solutions (troubleshooting)
8. Performance Optimizations (implementations, metrics)
9. Security Considerations (implemented, missing)
10. Deployment Notes (production checklist)
11. Quick Reference (file extensions, section IDs, cache structure, git commands)
12. Future Roadmap
13. Key Design Decisions (ADRs)
14. Working with Codebase (best practices)
15. Recent Changes (version-specific updates)

#### `HISTORY.md` - Project Evolution
**Purpose:** Chronological record of all major changes
**Length:** ~500-800 lines
**Updates:** After each significant feature/fix/optimization

**Required Sections:**
1. Project Genesis (original problem, solution vision, target metrics)
2. Version History (changelog with technical details)
3. Major Milestones (key achievements)
4. Architecture Evolution (diagrams of before/after)
5. Performance Optimizations (timeline, implementations, metrics)
6. Feature Development (major features by version)
7. Technical Debt Resolution (what was fixed, how, impact)
8. Lessons Learned (what worked, challenges, future considerations)
9. Key Metrics Evolution (graphs/tables of improvements)
10. Current State (production readiness assessment)

#### `FINAL_TEST_RESULTS.md` - Test Report
**Purpose:** Current state of testing and quality metrics
**Length:** ~500 lines
**Updates:** After running full test suite or adding tests

**Required Sections:**
1. Executive Summary (success rate, key achievements)
2. Test Results Overview (metrics, distribution)
3. Improvements Implemented (technical details)
4. Detailed File Analysis (file-by-file breakdown)
5. Performance Comparison (before/after tables)
6. Test Suite Results (unit tests, integration tests)
7. Technical Improvements Summary (code quality)
8. Deployment Recommendations (immediate actions)
9. Known Limitations (edge cases, frequency)
10. Success Criteria Assessment

#### `README.md` - Project Overview
**Purpose:** High-level project description (for GitHub)
**Length:** ~150-200 lines (simplified)
**Updates:** When project scope or key features change

**Required Sections:**
1. Project Name and Badges
2. Purpose (one paragraph)
3. Key Features (bullet points)
4. Technology Stack (table)
5. Quick Start (minimal commands)
6. Project Structure (tree view)
7. License
8. Recent Updates (link to HISTORY.md)

### Secondary Files (Specific Contexts)

#### `.github/agents/my-agent.agent.md`
**Purpose:** GitHub Copilot agent configuration
**Updates:** When agent behavior needs tuning

#### `.github/copilot-instructions.md`
**Purpose:** Onboarding instructions for GitHub Copilot and Claude agents
**Updates:** When setup commands, architecture, or common patterns change
**Length:** ~300 lines (concise, 2-page limit)
**Content:** Setup validation, build commands, architecture overview, troubleshooting

#### `requirements.txt`
**Purpose:** Python dependencies
**Updates:** When dependencies change

---

## Documentation Best Practices from Web Standards

### 1. **Information Architecture (IA) Principles**

Based on research from Nielsen Norman Group and W3C:

**Hierarchy:**
```
.claude/CLAUDE.md (L1: Main reference)
├── HISTORY.md (L2: Context/background)
├── FINAL_TEST_RESULTS.md (L2: Quality metrics)
└── README.md (L2: Overview)
```

**Navigation:**
- Each document has clear Table of Contents
- Internal links to specific sections
- Cross-references between documents

**Chunking:**
- Information grouped by task/context
- Maximum 50 lines per section
- Code examples self-contained

### 2. **Technical Writing Standards**

Based on Google Developer Documentation Style Guide:

**Voice:**
- Active voice: "Run the tests" (not "Tests should be run")
- Present tense: "The extractor processes files" (not "will process")
- Direct address: "You can add routes" (not "One can add")

**Clarity:**
- One idea per sentence
- Short paragraphs (3-5 sentences max)
- Specific over general

**Examples:**
- Every pattern includes code example
- File paths referenced explicitly
- Line numbers for large files

### 3. **Code Documentation Standards**

Based on PEP 257 and JSDoc:

**Python:**
```python
def process_file(self, file_path, output_dir, progress_callback=None):
    """
    Process a DMP file and extract content into structured sections.

    Args:
        file_path (str): Absolute path to PDF or DOCX file
        output_dir (str): Directory for output files
        progress_callback (callable, optional): Function(message, progress)

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'filename': str,
            'cache_id': str (UUID),
            'metadata': dict
        }

    Raises:
        ValueError: If file format not supported
        IOError: If file cannot be read

    Example:
        extractor = DMPExtractor()
        result = extractor.process_file('proposal.pdf', 'outputs')
        if result['success']:
            print(f"Cached as: {result['cache_id']}")
    """
```

**JavaScript:**
```javascript
/**
 * Connect to SSE progress stream for real-time updates
 *
 * @param {string} sessionId - Unique session identifier (UUID)
 * @param {function} onProgress - Callback(data) for progress updates
 * @param {function} onComplete - Callback(data) on completion
 * @param {function} onError - Callback(data) on error
 * @returns {EventSource} SSE connection (call .close() to terminate)
 *
 * @example
 * const stream = connectProgressStream(
 *     sessionId,
 *     (data) => updateProgressBar(data.progress),
 *     (data) => window.location.href = data.redirect_url,
 *     (data) => showError(data.message)
 * );
 */
```

### 4. **Version Control Integration**

Based on Conventional Commits and Semantic Versioning:

**Commit Messages:**
```
feat(extractor): Add OCR support for scanned PDFs

- Integrated Tesseract OCR with Polish + English packs
- Auto-detection of scanned PDFs (< 50 chars/page)
- Automatic fallback when PyPDF2 fails
- 100% success rate on previously failing scans

Closes #42
```

**Documentation Updates:**
- Update `.claude/CLAUDE.md` → Recent Changes section
- Add to `HISTORY.md` → appropriate version
- Update `FINAL_TEST_RESULTS.md` if tests affected
- Bump version in README.md badges

### 5. **Accessibility for AI Parsers**

Based on machine-readable documentation principles:

**Structure:**
- Markdown headers (H1-H6) for hierarchy
- Code fences with language tags
- Tables for structured data
- Lists for sequences/options

**Consistency:**
- File paths: Always absolute or relative to project root
- Code references: `file.py:line` or `file.py:start-end`
- Version numbers: Semantic versioning (X.Y.Z)
- Dates: ISO 8601 (YYYY-MM-DD)

**Searchability:**
- Unique section anchors
- Keywords in headers
- Cross-references with links
- Table of contents

---

## Update Workflows

### When to Update Documentation

#### `.claude/CLAUDE.md` Updates

**Trigger: New Code Pattern**
```markdown
Example: Added Server-Sent Events for progress

Update Location: .claude/CLAUDE.md
Section: ## Code Patterns and Conventions
Add: ### Server-Sent Events Pattern
Include:
- Backend setup (app.py example)
- Frontend connection (script.js example)
- Thread safety considerations
- Error handling pattern
```

**Trigger: Architecture Change**
```markdown
Example: Moved from monolithic JS to modules

Update Location: .claude/CLAUDE.md
Section: ## Codebase Structure → ### Critical Files
Change:
- static/js/script.js (42KB, all logic)
+ static/js/script.js (42KB, main logic)
+ static/js/template_editor.js (28KB)
+ static/js/dark-mode.js (4KB)
```

**Trigger: New Common Task**
```markdown
Example: How to add SSE endpoint

Update Location: .claude/CLAUDE.md
Section: ## Common Development Tasks
Add: ### Adding a Server-Sent Events Endpoint
Steps with code examples from app.py
```

**Trigger: Dependency Update**
```markdown
Example: Flask 3.1.0 → 3.1.1

Update Location: .claude/CLAUDE.md
Section: ## Technology Stack → Backend
Change: Flask 3.1.0 → Flask 3.1.1
Section: ## Recent Changes
Add note about security patches
```

#### `HISTORY.md` Updates

**Trigger: Version Bump**
```markdown
Example: v0.8.0 → v0.8.1

Update Location: HISTORY.md
Section: ## Version History
Add: ### v0.8.1 (YYYY-MM-DD)
Include:
- Major Changes
- Codebase Growth
- New Features
```

**Trigger: Performance Optimization**
```markdown
Example: Pre-compiled regex patterns

Update Location: HISTORY.md
Section: ## Performance Optimizations
Add timeline entry with:
- Before/after metrics
- Implementation code snippet
- Impact assessment
```

**Trigger: Technical Debt Resolution**
```markdown
Example: Removed duplicate DMP_TEMPLATES

Update Location: HISTORY.md
Section: ## Technical Debt Resolution
Mark as RESOLVED with:
- Original debt description
- Resolution approach
- Impact on codebase
```

#### `FINAL_TEST_RESULTS.md` Updates

**Trigger: Test Suite Changes**
```markdown
Example: Added 5 new unit tests

Update Location: FINAL_TEST_RESULTS.md
Section: ## Test Suite Results
Update:
- Total test count
- Pass rate percentage
- New test categories
```

**Trigger: Success Rate Change**
```markdown
Example: 94.1% → 95.3%

Update Location: FINAL_TEST_RESULTS.md
Sections to update:
- Executive Summary
- Test Results Overview
- Success Metrics table
- Performance Comparison
```

**Trigger: New Optimization**
```markdown
Example: Reduced extraction time by 20%

Update Location: FINAL_TEST_RESULTS.md
Section: ## Improvements Implemented
Add new subsection with:
- Problem statement
- Solution details
- Performance metrics
- Code reference
```

### Deprecating Old Documentation

#### Step 1: Identify Obsolete Content

**Criteria for deletion:**
- ✅ Information now in HISTORY.md
- ✅ Temporary implementation guide (task complete)
- ✅ Duplicate of information in .claude/CLAUDE.md
- ✅ User guide (not for AI agents)
- ✅ Pull request description (merged)
- ✅ Progress report (outdated)

**Examples:**
```
DELETE:
- IMPLEMENTATION_SUMMARY.md (content moved to HISTORY.md)
- USER_GUIDE_DATA_STEWARD.md (not for AI agents)
- PR_DESCRIPTION.md (PR merged, info in HISTORY.md)
- OPTIMIZATION_SUMMARY.md (consolidated into HISTORY.md)
- .claude/IMPLEMENTATION_PHASE_1.md (task complete)
```

#### Step 2: Merge Content Before Deletion

**Process:**
1. Read file to be deleted
2. Identify unique/valuable information
3. Merge into appropriate existing file:
   - Historical info → HISTORY.md
   - Implementation patterns → .claude/CLAUDE.md
   - Test results → FINAL_TEST_RESULTS.md
4. Create git commit with merge
5. Delete original file
6. Create git commit with deletion

**Example:**
```bash
# 1. Merge OPTIMIZATION_SUMMARY.md → HISTORY.md
#    (Manual: Copy performance metrics to HISTORY.md)

# 2. Commit merge
git add HISTORY.md
git commit -m "docs: Merge optimization details into HISTORY.md"

# 3. Delete old file
rm OPTIMIZATION_SUMMARY.md
git add OPTIMIZATION_SUMMARY.md
git commit -m "docs: Remove OPTIMIZATION_SUMMARY.md (merged into HISTORY.md)"
```

#### Step 3: Update Cross-References

**Check for broken links:**
```bash
# Search for references to deleted file
grep -r "OPTIMIZATION_SUMMARY.md" .

# Update any found references to point to HISTORY.md
```

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Duplicate Information

**Bad:**
```
README.md:
"The DMP structure has 14 sections: 1.1, 1.2, 2.1..."

.claude/CLAUDE.md:
"DMP sections: 1.1 Data description, 1.2 Data collection..."

config/dmp_structure.json:
{ "1. Data description": ["1.1 How will...", "1.2 What data..."] }
```

**Good:**
```
README.md:
"See config/dmp_structure.json for section definitions"

.claude/CLAUDE.md:
"DMP sections defined in config/dmp_structure.json (14 total: 1.1-6.2)"
```

### ❌ Anti-Pattern 2: Outdated Information

**Bad:**
```
Documentation says:
"Success rate: 64.7%"

Actual current rate:
94.1%

Last updated:
2025-11-18
```

**Good:**
```
Documentation says:
"Success rate: 94.1% (as of v0.8.1)"

With history:
"v0.7: 64.7% → v0.8.1: 94.1% (+29.4%)"
```

### ❌ Anti-Pattern 3: User-Facing Content

**Bad (in .claude/CLAUDE.md):**
```markdown
## How to Use DMP-ART

1. Open your web browser
2. Navigate to http://localhost:5000
3. Click the "Upload File" button
4. Select your DMP file from your computer
5. Wait for processing to complete
6. Review the extracted sections
```

**Good (in .claude/CLAUDE.md):**
```markdown
## Upload Workflow (Code References)

1. User uploads file → POST /upload (app.py:199-384)
2. Validation → validate_upload() (app.py:150-197)
3. Processing → DMPExtractor.process_file() (utils/extractor.py:318-420)
4. Cache generation → _create_cache_file() (utils/extractor.py:1450-1550)
5. Redirect → /review/<filename> (app.py:386-450)
```

### ❌ Anti-Pattern 4: Vague Instructions

**Bad:**
```markdown
## Adding a Category

You should create a JSON file in the config folder with the
appropriate structure. Make sure to follow the same format as
existing categories.
```

**Good:**
```markdown
## Adding a Category

1. Create `config/new_category_name.json`:
```json
{
  "1.1": ["Comment for section 1.1", "Another comment"],
  "1.2": ["Comment for section 1.2"]
}
```

2. Restart Flask (categories auto-discovered on startup)
3. Verify in Template Editor → new tab appears
4. Category available in review interface sidebar
```

### ❌ Anti-Pattern 5: Creating Documentation Files for Temporary Tasks

**Bad:**
```
Created files:
- IMPLEMENTATION_PLAN_PHASE_1.md
- IMPLEMENTATION_PLAN_PHASE_1_UPDATED.md
- IMPLEMENTATION_PLAN_PHASE_1_FINAL.md
- IMPLEMENTATION_PROGRESS_PHASE_1.md
- PHASE_1_RESULTS.md
- PHASE_1_ANALYSIS.md
```

**Good:**
```
Single file that gets updated:
- .claude/CLAUDE.md (updated with patterns learned)
- HISTORY.md (updated with completed phase)

Deleted after completion:
- IMPLEMENTATION_PLAN_PHASE_1.md (merged into HISTORY.md)
```

---

## Quality Checklist

Before committing documentation changes, verify:

### Content Quality
- [ ] Information is actionable (not theoretical)
- [ ] Code examples reference actual file locations
- [ ] No duplicate information across files
- [ ] All external links work
- [ ] All internal links work
- [ ] Version numbers updated
- [ ] Dates in ISO 8601 format

### Structure Quality
- [ ] Table of contents present and accurate
- [ ] Sections follow hierarchical order (H1 → H2 → H3)
- [ ] Code blocks have language tags
- [ ] Tables are properly formatted
- [ ] Lists use consistent bullet style

### Technical Accuracy
- [ ] Code examples are syntactically correct
- [ ] File paths match actual structure
- [ ] Line numbers are current
- [ ] Dependencies versions are current
- [ ] Test results reflect latest run

### AI Agent Usability
- [ ] Searchable keywords in headers
- [ ] Unique section anchors
- [ ] Cross-references between documents
- [ ] Pattern examples are complete
- [ ] Troubleshooting includes error messages

---

## Tools and Automation

### Recommended Tools

**Markdown Linting:**
```bash
# Install markdownlint-cli
npm install -g markdownlint-cli

# Lint all markdown files
markdownlint '**/*.md' --ignore node_modules

# Auto-fix where possible
markdownlint '**/*.md' --fix
```

**Link Checking:**
```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check for broken links
markdown-link-check .claude/CLAUDE.md
markdown-link-check HISTORY.md
markdown-link-check FINAL_TEST_RESULTS.md
markdown-link-check README.md
```

**Documentation Statistics:**
```bash
# Count total lines in documentation
wc -l .claude/CLAUDE.md HISTORY.md FINAL_TEST_RESULTS.md README.md

# Count markdown files
find . -name "*.md" | wc -l

# Find large files (>1000 lines)
find . -name "*.md" -exec wc -l {} \; | awk '$1 > 1000'
```

### Git Hooks (Optional)

**Pre-commit hook to validate docs:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check that updated docs have updated dates
if git diff --cached --name-only | grep -q "\.md$"; then
    echo "Markdown files modified. Checking for updated dates..."

    for file in $(git diff --cached --name-only | grep "\.md$"); do
        if ! grep -q "$(date +%Y-%m-%d)" "$file"; then
            echo "Warning: $file may have outdated 'Last Updated' date"
        fi
    done
fi
```

---

## Examples of Excellent Documentation

### Example 1: Code Pattern Documentation

```markdown
## Flask Route Pattern

All routes follow this standardized pattern (app.py:139-146):

```python
@app.route('/endpoint', methods=['GET', 'POST'])
def function_name():
    try:
        # 1. Validate input
        if not request.json:
            return jsonify({'success': False, 'message': 'No data'}), 400

        # 2. Process data
        result = process_data(request.json)

        # 3. Return JSON response
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        app.logger.error(f'Error in function_name: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Key Points:**
- Always return JSON (no HTML from POST routes)
- Use `try/except` for error handling
- Log errors with `app.logger.error()`
- Standard response: `{success: bool, message: str, data: object}`
- HTTP status codes: 200 (OK), 400 (Bad Request), 500 (Server Error)

**Example Routes:**
- `/upload` (app.py:199-384) - File upload and processing
- `/save_feedback` (app.py:452-495) - Save review feedback
- `/api/create-category` (app.py:850-890) - Create feedback category
```

### Example 2: Troubleshooting Documentation

```markdown
## Issue: "No text could be extracted from PDF"

**Symptoms:**
- Error message: "No text could be extracted from the PDF"
- File size > 0, but extraction returns empty content
- Occurs with scanned PDFs or image-based PDFs

**Root Cause:**
PDF contains images of text, not selectable text. PyPDF2 cannot extract from images.

**Solution:**

1. **Check if OCR is installed:**
```bash
tesseract --version
# Expected output: tesseract 5.3.x
```

2. **If not installed, install Tesseract:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-pol tesseract-ocr-eng poppler-utils

# macOS
brew install tesseract tesseract-lang poppler

# Python packages
pip install pytesseract pdf2image Pillow
```

3. **Verify auto-detection works:**
```python
# utils/extractor.py:1650-1675
def _is_scanned_pdf(self, pdf_path):
    """Returns True if PDF has < 50 chars/page"""
    # Automatically triggers OCR fallback
```

4. **Test with known scanned PDF:**
```bash
python test_real_files.py
# Should see: "OCR processing..." for scanned files
```

**Prevention:**
- OCR installed = 100% success on scans
- Without OCR = 0% success on scans
- Recommendation: Install OCR in production

**Related:**
- FINAL_TEST_RESULTS.md:59-88 (OCR implementation details)
- utils/extractor.py:1650-1750 (OCR code)
```

---

## Conclusion

Effective documentation for AI agents:
1. **Is actionable** - Shows how to do things
2. **Is current** - Reflects actual codebase state
3. **Is singular** - One source of truth per concept
4. **Is referenced** - Points to actual code
5. **Is maintained** - Updated with code changes

Follow these guidelines to maintain high-quality documentation that empowers AI agents to understand, modify, and optimize the DMP-ART codebase effectively.

---

**Maintained By:** AI Agents working on DMP-ART
**Referenced From:** `.claude/CLAUDE.md`
**Last Updated:** 2025-11-23
