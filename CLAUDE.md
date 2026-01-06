# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autonomous Research Agent with Claude as Principal Investigator (PI) and Gemini as execution sub-agent. Claude performs strategic research tasks (search, gap analysis, hypothesis generation) and produces a hand-off payload for Gemini to execute writing tasks.

## Commands

```bash
# Install dependencies
pip install -e .

# Interactive mode (no API key required) - RECOMMENDED
python -m src.interactive "research topic"
python -m src.interactive "topic" --year-from 2020 --papers-per-source 30
python -m src.interactive "topic" -q "additional query 1" "additional query 2"

# Automated mode (requires ANTHROPIC_API_KEY in .env)
python -m src.main "research topic"
```

## Architecture

### Two-Phase System
- **Phase 1 (Claude PI):** Search papers → Analyze relevance → Identify gaps → Generate hypothesis → Create hand-off payload
- **Phase 2 (Gemini):** Receives payload → Writes introduction/literature review (constrained to paper manifest)

### Sub-Agents (in `src/agents/`)
- `orchestrator.py` - Main coordinator that sequences the workflow
- `searcher.py` - Runs OpenAlex/PubMed searches, deduplicates results
- `critic.py` - Scores relevance, identifies research gaps
- `synthesizer.py` - Generates hypothesis, matches journals, assembles payload

### Hand-off Payload Contract
The `HandoffPayload` class in `src/schemas/handoff_payload.py` is the critical interface between Claude and Gemini. Key anti-hallucination safeguards:
- **Paper Manifest Lock:** Gemini can ONLY cite papers in the manifest
- **Evidence Linking:** Every gap must reference evidence paper IDs
- **Checksum Validation:** SHA256 checksum prevents tampering
- `validate_references()` method verifies all gap citations exist in manifest

### Search Tools (in `src/tools/search/`)
- `openalex.py` - Free, no API key required (primary source)
- `pubmed.py` - Free, optional NCBI API key for higher rate limits
- `google_scholar.py` - Requires SerpAPI key (optional)
- `deduplicator.py` - Cross-source deduplication by DOI/title similarity

## Interactive Mode Workflow

When running interactive research sessions:

1. Run `python -m src.interactive "topic"` to search papers
2. Outputs saved to `data/interactive/`:
   - `*_compact.md` - Compact format for Claude Code analysis
   - `*_papers.json` - Full structured data
   - `*_papers.md` - Human-readable format
3. Analyze papers in Claude Code chat (relevance, gaps, hypothesis)
4. Save synthesis outputs to `interactive mode/` folder:
   - `sota_review.md`
   - `hypothesis_specification.md`
   - `handoff_payload.json`
   - `gemini_prompt.md` (copy-paste to Google AI Studio)

## Project-Level Claude Config

This project has its own `.claude/` directory:
- `.claude/skills/` - Custom skills (`/deep-search`, `/handoff-gemini`)
- `.claude/agents/` - Custom agents (`research-critic`)
- `.claude/plans/` - Architecture plans

## License

MIT License
