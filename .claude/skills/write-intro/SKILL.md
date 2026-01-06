# /write-intro

Prepare a complete introduction-writing prompt for Gemini.

## Usage
```
/write-intro
```

## Prerequisites
- Hypothesis generated (run `/generate-hypothesis` first)
- All previous outputs exist in `interactive mode/`

## Workflow

### Step 1: Load All Context
Read:
- `session_config.json`
- `shortlist.json` (paper manifest)
- `sota_review.md`
- `gap_analysis.md`
- `hypothesis_specification.md`
- `journal_recommendations.md`

### Step 2: Build Paper Manifest Table
Create a citation-ready table of all papers:
```markdown
| ID | Authors | Year | Title | Relevance |
|----|---------|------|-------|-----------|
| P1 | Smith et al. | 2023 | ... | 0.95 |
```

### Step 3: Define Writing Structure
Based on target journal, define introduction structure:
```markdown
## Required Structure
1. Opening context (~400 words)
2. Theme 1: [from SOTA] (~500 words)
3. Theme 2: [from SOTA] (~400 words)
4. Theme 3: [from SOTA] (~400 words)
5. Gap synthesis (~400 words)
6. Study rationale and aims (~400 words)
```

### Step 4: Create Anti-Hallucination Constraints
```markdown
## Critical Constraints
1. ONLY cite papers from the Paper Manifest - NO invented citations
2. Use APA7 in-text format: (Author, Year)
3. Address all identified gaps: GAP_001, GAP_002, GAP_003
4. Population focus: [from PICO]
5. Scope: Stay within IN boundaries, avoid OUT areas
```

### Step 5: Assemble Gemini Prompt
Create `interactive mode/gemini_prompt.md`:
```markdown
# Gemini Prompt: Write Introduction Section

Copy everything below this line and paste into Google AI Studio.

---

## TASK
You are a scientific writing assistant. Write the Introduction section...

## PAPER MANIFEST
[Table of all citable papers]

## RESEARCH GAPS
[GAP_001, GAP_002, GAP_003 descriptions]

## HYPOTHESIS & AIMS
[From hypothesis_specification.md]

## REQUIRED STRUCTURE
[Section-by-section outline with word counts]

## CRITICAL CONSTRAINTS
[Anti-hallucination rules]

## BEGIN WRITING
Write the complete Introduction section now.
```

### Step 6: Create Payload JSON
Save to `interactive mode/handoff_payload.json`:
```json
{
  "metadata": {...},
  "paper_manifest": {...},
  "gap_analysis": {...},
  "hypothesis_specification": {...},
  "target_journals": [...],
  "gemini_instructions": {...}
}
```

## Output Files
- `interactive mode/gemini_prompt.md` (copy-paste ready)
- `interactive mode/handoff_payload.json` (structured data)

## Next Step
After completion, display:
```
Introduction prompt ready for Gemini.

To use:
1. Open Google AI Studio (https://aistudio.google.com/)
2. Copy contents of: interactive mode/gemini_prompt.md
3. Paste and submit

After Gemini writes introduction:
  → Verify all citations exist in paper manifest
  → Check APA7 formatting
  → Review for scope alignment

Session status:
  → /session-status    View complete session summary
```
