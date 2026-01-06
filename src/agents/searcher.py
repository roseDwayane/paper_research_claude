"""
Searcher Sub-Agent - Discovers candidate papers from multiple sources.
"""

import asyncio
from typing import Optional
from dataclasses import dataclass

from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

from src.schemas.paper import Paper
from src.tools.search import (
    OpenAlexSearchTool,
    PubMedSearchTool,
    GoogleScholarSearchTool,
    deduplicate_papers,
)
from src.storage.database import Database


console = Console()


@dataclass
class SearchConfig:
    """Configuration for search operations."""

    year_from: Optional[int] = None
    year_to: Optional[int] = None
    min_citations: Optional[int] = None
    papers_per_source: int = 50
    use_google_scholar: bool = False  # Requires API key


class SearcherAgent:
    """
    Searcher Sub-Agent.

    Responsible for discovering candidate papers from multiple sources.
    No judgment - just retrieval.
    """

    def __init__(self, db: Database):
        self.db = db
        self.openalex = OpenAlexSearchTool()
        self.pubmed = PubMedSearchTool()
        self.google_scholar = GoogleScholarSearchTool()

    async def search(
        self,
        session_id: str,
        query: str,
        config: Optional[SearchConfig] = None,
    ) -> list[Paper]:
        """
        Search for papers across all configured sources.

        Args:
            session_id: Research session ID
            query: Search query
            config: Search configuration

        Returns:
            List of deduplicated papers
        """
        config = config or SearchConfig()
        all_papers: list[Paper] = []

        console.print(f"\n[bold blue]Searcher Agent[/bold blue]: Starting search for '{query}'")

        # Search OpenAlex
        console.print("  [dim]Searching OpenAlex...[/dim]")
        openalex_result = await self.openalex.execute(
            query=query,
            year_from=config.year_from,
            year_to=config.year_to,
            cited_by_count_min=config.min_citations,
            limit=config.papers_per_source,
        )
        if openalex_result.success and openalex_result.data:
            all_papers.extend(openalex_result.data)
            console.print(f"  [green]OpenAlex: {len(openalex_result.data)} papers[/green]")
        else:
            console.print(f"  [red]OpenAlex: {openalex_result.error}[/red]")

        # Search PubMed
        console.print("  [dim]Searching PubMed...[/dim]")
        date_range = None
        if config.year_from and config.year_to:
            date_range = f"{config.year_from}:{config.year_to}"
        elif config.year_from:
            date_range = f"{config.year_from}:2099"

        pubmed_result = await self.pubmed.execute(
            query=query,
            date_range=date_range,
            limit=config.papers_per_source,
        )
        if pubmed_result.success and pubmed_result.data:
            all_papers.extend(pubmed_result.data)
            console.print(f"  [green]PubMed: {len(pubmed_result.data)} papers[/green]")
        else:
            console.print(f"  [yellow]PubMed: {pubmed_result.error or 'No results'}[/yellow]")

        # Search Google Scholar (if enabled and API key available)
        if config.use_google_scholar:
            console.print("  [dim]Searching Google Scholar...[/dim]")
            scholar_result = await self.google_scholar.execute(
                query=query,
                year_from=config.year_from,
                limit=min(config.papers_per_source, 20),
            )
            if scholar_result.success and scholar_result.data:
                all_papers.extend(scholar_result.data)
                console.print(f"  [green]Google Scholar: {len(scholar_result.data)} papers[/green]")
            else:
                console.print(f"  [yellow]Google Scholar: {scholar_result.error or 'Skipped'}[/yellow]")

        # Deduplicate papers
        console.print(f"\n[dim]Raw papers collected: {len(all_papers)}[/dim]")
        unique_papers = deduplicate_papers(all_papers)
        console.print(f"[dim]After deduplication: {len(unique_papers)}[/dim]")

        # Save to database
        await self.db.save_papers(session_id, unique_papers)

        # Log action
        await self.db.log_agent_action(
            session_id=session_id,
            agent_name="SearcherAgent",
            action="search",
            input_summary=f"Query: {query}",
            output_summary=f"Found {len(unique_papers)} unique papers",
        )

        console.print(f"[bold green]Searcher Agent[/bold green]: Found {len(unique_papers)} unique papers\n")

        return unique_papers

    async def expand_search(
        self,
        session_id: str,
        additional_queries: list[str],
        config: Optional[SearchConfig] = None,
    ) -> list[Paper]:
        """
        Expand search with additional queries.

        Args:
            session_id: Research session ID
            additional_queries: Additional search queries
            config: Search configuration

        Returns:
            All papers (existing + new)
        """
        config = config or SearchConfig()
        new_papers: list[Paper] = []

        for query in additional_queries:
            papers = await self.search(session_id, query, config)
            new_papers.extend(papers)

        # Get all papers from DB
        all_papers = await self.db.get_papers(session_id)

        return all_papers
