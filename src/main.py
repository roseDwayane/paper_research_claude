"""
Research Agent - Main entry point.

This is the CLI interface for running the autonomous research agent.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

console = Console()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Research Agent - Phase 1 (Claude PI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with a research topic
  python -m src.main "machine learning in healthcare diagnostics"

  # Run with custom search queries
  python -m src.main "AI diagnostics" --queries "deep learning medical imaging" "neural networks healthcare"

  # Run with year filter
  python -m src.main "transformer models NLP" --year-from 2020

  # Export to specific directory
  python -m src.main "quantum computing algorithms" --output ./my_research

Environment Variables:
  ANTHROPIC_API_KEY    - Required for Claude API access
  OPENALEX_EMAIL       - Recommended for OpenAlex API (polite pool)
  NCBI_API_KEY         - Optional for faster PubMed access
  NCBI_EMAIL           - Recommended for PubMed API
  SERPAPI_KEY          - Required for Google Scholar search
        """,
    )

    parser.add_argument(
        "topic",
        type=str,
        help="Research topic or question",
    )

    parser.add_argument(
        "--queries",
        "-q",
        type=str,
        nargs="+",
        help="Additional search queries (default: uses topic)",
    )

    parser.add_argument(
        "--year-from",
        type=int,
        help="Filter papers from this year onwards",
    )

    parser.add_argument(
        "--year-to",
        type=int,
        help="Filter papers up to this year",
    )

    parser.add_argument(
        "--min-citations",
        type=int,
        help="Minimum citation count filter",
    )

    parser.add_argument(
        "--papers-per-source",
        type=int,
        default=50,
        help="Maximum papers to fetch per source (default: 50)",
    )

    parser.add_argument(
        "--target-papers",
        type=int,
        default=25,
        help="Target number of papers for final selection (default: 25)",
    )

    parser.add_argument(
        "--min-relevance",
        type=float,
        default=0.5,
        help="Minimum relevance score for selection (default: 0.5)",
    )

    parser.add_argument(
        "--target-gaps",
        type=int,
        default=3,
        help="Number of research gaps to identify (default: 3)",
    )

    parser.add_argument(
        "--target-journals",
        type=int,
        default=5,
        help="Number of target journals to recommend (default: 5)",
    )

    parser.add_argument(
        "--use-google-scholar",
        action="store_true",
        help="Include Google Scholar search (requires SERPAPI_KEY)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output directory for results",
    )

    parser.add_argument(
        "--task-type",
        choices=["literature_review", "systematic_review", "introduction_writing"],
        default="introduction_writing",
        help="Task type for Gemini (default: introduction_writing)",
    )

    parser.add_argument(
        "--citation-style",
        choices=["APA7", "MLA9", "Chicago", "IEEE"],
        default="APA7",
        help="Citation style (default: APA7)",
    )

    parser.add_argument(
        "--launch-gemini",
        action="store_true",
        help="Prepare Gemini task after Phase 1 completion",
    )

    return parser.parse_args()


async def run_agent(args: argparse.Namespace) -> int:
    """Run the research agent."""
    from src.agents.orchestrator import PIOrchestrator, OrchestratorConfig
    from src.agents.searcher import SearchConfig
    from src.agents.critic import CriticConfig
    from src.agents.synthesizer import SynthesizerConfig
    from src.schemas.handoff_payload import TaskType, CitationStyle
    from src.tools.mcp import launch_gemini
    from src.config import config as app_config

    # Validate API key
    if not app_config.api.anthropic_api_key:
        console.print(
            "[bold red]Error:[/bold red] ANTHROPIC_API_KEY environment variable not set.\n"
            "Set it with: export ANTHROPIC_API_KEY=your_key_here",
            style="red",
        )
        return 1

    # Build configuration
    search_config = SearchConfig(
        year_from=args.year_from,
        year_to=args.year_to,
        min_citations=args.min_citations,
        papers_per_source=args.papers_per_source,
        use_google_scholar=args.use_google_scholar,
    )

    critic_config = CriticConfig(
        min_relevance_score=args.min_relevance,
        target_papers=args.target_papers,
        target_gaps=args.target_gaps,
    )

    synthesizer_config = SynthesizerConfig(
        target_journals=args.target_journals,
    )

    task_type = TaskType(args.task_type)
    citation_style = CitationStyle(args.citation_style)

    orchestrator_config = OrchestratorConfig(
        search_config=search_config,
        critic_config=critic_config,
        synthesizer_config=synthesizer_config,
        output_dir=args.output,
        task_type=task_type,
        citation_style=citation_style,
    )

    # Run orchestrator
    orchestrator = PIOrchestrator(orchestrator_config)

    try:
        search_queries = args.queries or [args.topic]

        payload = await orchestrator.run(
            research_topic=args.topic,
            search_queries=search_queries,
        )

        # Optionally prepare Gemini task
        if args.launch_gemini:
            console.print("\n[bold blue]Preparing Gemini task...[/bold blue]")
            result = await launch_gemini(
                handoff_payload=payload,
                task_type=task_type,
                output_dir=orchestrator_config.output_dir,
            )

            if result.success:
                console.print(
                    Panel(
                        f"Task ID: {result.data.task_id}\n"
                        f"Prompt file: {result.metadata.get('prompt_file', 'N/A')}\n"
                        f"Status: {result.data.status}",
                        title="[bold]Gemini Task Prepared[/bold]",
                        border_style="blue",
                    )
                )
            else:
                console.print(f"[red]Failed to prepare Gemini task: {result.error}[/red]")

        return 0

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        return 130

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc(), style="dim")
        return 1

    finally:
        await orchestrator.close()


def main() -> int:
    """Main entry point."""
    console.print(
        Panel(
            "[bold]Autonomous Research Agent[/bold]\n"
            "Phase 1: Claude Principal Investigator",
            border_style="blue",
        )
    )

    args = parse_args()

    return asyncio.run(run_agent(args))


if __name__ == "__main__":
    sys.exit(main())
