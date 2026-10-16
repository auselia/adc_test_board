"""Rules + bottom GND plane, then export the Specctra DSN for Freerouting."""
import pcbnew,os,re,sys
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
mm=pcbnew.FromMM; T=pcbnew.ToMM
TARGET=os.environ.get('BOARD','adc'); NAME='ADC_Head' if TARGET=='head' else 'ADC_Test'
PCB=os.path.join(HW,NAME+'.kicad_pcb')
b=pcbnew.LoadBoard(PCB)
OX,OY=100.0,100.0
import sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from layout_v3 import W as _W, H as _H
BOARDS=[('HGND',0.0,0.0,10.0,float(os.environ.get('HEADH','22')))] if TARGET=='head' else [('GND',0.0,0.0,_W,_H)]
def add_zone(layer,net,x0,y0,x1,y1,inset=0.3):
    x0,y0,x1,y1=x0+OX,y0+OY,x1+OX,y1+OY
    z=pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(b.FindNet(net))
    ch=pcbnew.SHAPE_LINE_CHAIN()
    for (x,y) in [(x0+inset,y0+inset),(x1-inset,y0+inset),(x1-inset,y1-inset),(x0+inset,y1-inset)]: ch.Append(mm(x),mm(y))
    ch.SetClosed(True); z.Outline().AddOutline(ch)
    z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.25)); z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3))
    b.Add(z); return z
if not os.environ.get('NOPLANE'):
    for net,x0,y0,x1,y1 in BOARDS: add_zone(pcbnew.B_Cu,net,x0,y0,x1,y1)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
pcbnew.ExportSpecctraDSN(b,os.path.join(HW,NAME+'.dsn'))
s=open(os.path.join(HW,NAME+'.dsn')).read()
CLR=os.environ.get('CLR','175'); s=s.replace('(clearance 200)','(clearance '+CLR+')',1)
power=['+5V','VMID5','+5V_IN','HV']   # AVDD/+3V3 stay 0.2 mm: they enter the 0.5 mm-pitch ADC pads
m=re.search(r'\(class kicad_default (.*?)\n\s+\(circuit',s,re.S)
names=m.group(1).split(); rest=[n for n in names if n not in power]
blk=lambda nm,ns,w:("    (class %s %s\n      (circuit\n        (use_via \"Via[0-1]_600:300_um\")\n      )\n      (rule\n        (width %d)\n        (clearance %s)\n      )\n    )\n"%(nm,' '.join(ns),w,CLR))
a=s.index("    (class kicad_default"); e=s.index("  (wiring")
s=s[:a]+blk('kicad_default',rest,200)+blk('Power',[n for n in power if n in names],350)+"  )\n"+s[e:]
open(os.path.join(HW,NAME+'_route.dsn'),'w').write(s)
print('dsn ok; nets',len(names),'power',[n for n in power if n in names])
