---
name: generate-hypothesis
description: Generate testable research hypothesis with IN/OUT scope from identified gaps
---

# Generate Hypothesis

## Instructions

1. **Load context:**
   - `gap_analysis.md` - Gaps to address
   - `sota_review.md` - Background
   - `session_config.json` - PICO (if exists)
2. **Select primary gap** with highest priority and feasibility
3. **Formulate research questions (3-4):**
   - RQ1: Feasibility question
   - RQ2: Primary outcome question
   - RQ3: Transfer/secondary outcome question
   - RQ4: Mechanism question
4. **Define hypothesis:**
   - Primary (H1): Clear, testable statement
   - Secondary (H2, H3): Supporting hypotheses
5. **Define scope boundaries:**
   - IN: Population, intervention, outcomes, setting, design
   - OUT: Exclusions with rationale
6. **Recommend 3-5 target journals** with impact factors
7. **Save outputs:**
   - `interactive mode/hypothesis_specification.md`
   - `interactive mode/journal_recommendations.md`
8. **Suggest agent:** `hypothesis-architect`
9. **Suggest next step:** `/write-intro`

## Examples

**User:** `/generate-hypothesis`

**Output:**
```
Hypothesis generated: 4 RQs, IN/OUT scope defined

Primary Hypothesis (H1):
"A lightweight transformer with Flash Attention can achieve
real-time EEG denoising (<10ms latency) while maintaining
CC >0.95, enabling BCI deployment."

Scope:
  IN: Scalp EEG, EOG/EMG/ECG artifacts, EEGdenoiseNet
  OUT: iEEG, MEG, clinical trials

Target Journal: IEEE J-BHI (IF: 7.7)

Suggested agent: hypothesis-architect
Next step: /write-intro
```
