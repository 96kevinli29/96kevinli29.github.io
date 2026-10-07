import json,os,collections,re
S=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(S+'/data_stage1.json')); C=json.load(open(S+'/contexts.json'))
FM={}
for line in open(S+'/fields_medal.txt'):
    y,ns=line.strip().split('|')
    for n in ns.split(';'): FM[n]=int(y)
ZH={'Shiing-Shen Chern':'陈省身','Israel Gelfand':'盖尔范德','Andrey Kolmogorov':'柯尔莫哥洛夫','André Weil':'韦伊','Jean Leray':'勒雷','Henri Cartan':'嘉当','Oscar Zariski':'扎里斯基','Hassler Whitney':'惠特尼','Paul Erdős':'埃尔德什','Friedrich Hirzebruch':'希策布鲁赫','Alberto Calderón':'卡尔德龙','Ennio De Giorgi':'德乔治','Jürgen Moser':'莫泽','Elias M. Stein':'斯坦','Raoul Bott':'博特','Vladimir Arnold':'阿诺尔德','Saharon Shelah':'谢拉','Peter Sarnak':'萨纳克','James Arthur':'亚瑟','Richard Schoen':'舍恩','George Lusztig':'卢斯蒂格','Ingrid Daubechies':'多贝西','Noga Alon':'阿隆','Adi Shamir':'沙米尔','David Kazhdan':'卡兹丹','Joseph Bernstein':'伯恩斯坦','Simon Donaldson':'唐纳森','Yakov Eliashberg':'埃利亚什伯格','Alexander Beilinson':'贝林森','Gregory F. Lawler':'劳勒','Jean-François Le Gall':'勒加尔','Phillip A. Griffiths':'格里菲斯','Michael Artin':'阿廷','Isadore Singer':'辛格','Peter Lax':'拉克斯','Lennart Carleson':'卡尔松','S. R. Srinivasa Varadhan':'瓦拉德汉','Jacques Tits':'蒂茨','Mikhail Gromov':'格罗莫夫','John Tate':'泰特','Endre Szemerédi':'塞迈雷迪','Yakov Sinai':'西奈','John Nash':'纳什','Louis Nirenberg':'尼伦伯格','Andrew Wiles':'怀尔斯','Yves Meyer':'迈耶','Robert Langlands':'朗兰兹','Karen Uhlenbeck':'乌伦贝克','Hillel Furstenberg':'弗斯滕伯格','László Lovász':'洛瓦斯','Avi Wigderson':'维格森','Dennis Sullivan':'沙利文','Luis Caffarelli':'卡法雷利','Michel Talagrand':'塔拉格朗','Masaki Kashiwara':'柏原正树','Terence Tao':'陶哲轩','Hong Wang':'王虹','Shaoming Guo':'郭少明','Shing-Tung Yau':'丘成桐','Yu Deng':'邓煜','Bao Châu Ngô':'吴宝珠','Jean Bourgain':'布尔甘','Jacob Tsimerman':'齐默曼','John Pardon':'帕登','Peter Scholze':'舒尔茨','Alexander Grothendieck':'格罗滕迪克','Jean-Pierre Serre':'塞尔','Pierre Deligne':'德利涅','Caucher Birkar':'比尔卡尔','Hugo Duminil-Copin':'迪米尼尔-科潘','Stanislav Smirnov':'斯米尔诺夫','Charles Fefferman':'费弗曼','Maryna Viazovska':'维亚佐夫斯卡','June Huh':'许埈珥','Alessio Figalli':'菲加利','Akshay Venkatesh':'文卡特什','Martin Hairer':'海尔','Artur Avila':'阿维拉','Manjul Bhargava':'巴尔加瓦','Maryam Mirzakhani':'米尔扎哈尼','Cédric Villani':'维拉尼','Elon Lindenstrauss':'林登施特劳斯','Grigori Perelman':'佩雷尔曼','Andrei Okounkov':'奥昆科夫','Wendelin Werner':'维尔纳','Timothy Gowers':'高尔斯','Maxim Kontsevich':'孔采维奇','Edward Witten':'威滕','Simon Donaldson':'唐纳森','Michael Atiyah':'阿蒂亚','John Milnor':'米尔诺','James Maynard':'梅纳德','Shigefumi Mori':'森重文','Kunihiko Kodaira':'小平邦彦','Heisuke Hironaka':'广中平祐','William Thurston':'瑟斯顿','Alain Connes':'孔涅','Gerd Faltings':'法尔廷斯','Vladimir Drinfeld':'德林费尔德','Lars Hörmander':'赫尔曼德','Enrico Bombieri':'邦别里','David Mumford':'芒福德','Daniel Quillen':'奎伦','Vladimir Voevodsky':'沃埃沃德斯基','Laurent Lafforgue':'拉福格','Curtis McMullen':'麦克马伦','Richard Borcherds':'博切兹','Pierre-Louis Lions':'利翁斯','Efim Zelmanov':'泽尔曼诺夫','Jean-Christophe Yoccoz':'约科兹','Vaughan Jones':'琼斯','Michael Freedman':'弗里德曼','Grigory Margulis':'马尔古利斯','Stephen Smale':'斯梅尔','Paul Cohen':'科恩','Lars Ahlfors':'阿尔福斯','Jesse Douglas':'道格拉斯','Laurent Schwartz':'施瓦茨','Atle Selberg':'塞尔伯格','Klaus Roth':'罗斯','René Thom':'托姆','Alan Baker':'贝克','Sergei Novikov':'诺维科夫','John G. Thompson':'汤普森'}
import unicodedata
SUP=str.maketrans('0123456789','⁰¹²³⁴⁵⁶⁷⁸⁹')
def texfix(s):
    if not s: return s
    acc={'"':'\u0308',"'":'\u0301','`':'\u0300','^':'\u0302','~':'\u0303','v':'\u030c','c':'\u0327','H':'\u030b','u':'\u0306'}
    s=re.sub(r'\\([\"\'`^~vcHu])\s*\{?([A-Za-z])\}?',lambda m:m.group(2)+acc[m.group(1)],s)
    s=re.sub(r'\^\{?(\d)\}?',lambda m:m.group(1).translate(SUP),s)
    s=re.sub(r'\$([^$]{0,60})\$',lambda m:m.group(1),s)
    s=s.replace('\\(','').replace('\\)','')
    s=re.sub(r'\\(mathbb|mathrm|mathcal|mathbf|operatorname|text|emph)\s*\{([^{}]*)\}',r'\2',s)
    s=re.sub(r'\\(mathbb|mathrm|mathcal|mathbf)\s*([A-Za-z])',r'\2',s)
    s=s.replace('\\ell','ℓ').replace('\\infty','∞').replace('\\le','≤').replace('\\ge','≥').replace('\\times','×').replace('\\to','→').replace('\\pi','π').replace('\\varepsilon','ε').replace('\\epsilon','ε').replace('\\delta','δ').replace('\\lambda','λ').replace('\\alpha','α').replace('\\beta','β')
    s=s.replace('{','').replace('}','')
    return unicodedata.normalize('NFC',s)
WF={}
for line in open(S+'/wolf.txt'):
    y,ns=line.strip().split('|')
    for n in ns.split(';'): WF.setdefault(n,int(y))
AB={}
for line in open(S+'/abel.txt'):
    y,ns=line.strip().split('|')
    for n in ns.split(';'): AB[n]=int(y)
FEAT=['Terence Tao','Hong Wang','Shaoming Guo','Yu Deng','John Pardon','Jacob Tsimerman']
# author index
cnt=collections.defaultdict(set)
for p in D['papers']:
    for r in p['refs']:
        for a in r['a']:
            if a and a!='OpenAI': cnt[a].add(p['id'])
keys=sorted(cnt,key=lambda k:-len(cnt[k]))
idx={k:i for i,k in enumerate(keys)}
CC={}
for line in open(S+'/countries.txt'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    n,c=line.split('|'); CC[n]=c
AF={}
for line in open(S+'/affil.txt',encoding='utf-8'):
    line=line.rstrip('\n')
    if not line or line.startswith('#'): continue
    n,zh,c,az,ae=line.split('|'); AF[n]=(zh,c,az,ae)
CC.pop('Juanyong Wang',None)
CIT=json.load(open(S+'/cites.json'))
authors=[]
for k in keys:
    n=D['names'].get(k,k)
    if n.startswith('init:'): n=k
    a={'n':n}
    if k in FM: a['fm']=FM[k]
    if k in ZH: a['zh']=ZH[k]
    if k in AB: a['ab']=AB[k]
    if k in WF: a['wf']=WF[k]
    if n in CC: a['c']=CC[n]
    if n in AF:
        zh,c,az,ae=AF[n]; a['c']=c; a['af']=[az,ae]
        if any(x in az for x in ['清华','北京','中国科学院','浙江','西湖','上海','复旦','中国科学技术','南开']): a['ml']=1
        if zh and 'zh' not in a: a['zh']=zh
    authors.append(a)
fields=sorted({p['field'] for p in D['papers']})
FZH={'Probability and statistical mechanics':'概率与统计力学','Algebraic and complex geometry':'代数与复几何','Theoretical computer science':'理论计算机科学','Mathematical physics':'数学物理','Number theory':'数论','Combinatorics':'组合','Differential geometry':'微分几何','Operator algebras':'算子代数','Convex and metric geometry':'凸几何与度量几何','Algebra':'代数','Partial differential equations':'偏微分方程','Real and complex analysis':'实分析与复分析','Topology':'拓扑','Group theory':'群论','Dynamical systems and ergodic theory':'动力系统与遍历论','Functional analysis':'泛函分析','Mathematical logic':'数理逻辑'}
pidx={p['id']:i for i,p in enumerate(D['papers'])}
papers=[]
for p in D['papers']:
    R=[]
    self_=0
    for r in p['refs']:
        if 'OpenAI' in r['a']: self_+=1
        R.append([[idx[a] for a in r['a'] if a in idx],texfix(r['t']),r['y'],r['l'],r['v'],CIT.get(p['id'],{}).get(r['key'],0)])
    papers.append(dict(t=texfix(p['title']),d=p['date'],f=fields.index(p['field']),fam=p['family'],ft=texfix(p['family_title']),u=p['pdf'],ha=1 if p['tags'] else 0,r=R,o=self_))
ctx={}
for who,L in C.items():
    if who not in idx: continue
    ctx[idx[who]]=[[pidx[x['p']],texfix(x['s']),{'use':2,'background':1,'mention':0}[x['c']]] for x in L]
works={}
def wkey(r):
    if r['l'] and ('doi.org' in r['l'] or 'arxiv.org' in r['l']):
        return re.sub(r'v\d+$','',r['l'].lower().split('doi.org/')[-1].split('abs/')[-1]).strip('/')
    k=re.sub(r'[^a-z0-9]','',(r['t'] or '').lower())[:60]
    return k or None
# title-based alias so DOI and non-DOI copies of the same work merge
tkey={}
for p_ in D['papers']:
    for r in p_['refs']:
        if not [a for a in r['a'] if a and a!='OpenAI']: continue
        k=wkey(r)
        if not k: continue
        tk=re.sub(r'[^a-z0-9]','',(r['t'] or '').lower())[:50]
        if len(tk)>=20:
            if tk in tkey: k=tkey[tk]
            else: tkey[tk]=k
        w=works.setdefault(k,dict(t=r['t'],a=[a for a in r['a'] if a and a!='OpenAI'],y=r['y'],l=r['l'],ps=set()))
        if not w['l'] and r['l']: w['l']=r['l']
        if len(r['t'] or '')>len(w['t'] or '') and len(r['t'])<200: w['t']=r['t']
        w['ps'].add(pidx[p_['id']])
def tclean(t):
    t=re.sub(r'^https?://\S*?(?=[A-Z][a-z])','',t or '')
    t=re.sub(r',\s*[A-Z][a-z]?\.?$','',t).strip(' ,.')
    return t
allw=sorted(works.values(),key=lambda w:-len(w['ps']))
chosen=allw[:110]
fieldsOf=lambda w:collections.Counter(papers[i]['f'] for i in w['ps'])
for fk in range(len(fields)):
    cand=[w for w in allw if any(papers[i]['f']==fk for i in w['ps'])]
    cand.sort(key=lambda w:-sum(1 for i in w['ps'] if papers[i]['f']==fk))
    for w in cand[:6]:
        if w not in chosen and len(w['ps'])>=3: chosen.append(w)
hacand=sorted([w for w in allw if sum(1 for i in w['ps'] if papers[i]['ha'])>=3],key=lambda w:-sum(1 for i in w['ps'] if papers[i]['ha']))
for w in hacand[:14]:
    if w not in chosen: chosen.append(w)
W=[[texfix(tclean(w['t'])),[idx[a] for a in w['a'] if a in idx],w['y'],w['l'],sorted(w['ps'])] for w in chosen]
import datetime
UPD=[l.rstrip('\n').split('|',2) for l in open(S+'/updates.txt',encoding='utf-8') if l.strip() and not l.startswith('#')]
out=dict(gen=datetime.date.today().isoformat(),upd=UPD,works=len(works),W=W,fields=[[f,FZH.get(f,f)] for f in fields],authors=authors,papers=papers,ctx=ctx)
s=json.dumps(out,ensure_ascii=False,separators=(',',':'))
import hashlib
_o=dict(out); _o.pop('gen',None); _o.pop('upd',None)
open(S+'/data.sha','w').write(hashlib.sha256(json.dumps(_o,ensure_ascii=False,sort_keys=True).encode()).hexdigest()+'\n')
open(S+'/data.json','w').write(s); print(len(s)/1e6,'MB',len(authors),'authors')
