"""Builds the essay pages from Markdown: blog/en.md -> blog/index.html, blog/zh.md -> blog/zh/index.html.
The design (theme_en.css, theme_zh.css) is the essay's own: a dark hero with a timeline, key numbers, a reading
column with wide figures, and a call to action. Numbers come from the math data and decades.json."""
import os, sys, re, html, json, collections
B = os.path.dirname(os.path.abspath(__file__))
H = os.path.dirname(B)
sys.path.insert(0, H)
from common import GC
import figures
from refs import REFS

# ---- key numbers, read from the data embedded in the math page (as the hub does) ---------------------
_h = open(os.path.join(H, 'math', 'index.html'), encoding='utf-8').read()
M, _ = json.JSONDecoder().raw_decode(_h[_h.index('{"gen"'):].replace('<\\/', '</'))
_ent = collections.Counter()
for p in M['papers']:
    for r in p['r']:
        _ent.update(r[0])
_A = M['authors']
STATS = [len(M['papers']), M['works'], len(_A),
         sum(1 for k in _ent if not _A[k]['n'].startswith('init:') and any(x in _A[k] for x in ('fm', 'ab', 'wf')))]
assert M['works'] == figures.DEC['works'], 'decades.json is out of date'

FONTS = {'en': 'family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600',
         'zh': 'family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;900'
               '&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600'}

# additions to the theme: what the reading column needs for the full text (citations, lists, references)
CSS = '''
.sf-article ul{margin:0 0 1.2em;padding-left:1.2em}
.sf-article li{margin:.5em 0}
.sf-article li::marker{color:var(--accent)}
.sf-fig + .sf-article{padding-top:0}
.sf-article > h2:first-child{margin-top:1.2em}
.sf-cite{font-family:var(--mono);font-size:.72em;white-space:nowrap;color:var(--muted)}
.sf-cite a{text-decoration:none}
.sf-cite a:hover{text-decoration:underline}
.sf-refs ol{margin:0;padding-left:2.2em;font-size:14px;line-height:1.65;color:var(--muted)}
.sf-refs li{margin:.55em 0;overflow-wrap:anywhere}
.sf-refs li::marker{color:var(--muted);font-family:var(--mono);font-size:12px}
.sf-refs li b{color:var(--text);font-weight:500}
.sf-refs a{color:inherit}
.sf-refs li:target{background:var(--soft);box-shadow:0 0 0 6px var(--soft);border-radius:2px}
.sf-citebox pre{margin:0 0 12px;white-space:pre-wrap;word-break:break-word;background:var(--soft);border-radius:6px;padding:16px 18px;font:13px/1.6 var(--mono);color:var(--text)}
.sf-citebox p{font-size:14px;color:var(--muted)}
.sf-cta p.sf-foot{font-size:12px;color:var(--on-ink-muted);margin:64px 0 0;max-width:none}
'''


ORDER = []


def cites(m):
    keys = [k.strip().lstrip('@') for k in m.group(1).split(';')]
    out = []
    for k in keys:
        assert k in REFS, k
        if k not in ORDER:
            ORDER.append(k)
        n = ORDER.index(k) + 1
        out.append(f'<a href="#ref-{k}">{n}</a>')
    return '<span class="sf-cite">[' + ', '.join(out) + ']</span>'


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\s*\[(@[^\]]+)\]', lambda m: ' ' + cites(m), s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'([。：])</b> ', r'\1</b>', s)                     # no gap after a Chinese run-in heading
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s


def names(a):
    return ', '.join(a[:-1]) + ' and ' + a[-1] if len(a) > 1 and a[-1] != 'others' else (a[0] + ' et al.' if a[-1] == 'others' else a[0])


def fmt(r):
    link = f'https://doi.org/{r["doi"]}' if r.get('doi') else r.get('url', '')
    venue = r.get('journal') or r.get('booktitle') or r.get('publisher') or r.get('howpublished') or ''
    if r.get('series'):
        venue += f', {r["series"]} {r.get("volume", "")}'
    elif r.get('volume'):
        venue += f' {r["volume"]}'
    if r.get('pages'):
        venue += f', {r["pages"]}'
    t = f'{html.escape(names(r["author"]).rstrip("."))}. <b>{html.escape(r["title"])}</b>.'
    if venue:
        t += f' <i>{html.escape(venue.strip())}</i>,'
    t += f' {r["year"]}.'
    if r.get('note'):
        t += f' {html.escape(r["note"])}.'
    if link:
        t += f' <a href="{html.escape(link)}">{html.escape(link.replace("https://", ""))}</a>'
    return t


def bibtex(key, r):
    corp = {'OpenAI', 'DeepSeek-AI', 'The mathlib Community', 'Sea-Fill Team'}
    f = {'author': ' and '.join('{' + a + '}' if a in corp else a for a in r['author'])}
    for k in ('title', 'journal', 'booktitle', 'series', 'volume', 'pages', 'publisher', 'howpublished', 'year', 'doi', 'url', 'note'):
        if r.get(k):
            f[k] = r[k]
    body = ',\n'.join(f'  {k} = {{{v}}}' for k, v in f.items())
    return f'@{r["type"]}{{{key},\n{body}\n}}'


def parse(md):
    """Front matter, the essay as a list of ('text' | 'fig', html) parts, the closing call to action, and the footnote."""
    meta, lines = {}, md.split('\n')
    while lines and re.match(r'^\w+: ', lines[0]):
        k, v = lines.pop(0).split(': ', 1)
        meta[k] = v
    notes = [l for l in lines if re.match(r'^\[\^\w+\]: ', l)]
    meta['note'] = re.sub(r'^\[\^\w+\]: ', '', notes[0]) if notes else ''
    lines = [l for l in lines if l not in notes]
    parts, cta, n = [], None, 0
    for b in re.split(r'\n\s*\n', '\n'.join(lines).strip()):
        if b == '{{cta}}':
            cta = dict(h='', p=[], links=[])
        elif cta is not None:
            m = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', b)
            if m:
                cta['links'].append(m.groups())
            elif b.startswith('## '):
                cta['h'] = b[3:]
            else:
                cta['p'].append(inline(' '.join(b.split())))
        elif b.startswith('{{fig:'):
            n += 1
            parts.append(('fig', figures.render(b[6:-2], LANG, n)))
        elif b.startswith('# '):
            meta['h1'] = '<br>'.join(html.escape(x.strip(), quote=False) for x in b[2:].split('|'))
        elif b.startswith('## '):
            parts.append(('text', f'<h2>{inline(b[3:])}</h2>'))
        elif all(l.startswith('- ') for l in b.split('\n')):
            parts.append(('text', '<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in b.split('\n')) + '</ul>'))
        else:
            parts.append(('text', f'<p>{inline(" ".join(b.split()))}</p>'))
    return meta, parts, cta


def flow(parts):
    """Text runs in the reading column; figures break out of it to the wide measure."""
    out, run = [], []
    for kind, h in parts + [('fig', '')]:
        if kind == 'text':
            run.append(h)
            continue
        if run:
            out.append('<article class="sf-article">\n' + '\n'.join(run) + '\n</article>')
            run = []
        out.append(h)
    return '\n'.join(x for x in out if x)


L10N = {
 'en': dict(out='index.html', hub='../', hub_label='← SEA-FILL · ON WHOSE SHOULDERS', nav='Site', url='https://seafill.info/Shoulders/blog/',
            refs='References', cite='Cite this essay', bib='All references as BibTeX: ', hw=600,
            og='{w:,} human works by {a:,} mathematicians stand behind OpenAI’s {p} AI-written math manuscripts.',
            foot='OPEN DATA (APACHE 2.0 SOURCE)'),
 'zh': dict(out='zh/index.html', hub='../../zh/', hub_label='← SEA-FILL · 巨人之肩', nav='站点', url='https://seafill.info/Shoulders/blog/zh/',
            refs='参考文献', cite='引用本文', bib='全部参考文献的 BibTeX：', hw=900,
            og='{w:,} 部人类著作，{a:,} 位数学家，撑起了 OpenAI {p} 篇 AI 数学稿件。',
            foot='数据开放（Apache 2.0 来源）'),
}

# Figures below the fold are marked .pre and released when they scroll into view (position is checked on scroll,
# resize and a slow poll, so a figure cannot stay hidden). On phones the hero timeline and the decade chart start at their recent end.
JS = ("<script>(function(){document.querySelectorAll('.sf-tl .sf-scroll,.sf-dec .sf-scroll').forEach(function(e){e.scrollLeft=e.scrollWidth});"
      "var f=[].slice.call(document.querySelectorAll('.sf-fig'));f.forEach(function(e){e.classList.add('pre')});"
      "function c(){f=f.filter(function(e){var r=e.getBoundingClientRect();"
      "if(r.top<innerHeight*.85&&r.bottom>0){e.classList.remove('pre');return false}return true})}"
      "addEventListener('scroll',c,{passive:true});addEventListener('resize',c);addEventListener('load',c);setTimeout(c,80);"
      "var t=setInterval(function(){c();if(!f.length)clearInterval(t)},300)})()</script>")

for lang, l in L10N.items():
    LANG = lang
    t = figures.T[lang]
    ORDER.clear()
    meta, parts, cta = parse(open(os.path.join(B, f'{lang}.md'), encoding='utf-8').read())
    for k, v in zip(('p', 'w', 'a'), STATS):                     # the prose quotes these numbers; fail if the data has moved on
        assert f'{v:,}' in meta['dek'], (k, v)
    body = flow(parts)

    me = dict(type='misc', author=['Hongyang Li', 'Sea-Fill Team'], title=meta['title'], year='2026', month='oct',
              howpublished='Sea-Fill, On Whose Shoulders', url=l['url'])
    me_bib = bibtex('li2026shoulders', me)
    out = os.path.join(B, l['out'])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(os.path.join(os.path.dirname(out), 'references.bib'), 'w', encoding='utf-8').write(
        '% References for "' + meta['title'] + '" (Hongyang Li and the Sea-Fill team, 2026)\n\n'
        + me_bib + '\n\n' + '\n\n'.join(bibtex(k, REFS[k]) for k in ORDER) + '\n')
    body += ('\n<article class="sf-article">\n'
             f'<section class="sf-refs" id="refs"><h2>{l["refs"]}</h2><ol>'
             + ''.join(f'<li id="ref-{k}">{fmt(REFS[k])}</li>' for k in ORDER) + '</ol></section>\n'
             f'<section class="sf-citebox"><h2>{l["cite"]}</h2><pre>{html.escape(me_bib)}</pre>'
             f'<p>{l["bib"]}<a href="references.bib" download>references.bib</a></p></section>\n</article>')

    en_cur, zh_cur = (' aria-current="page"', '') if lang == 'en' else ('', ' aria-current="page"')
    zh_href, en_href = ('zh/', './') if lang == 'en' else ('./', '../')
    hero = f'''<header class="sf-hero">
<div class="sf-wrap">
<nav class="sf-nav" aria-label="{l['nav']}">
<a href="{l['hub']}">{l['hub_label']}</a>
<div class="sf-lang"><a href="{zh_href}"{zh_cur} lang="zh">中文</a><a href="{en_href}"{en_cur} lang="en">EN</a></div>
</nav>
<p class="sf-kicker">{html.escape(meta['kicker'])}</p>
<h1>{meta['h1']}</h1>
<p class="sf-dek">{inline(meta['dek']).replace('<b>', '<strong>').replace('</b>', '</strong>')}</p>
<p class="sf-byline">{inline(meta['byline'])}</p>
{figures.timeline(t)}
</div>
</header>'''
    note = html.escape(meta['note'], quote=False).replace('github.com/openai/math', '<a href="https://github.com/openai/math">github.com/openai/math</a>')
    stats = (f'<section class="sf-stats" aria-label="{t["stats_aria"]}"><div class="sf-wrap"><ul class="sf-stat-grid">'
             + ''.join(f'<li><span class="n{" hl" if i == 1 else ""}">{v:,}</span><span class="l">{html.escape(lab)}</span></li>'
                       for i, (v, lab) in enumerate(zip(STATS, t['stats'])))
             + f'</ul>{figures.relay(t)}<p class="sf-fn">* {note}</p></div></section>')
    btns = ''.join(f'<a class="sf-btn {"pri" if i == 0 else "sec"}" href="{u}"{" download" if u.endswith(".bib") else ""}>{html.escape(x)}</a>'
                   for i, (x, u) in enumerate(cta['links']))
    closing = (f'<section class="sf-cta" aria-labelledby="cta-t"><div class="sf-wrap"><h2 id="cta-t">{inline(cta["h"])}</h2>'
               + ''.join(f'<p>{p}</p>' for p in cta['p']) + f'<div class="sf-btns">{btns}</div>'
               f'<p class="sf-foot">SEA-FILL · <a href="https://huggingface.co/SeaFill2025">HUGGING FACE</a> · {l["foot"]}</p></div></section>')

    title = html.escape(meta['title'] + ' · Sea-Fill')
    og = html.escape(l['og'].format(p=STATS[0], w=STATS[1], a=STATS[2]))
    theme = open(os.path.join(B, f'theme_{lang}.css'), encoding='utf-8').read()
    open(out, 'w', encoding='utf-8').write(f'''<!doctype html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{html.escape(meta['desc'])}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{og}">
<meta property="og:type" content="article">
<meta property="og:url" content="{l['url']}">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="{l['url']}">
<link rel="alternate" hreflang="en" href="{L10N['en']['url']}">
<link rel="alternate" hreflang="zh" href="{L10N['zh']['url']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{FONTS[lang]}&display=swap" rel="stylesheet">
<style>
{theme}:root{{--hw:{l['hw']}}}{CSS}{figures.CSS}</style>
</head>
<body>
{hero}
{stats}
<main>
{body}
</main>
{closing}
{JS}
{GC}
</body>
</html>
''')
    print('ok', l['out'], f'{len(ORDER)} references', STATS)
