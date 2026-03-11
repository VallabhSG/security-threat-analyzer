"""Ollama LLM initialization and health checking.

Provides functions to verify Ollama connectivity, check model availability,
and obtain a configured LLM instance for inference.
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass

import requests
from langchain_ollama import OllamaLLM

from security_analyzer.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OllamaStatus:
    """Result of an Ollama health check."""

    is_running: bool
    available_models: list[str]
    target_model_available: bool
    error: str | None = None


def check_ollama_health(model: str | None = None) -> OllamaStatus:
    """Check whether Ollama is reachable and the target model is available.

    Args:
        model: The model name to look for. Defaults to
            :pydata:`settings.ollama_model`.

    Returns:
        An ``OllamaStatus`` describing connectivity and model availability.
    """
    model = model or settings.ollama_model
    api_url = f"{settings.ollama_base_url}/api/tags"

    try:
        response = requests.get(api_url, timeout=3)
        if response.status_code != 200:
            return OllamaStatus(
                is_running=False,
                available_models=[],
                target_model_available=False,
                error=f"Ollama returned HTTP {response.status_code}",
            )

        data = response.json()
        model_names = [m.get("name", "") for m in data.get("models", [])]
        target_available = any(model in name for name in model_names)

        return OllamaStatus(
            is_running=True,
            available_models=model_names,
            target_model_available=target_available,
        )

    except requests.exceptions.ConnectionError:
        return OllamaStatus(
            is_running=False,
            available_models=[],
            target_model_available=False,
            error=f"Cannot connect to Ollama at {settings.ollama_base_url}",
        )
    except requests.exceptions.RequestException as exc:
        return OllamaStatus(
            is_running=False,
            available_models=[],
            target_model_available=False,
            error=str(exc),
        )


def get_llm(*, validate: bool = True) -> OllamaLLM:
    """Return a configured ``OllamaLLM`` instance.

    On first call the function verifies Ollama connectivity (unless
    *validate* is ``False``), forces CPU mode, and performs a smoke test.

    Args:
        validate: If ``True`` (default), perform a health check and
            raise on failure.

    Returns:
        A ready-to-use ``OllamaLLM``.

    Raises:
        ConnectionError: If Ollama is not reachable.
        RuntimeError: If the LLM fails its smoke test.
    """
    if validate:
        status = check_ollama_health()
        if not status.is_running:
            raise ConnectionError(
                f"Ollama is not running. {status.error or ''}\n"
                "Start it with: ollama serve"
            )
        logger.info("Ollama is running — available models: %s", status.available_models)

    # Force CPU mode to avoid CUDA OOM on low-VRAM machines
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

    logger.info("Initializing LLM: %s", settings.ollama_model)
    llm = OllamaLLM(
        model=settings.ollama_model,
        temperature=settings.ollama_temperature,
        base_url=settings.ollama_base_url,
        num_ctx=settings.ollama_num_ctx,
        request_timeout=settings.ollama_timeout,
    )

    # Smoke test
    try:
        test_result = llm.invoke("Hi")
        if test_result is None:
            raise RuntimeError("LLM returned None on smoke test")
        logger.info("LLM smoke test passed")
    except Exception as exc:
        raise RuntimeError(
            f"LLM smoke test failed: {exc}\n"
            "Try restarting Ollama in CPU mode: set OLLAMA_NUM_GPU=0 && ollama serve"
        ) from exc

    return llm


def print_health_report() -> None:
    """Print a human-readable Ollama health report to stdout."""
    status = check_ollama_health()

    if status.is_running:
        print("✓ Ollama is running")
        print(f"  Available models: {status.available_models}")
        if status.target_model_available:
            print(f"  ✓ Target model '{settings.ollama_model}' is available")
        else:
            print(f"  ✗ Target model '{settings.ollama_model}' not found")
            print(f"    Run: ollama pull {settings.ollama_model}")
            sys.exit(1)
    else:
        print(f"✗ {status.error}")
        print("  Start Ollama with: ollama serve")
        sys.exit(1)
