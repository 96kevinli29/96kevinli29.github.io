"""Figures for the essay, as HTML/SVG snippets. Text-heavy diagrams are HTML so they reflow on phones."""
import json, os, html

B = os.path.dirname(os.path.abspath(__file__))
esc = html.escape

CSS = '''
figure.fig{margin:2rem 0 2.2rem;padding:1.1rem 1.1rem .9rem;background:var(--sheet);border:1px solid var(--rule);border-radius:8px}
figure.fig figcaption{margin-top:.8rem;font-size:.84rem;line-height:1.55;color:var(--muted)}
figure.fig figcaption b{color:var(--ink);font-weight:600}
.fig-key{display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;font:.74rem var(--f-mono);color:var(--muted);margin-bottom:.8rem}
.fig-key i{display:inline-block;width:.7rem;height:.7rem;border-radius:2px;margin-right:.35rem;vertical-align:-.05rem}
.k-eng{background:var(--ink)}.k-sci{background:var(--gold)}
/* stages */
.stages{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem}
.stage{display:flex;flex-direction:column;gap:.45rem}
.stage h4{margin:0;font:600 .95rem var(--f-display)}
.stage h4 small{display:block;font:.68rem var(--f-mono);color:var(--muted);letter-spacing:.04em;text-transform:uppercase}
.cell{border-radius:6px;padding:.55rem .65rem;font-size:.82rem;line-height:1.45}
.cell b{display:block;font:500 .66rem var(--f-mono);letter-spacing:.05em;text-transform:uppercase;margin-bottom:.15rem}
.cell.eng{border:1px solid var(--rule);background:var(--paper)}
.cell.eng b{color:var(--muted)}
.cell.sci{background:var(--gold-soft);border:1px solid var(--gold-soft)}
.cell.sci b{color:var(--gold)}
.loop{font:.72rem var(--f-mono);color:var(--muted);text-align:center}
@media (max-width:620px){.stages{grid-template-columns:1fr}}
/* sampling */
.samp{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.samp h4{margin:0 0 .45rem;font:600 .9rem var(--f-display)}
.dots{display:grid;grid-template-columns:repeat(16,1fr);gap:3px;max-width:15rem}
.dots i{aspect-ratio:1;border-radius:50%;border:1.5px solid var(--rule);background:transparent}
.dots i.ok{background:var(--use);border-color:var(--use)}
.samp p{margin:.5rem 0 0;font-size:.8rem;line-height:1.45;color:var(--muted)}
.samp p b{color:var(--ink)}
@media (max-width:520px){.samp{grid-template-columns:1fr}}
/* relay */
.relay{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:.5rem;align-items:stretch}
.relay li{flex:1 1 7.5rem;line-height:1.35;margin:0;border:1px solid var(--rule);border-radius:6px;padding:.45rem .55rem;background:var(--paper)}
.relay li b{display:block;font:.7rem var(--f-mono);color:var(--muted)}
.relay li span{display:block;font:600 .86rem/1.35 var(--f-display)}
.relay li.ai{background:var(--ink);border-color:var(--ink)}.relay li.ai b,.relay li.ai span{color:var(--paper)}
/* decades */
.hist svg{width:100%;height:auto;display:block}
.hist .bar{fill:var(--gold)}
.hist .bar:hover{fill:var(--ink)}
.hist .ax{stroke:var(--rule)}
.hist text{fill:var(--muted);font:20px var(--f-mono)}
.hist text.v{fill:var(--ink)}
'''

T = {
 'en': dict(
  key_eng='Engineers build', key_sci='Scientists supply',
  stages=[('Pretraining', 'next-token prediction',
           'The model, the training code, data pipelines, compute.',
           'Papers, textbooks, proofs: the written record of human knowledge.'),
          ('Supervised fine-tuning', 'the cold start',
           'Fine-tuning runs and the tools that synthesise reasoning chains.',
           'Worked solutions, and the problems, instructions and checks behind synthetic chains.'),
          ('Reinforcement learning & test-time search', 'sampling, verifiers, agents',
           'Training loops, test-time search, agents that call tools; updates toward what worked.',
           'Problems worth solving, a precise definition of correct (e.g. Lean’s Mathlib), judgement of results.')],
  loop='↻ successful attempts seed the next round',
  cap1='<b>Figure 1.</b> Two groups are most closely tied to a model capable of scientific breakthroughs. In each stage of training, engineers make learning possible; much of what there is to learn comes from scientists.',
  weak='Weak starting point', strong='Strong starting point',
  weak_p='<b>0 of 64</b> attempts correct. Every reward is zero, so there is no gradient: nothing to learn from.',
  strong_p='<b>9 of 64</b> attempts correct. The successful paths can be reinforced and seed the next round.',
  cap2='<b>Figure 2.</b> Illustration, not data: 64 attempts at the same problem by two models. Reinforcement learning and test-time sampling can only strengthen or find what a model already samples. High-quality scientific data in pretraining and fine-tuning is a large part of what moves a model from the left panel to the right.',
  relay=[('1928', 'Besicovitch'), ('1971', 'Davies'), ('1995', 'Wolff'), ('2000', 'Katz · Łaba · Tao'),
         ('2006', 'Bennett · Carbery · Tao'), ('2010', 'Guth'), ('2025–26', 'Hong Wang · Joshua Zahl')],
  relay_ai=('2026', 'AI manuscript on four-dimensional Kakeya sets'),
  cap4='<b>Figure 4.</b> A selection of the human works cited by OpenAI’s manuscript on four-dimensional Kakeya sets, in order. The manuscript has 34 references in all.',
  lang='en',
  hist_y='works', cap3='<b>Figure 3.</b> The {n:,} cited human works with a known year, by decade of publication. The oldest is Descartes’s <i>La Géométrie</i> (1637); the most recent decades hold the most, but the shoulders reach back centuries. Hover a bar for its count.',
 ),
 'zh': dict(
  lang='zh',
  key_eng='工程师造的', key_sci='科学家提供的',
  stages=[('预训练', '预测下一个 token',
           '模型、训练代码、数据管线、算力。',
           '论文、教材、证明：人类知识的文字记录。'),
          ('监督微调', '冷启动',
           '微调流程，以及合成推理链的工具。',
           '完整的解答，以及合成推理链背后的题目、指令和检验。'),
          ('强化学习与推理时搜索', '采样、验证器、agent',
           '训练循环、推理时搜索、调用工具的 agent，朝成功的方向更新。',
           '值得解的题目，对“正确”的精确定义（如 Lean 的 Mathlib），对结果的评判。')],
  loop='↻ 成功的尝试成为下一轮的种子',
  cap1='<b>图 1.</b> 与一个能做出科学突破的模型关联最深的两类人。在训练的每个阶段，工程师让学习成为可能；可学的内容，很大一部分来自科学家。',
  weak='起点弱的模型', strong='起点强的模型',
  weak_p='64 次尝试中 <b>0 次</b>做对。奖励全为零，没有梯度，无从学起。',
  strong_p='64 次尝试中 <b>9 次</b>做对。成功的路径可以被强化，并成为下一轮的种子。',
  cap2='<b>图 2.</b> 示意，不是数据：两个模型对同一道题各尝试 64 次。强化学习和推理时采样，只能强化或找到模型本来就能采样到的东西。预训练和微调中的高质量科学数据，是让模型从左边走到右边的重要原因。',
  hist_y='部', cap3='<b>图 3.</b> {n:,} 部有年份的被引人类著作，按出版年代统计。最早的是笛卡尔的《几何学》（1637）；越近的年代越多，但肩膀一直延伸到几个世纪以前。鼠标悬停可看每个年代的数量。',
 ),
}


def stages(t):
    cols = ''.join(
        f'<div class="stage" style="--i:{i}"><h4>{esc(n)}<small>{esc(sub)}</small></h4>'
        f'<div class="cell eng"><b>{esc(t["key_eng"])}</b>{esc(e)}</div>'
        f'<div class="cell sci"><b>{esc(t["key_sci"])}</b>{esc(s)}</div></div>'
        for i, (n, sub, e, s) in enumerate(t['stages']))
    return (f'<figure class="fig"><div class="fig-key"><span><i class="k-eng"></i>{esc(t["key_eng"])}</span>'
            f'<span><i class="k-sci"></i>{esc(t["key_sci"])}</span></div>'
            f'<div class="stages">{cols}</div><div class="loop">{esc(t["loop"])}</div>'
            f'<figcaption>{t["cap1"]}</figcaption></figure>')


def sampling(t):
    def dots(ok):
        on = {3, 12, 18, 27, 33, 41, 46, 55, 60} if ok else set()
        return '<div class="dots" role="img" aria-label="64 attempts">' + ''.join(
            f'<i class="{"ok" if i in on else ""}" style="--k:{i}"></i>' for i in range(64)) + '</div>'
    return (f'<figure class="fig"><div class="samp">'
            f'<div><h4>{esc(t["weak"])}</h4>{dots(False)}<p>{t["weak_p"]}</p></div>'
            f'<div><h4>{esc(t["strong"])}</h4>{dots(True)}<p>{t["strong_p"]}</p></div>'
            f'</div><figcaption>{t["cap2"]}</figcaption></figure>')


def relay(t):
    items = ''.join(f'<li><b>{esc(y)}</b><span>{esc(n)}</span></li>' for y, n in t['relay'])
    y, n = t['relay_ai']
    items += f'<li class="ai"><b>{esc(y)}</b><span>{esc(n)}</span></li>'
    return f'<figure class="fig"><ol class="relay">{items}</ol><figcaption>{t["cap4"]}</figcaption></figure>'


def decades(t):
    d = json.load(open(os.path.join(B, 'decades.json')))
    data = [(y, n) for y, n in d['decades'] if y >= 1850]            # earlier decades: a handful of works, noted in the caption
    W, H, L, R, TOP, BOT = 640, 300, 70, 8, 14, 40
    bw = (W - L - R) / len(data)
    mx = max(n for _, n in data)
    bars, labels = [], []
    for i, (y, n) in enumerate(data):
        h = (H - TOP - BOT) * n / mx
        x = L + i * bw
        bars.append(f'<rect class="bar" style="--k:{i}" x="{x + 1:.1f}" y="{H - BOT - h:.1f}" width="{bw - 2:.1f}" height="{max(h, 1):.1f}" rx="2">'
                    f'<title>{y}s: {n:,} {t["hist_y"]}</title></rect>')
        if y % 50 == 0:
            labels.append(f'<text x="{x + bw / 2:.1f}" y="{H - 12}" text-anchor="middle">{y}</text>')
    ticks = ''.join(f'<line class="ax" x1="{L}" x2="{W - R}" y1="{H - BOT - (H - TOP - BOT) * v / mx:.1f}" y2="{H - BOT - (H - TOP - BOT) * v / mx:.1f}"/>'
                    f'<text x="{L - 6}" y="{H - BOT - (H - TOP - BOT) * v / mx + 7:.1f}" text-anchor="end">{v:,}</text>'
                    for v in (1000, 2000))
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["cap3"].split("</b>")[0][3:])}">'
           f'{ticks}<line class="ax" x1="{L}" x2="{W - R}" y1="{H - BOT}" y2="{H - BOT}"/>{"".join(bars)}{"".join(labels)}</svg>')
    return f'<figure class="fig hist">{svg}<figcaption>{t["cap3"].format(n=d["with_year"])}</figcaption></figure>'


FIGS = {'stages': stages, 'sampling': sampling, 'relay': relay, 'decades': decades}


def render(name, lang):
    return FIGS[name](T[lang])


# ---- trees: a breakthrough at the root, branches of human work, names on the leaves -----------------
CSS += '''
.tree{--line:var(--rule)}
.tree .root{width:fit-content;max-width:100%;margin:0 auto;background:var(--ink);color:var(--paper);border-radius:6px;padding:.5rem .9rem;text-align:center}
.tree .root b{display:block;font:600 .95rem/1.3 var(--f-display)}
.tree .root small{display:block;font:.7rem var(--f-mono);opacity:.75;margin-top:.15rem}
.tree .trunk{width:2px;height:.9rem;background:var(--line);margin:0 auto .3rem}
.tree .branches{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.5rem,1fr));gap:1rem .7rem}
.tree .br{position:relative;border-top:2px solid var(--line);padding-top:.45rem}
.tree .br h5{margin:0 0 .4rem;font:500 .68rem/1.35 var(--f-mono);letter-spacing:.05em;text-transform:uppercase;color:var(--gold);text-align:center}
.tree .br ul{list-style:none;margin:0;padding:0 0 0 .7rem;border-left:2px solid var(--line)}
.tree .br li{position:relative;margin:.28rem 0;padding-left:.15rem;font:600 .82rem/1.3 var(--f-display);color:var(--ink)}
.tree .br li:before{content:"";position:absolute;left:-.85rem;top:.62rem;width:.6rem;height:2px;background:var(--line)}
.tree .br li i{font:400 .7rem var(--f-mono);font-style:normal;color:var(--muted);margin-left:.3rem}
@media (max-width:520px){.tree .branches{grid-template-columns:1fr 1fr}}
'''


def tree(root, sub, branches, cap):
    br = ''.join(f'<div class="br" style="--i:{i}"><h5>{esc(h)}</h5><ul>' + ''.join(
        f'<li style="--j:{j}">{esc(n)}<i>{esc(y)}</i></li>' for j, (n, y) in enumerate(leaves)) + '</ul></div>'
        for i, (h, leaves) in enumerate(branches))
    return (f'<figure class="fig tree"><div class="root"><b>{esc(root)}</b><small>{esc(sub)}</small></div>'
            f'<div class="trunk"></div><div class="branches">{br}</div><figcaption>{cap}</figcaption></figure>')


def tree_fields(t):
    data = json.load(open(os.path.join(B, 'fields_tree.json'), encoding='utf-8'))
    zhn = {'Shing-Tung Yau': '丘成桐', 'Terence Tao': '陶哲轩'}
    zh = t['lang'] == 'zh'
    branches = [(f'{z if zh else en} · {n}', [((zhn.get(name, name) if zh else name), '') for name, _ in top]) for en, z, n, top in data]
    if zh:
        return tree('AI · OpenAI Math Release', '719 篇稿件 · 稿件最多的九个学科', branches,
                    '<b>Figure 0.</b> AI 稿件最多的九个学科（学科后的数字为稿件数），每个学科下是该学科中参考文献条目最多的三位人类数学家。每个领域，都站在不同的一群人身上。')
    return tree('AI · OpenAI Math Release', '719 manuscripts · the nine largest fields', branches,
                '<b>Figure 0.</b> The nine fields with the most AI manuscripts (number after the field) and, under each, the three human mathematicians '
                'with the most reference entries in that field. Every field rests on a different set of people.')


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
        for n, y in leaves:
            for a, b in names:
                n = n.replace(a, b)
            ls.append((n, y))
        out.append((ZH_HEAD[h], ls))
    return out


def tree_kakeya(t):
    if t['lang'] == 'zh':
        return tree('AI 稿件 · 四维 Kakeya 集', 'OpenAI，2026 · 34 条参考文献',
                    zh_tree(TREE_KAKEYA, [('Hong Wang', '王虹'), ('Guo ·', '郭少明 ·'), ('· Zhang', '· 张瑞祥'), ('Tao', '陶哲轩'), (' (sticky)', '（sticky）')]),
                    '<b>Figure 0.</b> OpenAI 四维 Kakeya 稿件 34 条参考文献的节选，按其所依托的工作脉络分组（分组由我们整理）。')
    return tree('AI manuscript · four-dimensional Kakeya sets', 'OpenAI, 2026 · 34 references', TREE_KAKEYA,
                '<b>Figure 0.</b> A selection of the 34 works cited by OpenAI’s manuscript on four-dimensional Kakeya sets, grouped by us into the lines of work it draws on.')


def tree_ns(t):
    if t['lang'] == 'zh':
        return tree('AI · OpenAI Navier–Stokes 与 Euler 论文', '2026 · 51 条参考文献',
                    zh_tree(TREE_NS, [('Tao', '陶哲轩'), ('Hou', '侯一钊'), ('Kato', '加藤敏夫'), ('Euler', '欧拉'), ('Navier', '纳维'),
                                      ('Stokes', '斯托克斯'), ('Leray', '勒雷'), (' (Clay statement)', '（克雷问题陈述）')]),
                    '<b>Figure 0.</b> OpenAI Navier–Stokes 与 Euler 论文所引文献的节选，分组由我们整理：从欧拉到今天，269 年。')
    return tree('AI · OpenAI Navier–Stokes and Euler papers', '2026 · 51 references', TREE_NS,
                '<b>Figure 0.</b> A selection of the works cited by OpenAI’s Navier–Stokes and Euler papers, grouped by us: 269 years from Euler to today.')


def tree_af(t):
    if t['lang'] == 'zh':
        return tree('AI · AlphaFold 2', 'DeepMind，Nature 2021 · 84 条参考文献',
                    zh_tree(TREE_AF, [('Anfinsen', '安芬森'), ('Zhang · Skolnick', '张阳 · Skolnick'), (' (NMR)', '（核磁共振）'),
                                      (' (cryo-EM)', '（冷冻电镜）'), (' (CASP)', '（CASP）'), (' (AlphaFold 1)', '（AlphaFold 1）'),
                                      (' (trRosetta)', '（trRosetta）'), (' (PSICOV)', '（PSICOV）'), (' (ResNet)', '（ResNet）'), (' (BERT)', '（BERT）')]),
                    '<b>Figure 0.</b> AlphaFold 2 论文所引文献的节选，分组由我们整理：半个世纪的结构生物学、协同进化与机器学习。')
    return tree('AI · AlphaFold 2', 'DeepMind, Nature 2021 · 84 references', TREE_AF,
                '<b>Figure 0.</b> A selection of the works cited by the AlphaFold 2 paper, grouped by us: half a century of structural biology, coevolution and machine learning.')


FIGS.update({'tree_fields': tree_fields, 'tree_kakeya': tree_kakeya, 'tree_ns': tree_ns, 'tree_af': tree_af})


# ---- the navigation loop: scientists and AI, each turn producing data that carries signal ---------
LOOP = {
 'zh': dict(steps=[('sci', '科学家', '提出值得解的问题，定下“正确”的标准'),
                   ('ai', 'AI', '大规模采样：成千上万次尝试'),
                   ('sci', '验证器', '人建立的标准，留下通过检验的尝试'),
                   ('sci', '科学家', '评判哪些结果成立、哪些重要'),
                   ('data', '新的数据', '带着学习信号，进入下一轮训练')],
            back='↻ 下一个问题',
            cap='<b>Figure 0.</b> 领航循环。AI 再强大，也需要有人指方向。科学家与 AI 合作，每转一圈，就产生一批带着学习信号的新数据。'),
 'en': dict(steps=[('sci', 'Scientists', 'pose a problem worth solving and define what counts as correct'),
                   ('ai', 'AI', 'samples at scale: thousands of attempts'),
                   ('sci', 'Verifier', 'built on human standards, keeps the attempts that pass'),
                   ('sci', 'Scientists', 'judge which results hold and which matter'),
                   ('data', 'New data', 'carrying a learning signal, feeds the next round of training')],
            back='↻ the next problem',
            cap='<b>Figure 0.</b> The navigation loop. However capable AI becomes, someone has to set the direction. Scientists and AI work together, and each turn of the loop produces new data that carries a learning signal.'),
}


def loop(t):
    L = LOOP[t['lang']]
    steps = ''.join(f'<li class="{c}" style="--i:{i}"><b>{esc(h)}</b><span>{esc(d)}</span></li>' for i, (c, h, d) in enumerate(L['steps']))
    return (f'<figure class="fig loopfig"><ol class="loop5">{steps}</ol><div class="loopback">{esc(L["back"])}</div>'
            f'<figcaption>{L["cap"]}</figcaption></figure>')


FIGS['loop'] = loop

CSS += """
.loop5{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(5,1fr);gap:.5rem}
.loop5 li{position:relative;border-radius:6px;padding:.6rem .65rem;line-height:1.4;border:1.5px solid var(--rule);background:var(--paper);margin:0}
.loop5 li b{display:block;font:600 .92rem var(--f-display);margin-bottom:.15rem}
.loop5 li span{font-size:.8rem;color:var(--muted)}
.loop5 li.sci{background:var(--gold-soft);border-color:var(--gold-soft)}.loop5 li.sci b{color:var(--gold)}
.loop5 li.ai{background:var(--ink);border-color:var(--ink)}.loop5 li.ai b{color:var(--paper)}.loop5 li.ai span{color:var(--paper);opacity:.8}
.loop5 li.data{border-color:var(--use)}.loop5 li.data b{color:var(--use)}
.loop5 li:not(:last-child):after{content:"→";position:absolute;right:-.52rem;top:50%;transform:translate(50%,-50%);color:var(--muted);font-size:.8rem;z-index:1}
.loopback{margin-top:.5rem;border:1.5px dashed var(--rule);border-top:0;border-radius:0 0 8px 8px;text-align:center;font:.72rem var(--f-mono);color:var(--muted);padding:.25rem}
@media (max-width:760px){.loop5{grid-template-columns:1fr}.loop5 li:not(:last-child):after{content:"↓";right:50%;top:auto;bottom:-.5rem;transform:translate(50%,50%)}}
@keyframes lit{0%,16%{box-shadow:0 0 0 3px var(--use);transform:translateY(-3px)}22%,100%{box-shadow:none;transform:none}}
/* motion: figures play once when scrolled into view (html.js is set by a script; without JS everything is simply visible) */
@media (prefers-reduced-motion:no-preference){
 .loopfig.in .loop5 li{animation:lit 10s calc(var(--i)*2s) infinite}
 html.js figure.tree .root{opacity:0;transform:translateY(-8px);transition:opacity .5s,transform .5s}
 html.js figure.tree .trunk{transform:scaleY(0);transform-origin:top;transition:transform .35s .35s}
 html.js figure.tree .br{opacity:0;transform:translateY(10px);transition:opacity .5s,transform .5s;transition-delay:calc(.6s + var(--i)*.16s)}
 html.js figure.tree .br li{opacity:0;transform:translateX(-8px);transition:opacity .35s,transform .35s;transition-delay:calc(.85s + var(--i)*.16s + var(--j)*.08s)}
 html.js figure.tree.in .root,html.js figure.tree.in .br,html.js figure.tree.in .br li{opacity:1;transform:none}
 html.js figure.tree.in .trunk{transform:scaleY(1)}
 html.js .stages .stage{opacity:0;transform:translateY(10px);transition:opacity .5s,transform .5s;transition-delay:calc(var(--i)*.25s)}
 html.js figure.in .stages .stage{opacity:1;transform:none}
 html.js .dots i{opacity:0;transform:scale(.3);transition:opacity .25s,transform .25s;transition-delay:calc(var(--k)*28ms)}
 html.js figure.in .dots i{opacity:1;transform:none}
 html.js .hist .bar{transform:scaleY(0);transform-box:fill-box;transform-origin:bottom;transition:transform .6s;transition-delay:calc(var(--k)*45ms)}
 html.js .hist.in .bar{transform:scaleY(1)}
}
html.js.shown figure.fig:not(.in) *{opacity:1!important;transform:none!important}
@media print{html.js figure.fig *{opacity:1!important;transform:none!important}}
@media (max-width:760px){figure.fig{width:auto!important;left:auto!important;transform:none!important}}
"""
