"""RAG chain construction and prompt templates.

Centralizes the prompt engineering and chain wiring so the Streamlit app
and CLI tools share identical RAG behaviour.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_ollama import OllamaLLM

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────

SECURITY_ANALYST_PROMPT = """\
You are a security analyst copilot. Analyze the provided REAL security \
logs and answer the user's question.

REAL Network Log Data (from Kaggle dataset):
{context}

Question: {input}

Instructions:
- Answer based ONLY on the provided REAL logs.
- If you find malicious activity, describe it clearly.
- Suggest security actions if threats are detected.
- Be concise and factual.
- If information is not in the logs, say "Not found in the provided logs."

Answer:"""


def get_prompt_template() -> PromptTemplate:
    """Return the security-analyst RAG prompt template.

    Returns:
        A ``PromptTemplate`` with input variables ``context`` and ``input``.
    """
    return PromptTemplate(
        template=SECURITY_ANALYST_PROMPT,
        input_variables=["context", "input"],
    )


# ── Chain ─────────────────────────────────────────────────────────────


def create_rag_chain(
    retriever: Any,
    llm: OllamaLLM,
    prompt: PromptTemplate | None = None,
) -> Runnable:
    """Build a retrieval-augmented generation chain.

    Args:
        retriever: A LangChain retriever (e.g. from a FAISS vector store).
        llm: The language model used for generation.
        prompt: An optional custom prompt template. Defaults to
            :func:`get_prompt_template`.

    Returns:
        A runnable LangChain RAG chain that accepts ``{"input": "..."}``
        and returns ``{"answer": "...", "context": [...]}``.
    """
    prompt = prompt or get_prompt_template()
    document_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, document_chain)
    logger.info("RAG chain created")
    return chain
