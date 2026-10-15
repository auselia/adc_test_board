"""Hardware manual, part F: section 9, the sensor head and the bias-T (steps 55 to 60)."""
import m4lib
from adc_common import *

sys.path.insert(0, os.path.join(REPO, 'hw', 'tools'))
import cost

CP = 1.6e-9                                   # piezo static capacitance, 1600 pF +-20 % (Steminc SMD05T04S311, AFE description 2.2)
GBW = 50e6                                    # DS: OPA365 gain-bandwidth
CF, RF = val('C34'), val('R28')
Q_LO, Q_HI = 4e-12, 7e-12                     # AFE description 2.2: peak charge of the seven events, after the model correction
SB = {}
for _l in open(os.path.join(REPO, 'sim', 'head_bias_t_results.txt')):
    m_ = re.match(r'\s*([a-z_0-9()]+)\s*=\s*([-\d.e+]+)', _l)
    if m_:
        SB[m_.group(1)] = float(m_.group(2))
assert abs(SB['loss_250k']) < 0.5 and SB['loss_10k'] < -15

section('THE SENSOR HEAD', 'The sensor head', 'Section 9', 'Steps 55 to 60',
        'The perfboard charge amplifier on its own small board, how it is powered through the coax by a '
        'bias-T, how it is laid out and how to test it.', active=['Input'])

# 55 --------------------------------------------------------------------------------------------
pg = step('What the sensor head does',
          ['The head is the perfboard on a PCB. The piezo wires solder to it. It turns the charge of the piezo into a voltage and sends that voltage down one coax cable.',
           'The same coax brings 5 V from the ADC board to the head. So the head needs one cable and no battery.'])
chip(pg, label='CHAIN')
bx_ = [(2, 'Piezo', ['1.6 nF'], 'ext'), (30, 'Head', ['charge amp', 'U8'], 'ctrl'), (58, 'Coax', ['5 V down', 'signal up'], 'bus'),
       (86, 'SENSOR IN', ['bias-T', 'J1'], 'arith'), (114, 'Filters', ['and ADC'], 'mem')]
for x_, t_, s_, k_ in bx_:
    pbox(pg, x_, 44, 24, 16, t_, s_, k_)
for x_ in (26, 54, 82, 110):
    pg.arrow([(x_, 52), (x_ + 4, 52)])
pg.text(70, 72, f'The head loses {abs(SB["loss_250k"]):.2f} dB at 250 kHz to the bias-T. To use a generator or a perfboard instead, cut the solder jumper JP1.', 2.5, MUTED, 'middle')

# 56 --------------------------------------------------------------------------------------------
gn = 1 + CP / CF
pg = step('How the charge becomes a voltage',
          [f'The amplifier keeps its input at a fixed voltage. So the charge Q of the piezo flows into the feedback capacitor Cf, and the output moves by Q / Cf. With Cf = {CF*1e12:.0f} pF, a charge of {Q_LO*1e12:.0f} to {Q_HI*1e12:.0f} pC gives {Q_LO/CF*1e3:.0f} to {Q_HI/CF*1e3:.0f} mV.',
           f'Rf = {RF/1e6:.0f} MΩ drains the capacitor with a time constant of {RF*CF*1e6:.0f} µs, a corner at {1/(2*math.pi*RF*CF)/1e3:.1f} kHz. The noise gain is {gn:.0f}, so the 50 MHz amplifier keeps {GBW/gn/1e6:.1f} MHz of bandwidth.'])
chip(pg, label='FROM THE NETLIST, ESTIMATE FOR Q')
pp, pm, po = opamp(pg, 52, 76, 18, 16, 'U8')
pg.line(pm[0], pm[1], 24, pm[1], INK, 0.5)
pg.line(24, pm[1], 24, 46, INK, 0.5)
pg.line(24, 46, 94, 46, INK, 0.5)
res_h(pg, 52, 46, 14, 'R28', '1 MΩ')
pg.line(24, 56, 94, 56, INK, 0.5); pg.line(24, 46, 24, 56, INK, 0.5)
cap_h(pg, 60, 56, 10, 'C34', '47 pF', INK, above=False)
pg.line(94, 46, 94, 76, INK, 0.5); pg.line(po[0], po[1], 94, 76, INK, 0.5)
pg.line(94, 76, 104, 76, INK, 0.5); pg.text(106, 77, 'out', 2.5, INK, 'start', True)
pg.line(pp[0], pp[1], 44, pp[1], INK, 0.5); pg.line(44, pp[1], 44, 86, INK, 0.5)
pg.text(46, 88, f'VREF {SB["v(vref)"]:.1f} V', 2.4, INK, 'start', True)
pg.rect(8, 70, 10, 8, AMBT, INK, 0.4)
pg.text(13, 75.4, 'Cp', 2.6, INK, 'middle', True)
pg.line(13, 78, 13, 82, INK, 0.5); gnd(pg, 13, 82)
pg.line(13, 70, 13, pm[1], INK, 0.5); pg.line(13, pm[1], 24, pm[1], INK, 0.5)

# 57 --------------------------------------------------------------------------------------------
L_ = val('L1')
zl = 2 * math.pi * 250e3 * L_
pg = step('How the coax carries power and signal',
          [f'A bias-T joins a DC path and an AC path on one wire. The DC path is an inductor: {L_*1e6:.0f} µH looks like {zl:.0f} Ω at 250 kHz, so it hardly loads the signal. The AC path is a capacitor: 100 nF passes 250 kHz and blocks the DC.',
           f'The simulation with the OPA365 model gives a loss of {abs(SB["loss_250k"]):.2f} dB at 250 kHz and {abs(SB["loss_10k"]):.0f} dB at 10 kHz. The low-frequency noise of the perfboard is cut before it reaches the filters.'])
chip(pg, label='SIMULATION, RG174 1 M')
yL = 66
pg.line(30, yL, 100, yL, INK, 0.6)
pg.text(65, yL + 5, 'coax, centre conductor', 2.3, MUTED, 'middle')
pbox(pg, 2, yL - 8, 20, 16, 'Head', ['U8'], 'ctrl')
pg.line(22, yL, 30, yL, INK, 0.6)
pbox(pg, 106, yL - 8, 26, 16, 'SIG_IN', ['to HPF'], 'mem')
pg.line(100, yL, 106, yL, INK, 0.6)
pg.text(34, 41, f'L1 {L_*1e6:.0f} µH', 2.5, INK, 'start', True)
pg.line(46, yL, 46, 56, INK, 0.5); pg.rect(43.5, 52, 5, 4, '#fff', INK, 0.5)
pg.line(46, 52, 46, 46, INK, 0.5); pg.text(50, 45.6, f'V+ of U8, about {SB["v(v5h)"]:.1f} V', 2.4, INK, 'start', True)
pg.text(76, 41, f'L2 {val("L2")*1e6:.0f} µH', 2.5, INK, 'start', True)
pg.line(84, yL, 84, 56, INK, 0.5); pg.rect(81.5, 52, 5, 4, '#fff', INK, 0.5)
pg.line(84, 52, 84, 46, INK, 0.5); pg.line(84, 46, 98, 46, INK, 0.5)
res_h(pg, 98, 46, 12, 'R26', '47 Ω')
pg.line(110, 46, 114, 46, INK, 0.5); pg.text(116, 47, '+5 V', 2.5, INK, 'start', True)
cap_h(pg, 32, yL, 6, 'C38', '100 nF', INK, above=False)
cap_h(pg, 90, yL, 6, 'C33', '100 nF', INK, above=False)
pg.text(65, 86, f'L1 and L2 are the same part. Cut the solder jumper JP1 (between C32 and L2) to turn the 5 V off.', 2.3, MUTED, 'middle')

# 58 --------------------------------------------------------------------------------------------
refs_h = sorted(HFP)
pg = step('Where the parts are on the head',
          [f'The head is {HW_:.0f} × {HH_:.0f} mm, with {len(HFP)} parts, all on one face. The piezo sits on the other face, flat against the pads. The SMA stands on the parts face and points out of the capsule.',
           'The capsule drawing v3 has a PCB of 10 × 20 mm. With the SMA and the inductor the head needs 2 mm more, so the PCB sticks out 9 mm instead of 7.'])
chip(pg, label='REAL BOARD, TOP VIEW, 2.2 : 1')
K_ = 2.2
bx, by = 4, 37
pg.rect(bx, by, HW_ * K_, HH_ * K_, '#e8f0e4', INK, 0.4)
col_ = {'U': PUR, 'L': GRN, 'J': '#8a8a8a', 'T': AMB, 'R': '#c47bb8', 'C': BLU}
for ref, f in HFP.items():
    x0, y0, x1, y1 = f['bbox']
    pg.rect(bx + max(x0, 0) * K_, by + max(y0, 0) * K_, (min(x1, HW_) - max(x0, 0)) * K_, (min(y1, HH_) - max(y0, 0)) * K_, col_.get(ref[0], '#bbb'), INK, 0.15, 0.3)
for ref in ('U8', 'L1', 'J6', 'TP1', 'TP2'):
    f = HFP[ref]
    pg.text(bx + f['x'] * K_, by + f['y'] * K_ + 0.9, ref, 2.0, '#fff' if ref in ('U8', 'J6') else INK, 'middle', True)
leg = [('U8', 'OPA365, charge amplifier'), ('L1', '470 µH, supply from the coax'), ('TP1', 'piezo +, summing node'), ('TP2', 'piezo −, ground'), ('J6', 'SMA, vertical'),
       ('R28 C34', 'Rf 1 MΩ, Cf 47 pF'), ('R29 R30 C35', f'VREF {SB["v(vref)"]:.1f} V'), ('C36 C37', 'supply bypass'), ('R31 C38', '49.9 Ω and 100 nF out')]
for i, (a_, b_) in enumerate(leg):
    pg.text(bx + HW_ * K_ + 6, 41 + i * 5.2, a_, 2.4, CANOPY, 'start', True)
    pg.text(bx + HW_ * K_ + 30, 41 + i * 5.2, b_, 2.4, INK, 'start')

# 59 --------------------------------------------------------------------------------------------
hrows = list(csv.DictReader(open(os.path.join(REPO, 'hw', 'fab', 'ADC_Head_BOM_JLC.csv'))))
hq = cost.quote(5, board='head')
pg = step('What goes to the factory for the head',
          [f'The head has its own Gerber zip, BOM and CPL. It is {len(hrows)} BOM lines and {sum(len(r["Designator"].split(",")) for r in hrows)} parts. The OPA365 and the inductor come from the extended library.',
           f'Five heads cost about ${hq["goods"]:.2f} at the factory, ${hq["goods"]/5:.2f} each (ESTIMATE). Fixed fees are most of it: setup, stencil and hand soldering of the SMA.'])
chip(pg, label='HEAD BOM, PRICE PER PART')
rows = [['Ref', 'Part', 'LCSC', 'Price']]
for r in hrows:
    l = r['LCSC Part #']
    rows.append([r['Designator'], r['Comment'], l, f'${cost.PRICE[l]:.3f}'])
table_ = None
rh = 4.6
for i, row in enumerate(rows):
    yy = 37 + i * rh
    if i == 0:
        pg.rect(4, yy, 126, rh, '#e6ece4', 'none', 0)
    pg.line(4, yy + rh, 130, yy + rh, '#bbb', 0.15)
    for xx, c_ in zip((5, 34, 80, 108), row):
        pg.text(xx, yy + rh / 2 + 0.8, c_, 2.3, INK, 'start', i == 0)

# 60 --------------------------------------------------------------------------------------------
ihead = 4.7e-3                                  # ngspice, OPA365 model (head_bias_t_results.txt, i(v5) minus the reference amplifier)
pg = step('How to test the head',
          ['Power the ADC board from 5 V (USB-C or header) and connect the head to SENSOR IN (J1) with the coax. Measure the head first, then inject a known charge. A 10 pF capacitor from the function generator to the piezo + pad gives Q = 10 pF × ΔV.',
           f'A step of 100 mV injects 1 pC. The output moves by {1e-12/CF*1e3:.0f} mV, because Q / Cf = 1 pC / {CF*1e12:.0f} pF.'])
chip(pg, label='EXPECTED VALUES')
rows = [['Where', 'Expect'],
        ['C37 (V+ of U8)', f'about {SB["v(v5h)"]:.1f} V'],
        ['VREF, C35', f'about {SB["v(vref)"]:.1f} V after 0.2 s'],
        ['U8 output, R31 pad 1', 'equal to VREF'],
        ['J1 centre pin', f'about {SB["v(lh)"]:.1f} V'],
        ['Extra current on the 5 V input', f'about {ihead*1e3:.0f} mA'],
        ['100 mV step via 10 pF', f'{1e-12/CF*1e3:.0f} mV step at SIG_IN']]
for i, row in enumerate(rows):
    yy = 38 + i * 6.2
    if i == 0:
        pg.rect(4, yy, 126, 6.2, '#e6ece4', 'none', 0)
    pg.line(4, yy + 6.2, 130, yy + 6.2, '#bbb', 0.15)
    pg.text(5, yy + 4.4, row[0], 2.6, INK, 'start', i == 0)
    pg.text(70, yy + 4.4, row[1], 2.6, INK, 'start', i == 0)

# head views page (after step 60) ---------------------------------------------------------------
m4lib._finish_page()
pg = new_page('head view')
chrome(pg, len(pages), 'Step 58  /  the sensor head  /  rendered views', divider=False)
IWH, IHH = 13.98, 25.99                 # mm covered by the top and back renders (board 10 x 22 plus 2 mm all round)
KH = 3.6
pg.text(24 + IWH * KH / 2, 24, 'FRONT, THE PARTS FACE', 2.6, MUTED, 'middle', True, mono=True)
pg.text(24 + IWH * KH + 8 + IWH * KH / 2, 24, 'BACK, THE PIEZO FACE', 2.6, MUTED, 'middle', True, mono=True)
image(pg, os.path.join(REPO, 'doc', 'assets', 'head_top.png'), 24, 28, IWH * KH, IHH * KH)
image(pg, os.path.join(REPO, 'doc', 'assets', 'head_back.png'), 24 + IWH * KH + 8, 28, IWH * KH, IHH * KH)
pg.text(24 + IWH * KH + 4, 28 + IHH * KH + 6, f'Both at 3.6 : 1, board {HW_:.0f} × {HH_:.0f} mm. The + pad is the centre of the piezo.', 2.6, MUTED, 'middle')
from PIL import Image as _I
_w, _h = _I.open(os.path.join(REPO, 'doc', 'assets', 'head_angled.jpg')).size
AW = 92.0
image(pg, os.path.join(REPO, 'doc', 'assets', 'head_angled.jpg'), 168, 28, AW, AW * _h / _w)
pg.text(168 + AW / 2, 28 + AW * _h / _w + 6, 'Seen at an angle, from the parts face.', 2.6, MUTED, 'middle')
image(pg, os.path.join(REPO, 'doc', 'assets', 'head_top.png'), 168, 28 + AW * _h / _w + 14, IWH, IHH)
pg.text(168 + IWH + 3, 28 + AW * _h / _w + 14 + IHH / 2, 'Real size, 1 : 1', 2.6, INK, 'start', True)
