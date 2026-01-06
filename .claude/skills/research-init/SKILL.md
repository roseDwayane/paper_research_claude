---
name: research-init
description: Initialize a research session with PICO framework and generate search queries
---

# Research Init

## Instructions

1. **Parse the research topic** and extract key components
2. **Build PICO framework:**
   - **P**opulation: Target group (e.g., "older adults aged 60+")
   - **I**ntervention: What's being studied
   - **C**omparison: Control or alternative
   - **O**utcome: Primary outcomes to measure
   - **S**etting: Study context
3. **Generate 5 search queries:**
   - Core intervention + population
   - Mechanism + theoretical basis
   - Outcome measures + population
   - Study designs + field
   - Setting + implementation
4. **Save outputs:**
   - `interactive mode/session_config.json` - PICO and queries
   - `interactive mode/search_queries.md` - Queries with rationale
5. **Suggest next step:** `/deep-search`

## Examples

**User:** `/research-init EEG-based cognitive training for elderly`

**Output:**
```json
{
  "topic": "EEG-based cognitive training for elderly",
  "pico": {
    "population": "Community-dwelling older adults aged 60+",
    "intervention": "EEG neurofeedback cognitive training",
    "comparison": "Standard care or no intervention",
    "outcome": "Cognitive function, attention, memory",
    "setting": "Community or home-based"
  },
  "queries": [
    "EEG neurofeedback cognitive training older adults",
    "brain-computer interface aging cognition mechanism",
    "cognitive assessment elderly intervention outcomes",
    "randomized controlled trial neurofeedback",
    "home-based EEG training feasibility"
  ]
}
```
