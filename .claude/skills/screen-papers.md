# /screen-papers

Screen and score all collected papers for relevance and quality.

## Usage
```
/screen-papers
```

## Prerequisites
- Search results available in `data/interactive/` (run `/deep-search` first)

## Workflow

### Step 1: Load All Papers
Read all `*_compact.md` files from the most recent search session(s).

### Step 2: Define Screening Criteria
Based on session PICO (from `session_config.json`), define:

**Inclusion Criteria:**
- Directly addresses [Population]
- Studies [Intervention] or closely related
- Reports [Outcome] measures
- Published [Year range]
- Peer-reviewed

**Exclusion Criteria:**
- Wrong population (e.g., clinical vs. community-dwelling)
- Review/commentary only (no original data)
- Non-English full text unavailable
- Duplicate/overlapping samples

### Step 3: Score Each Paper
For each paper, assign:

| Criterion | Score (1-5) |
|-----------|-------------|
| Relevance to PICO | How well does it match? |
| Methodological quality | Study design rigor |
| Evidence strength | Quality of findings |
| Recency | Temporal relevance |
| Unique contribution | Non-redundant value |

**Overall Score** = Weighted average (Relevance 40%, Quality 30%, Evidence 20%, Unique 10%)

### Step 4: Create Screening Results
Save to `interactive mode/screening_results.md`:
```markdown
# Screening Results

## Summary
- Total papers screened: X
- Included: Y
- Excluded: Z

## Included Papers (Score ≥ 3.5)
| ID | Title | Year | Score | Rationale |
|----|-------|------|-------|-----------|
| P1 | ... | 2023 | 4.2 | High relevance, strong RCT |

## Excluded Papers
| ID | Title | Reason |
|----|-------|--------|
| P45 | ... | Wrong population (stroke patients) |
```

### Step 5: Create Shortlist
Save to `interactive mode/shortlist.json`:
```json
{
  "total_screened": 250,
  "included": 35,
  "excluded": 215,
  "threshold": 3.5,
  "papers": [
    {"id": "P1", "title": "...", "score": 4.2, ...}
  ]
}
```

## Output Files
- `interactive mode/screening_results.md`
- `interactive mode/shortlist.json`

## Agent Suggestion
After completion, display:
```
Screening complete: 35 papers included from 250 screened.

Suggested agent for deeper analysis:
  → research-critic    For rigorous quality assessment and bias evaluation
  → methodology-expert For detailed study design critique (RCT, observational)

Next step:
  → /build-sota    Synthesize shortlisted papers into SOTA review
```
