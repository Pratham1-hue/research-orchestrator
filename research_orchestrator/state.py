# state.py
# The shared memory that flows through every node in the graph.
# Kept as a plain TypedDict instead of a Pydantic model on purpose --
# LangGraph handles TypedDict state natively and it stays readable.

from typing import List, Optional, TypedDict

from schemas import FactCheckResult, ResearchOutput, TechnicalSummary


class OrchestratorState(TypedDict):
    topic: str
    research_data: Optional[ResearchOutput]
    fact_check: Optional[FactCheckResult]
    final_summary: Optional[TechnicalSummary]

    # how many times the fact-checker bounced the research back
    revision_count: int

    # accumulated feedback strings, fed to the researcher on retries
    feedback_history: List[str]
