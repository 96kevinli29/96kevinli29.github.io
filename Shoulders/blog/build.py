"""Builds the essay pages from Markdown: blog/en.md -> blog/index.html, blog/zh.md -> blog/zh/index.html."""
import os, sys, re, html
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
from common import page
import figures
from refs import REFS

CSS = figures.CSS + '''
article{max-width:40rem;margin:0 auto}
.kicker{font:500 .74rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:2.2rem}
article h1{margin-top:.6rem;font-size:clamp(2rem,5.6vw,3rem);text-wrap:balance}
article h2{margin:2.6rem 0 .7rem}
article p,article li{font-size:1.06rem;line-height:1.8}
article p{margin:0 0 1.05rem}
article ul{padding-left:1.2rem;margin:0 0 1.2rem}
article li{margin:.35rem 0}
article blockquote{margin:1.2rem 0;padding:.2rem 0 .2rem 1rem;border-left:3px solid var(--gold);color:var(--ink)}
article sup a{text-decoration:none;font-size:.75em}
span.ap{font-family:Georgia,"Times New Roman",serif}
a.cite{text-decoration:none;font-size:.86em;white-space:nowrap}
.refs{margin-top:2.6rem;padding-top:1rem;border-top:1px solid var(--rule)}
.refs h2{margin-top:0}
.refs ol{padding-left:1.6rem;font-size:.86rem;line-height:1.55;color:var(--muted)}
.refs li{margin:.35rem 0}.refs li b{color:var(--ink);font-weight:500}
.cite-box{margin-top:2rem}
.cite-box pre{white-space:pre-wrap;word-break:break-word;background:var(--sheet);border:1px solid var(--rule);border-radius:6px;padding:.8rem 1rem;font:.78rem/1.55 var(--f-mono);color:var(--ink)}
.cite-box p{font-size:.86rem;color:var(--muted)}
.notes{margin-top:2.6rem;padding-top:1rem;border-top:1px solid var(--rule);font-size:.85rem;color:var(--muted)}
.notes ol{padding-left:1.2rem}
.cta{display:inline-block;margin-top:.6rem;font-weight:600}
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
    return '<span class="cite">[' + ', '.join(out) + ']</span>'


def ap(s):
    return s.replace('’', '<span class="ap">’</span>') if LANG == 'en' else s


MARKS = ['*', '†', '‡']


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\s*\[(@[^\]]+)\]', lambda m: '\u00a0' + cites(m), s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[\^(\w+)\]', lambda m: f'<sup id="r{m.group(1)}"><a href="#n{m.group(1)}">{MARKS[int(m.group(1)) - 1]}</a></sup>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}"{" class=cta" if "→" in m.group(1) else ""}>{m.group(1)}</a>', s)
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


def render(md):
    meta, body = {}, []
    lines = md.split('\n')
    while lines and re.match(r'^\w+: ', lines[0]):
        k, v = lines.pop(0).split(': ', 1)
        meta[k] = v
    notes = [l for l in lines if re.match(r'^\[\^\w+\]: ', l)]
    lines = [l for l in lines if l not in notes]
    blocks = re.split(r'\n\s*\n', '\n'.join(lines).strip())
    for b in blocks:
        if b.startswith('{{fig:'):
            body.append(figures.render(b[6:-2], LANG))
        elif b.startswith('# '):
            body.append(f'<p class="kicker">{html.escape(meta.get("kicker", ""))}</p><h1>{ap(inline(b[2:]))}</h1>')
        elif b.startswith('## '):
            body.append(f'<h2>{ap(inline(b[3:]))}</h2>')
        elif all(l.startswith('- ') for l in b.split('\n')):
            body.append('<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in b.split('\n')) + '</ul>')
        elif b.startswith('> '):
            body.append('<blockquote>' + inline(' '.join(l[2:] for l in b.split('\n'))) + '</blockquote>')
        else:
            body.append(f'<p>{inline(" ".join(b.split()))}</p>')
    if ORDER:
        body.append('<section class="refs"><h2>' + ('References' if LANG == 'en' else '参考文献') + '</h2><ol>'
                    + ''.join(f'<li id="ref-{k}">{fmt(REFS[k])}</li>' for k in ORDER) + '</ol></section>')
    if notes:
        items = ''.join(f'<p id="n{m.group(1)}">{MARKS[int(m.group(1)) - 1]} {inline(m.group(2))} <a href="#r{m.group(1)}">↩</a></p>'
                        for m in (re.match(r'^\[\^(\w+)\]: (.*)$', n) for n in notes))
        body.insert(-1 if ORDER else len(body), f'<div class="notes">{items}</div>')
    return meta, '\n'.join(body)


LANGS = {'en': ('en.md', 'index.html', ('← On Whose Shoulders', '../'), ('中文', 'zh/')),
         'zh': ('zh.md', 'zh/index.html', ('← 巨人之肩', '../../zh/'), ('English', '../'))}

for lang, (src, out, back, alt) in LANGS.items():
    LANG = lang
    f = os.path.join(B, src)
    if not os.path.exists(f):
        continue
    ORDER.clear()
    meta, body = render(open(f, encoding='utf-8').read())
    has_alt = os.path.exists(os.path.join(B, LANGS['zh' if lang == 'en' else 'en'][0]))
    top = (f'<div class="top"><a href="{back[1]}">{back[0]}</a>'
           + (f'<a href="{alt[1]}">{alt[0]}</a>' if has_alt else '') + '</div>')
    me = dict(type='misc', author=['Hongyang Li', 'Sea-Fill Team'], title=meta['title'], year='2026', month='oct',
              howpublished='Sea-Fill, On Whose Shoulders', url='https://seafill.info/Shoulders/blog/' + ('' if lang == 'en' else 'zh/'))
    me_bib = bibtex('li2026shoulders', me)
    label = ('Cite this essay', 'All references as BibTeX: ') if lang == 'en' else ('引用本文', '全部参考文献的 BibTeX：')
    body += (f'<section class="cite-box"><h2>{label[0]}</h2><pre>{html.escape(me_bib)}</pre>'
             f'<p>{label[1]}<a href="references.bib" download>references.bib</a></p></section>')
    open(os.path.join(B, 'references.bib'), 'w', encoding='utf-8').write(
        '% References for "' + meta['title'] + '" (Hongyang Li and the Sea-Fill team, 2026)\n\n'
        + me_bib + '\n\n' + '\n\n'.join(bibtex(k, REFS[k]) for k in ORDER) + '\n')
    foot = '<footer>Sea-Fill · <a href="https://huggingface.co/SeaFill2025">Hugging Face</a></footer>'
    o = os.path.join(B, out)
    os.makedirs(os.path.dirname(o), exist_ok=True)
    open(o, 'w', encoding='utf-8').write(page(lang, meta['title'] + (' · Sea-Fill' if lang == 'en' else ' · Sea-Fill'), meta['desc'], CSS,
                                              top + f'<article>{body}</article>' + foot))
    print('ok', out)
