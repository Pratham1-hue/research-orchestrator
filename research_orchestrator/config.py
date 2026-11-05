# config.py
# Single place where the LLM + search tool get wired up.
# Reads keys straight from the environment; no fancy factory patterns needed
# for a project this size.

import os

from langchain_openai import ChatOpenAI

# langchain renamed the tavily package a few times, this is the current path
from langchain_community.tools.tavily_search import TavilySearchResults

# sanity check -- better to fail here at startup than 3 nodes into a run
if not os.environ.get("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")
if not os.environ.get("TAVILY_API_KEY"):
    raise RuntimeError("TAVILY_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# 3 results is plenty; more just bloats the prompt
search_tool = TavilySearchResults(max_results=3)
