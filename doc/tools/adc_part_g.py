"""Hardware manual, part G: back cover."""
import m4lib
from adc_common import *

# ================================================================================================
# back cover
# ================================================================================================
m4lib.end_steps()
pg = new_page('back cover')
pg.bg = FOREST
pg.cur = None
pg.ox = pg.oy = 0
pg.text(20, 40, 'WHERE THINGS LIVE', 3.0, SAP, 'start', mono=True, ls=0.9)
pg.text(20, 62, 'Files, models and datasheets', min(12.0, 12.0 * 135 / text_w('Files, models and datasheets', 12.0, 'disp')), BONE, 'start', disp=True)
lines = [('hw/', 'KiCad project, schematic, both boards'),
         ('hw/fab/', 'Gerbers, BOM and CPL for JLCPCB, both boards'),
         ('hw/tools/', 'Generators, DRC, cost model, 1:1 print'),
         ('sim/', 'Chain simulation, vendor models list, LTspice netlist'),
         ('doc/tools/', 'This manual, built from the files above'),
         ('doc/data/', 'Board and simulation snapshots used in the figures')]
for i, (a_, b_) in enumerate(lines):
    pg.text(20, 84 + i * 9, a_, 3.4, AMBER, 'start', mono=True)
    pg.text(60, 84 + i * 9, b_, 3.4, '#D8E4D2', 'start')
pg.text(20, 150, 'DATASHEETS', 2.8, SAP, 'start', mono=True, ls=0.8)
pg.text(20, 158, 'ADS7057, THS4531, OPA365 (OPA2365), LM393, XC6206, AMS1117', 3.4, '#D8E4D2', 'start')
pg.text(20, 170, 'Rebuild: M4_PDF_PYTHON=<python with pymupdf> python3 doc/tools/make_adc_manual.py', 2.7, SAP, 'start', mono=True)
pg.text(20, PH - 12, 'AUSELIA  /  ' + m4lib.DOC_NAME, 2.5, '#7E9C86', 'start', mono=True, ls=0.5)
pg.text(PW - 20, PH - 12, f'{len(pages):02d}', 2.5, '#7E9C86', 'end', mono=True)
draw_mark(pg, 172, 44, 84, BONE, BONE, AMBER, AMBER, rings=True)
