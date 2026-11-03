"""
core/pdf_reader.py — PDF word extraction using PyMuPDF.
"""
from typing import List, Tuple
try:
    import pymupdf as fitz
except ImportError:
    import fitz


WordTuple = Tuple[float, float, float, float, str, int, int, int]
# (x0, y0, x1, y1, word, block_no, line_no, word_no)


def get_page_words(pdf_path: str, page_num: int = 0) -> List[WordTuple]:
    """
    Extract all words with coordinates from a given page.
    Returns list of (x0, y0, x1, y1, word, block_no, line_no, word_no).
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    words = page.get_text("words")
    doc.close()
    return words


def get_all_pages_words(pdf_path: str) -> List[List[WordTuple]]:
    """Extract words from all pages in the PDF."""
    doc = fitz.open(pdf_path)
    result = []
    for page in doc:
        result.append(page.get_text("words"))
    doc.close()
    return result


def get_page_text(pdf_path: str, page_num: int = 0) -> str:
    """Get plain text from a page."""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    text = page.get_text("text")
    doc.close()
    return text


def get_all_pages_text(pdf_path: str) -> str:
    """Get plain text from all pages concatenated."""
    doc = fitz.open(pdf_path)
    texts = []
    for page in doc:
        texts.append(page.get_text("text"))
    doc.close()
    return "\n".join(texts)


def get_page_count(pdf_path: str) -> int:
    """Return the number of pages in the PDF."""
    doc = fitz.open(pdf_path)
    count = doc.page_count
    doc.close()
    return count
