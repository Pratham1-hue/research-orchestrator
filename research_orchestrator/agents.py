# agents.py
# Each agent is just a function that takes the state and returns a partial
# update for it. LangGraph merges the returned dict into the state between
# nodes, so we only return the keys we actually touched.

from config import llm, search_tool
from schemas import FactCheckResult, ResearchOutput, TechnicalSummary
from state import OrchestratorState


def research_agent(state: OrchestratorState) -> dict:
    """Pulls fresh context from Tavily, then structures it into findings."""
    topic = state["topic"]
    feedback = state.get("feedback_history") or []

    # on retries the last feedback line gets folded into the query so
    # the search actually targets what the fact-checker flagged as missing
    query = f"{topic} {' '.join(feedback[-1:])}".strip()
    search_results = search_tool.invoke({"query": query})

    structured_llm = llm.with_structured_output(ResearchOutput)
    prompt = (
        f"Research topic: {topic}\n"
        f"Search context: {search_results}\n"
        f"Feedback to address: {feedback}"
    )

    result = structured_llm.invoke(prompt)
    return {"research_data": result}


def fact_checker_agent(state: OrchestratorState) -> dict:
    """Audits the research. If it's not accurate, the feedback gets queued
    up for the researcher's next pass."""
    research = state["research_data"]

    structured_llm = llm.with_structured_output(FactCheckResult)
    prompt = (
        f"Verify the following research for accuracy and gaps.\n"
        f"Topic: {research.topic}\n"
        f"Findings: {research.key_findings}\n"
        f"Sources: {research.sources}"
    )

    result = structured_llm.invoke(prompt)

    # always bump the counter, even on a passing check, so the router
    # can enforce a hard ceiling on total loop iterations
    revisions = state.get("revision_count", 0) + 1

    history = list(state.get("feedback_history") or [])
    if not result.is_accurate:
        history.append(result.feedback)

    return {
        "fact_check": result,
        "revision_count": revisions,
        "feedback_history": history,
    }


def editorial_agent(state: OrchestratorState) -> dict:
    """Turns the (now verified) research into the final written summary."""
    research = state["research_data"]

    structured_llm = llm.with_structured_output(TechnicalSummary)
    prompt = (
        f"Write a polished technical summary based on this verified research:\n"
        f"Topic: {research.topic}\n"
        f"Findings: {research.key_findings}\n"
        f"Sources: {research.sources}"
    )

    summary = structured_llm.invoke(prompt)
    return {"final_summary": summary}
