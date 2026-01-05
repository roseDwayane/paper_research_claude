"""
Analyze and present the EEG-Eye Tracking literature search results
"""

import json
import sys
from collections import defaultdict


def format_authors(authors, max_display=3):
    """Format author list"""
    if not authors:
        return "N/A"
    if len(authors) <= max_display:
        return ", ".join(authors)
    return ", ".join(authors[:max_display]) + ", et al."


def analyze_results(json_path):
    """Load and analyze search results"""

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data['papers']
    total = data['total_unique_papers']

    print("="*100)
    print("EEG + EYE-TRACKING + MULTIMODAL LEARNING: COMPREHENSIVE LITERATURE SEARCH RESULTS")
    print("="*100)
    print(f"\nTotal Unique Papers Found: {total}")
    print(f"Date Range: 2020-2025")
    print(f"Search Date: 2025-12-30")
    print("\n")

    # Year distribution
    print("="*100)
    print("YEAR DISTRIBUTION")
    print("="*100)
    years = defaultdict(int)
    for paper in papers:
        year = paper.get('year', 'Unknown')
        if year not in ['Unknown', 'N/A', '']:
            years[year] += 1

    for year in sorted(years.keys(), reverse=True):
        bar = '#' * (years[year] // 2)
        print(f"  {year}: {years[year]:3d} papers {bar}")

    # Top venues
    print(f"\n{'='*100}")
    print("TOP 20 VENUES/CONFERENCES/JOURNALS")
    print("="*100)
    venues = defaultdict(int)
    for paper in papers:
        venue = paper.get('venue', 'Unknown')
        if venue and venue not in ['Unknown', 'N/A', '']:
            venues[venue] += 1

    for i, (venue, count) in enumerate(sorted(venues.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        print(f"{i:2d}. [{count:2d} papers] {venue}")

    # Source distribution
    print(f"\n{'='*100}")
    print("SOURCE DATABASE DISTRIBUTION")
    print("="*100)
    sources = defaultdict(int)
    for paper in papers:
        source = paper.get('source', 'Unknown')
        sources[source] += 1

    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        print(f"  {source:20s}: {count:3d} papers ({pct:.1f}%)")

    # Top papers by citation (if available)
    print(f"\n{'='*100}")
    print("TOP 15 MOST RECENT PAPERS (2024-2025)")
    print("="*100)

    recent_papers = [p for p in papers if p.get('year') in ['2024', '2025']]
    recent_papers.sort(key=lambda x: x.get('published_date', '0000-00-00'), reverse=True)

    for i, paper in enumerate(recent_papers[:15], 1):
        print(f"\n{i}. {paper.get('title', 'N/A')}")
        print(f"   Authors: {format_authors(paper.get('authors', []))}")
        print(f"   Year: {paper.get('year', 'N/A')} | Venue: {paper.get('venue', 'N/A')}")
        print(f"   Source: {paper.get('source', 'N/A')}")
        if paper.get('url'):
            print(f"   URL: {paper.get('url')}")
        if paper.get('doi'):
            print(f"   DOI: {paper.get('doi')}")

        # Show abstract snippet
        abstract = paper.get('abstract', '')
        if abstract:
            snippet = abstract[:250].replace('\n', ' ')
            print(f"   Abstract: {snippet}...")

    # Key topics analysis (simple keyword extraction)
    print(f"\n{'='*100}")
    print("KEY RESEARCH THEMES (Based on Title Analysis)")
    print("="*100)

    # Count key terms in titles
    key_terms = {
        'deep learning': 0,
        'neural network': 0,
        'machine learning': 0,
        'attention': 0,
        'cognitive load': 0,
        'emotion': 0,
        'brain-computer interface': 0,
        'BCI': 0,
        'fusion': 0,
        'multimodal': 0,
        'CNN': 0,
        'LSTM': 0,
        'transformer': 0,
        'classification': 0,
        'recognition': 0,
        'detection': 0,
    }

    for paper in papers:
        title_abstract = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        for term in key_terms:
            if term.lower() in title_abstract:
                key_terms[term] += 1

    for term, count in sorted(key_terms.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {term:30s}: {count:3d} papers")

    # Export subset for detailed review
    print(f"\n{'='*100}")
    print("RECOMMENDED PAPERS FOR PHASE 2 DEEP READING")
    print("="*100)
    print("\nCriteria: Recent (2023-2025) + High relevance to multimodal EEG-eye tracking fusion")
    print()

    # Filter for most relevant papers
    keywords_high_relevance = ['multimodal', 'fusion', 'eeg', 'eye', 'gaze', 'tracking']

    relevant_papers = []
    for paper in papers:
        title_abstract = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        year = paper.get('year', '')

        # Count keyword matches
        score = sum(1 for kw in keywords_high_relevance if kw in title_abstract)

        # Prioritize recent papers
        if year in ['2023', '2024', '2025'] and score >= 3:
            relevant_papers.append((score, paper))

    relevant_papers.sort(key=lambda x: (x[0], x[1].get('published_date', '')), reverse=True)

    print(f"Found {len(relevant_papers)} highly relevant papers for deep reading:\n")

    for i, (score, paper) in enumerate(relevant_papers[:20], 1):
        print(f"{i:2d}. [{score} keywords] {paper.get('title', 'N/A')}")
        print(f"    {format_authors(paper.get('authors', []))} ({paper.get('year', 'N/A')})")
        print(f"    {paper.get('venue', 'N/A')}")
        if paper.get('url'):
            print(f"    {paper.get('url')}")
        print()

    return data


if __name__ == "__main__":
    json_file = "results/eeg_eyetracking_search_20251230_172435.json"
    results = analyze_results(json_file)

    print("="*100)
    print("NEXT STEPS (Following CLAUDE.md Workflow)")
    print("="*100)
    print()
    print("PHASE 1: Literature Discovery - COMPLETED")
    print(f"  - Found {results['total_unique_papers']} unique papers across 5 search queries")
    print("  - Filtered for 2020-2025 (last 5 years)")
    print("  - Identified top venues and recent trends")
    print()
    print("PHASE 2: Deep Reading & Extraction - READY TO START")
    print("  - Review the 20 recommended papers above")
    print("  - For each paper, extract:")
    print("    * Problem: What specific problem are they solving?")
    print("    * Methodology: Core technical contribution")
    print("    * Results: Quantitative metrics")
    print("    * Limitations: What they didn't solve")
    print()
    print("PHASE 3: Synthesis & Gap Identification")
    print("  - Create comparison table of methodologies")
    print("  - Identify research gaps and white space")
    print()
    print("PHASE 4: Hypothesis Generation")
    print("  - Formulate testable research hypothesis")
    print()
    print("PHASE 5: Reverse-Engineered Introduction")
    print("  - Draft Introduction section based on hypothesis")
    print()
    print("="*100)
    print()
    print(f"All results saved to: {json_file}")
    print("Ready for Phase 2 analysis!")
    print()
