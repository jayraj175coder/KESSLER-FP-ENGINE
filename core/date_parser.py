"""
core/date_parser.py — Date parsing for German V1 and V2 invoice formats.
"""
import re
from datetime import datetime, timedelta
from typing import Optional, List

GERMAN_MONTHS = {
    'januar': 1, 'jaenner': 1, 'jänner': 1, 'februar': 2, 'märz': 3, 'maerz': 3, 'marz': 3,
    'april': 4, 'mai': 5, 'juni': 6, 'juli': 7,
    'august': 8, 'september': 9, 'oktober': 10,
    'november': 11, 'dezember': 12,
}


def parse_date(s: str) -> str:
    """
    Parse a date string to ISO 8601 (YYYY-MM-DD).

    Handles:
      ISO 8601:  YYYY-MM-DD          e.g. "2026-10-19"
      V1 format: DD.MM.YYYY          e.g. "06.10.2026"
      V2 format: DD. MonthName YYYY  e.g. "19. Oktober 2026"
    """
    if s is None:
        raise ValueError("Cannot parse None as date")
    s = str(s).strip()
    if not s:
        raise ValueError("Empty string cannot be parsed as date")

    # If already ISO 8601 YYYY-MM-DD
    m_iso = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', s)
    if m_iso:
        y, mo, d = int(m_iso.group(1)), int(m_iso.group(2)), int(m_iso.group(3))
        try:
            return datetime(y, mo, d).strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid calendar date: {s!r}") from e

    # If string ends with period from sentence context (e.g. "18. November 2026.")
    if s.endswith('.') and not re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}\.?$', s):
        s = s.rstrip('.').strip()

    # V1: DD.MM.YYYY (optional trailing dot)
    m = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})\.?$', s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            dt = datetime(y, mo, d)
            return dt.strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid calendar date: {s!r}") from e

    # V2: "DD. MonthName YYYY"
    m = re.match(r'^(\d{1,2})\.\s+([A-Za-zÄÖÜäöüß]+)\s+(\d{4})\.?$', s)
    if m:
        d_s, month_name, y_s = m.group(1), m.group(2).lower(), m.group(3)
        d, y = int(d_s), int(y_s)
        mo = GERMAN_MONTHS.get(month_name)
        if mo is None:
            raise ValueError(f"Unknown month name: {month_name!r}")
        try:
            dt = datetime(y, mo, d)
            return dt.strftime("%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid calendar date: {s!r}") from e

    raise ValueError(f"Cannot parse date: {s!r}")


def add_days_to_date(iso_date: str, days: int) -> str:
    """Add integer days to an ISO 8601 date string (YYYY-MM-DD)."""
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    new_dt = dt + timedelta(days=days)
    return new_dt.strftime("%Y-%m-%d")


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Search for the first occurrence of a valid German date in text.
    Matches DD.MM.YYYY or DD. Month YYYY.
    """
    if not text:
        return None

    # Try DD. Month YYYY
    m_v2 = re.search(r'(\d{1,2})\.\s+([A-Za-zÄÖÜäöüß]+)\s+(\d{4})', text)
    if m_v2:
        try:
            return parse_date(m_v2.group(0))
        except ValueError:
            pass

    # Try DD.MM.YYYY
    m_v1 = re.search(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', text)
    if m_v1:
        try:
            return parse_date(m_v1.group(0))
        except ValueError:
            pass

    return None


def parse_date_tokens(tokens: List[str]) -> Optional[str]:
    """
    Try to parse a date from a list of consecutive text tokens.
    Used for V2 where date is split across multiple word objects.
    e.g. ["19.", "Oktober", "2026"] → "2026-10-19"
    """
    if not tokens:
        return None
    joined = ' '.join(tokens)
    try:
        return parse_date(joined)
    except ValueError:
        pass

    if len(tokens) >= 3 and tokens[0].endswith('.') and tokens[0][:-1].isdigit():
        try:
            return parse_date(f"{tokens[0]} {tokens[1]} {tokens[2]}")
        except (ValueError, IndexError):
            pass
    return None
