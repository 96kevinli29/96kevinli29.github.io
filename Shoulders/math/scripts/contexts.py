import json,re,glob,os,collections
S=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(os.environ.get('OPENAI_MATH','openai-math'),'preprints')
D=json.load(open(S+'/data_stage1.json'))
FM={}
for line in open(S+'/fields_medal.txt'):
    y,ns=line.strip().split('|')
    for n in ns.split(';'): FM[n]=int(y)
for fn_ in ('abel.txt','wolf.txt'):
    for line in open(S+'/'+fn_):
        y,ns=line.strip().split('|')
        for n in ns.split(';'): FM.setdefault(n,0)
_cnt=collections.Counter()
for p_ in D['papers']:
    for r_ in p_['refs']:
        for a_ in r_['a']:
            if a_ and a_!='OpenAI' and not str(a_).startswith('init:'): _cnt[a_]+=1
FEAT=set(FM)|{'Shaoming Guo'}|{k for k,_ in _cnt.most_common(60)}
CITE=re.compile(r'\\(?:[Cc]ite[a-zA-Z]*|parencite|textcite|autocite|footcite)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}')
def clean(s):
    s=re.sub(r'(?<!\\)%.*','',s)
    s=re.sub(r'\\(label|ref|eqref|cref|Cref|autoref)\{[^}]*\}',lambda m:'' if m.group(1)=='label' else '(ref)',s)
    s=CITE.sub(lambda m:'['+m.group(1).replace(' ','')+']',s)
    s=re.sub(r'\\(emph|textit|textbf|mathrm|operatorname|mathbb|mathcal|mathbf|text)\{([^{}]*)\}',r'\2',s)
    s=re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}','',s)
    s=re.sub(r'\\(item|noindent|medskip|smallskip|bigskip|par)\b','',s)
    s=s.replace('~',' ').replace('``','"').replace("''",'"').replace('--','–')
    return re.sub(r'\s+',' ',s).strip()
DIRECT=re.compile(r'\b(follow(s|ing)? (the|their)|used in \[|in the (invariant )?formulation of|puts? |we (use|apply|follow|invoke|adapt|combine|borrow|import|rely)|we take|following|by \[|from \[|using|applying|apply|invok|adapt|as in \[|in the form of|reduces to|the argument of|the method of|the proof of|their (method|argument|theorem|lemma|estimate|change|construction|approach|framework)|(theorem|lemma|proposition|corollary|estimate|inequality|identity) (of|from|in) |\[[^\]]*,\s*(Thm|Theorem|Lemma|Prop|Proposition|Cor|Corollary|Section|Sec\.|§|Eq|Equation|Remark|Definition)\b)',re.I)
BACK=re.compile(r'\b(see also|see,? e\.g|see for example|for example|e\.g\.|cf\.|for background|for a survey|survey|history|historical|introduced|conjectured|first (proved|studied|introduced)|was (proved|shown|established)|proved by|established by|classical|well[- ]known|recent(ly)?|related)\b',re.I)
def classify(sent):
    if DIRECT.search(sent): return 'use'
    if BACK.search(sent): return 'background'
    return 'mention'
out=collections.defaultdict(list)
for p in D['papers']:
    keymap={}
    for r in p['refs']:
        f=[a for a in r['a'] if a in FEAT]
        if f: keymap[r['key']]=(f,r)
    if not keymap: continue
    texs=glob.glob(f"{ROOT}/{p['id']}/build/**/*.tex",recursive=True)
    for tf in texs:
        t=open(tf,errors='ignore').read()
        if 'thebibliography' in t and t.count('\\bibitem')>5 and t.count('\\cite')<3: continue
        t=re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}','',t,flags=re.S)
        for m in CITE.finditer(t):
            keys=[k.strip() for k in m.group(1).split(',')]
            hit=[k for k in keys if k in keymap]
            if not hit: continue
            a=max(0,t.rfind('\n\n',0,m.start())); a=max(a,m.start()-700)
            b=t.find('\n\n',m.end()); b=min(b if b>0 else len(t),m.end()+500)
            seg=t[a:b]; pos=m.start()-a
            # sentence bounds
            left=seg[:pos]; right=seg[pos:]
            ls=max([left.rfind(x) for x in ('. ','.\n','? ','! ')]+[-1])
            rs=[right.find(x) for x in ('. ','.\n','.}')]; rs=[x for x in rs if x>=0]
            sent=clean(left[ls+1:]+right[:(min(rs)+1) if rs else len(right)])
            # include the previous sentence if very short
            if len(sent)<60:
                ls2=max([left[:ls].rfind(x) for x in ('. ','.\n')]+[-1]); sent=clean(left[ls2+1:]+right[:(min(rs)+1) if rs else len(right)])
            sent=sent[:700]
            for k in hit:
                f,r=keymap[k]
                pass
                for who in f:
                    out[who].append(dict(p=p['id'],k=k,s=sent,c=classify(sent),file=os.path.relpath(tf,f"{ROOT}/{p['id']}")))
# dedupe identical sentence per paper/person
for who in out:
    seen=set(); L=[]
    for x in out[who]:
        sig=(x['p'],x['s'])
        if sig in seen: continue
        seen.add(sig); L.append(x)
    out[who]=L

def lab(r):
    last=[n.split()[-1] if n else '?' for n in r['an']][:5]
    s='–'.join(last)+(' et al.' if len(r['an'])>5 else '')
    return (s or 'ref')+(' '+r['y'] if r['y'] else '')
for p in D['papers']:
    pass
L={p['id']:{r['key']:lab(r) for r in p['refs']} for p in D['papers']}
def sub(pid,s):
    def f(m):
        ks=[k for k in m.group(1).split(',')]
        if all(k in L[pid] for k in ks): return '['+'; '.join(L[pid][k] for k in ks)+']'
        return m.group(0)
    return re.sub(r'\[([^\[\]]+)\]',f,s)
for who in out:
    for x in out[who]: x['s']=sub(x['p'],x['s'])
json.dump(out,open(S+'/contexts.json','w'),ensure_ascii=False)
for who in ['Terence Tao','Hong Wang','Shaoming Guo','Yu Deng','John Pardon','Jacob Tsimerman']:
    L=out.get(who,[]); print(who,len(L),collections.Counter(x['c'] for x in L))
print(sum(len(v) for v in out.values()))
