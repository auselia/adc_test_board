"""Rough JLCPCB cost of the backplane boards (parts from the JLC library, fees from the 2026-10-12 quote calibration in hw/tools/cost.py).
The PCB price is an ESTIMATE (the JLC quote page is the only real source). usage: python3 bp_cost.py"""
import json,os,subprocess,collections,sys
HERE=os.path.dirname(os.path.abspath(__file__))
def part(code):
    out=subprocess.run(['curl','-s','-m','25','-X','POST','https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList','-H','Content-Type: application/json','-d',json.dumps({"currentPage":1,"pageSize":1,"keyword":code,"searchSource":"search"})],capture_output=True,text=True).stdout
    c=json.loads(out)['data']['componentPageInfo']['list'][0]; assert c['componentCode']==code
    return c['componentLibraryType'],[(p['startNumber'],p['productPrice']) for p in c['componentPrices']],c['stockCount']
def price(tiers,q):
    best=tiers[0][1]
    for s,p in tiers:
        if q>=s: best=p
    return best
EXT_FEE=3.09; SETUP=8.24; STENCIL=1.55; SMT_JOINT=1.32/775; LABOR=3.61; MANUAL=2.23/135
def board(name,n,sides,pcb_est,skip=('H','TP')):
    model=json.load(open(os.path.join(HERE,'out',name+'_model.json')))
    cnt=collections.Counter(p['lcsc'] for p in model if p['ref'][0:2] not in skip and not p['ref'].startswith('H') and p['lcsc'])
    parts=0; ext=0; rows=[]
    for code,k in cnt.items():
        t,tiers,stock=part(code); q=k*n; u=price(tiers,q); parts+=u*q; ext+= (t!='base'); rows.append((code,t,k,u,stock))
    joints=sum(1 for p in model for _ in [0] if p['lcsc'] and not p['ref'].startswith(('H','TP')))
    fees=SETUP*sides+STENCIL*sides+ext*EXT_FEE+LABOR
    return dict(parts=parts,fees=fees,pcb=pcb_est,ext=ext,rows=rows,total=parts+fees+pcb_est)
if __name__=='__main__':
    for name,n,sides,pcb in (('BP_Module',2,1,40.0),('FMC_Adapter',1,2,25.0)):
        r=board(name,n,sides,pcb)
        print(name,'x',n,'assembled: parts $%.2f  fees $%.2f (%d extended types)  PCB est. $%.0f  -> $%.2f'%(r['parts'],r['fees'],r['ext'],r['pcb'],r['total']))
        for row in r['rows']: print('   ',row)
