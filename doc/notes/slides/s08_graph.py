from style import *
tau=20*400e-12; t=np.linspace(0,100e-9,500)*1
fig,ax=plt.subplots(figsize=(7.2,4.0))
for dip,c,l in ((22.4e-3,accent,'worst step 0.56 V: dip 22 mV'),(13.6e-3,cu,'typical step 0.34 V: dip 13.6 mV')):
    ax.semilogy(t*1e9,dip*np.exp(-t/tau),color=c,lw=2.2,label=l+', first-order, τ = 20 Ω × 400 pF = 8 ns')
ax.axhline(0.2e-3,color='#b3261e',lw=1.2,ls='--'); ax.text(99,0.23e-3,'half an LSB, 0.2 mV',ha='right',fontsize=8.5,color='#b3261e')
ax.axvline(95,color=mut,lw=1.2,ls='--'); ax.text(93,5e-2,'tACQ 95 ns',ha='right',fontsize=8.5,color=ink)
ax.plot([29,54],[0.2e-3,0.2e-3],'o',color=ink,ms=7,label='ngspice with the driver: 29 ns and 54 ns')
ax.set_ylim(5e-5,6e-2); ax.set_xlim(0,100); ax.set_xlabel('Time after the sampling switch closes (ns)',color=ink); ax.set_ylabel('Error left on the input (V)',color=ink)
ax.set_title('ADC input: the kickback is gone long before 95 ns',fontsize=11,color=ink,loc='left'); ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.17),ncol=1,fontsize=8,frameon=False); style(ax)
save(fig,'s08_graph')
print('first-order settle worst %.0f ns, typical %.0f ns'%(tau*np.log(22.4e-3/0.2e-3)*1e9,tau*np.log(13.6e-3/0.2e-3)*1e9))
