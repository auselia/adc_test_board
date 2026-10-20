"""Symbol library Bp.kicad_sym for the FMC adapter and the backplane module."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','tools'))
from sexp import *
import customsym as cs
from fmc_pins import *
TI='https://www.ti.com/lit/ds/symlink/'
def build():
    S=[]
    # SN74LVC8T245 TSSOP-24: VCCA 1, DIR 2, A1..A8 3..10, GND 11-13, B8..B1 14..21, OE 22, VCCB 23,24
    S.append(cs.mk_ic('SN74LVC8T245','U','SN74LVC8T245','Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm',TI+'sn74lvc8t245.pdf','8-bit dual-supply bus transceiver, 1.65-5.5 V both sides, 3-state, TSSOP-24',
        [('2','DIR','input'),('22','~{OE}','input')]+[(str(3+i),'A%d'%(i+1),'bidirectional') for i in range(8)],
        [(str(21-i),'B%d'%(i+1),'bidirectional') for i in range(8)],
        [('1','VCCA','power_in'),('23','VCCB','power_in'),('24','VCCB','power_in')],
        [('11','GND','power_in'),('12','GND','power_in'),('13','GND','power_in')],w=20.32,pitch=2.54))
    S.append(cs.mk_ic('SN74LVC244A','U','SN74LVC244A','Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm',TI+'sn74lvc244a.pdf','Octal buffer, 3-state outputs, 1.65-3.6 V (5 V tolerant inputs), TSSOP-20',
        [('1','1~{OE}','input'),('2','1A1','input'),('4','1A2','input'),('6','1A3','input'),('8','1A4','input'),('19','2~{OE}','input'),('11','2A1','input'),('13','2A2','input'),('15','2A3','input'),('17','2A4','input')],
        [('18','1Y1','output'),('16','1Y2','output'),('14','1Y3','output'),('12','1Y4','output'),('9','2Y1','output'),('7','2Y2','output'),('5','2Y3','output'),('3','2Y4','output')],
        [('20','VCC','power_in')],[('10','GND','power_in')],w=20.32,pitch=2.54))
    S.append(cs.mk_ic('TPS7A8300','U','TPS7A8300','Package_DFN_QFN:QFN-20-1EP_3.5x3.5mm_P0.5mm_EP2x2mm',TI+'tps7a83.pdf','2 A ultra-low-noise LDO, ANY-OUT 0.8-3.95 V, VQFN-20 (RGR)',
        [('15','IN','power_in'),('16','IN','power_in'),('17','IN','power_in'),('14','EN','input'),('13','NR/SS','passive'),('12','BIAS','passive'),('4','PG','open_collector')],
        [('1','OUT','power_out'),('19','OUT','power_out'),('20','OUT','power_out'),('2','SNS','input'),('3','FB','passive')],
        [('5','50mV','passive'),('6','100mV','passive'),('7','200mV','passive'),('9','400mV','passive'),('10','800mV','passive'),('11','1.6V','passive')],
        [('8','GND','power_in'),('18','GND','power_in'),('21','EP','power_in')],w=30.48,pitch=2.54))
    # FMC mezzanine plug: only the pins this design uses (68 LA, GND, 3P3V, VADJ, PRSNT, TDI/TDO)
    left=[(LA[n][0],la_name(n,'P'),'bidirectional') for n in range(34)]
    right=[(LA[n][1],la_name(n,'N'),'bidirectional') for n in range(34)]
    gnd=[(p,'GND','passive') for p in GND_PADS]
    other=[(p,'3P3V','passive') for p in P3V3]+[(p,'VADJ','passive') for p in VADJ]+[('H2','PRSNT_M2C_L','passive'),('D30','TDI','passive'),('D31','TDO','passive')]
    nb=len(gnd)//2
    top=gnd[:nb]; bottom=gnd[nb:]+other
    # pad numbers are strings like G6; mk_ic wants (number,name,type)
    S.append(cs.mk_ic('ASP-134602-01','J','ASP-134602-01','Connector_Samtec:Samtec_FMC_ASP-134602-01_10x40_P1.27mm_Vertical','https://www.samtec.com/products/asp-134602-01','FMC (VITA 57.1) mezzanine plug, 10x40, rows C D G H used (LPC)',
        left,right,top,bottom,w=2.54*(len(bottom)+1),pitch=2.54))
    return cs.lib(S)
if __name__=='__main__':
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'Bp.kicad_sym'),'w').write(dump(build())+'\n')
    print('Bp.kicad_sym written')
