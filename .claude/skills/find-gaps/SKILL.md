---
name: find-gaps
description: Identify research gaps from SOTA review with evidence linking
---

# Find Gaps

## Instructions

1. **Load** `sota_review.md` and `knowledge_graph.json`
2. **Analyze for gap types:**
   - Topical: Subtopics not covered
   - Population: Groups underrepresented
   - Methodological: Missing study designs
   - Outcome: Unmeasured outcomes
   - Mechanism: Unexplored pathways
   - Context: Settings not studied
3. **Document 2-3 critical gaps** with:
   - Description
   - Evidence papers showing gap exists
   - Why it matters
   - Severity and novelty potential
4. **Prioritize gaps** by severity, novelty, feasibility
5. **Save output:** `interactive mode/gap_analysis.md`
6. **Suggest agents:** `gap-detective`, `research-critic`
7. **Suggest next step:** `/generate-hypothesis`

## Examples

**User:** `/find-gaps`

**Output:**
```
Gap analysis complete: 3 gaps (2 critical, 1 moderate)

GAP_001: Real-Time Lightweight Architectures (CRITICAL)
  - 0/8 papers report inference latency
  - Evidence: P1, P3, P10, P32, P34

GAP_002: Clinical Validation (CRITICAL)
  - All use semi-simulated datasets
  - Evidence: P1, P3, P31, P32, P33, P34

GAP_003: Cross-Dataset Generalization (MODERATE)
  - No domain adaptation studies
  - Evidence: P3, P32, P34

Suggested agents: gap-detective, research-critic
Next step: /generate-hypothesis
```
