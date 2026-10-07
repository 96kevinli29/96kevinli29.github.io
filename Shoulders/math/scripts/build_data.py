import json,re,os,glob,unicodedata,collections
S=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(os.environ.get('OPENAI_MATH','openai-math'),'preprints')
exec(open(S+'/extract.py').read().split('papers={}')[0])  # reuse delatex etc.
P=json.load(open(S+'/refs_all.json')); F=json.load(open(S+'/fields.json'))
HA_RE=re.compile(r'Hilbert-transform|Hilbert-form|Fourier-convergence|Maximal-Operator|Bochner|local-smoothing|Fourier-extension|Fourier-restriction|Schrodinger-equation-in|planar-Schrodinger|Kakeya|Riesz-estimates|Riesz-transforms|Falconer|pinned-planar|Erdos-similarity|ergodic-averages|Ergodic-Averages|Littlewood-polynomials|Fourier-certificate|self-similar-measures|[Dd]ecoupling|Strichartz|oscillatory-integral|Furstenberg-set|square-function',re.I)
HA={d for d in os.listdir(ROOT) if HA_RE.search(d) and 'Torus' not in d}
def fold(s): return ''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c)).lower().replace('ł','l').replace('ø','o')
PART={'de','van','von','der','den','le','la','di','da','du','dos','del'}
def split_name(n):
    n=n.strip().strip(',').strip()
    n=re.sub(r'\s+',' ',n)
    if ',' in n:
        last,first=[x.strip() for x in n.split(',',1)]
        first=re.sub(r',?\s*Jr\.?$','',first)
    else:
        tk=n.split()
        tk=[t for t in tk if t not in('Jr.','Jr','II','III')]
        if not tk: return None
        i=len(tk)-1
        while i>0 and tk[i-1].lower() in PART: i-=1
        last=' '.join(tk[i:]); first=' '.join(tk[:i])
    return first,last
def initials(first):
    parts=re.split(r'[\s\-]+',first.replace('.',' '))
    return ''.join(p[0] for p in parts if p and p[0].isalpha()).lower()
def is_full(first): return any(len(p.strip('.'))>1 for p in re.split(r'[\s\-]+',first))
# --- featured & fields
FM={}
for line in open(S+'/fields_medal.txt'):
    y,names=line.strip().split('|')
    for n in names.split(';'): FM[n]=int(y)
for fn_ in ('abel.txt','wolf.txt'):
    for line in open(S+'/'+fn_):
        y,names=line.strip().split('|')
        for n in names.split(';'): FM.setdefault(n,0)
SPECIAL_INIT={('bernstein','jn'),('bernstein','in'),('bernstein','j'),('keller','jb'),('arnold','vi'),('moser','j'),('sato','m'),('ito','k'),('siegel','cl'),('siegel','c'),('gelfand','im'),('gelfand','i'),('arthur','j'),('stein','em'),('stein','e'),('singer','im'),('singer','i'),('nash','j'),('tate','j'),('lax','p'),('lax','pd'),('meyer','y'),('sullivan','d'),('thompson','jg'),('jones','v'),('jones','vfr'),('lions','pl'),('yau','st'),('huh','j'),('cohen','pj'),('baker','a'),('roth','kf'),('thom','r'),('mori','s'),('werner','w')}
ALIAS={'misha':'mikhail','michael gromov':'mikhail','gregory':'grigory','grigori':'grigory','g. a.':'grigory','sergey':'sergei','alexandre':'alexander','tim':'timothy','w. t.':'timothy'}
HAKW=re.compile(r'kakeya|restriction|decoupl|furstenberg|falconer|projection|bochner|oscillatory|strichartz|hilbert|maximal|parabola|schr[oö]dinger|vinogradov|fourier|incidence|distance|wave|square function|multiplier',re.I)
HA_CO={'guth','zahl','maldague','shmerkin','orponen','ren','wu','iosevich','ou','du','zhang','guo','oh','zakharov','demeter','li','yung','roos','bourgain','tao'}
def resolve_featured(first,last,coauth,title):
    lf=fold(last); fi=initials(first); full=is_full(first); ff=fold(first)
    # explicit full-name matches for curated people
    if lf=='wang' and (ff.startswith('hong') and ff in('hong',)):
        return 'Hong Wang'
    if lf=='wang' and fi=='h' and not full:
        if (coauth & HA_CO) or HAKW.search(title or ''): return 'Hong Wang'
        return None
    if lf=='guo' and ff=='shaoming': return 'Shaoming Guo'
    if lf=='guo' and fi=='s' and not full:
        if (coauth & HA_CO) or HAKW.search(title or ''): return 'Shaoming Guo'
        return None
    if lf=='deng' and ff=='yu': return 'Yu Deng'
    if lf=='deng' and fi=='y' and not full:
        if (coauth & {'hani','nahmod','yue','ma','fan','guo','luo','germain','ionescu','pausader'}) or re.search(r'boltzmann|wave turbulence|dispersive|strichartz|schr|gibbs|hilbert.s sixth|euler',title or '',re.I): return 'Yu Deng'
        return None
    return 'GENERIC'
# canonical entities
ent=collections.defaultdict(lambda:dict(forms=collections.Counter(),papers=set(),refs=0))
fullnames=collections.defaultdict(set)   # (last,initials)->{full first}
recs=[]
for d,v in P.items():
    for r in v['refs']:
        names=[split_name(a) for a in r['authors']]
        names=[x for x in names if x and x[1]]
        for fn,ln in names:
            if is_full(fn): fullnames[(fold(ln),initials(fn))].add(fold(fn))
FMkey={}
for n,y in FM.items():
    fn,ln=split_name(n); FMkey[(fold(ln),initials(fn))]=n
AMBIG_SURNAMES={'bernstein','keller','arnold','moser','sato','ito','siegel','gelfand','arthur','stein','krein','singer','nash','tate','lax','meyer','sullivan','wang','li','zhang','liu','chen','yang','huang','zhao','wu','zhou','xu','sun','ma','zhu','hu','guo','he','lin','gao','luo','zheng','liang','xie','tang','han','cao','deng','feng','xiao','cheng','yu','jiang','kim','lee','park','choi','nguyen','tran','smith','jones','brown','baker','cohen','thompson','roth','thom','lions','mori','werner','huh'}
def ckey(fn,ln,coauth,title):
    lf=fold(ln); fi=initials(fn)
    r=resolve_featured(fn,ln,coauth,title)
    if r in('Hong Wang','Shaoming Guo','Yu Deng'): return r
    if r is None: pass
    # Fields medalists by full name or unambiguous initials
    k=(lf,fi[:1])
    for (l2,i2),name in FMkey.items():
        if l2==lf:
            mfn,mln=split_name(name)
            if is_full(fn):
                f0=ALIAS.get(fold(fn).split()[0],fold(fn).split()[0])
                if lf=='gromov' and f0 in('mikhail','misha','michael','m.'): return name
                if f0==fold(mfn).split()[0] or fold(fn).replace('-',' ')==fold(mfn).replace('-',' ') or (fold(fn).startswith(fold(mfn).split()[0][:3]) and lf not in AMBIG_SURNAMES):
                    return name
            else:
                if (lf,fi) in SPECIAL_INIT and fi[:1]==initials(mfn)[:1]: return name
                if lf not in AMBIG_SURNAMES and fi[:1]==initials(mfn)[:1]: return name
                if lf in('lions',) and fi.startswith('pl'): return name
                if lf=='yau' and fi.startswith('st'): return name
                if lf=='jones' and fi.startswith('v'): return name
                if lf=='huh' and fi=='j': return name
    if is_full(fn):
        return fold(re.split(r'[\s]+',fn)[0])+'|'+lf
    cands={c.split()[0] for c in fullnames.get((lf,fi),set())}
    if len(cands)==1 and lf not in AMBIG_SURNAMES: return list(cands)[0]+'|'+lf
    return 'init:'+fi+'|'+lf
papers=[]; refrows=[]
for d in sorted(P):
    v=P[d]; meta=F.get(d,{})
    readme=open(f'{ROOT}/{d}/README.md',errors='ignore').read()
    m=re.search(r'^#\s*\[(.*?)\]\(',readme,re.M); title=m.group(1) if m else d
    dm=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)-(\d+)-2026',d)
    months={'September':9,'October':10,'August':8,'July':7}
    date=f"2026-{months.get(dm.group(1),0):02d}-{int(dm.group(2)):02d}" if dm else '2026-09-24'
    pref=[]
    for r in v['refs']:
        names=[split_name(a) for a in r['authors']]; names=[x for x in names if x and x[1]]
        co={fold(ln) for fn,ln in names}
        keys=[]
        for fn,ln in names:
            if fold(ln)=='openai': keys.append('OpenAI'); continue
            if re.search(r'stacks|project|authors|committee|collaboration|contributors|developers|team|wiki|group',fold(fn+' '+ln)): keys.append(None); continue
            k=ckey(fn,ln,co-{fold(ln)},r.get('title',''))
            keys.append(k); e=ent[k]; e['forms'][(fn+' '+ln).strip()]+=1; e['papers'].add(d); e['refs']+=1
        link=''
        if r.get('doi'): link='https://doi.org/'+r['doi'].replace('https://doi.org/','')
        elif r.get('eprint') and re.match(r'\d{4}\.\d{4,5}',r['eprint']): link='https://arxiv.org/abs/'+r['eprint']
        elif r.get('url'): link=r['url']
        pref.append(dict(key=r['key'],a=keys,an=[(fn+' '+ln).strip() for fn,ln in names],t=r.get('title','')[:220],y=r.get('year',''),v=r.get('venue','')[:100],l=link))
    tags=[]
    if d in HA: tags.append('调和分析')
    papers.append(dict(id=d,title=delatex(title),date=date,field=meta.get('field',''),family=meta.get('family',''),family_title=delatex(meta.get('family_title','')),pdf='https://github.com/openai/math/blob/main/preprints/'+meta.get('pdf',d),tags=tags,refs=pref))
# display names
names={}
for k,e in ent.items():
    if k in FM or k in('Shaoming Guo','Hong Wang','Yu Deng'): names[k]=k if k!='Hong Wang' else 'Hong Wang'; continue
    best=max(e['forms'].items(),key=lambda x:(is_full(x[0].rsplit(' ',1)[0]) ,x[1],len(x[0])))[0]
    names[k]=best
json.dump(dict(papers=papers,names=names),open(S+'/data_stage1.json','w'),ensure_ascii=False)
c=sorted(ent.items(),key=lambda x:-len(x[1]['papers']))
print(len(papers),len(ent))
for k,e in c[:60]: print(len(e['papers']),names[k],'|',k)
