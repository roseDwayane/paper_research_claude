# /handoff-gemini

Prepare a complete hand-off payload for Gemini to write the journal introduction.

## Usage
```
/handoff-gemini [target-journal]
```

## Prerequisites
- Deep search completed (run `/deep-search` first)
- Papers collected in `data/interactive/`

## Workflow

When invoked, execute the following steps:

### Step 1: Read All Search Results
Read all `*_compact.md` files from the most recent deep search session.

### Step 2: Build SOTA Review
Synthesize papers into thematic categories:
1. Identify 4-6 major themes from the papers
2. For each theme, summarize:
   - Current state of knowledge
   - Key findings with paper citations
   - Limitations in the literature
3. Save to `interactive mode/sota_review.md`

### Step 3: Identify Research Gaps
Identify 2-3 research gaps:
- **Gap ID**: GAP_001, GAP_002, GAP_003
- **Title**: Short descriptive title
- **Description**: Detailed explanation
- **Evidence Papers**: Paper IDs that support this gap
- **Severity**: critical/moderate/minor
- **Novelty Potential**: high/medium/low

### Step 4: Generate Hypothesis Specification
Create hypothesis with:
- Problem statement
- Research questions (RQ1, RQ2, RQ3...)
- Primary hypothesis
- Expected significance (theoretical & practical)
- Scope boundaries (IN/OUT criteria)

Save to `interactive mode/hypothesis_specification.md`

### Step 5: Create Paper Manifest
Select 25-35 most relevant papers with:
- Paper ID, DOI, Title, Authors, Year
- Relevance score (0.0-1.0)
- Relevance rationale
- Themes

### Step 6: Assemble Hand-off Payload
Create JSON payload following schema in `src/schemas/handoff_payload.py`:
- metadata
- knowledge_graph
- paper_manifest
- gap_analysis
- hypothesis_specification
- target_journals
- gemini_instructions

Save to `interactive mode/handoff_payload.json`

### Step 7: Generate Gemini Prompt
Create a copy-paste ready prompt for Gemini including:
- Task definition (write introduction)
- Paper manifest table
- Research gaps
- Hypothesis & aims
- Required structure (7 sections)
- Critical constraints (no hallucination)

Save to `interactive mode/gemini_prompt.md`

### Step 8: Create Readable Version
Generate human-readable markdown version of payload.
Save to `interactive mode/handoff_payload_readable.md`

## Output Files
All outputs saved to `Research-agent/interactive mode/`:
```
interactive mode/
├── sota_review.md
├── hypothesis_specification.md
├── handoff_payload.json
├── handoff_payload_readable.md
└── gemini_prompt.md          <-- Copy this to Gemini
```

## Next Steps
1. Review `handoff_payload_readable.md` for accuracy
2. Copy contents of `gemini_prompt.md` to Google AI Studio
3. Submit to Gemini for introduction writing
