"""Rules + bottom GND plane, then export the Specctra DSN for Freerouting."""
import pcbnew,os,re,sys
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
mm=pcbnew.FromMM; T=pcbnew.ToMM
PCB=os.path.join(HW,'ADC_Test.kicad_pcb')
b=pcbnew.LoadBoard(PCB)
bb=b.GetBoardEdgesBoundingBox()
def add_zone(layer,inset=0.3):
    z=pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet('GND'))
    x0,y0,x1,y1=[T(v) for v in (bb.GetX(),bb.GetY(),bb.GetRight(),bb.GetBottom())]
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for (x,y) in [(x0+inset,y0+inset),(x1-inset,y0+inset),(x1-inset,y1-inset),(x0+inset,y1-inset)]: ch.Append(mm(x),mm(y))
    ch.SetClosed(True); z.Outline().AddOutline(ch)
    z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3))
    b.Add(z); return z
add_zone(pcbnew.B_Cu)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
pcbnew.ExportSpecctraDSN(b,os.path.join(HW,'ADC_Test.dsn'))
s=open(os.path.join(HW,'ADC_Test.dsn')).read()
s=s.replace('(clearance 200)','(clearance 160)',1)
power=['+5V','VMID5','+9VP','+9V_IN']   # AVDD/+3V3 stay 0.2 mm: they enter the 0.5 mm-pitch ADC pads
m=re.search(r'\(class kicad_default (.*?)\n\s+\(circuit',s,re.S)
names=m.group(1).split(); rest=[n for n in names if n not in power]
blk=lambda nm,ns,w:("    (class %s %s\n      (circuit\n        (use_via \"Via[0-1]_600:300_um\")\n      )\n      (rule\n        (width %d)\n        (clearance 160)\n      )\n    )\n"%(nm,' '.join(ns),w))
a=s.index("    (class kicad_default"); e=s.index("  (wiring")
s=s[:a]+blk('kicad_default',rest,200)+blk('Power',[n for n in power if n in names],350)+"  )\n"+s[e:]
open(os.path.join(HW,'ADC_Test_route.dsn'),'w').write(s)
print('dsn ok; nets',len(names),'power',[n for n in power if n in names])
