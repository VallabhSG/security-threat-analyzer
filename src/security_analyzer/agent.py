"""Query routing and overarching agents.

This module provides the intelligence to route user questions to either
the traditional semantic RAG (for retrieving specific log examples) or a
Pandas Dataframe Agent (for aggregate statistics and counting).
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)

# ── Router Prompt ─────────────────────────────────────────────────────

ROUTER_PROMPT_TEMPLATE = """\
You are an intelligent routing assistant for a cybersecurity log analysis platform.
Your job is to read the user's question and determine the best tool to answer it.

Available Tools:
1. "SEARCH": Use this for questions asking to find, list, or identify specific threats, IPs, attack patterns, or examples of malicious activity.
2. "ANALYZE": Use this for questions asking to count, summarize, aggregate, calculate percentages, or compare overall statistics across the dataset (e.g., "how many", "distribution", "vs", "most frequent").

Based on the question, output exactly one word: either SEARCH or ANALYZE. Do not output anything else.

Question: {question}
Classification:"""

def get_router_chain(llm: ChatOllama) -> Runnable:
    prompt = PromptTemplate(template=ROUTER_PROMPT_TEMPLATE, input_variables=["question"])
    return prompt | llm | (lambda classification: "ANALYZE" if "analyze" in classification.lower() else "SEARCH")

# ── Pandas Agent ──────────────────────────────────────────────────────

def create_pandas_agent(llm: ChatOllama, df: pd.DataFrame) -> Any:
    """Create a LangChain agent capable of executing Pandas code securely.
    
    Args:
        llm: The ChatOllama language model.
        df: The pre-loaded prepared logs DataFrame.
        
    Returns:
        An agent executor ready to optionally invoke.
    """
    logger.info("Initializing Pandas Dataframe Agent...")
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type="tool-calling",
        allow_dangerous_code=True,
        max_iterations=5,
    )
    return agent
