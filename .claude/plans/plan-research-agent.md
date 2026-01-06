# Autonomous Research Agent - Architecture Design Plan

## Overview

A dual-phase multi-agent system where **Claude** acts as the Principal Investigator (strategic reasoning) and **Gemini** serves as the execution arm (literature synthesis).

**Current Status:** Phase A-F Implementation Complete

**Execution Mode:** Interactive (Claude Max user - no API key)

---

## 1. System Architecture

### 1.1 Two Execution Modes

#### Mode A: Fully Automated (Requires API Key)
```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: CLAUDE (PI Agent)                       │
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  Searcher   │───▶│   Critic    │───▶│ Synthesizer │                 │
│  │  Sub-Agent  │    │  Sub-Agent  │    │  Sub-Agent  │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│         │                  │                  │                         │
│         ▼                  ▼                  ▼                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    SQLite State Store                             │  │
│  │   papers | knowledge_graph | gaps | hypothesis | journals         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Hand-off Payload (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     PHASE 2: GEMINI (via MCP)                           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Tasks: Full-text reading, Citation management, Intro writing    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Mode B: Interactive (No API Key - Current Mode)
```
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 1: AUTOMATED SEARCH                            │
│                                                                         │
│    python -m src.interactive "research topic"                           │
│                                                                         │
│    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐               │
│    │  OpenAlex   │    │   PubMed    │    │  Deduplicator│               │
│    │   Search    │───▶│   Search    │───▶│              │               │
│    └─────────────┘    └─────────────┘    └─────────────┘               │
│                                                 │                       │
│                                                 ▼                       │
│                                    ┌─────────────────────┐             │
│                                    │  *_compact.md       │             │
│                                    │  *_papers.json      │             │
│                                    └─────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Copy/paste to Claude Code
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   STEP 2: INTERACTIVE ANALYSIS                          │
│                         (Claude Code Session)                           │
│                                                                         │
│    User shares papers ───▶ Claude analyzes:                             │
│                            • Relevance scoring                          │
│                            • Gap detection                              │
│                            • Knowledge graph                            │
│                            • Hypothesis generation                      │
│                            • Journal recommendations                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Hand-off Payload (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 3: GEMINI (via MCP)                            │
│                                                                         │
│    Tasks: Literature Review, Introduction Writing                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Implementation Status

### Completed Phases

- [x] **Phase A: Core Infrastructure**
  - [x] Python project structure with `pyproject.toml`
  - [x] Pydantic schemas (`paper.py`, `handoff_payload.py`)
  - [x] SQLite storage layer (`database.py`)
  - [x] Configuration management (`config.py`)

- [x] **Phase B: Search Tools**
  - [x] OpenAlex search tool (free, no API key required)
  - [x] PubMed/NCBI search tool (free, optional API key)
  - [x] Google Scholar search tool (requires SerpAPI key)
  - [x] Paper deduplication utility

- [x] **Phase C: Analysis Tools**
  - [x] Relevance analyzer (LLM-based scoring)
  - [x] Gap detector (identifies research gaps)
  - [x] Knowledge graph builder

- [x] **Phase D: Synthesis Tools**
  - [x] Hypothesis generator
  - [x] Journal matcher
  - [x] Payload assembler (creates hand-off JSON)

- [x] **Phase E: Agent Orchestration**
  - [x] Searcher sub-agent
  - [x] Critic sub-agent
  - [x] Synthesizer sub-agent
  - [x] PI Orchestrator (main coordinator)

- [x] **Phase F: MCP Integration**
  - [x] Gemini launcher tool
  - [x] Prompt builder for Phase 2

- [x] **Phase G: Interactive Mode**
  - [x] `src/interactive.py` for search-only execution
  - [x] Compact markdown export for Claude Code

---

## 3. Project File Structure

```
research-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Full automated entry point (requires API)
│   ├── interactive.py             # Interactive mode entry point (no API)
│   ├── config.py                  # API keys, settings
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Main Claude PI orchestrator
│   │   ├── searcher.py            # Searcher sub-agent
│   │   ├── critic.py              # Critic sub-agent
│   │   └── synthesizer.py         # Synthesizer sub-agent
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                # Base tool class
│   │   ├── search/
│   │   │   ├── __init__.py
│   │   │   ├── openalex.py        # OpenAlex API
│   │   │   ├── pubmed.py          # PubMed/NCBI API
│   │   │   ├── google_scholar.py  # Google Scholar via SerpAPI
│   │   │   └── deduplicator.py    # Cross-source deduplication
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── relevance.py       # LLM-based relevance scoring
│   │   │   ├── gap_detector.py    # Research gap identification
│   │   │   └── knowledge_graph.py # Concept extraction
│   │   ├── synthesis/
│   │   │   ├── __init__.py
│   │   │   ├── hypothesis.py      # Hypothesis generation
│   │   │   ├── journal_matcher.py # Journal recommendations
│   │   │   └── payload_assembler.py # Hand-off payload builder
│   │   └── mcp/
│   │       ├── __init__.py
│   │       └── gemini_launcher.py # Gemini MCP integration
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   └── database.py            # SQLite operations
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── handoff_payload.py     # Hand-off contract schema
│       └── paper.py               # Paper data model
│
├── data/
│   └── interactive/               # Interactive mode outputs
│       ├── {session}_papers.json
│       ├── {session}_papers.md
│       └── {session}_compact.md
│
├── .env.example                   # Environment template
├── pyproject.toml                 # Python project config
├── requirements.txt               # Dependencies
├── TODO.md                        # Development status
└── CLAUDE.md                      # Claude Code instructions
```

---

## 4. How to Use (Interactive Mode)

### Step 1: Install

```bash
cd "C:\Users\PingChen\OneDrive - The University of Liverpool\Desktop\KYC NTHU\Research-agent"
pip install -e .
```

### Step 2: Run Search

```bash
# Basic search
python -m src.interactive "your research topic"

# With filters
python -m src.interactive "AI in healthcare" --year-from 2020 --papers-per-source 30

# Multiple queries
python -m src.interactive "federated learning" -q "federated learning privacy" "distributed ML"
```

### Step 3: Analyze in Claude Code

1. Open generated `*_compact.md` file
2. Share contents in Claude Code chat
3. Ask Claude to analyze:
   - Relevance scoring for each paper
   - Research gap identification
   - Knowledge graph construction
   - Hypothesis generation
   - Target journal recommendations

### Step 4: Generate Hand-off Payload

After interactive analysis, ask Claude to generate the hand-off JSON for Gemini.

---

## 5. Hand-off Payload Schema

The contract between Claude (Phase 1) and Gemini (Phase 2):

```json
{
  "metadata": {
    "research_topic": "string",
    "generated_at": "ISO8601 timestamp",
    "phase1_agent_id": "string",
    "validation_checksum": "sha256"
  },
  "knowledge_graph": {
    "core_concepts": [{"term": "string", "definition": "string", "relationships": []}],
    "field_boundaries": ["string"],
    "methodological_paradigms": ["string"]
  },
  "paper_manifest": {
    "total_papers": 25,
    "papers": [{
      "id": "string",
      "doi": "string",
      "title": "string",
      "authors": ["string"],
      "year": 2024,
      "abstract": "string",
      "relevance_score": 0.95,
      "relevance_rationale": "string",
      "themes": ["string"]
    }]
  },
  "gap_analysis": {
    "identified_gaps": [{
      "gap_id": "GAP_001",
      "title": "string",
      "description": "string",
      "evidence_papers": ["paper_id"],
      "severity": "critical|moderate|minor",
      "novelty_potential": "high|medium|low"
    }]
  },
  "hypothesis_specification": {
    "problem_statement": "string",
    "research_questions": ["RQ1: ..."],
    "hypothesis": "string",
    "expected_significance": {"theoretical": "string", "practical": "string"},
    "scope_boundaries": ["string"]
  },
  "target_journals": [{
    "name": "string",
    "impact_factor": 5.2,
    "review_cycle_days": 60,
    "fit_rationale": "string"
  }],
  "gemini_instructions": {
    "task": "introduction_writing",
    "citation_style": "APA7",
    "constraints": ["Only cite papers from paper_manifest"]
  }
}
```

---

## 6. Anti-Hallucination Safeguards

| Mechanism | Description |
|-----------|-------------|
| **Paper Manifest Lock** | Gemini can ONLY cite papers in the manifest |
| **Rationale Chain** | Every gap links to evidence papers |
| **Checksum Validation** | Payload has SHA256 checksum |
| **Source Attribution** | Every claim must map to a paper_id |
| **Scope Boundaries** | Explicit in/out scope prevents scope creep |

---

## 7. API Keys Reference

| Service | Required? | Purpose |
|---------|-----------|---------|
| Anthropic (Claude) | For automated mode | LLM analysis |
| OpenAlex | No (email recommended) | Paper search |
| PubMed/NCBI | No (optional) | Biomedical papers |
| SerpAPI | Optional | Google Scholar |

---

## 8. Future Enhancements

- [ ] Add unit tests
- [ ] Web UI / Streamlit interface
- [ ] Async batch processing
- [ ] Paper full-text retrieval
- [ ] Citation network analysis
- [ ] Actual MCP server integration for Gemini

---

*Last updated: Interactive mode added for Claude Max users*
