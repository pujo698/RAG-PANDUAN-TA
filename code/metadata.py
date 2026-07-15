"""
metadata.py — Metadata generation for document chunks.

Generates rich metadata for each chunk including:
chapter, section, content_type, keywords, and chunk_id.
"""

import re
from dataclasses import dataclass, field

from utils import setup_logger

logger = setup_logger("metadata")

# ── Content type classification rules ──────────────────────────────────

CONTENT_TYPE_RULES: list[tuple[str, list[str]]] = [
    ("flowchart", [
        r"^flowchart\b", r"^alur\b", r"^diagram\s+alir",
    ]),
    ("persyaratan", [
        r"persyaratan", r"syarat", r"ketentuan\s+(pendaftaran|administrasi)",
        r"minimal\s+sks", r"ipk\s*[≥>=]",
    ]),
    ("prosedur", [
        r"prosedur", r"tahap(an)?", r"pelaksanaan", r"proses\b",
        r"pendaftaran", r"alur\s+sidang",
    ]),
    ("penulisan", [
        r"penulisan", r"format\b", r"sistematika", r"tata\s+cara",
        r"petunjuk\s+umum", r"pengetikan", r"penomoran",
        r"margin", r"spasi", r"font", r"bahasa",
    ]),
    ("tabel", [
        r"tabel\b(?!\s+\d)", r"jadwal\s+kegiatan",
    ]),
    ("lampiran", [
        r"lampiran", r"formulir", r"lembar\s+pengesahan",
        r"surat\s+pernyataan", r"surat\s+keterangan",
        r"log\s*book", r"cover\s+cd", r"surat\s+bebas",
        r"tanda\s+tangan",
    ]),
    ("formulir", [
        r"formulir",
    ]),
    ("jadwal", [
        r"jadwal", r"rps\b", r"rencana\s+pembelajaran",
    ]),
    ("visi_misi", [
        r"(?<!re)visi\b", r"\bmisi\b", r"visi\s+dan\s+misi", r"visi\s+misi",
    ]),
    ("definisi", [
        r"definisi", r"pengertian", r"tujuan\b",
        r"fungsi\s+panduan",
    ]),
    ("aturan", [
        r"tata\s+tertib", r"etika", r"pelanggaran", r"sanksi",
        r"revisi\b", r"lulus\b", r"tidak\s+lulus", r"perbaikan",
    ]),
]


def classify_content_type(heading_text: str, body_text: str = "") -> str:
    """
    Classify the content type of a chunk based on heading and body text.
    Uses keyword/regex rules — no AI needed.
    """
    combined = f"{heading_text} {body_text}".lower()

    for content_type, patterns in CONTENT_TYPE_RULES:
        for pattern in patterns:
            if re.search(pattern, combined):
                return content_type

    return "aturan"  # default fallback


# ── Chapter/section extraction ─────────────────────────────────────────

# Matches: "BAB I", "BAB II", "BAB III", "BAB IV", etc.
BAB_PATTERN = re.compile(
    r"BAB\s+(I{1,3}V?|IV|V?I{0,3})\b",
    re.IGNORECASE,
)

# Matches: "1.1", "1.1.1", "2.3", "3.3.4", etc.
SECTION_PATTERN = re.compile(
    r"^(\d+\.\d+(?:\.\d+)?)\s+",
)

# Matches: "LAMPIRAN 1", "LAMPIRAN 10", etc.
LAMPIRAN_PATTERN = re.compile(
    r"LAMPIRAN\s*[-]?\s*(\d+)",
    re.IGNORECASE,
)


@dataclass
class ChapterInfo:
    """Tracks current chapter context during chunking."""
    chapter: str = ""            # e.g., "BAB I"
    chapter_title: str = ""      # e.g., "TUGAS AKHIR"
    section: str = ""            # e.g., "1.4"
    section_title: str = ""      # e.g., "Persyaratan Akademik"


def extract_chapter_info(heading_text: str, current: ChapterInfo) -> ChapterInfo:
    """
    Extract or update chapter/section info from a heading.
    Returns a new ChapterInfo with updated fields.
    """
    info = ChapterInfo(
        chapter=current.chapter,
        chapter_title=current.chapter_title,
        section=current.section,
        section_title=current.section_title,
    )

    text = heading_text.strip()

    # Check for BAB heading
    bab_match = BAB_PATTERN.search(text)
    if bab_match:
        roman = bab_match.group(1).upper()
        info.chapter = f"BAB {roman}"
        # Title is the text after "BAB X "
        title_part = BAB_PATTERN.sub("", text).strip()
        info.chapter_title = title_part if title_part else info.chapter_title
        # Reset section when entering new chapter
        info.section = ""
        info.section_title = ""
        return info

    # Check for LAMPIRAN heading
    lamp_match = LAMPIRAN_PATTERN.search(text)
    if lamp_match:
        info.chapter = "LAMPIRAN"
        lamp_num = lamp_match.group(1)
        title_part = LAMPIRAN_PATTERN.sub("", text).strip()
        info.section = f"lampiran_{lamp_num}"
        info.section_title = title_part if title_part else f"Lampiran {lamp_num}"
        return info

    # Check for numbered section heading (e.g., "1.4 Persyaratan Akademik")
    sec_match = SECTION_PATTERN.match(text)
    if sec_match:
        info.section = sec_match.group(1)
        info.section_title = text[sec_match.end():].strip()
        return info

    # For other headings, update section_title but keep chapter/section
    if text and not text.startswith(("DAFTAR", "KATA PENGANTAR")):
        info.section_title = text

    return info


# ── Keyword extraction ─────────────────────────────────────────────────

# Important terms to look for in Indonesian academic context
KEYWORD_PATTERNS = [
    r"IPK\s*[≥>=<]?\s*[\d.]+",
    r"\d+\s*SKS",
    r"Tugas\s+Akhir",
    r"Seminar\s+Proposal",
    r"Seminar\s+Kemajuan",
    r"Sidang\s+Tugas\s+Akhir",
    r"Ujian\s+Sarjana",
    r"Metodologi\s+Penelitian",
    r"Dosen\s+Pembimbing",
    r"Tim\s+Penguji",
    r"proposal\s+TA",
    r"laporan\s+TA",
    r"makalah\s+ilmiah",
    r"KKNI",
    r"CLO",
    r"SK\s+Rektor",
    r"SK\s+Dekan",
    r"Koordinator\s+TA",
    r"plagiarism|plagiat|plagiasi",
    r"Turn\s*It\s*In",
    r"Mendeley",
    r"IEEE",
    r"daftar\s+pustaka",
    r"abstrak",
    r"kata\s+pengantar",
    r"bimbingan",
    r"revisi",
    r"yudisium",
]


def extract_keywords(text: str) -> list[str]:
    """
    Extract relevant keywords from chunk text using regex patterns.
    """
    if not text:
        return []

    keywords = set()
    for pattern in KEYWORD_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            keywords.add(m.strip())

    # Also extract capitalized multi-word terms (likely proper nouns/concepts)
    cap_terms = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text)
    for term in cap_terms[:5]:  # limit to avoid noise
        if len(term) > 5:
            keywords.add(term)

    return sorted(keywords)[:10]  # cap at 10 keywords


# ── Chunk ID generation ────────────────────────────────────────────────

def generate_chunk_id(chapter: str, section: str, seq: int) -> str:
    """
    Generate a unique chunk ID.

    Format: bab1_1_4_001, lampiran_1_001, front_001
    """
    parts = []

    if chapter:
        # Convert "BAB I" -> "bab1", "BAB II" -> "bab2", etc.
        bab_match = re.match(r"BAB\s+(I{1,3}V?|IV|V?I{0,3})", chapter, re.IGNORECASE)
        if bab_match:
            roman = bab_match.group(1).upper()
            num = roman_to_int(roman)
            parts.append(f"bab{num}")
        elif "LAMPIRAN" in chapter.upper():
            parts.append("lampiran")
        else:
            parts.append(re.sub(r"[^a-z0-9]", "", chapter.lower()) or "misc")
    else:
        parts.append("front")

    if section:
        # Convert "1.4" -> "1_4", "1.4.1" -> "1_4_1", "lampiran_1" -> "1"
        sec_clean = section.replace(".", "_").replace("lampiran_", "")
        parts.append(sec_clean)

    parts.append(f"{seq:03d}")
    return "_".join(parts)


def roman_to_int(roman: str) -> int:
    """Convert Roman numeral to integer."""
    values = {"I": 1, "V": 5, "X": 10, "L": 50}
    result = 0
    prev = 0
    for ch in reversed(roman.upper()):
        val = values.get(ch, 0)
        if val < prev:
            result -= val
        else:
            result += val
        prev = val
    return result


# ── Build full metadata dict ───────────────────────────────────────────

def build_metadata(
    source: str,
    page: int,
    chapter_info: ChapterInfo,
    content_text: str,
    heading_text: str,
    chunk_seq: int,
) -> dict:
    """
    Build the complete metadata dictionary for a chunk.
    """
    content_type = classify_content_type(heading_text, content_text)
    keywords = extract_keywords(f"{heading_text} {content_text}")
    chunk_id = generate_chunk_id(
        chapter_info.chapter,
        chapter_info.section,
        chunk_seq,
    )

    return {
        "source": source,
        "page": page,
        "chapter": chapter_info.chapter,
        "chapter_title": chapter_info.chapter_title,
        "section": chapter_info.section,
        "section_title": chapter_info.section_title,
        "document_type": "panduan_ta",
        "content_type": content_type,
        "keywords": keywords,
        "chunk_id": chunk_id,
    }
