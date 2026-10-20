from style import *
import json
d = json.load(open('/Users/nico/Documents/GitHub/adc_test_board/doc/data/sim.json'))
f = np.logspace(3, 7, 1400); s = 1j * 2 * np.pi * f
def hpf(C1, C2, R1, R2): return s**2 / (s**2 + s * (C1 + C2) / (R2 * C1 * C2) + 1 / (R1 * R2 * C1 * C2))
def lpf(R5, R6, C1, C2): return 1 / (1 + s * C2 * (R5 + R6) + s**2 * R5 * R6 * C1 * C2)
def total(c, r, cl, rl):
    return hpf(c, c, r[0], r[1]) * lpf(rl, rl, 2 * cl, cl)
nom = total(100e-12, (10e3, 20e3), 100e-12, 2.2e3)
i = lambda x: np.argmin(abs(f - x))
ref = abs(nom[i(250e3)])
rng = np.random.default_rng(5); band = []
for _ in range(500):
    c, cl = 100e-12 * (1 + 0.05 * rng.uniform(-1, 1, 2))
    r = (10e3 * (1 + 0.01 * rng.uniform(-1, 1)), 20e3 * (1 + 0.01 * rng.uniform(-1, 1))); rl = 2.2e3 * (1 + 0.01 * rng.uniform(-1, 1))
    band.append(20 * np.log10(abs(total(c, r, cl, rl)) / ref))
band = np.array(band)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.fill_between(f, band.min(0), band.max(0), color=accent, alpha=0.22, lw=0, label='C ±5 %, R ±1 %')
ax.semilogx(f, 20 * np.log10(abs(nom) / ref), color=accent, lw=2.4, label='High-pass × low-pass, by hand')
fs = np.array(d['f']); adc = np.array(d['adc']); r0 = adc[np.argmin(abs(fs - 250e3))]
sel = [1e4, 3e4, 1e5, 2.5e5, 5e5, 1e6, 2e6, 5e6]
ax.plot(sel, [20 * np.log10(adc[np.argmin(abs(fs - x))] / r0) for x in sel], 'o', color=cu, ms=6.5, label='ngspice, SENSOR IN to ADC (whole chain)')
ax.axvspan(100e3, 500e3, color=ae, alpha=0.22, lw=0)
ax.axvline(600e3, color='#b3261e', lw=1.2, ls='--'); ax.text(640e3, -52, 'FS/2 = 600 kHz\n(FS = 1.2 MSPS)', color='#b3261e', fontsize=8.5, va='bottom')
ax.text(224e3, -8, 'AE band', ha='center', fontsize=9, color=ink)
ax.set_ylim(-60, 5); ax.set_xlim(1e3, 1e7); ax.set_xlabel('Frequency (Hz)', color=ink); ax.set_ylabel('Gain relative to 250 kHz (dB)', color=ink)
ax.set_title('Filter chain: high-pass and low-pass together', fontsize=11, color=ink, loc='left'); ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=8, frameon=False); style(ax)
save(fig, 's06_graph')
h = 20 * np.log10(abs(nom) / ref)
for x in (1e4, 1e5, 5e5, 8e5, 2e6): print('%.0f Hz: %.1f dB (hand)' % (x, h[i(x)]), ' sim %.1f' % (20 * np.log10(adc[np.argmin(abs(fs - x))] / r0)))
lp = 20 * np.log10(abs(lpf(2.2e3, 2.2e3, 200e-12, 100e-12))); print('LPF alone: 250k %.2f, 500k %.2f, 800k %.2f, 2M %.2f' % tuple(lp[i(x)] for x in (2.5e5, 5e5, 8e5, 2e6)))
