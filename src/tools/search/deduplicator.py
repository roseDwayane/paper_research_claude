"""
Paper deduplication utility.

Deduplicates papers across multiple sources using DOI, PMID, and title matching.
"""

from typing import Optional
from difflib import SequenceMatcher

from src.schemas.paper import Paper


def normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    import re
    # Lowercase
    title = title.lower()
    # Remove punctuation
    title = re.sub(r"[^\w\s]", "", title)
    # Collapse whitespace
    title = re.sub(r"\s+", " ", title).strip()
    return title


def title_similarity(title1: str, title2: str) -> float:
    """Calculate title similarity ratio."""
    t1 = normalize_title(title1)
    t2 = normalize_title(title2)
    return SequenceMatcher(None, t1, t2).ratio()


def deduplicate_papers(
    papers: list[Paper],
    title_threshold: float = 0.85,
    prefer_source_order: Optional[list[str]] = None,
) -> list[Paper]:
    """
    Deduplicate papers from multiple sources.

    Priority for keeping duplicates:
    1. Paper with DOI
    2. Paper with more metadata (abstract, authors, etc.)
    3. Paper from preferred source (if specified)
    4. First encountered

    Args:
        papers: List of papers to deduplicate
        title_threshold: Minimum title similarity to consider as duplicate
        prefer_source_order: Preferred source order (e.g., ["openalex", "pubmed", "google_scholar"])

    Returns:
        Deduplicated list of papers
    """
    if not papers:
        return []

    prefer_source_order = prefer_source_order or ["openalex", "pubmed", "google_scholar"]

    # Track seen papers by various keys
    seen_doi: dict[str, Paper] = {}
    seen_pmid: dict[str, Paper] = {}
    seen_title: dict[str, Paper] = {}

    unique_papers: list[Paper] = []

    def get_paper_score(paper: Paper) -> int:
        """Score paper by metadata completeness."""
        score = 0
        if paper.doi:
            score += 10
        if paper.abstract:
            score += 5
        if paper.authors:
            score += len(paper.authors)
        if paper.year:
            score += 2
        if paper.citation_count:
            score += 1

        # Prefer certain sources
        try:
            source_idx = prefer_source_order.index(paper.source_api.value)
            score += (len(prefer_source_order) - source_idx)
        except ValueError:
            pass

        return score

    def should_replace(existing: Paper, new: Paper) -> bool:
        """Determine if new paper should replace existing."""
        return get_paper_score(new) > get_paper_score(existing)

    for paper in papers:
        is_duplicate = False
        duplicate_of: Optional[Paper] = None

        # Check DOI match
        if paper.doi:
            doi_key = paper.doi.lower()
            if doi_key in seen_doi:
                is_duplicate = True
                duplicate_of = seen_doi[doi_key]
            else:
                seen_doi[doi_key] = paper

        # Check PMID match
        if not is_duplicate and paper.pmid:
            if paper.pmid in seen_pmid:
                is_duplicate = True
                duplicate_of = seen_pmid[paper.pmid]
            else:
                seen_pmid[paper.pmid] = paper

        # Check title similarity
        if not is_duplicate:
            normalized = normalize_title(paper.title)
            for seen_norm, seen_paper in seen_title.items():
                if title_similarity(normalized, seen_norm) >= title_threshold:
                    is_duplicate = True
                    duplicate_of = seen_paper
                    break

            if not is_duplicate:
                seen_title[normalized] = paper

        # Handle deduplication
        if is_duplicate and duplicate_of:
            if should_replace(duplicate_of, paper):
                # Replace the existing paper
                try:
                    idx = unique_papers.index(duplicate_of)
                    unique_papers[idx] = paper

                    # Update lookup tables
                    if paper.doi:
                        seen_doi[paper.doi.lower()] = paper
                    if paper.pmid:
                        seen_pmid[paper.pmid] = paper
                    seen_title[normalize_title(paper.title)] = paper
                except ValueError:
                    pass
        elif not is_duplicate:
            unique_papers.append(paper)

    return unique_papers


def merge_paper_metadata(primary: Paper, secondary: Paper) -> Paper:
    """
    Merge metadata from two papers representing the same work.

    Takes the best of both papers.
    """
    merged = primary.model_copy()

    # Fill in missing fields from secondary
    if not merged.doi and secondary.doi:
        merged.doi = secondary.doi
    if not merged.pmid and secondary.pmid:
        merged.pmid = secondary.pmid
    if not merged.openalex_id and secondary.openalex_id:
        merged.openalex_id = secondary.openalex_id
    if not merged.abstract and secondary.abstract:
        merged.abstract = secondary.abstract
    if not merged.authors and secondary.authors:
        merged.authors = secondary.authors
    if not merged.year and secondary.year:
        merged.year = secondary.year
    if not merged.journal and secondary.journal:
        merged.journal = secondary.journal
    if not merged.citation_count and secondary.citation_count:
        merged.citation_count = secondary.citation_count

    return merged
