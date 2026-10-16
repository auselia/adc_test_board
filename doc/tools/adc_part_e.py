"""Hardware manual, part E: section 7 (making the board, steps 45 to 48), section 8 (bring-up and checks,
steps 49 to 54) and the back cover."""
import json, zipfile
import m4lib
from adc_common import *

sys.path.insert(0, os.path.join(REPO, 'hw', 'tools'))
import cost

FAB = os.path.join(REPO, 'hw', 'fab')
CLP = 960.0                                     # CLP per USD, assumption, stated in step 48
LPF_GAIN = at(SIM['lpf'], 250e3)
EV = json.load(open(os.path.join(DATA, 'events.json')))
INB = max(sorted(b['inband'] for b in EV['baselines'])[:5])  # worst quiet in-band rms, mV


def table(pg, x, y, widths, rows, rh=6.2, size=2.5, head=True, colors=None):
    """plain table; first row is the header. colors: dict row -> fill"""
    tw = sum(widths)
    for i, row in enumerate(rows):
        yy = y + i * rh
        if i == 0 and head:
            pg.rect(x, yy, tw, rh, '#e6ece4', 'none', 0)
        elif colors and i in colors:
            pg.rect(x, yy, tw, rh, colors[i], 'none', 0)
        pg.line(x, yy + rh, x + tw, yy + rh, '#bbb', 0.15)
        xx = x
        for w_, c_ in zip(widths, row):
            pg.text(xx + 1.2, yy + rh / 2 + 0.9, str(c_), size, INK, 'start', i == 0 and head)
            xx += w_


# ================================================================================================
# SECTION 7: MAKING THE BOARD
# ================================================================================================
section('MAKING THE BOARD', 'Making the board', 'Section 7', 'Steps 45 to 48',
        'The files the factory needs, the parts list, what the placement viewer corrected and what the order '
        'costs.', active=None)

bom = list(csv.DictReader(open(os.path.join(FAB, 'ADC_Test_BOM_JLC.csv'))))
n_lines = len(bom)
n_parts = sum(len(r['Designator'].split(',')) for r in bom)
cpl = list(csv.DictReader(open(os.path.join(FAB, 'ADC_Test_CPL_JLC.csv'))))
assert n_parts == len(cpl)
zf = zipfile.ZipFile(os.path.join(FAB, 'ADC_Test_gerbers.zip'))
n_gb = len(zf.namelist())
joints = json.load(open(os.path.join(FAB, 'joints.json')))

# 45 --------------------------------------------------------------------------------------------
pg = step('Which files go to the factory',
          [f'JLCPCB needs three files. The Gerber zip makes the bare board. The BOM names every part. The CPL gives the position and angle of each part.',
           f'The main board zip holds {n_gb} files. The BOM has {n_lines} lines and {n_parts} parts. The CPL has {len(cpl)} rows. The mounting holes, the solder jumpers JP1 to JP6 and the test points are in none of them. The sensor head has its own zip, BOM and CPL.'])
chip(pg, label='FILES IN hw/fab')
items = [('ADC_Test_gerbers.zip', 'Copper, mask, silk, paste, outline, drill', PUR),
         ('ADC_Test_BOM_JLC.csv', 'Value, references, footprint, LCSC number', BLU),
         ('ADC_Test_CPL_JLC.csv', 'Reference, X, Y, layer, rotation', GRN)]
for i, (nm, d_, c_) in enumerate(items):
    yy = 40 + i * 14
    pg.rect(6, yy, 124, 11, '#fff', c_, 0.6, 1.2)
    pg.text(9, yy + 4.6, nm, 3.0, INK, 'start', True)
    pg.text(9, yy + 8.6, d_, 2.5, MUTED, 'start')
assert not any(r.startswith(('JP', 'TP', 'H')) for row in bom for r in row['Designator'].split(','))

# 46 --------------------------------------------------------------------------------------------
names = {r['LCSC Part #']: r for r in bom}
ext = [l for l in names if l in cost.EXT_SMD]
pg = step('What is in the BOM',
          [f'{n_lines} lines hold {n_parts} parts. {len(ext)} lines hold extended parts, and JLCPCB charges a fee for each type. All other lines hold basic parts.',
           'The ADC, the driver, the op-amps, the comparators and the 470 µH inductor of the bias-T are the extended parts.'])
chip(pg, label='EXTENDED PARTS, PRICE PER PART')
rows = [['Ref', 'Part', 'LCSC', 'Price']]
for l in ext:
    r = names[l]
    rows.append([r['Designator'][:14], r['Comment'][:26], l, f"${cost.PRICE[l]:.2f}"])
table(pg, 4, 38, [30, 48, 28, 20], rows, rh=5.6, size=2.5)
pg.text(4, 82, f'Through-hole parts: J1 and J4 SMA, J7 and J3. JLCPCB solders them by hand, for a fee per joint.', 2.5, MUTED)

# 47 --------------------------------------------------------------------------------------------
pos = {r['Ref']: r for r in csv.DictReader(open(os.path.join(FAB, 'ADC_Test_pos_kicad.csv')))}
cplr = {r['Designator']: r for r in cpl}
fix = []
for ref in sorted(pos, key=lambda r: (r[0], int(re.sub(r'\D', '', r) or 0))):
    if ref not in cplr:
        continue
    k_ = float(pos[ref]['Rot']) % 360
    c_ = float(cplr[ref]['Rotation'])
    if k_ != c_:
        fix.append([ref, f'{k_:.0f}°', f'{c_:.0f}°', 'viewer showed it turned; set absolute angle'])
assert fix
pg = step('What the placement viewer corrected',
          [f'The JLCPCB viewer showed parts turned wrong on the first revision. {len(fix)} rotations are corrected in the CPL. The new parts of this revision (U6 and U9 TLV7022, U8, L1, L2, J6) are not checked in the viewer yet. Each fix sits in `jlc_files.py`, not in the board.',
           'The KiCad footprints and the JLC library disagree on the zero angle. J3 and J7 also have their origin on pin 1, so they are placed by that pin.'])
chip(pg, label='KICAD ROTATION AGAINST CPL ROTATION')
table(pg, 4, 40, [14, 18, 18, 86], [['Ref', 'KiCad', 'CPL', 'Why']] + fix[:8], rh=5.6, size=2.5)
pg.text(4, 80, 'Rule: look at every part in the viewer once. The viewer shows the real answer.', 2.5, MUTED)

# 48 --------------------------------------------------------------------------------------------
T_ = cost.two_orders(2, 5)
A_, H_ = T_['adc'], T_['head']
q5 = cost.quote(5)
pg = step('What the order costs',
          [f"Two ADC boards and five sensor heads are two JLCPCB orders. They cost ${T_['goods']:.2f} at the factory. With one parcel, shipping and IVA, the total is ${T_['one_parcel']:.2f}, or {T_['one_parcel']*CLP/1000:.0f} thousand CLP at {CLP:.0f} CLP per USD.",
           f"The ADC order is ${A_['goods']:.2f} and the head order is ${H_['goods']:.2f}. Five ADC boards would cost ${q5['goods']:.2f}. These are estimates from the model of the first quote, until you upload the files."])
chip(pg, label='ESTIMATE, 2 ADC BOARDS + 5 HEADS, USD')
parts_ = [('PCB', A_['pcb'] + H_['pcb'], PUR), ('Parts', A_['parts'] + H_['parts'], BLU), ('Fees', A_['fees'] + H_['fees'], GRN),
          ('Shipping', cost.SHIP, AMB), ('IVA 19 %', cost.IVA * (T_['goods'] + cost.SHIP), PNK)]
tot = sum(v for _, v, _ in parts_)
assert abs(tot - T_['one_parcel']) < 0.01
x_ = 4.0
for nm, v, c_ in parts_:
    w_ = v / tot * 126
    pg.rect(x_, 42, w_, 9, c_, '#fff', 0.3)
    x_ += w_
yy = 56
for i, (nm, v, c_) in enumerate(parts_):
    xx = 4 + (i % 2) * 66
    yy2 = yy + (i // 2) * 6.5
    pg.rect(xx, yy2, 3.4, 3.4, c_, INK, 0.15)
    pg.text(xx + 5, yy2 + 2.9, f'{nm}   ${v:.2f}   {v*CLP/1000:.1f} k CLP', 2.5, INK, 'start')
pg.text(4, 80, f"Total ${T_['one_parcel']:.2f}.  Two parcels ${T_['separate_parcels']:.2f}.  5 + 5 boards ${cost.two_orders(5, 5)['one_parcel']:.2f}.", 2.7, INK, 'start', True)

# ================================================================================================
# SECTION 8: BRING-UP AND CHECKS
# ================================================================================================
section('BRING-UP AND CHECKS', 'Bring-up and checks', 'Section 8', 'Steps 49 to 54',
        'What to measure before the PMOD goes in, the first signal test, the response to expect, how to '
        'test the wake-up, what to do when something fails and what is still open.',
        active=['Input', 'High-pass', 'Gain', 'Low-pass', 'Driver', 'ADC', 'SPI port', 'Wake-up', 'Power'])

# 49 --------------------------------------------------------------------------------------------
pg = step('What to check before the PMOD goes in',
          ['Cut JP6 and feed 3.3 V to the header J7 from a bench supply set to 3.3 V with a 100 mA limit. Leave the PMOD unplugged. Measure each rail at the test points against GND. Switch off if +3V3 is off by more than 0.1 V or the current is above 60 mA.',
           'With the PMOD plugged in and JP6 closed, the same readings must appear. Never feed J7 and the PMOD at the same time.'])
chip(pg, label='EXPECTED VOLTAGES, 3.3 V IN')
rows = [['Node', 'Test point', 'Expect'],
        ['+3V3', 'TP11', '3.30 V'],
        ['AVDD', 'TP12', '3.30 V'],
        ['VMID5', 'TP13', f'{MID:.2f} V (half of +3V3_C)'],
        ['VOCM', 'TP14', f'{AVDD/2:.2f} V (half of AVDD)'],
        ['REFL', 'TP18', '1.65 V'],
        ['LST', 'TP15', 'about 1.65 V'],
        ['WAKE_N, BIG_N', 'TP16, TP17', '3.3 V (pulled up)']]
table(pg, 4, 38, [30, 36, 60], rows, rh=5.9, size=2.6)

# 50 --------------------------------------------------------------------------------------------
vin = 0.100
vadc = vin * ADC_GAIN_250
pg = step('The first signal test',
          [f'Plug the PMOD in. Put 100 mV peak at 250 kHz on J1 from the Analog Discovery 2 and send a burst of ten cycles. Look at SCOPE OUT and read the SPI words.',
           f'The scope shows {vin*LPF_GAIN*1000:.0f} mV peak above {MID:.1f} V. The ADC sees {vadc*1000:.0f} mV peak between its inputs, which is {vadc/LSB:.0f} codes.'])
chip(pg, label='EXPECTED, 100 mV PEAK AT J1')
rows = [['Where', 'Expect'],
        ['J1', f'{vin*1000:.0f} mV peak, 250 kHz'],
        ['SCOPE OUT (J4)', f'{vin*LPF_GAIN*1000:.0f} mV peak on {MID:.1f} V'],
        ['ADC input, differential', f'{vadc*1000:.0f} mV peak'],
        ['Code, peak', f'about {vadc/LSB:.0f} (0x{int(vadc/LSB):04X})'],
        ['Code, no signal', 'near 0 (0x0000), ± 1']]
table(pg, 4, 42, [52, 74], rows, rh=7.0, size=2.7)
assert 400 < vadc / LSB < 1200

# 51 --------------------------------------------------------------------------------------------
fs = [10e3, 50e3, 100e3, 250e3, 500e3, 1e6, 2e6]
ref = db(at(SIM['adc'], 250e3))
rows = [['Frequency', 'Gain SMA to ADC', 'Against 250 kHz']]
for f in fs:
    g = db(at(SIM['adc'], f))
    rows.append([f'{f/1e3:g} kHz', f'{g:+.1f} dB', f'{g-ref:+.1f} dB'])
pg = step('What response to measure',
          [f'Sweep J1 at 100 mV and read the code amplitude. Divide by the amplitude at 250 kHz. The numbers below come from the simulation.',
           f'Component spread moves the 10 kHz point. In {sum(1 for x in LOSS10 if x < 40)} of 150 random runs the loss at 10 kHz was below 40 dB.'])
chip(pg, label='SIMULATION, NOMINAL PARTS')
table(pg, 4, 40, [34, 48, 44], rows, rh=5.8, size=2.6)

# 52 --------------------------------------------------------------------------------------------
rows = [['Burst at J1', 'WAKE_N', 'BIG_N']]
for v_ in (0.020, 1.6 * L_WAKE, 1.4 * L_BIG):
    rows.append([f'{v_*1e3:.0f} mV peak', 'low' if v_ > L_WAKE else 'high', 'low' if v_ > L_BIG else 'high'])
pg = step('How to test the listener thresholds',
          [f'Sweep a 250 kHz burst at J1 from 10 mV upward. WAKE_N must drop between about {(L_WAKE-0.008)*1e3:.0f} and {(L_WAKE+0.008)*1e3:.0f} mV. BIG_N must drop between about {(L_BIG-0.008)*1e3:.0f} and {(L_BIG+0.008)*1e3:.0f} mV. The table gives the three points to check.',
           f'The quiet perfboard noise is {INB:.1f} mV rms in the band, so WAKE_N at {L_WAKE*1e3:.0f} mV is about {L_WAKE*1e3/INB:.0f} times the noise. The comparator offset (up to ±8 mV, datasheet) moves each threshold by that much.'])
chip(pg, label='COMPUTED FROM THE RESISTORS')
table(pg, 4, 40, [44, 40, 40], rows, rh=7.0, size=2.7)
pg.text(4, 82, 'ESTIMATE: the high-pass and low-pass of the listener are close to unity at 250 kHz.', 2.4, MUTED)

# 53 --------------------------------------------------------------------------------------------
pg = step('What if it does not work',
          ['Find the first stage that is wrong, then look only at that stage. Work from the input toward the ADC. Measure DC first, then the signal.',
           'Most first-board failures are a short, a part turned the wrong way or a missing 3.3 V.'])
chip(pg, label='SYMPTOM, CAUSE, CHECK')
rows = [['Symptom', 'Likely cause', 'Check'],
        ['3.3 V low', 'Weak PMOD supply or short', 'TP11 under load'],
        ['SCOPE OUT flat', 'U1 or U2 not powered', '3.3 V at pin 8, JP3 closed'],
        ['SDO all zeros', 'First frame only', 'Read twice'],
        ['SDO stuck', 'JP5 open or no 3.3 V', 'DVDD at U4 pin 4'],
        ['WAKE_N always low', 'LST noisy or REFL off', 'TP18 must be 1.65 V'],
        ['Code offset', 'VOCM or VMID off', 'Step 49 table, JP4']]
table(pg, 4, 40, [34, 52, 40], rows, rh=6.4, size=2.6)

# 54 --------------------------------------------------------------------------------------------
pg = step('What is verified and what is open',
          ['Checked by tools: the electrical rules, the design rules, the netlist against the board, and the rotations in the JLC viewer. Checked by simulation: gain, band, noise and settling.',
           'Nothing has run on a real board yet. Red rows mark the three open items. The THS4531 stability with its 400 pF load stays on the list of the ADC input filter, step 18.'])
chip(pg, label='STATUS')
rows = [['Item', 'Status', 'How'],
        ['ERC, DRC, parity', 'Done', 'KiCad, 0 errors'],
        ['Rotations', 'Done', 'JLC viewer'],
        ['Chain response, noise', 'Simulated', 'ngspice, vendor models'],
        ['Head and bias-T at 3.3 V', 'Simulated', 'ngspice, OPA365'],
        ['Listener on real captures', 'Simulated', 'Python, 25 captures'],
        ['ZedBoard 3.3 V rail noise', 'OPEN', 'probe TP11 and TP12'],
        ['PMOD fit, adjacent ports', 'OPEN', 'print 1:1 and test'],
        ['First board, bench', 'OPEN', 'steps 49 to 52']]
table(pg, 4, 36, [44, 28, 54], rows, rh=5.4, size=2.5, colors={6: '#fde5e5', 7: '#fde5e5', 8: '#fde5e5'})
