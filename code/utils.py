"""
utils.py — Shared utilities and logging configuration.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "ingest", level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def count_tokens_approx(text: str) -> int:
    """
    Approximate token count using whitespace splitting.
    
    For Indonesian/Malay text this is a reasonable heuristic.
    A more accurate approach would use a tokenizer, but for chunking
    threshold decisions this is sufficient.
    """
    if not text:
        return 0
    # Approximate: ~1.3 tokens per whitespace-separated word for Indonesian
    words = text.split()
    return int(len(words) * 1.3)


def clean_text(text: str) -> str:
    """Clean extracted text by normalizing whitespace."""
    if not text:
        return ""
    # Collapse multiple spaces/newlines into single space
    import re
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_for_chroma(text: str) -> str:
    """Ensure text is safe for ChromaDB storage (non-empty)."""
    if not text or not text.strip():
        return "[empty content]"
    return text.strip()
