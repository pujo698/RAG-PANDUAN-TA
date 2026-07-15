# 🛠️ Panduan Setup — RAG Buku Panduan TA

Panduan langkah demi langkah untuk menjalankan proyek ini di **komputer lokal** setelah clone dari GitHub.

---

## 📋 Prasyarat

| Software          | Versi Minimal | Cara Cek            | Download                                |
|-------------------|---------------|---------------------|-----------------------------------------|
| Python            | 3.11+         | `python --version`  | https://python.org                      |
| Node.js           | 18+           | `node --version`    | https://nodejs.org                      |
| npm               | 9+            | `npm --version`     | (ikut Node.js)                          |
| Ollama            | latest        | `ollama --version`  | https://ollama.com                      |
| Git               | 2.x           | `git --version`     | https://git-scm.com                     |

> **⚠️ RAM Minimal:** 8 GB (embedding model BGE-M3 butuh ~2.5 GB saat load)

---

## 🚀 Langkah 1 — Clone Repository

```bash
git clone https://github.com/pujo698/RAG-PANDUAN-TA.git
cd RAG-PANDUAN-TA
```

---

## 🐍 Langkah 2 — Setup Backend (Python)

### 2.1 Masuk ke folder code & buat virtual environment

```bash
cd code
python -m venv venv
```

### 2.2 Aktifkan virtual environment

**Windows (cmd / PowerShell):**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

> ✅ Setelah aktif, terminal akan menampilkan `(venv)` di awal prompt.

### 2.3 Install dependencies

```bash
pip install -r requirements.txt
```

> ⏳ Proses ini memakan waktu **5-15 menit** karena mengunduh PyTorch (~2 GB) dan transformers.

---

## 🤖 Langkah 3 — Setup Ollama (LLM Lokal)

### 3.1 Install Ollama

Download dan install dari: **https://ollama.com**

### 3.2 Jalankan Ollama (biarkan berjalan di terminal sendiri)

```bash
ollama serve
```

> Biarkan terminal ini tetap berjalan. Ollama akan listen di `http://localhost:11434`.

### 3.3 Download model LLM (buka terminal baru)

```bash
ollama pull llama3
```

> Model `llama3` sekitar 4.7 GB. Alternatif lebih ringan:
> - `ollama pull gemma3:4b` (lebih kecil, ~3 GB)
> - `ollama pull mistral` (~4 GB)
>
> Setelah pull, update `LLM_MODEL` di `code/config.py` sesuai model yang dipilih.

---

## 📂 Catatan: chroma_db Sudah Tersedia

Folder `code/chroma_db/` **sudah berisi hasil ingest** (247 chunks dari Buku Panduan TA, di-embed dengan BGE-M3).

> **Tidak perlu menjalankan `python ingest.py`** — database siap pakai.

Hanya jalankan ingest ulang jika PDF sumber berubah:
```bash
python ingest.py --force
```
> Jika ingin ingest ulang, install dulu: `pip install docling>=2.100.0`

---

## 🎨 Langkah 4 — Setup Frontend (Vue 3)

### 4.1 Masuk folder frontend

```bash
cd ../frontend
```

### 4.2 Install dependencies

```bash
npm install
```

> ⏳ Proses ini ~1-3 menit.

---

## ▶️ Langkah 5 — Menjalankan Aplikasi

Kamu butuh **3 terminal** yang berjalan bersamaan:

### Terminal 1 — Ollama Server
```bash
ollama serve
```
> Status: `http://localhost:11434`

### Terminal 2 — Backend FastAPI
```bash
cd code
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
python app.py
```
> Status: `http://localhost:8000`
>
> Cek health: buka `http://localhost:8000/health` → `{"status":"ok"}`

### Terminal 3 — Frontend Vue/Vite
```bash
cd frontend
npm run dev
```
> Status: `http://localhost:5173`

### Buka di Browser

**http://localhost:5173**

Ketik pertanyaan tentang panduan TA, contoh:
- "Apa syarat mengambil Tugas Akhir?"
- "Berapa minimal SKS?"
- "Bagaimana alur Seminar Proposal?"

---

## 🏗️ Arsitektur (Overview)

```
Browser (localhost:5173)
      │
      ▼
Vue 3 Frontend (Vite)
      │  POST /api/ask
      ▼  (proxy via vite.config.js)
FastAPI Backend (localhost:8000)
      │
      ├─► Embedding Model (BGE-M3)
      ├─► ChromaDB (chroma_db/)
      └─► Ollama LLM (localhost:11434)
```

---

## ⚙️ Konfigurasi

Semua konfigurasi ada di **`code/config.py`**:

| Variabel             | Default                                  | Keterangan                          |
|----------------------|------------------------------------------|-------------------------------------|
| `CHROMA_PATH`        | `"chroma_db"`                            | Folder vector database              |
| `EMBEDDING_MODEL`    | `"BAAI/bge-m3"`                          | Model embedding (HuggingFace)       |
| `EMBEDDING_DEVICE`   | `"cpu"`                                  | `"cuda"` jika ada GPU               |
| `LLM_MODEL`          | `"llama3"`                               | Model Ollama yang dipakai           |
| `OLLAMA_BASE_URL`    | `"http://localhost:11434"`               | URL Ollama server                   |
| `LLM_TEMPERATURE`    | `0.0`                                    | 0 = faktual, >0 = kreatif           |
| `TOP_K`              | `5`                                      | Jumlah chunk yang di-retrieve       |
| `CORS_ORIGINS`       | `["http://localhost:5173", ...]`         | Origin yang diizinkan akses API     |

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
> **Solusi:** Pastikan venv aktif (`venv\Scripts\activate`), lalu `pip install -r requirements.txt`.

### "Could not connect to Ollama"
> **Solusi:** Pastikan `ollama serve` berjalan di terminal lain.

### "No such file: chroma_db"
> **Solusi:** Pastikan working directory adalah `code/` saat menjalankan `python app.py`.

### "CUDA out of memory" / "std::bad_alloc"
> **Solusi:** Ubah `EMBEDDING_DEVICE = "cpu"` di `code/config.py` (lebih lambat tapi lebih hemat RAM).

### Frontend tidak bisa konek ke backend
> **Solusi:** Pastikan backend jalan di port 8000, frontend di 5173. Cek `vite.config.js` proxy sudah benar.

### Ingin ganti model LLM
> 1. `ollama pull nama-model` (misal: `gemma3:4b`, `mistral`, `qwen2.5:7b`)
> 2. Edit `LLM_MODEL` di `code/config.py` sesuai nama model
> 3. Restart `python app.py`

---

## 📊 Spesifikasi Hardware Direkomendasikan

| Komponen   | Minimum      | Direkomendasikan |
|------------|-------------|------------------|
| RAM        | 8 GB        | 16 GB            |
| CPU        | 4 core      | 8 core           |
| Disk       | 20 GB       | 50 GB (model + venv) |
| GPU        | Tidak wajib | NVIDIA 8GB+ VRAM |

---

## 📝 Struktur Proyek Lengkap

```
RAG-PANDUAN-TA/
│
├── SETUP.md                    # ◀ File ini
├── Readme.md                   # Overview proyek
├── DOCUMENTATION.md            # Dokumentasi detail pipeline
│
├── code/                       # Backend Python
│   ├── app.py                  # FastAPI server
│   ├── rag.py                  # Pipeline RAG (query → retrieval → LLM)
│   ├── ingest.py               # PDF → ChromaDB (hanya jika re-ingest)
│   ├── parser.py               # Docling PDF parser
│   ├── chunker.py              # 3-tier chunking strategy
│   ├── metadata.py             # Metadata extraction
│   ├── embedder.py             # BGE-M3 embedding wrapper
│   ├── vectorstore.py          # ChromaDB store/load
│   ├── prompt.py               # System prompt + guardrail
│   ├── config.py               # Konfigurasi sistem
│   ├── utils.py                # Logger & utility functions
│   ├── requirements.txt        # Daftar dependency Python
│   ├── chroma_db/              # Persistent vector database (247 chunks)
│   └── data/
│       └── Panduan-TA-TIF-2020.pdf
│
├── frontend/                   # Frontend Vue 3
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── components/
│   │   │   ├── ChatArea.vue
│   │   │   ├── Sidebar.vue
│   │   │   ├── SourceDoc.vue
│   │   │   ├── SuggestedChips.vue
│   │   │   └── WelcomeScreen.vue
│   │   └── composables/
│   │       └── useChat.js
│   ├── index.html
│   ├── vite.config.js          # Proxy /api → localhost:8000
│   └── package.json
│
└── docs/                       # Dokumentasi tambahan