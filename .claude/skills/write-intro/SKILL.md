---
name: write-intro
description: Prepare complete introduction-writing prompt for Gemini with anti-hallucination safeguards
---

# Write Intro

## Instructions

1. **Load all context:**
   - `shortlist.json` - Paper manifest
   - `sota_review.md` - Background themes
   - `gap_analysis.md` - Research gaps
   - `hypothesis_specification.md` - Hypothesis and scope
   - `journal_recommendations.md` - Target journal
2. **Build paper manifest table** with citation keys
3. **Define writing structure** (6 sections, ~2500 words):
   - Opening context
   - Deep learning background
   - Transformer emergence
   - Recent advances
   - Critical gap
   - Study rationale and aims
4. **Create anti-hallucination constraints:**
   - ONLY cite papers from manifest
   - Use exact APA 7 format
   - No fabricated statistics
   - Stay within scope boundaries
5. **Save outputs:**
   - `interactive mode/gemini_prompt.md` - Copy-paste ready
   - `interactive mode/handoff_payload.json` - Structured data
6. **Provide usage instructions** for Google AI Studio

## Examples

**User:** `/write-intro`

**Output:**
```
Introduction prompt ready for Gemini.

Paper manifest: 14 citable papers
Structure: 6 sections (~2500 words)
Target: IEEE J-BHI

Files created:
  → gemini_prompt.md (copy-paste ready)
  → handoff_payload.json (structured)

To use:
1. Open https://aistudio.google.com/
2. Copy contents of gemini_prompt.md
3. Paste and submit

After Gemini writes:
  → Verify citations against manifest
  → Check APA 7 formatting
```
