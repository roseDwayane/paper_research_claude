"""
Hand-off Payload Schema - The contract between Claude (PI) and Gemini (Executor).

This is the critical interface that prevents hallucination and ensures
reproducible research synthesis.
"""

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field

from src.schemas.paper import Paper


class Severity(str, Enum):
    """Gap severity levels."""

    CRITICAL = "critical"
    MODERATE = "moderate"
    MINOR = "minor"


class NoveltyPotential(str, Enum):
    """Novelty potential assessment."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskType(str, Enum):
    """Gemini task types."""

    LITERATURE_REVIEW = "literature_review"
    SYSTEMATIC_REVIEW = "systematic_review"
    INTRODUCTION_WRITING = "introduction_writing"


class CitationStyle(str, Enum):
    """Citation style options."""

    APA7 = "APA7"
    MLA9 = "MLA9"
    CHICAGO = "Chicago"
    IEEE = "IEEE"


# ============================================================================
# Knowledge Graph Components
# ============================================================================


class Concept(BaseModel):
    """A concept node in the knowledge graph."""

    term: str = Field(..., description="The concept term")
    definition: str = Field(..., description="Concise definition")
    relationships: list[str] = Field(
        default_factory=list, description="Related concept terms"
    )


class KnowledgeGraph(BaseModel):
    """Domain knowledge graph extracted from literature."""

    core_concepts: list[Concept] = Field(
        default_factory=list, description="Key concepts in the domain"
    )
    field_boundaries: list[str] = Field(
        default_factory=list, description="What defines this research field"
    )
    methodological_paradigms: list[str] = Field(
        default_factory=list, description="Common methodological approaches"
    )


# ============================================================================
# Paper Manifest
# ============================================================================


class ManifestPaper(BaseModel):
    """Paper entry in the manifest (subset of full Paper for hand-off)."""

    id: str
    doi: Optional[str] = None
    title: str
    authors: list[str]  # Simplified to just names
    year: Optional[int] = None
    abstract: Optional[str] = None
    source_api: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    relevance_rationale: str
    themes: list[str] = Field(default_factory=list)
    citation_count: Optional[int] = None
    retrieval_timestamp: str

    @classmethod
    def from_paper(cls, paper: Paper) -> "ManifestPaper":
        """Create manifest entry from full Paper object."""
        return cls(
            id=paper.id,
            doi=paper.doi,
            title=paper.title,
            authors=[a.name for a in paper.authors],
            year=paper.year,
            abstract=paper.abstract,
            source_api=paper.source_api.value,
            relevance_score=paper.relevance_score or 0.0,
            relevance_rationale=paper.relevance_rationale or "",
            themes=paper.themes,
            citation_count=paper.citation_count,
            retrieval_timestamp=paper.retrieved_at.isoformat(),
        )


class PaperManifest(BaseModel):
    """Collection of papers approved for citation."""

    total_papers: int = 0
    papers: list[ManifestPaper] = Field(default_factory=list)

    def add_paper(self, paper: Paper) -> None:
        """Add a paper to the manifest."""
        self.papers.append(ManifestPaper.from_paper(paper))
        self.total_papers = len(self.papers)

    def get_paper_ids(self) -> set[str]:
        """Get all paper IDs in the manifest."""
        return {p.id for p in self.papers}


# ============================================================================
# Gap Analysis
# ============================================================================


class Gap(BaseModel):
    """An identified research gap."""

    gap_id: str = Field(..., description="Unique gap identifier (e.g., GAP_001)")
    title: str = Field(..., description="Short title for the gap")
    description: str = Field(..., description="Detailed description of the gap")
    evidence_papers: list[str] = Field(
        default_factory=list, description="Paper IDs that evidence this gap"
    )
    severity: Severity = Field(default=Severity.MODERATE)
    novelty_potential: NoveltyPotential = Field(default=NoveltyPotential.MEDIUM)


class GapAnalysis(BaseModel):
    """Collection of identified research gaps."""

    identified_gaps: list[Gap] = Field(default_factory=list)


# ============================================================================
# Hypothesis Specification
# ============================================================================


class ExpectedSignificance(BaseModel):
    """Expected significance of the research."""

    theoretical: str = Field(..., description="Theoretical contribution")
    practical: str = Field(..., description="Practical implications")


class HypothesisSpecification(BaseModel):
    """Research hypothesis and problem definition."""

    problem_statement: str = Field(
        ..., description="Clear, falsifiable problem statement"
    )
    research_questions: list[str] = Field(
        default_factory=list, description="Specific research questions (RQ1, RQ2...)"
    )
    hypothesis: str = Field(..., description="Main research hypothesis")
    expected_significance: ExpectedSignificance
    scope_boundaries: list[str] = Field(
        default_factory=list,
        description="What's in scope and what's explicitly out of scope",
    )


# ============================================================================
# Target Journals
# ============================================================================


class TargetJournal(BaseModel):
    """A target journal for publication."""

    name: str
    impact_factor: Optional[float] = None
    review_cycle_days: Optional[int] = Field(
        None, description="Average review cycle in days"
    )
    fit_rationale: str = Field(..., description="Why this journal is a good fit")
    style_guide_url: Optional[str] = None
    word_limit: Optional[int] = None


# ============================================================================
# Gemini Instructions
# ============================================================================


class GeminiInstructions(BaseModel):
    """Instructions for Gemini sub-agent execution."""

    task: TaskType = Field(default=TaskType.INTRODUCTION_WRITING)
    output_format: str = Field(default="markdown")
    citation_style: CitationStyle = Field(default=CitationStyle.APA7)
    max_tokens: int = Field(default=15000)
    constraints: list[str] = Field(
        default_factory=lambda: [
            "Only cite papers from paper_manifest",
            "Address all identified gaps",
            "Follow hypothesis_specification scope",
        ]
    )


# ============================================================================
# Metadata
# ============================================================================


class Metadata(BaseModel):
    """Payload metadata for tracking and validation."""

    research_topic: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    phase1_agent_id: str = Field(default="claude_pi_agent")
    validation_checksum: Optional[str] = None


# ============================================================================
# Main Payload
# ============================================================================


class HandoffPayload(BaseModel):
    """
    The complete hand-off payload from Claude (PI) to Gemini (Executor).

    This is the contract that ensures Gemini operates within defined bounds
    and doesn't hallucinate citations or claims.
    """

    metadata: Metadata
    knowledge_graph: KnowledgeGraph = Field(default_factory=KnowledgeGraph)
    paper_manifest: PaperManifest = Field(default_factory=PaperManifest)
    gap_analysis: GapAnalysis = Field(default_factory=GapAnalysis)
    hypothesis_specification: Optional[HypothesisSpecification] = None
    target_journals: list[TargetJournal] = Field(default_factory=list)
    gemini_instructions: GeminiInstructions = Field(default_factory=GeminiInstructions)

    def compute_checksum(self) -> str:
        """Compute SHA256 checksum of the payload (excluding checksum field)."""
        # Create a copy without the checksum
        data = self.model_dump()
        data["metadata"]["validation_checksum"] = None

        # Serialize deterministically
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def sign(self) -> "HandoffPayload":
        """Sign the payload by computing and setting the checksum."""
        self.metadata.validation_checksum = self.compute_checksum()
        return self

    def verify(self) -> bool:
        """Verify the payload checksum."""
        stored_checksum = self.metadata.validation_checksum
        computed_checksum = self.compute_checksum()
        return stored_checksum == computed_checksum

    def validate_references(self) -> list[str]:
        """
        Validate that all gap evidence_papers reference valid paper IDs.
        Returns list of validation errors.
        """
        errors = []
        valid_paper_ids = self.paper_manifest.get_paper_ids()

        for gap in self.gap_analysis.identified_gaps:
            for paper_id in gap.evidence_papers:
                if paper_id not in valid_paper_ids:
                    errors.append(
                        f"Gap '{gap.gap_id}' references unknown paper: {paper_id}"
                    )

        return errors

    def to_debug_markdown(self) -> str:
        """Generate human-readable markdown summary for debugging."""
        lines = [
            f"# Research Hand-off Payload",
            f"",
            f"**Topic:** {self.metadata.research_topic}",
            f"**Generated:** {self.metadata.generated_at}",
            f"**Checksum:** `{self.metadata.validation_checksum}`",
            f"",
            f"## Paper Manifest ({self.paper_manifest.total_papers} papers)",
            f"",
        ]

        for i, paper in enumerate(self.paper_manifest.papers, 1):
            lines.append(
                f"{i}. **{paper.title}** ({paper.year})"
            )
            lines.append(f"   - Relevance: {paper.relevance_score:.2f}")
            lines.append(f"   - Rationale: {paper.relevance_rationale[:100]}...")
            lines.append(f"   - DOI: {paper.doi or 'N/A'}")
            lines.append("")

        lines.extend([
            f"## Identified Gaps ({len(self.gap_analysis.identified_gaps)})",
            f"",
        ])

        for gap in self.gap_analysis.identified_gaps:
            lines.append(f"### {gap.gap_id}: {gap.title}")
            lines.append(f"**Severity:** {gap.severity.value}")
            lines.append(f"**Description:** {gap.description}")
            lines.append(f"**Evidence:** {', '.join(gap.evidence_papers)}")
            lines.append("")

        if self.hypothesis_specification:
            lines.extend([
                f"## Hypothesis",
                f"",
                f"**Problem:** {self.hypothesis_specification.problem_statement}",
                f"",
                f"**Hypothesis:** {self.hypothesis_specification.hypothesis}",
                f"",
            ])

        return "\n".join(lines)
