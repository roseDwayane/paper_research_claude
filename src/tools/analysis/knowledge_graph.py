"""
Knowledge graph builder using Claude.
"""

import json
from typing import Optional

import anthropic

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.paper import Paper
from src.schemas.handoff_payload import KnowledgeGraph, Concept


class KnowledgeGraphBuilder(BaseTool):
    """Build a domain knowledge graph from paper corpus."""

    name = "build_knowledge_graph"
    description = "Extract concepts and relationships from paper corpus to build a knowledge graph."

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.api.anthropic_api_key)
        self.model = config.api.claude_model

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "papers": {
                    "type": "array",
                    "description": "List of papers to extract knowledge from",
                },
                "research_topic": {
                    "type": "string",
                    "description": "Research topic for context",
                },
                "max_concepts": {
                    "type": "integer",
                    "description": "Maximum concepts to extract (default: 30)",
                },
            },
            "required": ["papers", "research_topic"],
        }

    async def execute(
        self,
        papers: list[Paper],
        research_topic: str,
        max_concepts: int = 30,
    ) -> ToolResult[KnowledgeGraph]:
        """
        Build knowledge graph from paper corpus.

        Args:
            papers: Papers to extract knowledge from
            research_topic: Research topic context
            max_concepts: Max concepts to extract

        Returns:
            ToolResult with KnowledgeGraph
        """
        if not config.api.anthropic_api_key:
            return ToolResult.fail("Anthropic API key not configured")

        if not papers:
            return ToolResult.fail("No papers provided for knowledge extraction")

        try:
            # Prepare paper content for analysis
            paper_content = []
            for i, paper in enumerate(papers[:25]):  # Limit for context window
                content = f"""Paper {i+1}:
Title: {paper.title}
Abstract: {(paper.abstract or 'No abstract')[:400]}
Themes: {', '.join(paper.themes) if paper.themes else 'N/A'}"""
                paper_content.append(content)

            papers_text = "\n\n".join(paper_content)

            prompt = f"""You are a domain expert building a knowledge graph for academic research.

Research Topic: {research_topic}

Analyze these {len(papers)} papers and extract the core concepts, their definitions, and relationships.

Papers:
{papers_text}

Extract up to {max_concepts} key concepts that form the conceptual foundation of this research area.

Return your analysis in this JSON format:
{{
    "concepts": [
        {{
            "term": "<concept name>",
            "definition": "<concise 1-2 sentence definition>",
            "relationships": ["<related term 1>", "<related term 2>"]
        }}
    ],
    "field_boundaries": [
        "<what defines this field/area>",
        "<what's included>",
        "<what's excluded>"
    ],
    "methodological_paradigms": [
        "<common methodology 1>",
        "<common methodology 2>"
    ],
    "theoretical_foundations": [
        "<key theory 1>",
        "<key theory 2>"
    ]
}}

Focus on:
1. Core technical concepts specific to this domain
2. Key methodologies and approaches
3. Important theoretical frameworks
4. Domain-specific terminology

Concepts should be interconnected - show relationships between them."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
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

            # Build KnowledgeGraph
            concepts = [
                Concept(
                    term=c.get("term", ""),
                    definition=c.get("definition", ""),
                    relationships=c.get("relationships", []),
                )
                for c in analysis.get("concepts", [])
            ]

            knowledge_graph = KnowledgeGraph(
                core_concepts=concepts,
                field_boundaries=analysis.get("field_boundaries", []),
                methodological_paradigms=analysis.get("methodological_paradigms", []),
            )

            return ToolResult.ok(
                knowledge_graph,
                concept_count=len(concepts),
                theoretical_foundations=analysis.get("theoretical_foundations", []),
            )

        except json.JSONDecodeError as e:
            return ToolResult.fail(f"Failed to parse knowledge graph: {e}")
        except anthropic.APIError as e:
            return ToolResult.fail(f"Claude API error: {e}")
        except Exception as e:
            return ToolResult.fail(f"Knowledge graph building failed: {e}")


# Convenience function
async def build_knowledge_graph(
    papers: list[Paper],
    research_topic: str,
    max_concepts: int = 30,
) -> ToolResult[KnowledgeGraph]:
    """Convenience function to build knowledge graph."""
    builder = KnowledgeGraphBuilder()
    return await builder.execute(papers, research_topic, max_concepts)
