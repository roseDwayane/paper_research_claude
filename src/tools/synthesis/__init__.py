"""
Synthesis tools for generating research insights.
"""

from src.tools.synthesis.hypothesis import HypothesisGenerator, generate_hypothesis
from src.tools.synthesis.journal_matcher import JournalMatcher, match_target_journals
from src.tools.synthesis.payload_assembler import PayloadAssembler, assemble_handoff_payload

__all__ = [
    "HypothesisGenerator",
    "generate_hypothesis",
    "JournalMatcher",
    "match_target_journals",
    "PayloadAssembler",
    "assemble_handoff_payload",
]
