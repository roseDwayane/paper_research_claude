---
name: build-sota
description: Synthesize shortlisted papers into a thematic state-of-the-art review
---

# Build SOTA

## Instructions

1. **Load papers** from `shortlist.json` and search results
2. **Identify 4-6 themes** by analyzing paper topics and methods
3. **Synthesize each theme:**
   - Current state of knowledge
   - Key findings with paper IDs
   - Methodological approaches
   - Limitations
4. **Analyze cross-theme patterns:**
   - Convergent findings
   - Divergent findings
   - Methodological patterns
5. **Build knowledge graph** of concepts and relationships
6. **Save outputs:**
   - `interactive mode/sota_review.md` - Full thematic review
   - `interactive mode/knowledge_graph.json` - Concept relationships
7. **Suggest agent:** `sota-synthesizer`
8. **Suggest next step:** `/find-gaps`

## Examples

**User:** `/build-sota`

**Output:**
```
SOTA review complete: 5 themes from 14 papers.

Themes identified:
1. Pure Transformer Architectures (P1, P4, P31)
2. CNN-Transformer Hybrids (P3, P32, P34, P35)
3. GAN-Guided Denoising (P32, P35)
4. Attention Mechanisms (P33, P10)
5. Clinical Applications (P4, P8, P9, P18, P20)

Cross-theme: All agree transformers outperform CNNs/RNNs

Suggested agent: sota-synthesizer
Next step: /find-gaps
```
