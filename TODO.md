# Research Agent - Development Status

## Implementation Complete

All core phases (A-G) are complete. The system supports two execution modes.

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

## How to Use

### Interactive Mode (No API Key - Recommended)

#### Step 1: Install

```bash
cd "C:\Users\PingChen\OneDrive - The University of Liverpool\Desktop\KYC NTHU\Research-agent"
pip install -e .
```

#### Step 2: Run Search (Automated)

```bash
# Basic search
python -m src.interactive "your research topic"

# With filters
python -m src.interactive "AI in healthcare" --year-from 2020 --papers-per-source 30

# Multiple queries
python -m src.interactive "federated learning" -q "federated learning privacy" "distributed ML"
```

#### Step 3: Analyze in Claude Code (Interactive)

1. Open generated `*_compact.md` file in `data/interactive/`
2. Share contents in Claude Code chat
3. Ask Claude to:
   - Score relevance of each paper
   - Identify research gaps
   - Build knowledge graph
   - Generate hypothesis
   - Recommend journals

#### Step 4: Generate Hand-off Payload

Ask Claude to generate the hand-off JSON for Gemini based on the analysis.

### Output Files

After running search:
- `{session}_papers.json` - Full structured data
- `{session}_papers.md` - Human-readable format
- `{session}_compact.md` - Compact version for Claude Code

---

## Automated Mode (Requires API Key)

If you have an Anthropic API key:

```bash
# Set up environment
copy .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Run full automation
python -m src.main "your research topic"
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/interactive.py` | Interactive mode entry point |
| `src/main.py` | Automated mode entry point |
| `src/agents/orchestrator.py` | Main workflow coordinator |
| `src/schemas/handoff_payload.py` | Contract between Claude & Gemini |
| `src/storage/database.py` | SQLite persistence |

---

## API Keys Reference

| Service | Required? | Get it from |
|---------|-----------|-------------|
| Anthropic (Claude) | Automated mode only | https://console.anthropic.com/ |
| OpenAlex | No (email recommended) | Free, no key needed |
| PubMed/NCBI | No (faster with key) | https://www.ncbi.nlm.nih.gov/account/ |
| SerpAPI (Google Scholar) | Optional | https://serpapi.com/ |

---

## Future Enhancements

- [ ] Add unit tests (`tests/` directory)
- [ ] Web UI / Streamlit interface
- [ ] Async batch processing for faster analysis
- [ ] Paper full-text retrieval (for Phase 2)
- [ ] Citation network analysis
- [ ] Actual MCP server integration for Gemini

---

## Related Documents

- **Architecture Plan:** `C:\Users\PingChen\.claude\plans\plan-research-agent.md`
- **Claude Instructions:** `CLAUDE.md`

---

## Current Research Session (2026-01-04)

### Topic
**Cognitive Enhancement and Transfer Effects on Balance in Older Adults: A Feasibility Study of a Gamified EEG-Based BCI**

### Completed Workflow

- [x] **Deep Search** (5 searches, ~270 papers)
  - EEG neurofeedback balance training elderly (35 papers)
  - BCI older adults rehabilitation (59 papers)
  - Gamification cognitive training aging (41 papers)
  - Cognitive motor dual task balance fall prevention (58 papers)
  - Transfer effects cognitive training physical function (56 papers)

- [x] **SOTA Review**
  - 5 thematic synthesis (EEG/BCI, Gamification, Dual-Task, Balance, Transfer)
  - `data/synthesis/sota_review.md`

- [x] **Gap Identification**
  - GAP_001: No gamified EEG-BCI for balance in community-dwelling 60+ (CRITICAL)
  - GAP_002: Transfer from neurofeedback to balance unexplored (CRITICAL)
  - GAP_003: Feasibility of community-based EEG training unestablished (MODERATE)

- [x] **Hypothesis Specification**
  - Population: Community-dwelling older adults aged 60+
  - Intervention: Gamified EEG-BCI cognitive training
  - Outcomes: Cognitive (attention, EF, WM) + Balance/Postural Control
  - Design: Feasibility study
  - `data/synthesis/hypothesis_specification.md`

- [x] **Target Journal**
  - Primary: MDPI Brain Sciences - Special Issue "Non-Invasive Neurotechnologies for Cognitive Augmentation"

- [x] **Hand-off Payload**
  - `data/synthesis/handoff_payload.json` (Gemini-ready)
  - `data/synthesis/handoff_payload_readable.md` (Human-readable)

### Next Steps (Gemini Phase)
- [ ] Execute introduction writing task with Gemini
- [ ] Citation verification against paper manifest
- [ ] Generate reference list in APA7 format

---

*Last updated: 2026-01-04 - Phase 1 (Claude PI) complete for feasibility study*
