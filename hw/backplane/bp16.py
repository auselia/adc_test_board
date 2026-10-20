"""One-board 16-channel backplane: FMC plug on the left, 8 level shifters, a 4 x 4 matrix of 16 vertical 2x6 sockets for the channel cards,
buffered SCLK, low-noise 3.3 V LDO, 5 V screw terminal.  Usage: python3 bp16.py <outdir>"""
import sys,os
from bp_common import *
from fmc_pins import *
FP_TSSOP='Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm'
FP_SOCK='Connector_PinSocket_2.54mm:PinSocket_2x06_P2.54mm_Vertical'
FP_TERM='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
FP_QFN='Package_DFN_QFN:QFN-20-1EP_3.5x3.5mm_P0.5mm_EP2x2mm'; FP_TS20='Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'
FP_FMC='Bp:ASP-134602-01_LPC'
PAD2LA={p:(n,pn) for n,(a,b) in LA.items() for p,pn in ((a,'P'),(b,'N'))}
def rowkey(p): return (int(p[1:]),p[0])
west=sorted([p for p in PAD2LA if p[0] in 'CD'],key=rowkey)
east_all=sorted([p for p in PAD2LA if p[0] in 'GH'],key=rowkey); east=east_all[:34]
def la(p): n,pn=PAD2LA[p]; return la_name(n,pn)
def lane(k): return k//2
# shifter plan: (ref, direction, [slot-side net per bit], [FMC pad per bit])
PLAN=[
 ('U1','out',['CS%d'%i for i in range(8)],west[0:8]),
 ('U2','in', ['WAKE%d'%i for i in range(8)],west[8:16]),
 ('U3','in', ['BIG%d'%i for i in range(8)],west[16:24]),
 ('U4','out',['CS%d'%i for i in range(8,16)],east[0:8]),
 ('U5','in', ['WAKE%d'%i for i in range(8,16)],east[8:16]),
 ('U6','in', ['BIG%d'%i for i in range(8,16)],east[16:24]),
 ('U7','in', ['SDO%d'%i for i in range(8)],east[24:32]),
 ('U8','out',['SCLK_A','SCLK_B']+['NC']*6,east[32:34]+[None]*6),
]
def sock_nets(k):
    """Socket pads (card stands perpendicular, header rows swap): card pin1 CS -> pad 2, pin2 BIG_N -> 1, pin5 SDO -> 6, pin7 SCLK -> 8, pin8 WAKE_N -> 7, 9/10 GND, 11/12 3V3."""
    return {'1':'BIG%d'%k,'2':'CS%d'%k,'3':'NC','4':'NC','5':'NC','6':'SDO%d'%lane(k),'7':'WAKE%d'%k,'8':'SCLK%d'%k,'9':'GND','10':'GND','11':'+3V3','12':'+3V3'}
def build():
    r=start('BP16','ADS7057 backplane, 16 channels: FMC plug, level shifters, 4 x 4 slot matrix','A0')
    text(r,"16-channel backplane for the ADS7057 channel cards",20,22,5,True)
    text(r,"One board. The FMC plug (ZedBoard LPC) is on the left. Eight SN74LVC8T245 level shifters (A side VADJ, any of 1.8 / 2.5 / 3.3 V; B side the board's 3.3 V) feed a 4 x 4 matrix of vertical 2x6 sockets. Slot k = 4 * row + column.",20,32,2)
    text(r,"58 lines: 18 outputs (16 CS, 2 SCLK), 40 inputs (16 WAKE_N, 16 BIG_N, 8 SDO lanes; slots 2j and 2j+1 share lane j). SCLK of slots 0-7 and 8-15 each pass a SN74LVC244A with 22 R per branch. 100 k pull-ups keep CS, WAKE_N and BIG_N high on an empty slot.",20,38,2)
    text(r,"Socket pads are not the card pin numbers (the header rows swap): card pin 1 CS -> pad 2, pin 2 BIG_N -> pad 1, pin 5 SDO -> pad 6, pin 7 SCLK -> pad 8, pin 8 WAKE_N -> pad 7. Insert each card with its components facing +X. PRSNT_M2C_L grounded, TDI tied to TDO.",20,44,2)
    nets={}
    for p in GND_PADS: nets[p]='GND'
    for p in VADJ: nets[p]='VADJ'
    for p in P3V3: nets[p]='NC'
    for p,(n,pn) in PAD2LA.items(): nets[p]=la_name(n,pn)
    nets['H2']='GND'; nets['D30']='JTAG_BYP'; nets['D31']='JTAG_BYP'
    part('Bp:ASP-134602-01','ASP-134602-01',FP_FMC,150,330,nets,'J1','C2875619',side='bot')
    cc=0; rc=0
    for i,(ref,dr,rnets,pads) in enumerate(PLAN):
        sx=330+(i%4)*110; sy=130+(i//4)*230
        nn={'1':'VADJ','2':'VADJ' if dr=='out' else 'GND','22':'GND','23':'+3V3','24':'+3V3','11':'GND','12':'GND','13':'GND'}
        for b in range(8):
            apin=str(3+b); bpin=str(21-b); p=pads[b]
            if p is None: nn[apin]='GND'; nn[bpin]='NC'; continue
            nn[apin]=la(p); nn[bpin]=rnets[b]
        part('Bp:SN74LVC8T245','SN74LVC8T245',FP_TSSOP,sx,sy,nn,ref,'C27643')
        cc+=1; C(sx-20,sy+40,'100nF','VADJ','GND','C%d'%cc); cc+=1; C(sx+20,sy+40,'100nF','+3V3','GND','C%d'%cc)
    for k in range(8):
        rc+=1; R(800+k*10,200,'100k','SDO%d'%k,'GND','R%d'%rc,rot=0)
    cc+=1; C(60,230,'10uF','VADJ','GND','C%d'%cc); cc+=1; C(80,230,'100nF','VADJ','GND','C%d'%cc)
    # slots
    for k in range(16):
        sx=100+(k%8)*70; sy=480+(k//8)*160
        part('Connector_Generic:Conn_02x06_Odd_Even','SLOT %d'%k,FP_SOCK,sx,sy,sock_nets(k),'J%d'%(k+2),'C36191')
        for nm in ('CS','WAKE','BIG'): rc+=1; R(sx+30,sy-12+{'CS':0,'WAKE':8,'BIG':16}[nm],'100k','+3V3',nm+str(k),'R%d'%rc,rot=90)
        cc+=1; C(sx-15,sy+30,'10uF','+3V3','GND','C%d'%cc); cc+=1; C(sx+5,sy+30,'100nF','+3V3','GND','C%d'%cc)
    # SCLK buffers
    for h,(ref,inn,sl) in enumerate((('U9','SCLK_A',range(0,8)),('U10','SCLK_B',range(8,16)))):
        nb={'1':'GND','19':'GND','20':'+3V3','10':'GND'}
        for p in ('2','4','6','8','11','13','15','17'): nb[p]=inn
        for j,p in enumerate(('18','16','14','12','9','7','5','3')): nb[p]='SB%d'%sl[j]
        part('Bp:SN74LVC244A','SN74LVC244A',FP_TS20,700,130+h*230,nb,ref,'C7668')
        cc+=1; C(670,160+h*230,'100nF','+3V3','GND','C%d'%cc)
        for j,k in enumerate(sl): rc+=1; R(740+j*10,130+h*230,'22R','SB%d'%k,'SCLK%d'%k,'R%d'%rc,rot=90)
    # power
    part('Connector:Screw_Terminal_01x02','5 V IN',FP_TERM,100,820,{'1':'+5V_IN','2':'GND'},'J18','C8465')
    nl={'15':'+5V','16':'+5V','17':'+5V','14':'+5V','13':'NR','12':'NC','4':'NC','1':'+3V3','19':'+3V3','20':'+3V3','2':'+3V3','3':'FB','5':'NC','6':'GND','7':'NC','9':'NC','10':'GND','11':'GND','8':'GND','18':'GND','21':'GND'}
    part('Bp:TPS7A8300','TPS7A8300',FP_QFN,300,820,nl,'U11','C544500')
    part('Device:D_Schottky','SS14',FP_D,200,820,{'2':'+5V_IN','1':'+5V'},'D1',LCSC['SS14'])
    cc+=1; C(240,860,'22uF 25V','+5V','GND','C%d'%cc); cc+=1; C(260,860,'100nF','+5V','GND','C%d'%cc)
    for _ in range(3): cc+=1; C(400+_*20,860,'22uF 25V','+3V3','GND','C%d'%cc)
    cc+=1; C(480,860,'100nF','+3V3','GND','C%d'%cc); cc+=1; C(500,860,'10nF','NR','GND','C%d'%cc); cc+=1; C(520,860,'10nF','+3V3','FB','C%d'%cc)
    rc+=1; R(560,840,'1k','+3V3','LED_A','R%d'%rc,rot=90)
    part('Device:LED','3V3 OK',FP_LED,580,840,{'2':'LED_A','1':'GND'},'D2',LCSC['LED'])
    for k,(net,x) in enumerate((('+3V3',620),('GND',640),('+5V',660),('VADJ',680))): part('Connector:TestPoint',net,FP_TP,x,820,{'1':net},'TP%d'%(k+1))
    for k in range(6): part('Mechanical:MountingHole','M3',FP_HOLE,700+k*40,860,{},'H%d'%(k+1))
    return r
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    r=build()
    open(os.path.join(out,'BP16.kicad_sch'),'w').write(render(r))
    save_model(os.path.join(out,'BP16_model.json'))
    print('BP16 schematic written;',len(PARTS),'parts')
