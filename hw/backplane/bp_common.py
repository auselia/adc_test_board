"""Shared helpers for the two backplane boards: one Python model feeds the schematic (core.add) and the PCB (model.json)."""
import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'..','tools'))
import core
from core import *
class _All:
    def __contains__(self,x): return True
    def update(self,*a): pass
core.GLOBALS=_All()                      # every net is a global label (no wires), like the main board
FP_R='Resistor_SMD:R_0603_1608Metric'; FP_C='Capacitor_SMD:C_0603_1608Metric'; FP_C8='Capacitor_SMD:C_0805_2012Metric'
FP_LED='LED_SMD:LED_0603_1608Metric'; FP_D='Diode_SMD:D_SMA'; FP_TP='TestPoint:TestPoint_Pad_D1.5mm'
FP_HOLE='MountingHole:MountingHole_3.2mm_M3'
# LCSC numbers checked in the JLCPCB parts library (2026-10-20); "base" = Basic part, "ext" = Extended part ($3 each, once per board type)
LCSC={'47R':'C23182','22R':'C23345','1k':'C21190','100k':'C25803','100nF':'C14663','10uF':'C19702','10nF':'C57112','22uF 25V':'C45783',
      'LED':'C2286','SS14':'C2480'}
PARTS=[]; SHEET=None
def start(name,title,paper='A1'):
    global SHEET
    core.PROJECT=name
    r=D.root; r.paper=paper; r.title=title; r.file=name+'.kicad_sch'; r.path='/'+r.uuid
    SHEET=r; return r
def part(libid,value,fp,sx,sy,nets,ref,lcsc='',side='top',rot=0,props=None,dnp=False,pcb=True,**kw):
    pr=dict(props or {})
    if lcsc: pr['LCSC']=lcsc
    add(SHEET,libid,value,fp,sx,sy,nets,rot=rot,ref=ref,props=pr,dnp=dnp,**kw)
    PARTS.append(dict(ref=ref,value=value,fp=fp,lcsc=lcsc,nets={str(k):v for k,v in nets.items()},side=side,dnp=dnp))
    return ref
def R(sx,sy,val,a,b,ref,rot=90): return part('Device:R',val,FP_R,sx,sy,{'1':a,'2':b},ref,LCSC[val],rot=rot)
def C(sx,sy,val,a,b,ref,rot=0):
    fp=FP_C8 if '25V' in val else FP_C
    return part('Device:C',val,fp,sx,sy,{'1':a,'2':b},ref,LCSC[val],rot=rot)
def save_model(path):
    json.dump(PARTS,open(path,'w'),indent=1)
