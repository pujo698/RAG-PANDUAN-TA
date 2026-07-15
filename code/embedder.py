"""
embedder.py — Embedding model wrapper using BGE-M3 via LangChain.

Uses BAAI/bge-m3 through LangChain's HuggingFace embeddings.
Only page_content is embedded; metadata is NOT embedded.
"""

from langchain_huggingface import HuggingFaceEmbeddings

from utils import setup_logger

logger = setup_logger("embedder")

# Model configuration
MODEL_NAME = "BAAI/bge-m3"
MODEL_KWARGS = {"device": "cuda"}  # Use CPU; change to "cuda" if GPU available
ENCODE_KWARGS = {"normalize_embeddings": True}  # BGE models benefit from normalization


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
