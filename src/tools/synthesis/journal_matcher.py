"""
Journal matching tool using Claude.
"""

import json
from typing import Optional

import anthropic

from src.config import config
from src.tools.base import BaseTool, ToolResult
from src.schemas.handoff_payload import TargetJournal, HypothesisSpecification


class JournalMatcher(BaseTool):
    """Match research to appropriate target journals."""

    name = "match_target_journals"
    description = "Recommend target journals based on research profile and methodology."

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.api.anthropic_api_key)
        self.model = config.api.claude_model

    def _get_parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "research_topic": {
                    "type": "string",
                    "description": "Research topic",
                },
                "hypothesis": {
                    "type": "object",
                    "description": "Hypothesis specification",
                },
                "methodology": {
                    "type": "string",
                    "description": "Research methodology",
                },
                "target_count": {
                    "type": "integer",
                    "description": "Number of journals to recommend (default: 5)",
                },
                "preferred_if_range": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "number"},
                        "max": {"type": "number"},
                    },
                    "description": "Preferred impact factor range",
                },
            },
            "required": ["research_topic"],
        }

    async def execute(
        self,
        research_topic: str,
        hypothesis: Optional[HypothesisSpecification] = None,
        methodology: Optional[str] = None,
        target_count: int = 5,
        preferred_if_range: Optional[dict] = None,
    ) -> ToolResult[list[TargetJournal]]:
        """
        Recommend target journals.

        Args:
            research_topic: Research topic
            hypothesis: Optional hypothesis spec
            methodology: Research methodology
            target_count: Number of recommendations
            preferred_if_range: Preferred IF range

        Returns:
            ToolResult with list of TargetJournal
        """
        if not config.api.anthropic_api_key:
            return ToolResult.fail("Anthropic API key not configured")

        try:
            # Build context
            hypothesis_text = ""
            if hypothesis:
                hypothesis_text = f"""
Research Problem: {hypothesis.problem_statement}
Hypothesis: {hypothesis.hypothesis}
Theoretical Significance: {hypothesis.expected_significance.theoretical}
Practical Significance: {hypothesis.expected_significance.practical}"""

            methodology_text = f"\nMethodology: {methodology}" if methodology else ""

            if_range_text = ""
            if preferred_if_range:
                if_range_text = f"\nPreferred Impact Factor: {preferred_if_range.get('min', 0)}-{preferred_if_range.get('max', 50)}"

            prompt = f"""You are an academic publishing expert helping researchers identify appropriate target journals.

Research Topic: {research_topic}
{hypothesis_text}
{methodology_text}
{if_range_text}

Recommend {target_count} academic journals that would be appropriate for this research.

Consider:
1. Scope and aims alignment
2. Impact factor and prestige
3. Review turnaround time
4. Open access options
5. Geographic/regional focus if relevant

Return your recommendations in this JSON format:
{{
    "journals": [
        {{
            "name": "<Full journal name>",
            "publisher": "<Publisher name>",
            "impact_factor": <float or null>,
            "review_cycle_days": <integer estimate>,
            "fit_rationale": "<Why this journal fits (2-3 sentences)>",
            "style_guide_url": "<URL if known, or null>",
            "word_limit": <integer if known>,
            "open_access": "<full_oa|hybrid|subscription>",
            "rejection_rate": "<high|medium|low if known>"
        }}
    ],
    "strategy_notes": "<1-2 sentences on submission strategy>"
}}

Provide real, reputable journals. Order by fit quality (best first).
If you don't know exact values (IF, review time), provide reasonable estimates based on journal tier."""

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

            # Build TargetJournal objects
            journals = []
            for j in analysis.get("journals", []):
                journal = TargetJournal(
                    name=j.get("name", "Unknown"),
                    impact_factor=j.get("impact_factor"),
                    review_cycle_days=j.get("review_cycle_days"),
                    fit_rationale=j.get("fit_rationale", ""),
                    style_guide_url=j.get("style_guide_url"),
                    word_limit=j.get("word_limit"),
                )
                journals.append(journal)

            return ToolResult.ok(
                journals,
                strategy_notes=analysis.get("strategy_notes", ""),
            )

        except json.JSONDecodeError as e:
            return ToolResult.fail(f"Failed to parse journal recommendations: {e}")
        except anthropic.APIError as e:
            return ToolResult.fail(f"Claude API error: {e}")
        except Exception as e:
            return ToolResult.fail(f"Journal matching failed: {e}")


# Convenience function
async def match_target_journals(
    research_topic: str,
    hypothesis: Optional[HypothesisSpecification] = None,
    methodology: Optional[str] = None,
    target_count: int = 5,
    preferred_if_range: Optional[dict] = None,
) -> ToolResult[list[TargetJournal]]:
    """Convenience function to match journals."""
    matcher = JournalMatcher()
    return await matcher.execute(
        research_topic, hypothesis, methodology, target_count, preferred_if_range
    )
