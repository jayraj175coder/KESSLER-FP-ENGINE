"""
tests/test_number_parser.py — Unit tests for German number parsing.
"""
from decimal import Decimal
import pytest
from core.number_parser import parse_german_number, format_german_number


def test_plain_integers():
    assert parse_german_number("19") == Decimal("19")
    assert parse_german_number("400") == Decimal("400")
    assert parse_german_number("1") == Decimal("1")
    assert parse_german_number("0") == Decimal("0")


def test_german_decimal_comma():
    assert parse_german_number("202,80") == Decimal("202.80")
    assert parse_german_number("8,45") == Decimal("8.45")
    assert parse_german_number("1,92") == Decimal("1.92")
    assert parse_german_number("12,5") == Decimal("12.5")
    assert parse_german_number("37,5") == Decimal("37.5")
    assert parse_german_number("0,152") == Decimal("0.152")


def test_thousands_separator():
    assert parse_german_number("1.000") == Decimal("1000")
    assert parse_german_number("1.500") == Decimal("1500")
    assert parse_german_number("4.787,18") == Decimal("4787.18")
    assert parse_german_number("1.323,70") == Decimal("1323.70")
    assert parse_german_number("6.037,86") == Decimal("6037.86")


def test_trailing_minus_credit_notes():
    assert parse_german_number("225,80-") == Decimal("-225.80")
    assert parse_german_number("155,00-") == Decimal("-155.00")
    assert parse_german_number("19,25-") == Decimal("-19.25")
    assert parse_german_number("400,05-") == Decimal("-400.05")
    assert parse_german_number("476,06-") == Decimal("-476.06")
    # Trailing minus with currency symbols
    assert parse_german_number("225,80- €") == Decimal("-225.80")
    assert parse_german_number("476,06- EUR") == Decimal("-476.06")
    assert parse_german_number("225,80 € -") == Decimal("-225.80")


def test_leading_minus():
    assert parse_german_number("-13,97") == Decimal("-13.97")
    assert parse_german_number("- 13,97 €") == Decimal("-13.97")
    assert parse_german_number("-100") == Decimal("-100")


def test_positive_and_spaces():
    assert parse_german_number("+36,00") == Decimal("36.00")
    assert parse_german_number("1 000,50") == Decimal("1000.50")
    assert parse_german_number("1\u00a0000,50") == Decimal("1000.50")
    assert parse_german_number("1\u202f000") == Decimal("1000")


def test_currency_and_percent_symbols():
    assert parse_german_number("8,69 €") == Decimal("8.69")
    assert parse_german_number("1.154,43 €") == Decimal("1154.43")
    assert parse_german_number("19%") == Decimal("19")
    assert parse_german_number("7 %") == Decimal("7")


def test_format_german_number():
    assert format_german_number("202,80") == 202.80
    assert format_german_number("1.000") == 1000.0
    assert format_german_number("225,80-") == -225.80


def test_invalid_numbers():
    with pytest.raises(ValueError):
        parse_german_number("")
    with pytest.raises(ValueError):
        parse_german_number("   ")
    with pytest.raises(ValueError):
        parse_german_number(None)
    with pytest.raises(ValueError):
        parse_german_number("abc")
    with pytest.raises(ValueError):
        parse_german_number("€")
