# /deep-search

Run comprehensive literature searches for a research topic.

## Usage
```
/deep-search [topic]
/deep-search                  # Uses queries from session_config.json
```

## Workflow

### Step 1: Get Search Queries
**Option A:** If `interactive mode/session_config.json` exists, use queries from there.
**Option B:** If topic provided, generate 5 complementary queries:
1. Core technology/method (e.g., "EEG neurofeedback cognitive training")
2. Target population (e.g., "older adults rehabilitation BCI")
3. Intervention approach (e.g., "gamification cognitive training aging")
4. Outcome measures (e.g., "balance fall prevention dual-task")
5. Mechanism/theory (e.g., "transfer effects cognitive training physical function")

### Step 2: Execute Searches
For each query, run:
```bash
python -m src.interactive "[query]" --year-from 2015 --papers-per-source 30
```

Wait for each search to complete before starting the next.

### Step 3: Organize Results
1. Create timestamped folder: `data/interactive/search_[YYYYMMDD_HHMMSS]/`
2. Move all new search outputs to this folder
3. Read all `*_compact.md` files

### Step 4: Deduplicate Across Searches
Identify duplicate papers across searches (by DOI or title similarity).
Note duplicates but keep all versions for reference.

### Step 5: Report Summary
Display summary table:
```
| # | Query | Papers | Unique |
|---|-------|--------|--------|
| 1 | EEG neurofeedback... | 35 | 35 |
| 2 | BCI older adults... | 42 | 38 |
| 3 | Gamification... | 28 | 22 |
| 4 | Balance fall... | 45 | 31 |
| 5 | Transfer effects... | 38 | 25 |
|---|-------|--------|--------|
| **Total** | | **188** | **151** |
```

### Step 6: Update Session Status
If `session_config.json` exists, update:
```json
{
  "status": "search_complete",
  "search_stats": {
    "total_papers": 188,
    "unique_papers": 151,
    "search_date": "..."
  }
}
```

## Output
- Search results in `data/interactive/search_[timestamp]/`
- Summary displayed in chat
- Updated `session_config.json` (if exists)

## Next Step Suggestion
After completion, display:
```
Deep search complete: 151 unique papers from 5 searches.

Next steps:
  → /screen-papers    Screen and score papers for relevance

Suggested agent (optional):
  → research-critic   For preliminary quality check before full screening
```
