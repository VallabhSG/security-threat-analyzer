"""FAISS vector store operations.

Handles building, loading, saving, and querying the FAISS index used for
retrieval-augmented generation over security log data.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from security_analyzer.config import settings
from security_analyzer.embeddings import get_embeddings

if TYPE_CHECKING:
    from langchain_core.vectorstores import VectorStoreRetriever

logger = logging.getLogger(__name__)


# ── Loading ───────────────────────────────────────────────────────────


def load_vectorstore(index_path: str | None = None) -> FAISS:
    """Load a persisted FAISS index from disk.

    Args:
        index_path: Directory containing the FAISS index files.
            Defaults to :pydata:`settings.faiss_index_path`.

    Returns:
        A ``FAISS`` vector store instance.

    Raises:
        FileNotFoundError: If the index directory does not exist.
    """
    path = index_path or settings.faiss_index_path
    logger.info("Loading FAISS index from: %s", path)

    vectorstore = FAISS.load_local(
        path,
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )
    logger.info("FAISS index loaded — %s documents", vectorstore.index.ntotal)
    return vectorstore


def get_retriever(
    vectorstore: FAISS | None = None,
    k: int | None = None,
) -> VectorStoreRetriever:
    """Return a retriever backed by a FAISS vector store.

    Args:
        vectorstore: An existing ``FAISS`` instance, or ``None`` to load
            the default index from disk.
        k: Number of documents to retrieve per query.
            Defaults to :pydata:`settings.retriever_k`.

    Returns:
        A ``VectorStoreRetriever`` configured with *k* results.
    """
    if vectorstore is None:
        vectorstore = load_vectorstore()

    k = k or settings.retriever_k
    return vectorstore.as_retriever(search_kwargs={"k": k})


# ── Building ──────────────────────────────────────────────────────────


def build_vectorstore(documents: list[Document]) -> FAISS:
    """Build a FAISS index from a list of LangChain documents.

    Documents are split into chunks, embedded in batches, and indexed.
    Periodic checkpoints are saved every 100 batches.

    Args:
        documents: Pre-created ``Document`` objects to index.

    Returns:
        The fully-built ``FAISS`` vector store.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    splits = splitter.split_documents(documents)
    logger.info("Split %s documents into %s chunks", len(documents), len(splits))

    embeddings = get_embeddings()
    batch_size = settings.batch_size
    total_batches = (len(splits) - 1) // batch_size + 1
    vectorstore: FAISS | None = None

    for i in range(0, len(splits), batch_size):
        batch = splits[i : i + batch_size]
        batch_num = i // batch_size + 1

        logger.info(
            "Embedding batch %s/%s (%s docs)…",
            batch_num,
            total_batches,
            len(batch),
        )

        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)

        # Periodic checkpoint
        if batch_num % 100 == 0:
            logger.info("Checkpoint: saving progress at %s documents", min(i + batch_size, len(splits)))
            vectorstore.save_local(settings.faiss_index_path)

    assert vectorstore is not None, "No documents to index"
    logger.info("FAISS index built with %s vectors", vectorstore.index.ntotal)
    return vectorstore


def save_vectorstore(vectorstore: FAISS, index_path: str | None = None) -> None:
    """Persist a FAISS vector store to disk.

    Args:
        vectorstore: The vector store to save.
        index_path: Destination directory.
            Defaults to :pydata:`settings.faiss_index_path`.
    """
    path = index_path or settings.faiss_index_path
    vectorstore.save_local(path)
    logger.info("FAISS index saved to: %s", path)
