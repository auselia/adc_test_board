"""Verification suite for the ADS7057 test board, ngspice, TI vendor model for the OPA365.

What is real and what is not:
  OPA365 (4 channels)  TI vendor macromodel, unchanged (fetch it with models/fetch_models.py).
  THS4531              datasheet-based single-pole model (GBW 27 MHz, Zo 2.5 ohm). TI's own model runs but is wrong in
                       ngspice (-3 dB at 17 kHz, see README), and LTspice batch mode is not available here.
  ADS7057 input        datasheet section 8.3.2: 50 ohm switch and 16 pF per leg.
  Passives             ideal values with tolerance in the Monte Carlo run.
usage: python3 vendor_chain.py [mc_runs]
"""
import math,os,random,re,subprocess,sys,tempfile
HERE=os.path.dirname(os.path.abspath(__file__))
OPA=os.path.join(HERE,'models','OPA365.lib')
SUB="""
.subckt OA inp inn out vp vn params: gbw=50meg en=5n
rn inp ip {en*en/1.656e-20}
Gm 0 x ip inn 1m
R1 x 0 100meg
C1 x 0 {1/(6.2832*100meg*gbw/1e5)}
Bo ob 0 V=max(min(v(x),v(vp)-0.1),v(vn)+0.1)
Ro ob out 20
.ends
.subckt FDA inp inn op om vocm vp vn params: gbw=27meg en=10n zo=2.5
rn1 inp ip {en*en/1.656e-20}
rn2 inn in {en*en/1.656e-20}
Gm 0 x ip in 1m
R1 x 0 100meg
C1 x 0 {1/(6.2832*100meg*gbw/1e5)}
Bp op0 0 V=max(min(v(vocm)+v(x)/2,v(vp)-0.1),v(vn)+0.1)
Bm om0 0 V=max(min(v(vocm)-v(x)/2,v(vp)-0.1),v(vn)+0.1)
Rop op0 op {zo}
Rom om0 om {zo}
.ends
"""
NOM=dict(R1=10e3,R2=20e3,R3=3.9e3,R4=1e3,R5=2.2e3,R6=2.2e3,R7=10e3,R8=10e3,R9=10,R10=1e3,R11=1e3,R12=1e3,R13=1e3,
         R14=1e3,R15=1e3,R16=10,R17=10,Rmon=51,
         C1=100e-12,C2=100e-12,C4=100e-12,C5=100e-12,C6=100e-12,C7=1e-6,C8=10e-6,C9=100e-9,C11=1e-6,C13=1e-6,
         C14=100e-12,C15=100e-12,C16=100e-12,C17=100e-12)
TOL={k:(0.01 if k.startswith('R') else (0.05 if NOM[k]<=1e-9 else 0.10)) for k in NOM}
def chain(v=None,opa='vendor',cl=0.0,v5=5.0,avdd=3.3,body='',vin='DC 4.8 AC 1'):
    v=dict(NOM,**(v or {}))
    def op(n,p,m,o):
        return f"X{n} {p} {m} v5 0 {o} OPA365" if opa=='vendor' else f"X{n} {p} {m} {o} v5 0 OA gbw=50meg en=5n"
    return f"""* ADS7057 test board, signal chain
.include {OPA}
{SUB}
V5 v5 0 {v5}
Vavdd avdd 0 {avdd}
Vin vs 0 {vin}
Rs vs sig 50
R7 v5 vdiv {v['R7']}
R8 vdiv 0 {v['R8']}
C7 vdiv 0 {v['C7']}
{op('u2b','vdiv','vbuf','vbuf')}
R9 vbuf mid5 {v['R9']}
C8 mid5 0 {v['C8']}
C9 mid5 0 {v['C9']}
C1 sig hpa {v['C1']}
C2 hpa hpb {v['C2']}
R1 hpa hpf {v['R1']}
R2 hpb mid5 {v['R2']}
{op('u1a','hpb','hpf','hpf')}
R3 gout gnfb {v['R3']}
R4 gnfb mid5 {v['R4']}
{op('u1b','hpf','gnfb','gout')}
R5 gout lpa {v['R5']}
R6 lpa lpb {v['R6']}
C4 lpa lpf {v['C4']}
C5 lpa lpf {v['C5']}
C6 lpb mid5 {v['C6']}
{op('u2a','lpb','lpf','lpf')}
Rmon lpf mon {v['Rmon']}
Cmon mon 0 {15e-12+cl}
Rscope mon 0 1meg
R14 avdd vocm {v['R14']}
R15 vocm 0 {v['R15']}
C13 vocm 0 {v['C13']}
C11 lpf drva {v['C11']}
R10 drva dinp {v['R10']}
R11 vocm dinn {v['R11']}
Xu3 dinp dinn op om vocm v5 0 FDA gbw=27meg en=10n zo=2.5
R12 op dinn {v['R12']}
R13 om dinp {v['R13']}
R16 op ainp {v['R16']}
R17 om ainm {v['R17']}
C14 ainp ainm {v['C14']}
C15 ainp ainm {v['C15']}
C16 ainp ainm {v['C16']}
C17 ainp ainm {v['C17']}
Cs1 ainp 0 8p
Cs2 ainm 0 8p
{body}
.nodeset v(vdiv)=2.5 v(vbuf)=2.5 v(mid5)=2.5 v(hpf)=2.5 v(hpb)=2.5 v(gnfb)=2.5 v(gout)=2.5 v(lpa)=2.5 v(lpb)=2.5 v(lpf)=2.5
.nodeset v(vocm)=1.65 v(op)=1.65 v(om)=1.65 v(dinp)=1.65 v(dinn)=1.65 v(ainp)=1.65 v(ainm)=1.65
"""
def ngspice(text,control):
    d=tempfile.mkdtemp(); p=os.path.join(d,'c.cir')
    open(p,'w').write(text+"\n.control\n"+control+"\n.endc\n.end\n")
    r=subprocess.run(['ngspice','-b',p],capture_output=True,text=True,cwd=d)
    return d,r.stdout+r.stderr
def load_cols(d,name):
    return [list(map(float,l.split())) for l in open(os.path.join(d,name)) if l.strip()]
db=lambda x:20*math.log10(x)
def ac_metrics(rows):
    f=[r[0] for r in rows]; H=[r[1] for r in rows]
    def at(x): return H[min(range(len(f)),key=lambda k:abs(math.log(f[k]/x)))]
    ref=at(250e3); inb=[H[i]/ref for i in range(len(f)) if 230e3<=f[i]<=280e3]
    pk=max(H); f3=[f[i] for i in range(len(f)) if H[i]>=pk/math.sqrt(2)]
    return dict(gain_db=db(ref),flat=db(max(inb))-db(min(inb)),loss10k=-db(at(10e3)/ref),loss2M=-db(at(2e6)/ref),
                lo=min(f3)/1e3,hi=max(f3)/1e3)
def ac(opa='vendor',v=None,cl=0.0,probe='abs(v(ainp)-v(ainm))'):
    d,_=ngspice(chain(v,opa,cl),f"ac dec 40 1k 20meg\nlet h={probe}\nwrdata ac.txt h")
    return ac_metrics(load_cols(d,'ac.txt'))
def pr(label,m): print(f"  {label:34s} gain {m['gain_db']:6.2f} dB  flat {m['flat']:.2f} dB  10k {m['loss10k']:5.1f} dB  2M {m['loss2M']:5.1f} dB  band {m['lo']:.0f}-{m['hi']:.0f} kHz")
def main(mc=100):
    print('== 1. DC operating point, vendor OPA365')
    d,o=ngspice(chain(),"op\nprint v(mid5) v(vocm) v(hpf) v(gout) v(lpf) v(op) v(om) v(ainp) v(ainm)")
    for m in re.finditer(r'^(v\([a-z0-9_]+\))\s*=\s*(\S+)',o,re.M): print(f'  {m.group(1):10s} {float(m.group(2)):7.3f} V')
    print('== 2. AC response, vendor OPA365 versus behavioral op-amp')
    base=ac('vendor'); pr('vendor OPA365',base); pr('behavioral (datasheet GBW)',ac('behav'))
    print('== 3. Noise at the ADC input, 1 kHz to 2.5 MHz (vendor model noise)')
    d,o=ngspice(chain(),"noise v(ainp,ainm) Vin dec 30 1k 2.5meg 1\nprint onoise_total")
    m=re.search(r'onoise_total\s*=\s*(\S+)',o); n=float(m.group(1)) if m else float('nan')
    print(f'  {n*1e6:.0f} uV rms = {n/0.4e-3:.2f} LSB (LSB 0.40 mV); perfboard sensor noise is 40-53 LSB')
    print(f'== 4. Tolerance Monte Carlo, {mc} runs (R 1 %, C0G 5 %, X5R 10 %), vendor OPA365')
    random.seed(7); res=[]
    for _ in range(mc):
        v={k:NOM[k]*(1+random.uniform(-TOL[k],TOL[k])) for k in NOM}
        res.append(ac_metrics(load_cols(ngspice(chain(v),"ac dec 20 1k 20meg\nlet h=abs(v(ainp)-v(ainm))\nwrdata ac.txt h")[0],'ac.txt')))
    for key,lab,tgt in (('gain_db','gain at 250 kHz (dB)',''),('flat','flatness 230-280 kHz (dB)','< 1'),('loss10k','loss at 10 kHz (dB)','>= 40'),
                        ('loss2M','loss at 2 MHz (dB)','>= 20'),('lo','low -3 dB edge (kHz)',''),('hi','high -3 dB edge (kHz)','')):
        xs=[r[key] for r in res]; mu=sum(xs)/len(xs); sd=(sum((x-mu)**2 for x in xs)/len(xs))**0.5
        print(f'  {lab:28s} min {min(xs):7.2f}  mean {mu:7.2f}  max {max(xs):7.2f}  sigma {sd:.2f}   target {tgt}')
    fail10=sum(1 for r in res if r['loss10k']<40); print(f'  runs below 40 dB at 10 kHz: {fail10} of {mc}')
    print('== 5. Transient: 250 kHz burst, 10 cycles, vendor OPA365')
    for amp in (0.12,0.30,0.50):
        t=chain(vin="DC 0")
        t=t.replace("Vin vs 0 DC 0",f"Vin vs 0 DC 4.8 SIN(4.8 {amp} 250k 5u 0 0)")
        d,_=ngspice(t,"tran 20n 45u\nlet dd=v(ainp)-v(ainm)\nwrdata tr.txt v(gout) v(lpf) dd v(op) v(om) v(mid5)")
        r=load_cols(d,'tr.txt')
        g=[x[1] for x in r]; l=[x[3] for x in r]; a=[x[5] for x in r]; po=[x[7] for x in r]; pm=[x[9] for x in r]
        if abs(r[0][11]-2.5)>0.05: print('  WARNING: transient started at the wrong bias (mid5 = %.2f V), result not valid'%r[0][11])
        print(f'  burst {amp*1e3:3.0f} mV peak at the perfboard output: gout {min(g):.2f}..{max(g):.2f} V, ADC diff peak {max(a):.2f}/{min(a):.2f} V '
              f'({max(a)/3.3*100:.0f} % of full scale), legs {min(pm):.2f}..{max(po):.2f} V')
    print('== 6. ADC acquisition: 16 pF + 50 ohm per leg (datasheet 8.3.2), step from the previous sample')
    for step,label in ((0.34,'typical 250 kHz at 1.2 MSPS'),(0.56,'worst case, full 17 % FS swing')):
        vf=1.65+step/2
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
        t=chain(body=body)
        t=t.replace("C11 lpf drva","Rsrc srcn drva 0.001")   # drive R10 directly from a DC source
        d,_=ngspice(t,"tran 1n 3u\nwrdata st.txt v(sp1) v(sp2) v(mid5)")
        r=load_cols(d,'st.txt'); T=[x[0] for x in r]
        if abs(r[0][5]-2.5)>0.05: print('  WARNING: settling run started at the wrong bias (mid5 = %.2f V)'%r[0][5])
        diff=[x[1]-x[3] for x in r]; fin=diff[-1]
        thr=0.2e-3   # half an LSB (0.4 mV) on the differential
        settled=None
        for i in range(len(T)-1,-1,-1):
            if T[i]>=2e-6 and abs(diff[i]-fin)>thr: settled=T[i+1]-2e-6 if i+1<len(T) else None; break
        print(f"  {label:34s} step {step:.2f} V per leg: settles to 0.5 LSB in {settled*1e9 if settled else float('nan'):.0f} ns (tACQ >= 95 ns, 1.2 MSPS gives about 400 ns)")
    print('== 7. MON output with a cable: peaking and ringing of LPF_OUT, vendor OPA365')
    for cl,label in ((0,'scope probe only'),(100e-12,'1 m RG-58'),(1e-9,'10 m RG-58'),(5e-9,'50 m (abuse)')):
        d,_=ngspice(chain(cl=cl),"ac dec 60 10k 50meg\nlet h=abs(v(lpf))\nwrdata ac.txt h")
        rows=load_cols(d,'ac.txt'); f=[r[0] for r in rows]; H=[r[1] for r in rows]
        ref=H[min(range(len(f)),key=lambda k:abs(math.log(f[k]/250e3)))]
        pkdb=db(max(H[i] for i in range(len(f)) if f[i]>=250e3)/ref)
        print(f'  {label:20s} (+{cl*1e12:5.0f} pF)  LPF_OUT response above 250 kHz peaks at {pkdb:+.2f} dB re 250 kHz')
if __name__=='__main__': main(int(sys.argv[1]) if len(sys.argv)>1 else 100)
