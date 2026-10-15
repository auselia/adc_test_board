"""ADC test board (low-cost): perfboard SMA -> HPF -> gain x4.9 -> LPF -> THS4531 -> ADS7057 -> ZedBoard PMOD,
plus a window comparator (WAKE_N), a 5 V input (USB-C or header), a bias-T for the sensor head and test points.
Same topology as the Auselia AFE v0.1 (sections 5.2 to 5.5), rebuilt around JLCPCB Basic parts so only
the ADS7057, OPA2365 and THS4531 pay the extended-part fee.
Usage: python3 design.py <outdir>
"""
import os, sys
sys.path.insert(0,os.path.dirname(__file__))
import core
from core import *
class _All:
    def __contains__(self,x): return True
    def update(self,*a): pass
core.GLOBALS=_All()          # every net is a global label -> clean net names
FP_R='Resistor_SMD:R_0603_1608Metric'; FP_C='Capacitor_SMD:C_0603_1608Metric'
FP_SMA='Connector_Coaxial:SMA_Amphenol_132134-11_Vertical'
FP_PMOD='Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Horizontal'
FP_H2='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'
FP_C8='Capacitor_SMD:C_0805_2012Metric'
FP_R4='Resistor_SMD:R_0402_1005Metric'; FP_C4='Capacitor_SMD:C_0402_1005Metric'
FP_L='Inductor_SMD:L_1210_3225Metric'
FP_USBC='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12'
FP_TP='TestPoint:TestPoint_Pad_D1.5mm'
# test points, in the order they sit on the strip (ref, net)
TPS=[('TP3','SIG_IN'),('TP4','HPF_OUT'),('TP5','GAIN_OUT'),('TP6','LPF_OUT'),('TP7','DRV_OUTP'),('TP8','DRV_OUTN'),('TP9','AINP'),('TP10','AINM'),
     ('TP11','+5V'),('TP12','AVDD'),('TP13','VMID5'),('TP14','VOCM'),('TP15','+3V3'),('TP16','WAKE_N'),('TP17','VTH_H'),('TP18','VTH_L'),('TP19','GND'),('TP20','GND')]
FP_JP='Jumper:SolderJumper-2_P1.3mm_Bridged_Pad1.0x1.5mm'
FP_PZ='TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm'
# LCSC part numbers, checked in the JLCPCB parts library on 2026-10-12. All are JLC "Basic" parts
# except ADS7057, OPA2365, THS4531, the USB-C receptacle J2 and the THT parts J1/J4/J7/J3/RV1 (Extended).
LCSC={'10R':'C22859','22R':'C23345','1.00k':'C21190','2.2k':'C4190','3.9k':'C23018','10k':'C25804','20k':'C4184','33k':'C4216',
      '100pF C0G':'C14858','47pF C0G':'C1671','1M':'C22935','47R':'C23182','470uH':'C75644','100nF':'C14663','1uF':'C15849','4.7uF':'C19666','10uF':'C19702','10uF 25V':'C15850','22uF 25V':'C45783','51R':'C23197','5.1k':'C23186'}
def R(sh,x,y,val,a,b,ref,rot=90): return add(sh,'Device:R',val,FP_R,x,y,{'1':a,'2':b},'R',rot,ref=ref,props={'LCSC':LCSC[val]})
def C(sh,x,y,val,a,b,ref,rot=0): return add(sh,'Device:C',val,FP_C8 if '25V' in val else FP_C,x,y,{'1':a,'2':b},'C',rot,ref=ref,props={'LCSC':LCSC[val]})
def R4(sh,x,y,val,a,b,ref,lcsc,rot=90): return add(sh,'Device:R',val,FP_R4,x,y,{'1':a,'2':b},'R',rot,ref=ref,props={'LCSC':lcsc})
def C4(sh,x,y,val,a,b,ref,lcsc,rot=0): return add(sh,'Device:C',val,FP_C4,x,y,{'1':a,'2':b},'C',rot,ref=ref,props={'LCSC':lcsc})
def flag(sh,x,y,net): return add(sh,'power:PWR_FLAG','PWR_FLAG','',x,y,{'1':net},'#FLG',0,hide_val=True)
SO='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
def build():
    r=D.root; r.paper='A2'; r.title='Auselia ADS7057 test board, low-cost version (JLC Basic parts)'; r.path='/'+r.uuid
    sh=r
    text(sh,"ADS7057 test board (low cost)",20,22,4,True)
    text(sh,"Sensor head (SMA, bias-T) -> 2nd-order HPF 113 kHz -> gain x4.9 -> 2nd-order LPF 512 kHz -> THS4531 -> 10R/400pF -> ADS7057 -> ZedBoard PMOD.",20,30,1.8)
    text(sh,"AFE v0.1 topology rebuilt around JLC Basic parts (100 pF C0G, E12 resistors, AMS1117, LM393). Power: 5 V (USB-C or header) -> SS14 -> ferrite -> +5V, AVDD = XC6206 3.3 V from 5 V. DVDD = PMOD 3.3 V.",20,35,1.8)
    # ---- input + HPF + gain (U1)
    text(sh,"Input, high-pass filter (Sallen-Key, 100 pF / 10k / 20k: f0 = 113 kHz, Q = 0.71), gain 1 + 3.9k/1k = 4.9",20,55,2.2,True)
    add(sh,'Connector:Conn_Coaxial','SMA SENSOR IN',FP_SMA,30,90,{'1':'HEAD_LINE','2':'GND'},'J',ref='J1',props={'LCSC':'C496549'})
    C(sh,55,80,'100pF C0G','SIG_IN','HP_A','C1',90); C(sh,75,80,'100pF C0G','HP_A','HP_B','C2',90)
    R(sh,65,65,'10k','HP_A','HPF_OUT','R1',90); R(sh,85,100,'20k','HP_B','VMID5','R2',0)
    add(sh,'Auselia:OPA2365','OPA2365',SO,140,90,{'3':'HP_B','2':'HPF_OUT','1':'HPF_OUT','5':'HPF_OUT','6':'GN_FB','7':'GAIN_OUT','8':'+5V','4':'GND'},'U',ref='U1',props={'LCSC':'C130011'})
    R(sh,190,75,'3.9k','GAIN_OUT','GN_FB','R3',90); R(sh,190,110,'1.00k','GN_FB','VMID5','R4',0)
    C(sh,120,125,'100nF','+5V','GND','C3')
    # ---- LPF + VMID5 buffer (U2)
    text(sh,"Low-pass filter (2.2k / 2.2k, C1 = 2 x 100 pF, C2 = 100 pF: f0 = 512 kHz, Q = 0.71), VMID5",220,55,2.2,True)
    R(sh,235,80,'2.2k','GAIN_OUT','LP_A','R5',90); R(sh,255,80,'2.2k','LP_A','LP_B','R6',90)
    C(sh,245,65,'100pF C0G','LP_A','LPF_OUT','C4',90); C(sh,262,65,'100pF C0G','LP_A','LPF_OUT','C5',90); C(sh,265,100,'100pF C0G','LP_B','VMID5','C6')
    add(sh,'Auselia:OPA2365','OPA2365',SO,320,90,{'3':'LP_B','2':'LPF_OUT','1':'LPF_OUT','5':'VMID_DIV','6':'VMID_BUF','7':'VMID_BUF','8':'+5V','4':'GND'},'U',ref='U2',props={'LCSC':'C130011'})
    R(sh,235,130,'10k','+5V','VMID_DIV','R7',0); R(sh,235,150,'10k','VMID_DIV','GND','R8',0); C(sh,250,140,'1uF','VMID_DIV','GND','C7')
    R(sh,290,140,'10R','VMID_BUF','VMID5','R9',90); C(sh,310,150,'10uF','VMID5','GND','C8'); C(sh,325,150,'100nF','VMID5','GND','C9')
    C(sh,345,125,'100nF','+5V','GND','C10')
    # ---- driver + ADC
    text(sh,"Differential driver (gain 1), ADC. Kickback C = 4 x 100 pF C0G = 400 pF (25 x the 16 pF sampling C).",20,170,2.2,True)
    C(sh,40,200,'1uF','LPF_OUT','DRV_A','C11',90); R(sh,60,200,'1.00k','DRV_A','DRV_INP','R10',90); R(sh,60,225,'1.00k','VOCM','DRV_INN','R11',90)
    add(sh,'Auselia:THS4531','THS4531',SO,110,210,{'8':'DRV_INP','1':'DRV_INN','2':'VOCM','7':'+5V','4':'DRV_OUTP','5':'DRV_OUTN','3':'+5V','6':'GND'},'U',ref='U3',props={'LCSC':'C705347'})
    R(sh,110,180,'1.00k','DRV_OUTP','DRV_INN','R12',90); R(sh,110,245,'1.00k','DRV_OUTN','DRV_INP','R13',90)
    C(sh,80,250,'100nF','+5V','GND','C12')
    R(sh,20,240,'1.00k','AVDD','VOCM','R14',0); R(sh,35,240,'1.00k','VOCM','GND','R15',0); C(sh,50,240,'1uF','VOCM','GND','C13')
    R(sh,155,200,'10R','DRV_OUTP','AINP','R16',90); R(sh,155,220,'10R','DRV_OUTN','AINM','R17',90)
    for k,x in enumerate((170,180,190,200)): C(sh,x,235,'100pF C0G','AINP','AINM','C%d'%(14+k))
    add(sh,'Auselia:ADS7057','ADS7057','Auselia:ADS7057_X2QFN-8_1.5x1.5mm',230,210,
        {'7':'AINP','8':'AINM','1':'CS_A','3':'SCLK_A','2':'SDO_A','6':'AVDD','4':'+3V3','5':'GND'},'U',ref='U4',props={'LCSC':'C2669902'})
    C(sh,215,255,'4.7uF','AVDD','GND','C18'); C(sh,255,255,'1uF','+3V3','GND','C19'); C(sh,270,255,'100nF','+3V3','GND','C20')
    R(sh,280,195,'22R','CS','CS_A','R18',90); R(sh,280,210,'22R','SCLK','SCLK_A','R19',90); R(sh,280,225,'22R','SDO_A','SDO','R20',90)
    # ---- AVDD regulator
    text(sh,"AVDD = XC6206P332 from 5 V (also the ADC reference). Ceramic-stable LDO; C18 4.7 uF + C22 100 nF sit at the ADS7057 AVDD pin.",300,170,2.2,True)
    add(sh,'Auselia:XC6206P332','XC6206P332MR-G','Package_TO_SOT_SMD:SOT-23',330,205,{'3':'+5V','2':'AVDD','1':'GND'},'U',ref='U5',props={'LCSC':'C5446'})
    C(sh,305,235,'1uF','+5V','GND','C30'); C(sh,360,235,'1uF','AVDD','GND','C21'); C(sh,375,235,'100nF','AVDD','GND','C22')
    # ---- window comparator
    text(sh,"Window comparator / wake-up. Half window = 2.5 V x (1k + Rp)/(67k + Rp) = 37 ... 603 mV with the 20k RV1 (about 7 ... 120 mV at the perfboard output).",20,275,1.8)
    text(sh,"LM393 open-collector outputs are wired together: WAKE_N (PMOD pin 10) is pulled up to 3.3 V and goes LOW when the signal leaves the window.",20,281,1.8)
    add(sh,'Auselia:LM393','LM393',SO,150,320,{'3':'VTH_H','2':'LPF_OUT','5':'LPF_OUT','6':'VTH_L','1':'WAKE_N','7':'WAKE_N','8':'+5V','4':'GND'},'U',ref='U6',props={'LCSC':'C7955'})
    R(sh,40,300,'33k','+5V','VTH_H','R21',0); R(sh,55,300,'1.00k','VTH_H','PTOP','R22',0)
    add(sh,'Device:R_Potentiometer','20k trim','Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',75,300,{'1':'PTOP','2':'VTH_L','3':'VTH_L'},'RV',ref='RV1',props={'LCSC':'C34845'})
    R(sh,100,300,'33k','VTH_L','GND','R23',0); C(sh,40,330,'100nF','VTH_H','GND','C26'); C(sh,55,330,'100nF','VTH_L','GND','C27')
    C(sh,190,345,'100nF','+5V','GND','C28'); R(sh,230,315,'10k','+3V3','WAKE_N','R24',0)
    text(sh,"C31: optional filter on nWAKE, not fitted. No hysteresis: the outputs are wired together.",200,295,1.6)
    # ---- power: 5 V from USB-C (J2) or the header (J7) -> SS14 each (reverse protection, OR) -> ferrite -> +5V
    text(sh,"Power: 5 V from USB-C (J2, CC1/CC2 5.1k request 5 V from any charger) or the 2-pin header J7. SS14 per input = reverse protection and OR. Ferrite FB1 + 22 uF C23 filter the rail.",320,275,1.8)
    add(sh,'Connector:USB_C_Receptacle_USB2.0_16P','USB-C 5V',FP_USBC,330,300,
        {'A1':'GND','A12':'GND','B1':'GND','B12':'GND','SH':'GND','A4':'VBUS','A9':'VBUS','B4':'VBUS','B9':'VBUS','A5':'USB_CC1','B5':'USB_CC2',
         'A6':'NC','A7':'NC','B6':'NC','B7':'NC','A8':'NC','B8':'NC'},'J',ref='J2',props={'LCSC':'C165948'})
    R(sh,370,330,'5.1k','USB_CC1','GND','R32',0); R(sh,385,330,'5.1k','USB_CC2','GND','R33',0)
    add(sh,'Connector_Generic:Conn_01x02','5V IN',FP_H2,330,350,{'1':'+5V_EXT','2':'GND'},'J',ref='J7',props={'LCSC':'C492401'})
    add(sh,'Device:D_Schottky','SS14','Diode_SMD:D_SMA',400,300,{'2':'VBUS','1':'+5V_IN'},'D',rot=0,ref='D1',props={'LCSC':'C2480'})
    add(sh,'Device:D_Schottky','SS14','Diode_SMD:D_SMA',400,330,{'2':'+5V_EXT','1':'+5V_IN'},'D',rot=0,ref='D2',props={'LCSC':'C2480'})
    add(sh,'Device:FerriteBead','120R 2A','Inductor_SMD:L_0603_1608Metric',430,300,{'1':'+5V_IN','2':'+5V'},'FB',rot=90,ref='FB1',props={'LCSC':'C14709'})
    C(sh,455,320,'22uF 25V','+5V','GND','C23')
    # ---- test points after each stage (SMD pads 1.5 mm, not placed by JLCPCB)
    text(sh,"Test points: one after each stage of the signal chain, then the rails, WAKE_N and two grounds for the scope clip.",20,400,1.8,True)
    for k_,(ref_,net_) in enumerate(TPS):
        add(sh,'Connector:TestPoint',net_,FP_TP,20+k_*11,408,{'1':net_},'TP',ref=ref_)
    # ---- ZedBoard PMOD (Digilent type 2A SPI: 1 CS, 2 MOSI, 3 MISO, 4 SCK, 5 GND, 6 VCC; 7..10 extra I/O)
    text(sh,"ZedBoard PMOD JA..JD (3.3 V). Pin 6/12 = 3.3 V from the ZedBoard -> DVDD. Pin 10 = WAKE_N (active low).",330,55,2.2,True)
    pm={'1':'CS','3':'NC','5':'SDO','7':'SCLK','9':'GND','11':'+3V3',     # PMOD pins 1..6 (top row)
        '2':'NC','4':'NC','6':'NC','8':'WAKE_N','10':'GND','12':'+3V3'}     # PMOD pins 7..12 (bottom row)
    add(sh,'Connector_Generic:Conn_02x06_Odd_Even','PMOD (ZedBoard)',FP_PMOD,370,90,pm,'J',ref='J3',props={'LCSC':'C60565'})
    text(sh,"MON: LPF_OUT through 51R to an SMA for the scope (same signal the ADC samples).",480,55,2.2,True)
    R(sh,490,90,'51R','LPF_OUT','MON','R25',90)
    add(sh,'Connector:Conn_Coaxial','SMA MON',FP_SMA,520,90,{'1':'MON','2':'GND'},'J',ref='J4',props={'LCSC':'C496549'})
    add(sh,'Device:C','DNP','Capacitor_SMD:C_0603_1608Metric',250,330,{'1':'WAKE_N','2':'GND'},'C',ref='C31',dnp=True)
    add(sh,'Mechanical:MountingHole','M3','MountingHole:MountingHole_3.2mm_M3',480,150,{},'H',ref='H1')
    add(sh,'Mechanical:MountingHole','M3','MountingHole:MountingHole_3.2mm_M3',500,150,{},'H',ref='H2')
    # ---- SENSOR IN (J1): bias-T. +5 V through R26/L2 onto the coax centre = power for the sensor head; C33 passes its signal to SIG_IN.
    text(sh,"SENSOR IN (J1) = bias-T for the sensor head. +5V -> 47R (R26, C32 filter) -> 470 uH (L2) -> coax centre. C33 100 nF passes the head's signal to SIG_IN.",20,360,1.8,True)
    text(sh,"R27 1M gives SIG_IN a DC level (VMID5). To feed a function generator or a perfboard instead, cut the solder jumper JP1 (bridged by a copper trace) so the centre pin carries no DC.",20,366,1.8)
    add(sh,'Device:L','470uH',FP_L,80,390,{'1':'HEAD_LINE','2':'HEAD_PWR_L'},'L',rot=90,ref='L2',props={'LCSC':LCSC['470uH']})
    add(sh,'Jumper:SolderJumper_2_Bridged','HEAD PWR',FP_JP,95,390,{'1':'HEAD_PWR','2':'HEAD_PWR_L'},'JP',rot=90,ref='JP1')
    R(sh,110,380,'47R','+5V','HEAD_PWR','R26',90); C(sh,130,400,'10uF','HEAD_PWR','GND','C32')
    C(sh,150,380,'100nF','HEAD_LINE','SIG_IN','C33',90); R(sh,170,400,'1M','SIG_IN','VMID5','R27',0)
    # ---- SENSOR HEAD (separate 10 x 20 mm board in the same panel): perfboard charge amp, powered through the coax
    text(sh,"SENSOR HEAD (own board, same panel). Perfboard charge amp (TRL3): piezo -> summing node HSUM, Rf 1M || Cf 47 pF, Rs 49.9R. Runs from 5 V through the coax (L1), signal returns through C38.",220,360,1.8,True)
    text(sh,"Single OPA365 (same die as the OPA2365 on the main board), VREF = 5 V / 2 = 2.5 V (10k/10k + 10 uF), all 0402. Head ground is HGND (a separate board).",220,366,1.8)
    add(sh,'Connector:TestPoint','PIEZO +',FP_PZ,225,380,{'1':'HSUM'},'TP',ref='TP1')
    add(sh,'Connector:TestPoint','PIEZO -',FP_PZ,225,392,{'1':'HGND'},'TP',ref='TP2')
    add(sh,'Auselia:OPA365','OPA365','Package_TO_SOT_SMD:SOT-23-5',290,390,{'3':'HREF','4':'HSUM','1':'HOUT','5':'HV','2':'HGND'},'U',ref='U8',props={'LCSC':'C96626'})
    R4(sh,265,370,'1M','HSUM','HOUT','R28','C26083',90); C4(sh,285,370,'47pF C0G','HSUM','HOUT','C34','C1567',90)
    R4(sh,320,375,'10k','HV','HREF','R29','C25744',0); R4(sh,320,395,'10k','HREF','HGND','R30','C25744',0); C4(sh,340,395,'10uF','HREF','HGND','C35','C15525')
    C4(sh,360,375,'100nF','HV','HGND','C36','C307331'); C4(sh,375,375,'10uF','HV','HGND','C37','C15525')
    R4(sh,350,410,'49.9R','HOUT','HAC','R31','C25120',90); C4(sh,375,410,'100nF','HAC','HLINE','C38','C307331',90)
    add(sh,'Device:L','470uH',FP_L,400,395,{'1':'HLINE','2':'HV'},'L',rot=90,ref='L1',props={'LCSC':LCSC['470uH']})
    add(sh,'Connector:Conn_Coaxial','SMA HEAD OUT',FP_SMA,430,395,{'1':'HLINE','2':'HGND'},'J',ref='J6',props={'LCSC':'C496549'})
    flag(sh,365,250,'+3V3'); flag(sh,380,250,'GND'); flag(sh,395,250,'+5V_IN'); flag(sh,410,250,'+5V'); flag(sh,425,250,'HGND'); flag(sh,440,250,'HV')
    return r
if __name__=='__main__':
    out=sys.argv[1]
    r=build()
    open(os.path.join(out,'ADC_Test.kicad_sch'),'w').write(render(r))
    print('schematic written')
