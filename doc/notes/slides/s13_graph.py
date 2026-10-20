from style import *
rows=[('DC operating point, all rails (18 checks)','PASS','ngspice, as-built netlist'),('Gain 12.3 dB at 250 kHz; −40.5 dB at 10 kHz; −24 dB at 2 MHz','PASS','ngspice'),
('Listener thresholds: WAKE_N 35 mV, BIG_N 111 mV at SIG_IN','PASS','ngspice, 5 burst levels'),('ERC, DRC, schematic against board','PASS','KiCad, 0 errors'),
('Head and bias-T at 3.3 V; listener on 25 real captures','SIMULATED','ngspice, Python'),('ZedBoard 3.3 V rail noise (TP11, TP12)','OPEN','measure'),
('PMOD fit on adjacent ports','OPEN','print 1:1, test'),('THS4531 stable with 400 pF + 20 Ω','OPEN','LTspice / bench'),('First board on the bench','OPEN','manual steps 49 to 52')]
fig,ax=plt.subplots(figsize=(8.4,4.2)); ax.axis('off')
cc={'PASS':'#2e7d4f','SIMULATED':cu,'OPEN':'#b3261e'}
for i,(a,s,h) in enumerate(rows):
    y=len(rows)-i
    ax.add_patch(plt.Rectangle((0,y-0.45),10,0.9,fc='#f4f7f2' if i%2==0 else 'white',ec='none'))
    ax.text(0.1,y,a,va='center',fontsize=9,color=ink); ax.text(6.4,y,s,va='center',ha='center',fontsize=9,color='white',bbox=dict(boxstyle='round,pad=0.3',fc=cc[s],ec='none')); ax.text(7.4,y,h,va='center',fontsize=8.5,color=mut)
ax.set_xlim(0,10.2); ax.set_ylim(0.3,len(rows)+0.8)
ax.text(0.1,len(rows)+0.7,'What is checked and what is open',fontsize=11,color=ink,fontweight='bold')
save(fig,'s13_graph')
