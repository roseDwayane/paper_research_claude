"""
Search tools for academic literature.
"""

from src.tools.search.openalex import OpenAlexSearchTool
from src.tools.search.pubmed import PubMedSearchTool
from src.tools.search.google_scholar import GoogleScholarSearchTool
from src.tools.search.deduplicator import deduplicate_papers

__all__ = [
    "OpenAlexSearchTool",
    "PubMedSearchTool",
    "GoogleScholarSearchTool",
    "deduplicate_papers",
]
