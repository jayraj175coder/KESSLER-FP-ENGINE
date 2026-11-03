"""
extract.py — CLI tool to extract structured data from PDF invoices and credit notes.

Usage:
    python extract.py [--input-dir DIR] [--output-dir DIR] [--file FILE]
"""
import argparse
import glob
import json
import os
import sys

# Ensure engine modules are on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fingerprints.detector import detect_layout
from parsers import get_parser
from core.schema_validator import validate_output


def extract_pdf(pdf_path: str, output_dir: str) -> dict:
    """Extract a single PDF and write its schema-compliant JSON output."""
    filename = os.path.basename(pdf_path)
    stem = os.path.splitext(filename)[0]
    output_path = os.path.join(output_dir, f"{stem}.json")

    layout = detect_layout(pdf_path)
    if layout == "scanned":
        print(f"[WARN] {filename}: Scanned image PDF detected. Text extraction requires OCR (skipped).")
        return None

    try:
        parser = get_parser(pdf_path)
        doc = parser.parse()
        data = doc.to_dict()

        # Validate against JSON schema
        valid, errors = validate_output(data)
        if not valid:
            print(f"[SCHEMA ERROR] {filename} failed schema validation: {errors}")
        else:
            print(f"[OK] {filename} -> {doc.document_type} {doc.document_number} ({len(doc.line_items)} items) [Schema Valid]")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return data

    except Exception as e:
        print(f"[ERROR] Failed to extract {filename}: {e}", file=sys.stderr)
        return None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="KESSLER FP Engine — PDF Invoice Extractor")
    parser.add_argument(
        "--input-dir",
        default=os.path.join(os.path.dirname(__file__), "inputs"),
        help="Path to directory containing input PDFs"
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "outputs"),
        help="Path to directory for JSON outputs"
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Extract a single specific PDF file"
    )

    args = parser.parse_args()

    # Fallback to ../inputs if inputs doesn't exist
    if not os.path.exists(args.input_dir):
        fallback = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "inputs"))
        if os.path.exists(fallback):
            args.input_dir = fallback

    os.makedirs(args.output_dir, exist_ok=True)

    if args.file:
        files = [args.file]
    else:
        files = sorted(glob.glob(os.path.join(args.input_dir, "*.pdf")))

    if not files:
        print(f"No PDF files found in {args.input_dir}")
        sys.exit(1)

    print(f"KESSLER FP ENGINE — Extracting {len(files)} document(s)...")
    print("=" * 65)

    extracted_count = 0
    for pdf_path in files:
        res = extract_pdf(pdf_path, args.output_dir)
        if res is not None:
            extracted_count += 1

    print("=" * 65)
    print(f"Extraction complete: {extracted_count}/{len(files)} documents extracted successfully.")
    print(f"Output directory: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
