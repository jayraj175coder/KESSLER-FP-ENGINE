"""
tests/test_schema.py — Tests JSON schema conformance and ground-truth comparison for INV-01.
"""
import json
import os
import pytest

from core.schema_validator import validate_output
from parsers import get_parser

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs")
if not os.path.exists(INPUTS_DIR):
    INPUTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "inputs"))


def test_inv01_matches_expected_output_exactly():
    """Verify that INV-01 output matches INV-01_expected_output.json with 0 differences."""
    pdf_path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    expected_path = os.path.join(INPUTS_DIR, "INV-01_expected_output.json")

    assert os.path.exists(pdf_path), f"Missing {pdf_path}"
    assert os.path.exists(expected_path), f"Missing {expected_path}"

    with open(expected_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    parser = get_parser(pdf_path)
    actual = parser.parse().to_dict()

    assert actual == expected, f"Actual does not match expected output exactly: {actual} != {expected}"


def test_all_documents_schema_conformance():
    """Verify that all parsed documents conform to output_schema.json."""
    files = [
        "INV-01_RE-2026-10418.pdf",
        "INV-02_RE-2026-10431.pdf",
        "INV-03_GS-2026-00872.pdf",
        "INV-04_RE-2026-10457.pdf",
        "INV-05_2026-R-00117.pdf",
    ]

    for filename in files:
        path = os.path.join(INPUTS_DIR, filename)
        assert os.path.exists(path), f"Expected input file missing: {path}"
        parser = get_parser(path)
        doc_dict = parser.parse().to_dict()
        valid, errors = validate_output(doc_dict)
        assert valid, f"{filename} failed schema validation: {errors}"


def test_schema_rejects_missing_required_fields():
    """Verify schema validator fails when required fields are missing."""
    invalid_data = {
        "document_type": "invoice",
        # missing document_number, document_date, currency, supplier, buyer, line_items, totals
    }
    valid, errors = validate_output(invalid_data)
    assert not valid
    assert len(errors) > 0


def test_schema_rejects_invalid_document_type():
    """Verify schema validator rejects invalid document_type."""
    pdf_path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    parser = get_parser(pdf_path)
    data = parser.parse().to_dict()
    data["document_type"] = "receipt"  # invalid

    valid, errors = validate_output(data)
    assert not valid


def test_schema_rejects_invalid_currency():
    """Verify schema validator enforces EUR currency const."""
    pdf_path = os.path.join(INPUTS_DIR, "INV-01_RE-2026-10418.pdf")
    parser = get_parser(pdf_path)
    data = parser.parse().to_dict()
    data["currency"] = "USD"  # invalid

    valid, errors = validate_output(data)
    assert not valid
