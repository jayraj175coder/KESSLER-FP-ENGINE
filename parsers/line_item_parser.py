"""
parsers/line_item_parser.py — Word-coordinate-based line item parsing.

Supports both V1 and V2 layouts.
"""
import re
from decimal import Decimal
from typing import List, Dict, Optional, Tuple

from core.models import LineItem
from core.number_parser import parse_german_number
from fingerprints import kessler_v1 as v1
from fingerprints import kessler_v2 as v2


# ─── Shared helpers ────────────────────────────────────────────────────────────

def group_words_by_y(words: list, y_tolerance: float = 3.0) -> List[List]:
    """
    Group word tuples by their y0 coordinate within tolerance.
    Returns list of lines, each line being a list of word tuples,
    sorted by x0 within the line, and lines sorted by y0.
    """
    if not words:
        return []
    lines: Dict[float, List] = {}
    for w in words:
        x0, y0, x1, y1, text, bn, ln, wn = w
        # Find matching y bucket
        matched = None
        for key in lines:
            if abs(key - y0) <= y_tolerance:
                matched = key
                break
        if matched is None:
            matched = y0
            lines[matched] = []
        lines[matched].append(w)
    # Sort each line by x0, then sort lines by y
    result = []
    for key in sorted(lines.keys()):
        line = sorted(lines[key], key=lambda w: w[0])
        result.append(line)
    return result


# ─── V1 line item parsing ───────────────────────────────────────────────────────

ART_NR_RE = re.compile(r'^[A-Z]{2,3}-\d{5}$')
POS_RE = re.compile(r'^\d{1,3}$')
NUMERIC_RE = re.compile(r'^-?[\d.,]+-?$')


def _is_numeric(s: str) -> bool:
    """Check if string looks like a German number."""
    return bool(NUMERIC_RE.match(s.replace(' ', '')))


def _bucket_v1(words_in_line: list) -> Dict[str, List[str]]:
    """
    Bucket words from a V1 line into named columns.
    Returns dict: {col_name: [word, ...]}
    """
    buckets: Dict[str, List[str]] = {
        'pos': [], 'art': [], 'bez': [], 'menge': [],
        'me': [], 'preis': [], 'rab': [], 'gesamt': [], 'ust': []
    }
    for w in words_in_line:
        x0 = w[0]
        text = w[4]
        if x0 < v1.COL_POS_MAX:
            buckets['pos'].append(text)
        elif x0 < v1.COL_ART_MAX:
            buckets['art'].append(text)
        elif x0 < v1.COL_BEZ_MAX:
            buckets['bez'].append(text)
        elif x0 < v1.COL_MENGE_MAX:
            buckets['menge'].append(text)
        elif x0 < v1.COL_ME_MAX:
            buckets['me'].append(text)
        elif x0 < v1.COL_PREIS_MAX:
            buckets['preis'].append(text)
        elif x0 < v1.COL_RAB_MAX:
            buckets['rab'].append(text)
        elif x0 < v1.COL_GESAMT_MAX:
            buckets['gesamt'].append(text)
        else:
            buckets['ust'].append(text)
    return buckets


def _is_product_line_v1(buckets: Dict[str, List[str]]) -> bool:
    """True if this line looks like a product data row in V1."""
    has_pos = buckets['pos'] and POS_RE.match(buckets['pos'][0])
    has_art = buckets['art'] and ART_NR_RE.match(buckets['art'][0])
    return bool(has_pos and has_art)


def _is_desc_only_line_v1(buckets: Dict[str, List[str]]) -> bool:
    """True if this line is an extra description row (no pos/art/amounts)."""
    no_pos = not buckets['pos']
    no_art = not buckets['art']
    no_amounts = not buckets['gesamt'] and not buckets['ust']
    has_text = bool(buckets['bez'] or buckets['menge'] or buckets['me'] or buckets['preis'] or buckets['rab'])
    return no_pos and no_art and no_amounts and has_text


def _is_skip_line_v1(buckets: Dict[str, List[str]], raw_text: str) -> bool:
    """True if this line should be skipped (header, carry-forward, etc.)."""
    combined = ' '.join(
        buckets['pos'] + buckets['art'] + buckets['bez'] +
        buckets['menge'] + buckets['me'] + buckets['preis'] +
        buckets['rab'] + buckets['gesamt'] + buckets['ust']
    )
    # Detect table header row by multi-column signature (never match single "Pos." in descriptions)
    if 'Art.-Nr.' in combined and ('Bezeichnung' in combined or 'Einzelpreis' in combined or 'Pos.' in combined):
        return True
    if ('Pos.' in buckets['pos'] or 'Pos' in buckets['pos']) and ('Art.-Nr.' in buckets['art'] or 'Artikel' in buckets['art']):
        return True

    skip_keywords = ['Übertrag', 'Nettobetrag', 'zzgl.', 'Rechnungsbetrag',
                     'Gutschriftsbetrag', 'Zahlbar', 'Bei Zahlung',
                     'Sehr geehrte', 'wir berechnen', 'wir schreiben',
                     'Allgemeinen', 'USt-IdNr', 'Volksbank', 'IBAN',
                     'Steuer-Nr', 'Seite', 'Kessler', 'KESSLER',
                     'Tel.', 'buchhaltung']
    for kw in skip_keywords:
        if kw in combined:
            return True
    return False


def parse_v1_line_items(all_page_words: List[List]) -> List[LineItem]:
    """
    Parse V1 line items from all pages' word lists.
    Handles multi-page invoices and extra description lines.
    """
    items: List[LineItem] = []
    current_item: Optional[Dict] = None

    for page_words in all_page_words:
        lines = group_words_by_y(page_words, v1.LINE_Y_TOLERANCE)
        for line in lines:
            buckets = _bucket_v1(line)
            raw_text = ' '.join(w[4] for w in line)

            if _is_skip_line_v1(buckets, raw_text):
                continue

            if _is_product_line_v1(buckets):
                # Save previous item
                if current_item:
                    items.append(_build_line_item_v1(current_item))

                pos_str = buckets['pos'][0]
                art_nr = buckets['art'][0]
                description = ' '.join(buckets['bez'])
                menge_tokens = buckets['menge']
                me_tokens = buckets['me']
                preis_tokens = buckets['preis']
                rab_tokens = buckets['rab']
                gesamt_tokens = buckets['gesamt']
                ust_tokens = buckets['ust']

                current_item = {
                    'position': int(pos_str),
                    'article_number': art_nr,
                    'description_parts': [description],
                    'menge_tokens': menge_tokens,
                    'me_tokens': me_tokens,
                    'preis_tokens': preis_tokens,
                    'rab_tokens': rab_tokens,
                    'gesamt_tokens': gesamt_tokens,
                    'ust_tokens': ust_tokens,
                }

            elif _is_desc_only_line_v1(buckets) and current_item is not None:
                # Append extra description text across description columns
                extra = ' '.join(buckets['bez'] + buckets['menge'] + buckets['me'] + buckets['preis'] + buckets['rab']).strip()
                if extra:
                    current_item['description_parts'].append(extra)

    # Don't forget the last item
    if current_item:
        items.append(_build_line_item_v1(current_item))

    return items


def _build_line_item_v1(d: Dict) -> LineItem:
    """Construct a LineItem from parsed token dict (V1)."""
    position = d['position']
    article_number = d['article_number']
    description = ' '.join(d['description_parts'])

    # Parse quantity
    menge_raw = ' '.join(d['menge_tokens'])
    quantity = parse_german_number(menge_raw) if menge_raw else Decimal('1')

    # Parse unit
    unit = d['me_tokens'][0] if d['me_tokens'] else ''

    # Parse unit_price and price_unit from preis_tokens
    # preis_tokens may be: ["8,45", "1"] or ["14,60", "100"] or ["38,15", "1"]
    preis_tokens = d['preis_tokens']
    if not preis_tokens:
        unit_price = Decimal('0')
        price_unit = Decimal('1')
    elif len(preis_tokens) >= 2:
        # Second token is PE if it's a plain integer (1, 10, 100)
        unit_price = parse_german_number(preis_tokens[0])
        try:
            pe_val = parse_german_number(preis_tokens[1])
            # PE is typically 1, 10, 100 — a round power of 10
            price_unit = pe_val
        except Exception:
            price_unit = Decimal('1')
    else:
        unit_price = parse_german_number(preis_tokens[0])
        price_unit = Decimal('1')

    # Parse discount and line total
    rab_tokens = list(d['rab_tokens'])
    gesamt_tokens = list(d['gesamt_tokens'])

    # If gesamt is empty but rab has a token, it is the line total
    # (can happen if a large total spans slightly left of the boundary)
    if not gesamt_tokens and rab_tokens:
        gesamt_tokens = [rab_tokens.pop()]

    if rab_tokens:
        try:
            discount_percent = parse_german_number(rab_tokens[0])
        except Exception:
            discount_percent = None
    else:
        discount_percent = None

    if gesamt_tokens:
        line_total = parse_german_number(gesamt_tokens[0])
    else:
        line_total = Decimal('0')

    # Parse VAT rate
    ust_tokens = d['ust_tokens']
    if ust_tokens:
        try:
            vat_rate = int(ust_tokens[0])
        except (ValueError, IndexError):
            vat_rate = 19
    else:
        vat_rate = 19

    return LineItem(
        position=position,
        article_number=article_number,
        description=description,
        quantity=quantity,
        unit=unit,
        unit_price=unit_price,
        price_unit=price_unit,
        discount_percent=discount_percent,
        line_total=line_total,
        vat_rate=vat_rate,
    )


# ─── V2 line item parsing ───────────────────────────────────────────────────────

def _bucket_v2(words_in_line: list) -> Dict[str, List[str]]:
    """Bucket words from a V2 line into named columns."""
    buckets: Dict[str, List[str]] = {
        'pos': [], 'menge': [], 'einh': [], 'art': [],
        'bez': [], 'preis': [], 'mwst': [], 'betrag': []
    }
    for w in words_in_line:
        x0 = w[0]
        text = w[4]
        if x0 < v2.COL_POS_MAX:
            buckets['pos'].append(text)
        elif x0 < v2.COL_MENGE_MAX:
            buckets['menge'].append(text)
        elif x0 < v2.COL_EINH_MAX:
            buckets['einh'].append(text)
        elif x0 < v2.COL_ART_MAX:
            buckets['art'].append(text)
        elif x0 < v2.COL_BEZ_MAX:
            buckets['bez'].append(text)
        elif x0 < v2.COL_PREIS_MAX:
            buckets['preis'].append(text)
        elif x0 < v2.COL_MWST_MAX:
            buckets['mwst'].append(text)
        else:
            buckets['betrag'].append(text)
    return buckets


POS_V2_RE = re.compile(r'^\d{3}$')  # 001, 002, etc.


def _is_product_line_v2(buckets: Dict[str, List[str]]) -> bool:
    pos_ok = buckets['pos'] and POS_V2_RE.match(buckets['pos'][0])
    art_ok = buckets['art'] and ART_NR_RE.match(buckets['art'][0])
    return bool(pos_ok and art_ok)


def _is_discount_line_v2(buckets: Dict[str, List[str]]) -> bool:
    """True if this is a discount sub-row (abzgl. ...)."""
    return 'abzgl.' in buckets['bez'] or any('abzgl.' in t for t in buckets['bez'])


def _is_desc_line_v2(buckets: Dict[str, List[str]]) -> bool:
    """True if this is an extra description sub-row (no pos/art/amounts)."""
    no_pos = not buckets['pos']
    no_art = not buckets['art']
    no_betrag = not buckets['betrag']
    has_text = bool(buckets['bez'] or buckets['preis'] or buckets['mwst'])
    return no_pos and no_art and no_betrag and has_text


def _is_skip_line_v2(buckets: Dict[str, List[str]]) -> bool:
    combined = ' '.join(
        buckets['pos'] + buckets['menge'] + buckets['einh'] +
        buckets['art'] + buckets['bez'] + buckets['preis'] +
        buckets['mwst'] + buckets['betrag']
    )
    # Detect table header row by multi-column signature
    if 'Menge' in combined and ('Beschreibung' in combined or 'Preis/Einh.' in combined or 'Artikel' in combined):
        return True
    if 'Pos' in buckets['pos'] and ('Artikel' in buckets['art'] or 'Menge' in buckets['menge']):
        return True

    skip_keywords = ['Summe netto', 'MwSt 19%', 'MwSt 7%', 'Gesamtbetrag',
                     'Zahlungsziel', 'Hinweis', 'Rechnung\n', 'Übertrag', 'Zwischensumme',
                     'USt-IdNr', 'Volksbank', 'IBAN', 'Steuer-Nr',
                     'Seite', 'Kessler', 'KESSLER', 'Tel.', 'buchhaltung']
    for kw in skip_keywords:
        if kw in combined:
            return True
    # Skip if only betrag column has data (summary rows)
    if (not buckets['pos'] and not buckets['art'] and not buckets['menge']
            and not buckets['preis'] and buckets['betrag'] and not buckets['bez']):
        return True
    return False


def _strip_euro(s: str) -> str:
    """Remove € character and whitespace."""
    return s.replace('€', '').replace('\u20ac', '').strip()


def _strip_percent(s: str) -> str:
    """Remove % character."""
    return s.replace('%', '').strip()


def parse_v2_line_items(all_page_words: List) -> List[LineItem]:
    """
    Parse V2 line items from word lists.
    Accepts either a single page's words or a list of pages' words.
    """
    if not all_page_words:
        return []

    # If it's a list of pages (where elements are lists of tuples)
    if isinstance(all_page_words[0], list) and (len(all_page_words[0]) == 0 or isinstance(all_page_words[0][0], (tuple, list))):
        pages = all_page_words
    else:
        pages = [all_page_words]

    items: List[LineItem] = []
    current_item: Optional[Dict] = None

    for page_words in pages:
        lines = group_words_by_y(page_words, v2.LINE_Y_TOLERANCE)

        for line in lines:
            buckets = _bucket_v2(line)

            if _is_skip_line_v2(buckets):
                # Check if it's actually a summary line — if so, also finalize item
                summary_kw = ['Summe netto', 'Gesamtbetrag']
                combined = ' '.join(w[4] for w in line)
                if any(kw in combined for kw in summary_kw):
                    if current_item:
                        items.append(_build_line_item_v2(current_item))
                        current_item = None
                continue

            if _is_product_line_v2(buckets):
                # Save previous item (with any pending discount)
                if current_item:
                    items.append(_build_line_item_v2(current_item))

                pos_str = buckets['pos'][0].lstrip('0') or '0'
                menge_raw = ' '.join(buckets['menge'])
                einh_raw = ' '.join(buckets['einh'])
                art_nr = buckets['art'][0] if buckets['art'] else ''
                description = ' '.join(buckets['bez'])
                preis_tokens = buckets['preis']
                mwst_tokens = buckets['mwst']
                betrag_tokens = buckets['betrag']

                # Parse price (strip € symbol)
                preis_str = _strip_euro(' '.join(preis_tokens))
                betrag_str = _strip_euro(' '.join(betrag_tokens))
                mwst_str = _strip_percent(' '.join(mwst_tokens))

                current_item = {
                    'position': int(pos_str) if pos_str.isdigit() else 0,
                    'article_number': art_nr,
                    'description_parts': [description],
                    'menge_raw': menge_raw,
                    'einh_raw': einh_raw,
                    'preis_str': preis_str,
                    'betrag_str': betrag_str,
                    'mwst_str': mwst_str,
                    'discount_amount': None,
                    'discount_percent_str': None,
                }

            elif _is_discount_line_v2(buckets) and current_item is not None:
                # Parse discount row: "abzgl. Sonderrabatt 3 % auf 465,60 €" → amount in betrag
                betrag_tokens = buckets['betrag']
                betrag_str = _strip_euro(' '.join(betrag_tokens))
                bez_words = buckets['bez']

                # Extract percent from bez: look for pattern "N %" or "N%"
                pct = None
                for i, bw in enumerate(bez_words):
                    if bw.endswith('%'):
                        try:
                            pct = Decimal(bw.rstrip('%'))
                        except Exception:
                            pass
                    elif i + 1 < len(bez_words) and bez_words[i + 1] == '%':
                        try:
                            pct = Decimal(bw)
                        except Exception:
                            pass

                if betrag_str:
                    try:
                        disc_amount = parse_german_number(betrag_str)
                        current_item['discount_amount'] = disc_amount  # negative value
                        current_item['discount_percent_str'] = str(pct) if pct else None
                    except Exception:
                        pass

            elif _is_desc_line_v2(buckets) and current_item is not None:
                extra = ' '.join(buckets['bez'] + buckets['preis'] + buckets['mwst']).strip()
                if extra:
                    current_item['description_parts'].append(extra)

    # Don't forget last item
    if current_item:
        items.append(_build_line_item_v2(current_item))

    return items


def _build_line_item_v2(d: Dict) -> LineItem:
    """Construct a LineItem from parsed dict (V2)."""
    position = d['position']
    article_number = d['article_number']
    description = ' '.join(d['description_parts'])

    # Parse quantity
    menge_raw = d.get('menge_raw', '1')
    try:
        quantity = parse_german_number(menge_raw)
    except Exception:
        quantity = Decimal('1')

    unit = d.get('einh_raw', '').strip()

    # Parse unit price
    try:
        unit_price = parse_german_number(d['preis_str'])
    except Exception:
        unit_price = Decimal('0')

    price_unit = Decimal('1')  # V2 always PE=1

    # Parse betrag (line total before discount)
    try:
        betrag = parse_german_number(d['betrag_str'])
    except Exception:
        betrag = Decimal('0')

    # Apply discount if any
    discount_amount = d.get('discount_amount')
    discount_percent = None

    if discount_amount is not None:
        # discount_amount is negative (e.g., -13.97)
        line_total = betrag + discount_amount  # betrag - abs(discount)
        pct_str = d.get('discount_percent_str')
        if pct_str:
            try:
                discount_percent = Decimal(pct_str)
            except Exception:
                discount_percent = None
    else:
        line_total = betrag

    # Parse VAT
    mwst_str = d.get('mwst_str', '19')
    try:
        vat_rate = int(mwst_str.replace('%', '').strip())
    except Exception:
        vat_rate = 19

    return LineItem(
        position=position,
        article_number=article_number,
        description=description,
        quantity=quantity,
        unit=unit,
        unit_price=unit_price,
        price_unit=price_unit,
        discount_percent=discount_percent,
        line_total=line_total,
        vat_rate=vat_rate,
    )
