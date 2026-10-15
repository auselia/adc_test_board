"""G1 of doc/lowpower_plan.md: listener on the real AE captures (S2) and charge amplifier stability estimate (S4).
usage: python3 sim/g1_listener.py [path to cavitation_logger/data]   (numpy only)"""
import glob, math, os, sys
import numpy as np
D = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/Documents/cavitation_logger/data')
CF47 = 47e-12
def load():
    out = []
    for f in sorted(glob.glob(os.path.join(D, 'run_*', 'cap_*.npz'))):
        z = np.load(f, allow_pickle=True)
        y = (z['raw'].astype(float) - float(z['yref'])) * float(z['yinc']) + float(z['yorig'])
        out.append((os.path.basename(f)[:28], y - np.median(y), 1 / float(z['xinc'])))
    return out
def hp1(y, fs, fc):                       # first-order high-pass, bilinear
    k = math.tan(math.pi * fc / fs); a = (1 - k) / (1 + k); g = 1 / (1 + k)
    out = np.empty_like(y); xp = yp = 0.0
    for i, x in enumerate(y):
        yp = a * yp + g * (x - xp); xp = x; out[i] = yp
    return out
def lp1(y, fs, fc):                       # first-order low-pass at 500 kHz (comparator input network)
    k = math.tan(math.pi * fc / fs); a = (1 - k) / (1 + k); g = k / (1 + k)
    out = np.empty_like(y); xp = yp = 0.0
    for i, x in enumerate(y):
        yp = a * yp + g * (x + xp); xp = x; out[i] = yp
    return out
caps = load()
print('S2  listener on %d real captures (perfboard output, Cf 47 pF; charge = V x 47 pF)' % len(caps))
res = []
for name, y, fs in caps:
    h = lp1(hp1(y, fs, 100e3), fs, 500e3)
    n = len(h); pre = h[int(n * .12):int(n * .33)]
    res.append((name, np.std(pre) * 1e3, np.max(np.abs(h[int(n * .05):int(n * .95)])) * 1e3))
sig = np.array([r[1] for r in res]); pk = np.array([r[2] for r in res])
true = pk > 30
print('  after the 100 kHz high-pass: noise rms median %.2f mV (%.3f pC), worst %.2f mV (%.3f pC)' % (np.median(sig), np.median(sig) * 47e-3, sig.max(), sig.max() * 47e-3))
print('  true events %d: peak %.0f to %.0f mV (%.1f to %.1f pC)' % (true.sum(), pk[true].min(), pk[true].max(), pk[true].min() * 47e-3, pk[true].max() * 47e-3))
print('  largest peak in the %d noise captures: %.1f mV (%.2f pC)' % ((~true).sum(), pk[~true].max(), pk[~true].max() * 47e-3))
print('  threshold (pC) -> volts at 47 pF | events detected | noise captures that fire')
for th in (0.5, 0.75, 1.0, 1.5):
    v = th * 1e-12 / CF47 * 1e3
    print('   %.2f pC  %5.1f mV   %d of %d      %d of %d' % (th, v, (pk[true] > v).sum(), true.sum(), (pk[~true] > v).sum(), (~true).sum()))
print('  The 18 noise captures were selected by the scope trigger (70 mV), so they are the worst excursions the scope saw.')
print('  A threshold above their largest peak gives no false alarm in them. The false-alarm rate per hour must be measured (T5).')
print()
print('S4  charge amplifier loop (ESTIMATE: OPA314-class 3 MHz, second pole 10 MHz, output pole from 1 kohm open-loop Ro and 100 pF)')
GBW, F2, RO, CL = 3e6, 10e6, 1e3, 100e-12
for cf in (47e-12, 100e-12, 150e-12, 220e-12, 330e-12, 470e-12):
    gn = 1 + 1.6e-9 / cf
    fc = GBW / gn
    pm = 90 - math.degrees(math.atan(fc / F2)) - math.degrees(math.atan(2 * math.pi * fc * RO * CL))
    print('  Cf %4.0f pF: noise gain %5.1f, -3 dB at %4.0f kHz, crossover phase margin %2.0f deg, 5 pC gives %5.1f mV' % (cf * 1e12, gn, fc / 1e3, pm, 5e-12 / cf * 1e3))
