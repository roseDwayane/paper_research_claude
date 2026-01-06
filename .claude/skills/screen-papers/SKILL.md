---
name: screen-papers
description: Score and filter collected papers for relevance and quality
---

# Screen Papers

## Instructions

1. **Load papers** from `data/interactive/*_compact.md`
2. **Define screening criteria** based on PICO:
   - Inclusion: Addresses population, intervention, outcomes
   - Exclusion: Wrong population, reviews only, non-English
3. **Score each paper (1-5):**
   - Relevance to topic (40%)
   - Methodological quality (30%)
   - Evidence strength (20%)
   - Unique contribution (10%)
4. **Apply threshold** (default: score ≥ 3.5)
5. **Save outputs:**
   - `interactive mode/screening_results.md` - All scores and rationale
   - `interactive mode/shortlist.json` - Included papers
6. **Suggest agents:** `research-critic`, `methodology-expert`
7. **Suggest next step:** `/export-references`

## Examples

**User:** `/screen-papers`

**Output:**
```
Screening complete: 14 papers included from 38 screened.

| Category | Count |
|----------|-------|
| Core papers | 8 |
| Review papers | 2 |
| Context papers | 4 |

Top scoring: P1 (5.0), P3 (5.0), P33 (5.0)

Suggested agents:
  → research-critic    Quality assessment
  → methodology-expert Study design critique

Next step: /export-references
```
