# KESSLER FP ENGINE — Failure & Edge Case Diagnostic Log

This document records the critical failure modes, unexpected layout edge cases, arithmetic anomalies, and software engineering obstacles encountered and resolved during the engineering of the **KESSLER FP ENGINE**.

---

## Issue 1: Layout Boundary Conflict on Values $\ge$ 1,000 EUR (Layout V1)

### Symptom:
During early runs on `INV-04_RE-2026-10457.pdf`, Position 7 was extracted with `discount_percent = 1284.52` and `line_total = 0.0`.

### Root Cause Analysis:
In `fingerprints/kessler_v1.py`, initial column boundaries set the boundary between the `Rab. %` column and the `Gesamt €` column as:
```python
COL_RAB_MAX = 520
COL_GESAMT_MIN = 520
```
While short line totals (e.g. `385,20` with $x_0 \approx 526.76$) and small discounts (e.g. `5` with $x_0 \approx 499.84$) fell into their respective buckets, amounts exceeding 1,000 EUR (e.g., `1.284,52` in Pos 7) have 8 visual characters and begin further to the left at:
$$x_0 = 519.67$$
Because $519.67 < 520$, the parser classified `1.284,52` as belonging to the discount column (`rab`), leaving `gesamt` empty.

### Resolution:
Inspected the exact word coordinates across all 4 V1 documents:
- Maximum $x_1$ of any discount token: $504.57$
- Minimum $x_0$ of any total token: $516.74$ (the header `"Gesamt"`) and $519.67$ (the value `"1.284,52"`)
Updated the column boundary threshold in `fingerprints/kessler_v1.py` from `520` to `512`:
```python
COL_RAB_MAX = 512
COL_GESAMT_MIN = 512
```
Position 7 was immediately and correctly bucketed with `line_total = 1284.52` and `discount_percent = None`.

---

## Issue 2: INV-04 Printer Transposition Error (+36.00 EUR)

### Symptom:
Check V1 (Line Item Arithmetic) and Check V2 (Net Subtotal by VAT Rate) failed on `INV-04_RE-2026-10457.pdf`:
```
V1: Pos 7 (KI-71004): printed 1284.52 EUR vs calculated 1248.52 EUR (diff: 36.00 EUR)
V2: VAT 19%: sum of line items 5249.22 EUR vs printed net 5213.22 EUR (diff: 36.00 EUR)
```

### Investigation:
- Inspected the PDF visually and extracted text:
  - Quantity: `26 Stk`
  - Unit Price: `48,02 EUR`
  - Printed Gesamt: `1.284,52 EUR`
- Re-calculated:
  $$26 \times 48.02 = 1,248.52\text{ EUR}$$
- Notice that the supplier printed `1.284,52` instead of `1.248,52` (transposition of digits 4 and 8 in the tens and hundreds place).
- Furthermore, the supplier's ERP footer printed:
  $$\text{Nettobetrag 19 \% USt: } 5.213,22\text{ EUR}$$
  Notice that:
  $$5,249.22 - 36.00 = 5,213.22\text{ EUR}$$
  This proves the ERP calculated the invoice total using the correct $1,248.52$, but the print driver emitted the typographical error $1,284.52$.

### Handling Strategy:
- As dictated by `output_schema.json`, the extraction engine must faithfully extract the **printed** value (`1284.52`).
- The financial validation engine properly flags this as an error for accounts payable review before invoice settlement.

---

## Issue 3: Relative Cash Discount (Skonto) Phrasing Variation

### Symptom:
Early regex for Skonto extraction matched INV-01 and INV-02 but failed to extract the Skonto terms in `INV-04_RE-2026-10457.pdf`.

### Root Cause:
In INV-01 and INV-02, the cash discount line included the word `abzüglich`:
`"Bei Zahlung bis 16.10.2026 abzüglich 2 % Skonto (= 19,08 EUR)."`
In INV-04, the wording changed to a relative duration without `abzüglich`:
`"Bei Zahlung innerhalb von 7 Tagen ab Rechnungsdatum 3 % Skonto (= 188,35 EUR)."`

### Resolution:
Enhanced the regular expression in `invoice_parser.py` and `date_parser.py` to make the discount clause optional and dynamically compute the deadline date from the invoice date:
```python
r'Bei Zahlung (?:bis\s+([0-9.]+)|innerhalb von\s+(\d+)\s+Tagen ab Rechnungsdatum)(?:\s+\w+)?\s+([0-9.,]+)\s*%\s*Skonto\s*\(=?\s*([0-9.,]+)\s*EUR\)'
```
If relative days $N$ are captured, `add_days_to_date(document_date, N)` produces the correct ISO date (`2026-10-14` + 7 days = `2026-10-21`).

---

## Issue 4: Scanned Image-Only Document Fallback (INV-06)

### Symptom:
`INV-06_BONUS_scan_RE-2026-10466.pdf` has 0 bytes of extractable text stream and consists of a 1-bit `CCITTFaxDecode` image. When standard text extractors run, they return an empty string.

### Analysis:
1. Attempted OCR verification: Tesseract binary is not installed in the system environment (`shutil.which('tesseract') == None`).
2. Without local OCR engine binaries, running naive OCR causes an unhandled exception or crash.

### Resolution:
- Engineered proactive modality detection in `fingerprints.detector.detect_layout()`:
  - If `len(page.get_text('text').strip()) == 0` and images exist: returns `"scanned"`.
- `extract.py` and `validate.py` detect `"scanned"` documents and log clear, non-crashing informational warnings:
  `"[WARN] INV-06_BONUS_scan_RE-2026-10466.pdf: Scanned image PDF detected. Text extraction requires OCR (skipped)."`
- All 5 text documents continue processing with 100% success.

---

## Issue 5: Calendar Validation in Date Parser

### Symptom:
`parse_date("32.13.2026")` previously returned `"2026-13-32"` instead of raising a `ValueError`.

### Root Cause:
The initial implementation only checked the regex `^\d{1,2}\.\d{1,2}\.\d{4}$` and formatted the integers into an ISO string without validating day/month bounds against the calendar.

### Resolution:
Added strict calendar instantiation via `datetime(year, month, day)` in `core/date_parser.py`. Any non-existent or invalid date (e.g. month 13 or February 30) raises an immediate `ValueError`.

---

## Issue 6: Table Header Blacklist Keyword Over-matching Dropping Continuation Lines

### Symptom:
In `INV-02_RE-2026-10431.pdf`, Position 70 (`KI-63310`) and Position 190 (`KI-71004`) lost their multi-line continuation descriptions (`"Ersatz für Pos. 12 aus Auftrag 4500091180"`).

### Root Cause:
`_is_skip_line_v1` checked whether individual skip words appeared in the concatenated line text:
```python
skip_keywords = ['Übertrag', 'Pos.', 'Art.-Nr.', 'Bezeichnung', ...]
for kw in skip_keywords:
    if kw in combined:
        return True
```
Because the continuation line contained `"Pos. 12"`, the presence of `"Pos."` triggered an unwanted skip, discarding legitimate descriptive text.

### Resolution:
Refactored header detection to use composite structural criteria:
```python
if 'Art.-Nr.' in combined and ('Bezeichnung' in combined or 'Einzelpreis' in combined or 'Pos.' in combined):
    return True
if ('Pos.' in buckets['pos'] or 'Pos' in buckets['pos']) and ('Art.-Nr.' in buckets['art'] or 'Artikel' in buckets['art']):
    return True
```
Removed `'Pos.'`, `'Art.-Nr.'`, and `'Bezeichnung'` from naive substring matching. Positions 70 and 190 now fully preserve their complete multi-line descriptions.

---

## Issue 7: Trailing Minus with Currency Symbols in Number Parser

### Symptom:
`parse_german_number("225,80- €")` and `parse_german_number("476,06- EUR")` raised `ValueError: Cannot parse as number: '225.80-'`.

### Root Cause:
`s.endswith('-')` was checked before stripping currency symbols (`€`, `EUR`) and whitespace. Because the string ended with currency symbols, the trailing minus was not removed prior to `Decimal` conversion.

### Resolution:
Normalized whitespace, stripped non-breaking spaces (`\u00a0`, `\u202f`), stripped currency strings/symbols and percentage signs first, and then parsed leading/trailing minus or plus signs.

---

## Issue 8: Date Parser Idempotence & Trailing Sentence Punctuation

### Symptom:
Passing an already-formatted ISO 8601 date (e.g. `parse_date("2026-10-19")`) or a date followed by a period from invoice text (e.g. `"bis 18. November 2026."`) raised a `ValueError`.

### Root Cause:
The parser only matched German dot-notation or month strings without accommodating ISO format idempotence or trailing sentence periods.

### Resolution:
Added ISO 8601 regex check `^(\d{4})-(\d{2})-(\d{2})$` for idempotence, stripped sentence-terminal punctuation, and added Austrian German month aliases (`jänner`, `jaenner`).

---

## Issue 9: Multi-Page V2 Architecture and Dynamic Address Block Resolution

### Symptom:
`_parse_v2` indexed `all_words[0]`, which would drop pages 1+ on multi-page V2 layouts. Furthermore, buyer address extraction initially relied on searching for the hardcoded string `"Rheinwerk"`.

### Resolution:
- Updated `parse_v2_line_items` to iterate over all pages.
- Replaced hardcoded `"Rheinwerk"` search with dynamic DIN 5008 return address boundary detection: the recipient address block is located immediately under the supplier's sender return line (`Kessler Industrietechnik GmbH · Gewerbestraße 14 · 73760 Ostfildern`), with fallback to postal code anchoring.
