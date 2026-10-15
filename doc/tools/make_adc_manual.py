#!/usr/bin/env python3
"""ADS7057 test board hardware manual. Same layout and library as the other Auselia manuals (m4lib.py).

Data snapshots: doc/data/board.json (export_board.py, KiCad python) and doc/data/sim.json (export_sim.py, ngspice).
Run:  M4_PDF_PYTHON=<python with pymupdf> python3 doc/tools/make_adc_manual.py [part_a part_b ...]
"""
import os, sys, subprocess, importlib, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m4lib

m4lib.DOC_NAME = 'ADS7057 TEST BOARD  /  HARDWARE MANUAL  /  VERSION 0.1'
m4lib.OUT = os.path.abspath(os.path.join(m4lib.HERE, '..', 'manual_build'))
m4lib.TEXDIR = os.path.join(m4lib.OUT, 'tex')
os.makedirs(m4lib.TEXDIR, exist_ok=True)

PARTS = sys.argv[1:] or ['adc_part_a', 'adc_part_b', 'adc_part_c', 'adc_part_d', 'adc_part_e']
for p in PARTS:
    importlib.import_module(p)
from m4lib import pages, WARN, ste_report, steps_done, HERE


def build(final_name='ADS7057_test_board_hardware_manual_letter_v0.1.pdf'):
    out = m4lib.OUT
    files, runs = [], []
    for k, (pg, title) in enumerate(pages):
        svg = os.path.join(out, f'page_{k+1:02d}.svg')
        open(svg, 'w').write(pg.svg())
        pdf = svg.replace('.svg', '.pdf')
        subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', pdf, svg], check=True)
        files.append(pdf)
        runs.append([list(r) for r in pg.runs])
    json.dump(runs, open(os.path.join(out, 'runs.json'), 'w'))
    json.dump([k for k, (pg, _) in enumerate(pages) if pg.bg], open(os.path.join(out, 'dark.json'), 'w'))
    py = os.environ.get('M4_PDF_PYTHON')
    if py and os.path.exists(py):
        subprocess.run([py, os.path.join(HERE, 'm4_textlayer.py'), out, str(len(files))], check=True)
    else:
        print('NOTE: text layer and print versions skipped (set M4_PDF_PYTHON to a python with pymupdf)')
    final = os.path.abspath(os.path.join(HERE, '..', final_name))
    subprocess.run(['pdfunite'] + files + [final], check=True)
    print('pages:', len(files), 'steps:', steps_done(), '->', final)
    if py and os.path.exists(py):
        subprocess.run([py, os.path.join(HERE, 'm4_print.py'), final, '14', os.path.join(out, 'dark.json')], check=True)
    for w in WARN:
        print('WARN', w)
    for l in ste_report():
        print(l)


if __name__ == '__main__':
    m4lib.end_steps()
    build()
