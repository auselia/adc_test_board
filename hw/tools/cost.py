"""Cost estimate for a JLCPCB Economic PCBA order shipped to Chile, read from fab/ADC_Test_BOM_JLC.csv.
Prices: JLCPCB parts library and PCBA fee page, checked 2026-10-12.
usage: python3 cost.py [N ...]       N = assembled boards (5 bare PCBs are always made)
Two ways to get the through-hole parts (SMA x2, trimmer, two headers):
  jlc   JLCPCB solders them (manual-assembly joints + hand-soldering labor, and maybe the extended-part fee)
  self  you buy and solder them yourself (LCSC prices as a proxy)
"""
import csv,json,os,sys
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
PRICE={'C14858':0.0086,'C14663':0.0140,'C15849':0.0163,'C19702':0.0305,'C19666':0.0295,'C15850':0.0688,'C11366':0.1890,
 'C2480':0.0191,'C496549':0.4023,'C492401':0.0186,'C60565':0.0815,'C25804':0.0022,'C4184':0.0020,'C23018':0.0020,
 'C21190':0.0022,'C4190':0.0020,'C22859':0.0032,'C23345':0.0025,'C4216':0.0020,'C23197':0.0020,'C34845':0.8600,
 'C130011':1.3828,'C705347':2.9920,'C2669902':7.9823,'C5446':0.1429,'C7955':0.0662,'C6187':0.2546}
EXT={'C130011','C705347','C2669902','C11366'}                  # extended SMD parts
EXT_THT={'C496549','C492401','C60565','C34845'}                 # extended through-hole parts
THT_REFS={'J1','J2','J3','J4','RV1'}
XRAY_REFS={'U4'}                                                # ADS7057 (QFN, hidden joints)
FIX={'PCB fabrication (5 pcs, 2 layers, 50x32 mm)':4.00,'PCBA setup fee':8.18,'Stencil':1.53,'Confirm parts placement':0.45}
EXT_FEE=3.07; XRAY=1.64; SMT=0.0016; MANUAL=0.0164; LABOR=3.58; IVA=0.19
def load():
    rows=list(csv.DictReader(open(os.path.join(HW,'fab','ADC_Test_BOM_JLC.csv'))))
    j=json.load(open(os.path.join(HW,'fab','joints.json')))
    smd=[];tht=[]
    for r in rows:
        refs=r['Designator'].split(','); l=r['LCSC Part #']
        for ref in refs: (tht if ref in THT_REFS else smd).append((ref,l,r['Comment']))
    return smd,tht,j
def quote(N,mode,ext_tht=False,show=False):
    smd,tht,j=load()
    p_smd=sum(PRICE[l] for _,l,_ in smd)*N
    p_tht=sum(PRICE[l] for _,l,_ in tht)*N
    fees=sum(FIX.values())+len({l for _,l,_ in smd if l in EXT})*EXT_FEE+XRAY*N+SMT*j['smd']*N
    parts=p_smd
    hand=0
    if mode=='jlc':
        parts+=p_tht
        fees+=MANUAL*j['tht']*N+LABOR
        if ext_tht: fees+=len({l for _,l,_ in tht if l in EXT_THT})*EXT_FEE
    else: hand=p_tht
    goods=parts+fees
    ship=9.00 if goods<=150 else 37.04
    iva=IVA*(goods+ship)
    total=goods+ship+iva+hand
    return dict(parts=parts,fees=fees,goods=goods,ship=ship,iva=iva,hand=hand,total=total)
def main(Ns):
    smd,tht,j=load()
    print(f'{len(smd)} SMD parts, {len(tht)} through-hole parts, {j["smd"]} SMD joints, {j["tht"]} THT joints per board')
    print(f'{"":34s}'+''.join(f'{n:>10d}' for n in Ns)+'   boards')
    for label,mode,e in (('JLC solders THT (low)','jlc',False),('JLC solders THT (high: +4 ext fees)','jlc',True),('You solder THT','self',False)):
        print(f'{label:34s}'+''.join(f'{quote(n,mode,e)["total"]:10.2f}' for n in Ns)+'   total $')
    print()
    for n in Ns:
        for label,mode,e in (('JLC solders THT (low)','jlc',False),('JLC solders THT (high)','jlc',True),('You solder THT','self',False)):
            q=quote(n,mode,e)
            print(f'N={n} {label:24s} parts {q["parts"]:7.2f} fees {q["fees"]:6.2f} ship {q["ship"]:5.2f} IVA {q["iva"]:6.2f} own {q["hand"]:5.2f} = {q["total"]:7.2f}')
        print()
if __name__=='__main__':
    main([int(a) for a in sys.argv[1:]] or [2,3,5])
