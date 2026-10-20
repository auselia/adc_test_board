import sys,os,json,re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import pcbnew, bp_pcb
from legalize import legalize
import bp16
model=json.load(open(os.path.join(HERE,'out','BP16_model.json')))
by={p['ref']:p for p in model}
W,H=158.0,124.0
FX,FY=10.0,62.0
X0=62.0; PX=25.4; YC=[20.0,48.0,76.0,104.0]
P={}
P['J1']=(FX,FY,180)
# sockets (origin on pad 1)
for k in range(16):
    r,c=divmod(k,4); P['J%d'%(k+2)]=(X0+c*PX,YC[r]-6.35,0)
# first pass for FMC pad positions
b0,f0=bp_pcb.make('A',model,{p['ref']:(FX,FY,180 if p['ref']=='J1' else 0) for p in model},(0,0,W,H))
pads={p.GetNumber():(pcbnew.ToMM(p.GetPosition().x)-bp_pcb.OX,pcbnew.ToMM(p.GetPosition().y)-bp_pcb.OY) for p in f0['J1'].Pads() if p.GetNumber()}
chips=bp16.PLAN
def ymean(pl): ys=[pads[p][1] for p in pl if p]; return sum(ys)/len(ys)
def spread(items,xc,sep=12.0,lo=12.0,hi=100.0):
    items=sorted(items,key=lambda c:ymean(c[3])); ys=[ymean(c[3]) for c in items]
    for k in range(1,len(ys)): ys[k]=max(ys[k],ys[k-1]+sep)
    shift=(sum(ymean(c[3]) for c in items)-sum(ys))/len(ys); ys=[y+shift for y in ys]
    if ys[0]<lo: ys=[y+lo-ys[0] for y in ys]
    if ys[-1]>hi: ys=[y-(ys[-1]-hi) for y in ys]
    for c,y in zip(items,ys): P[c[0]]=(xc,y,0)
spread([c for c in chips if c[3][0] in bp16.east],27.0)
spread([c for c in chips if c[3][0] in bp16.west],42.0)
for i,(ref,dr,rn,pl) in enumerate(chips):
    cx,cy,_=P[ref]
    P['C%d'%(2*i+1)]=(cx-2.3,cy-6.4,0); P['C%d'%(2*i+2)]=(cx+2.3,cy-6.4,0)
# SDO pull-downs R1..R8 right of U7
u7=P['U7']
for k in range(8): P['R%d'%(k+1)]=(u7[0]+(7.0 if k%2==0 else 9.2),u7[1]+(k-3.5)*1.2,90)
# per slot passives
for k in range(16):
    r,c=divmod(k,4); xs=X0+c*PX+7.8; yc=YC[r]
    for i,nm in enumerate(('CS','WAKE','BIG')):
        ref=[q['ref'] for q in model if q['value']=='100k' and set(q['nets'].values())=={'+3V3',nm+str(k)}][0]; P[ref]=(xs,yc-5+i*2.0,0)
    P['C%d'%(19+2*k)]=(xs,yc+2.2,0); P['C%d'%(20+2*k)]=(xs,yc+4.2,0)
# SCLK buffers + 22R
for h,(ub,cb,y0) in enumerate((('U9','C%d'%(19+32),34.0),('U10','C%d'%(20+32),90.0))):
    pass
caps244=[q['ref'] for q in model if q['value']=='100nF' and set(q['nets'].values())=={'+3V3','GND'} and int(q['ref'][1:])>50]
P['U9']=(48.0,34.0,0); P['U10']=(48.0,90.0,0)
r22=sorted([q['ref'] for q in model if q['value']=='22R'],key=lambda s:int(s[1:]))
for j,ref in enumerate(r22[:8]): P[ref]=(55.0+(j%2)*3.0,29.0+(j//2)*2.4,0)
for j,ref in enumerate(r22[8:]): P[ref]=(55.0+(j%2)*3.0,85.0+(j//2)*2.4,0)
# power block bottom left
P['J18']=(12.0,112.0,0); P['D1']=(30.0,117.0,0); P['U11']=(46.0,112.0,0)
P['C17']=(20.0,28.0,0); P['C18']=(20.0,31.5,0); P['C51']=(44.0,28.0,0); P['C52']=(44.0,84.0,0)
rest=[q['ref'] for q in model if q['ref'] not in P]
print('unplaced before the pool:',rest)
pool={'C':[(36,106),(40,106),(52,106),(56,106),(60,106),(36,110),(40,110),(52,114)],'R':[(66,116)],'D':[(70,116)],'TP':[(92,118),(96,118),(100,118),(104,118)],'H':[(4,4),(154,4),(4,120),(154,120),(76,4),(76,120)]}
idx={k:0 for k in pool}
for ref in rest:
    key='TP' if ref.startswith('TP') else ref[0]
    x,y=pool[key][idx[key]]; idx[key]+=1; P[ref]=(x,y,0)
missing=[q['ref'] for q in model if q['ref'] not in P]; assert not missing,missing
silk=pcbnew.F_SilkS
texts=[("ADS7057 BACKPLANE 16 CH  (cards: components face +X)",60,2.4,1.2,silk,0),("FMC plug on the bottom side",3,H-1.2,1.0,silk,0),("5 V IN",8,106,1.0,silk,0)]
for k in range(16):
    r,c=divmod(k,4); texts.append(("S%d ->"%k,X0+c*PX-1.0,YC[r]-9.5,1.1,silk,0))
b,fps=bp_pcb.make('BP16',model,P,(0,0,W,H),texts)
fixed={r for r in fps if r[0] in 'JHU' or r.startswith('TP')}
legalize(fps,fixed)
out=os.path.join(HERE,'BP16.kicad_pcb'); b.Save(out); print('saved',out)
