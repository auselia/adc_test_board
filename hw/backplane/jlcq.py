"""Query the JLCPCB parts library: python3 jlcq.py "keyword" [n]"""
import sys,json,subprocess
kw=sys.argv[1]; n=int(sys.argv[2]) if len(sys.argv)>2 else 8
out=subprocess.run(['curl','-s','-m','25','-X','POST','https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList','-H','Content-Type: application/json','-d',json.dumps({"currentPage":1,"pageSize":n,"keyword":kw,"searchSource":"search"})],capture_output=True,text=True).stdout
d=json.loads(out)
for c in d['data']['componentPageInfo']['list'][:n]:
    print(c['componentCode'],'|',c['componentModelEn'],'|',c['componentSpecificationEn'],'|',c.get('componentBrandEn'),'| stock',c['stockCount'],'|',c.get('componentLibraryType'),'|',[(p['startNumber'],round(p['productPrice'],4)) for p in c['componentPrices'][:2]])
