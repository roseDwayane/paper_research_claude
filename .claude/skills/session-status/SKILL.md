# /session-status

Display current research session status and progress.

## Usage
```
/session-status
```

## Workflow

### Step 1: Check Session Files
Scan `interactive mode/` for existing outputs:

| File | Skill | Status |
|------|-------|--------|
| `session_config.json` | /research-init | ? |
| `search_queries.md` | /research-init | ? |
| `screening_results.md` | /screen-papers | ? |
| `shortlist.json` | /screen-papers | ? |
| `sota_review.md` | /build-sota | ? |
| `knowledge_graph.json` | /build-sota | ? |
| `gap_analysis.md` | /find-gaps | ? |
| `hypothesis_specification.md` | /generate-hypothesis | ? |
| `journal_recommendations.md` | /generate-hypothesis | ? |
| `gemini_prompt.md` | /write-intro | ? |
| `handoff_payload.json` | /write-intro | ? |

### Step 2: Check Search Data
Scan `data/interactive/` for search results:
- Number of search sessions
- Total papers collected
- Date of last search

### Step 3: Display Progress Report
```markdown
# Research Session Status

## Topic
[From session_config.json or inferred]

## Progress
| Step | Skill | Status | Output |
|------|-------|--------|--------|
| 1 | /research-init | ✓ Complete | session_config.json |
| 2 | /deep-search | ✓ Complete | 270 papers in 5 searches |
| 3 | /screen-papers | ✓ Complete | 35 papers shortlisted |
| 4 | /build-sota | ✓ Complete | 5 themes synthesized |
| 5 | /find-gaps | ✓ Complete | 3 gaps identified |
| 6 | /generate-hypothesis | ✓ Complete | Hypothesis + 3 journals |
| 7 | /write-intro | ○ Pending | - |

## Current Stage
[Description of where we are]

## Next Recommended Action
→ /write-intro    Prepare introduction prompt for Gemini

## Available Agents
For deeper analysis at any stage:
- research-critic      Paper quality assessment
- methodology-expert   Study design critique
- sota-synthesizer     Enhanced literature synthesis
- gap-detective        Thorough gap verification
- hypothesis-architect Hypothesis refinement
```

### Step 4: Show Key Statistics
```markdown
## Session Statistics
- Papers searched: 270
- Papers shortlisted: 35 (13%)
- Themes identified: 5
- Gaps found: 3 (2 critical)
- Target journal: [Name]
- Session started: [Date]
```

## Output
Display only (no file saved) - shows current status in chat.

## Quick Actions
```
Quick actions:
  /research-init       Start new session
  /deep-search         Run literature search
  /screen-papers       Screen collected papers
  /build-sota          Build SOTA review
  /find-gaps           Identify research gaps
  /generate-hypothesis Generate hypothesis
  /write-intro         Prepare Gemini prompt
```
