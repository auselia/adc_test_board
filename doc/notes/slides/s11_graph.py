from style import *
fig,ax=plt.subplots(figsize=(7.2,4.1))
L=[('largest noise peak (18 noise captures)',26,'#566559'),('WAKE_N threshold',35,accent),('smallest true event',52,cu),('BIG_N threshold',111,accent),('largest true event',188,cu)]
for i,(n,v,c) in enumerate(L):
    ax.barh(i,v,color=c,height=0.55); ax.text(v*1.04,i,'%d mV'%v,va='center',fontsize=9,color=ink)
ax.axvspan(0,4.0*5,color=ae,alpha=0.0)
ax.set_yticks(range(len(L))); ax.set_yticklabels([l[0] for l in L],fontsize=9,color=ink); ax.invert_yaxis(); ax.set_xscale('log'); ax.set_xlim(10,400)
ax.set_xlabel('Peak amplitude at SIG_IN (mV, log scale)',color=ink)
ax.set_title('Listener thresholds against real captures (ESTIMATE, scaled to Cf 47 pF)',fontsize=10.5,color=ink,loc='left'); style(ax); ax.grid(axis='y',visible=False)
save(fig,'s11_graph')
