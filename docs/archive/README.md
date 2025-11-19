# Documentation Archive

This directory contains historical documentation, analysis files, and planning documents that are no longer actively maintained but preserved for reference.

## Archived on: 2025-11-19

## Why These Were Archived

These documents were created during various development phases and served specific purposes at the time. They have been consolidated into streamlined documentation:

- **Active AI Agent Guide:** `/.claude/CLAUDE.md` - Comprehensive guide for AI agents
- **User Documentation:** `/README.md`, `/INSTALLATION.md`, `/USER_GUIDE_DATA_STEWARD.md`
- **Test Results:** `/FINAL_TEST_RESULTS.md` (kept in root for reference)

## What's in This Archive

### Action Plans (66KB + 54KB + 6.6KB = ~127KB)
- `ACTION_PLAN.md` - Comprehensive 5-phase development roadmap
- `ACTION_PLAN_DATA_STEWARD.md` - Data steward-focused enhancement plan
- `ACTION_PLAN_REFACTORED_OUTLINE.md` - Refactored plan outline

**Status:** Most features from these plans have been implemented or deprioritized. Current priorities are tracked in `.claude/CLAUDE.md` under "Future Roadmap".

### Analysis Files (~200KB)
- `DESIGN_SYSTEM_REVIEW.md` - CSS design system analysis
- `DOCUMENTATION_OPTIMIZATION_ANALYSIS.md` - Documentation structure review
- `FOOTER_ANALYSIS.md` - Footer component analysis
- `HEADER_ANALYSIS.md` - Header component analysis
- `HEADER_STANDARDIZATION_REVIEW.md` - Header standardization review
- `SPACING_VARIABLES_REVIEW.md` - CSS spacing system review
- `PHASE1_HTML_STRUCTURE_ANALYSIS.md` - HTML structure analysis
- `PHASE1_PZD_EXTRACTION_ANALYSIS.md` - PZD extraction analysis
- `REAL_FILES_TEST_ANALYSIS.md` - Real file testing results

**Status:** Analysis completed. Findings integrated into codebase. Design system consolidated in `static/css/style.css`.

### Session Summaries (~66KB)
- `SESSION_SUMMARY_2025-11-17.md` - Development session summary
- `PHASE1_FUNCTION_INVENTORY.md` - Function inventory
- `PHASE1_REVIEW_AND_ADJUSTMENTS.md` - Phase 1 review
- `PHASE4_BILINGUAL_COMPLETE.md` - Bilingual feature completion report
- `PHASE4_BILINGUAL_IMPLEMENTATION_PLAN.md` - Bilingual implementation plan

**Status:** Features completed. Current state documented in `.claude/CLAUDE.md`.

### Test and Optimization Reports (~30KB)
- `OPTIMIZATION_REPORT.md` - Performance optimization details

**Status:** Superseded by `FINAL_TEST_RESULTS.md` in root directory. Optimizations implemented in v0.8.1.

### Other Plans (~37KB)
- `CLAUDE_CODE_PROMO_SETUP.md` - Claude Code setup instructions
- `WEB_CLIENT_EXTRACTION_PLAN.md` - Web client extraction planning

**Status:** Not currently prioritized. May be revisited in future versions.

## If You Need These Files

All files are preserved in version control. You can access them via:

```bash
# View archived file
cat docs/archive/[filename].md

# Restore to root if needed
mv docs/archive/[filename].md .
```

## Current Documentation Structure

**For AI Agents:**
```
.claude/CLAUDE.md          # Primary development guide (15KB, streamlined)
.claude/CLAUDE_OLD.md      # Original comprehensive analysis (80KB, archived)
```

**For Users:**
```
README.md                  # Project overview and quick start
INSTALLATION.md            # Detailed installation instructions
USER_GUIDE_DATA_STEWARD.md # End-user guide for data stewards
FINAL_TEST_RESULTS.md      # Test results and benchmarks
```

**For Development:**
```
test_extractor_optimization.py  # Performance benchmarks
test_real_files.py              # Real file testing
tests/unit/test_extractor.py    # Unit tests
```

## Notes

- All action plan priorities have been evaluated and integrated into current roadmap
- Analysis findings have been applied to codebase where applicable
- Session summaries document completed work
- Test results are now tracked in FINAL_TEST_RESULTS.md

If you're an AI agent working on this codebase, refer to `.claude/CLAUDE.md` for current context, patterns, and guidelines.
