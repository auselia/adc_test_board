"""After routing: reference designators to F.Fab (no silk clutter), fill zones, save.  usage: kicad-python bp_finish.py NAME"""
import pcbnew,os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); name=sys.argv[1]
b=pcbnew.LoadBoard(os.path.join(HERE,name+'.kicad_pcb'))
for f in b.GetFootprints():
    r=f.Reference(); r.SetLayer(pcbnew.B_Fab if f.GetLayer()==pcbnew.B_Cu else pcbnew.F_Fab); r.SetVisible(True)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(os.path.join(HERE,name+'.kicad_pcb')); print('finished')
