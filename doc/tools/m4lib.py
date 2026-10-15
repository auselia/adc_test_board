"""Library of the hardware manual: text metrics (text becomes outlines), page and step classes, LaTeX equations
(tectonic -> pdftocairo -> inline SVG), a mechanical STE check. Every step is one panel of a 2 x 2 grid on a Letter
landscape page: a title and text on top and a figure below.
Generalized from Auselia_AFE_v1/doc/tools/m4lib.py: the FFT example data and model imports are removed.
"""
import os, sys, math, re, hashlib, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HERE, '..', 'manual_build'))
TEXDIR = os.path.join(OUT, 'tex')
os.makedirs(TEXDIR, exist_ok=True)

# ------------------------------------------------------------------------------------------------
# fonts and text metrics (text becomes outlines, so the PDF does not depend on installed fonts)
# ------------------------------------------------------------------------------------------------
FONTDIR = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
_FF = {'sans': 'Inter-Regular.ttf', 'bold': 'Inter-SemiBold.ttf', 'mono': 'IBMPlexMono-Regular.ttf',
       'disp': 'SpaceGrotesk-Bold.ttf'}
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

_TT = {}
WARN = []


def _tt(kind):
    if kind not in _TT:
        f = TTFont(os.path.join(FONTDIR, _FF[kind]))
        _TT[kind] = dict(gs=f.getGlyphSet(), cmap=f.getBestCmap(), upem=f['head'].unitsPerEm, hmtx=f['hmtx'], cache={})
    return _TT[kind]


def _gl(kind, ch):
    """(font table, glyph name) for the character, falls back to Inter"""
    t = _tt(kind)
    if ord(ch) in t['cmap']:
        return t, t['cmap'][ord(ch)]
    t = _tt('sans')
    if ord(ch) in t['cmap']:
        return t, t['cmap'][ord(ch)]
    if ('missing', ch) not in _TT:
        _TT[('missing', ch)] = 1
        WARN.append(f'missing glyph {ch!r}')
    return None, None


def text_w(s, size, kind='sans', ls=0.0):
    s = str(s)
    total = 0.0
    for ch in s:
        t, name = _gl(kind, ch)
        total += (t['hmtx'][name][0] / t['upem'] * size) if t else 0.5 * size
    return total + ls * max(len(s) - 1, 0)


def text_path(s, size, kind, ls=0.0):
    parts = []
    x = 0.0
    for ch in s:
        t, name = _gl(kind, ch)
        if t is None:
            x += 0.5 * size
            continue
        sc = size / t['upem']
        if name not in t['cache']:
            pen = SVGPathPen(t['gs'])
            t['gs'][name].draw(pen)
            t['cache'][name] = (pen.getCommands(), t['hmtx'][name][0])
        d, adv = t['cache'][name]
        if d:
            parts.append(f'<path d="{d}" transform="translate({x:.3f},0) scale({sc:.5f},{-sc:.5f})"/>')
        x += adv * sc + ls
    return ''.join(parts)


# ------------------------------------------------------------------------------------------------
# colors, page geometry
# ------------------------------------------------------------------------------------------------
PUR, GRN, PNK, LPK, BLU, LBL, GRY = '#910569', '#168638', '#d89cc8', '#efd3e6', '#1167b1', '#5a96c8', '#cccccc'
FOREST, CANOPY, AMBER, SAGE, SAP, BONE, BONE2, INK = '#14261C', '#1B3A2B', '#E8A13A', '#5C7A63', '#A9C7A0', '#F4F1EA', '#EDE8DC', '#1A1A1A'
CRIT = '#C0491F'
LGR, AMB, AMBT, RED, CRM, BG = BONE2, AMBER, '#F7DDA8', CRIT, '#FFF6DE', '#FFFFFF'
MUTED = '#3d4a43'

PW, PH = 279.4, 215.9
PAN_W, PAN_H = 141.0, 96.5
MARGIN_X, TOP, BOTTOM, GAP = 9.0, 16.0, 15.0, 5.0
SCALE = ((PW - 2 * MARGIN_X - GAP) / 2) / PAN_W
CELL_H = (PH - TOP - BOTTOM - GAP) / 2
ORIGINS = []
for _r in range(2):
    for _c in range(2):
        ORIGINS.append((MARGIN_X + _c * (PAN_W * SCALE + GAP), TOP + _r * (CELL_H + GAP)))
PIC = (3.0, 38.0, PAN_W - 3.0, 84.0)               # default figure area, set per step
MINF = 2.5                                          # smallest text in a figure (panel units)
KMAX = 1.5                                          # largest enlargement of a figure
BODY = 3.05                                         # body text size
BODY_DY = 4.1


def fmt(v):
    return f'{v:,}'.replace(',', ' ')


def sgn(v):
    return f'{v}' if v >= 0 else f'−{abs(v)}'.replace('-', '−')


# ------------------------------------------------------------------------------------------------
# LaTeX equations
# ------------------------------------------------------------------------------------------------
_TEX_N = [0]


def tex_asset(src, color='1A1A1A'):
    key = hashlib.md5((src + color).encode()).hexdigest()[:12]
    base = os.path.join(TEXDIR, key)
    if not os.path.exists(base + '.svg'):
        doc = ('\\documentclass[border=0.6pt]{standalone}\n\\usepackage{amsmath,amssymb,xcolor}\n\\begin{document}\n'
               f'\\color[HTML]{{{color}}}$\\displaystyle {src}$\n\\end{{document}}\n')
        open(base + '.tex', 'w').write(doc)
        r = subprocess.run(['tectonic', '-X', 'compile', base + '.tex'] if False else ['tectonic', base + '.tex'],
                           capture_output=True, text=True, cwd=TEXDIR)
        if not os.path.exists(base + '.pdf'):
            raise RuntimeError('LaTeX failed for ' + src + '\n' + r.stderr[-800:])
        subprocess.run(['pdftocairo', '-svg', base + '.pdf', base + '.svg'], check=True)
    s = open(base + '.svg').read()
    mm = re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"', s)
    w, h = float(mm.group(1)), float(mm.group(2))
    inner = s[s.index('>', s.index('<svg')) + 1: s.rindex('</svg>')]
    _TEX_N[0] += 1
    pre = f'e{_TEX_N[0]}_'
    for i in set(re.findall(r'id="([^"]+)"', inner)):
        inner = inner.replace(f'id="{i}"', f'id="{pre}{i}"').replace(f'#{i}"', f'#{pre}{i}"').replace(f'#{i})', f'#{pre}{i})')
    return w, h, inner


# ------------------------------------------------------------------------------------------------
# rich text: **bold**, `mono`, plain.  Items of a body: str (paragraph), ('tex', src[, pt]), ('gap', h)
# ------------------------------------------------------------------------------------------------
def parse_rich(s):
    segs = []
    for tok in re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', s):
        if not tok:
            continue
        if tok.startswith('**'):
            segs.append((tok[2:-2], 'bold'))
        elif tok.startswith('`'):
            segs.append((tok[1:-1], 'mono'))
        else:
            segs.append((tok, 'sans'))
    words, cur = [], []
    for text, kind in segs:
        parts = text.split(' ')
        for i, p in enumerate(parts):
            if i > 0 and cur:
                words.append(cur)
                cur = []
            if p:
                cur.append((p, kind))
    if cur:
        words.append(cur)
    return words


def plain(s):
    return re.sub(r'\*\*|`', '', s)


def wrap_rich(s, size, width):
    words = parse_rich(s)
    sp = text_w(' ', size)
    lines, cur, cw = [], [], 0.0
    for w in words:
        ww = sum(text_w(t, size * (0.92 if k == 'mono' else 1.0), k) for t, k in w)
        if cur and cw + sp + ww > width:
            lines.append(cur)
            cur, cw = [], 0.0
        cw += (sp if cur else 0) + ww
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


STE_TEXT = []        # (step, text) of every paragraph, for the mechanical STE check


class Page:
    def __init__(self, name=''):
        self.o = []
        self.ox = self.oy = 0
        self.slot = 0
        self.cur = None
        self.name = name
        self.step_no = None
        self.bg = None
        self.runs = []          # (x_mm, y_mm baseline, size_mm, width_mm, string) for the text layer

    def _emit(self, svg, bbox, text=None):
        if self.cur is None:
            self.o.append(svg)
            return
        tgt = self.cur[self.cur['target']]
        tgt.append(svg)
        if self.cur['target'] == 'pic' and bbox:
            self.cur['bbox'].append(bbox)
            if text is not None:
                self.cur['texts'].append((bbox, text))

    def rect(self, x, y, w, h, fill='none', stroke='none', sw=0.3, rx=0, dash=None, opacity=None):
        d = f';stroke-dasharray:{dash}' if dash else ''
        op = f';fill-opacity:{opacity}' if opacity is not None else ''
        self._emit(f'<rect x="{self.ox+x:.2f}" y="{self.oy+y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" '
                   f'style="fill:{fill};stroke:{stroke};stroke-width:{sw}{d}{op}"/>', (x, y, x + w, y + h))

    def text(self, x, y, s, size=2.6, fill=INK, anchor='start', bold=False, rot=None, italic=False, mono=False,
             disp=False, ls=0.0, rec=True):
        s = str(s)
        if self.cur is not None and self.cur['target'] == 'pic':
            size = max(size, MINF)
        kind = 'disp' if disp else ('mono' if mono else ('bold' if bold else 'sans'))
        w = text_w(s, size, kind, ls)
        x0 = x if anchor == 'start' else (x - w / 2 if anchor == 'middle' else x - w)
        bbox = (x0, y - 0.8 * size, x0 + w, y + 0.22 * size) if rot is None else None
        gx = self.ox + x0 if rot is None else self.ox + x
        gy = self.oy + y
        tr = f'translate({gx:.2f},{gy:.2f})'
        if rot is not None:
            tr = f'translate({self.ox+x:.2f},{self.oy+y:.2f}) rotate({rot}) translate({-w/2 if anchor=="middle" else 0:.2f},0)'
        if italic:
            tr += ' skewX(-12)'
        body = text_path(s, size, kind, ls)
        self._emit(f'<g transform="{tr}" fill="{fill}">{body}</g>', bbox, s if bbox else None)
        if rec and rot is None and s.strip():
            self._run(x0, y, size, w, s)

    def _run(self, x0, y, size, w, s):
        if self.cur is None:
            self.runs.append((self.ox + x0, self.oy + y, size, w, s))
        else:
            self.cur['runs'].append((self.cur['target'], x0, y, size, w, s))

    def lines(self, x, y, ls_, size=2.6, dy=3.4, **kw):
        for i, l in enumerate(ls_):
            self.text(x, y + i * dy, l, size, **kw)

    def line(self, x1, y1, x2, y2, color=INK, sw=0.3, dash=None):
        d = f';stroke-dasharray:{dash}' if dash else ''
        self._emit(f'<path d="M{self.ox+x1:.2f},{self.oy+y1:.2f} L{self.ox+x2:.2f},{self.oy+y2:.2f}" '
                   f'style="stroke:{color};stroke-width:{sw};fill:none{d}"/>', (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)))

    def poly(self, pts, color=INK, sw=0.3, fill='none', close=False, dash=None):
        d = ' L '.join(f'{self.ox+x:.2f},{self.oy+y:.2f}' for x, y in pts) + (' z' if close else '')
        ds = f';stroke-dasharray:{dash}' if dash else ''
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self._emit(f'<path d="M {d}" style="stroke:{color};stroke-width:{sw};fill:{fill}{ds}"/>', (min(xs), min(ys), max(xs), max(ys)))

    def circle(self, x, y, r, fill=INK, stroke='none', sw=0.3, opacity=None):
        op = f';stroke-opacity:{opacity}' if opacity is not None else ''
        self._emit(f'<circle cx="{self.ox+x:.2f}" cy="{self.oy+y:.2f}" r="{r}" style="fill:{fill};stroke:{stroke};stroke-width:{sw}{op}"/>',
                   (x - r, y - r, x + r, y + r))

    def arrow(self, pts, color=INK, sw=0.4, dash=None, both=False):
        mk = 'ahr' if color == RED else 'ah'
        d = 'M ' + ' L '.join(f'{self.ox+x:.2f},{self.oy+y:.2f}' for x, y in pts)
        ds = f';stroke-dasharray:{dash}' if dash else ''
        ms = f' marker-start="url(#{mk}s)"' if both else ''
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self._emit(f'<path d="{d}" style="stroke:{color};stroke-width:{sw};fill:none{ds}" marker-end="url(#{mk})"{ms}/>',
                   (min(xs), min(ys), max(xs), max(ys)))

    def tex(self, x, y, src, pt=9.0, color=INK, anchor='start'):
        """LaTeX equation, vertically centered on y, pt = nominal print size"""
        w_, h_, inner = tex_asset(src, color.lstrip('#'))
        k = pt / 10.0 * 0.3528 / SCALE
        w, h = w_ * k, h_ * k
        x0 = x if anchor == 'start' else (x - w / 2 if anchor == 'middle' else x - w)
        y0 = y - h / 2
        self._emit(f'<g transform="translate({self.ox+x0:.2f},{self.oy+y0:.2f}) scale({k:.4f})">{inner}</g>',
                   (x0, y0, x0 + w, y0 + h), 'tex:' + src[:20])
        return w, h

    # composite pieces ---------------------------------------------------------------------------------
    def cell(self, x, y, w, h, label='', fill=LPK, stroke=PUR, size=2.4, bold=False, color=INK):
        self.rect(x, y, w, h, fill, stroke, 0.3)
        if label != '':
            size_ = size
            avail = w - 1.2
            tw = text_w(str(label), max(size_, MINF if self.cur is not None else 0), 'bold' if bold else 'sans')
            if tw > avail and self.cur is not None:
                size_ = max(size * avail / tw, 1.6)
            self.text(x + w / 2, y + h / 2 + size_ * 0.35, label, size_, color, 'middle', bold)

    def block(self, x, y, w, h, title, sub=None, fill=PUR, size=2.7):
        self.rect(x, y, w, h, fill)
        cy = y + h / 2
        if sub:
            self.text(x + w / 2, cy - 0.3, title, size, '#fff', 'middle', True)
            for i, s in enumerate(sub if isinstance(sub, list) else [sub]):
                self.text(x + w / 2, cy + 2.8 + i * 2.8, s, size - 0.2, '#fff', 'middle')
        else:
            self.text(x + w / 2, cy + size * 0.35, title, size, '#fff', 'middle', True)

    def burst(self, x, y, s, size=3.4):
        pts = []
        for i in range(20):
            a = i * math.pi / 10
            rad = 11 if i % 2 == 0 else 7
            pts.append((x + rad * math.cos(a) * 1.5, y + rad * math.sin(a)))
        self.poly(pts, INK, 0.35, '#fff', True)
        self.text(x, y + 1.2, s, size, INK, 'middle', True, italic=True)

    # one step = one panel of the 2 x 2 grid: title, paragraph, figure, example strip ---------------------------------
    def begin_text(self, number, section, title, body, example):
        self._flush()
        self.step_no = number
        self.ox = self.oy = 0
        self.cur = {'origin': ORIGINS[self.slot], 'head': [], 'pic': [], 'target': 'head', 'bbox': [], 'texts': [],
                    'area': PIC, 'runs': []}
        self.slot += 1
        num = str(number)
        self.text(1.0, 10.2, num, 11, CANOPY, 'start', disp=True)
        tx = 1.0 + text_w(num, 11, 'disp') + 3.5
        self.text(tx, 3.8, section, 2.2, SAGE, 'start', mono=True, ls=0.6)
        tsz = 4.9
        while text_w(title, tsz, 'disp') > PAN_W - tx - 2 and tsz > 3.6:
            tsz -= 0.2
        self.text(tx, 9.6, title, tsz, INK, 'start', disp=True)
        self.line(1, 12.6, PAN_W - 1, 12.6, SAP, 0.35)
        W = PAN_W - 3
        y = 17.6
        prev_tex = False
        for it in body:
            if isinstance(it, str):
                STE_TEXT.append((number, plain(it)))
                for ln in wrap_rich(it, BODY, W):
                    self._rich_line(1.5, y, ln)
                    y += BODY_DY
                y += 0.9
                prev_tex = False
            elif it[0] == 'tex':
                pt = it[2] if len(it) > 2 else 9.0
                _w, _h, _ = tex_asset(it[1])
                hh = _h * pt / 10.0 * 0.3528 / SCALE
                if prev_tex:
                    y -= 2.4
                # equal gap above and below: the equation sits halfway between the two paragraphs
                self.tex(1.5 + W / 2, y + 0.1 + hh / 2, it[1], pt, anchor='middle')
                y += hh + 6.8
                prev_tex = True
        text_end = y - 0.9
        area = (3.0, text_end + 3.0, PAN_W - 3.0, PAN_H - 1.0)
        if area[3] - area[1] < 40:
            WARN.append(f'step {number}: figure area only {area[3]-area[1]:.0f} high (text ends {text_end:.0f})')
        self.cur['area'] = area
        self.cur['target'] = 'pic'

    def _rich_line(self, x, y, words, size=None):
        size = size or BODY
        sp = text_w(' ', size)
        x_start, parts = x, []
        for wi, w in enumerate(words):
            for t, k in w:
                sz = size * (0.92 if k == 'mono' else 1.0)
                self.text(x, y, t, sz, INK, 'start', bold=(k == 'bold'), mono=(k == 'mono'), rec=False)
                x += text_w(t, sz, k)
                parts.append(t)
            x += sp
            parts.append(' ')
        line = ''.join(parts).strip()
        if line:
            self._run(x_start, y, size, x - sp - x_start, line)

    def notes_panel(self):
        self._flush()
        self.ox = self.oy = 0
        self.cur = {'origin': ORIGINS[self.slot], 'head': [], 'pic': [], 'target': 'head', 'bbox': [], 'texts': [],
                    'area': PIC, 'runs': []}
        self.slot += 1
        self.text(1.0, 6.0, 'NOTES', 2.4, SAGE, 'start', mono=True, ls=0.7)
        y = 16.0
        while y < PAN_H - 2:
            self.line(1, y, PAN_W - 1, y, '#d9dfd6', 0.25)
            y += 7.5
        self._flush()

    def _flush(self):
        if self.cur is None:
            return
        c = self.cur
        self.cur = None
        ox, oy = c['origin']
        extra = ''
        k = 1.0
        if c.get('chip'):
            lab, cy0 = c['chip']
            w_ = text_w(lab, 2.2, 'mono', 0.6) + 4
            extra += (f'<rect x="1" y="{cy0:.2f}" width="{w_:.2f}" height="4.6" rx="1.2" style="fill:{BONE2}"/>'
                      f'<g transform="translate(3,{cy0+3.3:.2f})" fill="{SAGE}">{text_path(lab, 2.2, "mono", 0.6)}</g>')
        dx = dy = 0.0
        if c['bbox']:
            x0 = min(b[0] for b in c['bbox']); y0 = min(b[1] for b in c['bbox'])
            x1 = max(b[2] for b in c['bbox']); y1 = max(b[3] for b in c['bbox'])
            w, h = max(x1 - x0, 0.01), max(y1 - y0, 0.01)
            PA = c['area']
            aw, ah = PA[2] - PA[0], PA[3] - PA[1]
            k = min(aw / w, ah / h, KMAX)
            if k < 0.82:
                WARN.append(f'step {self.step_no}: figure {w:.0f}x{h:.0f} shrunk to {k:.2f}')
            tb = [((a, b, cc, d), s) for (a, b, cc, d), s in c['texts']]
            for i in range(len(tb)):
                for j in range(i + 1, len(tb)):
                    (a, b_, c_, d), s1 = tb[i]
                    (e, f, g, h_), s2 = tb[j]
                    ox_ = min(c_, g) - max(a, e)
                    oy_ = min(d, h_) - max(b_, f)
                    if ox_ > 0.4 and oy_ > 0.8:
                        WARN.append(f'step {self.step_no}: text overlap {s1!r} / {s2!r}')
            cx, cy = (PA[0] + PA[2]) / 2, (PA[1] + PA[3]) / 2
            bx, by = (x0 + x1) / 2, (y0 + y1) / 2
            pic = (f'<g transform="translate({cx:.2f},{cy:.2f}) scale({k:.4f}) translate({-bx:.2f},{-by:.2f})">'
                   + ''.join(c['pic']) + '</g>')
        else:
            pic = ''.join(c['pic'])
        for tgt, x, y, sz, w, st in c['runs']:
            if tgt == 'pic' and c['bbox']:
                X = ox + SCALE * (cx + k * (x - bx)); Y = oy + SCALE * (cy + k * (y - by)); f = SCALE * k
            else:
                X = ox + SCALE * x; Y = oy + SCALE * y; f = SCALE
            self.runs.append((X, Y, max(sz, MINF if tgt == 'pic' else 0) * f if False else sz * f, w * f, st))
        self.o.append(f'<g transform="translate({ox:.2f},{oy:.2f}) scale({SCALE:.4f})">' + extra + ''.join(c['head']) + pic + '</g>')

    def svg(self):
        self._flush()
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">'
                '<defs>'
                '<marker id="ah" orient="auto" markerWidth="2.6" markerHeight="2.6" refX="2.1" refY="1.3" markerUnits="userSpaceOnUse"><path d="M0,0 L2.6,1.3 L0,2.6 z" style="fill:#000"/></marker>'
                f'<marker id="ahr" orient="auto" markerWidth="2.6" markerHeight="2.6" refX="2.1" refY="1.3" markerUnits="userSpaceOnUse"><path d="M0,0 L2.6,1.3 L0,2.6 z" style="fill:{RED}"/></marker>'
                '<marker id="ahs" orient="auto" markerWidth="2.6" markerHeight="2.6" refX="0.5" refY="1.3" markerUnits="userSpaceOnUse"><path d="M2.6,0 L0,1.3 L2.6,2.6 z" style="fill:#000"/></marker>'
                f'<marker id="ahrs" orient="auto" markerWidth="2.6" markerHeight="2.6" refX="0.5" refY="1.3" markerUnits="userSpaceOnUse"><path d="M2.6,0 L0,1.3 L2.6,2.6 z" style="fill:{RED}"/></marker>'
                '</defs>'
                f'<rect width="{PW}" height="{PH}" style="fill:{self.bg or BG}"/>')
        return head + '\n'.join(self.o) + '</svg>'


# the Auselia mark (brand/mark/svg)
MARK_VB = (-4.6, 3.0, 64.0)


def draw_mark(pg, x, y, size, stem, leaf, node, arcs, rings=False):
    s = size / MARK_VB[2]
    tx, ty = x - MARK_VB[0] * s, y - MARK_VB[1] * s
    g = [f'<g transform="translate({pg.ox+tx:.3f},{pg.oy+ty:.3f}) scale({s:.4f})">']
    if rings:
        for r, op in ((9, 0.55), (18, 0.35), (28, 0.22)):
            g.append(f'<circle cx="28" cy="24" r="{r}" style="fill:none;stroke:{AMBER};stroke-width:0.35;stroke-opacity:{op}"/>')
    g.append(f'<path d="M28 58V12" fill="none" stroke="{stem}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(f'<path d="M28 48C28 37 18 31 7 31C7 42 17 50 28 48Z" fill="{leaf}"/>')
    g.append(f'<circle cx="28" cy="24" r="6" fill="{node}"/>')
    g.append(f'<path d="M39.5 16A14 14 0 0 1 39.5 32" fill="none" stroke="{arcs}" stroke-width="3.6" stroke-linecap="round"/>')
    g.append(f'<path d="M46 11.4A22 22 0 0 1 46 36.6" fill="none" stroke="{arcs}" stroke-width="3.6" stroke-linecap="round"/></g>')
    pg.o.append(''.join(g))


# ------------------------------------------------------------------------------------------------
# document: pages and steps
# ------------------------------------------------------------------------------------------------
pages = []
DOC_NAME = 'ADS7057 TEST BOARD  /  HARDWARE MANUAL  /  VERSION 0.1'
SECTIONS = []          # (first step, name), filled by section()
_cur = {'page': None, 'n': 0, 'section': '', 'first': '', 'last': ''}


def new_page(title):
    p_ = Page(title)
    pages.append((p_, title))
    return p_


def chrome(pg, number, kicker, divider=True):
    pg.cur = None
    pg.ox = pg.oy = 0
    pg.text(MARGIN_X, 11.0, kicker.upper(), 2.6, SAGE, 'start', mono=True, ls=0.5)
    draw_mark(pg, MARGIN_X - 1, PH - 14.2, 10, BONE, BONE, BONE, BONE)
    pg.text(MARGIN_X + 13, PH - 8.2, 'AUSELIA  /  ' + DOC_NAME, 2.3, SAGE, 'start', mono=True, ls=0.35)
    pg.text(PW - MARGIN_X, PH - 8.2, f'{number:02d}', 2.6, SAGE, 'end', mono=True)
    if number >= 4 and divider:
        pg.line(MARGIN_X, TOP + CELL_H + GAP / 2, PW - MARGIN_X, TOP + CELL_H + GAP / 2, SAP, 0.25)


# block map of page 3 (mm): name -> (x, y, w, h); reused small on the section pages
BLOCK_MAP = {
    'System SRAM': (9, 82, 35, 24), 'CPU': (238, 40, 32, 24),
    'Address unit': (58, 40, 38, 24), 'Sequencer': (106, 40, 70, 24), 'Registers': (190, 40, 36, 24),
    'OBI manager': (58, 82, 38, 24), 'r0, r1': (106, 82, 38, 24), 'Adder': (154, 82, 36, 24), 'Features': (196, 82, 30, 24),
    'Cosine ROM': (58, 122, 38, 24), 'Multiplier': (106, 122, 38, 24), 'Accumulator': (154, 122, 36, 24)}
MAP_FRAME = (52, 33, 178, 120)   # the accelerator frame on page 3, drawn small on the section pages
IDEA = 'THE IDEA'
N_IDEA = 12          # panels of part 0 (the idea); the hardware steps are numbered from 1 after them


def step_label(n):
    """panel index -> printed number: 0.1 ... 0.12 for the idea, then 1, 2, 3 ..."""
    return f'0.{n}' if n <= N_IDEA else str(n - N_IDEA)


def _finish_page():
    """fill the free panels of the current step page with notes panels and draw its header and footer"""
    pg = _cur['page']
    if pg is None:
        return
    pg._flush()
    while pg.slot < 4:
        pg.notes_panel()
    a_, b_ = _cur['first'], _cur['last']
    sec = _cur['section']
    if sec == IDEA:
        kick = f'Part 0  /  {IDEA.lower()}  /  {a_} to {b_}'
    else:
        kick = f'Steps {a_} to {b_}  /  {sec}' if a_ != b_ else f'Step {a_}  /  {sec}'
    chrome(pg, pg.num, kick)
    _cur['page'] = None


def section(name, title=None, part=None, rng=None, desc=None, active=None):
    """start a section: close the current page and add a dark section page"""
    _finish_page()
    _cur['section'] = name
    if title is None:
        return
    pg = new_page('section ' + name)
    pg.bg = FOREST
    pg.cur = None
    pg.ox = pg.oy = 0
    pg.text(20, 46, part.upper(), 3.0, SAP, 'start', mono=True, ls=0.9)
    ts_ = min(18.0, 18.0 * (125 if active is not None else 140) / text_w(title, 18.0, 'disp'))
    pg.text(20, 80, title, ts_, BONE, 'start', disp=True)
    pg.text(20, 94, rng.upper(), 3.4, AMBER, 'start', mono=True, ls=0.8)
    cur, out = '', []
    for w_ in desc.split():
        if text_w(cur + ' ' + w_, 4.4) > 112:
            out.append(cur)
            cur = w_
        else:
            cur = (cur + ' ' + w_).strip()
    out.append(cur)
    for k_, l_ in enumerate(out):
        pg.text(20, 112 + k_ * 6.6, l_, 4.4, '#D8E4D2')
    if active is None:
        draw_mark(pg, 172, 44, 84, BONE, BONE, AMBER, AMBER, rings=True)
    if active is not None:
        s_, x0, y0 = 0.45, 152, 62
        X_ = lambda x: x0 + (x - 9) * s_
        Y_ = lambda y: y0 + (y - 40) * s_
        fx, fy, fw, fh = MAP_FRAME
        pg.rect(X_(fx), Y_(fy), fw * s_, fh * s_, 'none', '#4d6b58', 0.4, 2)
        for nm, (x, y, w, h) in BLOCK_MAP.items():
            on = nm in active
            pg.rect(X_(x), Y_(y), w * s_, h * s_, AMBER if on else 'none', AMBER if on else '#4d6b58', 0.4, 1.2)
            sz = min(2.5, (w * s_ - 1.5) / max(text_w(nm, 1.0, 'bold'), 0.1))
            pg.text(X_(x) + w * s_ / 2, Y_(y) + h * s_ / 2 + sz * 0.35, nm, sz, INK if on else '#7E9C86', 'middle', True)
        pg.text(X_(9), Y_(fy) + fh * s_ + 4.5, 'BLOCKS AT WORK IN THIS SECTION (SEE PAGE 3)', 2.3, SAP, 'start', mono=True, ls=0.6)
    pg.text(20, PH - 12, 'AUSELIA  /  ' + DOC_NAME, 2.5, '#7E9C86', 'start', mono=True, ls=0.5)
    pg.text(PW - 20, PH - 12, f'{len(pages):02d}', 2.5, '#7E9C86', 'end', mono=True)


def step(title, body, example=None):   # the example is drawn in the figure, the argument is not used
    """Start the next step (one panel of the 2 x 2 grid). Returns the page, positioned for the figure."""
    _cur['n'] += 1
    n = _cur['n']
    if _cur['page'] is None or _cur['page'].slot >= 4:
        _finish_page()
        pg = new_page(f'step {n}')
        pg.num = len(pages)
        _cur['page'] = pg
        _cur['first'] = step_label(n)
    pg = _cur['page']
    _cur['last'] = step_label(n)
    pg.begin_text(step_label(n), _cur['section'], title, body, example)
    return pg


def end_steps():
    _finish_page()


def steps_done():
    return f"{N_IDEA} idea panels + {_cur['n'] - N_IDEA} steps"


# ------------------------------------------------------------------------------------------------
# helper drawings
# ------------------------------------------------------------------------------------------------
def reg_pair(pg, x, y, name, re_v, im_v, w=34, h=8, fill='#fff'):
    pg.rect(x, y, w, h, fill, PUR, 0.4)
    pg.line(x + w / 2, y, x + w / 2, y + h, PUR, 0.3)
    pg.text(x + w / 4, y + h / 2 + 0.9, re_v, 2.6, INK, 'middle', True)
    pg.text(x + 3 * w / 4, y + h / 2 + 0.9, im_v, 2.6, INK, 'middle', True)
    pg.text(x - 1.5, y + h / 2 + 0.9, name, 2.5, PUR, 'end', True)
    pg.text(x + w / 4, y - 1, 'Re', 2.0, '#555', 'middle')
    pg.text(x + 3 * w / 4, y - 1, 'Im', 2.0, '#555', 'middle')


def bars(pg, x, y, w, h, vals, hi=(), band=None, color=PUR, hicolor=AMB, kmin=None, label_every=16, labels=True):
    n = len(vals)
    mx = max(vals) or 1
    bw = w / n
    if band:
        pg.rect(x + band[0] * bw, y, (band[1] - band[0] + 1) * bw, h, LPK, 'none')
    for i, v in enumerate(vals):
        c = '#bbb' if (kmin is not None and i < kmin) else (hicolor if i in hi else color)
        bh = h * v / mx
        pg.rect(x + i * bw + 0.1, y + h - bh, max(bw - 0.2, 0.2), bh, c)
    pg.line(x, y + h, x + w, y + h, INK, 0.3)
    if labels:
        k = 0
        while k < n:
            pg.text(x + k * bw + bw / 2, y + h + 3.2, k, 2.1, INK, 'middle')
            k += label_every


def wave(pg, x, y, w, h, vals, color=PUR, sw=0.3, dots=False, scale=None, axis=True):
    mx = scale or max(abs(v) for v in vals) or 1
    pts = [(x + i * w / (len(vals) - 1), y + h / 2 - (v / mx) * h / 2) for i, v in enumerate(vals)]
    if axis:
        pg.line(x, y + h / 2, x + w, y + h / 2, '#999', 0.15)
    pg.poly(pts, color, sw)
    if dots:
        for px, py in pts:
            pg.circle(px, py, 0.5, color)


def stems(pg, x, y, w, h, vals, color=PUR, scale=None, labels=True, lab_size=2.4, cw=None):
    """lollipop plot of a few samples: axis in the middle, value written above or below"""
    n = len(vals)
    mx = scale or max(abs(v) for v in vals) or 1
    cw = cw or w / n
    pg.line(x, y + h / 2, x + n * cw, y + h / 2, '#888', 0.2)
    for i, v in enumerate(vals):
        cx = x + i * cw + cw / 2
        vy = y + h / 2 - (v / mx) * (h / 2 - 3)
        pg.line(cx, y + h / 2, cx, vy, color, 0.6)
        pg.circle(cx, vy, 1.0, color)
        if labels:
            ty = vy - 1.6 if v >= 0 else vy + 3.4
            pg.text(cx, ty, sgn(v), lab_size, INK, 'middle', True)


def cplx(r, i):
    return f'{r}{"+" if i >= 0 else "−"}{abs(i)}j'


def sine_wave(f, amp=1.0, ph=0.0):
    return [amp * math.sin(2 * math.pi * f * n / 128 + ph) for n in range(128)]


# ------------------------------------------------------------------------------------------------
# mechanical STE check (approximate, in the spirit of tools/ste_check.py)
# ------------------------------------------------------------------------------------------------
def ste_report():
    out = []
    words = 0
    issues = []
    for n, t in STE_TEXT:
        words += len(t.split())
        for s in re.split(r'(?<=[.!?:])\s+', t):
            c = len(s.split())
            if c > 25:
                issues.append((n, f'length {c}', s))
        for pat, nm in [(r';', 'semicolon'), (r'—|--', 'em dash'), (r"\b\w+n't\b|\b(it|that|there)'s\b", 'contraction'),
                        (r'\b(has|have|had) (been )?\w+(ed|en)\b', 'present perfect'),
                        (r'\b(is|are|was|were|be|been) (\w+ly )?\w+ed\b', 'passive?'),
                        (r'\b(utilize|leverage|facilitate|ensure|perform|provide|prior to|subsequent|additionally|furthermore|moreover|seamless|robust|powerful)\b', 'word')]:
            for mm in re.finditer(pat, t, re.I):
                issues.append((n, nm, t[max(0, mm.start() - 25):mm.end() + 25]))
    out.append(f'STE check: {words} words, {len(issues)} flags, {100*len(issues)/max(words,1):.1f} per 100 words')
    for i in issues:
        out.append(f'   step {i[0]}: {i[1]}: {i[2][:120]}')
    return out


def chip(pg, x=None, y=None, label='EXAMPLE'):
    """tag that marks a figure as a worked example. It sits in the gap above the figure; x and y are not used."""
    c = pg.cur
    a = c['area']
    c['chip'] = (label, a[1] - 1.3)
    c['area'] = (a[0], a[1] + 4.6, a[2], a[3])
