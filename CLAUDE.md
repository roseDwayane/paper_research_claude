# CLAUDE.md

Research Agent powered by Claude Code skills. Produces hand-off payload for Gemini to execute writing tasks.

## Skills (9 total)

| Step | Skill | Purpose | Output |
|------|-------|---------|--------|
| 1 | `/research-init` | Initialize PICO | `session_config.json` |
| 2 | `/deep-search` | Literature search | `data/interactive/` |
| 3 | `/screen-papers` | Score & filter | `shortlist.json` |
| 4 | `/export-references` | APA citations | `references_apa.md` |
| 5 | `/build-sota` | Thematic review | `sota_review.md` |
| 6 | `/find-gaps` | Research gaps | `gap_analysis.md` |
| 7 | `/generate-hypothesis` | Hypothesis | `hypothesis_specification.md` |
| 8 | `/write-intro` | Gemini prompt | `gemini_prompt.md` |
| 9 | `/session-status` | Progress | *(display)* |

**Chain:** `init → search → screen → references → sota → gaps → hypothesis → write`

## Agents (5 total)

| Agent | Expertise | Used By |
|-------|-----------|---------|
| `research-critic` | Paper quality | `/screen-papers` |
| `methodology-expert` | Study design | `/screen-papers` |
| `sota-synthesizer` | Literature synthesis | `/build-sota` |
| `gap-detective` | Gap verification | `/find-gaps` |
| `hypothesis-architect` | Hypothesis design | `/generate-hypothesis` |

## Output Structure

```
interactive mode/
├── shortlist.json, screening_results.md
├── references_apa.md, citation_keys.md
├── sota_review.md, knowledge_graph.json
├── gap_analysis.md
├── hypothesis_specification.md, journal_recommendations.md
└── gemini_prompt.md, handoff_payload.json
```

## License

MIT License
