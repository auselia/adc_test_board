"""8-slot backplane module: eight vertical 2x6 sockets for the ADS7057 channel cards, buffered SCLK, 3.3 V low-noise LDO, 50-pin ribbon input.
Two identical modules make the 16 channels.   Usage: python3 module.py <outdir>"""
import sys,os
from bp_common import *
from ribbon import RIB
FP_IDC='Connector_IDC:IDC-Header_2x25_P2.54mm_Vertical'
FP_SOCK='Connector_PinSocket_2.54mm:PinSocket_2x06_P2.54mm_Vertical'
FP_TERM='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
FP_QFN='Package_DFN_QFN:QFN-20-1EP_3.5x3.5mm_P0.5mm_EP2x2mm'; FP_TS20='Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'
def sock_nets(k):
    """Socket pad numbers. The card stands perpendicular to the backplane, so the two pin rows of the card header swap:
    card pin 2i+1 (odd row, farther from the card surface) lands on socket pad 2i+2 and card pin 2i+2 on socket pad 2i+1."""
    return {'1':'BIG%d'%k,'2':'CS%d'%k,'3':'NC','4':'NC','5':'NC','6':'SDO%d'%(k//2),'7':'WAKE%d'%k,'8':'SCLK%d'%k,'9':'GND','10':'GND','11':'+3V3','12':'+3V3'}
def build():
    r=start('BP_Module','ADS7057 backplane module, 8 slots (16 channels = two modules)')
    text(r,"8-slot backplane module for the ADS7057 channel cards",20,22,5,True)
    text(r,"Each card stands perpendicular to the board with its components facing +X (arrow on the silkscreen). Socket pad numbers are NOT the card pin numbers: the two header rows swap, so card pin 1 CS lands on pad 2, card pin 2 BIG_N on pad 1, pin 5 SDO on pad 6, pin 7 SCLK on pad 8, pin 8 WAKE_N on pad 7.",20,32,2)
    text(r,"Cards 0+1 share SDO lane 0, 2+3 lane 1, 4+5 lane 2, 6+7 lane 3 (SDO is Hi-Z while the card's CS is high). SCLK is buffered (SN74LVC244A, 22 R per branch). 5 V in -> SS14 -> TPS7A8300 ANY-OUT 3.3 V (pins 100 mV + 800 mV + 1.6 V to GND: 0.8 + 0.1 + 0.8 + 1.6 = 3.3 V).",20,38,2)
    text(r,"100 k pull-ups keep CS, WAKE_N and BIG_N high when a slot is empty or the adapter is not powered.",20,44,2)
    # ribbon header
    nn={str(n):('GND' if v=='GND' else ('SCLK_IN' if v=='SCLK' else v)) for n,v in RIB.items()}
    part('Connector_Generic:Conn_02x25_Odd_Even','RIBBON IN',FP_IDC,100,300,nn,'J1','C19193816')
    # sockets
    for k in range(8):
        part('Connector_Generic:Conn_02x06_Odd_Even','SLOT %d'%k,FP_SOCK,230+k*70,300,sock_nets(k),'J%d'%(k+2),'C36191')
    part('Connector:Screw_Terminal_01x02','5 V IN',FP_TERM,100,500,{'1':'+5V_IN','2':'GND'},'J10','C8465')
    # SCLK buffer
    nb={'1':'GND','19':'GND','20':'+3V3','10':'GND'}
    for p in ('2','4','6','8','11','13','15','17'): nb[p]='SCLK_IN'
    for k,p in enumerate(('18','16','14','12','9','7','5','3')): nb[p]='SB%d'%k
    part('Bp:SN74LVC244A','SN74LVC244A',FP_TS20,230,130,nb,'U1','C7668')
    for k in range(8): R(300+k*10,130,'22R','SB%d'%k,'SCLK%d'%k,'R%d'%(k+1),rot=90)
    n=8
    C(190,160,'100nF','+3V3','GND','C1')
    # pull-ups
    for k in range(8):
        for nm in ('CS','WAKE','BIG'):
            n+=1; R(230+k*70,230+{'CS':0,'WAKE':8,'BIG':16}[nm],'100k','+3V3',nm+str(k),'R%d'%n,rot=90)
    # per-slot decoupling
    c=1
    for k in range(8):
        c+=1; C(230+k*70-15,380,'10uF','+3V3','GND','C%d'%c); c+=1; C(230+k*70+5,380,'100nF','+3V3','GND','C%d'%c)
    # LDO
    nl={'15':'+5V','16':'+5V','17':'+5V','14':'+5V','13':'NR','12':'NC','4':'NC','1':'+3V3','19':'+3V3','20':'+3V3','2':'+3V3','3':'FB',
        '5':'NC','6':'GND','7':'NC','9':'NC','10':'GND','11':'GND','8':'GND','18':'GND','21':'GND'}
    part('Bp:TPS7A8300','TPS7A8300',FP_QFN,300,480,nl,'U2','C544500')
    part('Device:D_Schottky','SS14',FP_D,160,500,{'2':'+5V_IN','1':'+5V'},'D1',LCSC['SS14'],rot=0)
    c+=1; C(200,540,'22uF 25V','+5V','GND','C%d'%c); c+=1; C(220,540,'100nF','+5V','GND','C%d'%c)
    for _ in range(2): c+=1; C(380+(c%2)*20,540,'22uF 25V','+3V3','GND','C%d'%c)
    c+=1; C(420,540,'100nF','+3V3','GND','C%d'%c); c+=1; C(240,540,'10nF','NR','GND','C%d'%c); c+=1; C(260,540,'10nF','+3V3','FB','C%d'%c)
    n+=1; R(460,520,'1k','+3V3','LED_A','R%d'%n,rot=90)
    part('Device:LED','3V3 OK',FP_LED,480,520,{'2':'LED_A','1':'GND'},'D2',LCSC['LED'])
    for k,(net,x) in enumerate((('+3V3',600),('GND',620),('+5V',640))):
        part('Connector:TestPoint',net,FP_TP,x,500,{'1':net},'TP%d'%(k+1))
    for k in range(6):
        part('Mechanical:MountingHole','M3',FP_HOLE,700+k*40,560,{},'H%d'%(k+1))
    return r
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    r=build()
    open(os.path.join(out,'BP_Module.kicad_sch'),'w').write(render(r))
    save_model(os.path.join(out,'BP_Module_model.json'))
    print('module schematic written;',len(PARTS),'parts')
