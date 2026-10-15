"""G1 S1 and S3 of doc/lowpower_plan.md: the chain on a 3.3 V rail, with TI's OPA365 model.
usage: python3 sim/g1_chain33.py   (needs ngspice and sim/models/OPA365.lib)"""
import math, random
import vendor_chain as vc
V = 3.3
def metrics(v=None, v5=V):
    d, _ = vc.ngspice(vc.chain(v, v5=v5), "ac dec 40 1k 20meg\nlet ad=abs(v(ainp)-v(ainm))\nwrdata ac.txt ad")
    return vc.ac_metrics(vc.load_cols(d, 'ac.txt'))
print('S1  chain on %.1f V, vendor OPA365' % V)
m = metrics()
print('  nominal: gain %.2f dB, flatness %.2f dB, loss at 10 kHz %.1f dB, loss at 2 MHz %.1f dB, band %.0f to %.0f kHz' % (m['gain_db'], m['flat'], m['loss10k'], m['loss2M'], m['lo'], m['hi']))
d, o = vc.ngspice(vc.chain(v5=V), "noise v(ainp,ainm) Vin dec 30 1k 2.5meg 1\nprint onoise_total")
import re
nz = float(re.search(r'onoise_total\s*=\s*(\S+)', o).group(1))
print('  noise at the ADC input, 1 kHz to 2.5 MHz: %.0f uV rms = %.2f LSB' % (nz * 1e6, nz / (2 * 3.3 / 2 ** 14)))
random.seed(7); runs = []
for _ in range(100):
    v = {k: vc.NOM[k] * (1 + random.uniform(-vc.TOL[k], vc.TOL[k])) for k in vc.NOM}
    runs.append(metrics(v))
l10 = [r['loss10k'] for r in runs]
print('  Monte Carlo 100 runs: loss at 10 kHz min %.1f mean %.1f dB, runs under 40 dB: %d' % (min(l10), sum(l10) / len(l10), sum(1 for x in l10 if x < 40)))
print('  gain at 250 kHz min %.2f max %.2f dB' % (min(r['gain_db'] for r in runs), max(r['gain_db'] for r in runs)))
print('  bursts at the head output (gain 4.9 stage output, rail 0 to %.1f V):' % V)
for amp in (0.12, 0.2, 0.3, 0.4):
    t = vc.chain(v5=V, vin="DC 0").replace("Vin vs 0 DC 0", "Vin vs 0 DC 4.8 SIN(4.8 %g 250k 5u 0 0)" % amp)
    d, _ = vc.ngspice(t, "tran 20n 45u\nwrdata tr.txt v(gout) v(lpf)")
    r = vc.load_cols(d, 'tr.txt'); g = [x[1] for x in r if x[0] >= 10e-6]
    print('    %.2f V burst: %.2f to %.2f V %s' % (amp, min(g), max(g), 'CLIPS' if min(g) < 0.12 or max(g) > V - 0.12 else 'ok'))
