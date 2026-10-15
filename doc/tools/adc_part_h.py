"""Hardware manual, part H: section 10, questions and answers (steps 61 to 69).
Each step answers one question that came up while studying the board."""
import m4lib
from adc_common import *

section('QUESTIONS AND ANSWERS', 'Why is it like this?', 'Section 10', 'Steps 61 to 69',
        'Nine questions that come up when you study the board: the differential head, the supply filter, '
        'the buffer, the gain, Q, noise density, power-up order, open-collector outputs and the test points.', active=None)

CP_, CF_ = 1.6e-9, val('C34')
GN = 1 + CP_ / CF_
B_ = 400e3                                                   # AE band, 100 to 500 kHz

# 61 --------------------------------------------------------------------------------------------
n365, n4531 = 4.5e-9, 10e-9                                   # DS: OPA365 at 100 kHz, THS4531 at 1 kHz
o365, o4531 = n365 * GN * math.sqrt(B_), n4531 * GN * math.sqrt(B_)
pg = step('Why is the head not differential?',
          ['A differential amplifier subtracts its two inputs. Pickup that hits both wires equally cancels. That works only if both faces of the piezo float. Today the minus face connects to ground, so the head is single-ended.',
           f'The THS4531 would add noise: {o4531*1e6:.0f} µV against {o365*1e6:.0f} µV at the output in the AE band (ESTIMATE). It also draws 160 nA of input bias current, which a 1 MΩ resistor turns into 0.16 V. The measured noise is 4 mV, so only a test shows if the wires or the plant cause it.'])
chip(pg, label='NOISE AT THE HEAD OUTPUT, 100 TO 500 kHz')
rows = [('OPA365, single-ended (now)', o365 * 1e6, PUR), ('THS4531, differential (option)', o4531 * 1e6, BLU), ('measured on the perfboard', 4000.0, '#8c8c8c')]
mx = 4000.0
for i, (nm, v_, c_) in enumerate(rows):
    yy = 42 + i * 11
    pg.text(2, yy + 5, nm, 2.6, INK, 'start', True)
    w_ = max(v_ / mx * 70, 0.8)
    pg.rect(62, yy, w_, 7, c_, 'none', 0)
    pg.text(62 + w_ + 2, yy + 5.2, f'{v_:.0f} µV' if v_ < 1000 else f'{v_/1000:.1f} mV', 2.6, INK, 'start', True)
pg.text(2, 82, 'Test: tie both piezo faces to a differential input and compare the noise with the plant touching the stem.', 2.4, MUTED, 'start')

# 62 --------------------------------------------------------------------------------------------
L_FB, ESR, R_SRC, C_EFF = 0.3e-6, 0.01, 0.6, 22e-6 * 0.75     # ESTIMATES: bead inductance, 22 uF ESR, cable + SS14, X5R derating at 4.6 V
def atten(f):
    w = 2 * math.pi * f
    zc = ESR + 1 / (1j * w * C_EFF)
    zs = R_SRC + 1j * w * L_FB + 0.05
    return abs(zc / (zs + zc))
fr = [1e5, 2.5e5, 5e5, 1e6]
pg = step('Is the 5 V filter enough?',
          ['The filter is a series ferrite bead and a shunt ceramic. Its attenuation is the ratio of the capacitor impedance to the total impedance. Cable and diode resistance in front help, and they also damp the circuit.',
           f'With the estimates in the table, the ripple falls by {-db(atten(2.5e5)):.0f} dB at 250 kHz. The op-amps and the LDO reject more. The real bead may differ, so probe TP11 with the power bank you use.'])
chip(pg, label='ESTIMATE, ASSUMED PARTS')
pg.text(2, 42, 'assumed', 2.5, MUTED, 'start', True)
asm = [f'bead {L_FB*1e9:.0f} nH', f'cable and diode {R_SRC:.1f} Ω', f'22 µF at 4.6 V: {C_EFF*1e6:.0f} µF, ESR {ESR*1e3:.0f} mΩ']
for i, t_ in enumerate(asm):
    pg.text(2, 47 + i * 5, t_, 2.5, INK, 'start')
for i, f in enumerate(fr):
    xx = 74 + (i % 2) * 34
    yy = 42 + (i // 2) * 14
    pg.rect(xx, yy, 30, 11, BONE2, 'none', 0, 1.5)
    pg.text(xx + 15, yy + 4.6, f'{f/1e3:g} kHz', 2.5, MUTED, 'middle', True)
    pg.text(xx + 15, yy + 9.4, f'{db(atten(f)):.0f} dB', 3.0, INK, 'middle', True)
pg.text(70, 82, 'Measure: 20 MHz bandwidth, AC coupling, 10 mV per division at TP11.', 2.4, MUTED, 'middle')

# 63 --------------------------------------------------------------------------------------------
r_div = val('R7') * val('R8') / (val('R7') + val('R8'))
i_pk = 0.6 / (val('R3') + val('R4'))                           # gain stage return current for a 120 mV burst (0.59 V at its output)
c_tot = val('C8') + val('C9')
pg = step('Why copy the mid-rail with U2B?',
          [f'A divider cannot supply current. The two 10 kΩ resistors look like {r_div/1e3:.0f} kΩ. The gain stage returns up to {i_pk*1e3:.2f} mA of signal current into VMID5. Across {r_div/1e3:.0f} kΩ that would move the rail by {i_pk*r_div:.1f} V.',
           f'The capacitors C8 and C9 hold the rail in the AE band: {1/(2*math.pi*250e3*c_tot)*1e3:.0f} mΩ at 250 kHz. The buffer matters below a few kHz, where the capacitors are weak. It costs nothing, because it uses the spare half of U2.'])
chip(pg, label='IMPEDANCE OF VMID5, Ω')
fz = [10, 100, 1e3, 1e4, 1e5, 2.5e5]
zc_ = lambda f: 1 / (2 * math.pi * f * c_tot)
pg.text(2, 43, 'frequency', 2.5, MUTED, 'start', True)
pg.text(46, 43, 'capacitors alone', 2.5, MUTED, 'start', True)
pg.text(92, 43, 'with the buffer', 2.5, MUTED, 'start', True)
for i, f in enumerate(fz):
    yy = 49 + i * 5.6
    pg.text(2, yy, f'{f/1e3:g} kHz' if f >= 1e3 else f'{f:g} Hz', 2.6, INK, 'start')
    pg.text(46, yy, f'{zc_(f):.3g} Ω', 2.6, INK, 'start')
    pg.text(92, yy, f'{min(val("R9"), zc_(f)):.3g} Ω', 2.6, INK, 'start', True)
pg.text(70, 86, f'Buffer path: U2B, R9 {val("R9"):.0f} Ω and C8. Capacitors: C8 {val("C8")*1e6:.0f} µF and C9 {val("C9")*1e9:.0f} nF. Divider: {r_div/1e3:.0f} kΩ.', 2.3, MUTED, 'middle')

_adc = SIM['burst']['0.12']['adc']
base_codes = max(max(_adc), -min(_adc)) / LSB                  # codes for the 120 mV burst at gain 4.9, from the simulation
# 64 --------------------------------------------------------------------------------------------
Q_PEAK = 0.12
g_to_adc = ADC_GAIN_250                                        # SMA to ADC differential, V/V at 250 kHz (includes the gain stage)
pg = step('Why a gain of 4.9?',
          [f'The head gives 85 to 149 mV for a charge of 4 to 7 pC. With no gain, a {Q_PEAK*1e3:.0f} mV event reads about {base_codes / GAIN:.0f} codes of 16384, 1.5 % of full scale. The sensor noise is 4 mV rms, so the ADC noise of 0.6 LSB (0.24 mV) hardly matters in either case.',
           'The gain is not needed for the noise. It makes the event fill about 5 times more codes and it follows the AFE budget. The price is headroom: the stages clip at a smaller input. R3 sets the gain, so a change is one resistor.'])
chip(pg, label='SAME 120 mV EVENT, THREE GAINS')
_g = SIM['burst']['0.12']['gout']
gpk = max(abs(v - MID) for v in _g) / 0.12            # volts at the gain-stage output per volt at the head, 250 kHz burst
rows = [['Gain', 'R3', 'codes at the ADC', 'clips at the head']]
base_clip = None
for g_, r3 in ((1.0, 0.0), (2.0, 1e3), (4.9, 3.9e3)):
    clip_ = (MID - 0.1) / (gpk * g_ / GAIN)
    rows.append([f'x{g_:g}', 'wire' if r3 == 0 else eng(r3, 'Ω'), f'{base_codes * g_ / GAIN:.0f}', f'{clip_*1e3:.0f} mV'])
for i, row in enumerate(rows):
    yy = 41 + i * 7.2
    if i == 0:
        pg.rect(4, yy, 126, 7.2, '#e6ece4', 'none', 0)
    pg.line(4, yy + 7.2, 130, yy + 7.2, '#bbb', 0.15)
    for xx, c_ in zip((6, 30, 56, 100), row):
        pg.text(xx, yy + 5.0, c_, 2.6, INK, 'start', i == 0)

# 65 --------------------------------------------------------------------------------------------
pg = step('What is Q?',
          ['Q tells how much a second-order filter peaks near its corner frequency. A low Q gives a soft corner. A high Q gives a peak and ringing. Q = 0.71 has no peak and is the flattest curve, the Butterworth response.',
           'Both filters here use Q = 0.71. In the time domain, Q = 0.71 overshoots a step by 4 %. Q = 2 overshoots by 44 %.'])
chip(pg, label='SECOND-ORDER LOW-PASS')
X0, Y0, W_, H_ = 14, 38, 110, 40
pg.rect(X0, Y0, W_, H_, '#fff', '#999', 0.3)
xs_ = [10 ** (-1 + 2 * i / 80) for i in range(81)]
ydb = lambda v: Y0 + H_ - (v + 30) / 40 * H_
for Qv, c_ in ((0.5, '#8c8c8c'), (0.707, PUR), (2.0, RED)):
    pts = []
    for x in xs_:
        m = 1 / math.sqrt((1 - x * x) ** 2 + (x / Qv) ** 2)
        pts.append((X0 + (math.log10(x) + 1) / 2 * W_, ydb(max(db(m), -29))))
    pg.poly(pts, c_, 0.6)
pg.text(X0 + 3, ydb(7.5), 'Q = 2', 2.6, RED, 'start', True)
pg.text(X0 + 3, ydb(-9), 'Q = 0.71', 2.6, PUR, 'start', True)
pg.text(X0 + 3, ydb(-14), 'Q = 0.5', 2.6, '#6c6c6c', 'start', True)
pg.line(X0 + W_ / 2, Y0, X0 + W_ / 2, Y0 + H_, '#888', 0.3, '1.2,0.8')
pg.text(X0 + W_ / 2, Y0 + H_ + 4, 'corner frequency', 2.5, MUTED, 'middle')
pg.text(X0 - 1.5, ydb(0) + 0.9, '0 dB', 2.5, MUTED, 'end')

# 66 --------------------------------------------------------------------------------------------
pg = step('What is nV/√Hz?',
          ['Noise voltage spreads over frequency. A density of 4.5 nV/√Hz means 4.5 nV rms in each 1 Hz slice. The slices are independent, so their powers add, not their voltages. The rms of a band is the density times the square root of the bandwidth.',
           f'The OPA365 has 4.5 nV/√Hz. In the AE band of 400 kHz that is {n365*math.sqrt(B_)*1e6:.1f} µV rms. The charge amplifier has a noise gain of {GN:.0f}, so {o365*1e6:.0f} µV reach its output.'])
chip(pg, label='OPA365, 4.5 nV/√Hz')
rows = [('1 Hz', 1.0), ('1 kHz', 1e3), ('100 kHz', 1e5), ('400 kHz, AE band', B_)]
for i, (nm, bw) in enumerate(rows):
    yy = 42 + i * 8
    v_ = n365 * math.sqrt(bw)
    pg.text(2, yy + 5, f'{nm}', 2.7, INK, 'start', True)
    pg.text(56, yy + 5, f'4.5 nV × √{bw:g}', 2.5, MUTED, 'start')
    pg.text(110, yy + 5, f'{v_*1e6:.3g} µV' if v_ >= 1e-6 else f'{v_*1e9:.3g} nV', 2.7, INK, 'start', True)

# 67 --------------------------------------------------------------------------------------------
pg = step('Does the power-up order matter?',
          ['The ADS7057 datasheet gives no sequencing rule. It gives limits: AVDD and DVDD up to 3.9 V, inputs up to AVDD + 0.3 V and logic inputs up to DVDD + 0.3 V. The 22 Ω resistors and the 10 Ω resistors keep a stray current under the 10 mA pin limit.',
           'One order matters in practice: AVDD must be stable before the first SPI frame, because that frame calibrates the offset. The ZedBoard 3.3 V feeds only DVDD and the pull-up R24, not the reference, so its noise stays out of AVDD.'])
chip(pg, label='WHO POWERS WHAT')
pbox(pg, 2, 40, 28, 14, '5 V input', ['USB-C or J7'], 'ext')
pbox(pg, 40, 40, 30, 14, 'XC6206', ['U5, 3.3 V'], 'bus')
pbox(pg, 82, 40, 28, 14, 'AVDD', ['reference'], 'mem')
pbox(pg, 2, 62, 28, 14, 'ZedBoard', ['PMOD 3.3 V'], 'ext')
pbox(pg, 82, 62, 28, 14, 'DVDD', ['SPI side'], 'mem')
pg.arrow([(30, 47), (40, 47)]); pg.arrow([(70, 47), (82, 47)]); pg.arrow([(30, 69), (82, 69)])
pg.text(118, 70, 'and R24', 2.5, MUTED, 'start')
pg.text(70, 85, 'Ground is common. Keep the SPI at 10 to 20 MHz while you check the noise.', 2.4, MUTED, 'middle')

# 68 --------------------------------------------------------------------------------------------
pg = step('What is an open-collector output?',
          ['The output stage of the LM393 is one transistor. It can pull the output to ground. It cannot push it high. When it is off, the pin floats.',
           'A resistor to 3.3 V (R24) supplies the high level. Two outputs on one wire make an OR for low: either one pulls the line low. The pull-up also sets the voltage level, so a 5 V part drives a 3.3 V input.'])
chip(pg, label='TWO OUTPUTS ON ONE WIRE')
pg.line(30, 48, 110, 48, INK, 0.5)
res_v(pg, 70, 38, 8, 'R24', '10k', left=False)
pg.text(74, 38, '3.3 V', 2.5, GRN, 'start', True)
for x_, nm in ((46, 'upper'), (94, 'lower')):
    pg.line(x_, 48, x_, 56, INK, 0.5)
    pg.circle(x_, 62, 5, '#fff', INK, 0.5)
    pg.text(x_, 63, 'Q', 2.6, INK, 'middle', True)
    pg.line(x_, 67, x_, 74, INK, 0.5); gnd(pg, x_, 74)
    pg.text(x_, 80, f'{nm} comparator', 2.4, MUTED, 'middle')
pg.line(110, 48, 120, 48, INK, 0.5); pg.text(122, 49, 'nWAKE', 2.6, INK, 'start', True)
pg.text(70, 86, 'both off: high.   either on: low.', 2.5, INK, 'middle', True)

# 69 --------------------------------------------------------------------------------------------
tp_names = {'TP3': 'SIG', 'TP4': 'HPF', 'TP5': 'GAIN', 'TP6': 'LPF', 'TP7': 'DRV+', 'TP8': 'DRV-', 'TP9': 'AIN+', 'TP10': 'AIN-'}
def stub_len(ref):
    """shortest track length in mm from the test point pad to a pad of another part on the same net (vias count as zero length)"""
    import heapq
    pad = FP[ref]['pads'][0]
    net = pad['net']
    key = lambda x, y: (round(x, 1), round(y, 1))
    adj = {}
    for t in BOARD['tracks']:
        if t['net'] != net:
            continue
        a, b = key(t['x1'], t['y1']), key(t['x2'], t['y2'])
        L = math.hypot(t['x2'] - t['x1'], t['y2'] - t['y1'])
        adj.setdefault(a, []).append((b, L)); adj.setdefault(b, []).append((a, L))
    goals = {key(p['x'], p['y']) for r_, f in FP.items() for p in f['pads'] if p['net'] == net and not r_.startswith('TP')}
    start = key(pad['x'], pad['y'])
    dist = {start: 0.0}
    pq = [(0.0, start)]
    while pq:
        dd, u = heapq.heappop(pq)
        if u in goals and u != start:
            return dd
        if dd > dist.get(u, 1e9):
            continue
        for v, L in adj.get(u, []):
            if dd + L < dist.get(v, 1e9):
                dist[v] = dd + L
                heapq.heappush(pq, (dd + L, v))
    return 0.0
stubs = {r: stub_len(r) for r in tp_names}
pg = step('Do the test points disturb the circuit?',
          [f'Slightly. Each test point is a pad and a stub of track, about 0.5 pF per centimetre. The stubs here are {min(stubs.values()):.0f} to {max(stubs.values()):.0f} mm long, so 1 to 2 pF each. A 10:1 scope probe adds 10 pF, more than any stub, so the probe changes the circuit more than the test point does.',
           'The stubs sit on low-impedance nodes: op-amp outputs, or the ADC input behind 400 pF. The risk is pickup on a long stub. If the noise is too high, cut the stub of the quiet stage with a knife.'])
chip(pg, label='STUB LENGTH AND CAPACITANCE, ESTIMATE')
for i, (r_, nm) in enumerate(tp_names.items()):
    col, row = i // 4, i % 4
    xx, yy = 4 + col * 66, 41 + row * 9
    L_ = stubs[r_]
    pg.text(xx, yy + 5, f'{nm}', 2.7, INK, 'start', True)
    pg.text(xx + 18, yy + 5, f'{L_:.0f} mm', 2.6, INK, 'start')
    pg.text(xx + 38, yy + 5, f'{L_ / 10 * 0.5 + 0.3:.1f} pF', 2.6, INK, 'start', True)
pg.text(70, 86, 'One-off check: probe a stage with and without the 10 pF of the probe and compare.', 2.4, MUTED, 'middle')
