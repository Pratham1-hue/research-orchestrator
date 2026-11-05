# graph.py
# Wires the three agents into the actual state machine.
#
#   researcher -> fact_checker --(accurate OR out of revisions)--> editor -> END
#                       |
#                       +--(needs work)--> back to researcher
#
# The loop is bounded by MAX_REVISIONS so a stubborn fact-checker can't
# spin forever (and burn API credits).

from langgraph.graph import END, StateGraph

from agents import editorial_agent, fact_checker_agent, research_agent
from state import OrchestratorState

MAX_REVISIONS = 2


def route_fact_check(state: OrchestratorState) -> str:
    """Router after the fact-checker: pass goes to editor, fail goes
    back to the researcher -- unless we've already used up our revisions."""
    fact_check = state["fact_check"]
    if fact_check.is_accurate or state["revision_count"] >= MAX_REVISIONS:
        return "editor"
    return "researcher"


def build_graph():
    builder = StateGraph(OrchestratorState)

    builder.add_node("researcher", research_agent)
    builder.add_node("fact_checker", fact_checker_agent)
    builder.add_node("editor", editorial_agent)

    builder.set_entry_point("researcher")
    builder.add_edge("researcher", "fact_checker")

    builder.add_conditional_edges(
        "fact_checker",
        route_fact_check,
        {
            "editor": "editor",
            "researcher": "researcher",
        },
    )

    builder.add_edge("editor", END)
    return builder.compile()


graph = build_graph()
