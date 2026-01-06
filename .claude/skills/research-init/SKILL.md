# /research-init

Initialize a new research session with structured scope definition.

## Usage
```
/research-init [research topic]
```

## Workflow

### Step 1: Define Research Topic
Parse the research topic and extract key components.

### Step 2: Build PICO/PICOS Framework
Create structured research scope:

| Component | Description |
|-----------|-------------|
| **P**opulation | Target population (e.g., "community-dwelling older adults aged 60+") |
| **I**ntervention | What is being studied (e.g., "gamified EEG-BCI training") |
| **C**omparison | Control or alternative (e.g., "standard care, no intervention") |
| **O**utcome | Primary outcomes (e.g., "cognitive function, balance") |
| **S**etting | Study context (e.g., "community, home-based") |

### Step 3: Generate Search Queries
Based on PICO, generate 5 complementary search queries:
1. **Core intervention**: [Intervention] + [Population]
2. **Mechanism**: [Intervention mechanism] + [theoretical basis]
3. **Outcomes**: [Outcome measures] + [Population]
4. **Methodology**: [Study designs] + [Intervention field]
5. **Context**: [Setting] + [Implementation factors]

### Step 4: Create Session Configuration
Save to `interactive mode/session_config.json`:
```json
{
  "topic": "...",
  "pico": {
    "population": "...",
    "intervention": "...",
    "comparison": "...",
    "outcome": "...",
    "setting": "..."
  },
  "queries": ["...", "...", "...", "...", "..."],
  "created_at": "ISO8601",
  "status": "initialized"
}
```

### Step 5: Save Search Queries
Save to `interactive mode/search_queries.md`:
```markdown
# Search Queries for [Topic]

## Query 1: Core Intervention
**Query:** "..."
**Rationale:** ...

## Query 2: Mechanism
...
```

## Output Files
- `interactive mode/session_config.json`
- `interactive mode/search_queries.md`

## Next Step Suggestion
After completion, display:
```
Session initialized successfully.

Next steps:
  → /deep-search              Run all 5 search queries
  → Edit search_queries.md    Adjust queries before searching

No agent needed for this step.
```
