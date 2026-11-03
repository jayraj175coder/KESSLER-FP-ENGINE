"""
core/text_normalizer.py — Text normalization utilities.
"""
import re


def normalize_whitespace(s: str) -> str:
    """Collapse multiple spaces/tabs/newlines into a single space."""
    return re.sub(r'\s+', ' ', s).strip()


def strip_bullet_char(s: str) -> str:
    """Remove bullet/separator characters (·, •, etc.) from strings."""
    return re.sub(r'[·•·\uf0b7]', '', s).strip()


def clean_text(s: str) -> str:
    """Normalize and clean extracted text."""
    return normalize_whitespace(strip_bullet_char(s))
