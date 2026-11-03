# KESSLER FP ENGINE

> **Supplier Fingerprinting, Document Intelligence & Financial Reconciliation**  
> *DeepLogic AI — Software Engineer Intern (Data & Development) Take-Home Assignment*

---

## Overview

**KESSLER FP ENGINE** is a production-grade document intelligence and financial reconciliation pipeline specifically engineered to ingest, parse, normalize, and audit complex business-to-business PDF invoices and credit notes from **Kessler Industrietechnik GmbH**.

The system addresses the fundamental challenges of real-world document processing:
1. **Supplier Layout Fingerprinting**: Automatically detects document layout versions (V1 vs redesigned V2) and document modalities (vector PDF vs scanned image).
2. **Coordinate-Aware Table Extraction**: Reconstructs tabular line items using geometric x/y word bounding boxes from PyMuPDF, overcoming combined columns (e.g., `Einzelpreis € PE` = `14,60 100`) and sub-row discount lines (`abzgl. Sonderrabatt`).
3. **Multi-Page Reconciliation & Anomaly Filtering**: Seamlessly filters out pagination carry-forward headers (`Übertrag`, `Übertrag von Seite N`) across multi-page documents without dropping legitimate line items.
4. **Strict JSON Schema Conformance**: Validates all extractions against the official `JSON Schema 2020-12` standard.
5. **Multi-Stage Financial Reconciliation Engine (Checks V1 – V7)**: Runs an end-to-end 7-point audit trail from line-level arithmetic to gross totals, catching subtle supplier errors (such as typographical transposition errors in invoice line items).

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │          Input PDF Document         │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │      core.pdf_reader (PyMuPDF)      │
                    │   - Word extraction & coordinates   │
                    │   - Raw text & image detection      │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │        fingerprints.detector        │
                    │   - V1 vs V2 layout fingerprint     │
                    │   - Scanned image detection         │
                    └──────────────────┬──────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │   parsers.InvoiceParser   │                 │ parsers.CreditNoteParser  │
  │   - Header & buyer parser │                 │   - Reference invoice     │
  │   - Line item coordinate  │                 │   - Negative totals       │
  │     bucketing (V1 / V2)   │                 │   - Null service/due date │
  │   - Cash discount parser  │                 └─────────────┬─────────────┘
  └─────────────┬─────────────┘                               │
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │       core.schema_validator         │
                    │   - JSON Schema 2020-12 Validator   │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │      validation.ValidationEngine    │
                    │   - Check V1: Line Item Math        │
                    │   - Check V2: Net Subtotal by VAT   │
                    │   - Check V3: Total Net Sum         │
                    │   - Check V4: VAT Rate Calculations │
                    │   - Check V5: Total VAT Sum         │
                    │   - Check V6: Gross Total Reconcile │
                    │   - Check V7: Cash Discount / Terms │
                    └──────────────────┬──────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
         ┌─────────────────────────────┐┌─────────────────────────────┐
         │ outputs/{DOC_NAME}.json     ││ outputs/validation_report.md│
         └─────────────────────────────┘└─────────────────────────────┘
```

---

## Directory Structure

```
kessler-fp-engine/
├── core/
│   ├── __init__.py
│   ├── models.py              # Strongly-typed dataclasses & schema serialization
│   ├── pdf_reader.py          # PyMuPDF word-coordinate & text extraction
│   ├── number_parser.py       # Robust German decimal/thousands number parsing
│   ├── date_parser.py         # German V1/V2 date parsing and calendar validation
│   ├── text_normalizer.py     # String cleaning and whitespace normalization
│   └── schema_validator.py    # Draft 2020-12 JSON Schema validation
├── fingerprints/
│   ├── __init__.py
│   ├── detector.py            # Layout detection (kessler_v1, kessler_v2, scanned)
│   ├── kessler_v1.py          # Layout V1 geometric boundary constants
│   └── kessler_v2.py          # Layout V2 geometric boundary constants
├── parsers/
│   ├── __init__.py            # get_parser factory
│   ├── base_parser.py         # Abstract base class
│   ├── invoice_parser.py      # Unified parser for V1 and V2 invoices
│   ├── credit_note_parser.py  # Specialised credit note parser
│   └── line_item_parser.py    # Coordinate-based line item grouping & bucketing
├── validation/
│   ├── __init__.py
│   ├── checks.py              # Financial checks V1 through V7
│   ├── engine.py              # Validation orchestrator & summary metrics
│   └── report_generator.py    # Markdown audit report generator
├── inputs/                    # Input PDFs and schemas
├── outputs/                   # Generated JSON extractions & validation_report.md
├── tests/
│   ├── conftest.py
│   ├── test_number_parser.py   # German numeric formatting unit tests
│   ├── test_date_parser.py     # Date parsing & calendar edge cases
│   ├── test_layout_detection.py# Fingerprinting tests
│   ├── test_line_items.py      # Tabular extraction tests across all docs
│   ├── test_schema.py          # Schema conformance & INV-01 exact match test
│   └── test_validation.py      # Financial reconciliation V1-V7 test suite
├── extract.py                 # Extractor CLI
├── validate.py                # Validator CLI
├── pytest.ini                 # Pytest configuration
├── requirements.txt           # Project dependencies
├── README.md                  # System documentation
├── MARKING_NOTES.md           # Engineering rationale & interview guide
├── FAILURE_LOG.md             # Edge case & diagnostic failure log
└── AI_USAGE.md                # AI transparency & methodology disclosure
```

---

## Quickstart & Execution

### 1. Requirements & Installation

Python 3.10+ is recommended.

```bash
pip install -r requirements.txt
```

### 2. Run Document Extraction

To extract all PDFs in `inputs/` and generate schema-compliant JSON files into `outputs/`:

```bash
python extract.py
```

Options:
- `--input-dir <DIR>`: Custom input directory containing PDFs.
- `--output-dir <DIR>`: Custom directory for JSON outputs.
- `--file <PDF>`: Process a single PDF file.

### 3. Run Financial Reconciliation

To audit all extracted invoices against checks V1 through V7 and generate the audit report:

```bash
python validate.py
```

Generated report: `outputs/validation_report.md`.

### 4. Run Test Suite

Run all unit and integration tests with pytest:

```bash
python -m pytest -v
```

Expected output: `36 passed in ~1.2s` (100% pass rate).

---

## Layout Comparison: V1 vs V2

| Feature | Layout V1 (INV-01, 02, 03, 04) | Layout V2 (INV-05) |
|---|---|---|
| **Invoice Number** | `Rechnungs-Nr.` | `Rechnung Nr.` |
| **Document Date** | `DD.MM.YYYY` (e.g. `06.10.2026`) | `DD. Monat YYYY` (e.g. `19. Oktober 2026`) |
| **Service Date** | `Leistungsdatum` | `Lieferdatum` |
| **Order Reference** | `Ihre Bestellung: 4500093317 vom ...` | `Bestellnummer: 4500093701` |
| **Customer Number**| `Kunden-Nr.` | `Kundennummer` |
| **Price Column** | `Einzelpreis € PE` (Combined, e.g. `14,60 100`) | `Preis/Einh.` (Always per piece, e.g. `0,152 €`) |
| **Quantity Column** | `Menge` and `ME` separate columns | `Menge Einh.` combined into single column |
| **Discount Handling** | `Rab. %` column value (e.g. `5`, `10`) | Dedicated sub-row (`abzgl. Sonderrabatt 3 % auf 465,60 €`) |
| **Cash Discount** | `Bei Zahlung bis...` / `innerhalb von N Tagen...` | Explicitly marked `Kein Skontoabzug` (`null`) |

---

## Financial Validation Suite (Checks V1 – V7)

Every document undergoes seven strict financial validation rules:

- **Check V1: Line Item Arithmetic Reconciliation**  
  Verifies `quantity * (unit_price / price_unit) * (1 - discount_percent/100) == line_total` (within 0.02 EUR rounding tolerance). Negative amounts enforced for credit notes.
- **Check V2: Net Subtotal by VAT Rate Reconciliation**  
  Verifies that the sum of line item totals for tax rate $R$ equals the printed net subtotal `totals.net_by_vat_rate[R]`.
- **Check V3: Total Net Reconciliation**  
  Verifies that the sum of all net rate buckets equals `totals.net_total`.
- **Check V4: VAT Calculation Reconciliation**  
  Verifies `net_by_vat_rate[R] * (R / 100) == totals.vat_by_vat_rate[R]` within a 0.03 EUR rounding margin.
- **Check V5: Total VAT Reconciliation**  
  Verifies `sum(totals.vat_by_vat_rate.values()) == totals.vat_total`.
- **Check V6: Gross Total Reconciliation**  
  Verifies `totals.net_total + totals.vat_total == totals.gross_total`.
- **Check V7: Cash Discount (Skonto) Reconciliation**  
  Verifies `gross_total * (percent / 100) == amount` and ensures the discount deadline is before or on the invoice `due_date`.

### Audit Result Highlight: The INV-04 Typo
In `INV-04_RE-2026-10457.pdf`, Check V1 and Check V2 immediately flag a **+36.00 EUR discrepancy**:
- Line item 7 (`KI-71004`, Zahnriemen): printed total is `1.284,52 EUR`.
- True arithmetic: $26 \times 48.02 = 1,248.52\text{ EUR}$.
- Digits '4' and '8' were transposed by the supplier's printer.
- The supplier's ERP footer correctly used the calculated subtotal (5,213.22 EUR), causing Check V2 to catch the mismatch between the printed line sum (5,249.22 EUR) and printed net subtotal.

---

## Video Demonstration Script & Outline (Max 10 Minutes)

A complete step-by-step walkthrough script for presenting the solution during technical evaluation:

### 1. Introduction & Architecture (0:00 - 2:00)
- **Problem Statement**: Ingestion and financial audit of industrial invoices across layout evolutions without black-box ML/LLMs.
- **Architectural Overview**: Show project structure (`core/`, `fingerprints/`, `parsers/`, `validation/`).
- **Core Design Decision**: Explain why coordinate-based bounding box bucketing (`fitz.get_text("words")`) was chosen over fragile line-based regexes.

### 2. Live Extraction Run (2:00 - 4:00)
- Run `python extract.py`.
- Walk through terminal output showing automatic layout detection (`v1` for INV-01–04, `v2` for INV-05, `scanned` detection for INV-06).
- Demonstrate 100% JSON Schema 2020-12 compliance across all generated JSON files in `outputs/`.
- Show exact dictionary equality between `outputs/INV-01_RE-2026-10418.json` and `inputs/INV-01_expected_output.json`.

### 3. Deep Dive: Difficult Extraction Challenges (4:00 - 6:00)
- **Challenge 1: The Combined Price/PE Column**:
  - Show INV-01 Position 5 (`KI-20811`, Sechskantschraube DIN 933).
  - Point out that PyMuPDF extracts `14,60 100` into a single cell.
  - Explain how `_build_line_item_v1` detects two numeric tokens in the price bucket: first is unit price (14.60 EUR), second is price unit (100 pieces), yielding correct calculation: $400 \times 14.60 / 100 = 58.40\text{ EUR}$.
- **Challenge 2: Multi-Page Continuation & Description Lines**:
  - Show INV-02 with 26 items over 3 pages.
  - Point out that Pos 70 and Pos 190 include continuation lines like `"Ersatz für Pos. 12 aus Auftrag 4500091180"`.
  - Explain how `parsers/line_item_parser.py` avoids false-positive table header skipping while discarding carry-forwards (`Übertrag`).

### 4. Running the Validation Engine & Explaining Failures (6:00 - 8:30)
- Run `python validate.py`.
- Open `outputs/validation_report.md`.
- Explain how Checks V1 through V7 execute:
  - **INV-01, INV-02, INV-05**: Reconciled cleanly with all checks PASS.
  - **INV-03 (Credit Note)**: Reconciled with all negative totals and credit note reference integrity.
  - **INV-04 (Printer Typo Discovery)**:
    - Check V1 flags Position 7 (`KI-71004`): Printed total `1.284,52 EUR` vs calculated $26 \times 48.02 = 1.248,52\text{ EUR}$ (+36.00 EUR discrepancy).
    - Check V2 flags Net Subtotal 19%: Sum of printed line items (`5,249.22 EUR`) does not match printed subtotal (`5,213.22 EUR`).
    - Explain that preserving printed text while flagging discrepancies in validation is the exact industry best practice for audit systems.

### 5. Automated Testing & Verification (8:30 - 10:00)
- Run `python -m pytest -v`.
- Show all 36 tests passing in ~1.2s covering number parsing, date parsing, layout detection, multi-page line items, schema conformance, and financial reconciliation.
- Summary: Production-minded, deterministic, completely explainable engineering design.

