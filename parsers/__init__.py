"""
parsers package — Document intelligence parsers for Kessler invoices and credit notes.
"""
from core.pdf_reader import get_page_text
from fingerprints.detector import detect_layout
from parsers.base_parser import BaseParser
from parsers.invoice_parser import InvoiceParser
from parsers.credit_note_parser import CreditNoteParser


def get_parser(pdf_path: str) -> BaseParser:
    """
    Factory function to return the appropriate parser based on layout and document type.
    """
    layout = detect_layout(pdf_path)
    if layout == "scanned":
        raise ValueError(f"Document {pdf_path} is a scanned image. OCR is required.")

    text = get_page_text(pdf_path, 0)
    if "GUTSCHRIFT" in text or "Gutschrift-Nr." in text:
        return CreditNoteParser(pdf_path)

    return InvoiceParser(pdf_path)


__all__ = ["BaseParser", "InvoiceParser", "CreditNoteParser", "get_parser"]
