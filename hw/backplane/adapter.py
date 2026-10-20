"""FMC adapter: plugs into the ZedBoard FMC LPC connector, level-shifts 58 lines from VADJ (any of 1.8 / 2.5 / 3.3 V) to the 3.3 V of the
backplane modules and brings them out on two 50-pin ribbon headers (one per 8-slot module).
Usage: python3 adapter.py <outdir>"""
import sys,os
from bp_common import *
from fmc_pins import *
from ribbon import RIB
FP_TSSOP='Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm'; FP_IDC='Connector_IDC:IDC-Header_2x25_P2.54mm_Vertical'
LCSC8T='C27643'; LCSC_IDC='C19193816'; LCSC_FMC='C2875619'
PAD2LA={p:(n,pn) for n,(a,b) in LA.items() for p,pn in ((a,'P'),(b,'N'))}
def rowkey(p): return (int(p[1:]),p[0])
west=sorted([p for p in PAD2LA if p[0] in 'CD'],key=rowkey)        # 24 pads, rows C and D
east=sorted([p for p in PAD2LA if p[0] in 'GH'],key=rowkey)[:34]   # first 34 of the 44 pads in rows G and H
spare=sorted([p for p in PAD2LA if p[0] in 'GH'],key=rowkey)[34:]
def la(p): n,pn=PAD2LA[p]; return la_name(n,pn)
# chip plan: (ref, direction 'out' = FPGA -> modules, 'in' = modules -> FPGA, [ribbon net per bit], pad list)
def rn(mod,name): return 'R%s_%s'%(mod,name)
PLAN=[
 ('U1','out',[rn('A','CS%d'%i) for i in range(8)],west[0:8]),
 ('U2','in', [rn('A','WAKE%d'%i) for i in range(8)],west[8:16]),
 ('U3','in', [rn('A','BIG%d'%i) for i in range(8)],west[16:24]),
 ('U4','out',[rn('B','CS%d'%i) for i in range(8)],east[0:8]),
 ('U5','in', [rn('B','WAKE%d'%i) for i in range(8)],east[8:16]),
 ('U6','in', [rn('B','BIG%d'%i) for i in range(8)],east[16:24]),
 ('U7','in', [rn('A','SDO%d'%i) for i in range(4)]+[rn('B','SDO%d'%i) for i in range(4)],east[24:32]),
 ('U8','out',[rn('A','SCLK'),rn('B','SCLK')]+['NC']*6,east[32:34]+[None]*6),
]
def build():
    r=start('FMC_Adapter','ZedBoard FMC to backplane adapter (3 V level shifters, two 50-pin ribbon outputs)')
    text(r,"FMC adapter for the ADS7057 backplane",20,22,5,True)
    text(r,"Plugs into the ZedBoard FMC LPC connector (J1 in the ZedBoard schematic). Eight SN74LVC8T245 level shifters: A side = VADJ (any of 1.8 / 2.5 / 3.3 V, so no J18 change is needed), B side = 3.3 V from the FMC 3P3V pins.",20,32,2)
    text(r,"58 lines: 18 outputs (16 chip selects, 2 SCLK) and 40 inputs (16 WAKE_N, 16 BIG_N, 8 SDO lanes). Outputs have 47 R series resistors for the ribbon. SDO lane inputs have 100 k pull-downs (SDO is Hi-Z while no card is selected).",20,38,2)
    text(r,"PRSNT_M2C_L (H2) is grounded and TDI is tied to TDO (D30-D31), as the FMC standard asks a mezzanine without JTAG devices; the ZedBoard adds the FMC to the JTAG chain when it sees PRSNT.",20,44,2)
    # --- FMC connector
    nets={}
    for p in GND_PADS: nets[p]='GND'
    for p in P3V3: nets[p]='+3V3_FMC'
    for p in VADJ: nets[p]='VADJ'
    for p,(n,pn) in PAD2LA.items(): nets[p]=la_name(n,pn)
    nets['H2']='GND'; nets['D30']='JTAG_BYP'; nets['D31']='JTAG_BYP'
    part('Bp:ASP-134602-01','ASP-134602-01','Bp:ASP-134602-01_LPC',150,330,nets,'J1',LCSC_FMC,side='bot')
    # --- ribbon headers
    for ref,mod,sx in (('J2','A',820),('J3','B',980)):
        nn={str(n):('GND' if v=='GND' else rn(mod,v)) for n,v in RIB.items()}
        part('Connector_Generic:Conn_02x25_Odd_Even','RIBBON '+mod,FP_IDC,sx,330,nn,ref,LCSC_IDC)
    # --- level shifters
    rcount=0; ccount=0
    for i,(ref,dr,rnets,pads) in enumerate(PLAN):
        sx=330+(i%4)*110; sy=130+(i//4)*230
        nn={'1':'VADJ','2':'VADJ' if dr=='out' else 'GND','22':'GND','23':'+3V3_FMC','24':'+3V3_FMC','11':'GND','12':'GND','13':'GND'}
        for b in range(8):
            apin=str(3+b); bpin=str(21-b); rname=rnets[b]; p=pads[b]
            if p is None:                       # unused channel: A input tied low, B side open
                nn[apin]='GND'; nn[bpin]='NC'; continue
            nn[apin]=la(p)
            if dr=='out':
                nn[bpin]='T_'+rname; 
            else:
                nn[bpin]=rname
        part('Bp:SN74LVC8T245','SN74LVC8T245',FP_TSSOP,sx,sy,nn,ref,LCSC8T)
        ccount+=1; C(sx-20,sy+40,'100nF','VADJ','GND','C%d'%ccount)
        ccount+=1; C(sx+20,sy+40,'100nF','+3V3_FMC','GND','C%d'%ccount)
        if dr=='out':
            for b in range(8):
                if pads[b] is None: continue
                rcount+=1; R(sx+30+0,sy-18+b*5,'47R','T_'+rnets[b],rnets[b],'R%d'%rcount,rot=90)
    for mod in 'AB':
        for k in range(4):
            rcount+=1; R(820+(0 if mod=='A' else 160)+k*10,200,'100k',rn(mod,'SDO%d'%k),'GND','R%d'%rcount,rot=0)
    ccount+=1; C(60,230,'10uF','VADJ','GND','C%d'%ccount); ccount+=1; C(80,230,'10uF','+3V3_FMC','GND','C%d'%ccount)
    ccount+=1; C(100,230,'100nF','VADJ','GND','C%d'%ccount); ccount+=1; C(120,230,'100nF','+3V3_FMC','GND','C%d'%ccount)
    rcount+=1; R(60,260,'1k','+3V3_FMC','LED_A','R%d'%rcount,rot=90)
    part('Device:LED','3V3 OK',FP_LED,80,260,{'2':'LED_A','1':'GND'},'D1',LCSC['LED'],rot=0)
    for k,(x,y) in enumerate(((250,560),(450,560))):
        part('Mechanical:MountingHole','M3',FP_HOLE,x,y,{},'H%d'%(k+1),side='top')
    for k,(net,x) in enumerate((('GND',20),('+3V3_FMC',40),('VADJ',60))):
        part('Connector:TestPoint',net,FP_TP,x,200,{'1':net},'TP%d'%(k+1))
    return r
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    r=build()
    open(os.path.join(out,'FMC_Adapter.kicad_sch'),'w').write(render(r))
    save_model(os.path.join(out,'FMC_Adapter_model.json'))
    print('adapter schematic written;',len(PARTS),'parts')
