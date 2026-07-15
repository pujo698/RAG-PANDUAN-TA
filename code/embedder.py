"""
embedder.py — Embedding model wrapper using BGE-M3 via LangChain.

Uses BAAI/bge-m3 through LangChain's HuggingFace embeddings.
Only page_content is embedded; metadata is NOT embedded.
"""

from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL, EMBEDDING_DEVICE, EMBEDDING_NORMALIZE
from utils import setup_logger

logger = setup_logger("embedder")

# Model configuration (from config.py)
MODEL_NAME = EMBEDDING_MODEL
MODEL_KWARGS = {"device": EMBEDDING_DEVICE}
ENCODE_KWARGS = {"normalize_embeddings": EMBEDDING_NORMALIZE}


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Initialize and return the BGE-M3 embedding model.

    Returns:
        HuggingFaceEmbeddings instance configured for BGE-M3.
    """
    logger.info(f"Loading embedding model: {MODEL_NAME}")

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS,
    )

    logger.info("Embedding model loaded successfully")
    return embeddings
