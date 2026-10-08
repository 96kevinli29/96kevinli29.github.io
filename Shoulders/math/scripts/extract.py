import os,re,glob,json,unicodedata
ROOT=os.path.join(os.environ.get('OPENAI_MATH','openai-math'),'preprints')
ACC={"\\'":'\u0301','\\`':'\u0300','\\"':'\u0308','\\^':'\u0302','\\~':'\u0303','\\c':'\u0327','\\v':'\u030c','\\u':'\u0306','\\H':'\u030b','\\.':'\u0307','\\=':'\u0304'}
def delatex(s):
    s=re.sub(r'%.*','',s)
    for k,v in ACC.items():
        s=re.sub(re.escape(k)+r'\s*\{?\\?([a-zA-Z])\}?',lambda m:m.group(1)+v,s)
    # letters written as control words: {\L}ukasz, Radziwi\l\l, {\o}, \ss … (not \left, \label …)
    for cw,ch in (('AE','Æ'),('ae','æ'),('OE','Œ'),('oe','œ'),('AA','Å'),('aa','å'),('ss','ß'),('L','Ł'),('l','ł'),('O','Ø'),('o','ø'),('i','ı')):
        s=re.sub(r'\{\\'+cw+r'\}|\\'+cw+r'\{\}|\\'+cw+r'(?![a-zA-Z])\s?',ch,s)
    s=s.replace('ı','i').replace('\\&','&').replace('--','–').replace('~',' ')
    s=re.sub(r'\\(?:emph|textit|textbf|textsc|textrm|mathrm|mathbb|mathcal|bf|it|em|sc|rm|url|href)\b\s*','',s)
    s=re.sub(r'\\[a-zA-Z]+\*?','',s)
    s=re.sub(r'[{}]','',s); s=unicodedata.normalize('NFC',s)
    return re.sub(r'\s+',' ',s).strip()
def field(e,name):
    m=re.search(r'(?<![a-z])'+name+r'\s*=\s*',e,re.I)
    if not m: return ''
    i=m.end(); 
    if i>=len(e): return ''
    c=e[i]
    if c=='{':
        d=0
        for j in range(i,len(e)):
            if e[j]=='{': d+=1
            elif e[j]=='}':
                d-=1
                if d==0: return e[i+1:j]
    if c=='"':
        j=e.find('"',i+1); return e[i+1:j]
    m=re.match(r'[^,\n]+',e[i:]); return m.group(0) if m else ''
def parse_bib(t):
    out=[]
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,\s]+)\s*,',t):
        if m.group(1).lower() in('string','preamble','comment'): continue
        st=m.end(); nx=t.find('\n@',st); e=t[st: nx if nx>0 else len(t)]
        a=delatex(field(e,'author') or field(e,'editor'))
        names=[x.strip() for x in re.split(r'\s+and\s+',a) if x.strip()]
        out.append(dict(key=m.group(2),authors=names,title=delatex(field(e,'title')),year=(re.search(r'\d{4}',field(e,'year') or field(e,'date')) or [''])[0] if (field(e,'year') or field(e,'date')) else '',
             venue=delatex(field(e,'journal') or field(e,'booktitle') or field(e,'publisher') or field(e,'howpublished'))[:120],
             doi=field(e,'doi').strip(),url=field(e,'url').strip(),eprint=field(e,'eprint').strip()))
    return out
NAMETOK=re.compile(r"^(?:[A-ZÀ-ÞŁØ][\w'’\-]*\.?|[A-Z]\.-?[A-Z]?\.?|de|van|von|der|den|le|la|di|da|du|dos|del|Jr\.?|II|III)$")
STOP={'The','On','A','An','Theory','Introduction','Lectures','Lecture','Notes','Analysis','Geometry','Algebra','Equations','Groups','Spaces','Functions','Mathematics','Integral','Hodge','Complex','Mixed','Some','New','Note','Remarks','Problem','Problems','Conjecture','Theorem','Topics','Methods','Elements','Foundations','Principles','Handbook','Surfaces','Varieties','Theorems','Bounds','Sets','Random','Real','Linear','Graph','Graphs','Quantum','Algebraic','Differential','Partial','Elliptic','Modular','Geometric','Harmonic','Fourier','Convex','Minimal','Stochastic','Ergodic','Topological','Combinatorial','Probability','Statistical','Abelian','Lie','Finite','Infinite','Higher','Measure','Computational','In','Of','For','To','From','With','Mirror','Singularities','Mixed','Galois','Binary','Exact','Top-down','Volume','Proceedings','Annals','Journal','Inventiones','Acta','Duke','American','Cambridge','Springer','Princeton','Oxford','Academic','Press','University','Mathematical','Society','Grundlehren','Lecture','Graduate','Texts','Studies','Series','Advances','Communications','Transactions','Bulletin','Comptes','Annales','Physical','Review','Letters','Soviet','Math','Ann','Invent','Publ','IHES','Preprint','In:'}
INIT=re.compile(r"^(?:[A-Z][a-z]?\.(?:-[A-Z]\.)*|[A-Z]\.-?[A-Z]\.?)$")
WORD=re.compile(r"^(?:[A-ZÀ-ÞŁØŚŻŹĆŃŠČŘŽ][\w'’\-]*|de|van|von|der|den|le|la|di|da|du|dos|del|Jr\.?|II|III)$")
def parse_bibitem_authors(text):
    toks=text.replace('\\ ',' ').split()
    acc=[]; 
    for t in toks:
        core=t.rstrip(',;:')
        if core=='and' or core=='&': acc.append('and'); continue
        endp=core.endswith('.')
        c2=core.rstrip('.')
        if INIT.match(core) or core in('Jr.','Jr'): acc.append(t); continue
        if WORD.match(c2) and c2 not in STOP:
            acc.append(t)
            if endp and len(c2)>2: break
            continue
        break
    s=' '.join(acc).rstrip(',.; ')
    # if the last chunk is cut mid-title (no period end), drop chunks with a stopword-looking tail
    names=[x.strip() for x in re.split(r',\s*|\s+and\s+|^and\s+',s) if x and x.strip() and x.strip()!='and']
    names=[re.sub(r'^and\s+','',n) for n in names]
    good=[]
    if not names: return good
    hasinit=lambda n:any(INIT.match(x) for x in n.split())
    style_init=hasinit(names[0])
    for i,n in enumerate(names):
        tk=n.split()
        if n=='OpenAI' and i==0: good.append(n); break
        if style_init:
            if hasinit(n) and len(tk)<=5: good.append(n)
            else: break
        else:
            if 2<=len(tk)<=5: good.append(n)
            else: break
    return good
def parse_bibitems(t):
    out=[]
    for m in re.finditer(r'\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})',t,re.S):
        raw=delatex(m.group(2)); a=parse_bibitem_authors(raw)
        # title: after authors segment up to next comma
        rest=raw
        if a:
            idx=raw.find(a[-1])+len(a[-1]); rest=raw[idx:].lstrip(' ,.:')
        ti=re.split(r'\s,\s|,\s(?=[A-Z][a-z]+\.?\s)|\.\s',rest)[0][:200]
        y=re.findall(r'\((\d{4})\)|\b(19\d\d|20\d\d)\b',raw)
        yy=''
        for g in y:
            yy=g[0] or g[1]; break
        doi=(re.search(r'10\.\d{4,}/[^\s,;]+',m.group(2)) or [''])[0]
        url=(re.search(r'https?://[^\s}]+',m.group(2)) or [''])[0]
        out.append(dict(key=m.group(1).strip(),authors=a,title=ti,year=yy,venue='',doi=doi.rstrip('.'),url=url,eprint='',raw=raw[:300]))
    return out
def alltex(d):
    fs=glob.glob(f'{ROOT}/{d}/build/**/*.tex',recursive=True)
    return {f:open(f,errors='ignore').read() for f in fs}
papers={}
# Only the current editions listed in CONTENTS.md: revised papers keep their old edition's folder,
# and withdrawn papers keep theirs too, so listing preprints/ would count them twice or count retractions.
_cont=os.path.join(os.path.dirname(ROOT),'CONTENTS.md')
CURRENT=set(re.findall(r'\]\(preprints/(.+?)/[^/()\s]+\.(?:pdf|md)\)',open(_cont).read())) if os.path.exists(_cont) else None
for d in sorted(os.listdir(ROOT)):
    if CURRENT is not None and d not in CURRENT: continue
    b=f'{ROOT}/{d}/build'; refs=[]
    for f in glob.glob(b+'/**/*.bib',recursive=True):
        refs+=parse_bib(open(f,errors='ignore').read())
    src='bib'
    if not refs:
        texs=alltex(d)
        for f,t in texs.items(): refs+=parse_bibitems(t)
        for f in glob.glob(b+'/**/*.bbl',recursive=True): 
            if not refs: refs+=parse_bibitems(open(f,errors='ignore').read())
        src='bibitem'
    # dedupe keys
    seen=set(); R=[]
    for r in refs:
        if r['key'] in seen: continue
        seen.add(r['key']); R.append(r)
    papers[d]=dict(refs=R,src=src)
json.dump(papers,open(os.path.dirname(__file__)+'/refs_all.json','w'),ensure_ascii=False)
import collections
print(len(papers),sum(len(p['refs']) for p in papers.values()))
print('no refs:',[d for d,p in papers.items() if not p['refs']][:20])
print('refs w/o authors:',sum(1 for p in papers.values() for r in p['refs'] if not r['authors']))
