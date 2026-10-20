"""Pre-place a short stub + via on every SMD pad that belongs to an inner-plane net (so the autorouter only has to do the signals)."""
import pcbnew,math
T=pcbnew.ToMM; mm=pcbnew.FromMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
def free(b,p,r,net,keep):
    """True when a copper disc of radius r at p clears every pad / via / track of other nets by `keep` (mm) and the board edge."""
    px,py=p
    bb=b.GetBoardEdgesBoundingBox()
    if px-r<T(bb.GetX())+0.4 or px+r>T(bb.GetRight())-0.4 or py-r<T(bb.GetY())+0.4 or py+r>T(bb.GetBottom())-0.4: return False
    for f in b.GetFootprints():
        for pad in f.Pads():
            if pad.GetNetname()==net: continue
            q=pad.GetBoundingBox(); q.Inflate(mm(r+keep))
            if q.Contains(V(px,py)):
                # circle pads: use exact distance
                return False
        # keep off through-hole parts' drills (NPTH)
    for t in b.GetTracks():
        if t.GetNetname()==net and t.Type()!=pcbnew.PCB_VIA_T: continue
        if t.Type()==pcbnew.PCB_VIA_T:
            if math.dist((T(t.GetPosition().x),T(t.GetPosition().y)),p)<r+T(t.GetWidth())/2+keep: return False
        else:
            a=(T(t.GetStart().x),T(t.GetStart().y)); c=(T(t.GetEnd().x),T(t.GetEnd().y)); dx,dy=c[0]-a[0],c[1]-a[1]; L=dx*dx+dy*dy
            u=0 if L==0 else max(0,min(1,((px-a[0])*dx+(py-a[1])*dy)/L))
            if math.dist((a[0]+u*dx,a[1]+u*dy),p)<r+T(t.GetWidth())/2+keep: return False
    return True
def add_stub_vias(b,planes,via=0.6,drill=0.3,width=0.2,keep=0.2):
    nets={n:b.FindNet(n) for n in planes}
    n_added=0; fails=[]
    for f in b.GetFootprints():
        c=f.GetPosition(); ref=f.GetReference()
        pads=[p for p in f.Pads() if p.GetNetname() in nets and p.GetAttribute() in (pcbnew.PAD_ATTRIB_SMD,)]
        if not pads: continue
        # exposed pad: thermal vias inside it
        for i,p in enumerate(sorted(pads,key=lambda q:q.GetNumber())):
            pos=(T(p.GetPosition().x),T(p.GetPosition().y)); net=p.GetNetname(); sz=(T(p.GetSize().x),T(p.GetSize().y))
            if sz[0]>1.5 and sz[1]>1.5:                          # exposed pad
                for dx in (-0.5,0.5):
                    for dy in (-0.5,0.5):
                        v=pcbnew.PCB_VIA(b); v.SetPosition(V(pos[0]+dx,pos[1]+dy)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(0.5)); v.SetDrill(mm(0.25)); v.SetNet(nets[net]); b.Add(v); n_added+=1
                continue
            dirs=[]
            ox,oy=pos[0]-T(c.x),pos[1]-T(c.y)
            d0=(1,0) if abs(ox)>=abs(oy) and ox>=0 else (-1,0) if abs(ox)>=abs(oy) else (0,1) if oy>=0 else (0,-1)
            if abs(ox)<0.05 and abs(oy)<0.05: d0=(0,-1)
            alts=[d0,(-d0[1],d0[0]),(d0[1],-d0[0]),(-d0[0],-d0[1])]
            ok=False
            for dist in (1.1,1.5,2.0,2.6,3.2):
                for d in alts:
                    q=(pos[0]+d[0]*dist,pos[1]+d[1]*dist)
                    if free(b,q,via/2,net,keep):
                        v=pcbnew.PCB_VIA(b); v.SetPosition(V(*q)); v.SetViaType(pcbnew.VIATYPE_THROUGH); v.SetWidth(mm(via)); v.SetDrill(mm(drill)); v.SetNet(nets[net]); b.Add(v)
                        t=pcbnew.PCB_TRACK(b); t.SetStart(V(*pos)); t.SetEnd(V(*q)); t.SetLayer(pcbnew.F_Cu if f.GetLayer()==pcbnew.F_Cu else pcbnew.B_Cu); t.SetWidth(mm(width)); t.SetNet(nets[net]); b.Add(t)
                        ok=True; n_added+=1; break
                if ok: break
            if not ok: fails.append((ref,p.GetNumber()))
    return n_added,fails
