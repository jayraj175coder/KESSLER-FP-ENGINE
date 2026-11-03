"""
validate.py — CLI tool to perform financial reconciliation on extracted invoices.

Usage:
    python validate.py [--input-dir DIR] [--report-file FILE]
"""
import argparse
import glob
import os
import sys

# Ensure engine modules are on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fingerprints.detector import detect_layout
from parsers import get_parser
from validation.engine import ValidationEngine
from validation.report_generator import generate_markdown_report


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="KESSLER FP Engine — Financial Reconciliation Validator")
    parser.add_argument(
        "--input-dir",
        default=os.path.join(os.path.dirname(__file__), "inputs"),
        help="Path to directory containing input PDFs"
    )
    parser.add_argument(
        "--report-file",
        default=os.path.join(os.path.dirname(__file__), "outputs", "validation_report.md"),
        help="Path for generated Markdown validation report"
    )

    args = parser.parse_args()

    # Fallback to ../inputs if inputs doesn't exist
    if not os.path.exists(args.input_dir):
        fallback = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "inputs"))
        if os.path.exists(fallback):
            args.input_dir = fallback

    files = sorted(glob.glob(os.path.join(args.input_dir, "*.pdf")))
    if not files:
        print(f"No PDF files found in {args.input_dir}")
        sys.exit(1)

    print("KESSLER FP ENGINE — Financial Reconciliation Engine")
    print("=" * 75)

    engine = ValidationEngine()
    summaries = []

    for pdf_path in files:
        filename = os.path.basename(pdf_path)
        layout = detect_layout(pdf_path)
        if layout == "scanned":
            print(f"[SKIP] {filename}: Scanned image PDF (OCR required)")
            continue

        try:
            doc_parser = get_parser(pdf_path)
            doc = doc_parser.parse()
            summary = engine.validate_document(doc)
            summaries.append((doc, summary))

            status_str = "PASS" if summary.passed else "FAIL"
            print(f"[{status_str}] {doc.document_number} ({doc.document_type}, {float(doc.totals.gross_total):.2f} EUR):")
            for c in summary.checks:
                c_status = "PASS" if c.passed else f"FAIL ({c.severity})"
                print(f"       [{c.check_id}] {c.name}: {c_status}")
                if not c.passed:
                    print(f"             -> Details: {c.details}")

        except Exception as e:
            print(f"[ERROR] Failed to validate {filename}: {e}", file=sys.stderr)

    print("=" * 75)
    passed_count = sum(1 for _, s in summaries if s.passed)
    print(f"Reconciliation Summary: {passed_count}/{len(summaries)} documents passed all reconciliation checks.")

    # Generate Markdown report
    report_content = generate_markdown_report(summaries, args.report_file)
    print(f"Validation report successfully written to: {os.path.abspath(args.report_file)}")


if __name__ == "__main__":
    main()
