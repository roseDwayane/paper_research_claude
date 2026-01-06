# /export-references

Export screened papers as a formatted reference list in APA 7th edition.

## Usage
```
/export-references
/export-references --format apa7    # Default
/export-references --format bibtex  # BibTeX format
```

## Prerequisites
- Screening completed (run `/screen-papers` first)
- `interactive mode/shortlist.json` exists

## Workflow

### Step 1: Load Shortlisted Papers
Read papers from `shortlist.json` and full details from search results.

### Step 2: Extract Citation Information
For each paper, extract:
- Authors (all authors, formatted correctly)
- Year of publication
- Title
- Journal/Source name
- Volume, Issue, Pages (if available)
- DOI

### Step 3: Format in APA 7th Edition
Apply APA 7 formatting rules:

**Journal Article:**
```
Author, A. A., Author, B. B., & Author, C. C. (Year). Title of article. Title of Periodical, volume(issue), page–page. https://doi.org/xxxxx
```

**For 1-2 authors:** List all
**For 3-20 authors:** List all
**For 21+ authors:** List first 19, then ... then last author

**Examples:**
```
Marzbani, H., Marateb, H. R., & Mansourian, M. (2016). Methodological note: Neurofeedback: A comprehensive review on system design, methodology and clinical applications. Basic and Clinical Neuroscience, 7(2), 143–158. https://doi.org/10.15412/J.BCN.03070208

Gruzelier, J. H. (2014). EEG-neurofeedback for optimising performance. I: A review of cognitive and affective outcome in healthy participants. Neuroscience & Biobehavioral Reviews, 44, 124–141. https://doi.org/10.1016/j.neubiorev.2013.09.015
```

### Step 4: Organize References
Sort alphabetically by first author's last name.

Group by theme if requested:
```markdown
## References

### Theme 1: EEG Neurofeedback
[References for theme 1]

### Theme 2: Gamification
[References for theme 2]
```

### Step 5: Generate Reference List
Save to `interactive mode/references_apa.md`:
```markdown
# References (APA 7th Edition)

Total: X papers from screening

## Full Reference List

Author, A. A. (Year). Title...

Author, B. B. (Year). Title...

[Alphabetically sorted]
```

### Step 6: Generate BibTeX (Optional)
If `--format bibtex`, also save to `interactive mode/references.bib`:
```bibtex
@article{marzbani2016,
  author = {Marzbani, Hengameh and Marateb, Hamid Reza and Mansourian, Marjan},
  title = {Methodological Note: Neurofeedback: A Comprehensive Review on System Design, Methodology and Clinical Applications},
  journal = {Basic and Clinical Neuroscience},
  year = {2016},
  volume = {7},
  number = {2},
  pages = {143--158},
  doi = {10.15412/J.BCN.03070208}
}
```

### Step 7: Create Citation Keys
Generate quick-reference table:
```markdown
## Citation Keys (for in-text citations)

| Key | In-Text Citation | Full Reference |
|-----|------------------|----------------|
| P1 | (Marzbani et al., 2016) | Marzbani, H., Marateb, H. R... |
| P2 | (Gruzelier, 2014) | Gruzelier, J. H. (2014)... |
```

## Output Files
- `interactive mode/references_apa.md` - Full APA reference list
- `interactive mode/references.bib` - BibTeX format (if requested)
- `interactive mode/citation_keys.md` - Quick reference table

## APA 7 Formatting Rules Applied

1. **Author names:** Last name, Initials.
2. **Ampersand:** Use & before last author
3. **Year:** In parentheses after authors
4. **Title:** Sentence case (only first word and proper nouns capitalized)
5. **Journal:** Title case, italicized
6. **Volume:** Italicized
7. **Issue:** In parentheses, not italicized
8. **DOI:** As URL format https://doi.org/...

## Handling Missing Information

| Missing | Action |
|---------|--------|
| DOI | Omit DOI line |
| Pages | Omit pages |
| Issue | Omit issue number |
| Volume | Use "Article XXX" if available |
| Full author names | Use available initials |

## Next Step Suggestion
After completion, display:
```
References exported: 35 papers in APA 7th edition.

Files created:
  → interactive mode/references_apa.md
  → interactive mode/citation_keys.md

Use citation_keys.md for quick in-text citation lookup.
These references can be provided to Gemini via /write-intro.
```
