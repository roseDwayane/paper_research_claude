---
name: session-status
description: Display current research session progress and recommend next actions
---

# Session Status

## Instructions

1. **Scan `interactive mode/`** for existing outputs:
   - session_config.json → /research-init
   - screening_results.md, shortlist.json → /screen-papers
   - references_apa.md → /export-references
   - sota_review.md → /build-sota
   - gap_analysis.md → /find-gaps
   - hypothesis_specification.md → /generate-hypothesis
   - gemini_prompt.md → /write-intro
2. **Check `data/interactive/`** for search results
3. **Display progress table** with completion status
4. **Show key statistics:**
   - Papers searched/shortlisted
   - Themes identified
   - Gaps found
   - Target journal
5. **Recommend next action** based on current stage
6. **List available agents** for deeper analysis

## Examples

**User:** `/session-status`

**Output:**
```
# Research Session Status

Topic: EEG noise removal transformer

| Step | Skill | Status |
|------|-------|--------|
| 1 | /research-init | ⊘ Skipped |
| 2 | /deep-search | ✓ Complete |
| 3 | /screen-papers | ✓ Complete |
| 4 | /export-references | ✓ Complete |
| 5 | /build-sota | ✓ Complete |
| 6 | /find-gaps | ✓ Complete |
| 7 | /generate-hypothesis | ✓ Complete |
| 8 | /write-intro | ✓ Complete |

Statistics:
  Papers: 38 searched → 14 shortlisted
  Themes: 5 | Gaps: 3 (2 critical)
  Target: IEEE J-BHI

Workflow: 100% COMPLETE
```
