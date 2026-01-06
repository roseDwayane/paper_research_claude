"""
MCP-based Gemini Launcher for Phase 2 execution.

This tool interfaces with the pal-mcp-server to launch Gemini
for literature review and introduction writing tasks.
"""

import json
import uuid
from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from src.tools.base import BaseTool, ToolResult
from src.schemas.handoff_payload import HandoffPayload, TaskType
from src.config import config


@dataclass
class GeminiTaskResult:
    """Result from a Gemini task."""

    task_id: str
    status: str  # "queued", "running", "completed", "failed"
    output_location: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class GeminiLauncher(BaseTool):
    """
    Launch Gemini sub-agent via MCP for Phase 2 execution.

    This tool creates a task specification for Gemini and prepares
    the prompt with all necessary context from the hand-off payload.

    Note: Actual MCP integration depends on pal-mcp-server configuration.
    This implementation creates the task specification that would be
    passed to the MCP server.
    """

    name = "launch_gemini_via_mcp"
    description = "Hand off to Gemini sub-agent via MCP for literature review and introduction writing."

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "handoff_payload": {
                    "type": "object",
                    "description": "Complete hand-off payload from Phase 1",
                },
                "task_type": {
                    "type": "string",
                    "enum": ["literature_review", "systematic_review", "introduction_writing"],
                    "description": "Type of task for Gemini",
                },
            },
            "required": ["handoff_payload"],
        }

    async def execute(
        self,
        handoff_payload: HandoffPayload,
        task_type: Optional[TaskType] = None,
        output_dir: Optional[Path] = None,
    ) -> ToolResult[GeminiTaskResult]:
        """
        Prepare and launch Gemini task via MCP.

        Args:
            handoff_payload: Complete Phase 1 hand-off payload
            task_type: Type of task (defaults to payload setting)
            output_dir: Directory for output files

        Returns:
            ToolResult with GeminiTaskResult
        """
        try:
            # Verify payload
            if not handoff_payload.verify():
                return ToolResult.fail("Payload checksum verification failed")

            validation_errors = handoff_payload.validate_references()
            if validation_errors:
                return ToolResult.fail(f"Payload validation errors: {validation_errors}")

            task_type = task_type or handoff_payload.gemini_instructions.task

            # Generate task ID
            task_id = f"gemini_{uuid.uuid4().hex[:12]}"

            # Build Gemini prompt
            prompt = self._build_gemini_prompt(handoff_payload, task_type)

            # Create task specification
            task_spec = {
                "task_id": task_id,
                "model": "gemini-pro",  # or gemini-1.5-pro
                "task_type": task_type.value,
                "created_at": datetime.utcnow().isoformat(),
                "payload_checksum": handoff_payload.metadata.validation_checksum,
                "prompt": prompt,
                "constraints": handoff_payload.gemini_instructions.constraints,
                "max_tokens": handoff_payload.gemini_instructions.max_tokens,
                "output_format": handoff_payload.gemini_instructions.output_format,
            }

            # Save task specification
            output_dir = output_dir or config.storage.outputs_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            task_file = output_dir / f"{task_id}_spec.json"
            with open(task_file, "w", encoding="utf-8") as f:
                json.dump(task_spec, f, indent=2)

            prompt_file = output_dir / f"{task_id}_prompt.md"
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)

            # In a real implementation, this would call the MCP server
            # For now, we prepare the task and return the specification
            result = GeminiTaskResult(
                task_id=task_id,
                status="prepared",  # Would be "queued" when actually submitted
                output_location=str(output_dir / f"{task_id}_output.md"),
                started_at=datetime.utcnow().isoformat(),
            )

            return ToolResult.ok(
                result,
                task_file=str(task_file),
                prompt_file=str(prompt_file),
                message="Task prepared. Submit to MCP server to execute.",
            )

        except Exception as e:
            return ToolResult.fail(f"Gemini launch preparation failed: {e}")

    def _build_gemini_prompt(
        self,
        payload: HandoffPayload,
        task_type: TaskType,
    ) -> str:
        """Build the complete prompt for Gemini."""

        # Build paper citations section
        papers_section = self._build_papers_section(payload)

        # Build gaps section
        gaps_section = self._build_gaps_section(payload)

        # Build hypothesis section
        hypothesis_section = self._build_hypothesis_section(payload)

        # Build knowledge context
        knowledge_section = self._build_knowledge_section(payload)

        # Task-specific instructions
        task_instructions = self._get_task_instructions(task_type, payload)

        prompt = f"""# Research Writing Task

You are an academic research assistant tasked with writing a literature review and introduction section for a research paper.

## Critical Constraints

**IMPORTANT**: You must ONLY cite papers from the approved paper manifest below. Do NOT hallucinate or make up any citations. Every claim must be supported by a paper from the manifest.

Citation Style: {payload.gemini_instructions.citation_style.value}

## Research Topic

{payload.metadata.research_topic}

{hypothesis_section}

## Approved Paper Manifest

The following papers are the ONLY sources you may cite. Each paper has been verified and approved.

{papers_section}

## Identified Research Gaps

Your writing should address these identified gaps:

{gaps_section}

## Domain Knowledge Context

{knowledge_section}

## Target Journals

This paper is being prepared for submission to:
{chr(10).join(f"- {j.name} (IF: {j.impact_factor or 'N/A'})" for j in payload.target_journals[:3])}

## Your Task

{task_instructions}

## Output Format

Provide your output in Markdown format with:
1. Clear section headings
2. Proper in-text citations in {payload.gemini_instructions.citation_style.value} format
3. A References section at the end (using only papers from the manifest)

## Quality Requirements

- Academic writing standards
- Logical flow and coherence
- Critical analysis, not just summary
- Clear connection between literature and research gaps
- Proper transitions between sections

Begin your writing below:
"""
        return prompt

    def _build_papers_section(self, payload: HandoffPayload) -> str:
        """Build the papers section for the prompt."""
        lines = []
        for i, paper in enumerate(payload.paper_manifest.papers, 1):
            lines.append(f"""
### Paper {i}: {paper.id}
**Title:** {paper.title}
**Authors:** {', '.join(paper.authors[:5])}{'...' if len(paper.authors) > 5 else ''}
**Year:** {paper.year or 'Unknown'}
**DOI:** {paper.doi or 'N/A'}
**Relevance Score:** {paper.relevance_score:.2f}
**Key Themes:** {', '.join(paper.themes) if paper.themes else 'N/A'}
**Why Relevant:** {paper.relevance_rationale}

**Abstract:**
{paper.abstract or 'Abstract not available'}
""")
        return "\n".join(lines)

    def _build_gaps_section(self, payload: HandoffPayload) -> str:
        """Build the gaps section for the prompt."""
        if not payload.gap_analysis.identified_gaps:
            return "No specific gaps identified."

        lines = []
        for gap in payload.gap_analysis.identified_gaps:
            evidence = ", ".join(gap.evidence_papers) if gap.evidence_papers else "General observation"
            lines.append(f"""
### {gap.gap_id}: {gap.title}
**Severity:** {gap.severity.value}
**Novelty Potential:** {gap.novelty_potential.value}
**Description:** {gap.description}
**Evidence from papers:** {evidence}
""")
        return "\n".join(lines)

    def _build_hypothesis_section(self, payload: HandoffPayload) -> str:
        """Build the hypothesis section for the prompt."""
        if not payload.hypothesis_specification:
            return ""

        h = payload.hypothesis_specification
        return f"""
## Research Hypothesis

**Problem Statement:** {h.problem_statement}

**Research Questions:**
{chr(10).join(f"- {rq}" for rq in h.research_questions)}

**Hypothesis:** {h.hypothesis}

**Expected Significance:**
- Theoretical: {h.expected_significance.theoretical}
- Practical: {h.expected_significance.practical}

**Scope:**
{chr(10).join(f"- {s}" for s in h.scope_boundaries)}
"""

    def _build_knowledge_section(self, payload: HandoffPayload) -> str:
        """Build the knowledge context section."""
        kg = payload.knowledge_graph

        if not kg.core_concepts:
            return "No knowledge graph available."

        concepts = "\n".join(
            f"- **{c.term}**: {c.definition}"
            for c in kg.core_concepts[:15]
        )

        methods = ", ".join(kg.methodological_paradigms) if kg.methodological_paradigms else "Not specified"
        boundaries = ", ".join(kg.field_boundaries) if kg.field_boundaries else "Not specified"

        return f"""
**Key Concepts:**
{concepts}

**Methodological Paradigms:** {methods}

**Field Boundaries:** {boundaries}
"""

    def _get_task_instructions(self, task_type: TaskType, payload: HandoffPayload) -> str:
        """Get task-specific instructions."""
        word_limit = ""
        if payload.target_journals and payload.target_journals[0].word_limit:
            word_limit = f" (aim for approximately {payload.target_journals[0].word_limit // 4} words for this section)"

        if task_type == TaskType.LITERATURE_REVIEW:
            return f"""
Write a comprehensive literature review{word_limit} that:

1. **Introduces the research area** - Provide context and explain why this topic matters
2. **Organizes themes** - Group related studies by theme, methodology, or chronology
3. **Critically analyzes** - Don't just summarize; compare, contrast, and evaluate studies
4. **Identifies patterns** - Note agreements, disagreements, and trends across studies
5. **Highlights gaps** - Explicitly discuss the research gaps identified above
6. **Builds argument** - Lead toward the research hypothesis/questions

Structure suggestion:
- Introduction to the field
- Thematic sections covering key areas
- Methodological considerations
- Gap analysis and research opportunity
- Transition to current study
"""

        elif task_type == TaskType.INTRODUCTION_WRITING:
            return f"""
Write an introduction section{word_limit} that:

1. **Opens with significance** - Why should readers care about this topic?
2. **Establishes context** - What is the current state of knowledge?
3. **Reviews key literature** - Cite relevant studies from the manifest
4. **Identifies the gap** - What's missing in current research?
5. **States the purpose** - What does this study aim to do?
6. **Previews methodology** - Brief hint at approach
7. **Outlines contribution** - What will this study add?

Follow the funnel structure: broad context → specific problem → your study

The introduction should seamlessly lead to the research questions and hypothesis.
"""

        else:  # SYSTEMATIC_REVIEW
            return f"""
Write a systematic review section{word_limit} following PRISMA guidelines where applicable:

1. **Search strategy** - Describe how papers were identified (you may describe the search as systematic)
2. **Inclusion/exclusion** - Note that papers were selected based on relevance scoring
3. **Data extraction** - Summarize key findings from each paper
4. **Quality assessment** - Evaluate methodological quality where relevant
5. **Synthesis** - Combine findings thematically or by methodology
6. **Gap identification** - Highlight areas needing further research

Include a summary table of included studies if appropriate.
"""


# Convenience function
async def launch_gemini(
    handoff_payload: HandoffPayload,
    task_type: Optional[TaskType] = None,
    output_dir: Optional[Path] = None,
) -> ToolResult[GeminiTaskResult]:
    """Convenience function to launch Gemini task."""
    launcher = GeminiLauncher()
    return await launcher.execute(handoff_payload, task_type, output_dir)
