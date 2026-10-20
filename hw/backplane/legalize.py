import pcbnew
T=pcbnew.ToMM; mm=pcbnew.FromMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
def legalize(fps,fixed,gap=0.15,iters=300,log=True):
    """Push overlapping courtyards apart (movable = not in fixed)."""
    seen=set()
    for it in range(iters):
        moved=False
        cy={r:f.GetCourtyard(pcbnew.F_CrtYd).BBox() if f.GetLayer()==pcbnew.F_Cu else f.GetCourtyard(pcbnew.B_CrtYd).BBox() for r,f in fps.items()}
        refs=sorted(r for r in cy if cy[r].GetWidth()>0)
        for i,a in enumerate(refs):
            for c in refs[i+1:]:
                A,B=cy[a],cy[c]
                if fps[a].GetLayer()!=fps[c].GetLayer(): continue
                ox=T(min(A.GetRight(),B.GetRight())-max(A.GetX(),B.GetX())); oy=T(min(A.GetBottom(),B.GetBottom())-max(A.GetY(),B.GetY()))
                if ox<=0.02 or oy<=0.02: continue
                mv,other=(c,a) if a in fixed else (a,c)
                if mv in fixed:
                    if (a,c) not in seen: print('  fixed overlap',a,c); seen.add((a,c))
                    continue
                M,O=cy[mv],cy[other]
                if ox<oy: d=(ox+gap)*(1 if M.GetCenter().x>=O.GetCenter().x else -1); delta=V(d,0)
                else:     d=(oy+gap)*(1 if M.GetCenter().y>=O.GetCenter().y else -1); delta=V(0,d)
                fps[mv].Move(delta); moved=True
                cy[mv]=fps[mv].GetCourtyard(pcbnew.F_CrtYd).BBox()
        if not moved: break
