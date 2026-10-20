"""Bode plot of the sensor head charge amplifier (exact model with a one-pole OPA365) -> head_bode.svg / .png"""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.fonttype'] = 'none'          # keep text editable in slides
matplotlib.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']
Rf, Cf, GBW = 1e6, 47e-12, 50e6
f = np.logspace(2, 8, 2000); s = 1j * 2 * np.pi * f; wt = 2 * np.pi * GBW
def H(Cp):
    Zf = Rf / (1 + s * Rf * Cf)
    h = -s * Zf / (1 + s * (1 + s * Cp * Zf) / wt)        # v_o / Q, volts per coulomb
    return h * (-Cf)                                       # normalised: 1 = ideal mid-band gain (1/Cf)
def f3(Cp):
    return GBW / (1 + Cp / Cf)
ink, accent, cu, mut = '#14231b', '#0f3d2a', '#b8861b', '#566559'
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.6), sharex=True, gridspec_kw={'height_ratios': [2.2, 1], 'hspace': 0.08})
import itertools
CP = 1.6e-9
def Hx(Cp, cf, rf):
    Zf = rf / (1 + s * rf * cf)
    return (-s * Zf / (1 + s * (1 + s * Cp * Zf) / wt)) * (-Cf)      # relative to the nominal 1/Cf
combos = [Hx(CP * a, Cf * b, Rf * c) for a, b, c in itertools.product((0.8, 1, 1.2), (0.95, 1, 1.05), (0.99, 1, 1.01))]
mags = np.array([20 * np.log10(abs(h)) for h in combos]); phs = np.array([np.degrees(np.angle(h)) for h in combos])
a1.fill_between(f, mags.min(0), mags.max(0), color=accent, alpha=0.20, lw=0, label='All tolerance corners (Cp ±20 %, Cf ±5 %, Rf ±1 %)')
a1.semilogx(f, 20 * np.log10(abs(Hx(CP, Cf, Rf))), color=accent, lw=2.4, label='Nominal: Cp = 1.6 nF, Cf = 47 pF, Rf = 1 MΩ')
a2.fill_between(f, phs.min(0), phs.max(0), color=accent, alpha=0.20, lw=0)
a1.axvspan(100e3, 500e3, color='#d89cc8', alpha=0.22, lw=0); a2.axvspan(100e3, 500e3, color='#d89cc8', alpha=0.22, lw=0)
a1.text(224e3, -44, 'AE band\n100 to 500 kHz', ha='center', va='bottom', fontsize=9, color=ink)
fl = [1 / (2 * np.pi * Rf * c * Cf * r) for c in (0.95, 1.05) for r in (0.99, 1.01)]
fh = [GBW / (1 + CP * a / (Cf * b)) for a in (0.8, 1.2) for b in (0.95, 1.05)]
a1.axvspan(min(fl), max(fl), color=mut, alpha=0.25, lw=0); a1.axvspan(min(fh), max(fh), color=mut, alpha=0.25, lw=0)
a1.text(min(fl) * 0.86, -29, 'fL %.1f to %.1f kHz' % (min(fl) / 1e3, max(fl) / 1e3), fontsize=8.5, color=ink, rotation=90, va='bottom', ha='right')
a1.text(max(fh) * 1.1, -29, 'fH %.1f to %.1f MHz' % (min(fh) / 1e6, max(fh) / 1e6), fontsize=8.5, color=ink, rotation=90, va='bottom')
print('fL %.2f-%.2f kHz, fH %.2f-%.2f MHz' % (min(fl) / 1e3, max(fl) / 1e3, min(fh) / 1e6, max(fh) / 1e6))
for fq in (250e3, 500e3):
    i = np.argmin(abs(f - fq)); print('%.0f kHz: gain %.2f to %.2f dB re nominal, nominal %.2f dB' % (fq / 1e3, mags[:, i].min(), mags[:, i].max(), 20 * np.log10(abs(Hx(CP, Cf, Rf)[i]))))
a1.axhline(0, color=mut, lw=0.6); a1.set_ylim(-60, 4)
a1.set_ylabel('Gain relative to nominal (dB)\n0 dB = 21.3 mV per pC', color=ink)
a1.legend(loc='lower left', fontsize=8, frameon=False)
a2.semilogx(f, np.degrees(np.angle(Hx(CP, Cf, Rf))), color=accent, lw=2.4)
a2.axhline(0, color=mut, lw=0.6); a2.set_ylim(-100, 100); a2.set_yticks([-90, -45, 0, 45, 90])
a2.set_ylabel('Phase (°)', color=ink); a2.set_xlabel('Frequency (Hz)', color=ink); a2.set_xlim(1e2, 1e8)
for a in (a1, a2):
    a.grid(True, which='both', color='#d3dacf', lw=0.5); a.tick_params(colors=ink)
    for sp in a.spines.values(): sp.set_color(mut)
a1.set_title('Sensor head charge amplifier with part tolerances (OPA365, typical GBW 50 MHz)', fontsize=10.5, color=ink, loc='left')
fig.savefig('head_bode.svg', bbox_inches='tight'); fig.savefig('head_bode.png', dpi=200, bbox_inches='tight')
