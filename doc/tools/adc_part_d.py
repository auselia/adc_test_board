"""Hardware manual, part D: section 5 (the wake-up, steps 31 to 35) and section 6 (the board, steps 36 to 44)."""
import m4lib
from adc_common import *

LPF_GAIN = at(SIM['lpf'], 250e3)             # LPF_OUT per volt at J1, 250 kHz (50 ohm source included)
MON_GAIN = at(SIM['mon'], 250e3)
CF_HEAD = val('C34')                         # head feedback capacitor: charge = volts x Cf
HP_L = 1 / (2 * math.pi * val('R35') * val('C40'))           # listener high-pass corner
LP_L = 1 / (2 * math.pi * val('R36') * val('C41'))           # listener low-pass corner

# ================================================================================================
# SECTION 5: THE LISTENER
# ================================================================================================
section('THE LISTENER', 'The listener', 'Section 5', 'Steps 31 to 35',
        'How a small circuit next to the capture chain raises WAKE_N and BIG_N when a burst arrives, how the thresholds '
        'are set by one resistor chain and how to test them on the bench.', active=['Wake-up', 'Input', 'SPI port'])

# 31 --------------------------------------------------------------------------------------------
pg = step('What the listener does',
          [f'The listener is a second, very small circuit that watches SIG_IN, the same signal the chain sees. A 100 pF and 10 kΩ high-pass ({HP_L/1e3:.0f} kHz) and a 10 kΩ and 22 pF low-pass ({LP_L/1e3:.0f} kHz) keep only the AE band. The two filters pass {LST_GAIN:.2f} of the signal at 250 kHz. Two comparators judge the result.',
           'It is an **observer**. It never switches the capture chain. The chain stays on, so the FPGA has the full waveform and the listener decisions side by side. Both outputs are open-drain lines on the PMOD: WAKE_N for a medium burst and BIG_N for a large one.'])
chip(pg, label='LISTENER, SIG_IN TO PMOD')
xs_ = [2, 36, 70, 104]
bx_ = [('SIG_IN', ['from J1', 'after C33'], 'ext'), ('Filters', ['C40 R35', 'R36 C41'], 'arith'), ('LST', ['TP15,', 'rests 1.65 V'], 'ctrl'), ('U6, U9', ['TLV7022', '2 × 2 comp.'], 'mem')]
for x_, (t_, s_, k_) in zip(xs_, bx_):
    pbox(pg, x_, 42, 30, 20, t_, s_, k_)
for a_ in (32, 66, 100):
    pg.arrow([(a_, 52), (a_ + 4, 52)])
pg.text(104 + 15, 70, 'WAKE_N pin 10', 2.5, INK, 'middle', True)
pg.text(104 + 15, 75, 'BIG_N pin 7', 2.5, INK, 'middle', True)
pg.text(70, 86, 'comparator inputs are LST against the ladder of step 32', 2.5, MUTED, 'middle')
assert ('C40', '1') in NET['SIG_IN'] and ('U6', '2') in NET['LST'] and ('U9', '2') in NET['LST']

# 32 --------------------------------------------------------------------------------------------
pg = step('How the thresholds are set',
          ['One resistor chain from 3.3 V to ground makes all four thresholds. Its middle node REFL rests at 1.65 V. Each comparator pair looks at LST against a node above REFL and a node below it, so it trips for a burst of either polarity.',
           ('tex', r'V_{\mathrm{half}} = I \cdot R, \qquad I = \frac{3.3\,\mathrm{V}}{2.096\,\mathrm{M\Omega}} = 1.57\,\mu\mathrm{A}', 9.0),
           f'The window at LST is divided by the filter gain {LST_GAIN:.2f} to refer it to SIG_IN, then converted to charge with Cf = {CF_HEAD*1e12:.0f} pF.'])
chip(pg, label='THRESHOLDS, FROM THE RESISTORS')
hdr = ['Output', 'Resistors', 'At LST', 'At SIG_IN', 'Charge, Cf 47 pF']
rows = [hdr,
        ['WAKE_N (U6)', 'R39, R40 15 kΩ', f'{L_WAKE*1e3:.0f} mV', f'{L_WAKE_IN*1e3:.0f} mV', f'{L_WAKE_IN*CF_HEAD*1e12:.1f} pC'],
        ['BIG_N (U9)', 'R22 + R39, 48 kΩ', f'{L_BIG*1e3:.0f} mV', f'{L_BIG_IN*1e3:.0f} mV', f'{L_BIG_IN*CF_HEAD*1e12:.1f} pC']]
for i, row in enumerate(rows):
    yy = 42 + i * 7.4
    if i == 0:
        pg.rect(2, yy, 134, 7.4, '#e6ece4', 'none', 0)
    pg.line(2, yy + 7.4, 136, yy + 7.4, '#bbb', 0.15)
    for xx, c_ in zip((4, 32, 68, 90, 112), row):
        pg.text(xx, yy + 5.2, c_, 2.6, INK, 'start', i == 0)
pg.text(4, 74, 'Chain: R21 1 MΩ, R22 33 kΩ, R39 15 kΩ, REFL, R40 15 kΩ, R41 33 kΩ, R23 1 MΩ.', 2.5, MUTED, 'start')
pg.text(4, 80, 'With the low-power head (OPA314, Cf 220 pF) the volts per pC fall by 4.7. The thresholds then sit near the comparator offset and need the ladder changed (plan, section 13).', 2.5, MUTED, 'start')

# 33 --------------------------------------------------------------------------------------------
pg = step('Why WAKE_N and BIG_N are open-drain',
          ['The TLV7022 output stage is one transistor. It can pull the output to ground. It cannot drive it high. A 47 kΩ resistor (R24 for WAKE_N, R42 for BIG_N) pulls the line up to 3.3 V.',
           'The two comparators of one package share one wire, so either one pulls the line low. The FPGA sees a clean 3.3 V level and never more.'])
chip(pg, label='WIRED-OR')
pg.text(20, 40, '+3.3 V from the PMOD', 2.6, GRN, 'start', True)
pg.line(40, 42, 40, 46, INK, 0.45)
res_v(pg, 40, 46, 10, 'R24', '47 kΩ')
dot(pg, 40, 62)
pg.line(40, 56, 40, 62, INK, 0.45)
pg.line(40, 62, 76, 62, INK, 0.5)
pg.arrow([(70, 62), (76, 62)])
pg.text(78, 63, 'WAKE_N', 2.6, INK, 'start', True)
pg.text(78, 68, 'PMOD pin 10', 2.4, MUTED, 'start')
for k_, xx in enumerate((20, 56)):
    pg.line(xx, 62, xx, 66, INK, 0.45)
    pg.rect(xx - 7, 66, 14, 8, '#fff', INK, 0.5, 1.2)
    pg.text(xx, 71.4, ('OUTA', 'OUTB')[k_], 2.5, INK, 'middle', True)
    pg.line(xx, 74, xx, 78, INK, 0.45)
    gnd(pg, xx, 78)
dot(pg, 20, 62); dot(pg, 56, 62)
pg.text(100, 44, 'OUTA  OUTB  WAKE_N', 2.5, MUTED, 'start', True)
for k_, (a_, b_, c_) in enumerate((('off', 'off', 'high'), ('on', 'off', 'low'), ('off', 'on', 'low'), ('on', 'on', 'low'))):
    pg.text(100, 50 + k_ * 5.5, a_, 2.5, INK, 'start'); pg.text(112, 50 + k_ * 5.5, b_, 2.5, INK, 'start'); pg.text(124, 50 + k_ * 5.5, c_, 2.5, INK, 'start', True)
assert ('R24', '2') in NET['WAKE_N'] and ('R42', '2') in NET['BIG_N'] and ('U6', '1') in NET['WAKE_N'] and ('U6', '7') in NET['WAKE_N']

# 34 --------------------------------------------------------------------------------------------
pg = step('How fast and how accurate',
          [f'The TLV7022 answers in about 260 ns and draws 5 µA per channel. Its input offset is up to ±8 mV and it adds about 7 mV of hysteresis. Against a half window of {L_WAKE*1e3:.0f} mV at LST that is a third, so treat each threshold as ±8 mV at LST, about ±{0.008/LST_GAIN*1e3:.0f} mV at SIG_IN.',
           f'Real data decide the setting. On the 25 recorded captures the noise after the 100 kHz high-pass is 4.0 mV rms (worst 9.2 mV). The largest of the 18 noise captures peaks at 26 mV, under the {L_WAKE_IN*1e3:.0f} mV of WAKE_N at SIG_IN, a margin of only {L_WAKE_IN*1e3/26.1:.1f}×. The 7 true events peak at 52 to 188 mV, all above it (ESTIMATE, scaled to Cf 47 pF).'])
chip(pg, label='THRESHOLD AGAINST DATA, MV AT THE HEAD')
bars_ = [('noise rms, worst', 9.15, '#8c8c8c'), ('largest noise peak', 26.1, RED), ('WAKE_N at SIG_IN', L_WAKE_IN * 1e3, BLU),
         ('smallest true event', 52.0, PUR), ('BIG_N at SIG_IN', L_BIG_IN * 1e3, BLU), ('largest true event', 188.0, PUR)]
for k_, (nm, v_, c_) in enumerate(bars_):
    y_ = 40 + k_ * 7.4
    pg.text(2, y_ + 5.0, nm, 2.6, INK, 'start', True)
    pg.rect(48, y_, v_ / 200 * 80, 5.6, c_, 'none', 0)
    pg.text(48 + v_ / 200 * 80 + 2, y_ + 5.0, f'{v_:.0f} mV', 2.6, INK, 'start', True)

# 35 --------------------------------------------------------------------------------------------
v_w, v_b = L_WAKE_IN, L_BIG_IN
pg = step('How to test the listener',
          [f'Feed a 250 kHz burst of ten cycles to J1 and watch TP15 (LST), TP16 (WAKE_N) and TP17 (BIG_N). At 20 mV the lines must stay high. At {1.6*v_w*1e3:.0f} mV WAKE_N must drop. At {1.4*v_b*1e3:.0f} mV both must drop. TP18 (REFL) must read 1.65 V all the time.',
           'These amplitudes are at J1. The amplitudes are at SIG_IN, which J1 reaches through C33. Expect each threshold within about ±12 mV because of the comparator offset. WAKE_N and BIG_N stay low only for the length of the burst.'])
chip(pg, label='BENCH STEPS')
steps_ = [('1', 'TP18 REFL reads 1.65 V, TP16 and TP17 read 3.3 V'), ('2', 'Feed 250 kHz, 20 mV: both lines stay high'),
          ('3', f'Feed {1.6*v_w*1e3:.0f} mV: WAKE_N drops, BIG_N stays high'), ('4', f'Feed {1.4*v_b*1e3:.0f} mV: both drop'),
          ('5', 'Remove the burst: both lines return high')]
for k_, (n_, t_) in enumerate(steps_):
    y_ = 40 + k_ * 8.6
    pg.circle(8, y_ + 3.2, 3.2, AMBT, INK, 0.35)
    pg.text(8, y_ + 4.3, n_, 2.8, INK, 'middle', True)
    pg.text(15, y_ + 4.2, t_, 2.9, INK, 'start', True)

# ================================================================================================
# SECTION 6: THE BOARD
# ================================================================================================
section('THE BOARD', 'The board', 'Section 6', 'Steps 36 to 44',
        'The stack, the floor plan, where every part sits, how the tracks and the power are routed, '
        'what the silkscreen says and which footprints need care.', active=['Input', 'High-pass', 'Gain', 'Low-pass', 'Driver', 'ADC', 'SPI port', 'Wake-up', 'Power'])

n_top = sum(1 for t in BOARD['tracks'] if t['layer'] == 'F'); n_bot = sum(1 for t in BOARD['tracks'] if t['layer'] == 'B')
n_via = len(BOARD['vias']); n_gvia = sum(1 for v in BOARD['vias'] if v['net'] == 'GND')
widths = {}
for t in BOARD['tracks']:
    widths[t['w']] = widths.get(t['w'], 0) + 1
assert set(widths) <= {0.15, 0.2, 0.35}, widths
w15, w20 = widths.get(0.15, 0), widths.get(0.2, 0)
n_via5 = sum(1 for v in BOARD['vias'] if v['d'] < 0.55)

# 36 --------------------------------------------------------------------------------------------
pg = step('The stack and the size',
          [f'The main board is {BW:.0f} × {BH:.1f} mm with two copper layers on 1.6 mm FR-4. Both layers carry a ground pour. {n_gvia} of the {n_via} vias are ground stitching vias that tie the two pours together.',
           f'The board has {n_top + n_bot} track segments. {w20} are 0.2 mm wide and {w15} are 0.15 mm, near the fine-pitch pads. Vias are 0.6 mm with a 0.3 mm drill.'])
chip(pg, label='FROM THE BOARD FILE')
layers_ = [('top copper', 'F.Cu', f'{n_top} track segments, all parts, ground pour', PUR, 9),
           ('FR-4, 1.6 mm', '', 'fibreglass epoxy', '#d8cfa9', 16),
           ('bottom copper', 'B.Cu', f'{n_bot} track segments, ground pour', BLU, 9)]
y_ = 40
for nm, tag, desc, c_, h_ in layers_:
    pg.rect(4, y_, 62, h_, c_, 'none', 0)
    pg.text(70, y_ + h_ / 2 + 0.9, f'{nm}  {desc}', 2.6, INK, 'start', True)
    y_ += h_ + 1.2
pg.rect(30, 40, 4, 36, '#fff', GRN, 0.5)
pg.text(36, 80, 'via', 2.5, GRN, 'middle', True)

# 37 --------------------------------------------------------------------------------------------
pg = step('How the floor is planned',
          [f'The board is a narrow strip, {BW:.0f} × {BH:.1f} mm, so that boards fit on adjacent PMOD ports, about 22.7 mm apart. The signal runs from the SMA connectors on the left to the PMOD on the right.',
           'The top row holds the bias-T, the high-pass, the gain, the low-pass and the mid-rail. The bottom row holds the listener, the driver, the ADC input filter and the ADC. The power links and the header J7 sit next to the PMOD.'])
chip(pg, label='TOP VIEW, COLORS BY BLOCK')
k = 0.95
bx, by = 4, 36
pg.rect(bx, by, BW * k, BH * k, '#f8f8f4', INK, 0.5, 1)
for ref, f in FP.items():
    x0, y0, x1, y1 = f['bbox']
    c_ = BLOCK_COLOR[BLOCK_OF[ref]]
    pg.rect(bx + max(x0, 0) * k, by + max(y0, 0) * k, (min(x1, BW) - max(x0, 0)) * k, (min(y1, BH) - max(y0, 0)) * k, c_, INK, 0.12, 0.3)
names = [b for b in BLOCKS if b[0] != 'Holes']
for i, (nm, c_, rs) in enumerate(names):
    col_, row_ = i // 6, i % 6
    xx = bx + col_ * 46
    yy = by + BH * k + 4 + row_ * 4.0
    pg.rect(xx, yy, 3.0, 3.0, c_, INK, 0.2)
    pg.text(xx + 4.6, yy + 2.5, nm, 2.3, INK, 'start')

# 38 --------------------------------------------------------------------------------------------
n_tht = sum(1 for f in FP.values() if any(p['tht'] for p in f['pads']) and not f['fp'].startswith('Mounting'))
n_hole = sum(1 for r in FP if r.startswith('H'))
n_tp = sum(1 for r in FP if r.startswith('TP'))
n_jp = sum(1 for r in FP if r.startswith('JP'))
n_smd = len(FP) - n_tht - n_hole - n_tp - n_jp        # the solder jumpers are copper only
pg = step('Where every part is',
          [f'The table lists the blocks, the references and the count. The main board has {len(FP)} footprints: {n_smd} surface-mount parts, {n_tht} through-hole parts and {n_hole} mounting holes and {n_tp} test points, plus {n_jp} solder jumpers (JP1 to JP6) that are copper only.',
           'Every part has a place in exactly one block, and the same reference appears in the schematic, the BOM and the placement file.'])
chip(pg, label='BLOCKS, REFERENCES')
tot_ = 0
for i, (nm, c_, rs) in enumerate(BLOCKS):
    col, row = i // 8, i % 8
    x_, y_ = 2 + col * 68, 38 + row * 6.7
    pg.rect(x_, y_, 3.6, 3.6, c_, INK, 0.2)
    refs = ' '.join(sorted(rs, key=lambda r: (r[0], int(re.sub(r'\D', '', r) or 0))))
    pg.text(x_ + 5.4, y_ + 3.0, nm, 2.4, INK, 'start', True)
    pg.text(x_ + 5.4, y_ + 6.0, refs if len(refs) < 44 else refs[:42] + '…', 2.2, MUTED, 'start')
    tot_ += len(rs)
assert tot_ == len(FP)

# 39 --------------------------------------------------------------------------------------------
RX0, RY0, RX1, RY1 = FP['U4']['x'] - 7.0, FP['U4']['y'] - 5.5, FP['U4']['x'] + 7.0, FP['U4']['y'] + 5.5
S = 4.6
nets_hi = {'AINP': PUR, 'AINM': BLU}
dAINP, dAINM = net_length('AINP'), net_length('AINM')
pg = step('Why the ADC corner is built this way',
          [f'Everything that touches the ADC input sits around U4: the two 10 Ω resistors, the four 100 pF capacitors, the supply capacitors and the three 22 Ω resistors. The tracks AINP and AINM are {dAINP:.0f} and {dAINM:.0f} mm long.',
           f'A length difference of {abs(dAINP-dAINM):.0f} mm is harmless here. A 5 mm track delays a signal by about 30 ps, and a 500 kHz wave lasts 2 µs.'])
chip(pg, label='REAL BOARD, ADC CORNER')
pg.rect(0, 0, (RX1 - RX0) * S, (RY1 - RY0) * S, '#e8f0e4', INK, 0.3)
def clipw(x1, y1, x2, y2):
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
    c_ = clipw(t['x1'], t['y1'], t['x2'], t['y2'])
    if c_:
        col_ = nets_hi.get(t['net'], '#c9c4d6' if t['layer'] == 'F' else '#b6c8dc')
        pg.line((c_[0] - RX0) * S, (c_[1] - RY0) * S, (c_[2] - RX0) * S, (c_[3] - RY0) * S, col_, max(t['w'] * S, 0.4))
adc_refs = ['U4', 'R16', 'R17', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C22', 'R18', 'R19', 'R20']
for ref, f in FP.items():
    for p in f['pads']:
        if RX0 <= p['x'] <= RX1 and RY0 <= p['y'] <= RY1:
            pg.rect((p['x'] - RX0 - p['w'] / 2) * S, (p['y'] - RY0 - p['h'] / 2) * S, p['w'] * S, p['h'] * S, AMB if ref in adc_refs else '#d6d6d0', INK, 0.12)
for ref in adc_refs:
    f = FP[ref]
    if RX0 + 0.5 < f['x'] < RX1 - 0.5 and RY0 + 0.5 < f['y'] < RY1 - 0.5:
        pg.text((f['x'] - RX0) * S, (f['y'] - RY0) * S + 1.0, ref, 2.4, INK, 'middle', True)

# 40 --------------------------------------------------------------------------------------------
sel = ['SIG_IN', 'HPF_OUT', 'GAIN_OUT', 'LPF_OUT', 'DRV_OUTP', 'DRV_OUTN', 'AINP', 'AINM', 'SCLK', 'CS', 'SDO', 'WAKE_N']
lens = {n: net_length(n) for n in sel}
vcount = {n: sum(1 for v in BOARD['vias'] if v['net'] == n) for n in sel}
pg = step('How the analog tracks are routed',
          [f'The longest analog net is LPF_OUT at {lens["LPF_OUT"]:.0f} mm, because it feeds the SCOPE OUT connector and the driver. All other analog nets are under {sorted(lens.values())[-2]:.0f} mm.',
           'The router chose the paths, and the board is small enough that none of them matters at 500 kHz. The figure lists the lengths.'])
chip(pg, label='NET LENGTH, mm')
mxl = max(lens.values())
for i, n_ in enumerate(sel):
    col, row = i // 6, i % 6
    x_, y_ = 2 + col * 68, 40 + row * 7.6
    pg.text(x_, y_ + 4.6, n_, 2.5, INK, 'start', True)
    pg.rect(x_ + 26, y_, lens[n_] / mxl * 28, 5.6, PUR if n_ not in ('SCLK', 'CS', 'SDO', 'WAKE_N') else '#8c8c8c', 'none', 0)
    pg.text(x_ + 26 + lens[n_] / mxl * 28 + 1.6, y_ + 4.6, f'{lens[n_]:.0f}', 2.5, INK, 'start', True)

# 41 --------------------------------------------------------------------------------------------
pw = ['+3V3', '+3V3_C', '+3V3_L', 'AVDD', 'VMID5', 'VOCM']
plen = {n: net_length(n) for n in pw}
rho, thick = 1.7e-8, 35e-6
drop5 = rho * plen['+3V3_C'] * 1e-3 / (0.2e-3 * thick) * (I_BAT_A := 0.027)
pg = step('How power and ground are routed',
          [f'Ground is a pour on both layers, tied by {n_gvia} vias, so every ground pad finds a short path. The power nets are 0.2 mm tracks, because the currents are small.',
           f'The +3V3_C net is {plen["+3V3_C"]:.0f} mm of track in total. With 27 mA (22 mA, plus 5 mA for the sensor head) this drops about {drop5*1e3:.0f} mV across its whole length (ESTIMATE, worst case).'])
chip(pg, label='POWER NET LENGTH, mm')
mxp = max(plen.values())
for i, n_ in enumerate(pw):
    y_ = 40 + i * 6.8
    pg.text(2, y_ + 4.6, n_, 2.6, INK, 'start', True)
    pg.rect(26, y_, plen[n_] / mxp * 80, 5.6, GRN, 'none', 0)
    pg.text(26 + plen[n_] / mxp * 80 + 2, y_ + 4.6, f'{plen[n_]:.0f}', 2.6, INK, 'start', True)

# 42 --------------------------------------------------------------------------------------------
pg = step('What each label on the silkscreen means',
          ['The front carries the labels that a user needs: SENSOR IN and SCOPE OUT. The names of the parts (R16, C29 and so on) are not on the silkscreen, because the board is dense. They are in the KiCad file and in the 1:1 print.',
           'The back carries the name of each test point and each solder jumper, the Auselia logo, the PMOD pin list and the title.'])
chip(pg, label='FRONT SIDE')
k = 1.02
bx, by = 4, 38
pg.rect(bx, by, BW * k, BH * k, '#f8f8f4', INK, 0.5, 1)
marks = [('SENSOR IN', 5.4, 1.2, 1), ('SCOPE OUT', 5.4, 20.7, 2), ('test points', 40.0, 8.0, 3), ('jumpers', 108.0, 8.0, 4), ('PMOD', 118.0, 12.0, 5)]
for nm, x_, y_, n_ in marks:
    pg.circle(bx + x_ * k + 7, by + y_ * k + 2.5, 2.2, AMBT, INK, 0.3)
    pg.text(bx + x_ * k + 7, by + y_ * k + 3.4, n_, 2.5, INK, 'middle', True)
lst = ['SENSOR IN: J1, sensor head, 3.3 V on the centre', 'SCOPE OUT: J4, the signal at the ADC (front)', 'test points: the name of each pad is on the back',
       'jumpers: JP1 to JP6, name on the back', 'PMOD pin list and the Auselia logo: back']
for i, t_ in enumerate(lst):
    pg.text(bx + 4, by + BH * k + 6 + i * 5.0, f'{i+1}  {t_}', 2.5, INK, 'start', True)

# 43 --------------------------------------------------------------------------------------------
u4p = FP['U4']['pads']
pw_, ph_ = u4p[0]['w'], u4p[0]['h']
pg = step('Which footprints are tricky',
          [f'The ADS7057 pads are {pw_:.2f} × {ph_:.2f} mm at 0.5 mm pitch. The gap between pads is 0.25 mm, so the solder mask web is thin. JLCPCB assembled it in the quote without a warning.',
           'Three other parts need care. The factory model of each one had a different orientation or origin from the footprint, and the CPL now corrects it.'])
chip(pg, label='PARTS TO WATCH')
cards_ = [('U4  ADS7057', 'X2QFN-8, 1.5 mm', 'pin 1 mark checked, rotated 180'), ('U6, U9  TLV7022', 'SOT-23-8, 0.65 mm pitch', 'check in the JLC viewer'),
          ('U8  OPA365 (head)', 'SOT-23-5', 'check in the JLC viewer'), ('J3  PMOD', 'right-angle 2 × 6', 'set absolute angle, 5.9 mm beyond the edge')]
for i, (a_, b_, c_) in enumerate(cards_):
    x_, y_ = 2 + (i % 2) * 68, 40 + (i // 2) * 21
    pg.rect(x_, y_, 64, 18, BONE2, 'none', 0, 2)
    pg.text(x_ + 3, y_ + 6.4, a_, 2.9, CANOPY, 'start', True)
    pg.text(x_ + 3, y_ + 11.2, b_, 2.5, INK, 'start')
    pg.text(x_ + 3, y_ + 15.4, c_, 2.5, MUTED, 'start')

# 44 --------------------------------------------------------------------------------------------
pg = step('What the board looks like',
          ['The render is from the final KiCad file. J1 and J4 stand on the left edge, J1 above J4. The PMOD header J3 points off the right edge. The 2-pin header J7 and the solder jumpers are next to it.',
           'The two holes are M3 mounting holes.'])
chip(pg, label='3D RENDER, KICAD')
_wa, _ha = __import__('PIL.Image', fromlist=['Image']).open(os.path.join(REPO, 'doc', 'assets', 'render_angled.jpg')).size
image(pg, os.path.join(REPO, 'doc', 'assets', 'render_angled.jpg'), 0, 38, 82, 82 * _ha / _wa)
for i, t_ in enumerate(['J1: SENSOR IN, left edge, top', 'J4: SCOPE OUT, left edge, bottom', 'J3: PMOD, right edge', 'J7 and JP2 to JP6: power links', 'U4: ADS7057, right third']):
    pg.text(86, 44 + i * 6.0, t_, 2.5, INK, 'start', True)

# top view page (after step 44) -----------------------------------------------------------------
m4lib._finish_page()
pg = new_page('top view')
chrome(pg, len(pages), 'Step 44  /  the board  /  top view', divider=False)
from PIL import Image as _Im
RND = os.path.join(REPO, 'doc', 'assets', 'top_render.png')
_wr, _hr = _Im.open(RND).size
PXMM = _wr / (BW + 6.0)           # the render covers the board and the 5.9 mm of the PMOD pins
IW, IH = _wr / PXMM, _hr / PXMM
K = (PW - 40) / IW
x0, y0 = (PW - IW * K) / 2, 24
image(pg, RND, x0, y0, IW * K, IH * K)
bx = x0
yb = y0 + IH * K + 6
pg.line(bx, yb, bx + 10 * K, yb, INK, 0.5)
pg.line(bx, yb - 1.5, bx, yb + 1.5, INK, 0.5)
pg.line(bx + 10 * K, yb - 1.5, bx + 10 * K, yb + 1.5, INK, 0.5)
pg.text(bx + 10 * K + 3, yb + 1, f'10 mm at this scale ({K:.1f} : 1)', 2.8, INK, 'start', True)
pg.text(bx + IW * K, yb + 1, f'Board {BW:.1f} × {BH:.1f} mm, KiCad 3D render, view from the top', 2.8, MUTED, 'end')
image(pg, RND, bx, yb + 10, IW, IH)
pg.text(bx + IW + 3, yb + 10 + IH / 2, 'The same view at real size, 1 : 1', 2.8, INK, 'start', True)
