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
    """
    # Step 1: Retrieve relevant chunks
    vectorstore = _get_vectorstore()
    retrieved_docs = vectorstore.similarity_search(question, k=TOP_K)
    logger.info(f"Retrieved {len(retrieved_docs)} docs for: '{question[:80]}...'")

    if not retrieved_docs:
        return {
            "answer": "Maaf, tidak ditemukan informasi yang relevan dalam Buku Panduan Tugas Akhir.",
            "source_documents": [],
        }

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