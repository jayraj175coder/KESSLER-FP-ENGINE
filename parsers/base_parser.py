"""
parsers/base_parser.py — Abstract base class for invoice parsers.
"""
from abc import ABC, abstractmethod
from core.models import InvoiceDocument


class BaseParser(ABC):
    """Abstract base parser for invoice documents."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    @abstractmethod
    def parse(self) -> InvoiceDocument:
        """Parse the PDF and return an InvoiceDocument."""
        ...
