"""Snapshot of the simulation for the manual figures: doc/data/sim.json (needs ngspice and sim/models/OPA365.lib)."""
import json,os,sys,math,random,re
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'..','..','sim'))
import vendor_chain as vc
OUT=os.path.join(HERE,'..','data','sim.json')
R={}
# AC at four nodes, vendor OPA365
d,_=vc.ngspice(vc.chain(),"ac dec 40 1k 20meg\nlet hp=abs(v(hpf))\nlet go=abs(v(gout))\nlet lp=abs(v(lpf))\nlet ad=abs(v(ainp)-v(ainm))\nlet mo=abs(v(mon))\nwrdata ac.txt hp go lp ad mo")
rows=vc.load_cols(d,'ac.txt')
R['f']=[r[0] for r in rows]
for k,i in (('hpf',1),('gout',3),('lpf',5),('adc',7),('mon',9)): R[k]=[r[i] for r in rows]
d,_=vc.ngspice(vc.chain(opa='behav'),"ac dec 40 1k 20meg\nlet ad=abs(v(ainp)-v(ainm))\nwrdata ac.txt ad")
R['adc_behav']=[r[1] for r in vc.load_cols(d,'ac.txt')]
d,o=vc.ngspice(vc.chain(),"op\nprint v(mid5) v(vocm) v(hpf) v(gout) v(lpf) v(op) v(om)")
R['dc']={m.group(1):float(m.group(2)) for m in re.finditer(r'^v\(([a-z0-9_]+)\)\s*=\s*(\S+)',o,re.M)}
d,o=vc.ngspice(vc.chain(),"noise v(ainp,ainm) Vin dec 30 1k 2.5meg 1\nprint onoise_total")
R['noise_vrms']=float(re.search(r'onoise_total\s*=\s*(\S+)',o).group(1))
# Monte Carlo
random.seed(7); mc=[]
for _ in range(150):
    v={k:vc.NOM[k]*(1+random.uniform(-vc.TOL[k],vc.TOL[k])) for k in vc.NOM}
    d,_=vc.ngspice(vc.chain(v),"ac dec 20 1k 20meg\nlet h=abs(v(ainp)-v(ainm))\nwrdata ac.txt h")
    mc.append(vc.ac_metrics(vc.load_cols(d,'ac.txt')))
R['mc']=mc
# burst
R['burst']={}
for amp in (0.12,0.30,0.50):
    t=vc.chain(vin="DC 0").replace("Vin vs 0 DC 0",f"Vin vs 0 DC 4.8 SIN(4.8 {amp} 250k 5u 0 0)")
    d,_=vc.ngspice(t,"tran 20n 45u\nlet dd=v(ainp)-v(ainm)\nwrdata tr.txt v(gout) v(lpf) dd v(op) v(om) v(mid5)")
    r=vc.load_cols(d,'tr.txt'); k=3
    R['burst'][str(amp)]=dict(t=[x[0] for x in r][::k],gout=[x[1] for x in r][::k],lpf=[x[3] for x in r][::k],adc=[x[5] for x in r][::k],
                              op=[x[7] for x in r][::k],om=[x[9] for x in r][::k],mid5=r[0][11])
# ADC acquisition
R['settle']={}
for step in (0.34,0.56):
    body=f"""Vsrc srcn 0 DC {1.65+step}
Vprev1 pv1 0 DC {1.65-step/2}
Vprev2 pv2 0 DC {1.65+step/2}
Vbias vb 0 DC 1.65
Vc1 c1 0 PULSE(0 1 2u 1n 1n 1 2)
Vc2 c2 0 PULSE(1 0 2u 1n 1n 1 2)
S1 ainp x1 c1 0 SWI
S2 ainm x2 c1 0 SWI
S3 pv1 x1 c2 0 SWI
S4 pv2 x2 c2 0 SWI
Rsa x1 sp1 50
Rsb x2 sp2 50
Csa sp1 vb 16p
Csb sp2 vb 16p
.model SWI SW(Ron=1 Roff=1e9 Vt=0.5 Vh=0.1)
"""
    t=vc.chain(body=body).replace("C11 lpf drva","Rsrc srcn drva 0.001")
    d,_=vc.ngspice(t,"tran 1n 2.6u\nwrdata st.txt v(sp1) v(sp2) v(mid5)")
    r=vc.load_cols(d,'st.txt'); T=[x[0] for x in r]; diff=[x[1]-x[3] for x in r]; fin=diff[-1]
    sel=[i for i in range(len(T)) if 1.99e-6<=T[i]<=2.4e-6]
    R['settle'][str(step)]=dict(t=[(T[i]-2e-6)*1e9 for i in sel],v=[diff[i] for i in sel],final=fin,start=diff[sel[0]],mid5=r[0][5])
json.dump(R,open(OUT,'w'))
print('sim.json written;',len(R['f']),'freq points,',len(mc),'MC runs; dc',R['dc'])
