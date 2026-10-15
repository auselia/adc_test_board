"""Adds an invisible, selectable text layer to the page PDFs of the manual (needs pymupdf).
usage: m4_textlayer.py OUTDIR NPAGES   (reads OUTDIR/runs.json written by make_manual_v4.py)"""
import sys, os, json
import pymupdf as fitz

out, n = sys.argv[1], int(sys.argv[2])
runs = json.load(open(os.path.join(out, 'runs.json')))
FONT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts', 'Inter-Regular.ttf'))
font = fitz.Font(fontfile=FONT)
K = 72.0 / 25.4
for i in range(n):
    path = os.path.join(out, f'page_{i+1:02d}.pdf')
    doc = fitz.open(path)
    page = doc[0]
    page.insert_font(fontname='inter', fontfile=FONT)
    for x, y, size, w, s in runs[i]:
        fs = size * K * 1.0
        if fs < 1:
            continue
        tl = font.text_length(s, fontsize=fs)
        sx = (w * K) / tl if tl > 0 and w > 0 else 1.0
        p = fitz.Point(x * K, y * K)
        page.insert_text(p, s, fontsize=fs, fontname='inter', render_mode=3, morph=(p, fitz.Matrix(sx, 1)))
    tmp = path + '.tmp'
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    os.replace(tmp, path)
print('text layer added to', n, 'pages')
