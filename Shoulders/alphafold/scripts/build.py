"""Builds alphafold/index.html (English) and alphafold/zh/index.html from refs.json."""
import os, sys, json, html, re, unicodedata
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
sys.path.insert(0, ROOT)
from common import page, chips, tribute_button, TOPIC_CSS, RANK_JS

D = json.load(open(S + '/refs.json', encoding='utf-8'))
RENAME = {'A. Klug': 'Aaron Klug'}               # initials only in the reference list
for r in D['refs']:
    r['a'] = [RENAME.get(a, a) for a in r['a']]
esc = html.escape
AI_YEAR = 2021

# Nobel Prize in Chemistry among the cited authors (nobelprize.org).
NOBEL = {'anfinsen c': 1972, 'klug a': 1982, 'wuthrich k': 2002, 'baker d': 2024, 'hassabis d': 2024, 'jumper j': 2024}
ZH = {'Christian B. Anfinsen': '安芬森', 'Aaron Klug': '克鲁格', 'Kurt Wüthrich': '维特里希', 'David Baker': '大卫·贝克',
      'Demis Hassabis': '哈萨比斯', 'John Jumper': '江珀', 'Yang Zhang': '张阳', 'Jinbo Xu': '许锦波', 'Jianyi Yang': '杨建益'}


def pkey(name):
    """Surname + first initial, so 'C. Sander' and 'Chris Sander' are one person."""
    w = name.replace(',', ' ').split()
    f = lambda s: unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return f(w[-1]) + ' ' + f(w[0])[:1] if len(w) > 1 else f(name)


def prizes(name):
    y = NOBEL.get(pkey(name))
    return {'nc': y} if y else {}


people = {}
for r in D['refs']:
    for a in r['a']:
        q = people.setdefault(pkey(a), dict(n=a, r=0, t=0))
        if len(a) > len(q['n']):
            q['n'] = a
        q['r'] += 1
        q['t'] += len(r['c'])
works = sorted(D['refs'], key=lambda r: (-int(r['y'] or 0), r['n']))
NREF = len(D['refs'])
Y0 = min(int(r['y']) for r in D['refs'] if r['y'])
SPAN = AI_YEAR - Y0
NOB = sum(1 for k in people if k in NOBEL)
LINKS = {'paper': D['url'], 'pmc': 'https://europepmc.org/article/PMC/PMC8371605',
         'db': 'https://alphafold.ebi.ac.uk/', 'nobel': 'https://www.nobelprize.org/prizes/chemistry/2024/summary/'}

T = {
 'zh': dict(
  title='从安芬森到 AlphaFold · 巨人之肩',
  desc='AlphaFold 2 论文（Nature 2021）引用了哪些人类科学家：从 1973 年安芬森的序列决定结构，到 2021 年。',
  back='← 巨人之肩', alt=('English', '../'),
  h1=f'从安芬森到 AlphaFold：<br>蛋白质结构预测的 {SPAN} 年',
  dek=['2021 年 7 月，DeepMind 在《自然》发表 AlphaFold 2 论文，以接近实验的精度从氨基酸序列预测蛋白质的三维结构。2024 年诺贝尔化学奖的一半授予 Demis Hassabis 与 John Jumper 的蛋白质结构预测，另一半授予 David Baker 的计算蛋白质设计。',
       f'这一步站在半个世纪的积累之上：安芬森证明序列决定结构；X 射线晶体学、核磁共振与冷冻电镜测出一个又一个结构，蛋白质数据库把它们向全世界开放；CASP 竞赛二十多年推动着预测方法；协同进化分析从序列中读出残基之间的接触。论文列出 {NREF} 条参考文献，我们逐条找出背后的人。'],
  ms=[('安芬森', 1973), ('Altschuh · 克鲁格', 1987), ('Qian · Sejnowski', 1988), ('Šali · Blundell', 1993), ('CASP · Moult', 1995),
      ('Weigt 等', 2009), ('Marks 等', 2011), ('AlphaFold 1', 2020), ('trRosetta · 大卫·贝克', 2020)],
  links=[('Nature 论文', LINKS['paper']), ('全文（Europe PMC）', LINKS['pmc']), ('AlphaFold 数据库', LINKS['db']), ('2024 诺贝尔化学奖', LINKS['nobel'])],
  st=[(1, 'AI 论文（Nature 2021）'), (NREF, '条参考文献'), (len(people), '位被引用的科学家'), (NOB, '位诺贝尔化学奖得主'), (SPAN, f'年跨度（{Y0}–{AI_YEAR}）')],
  colH='向下追溯', colP='最上方是 AI 的结果，往下是它引用的人类工作，按年份一路回到 1973 年。金色标签为诺贝尔化学奖得主；点“正文怎样引用”可看论文原句。',
  ai='AI · DeepMind', aiS='AlphaFold 2：高精度蛋白质结构预测',
  how=lambda n: f'正文怎样引用（{n}）', citedIn='参考文献', etal='等',
  eras=[(2020, '2020 年代'), (2010, '2010 年代'), (2000, '2000 年代'), (1980, '1980–1999'), (0, '1970 年代：序列决定结构')],
  tAll=lambda n: f'向这 {n} 位科学家致敬', tDone='已致敬 · 谢谢你', tCount='次致敬',
  rankH='被引用的科学家', rankP='默认按参考文献条目数排名：论文列出某人的一项工作计一次。',
  metL='排名依据', mR='参考文献条目', mT='正文引用', more='更多排名方式', less='收起',
  showAll=lambda n: f'显示全部 {n} 位', showLess='收起',
  refH='参考文献原文', refP='保留原始编号；右侧数字为该条在正文与图注中被引用的次数。共有 8 条参考文献在原文中以“等”省略了作者，且无法从 DOI 补全，这些条目只列出第一作者。',
  foot='由 <a href="https://huggingface.co/SeaFill2025">Sea-Fill 开源科学团队</a>制作。参考文献与正文原句来自论文的开放获取全文，作者名单经 Crossref 补全。引用不等于依赖；本页不评判结果的正确性、原创性或归属。',
 ),
 'en': dict(
  title='From Anfinsen to AlphaFold · On Whose Shoulders',
  desc='Which human scientists does the AlphaFold 2 paper (Nature 2021) cite? From Anfinsen’s sequence-determines-structure in 1973 to 2021.',
  back='← On Whose Shoulders', alt=('中文', 'zh/'),
  h1=f'From Anfinsen to AlphaFold:<br>{SPAN} years of protein structure prediction',
  dek=['In July 2021 DeepMind published the AlphaFold 2 paper in Nature, predicting the three-dimensional structure of proteins from their amino-acid sequence with near-experimental accuracy. Half of the 2024 Nobel Prize in Chemistry went to Demis Hassabis and John Jumper for protein structure prediction, the other half to David Baker for computational protein design.',
       f'That step rests on half a century of human work: Anfinsen showed that sequence determines structure; X-ray crystallography, NMR and cryo-EM solved structure after structure, and the Protein Data Bank opened them to the world; the CASP experiment drove prediction methods for over two decades; coevolution analysis read residue contacts out of sequences. The paper lists {NREF} references. We traced the people behind every one.'],
  ms=[('Anfinsen', 1973), ('Altschuh · Klug', 1987), ('Qian · Sejnowski', 1988), ('Šali · Blundell', 1993), ('CASP · Moult', 1995),
      ('Weigt et al.', 2009), ('Marks et al.', 2011), ('AlphaFold 1', 2020), ('trRosetta · Baker', 2020)],
  links=[('Nature paper', LINKS['paper']), ('Full text (Europe PMC)', LINKS['pmc']), ('AlphaFold database', LINKS['db']), ('2024 Nobel Prize in Chemistry', LINKS['nobel'])],
  st=[(1, 'AI paper (Nature 2021)'), (NREF, 'reference entries'), (len(people), 'scientists cited'), (NOB, 'Nobel laureates in Chemistry'), (SPAN, f'years spanned ({Y0}–{AI_YEAR})')],
  colH='Tracing back', colP='The AI result sits at the top; below it are the human works it cites, by year, back to 1973. Gold tags mark Nobel laureates in Chemistry; open “How it is cited” for the sentences in the paper.',
  ai='AI · DeepMind', aiS='AlphaFold 2: highly accurate protein structure prediction',
  how=lambda n: f'How it is cited ({n})', citedIn='Reference', etal='et al.',
  eras=[(2020, '2020s'), (2010, '2010s'), (2000, '2000s'), (1980, '1980–1999'), (0, '1970s: sequence determines structure')],
  tAll=lambda n: f'Pay tribute to these {n} scientists', tDone='Tribute paid · thank you', tCount='tributes',
  rankH='Scientists cited', rankP='Ranked by reference entries by default: the paper listing one of their works counts once.',
  metL='Rank by', mR='Reference entries', mT='In-text citations', more='More ranking options', less='Fewer options',
  showAll=lambda n: f'Show all {n}', showLess='Show fewer',
  refH='Reference list', refP='Original numbering; the number on the right is how often the entry is cited in the text and figure legends. Eight entries abbreviate their authors with “et al.” in the original and cannot be completed from a DOI; they show the first author only.',
  foot='Made by <a href="https://huggingface.co/SeaFill2025">Sea-Fill</a>, an open-source science team. References and in-text sentences come from the paper’s open-access full text; author lists are completed from Crossref. Citation is not dependence; this page does not judge the correctness, originality or attribution of the results.',
 ),
}

CSS = TOPIC_CSS + '.thanks{margin:1.6rem 0 0 6rem}\n@media (max-width:560px){.thanks{margin-left:4.3rem}}\n'


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
        f'<span class="ms"><b>{esc(n)}</b><i>{y}</i></span>' for n, y in t['ms'])
        + f'<span class="arr">→</span><span class="ms now"><b>AlphaFold 2</b><i>{AI_YEAR}</i></span></div>')
    out.append('<div class="links">' + ''.join(f'<a href="{u}">{esc(n)}</a>' for n, u in t['links']) + '</div>')
    out.append('<div class="stats">' + ''.join(f'<div class="stat"><b>{n:,}</b><span>{esc(l)}</span></div>' for n, l in t['st']) + '</div>')

    col = [f'<div class="ai"><b>{t["ai"]}</b><span>{esc(t["aiS"])}</span><em>{AI_YEAR}</em></div>']
    era_i = -1
    for w in works:
        y = int(w['y'] or 0)
        e = next(i for i, (lo, _) in enumerate(t['eras']) if y >= lo)
        if e != era_i:
            col.append(f'<div class="era">{t["eras"][e][1]}</div>')
            era_i = e
        pz = [prizes(a) for a in w['a']]
        shown = list(zip(w['a'], pz))
        more = ''
        if len(shown) > 8:                      # long author lists: first six, then the laureates, then a count
            keep = shown[:6] + [x for x in shown[6:] if x[1]]
            more = f' <span class="lat">+{len(shown) - len(keep)}</span>'
            shown = keep
        names = '<span class="sep">, </span>'.join(name_html(a, lang, bool(p)) + chips(p, lang) for a, p in shown) + more
        if w['etal']:
            names += f' <span class="lat">{t["etal"]}</span>'
        title = f'<a href="{esc(w["u"])}">{esc(w["t"])}</a>' if w['u'] else esc(w['t'])
        det = ''
        if w['c']:
            det = f'<details><summary>{t["how"](len(w["c"]))}</summary>' + ''.join(
                f'<blockquote>{esc(c["s"])}</blockquote>' for c in w['c']) + '</details>'
        cls = 'w' + (' laur' if any(pz) else '') + (' classic' if y and y < 1990 else '')
        col.append(f'<div class="{cls}"><div class="yr">{w["y"] or "—"}</div><div><div class="who">{names}</div>'
                   f'<div class="ti">{title}</div><div class="by">{t["citedIn"]}<i>[{w["n"]}]</i></div>{det}</div></div>')
    out.append(f'<section class="sec"><span class="eyebrow">{t["colH"]}</span><p class="lead">{t["colP"]}</p><div class="col">' + '\n'.join(col) + '</div></section>')

    m = json.dumps(dict(l=t['metL'], r=t['mR'], t=t['mT'], more=t['more'], less=t['less'], ks=['r', 't']), ensure_ascii=False)
    rows = []
    for q in sorted(people.values(), key=lambda q: (-q['r'], -q['t'], q['n'])):
        zh = ZH.get(q['n']) if lang == 'zh' else None
        nm = f'{esc(zh)}<small>{esc(q["n"])}</small>' if zh else esc(q['n'])
        rows.append(f'<li data-r="{q["r"]}" data-t="{q["t"]}" data-p="1"><span class="nm">{nm}{chips(prizes(q["n"]), lang)}</span><span></span><span class="ct">{q["r"]}</span></li>')
    out.append(f'<section class="sec"><span class="eyebrow">{t["rankH"]}</span><p class="lead">{t["rankP"]}</p>'
               f'<div class="metsw" data-m="{esc(m)}"></div><ol class="rank">' + ''.join(rows) + '</ol>'
               f'<button type="button" class="toggle" data-all="{esc(t["showAll"](len(people)))}" data-less="{esc(t["showLess"])}"></button></section>')

    items = ''.join(f'<li value="{r["n"]}"><span class="n">{len(r["c"])}×</span><b>{esc(", ".join(r["a"][:6]) + (" …" if len(r["a"]) > 6 else "") + (" " + t["etal"] if r["etal"] else ""))}</b>, '
                    + (f'<a href="{esc(r["u"])}">{esc(r["t"])}</a>' if r['u'] else esc(r['t'])) + f' ({r["y"]})</li>' for r in D['refs'])
    out.append(f'<section class="sec"><span class="eyebrow">{t["refH"]}</span><p class="lead">{t["refP"]}</p><div class="refs" style="grid-template-columns:1fr">'
               f'<div><h3><a href="{D["url"]}">{esc(D["title"])}</a></h3><ol>{items}</ol></div></div></section>')
    out.append(f'<footer>{t["foot"]}</footer>')
    return page(lang, t['title'], t['desc'], CSS, '\n'.join(out) + RANK_JS)


base = os.path.dirname(S)
for lang, path in (('zh', 'zh/index.html'), ('en', 'index.html')):
    f = os.path.join(base, path)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(build(lang))
print('ok', len(works), 'works,', len(people), 'people,', NOB, 'Nobel laureates')
