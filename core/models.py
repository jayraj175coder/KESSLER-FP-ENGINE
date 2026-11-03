"""
core/models.py — Data classes for KESSLER FP Engine extraction output.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from decimal import Decimal


@dataclass
class LineItem:
    position: int
    article_number: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    price_unit: Decimal
    discount_percent: Optional[Decimal]
    line_total: Decimal
    vat_rate: int

    def to_dict(self) -> dict:
        return {
            "position": int(self.position),
            "article_number": str(self.article_number),
            "description": str(self.description),
            "quantity": float(self.quantity),
            "unit": str(self.unit),
            "unit_price": float(self.unit_price),
            "price_unit": float(self.price_unit),
            "discount_percent": float(self.discount_percent) if self.discount_percent is not None else None,
            "line_total": float(self.line_total),
            "vat_rate": int(self.vat_rate),
        }


@dataclass
class Supplier:
    name: str
    vat_id: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "vat_id": self.vat_id,
        }


@dataclass
class Buyer:
    name: str
    street: str
    postal_code: str
    city: str
    customer_number: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "street": self.street,
            "postal_code": self.postal_code,
            "city": self.city,
            "customer_number": self.customer_number,
        }


@dataclass
class CashDiscount:
    percent: Decimal
    until: str  # YYYY-MM-DD
    amount: Decimal

    def to_dict(self) -> dict:
        return {
            "percent": float(self.percent),
            "until": str(self.until),
            "amount": float(self.amount),
        }


@dataclass
class Totals:
    net_by_vat_rate: Dict[str, Decimal]   # {"19": Decimal, "7": Decimal}
    vat_by_vat_rate: Dict[str, Decimal]
    net_total: Decimal
    vat_total: Decimal
    gross_total: Decimal

    def to_dict(self) -> dict:
        return {
            "net_by_vat_rate": {str(k): float(v) for k, v in self.net_by_vat_rate.items()},
            "vat_by_vat_rate": {str(k): float(v) for k, v in self.vat_by_vat_rate.items()},
            "net_total": float(self.net_total),
            "vat_total": float(self.vat_total),
            "gross_total": float(self.gross_total),
        }


@dataclass
class InvoiceDocument:
    document_type: str          # "invoice" or "credit_note"
    document_number: str
    document_date: str          # YYYY-MM-DD
    service_date: Optional[str]
    due_date: Optional[str]
    currency: str
    supplier: Supplier
    buyer: Buyer
    order_reference: Optional[str]
    delivery_note_number: Optional[str]
    referenced_invoice: Optional[str]
    line_items: List[LineItem]
    totals: Totals
    cash_discount: Optional[CashDiscount]

    def to_dict(self) -> dict:
        return {
            "document_type": self.document_type,
            "document_number": self.document_number,
            "document_date": self.document_date,
            "service_date": self.service_date,
            "due_date": self.due_date,
            "currency": self.currency,
            "supplier": self.supplier.to_dict(),
            "buyer": self.buyer.to_dict(),
            "order_reference": self.order_reference,
            "delivery_note_number": self.delivery_note_number,
            "referenced_invoice": self.referenced_invoice,
            "line_items": [item.to_dict() for item in self.line_items],
            "totals": self.totals.to_dict(),
            "cash_discount": self.cash_discount.to_dict() if self.cash_discount is not None else None,
        }
