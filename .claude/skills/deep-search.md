# /deep-search

Run comprehensive literature searches for a research topic using the Research Agent.

## Usage
```
/deep-search [topic]
```

## Workflow

When invoked, execute the following steps:

### Step 1: Generate Search Queries
Based on the topic, generate 5 complementary search queries covering:
1. Core technology/method (e.g., "EEG neurofeedback")
2. Target population (e.g., "older adults rehabilitation")
3. Intervention approach (e.g., "gamification cognitive training")
4. Outcome measures (e.g., "balance fall prevention")
5. Mechanism/theory (e.g., "transfer effects cognitive training")

### Step 2: Execute Searches
For each query, run:
```bash
python -m src.interactive "[query]" --year-from 2015 --papers-per-source 30
```

### Step 3: Organize Results
1. Read all generated `*_compact.md` files from `data/interactive/`
2. Create a subfolder `data/interactive/deep_search_[timestamp]/`
3. Move search results to the subfolder

### Step 4: Report Summary
Output a summary table:
| Search | Query | Papers Found |
|--------|-------|--------------|
| 1 | ... | ... |
| 2 | ... | ... |
| ... | ... | ... |
| **Total** | | **X papers** |

### Step 5: Save to Interactive Mode Folder
Save any synthesis outputs to:
```
Research-agent/interactive mode/
```

## Output
- Search results in `data/interactive/deep_search_[timestamp]/`
- Summary report displayed in chat

## Next Steps
After deep search, suggest running `/handoff-gemini` to prepare the hand-off payload.
