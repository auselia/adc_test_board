"""Cost model for a JLCPCB Economic PCBA order shipped to Chile, calibrated on the real quote of 2026-10-12
(5 assembled boards: PCB $4.00 + PCBA $110.36 = $114.36, see README). Part prices come from the JLC library.
usage: python3 cost.py [N ...]       N = assembled boards (5 bare PCBs are always made)
"""
import csv,json,os,sys
HW=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
PRICE={'C1653':0.0058,'C14858':0.0086,'C14663':0.0140,'C15849':0.0163,'C19702':0.0305,'C19666':0.0295,'C15850':0.0688,'C11366':0.1890,
 'C2480':0.0191,'C496549':0.4023,'C492401':0.0186,'C60565':0.0815,'C25804':0.0022,'C4184':0.0020,'C23018':0.0020,
 'C21190':0.0022,'C4190':0.0020,'C22859':0.0032,'C23345':0.0025,'C4216':0.0020,'C23197':0.0020,'C34845':0.8600,
 'C130011':1.3828,'C23182':0.0017,'C22935':0.0019,'C75644':0.0896,'C1567':0.0081,'C15525':0.0256,'C307331':0.0099,'C26083':0.0024,'C25744':0.0016,'C25120':0.0023,'C96626':2.674,'C165948':0.1862,'C2862588':0.7077,'C25819':0.0016,'C25810':0.0040,'C23212':0.0018,'C22809':0.0017,'C1546':0.0060,'C130194':1.774,'C23186':0.0015,'C14709':0.0146,'C45783':0.1924,'C705347':2.9920,'C2669902':7.9823,'C5446':0.1429,'C7955':0.0662,'C6187':0.2546}
PRICE_SCALE=80.14/83.32                  # quote: components $80.14 for 5 boards, table sum $83.32
EXT_SMD={'C130011','C705347','C2669902','C75644','C96626','C2862588'}
THT_REFS={'J1','J3','J4','J6','J7'}
PCB=4.00; SETUP=8.24; STENCIL=1.55
EXT_FEE=12.36/4          # 4 extended SMD part types; the 4 through-hole types were NOT charged
SMT=1.32/775; MANUAL=2.23/135; LABOR=3.61; NITROGEN=0.91/5      # per joint, per joint, per order, per board
CONFIRM=0.45             # optional "Confirm Parts Placement", not in the quote
SHIP=10.75               # Global Standard Direct Line, 0.41 kg; DHL Express was $42.51
IVA=0.19
def load(board='adc'):
    name='ADC_Head' if board=='head' else 'ADC_Test'
    rows=list(csv.DictReader(open(os.path.join(HW,'fab',name+'_BOM_JLC.csv'))))
    j=json.load(open(os.path.join(HW,'fab','joints.json')))[name]
    smd=[];tht=[]
    for r in rows:
        for ref in r['Designator'].split(','): (tht if ref in THT_REFS else smd).append((ref,r['LCSC Part #']))
    return smd,tht,j
def quote(N,mode='jlc',confirm=False,ship=SHIP,board='adc'):
    smd,tht,j=load(board)
    p_smd=sum(PRICE[l] for _,l in smd)*N*PRICE_SCALE
    p_tht=sum(PRICE[l] for _,l in tht)*N*PRICE_SCALE
    fees=SETUP+STENCIL+len({l for _,l in smd if l in EXT_SMD})*EXT_FEE+SMT*j['smd']*N+NITROGEN*N+(CONFIRM if confirm else 0)
    parts=p_smd; own=0
    if mode=='jlc': parts+=p_tht; fees+=MANUAL*j['tht']*N+LABOR
    else: own=p_tht
    goods=PCB+parts+fees
    iva=IVA*(goods+ship)
    return dict(parts=parts,fees=fees,pcb=PCB,goods=goods,ship=ship,iva=iva,own=own,total=goods+ship+iva+own)
def main(Ns):
    print('Model, calibrated on the 5-board JLCPCB quote (goods $114.36).')
    print(f'{"":42s}'+''.join(f'{n:>10d}' for n in Ns)+'  boards')
    for label,mode in (('JLC solders through-hole','jlc'),('You solder through-hole','self')):
        print(f'{label+": order (goods)":42s}'+''.join(f'{quote(n,mode)["goods"]:10.2f}' for n in Ns))
        print(f'{label+": total with shipping and IVA":42s}'+''.join(f'{quote(n,mode)["total"]:10.2f}' for n in Ns))
    print()
    for n in Ns:
        q=quote(n)
        print(f'N={n}: PCB {q["pcb"]:.2f} + parts {q["parts"]:.2f} + fees {q["fees"]:.2f} = goods {q["goods"]:.2f}; ship {q["ship"]:.2f}; IVA {q["iva"]:.2f}; total {q["total"]:.2f} (${q["total"]/n:.2f} per board)')
if __name__=='__main__': main([int(a) for a in sys.argv[1:]] or [2,3,5])

def two_orders(n_adc=2,n_head=5,ship_each=SHIP,combined_ship=SHIP):
    """The main board and the sensor head as two separate JLCPCB orders (or as one order of two designs)."""
    a=quote(n_adc,board='adc',ship=0); h=quote(n_head,board='head',ship=0)
    goods=a['goods']+h['goods']
    return dict(adc=a,head=h,goods=goods,separate_parcels=goods+2*ship_each+IVA*(goods+2*ship_each),
                one_parcel=goods+combined_ship+IVA*(goods+combined_ship))
