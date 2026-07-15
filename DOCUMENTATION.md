# Dokumentasi Sistem RAG — Buku Panduan Tugas Akhir

## Daftar Isi

- [1. Gambaran Umum Sistem](#1-gambaran-umum-sistem)
- [2. Teknologi yang Digunakan](#2-teknologi-yang-digunakan)
- [3. Arsitektur Pipeline](#3-arsitektur-pipeline)
- [4. Struktur Proyek](#4-struktur-proyek)
- [5. Parsing PDF dengan Docling](#5-parsing-pdf-dengan-docling)
- [6. Strategi Chunking](#6-strategi-chunking)
- [7. Metadata Generation](#7-metadata-generation)
- [8. Embedding Model](#8-embedding-model)
- [9. Vector Database](#9-vector-database)
- [10. Cara Menjalankan](#10-cara-menjalankan)
- [11. Hasil Ingest](#11-hasil-ingest)

---

## 1. Gambaran Umum Sistem

Sistem ini adalah pipeline **Retrieval-Augmented Generation (RAG)** yang dibangun untuk memproses dokumen **Buku Panduan Tugas Akhir Teknik Informatika UNISSULA** (86 halaman, format PDF). Tujuannya adalah membantu mahasiswa memperoleh informasi seputar proses Tugas Akhir melalui *natural language query*, seperti:

- Apa syarat mengambil Tugas Akhir?
- Berapa minimal SKS dan IPK?
- Bagaimana alur Seminar Proposal?
- Bagaimana prosedur Sidang Tugas Akhir?
- Apa format Proposal TA?

Pipeline ini berfokus pada tahap **ingest** — yaitu mengubah dokumen PDF menjadi representasi vektor yang tersimpan di database, siap digunakan untuk retrieval.

---

## 2. Teknologi yang Digunakan

| Komponen | Teknologi | Versi | Peran |
|----------|-----------|-------|-------|
| Bahasa | Python | 3.11 | Bahasa pemrograman utama |
| PDF Parser | **Docling** | ≥2.100 | Parsing PDF dengan struktur heading, list, tabel |
| Framework | **LangChain** | ≥1.3 | Orkestrasi Document, TextSplitter, VectorStore |
| Embedding | **BAAI/bge-m3** | via HuggingFace | Model embedding multilingual (termasuk Bahasa Indonesia) |
| Vector DB | **ChromaDB** | ≥1.3 | Persistent vector database |
| ML Runtime | PyTorch + Transformers | ≥2.0 | Backend untuk embedding model |
| Text Splitter | LangChain Text Splitters | ≥1.1 | `RecursiveCharacterTextSplitter` sebagai fallback |

### Mengapa Teknologi Ini Dipilih?

**Docling vs PyPDF/pdfplumber:**
Docling mampu mendeteksi **struktur dokumen** (heading, sub-heading, list, tabel, gambar, caption) secara otomatis menggunakan layout analysis model. Parser konvensional seperti PyPDF2 atau pdfplumber hanya mengekstrak teks mentah tanpa informasi struktur, sehingga tidak memungkinkan heading-based chunking.

**BGE-M3 vs model embedding lain:**
BGE-M3 adalah model embedding multilingual yang mendukung Bahasa Indonesia dengan baik. Model ini menghasilkan vektor 1024 dimensi dan mendukung multiple retrieval modes (dense, sparse, multi-vector). Normalisasi embedding diaktifkan untuk meningkatkan kualitas cosine similarity search.

**ChromaDB vs FAISS/Pinecone:**
ChromaDB dipilih karena mendukung persistent storage secara lokal (tanpa server eksternal), terintegrasi langsung dengan LangChain, dan menyimpan metadata bersama vektor sehingga memungkinkan metadata filtering saat retrieval.

---

## 3. Arsitektur Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                        ingest.py                             │
│                      (Entry Point)                           │
└──────────────────────┬───────────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │     STEP 1: PARSING     │
          │       parser.py         │
          │                         │
          │  PDF ──► Docling ──►    │
          │    PyPdfiumBackend      │
          │         │               │
          │         ▼               │
          │   ParsedDocument        │
          │   (2140 items,          │
          │    214 headings,        │
          │    86 pages)            │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │    STEP 2: CHUNKING     │
          │      chunker.py         │
          │                         │
          │  Tier 1: Heading-based  │
          │  Tier 2: Semantic       │
          │  Tier 3: Recursive      │
          │         │               │
          │    metadata.py          │
          │  (chapter, section,     │
          │   content_type,         │
          │   keywords, chunk_id)   │
          │         │               │
          │         ▼               │
          │  List[Document] (247)   │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │  STEP 3: EMBED & STORE  │
          │  embedder.py            │
          │  vectorstore.py         │
          │                         │
          │  Document.page_content  │
          │      │                  │
          │      ▼                  │
          │  BGE-M3 Embedding       │
          │  (1024 dim, normalized) │
          │      │                  │
          │      ▼                  │
          │  ChromaDB               │
          │  (./chroma_db)          │
          └─────────────────────────┘
```

---

## 4. Struktur Proyek

```
code/
│
├── ingest.py            # Entry point — orkestrasi seluruh pipeline
├── parser.py            # Docling PDF parser → ParsedDocument
├── chunker.py           # 3-tier chunking → List[Document]
├── metadata.py          # Metadata generator (chapter, section, keywords, dll.)
├── embedder.py          # BGE-M3 embedding model wrapper
├── vectorstore.py       # ChromaDB persistent storage
├── utils.py             # Logger, text cleaning, token counting
│
├── data/
│   └── Panduan-TA-TIF-2020.pdf    # Dokumen sumber
│
├── chroma_db/           # Persistent vector database (hasil ingest)
│
└── requirements.txt     # Daftar dependency
```

Setiap modul memiliki **single responsibility** yang jelas:

| Modul | Tanggung Jawab |
|-------|---------------|
| `parser.py` | Hanya parsing PDF → struktur data internal (`ParsedDocument`) |
| `chunker.py` | Hanya chunking → `List[Document]` dari LangChain |
| `metadata.py` | Hanya generate metadata (chapter, section, content_type, keywords, chunk_id) |
| `embedder.py` | Hanya inisialisasi embedding model |
| `vectorstore.py` | Hanya interaksi dengan ChromaDB (store & load) |
| `utils.py` | Fungsi utilitas bersama (logger, cleaning, sanitization) |
| `ingest.py` | Orkestrasi — memanggil modul lain secara berurutan |

---

## 5. Parsing PDF dengan Docling

### Backend yang Digunakan

```python
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
```

Sistem menggunakan `PyPdfiumDocumentBackend` alih-alih default `DoclingParseDocumentBackend`. Alasan:

- `DoclingParseDocumentBackend` membutuhkan memori sangat besar untuk preprocessing halaman (mengkonversi setiap halaman PDF menjadi gambar resolusi tinggi untuk layout analysis), menyebabkan **`std::bad_alloc`** pada mesin dengan RAM terbatas (24GB)
- `PyPdfiumDocumentBackend` lebih ringan karena mengekstrak teks langsung dari PDF layer tanpa rendering gambar berukuran besar, namun tetap memanfaatkan layout model Docling untuk deteksi struktur

### Konfigurasi Pipeline

```python
PdfPipelineOptions(
    do_ocr=False,              # PDF sudah text-based, OCR tidak diperlukan
    do_table_structure=False,   # Tabel diambil sebagai markdown langsung
    images_scale=0.5,           # Skala gambar dikecilkan untuk hemat memori
    layout_batch_size=1,        # Batch kecil untuk stabilitas memori
)
```

### Elemen yang Terdeteksi Docling

| Label | Jumlah | Keterangan |
|-------|--------|------------|
| `text` | ~1501 | Paragraf teks biasa |
| `list_item` | ~276 | Item daftar (ordered/unordered) |
| `section_header` | 214 | Heading dan sub-heading |
| `picture` | ~103 | Gambar, flowchart, logo |
| `table` | 23 | Tabel data |
| `caption` | 9 | Caption gambar (termasuk flowchart) |
| `document_index` | 4 | Daftar isi |
| `footnote` | 8 | Catatan kaki |

### Struktur Data Output

```python
@dataclass
class ParsedItem:
    index: int              # urutan dalam dokumen
    label: str              # section_header, text, list_item, table, picture, caption
    level: int              # level nesting dari Docling tree
    text: str               # konten teks
    page: int               # nomor halaman (1-indexed)
    is_heading: bool        # True jika section_header
    table_markdown: str     # representasi markdown untuk tabel

@dataclass
class ParsedDocument:
    source: str             # nama file PDF
    items: list[ParsedItem] # seluruh elemen terstruktur
    total_pages: int        # total halaman
```

---

## 6. Strategi Chunking

Chunking menggunakan **strategi bertingkat (3-tier)** yang mengutamakan struktur dokumen, bukan jumlah karakter.

### Tier 1 — Heading-based Chunking (Utama)

Setiap heading menjadi satu chunk. Seluruh konten di bawah heading (paragraf, list, teks) dikumpulkan menjadi satu kesatuan hingga heading berikutnya ditemukan.

```
┌─────────────────────────────────────┐
│ 1.4.1 Mahasiswa                     │  ← heading menjadi judul chunk
│                                     │
│ Secara akademik mahasiswa dapat     │
│ mengikuti mata kuliah TA jika       │
│ memenuhi persyaratan:               │
│ • Lulus MK Metodologi Penelitian    │  ← list items digabung
│ • Minimal 130 SKS                   │
│ • IPK ≥ 2.50                        │
└─────────────────────────────────────┘
                 ↓
            1 chunk utuh
```

**Threshold:** Jika chunk ≤ 1000 token → langsung menjadi 1 chunk (mayoritas kasus).

### Tier 2 — Semantic Chunking

Jika satu subbab menghasilkan chunk > 1000 token, dilakukan pemecahan berdasarkan **batas paragraf** (double newline). Tidak pernah memotong di tengah kalimat.

```
┌─────────────────────────────────────┐
│ 3.2 Format Penulisan (>1000 token)  │
│                                     │
│ [Paragraf tentang margin...]        │ → Chunk A
│                                     │
│ [Paragraf tentang font...]          │ → Chunk B
│                                     │
│ [Paragraf tentang spasi...]         │ → Chunk C
└─────────────────────────────────────┘
```

Paragraf yang berdekatan dikelompokkan bersama selama total token masih di bawah threshold.

### Tier 3 — RecursiveCharacterTextSplitter (Fallback)

Jika hasil semantic chunk masih terlalu besar (> 3200 karakter), digunakan `RecursiveCharacterTextSplitter` dari LangChain sebagai fallback terakhir.

```python
RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " "],
)
```

Splitter ini memecah teks secara hierarkis: pertama di batas paragraf, lalu batas baris, lalu batas kalimat, dan terakhir di spasi.

### Penanganan Khusus

#### Flowchart → Chunk Mandiri

Flowchart diidentifikasi melalui **caption item** dari Docling (misalnya `"Gambar 1.1 Flowchart Pengajuan Judul Tugas Akhir"`). Setiap flowchart menjadi chunk tersendiri dengan `content_type = "flowchart"`.

Flowchart yang terdeteksi:
- Gambar 1.1 Flowchart Pengajuan Judul Tugas Akhir
- Gambar 1.2 Flowchart Seminar Proposal
- Gambar 1.3 Flowchart Seminar Kemajuan Tugas Akhir
- Gambar 1.4 Flowchart Sidang Tugas Akhir / Ujian Sarjana
- Gambar 1.5 Alur Sidang Tugas Akhir

#### Tabel → Chunk Mandiri (Format Markdown)

Tabel yang terdeteksi Docling diekspor sebagai **markdown table** dan dijadikan chunk tersendiri dengan `content_type = "tabel"`. Format markdown dipilih agar mudah dipahami LLM saat retrieval.

```markdown
| NO | KELENGKAPAN ADMINISTRASI | PEMERIKSA | TANDA TANGAN |
|----|--------------------------|-----------|--------------|
| 1  | Transkrip Nilai (130 SKS)| Sek. Prodi|              |
| 2  | Sertifikat TOEFL         | Sek. Prodi|              |
```

#### Pre-matter → Dilewati

Heading yang bersifat dekoratif (cover, nama penerbit, tim penyusun) dilewati dan tidak diproses menjadi chunk:

```python
SKIP_HEADINGS = {
    "BUKU PANDUAN & LOG BOOK BIMBINGAN",
    "TUGAS AKHIR",
    "PROGRAM STUDI TEKNIK INFORMATIKA",
    "Tim Penyusun :",
    # ... dll
}
```

---

## 7. Metadata Generation

Setiap chunk memiliki metadata lengkap yang dihasilkan secara otomatis (tanpa AI/LLM):

```python
metadata = {
    "source":        "Panduan-TA-TIF-2020.pdf",
    "page":          13,
    "chapter":       "BAB I",
    "chapter_title": "TUGAS AKHIR",
    "section":       "1.4.1",
    "section_title": "Mahasiswa",
    "document_type": "panduan_ta",
    "content_type":  "persyaratan",
    "keywords":      "130 SKS, IPK, Metodologi Penelitian, Tugas Akhir",
    "chunk_id":      "bab1_1_4_1_001",
}
```

### Detail Setiap Field

#### `source`
Nama file PDF sumber. Memungkinkan traceability ketika di masa depan terdapat lebih dari satu dokumen.

#### `page`
Nomor halaman PDF asli (1-indexed), diekstrak dari provenance info Docling.

#### `chapter` dan `chapter_title`
Dideteksi menggunakan regex pattern:

```python
BAB_PATTERN = re.compile(r"BAB\s+(I{1,3}V?|IV|V?I{0,3})\b", re.IGNORECASE)
```

Contoh: `"BAB I TUGAS AKHIR"` → `chapter="BAB I"`, `chapter_title="TUGAS AKHIR"`.

Lampiran dideteksi secara terpisah:

```python
LAMPIRAN_PATTERN = re.compile(r"LAMPIRAN\s*[-]?\s*(\d+)", re.IGNORECASE)
```

#### `section` dan `section_title`
Dideteksi dari heading bernomor:

```python
SECTION_PATTERN = re.compile(r"^(\d+\.\d+(?:\.\d+)?)\s+")
```

Contoh: `"1.4.1 Mahasiswa"` → `section="1.4.1"`, `section_title="Mahasiswa"`.

#### `document_type`
Selalu `"panduan_ta"`. Disiapkan untuk skenario multi-dokumen di masa depan.

#### `content_type`
Klasifikasi otomatis berdasarkan keyword/regex pada heading dan body text:

| content_type | Contoh Trigger Keywords |
|-------------|------------------------|
| `persyaratan` | persyaratan, syarat, minimal SKS, IPK |
| `prosedur` | prosedur, tahapan, pelaksanaan, pendaftaran |
| `penulisan` | penulisan, format, sistematika, tata cara |
| `flowchart` | flowchart, diagram alir (hanya di heading) |
| `tabel` | tabel, jadwal kegiatan |
| `lampiran` | lampiran, formulir, surat pernyataan, log book |
| `jadwal` | jadwal, RPS, rencana pembelajaran |
| `visi_misi` | visi, misi (bukan "revisi") |
| `definisi` | definisi, pengertian, tujuan |
| `aturan` | tata tertib, etika, pelanggaran, sanksi, revisi |

Urutan rules penting — rule yang lebih spesifik dievaluasi terlebih dahulu.

#### `keywords`
Diekstrak menggunakan regex patterns untuk istilah akademik penting:

```python
KEYWORD_PATTERNS = [
    r"IPK\s*[≥>=<]?\s*[\d.]+",    # "IPK ≥ 2.50"
    r"\d+\s*SKS",                   # "130 SKS"
    r"Tugas\s+Akhir",              # "Tugas Akhir"
    r"Seminar\s+Proposal",         # "Seminar Proposal"
    r"Dosen\s+Pembimbing",         # "Dosen Pembimbing"
    # ... dan 20+ pattern lainnya
]
```

Ditambah deteksi otomatis proper nouns (istilah multi-kata dengan kapital).

Maksimal 10 keywords per chunk.

#### `chunk_id`
Format unik dan deterministik:

```
bab1_1_4_1_001     → BAB I, section 1.4.1, chunk ke-1
bab2_2_2_003       → BAB II, section 2.2, chunk ke-3
lampiran_3_001     → LAMPIRAN 3, chunk ke-1
front_002          → Front matter, chunk ke-2
```

---

## 8. Embedding Model

### BAAI/bge-m3

| Aspek | Detail |
|-------|--------|
| Model | `BAAI/bge-m3` |
| Dimensi | 1024 |
| Multilingual | ✅ (100+ bahasa termasuk Indonesia) |
| Max Sequence | 8192 token |
| Normalisasi | `normalize_embeddings=True` |
| Interface | `langchain-huggingface` → `HuggingFaceEmbeddings` |

### Apa yang Di-embedding

- ✅ `page_content` — konten teks chunk
- ❌ `metadata` — **tidak** ikut di-embedding

Metadata disimpan bersama vektor di ChromaDB dan digunakan untuk filtering/attribution saat retrieval, bukan sebagai bagian dari similarity search.

### Konfigurasi

```python
HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},          # atau "cuda"
    encode_kwargs={"normalize_embeddings": True},
)
```

---

## 9. Vector Database

### ChromaDB

| Aspek | Detail |
|-------|--------|
| Mode | Persistent (data tersimpan di disk) |
| Direktori | `./chroma_db` |
| Collection | `panduan_ta` |
| Interface | `langchain-chroma` → `Chroma` |
| Batch Size | 50 dokumen per batch |

### Persistensi

Database tersimpan di `./chroma_db` dan dapat dimuat ulang tanpa ingest ulang:

```python
from vectorstore import load_vectorstore
from embedder import get_embedding_model

embedding_model = get_embedding_model()
vectorstore = load_vectorstore(embedding_model, "./chroma_db")

# Langsung siap query
results = vectorstore.similarity_search("syarat tugas akhir", k=5)
```

### Sanitasi Data

- `page_content` kosong diganti dengan placeholder `"[empty content]"`
- Metadata list (seperti `keywords`) dikonversi ke string yang dipisahkan koma (ChromaDB hanya menerima `str`, `int`, `float`, `bool`)

---

## 10. Cara Menjalankan

### Instalasi

```bash
pip install -r requirements.txt
```

### Menjalankan Ingest

```bash
# Default: menggunakan data/Panduan-TA-TIF-2020.pdf → ./chroma_db
python ingest.py

# Custom path
python ingest.py --pdf path/to/file.pdf --persist-dir ./my_db

# Force re-ingest (hapus database lama)
python ingest.py --force
```

### Contoh Output

```
[INFO] ==================================================
[INFO] STEP 1: Parsing PDF with Docling
[INFO] ==================================================
[INFO] Loading PDF: Panduan-TA-TIF-2020.pdf
[INFO] Parsing document with Docling...
[INFO] Headings detected: 214
[INFO] Total items parsed: 2140
[INFO] Total pages: 86

[INFO] ==================================================
[INFO] STEP 2: Chunking document
[INFO] ==================================================
[INFO] Total chunks created: 247
[INFO]   Chunks by content_type:
[INFO]     aturan: 57
[INFO]     lampiran: 44
[INFO]     penulisan: 34
[INFO]     persyaratan: 30
[INFO]     tabel: 30
[INFO]     prosedur: 27
[INFO]     ...

[INFO] ==================================================
[INFO] STEP 3: Embedding & storing in ChromaDB
[INFO] ==================================================
[INFO] Loading embedding model: BAAI/bge-m3
[INFO] Embedding 247 chunks...
[INFO] Saving into ChromaDB...
[INFO]   Batch 1/5 (50 chunks)
[INFO]   Batch 2/5 (50 chunks)
[INFO]   ...

[INFO] ==================================================
[INFO] PIPELINE COMPLETE
[INFO] ==================================================
[INFO] Source: Panduan-TA-TIF-2020.pdf
[INFO] Chunks: 247
[INFO] Done.
```

---

## 11. Hasil Ingest

### Statistik Final

| Metrik | Nilai |
|--------|-------|
| Total halaman PDF | 86 |
| Total elemen Docling | 2140 |
| Total heading terdeteksi | 214 |
| **Total chunk** | **247** |
| Embedding dimensi | 1024 |

### Distribusi Chunk per Content Type

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

### Distribusi Chunk per Chapter

| Chapter | Jumlah |
|---------|--------|
| LAMPIRAN | 87 |
| BAB I — Tugas Akhir | 49 |
| BAB IV — RPS dan Log Book | 47 |
| BAB II — Sistematika Proposal | 19 |
| BAB III — Sistematika Laporan | 17 |
| BAB V — (template bab laporan) | 17 |
| Front Matter | 11 |
