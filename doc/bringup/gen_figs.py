import json, math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
F='/Users/nico/Documents/GitHub/adc_test_board/doc/fonts/'
for f in ('Inter-Regular.ttf','Inter-SemiBold.ttf','Inter-Bold.ttf','IBMPlexMono-Regular.ttf'): fm.fontManager.addfont(F+f)
plt.rcParams['font.family']='Inter'; plt.rcParams['svg.fonttype']='none'
INK='#14231b'; GRN='#0f3d2a'; AMB='#d89a2b'; MUT='#566559'; RED='#b3261e'; BLU='#3b6aa8'; PNK='#c25a9a'
D='/Users/nico/Documents/GitHub/adc_test_board/doc/data/'
B=json.load(open(D+'board.json')); H=json.load(open(D+'head.json')); S=json.load(open(D+'sim.json'))
def save(fig,n): fig.savefig(n+'.pdf',bbox_inches='tight'); fig.savefig(n+'.png',dpi=200,bbox_inches='tight'); plt.close(fig)
# ---- 1. board map
def board_map(data,name,figsize,labels,tps=True,rot=False):
    fig,ax=plt.subplots(figsize=figsize); W,Hh=data['size']
    ax.add_patch(Rectangle((0,0),W,Hh,fc='#e9efe6',ec=INK,lw=1.2))
    for r,f in data['footprints'].items():
        x0,y0,x1,y1=f['bbox']; col='#b9c4b6'
        if r[0]=='U': col='#2f5a45'
        if r.startswith('J'): col='#d8b565'
        if r.startswith('TP'): col='#ffffff'
        if r.startswith('JP'): col=AMB
        if r[0]=='H': col='#8c9a8a'
        ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fc=col,ec='#6f7d6d',lw=0.3))
        if r[0]=='U':
            for p in f['pads']:
                if p['num']=='1': ax.add_patch(Circle((p['x'],p['y']),0.45,fc=RED,ec='none',zorder=5))
    for r,(dx,dy,ha) in labels.items():
        f=data['footprints'][r]; x=(f['bbox'][0]+f['bbox'][2])/2; y=(f['bbox'][1]+f['bbox'][3])/2
        ax.text(x+dx,y+dy,(r if (not r.startswith('TP') or data['size'][0]<20) else r[2:]),fontsize=6.2 if r.startswith('TP') else 7,ha=ha,va='center',color=INK,fontweight='bold' if r[0] in 'UJ' else 'normal')
    ax.set_xlim(-1,W+1); ax.set_ylim(Hh+1,-1); ax.set_aspect('equal'); ax.axis('off'); save(fig,name)
lab={}
for r in B['footprints']:
    if r.startswith('TP'): lab[r]=(0,-2.0 if B['footprints'][r]['bbox'][1]<8 else 2.0,'center')
for r in ('U1','U2','U3','U4','U6','U9','JP1','JP3','J1','J4','J7','J3'): lab[r]=(0,0,'center')
lab['U1']=(0,-3.9,'center'); lab['U2']=(0,-3.9,'center'); lab['U3']=(0,3.9,'center'); lab['U4']=(-3.2,-2,'center'); lab['U6']=(0,-3.0,'center'); lab['U9']=(0,-3.0,'center')
lab['JP1']=(0,-2.0,'center'); lab['JP3']=(0,-2.0,'center'); lab['J7']=(0,-2.6,'center'); lab['J3']=(-5,0,'center'); lab['J1']=(5.5,-3.2,'left'); lab['J4']=(5.5,3.2,'left')
board_map(B,'fig_boardmap',(11,2.4),lab)
hl={'TP1':(-3.2,0,'center'),'TP2':(3.2,0,'center'),'U8':(-4.2,0,'center'),'J6':(0,-4.5,'center')}
board_map(H,'fig_headmap',(2.6,5.2),hl)
# ---- 2. J7 wiring
def j7(name,mode):
    fig,ax=plt.subplots(figsize=(7.2,3.0)); ax.axis('off'); ax.set_xlim(0,14); ax.set_ylim(0,6)
    ax.add_patch(FancyBboxPatch((4.6,0.7),3.6,4.6,boxstyle='round,pad=0.05,rounding_size=0.15',fc='#f4f1e6',ec=INK,lw=1.3))
    ax.text(6.4,5.55,'J7  power / SMU header',ha='center',fontsize=8.5,fontweight='bold',color=INK)
    names=['1  Onboard +','2  Force +','3  Sense +','4  Sense -','5  Force -']
    for i,n in enumerate(names):
        y=4.6-i*0.85; ax.add_patch(Circle((5.0,y),0.22,fc=AMB,ec=INK,lw=0.8)); ax.text(5.45,y,n,fontsize=8,va='center',color=INK)
    ys=[4.6-i*0.85 for i in range(5)]
    if mode=='pmod':
        ax.plot([5.0,5.0],[ys[0],ys[1]],color=GRN,lw=6,solid_capstyle='round'); ax.text(3.7,(ys[0]+ys[1])/2,'jumper',ha='right',va='center',fontsize=8,color=GRN,fontweight='bold')
        ax.add_patch(Rectangle((0.2,3.6),2.6,1.5,fc='#dfe8e0',ec=INK)); ax.text(1.5,4.35,'ZedBoard PMOD\npins 6 and 12\n(3.3 V)',ha='center',va='center',fontsize=7.5)
        ax.plot([2.8,4.0,4.0,4.78],[4.35,4.35,ys[0],ys[0]],color=INK,lw=1)
        ax.text(9.0,2.8,'PMOD 3.3 V powers the board.\nPins 2 and 3 are the board rail.\nPins 4 and 5 are ground.',fontsize=8,va='center',color=INK)
    else:
        ax.add_patch(Rectangle((0.2,0.5),3.0,4.9,fc='#e7e2d3',ec=INK)); ax.text(1.7,5.55,'Keysight B2901BL',ha='center',fontsize=7.5,fontweight='bold')
        for lab_,y,c in (('Force +',4.6-0.85,RED),('Sense +',4.6-1.7,'#e07070'),('Sense -',4.6-2.55,'#506a9a'),('Force -',4.6-3.4,BLU)):
            ax.plot([3.2,4.78],[y+0.0,y],color=c,lw=2); ax.text(2.9,y,lab_,ha='right',va='center',fontsize=8,color=INK)
        ax.text(9.0,2.8,'Remove the jumper.\nForce to pins 2 and 5.\nSense to pins 3 and 4.\nSet 3.3 V, limit 50 mA.',fontsize=8,va='center',color=INK)
        ax.text(1.7,0.15,'pin 1 stays open',fontsize=7,ha='center',color=MUT)
    save(fig,name)
j7('fig_j7_pmod','pmod'); j7('fig_j7_smu','smu')
# ---- 3. test setup block diagram
fig,ax=plt.subplots(figsize=(7.4,2.6)); ax.axis('off'); ax.set_xlim(0,15); ax.set_ylim(0,5.4)
def box(x,y,w,h,t,fc='#e9efe6',fs=7): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04,rounding_size=0.12',fc=fc,ec=INK,lw=1)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,color=INK)
box(0.2,2.0,2.8,1.4,'Generator or\nAnalog Discovery 2\n(50 ohm)','#f6ecd2')
box(4.2,2.0,2.8,1.4,'J1 SENSOR IN\n(JP1 cut)\nTP3 = SIG_IN','#dfe8e0')
box(8.2,2.0,2.8,1.4,'Chain\nHPF, gain, LPF,\ndriver, ADC','#dfe8e0')
box(12.0,2.0,2.8,1.4,'J3 PMOD\nZedBoard\nSPI + WAKE_N','#dfe8e0')
for a,b in ((3.0,4.2),(7.0,8.2),(11.0,12.0)): ax.annotate('',xy=(b,2.7),xytext=(a,2.7),arrowprops=dict(arrowstyle='->',color=INK,lw=1.2))
box(8.2,0.3,2.8,1.1,'Scope probes\nTP4 to TP10','#efe4f0')
ax.annotate('',xy=(9.6,1.4),xytext=(9.6,2.0),arrowprops=dict(arrowstyle='<->',color=PNK,lw=1.2))
box(4.2,0.3,2.8,1.1,'J4 SCOPE OUT\n(51 ohm)','#efe4f0')
ax.annotate('',xy=(5.6,1.4),xytext=(5.6,2.0),arrowprops=dict(arrowstyle='<->',color=PNK,lw=1.2))
box(12.0,0.3,2.8,1.1,'TP16 WAKE_N\nTP17 BIG_N','#efe4f0'); ax.annotate('',xy=(13.4,1.4),xytext=(13.4,2.0),arrowprops=dict(arrowstyle='<->',color=PNK,lw=1.2))
save(fig,'fig_setup')
# ---- 4. expected waveforms (120 mV burst, simulation)
b=S['burst']['0.12']; t=np.array(b['t'])*1e6
fig,axs=plt.subplots(1,2,figsize=(7.4,2.8))
ax=axs[0]; ax.plot(t,np.array(b['gout']),color=GRN,lw=1.6,label='TP5 GAIN_OUT'); ax.plot(t,np.array(b['lpf']),color=AMB,lw=1.4,label='TP6 LPF_OUT'); ax.axhline(1.65,color=MUT,lw=0.7,ls=':')
ax.set_xlabel('time (us)'); ax.set_ylabel('volts'); ax.set_ylim(1.0,2.7); ax.set_title('Chain, 120 mV peak burst at 250 kHz',fontsize=8.5,loc='left'); ax.legend(fontsize=7,frameon=False,ncol=2,loc='upper left')
ax=axs[1]; ax.plot(t,np.array(b['op']),color=BLU,lw=1.4,label='TP7 DRV+'); ax.plot(t,np.array(b['om']),color=PNK,lw=1.4,label='TP8 DRV-'); ax.plot(t,np.array(b['adc'])+1.65,color=RED,lw=1.0,ls='--',label='difference (shifted)'); ax.axhline(1.65,color=MUT,lw=0.7,ls=':')
ax.set_xlabel('time (us)'); ax.set_ylim(1.0,2.7); ax.set_title('Driver outputs',fontsize=8.5,loc='left'); ax.legend(fontsize=7,frameon=False,ncol=3,loc='upper left')
for a in axs:
    a.grid(True,color='#d3dacf',lw=0.4)
    for s in a.spines.values(): s.set_color(MUT)
fig.tight_layout(); save(fig,'fig_waves')
# ---- 5. amplitude ladder at 250 kHz
f=np.array(S['f']); i=np.argmin(abs(f-250e3))
g={'SIG_IN':1.0,'TP4 HPF_OUT':S['hpf'][i],'TP5 GAIN_OUT':S['gout'][i],'TP6 LPF_OUT':S['lpf'][i],'TP7 / TP8 (each)':S['lpf'][i]/2,'TP9 - TP10 (ADC)':S['adc'][i]}
json.dump({k:float(v) for k,v in g.items()},open('gains250.json','w'),indent=1)
fig,ax=plt.subplots(figsize=(7.2,2.6)); ks=list(g)[::-1]
ax.barh(range(len(ks)),[g[k] for k in ks],color=[GRN if 'SIG' in k else AMB if 'ADC' in k else '#5a8f78' for k in ks],height=0.6)
for y,k in enumerate(ks): ax.text(g[k]+0.06,y,'x %.2f'%g[k],va='center',fontsize=8)
ax.set_yticks(range(len(ks))); ax.set_yticklabels(ks,fontsize=8); ax.set_xlim(0,5.2); ax.set_xlabel('amplitude relative to SIG_IN, 250 kHz (peak of the AC part)',fontsize=8)
for s in ax.spines.values(): s.set_color(MUT)
ax.grid(axis='x',color='#d3dacf',lw=0.4); save(fig,'fig_ladder')
print(g)
# ---- 6. flowchart
fig,ax=plt.subplots(figsize=(7.4,6.6)); ax.axis('off'); ax.set_xlim(0,15); ax.set_ylim(-0.3,14)
def n(x,y,w,h,t,fc,fs=7): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.03,rounding_size=0.15',fc=fc,ec=INK,lw=1)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,color=INK)
def ar(x0,y0,x1,y1,t=None,dx=0.15):
    ax.annotate('',xy=(x1,y1),xytext=(x0,y0),arrowprops=dict(arrowstyle='->',color=INK,lw=1.1))
    if t: ax.text((x0+x1)/2+dx,(y0+y1)/2+0.18,t,fontsize=7,color=MUT,ha='left' if dx else 'center')
G='#dfe8e0'; Y='#f6ecd2'; R='#f3d9d6'
cx,cw=4.7,5.6
ys=[12.6,10.4,8.2,6.0,3.8,1.6]
n(cx,ys[0],cw,1.0,'Power on: SMU 3.3 V, limit 50 mA',G)
q=['Current 18 to 30 mA?\n(about 20 mA without the head)','TP11 3.30 V, TP12 3.27 V,\nTP13 and TP14 near 1.65 V?','Burst at J1 (JP1 cut): TP5 about\n4.3 x SIG_IN, TP6 about 4.1 x?','TP9 and TP10 equal and opposite\naround 1.65 V?','SPI: 18 clocks, codes follow the\ninput, WAKE_N and BIG_N switch?']
bad=['Too high: open JP3 and read each\npart. Power off. Look for a solder\nbridge (U4, U6, U9) or a part\nturned wrong. Too low: J7 jumper.','Wrong rail: follow the net from\nthe test point. VMID5 needs 25 ms,\nwait and measure again.','First wrong stage: TP4, TP5, TP6.\nCheck its resistors, C0G caps and\nthe op-amp pin 1.','Driver or ADC input: U3, R10 to\nR17, C11 to C17, VOCM at TP14.','First frame is zeros: read twice.\nSDO stuck: +3V3 at U4 pin 4,\nR18 to R20. WAKE_N always low:\nTP18 must be 1.65 V.']
ar(cx+cw/2,ys[0],cx+cw/2,ys[1]+1.5)
for i,(qq,bb) in enumerate(zip(q,bad)):
    y=ys[i+1]; n(cx,y,cw,1.5,qq,Y)
    side=(0.1,3.9) if i%2==0 else (10.8,4.1)
    n(side[0],y-0.35,side[1],2.2,bb,R,6.6)
    if i%2==0: ar(cx,y+0.75,side[0]+side[1],y+0.75,'no',dx=0)
    else: ar(cx+cw,y+0.75,side[0],y+0.75,'no',dx=0)
    ar(cx+cw/2,y,cx+cw/2,(ys[i+2]+1.5 if i<4 else 0.9),'yes')
n(cx,0.0,cw,0.9,'Board passes: go to the head',G)
save(fig,'fig_flow')
