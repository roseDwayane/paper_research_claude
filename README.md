# Research Agent

Autonomous literature review agent powered by Claude Code skills. Produces a hand-off payload for Gemini to write paper introductions.

## Quick Start

```bash
# In Claude Code, run skills in order:
/research-init          # Define PICO and generate search queries
/deep-search            # Search OpenAlex for papers
/screen-papers          # Score and filter papers
/export-references      # Generate APA 7 citations
/build-sota             # Synthesize thematic review
/find-gaps              # Identify research gaps
/generate-hypothesis    # Formulate hypothesis with IN/OUT scope
/write-intro            # Prepare Gemini prompt
```

## Workflow

```
/research-init → /deep-search → /screen-papers → /export-references
                                      ↓
/write-intro ← /generate-hypothesis ← /find-gaps ← /build-sota
```

## Skills

| Skill | Purpose | Output |
|-------|---------|--------|
| `/research-init` | Define PICO, generate queries | `session_config.json` |
| `/deep-search` | Literature search via OpenAlex | `data/interactive/` |
| `/screen-papers` | Score & filter papers | `shortlist.json` |
| `/export-references` | APA 7 citations | `references_apa.md` |
| `/build-sota` | Thematic synthesis | `sota_review.md` |
| `/find-gaps` | Gap identification | `gap_analysis.md` |
| `/generate-hypothesis` | Hypothesis + scope | `hypothesis_specification.md` |
| `/write-intro` | Gemini prompt | `gemini_prompt.md` |
| `/session-status` | Progress check | *(display only)* |

## Agents

Skills suggest specialized agents at key steps:

| Agent | Purpose |
|-------|---------|
| `research-critic` | Paper quality assessment |
| `methodology-expert` | Study design critique |
| `sota-synthesizer` | Deep literature synthesis |
| `gap-detective` | Gap verification |
| `hypothesis-architect` | Hypothesis refinement |

## Output

After workflow completion:

```
interactive mode/
├── shortlist.json              # Screened papers
├── references_apa.md           # APA citations
├── sota_review.md              # Literature review
├── gap_analysis.md             # Research gaps
├── hypothesis_specification.md # Hypothesis + IN/OUT scope
├── gemini_prompt.md            # Copy-paste for Gemini
└── handoff_payload.json        # Structured payload
```

## Anti-Hallucination

- **Paper Manifest Lock**: Gemini can only cite papers in the manifest
- **Evidence Linking**: Every gap references paper IDs
- **Scope Boundaries**: Clear IN/OUT definitions prevent drift

## License

MIT
