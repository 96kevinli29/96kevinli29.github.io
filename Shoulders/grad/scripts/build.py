"""Builds grad/index.html (English) and grad/zh/index.html from refs.json: the 2026 counterexamples to Grad's conjecture.
Its own layout: three papers side by side with who did what, then the shared foundations they cite, oldest first."""
import os, sys, json, html, re, unicodedata
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
sys.path.insert(0, ROOT)
from common import page, laureates, person_key, chips

D = json.load(open(S + '/refs.json', encoding='utf-8'))
P = {p['id']: p for p in D['papers']}
W = [w for w in D['works'] if not (w['a'] and w['a'][0] in ('Javier Gómez-Serrano', 'Matt Landreman') and w['y'] == '2026')]  # the three papers cite each other
esc = html.escape
LAUR = laureates(os.path.join(ROOT, 'math', 'scripts'))
GRAD_YEAR, NOW = 1967, 2026
ORDER = ['glt', 'lan', 'gdm']

people = {}
for w in W:
    for a in w['a']:
        k = person_key(a)
        q = people.setdefault(k, dict(n=a, w=0, p=set()))
        if len(a) > len(q['n']):
            q['n'] = a
        q['w'] += 1
        q['p'] |= set(w['by'])
ALL3 = [w for w in W if len(w['by']) == 3]
Y0 = min(int(w['y']) for w in W if w['y'])

# who did what, from each paper's own disclosure (quoted in full on the page)
ROLES = {
 'glt': [('h', 'h'), ('b', 'b'), ('a', 'a'), ('h', 'h')],
 'lan': [('n', 'n'), ('a', 'a'), ('a', 'a'), ('h', 'h')],
 'gdm': [('h', 'h'), ('a', 'a'), ('a', 'a'), ('h', 'h')],
}
QUOTE = {
 'glt': 'In July, the authors set up the problem and provided a detailed roadmap to construct the solutions. After this, they used a combination of the LLMs GPT-5.6 Sol, Claude Fable 5, and Claude Opus 5 to fill in the technical details, assist with calculations, and provide mathematical feedback … The Lean code was produced by the same models with continuous guidance from the authors. … All mathematical statements and proofs have been checked by the authors, who take full responsibility for their correctness.',
 'lan': 'These solutions were discovered using the artificial intelligence model GPT-6 Astra Pro, which was also used to draft parts of the manuscript. All equations were confirmed manually by the author.',
 'gdm': 'This work was carried out using Gemini 4 running as a small team of agents in Google Antigravity … the agents proposed the generalized solutions that remove the stellarator-symmetry assumption. … The authors chose the problem, steered the agents, and ran several rounds of adversarial review. Every derivation was independently re-derived and checked symbolically by the authors.',
}
INST = {'glt': 'Brown · Bar-Ilan · Oxford', 'lan': 'University of Maryland', 'gdm': 'Google DeepMind · UC San Diego · University of Maryland'}

T = {
 'zh': dict(
  title='Grad 猜想的反例 · 巨人之肩', back='← 巨人之肩', home='../../zh/', alt=('English', '../'),
  desc='2026 年 9–10 月，三篇论文在两周内给出 Grad 1967 年猜想的反例，三篇都用了 AI，分工各不相同。它们站在哪些人类工作之上。',
  kicker='物理 · 磁约束聚变 · 2026 年 9—10 月',
  h1=f'Grad 猜想：<br>{NOW - GRAD_YEAR} 年后，两周内三篇反例',
  dek=['1967 年，等离子体物理学家 Harold Grad 提出：在环形区域里，除了轴对称这类特殊的对称情形，大概不存在压强不恒定、磁面层层嵌套的光滑磁流体平衡。这个问题关系到仿星器，一种不依赖轴对称的磁约束聚变装置，在理论上能否拥有完好的磁面。',
       '2026 年 9 月 21 日到 10 月 5 日，三篇论文先后在 arXiv 上给出反例。三篇都写明用了 AI，可分工完全不同：有的由人定下路线、让模型补细节，有的说解是模型找到的，有的由人选题、引导一组 AI 智能体。三篇都由作者亲自核对。目前它们都还是预印本，尚未经过同行评审。'],
  sv=('嵌套磁面', '磁轴', '磁力线'),
  st=lambda: [(3, '篇论文'), (14, '天之内'), (len(W), '部被引的人类著作'), (len(people), '位被引用的科学家'), (NOW - Y0, f'年跨度（{Y0}–{NOW}）')],
  aH='三篇论文，三种分工', aP='每张卡片下方是论文自己对 AI 用途的说明，原文照录。表格按这些说明整理，没写到的标为“未说明”。',
  rows=['提出问题、定路线', '找到构造或解', '写细节、代码、草稿', '核对与验证'],
  who=dict(h='人', a='AI', b='人 + AI', n='未说明'),
  what={'glt': '对每个足够大的 N，构造出恰好具有 N 重旋转对称的光滑磁流体静力学解，压强面是嵌套环面；附 Lean 4 形式化证明。',
        'lan': '用初等函数写出显式解析解：非轴对称、磁面严格嵌套、压强光滑，同时也是 Euler 方程的定常流。',
        'gdm': '在 Landreman 的解上加入破坏仿星器对称性的参数，得到两族更一般的精确解，可作为平衡计算程序的基准。'},
  ai={'glt': 'GPT-5.6 Sol · Claude Fable 5 · Claude Opus 5；后期 GPT-6 Astra · Claude Fable 5.1', 'lan': 'GPT-6 Astra Pro', 'gdm': 'Gemini 4（Google Antigravity 中的智能体小组）'},
  quoteL='论文原文', open='在 arXiv 打开',
  bH=f'{NOW - GRAD_YEAR} 年的地基', bP='三篇论文引用的人类著作，按年份从早到晚排列。右侧圆点表示哪篇论文引用了它；点“原文怎样引用”可以看三篇论文各自的原句。',
  all3H='三篇都引用的', all3P='三支团队互不相同的路径，落在同一块地基上。',
  eras=[(0, '1950—1960 年代：平衡理论的奠基'), (1980, '1980—1990 年代：计算程序与存在性'), (2000, '2000—2010 年代'), (2020, '2020 年代：刚性与柔性')],
  how='原文怎样引用', pname={'glt': 'Gómez-Serrano 等', 'lan': 'Landreman', 'gdm': 'Issan 等（DeepMind）'},
  cH='被引用的科学家', cP='按引用他的论文篇数排序，再按著作条数。金色、绿色、紫色标签分别为菲尔兹奖、阿贝尔奖、沃尔夫奖。',
  cols=('科学家', '引用他的论文', '著作'),
  note='说明：Grad 猜想有多种表述，三篇论文各自给出了它们所反驳的版本。参考文献与原句取自三篇论文在 arXiv 上的 LaTeX 源文件，同一著作在不同论文里的写法已合并。三篇论文互相引用的条目未计入。引用不等于依赖；本页不评判结果的正确性、原创性或归属。',
  foot='由 <a href="https://huggingface.co/SeaFill2025">Sea-Fill 开源科学团队</a>制作。',
 ),
 'en': dict(
  title="Counterexamples to Grad's conjecture · On Whose Shoulders", back='← On Whose Shoulders', home='../', alt=('中文', 'zh/'),
  desc="In September–October 2026, three papers gave counterexamples to Grad's 1967 conjecture within two weeks. All three used AI, each differently. The human work they stand on.",
  kicker='Physics · Magnetic confinement fusion · September–October 2026',
  h1=f"Grad<span class=ap>’</span>s conjecture:<br>{NOW - GRAD_YEAR} years on, three counterexamples in two weeks",
  dek=['In 1967 the plasma physicist Harold Grad argued that, inside a torus and outside special symmetric cases such as axisymmetry, there are probably no smooth magnetohydrodynamic equilibria with non-constant pressure and nested magnetic surfaces. The question bears on whether a stellarator, a fusion device that does without axisymmetry, can in principle have good magnetic surfaces.',
       'Between 21 September and 5 October 2026, three papers posted counterexamples on arXiv. All three say they used AI, and each in a different way: in one the authors set the route and models filled in details; in one the solutions were found by a model; in one the authors chose the problem and steered a team of AI agents. In all three the authors checked the results themselves. All three are preprints and have not yet been peer reviewed.'],
  sv=('nested surfaces', 'magnetic axis', 'field line'),
  st=lambda: [(3, 'papers'), (14, 'days'), (len(W), 'human works cited'), (len(people), 'scientists cited'), (NOW - Y0, f'years spanned ({Y0}–{NOW})')],
  aH='Three papers, three divisions of labour', aP='Under each card is the paper’s own statement on how AI was used, quoted in full. The table follows those statements; anything they do not say is marked “not stated”.',
  rows=['Posing the problem, setting the route', 'Finding the construction or solution', 'Details, code, drafting', 'Checking and verification'],
  who=dict(h='People', a='AI', b='People + AI', n='Not stated'),
  what={'glt': 'For every sufficiently large N, smooth magnetohydrostatic solutions with exactly N-fold rotational symmetry and nested toroidal pressure surfaces, with a Lean 4 certification.',
        'lan': 'Explicit analytic solutions in elementary functions: non-axisymmetric, with exactly nested surfaces and smooth pressure; they are also steady Euler flows.',
        'gdm': 'A symmetry-breaking parameter added to Landreman’s solutions gives two more general exact families, offered as benchmarks for equilibrium codes.'},
  ai={'glt': 'GPT-5.6 Sol · Claude Fable 5 · Claude Opus 5; later GPT-6 Astra · Claude Fable 5.1', 'lan': 'GPT-6 Astra Pro', 'gdm': 'Gemini 4 (a small team of agents in Google Antigravity)'},
  quoteL='From the paper', open='Open on arXiv',
  bH=f'{NOW - GRAD_YEAR} years of foundations', bP='The human works the three papers cite, oldest first. The dots on the right show which papers cite each one; open “How it is cited” for each paper’s own sentences.',
  all3H='Cited by all three', all3P='Three different routes, one shared foundation.',
  eras=[(0, '1950s–1960s: the theory of equilibria'), (1980, '1980s–1990s: codes and existence'), (2000, '2000s–2010s'), (2020, '2020s: rigidity and flexibility')],
  how='How it is cited', pname={'glt': 'Gómez-Serrano et al.', 'lan': 'Landreman', 'gdm': 'Issan et al. (DeepMind)'},
  cH='Scientists cited', cP='Ranked by how many of the three papers cite them, then by number of works. Gold, green and purple tags mark the Fields Medal, Abel Prize and Wolf Prize.',
  cols=('Scientist', 'Papers citing', 'Works'),
  note='Note: Grad’s conjecture has several formulations; each paper states the version it refutes. References and sentences come from the three papers’ LaTeX sources on arXiv; the same work cited under different keys is merged. Entries in which the three papers cite one another are left out. Citation is not dependence; this page does not judge the correctness, originality or attribution of the results.',
  foot='Made by <a href="https://huggingface.co/SeaFill2025">Sea-Fill</a>, an open-source science team.',
 ),
}

CSS = '''
body{background:#F6F5F2}
main{max-width:none;padding:0}
.gd{--ink:#12161C;--paper:#F6F5F2;--sheet:#FFFFFF;--muted:#5C636B;--line:#E2E0DA;--acc:#B8321C;--acc2:#F06A4E;--hum:#12161C;--ai:#B8321C;
 --f1:#2F6F9F;--f2:#B8321C;--f3:#6B4797;color:var(--ink);font-family:var(--f-body)}
.gd a{color:inherit}
.gd .wrap{max-width:1180px;margin:0 auto;padding:0 20px}
@media(min-width:760px){.gd .wrap{padding:0 40px}}
.gd .hero{background:#0E1218;color:#F2F0EB;padding:22px 0 56px}
.gd .nav{display:flex;justify-content:space-between;font:500 13px var(--f-mono);letter-spacing:.06em}
.gd .nav a{color:#A9B0B8;text-decoration:none}
.gd .hgrid{display:grid;gap:28px;margin-top:40px;align-items:center}
@media(min-width:900px){.gd .hgrid{grid-template-columns:minmax(0,1.35fr) minmax(0,1fr)}}
.gd .kick{font:500 13px var(--f-mono);letter-spacing:.08em;color:var(--acc2);margin:0 0 16px}
.gd h1{font:900 clamp(34px,5.4vw,60px)/1.12 var(--f-display);margin:0 0 22px;letter-spacing:.01em}
.gd .dek{font-size:17px;line-height:1.8;color:#C7CCD2;margin:0 0 14px;max-width:44em}
.gd .torus{width:100%;max-width:440px;justify-self:center}
.gd .torus text{font:500 13px var(--f-mono);fill:#A9B0B8}
.gd .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px;margin-top:40px}
@media(min-width:760px){.gd .stats{grid-template-columns:repeat(5,minmax(0,1fr))}}
.gd .stats div{border-top:1.5px solid #3A424C;padding-top:12px}
.gd .stats b{display:block;font:600 40px/1 var(--f-display);color:#F2F0EB}
.gd .stats span{display:block;font-size:14px;color:#A9B0B8;margin-top:6px}
.gd .sec{padding:64px 0 8px}
.gd .sec>.wrap>h2{font:900 clamp(26px,3.4vw,36px)/1.3 var(--f-display);margin:0 0 8px}
.gd .sec>.wrap>h2::before{content:"";display:block;width:40px;height:3px;background:var(--acc);margin-bottom:18px}
.gd .lead{color:var(--muted);font-size:15.5px;line-height:1.7;max-width:46em;margin:0 0 26px}
.gd .cards{display:grid;gap:18px}
@media(min-width:980px){.gd .cards{grid-template-columns:repeat(3,minmax(0,1fr))}}
.gd .card{background:var(--sheet);border:1px solid var(--line);border-radius:16px;padding:22px 22px 18px;display:flex;flex-direction:column}
.gd .card .top{display:flex;justify-content:space-between;align-items:baseline;gap:10px;font:500 12.5px var(--f-mono);color:var(--muted)}
.gd .card .dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px;vertical-align:0}
.gd .card h3{font:700 19px/1.4 var(--f-display);margin:12px 0 6px}
.gd .card .au{font-size:14.5px;line-height:1.5}
.gd .card .inst{font:500 12.5px/1.5 var(--f-mono);color:var(--muted);margin-top:2px}
.gd .card .what{font-size:14.5px;line-height:1.65;color:#2A3038;margin:12px 0 14px}
.gd .roles{display:grid;gap:6px;margin:0 0 14px}
.gd .roles div{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;font-size:13.5px;border-top:1px dashed var(--line);padding-top:6px}
.gd .tag{font:600 12.5px/1 var(--f-body);border-radius:999px;padding:5px 10px;white-space:nowrap;justify-self:end}
.gd .ap{font-family:Georgia,serif}
.gd .tag.b{border-radius:10px}
.gd .tag.h{background:var(--hum);color:#fff}.gd .tag.a{background:var(--ai);color:#fff}
.gd .tag.b{background:linear-gradient(90deg,var(--hum) 50%,var(--ai) 50%);color:#fff}.gd .tag.n{background:#ECEAE5;color:var(--muted)}
.gd .model{font:500 12.5px/1.5 var(--f-mono);color:var(--acc);margin-bottom:10px}
.gd details.q{margin-top:auto;border-top:1px solid var(--line);padding-top:10px}
.gd details.q summary{cursor:pointer;font:500 13px var(--f-mono);color:var(--muted)}
.gd details.q blockquote{margin:10px 0 6px;font-size:13.5px;line-height:1.65;color:#2A3038;border-left:3px solid var(--acc);padding-left:12px}
.gd .card .go{font:600 13.5px var(--f-body);color:var(--acc);text-decoration:none;margin-top:8px}
.gd .all3{display:grid;gap:14px;margin-bottom:34px}
@media(min-width:760px){.gd .all3{grid-template-columns:repeat(2,minmax(0,1fr))}}
.gd .all3 a{display:block;text-decoration:none;background:#0E1218;color:#F2F0EB;border-radius:14px;padding:18px 20px}
.gd .all3 b{display:block;font:600 34px/1 var(--f-display);color:var(--acc2)}
.gd .all3 span{display:block;font-size:15px;margin-top:8px;line-height:1.5}
.gd .all3 i{display:block;font:500 12.5px var(--f-mono);font-style:normal;color:#A9B0B8;margin-top:6px}
.gd .era{font:600 13px var(--f-mono);letter-spacing:.06em;color:var(--acc);margin:28px 0 8px}
.gd .rows{border-top:2px solid var(--ink)}
.gd .w{display:grid;grid-template-columns:56px minmax(0,1fr) auto;gap:4px 16px;padding:13px 0;border-bottom:1px solid var(--line)}
.gd .w .y{font:600 15px/1.5 var(--f-mono)}
.gd .w .who{font-size:15px;line-height:1.45;font-weight:500}
.gd .w .ti{font-size:14px;line-height:1.5;color:var(--muted);font-style:italic}
.gd .w .ti a{text-decoration:none}.gd .w .ti a:hover{text-decoration:underline}
.gd .w .ds{display:flex;gap:5px;padding-top:4px}
.gd .w .ds i{width:11px;height:11px;border-radius:50%;border:1.5px solid #CFCBC2}
.gd .w .ds i.on{border-color:transparent}
.gd .w details{grid-column:2 / -1}
.gd .w summary{cursor:pointer;font:500 12.5px var(--f-mono);color:var(--muted)}
.gd .w blockquote{margin:8px 0;font-size:13.5px;line-height:1.6;color:#2A3038;border-left:3px solid var(--line);padding-left:12px}
.gd .w blockquote b{font:600 12px var(--f-mono);display:block;margin-bottom:2px}
.gd .w.three{background:linear-gradient(90deg,rgba(184,50,28,.06),transparent 60%)}
.gd .key{display:flex;flex-wrap:wrap;gap:6px 18px;font:500 12.5px var(--f-mono);color:var(--muted);margin:0 0 6px}
.gd .key i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.gd table.rk{width:100%;border-collapse:collapse;font-size:15px}
.gd table.rk th{text-align:left;font:500 12.5px var(--f-mono);color:var(--muted);border-bottom:2px solid var(--ink);padding:8px 6px}
.gd table.rk td{border-bottom:1px solid var(--line);padding:9px 6px}
.gd table.rk td.n{text-align:right;font-variant-numeric:tabular-nums}
.gd table.rk .ds i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px}
.gd .more{display:block;margin:14px auto 0;font:600 14px var(--f-body);background:none;border:1px solid var(--line);border-radius:999px;padding:9px 18px;cursor:pointer}
.gd .note{font-size:13.5px;line-height:1.7;color:var(--muted);max-width:52em;margin:40px 0 0}
.gd footer{margin-top:28px;padding:22px 0 50px;font-size:13.5px;color:var(--muted);border-top:1px solid var(--line)}
'''
COL = {'glt': 'var(--f1)', 'lan': 'var(--f2)', 'gdm': 'var(--f3)'}

TORUS = '''<svg class="torus" viewBox="0 0 440 300" aria-hidden="true">
 <defs><linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#F06A4E" stop-opacity=".9"/><stop offset="1" stop-color="#F06A4E" stop-opacity=".25"/></linearGradient></defs>
 <g fill="none" stroke-width="1.6">
  <ellipse cx="220" cy="150" rx="190" ry="118" stroke="#3A424C"/>
  <ellipse cx="226" cy="146" rx="150" ry="90" stroke="#4E5864" transform="rotate(-6 220 150)"/>
  <ellipse cx="232" cy="143" rx="108" ry="62" stroke="#66717D" transform="rotate(-12 220 150)"/>
  <ellipse cx="238" cy="141" rx="64" ry="34" stroke="#87919C" transform="rotate(-18 220 150)"/>
  <path d="M40 170 C 110 60, 200 250, 260 120 S 380 70, 410 150" stroke="url(#gl)" stroke-width="2.4"/>
 </g>
 <circle cx="242" cy="140" r="5" fill="#F06A4E"/>
 <text x="300" y="24">{0}</text><line x1="298" y1="30" x2="330" y2="58" stroke="#5C636B"/>
 <text x="262" y="174">{1}</text>
 <text x="30" y="292">{2}</text><line x1="62" y1="282" x2="70" y2="200" stroke="#5C636B"/>
</svg>'''


def dots(by):
    return '<span class="ds">' + ''.join(f'<i class="on" style="background:{COL[k]}" title="{esc(k)}"></i>' if k in by else '<i></i>' for k in ORDER) + '</span>'


def who(a, w, lang):
    pz = LAUR.get(person_key(a), {})
    return esc(a) + chips(pz, lang)


def names(w, lang):
    a = w['a']
    s = ', '.join(who(x, w, lang) for x in a[:6])
    return s + (f' <span style="color:var(--muted)">+{len(a) - 6}</span>' if len(a) > 6 else '')


def build(lang):
    t = T[lang]
    o = ['<div class="gd">', '<header class="hero"><div class="wrap">',
         f'<nav class="nav"><a href="{t["home"]}">{t["back"]}</a><a href="{t["alt"][1]}">{t["alt"][0]}</a></nav>',
         '<div class="hgrid"><div>', f'<p class="kick">{t["kicker"]}</p><h1>{t["h1"]}</h1>'] + [f'<p class="dek">{x}</p>' for x in t['dek']]
    o += ['</div>', TORUS.format(*map(esc, t['sv'])), '</div>',
          '<div class="stats">' + ''.join(f'<div><b>{n:,}</b><span>{esc(l)}</span></div>' for n, l in t['st']()) + '</div>', '</div></header>']

    cards = []
    for k in ORDER:
        p = P[k]
        roles = ''.join(f'<div><span>{esc(r)}</span><span class="tag {c}">{esc(t["who"][c])}</span></div>' for r, (c, _) in zip(t['rows'], ROLES[k]))
        cards.append(f'<article class="card"><div class="top"><span><i class="dot" style="background:{COL[k]}"></i>arXiv:{p["arxiv"]}</span><span>{p["date"]}</span></div>'
                     f'<h3>{esc(p["title"])}</h3><div class="au">{esc(", ".join(p["authors"]))}</div><div class="inst">{esc(INST[k])}</div>'
                     f'<p class="what">{esc(t["what"][k])}</p><div class="model">{esc(t["ai"][k])}</div><div class="roles">{roles}</div>'
                     f'<details class="q"><summary>{t["quoteL"]}</summary><blockquote>{esc(QUOTE[k])}</blockquote></details>'
                     f'<a class="go" href="https://arxiv.org/abs/{p["arxiv"]}">{t["open"]} →</a></article>')
    o.append(f'<section class="sec"><div class="wrap"><h2>{t["aH"]}</h2><p class="lead">{t["aP"]}</p><div class="cards">{"".join(cards)}</div></div></section>')

    key = '<div class="key">' + ''.join(f'<span><i style="background:{COL[k]}"></i>{esc(t["pname"][k])}</span>' for k in ORDER) + '</div>'
    a3 = ''.join(f'<a href="{esc(w["u"])}"><b>{w["y"]}</b><span>{esc(", ".join(w["a"]))}</span><i>{esc(w["t"])}</i></a>' for w in ALL3)
    rows, era = [], None
    for w in sorted(W, key=lambda w: (int(w['y'] or 9999), w['t'])):
        y = int(w['y'] or 9999)
        e = max(i for i, (lo, _) in enumerate(t['eras']) if y >= lo)
        if e != era:
            rows.append(f'<div class="era">{t["eras"][e][1]}</div>'); era = e
        ctx = ''.join(f'<blockquote><b style="color:{COL[k]}">{esc(t["pname"][k])}</b>{esc(s)}</blockquote>' for k in ORDER for s in w['by'].get(k, [])[:2])
        ti = f'<a href="{esc(w["u"])}">{esc(w["t"])}</a>' if w['u'] else esc(w['t'])
        rows.append(f'<div class="w{" three" if len(w["by"]) == 3 else ""}"><div class="y">{w["y"] or "—"}</div><div><div class="who">{names(w, lang)}</div><div class="ti">{ti}</div></div>{dots(w["by"])}'
                    + (f'<details><summary>{t["how"]}</summary>{ctx}</details>' if ctx else '') + '</div>')
    o.append(f'<section class="sec"><div class="wrap"><h2>{t["bH"]}</h2><p class="lead">{t["bP"]}</p>'
             f'<h3 style="font:700 18px var(--f-display);margin:0 0 4px">{t["all3H"]}</h3><p class="lead" style="margin-bottom:14px">{t["all3P"]}</p><div class="all3">{a3}</div>'
             f'{key}<div class="rows">{"".join(rows)}</div></div></section>')

    ppl = sorted(people.values(), key=lambda q: (-len(q['p']), -q['w'], q['n']))
    tr = ''.join(f'<tr{" hidden" if i >= 20 else ""}><td>{who(q["n"], None, lang)}</td><td><span class="ds">' + ''.join(f'<i style="background:{COL[k]}"></i>' for k in ORDER if k in q['p'])
                 + f'</span></td><td class="n">{q["w"]}</td></tr>' for i, q in enumerate(ppl))
    o.append(f'<section class="sec"><div class="wrap"><h2>{t["cH"]}</h2><p class="lead">{t["cP"]}</p>'
             f'<table class="rk"><thead><tr><th>{t["cols"][0]}</th><th>{t["cols"][1]}</th><th style="text-align:right">{t["cols"][2]}</th></tr></thead><tbody>{tr}</tbody></table>'
             f'<button class="more" type="button" onclick="this.previousElementSibling.querySelectorAll(\'tr[hidden]\').forEach(function(r){{r.hidden=false}});this.remove()">+ {len(ppl) - 20}</button>'
             f'<p class="note">{t["note"]}</p><footer>{t["foot"]}</footer></div></section>')
    o.append('</div>')
    return page(lang, t['title'], t['desc'], CSS, '\n'.join(o))


base = os.path.dirname(S)
for lang, path in (('zh', 'zh/index.html'), ('en', 'index.html')):
    f = os.path.join(base, path)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(build(lang))
print('ok', len(W), 'works,', len(people), 'people,', len(ALL3), 'cited by all three')
