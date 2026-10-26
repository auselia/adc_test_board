"""Build ADC_Test.kicad_pcb from the netlist and the placement below (2 layers, all parts on top).
Usage: kicad-python build_board.py
"""
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from sexp import *
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
FPDIR='/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
mm=pcbnew.FromMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
OX,OY=100.0,100.0
W,H=57.0,37.6                  # main board (the bottom 3 mm carry the test-point strip)
DX=7.0                         # strip added on the left for the bias-T parts
TARGET=os.environ.get('BOARD','adc')   # 'adc' main board, 'head' sensor head (its own board file)
HW_,HH_=10.0,float(os.environ.get('HEADH','27'))   # sensor head outline (panel coordinates)
# ref: (x, y, rotation) in mm from the top-left corner of the board
POS={
 'J1':(4.6,7.6,0),                     # SMA in (hand-solder)
 'R1':(10.4,4.6,0),'C1':(10.4,7.6,0),'C2':(10.4,9.6,0),'R2':(10.4,11.6,0),   # HPF
 'U1':(16.8,7.6,0),'C3':(16.8,3.5,180),
 'R3':(22.4,6.6,0),'R4':(22.4,8.6,0),  # gain: Rf, Rg
 'R5':(26.0,6.6,0),'R6':(26.0,8.6,0),'C4':(26.0,4.6,0),'C5':(26.0,2.8,0),'C6':(26.0,10.6,180),  # LPF
 'U2':(31.6,7.6,0),'C10':(31.6,3.5,180),
 'R7':(37.0,4.0,0),'R8':(37.0,5.8,0),'C7':(37.0,7.6,0),'R9':(37.0,9.4,180),'C8':(37.0,11.4,0),'C9':(22.4,10.8,0),  # VMID5
 'C11':(28.6,13.6,270),'R10':(26.6,16.4,180),                                   # coupling into driver
 'U3':(21.0,20.0,0),'R12':(16.0,20.0,90),'R13':(26.0,20.0,90),
 'R11':(14.2,18.0,90),'C13':(12.5,18.0,90),'C12':(14.2,21.6,90),
 'R14':(12.5,14.4,90),'R15':(14.2,14.4,90),                                       # VOCM divider
 'U5':(8.6,14.6,0),'C21':(8.6,17.4,0),'C30':(8.6,19.4,0),'H1':(3.6,16.4,0),     # AVDD regulator, mounting hole
 'R16':(27.8,24.0,0),'R17':(28.2,22.0,0),                                       # 10R
 'C14':(31.4,22.7,0),'C15':(31.4,24.4,0),'C16':(34.8,23.0,0),'C17':(34.8,24.7,0),  # 4 x 100 pF across AINP/AINM
 'U4':(33.6,20.6,180),'C18':(30.6,19.2,90),'C20':(35.45,18.6,0),'C19':(32.3,18.2,0),'C22':(32.0,15.6,0),
 'R19':(38.6,20.4,0),'R20':(38.6,18.6,180),'R18':(38.95,14.8,0),               # 22R SPI
 'J3':(43.42,11.0,0),                                                           # PMOD, body flush with the right edge
 # window comparator (bottom middle/right)
 'RV1':(25.2,29.0,0),'R21':(30.2,26.4,0),'R22':(30.2,28.2,0),'R23':(30.2,30.0,0),'C26':(33.6,26.4,0),'C27':(33.6,30.0,0),
 'U6':(38.6,28.36,0),'C28':(37.8,24.6,0),'R24':(40.85,23.3,90),'C31':(38.6,22.4,0),'H2':(46.6,29.1,0),
 'J4':(45.6,4.4,0),'R25':(40.0,6.0,90),                                        # MON output
}
HEAD_REFS=set()
# bias-T strip (left of the old board) and the sensor head (second board, panel coordinates x 4..14, y 34..54)
NEW={'C33':(10.0,10.8,90),'R27':(10.0,13.6,90),
     'JP1':(3.2,12.8,90),'L2':(3.2,16.6,90),'R26':(12.0,24.9,90),'C32':(10.4,24.9,90),
     # 5 V input: USB-C on the left edge (mouth to the left), header, two SS14, ferrite, 22 uF
     'J2':(3.6,25.2,270),'J7':(11.6,29.4,90),'R32':(3.2,31.5,0),'R33':(6.2,31.5,0),'D1':(16.8,23.6,0),'D2':(16.8,26.6,0),
     'FB1':(21.4,24.4,0),'C23':(21.2,27.2,0)}
for _i,_r in enumerate(['TP%d'%k for k in range(3,21)]): NEW[_r]=(4.0+3.0*_i,33.9,0)
HEAD={'TP1':(5.0,3.6,0),'TP2':(8.4,3.6,0),
      'R31':(1.1,13.0,0),
      'C34':(3.05,13.0,0),
      'R28':(5.0,13.0,180),
      'R29':(6.95,13.0,180),
      'R30':(8.9,13.0,180),
      'C38':(1.5,1.1,0),
      'C36':(3.4,1.1,180),
      'C37':(5.3,1.1,0),
      'C35':(7.2,1.1,180),
      'U8':(5.0,10.5,180),
      'L1':(5.0,6.6,180),
      'J6':(5.0,HH_-4.1,0)}
HEAD_DY=5.0
for _k,(_x,_y,_r) in list(HEAD.items()):
    if _k!='J6': HEAD[_k]=(_x,_y+HEAD_DY,_r)
HEAD['H3']=(2.5,2.5,0); HEAD['H4']=(7.5,2.5,0)
import json
if os.environ.get('HEADJSON'): HEAD.update({k:tuple(v) for k,v in json.loads(os.environ['HEADJSON']).items()})
def load_fp(fpid):
    lib,name=fpid.split(':')
    path=os.path.join(HW,'Auselia.pretty') if lib=='Auselia' else FPDIR+lib+'.pretty'
    return pcbnew.FootprintLoad(path,name)
POS={r:(x+DX,y,rot) for r,(x,y,rot) in POS.items()}
POS.update(NEW)
if TARGET=='head':
    POS=dict(HEAD); W,H=HW_,HH_
else:
    from layout_v3 import POS as _P3, W as _W3, H as _H3
    POS=dict(_P3); W,H=_W3,_H3
PCBFILE='ADC_Head.kicad_pcb' if TARGET=='head' else 'ADC_Test.kicad_pcb'
FIXED={'J1','J2','J3','J4','J6','U4','H1','H2','H3','H4','TP1','TP2','U8','L1','J7'}
def legalize(b,gap=0.1,iters=200):
    """Push the smaller of two overlapping courtyards out along the shorter axis."""
    T=pcbnew.ToMM
    fps={f.GetReference():f for f in b.GetFootprints()}
    for it in range(iters):
        moved=False
        cy={r:f.GetCourtyard(pcbnew.F_CrtYd).BBox() for r,f in fps.items()}
        refs=sorted(cy)
        for i,a in enumerate(refs):
            for c in refs[i+1:]:
                A,B=cy[a],cy[c]
                ox=T(min(A.GetRight(),B.GetRight())-max(A.GetX(),B.GetX())); oy=T(min(A.GetBottom(),B.GetBottom())-max(A.GetY(),B.GetY()))
                if ox<=0.02 or oy<=0.02: continue
                aa=T(A.GetWidth())*T(A.GetHeight()); ab=T(B.GetWidth())*T(B.GetHeight())
                mv,other=(c,a) if (a in FIXED or (ab<aa and c not in FIXED)) else (a,c)
                if mv in FIXED: continue
                M,O=cy[mv],cy[other]
                if ox<oy: d=(ox+gap)*(1 if M.GetCenter().x>=O.GetCenter().x else -1); delta=V(d,0)
                else:     d=(oy+gap)*(1 if M.GetCenter().y>=O.GetCenter().y else -1); delta=V(0,d)
                fps[mv].Move(delta); moved=True
                cy[mv]=fps[mv].GetCourtyard(pcbnew.F_CrtYd).BBox()
        if not moved: break
    for r,f in sorted(fps.items()):
        x,y,rot=POS[r]; p=f.GetPosition(); nx,ny=T(p.x)-OX,T(p.y)-OY
        if abs(nx-x)>0.01 or abs(ny-y)>0.01: print('  moved %s -> (%.2f, %.2f)'%(r,nx,ny))
def build(out):
    t=parse(open(os.path.join(HW,'ADC_Test.net')).read())
    comps={}
    for c in find(get(t,'components'),'comp'):
        ref=get(c,'ref')[1]
        fields={get(f,'name')[1] if False else f[1][1]:f[2] for f in find(get(c,'fields') or [],'field') if len(f)>2}
        dnp=any(get(pp,'name') and get(pp,'name')[1]=='dnp' for pp in find(c,'property'))
        comps[ref]=dict(value=get(c,'value')[1],fp=get(c,'footprint')[1],fields=fields,dnp=dnp,
                        path=get(get(c,'sheetpath'),'tstamps')[1]+get(c,'tstamps')[1])
    nets={get(n,'name')[1]:[(get(x,'ref')[1],get(x,'pin')[1]) for x in find(n,'node')] for n in find(get(t,'nets'),'net')}
    nets={n:[(r,p) for r,p in pins if r in POS] for n,pins in nets.items()}
    nets={n:pins for n,pins in nets.items() if pins}
    b=pcbnew.BOARD(); b.SetCopperLayerCount(2)
    ni={}
    for name in nets:
        it=pcbnew.NETINFO_ITEM(b,name); b.Add(it); ni[name]=it
    pinnet={(r,p):n for n,pins in nets.items() for r,p in pins}
    comps={r:c for r,c in comps.items() if r in POS}
    for ref,c in comps.items():
        m=load_fp(c['fp']); b.Add(m)
        x,y,rot=POS[ref]
        m.SetReference(ref); m.SetValue(c['value'])
        lib,name=c['fp'].split(':'); m.SetFPID(pcbnew.LIB_ID(lib,name))
        m.SetDNP(c['dnp'])
        if ref.startswith('H') or ref.startswith('JP') or ref.startswith('TP'): m.SetAttributes(m.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
        if 'LCSC' in c['fields']:
            m.SetField('LCSC',c['fields']['LCSC'])
            f=m.GetField('LCSC'); f.SetVisible(False); f.SetLayer(pcbnew.F_Fab)
        m.SetOrientationDegrees(rot); m.SetPosition(V(OX+x,OY+y))
        m.SetPath(pcbnew.KIID_PATH(c['path']))
        for pad in m.Pads():
            n=pinnet.get((ref,pad.GetNumber()))
            if n: pad.SetNet(ni[n])
        if ref=='U4':
            for pad in m.Pads(): pad.SetLocalClearance(mm(0.15))
        r=m.Reference(); r.SetTextSize(V(0.8,0.8)); r.SetTextThickness(mm(0.12))
        m.Value().SetVisible(False)
    legalize(b)
    def line(x1,y1,x2,y2):
        s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1))
        s.SetStart(V(x1,y1)); s.SetEnd(V(x2,y2)); b.Add(s)
    x0,y0,x1,y1=OX,OY,OX+W,OY+H
    line(x0,y0,x1,y0); line(x1,y0,x1,y1); line(x1,y1,x0,y1); line(x0,y1,x0,y0)
    b.Save(out)
    print('saved',out,len(comps),'parts')
if __name__=='__main__':
    build(os.path.join(HW,PCBFILE))
