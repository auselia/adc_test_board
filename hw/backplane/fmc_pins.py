"""VITA 57.1 FMC LPC pinout, rows C, D, G, H (the four populated rows of the ZedBoard carrier connector).
Names follow the standard; the LA pad numbers were cross-checked against the ZedBoard schematic (64 of 68 listed there)."""
import re
def _row(letter,spec):
    return {letter+str(i):n for i,n in spec.items()}
GND_C=[1,4,5,8,9,12,13,16,17,20,21,24,25,28,29,32,33,36,38,40]
GND_D=[2,3,6,7,10,13,16,19,22,25,28,37,39]
GND_G=[1,4,5,8,11,14,17,20,23,26,29,32,35,38,40]
GND_H=[3,6,9,12,15,18,21,24,27,30,33,36,39]
LA={ # LA number -> (P pad, N pad)
 0:('G6','G7'),1:('D8','D9'),2:('H7','H8'),3:('G9','G10'),4:('H10','H11'),5:('D11','D12'),6:('C10','C11'),7:('H13','H14'),8:('G12','G13'),
 9:('D14','D15'),10:('C14','C15'),11:('H16','H17'),12:('G15','G16'),13:('D17','D18'),14:('C18','C19'),15:('H19','H20'),16:('G18','G19'),
 17:('D20','D21'),18:('C22','C23'),19:('H22','H23'),20:('G21','G22'),21:('H25','H26'),22:('G24','G25'),23:('D23','D24'),24:('H28','H29'),
 25:('G27','G28'),26:('D26','D27'),27:('C26','C27'),28:('H31','H32'),29:('G30','G31'),30:('H34','H35'),31:('G33','G34'),32:('H37','H38'),33:('G36','G37')}
CC={0,1,17,18}
def la_name(n,pn):
    return 'LA%02d_%s%s'%(n,pn,'_CC' if n in CC else '')
GND_PADS=sorted([r+str(i) for r,l in (('C',GND_C),('D',GND_D),('G',GND_G),('H',GND_H)) for i in l],key=lambda s:(s[0],int(s[1:])))
P3V3=['C39','D36','D38','D40']; VADJ=['G39','H40']
def pad_row(p): return p[0]
