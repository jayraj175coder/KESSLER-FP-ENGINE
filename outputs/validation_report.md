# KESSLER Financial Reconciliation & Document Intelligence Audit Report

> **Generated at:** 2026-11-03 09:38:36  
> **Engine:** KESSLER FP ENGINE v1.0.0  
> **Audit Status:** ⚠️ DISCREPANCIES DETECTED

---

## 1. Executive Summary

| Metric | Value |
|---|---|
| Total Documents Processed | **5** |
| Documents Reconciled (PASS) | **4** |
| Documents with Discrepancies (FAIL) | **1** |
| Total Net Volume Audited | **11,765.55 EUR** |
| Total VAT Volume Audited | **2,182.85 EUR** |
| Total Gross Volume Audited | **13,948.40 EUR** |

### Document Status Overview

| Document | Type | Gross Total | Status | Failed Checks |
|---|---|---|---|---|
| `RE-2026-10418` | `invoice` | 953.75 EUR | ✅ PASS | None |
| `RE-2026-10431` | `invoice` | 6,037.86 EUR | ✅ PASS | None |
| `GS-2026-00872` | `credit_note` | -476.06 EUR | ✅ PASS | None |
| `RE-2026-10457` | `invoice` | 6,278.42 EUR | ❌ FAIL | V1, V2 |
| `2026-R-00117` | `invoice` | 1,154.43 EUR | ✅ PASS | None |

---

## 2. Reconciliation Checks Specification

| Check ID | Check Name | Description | Severity |
|---|---|---|---|
| **V1** | Line Item Arithmetic | `quantity * (unit_price / price_unit) * (1 - discount) == line_total` | ERROR |
| **V2** | Net Subtotal by VAT Rate | `sum(line_totals by VAT rate) == printed net_by_vat_rate` | ERROR |
| **V3** | Net Total Reconciliation | `sum(net_by_vat_rate) == totals.net_total` | ERROR |
| **V4** | VAT Calculation Reconciliation | `net_by_vat_rate * VAT_rate == printed vat_by_vat_rate` | ERROR |
| **V5** | Total VAT Reconciliation | `sum(vat_by_vat_rate) == totals.vat_total` | ERROR |
| **V6** | Gross Total Reconciliation | `net_total + vat_total == gross_total` | ERROR |
| **V7** | Cash Discount (Skonto) | `gross_total * discount_% == discount_amount` & deadline check | WARNING |

---

## 3. Detailed Document Audits

### ✅ Document: `RE-2026-10418` (invoice)

- **Date:** 2026-10-06 | **Service Date:** 2026-10-02 | **Due Date:** 2026-11-05
- **Supplier:** Kessler Industrietechnik GmbH (`DE287364519`)
- **Buyer:** Rheinwerk Anlagenbau AG (Cust. No. `40217`)
- **Order Ref:** `4500093317` | **Delivery Note:** `LS-58821`
- **Line Items:** 6 items
- **Financial Totals:** Net: 801.47 EUR | VAT: 152.28 EUR | Gross: 953.75 EUR

#### Validation Results

| Check | Name | Result | Details |
|---|---|---|---|
| `V1` | Line Item Arithmetic Reconciliation | ✅ PASS | All 6 line items verified within 0.02 EUR tolerance. |
| `V2` | Net Subtotal by VAT Rate Reconciliation | ✅ PASS | Sum of line items matches net subtotals for all VAT rates. |
| `V3` | Net Total Reconciliation | ✅ PASS | Net total 801.47 EUR matches sum of VAT net buckets. |
| `V4` | VAT Calculation Reconciliation | ✅ PASS | Calculated VAT matches printed VAT for all rates. |
| `V5` | Total VAT Reconciliation | ✅ PASS | VAT total 152.28 EUR matches sum of VAT buckets. |
| `V6` | Gross Total Reconciliation | ✅ PASS | Gross total 953.75 EUR matches net + vat. |
| `V7` | Cash Discount (Skonto) Reconciliation | ✅ PASS | Cash discount 2.0% = 19.08 EUR verified against gross total 953.75 EUR. |

### ✅ Document: `RE-2026-10431` (invoice)

- **Date:** 2026-10-09 | **Service Date:** 2026-10-07 | **Due Date:** 2026-11-08
- **Supplier:** Kessler Industrietechnik GmbH (`DE287364519`)
- **Buyer:** Rheinwerk Anlagenbau AG (Cust. No. `40217`)
- **Order Ref:** `4500093402` | **Delivery Note:** `LS-58907`
- **Line Items:** 26 items
- **Financial Totals:** Net: 5,105.98 EUR | VAT: 931.88 EUR | Gross: 6,037.86 EUR

#### Validation Results

| Check | Name | Result | Details |
|---|---|---|---|
| `V1` | Line Item Arithmetic Reconciliation | ✅ PASS | All 26 line items verified within 0.02 EUR tolerance. |
| `V2` | Net Subtotal by VAT Rate Reconciliation | ✅ PASS | Sum of line items matches net subtotals for all VAT rates. |
| `V3` | Net Total Reconciliation | ✅ PASS | Net total 5105.98 EUR matches sum of VAT net buckets. |
| `V4` | VAT Calculation Reconciliation | ✅ PASS | Calculated VAT matches printed VAT for all rates. |
| `V5` | Total VAT Reconciliation | ✅ PASS | VAT total 931.88 EUR matches sum of VAT buckets. |
| `V6` | Gross Total Reconciliation | ✅ PASS | Gross total 6037.86 EUR matches net + vat. |
| `V7` | Cash Discount (Skonto) Reconciliation | ✅ PASS | Cash discount 2.0% = 120.76 EUR verified against gross total 6037.86 EUR. |

### ✅ Document: `GS-2026-00872` (credit_note)

- **Date:** 2026-10-12 | **Service Date:** N/A | **Due Date:** N/A
- **Supplier:** Kessler Industrietechnik GmbH (`DE287364519`)
- **Buyer:** Rheinwerk Anlagenbau AG (Cust. No. `40217`)
- **Order Ref:** `4500092977` | **Delivery Note:** `LS-58733` | **Ref. Invoice:** `RE-2026-10133`
- **Line Items:** 3 items
- **Financial Totals:** Net: -400.05 EUR | VAT: -76.01 EUR | Gross: -476.06 EUR

#### Validation Results

| Check | Name | Result | Details |
|---|---|---|---|
| `V1` | Line Item Arithmetic Reconciliation | ✅ PASS | All 3 line items verified within 0.02 EUR tolerance. |
| `V2` | Net Subtotal by VAT Rate Reconciliation | ✅ PASS | Sum of line items matches net subtotals for all VAT rates. |
| `V3` | Net Total Reconciliation | ✅ PASS | Net total -400.05 EUR matches sum of VAT net buckets. |
| `V4` | VAT Calculation Reconciliation | ✅ PASS | Calculated VAT matches printed VAT for all rates. |
| `V5` | Total VAT Reconciliation | ✅ PASS | VAT total -76.01 EUR matches sum of VAT buckets. |
| `V6` | Gross Total Reconciliation | ✅ PASS | Gross total -476.06 EUR matches net + vat. |
| `V7` | Cash Discount (Skonto) Reconciliation | ✅ PASS | No cash discount printed or applicable (OK). |

### ❌ Document: `RE-2026-10457` (invoice)

- **Date:** 2026-10-14 | **Service Date:** 2026-10-13 | **Due Date:** 2026-11-13
- **Supplier:** Kessler Industrietechnik GmbH (`DE287364519`)
- **Buyer:** Rheinwerk Anlagenbau AG (Cust. No. `40217`)
- **Order Ref:** `4500093560` | **Delivery Note:** `LS-59012`
- **Line Items:** 15 items
- **Financial Totals:** Net: 5,283.02 EUR | VAT: 995.40 EUR | Gross: 6,278.42 EUR

#### Validation Results

| Check | Name | Result | Details |
|---|---|---|---|
| `V1` | Line Item Arithmetic Reconciliation | ❌ **ERROR** | Pos 7 (KI-71004): printed 1284.52 EUR vs calculated 1248.52 EUR (diff: 36.00 EUR) |
| `V2` | Net Subtotal by VAT Rate Reconciliation | ❌ **ERROR** | VAT 19%: sum of line items 5249.22 EUR vs printed net 5213.22 EUR (diff: 36.00 EUR) |
| `V3` | Net Total Reconciliation | ✅ PASS | Net total 5283.02 EUR matches sum of VAT net buckets. |
| `V4` | VAT Calculation Reconciliation | ✅ PASS | Calculated VAT matches printed VAT for all rates. |
| `V5` | Total VAT Reconciliation | ✅ PASS | VAT total 995.40 EUR matches sum of VAT buckets. |
| `V6` | Gross Total Reconciliation | ✅ PASS | Gross total 6278.42 EUR matches net + vat. |
| `V7` | Cash Discount (Skonto) Reconciliation | ✅ PASS | Cash discount 3.0% = 188.35 EUR verified against gross total 6278.42 EUR. |

#### Root Cause Analysis of Failure

> 🔍 **Audit Finding:**
> - **V1 (Line Item Arithmetic Reconciliation):** Pos 7 (KI-71004): printed 1284.52 EUR vs calculated 1248.52 EUR (diff: 36.00 EUR)
> - **V2 (Net Subtotal by VAT Rate Reconciliation):** VAT 19%: sum of line items 5249.22 EUR vs printed net 5213.22 EUR (diff: 36.00 EUR)

### ✅ Document: `2026-R-00117` (invoice)

- **Date:** 2026-10-19 | **Service Date:** 2026-10-16 | **Due Date:** 2026-11-18
- **Supplier:** Kessler Industrietechnik GmbH (`DE287364519`)
- **Buyer:** Rheinwerk Anlagenbau AG (Cust. No. `40217`)
- **Order Ref:** `4500093701` | **Delivery Note:** `LS-59188`
- **Line Items:** 5 items
- **Financial Totals:** Net: 975.13 EUR | VAT: 179.30 EUR | Gross: 1,154.43 EUR

#### Validation Results

| Check | Name | Result | Details |
|---|---|---|---|
| `V1` | Line Item Arithmetic Reconciliation | ✅ PASS | All 5 line items verified within 0.02 EUR tolerance. |
| `V2` | Net Subtotal by VAT Rate Reconciliation | ✅ PASS | Sum of line items matches net subtotals for all VAT rates. |
| `V3` | Net Total Reconciliation | ✅ PASS | Net total 975.13 EUR matches sum of VAT net buckets. |
| `V4` | VAT Calculation Reconciliation | ✅ PASS | Calculated VAT matches printed VAT for all rates. |
| `V5` | Total VAT Reconciliation | ✅ PASS | VAT total 179.30 EUR matches sum of VAT buckets. |
| `V6` | Gross Total Reconciliation | ✅ PASS | Gross total 1154.43 EUR matches net + vat. |
| `V7` | Cash Discount (Skonto) Reconciliation | ✅ PASS | No cash discount printed or applicable (OK). |

---

## 4. Key Findings & Financial Integrity Takeaways

1. **INV-04 Printing Typo / Transposition Error:**
   - In `INV-04_RE-2026-10457.pdf`, line item position 7 (`KI-71004`, Zahnriemen HTD 8M-1200-30) has quantity 26 and unit price 48.02 EUR.
   - The true calculated amount is `26 × 48.02 = 1,248.52 EUR`.
   - The supplier's PDF printer transposed the digits '4' and '8', printing `1.284,52 EUR` (+36.00 EUR error).
   - The ERP footer calculation used the correct 1,248.52 EUR, which produced `Net 19% = 5,213.22 EUR`.
   - As a result, Check V1 flags the line arithmetic error (+36.00 EUR), and Check V2 flags the discrepancy between the sum of printed line totals (5,249.22 EUR) and the printed net subtotal (5,213.22 EUR).

2. **INV-03 Credit Note Negative Handling:**
   - All credit note amounts carry trailing minus signs in the German original (`400,05-`, `76,01-`, `476,06- EUR`).
   - The engine correctly normalizes these to negative values (`-400.05`, `-76.01`, `-476.06 EUR`).
   - All reconciliation checks (V1 through V6) pass perfectly on negative amounts.

3. **Multi-VAT Reconciliation in INV-02 and INV-04:**
   - Books (`BU-90011`, `BU-90034`) are taxed at the reduced 7% rate; hardware items are taxed at standard 19%.
   - Both VAT buckets reconcile independently with 100% precision across net subtotals and VAT sums.

4. **Layout Evolution (V1 to V2 in INV-05):**
   - INV-05 features the redesigned layout with German month strings, combined `Menge Einh.` columns, and discount rows (`abzgl. Sonderrabatt`).
   - All V1-V7 financial checks pass cleanly on V2.
