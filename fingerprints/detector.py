"""
fingerprints/detector.py — Layout fingerprint detector.

Identifies which KESSLER invoice layout a PDF uses:
  - "kessler_v1": Layout V1 (Rechnungs-Nr., columns Pos./Art.-Nr./...)
  - "kessler_v2": Layout V2 (Rechnung Nr., columns Pos/Menge Einh./Artikel/...)
  - "scanned": Image-only / scanned PDF without extractable text
  - "unknown": Cannot be determined
"""
from core.pdf_reader import get_page_text


def detect_layout(pdf_path: str) -> str:
    """
    Detect layout fingerprint from the first page of the PDF.
    Returns: "kessler_v1", "kessler_v2", "scanned", or "unknown"
    """
    try:
        text = get_page_text(pdf_path, 0)
    except Exception:
        return "unknown"

    if not text or not text.strip():
        return "scanned"

    # V2 signature: "Rechnung Nr." (without hyphen) and "Beschreibung" column header
    if "Rechnung Nr." in text or "Rechnung\nNr." in text or "Kundennummer" in text:
        return "kessler_v2"

    # V1 signature: "Rechnungs-Nr." or "Gutschrift-Nr." or "GUTSCHRIFT"
    if "Rechnungs-Nr." in text or "Gutschrift-Nr." in text or "GUTSCHRIFT" in text:
        return "kessler_v1"

    return "unknown"
