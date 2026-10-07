import re,json,collections,os
S=os.path.dirname(os.path.abspath(__file__))
t=open(os.path.join(os.environ.get('OPENAI_MATH','openai-math'),'overview.tex')).read()
pos=[(m.start(),'sec',m.group(1)) for m in re.finditer(r'\\cataloguesection\{([^}]*)\}\{\d+\}',t)]
out={}; fam={}
sec=None
for m in re.finditer(r'\\cataloguesection\{([^}]*)\}\{\d+\}|\\resultentry\{(\d+)\}\{',t):
    if m.group(1): sec=m.group(1); continue
    num=m.group(2)
    # find end of entry: next \resultentry or \cataloguesection
    nxt=re.compile(r'\\resultentry\{|\\cataloguesection\{|\\end\{document\}').search(t,m.end())
    body=t[m.end():nxt.start()]
    ftitle=body.split('}{',1)[0]
    for u in re.findall(r'\\href\{https://github.com/openai/math/blob/main/preprints/([^}]+)\}\{',body):
        d=u.split('/')[0]; out[d]=dict(field=sec,family=num,family_title=ftitle,pdf=u)
json.dump(out,open(S+'/fields.json','w'),ensure_ascii=False,indent=0)
print(len(out)); print(collections.Counter(v['field'] for v in out.values()))
