"""
Paper schema - Core data model for academic papers.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SourceAPI(str, Enum):
    """Source API identifiers."""

    OPENALEX = "openalex"
    PUBMED = "pubmed"
    GOOGLE_SCHOLAR = "google_scholar"


class Author(BaseModel):
    """Author information."""

    name: str
    orcid: Optional[str] = None
    affiliation: Optional[str] = None


class Paper(BaseModel):
    """
    Academic paper representation.

    This is the canonical format used throughout the system.
    All search tools normalize their results to this schema.
    """

    # Identifiers
    id: str = Field(..., description="Internal unique identifier")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    openalex_id: Optional[str] = Field(None, description="OpenAlex Work ID")

    # Core metadata
    title: str
    authors: list[Author] = Field(default_factory=list)
    year: Optional[int] = None
    abstract: Optional[str] = None

    # Publication info
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None

    # Metrics
    citation_count: Optional[int] = None
    is_open_access: bool = False

    # Source tracking
    source_api: SourceAPI
    source_url: Optional[str] = None
    raw_response: Optional[dict] = Field(None, exclude=True)

    # Analysis results (filled by Critic agent)
    relevance_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Relevance score from 0-1"
    )
    relevance_rationale: Optional[str] = Field(
        None, description="Why this paper is relevant"
    )
    themes: list[str] = Field(
        default_factory=list, description="Thematic tags assigned by analysis"
    )
    key_contributions: list[str] = Field(
        default_factory=list, description="Main contributions of the paper"
    )

    # Selection status
    is_selected: bool = Field(
        False, description="Whether selected for final manifest"
    )
    selection_reason: Optional[str] = None

    # Timestamps
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_citation(self, style: str = "APA7") -> str:
        """Generate citation string in specified style."""
        authors_str = ", ".join(a.name for a in self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."

        if style == "APA7":
            year_str = f"({self.year})" if self.year else "(n.d.)"
            journal_str = f" {self.journal}." if self.journal else ""
            doi_str = f" https://doi.org/{self.doi}" if self.doi else ""
            return f"{authors_str} {year_str}. {self.title}.{journal_str}{doi_str}"

        # Default fallback
        return f"{authors_str}. {self.title}. {self.year}"

    def get_unique_key(self) -> str:
        """Get a unique key for deduplication."""
        if self.doi:
            return f"doi:{self.doi}"
        if self.pmid:
            return f"pmid:{self.pmid}"
        if self.openalex_id:
            return f"openalex:{self.openalex_id}"
        # Fallback to title-based key (normalized)
        normalized_title = self.title.lower().strip()[:100]
        return f"title:{normalized_title}"
