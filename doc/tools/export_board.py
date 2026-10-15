"""Snapshot of the board for the manual figures (run with KiCad's python): doc/data/board.json.
Coordinates are mm from the top-left corner of the 50 x 32 board."""
import json,os,pcbnew
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','hw'))
OUT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','board.json'))
b=pcbnew.LoadBoard(os.path.join(HW,'ADC_Test.kicad_pcb')); T=pcbnew.ToMM
OX,OY=100.0,100.0
r2=lambda v:round(v,3)
d={'size':[50.0,32.0],'footprints':{},'tracks':[],'vias':[],'zones':[],'texts':[]}
for fp in b.GetFootprints():
    ref=fp.GetReference(); p=fp.GetPosition()
    cy=fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    lcsc=fp.GetFieldText('LCSC') if fp.HasField('LCSC') else ''
    pads=[]
    for pad in fp.Pads():
        pp=pad.GetPosition(); sz=pad.GetSize()
        pads.append(dict(num=pad.GetNumber(),net=pad.GetNetname(),x=r2(T(pp.x)-OX),y=r2(T(pp.y)-OY),w=r2(T(sz.x)),h=r2(T(sz.y)),
                         tht=pad.GetAttribute()==pcbnew.PAD_ATTRIB_PTH,rot=pad.GetOrientationDegrees()))
    d['footprints'][ref]=dict(value=fp.GetValue(),fp=str(fp.GetFPID().GetLibItemName()),x=r2(T(p.x)-OX),y=r2(T(p.y)-OY),
        rot=fp.GetOrientationDegrees(),lcsc=lcsc,dnp=fp.IsDNP(),
        bbox=[r2(T(cy.GetX())-OX),r2(T(cy.GetY())-OY),r2(T(cy.GetRight())-OX),r2(T(cy.GetBottom())-OY)],pads=pads)
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_VIA_T:
        q=t.GetPosition(); d['vias'].append(dict(x=r2(T(q.x)-OX),y=r2(T(q.y)-OY),net=t.GetNetname(),d=r2(T(t.GetWidth(pcbnew.F_Cu))),drill=r2(T(t.GetDrillValue()))))
    else:
        s,e=t.GetStart(),t.GetEnd()
        d['tracks'].append(dict(net=t.GetNetname(),x1=r2(T(s.x)-OX),y1=r2(T(s.y)-OY),x2=r2(T(e.x)-OX),y2=r2(T(e.y)-OY),w=r2(T(t.GetWidth())),
                                layer='F' if t.GetLayer()==pcbnew.F_Cu else 'B'))
for z in b.Zones():
    d['zones'].append(dict(net=z.GetNetname(),layer='F' if z.GetLayer()==pcbnew.F_Cu else 'B'))
d['nets']=sorted({p['net'] for f in d['footprints'].values() for p in f['pads'] if p['net']})
json.dump(d,open(OUT,'w'),indent=0)
print('board.json:',len(d['footprints']),'parts',len(d['tracks']),'tracks',len(d['vias']),'vias',len(d['nets']),'nets')
