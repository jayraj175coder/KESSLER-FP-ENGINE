"""
fingerprints/kessler_v1.py — Column boundary constants for Layout V1.

Measured from actual PyMuPDF word x0 coordinates on INV-01, 02, 03, 04:
  Pos:        ~51      (x0 < 80)
  Art.-Nr.:   ~85      (80 <= x0 < 150)
  Bezeichnung:~158     (150 <= x0 < 330)
  Menge:      ~337-362 (330 <= x0 < 370)
  ME:         ~371     (370 <= x0 < 400)
  Einzel+PE:  ~427-470 (400 <= x0 < 475)
  Rab.%:      ~495-505 (475 <= x0 < 512)
  Gesamt:     ~516-552 (512 <= x0 < 575)
  USt%:       ~577     (x0 >= 575)
"""

# Column x-boundary thresholds (x0 of word)
COL_POS_MAX = 80          # Pos column: x0 < 80
COL_ART_MIN = 80          # Art.-Nr.: 80 <= x0 < 150
COL_ART_MAX = 150
COL_BEZ_MIN = 150         # Bezeichnung: 150 <= x0 < 330
COL_BEZ_MAX = 330
COL_MENGE_MIN = 330       # Menge: 330 <= x0 < 370
COL_MENGE_MAX = 370
COL_ME_MIN = 370          # ME: 370 <= x0 < 400
COL_ME_MAX = 400
COL_PREIS_MIN = 400       # Einzelpreis+PE: 400 <= x0 < 475
COL_PREIS_MAX = 475
COL_RAB_MIN = 475         # Rab.%: 475 <= x0 < 512
COL_RAB_MAX = 512
COL_GESAMT_MIN = 512      # Gesamt: 512 <= x0 < 575
COL_GESAMT_MAX = 575
COL_UST_MIN = 575         # USt%: x0 >= 575

# Y tolerance for grouping words into lines
LINE_Y_TOLERANCE = 3.0

# Artikel number regex pattern
ART_NR_PATTERN = r'^[A-Z]{2,3}-\d{5}$'
