"""
tests/test_layout_detection.py — Unit tests for layout fingerprint detection.
"""
import os
import pytest
from fingerprints.detector import detect_layout

INPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "inputs")
if not os.path.exists(INPUTS_DIR):
    INPUTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "inputs"))


def test_detect_v1_documents():
    v1_files = [
        "INV-01_RE-2026-10418.pdf",
        "INV-02_RE-2026-10431.pdf",
        "INV-03_GS-2026-00872.pdf",
        "INV-04_RE-2026-10457.pdf",
    ]
    for filename in v1_files:
        path = os.path.join(INPUTS_DIR, filename)
        assert os.path.exists(path), f"Expected input file missing: {path}"
        assert detect_layout(path) == "kessler_v1", f"Failed for {filename}"


def test_detect_v2_documents():
    v2_file = os.path.join(INPUTS_DIR, "INV-05_2026-R-00117.pdf")
    assert os.path.exists(v2_file), f"Expected input file missing: {v2_file}"
    assert detect_layout(v2_file) == "kessler_v2"


def test_detect_scanned_documents():
    scan_file = os.path.join(INPUTS_DIR, "INV-06_BONUS_scan_RE-2026-10466.pdf")
    assert os.path.exists(scan_file), f"Expected input file missing: {scan_file}"
    assert detect_layout(scan_file) == "scanned"


def test_detect_nonexistent_file():
    assert detect_layout("nonexistent.pdf") == "unknown"
