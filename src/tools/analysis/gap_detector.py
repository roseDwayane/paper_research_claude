"""
Research gap detection tool using Claude.
"""

import json
from typing import Optional

import anthropic

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper
from src.schemas.handoff_payload import Gap, Severity, NoveltyPotential


class GapDetector(BaseTool):
    """Detect research gaps from a corpus of papers."""

    name = "detect_research_gaps"
    description = "Identify research gaps in literature based on paper corpus analysis."

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.api.anthropic_api_key)
        self.model = config.api.claude_model

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "papers": {
                    "type": "array",
                    "description": "List of papers to analyze",
                },
                "domain_context": {
                    "type": "string",
                    "description": "Research domain context",
                },
                "target_gaps": {
                    "type": "integer",
                    "description": "Target number of gaps to identify (default: 3)",
                },
            },
            "required": ["papers", "domain_context"],
        }

    async def execute(
        self,
        papers: list[Paper],
        domain_context: str,
        target_gaps: int = 3,
    ) -> ToolResult[list[Gap]]:
        """
        Identify research gaps from paper corpus.

        Args:
            papers: Papers to analyze
            domain_context: Research domain/topic
            target_gaps: Number of gaps to identify

        Returns:
            ToolResult with list of Gap objects
        """
        if not config.api.anthropic_api_key:
            return ToolResult.fail("Anthropic API key not configured")

        if not papers:
            return ToolResult.fail("No papers provided for gap analysis")

        try:
            # Build paper summaries for analysis
            paper_summaries = []
            for i, paper in enumerate(papers[:30]):  # Limit to 30 papers for context
                summary = f"""Paper {i+1} (ID: {paper.id}):
Title: {paper.title}
Year: {paper.year or 'Unknown'}
Themes: {', '.join(paper.themes) if paper.themes else 'Not analyzed'}
Key Contributions: {', '.join(paper.key_contributions) if paper.key_contributions else 'Not analyzed'}
Abstract: {(paper.abstract or 'No abstract')[:500]}..."""
                paper_summaries.append(summary)

            papers_text = "\n\n".join(paper_summaries)

            prompt = f"""You are a research methodology expert analyzing a corpus of academic papers to identify research gaps.

Research Domain: {domain_context}

Number of Papers Analyzed: {len(papers)}

Paper Summaries:
{papers_text}

Based on this corpus, identify {target_gaps} significant research gaps. A research gap is:
- An unexplored or under-explored area
- A methodological limitation across studies
- A contradiction or inconsistency in findings
- A population or context not adequately studied
- A theoretical framework that needs development

For each gap, provide evidence from the papers (by paper ID).

Return your analysis in this JSON format:
{{
    "gaps": [
        {{
            "gap_id": "GAP_001",
            "title": "<short descriptive title>",
            "description": "<detailed 2-3 sentence description of the gap>",
            "evidence_papers": ["<paper_id_1>", "<paper_id_2>"],
            "severity": "critical|moderate|minor",
            "novelty_potential": "high|medium|low",
            "research_opportunity": "<what research could fill this gap>"
        }}
    ],
    "overall_assessment": "<1-2 sentence summary of the field's maturity and opportunities>"
}}

Be specific and cite evidence from the papers. Gaps should be actionable research opportunities."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)

            # Convert to Gap objects
            gaps = []
            for gap_data in analysis.get("gaps", []):
                # Validate evidence papers exist
                valid_paper_ids = {p.id for p in papers}
                evidence = [
                    pid for pid in gap_data.get("evidence_papers", [])
                    if pid in valid_paper_ids
                ]

                gap = Gap(
                    gap_id=gap_data.get("gap_id", f"GAP_{len(gaps)+1:03d}"),
                    title=gap_data.get("title", "Unnamed Gap"),
                    description=gap_data.get("description", ""),
                    evidence_papers=evidence,
                    severity=Severity(gap_data.get("severity", "moderate").lower()),
                    novelty_potential=NoveltyPotential(
                        gap_data.get("novelty_potential", "medium").lower()
                    ),
                )
                gaps.append(gap)

            return ToolResult.ok(
                gaps,
                overall_assessment=analysis.get("overall_assessment", ""),
                papers_analyzed=len(papers),
            )

        except json.JSONDecodeError as e:
            return ToolResult.fail(f"Failed to parse gap analysis: {e}")
        except anthropic.APIError as e:
            return ToolResult.fail(f"Claude API error: {e}")
        except Exception as e:
            return ToolResult.fail(f"Gap detection failed: {e}")


# Convenience function
async def detect_research_gaps(
    papers: list[Paper],
    domain_context: str,
    target_gaps: int = 3,
) -> ToolResult[list[Gap]]:
    """Convenience function to detect research gaps."""
    detector = GapDetector()
    return await detector.execute(papers, domain_context, target_gaps)
