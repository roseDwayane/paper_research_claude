"""
Execute comprehensive literature search for EEG + Eye-tracking + Multimodal research
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from literature_search import search_literature, export_search_results
import json
from datetime import datetime


def main():
    """Execute 5 targeted search queries for EEG-eye tracking multimodal research"""

    # Define search queries with specific focus areas
    search_queries = [
        {
            'name': 'Query 1: Core Methodology',
            'query': 'EEG eye tracking multimodal fusion',
            'related_terms': ['neural signals', 'deep learning', 'feature fusion'],
            'negative_keywords': ['fMRI', 'PET scan', 'single modality'],
        },
        {
            'name': 'Query 2: Attention Detection',
            'query': 'EEG gaze attention detection deep learning',
            'related_terms': ['visual attention', 'cognitive state', 'attention recognition'],
            'negative_keywords': ['ADHD medication', 'pharmaceutical'],
        },
        {
            'name': 'Query 3: Neural-Gaze Integration',
            'query': 'brain signals eye movement multimodal',
            'related_terms': ['electroencephalography', 'oculomotor', 'neural correlates'],
            'negative_keywords': ['surgery', 'clinical trial'],
        },
        {
            'name': 'Query 4: Cognitive Load',
            'query': 'EEG pupil cognitive load',
            'related_terms': ['pupillometry', 'mental workload', 'cognitive assessment'],
            'negative_keywords': ['drug', 'medication'],
        },
        {
            'name': 'Query 5: BCI Applications',
            'query': 'multimodal brain-computer interface eye tracking',
            'related_terms': ['BCI', 'hybrid BCI', 'assistive technology', 'human-computer interaction'],
            'negative_keywords': ['invasive electrode', 'surgical'],
        },
    ]

    # Search parameters
    sources = ['arxiv', 'semantic_scholar', 'pubmed', 'crossref']
    start_date = '2020-01-01'  # Papers from 2020-2025
    max_results = 50

    all_results = {}
    all_papers = []

    print("="*80)
    print("EEG + Eye-Tracking + Multimodal Learning: Comprehensive Literature Search")
    print("="*80)
    print(f"Date Range: 2020-01-01 to {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Sources: {', '.join(sources)}")
    print(f"Max Results per Source: {max_results}")
    print("="*80)
    print()

    # Execute each search query
    for i, search_config in enumerate(search_queries, 1):
        print(f"\n{'='*80}")
        print(f"{search_config['name']}")
        print(f"{'='*80}")

        results = search_literature(
            query=search_config['query'],
            sources=sources,
            max_results_per_source=max_results,
            start_date=start_date,
            negative_keywords=search_config.get('negative_keywords', []),
            expand_query=True,
            related_terms=search_config.get('related_terms', [])
        )

        all_results[f"query_{i}"] = results
        all_papers.extend(results['papers'])

        print(f"\nFound {results['total_papers']} unique papers for this query")
        print(f"Source breakdown: {results['source_counts']}")

    # Deduplicate across all queries
    print(f"\n{'='*80}")
    print("DEDUPLICATION ACROSS ALL QUERIES")
    print(f"{'='*80}")

    from literature_search import AcademicSearchEngine
    engine = AcademicSearchEngine()
    unique_papers = engine.deduplicate_papers(all_papers)

    print(f"Total papers before deduplication: {len(all_papers)}")
    print(f"Total unique papers after deduplication: {len(unique_papers)}")

    # Sort by date (most recent first)
    unique_papers.sort(key=lambda x: x.get('published_date', '0000-00-00'), reverse=True)

    # Create combined results
    combined_results = {
        'search_metadata': {
            'total_queries': len(search_queries),
            'date_range': f"{start_date} to {datetime.now().strftime('%Y-%m-%d')}",
            'sources': sources,
            'search_date': datetime.now().isoformat(),
        },
        'individual_queries': all_results,
        'combined_results': {
            'total_unique_papers': len(unique_papers),
            'papers': unique_papers
        }
    }

    # Statistics
    print(f"\n{'='*80}")
    print("STATISTICS")
    print(f"{'='*80}")

    # Year distribution
    years = {}
    for paper in unique_papers:
        year = paper.get('year', 'Unknown')
        years[year] = years.get(year, 0) + 1

    print("\nYear Distribution:")
    for year in sorted(years.keys(), reverse=True):
        if year != 'Unknown' and year != 'N/A':
            print(f"  {year}: {years[year]} papers")

    # Venue distribution (top 15)
    venues = {}
    for paper in unique_papers:
        venue = paper.get('venue', 'Unknown')
        if venue and venue != 'N/A':
            venues[venue] = venues.get(venue, 0) + 1

    print("\nTop 15 Venues:")
    for venue, count in sorted(venues.items(), key=lambda x: x[1], reverse=True)[:15]:
        print(f"  {count:2d} - {venue}")

    # Source distribution
    sources_dist = {}
    for paper in unique_papers:
        source = paper.get('source', 'Unknown')
        sources_dist[source] = sources_dist.get(source, 0) + 1

    print("\nSource Distribution:")
    for source, count in sorted(sources_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} papers")

    return combined_results, unique_papers


if __name__ == "__main__":
    results, papers = main()

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = os.path.join(output_dir, f'eeg_eyetracking_search_{timestamp}.json')

    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}")

    # Export to JSON (recommended for complete metadata)
    export_search_results(results['combined_results'], json_path, format='json')
    print(f"[OK] JSON exported to: {json_path}")

    # Also export summary
    summary_path = os.path.join(output_dir, f'eeg_eyetracking_summary_{timestamp}.txt')
    export_search_results(results['combined_results'], summary_path, format='summary')
    print(f"[OK] Summary exported to: {summary_path}")

    # Export markdown for easy reading
    md_path = os.path.join(output_dir, f'eeg_eyetracking_papers_{timestamp}.md')
    export_search_results(results['combined_results'], md_path, format='markdown')
    print(f"[OK] Markdown exported to: {md_path}")

    print(f"\n{'='*80}")
    print("SEARCH COMPLETE")
    print(f"{'='*80}")
    print(f"Total unique papers found: {results['combined_results']['total_unique_papers']}")
    print(f"Results saved to: {output_dir}")
