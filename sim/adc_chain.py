"""ngspice check of the test board: SMA in -> HPF -> gain -> LPF -> THS4531 -> 10R/400pF -> ADS7057 input.
Same behavioral op-amp and FDA models as afe_pcb/sim/afe.py (single pole, GBW, input noise, rail clamp).
Values are the ones in hw/tools/design.py. usage: python3 adc_chain.py
"""
import subprocess,os,re,math,tempfile
SUB="""
.subckt OA inp inn out vp vn params: gbw=50meg en=5n
rn inp ip {en*en/1.656e-20}
Gm 0 x ip inn 1m
R1 x 0 100meg
C1 x 0 {1/(6.2832*100meg*gbw/1e5)}
Bo ob 0 V=max(min(v(x),v(vp)-0.1),v(vn)+0.1)
Ro ob out 20
.ends
.subckt FDA inp inn op om vocm vp vn params: gbw=27meg en=10n
rn1 inp ip {en*en/1.656e-20}
rn2 inn in {en*en/1.656e-20}
Gm 0 x ip in 1m
R1 x 0 100meg
C1 x 0 {1/(6.2832*100meg*gbw/1e5)}
Bp op0 0 V=max(min(v(vocm)+v(x)/2,v(vp)-0.1),v(vn)+0.1)
Bm om0 0 V=max(min(v(vocm)-v(x)/2,v(vp)-0.1),v(vn)+0.1)
Rop op0 op 20
Rom om0 om 20
.ends
"""
def net(rp=10e3,analysis=".ac dec 40 1k 20meg"):
    return SUB+f"""
V5 v5 0 5
Vavdd avdd 0 3.3
* perfboard output: 4.8 V idle, 50 ohm series
Vin vs 0 DC 4.8 AC 1
Rs vs sig 50
* VMID5 = 2.5 V buffered
R7 v5 vdiv 10k
R8 vdiv 0 10k
C7 vdiv 0 1u
Xu2b vdiv vbuf vbuf v5 0 OA gbw=50meg en=5n
R9 vbuf mid5 10
C8 mid5 0 10u
C9 mid5 0 100n
* high-pass, Sallen-Key
C1 sig hpa 100p
C2 hpa hpb 100p
R1 hpa hpf 10k
R2 hpb mid5 20k
Xu1a hpb hpf hpf v5 0 OA gbw=50meg en=5n
* gain 1 + 3.9k/1k
R3 gout gnfb 3.9k
R4 gnfb mid5 1k
Xu1b hpf gnfb gout v5 0 OA gbw=50meg en=5n
* low-pass, Sallen-Key
R5 gout lpa 2.2k
R6 lpa lpb 2.2k
C4 lpa lpf 100p
C5 lpa lpf 100p
C6 lpb mid5 100p
Xu2a lpb lpf lpf v5 0 OA gbw=50meg en=5n
* 51 ohm MON output into a 1 Mohm scope
Rmon lpf mon 51
Cmon mon 0 15p
Rscope mon 0 1meg
* VOCM = AVDD/2
R14 avdd vocm 1k
R15 vocm 0 1k
C13 vocm 0 1u
* THS4531, gain 1
C11 lpf drva 1u
R10 drva dinp 1k
R11 vocm dinn 1k
Xu3 dinp dinn op om vocm v5 0 FDA gbw=27meg en=10n
R12 op dinn 1k
R13 om dinp 1k
* ADC input filter + sampling capacitance
R16 op ainp 10
R17 om ainm 10
C14 ainp ainm 100p
C15 ainp ainm 100p
C16 ainp ainm 100p
C17 ainp ainm 100p
Cs1 ainp 0 8p
Cs2 ainm 0 8p
* comparator window
R19 v5 vth_h 33k
R20 vth_h ptop 1k
Rp ptop vth_l {rp}
R21 vth_l 0 33k
{analysis}
"""
def run(text,wr):
    d=tempfile.mkdtemp()
    p=os.path.join(d,'c.cir')
    open(p,'w').write(text+"\n.end\n")
    r=subprocess.run(['ngspice','-b',p],capture_output=True,text=True,cwd=d)
    return r.stdout+r.stderr
def table(analysis,rows,cols):
    return net(analysis=analysis)
def main():
    ctl="""
.control
op
print v(mid5) v(vocm) v(vbuf) v(hpf) v(gout) v(lpf) v(op) v(om) v(ainp) v(ainm) v(vth_h) v(vth_l)
ac dec 60 1k 20meg
let h=abs(v(ainp)-v(ainm))
let hl=abs(v(lpf))
wrdata ac.txt h hl abs(v(hpf)) abs(v(gout)) abs(v(mon))
noise v(ainp,ainm) Vin dec 30 1k 2.5meg 1
print onoise_total inoise_total
.endc
"""
    d=tempfile.mkdtemp(); p=os.path.join(d,'c.cir')
    open(p,'w').write(net(analysis=ctl)+"\n.end\n")
    out=subprocess.run(['ngspice','-b',p],capture_output=True,text=True,cwd=d)
    txt=out.stdout+out.stderr
    print('--- DC operating point (V)')
    for m in re.finditer(r'^(v\([a-z0-9_]+\))\s*=\s*(\S+)',txt,re.M): print(f'  {m.group(1):10s} {float(m.group(2)):7.3f}')
    rows=[list(map(float,l.split())) for l in open(os.path.join(d,'ac.txt')) if l.strip()]
    f=[r[0] for r in rows]; H=[r[1] for r in rows]; HL=[r[3] for r in rows]; HP=[r[5] for r in rows]; GO=[r[7] for r in rows]; MON=[r[9] for r in rows]
    def at(arr,x):
        i=min(range(len(f)),key=lambda k:abs(math.log(f[k]/x))); return arr[i]
    db=lambda v:20*math.log10(v)
    ref=at(H,250e3)
    print('--- Frequency response, SMA in -> ADC differential input')
    print('  gain at 250 kHz: %.2f dB (x%.2f; ideal x4.9, the rest is the 50 ohm source into the 100 pF input capacitor and the filter tails)'%(db(ref),ref))
    for fx in (1e3,10e3,50e3,100e3,230e3,250e3,280e3,500e3,1e6,2e6,5e6):
        print(f'  {fx/1e3:7.0f} kHz  {db(at(H,fx)):7.2f} dB  rel. 250 kHz {db(at(H,fx)/ref):7.2f} dB   MON/LPF {at(MON,fx)/at(HL,fx):.3f}')
    inband=[H[i]/ref for i in range(len(f)) if 230e3<=f[i]<=280e3]
    print('  variation 230-280 kHz: %.2f dB   (target < 1 dB)'%(db(max(inband))-db(min(inband))))
    print('  loss at 10 kHz: %.1f dB (target >= 40 dB)   loss at 2 MHz: %.1f dB (target >= 20 dB)'%(-db(at(H,10e3)/ref),-db(at(H,2e6)/ref)))
    pk=max(H); f3=[f[i] for i in range(len(f)) if H[i]>=pk/math.sqrt(2)]
    print('  -3 dB band: %.0f to %.0f kHz'%(min(f3)/1e3,max(f3)/1e3))
    m=re.findall(r'(onoise_total|inoise_total)\s*=\s*(\S+)',txt)
    nz=dict(m)
    if nz: print('--- Board noise at the ADC input, 1 kHz to 2.5 MHz: %.0f uV rms = %.2f LSB (LSB 0.40 mV; sensor noise on the perfboard is 40-53 LSB, ADC own noise ~0.6 LSB)'%(float(nz['onoise_total'])*1e6,float(nz['onoise_total'])*1e3/0.40))
    print('--- Comparator window (trimmer RV1 = Rp, 20k), half width at LPF_OUT and at the perfboard output (gain 4.9)')
    for rp in (0,5e3,10e3,14e3,20e3):
        h=2.5*(1e3+rp)/(67e3+rp)
        print(f'  Rp={rp/1e3:4.1f}k  VTH_H={2.5+h:5.3f} V  VTH_L={2.5-h:5.3f} V  half window {h*1e3:6.1f} mV  = {h/4.9*1e3:6.1f} mV at perfboard')
if __name__=='__main__': main()
