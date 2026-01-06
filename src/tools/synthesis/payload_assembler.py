"""
Payload assembler for creating the hand-off payload.
"""

from typing import Optional
from datetime import datetime

from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper
from src.schemas.handoff_payload import (
    HandoffPayload,
    Metadata,
    KnowledgeGraph,
    PaperManifest,
    GapAnalysis,
    Gap,
    HypothesisSpecification,
    TargetJournal,
    GeminiInstructions,
    TaskType,
    CitationStyle,
)


class PayloadAssembler(BaseTool):
    """Assemble the complete hand-off payload."""

    name = "assemble_handoff_payload"
    description = "Assemble all research artifacts into the final hand-off payload for Gemini."

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "research_topic": {"type": "string"},
                "papers": {"type": "array"},
                "knowledge_graph": {"type": "object"},
                "gaps": {"type": "array"},
                "hypothesis": {"type": "object"},
                "journals": {"type": "array"},
                "task_type": {"type": "string"},
                "citation_style": {"type": "string"},
            },
            "required": ["research_topic", "papers"],
        }

    async def execute(
        self,
        research_topic: str,
        papers: list[Paper],
        knowledge_graph: Optional[KnowledgeGraph] = None,
        gaps: Optional[list[Gap]] = None,
        hypothesis: Optional[HypothesisSpecification] = None,
        journals: Optional[list[TargetJournal]] = None,
        task_type: TaskType = TaskType.INTRODUCTION_WRITING,
        citation_style: CitationStyle = CitationStyle.APA7,
    ) -> ToolResult[HandoffPayload]:
        """
        Assemble the complete hand-off payload.

        Args:
            research_topic: Research topic
            papers: Selected papers for the manifest
            knowledge_graph: Domain knowledge graph
            gaps: Identified research gaps
            hypothesis: Research hypothesis
            journals: Target journals
            task_type: Task for Gemini
            citation_style: Citation style

        Returns:
            ToolResult with complete HandoffPayload
        """
        try:
            # Create metadata
            metadata = Metadata(
                research_topic=research_topic,
                generated_at=datetime.utcnow().isoformat(),
                phase1_agent_id="claude_pi_agent",
            )

            # Build paper manifest
            paper_manifest = PaperManifest()
            for paper in papers:
                if paper.is_selected or paper.relevance_score and paper.relevance_score >= 0.5:
                    paper_manifest.add_paper(paper)

            # Build gap analysis
            gap_analysis = GapAnalysis(identified_gaps=gaps or [])

            # Build Gemini instructions
            gemini_instructions = GeminiInstructions(
                task=task_type,
                output_format="markdown",
                citation_style=citation_style,
                max_tokens=15000,
                constraints=[
                    "Only cite papers from paper_manifest",
                    "Address all identified gaps",
                    "Follow hypothesis_specification scope",
                    "Maintain academic writing standards",
                    f"Use {citation_style.value} citation format",
                ],
            )

            # Assemble payload
            payload = HandoffPayload(
                metadata=metadata,
                knowledge_graph=knowledge_graph or KnowledgeGraph(),
                paper_manifest=paper_manifest,
                gap_analysis=gap_analysis,
                hypothesis_specification=hypothesis,
                target_journals=journals or [],
                gemini_instructions=gemini_instructions,
            )

            # Sign the payload
            payload.sign()

            # Validate references
            validation_errors = payload.validate_references()
            if validation_errors:
                return ToolResult.ok(
                    payload,
                    validation_warnings=validation_errors,
                    paper_count=paper_manifest.total_papers,
                    gap_count=len(gaps) if gaps else 0,
                )

            return ToolResult.ok(
                payload,
                paper_count=paper_manifest.total_papers,
                gap_count=len(gaps) if gaps else 0,
                checksum=payload.metadata.validation_checksum,
            )

        except Exception as e:
            return ToolResult.fail(f"Payload assembly failed: {e}")


# Convenience function
async def assemble_handoff_payload(
    research_topic: str,
    papers: list[Paper],
    knowledge_graph: Optional[KnowledgeGraph] = None,
    gaps: Optional[list[Gap]] = None,
    hypothesis: Optional[HypothesisSpecification] = None,
    journals: Optional[list[TargetJournal]] = None,
    task_type: TaskType = TaskType.INTRODUCTION_WRITING,
    citation_style: CitationStyle = CitationStyle.APA7,
) -> ToolResult[HandoffPayload]:
    """Convenience function to assemble payload."""
    assembler = PayloadAssembler()
    return await assembler.execute(
        research_topic=research_topic,
        papers=papers,
        knowledge_graph=knowledge_graph,
        gaps=gaps,
        hypothesis=hypothesis,
        journals=journals,
        task_type=task_type,
        citation_style=citation_style,
    )
