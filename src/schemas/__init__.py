"""
Pydantic schemas for the Research Agent.
"""

from src.schemas.paper import Paper, Author
from src.schemas.handoff_payload import (
    HandoffPayload,
    Metadata,
    KnowledgeGraph,
    Concept,
    PaperManifest,
    GapAnalysis,
    Gap,
    HypothesisSpecification,
    TargetJournal,
    GeminiInstructions,
)

__all__ = [
    "Paper",
    "Author",
    "HandoffPayload",
    "Metadata",
    "KnowledgeGraph",
    "Concept",
    "PaperManifest",
    "GapAnalysis",
    "Gap",
    "HypothesisSpecification",
    "TargetJournal",
    "GeminiInstructions",
]
