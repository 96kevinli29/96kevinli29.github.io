"""Builds navier-stokes/index.html (English) and navier-stokes/zh/index.html from refs.json."""
import os, sys, json, html, re
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
sys.path.insert(0, ROOT)
from common import page, laureates, person_key, chips

D = json.load(open(S + '/refs.json', encoding='utf-8'))
LAUR = laureates(ROOT + '/math/scripts')
ZH = {'Leonhard Euler': '欧拉', 'Claude Louis Marie Henri Navier': '纳维', 'George Gabriel Stokes': '斯托克斯',
      'Jean Leray': '勒雷', 'Tosio Kato': '加藤敏夫', 'Terence Tao': '陶哲轩', 'Elias M. Stein': '斯坦',
      'Charles L. Fefferman': '费弗曼', 'Jean Bourgain': '布尔甘', 'Luis Caffarelli': '卡法雷利',
      'Louis Nirenberg': '尼伦伯格', 'Thomas Y. Hou': '侯一钊'}
MILESTONES = [('Euler', '欧拉', 1757), ('Navier', '纳维', 1827), ('Stokes', '斯托克斯', 1845), ('Leray', '勒雷', 1934),
              ('Stein', '斯坦', 1970), ('Kato', '加藤敏夫', 1972), ('Caffarelli–Kohn–Nirenberg', '卡法雷利–科恩–尼伦伯格', 1982),
              ('Beale–Kato–Majda', 'Beale–加藤–Majda', 1984), ('Fefferman', '费弗曼', 2000), ('Tao', '陶哲轩', 2016)]
SHORT = {'ns': 'Navier–Stokes', 'euler': 'Euler'}
esc = html.escape


def tex(s):
    """Escape a title and turn ^{..}/^x and _{..}/_x into <sup>/<sub>."""
    s = esc(s)
    s = re.sub(r'\^\{([^}]*)\}|\^(\S)', lambda m: f'<sup>{m.group(1) or m.group(2)}</sup>', s)
    return re.sub(r'_\{([^}]*)\}|_(\w)', lambda m: f'<sub>{m.group(1) or m.group(2)}</sub>', s)

# ---- unique works and people -------------------------------------------------
works = {}
for p in D:
    for r in p['refs']:
        k = r['u'] or re.sub(r'\W', '', r['t'].lower())
        w = works.setdefault(k, dict(a=r['a'], t=r['t'], y=r['y'], u=r['u'], raw=r['raw'], by={}))
        w['by'][p['id']] = r
works = sorted(works.values(), key=lambda w: (-int(w['y'] or 0), w['a'][0] if w['a'] else ''))

people = {}
for p in D:
    for r in p['refs']:
        for a in r['a']:
            k = person_key(a)
            q = people.setdefault(k, dict(n=a, r=0, t=0, p=set()))
            if len(a) > len(q['n']):
                q['n'] = a
            q['r'] += 1
            q['t'] += len(r['c'])
            q['p'].add(p['id'])
for k, q in people.items():
    q['prize'] = LAUR.get(k, {})
NREF = sum(len(p['refs']) for p in D)
YEARS = [int(w['y']) for w in works if w['y']]
SPAN = 2026 - min(YEARS)
PAGES = {p['id']: p['pages'] for p in D}

T = {
 'zh': dict(
  title='从欧拉到 AI · 巨人之肩',
  desc='OpenAI 的 Navier–Stokes 与 Euler 方程有限时间爆破论文引用了哪些人类科学家：从 1757 年的欧拉到 2026 年。',
  back='← 巨人之肩', alt=('English', '../'), eyebrow='数学 · 流体方程 · 2026 年 9 月',
  h1=f'从欧拉到 AI：<br>流体方程的 {SPAN} 年',
  dek=[f'2026 年 9 月 8 日，OpenAI 公开两篇论文，给出三维不可压 <b>Navier–Stokes 方程</b>与 <b>Euler 方程</b>光滑解在有限时间内爆破的构造，并附 Lean 4 形式化证明。Navier–Stokes 一篇对应克雷数学研究所千禧年大奖难题中的情形 (C) 与 (D)。',
       f'这一步走在 {SPAN} 年的积累之上：从 1757 年欧拉写下流体运动方程，到纳维、斯托克斯、勒雷，再到今天仍在推进这一问题的数学家。两篇论文共列出 {NREF} 条参考文献。我们把它们逐条找出来，记下每一位被引用的人。'],
  links=[('OpenAI 博客', 'https://openai.com/index/navier-stokes-solution/'), ('Navier–Stokes 论文', D[0]['url']),
         ('Euler 论文', D[1]['url']), ('Lean 形式化', 'https://github.com/openai/NavierStokesAndEuler')],
  st=[(2, f'篇 AI 论文（{PAGES["ns"]} + {PAGES["euler"]} 页）'), (NREF, '条参考文献'), (len(works), '部被引用的人类著作'),
      (len(people), '位被引用的科学家'), (SPAN, f'年跨度（{min(YEARS)}–2026）')],
  colH='向下追溯', colP='最上方是 AI 的结果，往下是它引用的人类著作，按年份一路回到 1757 年。金色标签为菲尔兹奖、阿贝尔奖、沃尔夫奖得主；点“正文怎样引用”可看论文原句。',
  ai='AI · OpenAI', aiS='Navier–Stokes 与 Euler 方程有限时间爆破',
  how=lambda n: f'正文怎样引用（{n}）', pg='第 {} 页', citedIn='被引于',
  eras=[(2020, '2020 年代'), (2000, '2000–2019'), (1980, '1980–1999'), (1900, '20 世纪'), (0, '18–19 世纪：方程的诞生')],
  rankH='被引用的科学家', rankP='默认按参考文献条目数排名：一篇论文列出某人的一部著作计一次。',
  metL='排名依据', mR='参考文献条目', mT='正文引用', mP='引用论文数', more='更多排名方式', less='收起',
  showAll=lambda n: f'显示全部 {n} 位', showLess='收起',
  refH='参考文献原文', refP='按两篇论文分列，保留原始编号；右侧数字为该条在正文中被引用的次数。',
  foot='由 <a href="https://huggingface.co/SeaFill2025">Sea-Fill 开源科学团队</a>制作。参考文献与正文原句从论文 PDF 中解析。引用不等于依赖；本页不评判结果的正确性、原创性或归属。',
 ),
 'en': dict(
  title='From Euler to AI · On Whose Shoulders',
  desc='Which human scientists do OpenAI’s finite-time blowup papers for Navier–Stokes and Euler cite? From Euler in 1757 to 2026.',
  back='← On Whose Shoulders', alt=('中文', 'zh/'), eyebrow='Mathematics · Fluid equations · September 2026',
  h1=f'From Euler to AI:<br>{SPAN} years of fluid equations',
  dek=[f'On 8 September 2026 OpenAI released two papers constructing smooth solutions of the three-dimensional incompressible <b>Navier–Stokes</b> and <b>Euler equations</b> that blow up in finite time, with Lean 4 formalizations. The Navier–Stokes paper addresses alternatives (C) and (D) of the Clay Mathematics Institute’s Millennium Prize Problem.',
       f'That step rests on {SPAN} years of human work: from Euler writing down the equations of fluid motion in 1757, through Navier, Stokes and Leray, to the mathematicians still pushing on the problem today. Together the two papers list {NREF} references. We traced every one of them and the people behind it.'],
  links=[('OpenAI blog post', 'https://openai.com/index/navier-stokes-solution/'), ('Navier–Stokes paper', D[0]['url']),
         ('Euler paper', D[1]['url']), ('Lean formalization', 'https://github.com/openai/NavierStokesAndEuler')],
  st=[(2, f'AI papers ({PAGES["ns"]} + {PAGES["euler"]} pages)'), (NREF, 'reference entries'), (len(works), 'human works cited'),
      (len(people), 'scientists cited'), (SPAN, f'years spanned ({min(YEARS)}–2026)')],
  colH='Tracing back', colP='The AI result sits at the top; below it are the human works it cites, by year, all the way back to 1757. Gold tags mark Fields, Abel and Wolf laureates; open “How it is cited” for the sentences in the paper.',
  ai='AI · OpenAI', aiS='Finite-time blowup for Navier–Stokes and Euler',
  how=lambda n: f'How it is cited ({n})', pg='p. {}', citedIn='Cited in',
  eras=[(2020, '2020s'), (2000, '2000–2019'), (1980, '1980–1999'), (1900, '20th century'), (0, '18th–19th century: the equations are born')],
  rankH='Scientists cited', rankP='Ranked by reference entries by default: a paper listing one of their works counts once.',
  metL='Rank by', mR='Reference entries', mT='In-text citations', mP='Citing papers', more='More ranking options', less='Fewer options',
  showAll=lambda n: f'Show all {n}', showLess='Show fewer',
  refH='Reference lists', refP='One list per paper, with the original numbering; the number on the right is how often the entry is cited in the text.',
  foot='Made by <a href="https://huggingface.co/SeaFill2025">Sea-Fill</a>, an open-source science team. References and in-text sentences are parsed from the paper PDFs. Citation is not dependence; this page does not judge the correctness, originality or attribution of the results.',
 ),
}

CSS = '''
.tl{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .5rem;margin:1.4rem 0 .4rem}
.ms{display:inline-flex;flex-direction:column;align-items:center;line-height:1.2;padding:.3rem .55rem;border:1px solid var(--rule);border-radius:4px;background:var(--sheet)}
.ms b{font:600 .95rem var(--f-display)}.ms i{font:.68rem var(--f-mono);font-style:normal;color:var(--muted)}
.ms.now{background:var(--ink);border-color:var(--ink)}.ms.now b,.ms.now i{color:var(--paper)}
.arr{color:var(--muted);font-size:.8rem}
.links{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.2rem 0 0}
.links a{font:.78rem var(--f-mono);color:var(--ink);text-decoration:none;border:1px solid var(--rule);background:var(--sheet);border-radius:4px;padding:.35rem .7rem}
.links a:hover{border-color:var(--use);color:var(--use)}
.lead{color:var(--muted);max-width:42rem;margin:0 0 1.2rem}
.col{position:relative;margin:0;padding:0;list-style:none}
.col:before{content:"";position:absolute;left:4.6rem;top:2.6rem;bottom:1rem;width:2px;background:var(--rule)}
.ai{position:relative;display:flex;align-items:center;gap:1rem;background:var(--ink);color:var(--paper);border-radius:6px;padding:.8rem 1.1rem;margin-bottom:1.2rem}
.ai b{font:600 .95rem var(--f-mono);letter-spacing:.06em}
.ai span{font-size:.88rem;opacity:.8}
.ai em{font:600 .8rem var(--f-mono);font-style:normal;margin-left:auto;opacity:.75}
.era{font:500 .72rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.6rem 0 .4rem 6rem;position:relative}
.w{position:relative;display:grid;grid-template-columns:4.6rem 1fr;gap:0 1.4rem;padding:.55rem 0}
.w:before{content:"";position:absolute;left:calc(4.6rem - 4px);top:1.05rem;width:10px;height:10px;border-radius:50%;background:var(--paper);border:2px solid var(--muted)}
.w.laur:before{border-color:var(--gold);background:var(--gold)}
.yr{font:500 .9rem var(--f-mono);color:var(--muted);text-align:right;padding-right:.6rem;padding-top:.2rem}
.who{font:600 1.08rem/1.4 var(--f-display)}
.who .zh{font-weight:900}
.who .lat{font:400 .8rem var(--f-body);color:var(--muted);margin-left:.25rem}
.w.classic .who{font-size:1.5rem}.w.classic .yr{font-size:1.15rem;color:var(--ink);font-weight:600}
.w.laur .who .nm.g{color:var(--gold)}
.ti{font-size:.92rem;color:var(--muted);font-style:italic;margin:.1rem 0 .2rem}
.ti a{color:inherit;text-decoration-color:var(--rule)}
.by{font:.68rem var(--f-mono);color:var(--muted);letter-spacing:.04em}
.by i{font-style:normal;border:1px solid var(--rule);border-radius:3px;padding:0 .35rem;margin-left:.3rem}
details{margin-top:.25rem}
summary{cursor:pointer;font-size:.82rem;color:var(--use);list-style:none}
summary::-webkit-details-marker{display:none}
summary:before{content:"＋ "}details[open] summary:before{content:"－ "}
blockquote{margin:.4rem 0 .2rem;padding:.35rem .8rem;border-left:3px solid var(--use-soft);font-size:.9rem;color:var(--ink);background:var(--sheet)}
blockquote small{display:block;font:.7rem var(--f-mono);color:var(--muted);margin-top:.15rem}
.metsw{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;margin:.2rem 0 .9rem}
.metsw button{font:.8rem var(--f-body);border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:999px;padding:.2rem .75rem;cursor:pointer}
.metsw button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.metsw .more{border-style:dashed;color:var(--muted)}
.rank{list-style:none;margin:0;padding:0;counter-reset:r}
.rank li{display:grid;grid-template-columns:2rem 1fr auto;align-items:baseline;gap:.6rem;padding:.42rem 0;border-bottom:1px solid var(--rule)}
.rank li:before{counter-increment:r;content:counter(r);font:.8rem var(--f-mono);color:var(--muted);text-align:right}
.rank .nm{font:600 1rem var(--f-display)}
.rank .nm small{font:400 .78rem var(--f-body);color:var(--muted);margin-left:.3rem}
.rank .ct{font:600 .95rem var(--f-mono)}
.rank li.hide{display:none}
.toggle{margin-top:.7rem;font:.85rem var(--f-body);background:none;border:0;color:var(--use);cursor:pointer;padding:0}
.refs{display:grid;grid-template-columns:repeat(auto-fit,minmax(20rem,1fr));gap:1.5rem}
.refs h3{font:600 1.05rem var(--f-display);margin:0 0 .5rem}
.refs ol{margin:0;padding-left:1.8rem;font-size:.84rem;line-height:1.55}
.refs li{margin:.35rem 0;color:var(--muted)}
.refs li b{color:var(--ink);font-weight:500}
.refs .n{float:right;font:.72rem var(--f-mono);color:var(--use);margin-left:.5rem}
@media (max-width:560px){
 .col:before{left:3.3rem}.w{grid-template-columns:3.3rem 1fr;gap:0 1rem}.w:before{left:calc(3.3rem - 4px)}
 .era{margin-left:4.3rem}.yr{font-size:.8rem;padding-right:.5rem}.w.classic .who{font-size:1.25rem}.w.classic .yr{font-size:.95rem}
 .ai{flex-wrap:wrap;gap:.2rem .8rem}.ai em{margin-left:0}
}
'''

JS = '''<script>
(function(){
 var L=document.querySelector('.rank'),sw=document.querySelector('.metsw'),tg=document.querySelector('.toggle');
 var M=JSON.parse(sw.dataset.m),met='r',more=false,all=false,TOP=20;
 function draw(){
  var rows=[].slice.call(L.children);
  rows.sort(function(a,b){return b.dataset[met]-a.dataset[met]||b.dataset.r-a.dataset.r||b.dataset.t-a.dataset.t});
  rows.forEach(function(li,i){L.appendChild(li);li.querySelector('.ct').textContent=li.dataset[met];li.classList.toggle('hide',!all&&i>=TOP)});
  var ks=more?['r','t','p']:[met];
  sw.innerHTML='<span class="eyebrow">'+M.l+'</span>'+ks.map(function(k){return '<button type="button" data-k="'+k+'" aria-pressed="'+(k===met)+'">'+M[k]+'</button>'}).join('')+'<button type="button" class="more">'+(more?M.less:M.more)+'</button>';
  tg.textContent=all?tg.dataset.less:tg.dataset.all;
 }
 sw.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;if(b.classList.contains('more')){more=!more;if(!more)met='r'}else met=b.dataset.k;draw()});
 tg.addEventListener('click',function(){all=!all;draw()});
 draw();
})();
</script>'''


def name_html(a, lang, laur):
    zh = ZH.get(a) if lang == 'zh' else None
    cls = 'nm g' if laur else 'nm'
    if zh:
        return f'<span class="{cls}"><span class="zh">{esc(zh)}</span><span class="lat">{esc(a)}</span></span>'
    return f'<span class="{cls}">{esc(a)}</span>'


def build(lang):
    t = T[lang]
    out = [f'<div class="top"><a href="{"../../zh/" if lang == "zh" else "../"}">{t["back"]}</a><a href="{t["alt"][1]}">{t["alt"][0]}</a></div>',
           f'<h1>{t["h1"]}</h1>']
    out += [f'<p class="dek">{x}</p>' for x in t['dek']]
    out.append('<div class="tl">' + '<span class="arr">→</span>'.join(
        f'<span class="ms"><b>{esc(zh if lang == "zh" else en)}</b><i>{y}</i></span>' for en, zh, y in MILESTONES)
        + '<span class="arr">→</span><span class="ms now"><b>AI</b><i>2026</i></span></div>')
    out.append('<div class="links">' + ''.join(f'<a href="{u}">{esc(n)}</a>' for n, u in t['links']) + '</div>')
    out.append('<div class="stats">' + ''.join(f'<div class="stat"><b>{n:,}</b><span>{esc(l)}</span></div>' for n, l in t['st']) + '</div>')

    # the column: AI on top, human works below by year
    col = [f'<div class="ai"><b>{t["ai"]}</b><span>{esc(t["aiS"])}</span><em>2026</em></div>']
    era_i = -1
    for w in works:
        y = int(w['y'] or 0)
        e = next(i for i, (lo, _) in enumerate(t['eras']) if y >= lo)
        if e != era_i:
            col.append(f'<div class="era">{t["eras"][e][1]}</div>')
            era_i = e
        prizes = [LAUR.get(person_key(a), {}) for a in w['a']]
        laur = any(prizes)
        names = '<span class="sep">, </span>'.join(name_html(a, lang, bool(pz)) + chips(pz, lang) for a, pz in zip(w['a'], prizes))
        title = f'<a href="{esc(w["u"])}">{tex(w["t"])}</a>' if w['u'] else tex(w['t'])
        by = ''.join(f'<i>{SHORT[pid]} [{r["n"]}]</i>' for pid, r in w['by'].items())
        quotes = [(SHORT[pid], c) for pid, r in w['by'].items() for c in r['c']]
        det = ''
        if quotes:
            det = f'<details><summary>{t["how"](len(quotes))}</summary>' + ''.join(
                f'<blockquote>{esc(c["s"])}<small>{pid} · {t["pg"].format(c["p"])}</small></blockquote>' for pid, c in quotes) + '</details>'
        cls = 'w' + (' laur' if laur else '') + (' classic' if y and y < 1980 else '')
        col.append(f'<div class="{cls}"><div class="yr">{w["y"] or "—"}</div><div><div class="who">{names}</div>'
                   f'<div class="ti">{title}</div><div class="by">{t["citedIn"]}{by}</div>{det}</div></div>')
    out.append(f'<section class="sec"><span class="eyebrow">{t["colH"]}</span><p class="lead">{t["colP"]}</p><div class="col">' + '\n'.join(col) + '</div></section>')

    # ranking
    m = json.dumps(dict(l=t['metL'], r=t['mR'], t=t['mT'], p=t['mP'], more=t['more'], less=t['less']), ensure_ascii=False)
    rows = []
    for q in sorted(people.values(), key=lambda q: (-q['r'], -q['t'], q['n'])):
        zh = ZH.get(q['n']) if lang == 'zh' else None
        nm = f'{esc(zh)}<small>{esc(q["n"])}</small>' if zh else esc(q['n'])
        rows.append(f'<li data-r="{q["r"]}" data-t="{q["t"]}" data-p="{len(q["p"])}"><span class="nm">{nm}{chips(q["prize"], lang)}</span><span></span><span class="ct">{q["r"]}</span></li>')
    out.append(f'<section class="sec"><span class="eyebrow">{t["rankH"]}</span><p class="lead">{t["rankP"]}</p>'
               f'<div class="metsw" data-m="{esc(m)}"></div><ol class="rank">' + ''.join(rows) + '</ol>'
               f'<button type="button" class="toggle" data-all="{esc(t["showAll"](len(people)))}" data-less="{esc(t["showLess"])}"></button></section>')

    # reference lists
    lists = []
    for p in D:
        items = ''.join(f'<li value="{r["n"]}"><span class="n">{len(r["c"])}×</span><b>{esc(", ".join(r["a"]))}</b>, '
                        + (f'<a href="{esc(r["u"])}">{tex(r["t"])}</a>' if r['u'] else tex(r['t'])) + f' ({r["y"]})</li>' for r in p['refs'])
        lists.append(f'<div><h3><a href="{p["url"]}">{esc(p["title"])}</a></h3><ol>{items}</ol></div>')
    out.append(f'<section class="sec"><span class="eyebrow">{t["refH"]}</span><p class="lead">{t["refP"]}</p><div class="refs">' + ''.join(lists) + '</div></section>')
    out.append(f'<footer>{t["foot"]}</footer>')
    return page(lang, t['title'], t['desc'], CSS, '\n'.join(out) + JS)


base = os.path.dirname(S)
for lang, path in (('zh', 'zh/index.html'), ('en', 'index.html')):
    f = os.path.join(base, path)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(build(lang))
print('ok', len(works), 'works,', len(people), 'people')
