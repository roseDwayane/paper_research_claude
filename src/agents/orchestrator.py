"""
PI Orchestrator - Main orchestration agent that coordinates sub-agents.
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from src.schemas.paper import Paper
from src.schemas.handoff_payload import (
    HandoffPayload,
    KnowledgeGraph,
    Gap,
    HypothesisSpecification,
    TargetJournal,
    TaskType,
    CitationStyle,
)
from src.agents.searcher import SearcherAgent, SearchConfig
from src.agents.critic import CriticAgent, CriticConfig
from src.agents.synthesizer import SynthesizerAgent, SynthesizerConfig
from src.tools.synthesis import PayloadAssembler
from src.storage.database import Database, get_db
from src.config import config as app_config


console = Console()


@dataclass
class OrchestratorConfig:
    """Configuration for the PI Orchestrator."""

    # Search settings
    search_config: SearchConfig = field(default_factory=SearchConfig)

    # Critic settings
    critic_config: CriticConfig = field(default_factory=CriticConfig)

    # Synthesizer settings
    synthesizer_config: SynthesizerConfig = field(default_factory=SynthesizerConfig)

    # Output settings
    output_dir: Optional[Path] = None
    task_type: TaskType = TaskType.INTRODUCTION_WRITING
    citation_style: CitationStyle = CitationStyle.APA7


class PIOrchestrator:
    """
    Principal Investigator Orchestrator.

    Coordinates the research workflow:
    1. Searcher Agent -> Discover papers
    2. Critic Agent -> Analyze and select papers, detect gaps
    3. Synthesizer Agent -> Build knowledge graph, generate hypothesis, match journals
    4. Assembler -> Create hand-off payload for Gemini

    This is the main entry point for Phase 1 of the research agent.
    """

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.db: Optional[Database] = None
        self.session_id: Optional[str] = None

        # Sub-agents (initialized in run)
        self.searcher: Optional[SearcherAgent] = None
        self.critic: Optional[CriticAgent] = None
        self.synthesizer: Optional[SynthesizerAgent] = None
        self.assembler = PayloadAssembler()

    async def _initialize(self, research_topic: str) -> None:
        """Initialize database and sub-agents."""
        # Connect to database
        async with get_db() as db:
            self.db = db

        self.db = Database()
        await self.db.connect()

        # Create session
        self.session_id = await self.db.create_session(research_topic)

        # Initialize sub-agents
        self.searcher = SearcherAgent(self.db)
        self.critic = CriticAgent(self.db)
        self.synthesizer = SynthesizerAgent(self.db)

        # Set up output directory
        if not self.config.output_dir:
            self.config.output_dir = app_config.storage.outputs_dir / self.session_id
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    async def run(
        self,
        research_topic: str,
        search_queries: Optional[list[str]] = None,
    ) -> HandoffPayload:
        """
        Run the complete Phase 1 research workflow.

        Args:
            research_topic: The research topic/question
            search_queries: Optional list of search queries (defaults to topic)

        Returns:
            Complete HandoffPayload ready for Gemini
        """
        console.print(Panel(
            f"[bold]Research Topic:[/bold] {research_topic}",
            title="[bold blue]PI Orchestrator Starting[/bold blue]",
            border_style="blue",
        ))

        # Initialize
        await self._initialize(research_topic)

        search_queries = search_queries or [research_topic]

        # =====================================================================
        # Phase 1.1: Search (Searcher Agent)
        # =====================================================================
        console.rule("[bold blue]Phase 1.1: Paper Discovery[/bold blue]")

        all_papers: list[Paper] = []
        for query in search_queries:
            papers = await self.searcher.search(
                session_id=self.session_id,
                query=query,
                config=self.config.search_config,
            )
            all_papers.extend(papers)

        if not all_papers:
            raise RuntimeError("No papers found. Try different search queries.")

        console.print(f"\n[green]Total unique papers discovered: {len(all_papers)}[/green]")

        # =====================================================================
        # Phase 1.2: Analysis (Critic Agent)
        # =====================================================================
        console.rule("[bold yellow]Phase 1.2: Paper Analysis[/bold yellow]")

        # Analyze relevance
        analyzed_papers = await self.critic.analyze_papers(
            session_id=self.session_id,
            papers=all_papers,
            research_topic=research_topic,
            config=self.config.critic_config,
        )

        # Select top papers
        selected_papers = await self.critic.select_papers(
            session_id=self.session_id,
            papers=analyzed_papers,
            config=self.config.critic_config,
        )

        if not selected_papers:
            raise RuntimeError("No papers passed relevance threshold. Adjust min_relevance_score.")

        # Detect gaps
        gaps = await self.critic.detect_gaps(
            session_id=self.session_id,
            papers=selected_papers,
            research_topic=research_topic,
            config=self.config.critic_config,
        )

        # =====================================================================
        # Phase 1.3: Synthesis (Synthesizer Agent)
        # =====================================================================
        console.rule("[bold magenta]Phase 1.3: Knowledge Synthesis[/bold magenta]")

        # Build knowledge graph
        knowledge_graph = await self.synthesizer.build_knowledge_graph(
            session_id=self.session_id,
            papers=selected_papers,
            research_topic=research_topic,
            config=self.config.synthesizer_config,
        )

        if not knowledge_graph:
            knowledge_graph = KnowledgeGraph()

        # Generate hypothesis
        hypothesis: Optional[HypothesisSpecification] = None
        if gaps:
            hypothesis = await self.synthesizer.generate_hypothesis(
                session_id=self.session_id,
                gaps=gaps,
                knowledge_graph=knowledge_graph,
                research_topic=research_topic,
            )

        # Match target journals
        journals = await self.synthesizer.match_journals(
            session_id=self.session_id,
            research_topic=research_topic,
            hypothesis=hypothesis,
            config=self.config.synthesizer_config,
        )

        # =====================================================================
        # Phase 1.4: Payload Assembly
        # =====================================================================
        console.rule("[bold green]Phase 1.4: Payload Assembly[/bold green]")

        result = await self.assembler.execute(
            research_topic=research_topic,
            papers=selected_papers,
            knowledge_graph=knowledge_graph,
            gaps=gaps,
            hypothesis=hypothesis,
            journals=journals,
            task_type=self.config.task_type,
            citation_style=self.config.citation_style,
        )

        if not result.success:
            raise RuntimeError(f"Payload assembly failed: {result.error}")

        payload = result.data

        # Save payload
        await self._save_outputs(payload)

        # Final summary
        self._display_summary(payload)

        # Update session status
        await self.db.update_session_status(self.session_id, "completed")
        await self.db.save_handoff_payload(self.session_id, payload)

        console.print(Panel(
            f"[bold green]Phase 1 Complete![/bold green]\n\n"
            f"Session ID: {self.session_id}\n"
            f"Papers: {payload.paper_manifest.total_papers}\n"
            f"Gaps: {len(payload.gap_analysis.identified_gaps)}\n"
            f"Checksum: {payload.metadata.validation_checksum[:16]}...",
            title="[bold]Ready for Phase 2 (Gemini)[/bold]",
            border_style="green",
        ))

        return payload

    async def _save_outputs(self, payload: HandoffPayload) -> None:
        """Save all outputs to files."""
        output_dir = self.config.output_dir

        # Save hand-off payload (JSON)
        payload_path = output_dir / "handoff_payload.json"
        with open(payload_path, "w", encoding="utf-8") as f:
            f.write(payload.model_dump_json(indent=2))
        console.print(f"[dim]Saved: {payload_path}[/dim]")

        # Save debug view (Markdown)
        debug_path = output_dir / "papers_debug.md"
        debug_content = await self.db.export_debug_view(self.session_id, "markdown")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(debug_content)
        console.print(f"[dim]Saved: {debug_path}[/dim]")

        # Save knowledge graph (JSON)
        kg_path = output_dir / "knowledge_graph.json"
        with open(kg_path, "w", encoding="utf-8") as f:
            json.dump(payload.knowledge_graph.model_dump(), f, indent=2)
        console.print(f"[dim]Saved: {kg_path}[/dim]")

    def _display_summary(self, payload: HandoffPayload) -> None:
        """Display final summary."""
        summary = f"""
## Research Summary

**Topic:** {payload.metadata.research_topic}
**Generated:** {payload.metadata.generated_at}

### Papers Selected: {payload.paper_manifest.total_papers}

Top papers:
{"".join(f"- {p.title[:60]}... (Score: {p.relevance_score:.2f})" + chr(10) for p in payload.paper_manifest.papers[:5])}

### Research Gaps: {len(payload.gap_analysis.identified_gaps)}

{"".join(f"- **{g.gap_id}**: {g.title}" + chr(10) for g in payload.gap_analysis.identified_gaps)}

### Target Journals: {len(payload.target_journals)}

{"".join(f"- {j.name} (IF: {j.impact_factor or '?'})" + chr(10) for j in payload.target_journals[:3])}
"""

        if payload.hypothesis_specification:
            summary += f"""
### Hypothesis

{payload.hypothesis_specification.hypothesis}
"""

        console.print(Panel(
            Markdown(summary),
            title="[bold]Phase 1 Summary[/bold]",
            border_style="cyan",
        ))

    async def close(self) -> None:
        """Clean up resources."""
        if self.db:
            await self.db.close()


# Main entry point
async def run_research(
    research_topic: str,
    search_queries: Optional[list[str]] = None,
    config: Optional[OrchestratorConfig] = None,
) -> HandoffPayload:
    """
    Run the complete research workflow.

    Args:
        research_topic: The research topic/question
        search_queries: Optional list of search queries
        config: Optional orchestrator configuration

    Returns:
        HandoffPayload ready for Phase 2
    """
    orchestrator = PIOrchestrator(config)
    try:
        return await orchestrator.run(research_topic, search_queries)
    finally:
        await orchestrator.close()
