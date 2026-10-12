import re, copy
class Str(str):
    pass
_tok=re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
def parse(text):
    stack=[[]]
    for t in _tok.findall(text):
        if t=='(':
            stack.append([])
        elif t==')':
            l=stack.pop(); stack[-1].append(l)
        elif t[0]=='"':
            stack[-1].append(Str(t[1:-1].replace('\\"','"').replace('\\\\','\\')))
        else:
            stack[-1].append(t)
    return stack[0][0]
def q(s): return '"'+str(s).replace('\\','\\\\').replace('"','\\"')+'"'
def dump(n,ind=0):
    pad='\t'*ind
    if isinstance(n,Str): return q(n)
    if not isinstance(n,list): return str(n)
    if not any(isinstance(c,list) for c in n):
        return '('+' '.join(dump(c) for c in n)+')'
    out=['(']; first=True; line=[]
    i=0
    heads=[]
    while i<len(n) and not isinstance(n[i],list):
        heads.append(dump(n[i])); i+=1
    s='('+' '.join(heads)
    for c in n[i:]:
        if isinstance(c,list):
            s+='\n'+'\t'*(ind+1)+dump(c,ind+1)
        else:
            s+='\n'+'\t'*(ind+1)+dump(c)
    s+='\n'+pad+')'
    return s
def find(n,head):
    return [c for c in n if isinstance(c,list) and c and c[0]==head]
def get(n,head,default=None):
    r=find(n,head); return r[0] if r else default
