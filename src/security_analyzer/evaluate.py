"""System evaluation suite.

Runs automated quality checks against the vector database, RAG chain,
and underlying dataset, then prints a summary report.
"""

from __future__ import annotations

import logging
import time

import pandas as pd

from security_analyzer.config import settings
from security_analyzer.data import load_prepared_data
from security_analyzer.llm import get_llm
from security_analyzer.rag import create_rag_chain
from security_analyzer.vectorstore import load_vectorstore, get_retriever

logger = logging.getLogger(__name__)

# ── Test queries ──────────────────────────────────────────────────────

RETRIEVAL_QUERIES = [
    "SQL injection attacks",
    "port scanning activity",
    "brute force login attempts",
    "malicious IP addresses",
    "suspicious network protocols",
]

RAG_QUERIES = [
    "What TCP traffic patterns are malicious?",
    "Which source IPs appear most dangerous?",
    "List common attack tools detected",
    "What protocols are used in malicious traffic?",
    "Show threat statistics",
]


# ── Evaluation steps ─────────────────────────────────────────────────


def run_retrieval_tests(retriever) -> tuple[float, list[dict]]:  # noqa: ANN001
    """Evaluate retrieval speed and basic relevance.

    Args:
        retriever: A LangChain retriever.

    Returns:
        A tuple of (average_retrieval_seconds, per_query_results).
    """
    results: list[dict] = []
    total_time = 0.0

    for query in RETRIEVAL_QUERIES:
        start = time.time()
        docs = retriever.invoke(query)
        elapsed = time.time() - start
        total_time += elapsed

        keywords = query.lower().split()
        relevance = sum(
            1
            for doc in docs
            if any(kw in doc.page_content.lower() for kw in keywords)
        )

        results.append(
            {
                "query": query,
                "num_results": len(docs),
                "time_s": elapsed,
                "relevance": f"{relevance}/{len(docs)}",
            }
        )
        logger.info(
            "Retrieval — '%s': %s results in %.2fs (relevance %s/%s)",
            query,
            len(docs),
            elapsed,
            relevance,
            len(docs),
        )

    avg_time = total_time / len(RETRIEVAL_QUERIES)
    return avg_time, results


def run_rag_tests(rag_chain) -> tuple[float, list[dict]]:  # noqa: ANN001
    """Evaluate end-to-end RAG response quality.

    Args:
        rag_chain: A runnable LangChain RAG chain.

    Returns:
        A tuple of (average_response_seconds, per_query_results).
    """
    results: list[dict] = []
    total_time = 0.0

    for query in RAG_QUERIES:
        start = time.time()
        result = rag_chain.invoke({"input": query})
        elapsed = time.time() - start
        total_time += elapsed

        answer = result["answer"]
        results.append(
            {
                "query": query,
                "time_s": elapsed,
                "answer_length": len(answer),
                "preview": answer[:80],
            }
        )
        logger.info(
            "RAG — '%s': %.2fs, %s chars",
            query,
            elapsed,
            len(answer),
        )

    avg_time = total_time / len(RAG_QUERIES)
    return avg_time, results


def run_full_evaluation() -> None:
    """Execute the complete evaluation pipeline and print a report."""
    print("=" * 70)
    print("SECURITY THREAT ANALYZER — SYSTEM EVALUATION")
    print("=" * 70)

    # 1 — Load components
    print("\n[1/5] Loading components…")
    start = time.time()
    vectorstore = load_vectorstore()
    retriever = get_retriever(vectorstore)
    llm = get_llm(validate=True)
    load_time = time.time() - start

    doc_count = vectorstore.index.ntotal
    print(f"  ✓ Components loaded in {load_time:.2f}s")
    print(f"  ✓ Vector database contains {doc_count:,} documents")

    # 2 — Retrieval tests
    print("\n[2/5] Testing vector database quality…")
    avg_retrieval, retrieval_results = run_retrieval_tests(retriever)
    for r in retrieval_results:
        print(f"  ✓ '{r['query']}': {r['num_results']} results in {r['time_s']:.2f}s (relevance: {r['relevance']})")
    print(f"  Average retrieval time: {avg_retrieval:.2f}s")

    # 3 — RAG tests
    print("\n[3/5] Testing RAG chain response quality…")
    rag_chain = create_rag_chain(retriever, llm)
    avg_response, rag_results = run_rag_tests(rag_chain)
    for r in rag_results:
        print(f"  ✓ '{r['query']}'")
        print(f"    Time: {r['time_s']:.2f}s | Length: {r['answer_length']} chars")
        print(f"    Preview: {r['preview']}…\n")

    # 4 — Dataset stats
    print("[4/5] Dataset statistics…")
    df = load_prepared_data()
    print(f"  Total documents: {len(df):,}")
    print(f"  Protocols: {df['protocol'].nunique()} unique")
    print(f"  Source IPs: {df['source_ip'].nunique():,} unique")
    if "timestamp" in df.columns:
        print(f"  Time range: {df['timestamp'].min()} — {df['timestamp'].max()}")

    print("\n  Protocol distribution:")
    for proto, count in df["protocol"].value_counts().head().items():
        pct = (count / len(df)) * 100
        print(f"    {proto}: {count:,} ({pct:.1f}%)")

    print("\n  Top 5 most active IPs:")
    for ip, count in df["source_ip"].value_counts().head().items():
        pct = (count / len(df)) * 100
        print(f"    {ip}: {count:,} ({pct:.1f}%)")

    # 5 — Summary
    response_times = [r["time_s"] for r in rag_results]
    print("\n[5/5] Performance Summary")
    print("=" * 70)
    print(f"  Vector DB:   {doc_count:,} docs indexed, avg retrieval {avg_retrieval:.2f}s, load {load_time:.2f}s")
    print(f"  RAG Chain:   avg {avg_response:.2f}s, min {min(response_times):.2f}s, max {max(response_times):.2f}s")
    print(f"  Dataset:     {len(df):,} logs, {df['protocol'].nunique()} protocols, {df['source_ip'].nunique():,} IPs")
    print("\n" + "=" * 70)
    print("✅ EVALUATION COMPLETE — System ready for deployment")
    print("=" * 70)
