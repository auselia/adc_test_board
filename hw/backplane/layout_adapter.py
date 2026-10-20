import sys,os,json,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import pcbnew, bp_pcb
from legalize import legalize
from fmc_pins import *
import adapter
model=json.load(open(os.path.join(HERE,'out','FMC_Adapter_model.json')))
W,H=90.0,74.0; CX,CY=45.0,37.0
P={}
P['J1']=(CX,CY,180); P['J2']=(8.5,CY-30.48,0); P['J3']=(W-8.5-2.54,CY-30.48,0)
# first pass: put the FMC down to read the pad positions after the flip
b0,f0=bp_pcb.make('A',model,{**{p['ref']:(CX,CY,0) for p in model},'J1':(CX,CY,180)},(0,0,W,H))
pads={p.GetNumber():(pcbnew.ToMM(p.GetPosition().x)-bp_pcb.OX,pcbnew.ToMM(p.GetPosition().y)-bp_pcb.OY) for p in f0['J1'].Pads() if p.GetNumber()}
wx=sum(pads[p][0] for p in adapter.west)/len(adapter.west); ex=sum(pads[p][0] for p in adapter.east)/len(adapter.east)
print('west group mean x %.2f (should be < %.1f), east %.2f'%(wx,CX,ex))
assert wx<CX<ex,'FMC flipped the wrong way'
# chips
chips=[(ref,dr,rn,pl) for ref,dr,rn,pl in adapter.PLAN]
def ymean(pl): ys=[pads[p][1] for p in pl if p]; return sum(ys)/len(ys)
def spread(items,xc,rot,sep=12.0,lo=11.0,hi=H-11.0):
    items=sorted(items,key=lambda c:ymean(c[3])); ys=[ymean(c[3]) for c in items]
    for k in range(1,len(ys)): ys[k]=max(ys[k],ys[k-1]+sep)
    shift=(sum(ymean(c[3]) for c in items)-sum(ys))/len(ys); ys=[y+shift for y in ys]
    if ys[0]<lo: ys=[y+lo-ys[0] for y in ys]
    if ys[-1]>hi: ys=[y-(ys[-1]-hi) for y in ys]
    for c,y in zip(items,ys): P[c[0]]=(xc,y,rot)
spread([c for c in chips if c[3][0] in adapter.west],CX-17.0,180)
spread([c for c in chips if c[3][0] in adapter.east],CX+17.0,0)
# passives
refs=[p['ref'] for p in model]
nets={p['ref']:p['nets'] for p in model}
def chip_of_net(n):
    for c in chips:
        if n in c[2]: return c[0]
for p in model:
    r=p['ref']
    if r in P: continue
    if p['fp'].endswith('R_0603_1608Metric') and p['value']=='47R':
        n=[v for v in p['nets'].values() if v.startswith('T_')][0][2:]     # T_RA_CS0 -> RA_CS0
        ch=[c for c in chips if n in c[2]][0]; cx,cy,_=P[ch[0]]; b=ch[2].index(n); s=-1 if cx<CX else 1
        P[r]=(cx+s*(9.0+(b%2)*3.0),cy+(b-3.5)*1.3,90)
for c,(ref,dr,rn_,pl) in zip(range(len(chips)),chips): pass
# per chip decoupling: C1,C2 chip U1, ... (created in order: two per chip)
for i,(ref,dr,rn_,pl) in enumerate(chips):
    cx,cy,rot=P[ref]; s=-1 if cx<CX else 1
    P['C%d'%(2*i+1)]=(cx-s*2.3,cy-6.4,0)      # VCCA: pin 1 end is on the connector side (west chips are rotated 180)
    P['C%d'%(2*i+2)]=(cx+s*2.3,cy-6.4,0)
# SDO pull-downs: next to U7 B side
u7=P['U7']
sd=[p['ref'] for p in model if p['value']=='100k']
for k,r in enumerate(sd): P[r]=(u7[0]+9.0+(k%2)*3.0,u7[1]+(k-3.5)*1.3,90)
# bulk, LED, test points and holes along the south edge
for r,x in (('C17',17),('C18',21),('C19',25),('C20',29)): P[r]=(x,H-2.2,0)
P['R27']=(50,H-2.2,0); P['D1']=(54,H-2.2,0)
for k,x in enumerate((58,62,66)): P['TP%d'%(k+1)]=(x,H-2.2,0)
for k,(x,y) in enumerate(((CX,3.5),(CX,H-3.5))): P['H%d'%(k+1)]=(x,y,0)
missing=[r for r in refs if r not in P]; assert not missing,missing
silk=pcbnew.F_SilkS
texts=[("RIBBON A",16,2.4,1.0,silk,0),("RIBBON B",W-28,2.4,1.0,silk,0),("FMC ADAPTER  VADJ -> 3.3 V",36,H-0.9,0.9,silk,0)]
b,fps=bp_pcb.make('FMC_Adapter',model,P,(0,0,W,H),texts)
fixed={r for r in fps if r[0] in 'JHU' or r.startswith('TP')}
legalize(fps,fixed)
out=os.path.join(HERE,'FMC_Adapter.kicad_pcb'); b.Save(out); print('saved',out)
