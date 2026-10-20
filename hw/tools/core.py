import os, uuid, math, copy, collections
from sexp import *
import symlib, customsym
PROJECT="ADC_Test"
GLOBALS=set()
def U(): return str(uuid.uuid4())
def font(size=1.27,bold=False):
    return ['font',['size',size,size]]+([['bold','yes']] if bold else [])
class Sym:
    cache={}
    @classmethod
    def get(cls,libid):
        if libid not in cls.cache:
            if libid.startswith('Auselia:') or libid.startswith('Bp:'):
                libfile={'Auselia':os.path.join('..','Auselia.kicad_sym'),'Bp':os.path.join('..','backplane','Bp.kicad_sym')}[libid.split(':')[0]]
                t=parse(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),libfile)).read())
                s=[c for c in find(t,'symbol') if c[1]==libid.split(':')[1]][0]
                s=copy.deepcopy(s)
            else:
                s=symlib.get_symbol(libid)
            emb=copy.deepcopy(s); emb[1]=Str(libid)
            cls.cache[libid]=(emb,symlib.pins_of(s))
        return cls.cache[libid]
class Sheet:
    def __init__(s,name,file,paper='A3',title=''):
        s.name,s.file,s.paper,s.title=name,file,paper,title
        s.uuid=U(); s.items=[]; s.libs={}; s.path=None; s.page=None
class Design:
    def __init__(s):
        s.root=Sheet('root','AFE_v1.kicad_sch','A3'); s.sheets=[]; s.cnt=collections.defaultdict(int)
        s.nets=collections.defaultdict(list)  # (sheet,net)->pins for sanity
    def ref(s,prefix):
        s.cnt[prefix]+=1; return f"{prefix}{s.cnt[prefix]}"
D=Design()
def rotpt(vx,vy,rot):
    t=math.radians(rot); c,sn=round(math.cos(t)),round(math.sin(t))
    return vx*c+vy*sn, -vx*sn+vy*c
def effects(size=1.27,just=None,hide=False,bold=False):
    e=['effects',font(size,bold)]
    if just: e.append(['justify']+just.split())
    if hide: e.append(['hide','yes'])
    return e
def add(sh,libid,value,fp,x,y,nets=None,prefix=None,rot=0,ref=None,props=None,refpos=None,valpos=None,dnp=False,hide_val=False):
    x=round(round(x/2.54)*2.54,2); y=round(round(y/2.54)*2.54,2)
    emb,pins=Sym.get(libid)
    sh.libs[libid]=emb
    if ref is None: ref=D.ref(prefix or 'U')
    nets=nets or {}
    inst=['symbol',['lib_id',Str(libid)],['at',x,y,rot],['unit',1],['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['dnp','yes' if dnp else 'no'],['uuid',Str(U())]]
    # property positions
    xs=[p['x'] for p in pins] or [0]; ys=[p['y'] for p in pins] or [0]
    vert2 = len(pins)==2 and abs(pins[0]['x']-pins[1]['x'])<0.01
    if refpos: rp=refpos
    elif vert2: rp=(x+2.54,y-1.27) if rot in (0,180) else (x,y-3.2)
    else: rp=(x,y-(max(ys)+3.5))
    if valpos: vp=valpos
    elif vert2: vp=(x+2.54,y+1.27) if rot in (0,180) else (x,y+3.2)
    else: vp=(x,y+(-min(ys)+3.5))
    just = 'left' if (vert2 and rot in (0,180)) else None
    inst.append(['property',Str('Reference'),Str(ref),['at',round(rp[0],2),round(rp[1],2),0],effects(1.27,just)])
    inst.append(['property',Str('Value'),Str(value),['at',round(vp[0],2),round(vp[1],2),0],effects(1.27,just,hide_val)])
    inst.append(['property',Str('Footprint'),Str(fp),['at',x,y,0],effects(1.27,None,True)])
    inst.append(['property',Str('Datasheet'),Str('~'),['at',x,y,0],effects(1.27,None,True)])
    for k,v in (props or {}).items():
        inst.append(['property',Str(k),Str(v),['at',x,y,0],effects(1.27,None,True)])
    for p in pins: inst.append(['pin',Str(p['number']),['uuid',Str(U())]])
    inst.append(['__instances__',ref])
    sh.items.append(inst)
    # connections
    pn={p['number']:p for p in pins}
    for num,net in nets.items():
        p=pn[str(num)]
        vx,vy=rotpt(p['x'],-p['y'],rot)
        px,py=round(x+vx,2),round(y+vy,2)
        ang=(p['a']+180+rot)%360
        if net=='NC':
            sh.items.append(['no_connect',['at',px,py],['uuid',Str(U())]])
        else:
            label(sh,net,px,py,ang)
    missing=[p['number'] for p in pins if str(p['number']) not in {str(k) for k in nets} and libid not in ('Mechanical:MountingHole',)]
    if missing: raise Exception(f"{ref} {libid} unconnected pins {missing}")
    return ref
JUST={0:'left bottom',90:'left bottom',180:'right bottom',270:'right bottom'}
def label(sh,net,x,y,ang):
    if net in GLOBALS:
        sh.items.append(['global_label',Str(net),['shape','passive'],['at',x,y,ang],['fields_autoplaced','yes'],
            effects(1.27,'left' if ang in (0,90) else 'right'),['uuid',Str(U())],
            ['property',Str('Intersheetrefs'),Str('${INTERSHEET_REFS}'),['at',x,y,0],effects(1.27,None,True)]])
    else:
        sh.items.append(['label',Str(net),['at',x,y,ang],effects(1.27,JUST[ang]),['uuid',Str(U())]])
def text(sh,t,x,y,size=1.8,bold=False):
    sh.items.append(['text',Str(t),['exclude_from_sim','no'],['at',x,y,0],effects(size,'left bottom',False,bold),['uuid',Str(U())]])
def rule(sh,x,y,w):  # visual divider
    sh.items.append(['polyline',['pts',['xy',x,y],['xy',x+w,y]],['stroke',['width',0.25],['type','solid']],['uuid',Str(U())]])
def render(sh):
    path=sh.path
    libs=[sh.libs[k] for k in sorted(sh.libs)]
    out=['kicad_sch',['version',20250114],['generator',Str('eeschema')],['generator_version',Str('9.0')],['uuid',Str(sh.uuid)],['paper',Str(sh.paper)],
         ['title_block',['title',Str(sh.title)],['date',Str('2026-10-12')],['rev',Str('A')],['company',Str('Universidad de los Andes - Auselia')]],
         ['lib_symbols']+libs]
    for it in sh.items:
        if it[0]=='symbol':
            it=copy.deepcopy(it)
            ref=[c for c in it if c[0]=='__instances__'][0][1]
            it=[c for c in it if c[0]!='__instances__']
            it.append(['instances',['project',Str(PROJECT),['path',Str(path),['reference',Str(ref)],['unit',1]]]])
        out.append(it)
    out.append(['sheet_instances',['path',Str('/'),['page',Str('1')]]]) if sh is D.root else None
    out=[o for o in out if o is not None]
    out.append(['embedded_fonts','no'])
    return dump(out)+'\n'
