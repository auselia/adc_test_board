import json,sys,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
d=json.load(open(sys.argv[1])); f,ax=plt.subplots(figsize=(14,9))
for x,y,w,h in d['cy']: ax.add_patch(Rectangle((x,y),w,h,fill=False,ec='#999',lw=0.5))
for x1,y1,x2,y2,w,top,n in d['tracks']: ax.plot([x1,x2],[y1,y2],color='#c33' if top else '#36c',lw=w*14,alpha=0.8,solid_capstyle='round')
for x,y,w,h,n,pth,cx,cy in d['pads']: ax.add_patch(Rectangle((x,y),w,h,color='#d90' if not pth else '#888',alpha=0.9)); ax.text(x+w/2,y+h/2,n[:7],fontsize=3.5,ha='center',va='center')
for x,y in d['vias']: ax.add_patch(Circle((x,y),0.3,color='#2a2'))
import collections,math
routed=bool(d['tracks'])
nets=collections.defaultdict(list)
for x,y,w,h,n,pth,cx,cy in d['pads']:
    if n: nets[n].append((cx,cy))
if not routed:
  for n,pts in nets.items():
    done=[pts[0]]; rest=pts[1:]
    while rest:
        a,b=min(((a,b) for a in done for b in rest),key=lambda ab:math.dist(*ab))
        ax.plot([a[0],b[0]],[a[1],b[1]],color='#bbb' if n=='GND' else '#0a0',lw=0.3 if n=='GND' else 0.6)
        done.append(b); rest.remove(b)
for r,x,y in d['refs']: ax.text(x,y-1.0,r,fontsize=6,color='b',ha='center')
ax.add_patch(Rectangle((100,100),50,32,fill=False,ec='k')); ax.set_xlim(99,158); ax.set_ylim(133,99); ax.set_aspect('equal')
plt.savefig(sys.argv[2],dpi=170,bbox_inches='tight'); print('saved',sys.argv[2])
