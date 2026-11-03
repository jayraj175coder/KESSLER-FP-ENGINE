"""
validation/engine.py — Financial reconciliation engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict
from core.models import InvoiceDocument
from validation.checks import (
    CheckResult,
    check_v1_line_items,
    check_v2_net_by_vat,
    check_v3_net_total,
    check_v4_vat_calculation,
    check_v5_vat_total,
    check_v6_gross_total,
    check_v7_cash_discount,
)


@dataclass
class ValidationSummary:
    document_number: str
    document_type: str
    checks: List[CheckResult] = field(default_factory=list)
    passed: bool = True
    error_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> dict:
        return {
            "document_number": self.document_number,
            "document_type": self.document_type,
            "passed": self.passed,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "checks": [
                {
                    "check_id": c.check_id,
                    "name": c.name,
                    "passed": c.passed,
                    "details": c.details,
                    "difference": c.difference,
                    "severity": c.severity,
                }
                for c in self.checks
            ],
        }


class ValidationEngine:
    """Orchestrates financial reconciliation checks V1 through V7 on documents."""

    def __init__(self, tolerance: float = 0.02):
        self.tolerance = tolerance

    def validate_document(self, doc: InvoiceDocument) -> ValidationSummary:
        """Run all reconciliation checks on a single document."""
        results: List[CheckResult] = [
            check_v1_line_items(doc, tolerance=self.tolerance),
            check_v2_net_by_vat(doc, tolerance=self.tolerance),
            check_v3_net_total(doc, tolerance=self.tolerance),
            check_v4_vat_calculation(doc, tolerance=0.03),
            check_v5_vat_total(doc, tolerance=self.tolerance),
            check_v6_gross_total(doc, tolerance=self.tolerance),
            check_v7_cash_discount(doc, tolerance=self.tolerance),
        ]

        errors = sum(1 for c in results if not c.passed and c.severity == "ERROR")
        warnings = sum(1 for c in results if not c.passed and c.severity == "WARNING")
        all_passed = (errors == 0)

        return ValidationSummary(
            document_number=doc.document_number,
            document_type=doc.document_type,
            checks=results,
            passed=all_passed,
            error_count=errors,
            warning_count=warnings,
        )

    def validate_documents(self, docs: List[InvoiceDocument]) -> List[ValidationSummary]:
        """Run reconciliation checks on a batch of documents."""
        return [self.validate_document(doc) for doc in docs]
