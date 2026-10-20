from style import *
import json
f = np.logspace(3, 7, 1200); s = 1j * 2 * np.pi * f
def hpf(C1, C2, R1, R2):
    return s**2 / (s**2 + s * (C1 + C2) / (R2 * C1 * C2) + 1 / (R1 * R2 * C1 * C2))
C, R1, R2 = 100e-12, 10e3, 20e3
rng = np.random.default_rng(3)
band = []
for _ in range(400):
    c1, c2 = C * (1 + 0.05 * rng.uniform(-1, 1, 2)); r1, r2 = R1 * (1 + 0.01 * rng.uniform(-1, 1)), R2 * (1 + 0.01 * rng.uniform(-1, 1))
    band.append(20 * np.log10(abs(hpf(c1, c2, r1, r2))))
band = np.array(band)
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.fill_between(f, band.min(0), band.max(0), color=accent, alpha=0.22, lw=0, label='C ±5 %, R ±1 %')
nom = 20 * np.log10(abs(hpf(C, C, R1, R2)))
ax.semilogx(f, nom, color=accent, lw=2.4, label='Sallen-Key high-pass, f0 = 112.5 kHz, Q = 0.71')
d = json.load(open('/Users/nico/Documents/GitHub/adc_test_board/doc/data/sim.json'))
fs = np.array(d['f']); hp = np.array(d['hpf'])
ref = hp[np.argmin(abs(fs - 250e3))] / abs(hpf(C, C, R1, R2)[np.argmin(abs(f - 250e3))])
sel = [1e4, 3e4, 1e5, 2.5e5, 1e6]
ax.plot(sel, [20 * np.log10(hp[np.argmin(abs(fs - x))] / ref) for x in sel], 'o', color=cu, ms=7, label='ngspice (vendor OPA365 model)')
ax.axvspan(100e3, 500e3, color=ae, alpha=0.22, lw=0); ax.text(224e3, -52, 'AE band', ha='center', fontsize=9, color=ink)
i = lambda x: np.argmin(abs(f - x))
for x, y in ((1e4, -42), (112.5e3, -3)):
    ax.annotate('%.0f dB at %s' % (nom[i(x)], ('10 kHz' if x == 1e4 else '112.5 kHz')), (x, nom[i(x)]), xytext=(x * 1.2, nom[i(x)] - 6), fontsize=8.5, color=ink)
ax.set_ylim(-60, 4); ax.set_xlim(1e3, 1e7); ax.set_xlabel('Frequency (Hz)', color=ink); ax.set_ylabel('Gain relative to passband (dB)', color=ink)
ax.set_title('High-pass filter (U1A)', fontsize=11, color=ink, loc='left'); ax.legend(loc='upper left', fontsize=8.5, frameon=False); style(ax)
save(fig, 's04_graph')
print('10k %.1f dB, 100k %.2f, 250k %.2f, 500k %.2f' % tuple(nom[i(x)] for x in (1e4, 1e5, 2.5e5, 5e5)))
print('worst-case f-3dB range:', [f[np.argmin(abs(band[k] + 3.01))] / 1e3 for k in (band.argmin(0).min(), band.argmax(0).max())] if False else '')
