"""
parser.py — PDF parsing using Docling.

Uses PyPdfiumDocumentBackend to avoid memory issues with DoclingParseDocumentBackend
on machines with limited RAM. Extracts structured document elements including:
headings, paragraphs, lists, tables, pictures, and captions.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from utils import setup_logger

logger = setup_logger("parser")


@dataclass
class ParsedItem:
    """A single parsed element from the PDF document."""
    index: int
    label: str            # section_header, text, list_item, table, picture, caption, etc.
    level: int            # nesting level from Docling tree
    text: str             # text content
    page: int             # 1-indexed page number
    is_heading: bool = False
    table_markdown: str = ""  # markdown representation for tables


@dataclass
class ParsedDocument:
    """Complete parsed representation of a PDF document."""
    source: str           # filename
    items: list[ParsedItem] = field(default_factory=list)
    total_pages: int = 0

    @property
    def headings(self) -> list[ParsedItem]:
        return [item for item in self.items if item.is_heading]


def parse_pdf(pdf_path: str) -> ParsedDocument:
    """
    Parse a PDF file using Docling and return structured elements.

    Uses PyPdfiumDocumentBackend (lighter than DoclingParseDocumentBackend)
    with OCR disabled since the source PDF is text-based.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        ParsedDocument with all structured items.
    """
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    logger.info(f"Loading PDF: {path.name}")

    # Configure pipeline: no OCR needed (text-based PDF), lower image scale
    # to conserve memory, batch size 1 for stability
    pipeline_options = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=False,
        images_scale=0.5,
        layout_batch_size=1,
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                backend=PyPdfiumDocumentBackend,
            )
        }
    )

    logger.info("Parsing document with Docling...")
    result = converter.convert(str(path))
    doc = result.document

    parsed = ParsedDocument(source=path.name)
    heading_count = 0

    for i, (item, level) in enumerate(doc.iterate_items()):
        label = getattr(item, "label", type(item).__name__)

        # Extract page number
        page = 0
        prov = getattr(item, "prov", None)
        if prov:
            for p in prov:
                page_no = getattr(p, "page_no", 0)
                if page_no:
                    page = page_no
                    break

        # Extract text content
        text = ""
        if hasattr(item, "text") and item.text:
            text = item.text

        # Determine if this is a heading
        is_heading = label == "section_header"
        if is_heading:
            heading_count += 1

        # Handle tables — export as markdown
        table_md = ""
        if label == "table":
            try:
                table_md = item.export_to_markdown(doc=doc)
            except (TypeError, AttributeError):
                try:
                    table_md = item.export_to_markdown()
                except Exception:
                    table_md = text

        # Skip empty pictures without captions (logos, decorative images)
        if label == "picture" and not text:
            # Still record it for flowchart detection (via nearby captions)
            pass

        parsed_item = ParsedItem(
            index=i,
            label=label,
            level=level,
            text=text,
            page=page,
            is_heading=is_heading,
            table_markdown=table_md,
        )
        parsed.items.append(parsed_item)

        if page > parsed.total_pages:
            parsed.total_pages = page

    logger.info(f"Headings detected: {heading_count}")
    logger.info(f"Total items parsed: {len(parsed.items)}")
    logger.info(f"Total pages: {parsed.total_pages}")

    return parsed
