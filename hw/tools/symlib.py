import os, copy
from sexp import *
SYM='/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/'
_cache={}
def load(lib):
    if lib not in _cache:
        _cache[lib]=parse(open(SYM+lib+'.kicad_sym').read())
    return _cache[lib]
def get_symbol(libid):
    lib,name=libid.split(':')
    t=load(lib)
    for c in find(t,'symbol'):
        if c[1]==name: 
            ext=get(c,'extends')
            if ext: raise Exception('extends not handled for '+libid)
            return copy.deepcopy(c)
    raise KeyError(libid)
def embed(libid,symnode):
    s=copy.deepcopy(symnode); s[1]=Str(libid); return s
def pins_of(sym):
    out=[]
    def walk(n):
        for c in n:
            if isinstance(c,list) and c:
                if c[0]=='pin' and len(c)>2 and not isinstance(c[2],list) is False:
                    pass
                if c[0]=='pin':
                    at=get(c,'at'); nm=get(c,'name'); nu=get(c,'number'); ln=get(c,'length')
                    out.append(dict(number=str(nu[1]),name=str(nm[1]),x=float(at[1]),y=float(at[2]),a=int(float(at[3])),type=c[1]))
                else: walk(c)
    walk(sym)
    return out
