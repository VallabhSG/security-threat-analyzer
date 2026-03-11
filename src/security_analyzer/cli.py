"""Command-line interface for the Security Threat Analyzer.

Provides subcommands for data preparation, index building, evaluation,
and Ollama health checks.

Usage::

    python -m security_analyzer prepare-data
    python -m security_analyzer build-index
    python -m security_analyzer evaluate
    python -m security_analyzer check-health
"""

from __future__ import annotations

import argparse
import sys

from security_analyzer.config import configure_logging, settings


def cmd_prepare_data(args: argparse.Namespace) -> None:
    """Prepare raw CSV data into embedding-ready log records."""
    from security_analyzer.data import (
        load_raw_data,
        prepare_logs,
        print_data_summary,
        sample_logs,
    )

    raw = load_raw_data(args.input)
    prepared = prepare_logs(raw)
    sampled = sample_logs(prepared, args.sample_size)

    output = args.output or settings.prepared_data_path
    sampled.to_csv(output, index=False)

    print(f"\n✓ Saved {len(sampled):,} prepared log records to {output}")
    print_data_summary(sampled)


def cmd_build_index(args: argparse.Namespace) -> None:
    """Build a FAISS vector index from prepared log data."""
    from security_analyzer.data import dataframe_to_documents, load_prepared_data
    from security_analyzer.vectorstore import build_vectorstore, save_vectorstore

    df = load_prepared_data(args.input)
    documents = dataframe_to_documents(df)
    vectorstore = build_vectorstore(documents)
    save_vectorstore(vectorstore, args.output)

    # Quick smoke test
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke("SQL injection or Nmap scanning attacks")
    print(f"\n✓ Smoke test — found {len(results)} relevant chunks:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.page_content[:100]}…")
        print(f"     IP: {doc.metadata.get('source_ip', 'N/A')}")

    print("\n✓ Vector index ready for RAG!")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Run the full evaluation suite."""
    from security_analyzer.evaluate import run_full_evaluation

    run_full_evaluation()


def cmd_check_health(args: argparse.Namespace) -> None:
    """Check Ollama connectivity and model availability."""
    from security_analyzer.llm import print_health_report

    print_health_report()


# ── Parser ────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="security-analyzer",
        description="Security Threat Analyzer — AI-powered log analysis with RAG",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # prepare-data
    p_prep = subparsers.add_parser("prepare-data", help="Prepare raw CSV for embedding")
    p_prep.add_argument("-i", "--input", help=f"Input CSV path (default: {settings.raw_data_path})")
    p_prep.add_argument("-o", "--output", help=f"Output CSV path (default: {settings.prepared_data_path})")
    p_prep.add_argument(
        "-n",
        "--sample-size",
        type=int,
        default=settings.target_sample_size,
        help=f"Target sample size (default: {settings.target_sample_size:,})",
    )
    p_prep.set_defaults(func=cmd_prepare_data)

    # build-index
    p_build = subparsers.add_parser("build-index", help="Build FAISS vector index")
    p_build.add_argument("-i", "--input", help=f"Prepared CSV path (default: {settings.prepared_data_path})")
    p_build.add_argument("-o", "--output", help=f"Index output dir (default: {settings.faiss_index_path})")
    p_build.set_defaults(func=cmd_build_index)

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Run full system evaluation")
    p_eval.set_defaults(func=cmd_evaluate)

    # check-health
    p_health = subparsers.add_parser("check-health", help="Check Ollama status")
    p_health.set_defaults(func=cmd_check_health)

    return parser


def main() -> None:
    """CLI entry point."""
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
