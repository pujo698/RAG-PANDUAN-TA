"""
chunker.py — Multi-strategy document chunking.

Three-tier chunking strategy:
  1. Heading-based chunking (primary) — each heading becomes one chunk
  2. Semantic chunking — split long sections by paragraph/topic boundaries
  3. RecursiveCharacterTextSplitter (fallback) — for oversized chunks

Flowcharts and tables are isolated as standalone chunks.
"""

import re
from dataclasses import dataclass, field

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from parser import ParsedDocument, ParsedItem
from metadata import (
    ChapterInfo,
    build_metadata,
    extract_chapter_info,
)
from utils import count_tokens_approx, clean_text, setup_logger

logger = setup_logger("chunker")

# ── Configuration ──────────────────────────────────────────────────────

MAX_TOKENS_BEFORE_SEMANTIC = 1000   # trigger semantic split above this
MAX_CHARS_BEFORE_FALLBACK = 3200    # trigger RecursiveCharacterTextSplitter
FALLBACK_CHUNK_SIZE = 800
FALLBACK_CHUNK_OVERLAP = 100

# Pre-matter headings to skip (cover, TOC, etc.)
SKIP_HEADINGS = {
    "BUKU PANDUAN & LOG BOOK BIMBINGAN",
    "TUGAS AKHIR",
    "PROGRAM STUDI TEKNIK INFORMATIKA",
    "FAKULTAS TEKNOLOGI INDUSTRI UNIVERSITAS ISLAM SULTAN AGUNG",
    "BUKU PANDUAN & LOG BOOK BIMBINGAN TUGAS AKHIR PROGRAM STUDI TEKNIK INFORMATIKA",
    "Tim Penyusun :",
    "Cetakan :",
    "TEKNIK INFORMATIKA",
    "Buku Panduan & Asistensi Tugas Akhir",
}

# Headings that signal flowchart content
FLOWCHART_CAPTIONS = re.compile(
    r"(flowchart|diagram\s+alir|alur)",
    re.IGNORECASE,
)


# ── Section accumulation ──────────────────────────────────────────────

@dataclass
class SectionBuffer:
    """Accumulates content between headings."""
    heading: str = ""
    heading_item: ParsedItem | None = None
    content_parts: list[str] = field(default_factory=list)
    pages: list[int] = field(default_factory=list)
    has_table: bool = False
    table_markdowns: list[str] = field(default_factory=list)
    has_flowchart: bool = False
    is_caption: bool = False

    @property
    def full_text(self) -> str:
        return "\n\n".join(self.content_parts)

    @property
    def first_page(self) -> int:
        return self.pages[0] if self.pages else 0

    def add_content(self, text: str, page: int = 0):
        if text and text.strip():
            self.content_parts.append(clean_text(text))
        if page and page not in self.pages:
            self.pages.append(page)


# ── Core chunking logic ──────────────────────────────────────────────

def chunk_document(parsed: ParsedDocument) -> list[Document]:
    """
    Convert a ParsedDocument into LangChain Document chunks.

    Strategy:
      1. Walk through parsed items, grouping content under headings
      2. When a new heading is encountered, flush the previous section
      3. Apply semantic splitting for long sections
      4. Apply RecursiveCharacterTextSplitter as fallback for very long chunks
      5. Isolate flowcharts and tables as dedicated chunks

    Returns:
        List of LangChain Document objects with metadata.
    """
    documents: list[Document] = []
    chapter_info = ChapterInfo()
    current_section = SectionBuffer()
    chunk_counter: dict[str, int] = {}  # key -> sequence counter

    # Track which captions we've seen (for flowchart detection)
    # We map from caption index to caption text for precise matching
    flowchart_caption_indices: set[int] = set()

    # First pass: identify flowchart caption items by index
    for item in parsed.items:
        if item.label == "caption" and FLOWCHART_CAPTIONS.search(item.text):
            flowchart_caption_indices.add(item.index)

    def _next_seq(chapter: str, section: str) -> int:
        key = f"{chapter}|{section}"
        chunk_counter[key] = chunk_counter.get(key, 0) + 1
        return chunk_counter[key]

    def _flush_section(section: SectionBuffer):
        """Convert accumulated section into Document(s)."""
        if not section.heading and not section.content_parts:
            return

        nonlocal chapter_info

        # Update chapter/section info from heading
        if section.heading:
            chapter_info = extract_chapter_info(section.heading, chapter_info)

        full_text = section.full_text
        heading = section.heading or chapter_info.section_title

        # ── Handle flowcharts as standalone chunks ──
        if section.has_flowchart or (
            section.heading_item
            and section.heading_item.label == "caption"
            and FLOWCHART_CAPTIONS.search(section.heading)
        ):
            seq = _next_seq(chapter_info.chapter, chapter_info.section)
            meta = build_metadata(
                source=parsed.source,
                page=section.first_page,
                chapter_info=chapter_info,
                content_text=full_text,
                heading_text=heading,
                chunk_seq=seq,
            )
            meta["content_type"] = "flowchart"
            content = f"{heading}\n\n{full_text}" if full_text else heading
            documents.append(Document(page_content=content, metadata=meta))
            return

        # ── Handle tables as standalone chunks ──
        if section.has_table and section.table_markdowns:
            for table_md in section.table_markdowns:
                seq = _next_seq(chapter_info.chapter, chapter_info.section)
                meta = build_metadata(
                    source=parsed.source,
                    page=section.first_page,
                    chapter_info=chapter_info,
                    content_text=table_md,
                    heading_text=heading,
                    chunk_seq=seq,
                )
                meta["content_type"] = "tabel"
                content = f"{heading}\n\n{table_md}" if heading else table_md
                documents.append(Document(page_content=content, metadata=meta))

            # If there's also non-table text, process it
            non_table_parts = [
                p for p in section.content_parts
                if p not in section.table_markdowns
            ]
            if not non_table_parts:
                return
            full_text = "\n\n".join(non_table_parts)

        # ── Build chunk content ──
        if heading and full_text:
            chunk_text = f"{heading}\n\n{full_text}"
        elif heading:
            chunk_text = heading
        else:
            chunk_text = full_text

        if not chunk_text.strip():
            return

        # ── Tier 1: Direct heading-based chunk (if small enough) ──
        token_count = count_tokens_approx(chunk_text)

        if token_count <= MAX_TOKENS_BEFORE_SEMANTIC:
            seq = _next_seq(chapter_info.chapter, chapter_info.section)
            meta = build_metadata(
                source=parsed.source,
                page=section.first_page,
                chapter_info=chapter_info,
                content_text=chunk_text,
                heading_text=heading,
                chunk_seq=seq,
            )
            documents.append(Document(page_content=chunk_text, metadata=meta))
            return

        # ── Tier 2: Semantic chunking (split by paragraph/topic) ──
        sub_chunks = _semantic_split(chunk_text, heading)

        for sub_text in sub_chunks:
            if len(sub_text) > MAX_CHARS_BEFORE_FALLBACK:
                # ── Tier 3: RecursiveCharacterTextSplitter fallback ──
                fallback_chunks = _fallback_split(sub_text)
                for fb_text in fallback_chunks:
                    seq = _next_seq(chapter_info.chapter, chapter_info.section)
                    meta = build_metadata(
                        source=parsed.source,
                        page=section.first_page,
                        chapter_info=chapter_info,
                        content_text=fb_text,
                        heading_text=heading,
                        chunk_seq=seq,
                    )
                    documents.append(Document(page_content=fb_text, metadata=meta))
            else:
                seq = _next_seq(chapter_info.chapter, chapter_info.section)
                meta = build_metadata(
                    source=parsed.source,
                    page=section.first_page,
                    chapter_info=chapter_info,
                    content_text=sub_text,
                    heading_text=heading,
                    chunk_seq=seq,
                )
                documents.append(Document(page_content=sub_text, metadata=meta))

    # ── Main processing loop ──────────────────────────────────────────

    for item in parsed.items:
        # Skip document_index items (TOC entries)
        if item.label == "document_index":
            continue

        # Skip empty pictures without text
        if item.label == "picture" and not item.text:
            # Don't set flowchart flag based on page proximity alone;
            # flowcharts are identified via caption items, not pictures
            continue

        # Skip pre-matter headings
        if item.is_heading and item.text.strip() in SKIP_HEADINGS:
            continue

        if item.is_heading:
            # Flush previous section
            _flush_section(current_section)

            # Start new section
            current_section = SectionBuffer(
                heading=item.text.strip(),
                heading_item=item,
                pages=[item.page] if item.page else [],
            )

            # Check if this is a flowchart caption heading
            if item.label == "caption" and FLOWCHART_CAPTIONS.search(item.text):
                current_section.has_flowchart = True

        elif item.label == "caption" and FLOWCHART_CAPTIONS.search(item.text):
            # Flowchart caption — flush current and create standalone
            _flush_section(current_section)
            current_section = SectionBuffer(
                heading=item.text.strip(),
                heading_item=item,
                pages=[item.page] if item.page else [],
                has_flowchart=True,
            )

        elif item.label == "table":
            # Mark section as containing table
            current_section.has_table = True
            table_content = item.table_markdown if item.table_markdown else item.text
            if table_content:
                current_section.table_markdowns.append(table_content)
                current_section.add_content(table_content, item.page)

        elif item.label == "list_item":
            # Prefix list items with bullet
            bullet_text = f"• {item.text.strip()}" if item.text else ""
            current_section.add_content(bullet_text, item.page)

        else:
            # Regular text, footnotes, etc.
            current_section.add_content(item.text, item.page)

    # Flush last section
    _flush_section(current_section)

    logger.info(f"Total chunks created: {len(documents)}")
    return documents


# ── Semantic splitting ─────────────────────────────────────────────────

def _semantic_split(text: str, heading: str) -> list[str]:
    """
    Split a long section by paragraph/topic boundaries.

    Rules:
      - Split on double newlines (paragraph boundaries)
      - Never split mid-sentence
      - Each sub-chunk gets the heading prefix for context
    """
    # Split into paragraphs
    paragraphs = re.split(r"\n{2,}", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if len(paragraphs) <= 1:
        return [text]

    # Group paragraphs into sub-chunks under the token limit
    sub_chunks: list[str] = []
    current_group: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = count_tokens_approx(para)

        if current_tokens + para_tokens > MAX_TOKENS_BEFORE_SEMANTIC and current_group:
            # Flush current group
            chunk_text = "\n\n".join(current_group)
            sub_chunks.append(chunk_text)
            current_group = [para]
            current_tokens = para_tokens
        else:
            current_group.append(para)
            current_tokens += para_tokens

    # Flush remaining
    if current_group:
        chunk_text = "\n\n".join(current_group)
        sub_chunks.append(chunk_text)

    return sub_chunks


# ── Fallback splitting ─────────────────────────────────────────────────

def _fallback_split(text: str) -> list[str]:
    """
    Use RecursiveCharacterTextSplitter as last resort for very long text.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=FALLBACK_CHUNK_SIZE,
        chunk_overlap=FALLBACK_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "],
        keep_separator=True,
    )

    chunks = splitter.split_text(text)
    return chunks
