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
for fp in list(b.GetFootprints()):    # single-spoke thermal there: connect solid
    if fp.GetReference() in ('R21','R23','C26','C27'):
        for pad in fp.Pads():
            if pad.GetNetname()=='GND': pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
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
for s_,y_,sz in (('ADS7057 test board v1',14.0,1.5),('Auselia 2026-10',16.4,1.2)):   # title on the empty back side
    t=pcbnew.PCB_TEXT(b); t.SetText(s_); t.SetLayer(pcbnew.B_SilkS); t.SetPosition(V(OX+25,OY+y_)); t.SetTextSize(V(sz,sz))
    t.SetTextThickness(mm(0.2)); t.SetMirrored(True); b.Add(t)
# PMOD legend (top right, clear of J3)
for i,l in enumerate(['ZedBoard PMOD','1 CS   7 -','2 -    8 -','3 SDO  9 -','4 SCK 10 nWAKE','5 GND 11 GND','6 3V3 12 3V3']):
    text(l,39.4,1.2+i*1.15,0.8,pcbnew.GR_TEXT_H_ALIGN_LEFT)
text('1',42.0,11.0,0.8)      # next to pad 1 (PMOD pin 1)
b.GetDesignSettings().SetAuxOrigin(V(OX,OY+H))   # gerber + CPL origin: bottom-left corner
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print('finished')
