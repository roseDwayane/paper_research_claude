# /generate-hypothesis

Generate research hypothesis based on identified gaps.

## Usage
```
/generate-hypothesis [target-journal]
```

## Prerequisites
- Gap analysis completed (run `/find-gaps` first)
- `interactive mode/gap_analysis.md` exists

## Workflow

### Step 1: Load Context
Read:
- `session_config.json` (PICO)
- `gap_analysis.md` (gaps to address)
- `sota_review.md` (background)

### Step 2: Select Primary Gap to Address
Choose the highest-priority gap that:
- Is feasible to address
- Has high novelty potential
- Aligns with user's expertise/resources

### Step 3: Formulate Research Questions
Create 3-4 research questions:
```markdown
**RQ1:** Is [intervention] feasible and acceptable for [population]?
**RQ2:** Does [intervention] improve [primary outcome]?
**RQ3:** Do [primary outcome] gains transfer to [secondary outcome]?
**RQ4:** Does [feature] enhance [mediator] compared to [control]?
```

### Step 4: Define Hypothesis
Primary and secondary hypotheses:
```markdown
**Primary Hypothesis (H1):**
[Clear, testable statement addressing Gap 1]

**Secondary Hypotheses:**
- H2: [Addressing Gap 2]
- H3: [Addressing Gap 3]
```

### Step 5: Define Scope Boundaries
Explicitly state what's IN and OUT:
```markdown
## Scope Boundaries

### IN (Inclusion)
- Population: [specific]
- Intervention: [specific]
- Outcomes: [specific]
- Setting: [specific]
- Study design: [specific]

### OUT (Exclusion)
- Population: [what's excluded and why]
- Intervention: [what's excluded and why]
- Other: [other exclusions]
```

### Step 6: Match Target Journals
Recommend 3-5 journals based on:
- Scope alignment
- Impact factor
- Review timeline
- Open access options

```markdown
## Target Journals

### Primary: [Journal Name]
- Impact Factor: X.X
- Fit Rationale: [Why this journal is ideal]
- Special Issue: [If applicable]

### Alternatives:
1. [Journal 2] - IF: X.X
2. [Journal 3] - IF: X.X
```

### Step 7: Save Outputs
Save to `interactive mode/hypothesis_specification.md`:
```markdown
# Hypothesis Specification: [Topic]

## Research Questions
...

## Hypotheses
...

## Scope Boundaries
...

## Expected Significance
### Theoretical
[Contribution to theory]

### Practical
[Real-world implications]
```

Save to `interactive mode/journal_recommendations.md`

## Output Files
- `interactive mode/hypothesis_specification.md`
- `interactive mode/journal_recommendations.md`

## Agent Suggestion
After completion, display:
```
Hypothesis generated with 4 research questions, IN/OUT scope defined.
Target journal: [Journal Name]

Suggested agent for refinement:
  → hypothesis-architect    For testability review and scope optimization

Next step:
  → /write-intro    Prepare introduction prompt for Gemini
```
