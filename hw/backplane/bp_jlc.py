"""JLCPCB BOM + CPL for a backplane board.  usage: python3 bp_jlc.py BP_Module|FMC_Adapter   (needs fab/NAME_pos_kicad.csv from fab_bp.sh)"""
import csv,json,os,re,sys,collections
HERE=os.path.dirname(os.path.abspath(__file__)); name=sys.argv[1]
model=json.load(open(os.path.join(HERE,'out',name+'_model.json')))
SKIP=lambda r: r.startswith('H') or r.startswith('TP')
NAMES={'C19193816':'IDC box header 2x25','C36191':'Socket 2x6 2.54 mm','C8465':'Screw terminal 5.08 mm 2P','C2875619':'FMC plug ASP-134602-01'}
# JLC rotation offsets (community table); verify every row of the CPL in the JLCPCB placement viewer before paying
ROT_RULES=[(r'^TSSOP-',270),(r'^QFN-',270),(r'^SOT-23',270),(r'^D_SMA',180)]
def rot_off(fp):
    pkg=fp.split(':')[1]
    for rx,off in ROT_RULES:
        if re.match(rx,pkg): return off
    return 0
os.makedirs(os.path.join(HERE,'fab'),exist_ok=True)
groups=collections.OrderedDict(); fpmap={p['ref']:p for p in model}
key=lambda r:(r.rstrip('0123456789'),int(''.join(c for c in r if c.isdigit())))
for r in sorted(fpmap,key=key):
    p=fpmap[r]
    if SKIP(r): continue
    v=NAMES.get(p['lcsc'],p['value']); groups.setdefault((v,p['fp'].split(':')[1],p['lcsc']),[]).append(r)
with open(os.path.join(HERE,'fab',name+'_BOM_JLC.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['Comment','Designator','Footprint','LCSC Part #'])
    for (v,fp,l),refs in groups.items(): w.writerow([v,','.join(refs),fp,l])
rows=list(csv.DictReader(open(os.path.join(HERE,'fab',name+'_pos_kicad.csv'))))
with open(os.path.join(HERE,'fab',name+'_CPL_JLC.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
    for r in rows:
        if SKIP(r['Ref']): continue
        side='Bottom' if r['Side'].lower().startswith('b') else 'Top'
        rot=(float(r['Rot'])+rot_off(fpmap[r['Ref']]['fp']))%360
        w.writerow([r['Ref'],'%.3fmm'%float(r['PosX']),'%.3fmm'%float(r['PosY']),side,'%g'%rot])
print(name,'BOM lines',len(groups),'parts',sum(len(v) for v in groups.values()),'missing LCSC',[r for r,p in fpmap.items() if not SKIP(r) and not p['lcsc']])
