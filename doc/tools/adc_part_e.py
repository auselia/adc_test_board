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
assert n_parts == len(cpl) == 66
zf = zipfile.ZipFile(os.path.join(FAB, 'ADC_Test_gerbers.zip'))
n_gb = len(zf.namelist())
joints = json.load(open(os.path.join(FAB, 'joints.json')))

# 45 --------------------------------------------------------------------------------------------
pg = step('Which files go to the factory',
          [f'JLCPCB needs three files. The Gerber zip makes the bare board. The BOM names every part. The CPL gives the position and angle of each part.',
           f'The zip holds {n_gb} files. The BOM has {n_lines} lines and {n_parts} parts. The CPL has {len(cpl)} rows. The two mounting holes and the not-fitted capacitor C31 are in none of the two lists.'])
chip(pg, label='FILES IN hw/fab')
items = [('ADC_Test_gerbers.zip', 'Copper, mask, silk, paste, outline, drill', PUR),
         ('ADC_Test_BOM_JLC.csv', 'Value, references, footprint, LCSC number', BLU),
         ('ADC_Test_CPL_JLC.csv', 'Reference, X, Y, layer, rotation', GRN)]
for i, (nm, d_, c_) in enumerate(items):
    yy = 40 + i * 14
    pg.rect(6, yy, 124, 11, '#fff', c_, 0.6, 1.2)
    pg.text(9, yy + 4.6, nm, 3.0, INK, 'start', True)
    pg.text(9, yy + 8.6, d_, 2.5, MUTED, 'start')
assert 'C31' not in {r for row in bom for r in row['Designator'].split(',')}

# 46 --------------------------------------------------------------------------------------------
ext = ['C130011', 'C705347', 'C2669902', 'C11366']
names = {r['LCSC Part #']: r for r in bom}
pg = step('What is in the BOM',
          [f'{n_lines} lines hold {n_parts} parts. Four lines hold extended parts, and JLCPCB charges a fee for each type. All other lines hold basic parts.',
           'The ADC, the driver and the two op-amps are the extended parts. The tantalum capacitor is the fourth.'])
chip(pg, label='EXTENDED PARTS, PRICE PER PART')
rows = [['Ref', 'Part', 'LCSC', 'Price']]
for l in ext:
    r = names[l]
    rows.append([r['Designator'], r['Comment'], l, f"${cost.PRICE[l]:.2f}"])
table(pg, 4, 40, [24, 46, 28, 22], rows, rh=7.2, size=2.7)
pg.text(4, 80, f'Through-hole parts ({len(cost.THT_REFS)} lines): J1 J4 SMA, J2, J3, RV1. JLCPCB solders them by hand, for a fee per joint.', 2.5, MUTED)
assert all(l in cost.EXT_SMD for l in ext)

# 47 --------------------------------------------------------------------------------------------
pos = {r['Ref']: r for r in csv.DictReader(open(os.path.join(FAB, 'ADC_Test_pos_kicad.csv')))}
cplr = {r['Designator']: r for r in cpl}
fix = []
for ref, why in (('U5', 'viewer showed it turned; set absolute angle'), ('C29', 'library offset would turn it; kept KiCad angle'),
                 ('J2', 'viewer showed it turned; set absolute angle'), ('J3', 'viewer showed it turned; set absolute angle')):
    k_ = float(pos[ref]['Rot']) % 360
    c_ = float(cplr[ref]['Rotation'])
    assert k_ != c_ or ref == 'C29'
fix.append([ref, f'{k_:.0f}°', f'{c_:.0f}°', why])
pg = step('What the placement viewer corrected',
          ['The JLCPCB viewer showed four parts turned wrong. The KiCad footprints and the JLC library disagree on the zero angle. Each fix sits in `jlc_files.py`, not in the board.',
           'The trimmer RV1 also moved 2.54 mm in X and 1 mm in Y, because its library origin differs from the pin 1 pad.'])
chip(pg, label='KICAD ROTATION AGAINST CPL ROTATION')
table(pg, 4, 40, [14, 18, 18, 86], [['Ref', 'KiCad', 'CPL', 'Why']] + fix, rh=7.0, size=2.6)
pg.text(4, 80, 'Rule: look at every part in the viewer once. The viewer shows the real answer.', 2.5, MUTED)

# 48 --------------------------------------------------------------------------------------------
q5 = cost.quote(5)
dhl = q5['total'] + cost.IVA * (42.51 - cost.SHIP) + (42.51 - cost.SHIP)
pg = step('What the order costs',
          [f"Five assembled boards cost ${q5['goods']:.2f} at the factory. Shipping and IVA take it to ${q5['total']:.2f}, or {q5['total']*CLP/1000:.0f} thousand CLP at {CLP:.0f} CLP per USD.",
           f"That is ${q5['total']/5:.2f} per board. DHL Express would make the total ${dhl:.2f}, or {dhl*CLP/1000:.0f} thousand CLP."])
chip(pg, label='REAL QUOTE, 5 BOARDS, USD')
parts_ = [('PCB', q5['pcb'], PUR), ('Parts', q5['parts'], BLU), ('Fees', q5['fees'], GRN), ('Shipping', q5['ship'], AMB), ('IVA 19 %', q5['iva'], PNK)]
tot = sum(v for _, v, _ in parts_)
assert abs(tot - q5['total']) < 0.01 and abs(q5['total'] - 148.88) < 0.02
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
pg.text(4, 80, f"Total ${q5['total']:.2f}.  2 boards ${cost.quote(2)['total']:.2f},  3 boards ${cost.quote(3)['total']:.2f}.", 2.7, INK, 'start', True)

# ================================================================================================
# SECTION 8: BRING-UP AND CHECKS
# ================================================================================================
section('BRING-UP AND CHECKS', 'Bring-up and checks', 'Section 8', 'Steps 49 to 54',
        'What to measure before the PMOD goes in, the first signal test, the response to expect, how to '
        'test the wake-up, what to do when something fails and what is still open.',
        active=['Input', 'High-pass', 'Gain', 'Low-pass', 'Driver', 'ADC', 'SPI port', 'Wake-up', 'Power'])

# 49 --------------------------------------------------------------------------------------------
pg = step('What to check before the PMOD goes in',
          ['Feed 9 V to J2 with the PMOD unplugged. Measure each rail against GND with a meter. Unplug the supply if the 5 V rail is off by more than 0.25 V.',
           'The 3.3 V line comes from the ZedBoard through the PMOD. With no PMOD it reads 0 V, and that is correct.'])
chip(pg, label='EXPECTED VOLTAGES, 9 V IN')
rows = [['Node', 'Where', 'Expect'],
        ['+5V', 'C29 plus side', '5.0 V'],
        ['AVDD', 'C18 or U4 pin 6', '3.30 V'],
        ['VMID5', 'U2 pin 7', '2.50 V'],
        ['VOCM', 'R14 and R15 joint', f'{AVDD/2:.2f} V'],
        ['+3V3', 'J3 pin 11', '0 V (no PMOD)'],
        ['nWAKE', 'J3 pin 8', 'floats, no pull-up']]
table(pg, 4, 40, [30, 52, 44], rows, rh=6.6, size=2.6)

# 50 --------------------------------------------------------------------------------------------
vin = 0.100
vadc = vin * ADC_GAIN_250
pg = step('The first signal test',
          [f'Plug the PMOD in. Put 100 mV peak at 250 kHz on J1 from the Analog Discovery 2 and send a burst of ten cycles. Look at SCOPE OUT and read the SPI words.',
           f'The scope shows {vin*LPF_GAIN*1000:.0f} mV peak above 2.5 V. The ADC sees {vadc*1000:.0f} mV peak between its inputs, which is {vadc/LSB:.0f} codes.'])
chip(pg, label='EXPECTED, 100 mV PEAK AT J1')
rows = [['Where', 'Expect'],
        ['J1', f'{vin*1000:.0f} mV peak, 250 kHz'],
        ['SCOPE OUT (J4)', f'{vin*LPF_GAIN*1000:.0f} mV peak on 2.5 V'],
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
rows = [['Trimmer', 'RV1', 'Threshold at J1']]
for fr in (0.0, 0.25, 0.5, 0.75, 1.0):
    rp = fr * RP_MAX
    rows.append([f'{fr*100:.0f} %', eng(rp, 'Ω'), f'± {window(rp)/LPF_GAIN*1000:.0f} mV'])
lo_ = window(0) / LPF_GAIN * 1000
pg = step('How to test the wake-up',
          [f'Sweep RV1 and keep a burst at J1. nWAKE must drop for a burst above the threshold and stay high below it. The table gives the threshold for five trimmer positions.',
           f'The lowest setting is ± {lo_:.0f} mV at J1. The quiet perfboard noise is {INB:.1f} mV rms in the band, so that setting is only about {lo_/INB:.0f} times the noise.'])
chip(pg, label='COMPUTED FROM THE RESISTORS')
table(pg, 4, 40, [30, 40, 56], rows, rh=6.2, size=2.6)
pg.text(4, 82, 'ESTIMATE: comparator offset (up to 5 mV, datasheet) moves each threshold by that much.', 2.4, MUTED)

# 53 --------------------------------------------------------------------------------------------
pg = step('What if it does not work',
          ['Find the first stage that is wrong, then look only at that stage. Work from the input toward the ADC. Measure DC first, then the signal.',
           'Most first-board failures are a short, a part turned the wrong way or a missing 3.3 V.'])
chip(pg, label='SYMPTOM, CAUSE, CHECK')
rows = [['Symptom', 'Likely cause', 'Check'],
        ['5 V low', 'Battery under 6.7 V', 'J2 voltage'],
        ['SCOPE OUT flat', 'U1 or U2 not powered', '5 V at pin 8'],
        ['SDO all zeros', 'First frame only', 'Read twice'],
        ['SDO stuck', 'No 3.3 V from PMOD', 'J3 pin 11'],
        ['Wake always low', 'RV1 near 0 and noise', 'Turn RV1 up'],
        ['Code offset', 'VOCM or VMID off', 'Step 49 table']]
table(pg, 4, 40, [34, 52, 40], rows, rh=6.4, size=2.6)

# 54 --------------------------------------------------------------------------------------------
pg = step('What is verified and what is open',
          ['Checked by tools: the electrical rules, the design rules, the netlist against the board, and the rotations in the JLC viewer. Checked by simulation: gain, band, noise and settling.',
           'Nothing has run on a real board yet. Red rows mark the three open items.'])
chip(pg, label='STATUS')
rows = [['Item', 'Status', 'How'],
        ['ERC, DRC, parity', 'Done', 'KiCad, 0 errors'],
        ['Rotations', 'Done', 'JLC viewer'],
        ['Chain response, noise', 'Simulated', 'ngspice, vendor models'],
        ['THS4531, 400 pF load', 'OPEN', 'LTspice netlist, not run'],
        ['PMOD fit on ZedBoard', 'OPEN', 'print 1:1 and test'],
        ['First board, bench', 'OPEN', 'steps 49 to 52']]
table(pg, 4, 40, [44, 28, 54], rows, rh=6.4, size=2.6, colors={4: '#fde5e5', 5: '#fde5e5', 6: '#fde5e5'})

# ================================================================================================
# back cover
# ================================================================================================
m4lib.end_steps()
pg = new_page('back cover')
pg.bg = FOREST
pg.cur = None
pg.ox = pg.oy = 0
pg.text(20, 40, 'WHERE THINGS LIVE', 3.0, SAP, 'start', mono=True, ls=0.9)
pg.text(20, 62, 'Files, models and datasheets', min(12.0, 12.0 * 135 / text_w('Files, models and datasheets', 12.0, 'disp')), BONE, 'start', disp=True)
lines = [('hw/', 'KiCad project, schematic and board'),
         ('hw/fab/', 'Gerbers, BOM and CPL for JLCPCB'),
         ('hw/tools/', 'Generators, DRC, cost model, 1:1 print'),
         ('sim/', 'Chain simulation, vendor models list, LTspice netlist'),
         ('doc/tools/', 'This manual, built from the files above'),
         ('doc/data/', 'Board and simulation snapshots used in the figures')]
for i, (a_, b_) in enumerate(lines):
    pg.text(20, 84 + i * 9, a_, 3.4, AMBER, 'start', mono=True)
    pg.text(60, 84 + i * 9, b_, 3.4, '#D8E4D2', 'start')
pg.text(20, 150, 'DATASHEETS', 2.8, SAP, 'start', mono=True, ls=0.8)
pg.text(20, 158, 'ADS7057, THS4531, OPA365 (OPA2365), LM393, XC6206, AMS1117', 3.4, '#D8E4D2', 'start')
pg.text(20, 170, 'Rebuild: M4_PDF_PYTHON=<python with pymupdf> python3 doc/tools/make_adc_manual.py', 2.7, SAP, 'start', mono=True)
pg.text(20, PH - 12, 'AUSELIA  /  ' + m4lib.DOC_NAME, 2.5, '#7E9C86', 'start', mono=True, ls=0.5)
pg.text(PW - 20, PH - 12, f'{len(pages):02d}', 2.5, '#7E9C86', 'end', mono=True)
draw_mark(pg, 172, 44, 84, BONE, BONE, AMBER, AMBER, rings=True)
