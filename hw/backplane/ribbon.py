"""Ribbon cable pin plan shared by the adapter and the module (conductor n = header pin n).
GND sits next to every fast line (SCLK, SDO) and between small groups of CS / WAKE_N / BIG_N lines."""
def plan():
    r={1:'GND',2:'SCLK',3:'GND',4:'SDO0',5:'GND',6:'SDO1',7:'GND',8:'SDO2',9:'GND',10:'SDO3',11:'GND'}
    n=12
    for grp,names in (('CS',range(8)),('WAKE',range(8)),('BIG',range(8))):
        for i,k in enumerate(names):
            r[n]='%s%d'%(grp,k); n+=1
            if i in (1,4,7) if grp=='CS' else i in (3,7): r[n]='GND'; n+=1      # CS: GND after pairs; WAKE/BIG: GND after quads
    while n<=50: r[n]='GND'; n+=1
    return r
RIB=plan()
if __name__=='__main__':
    print(len(RIB),sum(1 for v in RIB.values() if v!='GND'),'signals')
    for n in range(1,51,2): print(n,RIB[n],'|',n+1,RIB[n+1])
