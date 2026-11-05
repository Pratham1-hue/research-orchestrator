# Project Research Orchestrator

A multi-agent pipeline that researches a topic, fact-checks itself, and writes a polished technical summary — all orchestrated with LangGraph.

## What is this thing?

Give it a topic, and it runs three agents in a loop until the output is actually good:

1. **Researcher** — hits Tavily for real web context, then structures the results into findings + sources.
2. **Fact-Checker** — audits the research. If something is missing or shaky, it sends constructive feedback back to the researcher.
3. **Editor** — once the research survives the fact-check, it writes the final summary: title, executive summary, technical details, key takeaways.

The feedback loop between the researcher and the fact-checker is bounded by a `MAX_REVISIONS` limit (default 2), so a stubborn fact-checker can't spin forever and burn API credits. That's a deliberate design choice — bounded cycles are one of the first things serious reviewers look for in agent architecture.

## Why I built it this way

- **TypedDict state, not loose dicts.** The whole flow passes around one shared `OrchestratorState`, so every node's input/output contract is obvious at a glance.
- **Pydantic structured outputs.** Each agent uses `with_structured_output()`, so the LLM always returns valid, typed JSON instead of free text I'd have to regex-pick through.
- **Flat file layout.** No factory patterns, no premature abstraction. Seven small files, each with one job. You can read the whole project in about ten minutes.

## Project structure

```text
research_orchestrator/
├── config.py           # Env vars + LLM/search tool setup (fails fast on missing keys)
├── schemas.py          # Pydantic models for each agent's output
├── state.py            # LangGraph state definition
├── agents.py           # The three agent nodes
├── graph.py            # StateGraph wiring + conditional routing
├── main.py             # CLI entry point
└── requirements.txt
```

## Getting started

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Set your API keys

```bash
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

(On Windows: `$env:OPENAI_API_KEY="sk-..."` or set them through System Properties.)

### 3. Run it

```bash
python main.py
# or with your own topic:
python main.py "Distributed training strategies for small research teams"
```

You'll get the final title, executive summary, technical details, and key takeaways printed to the terminal, plus how many fact-check passes the research went through.

## How the graph flows

```text
            ┌──────────────── feedback loop (max 2 retries) ───────────────┐
            │                                                             │
   researcher ──► fact_checker ── accurate or out of revisions ──► editor ──► END
            │               │
            └───────────────┘
                 (needs work)
```

The router lives in `graph.py::route_fact_check` — it's ~5 lines, and it's where the whole behavior of the system lives. When the fact-checker says "not accurate yet," its feedback string gets appended to `feedback_history` and folded into the researcher's next search query, so the retry actually targets what was flagged as missing instead of re-researching the same thing.

## Limitations & honest notes

- Default model is `gpt-4o-mini` at temperature 0.2 — cheap, fast, and reliable enough for structured output. Swap it in `config.py` if you need better writing.
- The fact-checker verifies internal consistency against the search results; it's not a substitute for a human reading the sources.
- `MAX_REVISIONS = 2` balances quality vs. cost; bump it in `graph.py` if you want more iteration.

## Requirements

- Python 3.10+
- An OpenAI API key
- A Tavily API key (free tier works fine at 3 results per query)
