"""
Relevance analysis tool using Claude for LLM-based scoring.
"""

import json
from typing import Optional

import anthropic

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper


class RelevanceAnalyzer(BaseTool):
    """Analyze paper relevance using Claude."""

    name = "analyze_paper_relevance"
    description = "Score paper relevance to research topic using LLM analysis. Returns relevance score, rationale, and thematic tags."

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.api.anthropic_api_key)
        self.model = config.api.claude_model

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "paper": {
                    "type": "object",
                    "description": "Paper object with title and abstract",
                },
                "research_topic": {
                    "type": "string",
                    "description": "The research topic/question to evaluate against",
                },
                "criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific relevance criteria to consider",
                },
            },
            "required": ["paper", "research_topic"],
        }

    async def execute(
        self,
        paper: Paper,
        research_topic: str,
        criteria: Optional[list[str]] = None,
    ) -> ToolResult[dict]:
        """
        Analyze paper relevance to research topic.

        Args:
            paper: Paper to analyze
            research_topic: Research topic/question
            criteria: Optional specific criteria

        Returns:
            ToolResult with relevance score, rationale, contributions, themes
        """
        if not config.api.anthropic_api_key:
            return ToolResult.fail("Anthropic API key not configured")

        try:
            criteria_text = ""
            if criteria:
                criteria_text = f"\n\nSpecific criteria to consider:\n" + "\n".join(
                    f"- {c}" for c in criteria
                )

            prompt = f"""Analyze the relevance of this academic paper to the given research topic.

Research Topic: {research_topic}
{criteria_text}

Paper Title: {paper.title}

Paper Abstract:
{paper.abstract or 'No abstract available'}

Year: {paper.year or 'Unknown'}
Citations: {paper.citation_count or 'Unknown'}

Provide your analysis in the following JSON format:
{{
    "relevance_score": <float 0.0-1.0>,
    "rationale": "<2-3 sentence explanation of relevance>",
    "key_contributions": ["<contribution 1>", "<contribution 2>"],
    "themes": ["<theme 1>", "<theme 2>"],
    "methodology_type": "<qualitative|quantitative|mixed|theoretical|review>",
    "potential_gaps_addressed": ["<gap if any>"]
}}

Be critical but fair. A score of:
- 0.9-1.0: Directly addresses the research topic
- 0.7-0.89: Highly relevant, addresses related aspects
- 0.5-0.69: Moderately relevant, provides useful context
- 0.3-0.49: Tangentially relevant
- 0.0-0.29: Not relevant to this research topic"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse JSON from response
            response_text = response.content[0].text

            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            analysis = json.loads(response_text)

            return ToolResult.ok(
                {
                    "relevance_score": float(analysis.get("relevance_score", 0.5)),
                    "rationale": analysis.get("rationale", ""),
                    "key_contributions": analysis.get("key_contributions", []),
                    "themes": analysis.get("themes", []),
                    "methodology_type": analysis.get("methodology_type", "unknown"),
                    "potential_gaps_addressed": analysis.get(
                        "potential_gaps_addressed", []
                    ),
                },
                paper_id=paper.id,
            )

        except json.JSONDecodeError as e:
            return ToolResult.fail(f"Failed to parse LLM response: {e}")
        except anthropic.APIError as e:
            return ToolResult.fail(f"Claude API error: {e}")
        except Exception as e:
            return ToolResult.fail(f"Relevance analysis failed: {e}")

    async def batch_analyze(
        self,
        papers: list[Paper],
        research_topic: str,
        criteria: Optional[list[str]] = None,
    ) -> list[ToolResult[dict]]:
        """Analyze multiple papers (sequential to respect rate limits)."""
        import asyncio

        results = []
        for paper in papers:
            result = await self.execute(paper, research_topic, criteria)
            results.append(result)
            await asyncio.sleep(config.agent.api_delay_seconds)

        return results


# Convenience function
async def analyze_paper_relevance(
    paper: Paper,
    research_topic: str,
    criteria: Optional[list[str]] = None,
) -> ToolResult[dict]:
    """Convenience function to analyze paper relevance."""
    analyzer = RelevanceAnalyzer()
    return await analyzer.execute(paper, research_topic, criteria)
