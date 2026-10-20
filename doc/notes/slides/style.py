import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
matplotlib.rcParams['svg.fonttype'] = 'none'
matplotlib.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']
ink, accent, cu, mut, ae = '#14231b', '#0f3d2a', '#b8861b', '#566559', '#d89cc8'
def style(ax):
    ax.grid(True, which='both', color='#d3dacf', lw=0.5); ax.tick_params(colors=ink)
    for sp in ax.spines.values(): sp.set_color(mut)
def save(fig, name):
    fig.savefig(name + '.pdf', bbox_inches='tight')
    fig.savefig(name + '.svg', bbox_inches='tight'); fig.savefig(name + '.png', dpi=200, bbox_inches='tight')
