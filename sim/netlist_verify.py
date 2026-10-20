"""Functional check of the as-built board: ngspice built from hw/ADC_Test.net (the netlist the PCB is made from).

Every R, C, L and jumper comes from the netlist, so a wrong value, a wrong pin or a missing connection shows up here.
Models: OPA365 TI vendor model, THS4531 datasheet single-pole model, ADS7057 input (50 ohm + 16 pF per leg, AVDD and
DVDD loads), TLV7022 behavioural open-drain comparators with 7 mV hysteresis, PMOD source 3.3 V with 50 mohm,
head replaced by its 4.3 mA load and a 50 ohm generator.
usage: python3 netlist_verify.py
"""
import os, re, subprocess, sys, tempfile, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'hw', 'tools'))
from sexp import parse, find, get

NET = os.path.join(HERE, '..', 'hw', 'ADC_Test.net')
OPA = os.path.join(HERE, 'models', 'OPA365.lib')
t = parse(open(NET).read())
comp = {}
for c in find(get(t, 'components'), 'comp'):
    comp[get(c, 'ref')[1]] = get(c, 'value')[1]
import json
for _k, _v in json.loads(os.environ.get('OVERRIDE', '{}')).items():
    comp[_k] = _v
pinnet = {}
for n in find(get(t, 'nets'), 'net'):
    name = get(n, 'name')[1]
    for x in find(n, 'node'):
        pinnet[(get(x, 'ref')[1], get(x, 'pin')[1])] = name


def node(ref, pin):
    n = pinnet.get((ref, str(pin)))
    if n is None:
        return 'nc_%s_%s' % (ref, pin)
    n = re.sub(r'[^A-Za-z0-9_]', '_', n)
    return '0' if n == 'GND' else n


def san(n):
    return re.sub(r'[^A-Za-z0-9_]', '_', n)


def val(s):
    s = s.split()[0]
    m = re.fullmatch(r'([\d.]+)(R|k|M|pF|nF|uF|uH)', s)
    return float(m.group(1)) * {'R': 1, 'k': 1e3, 'M': 1e6, 'pF': 1e-12, 'nF': 1e-9, 'uF': 1e-6, 'uH': 1e-6}[m.group(2)]


def build(gen):
    L = ['* ADS7057 test board from ADC_Test.net', '.include ' + OPA,
         """.subckt FDA inp inn op om vocm vp vn params: gbw=27meg en=10n zo=2.5
rn1 inp ip {en*en/1.656e-20}
rn2 inn in {en*en/1.656e-20}
Gm 0 x ip in 1m
R1 x 0 100meg
C1 x 0 {1/(6.2832*100meg*gbw/1e5)}
Bp op0 0 V=max(min(v(vocm)+v(x)/2,v(vp)-0.1),v(vn)+0.1)
Bm om0 0 V=max(min(v(vocm)-v(x)/2,v(vp)-0.1),v(vn)+0.1)
Rop op0 op {zo}
Rom om0 om {zo}
.ends
.model SWC sw(vt=0 vh=0.0035 ron=100 roff=1e12)""",
         'Vpmod vpm 0 3.3', 'Rpmod vpm %s 0.05' % node('J7', 1), 'Rj7 %s %s 0.001' % (node('J7', 1), node('J7', 2))]
    for ref, v in sorted(comp.items()):
        k = ref[0]
        if ref.startswith('JP'):
            L.append('Rjp_%s %s %s 0.001' % (ref, node(ref, 1), node(ref, 2)))
        elif ref.startswith(('TP', 'H', 'J')) and ref != 'J7':
            continue
        elif k in 'RCL' and ref not in ('R31', 'R28', 'R29', 'R30', 'C34', 'C35', 'C36', 'C37', 'C38', 'L1'):
            L.append('%s%s %s %s %.6g' % (k, ref[1:], node(ref, 1), node(ref, 2), val(v)))
    # op-amps, driver, ADC, comparators
    for u in ('U1', 'U2'):
        L.append('X%sa %s %s %s %s %s OPA365' % (u, node(u, 3), node(u, 2), node(u, 8), node(u, 4), node(u, 1)))
        L.append('X%sb %s %s %s %s %s OPA365' % (u, node(u, 5), node(u, 6), node(u, 8), node(u, 4), node(u, 7)))
    L.append('XU3 %s %s %s %s %s %s %s FDA gbw=27meg en=10n zo=2.5' % (node('U3', 8), node('U3', 1), node('U3', 4), node('U3', 5),
                                                                       node('U3', 2), node('U3', 3), node('U3', 6)))
    ainp, ainm, avdd, dvdd = node('U4', 7), node('U4', 8), node('U4', 6), node('U4', 4)
    L += ['Rsa %s sa 50' % ainp, 'Csa sa 0 16p', 'Rsb %s sb 50' % ainm, 'Csb sb 0 16p',
          'Iavdd %s 0 1.1m' % avdd, 'Idvdd %s 0 0.3m' % dvdd]
    for u in ('U6', 'U9'):
        vcc, vee = node(u, 8), node(u, 4)
        L.append('Riq_%s %s %s 330k' % (u, vcc, vee))
        for ch, (ip, im, out) in {'a': (3, 2, 1), 'b': (5, 6, 7)}.items():
            ip, im, out = node(u, ip), node(u, im), node(u, out)
            L.append('B%s%s ctl_%s%s 0 V=v(%s)-v(%s)' % (u, ch, u, ch, im, ip))
            L.append('S%s%s %s %s ctl_%s%s 0 SWC' % (u, ch, out, vee, u, ch))
    for nm in sorted({san(n) for n in pinnet.values() if n != 'GND'}):
        L.append('Rleak_%s %s 0 1G' % (nm, nm))
    L.append('.nodeset ' + ' '.join('v(%s)=1.65' % node(*p) for p in (('U2', 5), ('U2', 6), ('U1', 1), ('U1', 7), ('U2', 1), ('U3', 4), ('U3', 5), ('U4', 7), ('U4', 8), ('U3', 2))))
    L.append('.nodeset ' + ' '.join('v(%s)=3.3' % node(*p) for p in (('U1', 8), ('U6', 8), ('U4', 6))))
    # head: 4.3 mA load on the coax centre, generator through 49.9 ohm and 100 nF (R31, C38)
    L += ['Ihead %s 0 4.3m' % node('J1', 1), 'Rgen vgen_s hq 49.9', 'Cgen hq %s 100n' % node('J1', 1), gen]
    return '\n'.join(L)


def run(circuit, control):
    d = tempfile.mkdtemp()
    p = os.path.join(d, 'c.cir')
    open(p, 'w').write(circuit + '\n.control\n' + control + '\n.endc\n.end\n')
    r = subprocess.run(['ngspice', '-b', p], capture_output=True, text=True, cwd=d)
    return d, r.stdout + r.stderr


def cols(d, name):
    return [list(map(float, l.split())) for l in open(os.path.join(d, name)) if l.strip()]


nodes = ['+3V3', '+3V3_C', 'AVDD', 'VMID5', 'VOCM', 'REFL', 'LST', 'TH1P', 'TH1M', 'TH2P', 'TH2M', 'WAKE_N',
         'BIG_N', 'HEAD_LINE', 'SIG_IN', 'DRV_OUTP', 'DRV_OUTN']
ok = True


def check(name, v, lo, hi, unit=''):
    global ok
    good = lo <= v <= hi
    ok &= good
    print('  %-34s %9.4g %-3s  expect %.4g .. %.4g   %s' % (name, v, unit, lo, hi, 'PASS' if good else 'FAIL'))


print('== 1. DC operating point, all links closed, PMOD 3.3 V')
d, o = run(build('Vgen vgen_s 0 DC 0'),
           'op\n' + 'print ' + ' '.join('v(%s)' % san(n) for n in nodes) + ' v(ainp) v(ainm) i(Vpmod)')
dc = {}
for m in re.finditer(r'^v\(([^)]+)\)\s*=\s*(\S+)', o, re.M):
    dc[m.group(1).lower()] = float(m.group(2))
for n in nodes:
    dc[n.lower()] = dc.get(san(n).lower(), float('nan'))
m = re.search(r'i\(vpmod\)\s*=\s*(\S+)', o)
ipmod = -float(m.group(1)) if m else float('nan')
_r = [val(comp[r]) for r in ('R21', 'R22', 'R39', 'R40', 'R41', 'R23')]
_i = 3.3 / sum(_r)
_th = {'REFL': 3.3 - _i * (_r[0] + _r[1] + _r[2]), 'TH1P': 3.3 - _i * (_r[0] + _r[1]), 'TH2P': 3.3 - _i * _r[0]}
_th['TH1M'] = 2 * _th['REFL'] - _th['TH1P']
_th['TH2M'] = 2 * _th['REFL'] - _th['TH2P']
for n, lo, hi in (('+3V3', 3.25, 3.31), ('+3V3_C', 3.25, 3.31), ('AVDD', 3.25, 3.31),
                  ('VMID5', 1.6, 1.7), ('VOCM', 1.6, 1.7), ('LST', 1.6, 1.7), ('WAKE_N', 3.25, 3.31), ('BIG_N', 3.25, 3.31),
                  ('HEAD_LINE', 2.8, 3.11)):
    check(n, dc.get(n.lower(), float('nan')), lo, hi, 'V')
for n in ('REFL', 'TH1P', 'TH1M', 'TH2P', 'TH2M'):
    check(n + ' against the resistor chain', dc.get(n.lower(), float('nan')), _th[n] - 0.012, _th[n] + 0.012, 'V')
check('ADC differential input', dc['ainp'] - dc['ainm'], -0.005, 0.005, 'V')
check('current from the PMOD', ipmod * 1e3, 15, 40, 'mA')

print('== 2. AC gain from the head connector, SENSOR IN to nodes')
d, o = run(build('Vgen vgen_s 0 DC 0 AC 1'),
           'ac dec 40 1k 20meg\nlet g_adc=abs(v(ainp)-v(ainm))/abs(v(sig_in))\nlet g_lst=abs(v(lst))/abs(v(sig_in))\n'
           'let g_lpf=abs(v(lpf_out))/abs(v(sig_in))\nwrdata ac.txt g_adc g_lst g_lpf')
rows = cols(d, 'ac.txt')
at = lambda f, k: rows[min(range(len(rows)), key=lambda i: abs(math.log(rows[i][0] / f)))][k]
db = lambda x: 20 * math.log10(x)
g250 = at(250e3, 1)
check('SIG_IN to ADC at 250 kHz', db(g250), 11.5, 13.0, 'dB')
check('loss at 10 kHz re 250 kHz', db(g250) - db(at(10e3, 1)), 38, 50, 'dB')
check('loss at 2 MHz re 250 kHz', db(g250) - db(at(2e6, 1)), 18, 40, 'dB')
check('SIG_IN to LST at 250 kHz', db(at(250e3, 3)), -4.5, 0, 'dB')
HALF_W, HALF_B = _i * _r[2], _i * (_r[2] + _r[1])
print('  thresholds at SIG_IN: WAKE_N %.0f mV, BIG_N %.0f mV (half windows at LST %.1f and %.1f mV, filter gain %.2f)' % (HALF_W / at(250e3, 3) * 1e3, HALF_B / at(250e3, 3) * 1e3, HALF_W * 1e3, HALF_B * 1e3, at(250e3, 3)))
check('SIG_IN to LST at 10 kHz', db(at(10e3, 3)), -60, -12, 'dB')

print('== 3. burst test, 250 kHz, 10 cycles, listener lines')
res = []
for amp in (0.010, 0.020, 0.045, 0.112, 0.200):
    gen = 'Vgen vgen_s 0 DC 0 SIN(0 %g 250k 5u 0 0) ' % amp
    d, o = run(build(gen), 'tran 20n 60u 0\nwrdata tr.txt v(sig_in) v(lst) v(wake_n) v(big_n) v(ainp)-v(ainm)')
    r = cols(d, 'tr.txt')
    w = [x for x in r if x[0] > 4e-6]
    vsig = max(abs(x[1] - 1.65) for x in w)
    lst = max(abs(x[3] - 1.65) for x in w)
    wmin = min(x[5] for x in w)
    bmin = min(x[7] for x in w)
    adcpk = max(abs(x[9]) for x in w)
    res.append((amp, vsig, lst, wmin < 1.65, bmin < 1.65, adcpk))
    print('  burst %5.0f mV at the generator: SIG_IN %5.1f mV pk, LST %5.1f mV pk, WAKE_N %s, BIG_N %s, ADC %5.0f mV pk = %4.0f codes'
          % (amp * 1e3, vsig * 1e3, lst * 1e3, 'LOW ' if wmin < 1.65 else 'high', 'LOW ' if bmin < 1.65 else 'high', adcpk * 1e3, adcpk / 0.4029e-3))
exp = {0.010: (False, False), 0.020: (False, False), 0.045: (True, False), 0.112: (True, True), 0.200: (True, True)}
for amp, vsig, lst, wk, bg, adcpk in res:
    good = (wk, bg) == exp[amp]
    ok &= good
    print('  %5.0f mV: WAKE_N %s, BIG_N %s  %s' % (amp * 1e3, 'low' if wk else 'high', 'low' if bg else 'high', 'PASS' if good else 'FAIL'))
print('\nRESULT:', 'ALL PASS' if ok else 'SOME FAILED')
