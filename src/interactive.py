"""
Interactive Research Agent - Search-only mode for use with Claude Code.

This script runs the search phase automatically, then exports results
for interactive analysis in Claude Code.
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

load_dotenv()

console = Console()


async def run_search(
    topic: str,
    queries: list[str],
    year_from: int | None = None,
    year_to: int | None = None,
    papers_per_source: int = 50,
    output_dir: Path | None = None,
) -> dict:
    """
    Run search phase only (no LLM calls).

    Returns papers ready for interactive analysis.
    """
    from src.storage.database import Database
    from src.agents.searcher import SearcherAgent, SearchConfig
    from src.tools.search import deduplicate_papers

    # Setup
    output_dir = output_dir or Path("./data/interactive")
    output_dir.mkdir(parents=True, exist_ok=True)

    db = Database(output_dir / "research.db")
    await db.connect()

    session_id = await db.create_session(topic)

    console.print(Panel(
        f"[bold]Research Topic:[/bold] {topic}\n"
        f"[bold]Session ID:[/bold] {session_id}",
        title="[blue]Interactive Search Mode[/blue]",
        border_style="blue",
    ))

    # Configure search
    config = SearchConfig(
        year_from=year_from,
        year_to=year_to,
        papers_per_source=papers_per_source,
        use_google_scholar=False,  # Requires API key
    )

    searcher = SearcherAgent(db)

    # Run searches
    all_papers = []
    for query in queries:
        papers = await searcher.search(session_id, query, config)
        all_papers.extend(papers)

    # Deduplicate
    unique_papers = deduplicate_papers(all_papers)

    # Export for interactive analysis
    export_data = {
        "metadata": {
            "topic": topic,
            "session_id": session_id,
            "searched_at": datetime.utcnow().isoformat(),
            "queries": queries,
            "total_papers": len(unique_papers),
        },
        "papers": []
    }

    for paper in unique_papers:
        export_data["papers"].append({
            "id": paper.id,
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "year": paper.year,
            "abstract": paper.abstract,
            "doi": paper.doi,
            "source": paper.source_api.value,
            "citations": paper.citation_count,
            "journal": paper.journal,
        })

    # Save JSON export
    json_path = output_dir / f"{session_id}_papers.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    # Save readable markdown
    md_path = output_dir / f"{session_id}_papers.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Research Papers: {topic}\n\n")
        f.write(f"**Session:** {session_id}\n")
        f.write(f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}\n")
        f.write(f"**Total Papers:** {len(unique_papers)}\n\n")
        f.write("---\n\n")

        for i, paper in enumerate(unique_papers, 1):
            f.write(f"## {i}. {paper.title}\n\n")
            f.write(f"- **Authors:** {', '.join(a.name for a in paper.authors[:5])}")
            if len(paper.authors) > 5:
                f.write(f" et al.")
            f.write("\n")
            f.write(f"- **Year:** {paper.year or 'Unknown'}\n")
            f.write(f"- **DOI:** {paper.doi or 'N/A'}\n")
            f.write(f"- **Source:** {paper.source_api.value}\n")
            f.write(f"- **Citations:** {paper.citation_count or 'N/A'}\n")
            f.write(f"- **Journal:** {paper.journal or 'N/A'}\n")
            f.write(f"\n**Abstract:**\n{paper.abstract or 'No abstract available'}\n\n")
            f.write("---\n\n")

    # Save compact version for Claude Code (limited context)
    compact_path = output_dir / f"{session_id}_compact.md"
    with open(compact_path, "w", encoding="utf-8") as f:
        f.write(f"# Papers for Analysis: {topic}\n\n")
        f.write(f"Total: {len(unique_papers)} papers\n\n")

        for i, paper in enumerate(unique_papers, 1):
            # Truncate abstract for compact view
            abstract = paper.abstract or "No abstract"
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."

            f.write(f"### P{i}: {paper.title[:80]}{'...' if len(paper.title) > 80 else ''}\n")
            f.write(f"**{paper.year or '?'}** | {paper.source_api.value} | Citations: {paper.citation_count or '?'}\n")
            f.write(f"{abstract}\n\n")

    await db.close()

    # Display summary
    console.print(f"\n[green]Search complete![/green]\n")

    table = Table(title="Output Files")
    table.add_column("File", style="bold")
    table.add_column("Purpose")
    table.add_row(str(json_path), "Full data (JSON)")
    table.add_row(str(md_path), "Readable format (Markdown)")
    table.add_row(str(compact_path), "Compact for Claude Code")
    console.print(table)

    console.print(Panel(
        f"[bold]Next Step:[/bold]\n\n"
        f"1. Open [cyan]{compact_path.name}[/cyan] in Claude Code\n"
        f"2. Ask Claude to analyze relevance to your topic\n"
        f"3. Ask Claude to identify research gaps\n"
        f"4. Ask Claude to generate hypothesis\n\n"
        f"[dim]Or share the file contents directly in chat[/dim]",
        title="[yellow]Interactive Analysis[/yellow]",
        border_style="yellow",
    ))

    return export_data


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Research Agent - Search Mode",
    )

    parser.add_argument("topic", help="Research topic")
    parser.add_argument("--queries", "-q", nargs="+", help="Search queries")
    parser.add_argument("--year-from", type=int, help="Start year")
    parser.add_argument("--year-to", type=int, help="End year")
    parser.add_argument("--papers-per-source", type=int, default=30)
    parser.add_argument("--output", "-o", type=Path, help="Output directory")

    args = parser.parse_args()

    queries = args.queries or [args.topic]

    asyncio.run(run_search(
        topic=args.topic,
        queries=queries,
        year_from=args.year_from,
        year_to=args.year_to,
        papers_per_source=args.papers_per_source,
        output_dir=args.output,
    ))


if __name__ == "__main__":
    main()
