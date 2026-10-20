from style import *
items=[('OPA2365 (4 channels)',18),('Sensor head',4.7),('VOCM divider',1.65),('ADS7057 AVDD',1.1),('THS4531',0.25),('VMID5 divider',0.165),('Listener',0.022)]
tot=sum(v for _,v in items)
fig,ax=plt.subplots(figsize=(7.2,3.8))
ys=np.arange(len(items))[::-1]
ax.barh(ys,[v for _,v in items],color=accent,height=0.62)
for y,(n,v) in zip(ys,items): ax.text(v+0.3,y,'%g mA'%v,va='center',fontsize=9,color=ink)
ax.set_yticks(ys); ax.set_yticklabels([n for n,_ in items],fontsize=9,color=ink); ax.set_xlim(0,22)
ax.set_xlabel('Current from the 3.3 V of the PMOD (mA)',color=ink); ax.set_title('Current budget: %.1f mA (datasheet typical values), ngspice %.1f mA'%(tot,24.77),fontsize=11,color=ink,loc='left'); style(ax); ax.grid(axis='y',visible=False)
save(fig,'s10_graph')
# AVDD filter
f=np.logspace(1,7,400); s=1j*2*np.pi*f; h=1/(1+s*10*10e-6)
fig,ax=plt.subplots(figsize=(6.4,3.4)); ax.semilogx(f,20*np.log10(abs(h)),color=accent,lw=2.4); ax.axvline(1592,color=mut,ls='--',lw=1); ax.axvspan(100e3,500e3,color=ae,alpha=0.22,lw=0)
ax.set_xlabel('Frequency (Hz)',color=ink); ax.set_ylabel('Supply noise passed to AVDD (dB)',color=ink); ax.set_ylim(-80,3); ax.set_title('R34 10 Ω with C21 10 µF: corner 1.6 kHz, −44 dB at 250 kHz',fontsize=10,color=ink,loc='left'); style(ax)
save(fig,'s10_avdd'); print('total %.2f mA; avdd at 250k %.1f dB'%(tot,20*np.log10(abs(1/(1+1j*2*np.pi*250e3*1e-4)))))
