from style import *
t=np.linspace(0,12e-6,1200); vin=0.5*np.sin(2*np.pi*250e3*t); vocm=1.65
fig,ax=plt.subplots(figsize=(7.2,4.0))
ax.plot(t*1e6,vocm+vin/2,color=accent,lw=2,label='OUT+  = VOCM + vin/2'); ax.plot(t*1e6,vocm-vin/2,color=cu,lw=2,label='OUT−  = VOCM − vin/2')
ax.plot(t*1e6,vin,color='#b3261e',lw=1.2,ls='--',label='difference OUT+ − OUT− = vin (0.5 V peak)')
ax.axhline(vocm,color=mut,lw=0.9,ls=':'); ax.text(11.9,vocm+0.04,'VOCM 1.65 V',ha='right',fontsize=8.5,color=ink)
ax.axhline(3.3,color=mut,lw=1.2,ls='--'); ax.axhline(0,color=mut,lw=1.2,ls='--')
ax.set_ylim(-0.4,3.6); ax.set_xlim(0,12); ax.set_xlabel('Time (µs), 250 kHz tone',color=ink); ax.set_ylabel('Voltage (V)',color=ink)
ax.set_title('Driver: one wire in, two opposite wires out',fontsize=11,color=ink,loc='left'); ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.17),ncol=2,fontsize=8,frameon=False); style(ax)
save(fig,'s07_graph')
