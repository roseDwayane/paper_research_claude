"""
Critic Sub-Agent - Evaluates quality, identifies gaps, ranks relevance.
"""

import asyncio
from typing import Optional
from dataclasses import dataclass

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from src.schemas.paper import Paper
from src.schemas.handoff_payload import Gap
from src.tools.analysis import RelevanceAnalyzer, GapDetector
from src.storage.database import Database
from src.config import config as app_config


console = Console()


@dataclass
class CriticConfig:
    """Configuration for critic operations."""

    min_relevance_score: float = 0.5
    target_papers: int = 25
    target_gaps: int = 3
    batch_size: int = 5  # Papers to analyze concurrently


class CriticAgent:
    """
    Critic Sub-Agent.

    Responsible for:
    - Evaluating paper quality and relevance
    - Identifying research gaps
    - Selecting final paper set
    """

    def __init__(self, db: Database):
        self.db = db
        self.relevance_analyzer = RelevanceAnalyzer()
        self.gap_detector = GapDetector()

    async def analyze_papers(
        self,
        session_id: str,
        papers: list[Paper],
        research_topic: str,
        config: Optional[CriticConfig] = None,
    ) -> list[Paper]:
        """
        Analyze paper relevance and rank them.

        Args:
            session_id: Research session ID
            papers: Papers to analyze
            research_topic: Research topic for relevance scoring
            config: Critic configuration

        Returns:
            Papers with relevance scores, sorted by relevance
        """
        config = config or CriticConfig()

        console.print(f"\n[bold yellow]Critic Agent[/bold yellow]: Analyzing {len(papers)} papers...")

        analyzed_papers = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing papers...", total=len(papers))

            # Process in batches to avoid rate limits
            for i in range(0, len(papers), config.batch_size):
                batch = papers[i : i + config.batch_size]

                for paper in batch:
                    result = await self.relevance_analyzer.execute(
                        paper=paper,
                        research_topic=research_topic,
                    )

                    if result.success and result.data:
                        # Update paper with analysis
                        paper.relevance_score = result.data["relevance_score"]
                        paper.relevance_rationale = result.data["rationale"]
                        paper.themes = result.data.get("themes", [])
                        paper.key_contributions = result.data.get("key_contributions", [])

                        # Update in database
                        await self.db.update_paper_analysis(
                            paper_id=paper.id,
                            relevance_score=paper.relevance_score,
                            relevance_rationale=paper.relevance_rationale,
                            themes=paper.themes,
                            key_contributions=paper.key_contributions,
                        )

                    analyzed_papers.append(paper)
                    progress.update(task, advance=1)

                # Rate limiting between batches
                await asyncio.sleep(app_config.agent.api_delay_seconds)

        # Sort by relevance score
        analyzed_papers.sort(
            key=lambda p: p.relevance_score or 0,
            reverse=True,
        )

        # Log action
        high_relevance = sum(
            1 for p in analyzed_papers
            if p.relevance_score and p.relevance_score >= config.min_relevance_score
        )

        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="CriticAgent",
            action="analyze_papers",
            input_summary=f"Analyzed {len(papers)} papers",
            output_summary=f"{high_relevance} papers above {config.min_relevance_score} threshold",
        )

        return analyzed_papers

    async def select_papers(
        self,
        session_id: str,
        papers: list[Paper],
        config: Optional[CriticConfig] = None,
    ) -> list[Paper]:
        """
        Select top papers for the final manifest.

        Args:
            session_id: Research session ID
            papers: Analyzed papers (should have relevance scores)
            config: Critic configuration

        Returns:
            Selected papers
        """
        config = config or CriticConfig()

        console.print(f"\n[bold yellow]Critic Agent[/bold yellow]: Selecting top {config.target_papers} papers...")

        # Filter and select
        eligible = [
            p for p in papers
            if p.relevance_score and p.relevance_score >= config.min_relevance_score
        ]

        selected = eligible[: config.target_papers]

        # Mark as selected in database
        for paper in selected:
            paper.is_selected = True
            paper.selection_reason = f"Relevance score: {paper.relevance_score:.2f}"
            await self.db.select_paper(
                paper_id=paper.id,
                selected=True,
                reason=paper.selection_reason,
            )

        # Display selection table
        self._display_selection(selected)

        # Log action
        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="CriticAgent",
            action="select_papers",
            input_summary=f"From {len(papers)} analyzed papers",
            output_summary=f"Selected {len(selected)} papers",
        )

        return selected

    def _display_selection(self, papers: list[Paper]) -> None:
        """Display selected papers in a table."""
        table = Table(title="Selected Papers for Manifest")
        table.add_column("#", style="dim")
        table.add_column("Title", max_width=50)
        table.add_column("Year", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Themes", max_width=30)

        for i, paper in enumerate(papers[:15], 1):  # Show top 15
            table.add_row(
                str(i),
                paper.title[:47] + "..." if len(paper.title) > 50 else paper.title,
                str(paper.year or "?"),
                f"{paper.relevance_score:.2f}" if paper.relevance_score else "?",
                ", ".join(paper.themes[:3]) if paper.themes else "-",
            )

        if len(papers) > 15:
            table.add_row("...", f"({len(papers) - 15} more papers)", "", "", "")

        console.print(table)

    async def detect_gaps(
        self,
        session_id: str,
        papers: list[Paper],
        research_topic: str,
        config: Optional[CriticConfig] = None,
    ) -> list[Gap]:
        """
        Identify research gaps from the paper corpus.

        Args:
            session_id: Research session ID
            papers: Papers to analyze for gaps
            research_topic: Research topic context
            config: Critic configuration

        Returns:
            List of identified gaps
        """
        config = config or CriticConfig()

        console.print(f"\n[bold yellow]Critic Agent[/bold yellow]: Detecting research gaps...")

        # Use only selected/high-relevance papers for gap detection
        relevant_papers = [
            p for p in papers
            if p.is_selected or (p.relevance_score and p.relevance_score >= 0.6)
        ]

        result = await self.gap_detector.execute(
            papers=relevant_papers,
            domain_context=research_topic,
            target_gaps=config.target_gaps,
        )

        if not result.success:
            console.print(f"[red]Gap detection failed: {result.error}[/red]")
            return []

        gaps = result.data or []

        # Save gaps to database
        for gap in gaps:
            await self.db.save_gap(session_id, gap)

        # Display gaps
        self._display_gaps(gaps)

        # Log action
        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="CriticAgent",
            action="detect_gaps",
            input_summary=f"Analyzed {len(relevant_papers)} papers",
            output_summary=f"Identified {len(gaps)} research gaps",
        )

        return gaps

    def _display_gaps(self, gaps: list[Gap]) -> None:
        """Display identified gaps."""
        table = Table(title="Identified Research Gaps")
        table.add_column("ID", style="bold")
        table.add_column("Title", max_width=40)
        table.add_column("Severity", justify="center")
        table.add_column("Novelty", justify="center")
        table.add_column("Evidence Papers")

        for gap in gaps:
            severity_color = {
                "critical": "red",
                "moderate": "yellow",
                "minor": "green",
            }.get(gap.severity.value, "white")

            table.add_row(
                gap.gap_id,
                gap.title,
                f"[{severity_color}]{gap.severity.value}[/{severity_color}]",
                gap.novelty_potential.value,
                str(len(gap.evidence_papers)),
            )

        console.print(table)

        for gap in gaps:
            console.print(f"\n[bold]{gap.gap_id}[/bold]: {gap.description}")
