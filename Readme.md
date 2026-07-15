# 📚 RAG Buku Panduan Tugas Akhir Teknik Informatika UNISSULA

Sistem **Retrieval-Augmented Generation (RAG)** berbasis **LangChain**, **ChromaDB**, **Docling**, dan **Ollama** untuk menjawab pertanyaan mengenai **Buku Panduan Tugas Akhir Teknik Informatika Universitas Islam Sultan Agung**.

---

## 🚀 Fitur

- 📄 Parsing PDF dengan **Docling** (layout-aware, deteksi heading/tabel/list)
- ✂️ Chunking 3-tier (heading-based → semantic → recursive fallback)
- 🏷️ Metadata otomatis (chapter, section, content_type, keywords)
- 🧠 Embedding **BAAI/bge-m3** (1024 dimensi, multilingual)
- 💾 Vector database **ChromaDB** (persistent)
- 🔍 Semantic search + Top-K retrieval
- 🤖 LLM **Ollama** lokal (llama3 / gemma3 / mistral)
- 🛡️ Prompt guardrail anti-halusinasi
- 🖥️ **FastAPI** backend + **Vue 3** frontend

---

## 🛠️ Tech Stack

| Teknologi            | Fungsi                              |
|----------------------|-------------------------------------|
| Python 3.11+         | Bahasa pemrograman                  |
| FastAPI + Uvicorn    | Backend REST API                    |
| Vue 3 + Vite         | Frontend UI                         |
| Docling              | PDF parser (layout analysis)        |
| LangChain            | Framework RAG                       |
| ChromaDB             | Vector database                     |
| BAAI/bge-m3          | Embedding model (HuggingFace)       |
| Ollama               | Local LLM engine                    |

---

## 📂 Struktur Proyek

```
RAG-PANDUAN-TA/
├── code/
│   ├── app.py              # FastAPI backend
│   ├── rag.py              # RAG query pipeline
│   ├── ingest.py           # PDF → ChromaDB ingest pipeline
│   ├── parser.py           # Docling PDF parser
│   ├── chunker.py          # 3-tier chunking
│   ├── metadata.py         # Metadata generator
│   ├── embedder.py         # BGE-M3 embedding model
│   ├── vectorstore.py      # ChromaDB store/load
│   ├── prompt.py           # System prompt guardrail
│   ├── config.py           # Konfigurasi
│   ├── utils.py            # Logger, text cleaning
│   ├── requirements.txt
│   ├── chroma_db/          # Persistent vector DB
│   └── data/
│       └── Panduan-TA-TIF-2020.pdf
├── frontend/
│   ├── src/                # Vue 3 components
│   ├── index.html
│   ├── vite.config.js      # Proxy /api → localhost:8000
│   └── package.json
├── docs/
├── DOCUMENTATION.md
└── Readme.md
```

---

## ⚙️ Instalasi

### 1. Setup Python Environment

```bash
cd code
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 2. Install Ollama & Pull Model

Download Ollama: https://ollama.com

```bash
ollama serve                  # Jalankan di terminal terpisah
ollama pull llama3            # atau gemma3, mistral
```

### 3. Ingest PDF (sekali saja)

```bash
python ingest.py              # Default: data/Panduan-TA-TIF-2020.pdf

# Force re-ingest:
python ingest.py --force
```

### 4. Install Frontend

```bash
cd ../frontend
npm install
```

---

## ▶️ Menjalankan

### Terminal 1 — Ollama
```bash
ollama serve
```

### Terminal 2 — Backend (FastAPI)
```bash
cd code
venv\Scripts\activate
python app.py                  # http://localhost:8000
```

### Terminal 3 — Frontend (Vue/Vite)
```bash
cd frontend
npm run dev                    # http://localhost:5173
```

Buka `http://localhost:5173` di browser.

---

## 🔍 Pipeline RAG

```
User Question
      │
      ▼
Embedding (BGE-M3)
      │
      ▼
ChromaDB Similarity Search (Top-K)
      │
      ▼
Context + Prompt → Ollama LLM
      │
      ▼
Answer + Source Documents
```

---

## 🛡️ Anti Hallucination

LLM hanya menjawab berdasarkan konteks dokumen. Jika informasi tidak ditemukan:

> *"Maaf, informasi tersebut tidak terdapat pada Buku Panduan Tugas Akhir."*

---

## 📊 Statistik Ingest

| Metrik                | Nilai |
|-----------------------|-------|
| Halaman PDF           | 86    |
| Total chunk           | 247   |
| Embedding dimensi     | 1024  |
| Kategori chunk        | 10    |

---

## 📝 Catatan

- `config.py` menentukan model embedding, LLM, dan parameter retrieval
- `chroma_db/` sudah berisi hasil ingest — tidak perlu re-ingest kecuali PDF berubah
- Frontend Vite mem-proxy `/api` ke backend FastAPI di port 8000