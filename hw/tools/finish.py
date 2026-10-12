"""After routing: widen thin tracks, top GND pour + stitching vias, silkscreen labels, refs to F.Fab."""
import pcbnew,os,math
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
PCB=os.path.join(HW,'ADC_Test.kicad_pcb')
mm=pcbnew.FromMM; T=pcbnew.ToMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
OX,OY,W,H=100.0,100.0,50.0,32.0
b=pcbnew.LoadBoard(PCB)
gnd=b.FindNet('GND')
# 1. drop Freerouting's 0.12 mm GND neck-down stubs (the GND pours connect those pads)
for t in list(b.GetTracks()):
    if t.Type()==pcbnew.PCB_TRACE_T and t.GetWidth()<mm(0.15) and t.GetNetname()=='GND': b.Delete(t)
def gnd_stubs():   # GND track ends that touch nothing but the pour
    out=[]
    trs=[t for t in b.GetTracks() if t.GetNetname()=='GND']
    pads=[p for f in b.GetFootprints() for p in f.Pads() if p.GetNetname()=='GND']
    for t in trs:
        if t.Type()!=pcbnew.PCB_TRACE_T: continue
        for e in (t.GetStart(),t.GetEnd()):
            hit=any(o is not t and (o.HitTest(e) if o.Type()==pcbnew.PCB_VIA_T else (o.GetStart()==e or o.GetEnd()==e)) for o in trs) \
                or any(p.HitTest(e) for p in pads)
            if not hit: out.append(t); break
    return out
def via_ok(p,r):       # free copper circle of radius r around p (other nets, both layers)
    for t in b.GetTracks():
        if t.GetNetname()=='GND': continue
        if t.Type()==pcbnew.PCB_VIA_T:
            if math.dist((T(t.GetPosition().x),T(t.GetPosition().y)),p)<r+0.3: return False
        else:
            a=(T(t.GetStart().x),T(t.GetStart().y)); c=(T(t.GetEnd().x),T(t.GetEnd().y))
            dx,dy=c[0]-a[0],c[1]-a[1]; L=dx*dx+dy*dy
            u=0 if L==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L))
            if math.dist((a[0]+u*dx,a[1]+u*dy),p)<r+T(t.GetWidth())/2: return False
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetname()=='GND': continue
            bb=pad.GetBoundingBox(); bb.Inflate(mm(r))
            if bb.Contains(V(*p)): return False
    return True
for _ in range(5):
    st=gnd_stubs()
    if not st: break
    for t in st:
        for e in (t.GetStart(),t.GetEnd()):
            p=(T(e.x),T(e.y))
            trs=[o for o in b.GetTracks() if o.GetNetname()=='GND' and o is not t]
            pads=[q for f in b.GetFootprints() for q in f.Pads() if q.GetNetname()=='GND']
            if any(q.HitTest(e) for q in pads) or any((o.HitTest(e) if o.Type()==pcbnew.PCB_VIA_T else (o.GetStart()==e or o.GetEnd()==e)) for o in trs): continue
            if via_ok(p,0.3+0.16):
                v=pcbnew.PCB_VIA(b); v.SetPosition(e); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
                v.SetNet(gnd); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); print('  GND via at track end',round(p[0]-OX,2),round(p[1]-OY,2))
            else:
                b.Delete(t); print('  removed GND stub at',round(p[0]-OX,2),round(p[1]-OY,2))
            break
for t in gnd_stubs():          # anything still dangling: the pours already carry GND there
    print('  removed dangling GND stub',round(T(t.GetStart().x)-OX,2),round(T(t.GetStart().y)-OY,2)); b.Delete(t)
# 2. top GND pour (bottom pour exists from prep_route)
if not any(z.GetLayer()==pcbnew.F_Cu for z in b.Zones()):
    z=pcbnew.ZONE(b); z.SetLayer(pcbnew.F_Cu); z.SetNet(gnd)
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for x,y in [(0.3,0.3),(W-0.3,0.3),(W-0.3,H-0.3),(0.3,H-0.3)]: ch.Append(mm(OX+x),mm(OY+y))
    ch.SetClosed(True); z.Outline().AddOutline(ch)
    z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3)); z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
for z in b.Zones(): z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
# 3. stitching vias on a 2 mm grid where both pours are solid and nothing else is near
def clear_of_others(p,r):
    for t in b.GetTracks():
        if t.Type()==pcbnew.PCB_VIA_T and math.dist((T(t.GetPosition().x),T(t.GetPosition().y)),p)<1.0: return False
        if t.GetNetCode()==gnd.GetNetCode(): continue
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
zones={z.GetLayer():z for z in b.Zones()}
added=[]
gx=1.6
while gx<W-1.0:
    gy=1.6
    while gy<H-1.0:
        p=(OX+gx,OY+gy)
        if all(zones[l].HitTestFilledArea(l,V(*p),mm(0.45)) for l in (pcbnew.F_Cu,pcbnew.B_Cu)) and clear_of_others(p,0.65) \
           and all(math.dist(p,q)>1.6 for q in added):
            v=pcbnew.PCB_VIA(b); v.SetPosition(V(*p)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
            v.SetNet(gnd); v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); b.Add(v); added.append(p)
        gy+=2.0
    gx+=2.0
print('stitching vias',len(added))
# 4. reference designators to F.Fab (dense board); keep a few useful ones on silk
for fp in b.GetFootprints():
    r=fp.Reference()
    if fp.GetReference() in ('J1',): continue
    r.SetLayer(pcbnew.F_Fab)
def text(s,x,y,size=0.8,just=pcbnew.GR_TEXT_H_ALIGN_CENTER,layer=pcbnew.F_SilkS):
    t=pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetPosition(V(OX+x,OY+y))
    t.SetTextSize(V(size,size)); t.SetTextThickness(mm(0.13 if size<1 else 0.18)); t.SetHorizJustify(just); b.Add(t)
for fp in b.GetFootprints():
    p=fp.GetPosition(); x,y=T(p.x)-OX,T(p.y)-OY; ref=fp.GetReference()
    if ref=='J1': fp.Reference().SetPosition(V(OX+x,OY+y-5.2)); fp.Reference().SetText('J1');
    if ref=='J2': fp.Reference().SetPosition(V(OX+x,OY+y-2.0))
    if ref=='J3': fp.Reference().SetPosition(V(OX+x+1.27,OY+y-2.2))
text('SMA IN',4.6,1.2,1.0)
text('+9V',2.6,21.2); text('GND',2.6,28.1)
text('THRESHOLD',23.8,25.6,0.8)
for s_,y_,sz in (('ADS7057 test board v1',6.0,1.5),('Auselia 2026-10',8.4,1.2)):   # title on the empty back side
    t=pcbnew.PCB_TEXT(b); t.SetText(s_); t.SetLayer(pcbnew.B_SilkS); t.SetPosition(V(OX+25,OY+y_)); t.SetTextSize(V(sz,sz))
    t.SetTextThickness(mm(0.2)); t.SetMirrored(True); b.Add(t)
# PMOD legend on the back (the front corner holds the MON SMA)
for i,l in enumerate(['ZedBoard PMOD (J3)','1 CS    7 -','2 -     8 -','3 SDO   9 -','4 SCK  10 nWAKE','5 GND  11 GND','6 3V3  12 3V3']):
    t=pcbnew.PCB_TEXT(b); t.SetText(l); t.SetLayer(pcbnew.B_SilkS); t.SetPosition(V(OX+33.0,OY+16.5+i*1.4))
    t.SetTextSize(V(1.0,1.0)); t.SetTextThickness(mm(0.15)); t.SetMirrored(True); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT); b.Add(t)
text('MON',39.9,1.4,0.9)
text('CH',9.6,1.2,1.0)                     # channel number, written by hand in the box
r_=pcbnew.PCB_SHAPE(b); r_.SetShape(pcbnew.SHAPE_T_RECT); r_.SetLayer(pcbnew.F_SilkS); r_.SetWidth(mm(0.15))
r_.SetStart(V(OX+11.0,OY+0.35)); r_.SetEnd(V(OX+19.5,OY+2.15)); b.Add(r_)
text('1',42.0,11.0,0.8)      # next to pad 1 (PMOD pin 1)
b.GetDesignSettings().SetAuxOrigin(V(OX,OY+H))
# pads that DRC reports with a starved thermal relief get a solid connection (self-correcting, up to 3 rounds)
import subprocess,re
K='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
for _ in range(3):
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(PCB)
    rpt=os.path.join(HW,'_therm.rpt')
    subprocess.run([K,'pcb','drc','--severity-all','-o',rpt,PCB],capture_output=True)
    bad=set(re.findall(r'\[starved_thermal\][^\n]*\n[^\n]*\n[^\n]*\n\s*@\([^)]*\): Pad (\S+) \[GND\] of (\S+)',open(rpt).read()))
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
