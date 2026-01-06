---
name: deep-search
description: Run comprehensive literature search using multiple queries and sources
---

# Deep Search

## Instructions

1. **Get search queries** from `session_config.json` or generate from topic
2. **Execute searches** using OpenAlex and PubMed APIs:
   - Run each query with year filters (default: 2015+)
   - Collect ~30 papers per source per query
3. **Deduplicate results** by DOI and title similarity
4. **Save outputs to `data/interactive/`:**
   - `{session_id}_papers.json` - Full data
   - `{session_id}_papers.md` - Readable format
   - `{session_id}_compact.md` - Compact for analysis
5. **Report summary** with paper counts per query
6. **Suggest next step:** `/screen-papers`

## Examples

**User:** `/deep-search transformer EEG denoising`

**Output:**
```
Search complete!

| # | Query | Papers | Unique |
|---|-------|--------|--------|
| 1 | transformer EEG denoising | 30 | 30 |
| 2 | attention mechanism biosignal | 28 | 24 |
| 3 | deep learning artifact removal | 35 | 22 |
|---|-------|--------|--------|
| Total | | 93 | 76 |

Files saved to: data/interactive/{session_id}/
Next step: /screen-papers
```
