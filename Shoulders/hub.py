"""Builds the hub pages (index.html, en/index.html). Run from anywhere."""
import os,json,collections,html
H=os.path.dirname(os.path.abspath(__file__))
_h=open(H+'/math/index.html',encoding='utf-8').read()
D,_=json.JSONDecoder().raw_decode(_h[_h.index('{"gen"'):].replace('<\\/','</'))
_c=collections.Counter()
for p in D['papers']:
    _c.update({i for r in p['r'] for i in r[0]})
A=D['authors']
LAUR=sum(1 for k in _c if any(x in A[k] for x in ('fm','ab','wf')))
ROWS=[3,5,8,11,14]
TOP=_c.most_common(sum(ROWS))
NP=len(D['papers'])
def stack(lang):
    mx=TOP[0][1]; out=[]; i=0
    for n in ROWS:
        row=[]
        for k,v in TOP[i:i+n]:
            a=A[k]; nm=a.get('zh',a['n']) if lang=='zh' else a['n']
            prize=[x for x,lab in (('fm','Fields'),('ab','Abel'),('wf','Wolf')) if x in a]
            cls='g laur' if prize else 'g'
            tip=(f"{a['n']} · 被 {v} 篇 AI 预印本引用" if lang=='zh' else f"{a['n']} · cited by {v} AI preprints")
            if prize: tip+=' · '+' / '.join(lab for x,lab in (('fm','Fields'),('ab','Abel'),('wf','Wolf')) if x in a)
            fs=0.8+1.3*(v/mx)**1.4
            row.append(f'<span class="{cls}" style="--s:{fs:.2f}" title="{html.escape(tip)}">{html.escape(nm)}</span>')
        out.append('<div class="row">'+''.join(row)+'</div>'); i+=n
    return '\n'.join(out)
CSS='''<style>
:root{--paper:#eef1f3;--sheet:#fbfcfc;--ink:#14212b;--muted:#5b6b76;--rule:#d3dadf;--gold:#a8791c;--gold-soft:#f3e7c9;--use:#1f6f68;
--f-display:"Noto Serif SC","Songti SC","STSong",Georgia,serif;--f-body:"IBM Plex Sans","PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#11181e;--sheet:#182129;--ink:#e4e9ec;--muted:#93a3ae;--rule:#2b3741;--gold:#e0b351;--gold-soft:#3a3020;--use:#5cc2b6;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#11181e;--sheet:#182129;--ink:#e4e9ec;--muted:#93a3ae;--rule:#2b3741;--gold:#e0b351;--gold-soft:#3a3020;--use:#5cc2b6;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 var(--f-body)}
main{max-width:52rem;margin:0 auto;padding:2.5rem 16px 4rem}
.top{display:flex;justify-content:space-between;align-items:center;font:500 .75rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.top a{color:var(--muted)}
h1{font:900 clamp(2.2rem,7vw,3.6rem)/1.1 var(--f-display);margin:2.2rem 0 .6rem}
.dek{font-size:1.1rem;color:var(--muted);max-width:38rem;margin:0 0 2.5rem}
.feature{display:block;background:var(--sheet);border:1px solid var(--rule);border-top:4px solid var(--gold);border-radius:6px;padding:1.6rem 1.5rem;text-decoration:none;color:inherit}
.feature:hover,.feature:focus-visible{border-color:var(--gold);outline:none}
.tag{display:inline-block;font:500 .72rem var(--f-mono);letter-spacing:.06em;text-transform:uppercase;background:var(--gold-soft);color:var(--gold);padding:.15rem .5rem;border-radius:3px}
.feature h2{font:900 1.8rem/1.2 var(--f-display);margin:.7rem 0 .4rem}
.feature p{margin:.3rem 0}
.src{margin-top:1rem;font:.85rem var(--f-mono);color:var(--muted)}
.src a{color:var(--use)}
.go{display:inline-block;margin-top:1rem;font-weight:600;color:var(--use)}
h3{font:500 .75rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:3rem 0 .8rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.75rem}
.soon{border:1px dashed var(--rule);border-radius:6px;padding:1rem;color:var(--muted)}
.soon b{display:block;color:var(--ink);font:600 1.1rem var(--f-display)}
.viz{margin:0 0 2.5rem;text-align:center}
.ai{display:inline-block;font:600 .9rem var(--f-mono);letter-spacing:.08em;color:var(--sheet);background:var(--ink);padding:.45rem 1rem;border-radius:4px 4px 0 0;position:relative}
.ai small{display:block;font-size:.68rem;opacity:.75;letter-spacing:.04em}
.pyr{border-top:3px solid var(--ink);padding-top:.6rem}
.row{display:flex;flex-wrap:wrap;justify-content:center;align-items:baseline;gap:.15rem 1rem;padding:.3rem 0;margin:0 auto;border-bottom:1px solid var(--rule)}
.row:nth-child(1){max-width:26rem}.row:nth-child(2){max-width:34rem}.row:nth-child(3){max-width:42rem}
.g{font-size:calc(var(--s)*1rem);font-family:var(--f-display);font-weight:600;color:var(--ink);line-height:1.25;white-space:nowrap;cursor:default}
.g.laur{color:var(--gold);font-weight:900}
.legend{font:.78rem var(--f-mono);color:var(--muted);margin-top:.8rem}
.legend b{color:var(--gold)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));gap:.75rem;margin:0 0 2.5rem}
.stat{border-left:3px solid var(--gold);padding:.2rem .8rem}
.stat b{display:block;font:900 1.9rem/1.1 var(--f-display)}
.stat span{font-size:.85rem;color:var(--muted)}
@media (max-width:520px){.g{font-size:calc(var(--s)*.78rem)}.row{gap:.1rem .7rem}}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--rule);font-size:.85rem;color:var(--muted)}
footer a{color:var(--muted)}
</style>'''
T={'zh':dict(lang='zh-CN',title='巨人之肩',alt=('English','en/'),math='math/',
 desc='AI 时代的科学突破，站在谁的肩膀上？按学科记录 AI 前沿成果所引用的人类科学家。',
 eyebrow='巨人之肩 · On Whose Shoulders',h1='AI 的每一项突破，<br>都站在人类科学家的肩膀上',
 dek='本项目在每一次 AI 科学突破后更新，按学科分开，记录这些成果引用了哪些人类科学家的工作，向他们的智慧与努力致敬。',
 tag='第 1 期 · 数学',h2='OpenAI Math Release：722 篇 AI 数学预印本',
 p='OpenAI 公开了 722 篇 AI 撰写的数学预印本及其 LaTeX 源码。我们解析了全部参考文献：哪些数学家被引用最多、哪些经典论文被反复使用，菲尔兹奖、阿贝尔奖、沃尔夫奖得主的工作如何成为基石。',
 src='数据来源',go='进入数学专题 →',more='其他学科',soon='即将推出',
 ai='AI · OpenAI Math Release',ais=f'{NP} 篇 AI 数学预印本',
 legend='字号 = 引用它的 AI 预印本篇数；<b>金色</b> = 菲尔兹 / 阿贝尔 / 沃尔夫奖得主。悬停查看详情。',
 st=[(NP,'篇 AI 数学预印本'),(D['works'],'部被引用的人类著作'),(len(A),'位人类作者'),(LAUR,'位菲尔兹 / 阿贝尔 / 沃尔夫奖得主被引用')],
 subs=['物理','化学','生命科学','计算机科学'],
 foot='引用不等于依赖；本项目不评判 AI 结果的原创性。'),
 'en':dict(lang='en',title='On Whose Shoulders',alt=('中文','../'),math='../math/en/',
 desc='Whose shoulders does AI-era science stand on? A field-by-field record of the human scientists cited by frontier AI results.',
 eyebrow='On Whose Shoulders · 巨人之肩',h1='Every AI breakthrough<br>stands on human shoulders',
 dek='Updated with each AI breakthrough in science, field by field: which human scientists’ work these results cite, in tribute to their insight and effort.',
 tag='Issue 1 · Mathematics',h2='OpenAI Math Release: 722 AI-written math preprints',
 p='OpenAI published 722 AI-written mathematics preprints with their LaTeX sources. We parsed every reference: which mathematicians are cited most, which classic papers recur, and how the work of Fields, Abel and Wolf laureates forms the foundations.',
 src='Source',go='Open the mathematics index →',more='Other fields',soon='Coming soon',
 ai='AI · OpenAI Math Release',ais=f'{NP} AI-written math preprints',
 legend='Size = number of AI preprints citing them; <b>gold</b> = Fields / Abel / Wolf laureate. Hover for details.',
 st=[(NP,'AI-written math preprints'),(D['works'],'human works cited'),(len(A),'human authors'),(LAUR,'Fields / Abel / Wolf laureates cited')],
 subs=['Physics','Chemistry','Life sciences','Computer science'],
 foot='Citation is not dependence; this project does not judge the originality of AI results.')}
for k,t in T.items():
    soon=''.join(f'<div class="soon"><b>{s}</b>{t["soon"]}</div>' for s in t['subs'])
    h=f'''<!doctype html>
<html lang="{t['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t['title']}</title>
<meta name="description" content="{t['desc']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}
</head>
<body>
<main>
<div class="top"><span>{t['eyebrow']}</span><a href="{t['alt'][1]}">{t['alt'][0]}</a></div>
<h1>{t['h1']}</h1>
<p class="dek">{t['dek']}</p>
<figure class="viz">
<div class="ai">{t['ai']}<small>{t['ais']}</small></div>
<div class="pyr">
{stack(k)}
</div>
<figcaption class="legend">{t['legend']}</figcaption>
</figure>
<div class="stats">{''.join(f'<div class="stat"><b>{n:,}</b><span>{l}</span></div>' for n,l in t['st'])}</div>
<a class="feature" href="{t['math']}">
<span class="tag">{t['tag']}</span>
<h2>{t['h2']}</h2>
<p>{t['p']}</p>
<span class="go">{t['go']}</span>
</a>
<p class="src">{t['src']}: <a href="https://github.com/openai/math">github.com/openai/math</a> (Apache 2.0)</p>
<h3>{t['more']}</h3>
<div class="grid">{soon}</div>
<footer>{t['foot']} · <a href="https://github.com/96kevinli29/96kevinli29.github.io/tree/main/Shoulders">GitHub</a></footer>
</main>
</body>
</html>
'''
    p=os.path.join(H,'index.html' if k=='zh' else 'en/index.html')
    os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,'w').write(h)
