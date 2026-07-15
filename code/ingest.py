"""
ingest.py — Entry point for the RAG ingest pipeline.

Pipeline:
  PDF → Docling Parser → Heading-based Chunking → Metadata → Embedding (BGE-M3) → ChromaDB

Usage:
    python ingest.py
    python ingest.py --pdf path/to/file.pdf
    python ingest.py --persist-dir ./my_chroma_db
"""

import argparse
import shutil
import sys
import time
from pathlib import Path

from utils import setup_logger

logger = setup_logger("ingest")

# Default paths (relative to this script's location)
DEFAULT_PDF = "data/Panduan-TA-TIF-2020.pdf"
DEFAULT_PERSIST_DIR = "./chroma_db"


def run_pipeline(pdf_path: str, persist_directory: str, force: bool = False):
    """
    Execute the full ingest pipeline.

    Args:
        pdf_path: Path to the PDF file to ingest.
        persist_directory: Path to ChromaDB persistent storage.
        force: If True, delete existing ChromaDB and re-ingest.
    """
    start_time = time.time()

    # ── Validate input ──
    pdf = Path(pdf_path)
    if not pdf.exists():
        logger.error(f"PDF not found: {pdf_path}")
        sys.exit(1)

    # ── Check for existing database ──
    persist_path = Path(persist_directory)
    if persist_path.exists() and not force:
        logger.warning(
            f"ChromaDB already exists at {persist_path.resolve()}. "
            f"Use --force to re-ingest."
        )
        logger.info("Loading existing database instead...")
        _verify_existing(persist_directory)
        return

    if persist_path.exists() and force:
        logger.info("Removing existing ChromaDB (--force)...")
        shutil.rmtree(persist_path)

    # ── Step 1: Parse PDF ──
    logger.info("=" * 50)
    logger.info("STEP 1: Parsing PDF with Docling")
    logger.info("=" * 50)
    from parser import parse_pdf
    parsed = parse_pdf(str(pdf))

    # ── Step 2: Chunk document ──
    logger.info("")
    logger.info("=" * 50)
    logger.info("STEP 2: Chunking document")
    logger.info("=" * 50)
    from chunker import chunk_document
    documents = chunk_document(parsed)

    # Show chunk statistics
    _log_chunk_stats(documents)

    # ── Step 3: Embed and store ──
    logger.info("")
    logger.info("=" * 50)
    logger.info("STEP 3: Embedding & storing in ChromaDB")
    logger.info("=" * 50)
    from embedder import get_embedding_model
    embedding_model = get_embedding_model()

    from vectorstore import store_documents
    vectorstore = store_documents(documents, embedding_model, persist_directory)

    # ── Done ──
    elapsed = time.time() - start_time
    logger.info("")
    logger.info("=" * 50)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Source: {pdf.name}")
    logger.info(f"Chunks: {len(documents)}")
    logger.info(f"ChromaDB: {persist_path.resolve()}")
    logger.info(f"Time: {elapsed:.1f}s")
    logger.info("Done.")


def _verify_existing(persist_directory: str):
    """Verify an existing ChromaDB is loadable and show stats."""
    from embedder import get_embedding_model
    from vectorstore import load_vectorstore

    embedding_model = get_embedding_model()
    vectorstore = load_vectorstore(embedding_model, persist_directory)

    count = vectorstore._collection.count()
    logger.info(f"Existing database verified: {count} chunks")


def _log_chunk_stats(documents):
    """Log statistics about the generated chunks."""
    from collections import Counter

    content_types = Counter()
    chapters = Counter()

    for doc in documents:
        ct = doc.metadata.get("content_type", "unknown")
        ch = doc.metadata.get("chapter", "none")
        content_types[ct] += 1
        chapters[ch] += 1

    logger.info(f"  Chunks by content_type:")
    for ct, count in content_types.most_common():
        logger.info(f"    {ct}: {count}")

    logger.info(f"  Chunks by chapter:")
    for ch, count in chapters.most_common():
        logger.info(f"    {ch or '(front matter)'}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest Panduan TA PDF into ChromaDB for RAG"
    )
    parser.add_argument(
        "--pdf",
        default=DEFAULT_PDF,
        help=f"Path to the PDF file (default: {DEFAULT_PDF})",
    )
    parser.add_argument(
        "--persist-dir",
        default=DEFAULT_PERSIST_DIR,
        help=f"ChromaDB persist directory (default: {DEFAULT_PERSIST_DIR})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingest even if ChromaDB already exists",
    )
    args = parser.parse_args()

    run_pipeline(args.pdf, args.persist_dir, args.force)


if __name__ == "__main__":
    main()
