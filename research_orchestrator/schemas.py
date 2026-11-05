# schemas.py
# Structured outputs for each agent. Pydantic models so the graph
# always gets predictable data back from the LLM calls.

from typing import List

from pydantic import BaseModel, Field


class ResearchOutput(BaseModel):
    """What the researcher agent hands back after hitting Tavily."""

    topic: str
    key_findings: List[str] = Field(description="List of verified facts and insights")
    sources: List[str] = Field(description="URLs or source identifiers used")


class FactCheckResult(BaseModel):
    """Verdict from the fact-checker. feedback empty unless is_accurate is False."""

    is_accurate: bool = Field(description="True if facts are supported by research")
    feedback: str = Field(description="Constructive notes if revision is needed")
    missing_points: List[str] = Field(default_factory=list)


class TechnicalSummary(BaseModel):
    """Final deliverable from the editor agent."""

    title: str
    executive_summary: str
    technical_details: str
    key_takeaways: List[str]
