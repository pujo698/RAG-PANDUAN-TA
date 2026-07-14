# 📚 RAG Buku Panduan Tugas Akhir Teknik Informatika UNISSULA

Sistem **Retrieval-Augmented Generation (RAG)** berbasis **LangChain**, **ChromaDB**, dan **Ollama** yang digunakan untuk menjawab pertanyaan mengenai **Buku Panduan Tugas Akhir Teknik Informatika Universitas Islam Sultan Agung**.

Sistem ini dirancang untuk membantu mahasiswa memperoleh informasi terkait persyaratan, prosedur, seminar proposal, seminar kemajuan, sidang tugas akhir, hingga sistematika penulisan laporan secara cepat dan akurat berdasarkan dokumen resmi.

---

# 🚀 Fitur

- 📄 Membaca dokumen PDF Buku Panduan Tugas Akhir
- ✂️ Chunking dokumen menggunakan RecursiveCharacterTextSplitter
- 🧠 Embedding menggunakan model HuggingFace
- 💾 Penyimpanan embedding pada ChromaDB
- 🔍 Semantic Search (Top-K Retrieval)
- 🤖 Chatbot menggunakan Ollama LLM
- 🛡️ Prompt Guardrail (Anti Hallucination)
- 📖 Menampilkan sumber jawaban
- 🌐 User Interface menggunakan Streamlit

---

# 🛠️ Tech Stack

| Teknologi | Fungsi |
|------------|--------|
| Python 3.11+ | Bahasa Pemrograman |
| Streamlit | User Interface |
| LangChain | Framework RAG |
| ChromaDB | Vector Database |
| HuggingFace Embeddings | Membuat Embedding Dokumen |
| Sentence Transformers | Model Embedding |
| Ollama | Local LLM Engine |
| PyPDF | Membaca Dokumen PDF |

---

# 📦 Library

```txt
streamlit

langchain

langchain-community

langchain-core

langchain-text-splitters

langchain-chroma

langchain-huggingface

langchain-ollama

chromadb

sentence-transformers

pypdf
```

---

# 🏗️ Arsitektur Sistem

```
PDF Buku Panduan TA
        │
        ▼
PyPDFLoader
        │
        ▼
Document Loader
        │
        ▼
Chunking
(RecursiveCharacterTextSplitter)
        │
        ▼
Embedding
(HuggingFace)
        │
        ▼
ChromaDB
(Vector Database)
        │
        ▼
Retriever
        │
        ▼
Prompt Template
        │
        ▼
Ollama
        │
        ▼
Jawaban Chatbot
```

---

# 📂 Struktur Project

```
TA-RAG/
│
├── app.py                 # Streamlit UI
├── ingest.py              # Proses indexing dokumen
├── rag.py                 # Pipeline RAG
├── config.py              # Konfigurasi sistem
├── prompt.py              # Prompt Guardrail
│
├── data/
│   └── Panduan-TA-TIF-2020.pdf
│
├── chroma_db/             # Vector Database
│
├── utils/
│   ├── loader.py
│   └── splitter.py
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Instalasi

## Clone Repository

```bash
git clone https://github.com/username/TA-RAG.git
cd TA-RAG
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🤖 Install Ollama

Install Ollama

https://ollama.com

Download model

```bash
ollama pull llama3
```

atau

```bash
ollama pull gemma3
```

Jalankan Ollama

```bash
ollama serve
```

---

# 📥 Membuat Vector Database

```bash
python ingest.py
```

Output

```
Jumlah Halaman : xx
Jumlah Chunk : xxx

Database berhasil dibuat.
```

---

# ▶️ Menjalankan Aplikasi

```bash
streamlit run app.py
```

---

# 🔍 Pipeline Retrieval-Augmented Generation (RAG)

1. Membaca dokumen PDF.
2. Memecah dokumen menjadi beberapa chunk.
3. Membuat embedding setiap chunk menggunakan HuggingFace.
4. Menyimpan embedding pada ChromaDB.
5. Mengubah pertanyaan pengguna menjadi embedding.
6. Mengambil Top-K dokumen yang paling relevan.
7. Mengirim konteks beserta pertanyaan ke LLM.
8. Menghasilkan jawaban berdasarkan dokumen.

---

# 🛡️ Anti Hallucination

Sistem menggunakan Prompt Guardrail sehingga model hanya menjawab berdasarkan isi dokumen.

Apabila informasi tidak ditemukan pada dokumen, sistem akan memberikan respons:

> "Maaf, informasi tersebut tidak terdapat pada Buku Panduan Tugas Akhir."

---

# 📈 Parameter RAG

| Parameter | Nilai |
|------------|--------|
| Chunk Size | 800 |
| Chunk Overlap | 150 |
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Retriever Top-K | 3 |
| Temperature | 0 |
| LLM | Llama 3 / Gemma 3 |

---

# 👨‍💻 Tim Pengembang

Kelompok Mata Kuliah Artificial Intelligence

Program Studi Teknik Informatika

Fakultas Teknologi Industri

Universitas Islam Sultan Agung