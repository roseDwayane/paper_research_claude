---
name: export-references
description: Generate APA 7th edition reference list from shortlisted papers
---

# Export References

## Instructions

1. **Load papers** from `shortlist.json` and search results
2. **Extract citation info:** authors, year, title, journal, DOI
3. **Format in APA 7:**
   - Author, A. A., & Author, B. B. (Year). Title. *Journal*, *vol*(issue), pages. https://doi.org/...
4. **Sort alphabetically** by first author
5. **Generate citation keys table:** P1 → (Author et al., Year)
6. **Save outputs:**
   - `interactive mode/references_apa.md` - Full reference list
   - `interactive mode/citation_keys.md` - Quick lookup table
7. **Suggest next step:** `/build-sota`

## Examples

**User:** `/export-references`

**Output:**
```markdown
# References (APA 7th Edition)
Total: 14 papers

Chuang, C.-H., Chang, K.-Y., Huang, C.-S., & Bessas, A.-M. (2024).
ART: Artifact removal transformer... *arXiv*. https://doi.org/...

Pu, X., Yi, P., Chen, K., Ma, Z., Zhao, D., & Ren, Y. (2022).
EEGDnet: Fusing non-local and local self-similarity...
*Computers in Biology and Medicine*, *151*, 106248.

## Citation Keys
| Key | Citation |
|-----|----------|
| P1 | (Chuang et al., 2024) |
| P33 | (Pu et al., 2022) |
```
