"""Single-ended chain (as built) against a fully differential chain, same parts and same ADC load, ngspice.
A: SIG_IN -> Sallen-Key HPF -> gain 4.9 -> Sallen-Key LPF -> VMID5 buffer -> THS4531 (gain 1) -> 10R/400pF -> ADC
B: SIG_IN -> THS4531 (gain 4.9, single-ended to differential) -> coupled differential HPF -> coupled differential LPF -> 10R/400pF -> ADC
   (Massarotto, Casas, Ferrari, Pallas-Areny, IEEE TIM 56(6) 2007: coupling method, Rd damping, common-mode estimate resistors)
Measures: signal gain, supply-to-ADC gain (rail noise), mid-rail noise, own noise. usage: python3 diff_vs_se.py"""
import os,subprocess,tempfile,json,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); OPA=os.path.join(HERE,'models','OPA365.lib')
HEAD="""* chain comparison
.include %s
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
"""%OPA
def sk_hp(p,inp,out,ref,sfx,vdd='vdd'):    # Sallen-Key high-pass: C1 C2 R1(A->out) R2(B->ref), follower
    return f"""C1{sfx} {inp} a{sfx} 100p
C2{sfx} a{sfx} b{sfx} 100p
R1{sfx} a{sfx} {out} 10k
R2{sfx} b{sfx} {ref} 20k
X{sfx} b{sfx} {out} {vdd} 0 {out} OPA365
"""
def sk_lp(inp,out,ref,sfx,rd=0,vdd='vdd'):  # R5 R6, C4|C5 (200p) A->out, C6 (100p) B->ref
    cf=f"Rd{sfx} a{sfx} fb{sfx} {rd}\nC4{sfx} fb{sfx} {out} 200p" if rd else f"C4{sfx} a{sfx} {out} 200p"
    return f"""R5{sfx} {inp} a{sfx} 2.2k
R6{sfx} a{sfx} b{sfx} 2.2k
{cf}
C6{sfx} b{sfx} {ref} 100p
X{sfx} b{sfx} {out} {vdd} 0 {out} OPA365
"""
ADC="""R16 {p} ainp 10
R17 {m} ainm 10
C14 ainp ainm 400p
Rsa ainp sa 50
Csa sa 0 16p
Rsb ainm sb 50
Csb sb 0 16p
"""
COMMON="""Vdd vdd 0 DC 3.3 AC {acv}
Rs vgen_s0 sigq 49.9
Vg vgen_s0 0 DC 0 AC {acg}
Cc sigq sig_in 100n
Ravdd vdd avdd 10
Cavdd avdd 0 10u
R14 avdd vocm 1k
R15 vocm 0 1k
C13 vocm 0 1u
"""
def circuit_A(acv,acg):
    s=HEAD+COMMON.format(acv=acv,acg=acg)
    s+="R27 sig_in vmid5 1meg\n"
    s+="R7 vdd vdiv 10k\nR8 vdiv 0 10k\nC7 vdiv 0 1u\nXvm vdiv vmb vdd 0 vmb OPA365\nR9 vmb vmid5 10\nC8 vmid5 0 10u\nC9 vmid5 0 100n\n"
    s+=sk_hp(0,'sig_in','hpf','vmid5','h')
    s+="Xg hpf fb vdd 0 gout OPA365\nR3 gout fb 3.9k\nR4 fb vmid5 1k\n"
    s+=sk_lp('gout','lpf','vmid5','l')
    s+="C11 lpf da 1u\nR10 da inp 1k\nR11 vocm inn 1k\nR12 op inn 1k\nR13 om inp 1k\nXu3 inp inn op om vocm vdd 0 FDA\n"
    s+=ADC.format(p='op',m='om')
    return s
def circuit_A2(acv,acg):
    return circuit_A(acv,acg).replace('R7 vdd vdiv 10k','R7 avdd vdiv 10k')
def circuit_A3(acv,acg):
    c=circuit_A(acv,acg)
    head,tail=c.split('Vdd vdd 0',1)
    body=('Vdd vdd 0'+tail)
    body=body.replace(' vdd 0 ',' vo 0 ').replace(' vdd 0\n',' vo 0\n')
    body=body.replace('Vdd vo 0','Vdd vdd 0')
    return head+body+'Rfil vdd vo 2.2\nCfil vo 0 22u\n'
def circuit_B(acv,acg):
    s=HEAD+COMMON.format(acv=acv,acg=acg)
    s+="R27 sig_in vocm 1meg\n"
    s+="C11 sig_in da 1u\nR10 da inp 1k\nR11 vocm inn 1k\nR12 op inn 4.9k\nR13 om inp 4.9k\nXu3 inp inn op om vocm vdd 0 FDA\n"
    # coupled differential high-pass: common node N=P from two 1M resistors (paper eq. 7)
    s+="RN1 op nn 1meg\nRN2 om nn 1meg\n"
    s+=sk_hp(0,'op','hp','nn','p')+sk_hp(0,'om','hm','nn','m')
    # coupled differential low-pass with damping resistors Rd (paper eq. 4), floating common node P (1G to ground for the solver)
    s+=sk_lp('hp','lp','pp','q',rd=330)+sk_lp('hm','lm','pp','r',rd=330)+"Rpp pp 0 1g\n"
    s+=ADC.format(p='lp',m='lm')
    return s
def run(circ,ctl):
    d=tempfile.mkdtemp(); open(d+'/c.cir','w').write(circ+'.nodeset v(vdd)=3.3 v(vocm)=1.65\n.control\n'+ctl+'\n.endc\n.end\n')
    r=subprocess.run(['ngspice','-b',d+'/c.cir'],capture_output=True,text=True,cwd=d); return d,r.stdout+r.stderr
F=[1e4,3e4,1e5,2.5e5,5e5,1e6,2e6]
def ac(fn,acv,acg,tag):
    d,o=run(fn(acv,acg),f"ac dec 40 1k 10meg\nlet d=v(ainp)-v(ainm)\nlet cm=(v(ainp)+v(ainm))/2\nwrdata ac.txt abs(d) abs(cm)\n")
    a=np.loadtxt(d+'/ac.txt'); 
    if a.ndim<2: print(o[-800:]); raise SystemExit
    return a[:,0],a[:,1],a[:,3]
def at(f,x,fx): return np.interp(np.log(fx),np.log(f),x)
res={}
for name,fn in (('A single-ended',circuit_A),('A2 single-ended, VMID5 from AVDD',circuit_A2),('A3 single-ended, op-amp supply filter 2.2R+22uF',circuit_A3),('B differential',circuit_B)):
    f,sig,_=ac(fn,0,1,name); f2,sup,supcm=ac(fn,1,0,name)
    # own noise at the ADC differential output
    d,o=run(fn(0,1),"noise v(ainp,ainm) Vg dec 20 1k 10meg\nsetplot noise1\nwrdata nz.txt onoise_spectrum\nprint onoise_total")
    nz=np.loadtxt(d+'/nz.txt'); tot=[l for l in o.splitlines() if 'onoise_total' in l]
    # integrate 100k..500k
    m=(nz[:,0]>=1e5)&(nz[:,0]<=5e5); inb=np.sqrt(np.trapezoid(nz[m,1]**2,nz[m,0]))
    g250=at(f,sig,2.5e5)
    res[name]=dict(gain_db={int(x):20*np.log10(at(f,sig,x)/g250) for x in F},g250=g250,supply_mV_per_V={int(x):1e3*at(f2,sup,x) for x in F},
                   supply_cm_mV_per_V={int(x):1e3*at(f2,supcm,x) for x in F},noise_inband_uV=inb*1e6,noise_inband_lsb=inb/0.000403)
    print(name,'g250 %.2f (%.1f dB)'%(g250,20*np.log10(g250)))
    print('  gain re 250k (dB):',' '.join('%d:%.1f'%(x,res[name]['gain_db'][int(x)]) for x in F))
    print('  supply to ADC diff (mV per V):',' '.join('%d:%.2f'%(x,res[name]['supply_mV_per_V'][int(x)]) for x in F))
    print('  own noise 100-500k at ADC: %.1f uV rms = %.2f LSB'%(inb*1e6,inb/0.000403))
json.dump(res,open(os.path.join(HERE,'diff_vs_se_results.json'),'w'),indent=1)
