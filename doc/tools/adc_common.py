"""Shared helpers and numbers of the hardware manual. Every number in a figure comes from here.
Sources: hw/ADC_Test.net (parts and values), doc/data/board.json (layout), doc/data/sim.json (simulation),
hw/fab/*.csv (BOM and CPL), and the datasheets (constants marked DS)."""
import json, math, os, re, sys, csv
from m4lib import *
import m4lib

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
DATA = os.path.join(REPO, 'doc', 'data')
BOARD = json.load(open(os.path.join(DATA, 'board.json')))
SIM = json.load(open(os.path.join(DATA, 'sim.json')))
FP = BOARD['footprints']
HEAD = json.load(open(os.path.join(DATA, 'head.json')))
HFP = HEAD['footprints']
BW, BH = BOARD['size']                      # main board, mm
HW_, HH_ = HEAD['size']                     # sensor head, mm

# ------------------------------------------------------------------------------------------------
# parts and values from the netlist
# ------------------------------------------------------------------------------------------------
sys.path.insert(0, os.path.join(REPO, 'hw', 'tools'))
from sexp import parse, find, get
_t = parse(open(os.path.join(REPO, 'hw', 'ADC_Test.net')).read())
COMP = {}
for _c in find(get(_t, 'components'), 'comp'):
    COMP[get(_c, 'ref')[1]] = dict(value=get(_c, 'value')[1], fp=get(_c, 'footprint')[1])
NET = {}
for _n in find(get(_t, 'nets'), 'net'):
    NET[get(_n, 'name')[1]] = [(get(x, 'ref')[1], get(x, 'pin')[1]) for x in find(_n, 'node')]


def val(ref):
    """numeric value of a resistor or capacitor from its value string"""
    s = COMP[ref]['value'].split()[0]
    m = re.fullmatch(r'([\d.]+)(R|k|M|pF|nF|uF|uH)', s)
    mult = {'R': 1, 'k': 1e3, 'M': 1e6, 'pF': 1e-12, 'nF': 1e-9, 'uF': 1e-6, 'uH': 1e-6}[m.group(2)]
    return float(m.group(1)) * mult


def eng(v, unit=''):
    for lim, pre, k in ((1e6, 'M', 1e6), (1e3, 'k', 1e3), (1, '', 1), (1e-3, 'm', 1e-3), (1e-6, 'µ', 1e-6), (1e-9, 'n', 1e-9), (1e-12, 'p', 1e-12)):
        if abs(v) >= lim * 0.9999:
            x = v / k
            return (f'{x:.3g}' if x < 100 else f'{x:.0f}') + ' ' + pre + unit
    return f'{v} {unit}'


# ------------------------------------------------------------------------------------------------
# design numbers (computed, then checked against the simulation)
# ------------------------------------------------------------------------------------------------
AVDD = 3.3
LSB = 2 * AVDD / 2 ** 14                         # DS: 1 LSB = 2 x VREF / 2^N
HP_C, HP_R1, HP_R2 = val('C1'), val('R1'), val('R2')
assert val('C2') == HP_C
HP_F0 = 1 / (2 * math.pi * HP_C * math.sqrt(HP_R1 * HP_R2))
HP_Q = 0.5 * math.sqrt(HP_R2 / HP_R1)
GAIN = 1 + val('R3') / val('R4')
LP_R = val('R5'); assert val('R6') == LP_R
LP_C1 = val('C4') + val('C5'); LP_C2 = val('C6')
LP_F0 = 1 / (2 * math.pi * LP_R * math.sqrt(LP_C1 * LP_C2))
LP_Q = 0.5 * math.sqrt(LP_C1 / LP_C2)
CPL_FC = 1 / (2 * math.pi * val('R10') * val('C11'))              # coupling into the driver
ADC_C = sum(val(r) for r in ('C14', 'C15', 'C16', 'C17'))
ADC_R = val('R16') + val('R17')
ADC_POLE = 1 / (2 * math.pi * ADC_R * ADC_C)
CS_ADC = 16e-12                                                    # DS 8.3.2
RS_ADC = 50.0
assert 111e3 < HP_F0 < 114e3 and abs(HP_Q - 0.7071) < 0.01
assert 510e3 < LP_F0 < 513e3 and abs(LP_Q - 0.7071) < 0.01
assert abs(GAIN - 4.9) < 1e-9
RP_MAX = 20e3


def window(rp):
    """half width of the comparator window at LPF_OUT, volts"""
    return 2.5 * (val('R22') + rp) / (val('R21') + val('R23') + val('R22') + rp)


assert abs(window(0) - 0.0373) < 0.001 and abs(window(RP_MAX) - 0.6034) < 0.001
SIM_GAIN = SIM['adc']
F = SIM['f']


def at(arr, f):
    i = min(range(len(F)), key=lambda k: abs(math.log(F[k] / f)))
    return arr[i]


ADC_GAIN_250 = at(SIM['adc'], 250e3)               # SMA to ADC differential, V/V
assert 3.9 < ADC_GAIN_250 < 4.4
MC = SIM['mc']
LOSS10 = [r['loss10k'] for r in MC]
assert len(MC) == 150 and sum(1 for x in LOSS10 if x < 40) == 11


def db(x):
    return 20 * math.log10(x)


# ------------------------------------------------------------------------------------------------
# blocks of the board (for the placement map and the BOM)
# ------------------------------------------------------------------------------------------------
BLOCKS = [
    ('Input and high-pass', PUR, ['C1', 'C2', 'R1', 'R2']),
    ('Gain', '#b04aa0', ['R3', 'R4']),
    ('Low-pass', '#c47bb8', ['R5', 'R6', 'C4', 'C5', 'C6']),
    ('Op-amps U1, U2 and bypass', '#6b2d86', ['U1', 'U2', 'C3', 'C10']),
    ('Mid-rail VMID5', '#8a6fb0', ['R7', 'R8', 'C7', 'R9', 'C8', 'C9']),
    ('Driver THS4531', BLU, ['U3', 'C11', 'R10', 'R11', 'R12', 'R13', 'C12']),
    ('VOCM 1.65 V', '#4f86c6', ['R14', 'R15', 'C13']),
    ('ADC input filter', '#2c9aa8', ['R16', 'R17', 'C14', 'C15', 'C16', 'C17']),
    ('ADS7057 and bypass', '#0e6e7a', ['U4', 'C18', 'C19', 'C20', 'C22']),
    ('SPI series resistors', '#6aa8b0', ['R18', 'R19', 'R20']),
    ('AVDD regulator', '#6aa84f', ['U5', 'C21', 'C30']),
    ('9 V to 5 V', GRN, ['D1', 'C23', 'U7', 'C29']),
    ('Wake-up comparator', '#d89cc8', ['U6', 'R21', 'R22', 'R23', 'RV1', 'C26', 'C27', 'C28', 'R24', 'C31']),
    ('Bias-T for the head', '#d9822b', ['L2', 'R26', 'R27', 'C32', 'C33']),
    ('Connectors', '#8a8a8a', ['J1', 'J2', 'J3', 'J4', 'R25']),
    ('Holes', '#bbbbbb', ['H1', 'H2']),
]
BLOCK_OF = {r: n for n, c, rs in BLOCKS for r in rs}
BLOCK_COLOR = {n: c for n, c, rs in BLOCKS}
assert set(BLOCK_OF) == set(FP), (set(FP) - set(BLOCK_OF), set(BLOCK_OF) - set(FP))


def net_length(name):
    """total routed length of a net in mm, F.Cu and B.Cu"""
    return sum(math.hypot(t['x2'] - t['x1'], t['y2'] - t['y1']) for t in BOARD['tracks'] if t['net'] == name)


# ------------------------------------------------------------------------------------------------
# drawing helpers (from the SPI manual, same colors by role)
# ------------------------------------------------------------------------------------------------
KIND = {
    'ctrl': (LPK, PUR, INK, INK), 'arith': (PUR, PUR, '#fff', '#fff'), 'reg': ('#fff', PUR, INK, INK),
    'mem': (BLU, BLU, '#fff', '#fff'), 'bus': (GRN, GRN, '#fff', '#fff'), 'ext': (LGR, '#777', INK, INK),
    'dev': ('#fff', CANOPY, INK, INK), 'item': (AMBT, AMB, INK, INK)}


def fit(s, size, kind, w):
    tw = text_w(s, size, kind)
    return size if tw <= w else size * w / tw


def pbox(pg, x, y, w, h, title, subs=(), kind='reg', tsz=3.0, ssz=2.5, dy=4.0):
    f, b, tc, sc = KIND[kind]
    pg.rect(x, y, w, h, f, b, 0.5, 1.8)
    lines = [(title, tsz, 'bold', tc)] + [(s_, ssz, 'sans', sc) for s_ in subs]
    y0 = y + h / 2 - (len(lines) - 1) * dy / 2 + 1.0
    for k_, (s_, sz, kd, col) in enumerate(lines):
        sz = fit(s_, sz, kd, w - 3)
        pg.text(x + w / 2, y0 + k_ * dy, s_, sz, col, 'middle', bold=(kd == 'bold'))


def lab(pg, x, y, s, anchor='middle', size=2.5, color='#2d3b33', bold=True):
    pg.text(x, y, s, size, color, anchor, bold)


def sq_wave(pg, x, y, w, h, levels, color=INK, sw=0.45):
    n = len(levels)
    dx = w / n
    pts = []
    for i, l in enumerate(levels):
        yy = y + (0 if l else h)
        pts.append((x + i * dx, yy))
        pts.append((x + (i + 1) * dx, yy))
    pg.poly(pts, color, sw)


def data_lane(pg, x, y, w, h, labels, fill='#fff', stroke=INK, size=2.5):
    n = len(labels)
    dx = w / n
    for i, s_ in enumerate(labels):
        x0, x1 = x + i * dx, x + (i + 1) * dx
        c = 0.8
        pts = [(x0 + c, y), (x1 - c, y), (x1, y + h / 2), (x1 - c, y + h), (x0 + c, y + h), (x0, y + h / 2)]
        f = fill if not isinstance(fill, list) else fill[i]
        pg.poly(pts, stroke, 0.3, f, True)
        if s_ != '':
            sz = fit(str(s_), size, 'sans', dx - 1.6)
            pg.text((x0 + x1) / 2, y + h / 2 + sz * 0.35, s_, sz, INK, 'middle')


def curve(pg, x, y, w, h, xs, ys, xlo, xhi, ylo, yhi, color=PUR, sw=0.5, logx=True, dash=None):
    """plot (xs, ys) in a box at (x, y) of size w x h; axes ranges xlo..xhi, ylo..yhi"""
    pts = []
    for a, b in zip(xs, ys):
        if a < xlo or a > xhi:
            continue
        px = x + ((math.log10(a / xlo) / math.log10(xhi / xlo)) if logx else (a - xlo) / (xhi - xlo)) * w
        py = y + h - (min(max(b, ylo), yhi) - ylo) / (yhi - ylo) * h
        pts.append((px, py))
    pg.poly(pts, color, sw, dash=dash)
    return pts


def freq_axis(pg, x, y, w, xlo, xhi, ticks, size=2.3):
    pg.line(x, y, x + w, y, '#888', 0.25)
    for f in ticks:
        px = x + math.log10(f / xlo) / math.log10(xhi / xlo) * w
        pg.line(px, y, px, y + 1.4, '#888', 0.25)
        s = f'{f/1e6:g} M' if f >= 1e6 else (f'{f/1e3:g} k' if f >= 1e3 else f'{f:g}')
        pg.text(px, y + 4.2, s, size, MUTED, 'middle')


def mini_map(pg, x, y, w, active, label_refs=False, fill_others='#e4e4df'):
    """the board outline at scale w/BW with every part as a small box; parts in `active` are amber"""
    k = w / BW
    pg.rect(x, y, BW * k, BH * k, '#f8f8f4', INK, 0.4, 0.8)
    for ref, f in FP.items():
        x0, y0, x1, y1 = f['bbox']
        on = ref in active
        pg.rect(x + max(x0, 0) * k, y + max(y0, 0) * k, (min(x1, BW) - max(x0, 0)) * k, (min(y1, BH) - max(y0, 0)) * k,
                AMB if on else fill_others, '#6c6c66' if not on else INK, 0.15, 0.3)
    if label_refs:
        for ref in active:
            f = FP[ref]
            x0, y0, x1, y1 = f['bbox']
            pg.text(x + (x0 + x1) / 2 * k, y + (y0 + y1) / 2 * k + 0.9, ref, 2.5, INK, 'middle', True)
    return BW * k, BH * k


# ------------------------------------------------------------------------------------------------
# schematic symbols (drawn on the page in panel units)
# ------------------------------------------------------------------------------------------------
def res_h(pg, x, y, w=12.0, name=None, value=None, color=INK, above=True):
    n, a = 6, 1.6
    seg = w / (n + 1)
    pts = [(x, y), (x + seg * 0.5, y)]
    for i in range(n):
        pts.append((x + seg * (0.5 + i + 0.5), y + (a if i % 2 == 0 else -a)))
    pts += [(x + w - seg * 0.5, y), (x + w, y)]
    pg.poly(pts, color, 0.45)
    t = ' '.join(s for s in (name, value) if s)
    if t:
        pg.text(x + w / 2, y - 3.0 if above else y + 5.2, t, 2.5, color, 'middle', True)


def res_v(pg, x, y, h=12.0, name=None, value=None, color=INK, left=False):
    n, a = 6, 1.6
    seg = h / (n + 1)
    pts = [(x, y), (x, y + seg * 0.5)]
    for i in range(n):
        pts.append((x + (a if i % 2 == 0 else -a), y + seg * (0.5 + i + 0.5)))
    pts += [(x, y + h - seg * 0.5), (x, y + h)]
    pg.poly(pts, color, 0.45)
    t = ' '.join(s for s in (name, value) if s)
    if t:
        if left:
            pg.text(x - 3.2, y + h / 2 + 0.9, t, 2.5, color, 'end', True)
        else:
            pg.text(x + 3.2, y + h / 2 + 0.9, t, 2.5, color, 'start', True)


def cap_h(pg, x, y, w=8.0, name=None, value=None, color=INK, above=True):
    m = x + w / 2
    pg.line(x, y, m - 0.7, y, color, 0.45)
    pg.line(m + 0.7, y, x + w, y, color, 0.45)
    pg.line(m - 0.7, y - 2.8, m - 0.7, y + 2.8, color, 0.6)
    pg.line(m + 0.7, y - 2.8, m + 0.7, y + 2.8, color, 0.6)
    t = ' '.join(s for s in (name, value) if s)
    if t:
        pg.text(m, y - 4.2 if above else y + 7.0, t, 2.5, color, 'middle', True)


def cap_v(pg, x, y, h=8.0, name=None, value=None, color=INK, left=False):
    m = y + h / 2
    pg.line(x, y, x, m - 0.7, color, 0.45)
    pg.line(x, m + 0.7, x, y + h, color, 0.45)
    pg.line(x - 2.8, m - 0.7, x + 2.8, m - 0.7, color, 0.6)
    pg.line(x - 2.8, m + 0.7, x + 2.8, m + 0.7, color, 0.6)
    t = ' '.join(s for s in (name, value) if s)
    if t:
        if left:
            pg.text(x - 4.2, m + 0.9, t, 2.5, color, 'end', True)
        else:
            pg.text(x + 4.2, m + 0.9, t, 2.5, color, 'start', True)


def gnd(pg, x, y, color=INK):
    pg.line(x, y, x, y + 2, color, 0.45)
    pg.line(x - 3, y + 2, x + 3, y + 2, color, 0.5)
    pg.line(x - 2, y + 3.4, x + 2, y + 3.4, color, 0.5)
    pg.line(x - 1, y + 4.8, x + 1, y + 4.8, color, 0.5)


def dot(pg, x, y, r=0.8, color=INK):
    pg.circle(x, y, r, color)


def opamp(pg, x, y, w=16.0, h=14.0, label=None, fill='#fff', stroke=INK, plus_top=False):
    """triangle pointing right, left edge at x, vertical center at y. Returns the (+ input, - input, output) points"""
    pg.poly([(x, y - h / 2), (x + w, y), (x, y + h / 2)], stroke, 0.5, fill, True)
    yt, yb = y - h / 4, y + h / 4
    if plus_top:
        pg.text(x + 1.4, yt + 0.9, '+', 3.0, INK, 'start', True)
        pg.text(x + 1.4, yb + 0.9, '−', 3.0, INK, 'start', True)
        pp, pm = (x, yt), (x, yb)
    else:
        pg.text(x + 1.4, yt + 0.9, '−', 3.0, INK, 'start', True)
        pg.text(x + 1.4, yb + 0.9, '+', 3.0, INK, 'start', True)
        pm, pp = (x, yt), (x, yb)
    if label:
        pg.text(x + w * 0.5, y + 0.9, label, 2.5, INK, 'middle', True)
    return pp, pm, (x + w, y)


def image(pg, path, x, y, w, h):
    """embed a JPEG or PNG in the figure"""
    import base64
    data = base64.b64encode(open(path, 'rb').read()).decode()
    mime = 'image/jpeg' if path.endswith('.jpg') else 'image/png'
    pg._emit(f'<image x="{pg.ox+x:.2f}" y="{pg.oy+y:.2f}" width="{w:.2f}" height="{h:.2f}" '
             f'xlink:href="data:{mime};base64,{data}"/>', (x, y, x + w, y + h))
