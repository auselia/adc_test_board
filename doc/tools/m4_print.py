"""Print versions of the manual with a binding gutter (needs pymupdf).
usage: m4_print.py IN.pdf GUTTER_MM
  writes IN_print.pdf         gutter on the left of every page (single-sided printing)
  and    IN_print_duplex.pdf  gutter on the left of odd pages and on the right of even pages (double-sided)
Each page is scaled down uniformly to free the gutter and centered vertically; the text stays selectable."""
import sys
import pymupdf as fitz

import json
src, gut = sys.argv[1], float(sys.argv[2])
dark = set(json.load(open(sys.argv[3]))) if len(sys.argv) > 3 else set()
G = gut * 72.0 / 25.4
doc = fitz.open(src)
for duplex in (False, True):
    out = fitz.open()
    for i, p in enumerate(doc):
        W, H = p.rect.width, p.rect.height
        s = (W - G) / W
        h = H * s
        left = not duplex or i % 2 == 0
        x0 = G if left else 0
        y0 = (H - h) / 2
        np_ = out.new_page(width=W, height=H)
        if i in dark or (not dark and i in (0, len(doc) - 1)):   # dark pages: fill the whole sheet, so the gutter is green too
            np_.draw_rect(np_.rect, color=None, fill=(0x14 / 255, 0x26 / 255, 0x1C / 255))
        np_.show_pdf_page(fitz.Rect(x0, y0, x0 + W - G, y0 + h), doc, i)
    name = src.replace('.pdf', '_print_duplex.pdf' if duplex else '_print.pdf')
    out.save(name, garbage=3, deflate=True)
    print('wrote', name)
