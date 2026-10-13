"""Download the TI vendor SPICE models and make them readable by ngspice. The files are not stored in the repo.
usage: python3 fetch_models.py     (writes OPA365.lib and THS4531.lib next to this script)
"""
import os,re,subprocess,tempfile,zipfile
HERE=os.path.dirname(os.path.abspath(__file__))
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def get(url,dst): subprocess.run(['curl','-sL','-A',UA,'-o',dst,url],check=True)
def opa365(tsm,out):
    d=open(tsm,'rb').read(); pos=d.find(b'* OPA365 SPICE MACROMODEL')-1; lines=[]
    while pos<len(d):                     # TINA container: [length byte][text][NULs]...
        L=d[pos]; s=d[pos+1:pos+1+L].split(b'\x00')[0]
        if not s or not all(32<=c<127 for c in s): break
        t=s.decode(); lines.append(t); pos+=1+L
        if t.strip().upper().startswith('.ENDS'): break
        while pos<len(d) and d[pos]==0: pos+=1
    open(out,'w').write('\n'.join(lines)+'\n')
def clean(src,dst):                       # strip non-ASCII bytes, convert PSpice VSWITCH to ngspice SW
    t=open(src,'rb').read().decode('latin1'); t=re.sub(r'[^\x09\x0a\x0d\x20-\x7e]','',t)
    def num(s):
        s=s.strip().rstrip('Vv').lower(); m=re.fullmatch(r'([-+]?[\d.]+(?:e[-+]?\d+)?)(meg|k|m|u|n|p|f)?',s)
        return float(m.group(1))*{'meg':1e6,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,None:1}[m.group(2)]
    def sw(m):
        kv={a[0].lower():a[1] for a in re.findall(r'(\w+)\s*=\s*([^\s)]+)',m.group(2))}
        if 'vt' in kv: vt,vh=num(kv['vt']),num(kv['vh'])
        else: von,voff=num(kv['von']),num(kv['voff']); vt=(von+voff)/2; vh=(von-voff)/2
        return f".MODEL {m.group(1)} SW(Roff={num(kv['roff'])} Ron={num(kv['ron'])} Vt={vt} Vh={vh})"
    open(dst,'w').write(re.sub(r'\.MODEL\s+(\S+)\s+VSWITCH\s*\(?(.*?)\)?\s*$',sw,t,flags=re.I|re.M))
if __name__=='__main__':
    d=tempfile.mkdtemp()
    get('https://www.ti.com/lit/tsm/sbom203',os.path.join(d,'opa365.tsm'))
    opa365(os.path.join(d,'opa365.tsm'),os.path.join(HERE,'OPA365.lib'))
    get('https://www.ti.com/lit/zip/slom263',os.path.join(d,'ths.zip'))
    zipfile.ZipFile(os.path.join(d,'ths.zip')).extractall(d)
    src=[os.path.join(r,f) for r,_,fs in os.walk(d) for f in fs if f.lower()=='ths4531.lib'][0]
    clean(src,os.path.join(HERE,'THS4531.lib'))
    print('ok: OPA365.lib, THS4531.lib')
