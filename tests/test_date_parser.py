"""
tests/test_date_parser.py — Unit tests for date parsing and arithmetic.
"""
import pytest
from core.date_parser import parse_date, add_days_to_date, extract_date_from_text, parse_date_tokens


def test_parse_date_v1():
    assert parse_date("06.10.2026") == "2026-10-06"
    assert parse_date("02.10.2026") == "2026-10-02"
    assert parse_date("12.10.2026") == "2026-10-12"
    assert parse_date("14.10.2026") == "2026-10-14"
    assert parse_date("01.01.2025") == "2025-01-01"
    assert parse_date("6.5.2026") == "2026-05-06"
    assert parse_date("2026-10-19") == "2026-10-19"  # ISO idempotence


def test_parse_date_v2_german_months():
    assert parse_date("19. Oktober 2026") == "2026-10-19"
    assert parse_date("16. Oktober 2026") == "2026-10-16"
    assert parse_date("18. November 2026") == "2026-11-18"
    assert parse_date("18. November 2026.") == "2026-11-18"  # trailing period
    assert parse_date("01. Januar 2026") == "2026-01-01"
    assert parse_date("15. Jänner 2026") == "2026-01-15"   # Austrian variant
    assert parse_date("15. Februar 2026") == "2026-02-15"
    assert parse_date("31. März 2026") == "2026-03-31"
    assert parse_date("30. April 2026") == "2026-04-30"
    assert parse_date("01. Mai 2026") == "2026-05-01"
    assert parse_date("30. Juni 2026") == "2026-06-30"
    assert parse_date("31. Juli 2026") == "2026-07-31"
    assert parse_date("31. August 2026") == "2026-08-31"
    assert parse_date("30. September 2026") == "2026-09-30"
    assert parse_date("31. Dezember 2026") == "2026-12-31"


def test_add_days_to_date():
    assert add_days_to_date("2026-10-14", 7) == "2026-10-21"
    assert add_days_to_date("2026-10-31", 1) == "2026-11-01"
    assert add_days_to_date("2026-02-28", 1) == "2026-03-01"
    assert add_days_to_date("2026-10-06", 10) == "2026-10-16"


def test_extract_date_from_text():
    text_v1 = "Zahlbar bis 05.11.2026 ohne Abzug."
    assert extract_date_from_text(text_v1) == "2026-11-05"

    text_v2 = "Zahlungsziel: 30 Tage netto (bis 18. November 2026)."
    assert extract_date_from_text(text_v2) == "2026-11-18"

    assert extract_date_from_text("Kein Datum hier") is None


def test_parse_date_tokens():
    tokens = ["19.", "Oktober", "2026"]
    assert parse_date_tokens(tokens) == "2026-10-19"
    assert parse_date_tokens([]) is None


def test_invalid_dates():
    with pytest.raises(ValueError):
        parse_date("not-a-date")
    with pytest.raises(ValueError):
        parse_date("32.13.2026")
    with pytest.raises(ValueError):
        parse_date("19. Somemonth 2026")
