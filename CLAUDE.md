# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autonomous Research Agent with Claude as Principal Investigator (PI) and Gemini as execution sub-agent. Claude performs strategic research tasks (search, gap analysis, hypothesis generation) and produces a hand-off payload for Gemini to execute writing tasks.

## Two Execution Modes

| Mode | Entry Point | API Key | Description |
|------|-------------|---------|-------------|
| **A: Automated** | `python -m src.main "topic"` | Required | Sub-agents run automatically |
| **B: Interactive** | `python -m src.interactive "topic"` | Not required | Step-by-step with skills |

## Commands

```bash
# Install dependencies
pip install -e .

# Interactive mode (no API key required) - RECOMMENDED
python -m src.interactive "research topic"
python -m src.interactive "topic" --year-from 2020 --papers-per-source 30

# Automated mode (requires ANTHROPIC_API_KEY in .env)
python -m src.main "research topic"
```

---

## Mode B: Interactive Workflow (Recommended)

### Skills (9 total)

| Step | Skill | Purpose | Output Files |
|------|-------|---------|--------------|
| 1 | `/research-init` | Initialize session with PICO | `session_config.json`, `search_queries.md` |
| 2 | `/deep-search` | Run 5-query literature search | `data/interactive/search_*/` |
| 3 | `/screen-papers` | Score and filter papers | `screening_results.md`, `shortlist.json` |
| 4 | `/export-references` | Generate APA citations | `references_apa.md`, `citation_keys.md` |
| 5 | `/build-sota` | Synthesize thematic review | `sota_review.md`, `knowledge_graph.json` |
| 6 | `/find-gaps` | Identify research gaps | `gap_analysis.md` |
| 7 | `/generate-hypothesis` | Formulate hypothesis | `hypothesis_specification.md`, `journal_recommendations.md` |
| 8 | `/write-intro` | Prepare Gemini prompt | `gemini_prompt.md`, `handoff_payload.json` |
| 9 | `/session-status` | Show progress | *(display only)* |

### Workflow Diagram

```
/research-init ──→ /deep-search ──→ /screen-papers ──→ /export-references
      │                 │                  │                   │
      ▼                 ▼                  ▼                   ▼
 session_config    ~200 papers        shortlist.json    references_apa.md
 search_queries                       (25-40 papers)    citation_keys.md
                                                              │
                                                              ▼
/build-sota ──→ /find-gaps ──→ /generate-hypothesis ──→ /write-intro
      │              │                  │                    │
      ▼              ▼                  ▼                    ▼
 sota_review    gap_analysis      hypothesis_spec      gemini_prompt.md
 knowledge_graph  (2-3 gaps)      journal_recs        (copy to Gemini)
```

**Skill Chain:**
```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
init → search → screen → references → sota → gaps → hypothesis → write
```

### Agents (5 total)

Skills suggest agents at key steps. User decides whether to invoke.

| Agent | Expertise | Suggested By |
|-------|-----------|--------------|
| `research-critic` | Paper quality & relevance | `/screen-papers` |
| `methodology-expert` | Study design assessment | `/screen-papers` |
| `sota-synthesizer` | Literature synthesis | `/build-sota` |
| `gap-detective` | Gap identification | `/find-gaps` |
| `hypothesis-architect` | Hypothesis design | `/generate-hypothesis` |

**Key:** All agents work WITHIN user's defined PICO scope, not deciding fields independently.

---

## Output File Structure

After complete workflow:

```
Research-agent/
├── interactive mode/
│   ├── session_config.json          # PICO, queries, session status
│   ├── search_queries.md            # 5 queries with rationale
│   ├── screening_results.md         # All papers scored
│   ├── shortlist.json               # Papers passing threshold
│   ├── references_apa.md            # APA 7 reference list
│   ├── citation_keys.md             # P1 → (Author, Year) lookup
│   ├── references.bib               # BibTeX format (optional)
│   ├── sota_review.md               # Thematic synthesis
│   ├── knowledge_graph.json         # Concept relationships
│   ├── gap_analysis.md              # 2-3 gaps with evidence
│   ├── hypothesis_specification.md  # Hypothesis + IN/OUT scope
│   ├── journal_recommendations.md   # Target journals
│   ├── gemini_prompt.md             # Copy-paste for Gemini
│   └── handoff_payload.json         # Structured payload
│
└── data/
    └── interactive/
        └── search_[timestamp]/      # Raw search results
            ├── {uuid}_compact.md
            ├── {uuid}_papers.json
            ├── {uuid}_papers.md
            └── research.db
```

---

## Architecture

### Hand-off Payload Contract
The `HandoffPayload` class in `src/schemas/handoff_payload.py` is the interface between Claude and Gemini.

**Anti-hallucination safeguards:**
- **Paper Manifest Lock:** Gemini can ONLY cite papers in the manifest
- **Evidence Linking:** Every gap must reference evidence paper IDs
- **Checksum Validation:** SHA256 checksum prevents tampering

### Search Tools (in `src/tools/search/`)
- `openalex.py` - Free, no API key required (primary)
- `pubmed.py` - Free, optional NCBI API key
- `google_scholar.py` - Requires SerpAPI key (optional)
- `deduplicator.py` - Cross-source deduplication

### Sub-Agents for Automated Mode (in `src/agents/`)
- `orchestrator.py` - Main coordinator
- `searcher.py` - Search execution
- `critic.py` - Relevance scoring
- `synthesizer.py` - Hypothesis generation

---

## Project-Level Claude Config

```
.claude/
├── skills/           # 9 workflow skills
│   ├── research-init.md
│   ├── deep-search.md
│   ├── screen-papers.md
│   ├── export-references.md
│   ├── build-sota.md
│   ├── find-gaps.md
│   ├── generate-hypothesis.md
│   ├── write-intro.md
│   └── session-status.md
├── agents/           # 5 specialized agents
│   ├── research-critic.md
│   ├── methodology-expert.md
│   ├── sota-synthesizer.md
│   ├── gap-detective.md
│   └── hypothesis-architect.md
└── plans/
    └── plan-research-agent.md
```

## License

MIT License
