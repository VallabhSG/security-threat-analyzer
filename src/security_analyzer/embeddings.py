"""Embedding model factory.

Provides a single cached entry point for obtaining the HuggingFace
embedding model used across the entire application.
"""

from __future__ import annotations

import logging

from langchain_huggingface import HuggingFaceEmbeddings

from security_analyzer.config import settings

logger = logging.getLogger(__name__)

_cached_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a shared ``HuggingFaceEmbeddings`` instance.

    The model is loaded lazily on first call and cached for subsequent
    calls within the same process.

    Returns:
        A ``HuggingFaceEmbeddings`` instance configured via
        :pydata:`settings.embedding_model`.
    """
    global _cached_embeddings  # noqa: PLW0603

    if _cached_embeddings is None:
        logger.info("Loading embedding model: %s", settings.embedding_model)
        _cached_embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
        )
        logger.info("Embedding model loaded successfully")

    return _cached_embeddings
