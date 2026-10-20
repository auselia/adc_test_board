"""Build the .kicad_pcb of a backplane board from its model json + a layout (runs in KiCad's python).
usage: kicad-python bp_pcb.py adapter|module"""
import sys,os,json,math
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','tools'))
import pcbnew
mm=pcbnew.FromMM; T=pcbnew.ToMM
def V(x,y): return pcbnew.VECTOR2I(mm(x),mm(y))
FPDIR='/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/'
OX,OY=100.0,100.0
def load_fp(fpid):
    lib,name=fpid.split(':'); return pcbnew.FootprintLoad((os.path.join(HERE,'Bp.pretty') if lib=='Bp' else FPDIR+lib+'.pretty'),name)
def make(name,model,place,outline,texts=(),drop_pads=None):
    """place: ref -> (x,y,rot) in board coords (mm, origin top-left of the outline); side comes from the model."""
    b=pcbnew.BOARD(); b.SetCopperLayerCount(4)
    nets=sorted({n for p in model for n in p['nets'].values() if n!='NC'})
    ni={}
    for n in nets:
        it=pcbnew.NETINFO_ITEM(b,n); b.Add(it); ni[n]=it
    fps={}
    for p in model:
        m=load_fp(p['fp']); b.Add(m); ref=p['ref']; fps[ref]=m
        m.SetReference(ref); m.SetValue(p['value']); lib,nm=p['fp'].split(':'); m.SetFPID(pcbnew.LIB_ID(lib,nm))
        for pad in m.Pads():
            n=p['nets'].get(pad.GetNumber())
            if n and n!='NC': pad.SetNet(ni[n])
        if p['lcsc']:
            m.SetField('LCSC',p['lcsc']); f=m.GetField('LCSC'); f.SetVisible(False); f.SetLayer(pcbnew.F_Fab)
        x,y,rot=place[ref]
        m.SetPosition(V(OX+x,OY+y)); m.SetOrientationDegrees(rot)
        if p['side']=='bot':
            m.Flip(m.GetPosition(),False)          # flip about the horizontal axis through the part
            m.SetOrientationDegrees((m.GetOrientationDegrees()))
        r=m.Reference(); r.SetTextSize(V(0.8,0.8)); r.SetTextThickness(mm(0.12)); m.Value().SetVisible(False)
        if ref.startswith('H') or ref.startswith('TP'): m.SetAttributes(m.GetAttributes()|pcbnew.FP_EXCLUDE_FROM_POS_FILES|pcbnew.FP_EXCLUDE_FROM_BOM) if ref.startswith('TP') else None
    x0,y0,x1,y1=outline
    def line(a,c,d,e):
        s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(mm(0.1)); s.SetStart(V(OX+a,OY+c)); s.SetEnd(V(OX+d,OY+e)); b.Add(s)
    line(x0,y0,x1,y0); line(x1,y0,x1,y1); line(x1,y1,x0,y1); line(x0,y1,x0,y0)
    for (t,x,y,size,layer,rot) in texts:
        tx=pcbnew.PCB_TEXT(b); tx.SetText(t); tx.SetPosition(V(OX+x,OY+y)); tx.SetLayer(layer); tx.SetTextSize(V(size,size)); tx.SetTextThickness(mm(0.15)); tx.SetTextAngleDegrees(rot); b.Add(tx)
    return b,fps
def save(b,path): b.Save(path)
