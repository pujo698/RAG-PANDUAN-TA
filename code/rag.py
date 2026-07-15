"""
rag.py — RAG query pipeline.

Flow:
    User question → Embedding → ChromaDB similarity search → Ollama LLM → Answer + sources
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from config import (
    CHROMA_PATH,
    LLM_MODEL,
    OLLAMA_BASE_URL,
    LLM_TEMPERATURE,
    TOP_K,
)
from embedder import get_embedding_model
from vectorstore import load_vectorstore
from prompt import SYSTEM_PROMPT
from utils import setup_logger

logger = setup_logger("rag")

# ── Global singletons (lazy init) ──
_embedding_model = None
_vectorstore = None
_llm = None


def _get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = get_embedding_model()
    return _embedding_model


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        embedding = _get_embedding_model()
        _vectorstore = load_vectorstore(embedding, CHROMA_PATH)
    return _vectorstore


def _get_llm():
    global _llm
    if _llm is None:
        logger.info(f"Initializing Ollama LLM: {LLM_MODEL} @ {OLLAMA_BASE_URL}")
        _llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE,
        )
    return _llm


def query_rag(question: str) -> dict:
    """
    Execute full RAG query pipeline.

    Args:
        question: User's natural language question.

    Returns:
        dict with keys:
            - "answer": LLM-generated answer
            - "source_documents": List of LangChain Document objects
            - "scores": List of float (relevance scores, 0-1)
    """
    # Step 1: Retrieve relevant chunks with scores
    vectorstore = _get_vectorstore()
    results_with_scores = vectorstore.similarity_search_with_score(question, k=TOP_K)
    logger.info(f"Retrieved {len(results_with_scores)} docs for: '{question[:80]}...'")

    if not results_with_scores:
        return {
            "answer": "Maaf, tidak ditemukan informasi yang relevan dalam Buku Panduan Tugas Akhir.",
            "source_documents": [],
            "scores": [],
        }

    # Unpack documents and scores
    # ChromaDB returns L2 distance (lower = more similar)
    # Convert to relevance score: 1.0 = perfect match, 0.0 = unrelated
    retrieved_docs = []
    scores = []
    for doc, distance in results_with_scores:
        retrieved_docs.append(doc)
        # Normalize: typical L2 distance for normalized embeddings ranges 0-2
        relevance = max(0.0, 1.0 - (distance / 2.0))
        scores.append(round(relevance, 4))

    # Step 2: Build context from retrieved chunks
    context = _build_context(retrieved_docs)

    # Step 3: Generate answer with LLM
    llm = _get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Konteks:\n{context}\n\nPertanyaan: {question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "question": question,
    })

    logger.info(f"Answer generated ({len(answer)} chars)")

    return {
        "answer": answer,
        "source_documents": retrieved_docs,
        "scores": scores,
    }


def _build_context(documents: list[Document]) -> str:
    """
    Build a formatted context string from retrieved documents.

    Each chunk is prefixed with its metadata for traceability.
    """
    parts = []
    for i, doc in enumerate(documents, 1):
        meta = doc.metadata
        header = f"[Sumber {i}] "
        if meta.get("chapter"):
            header += f"{meta['chapter']}"
        if meta.get("section"):
            header += f" - {meta['section']}"
        if meta.get("section_title"):
            header += f" {meta['section_title']}"
        if meta.get("page"):
            header += f" (hal. {meta['page']})"

        parts.append(f"{header}\n{doc.page_content}")

    return "\n\n---\n\n".join(parts)