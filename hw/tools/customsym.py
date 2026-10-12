from sexp import *
def eff(size=1.27,hide=False,just=None):
    e=['effects',['font',['size',size,size]]]
    if just: e.append(['justify',just])
    if hide: e.append(['hide','yes'])
    return e
def prop(name,val,x,y,hide=False,rot=0):
    p=['property',Str(name),Str(val),['at',x,y,rot],['show_name','no'],['do_not_autoplace','no']]
    if hide: p.append(['hide','yes'])
    p.append(eff(1.27))
    return p
def mk_ic(name,ref,value,fp,ds,desc,left,right,top,bottom,w=15.24,pitch=5.08):
    """pins: (number,name,type). Pins listed top->bottom (left/right) or left->right (top/bottom)."""
    nl=max(len(left),len(right),1)
    h=max((nl-1)*pitch+2*pitch, 10.16)
    nt=max(len(top),len(bottom),1)
    w=max(w,(nt-1)*pitch+2*pitch)
    hw,hh=w/2,h/2
    # snap to 2.54 grid
    def sn(v): return round(v/2.54)*2.54
    hw,hh=sn(hw),sn(hh)
    pins=[]
    def pin(num,nm,typ,x,y,a):
        pins.append(['pin',typ,'line',['at',round(x,2),round(y,2),a],['length',2.54],['name',Str(nm),eff()],['number',Str(num),eff()]])
    for i,(n,nm,t) in enumerate(left):
        y=hh-pitch*(i+1) if nl>1 else 0; y=sn(hh-pitch*(i+1)+ (pitch if False else 0)); pin(n,nm,t,-hw-2.54,y,0)
    for i,(n,nm,t) in enumerate(right):
        y=sn(hh-pitch*(i+1)); pin(n,nm,t,hw+2.54,y,180)
    def xs(k):
        return [sn(((i-(k-1)/2))*pitch) for i in range(k)]
    for x,(n,nm,t) in zip(xs(len(top)),top): pin(n,nm,t,x,hh+2.54,270)
    for x,(n,nm,t) in zip(xs(len(bottom)),bottom): pin(n,nm,t,x,-hh-2.54,90)
    sym=['symbol',Str(name),
         ['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['in_pos_files','yes'],['duplicate_pin_numbers_are_jumpers','no'],
         prop('Reference',ref,0,hh+5.08),prop('Value',value,0,-hh-5.08),prop('Footprint',fp,0,0,True),prop('Datasheet',ds,0,0,True),prop('Description',desc,0,0,True),
         ['symbol',Str(name+'_0_1'),['rectangle',['start',-hw,hh],['end',hw,-hh],['stroke',['width',0.254],['type','default']],['fill',['type','background']]]],
         ['symbol',Str(name+'_1_1')]+pins,
         ['embedded_fonts','no']]
    return sym
def lib(symbols):
    return ['kicad_symbol_lib',['version',20251024],['generator',Str('auselia_gen')],['generator_version',Str('10.0')]]+symbols
TI='https://www.ti.com/lit/ds/symlink/'
SOIC='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
def build():
    S=[]
    S.append(mk_ic('OPA2365','U','OPA2365',SOIC,TI+'opa365.pdf','Dual 50 MHz zero-crossover RRIO op-amp, 2.2-5.5 V, SOIC-8',
        [('3','+INA','input'),('2','-INA','input'),('5','+INB','input'),('6','-INB','input')],
        [('1','OUTA','output'),('7','OUTB','output')],[('8','V+','power_in')],[('4','V-','power_in')]))
    S.append(mk_ic('THS4531','U','THS4531',SOIC,TI+'ths4531.pdf','Low-power fully-differential amplifier, 2.5-5.5 V, SOIC-8',
        [('8','VIN+','input'),('1','VIN-','input'),('2','VOCM','input'),('7','~{PD}','input')],
        [('4','VOUT+','output'),('5','VOUT-','output')],[('3','VS+','power_in')],[('6','VS-','power_in')]))
    S.append(mk_ic('ADS7057','U','ADS7057','Auselia:ADS7057_X2QFN-8_1.5x1.5mm',TI+'ads7057.pdf','14-bit 2.5 MSPS differential SAR ADC, X2QFN-8 (RUG)',
        [('7','AINP','input'),('8','AINM','input')],
        [('1','~{CS}','input'),('3','SCLK','input'),('2','SDO','output')],[('6','AVDD','power_in'),('4','DVDD','power_in')],[('5','GND','power_in')]))
    S.append(mk_ic('REF1933','U','REF1933','Package_TO_SOT_SMD:SOT-23-5',TI+'ref1933.pdf','3.3 V reference with VREF/2 bias output, SOT-23-5 (DDC)',
        [('4','VIN','power_in'),('3','EN','input')],
        [('5','VREF','power_out'),('1','VBIAS','output')],[],[('2','GND','power_in')]))
    S.append(mk_ic('TLV3202','U','TLV3202',SOIC,TI+'tlv3202.pdf','Dual 40 ns push-pull comparator, 2.7-5.5 V, SOIC-8',
        [('3','1IN+','input'),('2','1IN-','input'),('5','2IN+','input'),('6','2IN-','input')],
        [('1','1OUT','output'),('7','2OUT','output')],[('8','VCC','power_in')],[('4','GND','power_in')]))
    S.append(mk_ic('TPS7A4901','U','TPS7A4901','Package_SO:HVSSOP-8-1EP_3x3mm_P0.65mm_EP1.57x1.89mm',TI+'tps7a49.pdf','36 V 150 mA ultra-low-noise adjustable LDO, HVSSOP-8 PowerPAD',
        [('8','IN','power_in'),('5','EN','input'),('6','NR/SS','passive')],
        [('1','OUT','power_out'),('2','FB','input'),('3','NC','no_connect'),('7','DNC','no_connect')],[],[('4','GND','power_in'),('9','PAD','passive')]))
    S.append(mk_ic('LM393','U','LM393',SOIC,TI+'lm393.pdf','Dual open-collector comparator, 2-36 V, SOIC-8',
        [('3','1IN+','input'),('2','1IN-','input'),('5','2IN+','input'),('6','2IN-','input')],
        [('1','1OUT','open_collector'),('7','2OUT','open_collector')],[('8','VCC','power_in')],[('4','GND','power_in')]))
    for v in ('3.3','5.0'):
        S.append(mk_ic('AMS1117-'+v,'U','AMS1117-'+v,'Package_TO_SOT_SMD:SOT-223-3_TabPin2','http://www.advanced-monolithic.com/pdf/ds1117.pdf','1 A LDO, fixed '+v+' V, SOT-223',
            [('3','VIN','power_in')],[('2','VOUT','power_out')],[],[('1','GND','power_in')]))
    return lib(S)
if __name__=='__main__':
    open('../Auselia.kicad_sym','w').write(dump(build())+'\n')
    print('written')
