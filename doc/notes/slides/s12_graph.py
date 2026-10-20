from style import *
import json
from matplotlib.patches import Rectangle
b=json.load(open('/Users/nico/Documents/GitHub/adc_test_board/doc/data/board.json'))
W,H=b['size']
blocks={'Input and bias-T':('#d8c27a','C1 C2 R1 R2 C32 C33 JP1 L2 R26 R27 J1'),'High-pass, gain, low-pass':(accent,'R3 R4 C4 C5 C6 R5 R6 U1 U2 C3 C10 C9 R7 R8 R9 C7 C8'),
 'Driver and ADC':('#b3261e','C11 C12 R10 R11 R12 R13 U3 C13 R14 R15 C14 C15 C16 C17 R16 R17 U4 C18 C19 C20 C22 R18 R19 R20'),
 'Listener':('#5a7fb5','C26 C27 C28 C40 C41 C42 C43 C44 C45 U6 U9 R21 R22 R23 R24 R35 R36 R39 R40 R41 R42 RV1 C31'),
 'Power, PMOD, SCOPE OUT':('#7a5a9a','C21 C23 JP2 JP3 JP4 JP5 JP6 J7 R34 J3 J4 R25 J2 D1 D2 FB1 R32 R33 U5 C30')}
col={}
for n,(c,refs) in blocks.items():
    for r in refs.split(): col[r]=c
fig,ax=plt.subplots(figsize=(12,3.2))
ax.add_patch(Rectangle((0,0),W,H,fc='#f4f7f2',ec=ink,lw=1.4))
for r,f in b['footprints'].items():
    x0,y0,x1,y1=f['bbox']
    if r.startswith('TP'): c='#9aa59c'
    else: c=col.get(r,'#9aa59c')
    ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=c,ec='none',alpha=0.85))
ax.set_xlim(-1,W+1); ax.set_ylim(H+1,-1); ax.set_aspect('equal'); ax.axis('off')
hs=[Rectangle((0,0),1,1,fc=c) for c,_ in blocks.values()]+[Rectangle((0,0),1,1,fc='#9aa59c')]
ax.legend(hs,list(blocks)+['Test points, other'],loc='upper center',bbox_to_anchor=(0.5,0.0),ncol=3,fontsize=8,frameon=False)
ax.set_title('Top view, 125 × 21.5 mm: parts by block (courtyards from the KiCad file)',fontsize=10,color=ink,loc='left')
save(fig,'s12_graph')
unk=[r for r in b['footprints'] if r not in col and not r.startswith(('TP','H'))]; print('unassigned',unk)
