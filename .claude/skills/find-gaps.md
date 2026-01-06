# /find-gaps

Identify research gaps from the SOTA review with evidence linking.

## Usage
```
/find-gaps
```

## Prerequisites
- SOTA review completed (run `/build-sota` first)
- `interactive mode/sota_review.md` exists

## Workflow

### Step 1: Load SOTA Review
Read `sota_review.md` and `knowledge_graph.json`.

### Step 2: Analyze for Gap Types
Systematically search for:

| Gap Type | Description | Example |
|----------|-------------|---------|
| **Topical** | Important subtopics not covered | No studies on home-based BCI |
| **Population** | Groups underrepresented | No community-dwelling 60+ |
| **Methodological** | Missing research designs | No RCTs, only observational |
| **Outcome** | Unmeasured outcomes | Balance not measured |
| **Mechanism** | Unexplored pathways | Transfer effects unknown |
| **Context** | Settings not studied | Real-world feasibility |

### Step 3: Identify 2-3 Critical Gaps
For each gap, document:

```markdown
### GAP_001: [Title]

**Type:** [Topical/Population/Methodological/Outcome/Mechanism/Context]

**Description:**
[Detailed explanation of what's missing]

**Evidence Papers:**
- P1: [How this paper shows the gap exists]
- P5: [How this paper shows the gap exists]
- P12: [How this paper shows the gap exists]

**Why This Matters:**
[Impact on field if gap is addressed]

**Severity:** Critical / Moderate / Minor
**Novelty Potential:** High / Medium / Low
```

### Step 4: Prioritize Gaps
Rank gaps by:
1. **Severity**: How much does this limit the field?
2. **Novelty**: How novel would addressing it be?
3. **Feasibility**: Can it realistically be addressed?

### Step 5: Save Gap Analysis
Save to `interactive mode/gap_analysis.md`:
```markdown
# Research Gap Analysis: [Topic]

## Summary
Identified X gaps from analysis of Y papers across Z themes.

## GAP_001: [Title] (CRITICAL)
...

## GAP_002: [Title] (CRITICAL)
...

## GAP_003: [Title] (MODERATE)
...

## Gap Prioritization Matrix
| Gap | Severity | Novelty | Feasibility | Priority |
|-----|----------|---------|-------------|----------|
| GAP_001 | Critical | High | Medium | 1 |
| GAP_002 | Critical | High | High | 2 |
| GAP_003 | Moderate | Medium | High | 3 |

## Recommendations
[How to address these gaps]
```

## Output Files
- `interactive mode/gap_analysis.md`

## Agent Suggestion
After completion, display:
```
Gap analysis complete: 3 gaps identified (2 critical, 1 moderate).

Suggested agent for validation:
  → gap-detective       For thorough evidence verification
  → research-critic     To confirm gaps aren't addressed by excluded papers

Next step:
  → /generate-hypothesis    Formulate hypothesis addressing the gaps
```
