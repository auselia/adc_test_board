import sys,os,json
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import pcbnew, bp_pcb
from legalize import legalize
model=json.load(open(os.path.join(HERE,'out','BP_Module_model.json')))
PITCH=25.4; X0=52.0; SY=33.65; W=X0+7*PITCH+16; H=72.0
P={}
P['J1']=(8,5.5,0)
for k in range(8): P['J%d'%(k+2)]=(X0+k*PITCH,SY,0)
P['J10']=(30,64,0)
P['U1']=(32,14,0); P['C1']=(32,6.5,0)
for k in range(8): P['R%d'%(k+1)]=(44+(k%2)*3.5,7+ (k//2)*3.2,90)
rn={}
for p in model:
    if p['fp']==bp_pcb and False: pass
# pull-ups R9..R32 (k-major: CS,WAKE,BIG per slot), slot caps C2..C17
n=8; c=1
for k in range(8):
    xs=X0+k*PITCH+7
    for i,nm in enumerate(('CS','WAKE','BIG')):
        n+=1; P['R%d'%n]=(xs,SY+1+i*2.2,0)
    c+=1; P['C%d'%c]=(xs,SY+9,0); c+=1; P['C%d'%c]=(xs,SY+11,0)
P['U2']=(34,52,0); P['D1']=(46,64,0)
for ref,(x,y) in {'C18':(26,48),'C19':(26,51),'C20':(43,48),'C21':(43,51),'C22':(43,54),'C23':(40,57),'C24':(28,56),'C25':(30,57),'R33':(56,64),'D2':(60,64),'TP1':(60,50),'TP2':(64,50),'TP3':(68,50)}.items(): P[ref]=(x,y,0)
for k in range(6): P['H%d'%(k+1)]=((20,125,238)[k//2],(3.5,68.5)[k%2],0)
missing=[p['ref'] for p in model if p['ref'] not in P]; assert not missing,missing
silk=pcbnew.F_SilkS
texts=[("5 V IN",30,59.5,1.2,silk,0),("RIBBON IN",8,2,1.2,silk,0),("ADS7057 BACKPLANE MODULE 8 SLOTS  (card components face +X, arrow ->)",100,3.2,1.2,silk,0)]
for k in range(8): texts.append(("SLOT %d  ->"%k,X0+k*PITCH-1.5,SY-4.5,1.2,silk,0))
b,fps=bp_pcb.make('BP_Module',model,P,(0,0,W,H),texts)
fixed={r for r in fps if r[0] in 'JHU' or r.startswith('TP')}
legalize(fps,fixed)
out=os.path.join(HERE,'BP_Module.kicad_pcb'); b.Save(out); print('saved',out,W,H)
