"""Sensor head (perfboard charge amplifier) powered through the coax by the bias-T, ngspice with the TI OPA365 model.
Compares the signal at the main board's SIG_IN node with the perfboard case (same amplifier straight into J1).
usage: python3 sim/head_bias_t.py   (needs sim/models/OPA365.lib: python3 sim/models/fetch_models.py)
"""
import os,re,subprocess,sys,tempfile
VR=float(sys.argv[1]) if len(sys.argv)>1 else 4.6      # supply rail at the main board, volts
HERE=os.path.dirname(os.path.abspath(__file__))
NET=f"""* head board + bias-T
.include {HERE}/models/OPA365.lib
V5 v5 0 {VR}
Vmid vmid 0 {VR/2}
Vpz pz 0 DC 0 AC 1
Cp pz sum 1.6n
* head: U8 OPA365, Rf 1M, Cf 47p, VREF 10k/10k + 10u, Rs 49.9, Cac 100n, L1 470u (22.5 ohm), C37 10u + C36 100n
Xu vref sum v5h 0 out OPA365
Rf sum out 1meg
Cf sum out 47p
R29 v5h vref 10k
R30 vref 0 10k
C35 vref 0 10u
Rs out o2 49.9
Cac o2 lh 100n
RL1 lh l1a 22.5
L1 l1a v5h 470u
C37 v5h 0 10u
C36 v5h 0 100n
* 1 m of RG174: 100 pF, 5 ns
Cx1 lh 0 50p
Tx lh 0 lb 0 Z0=50 TD=5n
Cx2 lb 0 50p
* main board: R26 47R + C32 10u, L2 470u (22.5 ohm), C33 100n into SIG_IN, R27 1M to VMID5, then C1 100p and R1 10k
RL2 lb l2a 22.5
L2 l2a hp 470u
R26 v5 hp 47
C32 hp 0 10u
C33 lb sig 100n
R27 sig vmid 1meg
C1 sig a 100p
R1 a vmid 10k
* reference: perfboard (same amplifier, 5 V) through 49.9 ohm straight to J1
Xu2 vref2 sum2 v5 0 out2 OPA365
Vref2 vref2 0 {VR/2}
Cp2 pz sum2 1.6n
Rf2 sum2 out2 1meg
Cf2 sum2 out2 47p
Rs2 out2 sig2 49.9
C1b sig2 b 100p
R1b b vmid 10k
.control
op
print v(v5h) v(vref) v(out) v(lh) v(hp) v(sig) i(V5)
ac dec 40 1k 5meg
let g = vdb(sig)-vdb(sig2)
meas ac loss_10k find g at=10k
meas ac loss_100k find g at=100k
meas ac loss_250k find g at=250k
meas ac loss_500k find g at=500k
meas ac gain_head_250k find vdb(sig) at=250k
meas ac gain_ref_250k find vdb(sig2) at=250k
.endc
.end
"""
def main():
    with tempfile.NamedTemporaryFile('w',suffix='.cir',delete=False) as f: f.write(NET)
    out=subprocess.run(['ngspice','-b',f.name],capture_output=True,text=True).stdout
    keep=[l for l in out.splitlines() if re.match(r'\s*(v\(|i\(|loss_|gain_)',l)]
    print('\n'.join(keep))
if __name__=='__main__': main()
