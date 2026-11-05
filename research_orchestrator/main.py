# main.py
# CLI entry point. Pass the topic as an argument, or fall back to the
# default demo topic.

import sys

from graph import graph


def main():
    topic = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Retrieval-Augmented Generation (RAG) evaluation frameworks in 2026"
    )

    initial_state = {
        "topic": topic,
        "research_data": None,
        "fact_check": None,
        "final_summary": None,
        "revision_count": 0,
        "feedback_history": [],
    }

    print("Running Multi-Agent Orchestrator...\n")

    final_output = graph.invoke(initial_state)

    summary = final_output["final_summary"]
    print(f"Title: {summary.title}\n")
    print(f"Executive Summary:\n{summary.executive_summary}\n")
    print(f"Technical Details:\n{summary.technical_details}\n")
    print("Key Takeaways:")
    for point in summary.key_takeaways:
        print(f"- {point}")

    revisions = final_output["revision_count"]
    print(f"\n(research passed fact-check after {revisions} check(s))")


if __name__ == "__main__":
    main()
