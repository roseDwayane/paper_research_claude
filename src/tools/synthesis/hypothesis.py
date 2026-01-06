"""
Hypothesis generation tool using Claude.
"""

import json
from typing import Optional

import anthropic

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.handoff_payload import (
    Gap,
    KnowledgeGraph,
    HypothesisSpecification,
    ExpectedSignificance,
)


class HypothesisGenerator(BaseTool):
    """Generate research hypothesis based on gaps and knowledge."""

    name = "generate_hypothesis"
    description = "Formulate research hypothesis based on identified gaps and domain knowledge."

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.api.anthropic_api_key)
        self.model = config.api.claude_model

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "gaps": {
                    "type": "array",
                    "description": "Identified research gaps",
                },
                "knowledge_graph": {
                    "type": "object",
                    "description": "Domain knowledge graph",
                },
                "research_topic": {
                    "type": "string",
                    "description": "Original research topic",
                },
            },
            "required": ["gaps", "knowledge_graph", "research_topic"],
        }

    async def execute(
        self,
        gaps: list[Gap],
        knowledge_graph: KnowledgeGraph,
        research_topic: str,
    ) -> ToolResult[HypothesisSpecification]:
        """
        Generate research hypothesis.

        Args:
            gaps: Identified research gaps
            knowledge_graph: Domain knowledge
            research_topic: Research topic

        Returns:
            ToolResult with HypothesisSpecification
        """
        if not config.api.anthropic_api_key:
            return ToolResult.fail("Anthropic API key not configured")

        if not gaps:
            return ToolResult.fail("No gaps provided for hypothesis generation")

        try:
            # Prepare gaps summary
            gaps_text = "\n".join(
                f"- {gap.gap_id}: {gap.title} (Severity: {gap.severity.value}, Novelty: {gap.novelty_potential.value})\n  {gap.description}"
                for gap in gaps
            )

            # Prepare knowledge context
            concepts_text = "\n".join(
                f"- {c.term}: {c.definition}"
                for c in knowledge_graph.core_concepts[:15]
            )

            methodologies = ", ".join(knowledge_graph.methodological_paradigms[:5])

            prompt = f"""You are a research methodology expert helping to formulate a strong research hypothesis.

Research Topic: {research_topic}

Identified Research Gaps:
{gaps_text}

Key Domain Concepts:
{concepts_text}

Common Methodologies: {methodologies}

Field Boundaries: {', '.join(knowledge_graph.field_boundaries[:3])}

Based on the gaps and domain knowledge, formulate a clear, testable research hypothesis.

Return your analysis in this JSON format:
{{
    "problem_statement": "<Clear, specific problem statement (2-3 sentences)>",
    "research_questions": [
        "RQ1: <First research question>",
        "RQ2: <Second research question>",
        "RQ3: <Optional third question>"
    ],
    "hypothesis": "<Main hypothesis - clear, falsifiable, specific>",
    "expected_significance": {{
        "theoretical": "<How this contributes to theory (2-3 sentences)>",
        "practical": "<Real-world implications (2-3 sentences)>"
    }},
    "scope_in": [
        "<What is included in this research>",
        "<Another inclusion>"
    ],
    "scope_out": [
        "<What is explicitly excluded>",
        "<Another exclusion>"
    ],
    "suggested_methodology": "<Brief methodology suggestion>",
    "primary_gap_addressed": "<gap_id of the main gap being addressed>"
}}

Guidelines for strong hypothesis:
1. Directly addresses at least one identified gap
2. Is testable/falsifiable
3. Builds on existing knowledge
4. Has clear theoretical and practical significance
5. Is appropriately scoped"""

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

            # Build HypothesisSpecification
            sig_data = analysis.get("expected_significance", {})
            significance = ExpectedSignificance(
                theoretical=sig_data.get("theoretical", ""),
                practical=sig_data.get("practical", ""),
            )

            # Combine scope in/out for scope_boundaries
            scope_in = [f"IN: {s}" for s in analysis.get("scope_in", [])]
            scope_out = [f"OUT: {s}" for s in analysis.get("scope_out", [])]

            hypothesis_spec = HypothesisSpecification(
                problem_statement=analysis.get("problem_statement", ""),
                research_questions=analysis.get("research_questions", []),
                hypothesis=analysis.get("hypothesis", ""),
                expected_significance=significance,
                scope_boundaries=scope_in + scope_out,
            )

            return ToolResult.ok(
                hypothesis_spec,
                suggested_methodology=analysis.get("suggested_methodology", ""),
                primary_gap_addressed=analysis.get("primary_gap_addressed", ""),
            )

        except json.JSONDecodeError as e:
            return ToolResult.fail(f"Failed to parse hypothesis: {e}")
        except anthropic.APIError as e:
            return ToolResult.fail(f"Claude API error: {e}")
        except Exception as e:
            return ToolResult.fail(f"Hypothesis generation failed: {e}")


# Convenience function
async def generate_hypothesis(
    gaps: list[Gap],
    knowledge_graph: KnowledgeGraph,
    research_topic: str,
) -> ToolResult[HypothesisSpecification]:
    """Convenience function to generate hypothesis."""
    generator = HypothesisGenerator()
    return await generator.execute(gaps, knowledge_graph, research_topic)
