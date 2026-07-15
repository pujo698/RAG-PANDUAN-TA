# LAPORAN TUGAS KELOMPOK — RAG BUKU PANDUAN TUGAS AKHIR

**Mata Kuliah:** Artificial Intelligence  
**Topik:** Panduan Tugas Akhir Teknik Informatika UNISSULA  
**Kelompok:** [Nama Anggota 1] (NIM), [Nama Anggota 2] (NIM), [Nama Anggota 3] (NIM)

---

## BAB I: PENDAHULUAN

### 1.1 Latar Belakang

Mahasiswa Teknik Informatika UNISSULA sering menghadapi kendala dalam memahami prosedur, persyaratan, dan format penulisan Tugas Akhir (TA). Informasi yang dibutuhkan tersebar di dalam dokumen **Buku Panduan Tugas Akhir Teknik Informatika** sepanjang 86 halaman dalam format PDF. Mencari informasi spesifik seperti "berapa minimal SKS untuk TA?" atau "bagaimana alur seminar proposal?" secara manual memakan waktu dan tidak efisien.

Untuk mengatasi masalah tersebut, sistem **Retrieval-Augmented Generation (RAG)** dibangun. RAG adalah pendekatan yang menggabungkan *information retrieval* (pencarian dokumen relevan) dengan *text generation* (LLM) untuk menghasilkan jawaban faktual berdasarkan isi dokumen. Sistem ini memungkinkan mahasiswa bertanya dalam bahasa alami dan mendapatkan jawaban akurat yang bersumber langsung dari buku panduan, **tanpa mengada-ngada (halusinasi)**.

### 1.2 Tujuan

1. Membangun pipeline RAG yang memproses Buku Panduan TA menjadi database vektor yang dapat dicari.
2. Menghasilkan sistem tanya-jawab berbasis dokumen dengan LLM lokal (Ollama) yang anti-halusinasi.
3. Menyediakan antarmuka pengguna (UI) yang intuitif untuk mengakses informasi TA.
4. Mengevaluasi kualitas retrieval menggunakan metrik similarity score dan RAGAS.

### 1.3 Dokumen Sumber

- **Dokumen:** Buku Panduan Tugas Akhir Program Studi Teknik Informatika UNISSULA
- **Format:** PDF, 86 halaman, text-based
- **Isi:** Persyaratan, prosedur, format penulisan, lampiran, log book, RPS

---

## BAB II: ARSITEKTUR PIPELINE

### 2.1 Diagram Alur

```
┌──────────────────────────────────────────────────────────────────┐
│                        INGEST PIPELINE                           │
│                                                                  │
│  PDF (86 halaman)                                                │
│      │                                                           │
│      ▼                                                           │
│  Docling Parser (parser.py)                                      │
│  • PyPdfium2Backend — ringan, tanpa rendering gambar besar       │
│  • Output: ParsedDocument (2140 items, 214 headings, 86 halaman) │
│      │                                                           │
│      ▼                                                           │
│  Chunker (chunker.py)                                            │
│  • Tier 1: Heading-based chunking                                │
│  • Tier 2: Semantic splitting (paragraph boundaries)             │
│  • Tier 3: RecursiveCharacterTextSplitter (fallback)             │
│  • Flowchart & tabel → chunk mandiri                             │
│      │                                                           │
│      ▼                                                           │
│  Metadata Generator (metadata.py)                                │
│  • chapter, section, content_type, keywords, chunk_id            │
│      │                                                           │
│      ▼                                                           │
│  BGE-M3 Embedding (embedder.py)                                  │
│  • 1024 dimensi, normalized                                      │
│      │                                                           │
│      ▼                                                           │
│  ChromaDB (vectorstore.py)                                       │
│  • Persistent storage: ./chroma_db                               │
│  • 247 chunks tersimpan                                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        QUERY PIPELINE                             │
│                                                                  │
│  User Question (UI)                                              │
│      │                                                           │
│      ▼                                                           │
│  FastAPI Backend (app.py) — POST /api/ask                        │
│      │                                                           │
│      ▼                                                           │
│  BGE-M3 Embedding Query                                          │
│      │                                                           │
│      ▼                                                           │
│  ChromaDB similarity_search_with_score (Top-K=5)                 │
│      │                                                           │
│      ▼                                                           │
│  Context + System Prompt → Ollama LLM (llama3.2)                 │
│      │                                                           │
│      ▼                                                           │
│  Answer + Source Documents + Similarity Scores                   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Tech Stack

| Komponen | Teknologi | Alasan Pemilihan |
|----------|-----------|-----------------|
| PDF Parser | **Docling** + PyPdfium2Backend | Deteksi struktur dokumen (heading, tabel, list), lebih ringan dari OCR-based parsing |
| Framework RAG | **LangChain** 1.3.13 | Integrasi native dengan ChromaDB, HuggingFace, dan Ollama |
| Text Splitter | **RecursiveCharacterTextSplitter** | Digunakan sebagai tier-3 fallback. Tier 1-2 menggunakan heading-based dan semantic splitting |
| Embedding | **BAAI/bge-m3** | Multilingual (100+ bahasa termasuk Indonesia), 1024 dimensi, performa SOTA |
| Vector DB | **ChromaDB** 1.5.9 | Persistent storage lokal, metadata filtering, integrasi LangChain |
| LLM | **Ollama + llama3.2** | Open-source, berjalan 100% lokal, 2 GB VRAM (muat penuh di GPU GTX 1650) |
| Backend | **FastAPI** | Ringan, async-native, CORS support |
| Frontend | **Vue 3 + Vite** | UI interaktif dengan proxy ke backend |

---

## BAB III: IMPLEMENTASI & PREVIEW DATA

### 3.1 Parsing PDF dengan Docling

Sistem menggunakan **Docling** dengan `PyPdfium2Backend` untuk mengekstrak struktur dokumen. Alasan memilih backend ini: `DoclingParseDocumentBackend` membutuhkan RAM besar karena mengkonversi setiap halaman menjadi gambar untuk layout analysis, menyebabkan `std::bad_alloc`. `PyPdfium2Backend` mengekstrak teks langsung tanpa rendering gambar besar.

**Konfigurasi Pipeline:**
```python
PdfPipelineOptions(
    do_ocr=False,               # PDF text-based
    do_table_structure=False,
    images_scale=0.5,
    layout_batch_size=1,
)
```

**Hasil Parsing:**
- Total halaman: 86
- Total elemen: 2.140 items
- Heading terdeteksi: 214
- Tabel: 23
- List items: 276
- Gambar: 103

### 3.2 Strategi Chunking (3-Tier)

Chunking menggunakan strategi bertingkat yang mengutamakan struktur dokumen:

**Tier 1 — Heading-based Chunking (Utama)**
Setiap heading menjadi satu chunk. Konten di bawah heading dikumpulkan menjadi satu kesatuan hingga heading berikutnya. Jika chunk ≤ 1000 token, langsung menjadi satu chunk.

**Tier 2 — Semantic Chunking**
Untuk subbab panjang (> 1000 token), dilakukan pemecahan berdasarkan paragraf (double newline). Paragraf berdekatan dikelompokkan selama total token di bawah threshold.

**Tier 3 — RecursiveCharacterTextSplitter (Fallback)**
Jika semantic chunk masih > 3200 karakter, digunakan `RecursiveCharacterTextSplitter`:
```python
RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " "],
)
```

**Parameter Chunking:**
| Parameter | Nilai | Alasan |
|-----------|-------|--------|
| `chunk_size` | 800 karakter (fallback) | Cukup untuk 1 paragraf + heading, tidak terlalu besar untuk embedding |
| `chunk_overlap` | 100 karakter | Menjaga kontinuitas antar chunk, tidak kehilangan konteks di batas potongan |
| `MAX_TOKENS_BEFORE_SEMANTIC` | 1000 token | Mayoritas section di panduan TA pendek (1-2 paragraf) |
| `MAX_CHARS_BEFORE_FALLBACK` | 3200 karakter | Hanya 5 chunk yang perlu split Recursive |

**Penanganan Khusus:**
- **Flowchart** → chunk mandiri dengan `content_type = "flowchart"` (8 flowchart terdeteksi)
- **Tabel** → chunk mandiri format markdown dengan `content_type = "tabel"` (30 tabel)
- **Pre-matter** → dilewati (cover, tim penyusun, dll.)

### 3.3 Hasil Chunking

**Total: 247 chunks**

**Distribusi per Content Type:**
| Content Type | Jumlah | Persentase |
|-------------|--------|------------|
| aturan | 57 | 23.1% |
| lampiran | 44 | 17.8% |
| penulisan | 34 | 13.8% |
| persyaratan | 30 | 12.1% |
| tabel | 30 | 12.1% |
| prosedur | 27 | 10.9% |
| definisi | 9 | 3.6% |
| flowchart | 8 | 3.2% |
| visi_misi | 6 | 2.4% |
| jadwal | 2 | 0.8% |

**Distribusi per Chapter:**
| Chapter | Jumlah |
|---------|--------|
| LAMPIRAN | 87 |
| BAB I — Tugas Akhir | 49 |
| BAB IV — RPS dan Log Book | 47 |
| BAB II — Sistematika Proposal | 19 |
| BAB III — Sistematika Laporan | 17 |
| BAB V — Template Bab Laporan | 17 |
| Front Matter | 11 |

### 3.4 Preview Chunk

Contoh chunk `bab1_1_4_1_001`:

```
Chapter: BAB I — TUGAS AKHIR
Section: 1.4.1 — Mahasiswa
Content Type: persyaratan
Keywords: 130 SKS, IPK ≥ 2.50, Metodologi Penelitian, Tugas Akhir
Page: 13
Length: 487 chars

1.4.1 Mahasiswa

Secara akademik mahasiswa dapat mengikuti mata kuliah TA
jika memenuhi persyaratan:
• Lulus MK Metodologi Penelitian
• Minimal 130 SKS
• IPK ≥ 2.50
```

### 3.5 Embedding Model

**BAAI/bge-m3:**
- Dimensi: 1024
- Multilingual: 100+ bahasa (termasuk Indonesia)
- Max Sequence: 8192 token
- Normalisasi: `normalize_embeddings=True`
- Device: **CUDA (NVIDIA GTX 1650, 4 GB VRAM)**

### 3.6 Vector Database

**ChromaDB — Persistent Storage:**
- Direktori: `./chroma_db`
- Collection: `panduan_ta`
- Total chunks: 247
- Batch insert: 50 dokumen per batch

### 3.7 System Prompt Guardrail (Anti-Halusinasi)

```python
SYSTEM_PROMPT = """Kamu adalah asisten AI yang bertugas membantu mahasiswa Teknik Informatika
UNISSULA memahami Buku Panduan Tugas Akhir.

Aturan penting:
1. Jawab pertanyaan HANYA berdasarkan konteks yang diberikan di bawah.
2. Jika informasi tidak ditemukan dalam konteks, katakan dengan sopan:
   "Maaf, informasi tersebut tidak terdapat pada Buku Panduan Tugas Akhir."
3. Jangan mengarang, menebak, atau menggunakan pengetahuan di luar konteks yang diberikan.
4. Gunakan Bahasa Indonesia yang jelas dan mudah dipahami.
5. Jika relevan, sebutkan BAB atau bagian dari buku panduan sebagai referensi.
6. Jawaban harus akurat dan langsung ke inti pertanyaan.
7. Jika pertanyaan tidak berhubungan dengan Tugas Akhir atau Buku Panduan,
   arahkan kembali ke topik Tugas Akhir.
"""
```

### 3.8 Parameter LLM

| Parameter | Nilai | Alasan |
|-----------|-------|--------|
| `LLM_MODEL` | `llama3.2` | 2.0 GB, muat penuh di GPU GTX 1650, performa lebih cepat dari llama3 (8B) |
| `LLM_TEMPERATURE` | `0.0` | Output deterministik, tidak kreatif — penting untuk jawaban faktual |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server lokal |
| `TOP_K` | `5` | 5 dokumen teratas cukup untuk cakupan konteks tanpa noise |

### 3.9 User Interface

Sistem menggunakan **Vue 3 + Vite** sebagai frontend dengan fitur:
- Input pertanyaan natural language
- Markdown rendering untuk jawaban (heading, list, bold)
- Panel "Sumber Dokumen" dengan halaman, chapter, section, content type, dan **similarity score (%)**
- Suggested chips untuk pertanyaan umum
- Dark theme

---

## BAB IV: EVALUASI & UJI COBA

### 4.1 Tabel Uji Coba — Pertanyaan Sah vs Jebakan

| No | Pertanyaan | Jenis | Jawaban Sistem | Halaman Sumber | Skor Relevansi | Status |
|----|-----------|-------|---------------|----------------|----------------|--------|
| 1 | "Apa saja persyaratan akademik mahasiswa untuk mengikuti Tugas Akhir?" | Sah | Lulus MK Metodologi Penelitian, minimal 130 SKS, IPK ≥ 2.50 | 13 | 0.92 | ✅ |
| 2 | "Berapa minimal SKS yang harus ditempuh untuk mengambil Tugas Akhir?" | Sah | Minimal 130 SKS | 13 | 0.95 | ✅ |
| 3 | "Bagaimana tahapan pelaksanaan Tugas Akhir?" | Sah | 5 tahap: Pengajuan Judul, Seminar Proposal, Seminar Kemajuan, Sidang TA, Pasca Sidang | 7-16 | 0.88 | ✅ |
| 4 | "Apa saja komponen penilaian Sidang Tugas Akhir beserta bobotnya?" | Sah | Laporan TA: 35%, Presentasi: 30%, Produk: 35% | 16 | 0.91 | ✅ |
| 5 | "Berapa lama waktu revisi Tugas Akhir setelah sidang?" | Sah | Hingga 15 hari kerja | 16 | 0.93 | ✅ |
| 6 | "Apa saja sistematika penulisan laporan Tugas Akhir?" | Sah | BAB I-V, Daftar Pustaka, Lampiran | 24-26 | 0.89 | ✅ |
| 7 | "Apa visi Program Studi Teknik Informatika UNISSULA?" | Sah | Menjadi prodi unggulan pengembangan IPTEK berkontribusi internasional 2024... | 2 | 0.86 | ✅ |
| 8 | "Apa definisi Tugas Akhir menurut panduan?" | Sah | Karya ilmiah hasil penelitian/pemecahan masalah secara sistematis... | 5 | 0.94 | ✅ |
| 9 | "Bagaimana prosedur Seminar Proposal Tugas Akhir?" | Sah | Mahasiswa mempresentasikan latar belakang, rumusan masalah, tujuan... | 9 | 0.87 | ✅ |
| 10 | "Apa saja kelengkapan administrasi untuk pendaftaran Seminar Proposal?" | Sah | Transkrip Nilai (130 SKS), sertifikat TOEFL... | 59 | 0.85 | ✅ |
| 11 | "Siapa presiden Indonesia tahun 2025?" | **Jebakan** | "Maaf, informasi tersebut tidak terdapat pada Buku Panduan Tugas Akhir." | - | 0.0 | ✅ Ditolak |
| 12 | "Bagaimana cara membuat nasi goreng?" | **Jebakan** | "Maaf, pertanyaan Anda tidak berhubungan dengan Tugas Akhir..." | - | 0.0 | ✅ Ditolak |
| 13 | "Siapa pemenang Piala Dunia 2022?" | **Jebakan** | "Maaf, informasi tersebut tidak terdapat pada Buku Panduan Tugas Akhir." | - | 0.0 | ✅ Ditolak |
| 14 | "Berapa harga Bitcoin hari ini?" | **Jebakan** | "Maaf, pertanyaan Anda tidak berhubungan dengan Tugas Akhir..." | - | 0.0 | ✅ Ditolak |
| 15 | "Apa itu teori relativitas Einstein?" | **Jebakan** | "Maaf, informasi tersebut tidak terdapat pada Buku Panduan Tugas Akhir." | - | 0.0 | ✅ Ditolak |

**Hasil:**
- **Pertanyaan Sah:** 10/10 dijawab dengan benar (akurasi 100%)
- **Pertanyaan Jebakan:** 5/5 ditolak (akurasi 100%)
- **Rata-rata relevansi untuk pertanyaan sah:** 0.90

### 4.2 Uji Validitas Retrieval — Similarity Score

Sistem menggunakan `similarity_search_with_score` dari ChromaDB untuk mengembalikan nilai kedekatan semantik. L2 distance dikonversi menjadi relevance score (0-1):

```
Relevance = max(0.0, 1.0 - (distance / 2.0))
```

Contoh hasil retrieval untuk pertanyaan "Apa syarat mengambil Tugas Akhir?":

| Peringkat | Chunk ID | Chapter | Section | Skor Relevansi |
|-----------|----------|---------|---------|----------------|
| #1 | bab1_1_4_1_001 | BAB I | 1.4.1 | 0.92 |
| #2 | bab1_1_4_2_001 | BAB I | 1.4.2 | 0.87 |
| #3 | bab1_1_4_3_001 | BAB I | 1.4.3 | 0.74 |
| #4 | lampiran_1_005 | LAMPIRAN | - | 0.52 |
| #5 | bab1_1_1_001 | BAB I | 1.1 | 0.48 |

Dokumen paling relevan (score 0.92) berada di BAB I section 1.4.1 — tepat sesuai dengan isi persyaratan mahasiswa.

### 4.3 Analisis Bottleneck

| Bottleneck | Penyebab | Dampak | Solusi |
|------------|----------|--------|--------|
| Latensi LLM inference | llama3.2 2B berjalan di GPU 4GB | ~5-15 detik per query | Upgrade GPU, atau gunakan gemma3:1b (~2-5 detik) |
| Embedding model loading | BGE-M3 2.27 GB dimuat saat startup | ~30 detik cold start | Caching, model tetap di memori |
| Chunking pada section besar | BAB I section 1.6 (Sidang) > 3200 chars | 5 chunk fallback ke RecursiveSplitter | Fine-tune threshold |
| Docling parsing lambat | PDF 86 halaman | ~30-60 detik saat ingest | Hanya dijalankan sekali (re-ingest) |

---

## BAB V: KESIMPULAN & TANTANGAN

### 5.1 Kesimpulan

1. **Sistem RAG berhasil dibangun** menggunakan LangChain, ChromaDB, BGE-M3 embedding, dan Ollama LLM untuk memproses Buku Panduan Tugas Akhir 86 halaman.

2. **Pipeline chunking 3-tier** (heading-based → semantic → Recursive fallback) menghasilkan 247 chunks dengan metadata lengkap (chapter, section, content_type, keywords).

3. **Prompt guardrail berhasil** mencegah halusinasi: 100% pertanyaan jebakan ditolak dengan respons sopan.

4. **Similarity score** memberikan transparansi pada kualitas retrieval — dokumen paling relevan konsisten memiliki score ≥ 0.85 untuk pertanyaan sah.

5. **Sistem berjalan 100% lokal** tanpa biaya API, menggunakan Ollama + llama3.2 (2 GB, muat di GPU GTX 1650).

### 5.2 Tantangan

1. **Keterbatasan GPU:** GTX 1650 4GB membatasi pilihan LLM ke model kecil (≤ 3B parameter). Model lebih besar seperti llama3 (8B) jatuh ke CPU inference.

2. **Python 3.14 compatibility:** Python versi terbaru belum didukung penuh oleh PyTorch wheel stabil, memerlukan nightly build untuk CUDA.

3. **Docling dependency:** Library parsing PDF (Docling) besar (~1 GB) dan hanya dibutuhkan saat ingest, tidak untuk runtime QA.

4. **Evaluasi RAGAS terbatas:** Evaluasi dengan RAGAS membutuhkan LLM judge — hasil bervariasi tergantung model yang digunakan. Retrieval accuracy tanpa LLM lebih objektif.

5. **Bahasa Indonesia:** BGE-M3 mendukung multilingual, namun akurasi retrieval untuk teks berbahasa Indonesia perlu pengujian lebih lanjut dengan dataset benchmark.

---

## LAMPIRAN

### A. Struktur Proyek

```
RAG-PANDUAN-TA/
├── code/
│   ├── app.py              # FastAPI backend
│   ├── rag.py              # RAG query pipeline
│   ├── ingest.py           # PDF → ChromaDB ingest
│   ├── parser.py           # Docling PDF parser
│   ├── chunker.py          # 3-tier chunking strategy
│   ├── metadata.py         # Metadata extraction
│   ├── embedder.py         # BGE-M3 embedding wrapper
│   ├── vectorstore.py      # ChromaDB store/load
│   ├── prompt.py           # System prompt guardrail
│   ├── config.py           # Konfigurasi sistem
│   ├── utils.py            # Logger & utilities
│   ├── chroma_db/          # Persistent vector DB (247 chunks)
│   └── data/
│       └── Panduan-TA-TIF-2020.pdf
├── frontend/               # Vue 3 + Vite UI
│   └── src/
│       ├── App.vue
│       ├── components/
│       │   ├── ChatArea.vue
│       │   ├── Sidebar.vue
│       │   ├── SourceDoc.vue
│       │   ├── SuggestedChips.vue
│       │   └── WelcomeScreen.vue
│       └── composables/
│           └── useChat.js
├── docs/
├── DOCUMENTATION.md        # Dokumentasi teknis
├── evaluation.ipynb        # Notebook evaluasi RAGAS
├── SETUP.md                # Panduan instalasi
└── LAPORAN.md              # Laporan ini
```

### B. Cara Menjalankan

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd code && python app.py          # http://localhost:8000

# Terminal 3: Frontend
cd frontend && npm run dev         # http://localhost:5173