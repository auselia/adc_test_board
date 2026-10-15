"""Hardware manual, part D: section 5 (the wake-up, steps 31 to 35) and section 6 (the board, steps 36 to 44)."""
import m4lib
from adc_common import *

LPF_GAIN = at(SIM['lpf'], 250e3)             # LPF_OUT per volt at J1, 250 kHz (50 ohm source included)
MON_GAIN = at(SIM['mon'], 250e3)


def rp_for(half):
    """trimmer resistance that gives a half window `half` at LPF_OUT (volts)"""
    k = half / 2.5
    return (k * (val('R21') + val('R22') + val('R23')) - val('R22')) / (1 - k)


# ================================================================================================
# SECTION 5: THE WAKE-UP
# ================================================================================================
section('THE WAKE-UP', 'The wake-up', 'Section 5', 'Steps 31 to 35',
        'How the LM393 turns a strong burst into a low level on nWAKE, how the trimmer sets the window and '
        'how to set it on the bench.', active=['Wake-up', 'Low-pass', 'SPI port'])

# 31 --------------------------------------------------------------------------------------------
H = window(10e3)
b = SIM['burst']['0.12']
tb = [t for t in b['t'] if t >= 4e-6]
lp = [v for t, v in zip(b['t'], b['lpf']) if t >= 4e-6]
low = [(abs(v - 2.5) > H) for v in lp]
assert any(low) and not all(low)
pg = step('What a window comparator is',
          ['The LM393 holds two comparators. One trips when the signal rises above the **upper** threshold. The other trips when it falls below the **lower** threshold. Both thresholds sit around 2.5 V.',
           'The two outputs share one wire. So nWAKE goes low as soon as the signal leaves the window on either side.'])
chip(pg, label='SIMULATION, 120 mV BURST')
X0, Y0, W_, H_ = 14, 38, 112, 26
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
yl = lambda v: Y0 + H_ / 2 - (v - 2.5) / 0.7 * (H_ / 2)
pts = [(X0 + (t - 4e-6) / 41e-6 * W_, yl(v)) for t, v in zip(tb, lp)]
pg.poly(pts, PUR, 0.6)
for s_ in (+1, -1):
    pg.line(X0, yl(2.5 + s_ * H), X0 + W_, yl(2.5 + s_ * H), RED, 0.4, '1.2,0.8')
pg.text(X0 + W_ + 1.5, yl(2.5 + H) + 0.9, 'upper', 2.5, RED, 'start', True)
pg.text(X0 + W_ + 1.5, yl(2.5 - H) + 0.9, 'lower', 2.5, RED, 'start', True)
pg.text(X0 - 1.5, yl(2.5) + 0.9, '2.5 V', 2.5, MUTED, 'end')
pg.text(X0 + W_ / 2, Y0 - 2.4, 'LPF_OUT', 2.5, MUTED, 'middle')
yn = Y0 + H_ + 12
pg.text(X0 - 1.5, yn + 4.5, 'nWAKE', 2.5, MUTED, 'end', True)
n_ = len(low)
lev = [0 if l else 1 for l in low]
pts = []
for i, l in enumerate(lev):
    x1 = X0 + i / n_ * W_
    pts += [(x1, yn + (0 if l else 6)), (X0 + (i + 1) / n_ * W_, yn + (0 if l else 6))]
pg.poly(pts, INK, 0.5)
pg.text(X0 + W_ / 2, yn + 14, f'window ±{H*1e3:.0f} mV, trimmer at 10 kΩ', 2.5, MUTED, 'middle')

# 32 --------------------------------------------------------------------------------------------
pg = step('How the window is set',
          ['One resistor chain from 5 V to ground makes both thresholds. The trimmer RV1 and a 1 kΩ resistor set the distance between them.',
           ('tex', r'V_{\mathrm{half}} = 2.5\,\mathrm{V} \cdot \frac{1\,\mathrm{k\Omega} + R_p}{67\,\mathrm{k\Omega} + R_p}', 9.0),
           f'The last column converts the window back to the perfboard output with a gain of {LPF_GAIN:.1f}.'])
chip(pg, label='RP AGAINST WINDOW')
pg.text(4, 41, 'Rp', 2.5, MUTED, 'start', True); pg.text(26, 41, 'upper', 2.5, MUTED, 'start', True); pg.text(52, 41, 'lower', 2.5, MUTED, 'start', True)
pg.text(78, 41, 'half window', 2.5, MUTED, 'start', True); pg.text(110, 41, 'at J1', 2.5, MUTED, 'start', True)
for k_, rp in enumerate((0, 5e3, 10e3, 14e3, 20e3)):
    y_ = 44 + k_ * 6.4
    hh = window(rp)
    pg.rect(2, y_, 134, 5.6, BONE2 if k_ % 2 == 0 else '#fff', 'none', 0)
    pg.text(4, y_ + 4, f'{rp/1e3:.0f} kΩ', 2.6, INK, 'start', True)
    pg.text(26, y_ + 4, f'{2.5+hh:.3f} V', 2.6, INK, 'start')
    pg.text(52, y_ + 4, f'{2.5-hh:.3f} V', 2.6, INK, 'start')
    pg.text(78, y_ + 4, f'{hh*1e3:.0f} mV', 2.6, INK, 'start', True)
    pg.text(110, y_ + 4, f'{hh/LPF_GAIN*1e3:.0f} mV', 2.6, PUR, 'start', True)

# 33 --------------------------------------------------------------------------------------------
pg = step('Why nWAKE is open-collector',
          ['The LM393 output can only pull the line to ground. It cannot drive it high. A 10 kΩ resistor (R24) pulls the line up to 3.3 V from the PMOD.',
           'So the FPGA never sees 5 V, although the LM393 runs from 5 V. The two outputs share one wire, so either one can pull nWAKE low.'])
chip(pg, label='WIRED-OR')
pg.text(20, 40, '+3.3 V from the PMOD', 2.6, GRN, 'start', True)
pg.line(40, 42, 40, 46, INK, 0.45)
res_v(pg, 40, 46, 10, 'R24', '10 kΩ')
dot(pg, 40, 62)
pg.line(40, 56, 40, 62, INK, 0.45)
pg.line(40, 62, 76, 62, INK, 0.5)
pg.arrow([(70, 62), (76, 62)])
pg.text(78, 63, 'nWAKE, PMOD pin 10', 2.6, INK, 'start', True)
for k_, xx in enumerate((20, 56)):
    pg.line(xx, 62, xx, 66, INK, 0.45)
    pg.rect(xx - 7, 66, 14, 8, '#fff', INK, 0.5, 1.2)
    pg.text(xx, 71.4, ('OUT1', 'OUT2')[k_], 2.5, INK, 'middle', True)
    pg.line(xx, 74, xx, 78, INK, 0.45)
    gnd(pg, xx, 78)
dot(pg, 20, 62); dot(pg, 56, 62)
pg.text(100, 44, 'OUT1  OUT2  nWAKE', 2.5, MUTED, 'start', True)
for k_, (a_, b_, c_) in enumerate((('off', 'off', 'high'), ('on', 'off', 'low'), ('off', 'on', 'low'), ('on', 'on', 'low'))):
    pg.text(100, 50 + k_ * 5.5, a_, 2.5, INK, 'start'); pg.text(112, 50 + k_ * 5.5, b_, 2.5, INK, 'start'); pg.text(124, 50 + k_ * 5.5, c_, 2.5, INK, 'start', True)

# 34 --------------------------------------------------------------------------------------------
noise_q = sorted(b_['inband'] for b_ in json.load(open(os.path.join(DATA, 'events.json')))['baselines'])[:5]
noise_lpf = (sum(noise_q) / 5) * 1e-3 * LPF_GAIN
rp_min = rp_for(3 * noise_lpf)
pg = step('How fast and how accurate',
          [f'The LM393 answers in about 1.3 µs. That is slow for a clock but fast for a wake-up. Its input offset is about 5 mV, which is small against the window.',
           f'The noise decides the smallest useful setting. The quiet baseline of {sum(noise_q)/5:.1f} mV rms becomes {noise_lpf*1e3:.0f} mV rms at the comparator. Three times that is {3*noise_lpf*1e3:.0f} mV. Below Rp = {rp_min/1e3:.1f} kΩ the noise alone trips the output.'])
chip(pg, label='NOISE AGAINST WINDOW, ESTIMATE')
for k_, (nm, v_, c_) in enumerate((('smallest window', window(0) * 1e3, BLU), ('3 × noise', 3 * noise_lpf * 1e3, RED), ('typical event', 0.12 * LPF_GAIN * 1e3, PUR), ('largest window', window(RP_MAX) * 1e3, BLU))):
    y_ = 40 + k_ * 9.4
    pg.text(2, y_ + 5.2, nm, 2.6, INK, 'start', True)
    pg.rect(40, y_, v_ / 640 * 84, 6.6, c_, 'none', 0)
    pg.text(40 + v_ / 640 * 84 + 2, y_ + 5.2, f'{v_:.0f} mV', 2.6, INK, 'start', True)

# 35 --------------------------------------------------------------------------------------------
want = 0.100 * LPF_GAIN
rp100 = rp_for(want)
rp50 = rp_for(0.050 * LPF_GAIN)
pg = step('How to set the trimmer',
          ['Choose the burst that should wake the system. Feed that burst to J1. Watch SCOPE OUT and nWAKE together. Turn RV1 slowly until nWAKE drops for that burst and stays high without it.',
           f'A 50 mV burst at J1 needs Rp near {rp50/1e3:.1f} kΩ. A 100 mV burst needs Rp near {rp100/1e3:.1f} kΩ. The trimmer is a 20 kΩ part, so the middle of its travel is close to 100 mV.'])
chip(pg, label='BENCH STEPS')
steps_ = [('1', 'Feed 250 kHz, 100 mV to J1'), ('2', f'Read {100e-3*MON_GAIN:.2f} V peak on SCOPE OUT'),
          ('3', 'Turn RV1 until nWAKE just pulses'), ('4', 'Remove the burst. nWAKE must stay high')]
for k_, (n_, t_) in enumerate(steps_):
    y_ = 40 + k_ * 9.2
    pg.circle(8, y_ + 3.2, 3.2, AMBT, INK, 0.35)
    pg.text(8, y_ + 4.3, n_, 2.8, INK, 'middle', True)
    pg.text(15, y_ + 4.2, t_, 2.9, INK, 'start', True)
pg.text(70, 83, 'clockwise should widen the window. Check with a meter on VTH_H', 2.5, MUTED, 'middle')

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
assert sorted(widths) == [0.15, 0.2]

# 36 --------------------------------------------------------------------------------------------
pg = step('The stack and the size',
          [f'The main board is {BW:.0f} × {BH:.0f} mm with two copper layers on 1.6 mm FR-4. Both layers carry a ground pour. {n_gvia} of the {n_via} vias are ground stitching vias that tie the two pours together.',
           f'All {n_top + n_bot} track segments are 0.2 mm wide, except {widths[0.15]} short segments of 0.15 mm near the fine-pitch pads. Vias are 0.6 mm with a 0.3 mm drill.'])
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
          ['The signal runs left to right across the top half, as in the block diagram. The driver and the ADC sit in the middle. The power parts take the bottom left. The comparator sits in the bottom right.',
           'The PMOD connector is on the right edge so the board hangs on the ZedBoard. The SMA connectors stand at the top, away from the ADC. The left strip holds HEAD IN and its bias-T.'])
chip(pg, label='TOP VIEW, COLORS BY BLOCK')
k = 1.35
bx, by = 4, 36
pg.rect(bx, by, BW * k, BH * k, '#f8f8f4', INK, 0.5, 1)
for ref, f in FP.items():
    x0, y0, x1, y1 = f['bbox']
    c_ = BLOCK_COLOR[BLOCK_OF[ref]]
    pg.rect(bx + max(x0, 0) * k, by + max(y0, 0) * k, (min(x1, BW) - max(x0, 0)) * k, (min(y1, BH) - max(y0, 0)) * k, c_, INK, 0.12, 0.3)
leg = [('Input and high-pass', 'in'), ('Gain', 'gain'), ('Low-pass', 'lp'), ('Op-amps U1, U2 and bypass', 'U1 U2'), ('Mid-rail VMID5', 'VMID5'),
       ('Driver THS4531', 'drv'), ('VOCM 1.65 V', 'VOCM'), ('ADC input filter', 'filt'), ('ADS7057 and bypass', 'ADC'), ('SPI series resistors', 'SPI R'),
       ('AVDD regulator', 'AVDD'), ('9 V to 5 V', '5 V'), ('Wake-up comparator', 'wake'), ('Connectors', 'conn')]
names = [b for b in BLOCKS if b[0] != 'Holes']
for i, (nm, c_, rs) in enumerate(names):
    yy = 36 + i * 3.6
    pg.rect(bx + BW * k + 4, yy, 2.8, 2.8, c_, INK, 0.2)
    pg.text(bx + BW * k + 8.5, yy + 2.5, nm, 2.2, INK, 'start')

# 38 --------------------------------------------------------------------------------------------
n_tht = sum(1 for f in FP.values() if any(p['tht'] for p in f['pads']) and not f['fp'].startswith('Mounting'))
n_hole = sum(1 for r in FP if r.startswith('H'))
n_smd = len(FP) - n_tht - n_hole - 1
pg = step('Where every part is',
          [f'The table lists the blocks, the references and the count. The main board has {len(FP)} footprints: {n_smd} surface-mount parts, {n_tht} through-hole parts and {n_hole} mounting holes, plus one not-fitted capacitor.',
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
           'The 5 mm difference is harmless here. A 5 mm track delays a signal by about 30 ps, and a 500 kHz wave lasts 2 µs.'])
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
          [f'The longest analog net is LPF_OUT at {lens["LPF_OUT"]:.0f} mm, because it feeds the SCOPE OUT connector, the comparator and the driver. All other analog nets are under {sorted(lens.values())[-2]:.0f} mm.',
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
pw = ['+5V', 'AVDD', '+3V3', '+9VP', 'VMID5', 'VOCM']
plen = {n: net_length(n) for n in pw}
rho, thick = 1.7e-8, 35e-6
drop5 = rho * plen['+5V'] * 1e-3 / (0.2e-3 * thick) * (I_BAT_A := 0.027)
pg = step('How power and ground are routed',
          [f'Ground is a pour on both layers, tied by {n_gvia} vias, so every ground pad finds a short path. The power nets are ordinary 0.2 mm tracks, not wide ones, because the currents are small.',
           f'The +5 V net is {plen["+5V"]:.0f} mm of track in total. With 27 mA (22 mA, plus 5 mA for the sensor head) this drops about {drop5*1e3:.0f} mV across its whole length (ESTIMATE, worst case).'])
chip(pg, label='POWER NET LENGTH, mm')
mxp = max(plen.values())
for i, n_ in enumerate(pw):
    y_ = 40 + i * 6.8
    pg.text(2, y_ + 4.6, n_, 2.6, INK, 'start', True)
    pg.rect(26, y_, plen[n_] / mxp * 80, 5.6, GRN, 'none', 0)
    pg.text(26 + plen[n_] / mxp * 80 + 2, y_ + 4.6, f'{plen[n_]:.0f}', 2.6, INK, 'start', True)

# 42 --------------------------------------------------------------------------------------------
pg = step('What each label on the silkscreen means',
          ['The front carries the labels that a user needs. The names of the parts (R16, C29 and so on) are not on the silkscreen, because the board is dense. They are in the KiCad file and in the 1:1 print.',
           'The back carries the PMOD pin list and the title.'])
chip(pg, label='FRONT SIDE')
k = 1.35
bx, by = 2, 38
pg.rect(bx, by, BW * k, BH * k, '#f8f8f4', INK, 0.5, 1)
marks = [('HEAD IN', 5.0, 1.1, 1), ('SENSOR IN', 18.6, 1.1, 2), ('CH', 26.0, 1.2, 3), ('SCOPE OUT', 50.6, 0.9, 4), ('+9V', 16.6, 21.2, 5), ('GND', 16.6, 28.1, 5),
         ('WAKE LEVEL', 37.2, 25.3, 6), ('1', 56.0, 11.0, 7), ('logo', 32, 14.2, 8)]
for nm, x_, y_, n_ in marks:
    pg.circle(bx + x_ * k, by + y_ * k + 2.5, 2.2, AMBT, INK, 0.3)
    pg.text(bx + x_ * k, by + y_ * k + 3.4, n_, 2.5, INK, 'middle', True)
lst = ['HEAD IN: J5, sensor head, +5 V on the centre', 'SENSOR IN: J1, perfboard or generator', 'CH box: write the channel number', 'SCOPE OUT: J4, the signal at the ADC', '+9V and GND: battery, square pad is +',
       'WAKE LEVEL: trimmer RV1', '1: PMOD pin 1', 'logo: Auselia mark']
for i, t_ in enumerate(lst):
    pg.text(bx + BW * k + 4, 41 + i * 5.0, f'{i+1}  {t_}', 2.3, INK, 'start', True)

# 43 --------------------------------------------------------------------------------------------
u4p = FP['U4']['pads']
pw_, ph_ = u4p[0]['w'], u4p[0]['h']
pg = step('Which footprints are tricky',
          [f'The ADS7057 pads are {pw_:.2f} × {ph_:.2f} mm at 0.5 mm pitch. The gap between pads is 0.25 mm, so the solder mask web is thin. JLCPCB assembled it in the quote without a warning.',
           'Four other parts needed care. The factory model of each one had a different orientation or origin from the footprint, and the CPL now corrects it.'])
chip(pg, label='PARTS TO WATCH')
cards_ = [('U4  ADS7057', 'X2QFN-8, 1.5 mm', 'pin 1 mark checked'), ('U5  XC6206', 'SOT-23, 3 pins', 'rotation 180'),
          ('C29  tantalum', 'polarity: + on pad 1', 'rotation 0'), ('J3  PMOD', 'right-angle 2 × 6', '5.9 mm beyond the edge')]
for i, (a_, b_, c_) in enumerate(cards_):
    x_, y_ = 2 + (i % 2) * 68, 40 + (i // 2) * 21
    pg.rect(x_, y_, 64, 18, BONE2, 'none', 0, 2)
    pg.text(x_ + 3, y_ + 6.4, a_, 2.9, CANOPY, 'start', True)
    pg.text(x_ + 3, y_ + 11.2, b_, 2.5, INK, 'start')
    pg.text(x_ + 3, y_ + 15.4, c_, 2.5, MUTED, 'start')

# 44 --------------------------------------------------------------------------------------------
pg = step('What the board looks like',
          ['The render is from the final KiCad file. J5 and J1 stand on the top left and J4 on the top right. The PMOD header J3 points off the right edge. The blue trimmer RV1 is at the bottom.',
           'The two holes are M3 mounting holes.'])
chip(pg, label='3D RENDER, KICAD')
image(pg, os.path.join(REPO, 'doc', 'assets', 'render_angled.jpg'), 0, 38, 76, 76 * 1568 / 2384)
for i, t_ in enumerate(['J5: HEAD IN, top left', 'J1: SMA in, next to it', 'J4: SCOPE OUT, top right', 'J3: PMOD, right edge', 'RV1: wake level trimmer', 'U4: ADS7057, centre right']):
    pg.text(82, 44 + i * 6, t_, 2.6, INK, 'start', True)

# top view page (after step 44) -----------------------------------------------------------------
m4lib._finish_page()
pg = new_page('top view')
chrome(pg, len(pages), 'Step 44  /  the board  /  top view at 3 : 1', divider=False)
IW, IH = 74.99, 37.98            # mm covered by the render; board starts 3 mm from the left and top edges
K = 3.0
RND = os.path.join(REPO, 'doc', 'assets', 'top_render.png')
x0, y0 = (PW - IW * K) / 2, 24
image(pg, RND, x0, y0, IW * K, IH * K)
bx, by = x0 + 3 * K, y0 + 3 * K
yb = y0 + IH * K + 6
pg.line(bx, yb, bx + 10 * K, yb, INK, 0.5)
pg.line(bx, yb - 1.5, bx, yb + 1.5, INK, 0.5)
pg.line(bx + 10 * K, yb - 1.5, bx + 10 * K, yb + 1.5, INK, 0.5)
pg.text(bx + 10 * K + 3, yb + 1, '10 mm at this scale (3 : 1)', 2.8, INK, 'start', True)
pg.text(bx + BW * K, yb + 1, f'Board {BW:.1f} × {BH:.1f} mm, KiCad 3D render, view from the top', 2.8, MUTED, 'end')
image(pg, RND, bx - 3, yb + 8, IW, IH)
pg.text(bx + IW + 2, yb + 8 + IH / 2, 'The same view at real size, 1 : 1', 2.8, INK, 'start', True)
