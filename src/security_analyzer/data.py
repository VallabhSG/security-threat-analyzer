"""Data preparation and validation utilities.

Handles raw CSV ingestion, log text formatting, stratified sampling,
and basic data-quality reporting.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document

from security_analyzer.config import settings

logger = logging.getLogger(__name__)


# ── Loading ───────────────────────────────────────────────────────────


def load_raw_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load the raw security log CSV.

    Args:
        path: Path to the CSV file.
            Defaults to :pydata:`settings.raw_data_path`.

    Returns:
        A ``DataFrame`` with the raw log data.
    """
    path = Path(path or settings.raw_data_path)
    logger.info("Loading raw data from: %s", path)
    df = pd.read_csv(path)
    logger.info("Loaded %s rows, columns: %s", f"{len(df):,}", df.columns.tolist())
    return df


def load_prepared_data(path: str | Path | None = None) -> pd.DataFrame:
    """Load the prepared (processed) log CSV.

    Args:
        path: Path to the CSV file.
            Defaults to :pydata:`settings.prepared_data_path`.

    Returns:
        A ``DataFrame`` with prepared log data.
    """
    path = Path(path or settings.prepared_data_path)
    logger.info("Loading prepared data from: %s", path)
    return pd.read_csv(path)


# ── Preparation ───────────────────────────────────────────────────────


def _format_log_entry(row: pd.Series) -> str:
    """Convert a single DataFrame row into a human-readable log line."""
    parts = [
        f"[{row.get('timestamp', 'N/A')}]",
        f"IP: {row.get('source_ip', 'N/A')}",
        f"Protocol: {row.get('protocol', 'N/A')}",
        f"Path: {row.get('request_path', 'N/A')}",
    ]

    user_agent = str(row.get("user_agent", "N/A"))
    ua_lower = user_agent.lower()
    if "nmap" in ua_lower:
        parts.append("Tool: NMAP")
    elif "sqlmap" in ua_lower:
        parts.append("Tool: SQLMAP")
    elif "curl" in ua_lower:
        parts.append("Tool: CURL")
    else:
        parts.append(f"UA: {user_agent[:30]}…")

    return " ".join(parts)


def prepare_logs(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw log data into embedding-ready records.

    Steps:
      1. Drop rows missing critical fields (``source_ip``, ``protocol``).
      2. Convert each row into a human-readable ``log_text`` string.
      3. Retain key columns alongside the text.

    Args:
        df: Raw log ``DataFrame`` (must contain ``source_ip`` and
            ``protocol`` columns).

    Returns:
        A new ``DataFrame`` with ``log_text`` and metadata columns.
    """
    logger.info("Preparing logs — starting with %s rows", f"{len(df):,}")
    df = df.dropna(subset=["source_ip", "protocol"])
    logger.info("After dropping NaN rows: %s", f"{len(df):,}")

    records: list[dict[str, str]] = []
    for _, row in df.iterrows():
        records.append(
            {
                "log_text": _format_log_entry(row),
                "source_ip": row.get("source_ip", "N/A"),
                "protocol": row.get("protocol", "N/A"),
                "request_path": row.get("request_path", "N/A"),
                "user_agent": row.get("user_agent", "N/A"),
                "timestamp": row.get("timestamp", "N/A"),
            }
        )

    prepared = pd.DataFrame(records)
    logger.info("Prepared %s log records", f"{len(prepared):,}")
    return prepared


def sample_logs(
    df: pd.DataFrame,
    target_size: int | None = None,
) -> pd.DataFrame:
    """Downsample prepared logs to a target size.

    If the DataFrame is already smaller than *target_size* it is returned
    unchanged.

    Args:
        df: Prepared log ``DataFrame``.
        target_size: Maximum number of rows.
            Defaults to :pydata:`settings.target_sample_size`.

    Returns:
        A (possibly sampled) ``DataFrame``.
    """
    target = target_size or settings.target_sample_size
    if len(df) > target:
        logger.info("Sampling %s rows from %s", f"{target:,}", f"{len(df):,}")
        return df.sample(n=target, random_state=42)
    logger.info("Dataset fits target (%s rows) — no sampling required", f"{len(df):,}")
    return df


# ── Document conversion ──────────────────────────────────────────────


def dataframe_to_documents(df: pd.DataFrame) -> list[Document]:
    """Convert a prepared ``DataFrame`` into LangChain ``Document`` objects.

    Args:
        df: A ``DataFrame`` containing at least a ``log_text`` column.

    Returns:
        A list of ``Document`` instances with metadata.
    """
    documents: list[Document] = []
    for idx, row in df.iterrows():
        doc = Document(
            page_content=row["log_text"],
            metadata={
                "source_ip": row.get("source_ip", "N/A"),
                "protocol": row.get("protocol", "N/A"),
                "request_path": row.get("request_path", "N/A"),
                "user_agent": row.get("user_agent", "N/A"),
                "timestamp": row.get("timestamp", "N/A"),
                "index": idx,
            },
        )
        documents.append(doc)

    logger.info("Created %s LangChain documents", f"{len(documents):,}")
    return documents


# ── Validation / reporting ────────────────────────────────────────────


def print_data_summary(df: pd.DataFrame) -> None:
    """Print a human-readable summary of a log DataFrame to stdout."""
    print(f"Total rows:        {len(df):,}")
    print(f"Columns:           {df.columns.tolist()}")

    if "protocol" in df.columns:
        print(f"Unique protocols:  {df['protocol'].nunique()}")
        print("\nProtocol distribution:")
        for proto, count in df["protocol"].value_counts().head().items():
            pct = (count / len(df)) * 100
            print(f"  {proto:10s}  {count:>8,}  ({pct:.1f}%)")

    if "source_ip" in df.columns:
        print(f"\nUnique source IPs: {df['source_ip'].nunique():,}")
        print("\nTop 5 most active IPs:")
        for ip, count in df["source_ip"].value_counts().head().items():
            pct = (count / len(df)) * 100
            print(f"  {ip:15s}  {count:>8,}  ({pct:.2f}%)")

    if "timestamp" in df.columns:
        print(f"\nTime range:        {df['timestamp'].min()} — {df['timestamp'].max()}")

    if "label" in df.columns:
        print("\nThreat distribution:")
        for label, count in df["label"].value_counts().items():
            print(f"  {label:12s}  {count:>8,}")
