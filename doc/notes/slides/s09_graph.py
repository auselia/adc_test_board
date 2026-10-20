from style import *
fig,ax=plt.subplots(figsize=(7.4,3.6)); ax.axis('off')
def wave(y,xs,vs,c=ink): ax.step(xs,[y+0.6*v for v in vs],where='post',color=c,lw=1.6)
n=18; x=np.arange(0,n+4)
ax.step([-1,0,0,n+0.5,n+0.5,n+3],[2.6,2.6,2.0,2.0,2.6,2.6],color=accent,lw=1.8); ax.text(-1.2,2.3,'CS',ha='right',va='center',fontsize=10,color=ink)
clk=[];
for k in range(n): clk+=[0,1]
xs=np.arange(0,2*n)/2.0; ax.step(np.r_[xs,n],np.r_[[1.0+0.6*v for v in clk],1.0],where='post',color=ink,lw=1.2); ax.text(-1.2,1.3,'SCLK',ha='right',va='center',fontsize=10,color=ink)
ax.text(-1.2,0.2,'SDO',ha='right',va='center',fontsize=10,color=ink)
lab=['0']+['D%d'%k for k in range(13,-1,-1)]+['0','0','0']
for k,l in enumerate(lab):
    ax.add_patch(plt.Rectangle((k+0.5,-0.1),1,0.6,fc='#e6efe3' if l[0]=='D' else '#f0f0f0',ec=mut,lw=0.8)); ax.text(k+1,0.2,l,ha='center',va='center',fontsize=7.5,color=ink)
ax.annotate('',xy=(0,2.75),xytext=(0,2.0)); ax.text(0.15,2.82,'CS falls: the ADC samples here',fontsize=8.5,color=cu,va='bottom')
ax.text(9.5,-0.55,'18 clocks: leading 0, 14 data bits (MSB first), 3 zeros. After the 18th clock CS rises; at least 95 ns of acquisition follow.',ha='center',fontsize=8.5,color=ink)
ax.set_xlim(-3,19.5); ax.set_ylim(-0.9,3.3)
save(fig,'s09_graph')
# sample rate against the clock
f=np.logspace(6.5,np.log10(60e6),200); fs=1/(18/f+95e-9)
fig,ax=plt.subplots(figsize=(6.4,3.6)); ax.semilogx(f/1e6,fs/1e6,color=accent,lw=2.4)
for fm in (10,20,25,40,60):
    v=1/(18/(fm*1e6)+95e-9)/1e6; ax.plot(fm,v,'o',color=cu,ms=6.5); ax.text(fm,v-0.22,'%.2f'%v,ha='center',fontsize=8.5,color=ink)
ax.set_xlabel('SCLK (MHz)',color=ink); ax.set_ylabel('Sample rate (MSPS)',color=ink); ax.set_ylim(0,2.9); ax.set_title('Sample rate = 1 / (18 / SCLK + 95 ns)',fontsize=11,color=ink,loc='left'); style(ax)
save(fig,'s09_rate')
