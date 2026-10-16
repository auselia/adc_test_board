"""Hardware manual, part B: section 1 (power and references, steps 1 to 6) and section 2 (the signal path, steps 7 to 16)."""
import m4lib
from adc_common import *

# ================================================================================================
# SECTION 1: POWER AND REFERENCES
# ================================================================================================
section('POWER AND REFERENCES', 'Power and references', 'Section 1', 'Steps 1 to 6',
        'How 3.3 V comes in from the ZedBoard PMOD alone, how the four links split it, how AVDD is filtered and how the 1.65 V mid-rails are made. '
        'Everything else on the board rests on these rails.', active=['Power', 'Mid-rails'])

# 1 ---------------------------------------------------------------------------------------------
pg = step('How 3.3 V comes in',
          ['The board takes all its power from the ZedBoard PMOD. Pins 6 and 12 of J3 carry 3.3 V, and pins 5 and 11 carry ground. There is no USB, no regulator and no diode. The solder jumper JP6 joins the PMOD pins to the board rail +3V3.',
           'To run the board on the bench without a ZedBoard, cut JP6 and feed 3.3 V to the 2-pin header J7. Never feed both at once.'])
chip(pg, label='INPUT PATH')
pbox(pg, 2, 40, 28, 14, 'PMOD J3', ['pins 6 and 12'], 'ext')
pbox(pg, 2, 62, 28, 14, 'Header', ['J7, 3.3 V'], 'ext')
pbox(pg, 52, 40, 22, 14, 'JP6', ['solder link'], 'arith')
pbox(pg, 104, 51, 30, 14, '+3V3', ['C23, 10 µF'], 'bus')
pg.arrow([(30, 47), (52, 47)])
pg.line(74, 47, 90, 47, INK, 0.5); pg.line(90, 47, 90, 58, INK, 0.5); pg.arrow([(90, 58), (104, 58)])
pg.line(30, 69, 90, 69, INK, 0.5); pg.line(90, 69, 90, 58, INK, 0.5)
pg.text(62, 82, 'one source at a time: PMOD or header', 2.5, MUTED, 'middle')
assert ('JP6', '1') in NET['+3V3_PMOD'] and ('JP6', '2') in NET['+3V3'] and ('J7', '1') in NET['+3V3'] and ('J3', '11') in NET['+3V3_PMOD']

# 2 ---------------------------------------------------------------------------------------------
pg = step('Why the four links JP2 to JP5',
          ['Four solder jumpers split the 3.3 V into the rails that the blocks use. JP2 feeds the listener (+3V3_L), JP3 the capture chain (+3V3_C), JP4 the ADC reference path (AVDD) and JP5 the ADC logic (DVDD). All four are closed. The board is always on.',
           'To measure the current of one block, cut its jumper with a knife and solder a 2-pin header or an ammeter across the gap. Close the jumper with a drop of solder when you are done.'])
chip(pg, label='RAILS AND LINKS')
pbox(pg, 2, 54, 22, 14, '+3V3', [], 'bus')
rows_l = [('JP2', '+3V3_L', 'listener', 38), ('JP3', '+3V3_C', 'U1, U2, U3', 50), ('JP4', 'AVDD', 'ADC reference, after JP3', 62), ('JP5', 'DVDD', 'ADC logic', 74)]
pg.line(24, 61, 34, 61, INK, 0.5); pg.line(34, 42, 34, 78, INK, 0.5)
for nm, rail, who, yy in rows_l:
    pg.arrow([(34, yy + 4), (46, yy + 4)])
    pbox(pg, 46, yy - 1.5, 18, 11, nm, [], 'arith', 2.6, 2.2)
    pg.arrow([(64, yy + 4), (76, yy + 4)])
    pg.text(78, yy + 3.2, f'{rail}   {who}', 2.5, INK, 'start', True)
for nm, rail, who, yy in rows_l:
    assert (nm, '1') in NET['+3V3'] or (nm, '1') in NET['+3V3_C'] or (nm, '1') in NET['AVDD_IN'] or (nm, '1') in NET['+3V3']

# 3 ---------------------------------------------------------------------------------------------
R_A, C_A = val('R34'), val('C21')
f_a = 1 / (2 * math.pi * R_A * C_A)
a_250 = 1 / math.sqrt(1 + (250e3 / f_a) ** 2)
pg = step('Where the ADC reference comes from',
          ['The ADS7057 uses its supply pin AVDD as its reference. Full scale is ±AVDD, so noise on AVDD is noise in every code.',
           f'There is no second regulator. AVDD comes from the rail through JP4, a 10 Ω resistor (R34) and 10 µF (C21). That RC has a corner at {f_a:.0f} Hz and removes {-db(a_250):.0f} dB at 250 kHz (ESTIMATE). The 4.7 µF C18 and the 100 nF C22 sit at the ADC pin.'])
chip(pg, label='AVDD PATH')
pbox(pg, 2, 40, 22, 18, '+3V3_C', [], 'bus')
pbox(pg, 100, 40, 36, 18, 'ADS7057', ['pin 6, AVDD'], 'mem')
pg.arrow([(24, 49), (34, 49)])
pbox(pg, 34, 43, 14, 12, 'JP4', [], 'arith', 2.6, 2.2)
pg.line(48, 49, 56, 49, INK, 0.5)
res_h(pg, 56, 49, 12, 'R34', '10 Ω')
pg.line(68, 49, 100, 49, INK, 0.5)
pg.arrow([(96, 49), (100, 49)])
for k_, (nm, v_, xx) in enumerate((('C21', '10 µF', 74), ('C18', '4.7 µF', 88), ('C22', '100 nF', 120))):
    pg.line(xx, 49, xx, 61, INK, 0.45)
    cap_v(pg, xx, 61, 7)
    gnd(pg, xx, 68)
    pg.text(xx, 80, nm, 2.5, INK, 'middle', True)
    pg.text(xx, 84.2, v_, 2.5, INK, 'middle')
    dot(pg, xx, 49)
pg.text(60, 36, 'AVDD 3.3 V', 2.8, GRN, 'middle', True)
assert ('C18', '1') in NET['AVDD'] and ('C22', '1') in NET['AVDD'] and ('C21', '1') in NET['AVDD'] and ('R34', '2') in NET['AVDD']

# 4 ---------------------------------------------------------------------------------------------
tau = (val('R7') * val('R8') / (val('R7') + val('R8'))) * val('C7')
assert abs(tau - 5e-3) < 1e-9
pg = step('How the 1.65 V mid-rail VMID5 is made',
          [f'Two 10 kΩ resistors (R7, R8) divide the capture rail +3V3_C in half, {MID:.2f} V. The 1 µF capacitor C7 smooths it. The op-amp U2B then copies this voltage and drives the rail called **VMID5**.',
           f'The divider and C7 form an RC of {tau*1e3:.0f} ms, so VMID5 needs about {5*tau*1e3:.0f} ms to settle after power-up. R9 (10 Ω) and C8 (10 µF) keep the buffer calm.'])
chip(pg, label='SETTLING AFTER POWER-UP')
X0, Y0, W_, H_ = 14, 38, 106, 38
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
tt = [i * 30e-3 / 60 for i in range(61)]
yv = lambda v: Y0 + H_ - v / 1.9 * H_
MID_ = MID
tx = lambda t: X0 + t / 30e-3 * W_
pg.poly([(tx(t), yv(MID_ * (1 - math.exp(-t / tau)))) for t in tt], PUR, 0.8)
pg.line(X0, yv(MID_), X0 + W_, yv(MID_), '#888', 0.3, '1.2,0.8')
pg.text(X0 + W_ + 1, yv(MID_) + 0.9, f'{MID_:.2f} V', 2.5, MUTED, 'start')
pg.line(tx(tau), Y0 + H_, tx(tau), yv(MID_ * (1 - math.exp(-1))), RED, 0.3, '1,0.8')
pg.text(tx(tau), Y0 + H_ + 4, f'τ = {tau*1e3:.0f} ms', 2.5, RED, 'middle', True)
pg.line(tx(5 * tau), Y0 + H_, tx(5 * tau), yv(MID_ * (1 - math.exp(-5))), RED, 0.3, '1,0.8')
pg.text(tx(5 * tau), Y0 + H_ + 4, f'{5*tau*1e3:.0f} ms', 2.5, RED, 'middle', True)
pg.text(X0 + W_ / 2, Y0 + H_ + 8.4, 'time after power-up', 2.5, MUTED, 'middle')

# 5 ---------------------------------------------------------------------------------------------
pg = step('How the 1.65 V mid-rail VOCM is made',
          ['Two 1 kΩ resistors (R14, R15) divide **AVDD** in half, and C13 smooths the result. This voltage, VOCM, tells the THS4531 where to centre its two outputs. It is a second 1.65 V rail, separate from VMID5.',
           'The datasheet asks for the ADC inputs to rest at AVDD/2, within ±0.1 V. The divider follows AVDD by ratio, so any change of AVDD moves VOCM with it.'])
chip(pg, label='VOCM')
pg.text(8, 40, 'AVDD  3.3 V', 2.8, GRN, 'start', True)
pg.line(14, 42, 14, 47, INK, 0.45)
res_v(pg, 14, 47, 12, 'R14', '1 kΩ')
dot(pg, 14, 59)
pg.line(14, 59, 50, 59, INK, 0.45)
res_v(pg, 14, 59, 12, None, None)
pg.text(18, 66, 'R15 1 kΩ', 2.5, INK, 'start', True)
gnd(pg, 14, 71)
pg.line(36, 59, 36, 66, INK, 0.45)
cap_v(pg, 36, 66, 7, 'C13', '1 µF')
gnd(pg, 36, 73)
pg.text(50, 57.5, 'VOCM = 1.65 V', 2.8, BLU, 'start', True)
pg.line(86, 44, 86, 78, '#aaa', 0.3, '1.2,0.8')
pg.rect(90, 46, 40, 30, BONE2, 'none', 0, 1.5)
pg.text(110, 52, 'allowed window', 2.5, MUTED, 'middle', True)
pg.text(110, 61, '1.55 to 1.75 V', 2.9, INK, 'middle', True)
pg.text(110, 69, 'AVDD/2 ± 0.1 V', 2.5, MUTED, 'middle')
assert ('R14', '1') in NET['AVDD'] and ('R15', '2') in NET['GND'] and ('C13', '1') in NET['VOCM']

# 6 ---------------------------------------------------------------------------------------------
LOADS = [('OPA2365, 4 channels', 4 * 4.6), ('Sensor head', 4.7), ('VOCM divider', AVDD / (val('R14') + val('R15')) * 1e3),
         ('ADS7057 AVDD', 1.1), ('THS4531', 0.25), ('VMID5 divider', RAIL / (val('R7') + val('R8')) * 1e3),
         ('Listener, 2 × TLV7022', 4 * 0.005 + RAIL / (val('R21') + val('R22') + val('R39') + val('R40') + val('R41') + val('R23')) * 1e3)]
I_BAT = sum(v for _, v in LOADS)
pg = step('How much current, and where to probe',
          [f'The board draws about {I_BAT:.0f} mA from the 3.3 V of the PMOD (ESTIMATE from datasheet typical values). The four op-amp channels and the sensor head are the largest parts. The listener is only about 25 µA.',
           'Every stage has a test point. The list below names the rails. The four links of step 2 let you check each block alone.'])
chip(pg, label='ESTIMATE, mA')
x_ = 4
tot = sum(v for _, v in LOADS)
cols = [PUR, GRN, BLU, '#0e6e7a', '#d89cc8', '#4f86c6', '#8a6fb0', '#bbbbbb']
for (nm, v_), c_ in zip(LOADS, cols):
    w_ = 132 * v_ / tot
    pg.rect(x_, 38, w_, 9, c_, 'none', 0)
    x_ += w_
for k_, ((nm, v_), c_) in enumerate(zip(LOADS, cols)):
    col, row = k_ % 2, k_ // 2
    xx, yy = 4 + col * 68, 53 + row * 5.6
    pg.rect(xx, yy - 2.6, 3.2, 3.2, c_, 'none', 0)
    pg.text(xx + 5, yy, f'{nm}  {v_:.2g}', 2.5, INK, 'start')
tp = [('+3V3', 'TP11'), ('AVDD', 'TP12'), ('VMID5', 'TP13'), ('VOCM', 'TP14'), ('LST', 'TP15'), ('GND', 'TP19, TP20')]
assert ('TP11', '1') in NET['+3V3'] and ('TP12', '1') in NET['AVDD'] and ('TP13', '1') in NET['VMID5'] and ('TP14', '1') in NET['VOCM'] and ('TP15', '1') in NET['LST']
for k_, (a_, b_) in enumerate(tp):
    xx, yy = 4 + (k_ % 3) * 46, 78 + (k_ // 3) * 6
    pg.text(xx, yy, a_, 2.6, CANOPY, 'start', True)
    pg.text(xx + 16, yy, b_, 2.6, INK, 'start')

# ================================================================================================
# SECTION 2: THE SIGNAL PATH
# ================================================================================================
section('THE SIGNAL PATH', 'The signal path', 'Section 2', 'Steps 7 to 16',
        'From the SMA connector to the output of the low-pass filter: input coupling, high-pass, gain, low-pass, '
        'the total response, headroom, the SCOPE OUT tap and the op-amps.', active=['Input', 'High-pass', 'Gain', 'Low-pass', 'Scope out'])

# 7 ---------------------------------------------------------------------------------------------
pg = step('How the signal gets in',
          ['The sensor head reaches J1 through a coax cable. The head has its own 49.9 Ω output resistor. The same cable carries the 3.3 V that powers the head, so the centre pin of J1 sits near 3 V.',
           'So the first part is a 100 nF capacitor, C33. It passes the 250 kHz burst and blocks the DC level. A 1 MΩ resistor R27 to VMID5 sets the DC level of the next node, and C1 continues to the high-pass.'])
chip(pg, label='INPUT')
pg.rect(2, 44, 24, 18, '#fff', INK, 0.5, 1.5)
pg.text(14, 51, 'sensor head', 2.7, INK, 'middle', True)
pg.text(14, 56, 'on 3.3 V coax', 2.5, MUTED, 'middle')
res_h(pg, 26, 53, 14, 'Rs', '50 Ω')
pg.line(40, 53, 50, 53, INK, 0.5)
pbox(pg, 50, 46, 16, 14, 'J1', ['SMA'], 'ext')
pg.line(66, 53, 74, 53, INK, 0.5)
cap_h(pg, 74, 53, 12, 'C1', '100 pF')
pg.line(86, 53, 104, 53, INK, 0.5)
pg.text(112, 53.9, 'to the', 2.5, MUTED, 'middle')
pg.text(112, 58.4, 'high-pass', 2.5, MUTED, 'middle')
pg.arrow([(98, 53), (104, 53)])
xc = 1 / (2 * math.pi * 250e3 * val('C1'))
pg.text(80, 76, f'at 250 kHz, C1 is {xc/1e3:.1f} kΩ. At DC it is open.', 2.6, INK, 'middle', True)

# 8 ---------------------------------------------------------------------------------------------
pg = step('How the high-pass works',
          ['The high-pass is a **Sallen-Key** stage: two capacitors in series, two resistors and one op-amp used as a buffer. Low frequencies cannot pass the capacitors.',
           ('tex', r'f_0 = \frac{1}{2\pi C \sqrt{R_1 R_2}}, \qquad Q = \frac{1}{2}\sqrt{\frac{R_2}{R_1}}', 9.0),
           f'With C = 100 pF, R1 = 10 kΩ and R2 = 20 kΩ, the corner is {HP_F0/1e3:.1f} kHz. Q is {HP_Q:.2f}. That is a maximally flat response.'])
chip(pg, label='SALLEN-KEY HIGH-PASS')
yb = 62
pg.text(2, yb - 2, 'in', 2.6, MUTED, 'start')
pg.line(8, yb, 10, yb, INK, 0.5)
cap_h(pg, 10, yb, 14, 'C1', None)
dot(pg, 24, yb)
cap_h(pg, 24, yb, 14, 'C2', None)
pg.line(38, yb, 50, yb, INK, 0.5)
pp, pm, out = opamp(pg, 50, yb - 4, 16, 14, 'U1A', plus_top=True)
dot(pg, 38, yb)
pg.line(38, yb, 38, yb + 6, INK, 0.45)
res_v(pg, 38, yb + 6, 12, 'R2', '20 kΩ')
pg.text(42, yb + 23.4, 'to VMID5', 2.5, MUTED, 'start')
pg.line(50, yb - 0.5, 46, yb - 0.5, INK, 0.45)
pg.line(46, yb - 0.5, 46, yb - 14, INK, 0.45)
pg.line(46, yb - 14, 82, yb - 14, INK, 0.45)
pg.line(82, yb - 14, 82, yb - 4, INK, 0.45)
pg.line(66, yb - 4, 94, yb - 4, INK, 0.45)
pg.arrow([(90, yb - 4), (94, yb - 4)])
dot(pg, 82, yb - 4)
pg.line(24, yb, 24, yb - 14, INK, 0.45)
pg.line(24, yb - 14, 46, yb - 14, INK, 0.45)
pg.text(26, yb - 16, 'R1 10 kΩ, to the output', 2.5, INK, 'start', True)
pg.text(17, yb + 9, 'C1 = C2 = 100 pF', 2.5, INK, 'middle', True)
pg.text(98, yb - 3, f'f0 {HP_F0/1e3:.1f} kHz', 2.8, PUR, 'start', True)
pg.text(98, yb + 2.5, f'Q {HP_Q:.2f}', 2.8, PUR, 'start', True)
assert NET['HP_A'] and ('R1', '1') in NET['HP_A'] and ('R1', '2') in NET['HPF_OUT']

# 9 ---------------------------------------------------------------------------------------------
lo = sorted(b['low'] for b in __import__('json').load(open(os.path.join(DATA, 'events.json')))['baselines'])
hp = SIM['hpf']
loss10 = db(at(hp, 10e3) / at(hp, 250e3))
pg = step('Why the corner is at 113 kHz',
          [f'Most noise on the perfboard sits below 100 kHz, from {lo[0]} to {lo[-1]} mV rms. The AE band starts at 100 kHz and holds only about 4 mV rms.',
           f'So the high-pass sits just under the band. At 10 kHz it already removes {abs(loss10):.0f} dB of this stage alone. A corner any higher would also cut the events.'])
chip(pg, label='SIMULATION, HIGH-PASS STAGE ONLY')
X0, Y0, W_, H_ = 12, 36, 112, 40
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
ydb = [db(max(v / at(hp, 250e3), 1e-6)) for v in hp]
curve(pg, X0, Y0, W_, H_, F, ydb, 1e3, 5e6, -60, 6, PUR, 0.8)
yy_ = lambda d: Y0 + H_ - (d + 60) / 66 * H_
pg.rect(X0 + math.log10(1e5 / 1e3) / math.log10(5e3) * W_, Y0, math.log10(5) / math.log10(5e3) * W_, H_, LPK, 'none', opacity=0.6)
pg.text(X0 + math.log10(1.6e5 / 1e3) / math.log10(5e3) * W_, Y0 + 5, 'AE band', 2.5, PUR, 'middle', True)
freq_axis(pg, X0, Y0 + H_, W_, 1e3, 5e6, [1e3, 1e4, 1e5, 1e6])
for d_ in (0, -20, -40, -60):
    pg.text(X0 - 1.5, yy_(d_) + 0.9, d_, 2.5, MUTED, 'end')
pg.text(X0 + 2, Y0 + H_ + 8.5, 'dB relative to 250 kHz', 2.5, MUTED, 'start')

# 10 --------------------------------------------------------------------------------------------
pg = step('How the gain is set',
          ['The second half of U1 is a non-inverting amplifier. Its gain comes from two resistors: R3 from the output back to the minus input, and R4 from that input to VMID5.',
           ('tex', r'G = 1 + \frac{R_3}{R_4} = 1 + \frac{3.9\,\mathrm{k\Omega}}{1\,\mathrm{k\Omega}} = 4.9', 9.0),
           'Because R4 goes to VMID5 and not to ground, the gain is 1 for DC. The stage output rests at 1.65 V, and the gain applies only to the burst.'])
chip(pg, label='GAIN 4.9')
yb = 60
pp, pm, out = opamp(pg, 40, yb, 20, 16, 'U1B', plus_top=False)
pg.line(10, yb + 4, 40, yb + 4, INK, 0.5)
pg.text(2, yb + 5, 'in', 2.6, MUTED, 'start')
dot(pg, 34, yb - 4)
pg.line(34, yb - 4, 40, yb - 4, INK, 0.45)
pg.line(34, yb - 4, 34, yb - 16, INK, 0.45)
pg.line(34, yb - 16, 44, yb - 16, INK, 0.45)
res_h(pg, 44, yb - 16, 18, 'R3', '3.9 kΩ')
pg.line(62, yb - 16, 72, yb - 16, INK, 0.45)
pg.line(72, yb - 16, 72, yb, INK, 0.45)
dot(pg, 72, yb)
pg.line(60, yb, 90, yb, INK, 0.5)
pg.arrow([(86, yb), (92, yb)])
pg.line(34, yb - 4, 24, yb - 4, INK, 0.45)
res_v(pg, 24, yb - 14, 10, 'R4', '1 kΩ', left=True)
pg.text(24, yb - 17, 'to VMID5', 2.5, MUTED, 'middle')
pg.text(98, yb + 0.9, f'× {GAIN:.1f}', 3.2, PUR, 'start', True)
pg.text(98, yb + 7, f'{db(GAIN):.1f} dB', 2.6, MUTED, 'start')
pg.text(98, yb + 13, f'bandwidth {50/GAIN:.0f} MHz', 2.5, MUTED, 'start')

# 11 --------------------------------------------------------------------------------------------
pg = step('How the low-pass works',
          ['The low-pass is also a Sallen-Key stage, with the parts swapped: two resistors in series and two capacitors. The capacitors give high frequencies a path to VMID5.',
           ('tex', r'f_0 = \frac{1}{2\pi R \sqrt{C_1 C_2}}, \qquad Q = \frac{1}{2}\sqrt{\frac{C_1}{C_2}}', 9.0),
           f'With R = 2.2 kΩ, C1 = 200 pF (C4 and C5 in parallel) and C2 = 100 pF (C6), the corner is {LP_F0/1e3:.0f} kHz. Q is {LP_Q:.2f}.'])
chip(pg, label='SALLEN-KEY LOW-PASS')
yb = 62
pg.line(6, yb, 8, yb, INK, 0.5)
pg.text(2, yb - 3, 'in', 2.6, MUTED, 'start')
res_h(pg, 8, yb, 14, 'R5', None)
dot(pg, 22, yb)
res_h(pg, 22, yb, 14, 'R6', None)
pg.line(36, yb, 46, yb, INK, 0.5)
pp, pm, out = opamp(pg, 46, yb - 4, 16, 14, 'U2A', plus_top=True)
dot(pg, 36, yb)
pg.line(36, yb, 36, yb + 6, INK, 0.45)
cap_v(pg, 36, yb + 6, 8, 'C6', '100 pF')
pg.text(40, yb + 21, 'to VMID5', 2.5, MUTED, 'start')
pg.line(46, yb - 0.5, 42, yb - 0.5, INK, 0.45)
pg.line(42, yb - 0.5, 42, yb - 14, INK, 0.45)
pg.line(42, yb - 14, 78, yb - 14, INK, 0.45)
pg.line(78, yb - 14, 78, yb - 4, INK, 0.45)
pg.line(62, yb - 4, 88, yb - 4, INK, 0.45)
dot(pg, 78, yb - 4)
pg.arrow([(84, yb - 4), (88, yb - 4)])
pg.line(22, yb, 22, yb - 14, INK, 0.45)
pg.line(22, yb - 14, 42, yb - 14, INK, 0.45)
pg.text(24, yb - 16, 'C4 and C5, 200 pF in parallel, to the output', 2.5, INK, 'start', True)
pg.text(15, yb + 8, 'R5 = R6 = 2.2 kΩ', 2.5, INK, 'middle', True)
pg.text(92, yb - 3, f'f0 {LP_F0/1e3:.0f} kHz', 2.8, PUR, 'start', True)
pg.text(92, yb + 2.5, f'Q {LP_Q:.2f}', 2.8, PUR, 'start', True)
assert ('C4', '1') in NET['LP_A'] and ('C5', '2') in NET['LPF_OUT'] and ('C6', '1') in NET['LP_B']

# 12 --------------------------------------------------------------------------------------------
adc = SIM['adc']
ref = at(adc, 250e3)
l10 = -db(at(adc, 10e3) / ref); l2m = -db(at(adc, 2e6) / ref)
nlow = sum(1 for x in LOSS10 if x < 40)
pg = step('The total response',
          [f'Put the three stages together and add the 50 Ω source. The simulation, with TI\'s own OPA365 model, gives {db(ref):.1f} dB of gain at 250 kHz. That is ×{ref:.1f}, a little below the ideal ×4.9.',
           f'The loss at 10 kHz is {l10:.1f} dB against a target of 40 dB. With part tolerances {nlow} of 150 runs fall under 40 dB, the worst at {min(LOSS10):.1f} dB.'])
chip(pg, label='SIMULATION, SMA TO ADC')
X0, Y0, W_, H_ = 12, 36, 112, 42
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
yd = lambda d: Y0 + H_ - (d + 50) / 60 * H_
ydb = [db(max(v / ref, 1e-6)) for v in adc]
curve(pg, X0, Y0, W_, H_, F, ydb, 1e3, 2e7, -50, 10, PUR, 0.9)
fxx = lambda f: X0 + math.log10(f / 1e3) / math.log10(2e4) * W_
pg.rect(fxx(230e3), yd(1), fxx(280e3) - fxx(230e3), yd(-1) - yd(1), AMBT, AMB, 0.3)
pg.circle(fxx(10e3), yd(-40), 1.3, RED, 'none')
pg.text(fxx(10e3) + 2, yd(-40) + 5, '≥ 40 dB at 10 kHz', 2.5, RED, 'start', True)
pg.circle(fxx(2e6), yd(-20), 1.3, RED, 'none')
pg.text(fxx(2e6) + 3, yd(-20) - 1.5, '≥ 20 dB at 2 MHz', 2.5, RED, 'start', True)
freq_axis(pg, X0, Y0 + H_, W_, 1e3, 2e7, [1e3, 1e4, 1e5, 1e6, 1e7])
for d_ in (0, -20, -40):
    pg.text(X0 - 1.5, yd(d_) + 0.9, d_, 2.5, MUTED, 'end')
pg.text(X0 + 2, Y0 + H_ + 8.5, 'dB relative to 250 kHz', 2.5, MUTED, 'start')

# 13 --------------------------------------------------------------------------------------------
bur = SIM['burst']
pk = {k: (max(v['gout']) - min(v['gout'])) / 2 for k, v in bur.items()}
gpk = pk['0.12'] / 0.12                      # V per V at the 3.3 V stages for a 250 kHz burst
clip_at = (MID - 0.1) / gpk
assert 0.25 < clip_at < 0.5
pct = {k: max(max(v['adc']), -min(v['adc'])) / AVDD * 100 for k, v in bur.items()}
pg = step('What clips first',
          [f'The 3.3 V stages are the narrowest part of the path. They can swing about {MID - 0.1:.2f} V either side of {MID:.2f} V. A burst clips there when it is larger than {clip_at:.2f} V at the sensor head output.',
           f'A typical recorded event is 120 mV, so the margin is {clip_at/0.12:.1f}×. At the ADC that event fills {pct["0.12"]:.0f} % of the full scale.'])
chip(pg, label='SIMULATION, 3 BURSTS')
X0, Y0, W_, H_ = 14, 38, 100, 40
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
yg = lambda v: Y0 + H_ - v / 3.3 * H_
for lim in (0.1, RAIL - 0.1):
    pg.line(X0, yg(lim), X0 + W_, yg(lim), RED, 0.35, '1.2,0.8')
pg.text(X0 + W_ + 1.5, yg(RAIL - 0.1) + 0.9, 'rail', 2.5, RED, 'start')
for (k, v), c_ in zip(bur.items(), (PUR, '#6b2d86', BLU)):
    tt = v['t']; gg = v['gout']
    pts = [(X0 + (t - 4e-6) / 41e-6 * W_, yg(g)) for t, g in zip(tt, gg) if t >= 4e-6]
    pg.poly(pts, c_, 0.5)
    ki = list(bur).index(k)
    pg.line(X0 + W_ + 3, Y0 + 14 + ki * 6, X0 + W_ + 9, Y0 + 14 + ki * 6, c_, 0.9)
    pg.text(X0 + W_ + 11, Y0 + 15 + ki * 6, f'{float(k)*1e3:.0f} mV', 2.5, c_, 'start', True)
for v_ in (0, 1.65, 3.3):
    pg.text(X0 - 1.5, yg(v_) + 0.9, v_, 2.5, MUTED, 'end')
pg.text(X0 + W_ / 2, Y0 + H_ + 5, 'time, 40 µs', 2.5, MUTED, 'middle')
pg.text(2, Y0 - 3, 'GAIN_OUT, V', 2.5, MUTED, 'start')

# 14 --------------------------------------------------------------------------------------------
pg = step('What SCOPE OUT is for',
          ['J4 gives the scope the same signal that the ADC sees, taken at the output of the low-pass. A 51 Ω resistor (R25) sits between the op-amp and the connector.',
           'The resistor keeps the cable capacitance away from the op-amp, so the filter cannot ring. Use the 1 MΩ input of the scope. A 50 Ω input would form a divider with R25 and halve the signal.'])
chip(pg, label='CABLE LOAD')
pg.text(2, 44, 'LPF_OUT', 2.6, MUTED, 'start', True)
pg.line(18, 50, 28, 50, INK, 0.5)
dot(pg, 22, 50)
res_h(pg, 28, 50, 14, 'R25', '51 Ω')
pbox(pg, 46, 43, 14, 14, 'J4', ['SMA'], 'ext')
pg.line(60, 50, 74, 50, INK, 0.5)
pg.text(67, 46, 'cable', 2.5, MUTED, 'middle')
pg.rect(74, 42, 24, 16, '#fff', INK, 0.5, 1.5)
pg.text(86, 51, 'scope', 2.7, INK, 'middle', True)
pg.text(86, 55.4, '1 MΩ', 2.5, MUTED, 'middle')
pg.line(22, 50, 22, 66, INK, 0.45)
pg.line(22, 66, 100, 66, INK, 0.45)
pg.text(104, 66.9, 'to the filter output, U2A', 2.5, MUTED, 'start')
pg.text(70, 78, f'1 MΩ input: {SIM["mon"][F.index(min(F, key=lambda f: abs(f-250e3)))] / SIM["lpf"][F.index(min(F, key=lambda f: abs(f-250e3)))]:.3f} of LPF_OUT.  50 Ω input: {50/(50+51):.2f}', 2.6, INK, 'middle', True)

# 15 --------------------------------------------------------------------------------------------
pg = step('What the OPA2365 does here',
          ['Two dual op-amps, U1 and U2, do all the active filtering. The OPA2365 is rail-to-rail on input and output and runs from 2.2 to 5.5 V. Its gain-bandwidth is 50 MHz and its noise is 4.5 nV/√Hz.',
           'Each package holds two channels. The table shows which stage uses which channel.'])
chip(pg, label='SOIC-8, TOP VIEW')
pg.rect(8, 38, 26, 30, '#fff', INK, 0.6, 1.0)
pg.circle(13, 42, 1.0, INK)
names = [('1', 'OUTA'), ('2', '−INA'), ('3', '+INA'), ('4', 'V−'), ('5', '+INB'), ('6', '−INB'), ('7', 'OUTB'), ('8', 'V+')]
for k_, (n_, nm) in enumerate(names[:4]):
    y_ = 43 + k_ * 7
    pg.line(3, y_, 8, y_, INK, 0.5)
    pg.text(2, y_ - 1.2, nm, 2.4, INK, 'end', True)
    pg.text(10, y_ + 0.9, n_, 2.3, MUTED, 'start')
for k_, (n_, nm) in enumerate(names[4:]):
    y_ = 64 - k_ * 7
    pg.line(34, y_, 39, y_, INK, 0.5)
    pg.text(40, y_ - 1.2, nm, 2.4, INK, 'start', True)
    pg.text(31, y_ + 0.9, n_, 2.3, MUTED, 'end')
rows_ = [('U1A  pins 1 2 3', 'high-pass buffer'), ('U1B  pins 5 6 7', 'gain × 4.9'), ('U2A  pins 1 2 3', 'low-pass buffer'), ('U2B  pins 5 6 7', 'VMID5 buffer')]
for k_, (a_, b_) in enumerate(rows_):
    y_ = 42 + k_ * 9
    pg.rect(66, y_, 66, 7.4, BONE2 if k_ % 2 == 0 else '#fff', 'none', 0)
    pg.text(69, y_ + 5.2, a_, 2.6, CANOPY, 'start', True)
    pg.text(98, y_ + 5.2, b_, 2.6, INK, 'start')

# 16 --------------------------------------------------------------------------------------------
sig_refs = ['C1', 'C2', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'C4', 'C5', 'C6', 'U1', 'U2', 'C3', 'C10', 'R7', 'R8', 'C7', 'R9', 'C8', 'C9', 'R25', 'J1', 'J4']
pg = step('Where these parts are',
          ['The signal parts sit in the top half of the board, from J1 on the left to U2 on the right. U1 holds the high-pass and the gain. U2 holds the low-pass and the VMID5 buffer.',
           'J4 and its resistor R25 stand in the top right corner, away from the ADC.'])
chip(pg, label='TOP VIEW, ACTIVE PARTS IN AMBER')
mini_map(pg, 2, 38, 78, sig_refs)
legend = [('Input and high-pass', 'C1 C2 R1 R2'), ('Gain', 'R3 R4'), ('Low-pass', 'R5 R6 C4 C5 C6'), ('Op-amps', 'U1 U2 C3 C10'), ('VMID5', 'R7 R8 C7 R9 C8 C9'), ('Connectors', 'J1 J4 R25')]
for k_, (a_, b_) in enumerate(legend):
    y_ = 40 + k_ * 8
    pg.text(86, y_, a_, 2.6, CANOPY, 'start', True)
    pg.text(86, y_ + 3.6, b_, 2.5, INK, 'start')
assert all(r in FP for r in sig_refs)
