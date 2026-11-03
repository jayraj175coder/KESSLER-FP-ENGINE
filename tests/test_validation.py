"""
tests/test_validation.py — Unit tests for financial reconciliation checks V1 through V7.
"""
import os
import pytest

from parsers import get_parser
from validation.checks import (
    check_v1_line_items,
    check_v2_net_by_vat,
    check_v3_net_total,
    check_v4_vat_calculation,
    check_v5_vat_total,
    check_v6_gross_total,
    check_v7_cash_discount,
)
from validation.engine import ValidationEngine

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs")
if not os.path.exists(INPUTS_DIR):
    INPUTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "inputs"))


def test_inv01_all_checks_pass():
    path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    doc = get_parser(path).parse()
    engine = ValidationEngine()
    summary = engine.validate_document(doc)

    assert summary.passed is True
    assert summary.error_count == 0
    for c in summary.checks:
        assert c.passed is True, f"Check {c.check_id} failed: {c.details}"


def test_inv02_all_checks_pass():
    path = os.path.join(INPUTS_DIR, "INV-02_RE-2026-10431.pdf")
    doc = get_parser(path).parse()
    engine = ValidationEngine()
    summary = engine.validate_document(doc)

    assert summary.passed is True
    assert summary.error_count == 0


def test_inv03_credit_note_reconciliation():
    path = os.path.join(INPUTS_DIR, "INV-03_GS-2026-00872.pdf")
    doc = get_parser(path).parse()
    engine = ValidationEngine()
    summary = engine.validate_document(doc)

    assert summary.passed is True
    assert summary.error_count == 0
    # Negative totals correctly reconcile
    v6 = next(c for c in summary.checks if c.check_id == "V6")
    assert v6.passed is True


def test_inv04_detects_printing_typo_on_pos7():
    """Verify that V1 and V2 catch the 36.00 EUR transposition error in INV-04 Pos 7."""
    path = os.path.join(INPUTS_DIR, "INV-04_RE-2026-10457.pdf")
    doc = get_parser(path).parse()

    # V1 must fail because 26 * 48.02 = 1248.52 != 1284.52 printed
    v1 = check_v1_line_items(doc)
    assert v1.passed is False
    assert "Pos 7" in v1.details
    assert v1.difference == 36.0

    # V2 must fail because sum of line items (5249.22) != printed net subtotal (5213.22)
    v2 = check_v2_net_by_vat(doc)
    assert v2.passed is False
    assert v2.difference == 36.0

    # V3 through V7 should still pass
    assert check_v3_net_total(doc).passed is True
    assert check_v4_vat_calculation(doc).passed is True
    assert check_v5_vat_total(doc).passed is True
    assert check_v6_gross_total(doc).passed is True
    assert check_v7_cash_discount(doc).passed is True

    # Engine summary reflects failure
    engine = ValidationEngine()
    summary = engine.validate_document(doc)
    assert summary.passed is False
    assert summary.error_count == 2


def test_inv05_v2_all_checks_pass():
    path = os.path.join(INPUTS_DIR, "INV-05_2026-R-00117.pdf")
    doc = get_parser(path).parse()
    engine = ValidationEngine()
    summary = engine.validate_document(doc)

    assert summary.passed is True
    assert summary.error_count == 0


def test_v7_skonto_deadline_validation():
    """Verify V7 handles null cash discount and validates cash discount correctly."""
    path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    doc = get_parser(path).parse()

    # Original passes
    res = check_v7_cash_discount(doc)
    assert res.passed is True

    # Artificially modify discount to trigger mismatch
    doc.cash_discount.amount = doc.cash_discount.amount + 10
    res_bad = check_v7_cash_discount(doc)
    assert res_bad.passed is False
    assert res_bad.severity == "WARNING"

    # Test deadline after due_date triggers warning failure
    doc.cash_discount.amount = doc.cash_discount.amount - 10
    doc.cash_discount.until = "2026-12-01"  # after due_date 2026-11-05
    res_late = check_v7_cash_discount(doc)
    assert res_late.passed is False
    assert res_late.severity == "WARNING"
    assert "after due date" in res_late.details


def test_v2_catches_unmapped_vat_rate():
    """Verify Check V2 fails if a line item uses a VAT rate missing from totals."""
    path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    doc = get_parser(path).parse()

    # Artificially set a line item's VAT rate to 7% while net_by_vat_rate only has 19%
    doc.line_items[0].vat_rate = 7
    v2 = check_v2_net_by_vat(doc)
    assert v2.passed is False
    assert "missing from totals.net_by_vat_rate" in v2.details
