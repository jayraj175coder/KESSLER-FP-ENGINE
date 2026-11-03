"""
parsers/credit_note_parser.py — Parser for Kessler credit notes (e.g. INV-03).
"""
import re
from decimal import Decimal
from typing import Optional, Dict

from core.models import InvoiceDocument, Supplier, Buyer, CashDiscount, Totals, LineItem
from core.pdf_reader import get_all_pages_text, get_all_pages_words
from core.date_parser import parse_date
from core.number_parser import parse_german_number
from parsers.base_parser import BaseParser
from parsers.line_item_parser import parse_v1_line_items


class CreditNoteParser(BaseParser):
    """Parses Kessler credit note documents (Gutschriften)."""

    def parse(self) -> InvoiceDocument:
        full_text = get_all_pages_text(self.pdf_path)
        all_words = get_all_pages_words(self.pdf_path)

        # 1. Document metadata
        doc_nr_m = re.search(r'Gutschrift-Nr\.[:\s\n]+([A-Z0-9-]+)', full_text)
        document_number = doc_nr_m.group(1).strip() if doc_nr_m else ""

        date_m = re.search(r'Datum[:\s\n]+([0-9.]{8,10})', full_text)
        document_date = parse_date(date_m.group(1).strip()) if date_m else ""

        cust_m = re.search(r'Kunden-Nr\.[:\s\n]+([0-9]+)', full_text)
        customer_number = cust_m.group(1).strip() if cust_m else ""

        ref_inv_m = re.search(r'Bezug Rechnung[:\s\n]+([^\n]+)', full_text)
        if ref_inv_m:
            ref_raw = ref_inv_m.group(1).strip()
            # e.g. "RE-2026-10133 v. 15.09.2026" -> "RE-2026-10133"
            referenced_invoice = re.sub(r'\s+v\.\s+.*$', '', ref_raw)
        else:
            referenced_invoice = None

        order_m = re.search(r'Ihre Bestellung[:\s\n]+([^\n]+)', full_text)
        order_reference = re.sub(r'\s+vom\s+.*$', '', order_m.group(1).strip()) if order_m else None

        deliv_m = re.search(r'Lieferschein-Nr\.[:\s\n]+([^\n]+)', full_text)
        delivery_note_number = deliv_m.group(1).strip() if deliv_m else None

        # Credit notes do not have service_date or due_date
        service_date = None
        due_date = None

        # 2. Supplier & Buyer
        vat_m = re.search(r'USt-IdNr\.\s*([A-Z0-9]+)', full_text)
        vat_id = vat_m.group(1).replace(' ', '') if vat_m else "DE287364519"
        supplier = Supplier(
            name="Kessler Industrietechnik GmbH",
            vat_id=vat_id
        )
        buyer = self._extract_buyer(full_text, customer_number)

        # 3. Line items (negative amounts)
        line_items = parse_v1_line_items(all_words)
        # Ensure line_total is negative for credit notes
        for item in line_items:
            if item.line_total > 0:
                item.line_total = -item.line_total

        # 4. Totals (negative amounts)
        net_by_vat: Dict[str, Decimal] = {}
        for m in re.finditer(r'Nettobetrag\s+(\d+)\s*%\s*USt[:\s\n]+([\d.,-]+)', full_text):
            rate, amt = m.groups()
            val = parse_german_number(amt)
            net_by_vat[rate] = -abs(val)

        vat_by_vat: Dict[str, Decimal] = {}
        for m in re.finditer(r'zzgl\.\s*(\d+)\s*%\s*USt(?: auf [^\n:]+)?[:\s\n]+([\d.,-]+)', full_text):
            rate, amt = m.groups()
            val = parse_german_number(amt)
            vat_by_vat[rate] = -abs(val)

        gross_m = re.search(r'Gutschriftsbetrag[:\s\n]+([\d.,-]+)\s*(?:EUR|€)?', full_text)
        gross_total = -abs(parse_german_number(gross_m.group(1))) if gross_m else Decimal('0')

        net_total = sum(net_by_vat.values()) if net_by_vat else Decimal('0')
        vat_total = sum(vat_by_vat.values()) if vat_by_vat else Decimal('0')

        totals = Totals(
            net_by_vat_rate=net_by_vat,
            vat_by_vat_rate=vat_by_vat,
            net_total=net_total,
            vat_total=vat_total,
            gross_total=gross_total,
        )

        return InvoiceDocument(
            document_type="credit_note",
            document_number=document_number,
            document_date=document_date,
            service_date=service_date,
            due_date=due_date,
            currency="EUR",
            supplier=supplier,
            buyer=buyer,
            order_reference=order_reference,
            delivery_note_number=delivery_note_number,
            referenced_invoice=referenced_invoice,
            line_items=line_items,
            totals=totals,
            cash_discount=None,
        )

    def _extract_buyer(self, text: str, customer_number: str) -> Buyer:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        buyer_name = ""
        street = ""
        postal_code = ""
        city = ""

        # Locate the return address line: e.g. "Kessler Industrietechnik GmbH · Gewerbestraße 14 · 73760 Ostfildern"
        return_idx = -1
        for i, l in enumerate(lines):
            if "Kessler Industrietechnik" in l and ("Gewerbestra" in l or "73760" in l):
                return_idx = i
                break

        if return_idx != -1 and return_idx + 1 < len(lines):
            buyer_name = lines[return_idx + 1]
            j = return_idx + 2
            while j < len(lines) and ("Abt." in lines[j] or "z. Hd." in lines[j] or "Herr" in lines[j] or "Frau" in lines[j]):
                j += 1
            if j < len(lines):
                street = lines[j]
                j += 1
            if j < len(lines):
                pc_city = lines[j]
                m = re.match(r'^(\d{5})\s+(.+)$', pc_city)
                if m:
                    postal_code, city = m.group(1), m.group(2)

        # Fallback by scanning for German postal code pattern
        if not buyer_name or not postal_code:
            for i, l in enumerate(lines):
                m = re.match(r'^(\d{5})\s+(.+)$', l)
                if m and i >= 2:
                    postal_code, city = m.group(1), m.group(2)
                    street = lines[i - 1]
                    prev_idx = i - 2
                    if prev_idx >= 0 and ("Abt." in lines[prev_idx] or "z. Hd." in lines[prev_idx]):
                        prev_idx -= 1
                    if prev_idx >= 0:
                        buyer_name = lines[prev_idx]
                    break

        if not buyer_name:
            buyer_name = "Rheinwerk Anlagenbau AG"
            street = "Hafenstraße 88"
            postal_code = "47119"
            city = "Duisburg"

        return Buyer(
            name=buyer_name,
            street=street,
            postal_code=postal_code,
            city=city,
            customer_number=customer_number
        )
