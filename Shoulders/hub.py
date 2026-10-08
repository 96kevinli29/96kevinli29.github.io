"""Builds the hub pages (index.html, en/index.html) from the topic data. Run from anywhere."""
import os, sys, json, collections, html
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
from common import page

esc = html.escape

# ---- math: OpenAI Math Release (data embedded in math/index.html) -------------
_h = open(H + '/math/index.html', encoding='utf-8').read()
M, _ = json.JSONDecoder().raw_decode(_h[_h.index('{"gen"'):].replace('<\\/', '</'))
A = M['authors']
ent = collections.Counter()                     # reference entries per author (the default ranking)
for p in M['papers']:
    for r in p['r']:
        ent.update(r[0])
ent = collections.Counter({k: v for k, v in ent.items() if not A[k]['n'].startswith('init:')})
M_LAUR = sum(1 for k in ent if any(x in A[k] for x in ('fm', 'ab', 'wf')))
NP = len(M['papers'])
ROWS = [3, 5, 8, 11, 14]
TOP = ent.most_common(sum(ROWS))
# Always shown in the bottom row, whatever their rank.
PIN = ['Shaoming Guo']
PINNED = set()
FLOOR = TOP[-1][1]          # pinned names are drawn no smaller than the last ranked name
for n in PIN:
    k = next((i for i, a in enumerate(A) if a['n'] == n), None)
    if k is not None and k not in dict(TOP):
        TOP.append((k, ent[k]))
        PINNED.add(k)
ROWS[-1] += len(TOP) - sum(ROWS)

# ---- Navier–Stokes / Euler -----------------------------------------------------
NS = json.load(open(H + '/navier-stokes/scripts/refs.json', encoding='utf-8'))
NS_REFS = sum(len(p['refs']) for p in NS)
MILESTONES = [('Leonhard Euler', '欧拉', 1757), ('Claude Navier', '纳维', 1827), ('George Gabriel Stokes', '斯托克斯', 1845),
              ('Jean Leray', '勒雷', 1934), ('Elias M. Stein', '斯坦', 1970), ('Tosio Kato', '加藤敏夫', 1972),
              ('Caffarelli–Kohn–Nirenberg', '卡法雷利–科恩–尼伦伯格', 1982), ('Terence Tao', '陶哲轩', 2016)]


def pyramid(lang):
    mx = TOP[0][1]
    out, i = [], 0
    for n in ROWS:
        row = []
        for k, v in TOP[i:i + n]:
            a = A[k]
            nm = a.get('zh', a['n']) if lang == 'zh' else a['n']
            prize = [lab for x, lab in (('fm', 'Fields'), ('ab', 'Abel'), ('wf', 'Wolf')) if x in a]
            tip = (f"{a['n']} · {v} 条参考文献" if lang == 'zh' else f"{a['n']} · {v} reference entries")
            if prize:
                tip += ' · ' + ' / '.join(prize)
            fs = 0.8 + 1.3 * (max(v, FLOOR if k in PINNED else 0) / mx) ** 1.2
            row.append(f'<span class="g{" laur" if prize else ""}" style="--s:{fs:.2f}" title="{esc(tip)}">{esc(nm)}</span>')
        out.append('<div class="row">' + ''.join(row) + '</div>')
        i += n
    return '\n'.join(out)


def timeline(lang):
    items = [f'<span class="ms"><b>{esc(zh if lang == "zh" else en)}</b><i>{y}</i></span>' for en, zh, y in MILESTONES]
    return '<div class="tl">' + '<span class="arr">→</span>'.join(items) + '<span class="arr">→</span><span class="ms ai"><b>AI</b><i>2026</i></span></div>'


SEAFILL = 'https://huggingface.co/SeaFill2025'
SEAFILL_LOGO = 'https://cdn-avatars.huggingface.co/v1/production/uploads/68d669e121785bf79dec4f7a/HN8cIsNLsI8vrUUvv4sva.png'

CSS = '''
.team{display:inline-flex;align-items:center;gap:.6rem;margin-top:1.3rem;text-decoration:none;color:var(--ink)}
.team img{width:34px;height:34px;border-radius:8px;flex:none}
.team b{display:block;font:700 1.05rem/1.2 var(--f-display)}
.team small{display:block;font:.72rem var(--f-mono);color:var(--muted);letter-spacing:.04em}
.team:hover b{color:var(--use)}
.hero{padding-bottom:.5rem}
.hero h1{font-size:clamp(2.3rem,7vw,3.9rem)}
.manifesto{font:600 clamp(1.05rem,2.6vw,1.25rem)/1.6 var(--f-display);border-left:3px solid var(--gold);padding:.1rem 0 .1rem 1rem;margin:1.4rem 0 0;max-width:40rem}
.card{display:block;background:var(--sheet);border:1px solid var(--rule);border-top:4px solid var(--gold);border-radius:6px;padding:1.5rem 1.4rem;margin-top:1.1rem;text-decoration:none;color:inherit}
a.card:hover,a.card:focus-visible{border-color:var(--gold);outline:none}
.card h2{margin:.6rem 0 .4rem}
.card p{margin:.3rem 0;max-width:44rem}
.card .go{display:inline-block;margin-top:.9rem;font-weight:600;color:var(--use)}
.card .src{margin-top:.9rem;font:.78rem var(--f-mono);color:var(--muted)}
.card .stats{margin-top:1.1rem}
.tl{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .5rem;margin:1.1rem 0 .2rem}
.ms{display:inline-flex;flex-direction:column;align-items:center;line-height:1.2;padding:.3rem .55rem;border:1px solid var(--rule);border-radius:4px;background:var(--paper)}
.ms b{font:600 .95rem var(--f-display)}
.ms i{font:.68rem var(--f-mono);font-style:normal;color:var(--muted)}
.ms.ai{background:var(--ink);border-color:var(--ink)}.ms.ai b,.ms.ai i{color:var(--paper)}
.arr{color:var(--muted);font-size:.8rem}
.viz{margin:1.2rem 0 .4rem;text-align:center}
.aiblk{display:inline-block;font:600 .85rem var(--f-mono);letter-spacing:.08em;color:var(--paper);background:var(--ink);padding:.4rem 1rem;border-radius:4px 4px 0 0}
.aiblk small{display:block;font-size:.66rem;opacity:.75;letter-spacing:.04em}
.pyr{border-top:3px solid var(--ink);padding-top:.5rem}
.row{display:flex;flex-wrap:wrap;justify-content:center;align-items:baseline;gap:.1rem 1rem;padding:.28rem 0;margin:0 auto;border-bottom:1px solid var(--rule)}
.row:nth-child(1){max-width:26rem}.row:nth-child(2){max-width:34rem}.row:nth-child(3){max-width:42rem}
.g{font-size:calc(var(--s)*1rem);font-family:var(--f-display);font-weight:600;color:var(--ink);line-height:1.25;white-space:nowrap}
.g.laur{color:var(--gold);font-weight:900}
.legend{font:.74rem var(--f-mono);color:var(--muted);margin-top:.7rem}
.legend b{color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.75rem}
.soon{border:1px dashed var(--rule);border-radius:6px;padding:1rem;color:var(--muted)}
.soon b{display:block;color:var(--ink);font:600 1.1rem var(--f-display)}
@media (max-width:520px){.g{font-size:calc(var(--s)*.78rem)}.row{gap:.1rem .7rem}.card{padding:1.2rem 1rem}.ms b{font-size:.85rem}}
'''

T = {
 'zh': dict(
  lang='zh-CN', title='巨人之肩 · On Whose Shoulders', alt=('English', 'en/'), ns='navier-stokes/', math='math/',
  desc='向 AI 时代的人类科学家致敬：逐条记录 AI 前沿成果引用的人类科学家，按学科分开，随每一次突破更新。',
  eyebrow='巨人之肩 · On Whose Shoulders',
  h1='AI 的每一次突破，<br>都站在人类科学家的肩膀上',
  dek='当 AI 证明一条定理、攻克一个难题，它用到的概念、方法和工具，来自几代科学家的积累。我们逐条整理 AI 成果的参考文献，找出其中的每一个名字，按学科分开，随每一次突破更新。',
  manifesto='科学家是桥梁：一端连着几百年的人类知识，一端连着今天的 AI。这个项目向 AI 时代的人类科学家致敬。',
  team=('Sea-Fill 开源科学团队', '我们是 Sea-Fill，一个开源科学团队'),
  secMath='数学',
  nsTag='最新 · 2026 年 9 月 · 流体方程', nsH='从欧拉到 AI：Navier–Stokes 与 Euler 方程',
  nsP=f'OpenAI 公开两篇论文，给出三维 Navier–Stokes 方程与 Euler 方程有限时间爆破的构造，并附 Lean 形式化证明。两篇论文的 {NS_REFS} 条参考文献，从 1757 年的欧拉一直延续到 2026 年。',
  nsGo='进入流体方程专题 →',
  mTag='2026 年 10 月 · 数学全景', mH=f'OpenAI Math Release：{NP} 篇 AI 数学预印本',
  mP=f'OpenAI 公开了 {NP} 篇 AI 撰写的数学预印本及其 LaTeX 源码。下面的金字塔是被引用最多的数学家：顶端是 AI，托起它的是人类。',
  aiS=f'{NP} 篇 AI 数学预印本',
  legend='字号 = 参考文献条目数；<b>金色</b> = 菲尔兹 / 阿贝尔 / 沃尔夫奖得主。悬停查看详情。',
  st=[(NP, '篇 AI 数学预印本'), (M['works'], '部被引用的人类著作'), (len(A), '位人类作者'), (M_LAUR, '位获奖数学家被引用')],
  mGo='进入数学专题 →', src='数据来源',
  more='其他学科', soon='即将推出', subs=['物理', '化学', '生命科学', '计算机科学'],
  foot='引用不等于依赖；本项目不评判 AI 结果的正确性、原创性或归属。',
 ),
 'en': dict(
  lang='en', title='On Whose Shoulders · 巨人之肩', alt=('中文', '../'), ns='../navier-stokes/en/', math='../math/en/',
  desc='A tribute to the human scientists of the AI era: every human scientist cited by frontier AI results, field by field, updated with each breakthrough.',
  eyebrow='On Whose Shoulders · 巨人之肩',
  h1='Every AI breakthrough<br>stands on human shoulders',
  dek='When AI proves a theorem or settles an open problem, the ideas, methods and tools it uses come from generations of scientists. We go through the references of AI results entry by entry, find every name, and keep the record field by field, updated with each breakthrough.',
  manifesto='Scientists are the bridge: one end rests on centuries of human knowledge, the other on today’s AI. This project is a tribute to the human scientists of the AI era.',
  team=('Sea-Fill · open-source science team', 'We are Sea-Fill, an open-source science team'),
  secMath='Mathematics',
  nsTag='Latest · September 2026 · Fluid equations', nsH='From Euler to AI: Navier–Stokes and Euler',
  nsP=f'OpenAI released two papers constructing finite-time blowup for the three-dimensional Navier–Stokes and Euler equations, with Lean formalizations. Their {NS_REFS} references run from Euler in 1757 to 2026.',
  nsGo='Open the fluid equations page →',
  mTag='October 2026 · Mathematics overview', mH=f'OpenAI Math Release: {NP} AI-written math preprints',
  mP=f'OpenAI published {NP} AI-written mathematics preprints with their LaTeX sources. The pyramid shows the most-cited mathematicians: AI at the top, held up by people.',
  aiS=f'{NP} AI-written math preprints',
  legend='Size = reference entries; <b>gold</b> = Fields / Abel / Wolf laureate. Hover for details.',
  st=[(NP, 'AI-written math preprints'), (M['works'], 'human works cited'), (len(A), 'human authors'), (M_LAUR, 'laureates cited')],
  mGo='Open the mathematics index →', src='Source',
  more='Other fields', soon='Coming soon', subs=['Physics', 'Chemistry', 'Life sciences', 'Computer science'],
  foot='Citation is not dependence; this project does not judge the correctness, originality or attribution of AI results.',
 ),
}

for k, t in T.items():
    body = f'''<div class="top"><span>{t['eyebrow']}</span><a href="{t['alt'][1]}">{t['alt'][0]}</a></div>
<header class="hero">
<h1>{t['h1']}</h1>
<p class="dek">{t['dek']}</p>
<p class="manifesto">{t['manifesto']}</p>
<a class="team" href="{SEAFILL}"><img src="{SEAFILL_LOGO}" alt="" width="34" height="34"><span><b>{t['team'][0]}</b><small>{t['team'][1]}</small></span></a>
</header>

<section class="sec">
<span class="eyebrow">{t['secMath']}</span>

<a class="card" href="{t['ns']}">
<span class="tag">{t['nsTag']}</span>
<h2>{t['nsH']}</h2>
<p>{t['nsP']}</p>
{timeline(k)}
<span class="go">{t['nsGo']}</span>
</a>

<div class="card">
<span class="tag">{t['mTag']}</span>
<h2><a href="{t['math']}" style="color:inherit;text-decoration:none">{t['mH']}</a></h2>
<p>{t['mP']}</p>
<figure class="viz">
<div class="aiblk">AI · OpenAI Math Release<small>{t['aiS']}</small></div>
<div class="pyr">
{pyramid(k)}
</div>
<figcaption class="legend">{t['legend']}</figcaption>
</figure>
<div class="stats">{''.join(f'<div class="stat"><b>{n:,}</b><span>{esc(l)}</span></div>' for n, l in t['st'])}</div>
<a class="go" href="{t['math']}">{t['mGo']}</a>
<p class="src">{t['src']}: <a href="https://github.com/openai/math">github.com/openai/math</a> (Apache 2.0)</p>
</div>
</section>

<section class="sec">
<span class="eyebrow">{t['more']}</span>
<div class="grid">{''.join(f'<div class="soon"><b>{s}</b>{t["soon"]}</div>' for s in t['subs'])}</div>
</section>
<footer>{t['foot']} · <a href="{SEAFILL}">Sea-Fill</a> · <a href="https://github.com/96kevinli29/96kevinli29.github.io/tree/main/Shoulders">GitHub</a></footer>'''
    f = os.path.join(H, 'index.html' if k == 'zh' else 'en/index.html')
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(page(k, t['title'], t['desc'], CSS, body))
