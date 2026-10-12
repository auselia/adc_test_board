"""JLCPCB BOM + CPL from the netlist and the KiCad position file.
Left out: H1/H2 (mounting holes) and C31 (DNP). THT parts stay in: JLCPCB wave-solders them (Economic, top side)."""
import csv,os,sys,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sexp import *
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
SKIP={'H1','H2','C31'}   # THT: hand-soldered, keeps them out of the extended-part fee
import re
# JLC rotation offsets, from matthewlai/JLCKicadTools cpl_rotations_db.csv (the table kicad-jlcpcb-tools uses)
ROT_RULES=[(r'^SOT-223',180),(r'^SOT-23',-90),(r'^SOIC-',270),(r'^CP_EIA-',180)]
# Absolute CPL rotations taken from the JLCPCB placement viewer (upload of 2026-10-12), where the community
# table was wrong for these parts. Assumes JLC rotation is counter-clockwise positive, like KiCad.
#   U5  XC6206 SOT-23-3L : viewer showed the single leg on top, our pad 3 is on the right -> 270 -> 180
#   C29 tantalum         : viewer showed + on the right, our pad 1 (+) is on the left      -> 180 -> 0
#   J2  1x2 header       : viewer showed the pins horizontal, our pads are vertical        -> 0 -> 90
#   J3  2x6 right angle  : viewer showed the row horizontal, our pads run vertically       -> 0 -> 90
ROT_ABS={'U5':180,'C29':0,'J2':90,'J3':90}
def rot_off(pkg):
    for rx,off in ROT_RULES:
        if re.match(rx,pkg): return off
    return 0
t=parse(open(os.path.join(HW,'ADC_Test.net')).read())
comps={}
for c in find(get(t,'components'),'comp'):
    ref=get(c,'ref')[1]
    fields={f[1][1]:f[2] for f in find(get(c,'fields') or [],'field') if len(f)>2}
    comps[ref]=dict(value=get(c,'value')[1],fp=get(c,'footprint')[1].split(':')[1],lcsc=fields.get('LCSC',''))
groups=collections.OrderedDict()
key=lambda r:(r.rstrip('0123456789'),int(''.join(ch for ch in r if ch.isdigit())))
for ref in sorted(comps,key=key):
    if ref in SKIP: continue
    c=comps[ref]
    # one BOM line per LCSC part for the connectors (JLC warns when two lines match the same part)
    names={'C496549':'SMA jack','C492401':'Header 1x2','C60565':'Header 2x6 right angle','C34845':'20k trimmer'}
    val=names.get(c['lcsc'],c['value']) if ref in ('J1','J2','J3','J4','RV1') else c['value']
    fpn=c['fp'] if val==c['value'] else {'C496549':'SMA_Amphenol_132134-11_Vertical'}.get(c['lcsc'],c['fp'])
    groups.setdefault((val,fpn,c['lcsc']),[]).append(ref)
with open(os.path.join(HW,'fab','ADC_Test_BOM_JLC.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['Comment','Designator','Footprint','LCSC Part #'])
    for (v,fp,l),refs in groups.items(): w.writerow([v,','.join(refs),fp,l])
rows=list(csv.DictReader(open(os.path.join(HW,'fab','ADC_Test_pos_kicad.csv'))))
with open(os.path.join(HW,'fab','ADC_Test_CPL_JLC.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
    for r in rows:
        if r['Ref'] in SKIP: continue
        rot=ROT_ABS.get(r['Ref'],(float(r['Rot'])+rot_off(r['Package']))%360)
        w.writerow([r['Ref'],'%.3fmm'%float(r['PosX']),'%.3fmm'%float(r['PosY']),'Top','%g'%rot])
missing=[r for r,c in comps.items() if r not in SKIP and not c['lcsc']]
print('BOM lines',len(groups),'parts',sum(len(v) for v in groups.values()),'missing LCSC',missing)
