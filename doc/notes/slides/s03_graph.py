from style import *
f = np.logspace(2, 7, 1500); w = 2 * np.pi * f; s = 1j * w
R31, C38, Rdcr, Cpar = 49.9, 100e-9, 22.5, 13.5e-12
def branch(L):
    Z = Rdcr + s * L
    return Z / (1 + s * Cpar * Z)
def H(L1, L2):
    ZL = 1 / (1 / branch(L1) + 1 / branch(L2))      # both inductors hang on the coax line, the far ends are AC ground
    Zs = R31 + 1 / (s * C38)
    return ZL / (ZL + Zs)
fig, ax = plt.subplots(figsize=(7.2, 4.0))
cs = [H(L1, L2) for L1 in (423e-6, 517e-6) for L2 in (423e-6, 517e-6)]
m = np.array([20 * np.log10(abs(h)) for h in cs])
ax.fill_between(f, m.min(0), m.max(0), color=accent, alpha=0.2, lw=0, label='L1 and L2 at ±10 %')
ax.semilogx(f, 20 * np.log10(abs(H(470e-6, 470e-6))), color=accent, lw=2.4, label='Hand model, nominal 470 µH')
sim = [(1e4, -18.69), (1e5, -0.055), (2.5e5, -0.175), (5e5, -0.111)]
ax.plot([p[0] for p in sim], [p[1] for p in sim], 'o', color=cu, ms=7, label='ngspice, head + bias-T + cable')
ax.axvspan(100e3, 500e3, color=ae, alpha=0.22, lw=0); ax.text(224e3, -12, 'AE band', ha='center', fontsize=9, color=ink)
ax.set_ylim(-40, 3); ax.set_xlim(1e3, 1e7)
ax.set_xlabel('Frequency (Hz)', color=ink); ax.set_ylabel('Signal path loss, head to SENSOR IN (dB)', color=ink)
ax.set_title('Bias-T: the signal path', fontsize=11, color=ink, loc='left'); ax.legend(loc='lower right', fontsize=8.5, frameon=False); style(ax)
save(fig, 's03_graph'); fig.savefig('s03_graph.pdf', bbox_inches='tight')
i = lambda x: np.argmin(abs(f - x))
h = H(470e-6, 470e-6)
for x in (1e4, 1e5, 2.5e5, 5e5): print('%.0f Hz: model %.2f dB' % (x, 20 * np.log10(abs(h[i(x)]))))
