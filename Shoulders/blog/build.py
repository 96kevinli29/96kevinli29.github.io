"""Builds the essay pages from Markdown: blog/en.md -> blog/index.html, blog/zh.md -> blog/zh/index.html."""
import os, sys, re, html
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
from common import page
import figures

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
.notes{margin-top:2.6rem;padding-top:1rem;border-top:1px solid var(--rule);font-size:.85rem;color:var(--muted)}
.notes ol{padding-left:1.2rem}
.cta{display:inline-block;margin-top:.6rem;font-weight:600}
'''


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[\^(\w+)\]', r'<sup id="r\1"><a href="#n\1">\1</a></sup>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{m.group(2)}"{" class=cta" if "→" in m.group(1) else ""}>{m.group(1)}</a>', s)
    return s


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
            body.append(f'<p class="kicker">{html.escape(meta.get("kicker", ""))}</p><h1>{inline(b[2:])}</h1>')
        elif b.startswith('## '):
            body.append(f'<h2>{inline(b[3:])}</h2>')
        elif all(l.startswith('- ') for l in b.split('\n')):
            body.append('<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in b.split('\n')) + '</ul>')
        elif b.startswith('> '):
            body.append('<blockquote>' + inline(' '.join(l[2:] for l in b.split('\n'))) + '</blockquote>')
        else:
            body.append(f'<p>{inline(" ".join(b.split()))}</p>')
    if notes:
        items = ''.join(f'<li id="n{m.group(1)}">{inline(m.group(2))} <a href="#r{m.group(1)}">↩</a></li>'
                        for m in (re.match(r'^\[\^(\w+)\]: (.*)$', n) for n in notes))
        body.append(f'<div class="notes"><ol>{items}</ol></div>')
    return meta, '\n'.join(body)


LANGS = {'en': ('en.md', 'index.html', ('← On Whose Shoulders', '../'), ('中文', 'zh/')),
         'zh': ('zh.md', 'zh/index.html', ('← 巨人之肩', '../../zh/'), ('English', '../'))}

for lang, (src, out, back, alt) in LANGS.items():
    LANG = lang
    f = os.path.join(B, src)
    if not os.path.exists(f):
        continue
    meta, body = render(open(f, encoding='utf-8').read())
    has_alt = os.path.exists(os.path.join(B, LANGS['zh' if lang == 'en' else 'en'][0]))
    top = (f'<div class="top"><a href="{back[1]}">{back[0]}</a>'
           + (f'<a href="{alt[1]}">{alt[0]}</a>' if has_alt else '') + '</div>')
    foot = '<footer>Sea-Fill · <a href="https://huggingface.co/SeaFill2025">Hugging Face</a></footer>'
    o = os.path.join(B, out)
    os.makedirs(os.path.dirname(o), exist_ok=True)
    open(o, 'w', encoding='utf-8').write(page(lang, meta['title'] + (' · Sea-Fill' if lang == 'en' else ' · Sea-Fill'), meta['desc'], CSS,
                                              top + f'<article>{body}</article>' + foot))
    print('ok', out)
