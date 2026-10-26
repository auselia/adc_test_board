"""After routing: widen thin tracks, top GND pour + stitching vias, silkscreen labels, refs to F.Fab."""
import pcbnew,os,math,sys
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TARGET=os.environ.get('BOARD','adc'); NAME='ADC_Head' if TARGET=='head' else 'ADC_Test'
PCB=os.path.join(HW,NAME+'.kicad_pcb')
mm=pcbnew.FromMM; T=pcbnew.ToMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
OX,OY=100.0,100.0
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from layout_v3 import W,H
HEADH=float(os.environ.get('HEADH','27'))
DX=7.0
BOARDS=[('HGND',0.0,0.0,10.0,HEADH)] if TARGET=='head' else [('GND',0.0,0.0,W,H)]
b=pcbnew.LoadBoard(PCB)
GNDS=['HGND'] if TARGET=='head' else ['GND']; gndn={n:b.FindNet(n) for n in GNDS}
# 1. drop Freerouting's 0.12 mm GND neck-down stubs (the GND pours connect those pads)
for t in list(b.GetTracks()):
    if t.Type()==pcbnew.PCB_TRACE_T and t.GetWidth()<mm(0.15) and t.GetNetname() in GNDS: b.Delete(t)
def gnd_stubs():   # GND track ends that touch nothing but the pour
    out=[]
    trs=[t for t in b.GetTracks() if t.GetNetname() in GNDS]
    pads=[p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname() in GNDS]
    for t in trs:
        if t.Type()!=pcbnew.PCB_TRACE_T: continue
        for e in (t.GetStart(),t.GetEnd()):
            hit=any(o is not t and (o.HitTest(e) if o.Type()==pcbnew.PCB_VIA_T else (o.GetStart()==e or o.GetEnd()==e)) for o in trs) \
                or any(p.HitTest(e) for p in pads)
            if not hit: out.append(t); break
    return out
def via_ok(p,r):       # free copper circle of radius r around p (other nets, both layers)
    for t in b.GetTracks():
        if t.GetNetname() in GNDS: continue
        if t.Type()==pcbnew.PCB_VIA_T:
            if math.dist((T(t.GetPosition().x),T(t.GetPosition().y)),p)<r+0.3: return False
        else:
            a=(T(t.GetStart().x),T(t.GetStart().y)); c=(T(t.GetEnd().x),T(t.GetEnd().y))
            dx,dy=c[0]-a[0],c[1]-a[1]; L=dx*dx+dy*dy
            u=0 if L==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L))
            if math.dist((a[0]+u*dx,a[1]+u*dy),p)<r+T(t.GetWidth())/2: return False
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetname() in GNDS: continue
            bb=pad.GetBoundingBox(); bb.Inflate(mm(r))
            if bb.Contains(V(*p)): return False
    return True
for _ in range(5):
    st=gnd_stubs()
    if not st: break
    for t in st:
        for e in (t.GetStart(),t.GetEnd()):
            p=(T(e.x),T(e.y))
            trs=[o for o in b.GetTracks() if o.GetNetname() in GNDS and o is not t]
            pads=[q for f in b.GetFootprints() for q in f.Pads() if q.GetNetname() in GNDS]
            if any(q.HitTest(e) for q in pads) or any((o.HitTest(e) if o.Type()==pcbnew.PCB_VIA_T else (o.GetStart()==e or o.GetEnd()==e)) for o in trs): continue
            if via_ok(p,0.3+0.16):
                v=pcbnew.PCB_VIA(b); v.SetPosition(e); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetNet(gndn[t.GetNetname()]); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); print('  GND via at track end',round(p[0]-OX,2),round(p[1]-OY,2))
            else:
                b.Delete(t); print('  removed GND stub at',round(p[0]-OX,2),round(p[1]-OY,2))
            break
for t in gnd_stubs():          # anything still dangling: the pours already carry GND there
    print('  removed dangling GND stub',round(T(t.GetStart().x)-OX,2),round(T(t.GetStart().y)-OY,2)); b.Delete(t)
for t in b.GetTracks():                     # Freerouting neck-downs below the 0.15 mm fab minimum
    if t.Type()==pcbnew.PCB_TRACE_T and t.GetWidth()<mm(0.15): t.SetWidth(mm(0.15))
# 2. top GND pour on each board (the bottom pours exist from prep_route)
for (net,bx0,by0,bx1,by1),LY in [(bd,ly) for bd in BOARDS for ly in (pcbnew.F_Cu,pcbnew.B_Cu)]:
    if any(z.GetLayer()==LY and z.GetNetname()==net for z in b.Zones()): continue
    z=pcbnew.ZONE(b); z.SetLayer(LY); z.SetNet(gndn[net])
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for x,y in [(bx0+0.3,by0+0.3),(bx1-0.3,by0+0.3),(bx1-0.3,by1-0.3),(bx0+0.3,by1-0.3)]: ch.Append(mm(OX+x),mm(OY+y))
    ch.SetClosed(True); z.Outline().AddOutline(ch)
    z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
for z in b.Zones(): z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
for fp in b.GetFootprints():
    if fp.GetReference()=='J3':
        for pd in fp.Pads():
            if pd.GetNetname() in GNDS: pd.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
# 3. stitching vias on a 2 mm grid where both pours are solid and nothing else is near
def clear_of_others(p,r):
    for t in b.GetTracks():
        if t.Type()==pcbnew.PCB_VIA_T and math.dist((T(t.GetPosition().x),T(t.GetPosition().y)),p)<1.0: return False
        if t.GetNetname() in GNDS: continue
        if t.Type()==pcbnew.PCB_VIA_T:
            if math.dist((T(t.GetPosition().x),T(t.GetPosition().y)),p)<r+T(t.GetWidth(pcbnew.F_Cu))/2: return False
        else:
            a=(T(t.GetStart().x),T(t.GetStart().y)); c=(T(t.GetEnd().x),T(t.GetEnd().y))
            dx,dy=c[0]-a[0],c[1]-a[1]; L=dx*dx+dy*dy
            u=0 if L==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L))
            if math.dist((a[0]+u*dx,a[1]+u*dy),p)<r+T(t.GetWidth())/2: return False
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            bb=pad.GetBoundingBox(); bb.Inflate(mm(r))
            if bb.Contains(V(*p)): return False
    return True
zones={(z.GetNetname(),z.GetLayer()):z for z in b.Zones()}
added=[]
for net,bx0,by0,bx1,by1 in BOARDS:
    gx=bx0+1.6
    while gx<bx1-1.0:
        gy=by0+1.6
        while gy<by1-1.0:
            p=(OX+gx,OY+gy)
            if all(zones[(net,l)].HitTestFilledArea(l,V(*p),mm(0.45)) for l in (pcbnew.F_Cu,pcbnew.B_Cu)) and clear_of_others(p,0.65) \
               and all(math.dist(p,q)>1.6 for q in added):
                v=pcbnew.PCB_VIA(b); v.SetPosition(V(*p)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetNet(gndn[net]); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); added.append(p)
            gy+=2.0
        gx+=2.0
print('stitching vias',len(added))
# 3b. every GND pour island needs a via to the other layer (narrow boards cut the pours into pieces)
def island_vias():
    n=0
    for _ in range(4):
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        fixed=0
        gvias=[(T(t.GetPosition().x),T(t.GetPosition().y)) for t in b.GetTracks() if t.Type()==pcbnew.PCB_VIA_T and t.GetNetname() in GNDS]
        gpth=[(T(p.GetPosition().x),T(p.GetPosition().y)) for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() in GNDS and p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH]
        for net in GNDS:
            for layer in (pcbnew.F_Cu,pcbnew.B_Cu):
                z=zones.get((net,layer))
                if z is None: continue
                polys=z.GetFilledPolysList(layer)
                for i in range(polys.OutlineCount()):
                    ol=polys.COutline(i); bb=ol.BBox()
                    x0,y0,x1,y1=T(bb.GetX()),T(bb.GetY()),T(bb.GetRight()),T(bb.GetBottom())
                    inside=lambda p: polys.Contains(V(*p),i)
                    if any(inside(p) for p in gvias+gpth): continue
                    done=False
                    for vw,vd,hit,clr,step in ((0.6,0.3,0.45,0.65,0.3),(0.5,0.2,0.35,0.5,0.1)):
                        gy=y0
                        while gy<=y1 and not done:
                            gx=x0
                            while gx<=x1 and not done:
                                p=(gx,gy)
                                if inside(p) and all(zones[(net,l)].HitTestFilledArea(l,V(*p),mm(hit)) for l in (pcbnew.F_Cu,pcbnew.B_Cu)) and clear_of_others(p,clr):
                                    v=pcbnew.PCB_VIA(b); v.SetPosition(V(*p)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(vw)); v.SetDrill(mm(vd))
                                    v.SetNet(gndn[net]); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); added.append(p); fixed+=1; n+=1; done=True
                                gx+=step
                            gy+=step
                        if done: break
        if not fixed: break
    return n
print('island vias',island_vias())
for z in b.Zones(): z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())

for d_ in list(b.GetDrawings()):
    if d_.GetLayer() in (pcbnew.F_SilkS,pcbnew.B_SilkS): b.Delete(d_)
# 4. silkscreen. Reference designators go to F.Fab (the board is dense); the silk carries plain-language labels.
for fp in b.GetFootprints(): fp.Reference().SetLayer(pcbnew.F_Fab)
def text(s,x,y,size=0.8,just=pcbnew.GR_TEXT_H_ALIGN_CENTER,layer=pcbnew.F_SilkS,thick=None,mirror=False):
    t=pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetPosition(V(OX+x,OY+y))
    t.SetTextSize(V(size,size)); t.SetTextThickness(mm(thick or (0.13 if size<1 else 0.18))); t.SetHorizJustify(just); t.SetMirrored(mirror); b.Add(t)
def shape(kind,layer=pcbnew.F_SilkS,width=0.1,fill=False):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(kind); s.SetLayer(layer); s.SetWidth(mm(width))
    if fill: s.SetFilled(True)
    b.Add(s); return s
def logo(x0,y0,s=0.1,layer=pcbnew.F_SilkS,mirror=False):
    """Auselia mark (platform/brand/mark/svg/auselia-mark-mono-bone.svg), top-left of its bounding box at (x0,y0) mm, s mm per SVG unit.
    mirror=True draws it for the back side (seen from the back it reads correctly)."""
    if mirror: P=lambda u,v: V(OX+x0+(50-u)*s, OY+y0+(v-9.5)*s)
    else: P=lambda u,v: V(OX+x0+(u-7.0)*s, OY+y0+(v-9.5)*s)
    st=shape(pcbnew.SHAPE_T_SEGMENT,layer=layer,width=5*s); st.SetStart(P(28,58)); st.SetEnd(P(28,12))                # stem
    def bez(p0,c1,c2,p3,n=14):
        return [((1-t)**3*p0[0]+3*(1-t)**2*t*c1[0]+3*(1-t)*t*t*c2[0]+t**3*p3[0],
                 (1-t)**3*p0[1]+3*(1-t)**2*t*c1[1]+3*(1-t)*t*t*c2[1]+t**3*p3[1]) for t in [k/n for k in range(n+1)]]
    pts=bez((28,48),(28,37),(18,31),(7,31))+bez((7,31),(7,42),(17,50),(28,48))[1:]                    # leaf
    lf=shape(pcbnew.SHAPE_T_POLY,layer=layer,width=0.05,fill=True)
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for u,v in pts: ch.Append(P(u,v))
    ch.SetClosed(True); lf.SetPolyShape(pcbnew.SHAPE_POLY_SET(ch))
    c=shape(pcbnew.SHAPE_T_CIRCLE,layer=layer,width=0.05,fill=True); c.SetCenter(P(28,24)); c.SetEnd(P(34,24))   # bud
    for r in (14,22):                                                                                  # two sound arcs
        a=shape(pcbnew.SHAPE_T_ARC,layer=layer,width=3.6*s)
        h=8.0 if r==14 else 12.6; dx=(r*r-h*h)**0.5
        a.SetArcGeometry(P(28+dx,24-h),P(28+r,24),P(28+dx,24+h))
# front: labels a person can read without the schematic
if TARGET=='head':
    text('+ centre',5.0,11.0,0.8,layer=pcbnew.B_SilkS,thick=0.15,mirror=True); text('-',8.4,10.8,0.9,layer=pcbnew.B_SilkS,thick=0.15,mirror=True)
    logo(2.9,14.0,0.1,layer=pcbnew.B_SilkS,mirror=True)                        # back, the face the piezo sits on
    text('HEAD v1',5.0,12.8,0.8,layer=pcbnew.B_SilkS,thick=0.15,mirror=True)
else:
    text('SENSOR IN',5.4,1.2,0.8); text('+3V3 on centre',5.4,20.6,0.0001) if False else None
    text('SCOPE OUT',5.4,20.7,0.8)
    TPN={'TP3':'SIG','TP4':'HPF','TP5':'GAIN','TP6':'LPF','TP7':'DRV+','TP8':'DRV-','TP9':'AIN+','TP10':'AIN-','TP11':'3V3','TP12':'AVDD','TP13':'MID5',
         'TP14':'VOCM','TP15':'LST','TP16':'WAKE','TP17':'BIG','TP18':'REFL','TP19':'GND','TP20':'GND'}
    # back: one tidy information panel (mirrored text: the anchor is where reading starts, the text runs toward smaller x)
    def bt(s,x,y,size=0.8): text(s,x,y,size,pcbnew.GR_TEXT_H_ALIGN_LEFT,pcbnew.B_SilkS,0.15,True)
    TPL=[('TP3','SIG_IN'),('TP4','HPF'),('TP5','GAIN'),('TP6','LPF'),('TP7','DRV+'),('TP8','DRV-'),('TP9','AIN+'),('TP10','AIN-'),('TP11','3V3'),('TP12','AVDD'),
         ('TP13','VMID5'),('TP14','VOCM'),('TP15','LST'),('TP16','WAKE_N'),('TP17','BIG_N'),('TP18','REFL'),('TP19','GND'),('TP20','GND')]
    for i,(tp_,nm_) in enumerate(TPL):
        bt('%s %s'%(tp_,nm_),86.0-(i//6)*10.0,3.4+(i%6)*1.25)
    bt('JP1 head power',86.0,11.9); bt('JP3 capture rail',86.0,13.2)
    bt('J7 1 ONBOARD+ 2 FORCE+',66.0,11.9); bt('3 SENSE+ 4 SENSE- 5 FORCE-',66.0,13.2)
    logo(59.5,14.6,0.1,layer=pcbnew.B_SilkS,mirror=True)
    bt('AFE Test Board',58.0,16.5,1.4); bt('ADS7057 v1   Auselia 2026-10',58.0,18.8,0.8)
    for i,l in enumerate(['PMOD (J3)','1 CS    7 BIG_N','2 -     8 -','3 SDO   9 -','4 SCK  10 WAKE_N','5 GND  11 GND','6 3V3  12 3V3']):
        bt(l,W-27.0,9.0+i*1.5,0.9)
    # top: pin names of the power / SMU header J7 (pin 1 at x = 98.0)
    for k_,(num_,nm_) in enumerate((('1','ON+'),('2','F+'),('3','S+'),('4','S-'),('5','F-'))):
        text(num_,98.0+2.54*k_,4.5,0.8,layer=pcbnew.F_SilkS,thick=0.12); text(nm_,98.0+2.54*k_,8.9,0.8,layer=pcbnew.F_SilkS,thick=0.12)

# 5. top silkscreen: test point numbers and IC numbers, each placed where it touches no pad, via, text or board edge
def place_labels(items,size=0.8):
    BW,BH=(10.0,HEADH) if TARGET=='head' else (W,H)
    obst=[]
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            bb=pad.GetBoundingBox(); obst.append([T(bb.GetX())-OX-0.08,T(bb.GetY())-OY-0.08,T(bb.GetRight())-OX+0.08,T(bb.GetBottom())-OY+0.08])
    for d_ in b.GetDrawings():
        if d_.GetLayer()==pcbnew.F_SilkS:
            bb=d_.GetBoundingBox(); obst.append([T(bb.GetX())-OX,T(bb.GetY())-OY,T(bb.GetRight())-OX,T(bb.GetBottom())-OY])
    miss=[]
    for ref,label,cx,cy,centre_first in items:
        w=len(label)*size*0.78+0.3; h=size*1.3
        d0=[(0,0)] if centre_first else []
        order=((0,-1),(0,1),(1,0),(-1,0),(1,-1),(-1,-1),(1,1),(-1,1)) if cy<8 else ((0,1),(0,-1),(1,0),(-1,0),(1,-1),(-1,-1),(1,1),(-1,1))
        cand=d0+[(dx*k,dy*k) for k in ((1.25,1.5,1.8,2.3,2.8) if ref.startswith('TP') else (1.0,1.4,1.9,2.5,3.2)) for dx,dy in order]
        ok=None
        for ox,oy in cand:
            # push the box out by half its size when the offset is sideways or vertical
            x=cx+ox+(ox!=0 and (w/2 if ox>0 else -w/2) or 0); y=cy+oy+(oy!=0 and (h/2 if oy>0 else -h/2) or 0)
            bx=[x-w/2,y-h/2,x+w/2,y+h/2]
            if bx[0]<0.3 or bx[1]<0.3 or bx[2]>BW-0.3 or bx[3]>BH-0.3: continue
            if any(not(bx[2]<=o[0] or bx[0]>=o[2] or bx[3]<=o[1] or bx[1]>=o[3]) for o in obst): continue
            ok=(x,y,bx); break
        if ok is None: miss.append(ref); continue
        text(label,ok[0],ok[1],size,layer=pcbnew.F_SilkS,thick=0.12); obst.append(ok[2])
    return miss
items=[]
for fp in b.GetFootprints():
    r=fp.GetReference(); p=fp.GetPosition()
    if r.startswith('TP') and TARGET=='head': continue
    if r.startswith('TP'): items.append((r,r,T(p.x)-OX,T(p.y)-OY,False))
    elif r[0]=='U': items.append((r,r,T(p.x)-OX,T(p.y)-OY,True))
items.sort(key=lambda i:(i[0][0]!='U',i[0]))          # ICs first, they have the fewest options
print('silk labels not placed:',place_labels(items))
if TARGET!='head':
    for _r in ('JP1','JP3'):
        for _f in b.GetFootprints():
            if _f.GetReference()==_r: text(_r,T(_f.GetPosition().x)-OX,T(_f.GetPosition().y)-OY-2.4,0.8,layer=pcbnew.F_SilkS,thick=0.12)
if TARGET=='head':
    text('+',2.2,8.6,1.2,layer=pcbnew.F_SilkS,thick=0.18); text('-',8.4,11.2,1.2,layer=pcbnew.F_SilkS,thick=0.18)
b.GetDesignSettings().SetAuxOrigin(V(OX,OY+(HEADH if TARGET=='head' else H)))
# pads that DRC reports with a starved thermal relief get a solid connection (self-correcting, up to 3 rounds)
import subprocess,re
K='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
for _ in range(3):
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(PCB)
    rpt=os.path.join(HW,'_therm.rpt')
    subprocess.run([K,'pcb','drc','--severity-all','-o',rpt,PCB],capture_output=True)
    bad=set(re.findall(r'\[starved_thermal\][^\n]*\n[^\n]*\n[^\n]*\n\s*@\([^)]*\): [Pp][Aa][Dd] (\S+) \[H?GND\] of (\S+)',open(rpt).read()))
    if not bad: break
    for num,ref in bad:
        for fp in b.GetFootprints():
            if fp.GetReference()==ref:
                for pad in fp.Pads():
                    if pad.GetNumber()==num: pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL); print('  solid GND connection',ref,num)
if os.path.exists(os.path.join(HW,'_therm.rpt')): os.remove(os.path.join(HW,'_therm.rpt'))   # gerber + CPL origin: bottom-left corner
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print('finished')
