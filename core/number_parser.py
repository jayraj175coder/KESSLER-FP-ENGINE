"""
core/number_parser.py — German number parsing utilities.
"""
import re
from decimal import Decimal, InvalidOperation


def parse_german_number(s: str) -> Decimal:
    """
    Parse a German-formatted number string to Decimal.
    Handles:
      - Thousands separator: period   e.g. "1.000", "4.787,18"
      - Decimal separator: comma      e.g. "202,80", "12,5", "0,152"
      - Trailing minus for negatives  e.g. "225,80-"
      - Leading minus                 e.g. "-13,97"
      - Plain integers                e.g. "19", "400"
    """
    if s is None:
        raise ValueError("Cannot parse None as number")
    s = str(s).strip()
    if not s:
        raise ValueError("Empty string cannot be parsed as number")

    # Normalize non-breaking and thin spaces
    s = s.replace('\u00a0', ' ').replace('\u202f', ' ')
    # Remove currency words/symbols and percentage signs
    s = re.sub(r'(?i)\bEUR\b', '', s)
    s = s.replace('€', '').replace('\u20ac', '').replace('%', '').strip()

    if not s:
        raise ValueError("String contained only symbols, no number")

    negative = False
    if s.endswith('-'):
        negative = True
        s = s[:-1].strip()
    elif s.startswith('-'):
        negative = True
        s = s[1:].strip()
    elif s.startswith('+'):
        s = s[1:].strip()

    # Re-check trailing minus in case whitespace or signs were trimmed
    if s.endswith('-'):
        negative = True
        s = s[:-1].strip()

    if not s:
        raise ValueError("String contained only symbols, no number")

    # Remove interior spaces (e.g. thousands separated by space "1 000,50")
    s_clean = s.replace(' ', '')

    if ',' in s_clean and '.' in s_clean:
        # e.g. "4.787,18" or "1.323,70" -> remove dot, replace comma with dot
        s_clean = s_clean.replace('.', '').replace(',', '.')
    elif ',' in s_clean:
        # e.g. "202,80" or "12,5" or "0,152" -> replace comma with dot
        s_clean = s_clean.replace(',', '.')
    elif '.' in s_clean:
        # Dot only: check if German thousands e.g. "1.000"
        if re.match(r'^\d{1,3}(\.\d{3})+$', s_clean):
            s_clean = s_clean.replace('.', '')
        # Otherwise keep as decimal point (e.g. 12.5)

    try:
        val = Decimal(s_clean)
    except InvalidOperation:
        raise ValueError(f"Cannot parse as number: {s!r}")

    return -val if negative else val


def format_german_number(s: str) -> float:
    """Parse a German number string and return as float."""
    return float(parse_german_number(s))
