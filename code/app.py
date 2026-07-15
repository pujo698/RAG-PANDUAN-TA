"""
app.py — FastAPI backend for RAG Buku Panduan TA.

Exposes:
    POST /api/chat  — QA endpoint
    GET  /health    — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import query_rag
from utils import setup_logger
from config import CORS_ORIGINS

logger = setup_logger("api")

app = FastAPI(title="RAG Panduan TA API", version="1.0.0")

# Allow frontend (Vite dev server) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ──

class ChatRequest(BaseModel):
    question: str


class SourceDoc(BaseModel):
    content: str
    page: int
    chapter: str
    section: str
    content_type: str
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDoc]


# ── Routes ──

@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "ok"}


@app.post("/api/ask", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer a question using RAG pipeline.

    Returns the LLM-generated answer + list of source documents.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    logger.info(f"Query: {request.question[:100]}...")

    try:
        result = query_rag(request.question)
        scores = result.get("scores", [0.0] * len(result["source_documents"]))
        return ChatResponse(
            answer=result["answer"],
            sources=[
                SourceDoc(
                    content=doc.page_content[:500],
                    page=doc.metadata.get("page", 0),
                    chapter=doc.metadata.get("chapter", ""),
                    section=doc.metadata.get("section", ""),
                    content_type=doc.metadata.get("content_type", ""),
                    score=scores[i] if i < len(scores) else 0.0,
                )
                for i, doc in enumerate(result["source_documents"])
            ],
        )
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Entry point ──

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)