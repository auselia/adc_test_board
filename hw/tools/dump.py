"""Dump pads, courtyards, tracks, vias and ratsnest of ADC_Test.kicad_pcb to JSON (for plot.py)."""
import pcbnew,json,sys,os
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
b=pcbnew.LoadBoard(os.path.join(HW,'ADC_Test.kicad_pcb'))
T=pcbnew.ToMM; out={'pads':[],'cy':[],'tracks':[],'vias':[],'rats':[],'refs':[]}
for fp in b.GetFootprints():
    cy=fp.GetCourtyard(pcbnew.F_CrtYd)
    bb=fp.GetBoundingBox(False)
    out['cy'].append([T(bb.GetX()),T(bb.GetY()),T(bb.GetWidth()),T(bb.GetHeight())])
    p=fp.GetPosition(); out['refs'].append([fp.GetReference(),T(p.x),T(p.y)])
    for pad in fp.Pads():
        bb=pad.GetBoundingBox(); pc=pad.GetPosition(); out['pads'].append([T(bb.GetX()),T(bb.GetY()),T(bb.GetWidth()),T(bb.GetHeight()),pad.GetNetname(),pad.GetAttribute()==pcbnew.PAD_ATTRIB_PTH,T(pc.x),T(pc.y)])
for t in b.GetTracks():
    if t.Type()==pcbnew.PCB_VIA_T: out['vias'].append([T(t.GetPosition().x),T(t.GetPosition().y)])
    else: out['tracks'].append([T(t.GetStart().x),T(t.GetStart().y),T(t.GetEnd().x),T(t.GetEnd().y),T(t.GetWidth()),t.GetLayer()==pcbnew.F_Cu,t.GetNetname()])
json.dump(out,open(sys.argv[1],'w'))
print('dumped',len(out['pads']),'pads',len(out['rats']),'rats',len(out['tracks']),'tracks')
