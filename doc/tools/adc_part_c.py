"""Hardware manual, part C: section 3 (driver and ADC, steps 17 to 24) and section 4 (the SPI link, steps 25 to 30)."""
import m4lib
from adc_common import *

# ================================================================================================
# SECTION 3: DRIVER AND ADC
# ================================================================================================
section('DRIVER AND ADC', 'Driver and ADC', 'Section 3', 'Steps 17 to 24',
        'How one wire becomes two, how the ADC input is protected from its own sampling kick, what the ADS7057 is '
        'and what its numbers mean for this board.', active=['Driver', 'ADC'])

bur = SIM['burst']['0.12']
ADC_PK = max(bur['adc'])
ADC_NEG = min(bur['adc'])


def closest(a, b):
    best = 1e9
    for p in FP[a]['pads']:
        for q in FP[b]['pads']:
            best = min(best, math.hypot(p['x'] - q['x'], p['y'] - q['y']))
    return best


# 17 --------------------------------------------------------------------------------------------
pg = step('How one wire becomes two',
          [f'The ADS7057 needs two inputs that move in opposite directions. The **THS4531** (U3) makes them from one wire. The capacitor C11 and R10 bring the signal in. The corner of this coupling is {CPL_FC:.0f} Hz, far below the band.',
           ('tex', r'V_{\mathrm{OUT+}} - V_{\mathrm{OUT-}} = \frac{R_{12}}{R_{10}}\,V_{\mathrm{IN}} = 1 \cdot V_{\mathrm{IN}}', 9.0),
           'Each output moves half of the signal around VOCM, in opposite directions.'])
chip(pg, label='SIMULATION, 120 mV BURST')
X0, Y0, W_, H_ = 10, 38, 120, 38
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
yv_ = lambda v: Y0 + H_ - (v - 1.0) / 1.3 * H_
t0_ = 4e-6
for key, c_ in (('op', PUR), ('om', BLU)):
    pts = [(X0 + (t - t0_) / 41e-6 * W_, yv_(v)) for t, v in zip(bur['t'], bur[key]) if t >= t0_]
    pg.poly(pts, c_, 0.6)
pg.line(X0, yv_(1.65), X0 + W_, yv_(1.65), '#888', 0.3, '1.2,0.8')
pg.text(X0 - 1.5, yv_(1.65) + 0.9, '1.65', 2.5, MUTED, 'end')
pg.text(X0 + W_ + 1.5, yv_(1.9) + 0.9, 'OUT+', 2.6, PUR, 'start', True)
pg.text(X0 + W_ + 1.5, yv_(1.4) + 0.9, 'OUT−', 2.6, BLU, 'start', True)
pg.text(X0 + W_ / 2, Y0 + H_ + 5, 'time, 40 µs      volts', 2.5, MUTED, 'middle')
assert ('R12', '1') in NET['DRV_OUTP'] and ('R12', '2') in NET['DRV_INN'] and ('R13', '1') in NET['DRV_OUTN']

# 18 --------------------------------------------------------------------------------------------
pg = step('What to know about the THS4531',
          ['Three facts from the datasheet shape the board. The **PD** pin must be driven, so U3 ties it to 3.3 V. The **VOCM** pin accepts 0.95 to 2.3 V on a 3.3 V supply, so 1.65 V is fine.',
           'The third fact is a limit. The designers of the part expect about 2 pF of load between its outputs. A larger load needs a series resistor.'])
chip(pg, label='DATASHEET AGAINST THIS BOARD')
rows_ = [('Supply', '2.5 to 5.5 V', '3.3 V', 'ok'), ('Gain-bandwidth', '27 MHz', 'gain 1', 'ok'), ('Noise', '10 nV/√Hz', '0.2 LSB', 'ok'),
         ('VOCM range at 3.3 V', '0.95 to 2.3 V', '1.65 V', 'ok'), ('PD pin', 'must be driven', 'tied to 3.3 V', 'ok'),
         ('Load between outputs', '2 pF nominal', '400 pF + 20 Ω', 'open')]
pg.text(4, 40, 'item', 2.5, MUTED, 'start', True); pg.text(50, 40, 'datasheet', 2.5, MUTED, 'start', True)
pg.text(92, 40, 'this board', 2.5, MUTED, 'start', True)
for k_, (a_, b_, c_, st_) in enumerate(rows_):
    y_ = 43 + k_ * 7.6
    pg.rect(2, y_, 134, 6.6, AMBT if st_ == 'open' else (BONE2 if k_ % 2 == 0 else '#fff'), 'none', 0)
    pg.text(4, y_ + 4.6, a_, 2.6, INK, 'start', st_ == 'open')
    pg.text(50, y_ + 4.6, b_, 2.6, INK, 'start')
    pg.text(92, y_ + 4.6, c_, 2.6, INK, 'start', True)
    if st_ == 'open':
        pg.text(134, y_ + 4.6, 'OPEN', 2.5, RED, 'end', True)

st = SIM['settle']
def settle_ns(d, thr=0.2e-3):
    t_, v_ = d['t'], d['v']
    last = 0.0
    for tt, vv in zip(t_, v_):
        if abs(vv - d['final']) > thr:
            last = tt
    return last
s1, s2 = settle_ns(st['0.34']), settle_ns(st['0.56'])
assert 20 < s1 < 45 and 40 < s2 < 70
# 19 --------------------------------------------------------------------------------------------
Q = CS_ADC * 0.56
DV = CS_ADC / (CS_ADC + ADC_C) * 0.56
pg = step('What the 10 Ω and 400 pF are for',
          [f'When the ADC samples, its 16 pF capacitor connects to the input and pulls a burst of charge. A step of 0.56 V moves {Q*1e12:.0f} pC. A big capacitor next to the pins supplies this charge, so the driver sees only a small glitch.',
           f'Four 100 pF capacitors make 400 pF, which is {ADC_C/CS_ADC:.0f} times the sampling capacitor. The datasheet asks for at least 20 times. The two 10 Ω resistors isolate the driver. The pole is at {ADC_POLE/1e6:.0f} MHz, far above the band.'])
chip(pg, label='KICKBACK FILTER')
pbox(pg, 2, 40, 20, 18, 'THS4531', ['OUT+', 'OUT−'], 'mem', 2.8, 2.4)
res_h(pg, 22, 44, 18, 'R16', '10 Ω')
res_h(pg, 22, 54, 18, 'R17', '10 Ω', above=False)
dot(pg, 46, 44); dot(pg, 46, 54)
pg.line(40, 44, 46, 44, INK, 0.45); pg.line(40, 54, 46, 54, INK, 0.45)
pg.line(46, 44, 46, 46.5, INK, 0.45); pg.line(46, 54, 46, 51.5, INK, 0.45)
pg.line(42, 46.5, 50, 46.5, INK, 0.7); pg.line(42, 51.5, 50, 51.5, INK, 0.7)
pg.text(52, 38.5, 'C14 to C17', 2.5, INK, 'start', True)
pg.text(52, 42.5, '4 × 100 pF', 2.5, INK, 'start', True)
pg.line(46, 44, 74, 44, INK, 0.45); pg.line(46, 54, 74, 54, INK, 0.45)
pbox(pg, 74, 38, 40, 22, 'ADS7057', [], 'mem', 2.8, 2.4)
pg.text(94, 47.4, 'AINP, AINM', 2.4, '#fff', 'middle')
pg.text(94, 55, '50 Ω and 16 pF per leg', 2.4, '#fff', 'middle')
pg.text(70, 72, f'the node dips by {DV*1e3:.0f} mV ({DV/LSB:.0f} LSB) and recovers in {s2:.0f} ns at worst', 2.6, INK, 'middle', True)
pg.text(70, 78, 'the 25× rule: 16 pF × 20 = 320 pF minimum', 2.5, MUTED, 'middle')

# 20 --------------------------------------------------------------------------------------------
pg = step('What the ADC input looks like',
          [f'The sampling switch of the ADC is 50 Ω in series with 16 pF on each leg. The simulation closes the switch on a signal that was left at the previous sample. The input settles to half an LSB in {s1:.0f} ns for a typical step and {s2:.0f} ns for a large one.',
           'How to read the graph: at time 0 the switch closes and the input is wrong by the step (340 or 560 mV). The curve is the remaining error as it shrinks. When it falls under the red line, the sample is right to half an LSB. The ADC allows 95 ns.'])
chip(pg, label='SIMULATION, SETTLING')
X0, Y0, W_, H_ = 14, 36, 112, 40
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
tx_ = lambda t: X0 + t / 100.0 * W_
ey = lambda mv: Y0 + H_ - (math.log10(max(mv, 0.05)) - math.log10(0.1)) / (math.log10(2000) - math.log10(0.1)) * H_
for key, c_ in (('0.34', PUR), ('0.56', BLU)):
    d = st[key]
    pts = [(tx_(tt), ey(abs(vv - d['final']) * 1e3)) for tt, vv in zip(d['t'], d['v']) if 0 <= tt <= 100]
    pg.poly(pts, c_, 0.6)
pg.line(X0, ey(0.2), X0 + W_, ey(0.2), RED, 0.35, '1.2,0.8')
pg.text(X0 + W_ - 1, ey(0.2) - 1.4, 'half an LSB, 0.2 mV', 2.5, RED, 'end', True)
pg.line(tx_(95), Y0, tx_(95), Y0 + H_, RED, 0.4, '1.2,0.8')
pg.text(tx_(95) - 1.4, Y0 + 4, 'tACQ 95 ns', 2.5, RED, 'end', True)
for t_ in (0, 25, 50, 75, 100):
    pg.text(tx_(t_), Y0 + H_ + 4, t_, 2.5, MUTED, 'middle')
for mv, nm in ((1000, '1 V'), (10, '10 mV'), (0.1, '0.1 mV')):
    pg.text(X0 - 1.5, ey(mv) + 0.9, nm, 2.5, MUTED, 'end')
pg.text(X0 + W_ / 2, Y0 + H_ + 8.4, 'ns after the switch closes. Vertical: remaining error, log scale.', 2.5, MUTED, 'middle')
pg.rect(X0, ey(0.2), tx_(95) - X0, Y0 + H_ - ey(0.2), '#e4f2e0', 'none', 0, 0)
pg.text(X0 + 2, Y0 + H_ - 2, 'settled in time', 2.4, '#2f7a3f', 'start', True)
for key, c_, nm in (('0.34', PUR, 'typical step, 0.34 V'), ('0.56', BLU, 'worst step, 0.56 V')):
    d_ = st[key]
    err_ = [(tt, abs(vv - d_['final']) * 1e3) for tt, vv in zip(d_['t'], d_['v']) if 0 <= tt <= 100]
    tcross = max((tt for tt, ee in err_ if ee >= 0.2), default=None)       # the last time the error is above half an LSB
    if tcross is not None:
        pg.circle(tx_(tcross), ey(0.2), 1.1, c_, '#fff', 0.3)
        pg.text(tx_(tcross) + (-1.5 if key == '0.34' else 1.5), ey(0.2) + 5.0, f'{tcross:.0f} ns', 2.4, c_, 'end' if key == '0.34' else 'start', True)
    pg.text(X0 + 4, ey(d_['final'] and abs(d_['v'][0] - d_['final']) * 1e3) + (3.2 if key == '0.34' else -1.0), nm, 2.4, c_, 'start', True)

# 21 --------------------------------------------------------------------------------------------
pg = step('What the ADS7057 is',
          ['A 14-bit successive-approximation ADC in a 1.5 × 1.5 mm package with eight pads. It samples on the falling edge of CS and sends its result over SPI.',
           'The table lists the numbers that matter for this board. All come from datasheet SBAS821.'])
chip(pg, label='X2QFN-8, TOP VIEW')
pg.rect(8, 40, 24, 24, '#fff', INK, 0.6, 1.0)
pg.circle(12, 44, 0.9, INK)
PINS = [('1', 'nCS', 'left', 0), ('2', 'SDO', 'left', 1), ('3', 'SCLK', 'left', 2), ('4', 'DVDD', 'bottom', 0),
        ('5', 'GND', 'right', 2), ('6', 'AVDD', 'right', 1), ('7', 'AINP', 'right', 0), ('8', 'AINM', 'top', 0)]
for n_, nm, side, k_ in PINS:
    if side == 'left':
        y_ = 45 + k_ * 7
        pg.line(3, y_, 8, y_, INK, 0.5); pg.text(2, y_ - 1.2, nm, 2.4, INK, 'end', True); pg.text(10, y_ + 0.9, n_, 2.3, MUTED, 'start')
    elif side == 'right':
        y_ = 45 + k_ * 7
        pg.line(32, y_, 37, y_, INK, 0.5); pg.text(38, y_ - 1.2, nm, 2.4, INK, 'start', True); pg.text(30, y_ + 0.9, n_, 2.3, MUTED, 'end')
    elif side == 'top':
        pg.line(20, 35, 20, 40, INK, 0.5); pg.text(20, 33.5, nm, 2.4, INK, 'middle', True); pg.text(20, 43.5, n_, 2.3, MUTED, 'middle')
    else:
        pg.line(20, 64, 20, 69, INK, 0.5); pg.text(20, 72.4, nm, 2.4, INK, 'middle', True); pg.text(20, 62, n_, 2.3, MUTED, 'middle')
facts = [('Resolution', '14 bit, no missing codes'), ('Rate', 'up to 2.5 MSPS'), ('Supply', 'AVDD 2.35 to 3.6 V, DVDD 1.65 to 3.6 V'),
         ('Input', 'differential, ±AVDD, common mode AVDD/2'), ('SNR', '79.6 dB at 2 kHz'), ('INL, DNL', '±0.9 LSB, ±0.3 LSB typical'),
         ('SPI', 'mode 1, SCLK up to 60 MHz'), ('Conversion', '18 SCLK, then at least 95 ns acquisition')]
for k_, (a_, b_) in enumerate(facts):
    y_ = 38 + k_ * 6.8
    pg.text(58, y_, a_, 2.5, CANOPY, 'start', True)
    pg.text(82, y_, b_, 2.4, INK, 'start')

# 22 --------------------------------------------------------------------------------------------
dist = {r: closest('U4', r) for r in ('C18', 'C22', 'C19', 'C20')}
pg = step('How the ADC is decoupled',
          [f'AVDD gets a 4.7 µF (C18) and a 100 nF (C22). DVDD gets a 1 µF (C19) and a 100 nF (C20). The datasheet asks for 3.3 µF and 1 µF and says to keep them close, with no vias between the pin and the capacitor.',
           f'On this board C22 is {dist["C22"]:.1f} mm from the ADC and C18 is {dist["C18"]:.1f} mm. C20 is {dist["C20"]:.1f} mm and C19 is {dist["C19"]:.1f} mm. The 100 nF parts sit farther than the large ones, which is a point to improve.'])
chip(pg, label='REAL BOARD, 7 ×')
RX0, RY0, RX1, RY1 = 28.0, 15.0, 42.0, 24.0
S = 5.2
pg.rect(0, 0, (RX1 - RX0) * S, (RY1 - RY0) * S, '#e8f0e4', INK, 0.3)
def clipl(x1, y1, x2, y2):
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
    c_ = clipl(t['x1'], t['y1'], t['x2'], t['y2'])
    if c_:
        pg.line((c_[0] - RX0) * S, (c_[1] - RY0) * S, (c_[2] - RX0) * S, (c_[3] - RY0) * S, '#b9b4c9' if t['layer'] == 'F' else '#b6c8dc', max(t['w'] * S, 0.4))
hi = {'U4': AMB, 'C18': '#6aa84f', 'C22': '#6aa84f', 'C19': BLU, 'C20': BLU}
for ref, f in FP.items():
    for p in f['pads']:
        if RX0 <= p['x'] <= RX1 and RY0 <= p['y'] <= RY1:
            pg.rect((p['x'] - RX0 - p['w'] / 2) * S, (p['y'] - RY0 - p['h'] / 2) * S, p['w'] * S, p['h'] * S, hi.get(ref, '#d6d6d0'), INK, 0.12)
for ref in hi:
    f = FP[ref]
    x0, y0, x1, y1 = f['bbox']
    if RX0 <= f['x'] <= RX1 and RY0 <= f['y'] <= RY1:
        pg.text((f['x'] - RX0) * S, (f['y'] - RY0) * S - 6.0 if ref == 'U4' else (f['y'] - RY0) * S - 4.2, ref, 2.8, INK, 'middle', True)
pg.text(0, (RY1 - RY0) * S + 4, 'AVDD parts green, DVDD parts blue', 2.5, MUTED, 'start')

# 23 --------------------------------------------------------------------------------------------
code_p = int(math.floor(ADC_PK / LSB)); code_n = int(math.floor(ADC_NEG / LSB))
b14 = lambda c: c & 0x3FFF
assert 1000 < code_p < 1700 and -1700 < code_n < -1000
pg = step('How a voltage becomes a code',
          [f'The 120 mV event of the simulation reaches {ADC_PK:.3f} V between AINP and AINM. The code is the voltage divided by 1 LSB, rounded down.',
           ('tex', r'\mathrm{code} = \left\lfloor \frac{V_{\mathrm{AINP}} - V_{\mathrm{AINM}}}{1\ \mathrm{LSB}} \right\rfloor', 9.0),
           f'So the peak is {code_p}, which is 0x{b14(code_p):04X}. The negative peak {ADC_NEG:.3f} V gives {code_n}, which is 0x{b14(code_n):04X} in two\'s complement.'])
chip(pg, label='FROM THE SIMULATION')
for r_, (c_, nm) in enumerate(((code_p, 'positive peak'), (code_n, 'negative peak'))):
    y_ = 52 + r_ * 14
    bits = format(b14(c_), '014b')
    pg.text(2, y_ - 1.2, nm, 2.5, INK, 'start', True)
    for i_, bch in enumerate(bits):
        pg.cell(30 + i_ * 6.2, y_ - 4, 6.0, 6.2, bch, AMBT if bch == '1' else '#fff', PUR, 2.6, True)
    pg.text(30 + 14 * 6.2 + 3, y_ + 0.4, f'0x{b14(c_):04X}', 2.7, INK, 'start', True)
pg.text(30, 44, 'D13 is the sign bit', 2.4, MUTED, 'start')

# 24 --------------------------------------------------------------------------------------------
sens_lsb = (3.7e-3 * ADC_GAIN_250 / LSB, 4.6e-3 * ADC_GAIN_250 / LSB)
board_lsb = SIM['noise_vrms'] / LSB
rms_fs = AVDD / math.sqrt(2)
adc_lsb = rms_fs / 10 ** (79.6 / 20) / LSB
pg = step('How much noise the ADC sees',
          [f'Three noise sources add. The sensor noise of the perfboard, through this board, is {sens_lsb[0]:.0f} to {sens_lsb[1]:.0f} LSB rms. The board adds {board_lsb:.1f} LSB. The ADC itself adds about {adc_lsb:.1f} LSB.',
           'So the sensor decides the noise floor. The board and the ADC are small by comparison, and this is what a test board should show.'])
chip(pg, label='LSB RMS, ESTIMATE FOR THE ADC')
mx = 50.0
items = [('perfboard sensor', sens_lsb[1], PUR), ('this board', board_lsb, BLU), ('ADS7057 itself', adc_lsb, GRN)]
for k_, (nm, v_, c_) in enumerate(items):
    y_ = 42 + k_ * 12
    pg.text(2, y_ + 5.2, nm, 2.7, INK, 'start', True)
    pg.rect(44, y_, max(v_ / mx * 80, 0.8), 7, c_, 'none', 0)
    lbl = f'{sens_lsb[0]:.0f} to {sens_lsb[1]:.0f}' if k_ == 0 else f'{v_:.1f}'
    pg.text(44 + max(v_ / mx * 80, 0.8) + 2, y_ + 5.2, lbl, 2.7, INK, 'start', True)

# ================================================================================================
# SECTION 4: THE SPI LINK
# ================================================================================================
section('THE SPI LINK', 'The SPI link', 'Section 4', 'Steps 25 to 30',
        'The four wires from the ADC to the ZedBoard, what one frame looks like, why the data comes one frame late, '
        'the calibration at power-up and how fast the link can go.', active=['ADC', 'SPI port'])

# 25 --------------------------------------------------------------------------------------------
PMOD = {}
for pad, net in (('1', 'CS'), ('5', 'SDO'), ('7', 'SCLK'), ('9', 'GND'), ('10', 'GND'), ('11', '+3V3_PMOD'), ('12', '+3V3_PMOD'), ('8', 'WAKE_N'), ('2', 'BIG_N')):
    assert ('J3', pad) in NET[net], (pad, net)
    n = int(pad); r_, c_ = (n + 1) // 2, 2 - n % 2        # row, column of the KiCad zig-zag numbering
    PMOD[n] = (net, r_, c_, r_ if c_ == 1 else r_ + 6)    # PMOD pin number: left column 1 to 6, right column 7 to 12
assert PMOD[1][3] == 1 and PMOD[5][3] == 3 and PMOD[7][3] == 4 and PMOD[8][3] == 10 and PMOD[2][3] == 7 and PMOD[9][3] == 5 and PMOD[11][3] == 6
pg = step('Which pin is which on the PMOD',
          ['The board plugs into one PMOD port of the ZedBoard, JA to JD. The board uses nine of the twelve pins. **CS**, **SCLK** and **SDO** carry SPI. **WAKE_N** and **BIG_N** are the two listener lines. 3V3 on pins 6 and 12 powers the whole board, and GND is the return.',
           'There is no MOSI wire, because this ADC only sends data. The numbering follows the Digilent SPI PMOD, so pin 1 is CS.'])
chip(pg, label='J3, SEEN FROM THE TOP')
cols_ = {'CS': AMBT, 'SCLK': AMBT, 'SDO': AMBT, 'WAKE_N': '#d3e3f3', 'BIG_N': '#d3e3f3', 'GND': '#e6e6e0', '+3V3_PMOD': '#cfe8cf'}
nm_ = {'+3V3_PMOD': '3V3'}
for n_, (net, r_, c_, pm_) in PMOD.items():
    x_ = 24 + (c_ - 1) * 34
    y_ = 36 + (r_ - 1) * 7.0
    pg.cell(x_, y_, 30, 6.2, f'{pm_}  {nm_.get(net, net)}', cols_[net], PUR, 2.6, True)
pg.text(39, 33.5, 'left column', 2.4, MUTED, 'middle'); pg.text(73, 33.5, 'right column', 2.4, MUTED, 'middle')
for r_ in range(1, 7):
    for c_ in (1, 2):
        n_ = 2 * (r_ - 1) + c_
        if n_ not in PMOD:
            x_ = 24 + (c_ - 1) * 34
            y_ = 36 + (r_ - 1) * 7.0
            pg.cell(x_, y_, 30, 6.2, f'{r_ if c_ == 1 else r_ + 6}  not used', '#fff', '#bbb', 2.4)
pg.text(108, 44, 'The number is the', 2.5, MUTED, 'start')
pg.text(108, 48.4, 'PMOD pin. Row 1 holds', 2.5, MUTED, 'start')
pg.text(108, 52.8, 'pin 1 and pin 7.', 2.5, MUTED, 'start')

# 26 --------------------------------------------------------------------------------------------
tb = 1 / 60e6
pg = step('Why 22 Ω in each line',
          ['R18, R19 and R20 sit in the CS, SCLK and SDO lines at the ADC. Together with the small capacitance of the trace and the pin they slow the edge of the FPGA output a little and damp ringing.',
           f'The cost in speed is tiny. 22 Ω with about 10 pF (ESTIMATE) gives 0.2 ns, and one bit at 60 MHz lasts {tb*1e9:.1f} ns.'])
chip(pg, label='SERIES RESISTOR')
pbox(pg, 2, 38, 16, 44, 'FPGA', ['PMOD'], 'ext', 2.8, 2.4)
pbox(pg, 112, 38, 24, 44, 'ADS7057', [], 'mem', 2.8, 2.4)
for k_, (nm, r_, d_) in enumerate((('CS', 'R18', 1), ('SCLK', 'R19', 1), ('SDO', 'R20', -1))):
    y_ = 46 + k_ * 14
    pg.line(18, y_, 48, y_, INK, 0.45)
    res_h(pg, 48, y_, 18, r_, '22 Ω')
    pg.line(66, y_, 112, y_, INK, 0.45)
    if d_ > 0:
        pg.arrow([(104, y_), (112, y_)])
    else:
        pg.arrow([(26, y_), (18, y_)])
    pg.text(88, y_ - 2.4, nm, 2.5, INK, 'middle', True)
for r_, nm in (('R18', 'CS'), ('R19', 'SCLK'), ('R20', 'SDO')):
    assert val(r_) == 22

# 27 --------------------------------------------------------------------------------------------
pg = step('What one frame looks like',
          ['A **frame** starts when CS falls. The ADC samples at that moment. The host then sends 18 clock pulses. On SDO the ADC answers with a leading 0, then 14 data bits, most significant bit first, then three zeros.',
           'After the 18th clock the ADC converts nothing more. CS goes high and the ADC acquires the next sample for at least 95 ns.'])
chip(pg, label='ONE FRAME')
xL, wL = 22, 112
pg.text(18, 46, 'CS', 2.6, MUTED, 'end', True)
sq_wave(pg, xL, 41, wL, 6, [1] + [0] * 8 + [1])
pg.text(18, 61, 'SCLK', 2.6, MUTED, 'end', True)
sq_wave(pg, xL + wL / 10, 56, wL * 0.8, 6, [0, 1] * 18)
pg.text(18, 76, 'SDO', 2.6, MUTED, 'end', True)
data_lane(pg, xL + wL / 10, 71, wL * 0.8, 6, ['0'] + [f'D{k}' for k in range(13, -1, -1)] + ['0', '0', '0'], size=2.2)
pg.line(xL + wL / 10, 38, xL + wL / 10, 80, RED, 0.35, '0.8,0.6')
pg.text(xL + wL / 10 + 1.5, 38.2, 'sample taken', 2.4, RED, 'start', True)
pg.text(xL + wL * 0.9 + 1, 66, '18 clocks', 2.5, INK, 'end', True)

# 28 --------------------------------------------------------------------------------------------
pg = step('Why the data is one frame late',
          ['The ADC uses the clocks of a frame to send the result of the **previous** conversion. The conversion of the current sample runs inside the same frame, and its result waits for the next one.',
           'So the first frame after power-up returns all zeros, and every later frame returns the sample that was taken one frame before.'])
chip(pg, label='THREE FRAMES')
labs_ = [('frame 1', 'takes sample 1', 'returns 0000'), ('frame 2', 'takes sample 2', 'returns code of sample 1'), ('frame 3', 'takes sample 3', 'returns code of sample 2')]
for k_, (a_, b_, c_) in enumerate(labs_):
    x_ = 4 + k_ * 45
    pg.rect(x_, 40, 42, 32, BONE2, 'none', 0, 2)
    pg.text(x_ + 21, 47, a_, 2.9, CANOPY, 'middle', True)
    pg.cell(x_ + 3, 51, 36, 6.2, b_, AMBT, PUR, 2.5, True)
    pg.cell(x_ + 3, 61, 36, 6.2, c_, '#d3e3f3', BLU, 2.4, True)
for k_ in range(2):
    pg.arrow([(4 + k_ * 45 + 39, 54), (4 + (k_ + 1) * 45 + 3, 64)], RED, 0.45, '1.2,0.8')

# 29 --------------------------------------------------------------------------------------------
F_SPI = 20e6
tcal = 24 / F_SPI + 95e-9
pg = step('What happens at power-up',
          ['The datasheet recommends an offset calibration at power-up. The host does it by sending **24** clocks in the first frame, not 18. The ADC then disconnects its input, corrects its own offset and sends zeros.',
           f'At a 20 MHz clock this first frame takes {24/F_SPI*1e9:.0f} ns plus 95 ns of acquisition, so {tcal*1e9:.0f} ns. Repeat it when AVDD or the temperature changes a lot.'])
chip(pg, label='FIRST FRAME')
xL, wL = 22, 112
pg.text(18, 46, 'CS', 2.6, MUTED, 'end', True)
sq_wave(pg, xL, 41, wL, 6, [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
pg.text(18, 61, 'SCLK', 2.6, MUTED, 'end', True)
sq_wave(pg, xL + wL / 11, 56, wL * 0.82, 6, [0, 1] * 24)
pg.text(xL + wL * 0.45, 53, '24 clocks', 2.6, RED, 'middle', True)
pg.text(18, 76, 'SDO', 2.6, MUTED, 'end', True)
data_lane(pg, xL + wL / 11, 71, wL * 0.82, 6, ['0'] * 24, BONE2, size=2.2)
pg.text(xL + wL * 0.5, 82, 'zeros while the offset is calibrated', 2.5, MUTED, 'middle')

# 30 --------------------------------------------------------------------------------------------
def rate(f):
    return min(2.5e6, 1 / (18 / f + 95e-9))
rows_ = [(10e6, rate(10e6)), (20e6, rate(20e6)), (25e6, rate(25e6)), (40e6, rate(40e6)), (60e6, rate(60e6))]
assert abs(rate(25e6) - 1.2e6) < 0.1e6 and abs(rate(60e6) - 2.5e6) < 1
pg = step('How fast the link can go',
          ['One sample costs 18 clock periods plus 95 ns. So the sample rate is set by SCLK. The datasheet allows up to 60 MHz, which gives the full 2.5 MSPS.',
           'There are no level shifters on this board, so the FPGA drives the ADC pins directly at 3.3 V. Start at 10 to 20 MHz and raise the clock when the first test works.'])
chip(pg, label='SAMPLE RATE AGAINST SCLK')
pg.text(8, 40, 'SCLK', 2.6, MUTED, 'start', True); pg.text(44, 40, 'one sample', 2.6, MUTED, 'start', True); pg.text(88, 40, 'sample rate', 2.6, MUTED, 'start', True)
for k_, (f_, r_) in enumerate(rows_):
    y_ = 43 + k_ * 7.4
    pg.rect(4, y_, 130, 6.4, BONE2 if k_ % 2 == 0 else '#fff', 'none', 0)
    pg.text(8, y_ + 4.5, f'{f_/1e6:.0f} MHz', 2.7, INK, 'start', True)
    pg.text(44, y_ + 4.5, f'{(18/f_+95e-9)*1e9:.0f} ns', 2.7, INK, 'start')
    pg.text(88, y_ + 4.5, f'{r_/1e6:.2f} MSPS', 2.7, INK, 'start', True)
