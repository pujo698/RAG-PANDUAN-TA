"""
vectorstore.py — ChromaDB persistent vector database.

Stores embedded document chunks in a persistent ChromaDB collection.
Reusable across sessions without re-ingesting.
"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from utils import setup_logger, sanitize_for_chroma

logger = setup_logger("vectorstore")

# Default persist directory
DEFAULT_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "panduan_ta"
BATCH_SIZE = 50  # ChromaDB batch insert size


def store_documents(
    documents: list[Document],
    embedding_model: HuggingFaceEmbeddings,
    persist_directory: str = DEFAULT_PERSIST_DIR,
) -> Chroma:
    """
    Embed and store documents in ChromaDB.

    ChromaDB with langchain-chroma auto-persists; no manual persist() needed.

    Args:
        documents: List of LangChain Document objects.
        embedding_model: Initialized embedding model.
        persist_directory: Path to ChromaDB storage directory.

    Returns:
        Chroma vectorstore instance.
    """
    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Embedding {len(documents)} chunks...")

    # Sanitize documents — ensure no empty page_content
    sanitized_docs = []
    for doc in documents:
        sanitized = Document(
            page_content=sanitize_for_chroma(doc.page_content),
            metadata=_sanitize_metadata(doc.metadata),
        )
        sanitized_docs.append(sanitized)

    # Store in batches to avoid memory issues
    logger.info("Saving into ChromaDB...")

    vectorstore = None
    for i in range(0, len(sanitized_docs), BATCH_SIZE):
        batch = sanitized_docs[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        total_batches = (len(sanitized_docs) + BATCH_SIZE - 1) // BATCH_SIZE
        logger.info(f"  Batch {batch_num}/{total_batches} ({len(batch)} chunks)")

        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embedding_model,
                persist_directory=str(persist_path),
                collection_name=COLLECTION_NAME,
            )
        else:
            vectorstore.add_documents(batch)

    logger.info(f"ChromaDB saved to: {persist_path.resolve()}")
    return vectorstore


def load_vectorstore(
    embedding_model: HuggingFaceEmbeddings,
    persist_directory: str = DEFAULT_PERSIST_DIR,
) -> Chroma:
    """
    Load an existing ChromaDB vectorstore (no re-ingest needed).

    Args:
        embedding_model: Initialized embedding model.
        persist_directory: Path to ChromaDB storage directory.

    Returns:
        Chroma vectorstore instance.
    """
    persist_path = Path(persist_directory)
    if not persist_path.exists():
        raise FileNotFoundError(
            f"ChromaDB directory not found: {persist_directory}. Run ingest first."
        )

    logger.info(f"Loading ChromaDB from: {persist_path.resolve()}")

    vectorstore = Chroma(
        persist_directory=str(persist_path),
        embedding_function=embedding_model,
        collection_name=COLLECTION_NAME,
    )

    count = vectorstore._collection.count()
    logger.info(f"Loaded {count} documents from ChromaDB")
    return vectorstore


def _sanitize_metadata(metadata: dict) -> dict:
    """
    Ensure metadata values are ChromaDB-compatible types.
    ChromaDB accepts: str, int, float, bool. Lists must be converted to strings.
    """
    clean = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            clean[key] = ", ".join(str(v) for v in value)
        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value
        else:
            clean[key] = str(value)
    return clean
