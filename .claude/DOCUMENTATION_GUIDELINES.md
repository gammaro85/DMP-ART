# Documentation Guidelines for DMP-ART

**Version:** 2.0
**Last Updated:** 2026-03-11

---

## Core Principles

1. **AI agents, not humans** — docs are for code assistants, not end users
2. **Single Source of Truth** — each fact lives in exactly one file
3. **Modify, don't create** — update existing files; never create new `*_PLAN.md`, `*_REPORT.md`, `*_SUMMARY.md`
4. **Code references over prose** — link to actual file:line locations
5. **Actionable** — every section answers "what should an AI agent do here?"

---

## File Ownership

| File | Owns | Update when |
|------|------|------------|
| `.claude/CLAUDE.md` | Patterns, conventions, architecture, API routes, CSS vars, ADRs | Any new pattern, route, breaking change, or architectural decision |
| `HISTORY.md` | Version changelog, all past changes | Every version bump or significant fix |
| `README.md` | GitHub-facing overview, badges | Version number changes, major feature additions |
| `BUILD.md` | Build/deployment instructions, standalone user guide | Build process changes |
| `SECURITY.md` | Security considerations | Security-relevant changes |
| `.github/copilot-instructions.md` | Quick onboarding for AI agents | Major structural changes |
| `.claude/DOCUMENTATION_GUIDELINES.md` | This file — documentation standards | Standards changes |

**Never create additional `.md` files** in the project root for plans, analyses, or reports.
Temporary notes → Claude memory files in `.claude/projects/*/memory/`.

---

## Documentation Update Protocol

### When finishing a task, update docs as follows:

**If you changed a code pattern, added a route, or changed CSS vars:**
→ Update `.claude/CLAUDE.md` in the relevant section

**If you fixed a bug or shipped a feature:**
→ Add entry to `HISTORY.md` under the current version heading (see format below)

**If the version number changed:**
→ Update version badge in `README.md` and header of `CLAUDE.md`

**If you changed build/deployment:**
→ Update `BUILD.md`

### Standard HISTORY.md entry format

```markdown
### v{X.Y.Z} ({YYYY-MM-DD}) — {Short Title}

**Status:** Production-ready | In progress | Experimental
**Focus:** One-line description of the release focus

#### Changes
- **File/component:** What changed and why
- Bug: **Root Cause** + **Fix** (file:line if helpful)
- New route: `METHOD /path` — description
```

### Standard CLAUDE.md "Recent Changes" entry format

```markdown
### {YYYY-MM-DD} Update (v{X.Y.Z}) — {Title}

**Fixes:**
- ✅ Short description — root cause if non-obvious

**New features/patterns:**
- ✅ Description — file or route reference
```

---

## Anti-Patterns

| ❌ Don't do this | ✅ Do this instead |
|-----------------|-------------------|
| Create `FEATURE_X_PLAN.md` | Add to `HISTORY.md` roadmap or CLAUDE.md ADRs |
| Create `ANALYSIS_REPORT.md` | Add findings to relevant section in `CLAUDE.md` |
| Create `OPTIMIZATION_NOTES.md` | Update `CLAUDE.md` Performance Optimizations section |
| Duplicate info across files | Pick the owning file, reference from others |
| Leave outdated version numbers | Update badges in `README.md` on every release |
| Write docs without code examples | Always include file:line references |

---

## Quality Checklist

Before completing any documentation update:

- [ ] Version numbers consistent across `README.md`, `CLAUDE.md`, `HISTORY.md`
- [ ] No duplicate information (same fact in two places)
- [ ] Code examples reference real files/lines
- [ ] "Last Updated" fields updated
- [ ] No new standalone `.md` files created in project root
- [ ] `CLAUDE.md` "Recent Changes" section reflects actual changes made
