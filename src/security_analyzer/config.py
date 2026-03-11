"""Centralized configuration for the Security Threat Analyzer.

All settings can be overridden via environment variables or a `.env` file
placed at the project root.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)


def _env(key: str, default: str) -> str:
    """Read an environment variable with a fallback default."""
    return os.getenv(key, default)


def _env_int(key: str, default: int) -> int:
    """Read an integer environment variable with a fallback default."""
    return int(os.getenv(key, str(default)))


@dataclass(frozen=True)
class Settings:
    """Application-wide settings, populated from env vars at import time."""

    # ── Ollama / LLM ──────────────────────────────────────────────────
    ollama_base_url: str = field(default_factory=lambda: _env("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: _env("OLLAMA_MODEL", "gemma3:1b"))
    ollama_num_ctx: int = field(default_factory=lambda: _env_int("OLLAMA_NUM_CTX", 1536))
    ollama_timeout: int = field(default_factory=lambda: _env_int("OLLAMA_TIMEOUT", 120))
    ollama_temperature: float = field(default_factory=lambda: float(_env("OLLAMA_TEMPERATURE", "0")))

    # ── Embeddings ────────────────────────────────────────────────────
    embedding_model: str = field(default_factory=lambda: _env("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))

    # ── FAISS / Retrieval ─────────────────────────────────────────────
    faiss_index_path: str = field(default_factory=lambda: _env("FAISS_INDEX_PATH", "faiss_index_real"))
    retriever_k: int = field(default_factory=lambda: _env_int("RETRIEVER_K", 5))

    # ── Data Paths ────────────────────────────────────────────────────
    raw_data_path: str = field(default_factory=lambda: _env("RAW_DATA_PATH", "log_data.csv"))
    prepared_data_path: str = field(default_factory=lambda: _env("PREPARED_DATA_PATH", "prepared_logs.csv"))

    # ── Processing ────────────────────────────────────────────────────
    batch_size: int = field(default_factory=lambda: _env_int("BATCH_SIZE", 10_000))
    chunk_size: int = field(default_factory=lambda: _env_int("CHUNK_SIZE", 500))
    chunk_overlap: int = field(default_factory=lambda: _env_int("CHUNK_OVERLAP", 50))
    target_sample_size: int = field(default_factory=lambda: _env_int("TARGET_SAMPLE_SIZE", 2_000_000))

    def __repr__(self) -> str:
        lines = [f"  {k} = {v!r}" for k, v in self.__dict__.items()]
        return "Settings(\n" + "\n".join(lines) + "\n)"


# Singleton instance — import this everywhere
settings = Settings()


def configure_logging(level: int = logging.INFO) -> None:
    """Set up consistent logging format for the entire application.

    Args:
        level: The root logging level (default ``logging.INFO``).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
