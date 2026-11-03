"""
fingerprints/kessler_v2.py — Column boundary constants for Layout V2.

Measured from actual PyMuPDF word x0 coordinates on INV-05:
  Pos:           ~51      (x0 < 80)
  Menge:         ~87-97   (80 <= x0 < 107)
  Einh.:         ~107     (107 <= x0 < 140)
  Artikel:       ~141     (140 <= x0 < 205)
  Beschreibung:  ~209     (205 <= x0 < 420)
  Preis/Einh.:   ~434-444 (420 <= x0 < 470)
  MwSt:          ~481     (470 <= x0 < 530)
  Betrag:        ~533     (x0 >= 530)
"""

# Column x-boundary thresholds (x0 of word)
COL_POS_MAX = 80           # Pos: x0 < 80
COL_MENGE_MIN = 80         # Menge: 80 <= x0 < 107
COL_MENGE_MAX = 107
COL_EINH_MIN = 107         # Einheit: 107 <= x0 < 140
COL_EINH_MAX = 140
COL_ART_MIN = 140          # Artikel: 140 <= x0 < 205
COL_ART_MAX = 205
COL_BEZ_MIN = 205          # Beschreibung: 205 <= x0 < 420
COL_BEZ_MAX = 420
COL_PREIS_MIN = 420        # Preis/Einh.: 420 <= x0 < 470
COL_PREIS_MAX = 470
COL_MWST_MIN = 470         # MwSt: 470 <= x0 < 530
COL_MWST_MAX = 530
COL_BETRAG_MIN = 530       # Betrag: x0 >= 530

# Y tolerance for grouping words into lines
LINE_Y_TOLERANCE = 3.0
