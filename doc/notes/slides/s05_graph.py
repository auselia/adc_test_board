from style import *
import json
d = json.load(open('/Users/nico/Documents/GitHub/adc_test_board/doc/data/sim.json'))
b = d['burst']
fig, ax = plt.subplots(figsize=(7.2, 4.0))
cols = {'0.12': accent, '0.2': cu, '0.4': '#b3261e'}
for k, v in b.items():
    t = np.array(v['t']); g = np.array(v['gout']); m = t >= 4e-6
    ax.plot((t[m] - 4e-6) * 1e6, g[m], color=cols[k], lw=1.6, label='%d mV peak at the head output' % round(float(k) * 1000))
ax.axhline(3.3, color=mut, lw=1.2, ls='--'); ax.axhline(0, color=mut, lw=1.2, ls='--'); ax.axhline(1.65, color=mut, lw=0.8, ls=':')
ax.text(0.5, 3.36, 'supply rail 3.3 V', fontsize=8.5, color=ink); ax.text(0.5, 0.06, 'ground', fontsize=8.5, color=ink); ax.text(40.5, 1.69, 'VMID5 1.65 V', fontsize=8.5, color=ink, ha='right')
ax.set_ylim(-0.15, 3.6); ax.set_xlim(0, 41)
ax.set_xlabel('Time (µs)', color=ink); ax.set_ylabel('Gain-stage output, GAIN_OUT (V)', color=ink)
ax.set_title('Gain stage: what clips first (250 kHz bursts, gain 4.9)', fontsize=11, color=ink, loc='left'); ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3, fontsize=8.5, frameon=False); style(ax)
save(fig, 's05_graph')
g12 = (max(b['0.12']['gout']) - min(b['0.12']['gout'])) / 2 / 0.12
print('gain at 250 kHz at GAIN_OUT per volt at the head: %.2f; clip at %.2f V' % (g12, (1.65 - 0.1) / g12))
