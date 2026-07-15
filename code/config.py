# ── PDF Source ──
PDF_PATH = "data/Panduan-TA-TIF-2020.pdf"

# ── ChromaDB ──
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "panduan_ta"

# ── Embedding Model (BGE-M3 via HuggingFace) ──
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DEVICE = "cuda"  # "cpu" if no GPU
EMBEDDING_NORMALIZE = True

# ── LLM (Ollama local) ──
LLM_MODEL = "llama3.2"  # 2.0 GB, fits GPU. Alternatives: gemma3:1b (fastest), llama3 (slow CPU)
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_TEMPERATURE = 0.0

# ── CORS ──
CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]

# ── Retrieval ──
TOP_K = 5

# ── Chunking (for reference, used by chunker.py) ──
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150