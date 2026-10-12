import pcbnew,sys
b=pcbnew.LoadBoard(sys.argv[1] if len(sys.argv)>1 else 'ADC_Test.kicad_pcb')
T=pcbnew.ToMM
cy={f.GetReference():f.GetCourtyard(pcbnew.F_CrtYd).BBox() for f in b.GetFootprints()}
r=list(cy)
for i,a in enumerate(r):
    for c in r[i+1:]:
        A,B=cy[a],cy[c]
        ox=min(A.GetRight(),B.GetRight())-max(A.GetX(),B.GetX()); oy=min(A.GetBottom(),B.GetBottom())-max(A.GetY(),B.GetY())
        if ox>pcbnew.FromMM(0.02) and oy>pcbnew.FromMM(0.02): print('overlap',a,c,'dx %.2f dy %.2f'%(T(ox),T(oy)))
