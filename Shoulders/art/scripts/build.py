"""Builds art/index.html (English) and art/zh/index.html from refs.json (the ART preprint, Anthropic 2026)."""
import os, sys, json, html, re, unicodedata
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
sys.path.insert(0, ROOT)
from common import page, chips, tribute_button, TOPIC_CSS, RANK_JS

D = json.load(open(S + '/refs.json', encoding='utf-8'))
RENAME = {'Y Ishino': 'Yoshizumi Ishino', 'H Shinagawa': 'Hideo Shinagawa', 'K Makino': 'Kozo Makino',
          'M Amemura': 'Mitsuko Amemura', 'A Nakata': 'Atsuo Nakata'}   # Crossref gives initials only for the 1987 paper
for r in D['refs']:
    r['a'] = [RENAME.get(a, a) for a in r['a']]
esc = html.escape
AI_YEAR = 2026

# Nobel Prize in Chemistry among the cited authors (nobelprize.org).
NOBEL = {'doudna j': 2020, 'charpentier e': 2020, 'hassabis d': 2024, 'jumper j': 2024, 'baker d': 2024}
ZH = {'Feng Zhang': '张锋', 'Jennifer A. Doudna': '杜德纳', 'Demis Hassabis': '哈萨比斯', 'John Jumper': '江珀', 'Yang Zhang': '张阳'}


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
LINKS = {'paper': D['url'], 'pdf': D['url'] + '.full.pdf', 'post': 'https://www.anthropic.com/research',
         'news': 'https://theprint.in/science/did-claude-discover-a-new-enzyme-or-stole-a-biologists-work-anthropic-responds/3057122/'}

T = {
 'zh': dict(
  title='从逆转录子到 ART · 巨人之肩',
  desc='Anthropic 的 Claude 智能体在噬菌体 DNA 中找到一类新的逆转录酶系统 ART。这篇预印本引用了哪些人类科学家。',
  back='← 巨人之肩', alt=('English', '../'),
  h1='从逆转录子到 ART：<br>AI 智能体在噬菌体里找到的酶',
  dek=['2026 年 9 月，Anthropic 宣布它的 Claude 智能体在海量宏基因组数据里找到一类此前没有被描述过的逆转录酶系统，命名为 ART：一个逆转录酶、一个相邻的伙伴基因，以及一长串约 200 个核苷酸的重复单元。预印本于 10 月 11 日发布在 bioRxiv，尚未经过同行评审。据论文，智能体在约 21.5 小时里完成 949 次会话，检索了 19 亿个蛋白质簇；研究方向和最后的审阅由人完成。ART 的功能目前还不清楚。',
       f'这一发现站在几十年的人类工作上：1987 年石野良纯等人在大肠杆菌里第一次看到奇怪的重复序列，后来它被认出是 CRISPR；逆转录子、噬菌体防御系统、细菌逆转录酶的多样性，一项项被测序、命名、实验验证。智能体检索的数据库本身，也是全世界研究者多年提交的序列。论文列出 {NREF} 条参考文献，我们逐条找出背后的人。',
       '还有看不见的部分。据媒体报道，哥本哈根大学 Mario Rodríguez Mestre 的团队说，他们自 2022 年起就在研究同一批酶，只是尚未发表；Anthropic 表示不知道有已发表的相关工作。这篇预印本引用了 Mestre 参与的三篇关于细菌逆转录酶的论文。论文还写道，这个位点所在噬菌体 2021 年的基因组报告已经识别出其中的逆转录酶，只是没有描述重复序列和伙伴基因。'],
  ms=[('石野良纯 · CRISPR 重复', 1987), ('Zimmerly · 细菌逆转录酶', 2015), ('Doron · 抗噬菌体系统', 2018), ('Millman · 逆转录子', 2020),
      ('Mestre · 逆转录子三元系统', 2020), ('Korn · MarsHill 噬菌体', 2021), ('Mestre · UG/Abi', 2022), ('Tang · Wilkinson', 2024)],
  links=[('bioRxiv 预印本', LINKS['paper']), ('PDF 全文', LINKS['pdf']), ('优先权争议报道（ThePrint）', LINKS['news'])],
  st=[(1, 'AI 预印本（bioRxiv 2026）'), (NREF, '条参考文献'), (len(people), '位被引用的科学家'), (NOB, '位诺贝尔化学奖得主'), (SPAN, f'年跨度（{Y0}–{AI_YEAR}）')],
  colH='向下追溯', colP='最上方是 AI 的结果，往下是它引用的人类工作，按年份一路回溯。金色标签为诺贝尔化学奖得主；点“正文怎样引用”可看论文原句。',
  ai='AI · Anthropic', aiS='Claude 智能体发现带串联重复阵列的逆转录酶（ART）',
  how=lambda n: f'正文怎样引用（{n}）', citedIn='参考文献', etal='等',
  eras=[(2020, '2020 年代'), (2010, '2010 年代'), (2000, '2000 年代'), (1980, '1980–1999'), (0, '1960–1979')],
  tAll=lambda n: f'向这 {n} 位科学家致敬', tDone='已致敬 · 谢谢你', tCount='次致敬',
  rankH='被引用的科学家', rankP='默认按参考文献条目数排名：论文列出某人的一项工作计一次。',
  metL='排名依据', mR='参考文献条目', mT='正文引用', more='更多排名方式', less='收起',
  showAll=lambda n: f'显示全部 {n} 位', showLess='收起',
  refH='参考文献原文', refP='保留原始编号；右侧数字为该条在正文与方法中被引用的次数。有 9 条在原文中以“等”省略了作者，且无法从 DOI 补全，这些条目只列出第一作者。',
  foot='由 <a href="https://huggingface.co/SeaFill2025">Sea-Fill 开源科学团队</a>制作。参考文献与正文原句来自预印本 PDF，作者名单经 Crossref 补全；优先权争议部分依据媒体报道。引用不等于依赖；本页不评判结果的正确性、原创性或归属。',
 ),
 'en': dict(
  title='From retrons to ART · On Whose Shoulders',
  desc='Anthropic’s Claude agents found a new family of reverse-transcriptase systems, ART, in phage DNA. Which human scientists does the preprint cite?',
  back='← On Whose Shoulders', alt=('中文', 'zh/'),
  h1='From retrons to ART:<br>an enzyme system found by AI agents',
  dek=['In September 2026 Anthropic announced that its Claude agents had found, in vast metagenomic data, a previously undescribed family of reverse-transcriptase systems it calls ART: a reverse transcriptase, a neighbouring partner gene and a long array of roughly 200-nucleotide repeats. The preprint was posted on bioRxiv on 11 October and has not been peer reviewed. According to the paper, the agents ran 949 sessions over about 21.5 hours across 1.9 billion protein clusters; people set the research brief and reviewed the results. What ART does is not yet known.',
       f'The finding rests on decades of human work: in 1987 Yoshizumi Ishino and colleagues first saw odd repeats in E. coli that were later recognised as CRISPR; retrons, anti-phage defence systems and the diversity of bacterial reverse transcriptases were sequenced, named and tested one by one. The databases the agents searched are themselves sequences submitted by researchers worldwide over many years. The preprint lists {NREF} references. We traced the people behind every one.',
       'Some of it is not visible. According to press reports, a University of Copenhagen team led by Mario Rodríguez Mestre says it has studied the same enzymes since 2022 but has not yet published; Anthropic says it knew of no published work. The preprint cites three earlier papers on bacterial reverse transcriptases that Mestre co-authored. It also notes that the 2021 genome report of the phage carrying this locus had already identified its reverse transcriptase, without describing the repeats or the partner gene.'],
  ms=[('Ishino · CRISPR repeats', 1987), ('Zimmerly · bacterial RTs', 2015), ('Doron · anti-phage systems', 2018), ('Millman · retrons', 2020),
      ('Mestre · retron tripartite systems', 2020), ('Korn · MarsHill phage', 2021), ('Mestre · UG/Abi', 2022), ('Tang · Wilkinson', 2024)],
  links=[('bioRxiv preprint', LINKS['paper']), ('Full-text PDF', LINKS['pdf']), ('Priority dispute (ThePrint)', LINKS['news'])],
  st=[(1, 'AI preprint (bioRxiv 2026)'), (NREF, 'reference entries'), (len(people), 'scientists cited'), (NOB, 'Nobel laureates in Chemistry'), (SPAN, f'years spanned ({Y0}–{AI_YEAR})')],
  colH='Tracing back', colP='The AI result sits at the top; below it are the human works it cites, by year. Gold tags mark Nobel laureates in Chemistry; open “How it is cited” for the sentences in the paper.',
  ai='AI · Anthropic', aiS='Claude agents discover reverse transcriptases with tandem repeat arrays (ART)',
  how=lambda n: f'How it is cited ({n})', citedIn='Reference', etal='et al.',
  eras=[(2020, '2020s'), (2010, '2010s'), (2000, '2000s'), (1980, '1980–1999'), (0, '1960–1979')],
  tAll=lambda n: f'Pay tribute to these {n} scientists', tDone='Tribute paid · thank you', tCount='tributes',
  rankH='Scientists cited', rankP='Ranked by reference entries by default: the paper listing one of their works counts once.',
  metL='Rank by', mR='Reference entries', mT='In-text citations', more='More ranking options', less='Fewer options',
  showAll=lambda n: f'Show all {n}', showLess='Show fewer',
  refH='Reference list', refP='Original numbering; the number on the right is how often the entry is cited in the text and Methods. Nine entries abbreviate their authors with “et al.” in the original and cannot be completed from a DOI; they show the first author only.',
  foot='Made by <a href="https://huggingface.co/SeaFill2025">Sea-Fill</a>, an open-source science team. References and in-text sentences come from the preprint PDF; author lists are completed from Crossref; the priority dispute is based on press reports. Citation is not dependence; this page does not judge the correctness, originality or attribution of the results.',
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
        + f'<span class="arr">→</span><span class="ms now"><b>ART</b><i>{AI_YEAR}</i></span></div>')
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
