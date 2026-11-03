"""
tests/test_line_items.py — Unit tests for line item parsing across all documents.
"""
import os
from decimal import Decimal
import pytest

from core.pdf_reader import get_all_pages_words
from parsers.line_item_parser import parse_v1_line_items, parse_v2_line_items
from parsers import get_parser

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs")
if not os.path.exists(INPUTS_DIR):
    INPUTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "inputs"))


def test_inv01_line_items():
    path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    words = get_all_pages_words(path)
    items = parse_v1_line_items(words)
    assert len(items) == 6

    # Verify Pos 1
    assert items[0].position == 1
    assert items[0].article_number == "KI-40112"
    assert items[0].quantity == Decimal("24")
    assert items[0].unit == "Stk"
    assert items[0].unit_price == Decimal("8.45")
    assert items[0].price_unit == Decimal("1")
    assert items[0].discount_percent is None
    assert items[0].line_total == Decimal("202.80")
    assert items[0].vat_rate == 19

    # Verify Pos 4 has 5% discount
    assert items[3].position == 4
    assert items[3].discount_percent == Decimal("5")
    assert items[3].line_total == Decimal("144.97")

    # Verify Pos 5 has PE=100
    assert items[4].position == 5
    assert items[4].price_unit == Decimal("100")
    assert items[4].unit_price == Decimal("14.60")
    assert items[4].quantity == Decimal("400")
    assert items[4].line_total == Decimal("58.40")


def test_inv02_multipage_and_carry_forward():
    path = os.path.join(INPUTS_DIR, "INV-02_RE-2026-10431.pdf")
    words = get_all_pages_words(path)
    items = parse_v1_line_items(words)
    # Exactly 26 items across 3 pages (Übertrag carry-forward lines excluded)
    assert len(items) == 26

    # Verify German 1.000 quantity parsed as 1000
    pos30 = next(it for it in items if it.position == 30)
    assert pos30.quantity == Decimal("1000")
    assert pos30.price_unit == Decimal("100")

    # Verify books have 7% VAT
    pos90 = next(it for it in items if it.position == 90)
    assert pos90.vat_rate == 7
    assert pos90.article_number == "BU-90011"

    pos200 = next(it for it in items if it.position == 200)
    assert pos200.vat_rate == 7
    assert pos200.article_number == "BU-90034"

    # Verify multi-line description continuation joined
    pos10 = next(it for it in items if it.position == 10)
    assert "Charge 2026-114" in pos10.description

    # Verify continuation descriptions containing 'Pos.' are NOT dropped
    pos70 = next(it for it in items if it.position == 70)
    assert "Ersatz für Pos. 12 aus Auftrag 4500091180" in pos70.description

    pos190 = next(it for it in items if it.position == 190)
    assert "Ersatz für Pos. 12 aus Auftrag 4500091180" in pos190.description


def test_inv03_credit_note_line_items():
    path = os.path.join(INPUTS_DIR, "INV-03_GS-2026-00872.pdf")
    parser = get_parser(path)
    doc = parser.parse()
    assert len(doc.line_items) == 3

    # Credit note line totals must be negative
    for it in doc.line_items:
        assert it.line_total < 0, f"Line total should be negative: {it.line_total}"

    assert doc.line_items[0].line_total == Decimal("-225.80")
    assert doc.line_items[1].line_total == Decimal("-155.00")
    assert doc.line_items[2].line_total == Decimal("-19.25")


def test_inv04_fifteen_items():
    path = os.path.join(INPUTS_DIR, "INV-04_RE-2026-10457.pdf")
    words = get_all_pages_words(path)
    items = parse_v1_line_items(words)
    assert len(items) == 15

    # Pos 7 printed amount is 1284.52 (as printed)
    pos7 = next(it for it in items if it.position == 7)
    assert pos7.article_number == "KI-71004"
    assert pos7.line_total == Decimal("1284.52")


def test_inv05_v2_line_items_and_discount():
    path = os.path.join(INPUTS_DIR, "INV-05_2026-R-00117.pdf")
    words = get_all_pages_words(path)
    items = parse_v2_line_items(words)
    assert len(items) == 5

    # Pos 2 has 3% discount deducted from betrag: 465.60 - 13.97 = 451.63
    pos2 = next(it for it in items if it.position == 2)
    assert pos2.discount_percent == Decimal("3")
    assert pos2.line_total == Decimal("451.63")

    # Pos 3 has price per piece without PE column: 0.152
    pos3 = next(it for it in items if it.position == 3)
    assert pos3.unit_price == Decimal("0.152")
    assert pos3.quantity == Decimal("600")
    assert pos3.line_total == Decimal("91.20")

    # Pos 5 has 7% VAT
    pos5 = next(it for it in items if it.position == 5)
    assert pos5.vat_rate == 7
