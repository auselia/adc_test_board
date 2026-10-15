"""After routing: widen thin tracks, top GND pour + stitching vias, silkscreen labels, refs to F.Fab."""
import pcbnew,os,math
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
TARGET=os.environ.get('BOARD','adc'); NAME='ADC_Head' if TARGET=='head' else 'ADC_Test'
PCB=os.path.join(HW,NAME+'.kicad_pcb')
mm=pcbnew.FromMM; T=pcbnew.ToMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
OX,OY,W,H=100.0,100.0,64.0,32.0
HEADH=float(os.environ.get('HEADH','22'))
DX=14.0
BOARDS=[('HGND',0.0,0.0,10.0,HEADH)] if TARGET=='head' else [('GND',0.0,0.0,64.0,32.0)]
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
for net,bx0,by0,bx1,by1 in BOARDS:
    if any(z.GetLayer()==pcbnew.F_Cu and z.GetNetname()==net for z in b.Zones()): continue
    z=pcbnew.ZONE(b); z.SetLayer(pcbnew.F_Cu); z.SetNet(gndn[net])
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for x,y in [(bx0+0.3,by0+0.3),(bx1-0.3,by0+0.3),(bx1-0.3,by1-0.3),(bx0+0.3,by1-0.3)]: ch.Append(mm(OX+x),mm(OY+y))
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
# 4. silkscreen. Reference designators go to F.Fab (the board is dense); the silk carries plain-language labels.
for fp in b.GetFootprints(): fp.Reference().SetLayer(pcbnew.F_Fab)
def text(s,x,y,size=0.8,just=pcbnew.GR_TEXT_H_ALIGN_CENTER,layer=pcbnew.F_SilkS,thick=None,mirror=False):
    t=pcbnew.PCB_TEXT(b); t.SetText(s); t.SetLayer(layer); t.SetPosition(V(OX+x,OY+y))
    t.SetTextSize(V(size,size)); t.SetTextThickness(mm(thick or (0.13 if size<1 else 0.18))); t.SetHorizJustify(just); t.SetMirrored(mirror); b.Add(t)
def shape(kind,layer=pcbnew.F_SilkS,width=0.1,fill=False):
    s=pcbnew.PCB_SHAPE(b); s.SetShape(kind); s.SetLayer(layer); s.SetWidth(mm(width))
    if fill: s.SetFilled(True)
    b.Add(s); return s
def logo(x0,y0,s=0.1):
    """Auselia mark (platform/brand/mark/svg/auselia-mark-mono-bone.svg), top-left of its bounding box at (x0,y0) mm, s mm per SVG unit."""
    P=lambda u,v: V(OX+x0+(u-7.0)*s, OY+y0+(v-9.5)*s)
    st=shape(pcbnew.SHAPE_T_SEGMENT,width=5*s); st.SetStart(P(28,58)); st.SetEnd(P(28,12))                # stem
    def bez(p0,c1,c2,p3,n=14):
        return [((1-t)**3*p0[0]+3*(1-t)**2*t*c1[0]+3*(1-t)*t*t*c2[0]+t**3*p3[0],
                 (1-t)**3*p0[1]+3*(1-t)**2*t*c1[1]+3*(1-t)*t*t*c2[1]+t**3*p3[1]) for t in [k/n for k in range(n+1)]]
    pts=bez((28,48),(28,37),(18,31),(7,31))+bez((7,31),(7,42),(17,50),(28,48))[1:]                    # leaf
    lf=shape(pcbnew.SHAPE_T_POLY,width=0.05,fill=True)
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for u,v in pts: ch.Append(P(u,v))
    ch.SetClosed(True); lf.SetPolyShape(pcbnew.SHAPE_POLY_SET(ch))
    c=shape(pcbnew.SHAPE_T_CIRCLE,width=0.05,fill=True); c.SetCenter(P(28,24)); c.SetEnd(P(34,24))   # bud
    for r in (14,22):                                                                                  # two sound arcs
        a=shape(pcbnew.SHAPE_T_ARC,width=3.6*s)
        dy=(r*r-(r*r-8.0**2 if r==14 else r*r-12.6**2))**0.5
        h=8.0 if r==14 else 12.6; dx=(r*r-h*h)**0.5
        a.SetArcGeometry(P(28+dx,24-h),P(28+r,24),P(28+dx,24+h))
# front: labels a person can read without the schematic
if TARGET=='head':
    text('+',1.0,2.2,1.0)
    text('PZT',5.0,5.2,0.8,layer=pcbnew.B_SilkS,thick=0.15,mirror=True); text('+',2.6,5.6,0.9,layer=pcbnew.B_SilkS,thick=0.15,mirror=True); text('-',7.4,5.6,0.9,layer=pcbnew.B_SilkS,thick=0.15,mirror=True)
    text('HEAD v1',5.0,HEADH-0.9,0.8,layer=pcbnew.B_SilkS,thick=0.15,mirror=True)
else:
    text('SENSOR IN',4.6+DX,1.1,0.9); text('HEAD IN',5.0,1.1,0.9); text('+5V on centre',5.0,2.3,0.7)                                  # J1, from the perfboard
    text('SCOPE OUT',36.6+DX,0.9,0.9)                                 # J4, same signal the ADC sees (51 ohm)
    text('+9V',2.6+DX,21.2); text('GND',2.6+DX,28.1)                     # J2
    text('WAKE LEVEL',23.2+DX,25.3,0.8)                               # RV1
    text('1',42.0+DX,11.0,0.8)                                        # PMOD pin 1
    text('CH',12.0+DX,1.2,1.0)                                        # channel number: write it in the box
    r_=shape(pcbnew.SHAPE_T_RECT,width=0.15); r_.SetStart(V(OX+13.2+DX,OY+0.35)); r_.SetEnd(V(OX+21.5+DX,OY+2.15))
    logo(15.6+DX,11.7,0.1)
    text('AUSELIA',21.0+DX,13.4,1.0,pcbnew.GR_TEXT_H_ALIGN_LEFT)
    text('TEST v2',21.0+DX,14.8,0.8,pcbnew.GR_TEXT_H_ALIGN_LEFT)
    # back: the PMOD pin list and the title
    for s_,y_,sz in (('ADS7057 test board v2',6.0,1.5),('Auselia 2026-10',8.4,1.2)):
        text(s_,25+DX,y_,sz,layer=pcbnew.B_SilkS,thick=0.2,mirror=True)
    for i,l in enumerate(['ZedBoard PMOD (J3)','1 CS    7 -','2 -     8 -','3 SDO   9 -','4 SCK  10 nWAKE','5 GND  11 GND','6 3V3  12 3V3']):
        text(l,33.0+DX,16.5+i*1.4,1.0,pcbnew.GR_TEXT_H_ALIGN_LEFT,pcbnew.B_SilkS,0.15,True)
b.GetDesignSettings().SetAuxOrigin(V(OX,OY+(HEADH if TARGET=='head' else H)))
# pads that DRC reports with a starved thermal relief get a solid connection (self-correcting, up to 3 rounds)
import subprocess,re
K='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
for _ in range(3):
    pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(PCB)
    rpt=os.path.join(HW,'_therm.rpt')
    subprocess.run([K,'pcb','drc','--severity-all','-o',rpt,PCB],capture_output=True)
    bad=set(re.findall(r'\[starved_thermal\][^\n]*\n[^\n]*\n[^\n]*\n\s*@\([^)]*\): Pad (\S+) \[H?GND\] of (\S+)',open(rpt).read()))
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
