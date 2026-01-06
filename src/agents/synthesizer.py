"""
Synthesizer Sub-Agent - Builds knowledge graph, formulates hypothesis, selects journals.
"""

from typing import Optional
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from src.schemas.paper import Paper
from src.schemas.handoff_payload import (
    Gap,
    KnowledgeGraph,
    HypothesisSpecification,
    TargetJournal,
)
from src.tools.analysis import KnowledgeGraphBuilder
from src.tools.synthesis import HypothesisGenerator, JournalMatcher
from src.storage.database import Database


console = Console()


@dataclass
class SynthesizerConfig:
    """Configuration for synthesizer operations."""

    max_concepts: int = 30
    target_journals: int = 5
    preferred_if_min: Optional[float] = None
    preferred_if_max: Optional[float] = None


class SynthesizerAgent:
    """
    Synthesizer Sub-Agent.

    Responsible for:
    - Building domain knowledge graph
    - Formulating research hypothesis
    - Selecting target journals
    """

    def __init__(self, db: Database):
        self.db = db
        self.kg_builder = KnowledgeGraphBuilder()
        self.hypothesis_gen = HypothesisGenerator()
        self.journal_matcher = JournalMatcher()

    async def build_knowledge_graph(
        self,
        session_id: str,
        papers: list[Paper],
        research_topic: str,
        config: Optional[SynthesizerConfig] = None,
    ) -> Optional[KnowledgeGraph]:
        """
        Build domain knowledge graph from papers.

        Args:
            session_id: Research session ID
            papers: Papers to extract knowledge from
            research_topic: Research topic
            config: Synthesizer configuration

        Returns:
            KnowledgeGraph object
        """
        config = config or SynthesizerConfig()

        console.print(f"\n[bold magenta]Synthesizer Agent[/bold magenta]: Building knowledge graph...")

        result = await self.kg_builder.execute(
            papers=papers,
            research_topic=research_topic,
            max_concepts=config.max_concepts,
        )

        if not result.success:
            console.print(f"[red]Knowledge graph building failed: {result.error}[/red]")
            return None

        knowledge_graph = result.data

        # Save concepts to database
        for concept in knowledge_graph.core_concepts:
            await self.db.save_concept(session_id, concept)

        # Display knowledge graph summary
        self._display_knowledge_graph(knowledge_graph)

        # Log action
        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="SynthesizerAgent",
            action="build_knowledge_graph",
            input_summary=f"From {len(papers)} papers",
            output_summary=f"Extracted {len(knowledge_graph.core_concepts)} concepts",
        )

        return knowledge_graph

    def _display_knowledge_graph(self, kg: KnowledgeGraph) -> None:
        """Display knowledge graph summary."""
        # Concepts table
        table = Table(title=f"Knowledge Graph ({len(kg.core_concepts)} concepts)")
        table.add_column("Concept", style="bold")
        table.add_column("Definition", max_width=50)
        table.add_column("Related To", max_width=30)

        for concept in kg.core_concepts[:10]:  # Show top 10
            table.add_row(
                concept.term,
                concept.definition[:47] + "..." if len(concept.definition) > 50 else concept.definition,
                ", ".join(concept.relationships[:3]) if concept.relationships else "-",
            )

        if len(kg.core_concepts) > 10:
            table.add_row("...", f"({len(kg.core_concepts) - 10} more)", "")

        console.print(table)

        # Field info
        if kg.field_boundaries:
            console.print("\n[bold]Field Boundaries:[/bold]")
            for boundary in kg.field_boundaries:
                console.print(f"  - {boundary}")

        if kg.methodological_paradigms:
            console.print("\n[bold]Methodological Paradigms:[/bold]")
            for paradigm in kg.methodological_paradigms:
                console.print(f"  - {paradigm}")

    async def generate_hypothesis(
        self,
        session_id: str,
        gaps: list[Gap],
        knowledge_graph: KnowledgeGraph,
        research_topic: str,
    ) -> Optional[HypothesisSpecification]:
        """
        Generate research hypothesis based on gaps and knowledge.

        Args:
            session_id: Research session ID
            gaps: Identified research gaps
            knowledge_graph: Domain knowledge
            research_topic: Research topic

        Returns:
            HypothesisSpecification object
        """
        console.print(f"\n[bold magenta]Synthesizer Agent[/bold magenta]: Generating hypothesis...")

        result = await self.hypothesis_gen.execute(
            gaps=gaps,
            knowledge_graph=knowledge_graph,
            research_topic=research_topic,
        )

        if not result.success:
            console.print(f"[red]Hypothesis generation failed: {result.error}[/red]")
            return None

        hypothesis = result.data

        # Display hypothesis
        self._display_hypothesis(hypothesis)

        # Log action
        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="SynthesizerAgent",
            action="generate_hypothesis",
            input_summary=f"From {len(gaps)} gaps",
            output_summary="Generated hypothesis specification",
        )

        return hypothesis

    def _display_hypothesis(self, hypothesis: HypothesisSpecification) -> None:
        """Display hypothesis specification."""
        md_content = f"""
## Problem Statement
{hypothesis.problem_statement}

## Research Questions
{"".join(f"- {rq}" + chr(10) for rq in hypothesis.research_questions)}

## Hypothesis
{hypothesis.hypothesis}

## Expected Significance

**Theoretical:** {hypothesis.expected_significance.theoretical}

**Practical:** {hypothesis.expected_significance.practical}

## Scope
{"".join(f"- {s}" + chr(10) for s in hypothesis.scope_boundaries)}
"""
        panel = Panel(
            Markdown(md_content),
            title="[bold]Research Hypothesis[/bold]",
            border_style="magenta",
        )
        console.print(panel)

    async def match_journals(
        self,
        session_id: str,
        research_topic: str,
        hypothesis: Optional[HypothesisSpecification] = None,
        methodology: Optional[str] = None,
        config: Optional[SynthesizerConfig] = None,
    ) -> list[TargetJournal]:
        """
        Match research to target journals.

        Args:
            session_id: Research session ID
            research_topic: Research topic
            hypothesis: Optional hypothesis spec
            methodology: Research methodology
            config: Synthesizer configuration

        Returns:
            List of target journals
        """
        config = config or SynthesizerConfig()

        console.print(f"\n[bold magenta]Synthesizer Agent[/bold magenta]: Matching target journals...")

        if_range = None
        if config.preferred_if_min or config.preferred_if_max:
            if_range = {
                "min": config.preferred_if_min or 0,
                "max": config.preferred_if_max or 50,
            }

        result = await self.journal_matcher.execute(
            research_topic=research_topic,
            hypothesis=hypothesis,
            methodology=methodology,
            target_count=config.target_journals,
            preferred_if_range=if_range,
        )

        if not result.success:
            console.print(f"[red]Journal matching failed: {result.error}[/red]")
            return []

        journals = result.data or []

        # Save to database
        for journal in journals:
            await self.db.save_journal(session_id, journal)

        # Display journals
        self._display_journals(journals)

        # Log action
        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="SynthesizerAgent",
            action="match_journals",
            input_summary=f"Topic: {research_topic}",
            output_summary=f"Matched {len(journals)} journals",
        )

        return journals

    def _display_journals(self, journals: list[TargetJournal]) -> None:
        """Display matched journals."""
        table = Table(title="Target Journals")
        table.add_column("#", style="dim")
        table.add_column("Journal", style="bold")
        table.add_column("IF", justify="center")
        table.add_column("Review (days)", justify="center")
        table.add_column("Fit Rationale", max_width=40)

        for i, journal in enumerate(journals, 1):
            table.add_row(
                str(i),
                journal.name,
                f"{journal.impact_factor:.1f}" if journal.impact_factor else "?",
                str(journal.review_cycle_days) if journal.review_cycle_days else "?",
                journal.fit_rationale[:37] + "..." if len(journal.fit_rationale) > 40 else journal.fit_rationale,
            )

        console.print(table)
