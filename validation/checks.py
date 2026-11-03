"""
validation/checks.py — Financial reconciliation and integrity checks (V1 through V7).
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List, Dict
from core.models import InvoiceDocument


@dataclass
class CheckResult:
    check_id: str
    name: str
    passed: bool
    details: str
    difference: Optional[float] = None
    severity: str = "ERROR"  # "ERROR", "WARNING", "INFO"


def check_v1_line_items(doc: InvoiceDocument, tolerance: float = 0.02) -> CheckResult:
    """
    V1: Line Item Arithmetic Reconciliation.
    Verifies: quantity * (unit_price / price_unit) * (1 - discount_percent/100) == line_total.
    For credit notes, line_total must be negative.
    """
    errors = []
    max_diff = 0.0

    for it in doc.line_items:
        qty = float(it.quantity)
        price = float(it.unit_price)
        pe = float(it.price_unit) if float(it.price_unit) != 0 else 1.0
        disc = float(it.discount_percent) if it.discount_percent is not None else 0.0

        mult = (qty * price) / pe
        calc = round(mult * (1.0 - disc / 100.0), 2)
        if doc.document_type == "credit_note":
            calc = -abs(calc)

        actual = float(it.line_total)
        diff = abs(actual - calc)
        if diff > tolerance:
            errors.append(
                f"Pos {it.position} ({it.article_number}): printed {actual:.2f} EUR vs calculated {calc:.2f} EUR (diff: {diff:.2f} EUR)"
            )
            if diff > max_diff:
                max_diff = diff

    if errors:
        return CheckResult(
            check_id="V1",
            name="Line Item Arithmetic Reconciliation",
            passed=False,
            details="; ".join(errors),
            difference=round(max_diff, 2),
            severity="ERROR",
        )
    return CheckResult(
        check_id="V1",
        name="Line Item Arithmetic Reconciliation",
        passed=True,
        details=f"All {len(doc.line_items)} line items verified within {tolerance} EUR tolerance.",
        difference=0.0,
        severity="INFO",
    )


def check_v2_net_by_vat(doc: InvoiceDocument, tolerance: float = 0.02) -> CheckResult:
    """
    V2: Net Subtotal by VAT Rate Reconciliation.
    Verifies: sum(line_items for vat_rate R) == totals.net_by_vat_rate[R].
    Also verifies all line item VAT rates are accounted for in totals.net_by_vat_rate.
    """
    errors = []
    max_diff = 0.0

    line_vat_rates = {str(it.vat_rate) for it in doc.line_items}
    totals_vat_rates = set(doc.totals.net_by_vat_rate.keys())

    missing_rates = line_vat_rates - totals_vat_rates
    for r in sorted(missing_rates):
        errors.append(f"Line items contain VAT rate {r}%, but this rate is missing from totals.net_by_vat_rate")

    for rate_str, printed_net in doc.totals.net_by_vat_rate.items():
        try:
            rate_int = int(rate_str)
        except ValueError:
            rate_int = 19
        line_sum = sum(
            float(it.line_total) for it in doc.line_items if it.vat_rate == rate_int
        )
        printed = float(printed_net)
        diff = abs(printed - line_sum)
        if diff > tolerance:
            errors.append(
                f"VAT {rate_str}%: sum of line items {line_sum:.2f} EUR vs printed net {printed:.2f} EUR (diff: {diff:.2f} EUR)"
            )
            if diff > max_diff:
                max_diff = diff

    if errors:
        return CheckResult(
            check_id="V2",
            name="Net Subtotal by VAT Rate Reconciliation",
            passed=False,
            details="; ".join(errors),
            difference=round(max_diff, 2),
            severity="ERROR",
        )
    return CheckResult(
        check_id="V2",
        name="Net Subtotal by VAT Rate Reconciliation",
        passed=True,
        details="Sum of line items matches net subtotals for all VAT rates.",
        difference=0.0,
        severity="INFO",
    )


def check_v3_net_total(doc: InvoiceDocument, tolerance: float = 0.02) -> CheckResult:
    """
    V3: Net Total Reconciliation.
    Verifies: sum(totals.net_by_vat_rate.values()) == totals.net_total.
    """
    sum_net = sum(float(v) for v in doc.totals.net_by_vat_rate.values())
    net_total = float(doc.totals.net_total)
    diff = abs(sum_net - net_total)

    if diff > tolerance:
        return CheckResult(
            check_id="V3",
            name="Net Total Reconciliation",
            passed=False,
            details=f"Sum of net rates {sum_net:.2f} EUR != net total {net_total:.2f} EUR (diff: {diff:.2f} EUR)",
            difference=round(diff, 2),
            severity="ERROR",
        )
    return CheckResult(
        check_id="V3",
        name="Net Total Reconciliation",
        passed=True,
        details=f"Net total {net_total:.2f} EUR matches sum of VAT net buckets.",
        difference=0.0,
        severity="INFO",
    )


def check_v4_vat_calculation(doc: InvoiceDocument, tolerance: float = 0.03) -> CheckResult:
    """
    V4: VAT Calculation Reconciliation.
    Verifies: totals.net_by_vat_rate[R] * (R / 100) == totals.vat_by_vat_rate[R].
    Tolerance is 0.03 EUR to accommodate standard rounding.
    """
    errors = []
    max_diff = 0.0

    for r in sorted(set(doc.totals.vat_by_vat_rate.keys()) - set(doc.totals.net_by_vat_rate.keys())):
        errors.append(f"VAT rate {r}% exists in totals.vat_by_vat_rate but missing from totals.net_by_vat_rate")

    for rate_str, printed_net in doc.totals.net_by_vat_rate.items():
        rate = float(rate_str)
        calc_vat = float(printed_net) * (rate / 100.0)
        printed_vat = float(doc.totals.vat_by_vat_rate.get(rate_str, 0.0))
        diff = abs(printed_vat - calc_vat)
        if diff > tolerance:
            errors.append(
                f"VAT {rate_str}%: expected {calc_vat:.2f} EUR on {float(printed_net):.2f} EUR net, got {printed_vat:.2f} EUR (diff: {diff:.2f} EUR)"
            )
            if diff > max_diff:
                max_diff = diff

    if errors:
        return CheckResult(
            check_id="V4",
            name="VAT Calculation Reconciliation",
            passed=False,
            details="; ".join(errors),
            difference=round(max_diff, 2),
            severity="ERROR",
        )
    return CheckResult(
        check_id="V4",
        name="VAT Calculation Reconciliation",
        passed=True,
        details="Calculated VAT matches printed VAT for all rates.",
        difference=0.0,
        severity="INFO",
    )


def check_v5_vat_total(doc: InvoiceDocument, tolerance: float = 0.02) -> CheckResult:
    """
    V5: Total VAT Reconciliation.
    Verifies: sum(totals.vat_by_vat_rate.values()) == totals.vat_total.
    """
    sum_vat = sum(float(v) for v in doc.totals.vat_by_vat_rate.values())
    vat_total = float(doc.totals.vat_total)
    diff = abs(sum_vat - vat_total)

    if diff > tolerance:
        return CheckResult(
            check_id="V5",
            name="Total VAT Reconciliation",
            passed=False,
            details=f"Sum of VAT rates {sum_vat:.2f} EUR != VAT total {vat_total:.2f} EUR (diff: {diff:.2f} EUR)",
            difference=round(diff, 2),
            severity="ERROR",
        )
    return CheckResult(
        check_id="V5",
        name="Total VAT Reconciliation",
        passed=True,
        details=f"VAT total {vat_total:.2f} EUR matches sum of VAT buckets.",
        difference=0.0,
        severity="INFO",
    )


def check_v6_gross_total(doc: InvoiceDocument, tolerance: float = 0.02) -> CheckResult:
    """
    V6: Gross Total Reconciliation.
    Verifies: totals.net_total + totals.vat_total == totals.gross_total.
    """
    calc_gross = float(doc.totals.net_total) + float(doc.totals.vat_total)
    gross_total = float(doc.totals.gross_total)
    diff = abs(calc_gross - gross_total)

    if diff > tolerance:
        return CheckResult(
            check_id="V6",
            name="Gross Total Reconciliation",
            passed=False,
            details=f"net ({float(doc.totals.net_total):.2f}) + vat ({float(doc.totals.vat_total):.2f}) = {calc_gross:.2f} EUR != gross {gross_total:.2f} EUR (diff: {diff:.2f} EUR)",
            difference=round(diff, 2),
            severity="ERROR",
        )
    return CheckResult(
        check_id="V6",
        name="Gross Total Reconciliation",
        passed=True,
        details=f"Gross total {gross_total:.2f} EUR matches net + vat.",
        difference=0.0,
        severity="INFO",
    )


def check_v7_cash_discount(doc: InvoiceDocument, tolerance: float = 0.02) -> CheckResult:
    """
    V7: Cash Discount (Skonto) Reconciliation.
    Verifies: if cash_discount is present, gross_total * (percent / 100) == amount.
    Also verifies discount deadline is before or on due_date.
    """
    if doc.cash_discount is None:
        return CheckResult(
            check_id="V7",
            name="Cash Discount (Skonto) Reconciliation",
            passed=True,
            details="No cash discount printed or applicable (OK).",
            difference=0.0,
            severity="INFO",
        )

    gross = float(doc.totals.gross_total)
    pct = float(doc.cash_discount.percent)
    calc_amt = gross * (pct / 100.0)
    actual_amt = float(doc.cash_discount.amount)
    diff = abs(calc_amt - actual_amt)

    if diff > tolerance:
        return CheckResult(
            check_id="V7",
            name="Cash Discount (Skonto) Reconciliation",
            passed=False,
            details=f"Expected {pct}% on {gross:.2f} EUR = {calc_amt:.2f} EUR, printed amount is {actual_amt:.2f} EUR (diff: {diff:.2f} EUR)",
            difference=round(diff, 2),
            severity="WARNING",
        )

    # Check date logic if due_date is present
    if doc.due_date and doc.cash_discount.until > doc.due_date:
        return CheckResult(
            check_id="V7",
            name="Cash Discount (Skonto) Reconciliation",
            passed=False,
            details=f"Skonto deadline {doc.cash_discount.until} is after due date {doc.due_date}.",
            difference=0.0,
            severity="WARNING",
        )

    return CheckResult(
        check_id="V7",
        name="Cash Discount (Skonto) Reconciliation",
        passed=True,
        details=f"Cash discount {pct}% = {actual_amt:.2f} EUR verified against gross total {gross:.2f} EUR.",
        difference=0.0,
        severity="INFO",
    )
