"""Cost estimate for a JLCPCB Economic PCBA order shipped to Chile.
Prices: JLCPCB parts library and PCBA fee page, checked 2026-10-12. Hand-soldered parts at LCSC prices.
usage: python3 cost.py [N ...]       N = number of assembled boards (5 bare PCBs are always made)
"""
import sys
# ref-group: (description, LCSC, unit $, qty per board, block, extended?)
PARTS=[
 ('ADS7057 14-bit ADC','C2669902',7.9823,1,'ADC',True),
 ('OPA2365 dual op-amp','C130011',1.3828,2,'Filters',True),
 ('THS4531 differential driver','C705347',2.9920,1,'Driver',True),
 ('LM393 comparator','C7955',0.0662,1,'Wake',False),
 ('AMS1117-5.0','C6187',0.2546,1,'Power',False),
 ('AMS1117-3.3','C6186',0.2080,1,'Power',False),
 ('SS14 diode','C2480',0.0191,1,'Power',False),
 ('22 uF 0805','C45783',0.2369,2,'Power',False),
 ('10 uF 25 V 0805','C15850',0.0688,1,'Power',False),
 ('100 pF C0G (filters)','C14858',0.0086,5,'Filters',False),
 ('100 pF C0G (ADC input)','C14858',0.0086,4,'ADC',False),
 ('100 nF','C14663',0.0140,9,'mixed',False),
 ('1 uF','C15849',0.0163,4,'mixed',False),
 ('4.7 uF (AVDD)','C19666',0.0295,1,'ADC',False),
 ('10 uF (VMID)','C19702',0.0305,1,'Filters',False),
 ('Resistors 0603 (24 pcs)','basic',0.0024,24,'mixed',False),
]
HAND=[('SMA jack (J1)','C496549',0.40),('20k trimmer 3296W (RV1)','C34845',0.86),('Pin headers 1x2 + 2x6 R/A','-',0.30)]
SMD_JOINTS=150
FIX={'PCB fabrication (5 pcs, 2 layers, 50x32 mm)':4.00,'PCBA setup fee':8.18,'Stencil':1.53,'Confirm parts placement':0.45}
EXT_FEE=3.07; XRAY=1.64; JOINT=0.0016; IVA=0.19
def ship(total):           # Global Standard Direct Line to Chile (<= $150 declared value), else FedEx
    return (9.00,'Global Standard (13-22 days)') if total<=150 else (37.04,'FedEx (6-10 days)')
def quote(N,show=True):
    parts=sum(u*q for _,_,u,q,_,_ in PARTS)*N
    hand=sum(u for _,_,u in HAND)*N
    ext=sum(1 for p in PARTS if p[5])*EXT_FEE
    fees=sum(FIX.values())+ext+XRAY*N+JOINT*SMD_JOINTS*N
    goods=parts+fees
    s,how=ship(goods)
    iva=IVA*(goods+s)
    total=goods+s+iva+hand
    if show:
        print(f'===== {N} assembled boards =====')
        print('Components (JLC buys and places them):')
        for d,l,u,q,b,e in PARTS: print(f'  {d:30s} {l:9s} {q*N:3d} x ${u:.4f} = ${u*q*N:7.2f}{"  (extended)" if e else ""}')
        print(f'  {"":30s} {"":9s} components  ${parts:7.2f}')
        print('JLCPCB fees:')
        for k,v in FIX.items(): print(f'  {k:46s} ${v:7.2f}')
        print(f'  {"Extended-part fee: 3 x $3.07":46s} ${ext:7.2f}')
        print(f'  {"X-ray, ADS7057: %d x $1.64"%N:46s} ${XRAY*N:7.2f}')
        print(f'  {"SMT joints: %d x %d x $0.0016"%(SMD_JOINTS,N):46s} ${JOINT*SMD_JOINTS*N:7.2f}')
        print(f'JLCPCB order (goods):                           ${goods:7.2f}')
        print(f'Shipping, {how:36s} ${s:7.2f}')
        print(f'IVA 19% on goods + shipping:                    ${iva:7.2f}')
        print(f'Hand-soldered parts (bought separately):        ${hand:7.2f}')
        print(f'TOTAL                                           ${total:7.2f}   (${total/N:.2f} per board)\n')
    return dict(parts=parts,fees=fees,goods=goods,ship=s,iva=iva,hand=hand,total=total)
if __name__=='__main__':
    Ns=[int(a) for a in sys.argv[1:]] or [2,3,5]
    for n in Ns: quote(n)
