"""Hardware manual, part A: cover, reading guide, the board in one view, Part 0 (the basics)."""
import json
import m4lib
from adc_common import *

DOC = m4lib.DOC_NAME
EV = json.load(open(os.path.join(DATA, 'events.json')))

# ================================================================================================
# cover
# ================================================================================================
pg = new_page('cover')
pg.bg = FOREST
pg.text(20, 46, 'HARDWARE MANUAL  /  VERSION 0.1', 3.0, SAP, 'start', mono=True, ls=0.9)
pg.text(20, 78, 'AUS', 24, BONE, 'start', disp=True)
pg.text(20 + text_w('AUS', 24, 'disp'), 78, 'ELIA', 24, AMBER, 'start', disp=True)
pg.text(20, 100, 'ADS7057 test board', 15, BONE, 'start', disp=True)
pg.text(20, 114, 'How a perfboard signal becomes SPI samples, one step at a time.', 5.2, '#D8E4D2', 'start')
pg.text(20, 144, 'The topology, the datasheet facts that matter, the routing of the board,', 3.7, SAP)
pg.text(20, 150, 'and what each part is and where it sits.', 3.7, SAP)
pg.text(20, 177, 'Version 0.1  /  October 15, 2026  /  Nicolás Villegas', 3.0, SAP, 'start', mono=True, ls=0.4)
pg.text(20, PH - 12, 'AUSELIA  /  ' + DOC, 2.5, '#7E9C86', 'start', mono=True, ls=0.5)
pg.text(PW - 20, PH - 12, '01', 2.5, '#7E9C86', 'end', mono=True)
draw_mark(pg, 168, 36, 96, BONE, BONE, AMBER, AMBER, rings=True)

# ================================================================================================
# reading guide
# ================================================================================================
pg = new_page('how to read')
chrome(pg, 2, 'Reading guide')
pg.text(MARGIN_X, 32, 'How to read this manual', 11, CANOPY, 'start', disp=True)
pg.text(MARGIN_X, 41, 'Read the text first. Then look at the figure. The figure shows the same thing with numbers.', 3.8, INK)
cards = [
    ('One panel, one step', 'A page holds four steps in a 2 × 2 grid. Each panel has a title, a text and a figure.'),
    ('Example tag', 'A figure with this tag is a worked example. Its numbers come from the netlist, the board file or the simulation.'),
    ('Source', 'The KiCad project in hw/, the simulations in sim/, the vendor datasheets and one real JLCPCB quote.'),
    ('Estimate', 'A number marked ESTIMATE is not measured. Read it as a size, not as a promise.'),
    ('Names', 'R16 is a reference designator. It is the same name in the schematic, the BOM and the silkscreen file.'),
    ('Order', 'Part 0 gives the basics. Steps 1 to 54 follow the power, the signal, the ADC, SPI, the wake-up, the board and the bring-up.'),
]
for i, (t, d) in enumerate(cards):
    col, row = i % 2, i // 2
    x, y = MARGIN_X + col * 130, 52 + row * 38
    pg.rect(x, y, 124, 32, BONE2, 'none', 0, 3)
    pg.text(x + 5, y + 9, f'{i+1:02d}', 2.8, SAGE, 'start', mono=True)
    pg.text(x + 15, y + 9.5, t, 5, CANOPY, 'start', disp=True)
    cur, out = '', []
    for w_ in d.split():
        if text_w(cur + ' ' + w_, 3.2) > 102:
            out.append(cur)
            cur = w_
        else:
            cur = (cur + ' ' + w_).strip()
    out.append(cur)
    pg.lines(x + 15, y + 17, out, 3.2, 4.4, fill='#2b3a31')
sx, sy = MARGIN_X, 175
pg.text(sx, sy, 'Colors', 5, CANOPY, 'start', disp=True)
for i, (c, t) in enumerate([(PUR, 'signal chain'), (BLU, 'driver and ADC'), (GRN, 'power'), (LPK, 'control, data of the example'),
                            (AMBT, 'the item of this step')]):
    px = sx + [0, 40, 80, 105, 175][i]
    pg.rect(px, sy + 5, 8, 5, c, '#444', 0.2, 1)
    pg.text(px + 11, sy + 9, t, 2.9)

# ================================================================================================
# the board in one view
# ================================================================================================
pg = new_page('one view')
chrome(pg, 3, 'The board in one view')
pg.ox = pg.oy = 0
pg.text(MARGIN_X, 25, 'The board in one view', 9, CANOPY, 'start', disp=True)
pg.text(270, 25, 'the signal goes left to right, the power runs along the bottom', 3.0, MUTED, 'end')
B = {
    'Input': (9, 62, 26, 24), 'High-pass': (42, 62, 28, 24), 'Gain': (77, 62, 24, 24), 'Low-pass': (108, 62, 28, 24),
    'Driver': (144, 62, 30, 24), 'ADC': (181, 62, 32, 24), 'SPI port': (222, 62, 36, 24),
    'Scope out': (108, 36, 28, 14), 'Wake-up': (108, 100, 36, 22),
    'Power': (9, 134, 118, 22), 'Mid-rails': (150, 134, 108, 22)}
m4lib.BLOCK_MAP = B
m4lib.MAP_FRAME = (5, 32, 258, 128)
pbox(pg, *B['Input'], 'SMA in', ['J1', 'from the', 'perfboard'], 'ext')
pbox(pg, *B['High-pass'], 'High-pass', ['113 kHz', 'U1A'], 'arith')
pbox(pg, *B['Gain'], 'Gain', ['× 4.9', 'U1B'], 'arith')
pbox(pg, *B['Low-pass'], 'Low-pass', ['512 kHz', 'U2A'], 'arith')
pbox(pg, *B['Driver'], 'Driver', ['THS4531', 'one wire to two'], 'mem')
pbox(pg, *B['ADC'], 'ADS7057', ['14 bit, SPI', 'U4'], 'mem')
pbox(pg, *B['SPI port'], 'PMOD J3', ['CS, SCLK, SDO', 'nWAKE, GND, 3V3'], 'bus')
pbox(pg, *B['Scope out'], 'SCOPE OUT', ['J4, 51 Ω'], 'ext')
pbox(pg, *B['Wake-up'], 'Wake-up', ['LM393 window', 'U6, trimmer RV1'], 'ctrl')
pbox(pg, 9, 134, 28, 22, '9 V in', ['J2'], 'ext')
pbox(pg, 44, 134, 40, 22, '+5 V', ['SS14, AMS1117', 'U7'], 'bus')
pbox(pg, 91, 134, 36, 22, 'AVDD 3.3 V', ['XC6206', 'U5'], 'bus')
pbox(pg, 150, 134, 50, 22, 'VMID5 2.5 V', ['divider and buffer'], 'ctrl')
pbox(pg, 208, 134, 50, 22, 'VOCM 1.65 V', ['AVDD / 2'], 'ctrl')
for a, b in (('Input', 'High-pass'), ('High-pass', 'Gain'), ('Gain', 'Low-pass'), ('Low-pass', 'Driver'), ('Driver', 'ADC'), ('ADC', 'SPI port')):
    ax = B[a][0] + B[a][2]
    pg.arrow([(ax, 74), (B[b][0], 74)])
lab(pg, 196.5, 59.6, 'AINP, AINM')
lab(pg, 159, 59.6, 'diff.')
pg.arrow([(122, 62), (122, 50)])
pg.arrow([(122, 86), (122, 100)])
lab(pg, 124, 94.6, 'LPF_OUT', 'start', 2.3)
pg.arrow([(144, 111), (240, 111), (240, 86)])
lab(pg, 192, 109.4, 'nWAKE', 'middle')
pg.arrow([(37, 145), (44, 145)])
pg.arrow([(84, 145), (91, 145)])
pg.line(8, 129, 262, 129, '#8c8c8c', 0.5, '1.2,1.0')
pg.text(262, 127.6, '+5 V rail to U1, U2, U3 and U6', 2.3, MUTED, 'end')
for xx in (56, 90, 122, 159):
    pg.arrow([(xx, 129), (xx, 126)], '#8c8c8c', 0.4)
pg.line(122, 126, 122, 122, '#8c8c8c', 0.4, '1.2,1.0')
pg.arrow([(197, 88), (197, 100)], '#8c8c8c', 0.4, '1.2,1.0')
lab(pg, 199, 98, 'DVDD 3.3 V from the PMOD', 'start', 2.3, MUTED)
cards = [
    ('THE BASICS', 'part 0', 'What the signal is, why the mid-rails, what an ADC measures and why the filter comes first.'),
    ('POWER', 'steps 1 to 6', '9 V to 5 V to 3.3 V, then the 2.5 V and 1.65 V mid-rails that the signal rides on.'),
    ('SIGNAL AND ADC', 'steps 7 to 24', 'High-pass, gain, low-pass, then the driver and the ADC with its input filter.'),
    ('SPI AND WAKE-UP', 'steps 25 to 35', 'The four SPI wires, the frame and its power-up rule, and the window comparator.'),
    ('THE BOARD', 'steps 36 to 48', 'Layers, floor plan, every part and where it sits, routing, files for the factory and the cost.'),
    ('BRING-UP', 'steps 49 to 54', 'Power-on checks, the first signal, the expected response and what is still open.'),
]
cw_ = (261 - 5 * 3) / 6
for k_, (t_, st_, body_) in enumerate(cards):
    cx0 = MARGIN_X + k_ * (cw_ + 3)
    pg.rect(cx0, 166, cw_, 32, BONE2, 'none', 0, 2.5)
    pg.text(cx0 + 3, 172, t_, 2.7, CANOPY, 'start', True)
    pg.text(cx0 + 3, 177, st_, 2.2, SAGE, 'start', mono=True)
    for l_, ln in enumerate(wrap_rich(body_, 2.5, cw_ - 6)):
        pg._rich_line(cx0 + 3, 183 + l_ * 3.7, ln, 2.5)
pg.ox = pg.oy = 0

# ================================================================================================
# PART 0: THE BASICS
# ================================================================================================
m4lib.IDEA = 'THE BASICS'
m4lib.N_IDEA = 6
section('THE BASICS', 'The basics', 'Part 0', '0.1 to 0.6',
        'What the board is for, what the signal looks like, why there are two mid-rails, what an ADC measures, '
        'why the filter comes first and how to read a PCB. No board details yet.')

# 0.1 -------------------------------------------------------------------------------------------
pg = step('What the board is for',
          ['A piezoelectric sensor on a plant stem hears the clicks of **acoustic emission** (AE). The perfboard charge amplifier turns the charge of the sensor into a voltage.',
           'This board takes that voltage, filters it and measures it with a 14-bit ADC. It hands the numbers to the ZedBoard over SPI. It also raises a wake-up line when a click is strong.'])
chip(pg, label='CHAIN')
xs_ = [2, 36, 72, 108]
subs_ = [('Sensor', ['1.6 nF piezo', 'on the stem'], 'ext'), ('Perfboard', ['OPA1642 charge', 'amplifier, 9 V'], 'ctrl'),
         ('This board', ['filters, ADC,', 'wake-up'], 'arith'), ('ZedBoard', ['FPGA reads', 'SPI and nWAKE'], 'dev')]
for x_, (t_, s_, k_) in zip(xs_, subs_):
    pbox(pg, x_, 40, 30, 24, t_, s_, k_)
for a_ in (32, 66, 102):
    pg.arrow([(a_, 52), (a_ + 4, 52)])
lab(pg, 34, 36.5, 'charge')
lab(pg, 68, 36.5, '4.8 V + events')
lab(pg, 104, 36.5, 'SPI, nWAKE')
pg.text(70, 76, 'the gray box is the part that this manual describes', 2.5, MUTED, 'middle')

# 0.2 -------------------------------------------------------------------------------------------
evs = EV['events']
assert len(evs) == 7 and min(e['fpeak'] for e in evs) == 233 and max(e['fpeak'] for e in evs) == 275
vmin, vmax = min(e['vpp'] for e in evs), max(e['vpp'] for e in evs)
dmin, dmax = min(e['dur'] for e in evs), max(e['dur'] for e in evs)
quiet = sorted(b['inband'] for b in EV['baselines'])[:5]       # five of the eight records are quiet, three are not
nmin, nmax = min(quiet), max(quiet)
assert (nmin, nmax) == (3.7, 4.6)
pg = step('What the signal looks like',
          [f'The perfboard output rests near 4.8 V. An AE event rides on it as a burst between 233 and 275 kHz that lasts {dmin:.0f} to {dmax:.0f} µs. The seven recorded events are {vmin} to {vmax} mV peak to peak.',
           f'Between events, five of the eight baseline records show {nmin} to {nmax} mV rms of noise in the band. That noise sets the smallest event that this board can see.'])
chip(pg, label='7 RECORDED EVENTS')
X0, Y0, W_, H_ = 14, 36, 112, 40
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
fx = lambda f: X0 + (f - 220) / (290 - 220) * W_
vy = lambda v: Y0 + H_ - (v - 100) / (260 - 100) * H_
pg.rect(fx(230), Y0, fx(280) - fx(230), H_, LPK, 'none')
pg.text(fx(255), Y0 + 4.5, 'band 230 to 280 kHz', 2.5, PUR, 'middle', True)
for e in evs:
    pg.circle(fx(e['fpeak']), vy(e['vpp']), 1.5, AMB, INK, 0.3)
    pg.text(fx(e['fpeak']) + 2.2, vy(e['vpp']) + 0.9, e['event'], 2.5, INK, 'start', True)
for f_ in (220, 240, 260, 280):
    pg.text(fx(f_), Y0 + H_ + 4, f_, 2.5, MUTED, 'middle')
for v_ in (100, 150, 200, 250):
    pg.text(X0 - 1.5, vy(v_) + 0.9, v_, 2.5, MUTED, 'end')
pg.text(X0 + W_ / 2, Y0 + H_ + 8.4, 'peak frequency, kHz', 2.5, MUTED, 'middle')
pg.text(2, Y0 - 3, 'mV pp', 2.5, MUTED, 'start')

# 0.3 -------------------------------------------------------------------------------------------
pg = step('Why 2.5 V and 1.65 V',
          ['This board has no negative supply. A signal that swings below 0 V would be cut off. So each stage rests at the middle of its own supply, and the signal swings around that level.',
           'The op-amps run from 0 to 5 V, so they rest at **2.5 V**. The ADC runs from 0 to 3.3 V, so its inputs rest at **1.65 V**.'])
chip(pg, label='VOLTAGE LADDER')
rails = [(0.0, '0 V  ground', INK), (1.65, '1.65 V  VOCM, ADC inputs rest here', BLU), (2.5, '2.5 V  VMID5, op-amp stages rest here', PUR),
         (3.3, '3.3 V  AVDD, ADC reference', GRN), (4.8, '4.8 V  perfboard output rests here', MUTED), (5.0, '5.0 V  op-amp supply', GRN)]
ly = lambda v: 78 - v * 8.6
pg.line(20, ly(0), 20, ly(5.0), INK, 0.6)
for v_, t_, c_ in rails:
    pg.line(17, ly(v_), 24, ly(v_), c_, 0.8)
    off = {5.0: -1.0, 4.8: 3.0}.get(v_, 0.9)
    pg.text(27, ly(v_) + off, t_, 2.6, c_, 'start', True)
pg.text(2, ly(2.5) + 0.9, 'volts', 2.5, MUTED, 'start')

# 0.4 -------------------------------------------------------------------------------------------
pg = step('What an ADC measures',
          [f'The ADS7057 measures the **difference** between two pins, AINP and AINM. It reports the difference as a 14-bit signed number in two\'s complement. One step, called 1 LSB, is {LSB*1e3:.3f} mV.',
           'The full-scale range is plus and minus the supply AVDD, so ±3.3 V. The code 0x0000 means no difference.'])
chip(pg, label='CODE LADDER')
codes = [(-AVDD, '−3.3 V', '0x2000', 'negative full scale −8192'), (0.0, '0 V', '0x0000', 'mid code 0'), (AVDD, '+3.3 V', '0x1FFF', 'positive full scale +8191')]
yy = lambda v: 76 - (v + AVDD) / (2 * AVDD) * 38
pg.line(46, yy(-AVDD), 46, yy(AVDD), INK, 0.6)
for v_, vs, hx, nm in codes:
    pg.line(42, yy(v_), 50, yy(v_), INK, 0.8)
    pg.text(40, yy(v_) + 0.9, vs, 2.7, INK, 'end', True)
    pg.cell(54, yy(v_) - 2.6, 20, 5.2, hx, AMBT, PUR, 2.7, True)
    pg.text(77, yy(v_) + 0.9, nm, 2.6, MUTED, 'start')
v_ex = 1000 * LSB
pg.text(40, yy(0.5) + 0.9, f'1 LSB = {LSB*1e3:.3f} mV', 2.6, PUR, 'end', True)
assert abs(LSB * 16384 - 6.6) < 1e-9

# 0.5 -------------------------------------------------------------------------------------------
FS = 1.2e6
pg = step('Why filter before sampling',
          ['A sampled signal cannot tell a frequency f from FS − f. At 1.2 MSPS a tone at 800 kHz looks exactly like a tone at 400 kHz, inside the band of interest.',
           'So a low-pass filter must remove what lies above half the sample rate before the ADC sees it. The sample rate here is about 1.2 MSPS with a 25 MHz SPI clock (ESTIMATE).'])
chip(pg, label='ALIASING')
ax0, aw, ay = 8, 124, 70
fxs = lambda f: ax0 + f / 1.4e6 * aw
pg.line(ax0, ay, ax0 + aw, ay, INK, 0.5)
for f_ in (0, 0.2e6, 0.4e6, 0.6e6, 0.8e6, 1.0e6, 1.2e6, 1.4e6):
    pg.line(fxs(f_), ay, fxs(f_), ay + 1.5, INK, 0.3)
    pg.text(fxs(f_), ay + 5, f'{f_/1e3:g}', 2.5, MUTED, 'middle')
pg.text(ax0 + aw, ay + 9.6, 'kHz', 2.5, MUTED, 'end')
pg.rect(fxs(100e3), ay - 22, fxs(500e3) - fxs(100e3), 22, LPK, PUR, 0.3)
pg.text((fxs(100e3) + fxs(500e3)) / 2, ay - 25, 'wanted band', 2.5, PUR, 'middle', True)
pg.line(fxs(400e3), ay, fxs(400e3), ay - 15, GRN, 0.8)
pg.line(fxs(800e3), ay, fxs(800e3), ay - 15, RED, 0.8)
pg.text(fxs(800e3), ay - 17, 'noise at 800', 2.5, RED, 'middle', True)
pg.arrow([(fxs(800e3), ay - 10), (fxs(400e3) + 1, ay - 10)], RED, 0.5, '1.2,0.8')
pg.text(fxs(400e3), ay - 17, 'looks like 400', 2.5, GRN, 'middle', True)
pg.line(fxs(600e3), ay - 30, fxs(600e3), ay + 2, '#555', 0.35, '1.4,1.0')
pg.text(fxs(600e3) + 1.2, ay - 28, 'FS/2 = 600', 2.5, '#555', 'start')

# 0.6 -------------------------------------------------------------------------------------------
pg = step('How to read a PCB',
          ['The board has two copper layers. A **pad** holds a part. A **track** joins pads. A **via** is a plated hole that joins the two layers. A **pour** fills free space with copper, here ground.',
           'The **silkscreen** prints the names. The figure is a 20 × 8 mm cut of this board around the ADC.'])
chip(pg, label='REAL BOARD, 6 ×')
RX0, RY0, RX1, RY1 = 28.0, 17.0, 48.0, 25.0
S = 6.0
pg.rect(0, 0, (RX1 - RX0) * S, (RY1 - RY0) * S, '#e8f0e4', INK, 0.3)


def clip(x1, y1, x2, y2):
    t0, t1 = 0.0, 1.0
    dx, dy = x2 - x1, y2 - y1
    for p, q in ((-dx, x1 - RX0), (dx, RX1 - x1), (-dy, y1 - RY0), (dy, RY1 - y1)):
        if p == 0:
            if q < 0:
                return None
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
    if t0 > t1:
        return None
    return (x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy)


for t in BOARD['tracks']:
    c_ = clip(t['x1'], t['y1'], t['x2'], t['y2'])
    if c_:
        pg.line((c_[0] - RX0) * S, (c_[1] - RY0) * S, (c_[2] - RX0) * S, (c_[3] - RY0) * S, PUR if t['layer'] == 'F' else BLU, max(t['w'] * S, 0.4))
for ref, f in FP.items():
    for p in f['pads']:
        if RX0 <= p['x'] <= RX1 and RY0 <= p['y'] <= RY1:
            pg.rect((p['x'] - RX0 - p['w'] / 2) * S, (p['y'] - RY0 - p['h'] / 2) * S, p['w'] * S, p['h'] * S, AMB, INK, 0.15)
for v in BOARD['vias']:
    if RX0 <= v['x'] <= RX1 and RY0 <= v['y'] <= RY1:
        pg.circle((v['x'] - RX0) * S, (v['y'] - RY0) * S, v['d'] * S / 2, '#fff', GRN, 0.5)
        pg.circle((v['x'] - RX0) * S, (v['y'] - RY0) * S, v['drill'] * S / 2, INK)
u4 = FP['U4']
pg.text((u4['x'] - RX0) * S, (u4['y'] - RY0) * S - 7.5, 'U4', 3.0, INK, 'middle', True)
pg.text(5, 52.5, 'amber: pads    purple: top tracks    blue: bottom tracks    green ring: vias    pale green: ground pour', 2.5, MUTED, 'start')
