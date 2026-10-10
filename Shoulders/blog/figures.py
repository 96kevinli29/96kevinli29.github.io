"""Figures for the essay, as HTML snippets in the essay's design system (theme_*.css).
Everything is HTML so it reflows on phones; numbers are read from decades.json and fields_tree.json."""
import json, os, html

B = os.path.dirname(os.path.abspath(__file__))
esc = html.escape
dot = lambda x: esc(x).replace(' · ', '<span class="sf-dot"> · </span>')   # names joined by a middle dot
DEC = json.load(open(os.path.join(B, 'decades.json')))
START, END = DEC['oldest'], 2030                               # the hero timeline runs from the oldest cited work to the end of this decade
BARS = [(y, n) for y, n in DEC['decades'] if y >= 1850]        # earlier decades hold a handful of works; they are named in the notes
EARLY = sum(n for y, n in DEC['decades'] if y < 1850)
MX = max(n for _, n in BARS)
assert sum(n for _, n in DEC['decades']) == DEC['with_year']

# ---- styles for the figures the design leaves open (2, 4-7) and for motion ---------------------------
CSS = '''
/* figure 2: two models, 64 attempts each */
.sf-f2-grid{display:grid;grid-template-columns:minmax(0,1fr);gap:36px}
@media (min-width:720px){.sf-f2-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:48px}}
.sf-f2-p{border-top:2px solid var(--text);padding-top:16px}
.sf-f2-n{display:block;font-family:var(--num);font-weight:600;font-size:clamp(40px,5vw,64px);line-height:1.05;font-variant-numeric:tabular-nums lining-nums}
.sf-f2-n small{font-family:var(--mono);font-weight:400;font-size:14px;letter-spacing:.02em;color:var(--muted);margin-left:8px}
.sf-f2-p.hi .sf-f2-n{color:var(--accent)}
.sf-f2-p h4{font-family:var(--serif);font-weight:var(--hw);font-size:20px;line-height:1.4;margin:8px 0 18px}
.sf-f2-dots{display:grid;grid-template-columns:repeat(16,minmax(0,1fr));gap:6px;max-width:440px}
.sf-f2-dots i{aspect-ratio:1;border-radius:50%;border:1.5px solid var(--line);border-color:color-mix(in srgb,var(--muted) 45%,transparent)}
.sf-f2-dots i.ok{background:var(--accent);border-color:var(--accent)}
.sf-f2-p p{margin:18px 0 0;font-size:15px;line-height:1.65;color:var(--muted);max-width:440px}
/* figure 3: room above the tallest bar for its value; the note sits on the paper, not on the grid lines */
.sf-dec-plot{padding-top:28px}
.sf-dec-wrap{position:relative}
.sf-dec-wrap .sf-dec-note{position:static;max-width:var(--read);margin:0 0 20px}
@media (min-width:880px){.sf-dec-wrap .sf-dec-note{position:absolute;z-index:1;left:64px;top:28px;max-width:300px;margin:0;background:var(--paper);padding:6px 12px}}
/* the separator between coauthors keeps a Latin width on the Chinese page */
.sf-dot{font-family:"Source Serif 4",Georgia,serif}
.sf-tl-lbl .sf-dot,.sf-relay .sf-dot{display:inline}
/* figures 4-7: a result at the root, lines of human work below it, names on the leaves */
.sf-tree-root{width:fit-content;max-width:100%;margin:0 auto;background:var(--text);color:var(--paper);border-radius:6px;padding:12px 22px;text-align:center}
.sf-tree-root b{display:block;font-family:var(--serif);font-weight:var(--hw);font-size:18px;line-height:1.4}
.sf-tree-root small{display:block;font-family:var(--mono);font-size:12px;letter-spacing:.04em;opacity:.78;margin-top:2px}
.sf-tree-trunk{width:2px;height:28px;background:var(--text);margin:0 auto}
.sf-tree-brs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:32px 20px}
@media (min-width:720px){.sf-tree-brs{grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:36px 24px}}
.sf-tree-b{border-top:2px solid var(--text);padding-top:12px}
.sf-tree-b h5{margin:0 0 8px;font-family:var(--mono);font-weight:500;font-size:12px;line-height:1.5;letter-spacing:.04em;text-transform:uppercase;color:var(--accent)}
.sf-tree-b ul{list-style:none;margin:0;padding:0}
.sf-tree-b li{display:flex;justify-content:space-between;align-items:baseline;gap:10px;padding:6px 0;border-bottom:1px solid var(--line);font-size:15px;line-height:1.45;font-weight:500}
.sf-tree-b li i{font-style:normal;font-family:var(--mono);font-weight:400;font-size:12px;color:var(--muted);white-space:nowrap}
/* stage figures: what scientists supply at each stage of training (left), what the model gets from it (right) */
.sf-st{display:grid;grid-template-columns:minmax(0,1fr);gap:14px;align-items:stretch}
@media (min-width:880px){.sf-st{grid-template-columns:minmax(0,5fr) 44px minmax(0,6fr)}}
.sf-st-c{border-radius:8px;padding:18px 20px;font-size:15px;line-height:1.65}
.sf-st-c>i{display:block;font-style:normal;font-family:var(--mono);font-size:12px;letter-spacing:.04em;margin-bottom:10px}
.sf-st-c.sci{background:#B8321C;color:#fff}.sf-st-c.sci>i{color:#FFE2DA}
.sf-st-c.mod{border:1px solid var(--line);background:var(--paper)}.sf-st-c.mod>i{color:var(--muted)}
.sf-st-c ul{margin:0;padding:0;list-style:none}.sf-st-c li{padding:6px 0;border-top:1px solid rgba(255,255,255,.28)}.sf-st-c li:first-child{border-top:0;padding-top:0}
.sf-st-c.mod li{border-top-color:var(--line)}
.sf-st-a{display:flex;align-items:center;justify-content:center;color:var(--accent);font-size:22px;line-height:1}
.sf-st-a::before{content:"↓"}
@media (min-width:880px){.sf-st-a::before{content:"→"}}
.sf-st-q{font-family:var(--mono);font-size:13.5px;line-height:1.6;background:var(--soft);border-radius:6px;padding:10px 12px;margin-bottom:14px}
.sf-st-q b{color:var(--accent);font-weight:500}
.sf-st-bar{display:grid;grid-template-columns:minmax(0,1fr);gap:4px;margin-top:10px;font-size:14px}
.sf-st-bar span{display:block;height:10px;border-radius:2px;background:var(--text);width:calc(var(--w)*1%);transform-origin:left}
.sf-st-bar.top span{background:var(--accent)}
.sf-st-chain{display:flex;flex-wrap:wrap;gap:6px 4px;align-items:center;font-family:var(--mono);font-size:13px;margin-bottom:12px}
.sf-st-chain b{font-weight:500;border:1px solid var(--line);border-radius:5px;padding:4px 9px;background:var(--soft)}
.sf-st-chain b.end{background:var(--text);color:var(--paper);border-color:var(--text)}
.sf-st-chain em{font-style:normal;color:var(--muted)}
.sf-st-dots{display:flex;flex-wrap:wrap;gap:4px;margin:4px 0 12px}
.sf-st-dots u{width:11px;height:11px;border-radius:50%;border:1.5px solid var(--line);border-color:color-mix(in srgb,var(--muted) 45%,transparent)}
.sf-st-dots u.ok{background:var(--accent);border-color:var(--accent)}
@media screen and (prefers-reduced-motion:no-preference){
 .sf-fig:not(.pre) .sf-st-bar span{transition:transform .7s cubic-bezier(.2,.7,.2,1);transition-delay:calc(.2s + var(--k)*.15s)}
 .sf-fig.pre .sf-st-bar span{transform:scaleX(0)}
 .sf-fig:not(.pre) .sf-st-chain>*{transition:opacity .35s;transition-delay:calc(var(--k)*.12s)}
 .sf-fig.pre .sf-st-chain>*{opacity:0}
 .sf-fig:not(.pre) .sf-st-dots u{transition:opacity .25s,transform .25s;transition-delay:calc(var(--k)*30ms)}
 .sf-fig.pre .sf-st-dots u{opacity:0;transform:scale(.3)}
}
/* motion. Figures play once when they scroll into view: a script marks figures below the fold with .pre and removes it
   when they arrive, so without the script, in print, or with reduced motion, everything is simply visible. */
@keyframes sf-rise{from{transform:scaleY(0)}}
@keyframes sf-lit{0%,16%{box-shadow:0 0 0 2px var(--accent);transform:translateY(-3px)}22%,100%{box-shadow:none;transform:none}}
@media screen and (prefers-reduced-motion:no-preference){
 .sf-tl-bars li{transform-origin:bottom;animation:sf-rise .8s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(.15s + var(--k)*40ms)}
 .sf-fig:not(.pre) :is(.sf-f1-h,.sf-f1-c){transition:opacity .5s,transform .5s;transition-delay:calc(var(--i)*.22s)}
 .sf-fig.pre :is(.sf-f1-h,.sf-f1-c){opacity:0;transform:translateY(12px)}
 .sf-fig:not(.pre) .sf-f2-dots i{transition:opacity .25s,transform .25s;transition-delay:calc(var(--k)*26ms)}
 .sf-fig.pre .sf-f2-dots i{opacity:0;transform:scale(.3)}
 .sf-dec-bars i{transform-origin:bottom}
 .sf-fig:not(.pre) .sf-dec-bars i{transition:transform .7s cubic-bezier(.2,.7,.2,1);transition-delay:calc(var(--k)*45ms)}
 .sf-fig.pre .sf-dec-bars i{transform:scaleY(0)}
 .sf-fig:not(.pre) .sf-dec-bars .v{transition:opacity .4s;transition-delay:calc(.45s + var(--k)*45ms)}
 .sf-fig.pre .sf-dec-bars .v{opacity:0}
 .sf-tree-trunk{transform-origin:top}
 .sf-fig:not(.pre) .sf-tree-root{transition:opacity .5s,transform .5s}
 .sf-fig:not(.pre) .sf-tree-trunk{transition:transform .35s .35s}
 .sf-fig:not(.pre) .sf-tree-b{transition:opacity .5s,transform .5s;transition-delay:calc(.6s + var(--i)*.14s)}
 .sf-fig:not(.pre) .sf-tree-b li{transition:opacity .35s,transform .35s;transition-delay:calc(.85s + var(--i)*.14s + var(--j)*.07s)}
 .sf-fig.pre .sf-tree-root{opacity:0;transform:translateY(-8px)}
 .sf-fig.pre .sf-tree-trunk{transform:scaleY(0)}
 .sf-fig.pre .sf-tree-b{opacity:0;transform:translateY(12px)}
 .sf-fig.pre .sf-tree-b li{opacity:0;transform:translateX(-8px)}
 .sf-f8:not(.pre) .sf-f8-steps li{animation:sf-lit 10s calc(var(--i)*2s) infinite}
}
'''

T = {
 'en': dict(
  lang='en', figno='FIGURE {n}', capno='Figure {n}.',
  # hero timeline
  tl_head=('CITED HUMAN WORKS · BY DECADE OF PUBLICATION', '{a} — 2026 · ONE BAR = ONE DECADE'),
  tl_marks=[(1637, 'Descartes', 'La Géométrie', 0, 0), (1757, 'Euler', 'Fluid equations', 0, 0), (1859, 'Riemann', 'Counting primes', 0, 0),
            (1928, 'Besicovitch', 'Kakeya problem', 0, 0), (1957, 'Grothendieck', 'Splitting theorem', 1, 0), (1978, 'Yau', 'Calabi conjecture', 2, 1),
            (2002, 'Perelman', 'Entropy formula', 3, 1), (2025, 'Wang · Zahl', 'Kakeya in 3D', 0, 1)],
  tl_cap='Bars: the {n:,} cited human works with a known year, by decade; {e} of them predate 1850 and are not drawn. Dots: a few of the giants named in the references and the essay. Euler comes from OpenAI’s Navier–Stokes paper.',
  # key numbers and the Kakeya relay
  stats_aria='Key numbers',
  stats=['AI-written math manuscripts (current release)*', 'cited human works', 'mathematicians', 'Fields, Abel and Wolf laureates'],
  relay_h='One manuscript, a century-long relay: four-dimensional Kakeya sets, 34 references',
  relay=[('1928', 'Besicovitch'), ('1971', 'Davies'), ('1995', 'Wolff'), ('2000', 'Katz · Łaba · Tao'), ('2010', 'Guth'), ('2025–26', 'Hong Wang · Zahl')],
  relay_ai=('2026', 'AI manuscript'),
  # figure 1
  f1_h='Both groups are present at every stage of training',
  f1_sub='Engineers make learning possible; much of what there is to learn comes from scientists.',
  key_eng='Engineers build', key_sci='Scientists supply',
  stages=[('Pretraining', 'next-token prediction',
           'The model, the training code, data pipelines, compute.',
           'Papers, textbooks, proofs: the written record of human knowledge.'),
          ('Supervised fine-tuning', 'the cold start',
           'Fine-tuning runs and the tools that synthesise reasoning chains.',
           'Worked solutions, and the problems, instructions and checks behind synthetic chains.'),
          ('RL & test-time search', 'sampling · verifiers · agents',
           'Training loops, test-time search, agents that call tools; updates toward what worked.',
           'Problems worth solving, a precise definition of correct (e.g. Lean’s Mathlib), judgement of results.')],
  f1_loop='↻ successful attempts seed the next round',
  f1_cap='Two groups are most closely tied to a model capable of scientific breakthroughs. In each stage of training, engineers make learning possible; much of what there is to learn comes from scientists.',
  # figure 2
  f2_h='Sampling finds only what a model can already produce',
  f2_sub='Illustration, not data: two models, 64 attempts each at the same problem',
  f2_unit='/ 64 correct', weak='Weak starting point', strong='Strong starting point',
  weak_p='Every reward is zero, so there is no gradient: nothing to learn from.',
  strong_p='The successful paths can be reinforced and seed the next round.',
  f2_aria='64 attempts, {k} correct',
  f2_cap='Reinforcement learning and test-time sampling can only strengthen or find what a model already samples. High-quality scientific data in pretraining and fine-tuning is a large part of what moves a model from the first panel to the second.',
  # figure 3
  f3_h='The shoulders reach back centuries',
  f3_sub='The {n:,} cited human works with a known year, by decade of publication',
  f3_note='{E} of them predate 1850 and are not drawn; the oldest is Descartes’s <i>La Géométrie</i> (1637). The “quasi-Riemann hypothesis” manuscript cites Riemann’s own paper of 1859.',
  f3_cap='The most recent decades hold the most, but the shoulders reach back centuries.',
 ),
 'zh': dict(
  lang='zh', figno='图 {n}', capno='图 {n}.',
  tl_head=('被引人类著作 · 按出版年代', '{a} — 2026 · 每根柱 = 十年'),
  tl_marks=[(1637, '笛卡尔', '《几何学》', 0, 0), (1757, '欧拉', '流体运动方程', 0, 0), (1859, '黎曼', '素数个数', 0, 0),
            (1928, 'Besicovitch', 'Kakeya 问题', 0, 0), (1957, '格罗滕迪克', '向量丛分裂', 1, 0), (1978, '丘成桐', '卡拉比猜想', 2, 1),
            (2002, '佩雷尔曼', '熵公式', 3, 1), (2025, '王虹 · Zahl', '三维 Kakeya', 0, 1)],
  tl_cap='柱：{n:,} 部有年份的被引人类著作按年代统计，其中 {e} 部早于 1850 年，未画出。点：参考文献与正文中提到的几位“巨人”。欧拉一条出自 OpenAI 的 Navier–Stokes 论文。',
  stats_aria='关键数字',
  stats=['篇 AI 撰写的数学稿件（当前版本）*', '部被引用的人类著作', '位数学家', '位菲尔兹、阿贝尔或沃尔夫奖得主'],
  relay_h='一篇稿件，一个世纪的接力：四维 Kakeya 集，34 条参考文献',
  relay=[('1928', 'Besicovitch'), ('1971', 'Davies'), ('1995', 'Wolff'), ('2000', 'Katz · Łaba · 陶哲轩'), ('2010', 'Guth'), ('2025–26', '王虹 · Zahl')],
  relay_ai=('2026', 'AI 稿件'),
  f1_h='训练的每个阶段，都有这两类人',
  f1_sub='工程师让学习成为可能；可学的内容，很大一部分来自科学家。',
  key_eng='工程师造的', key_sci='科学家提供的',
  stages=[('预训练', '预测下一个 token',
           '模型、训练代码、数据管线、算力。',
           '论文、教材、证明：人类知识的文字记录。'),
          ('监督微调', '冷启动',
           '微调流程，以及合成推理链的工具。',
           '完整的解答，以及合成推理链背后的题目、指令和检验。'),
          ('强化学习与推理时搜索', '采样 · 验证器 · agent',
           '训练循环、推理时搜索、调用工具的 agent，朝成功的方向更新。',
           '值得解的题目，对“正确”的精确定义（如 Lean 的 Mathlib），对结果的评判。')],
  f1_loop='↻ 成功的尝试成为下一轮的种子',
  f1_cap='与一个能做出科学突破的模型关联最深的两类人。在训练的每个阶段，工程师让学习成为可能；可学的内容，很大一部分来自科学家。',
  f2_h='采样，只能找到模型本来就能生成的东西',
  f2_sub='示意，不是数据：两个模型对同一道题各尝试 64 次',
  f2_unit='/ 64 次做对', weak='起点弱的模型', strong='起点强的模型',
  weak_p='奖励全为零，没有梯度，无从学起。',
  strong_p='成功的路径可以被强化，并成为下一轮的种子。',
  f2_aria='64 次尝试，{k} 次做对',
  f2_cap='强化学习和推理时采样，只能强化或找到模型本来就能采样到的东西。预训练和微调中的高质量科学数据，是让模型从前一种情形走到后一种的重要原因。',
  f3_h='肩膀，延伸到几个世纪以前',
  f3_sub='{n:,} 部有年份的被引人类著作，按出版年代统计',
  f3_note='其中 {e} 部早于 1850 年，未画出；最早的是笛卡尔的《几何学》（1637）。那篇“拟黎曼假设”稿件引用了黎曼 1859 年的原始论文。',
  f3_cap='越近的年代越多，但肩膀一直延伸到几个世纪以前。',
 ),
}


def fig(t, n, cls, title, sub, inner, cap):
    """The shared figure frame: number, title, subtitle, the figure itself, caption."""
    return (f'<figure class="sf-fig {cls}" aria-labelledby="f{n}-t"><div class="sf-fig-head">'
            f'<span class="sf-fig-no">{t["figno"].format(n=n)}</span><h3 id="f{n}-t">{esc(title)}</h3><p>{esc(sub)}</p></div>'
            f'{inner}<figcaption><b>{t["capno"].format(n=n)}</b> {cap}</figcaption></figure>')


# ---- hero: decade bars from the oldest cited work to today, with a few names on the axis ------------
def timeline(t):
    x = lambda y: f'{(y - START) / (END - START) * 100:.2f}%'
    bars = ''.join(f'<li style="--x:{x(y)};--v:{n};--k:{k}"></li>' for k, (y, n) in enumerate(BARS))
    marks = ''.join(f'<li{" class=r" if r else ""} style="--x:{x(y)};--t:{tier}"><div class="sf-tl-lbl"><b>{y}</b><span>{dot(who)}</span>'
                    f'<em>{esc(what)}</em></div></li>' for y, who, what, tier, r in t['tl_marks'])
    a, b = t['tl_head']
    return (f'<figure class="sf-tl" aria-labelledby="sf-tl-cap"><div class="sf-tl-head"><span>{a}</span><span>{b.format(a=START)}</span></div>'
            f'<div class="sf-scroll"><div class="sf-tl-plot" style="--mx:{MX}"><ol class="sf-tl-bars" aria-hidden="true">{bars}</ol>'
            f'<div class="sf-tl-axis"></div><ol class="sf-tl-marks">{marks}</ol></div></div>'
            f'<figcaption id="sf-tl-cap">{t["tl_cap"].format(n=DEC["with_year"], e=EARLY)}</figcaption></figure>')


def relay(t):
    items = ''.join(f'<li><b>{esc(y)}</b><span>{dot(n)}</span></li>' for y, n in t['relay'])
    y, n = t['relay_ai']
    return (f'<div class="sf-relay"><h2>{esc(t["relay_h"])}</h2><div class="sf-scroll"><ol>{items}'
            f'<li class="ai"><b>{esc(y)}</b><span>{esc(n)}</span></li></ol></div></div>')


# ---- figure 1: three stages of training, two groups of people ----------------------------------------
def stages(t, n):
    cells = f'<div class="sf-f1-lab e">{esc(t["key_eng"])}</div><div class="sf-f1-lab c">{esc(t["key_sci"])}</div>'
    for i, (name, sub, e, s) in enumerate(t['stages']):
        c = f's{i + 1}" style="--i:{i}'
        cells += (f'<div class="sf-f1-h {c}"><b>{i + 1:02d}</b><h4>{esc(name)}</h4><span>{dot(sub)}</span></div>'
                  f'<div class="sf-f1-c e {c}"><i>{esc(t["key_eng"])}</i>{esc(e)}</div>'
                  f'<div class="sf-f1-c c {c}"><i>{esc(t["key_sci"])}</i>{esc(s)}</div>')
    return fig(t, n, 'sf-f1', t['f1_h'], t['f1_sub'],
               f'<div class="sf-f1-grid">{cells}</div><div class="sf-loop"><span>{esc(t["f1_loop"])}</span></div>'
               f'<p class="sf-loop-m">{esc(t["f1_loop"])}</p>', t['f1_cap'])


# ---- figure 2: the same problem, sampled 64 times by a weak and by a strong model --------------------
def sampling(t, n):
    def panel(on, head, p):
        dots = ''.join(f'<i{" class=ok" if i in on else ""} style="--k:{i}"></i>' for i in range(64))
        return (f'<div class="sf-f2-p{" hi" if on else ""}"><span class="sf-f2-n">{len(on)}<small>{esc(t["f2_unit"])}</small></span><h4>{esc(head)}</h4>'
                f'<div class="sf-f2-dots" role="img" aria-label="{esc(t["f2_aria"].format(k=len(on)))}">{dots}</div><p>{esc(p)}</p></div>')
    return fig(t, n, 'sf-f2', t['f2_h'], t['f2_sub'],
               '<div class="sf-f2-grid">' + panel(set(), t['weak'], t['weak_p'])
               + panel({3, 12, 18, 27, 33, 41, 46, 55, 60}, t['strong'], t['strong_p']) + '</div>', t['f2_cap'])


# ---- figure 3: cited works by decade -----------------------------------------------------------------
def decades(t, n):
    bars = ''.join(f'<li{" class=hi" if v == MX else ""} style="--v:{v};--k:{k}"><span class="v">{v:,}</span><i></i><span class="d">{y}s</span></li>'
                   for k, (y, v) in enumerate(BARS))
    grid = ''.join(f'<span style="--g:{g}">{g:,}</span>' for g in range(0, MX, 1000))
    note = t['f3_note'].format(e=EARLY, E={1: 'One', 2: 'Two', 3: 'Three', 4: 'Four'}.get(EARLY, EARLY))
    return fig(t, n, 'sf-dec', t['f3_h'], t['f3_sub'].format(n=DEC['with_year']),
               f'<div class="sf-dec-wrap"><p class="sf-dec-note">{note}</p>'
               f'<div class="sf-scroll"><div class="sf-dec-plot" style="--mx:{MX}"><div class="sf-dec-area">'
               f'<div class="sf-dec-grid" aria-hidden="true">{grid}</div>'
               f'<ol class="sf-dec-bars" style="grid-template-columns:repeat({len(BARS)},minmax(0,1fr))">{bars}</ol>'
               '</div></div></div></div>', t['f3_cap'])


# ---- figures 4-7: trees ------------------------------------------------------------------------------
def tree(t, n, title, sub, root, root_sub, branches, cap):
    br = ''.join(f'<div class="sf-tree-b" style="--i:{i}"><h5>{esc(h)}</h5><ul>' + ''.join(
        f'<li style="--j:{j}"><span>{dot(name)}</span>' + (f'<i>{esc(y)}</i>' if y else '') + '</li>' for j, (name, y) in enumerate(leaves)) + '</ul></div>'
        for i, (h, leaves) in enumerate(branches))
    return fig(t, n, 'sf-tree', title, sub,
               f'<div class="sf-tree-root"><b>{esc(root)}</b><small>{esc(root_sub)}</small></div>'
               f'<div class="sf-tree-trunk"></div><div class="sf-tree-brs">{br}</div>', cap)


def tree_fields(t, n):
    data = json.load(open(os.path.join(B, 'fields_tree.json'), encoding='utf-8'))
    zhn = {'Shing-Tung Yau': '丘成桐', 'Terence Tao': '陶哲轩'}
    zh = t['lang'] == 'zh'
    branches = [(f'{z if zh else en} · {k}', [((zhn.get(name, name) if zh else name), '') for name, _ in top]) for en, z, k, top in data]
    if zh:
        return tree(t, n, '九个学科，九群不同的人', 'AI 稿件最多的九个学科，以及每个学科中参考文献条目最多的三位数学家',
                    'AI · OpenAI Math Release', '719 篇稿件 · 稿件最多的九个学科', branches, '学科后的数字，是该学科的 AI 稿件数。')
    return tree(t, n, 'Nine fields, nine different sets of shoulders',
                'The nine fields with the most AI manuscripts and, in each, the three mathematicians with the most reference entries',
                'AI · OpenAI Math Release', '719 manuscripts · the nine largest fields', branches,
                'The number after each field is its count of AI manuscripts.')


TREE_KAKEYA = [
    ('Foundations', [('Besicovitch', '1928'), ('Davies', '1971'), ('Wolff', '1995'), ('Bourgain', '1999'), ('Katz · Łaba · Tao', '2000'), ('Katz · Tao', '2002')]),
    ('Multilinear Kakeya', [('Bennett · Carbery · Tao', '2006'), ('Guth', '2010'), ('Bourgain · Guth', '2011'), ('Carbery · Valdimarsson', '2013')]),
    ('Kakeya in 3 and 4 dimensions', [('Guth · Zahl', '2018'), ('Katz · Zahl', '2021'), ('Hong Wang · Zahl', '2025'), ('Hong Wang · Zahl (sticky)', '2026'), ('Guth · Hong Wang · Zahl', '2026')]),
    ('Oscillatory integrals', [('Guo · Hong Wang · Zhang', '2024'), ('Gao · Liu · Xi', '2025'), ('Nadjimzadah', '2026')]),
    ('Tools', [('Tao · Vu', '2006'), ('Basu · Pollack · Roy', '2006'), ('Cover · Thomas', '2006')]),
]
TREE_NS = [
    ('The equations', [('Euler', '1757'), ('Navier', '1827'), ('Stokes', '1845')]),
    ('Weak solutions & regularity', [('Leray', '1934'), ('Kato', '1972'), ('Caffarelli · Kohn · Nirenberg', '1982'), ('Beale · Kato · Majda', '1984'), ('Escauriaza · Seregin · Šverák', '2003')]),
    ('The problem', [('Fefferman (Clay statement)', '2000')]),
    ('Blowup & non-uniqueness', [('Tao', '2016'), ('Buckmaster · Vicol', '2019'), ('Elgindi', '2021'), ('Albritton · Brué · Colombo', '2022'), ('Chen · Hou', '2022'), ('Córdoba · Martínez-Zoroa', '2023')]),
    ('Instability & waves', [('Leibovich · Stewartson', '1983'), ('Craik · Criminale', '1986'), ('Friedlander · Vishik', '1991'), ('Lifschitz · Hameiri', '1991')]),
]
TREE_AF = [
    ('Folding principle', [('Anfinsen', '1973')]),
    ('Solving structures', [('Wüthrich (NMR)', '2001'), ('Jaskolski · Dauter · Wlodawer', '2014'), ('Bai · McMullan · Scheres (cryo-EM)', '2015'), ('wwPDB', '2018')]),
    ('Coevolution', [('Altschuh · Lesk · Bloomer · Klug', '1987'), ('Shindyalov · Kolchanov · Sander', '1994'), ('Weigt et al.', '2009'), ('Marks et al.', '2011'), ('Jones et al. (PSICOV)', '2012')]),
    ('Prediction & assessment', [('Šali · Blundell', '1993'), ('Moult et al. (CASP)', '1995'), ('Zhang · Skolnick', '2004'), ('Senior et al. (AlphaFold 1)', '2020'), ('Yang · … · Baker (trRosetta)', '2020')]),
    ('Deep learning', [('Qian · Sejnowski', '1988'), ('He et al. (ResNet)', '2016'), ('Devlin et al. (BERT)', '2019')]),
]

ZH_HEAD = {'Foundations': '奠基', 'Multilinear Kakeya': '多线性 Kakeya', 'Kakeya in 3 and 4 dimensions': '三维与四维 Kakeya',
           'Oscillatory integrals': '振荡积分', 'Tools': '工具', 'The equations': '方程本身', 'Weak solutions & regularity': '弱解与正则性',
           'The problem': '问题陈述', 'Blowup & non-uniqueness': '爆破与非唯一性', 'Instability & waves': '不稳定性与波',
           'Folding principle': '折叠原理', 'Solving structures': '测定结构', 'Coevolution': '协同进化',
           'Prediction & assessment': '预测与评测', 'Deep learning': '深度学习'}


def zh_tree(branches, names):
    """Chinese page: branch headings in Chinese, Chinese mathematicians in Chinese, other names in the original."""
    out = []
    for h, leaves in branches:
        ls = []
        for name, y in leaves:
            for a, b in names:
                name = name.replace(a, b)
            ls.append((name, y))
        out.append((ZH_HEAD[h], ls))
    return out


def tree_kakeya(t, n):
    if t['lang'] == 'zh':
        return tree(t, n, '一篇稿件，五条人类工作的脉络', 'OpenAI 四维 Kakeya 稿件 34 条参考文献的节选',
                    'AI 稿件 · 四维 Kakeya 集', 'OpenAI，2026 · 34 条参考文献',
                    zh_tree(TREE_KAKEYA, [('Hong Wang', '王虹'), ('Guo ·', '郭少明 ·'), ('· Zhang', '· 张瑞祥'), ('Tao', '陶哲轩'), (' (sticky)', '（sticky）')]),
                    '按稿件所依托的工作脉络分组；分组由我们整理。')
    return tree(t, n, 'One manuscript, five lines of human work', 'A selection of the 34 works cited by OpenAI’s manuscript on four-dimensional Kakeya sets',
                'AI manuscript · four-dimensional Kakeya sets', 'OpenAI, 2026 · 34 references', TREE_KAKEYA,
                'The works are grouped into the lines of research the manuscript draws on; the grouping is ours.')


def tree_ns(t, n):
    if t['lang'] == 'zh':
        return tree(t, n, '从欧拉到今天，269 年', 'OpenAI Navier–Stokes 与 Euler 论文所引文献的节选（共 51 条）',
                    'AI · OpenAI Navier–Stokes 与 Euler 论文', '2026 · 51 条参考文献',
                    zh_tree(TREE_NS, [('Tao', '陶哲轩'), ('Hou', '侯一钊'), ('Kato', '加藤敏夫'), ('Euler', '欧拉'), ('Navier', '纳维'),
                                      ('Stokes', '斯托克斯'), ('Leray', '勒雷'), (' (Clay statement)', '（克雷问题陈述）')]),
                    '从写下方程，到弱解、正则性、爆破与不稳定性；分组由我们整理。')
    return tree(t, n, '269 years, from Euler to today', 'A selection of the works cited by OpenAI’s Navier–Stokes and Euler papers (51 references)',
                'AI · OpenAI Navier–Stokes and Euler papers', '2026 · 51 references', TREE_NS,
                'From the equations themselves to weak solutions, regularity, blowup and instability; the grouping is ours.')


def tree_af(t, n):
    if t['lang'] == 'zh':
        return tree(t, n, 'AlphaFold 背后，半个世纪的科学', 'AlphaFold 2 论文（Nature 2021，84 条参考文献）所引文献的节选',
                    'AI · AlphaFold 2', 'DeepMind，Nature 2021 · 84 条参考文献',
                    zh_tree(TREE_AF, [('Anfinsen', '安芬森'), ('Zhang · Skolnick', '张阳 · Skolnick'), (' (NMR)', '（核磁共振）'),
                                      (' (cryo-EM)', '（冷冻电镜）'), (' (CASP)', '（CASP）'), (' (AlphaFold 1)', '（AlphaFold 1）'),
                                      (' (trRosetta)', '（trRosetta）'), (' (PSICOV)', '（PSICOV）'), (' (ResNet)', '（ResNet）'), (' (BERT)', '（BERT）')]),
                    '结构生物学、协同进化与机器学习；分组由我们整理。')
    return tree(t, n, 'Half a century of science behind AlphaFold', 'A selection of the works cited by the AlphaFold 2 paper (Nature 2021, 84 references)',
                'AI · AlphaFold 2', 'DeepMind, Nature 2021 · 84 references', TREE_AF,
                'Structural biology, coevolution and machine learning; the grouping is ours.')


# ---- figure 8: the navigation loop -------------------------------------------------------------------
LOOP = {
 'en': dict(h='The navigation loop',
            sub='However capable AI becomes, someone has to help synthesise the data and point the way. Each turn produces new data that carries a learning signal.',
            steps=[('sci', 'Scientists', 'pose problems worth solving and set the standard for “correct”'),
                   ('ai', 'AI', 'samples at scale: thousands of attempts'),
                   ('ver', 'Verifier', 'human-built standards keep the attempts that pass'),
                   ('sci', 'Scientists', 'judge which results hold and which matter'),
                   ('data', 'New data', 'carries a learning signal into the next round of training')],
            back='↻ the next problem', back_m='↻ back to step 1: the next problem',
            cap='The navigation loop. Scientists choose the problems, define correctness and judge the results; AI tries at a scale no person can.'),
 'zh': dict(h='领航循环',
            sub='AI 再强大，也需要有人参与合成数据、指引方向。每转一圈，就产生一批带着学习信号的新数据。',
            steps=[('sci', '科学家', '提出值得解的问题，定下“正确”的标准'),
                   ('ai', 'AI', '大规模采样：成千上万次尝试'),
                   ('ver', '验证器', '人建立的标准，留下通过检验的尝试'),
                   ('sci', '科学家', '评判哪些结果成立、哪些重要'),
                   ('data', '新的数据', '带着学习信号，进入下一轮训练')],
            back='↻ 下一个问题', back_m='↻ 回到第 1 步：下一个问题',
            cap='领航循环。科学家挑选问题、定义正确、评判结果；AI 以人无法企及的规模去尝试。'),
}


def loop(t, n):
    L = LOOP[t['lang']]
    steps = ''.join(f'<li style="--i:{i}"><b>{i + 1:02d}</b><br><span class="sf-tag {c}">{esc(h)}</span><p>{esc(d)}</p></li>'
                    for i, (c, h, d) in enumerate(L['steps']))
    return fig(t, n, 'sf-f8', L['h'], L['sub'],
               f'<ol class="sf-f8-steps">{steps}</ol><div class="sf-loop" style="margin-top:20px"><span>{esc(L["back"])}</span></div>'
               f'<p class="sf-loop-m">{esc(L["back_m"])}</p>', L['cap'])


FIGS = {'stages': stages, 'sampling': sampling, 'decades': decades, 'tree_fields': tree_fields, 'tree_kakeya': tree_kakeya,
        'tree_ns': tree_ns, 'tree_af': tree_af, 'loop': loop}


# ---- one figure per stage: the scientists' part in pretraining, fine-tuning, and reinforcement learning ----
ST = {
 'en': dict(sci='SCIENTISTS SUPPLY', mod='WHAT THE MODEL GETS',
  pre=dict(h='Pretraining: intuition is the next step people wrote down', sub='Illustration, not data: how one step of a proof becomes a probability',
           left=['1957: Grothendieck proves the splitting theorem', 'Since then, the step is written again and again in papers, textbooks and lecture notes', 'Every careful proof adds clear “next steps” to the text'],
           q='By the splitting theorem for vector bundles on the projective line, <b>▁</b>',
           bars=[('E is a direct sum of line bundles', 92), ('E is trivial', 14), ('E is indecomposable', 5)], lab='Likely continuations',
           cap='The model did not discover the fact. It learned that this step very probably comes next, because mathematicians wrote it that way.'),
  sft=dict(h='Supervised fine-tuning: how to get from one step to the next', sub='The cold start: a small, carefully chosen set of long chains of reasoning',
           left=['Chains written by people: proofs, derivations, worked solutions', 'For synthetic chains: the problems and the instructions they start from', 'The checks that decide which synthetic chains are kept'],
           chain=['Problem', 'Step 1', 'Step 2', '…', 'Conclusion'], note='The model learns the path, not only the answer: which step follows which, and why.',
           cap='Engineers assemble and run this stage. The way of reasoning it teaches is the way mathematicians write proofs.'),
  rl=dict(h='Reinforcement learning and search: the target still comes largely from scientists', sub='Illustration, not data: one problem, many attempts, a verifier',
          left=['A problem worth solving, at the edge of what the model can do', 'A precise definition of “correct” (for example, a proof that checks in Lean)', 'Judgement: which of the results that pass matter'],
          a='32 attempts', b='3 pass the verifier', note='Passing attempts are reinforced in training, or kept as the answer at test time.',
          cap='Sampling can run without people. What it aims at, and what counts as a hit, still comes largely from scientists.')),
 'zh': dict(sci='科学家提供的', mod='模型得到的',
  pre=dict(h='预训练：直觉，是人类写下的“下一步”', sub='示意，不是数据：证明里的一步，怎样变成一个概率',
           left=['1957 年，格罗滕迪克证明分裂定理', '此后，这一步在论文、教材和讲义里被一遍遍写下', '每一个严谨的证明，都给文本添上清晰的“下一步”'],
           q='由射影直线上向量丛的分裂定理，<b>▁</b>',
           bars=[('E 是线丛的直和', 92), ('E 是平凡丛', 14), ('E 不可分解', 5)], lab='可能的下一步',
           cap='这个事实不是模型发现的。它学到的是这一步极有可能紧跟在后面，因为数学家就是这样写的。'),
  sft=dict(h='监督微调：怎样从一步走到下一步', sub='冷启动：一小批精选的长推理链',
           left=['人写的推理链：证明、推导、完整的解答', '合成推理链所依据的题目和指令', '决定合成推理链去留的检验'],
           chain=['题目', '第 1 步', '第 2 步', '…', '结论'], note='模型学的是路径，不只是答案：哪一步接哪一步，为什么。',
           cap='这个阶段由工程师组织和运行。它教给模型的推理方式，是数学家写证明的方式。'),
  rl=dict(h='强化学习与搜索：靶子，今天仍主要由科学家立', sub='示意，不是数据：一道题，许多次尝试，一个验证器',
          left=['一道值得解的题，处在模型能力的边缘', '对“正确”的精确定义（例如能在 Lean 里通过检验的证明）', '评判：通过检验的结果里，哪些重要'],
          a='32 次尝试', b='3 次通过验证器', note='通过的尝试，在训练时被强化，在推理时被留下作为答案。',
          cap='采样可以没有人参与。但朝哪里采、什么算命中，今天仍主要来自科学家。')),
}


def _stage(t, n, key, right):
    L, d = ST[t['lang']], ST[t['lang']][key]
    left = ''.join(f'<li>{esc(x)}</li>' for x in d['left'])
    return fig(t, n, 'sf-stg', d['h'], d['sub'],
               f'<div class="sf-st"><div class="sf-st-c sci"><i>{L["sci"]}</i><ul>{left}</ul></div><div class="sf-st-a" aria-hidden="true"></div>'
               f'<div class="sf-st-c mod"><i>{L["mod"]}</i>{right(d)}</div></div>', esc(d['cap']))


def stage_pre(t, n):
    return _stage(t, n, 'pre', lambda d: f'<div class="sf-st-q">{d["q"]}</div><div style="font-size:13px;color:var(--muted)">{esc(d["lab"])}</div>' + ''.join(
        f'<div class="sf-st-bar{" top" if k == 0 else ""}">{esc(x)}<span style="--w:{w};--k:{k}"></span></div>' for k, (x, w) in enumerate(d['bars'])))


def stage_sft(t, n):
    def right(d):
        parts = []
        for k, x in enumerate(d['chain']):
            if k:
                parts.append(f'<em style="--k:{2 * k - 1}">→</em>')
            parts.append(f'<b{" class=end" if k == len(d["chain"]) - 1 else ""} style="--k:{2 * k}">{esc(x)}</b>')
        return f'<div class="sf-st-chain">{"".join(parts)}</div><div>{esc(d["note"])}</div>'
    return _stage(t, n, 'sft', right)


def stage_rl(t, n):
    def right(d):
        ok = {5, 17, 26}
        dots = ''.join(f'<u{" class=ok" if k in ok else ""} style="--k:{k}"></u>' for k in range(32))
        return (f'<div style="font-size:13px;color:var(--muted)">{esc(d["a"])} · <b style="color:var(--accent)">{esc(d["b"])}</b></div>'
                f'<div class="sf-st-dots">{dots}</div><div>{esc(d["note"])}</div>')
    return _stage(t, n, 'rl', right)


FIGS.update({'stage_pre': stage_pre, 'stage_sft': stage_sft, 'stage_rl': stage_rl})


def render(name, lang, n):
    return FIGS[name](T[lang], n)
