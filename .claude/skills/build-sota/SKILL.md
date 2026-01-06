# /build-sota

Build a State-of-the-Art (SOTA) review from shortlisted papers.

## Usage
```
/build-sota
```

## Prerequisites
- Screening completed (run `/screen-papers` first)
- `interactive mode/shortlist.json` exists

## Workflow

### Step 1: Load Shortlisted Papers
Read papers from `shortlist.json` and their full details from search results.

### Step 2: Identify Themes
Analyze papers to identify 4-6 major themes, e.g.:
- Theme 1: [Core technology/method]
- Theme 2: [Application domain]
- Theme 3: [Population-specific findings]
- Theme 4: [Outcome measures]
- Theme 5: [Mechanisms/theory]

### Step 3: Synthesize Each Theme
For each theme, write:

```markdown
## Theme X: [Theme Title]

### Current State of Knowledge
[Summary of what is known, citing papers]

### Key Findings
1. Finding 1 (Paper IDs: P1, P5, P12)
2. Finding 2 (Paper IDs: P3, P8)
...

### Methodological Approaches
- Common designs used
- Sample characteristics
- Outcome measures

### Limitations in Current Literature
- What's missing or weak in this theme
```

### Step 4: Identify Cross-Theme Patterns
Analyze:
- **Convergent findings**: What do multiple themes agree on?
- **Divergent findings**: Where do studies conflict?
- **Methodological patterns**: Common strengths/weaknesses

### Step 5: Build Knowledge Graph
Create `interactive mode/knowledge_graph.json`:
```json
{
  "concepts": [
    {"term": "EEG neurofeedback", "definition": "...", "related": ["BCI", "cognitive training"]}
  ],
  "relationships": [
    {"from": "neurofeedback", "to": "attention", "type": "improves", "evidence": ["P1", "P5"]}
  ],
  "themes": ["Theme 1", "Theme 2", ...]
}
```

### Step 6: Save SOTA Review
Save to `interactive mode/sota_review.md`:
```markdown
# State-of-the-Art Review: [Topic]

## Executive Summary
[2-3 paragraph overview]

## Theme 1: ...
...

## Theme N: ...
...

## Cross-Theme Synthesis
### Convergent Findings
### Divergent Findings
### Methodological Patterns

## Conclusion
[Summary of current state, setting up gaps]
```

## Output Files
- `interactive mode/sota_review.md`
- `interactive mode/knowledge_graph.json`

## Agent Suggestion
After completion, display:
```
SOTA review complete: 5 themes synthesized from 35 papers.

Suggested agent for enhanced synthesis:
  → sota-synthesizer    For deeper thematic analysis and cross-study comparison

Next step:
  → /find-gaps    Identify research gaps from the SOTA review
```
