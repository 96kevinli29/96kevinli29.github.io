# count in-text \cite occurrences for every reference key in every paper
import json,re,glob,os,collections
S=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(os.environ.get('OPENAI_MATH','openai-math'),'preprints')
D=json.load(open(S+'/data_stage1.json'))
CITE=re.compile(r'\\(?:[Cc]ite[a-zA-Z]*|parencite|textcite|autocite|footcite|Citet|Citep)\*?\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}')
out={}
for p in D['papers']:
    keys={r['key'] for r in p['refs']}; c=collections.Counter()
    for tf in glob.glob(f"{ROOT}/{p['id']}/build/**/*.tex",recursive=True):
        t=open(tf,errors='ignore').read()
        t=re.sub(r'(?<!\\)%.*','',t)
        t=re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}','',t,flags=re.S)
        for m in CITE.finditer(t):
            for k in m.group(1).split(','):
                k=k.strip()
                if k in keys: c[k]+=1
    out[p['id']]=dict(c)
json.dump(out,open(S+'/cites.json','w'))
tot=sum(len(p['refs']) for p in D['papers']); zero=sum(1 for p in D['papers'] for r in p['refs'] if not out[p['id']].get(r['key']))
print('refs',tot,'never cited in text',zero,'total in-text',sum(sum(v.values()) for v in out.values()))
