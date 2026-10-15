"""First look at the real AE captures for the listener design (plan: doc/lowpower_plan.md, S2).
usage: python3 sim/listener_first_look.py [path to cavitation_logger/data]
Needs numpy only. Values are on the perfboard output (Cf = 47 pF): charge = voltage x 47 pF."""
import glob, os, sys
import numpy as np
D = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/Documents/cavitation_logger/data')
CF = 47e-12
def band(y, fs, lo, hi):
    n = len(y); F = np.fft.rfft(y * np.hanning(n)); f = np.fft.rfftfreq(n, 1 / fs)
    F[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(F, n)
rows = []
for f in sorted(glob.glob(os.path.join(D, 'run_*', 'cap_*.npz'))):
    z = np.load(f, allow_pickle=True)
    y = (z['raw'].astype(float) - float(z['yref'])) * float(z['yinc']) + float(z['yorig'])
    fs = 1 / float(z['xinc']); n = len(y); y -= np.median(y)
    bp = band(y, fs, 100e3, 500e3)
    pre = slice(int(n * .02), int(n * .30))
    rows.append((os.path.basename(f)[:30], np.std(y[pre]) * 1e3, np.std(bp[pre]) * 1e3, np.max(np.abs(bp[int(n * .05):int(n * .95)])) * 1e3))
print('capture                          broadband rms   band rms   band peak   (mV; x 47 pF = pC)')
for r in rows:
    print('%-30s %10.1f %10.1f %10.1f' % r)
pk = np.array([r[3] for r in rows]); nz = np.array([r[2] for r in rows])
ev = pk > 30
print('captures %d, true events (band peak > 30 mV) %d, noise triggers %d' % (len(rows), ev.sum(), (~ev).sum()))
print('band noise rms: median %.1f mV (%.2f pC), worst %.1f mV (%.2f pC)' % (np.median(nz), np.median(nz) * CF * 1e9, nz.max(), nz.max() * CF * 1e9))
print('true events: %.0f to %.0f mV = %.1f to %.1f pC' % (pk[ev].min(), pk[ev].max(), pk[ev].min() * CF * 1e9, pk[ev].max() * CF * 1e9))
