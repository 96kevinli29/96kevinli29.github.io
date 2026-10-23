"""Builds grad/scripts/refs.json from the LaTeX sources of the three 2026 papers on Grad's conjecture.
Usage: python3 extract.py DIR   where DIR holds x_2609.24739/, x_2609.26742/, x_2610.07304/ (arXiv e-print sources, unpacked).
Only references actually cited in each paper are kept; citing sentences come from the .tex; DOIs are completed from Crossref."""
import sys, os, re, json, glob, time, urllib.request, urllib.parse, unicodedata

S = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
PAPERS = [
    dict(id='glt', arxiv='2609.24739', date='2026-09-21', title="Counterexamples to Grad's conjecture",
         authors=['Javier Gómez-Serrano', 'Lukas Liehr', 'Mitchell A. Taylor']),
    dict(id='lan', arxiv='2609.26742', date='2026-09-22', title='Analytic toroidal 3D MHD equilibria and steady Euler flows with invariant surfaces',
         authors=['Matt Landreman']),
    dict(id='gdm', arxiv='2610.07304', date='2026-10-05', title='Analytic non-axisymmetric 3D MHD equilibria without stellarator symmetry',
         authors=['Opal Issan', 'Jonathan Citrin', 'Matt Landreman', 'Brendan Tracey']),
]

ACC = {"'": '\u0301', '`': '\u0300', '"': '\u0308', '^': '\u0302', '~': '\u0303', 'c': '\u0327', 'v': '\u030c', 'u': '\u0306', 'H': '\u030b', '=': '\u0304', '.': '\u0307'}
def detex(s):
    s = re.sub(r'\\([\'`"^~=.])\s*\{?\\?([A-Za-z])\}?', lambda m: m.group(2) + ACC[m.group(1)], s)
    s = re.sub(r'\\([cvuH])\s*\{([A-Za-z])\}', lambda m: m.group(2) + ACC[m.group(1)], s)
    s = s.replace('\\ss', 'ß').replace('\\o', 'ø').replace('\\O', 'Ø').replace('\\l ', 'ł').replace('\\L ', 'Ł').replace('\\aa', 'å').replace('\\&', '&')
    s = s.replace('``', '“').replace("''", '”').replace('\\ldots', '…').replace('\\dots', '…')
    s = s.replace('--', '–').replace('~', ' ')
    s = re.sub(r'\\(?:textit|emph|textbf|mathrm|mathbb|mathcal|text|textrm)\s*\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\$([^$]*)\$', lambda m: re.sub(r'\\([A-Za-z]+)', r'\1', m.group(1)), s)
    s = s.replace('{', '').replace('}', '').replace('\\', '')
    return unicodedata.normalize('NFC', ' '.join(s.split()))

def parse_bib(text):
    out = {}
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,\s]+)\s*,', text):
        typ, key = m.group(1).lower(), m.group(2)
        if typ in ('comment', 'string', 'preamble'):
            continue
        i, depth, j = m.end(), 1, m.end()
        while j < len(text) and depth:
            depth += {'{': 1, '}': -1}.get(text[j], 0); j += 1
        body, fields, k = text[i:j - 1], {}, 0
        for fm in re.finditer(r'(\w+)\s*=\s*', body):
            if fm.start() < k:
                continue
            p = fm.end()
            if p < len(body) and body[p] == '{':
                d, q = 1, p + 1
                while q < len(body) and d:
                    d += {'{': 1, '}': -1}.get(body[q], 0); q += 1
                val = body[p + 1:q - 1]
            elif p < len(body) and body[p] == '"':
                q = body.index('"', p + 1) + 1; val = body[p + 1:q - 1]
            else:
                q = p; 
                while q < len(body) and body[q] not in ',\n': q += 1
                val = body[p:q]
            fields[fm.group(1).lower()] = val.strip(); k = q
        out[key] = fields
    return out

def names(a):
    res = []
    for x in re.split(r'\s+and\s+', a):
        x = detex(x).strip()
        if not x or x.lower() == 'others':
            continue
        if ',' in x:
            last, first = [y.strip() for y in x.split(',', 1)]
            x = (first + ' ' + last).strip()
        res.append(x)
    return res

def strip_tex(t):
    t = re.sub(r'(?<!\\)%.*', '', t)
    return t

def sentences(tex):
    body = tex[tex.find('\\begin{document}'):] if '\\begin{document}' in tex else tex
    body = re.sub(r'\\begin\{(equation|align|figure|table|lstlisting|eqnarray|multline|gather)\*?\}.*?\\end\{\1\*?\}', ' ', body, flags=re.S)
    flat = ' '.join(body.split())
    return re.split(r'(?<=[.!?])\s+(?=[A-Z\\])', flat)

CITE = re.compile(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}')
def clean_sentence(s, labels):
    s = CITE.sub(lambda m: '[' + ', '.join(labels.get(k.strip(), '?') for k in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\\(?:ref|eqref|cref|Cref|label)\{[^}]*\}', '', s)
    return detex(s)

def crossref(fields):
    t = detex(fields.get('title', ''))
    if fields.get('doi'):
        return fields['doi']
    if not t:
        return None
    q = urllib.parse.quote(t[:200])
    try:
        req = urllib.request.Request(f'https://api.crossref.org/works?rows=1&query.bibliographic={q}', headers={'User-Agent': 'shoulders (mailto:hongyang.li@uni.lu)'})
        it = json.load(urllib.request.urlopen(req, timeout=30))['message']['items']
        time.sleep(0.15)
        if it and it[0].get('title') and re.sub(r'\W', '', it[0]['title'][0].lower())[:40] == re.sub(r'\W', '', t.lower())[:40]:
            return it[0].get('DOI')
    except Exception:
        pass
    return None

works = {}
def wkey(f):
    if f.get('doi'):
        return 'doi:' + f['doi'].lower()
    return 't:' + re.sub(r'[^a-z0-9]', '', detex(f.get('title', '')).lower())[:60]

for P in PAPERS:
    d = os.path.join(SRC, 'x_' + P['arxiv'])
    tex = '\n'.join(strip_tex(open(f, encoding='utf-8', errors='replace').read()) for f in glob.glob(d + '/*.tex'))
    bib = {}
    for f in glob.glob(d + '/*.bib'):
        bib.update(parse_bib(open(f, encoding='utf-8', errors='replace').read()))
    order = []
    for m in CITE.finditer(tex):
        for k in m.group(1).split(','):
            k = k.strip()
            if k in bib and k not in order:
                order.append(k)
    labels = {}
    for k in order:
        f = bib[k]
        au = names(f.get('author', f.get('editor', '')))
        y = re.sub(r'\D', '', f.get('year', ''))[:4]
        labels[k] = (au[0].split()[-1] if au else detex(f.get('title', ''))[:20]) + (' ' + y if y else '')
    ctx = {k: [] for k in order}
    for s in sentences(tex):
        ks = [k.strip() for m in CITE.finditer(s) for k in m.group(1).split(',')]
        for k in set(ks):
            if k in ctx and len(s) < 1400:
                c = clean_sentence(s, labels)
                if c not in ctx[k]:
                    ctx[k].append(c)
    P['nref'] = len(order)
    for k in order:
        f = bib[k]
        wk = wkey(f)
        w = works.get(wk)
        if not w:
            au = names(f.get('author', f.get('editor', '')))
            venue = detex(f.get('journal') or f.get('booktitle') or f.get('publisher') or f.get('howpublished') or f.get('note') or ('arXiv:' + f['eprint'] if f.get('eprint') else ''))
            w = works[wk] = dict(a=au, t=detex(f.get('title', '')), y=re.sub(r'\D', '', f.get('year', ''))[:4], v=venue,
                                 doi=f.get('doi', ''), u=f.get('url', '') or (('https://arxiv.org/abs/' + f['eprint']) if f.get('eprint') else ''), by={})
        w['by'][P['id']] = ctx[k]

for w in works.values():
    if not w['doi'] and not w['u'].startswith('https://arxiv.org') and w['t']:
        doi = crossref({'title': w['t']})
        if doi:
            w['doi'] = doi
    if w['doi'] and not w['u']:
        w['u'] = 'https://doi.org/' + w['doi']

# the same work is often keyed differently in the three .bib files: merge on first author + year + opening words of the title
def fold(x):
    return unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
merged = {}
for w in works.values():
    sur = fold(w['a'][0].split()[-1]) if w['a'] else ''
    k = (sur, w['y'], ' '.join(re.sub(r'[^a-z0-9 ]', '', fold(w['t'])).split()[:4]))
    m = merged.get(k)
    if m and m['doi'] and w['doi'] and m['doi'].lower() != w['doi'].lower():
        k = k + (w['doi'].lower(),); m = merged.get(k)
    if not m:
        merged[k] = w; continue
    for pid, cs in w['by'].items():
        m['by'].setdefault(pid, [])
        m['by'][pid] += [c for c in cs if c not in m['by'][pid]]
    if sum(map(len, w['a'])) > sum(map(len, m['a'])): m['a'] = w['a']
    for f in ('doi', 'u', 'v'):
        m[f] = m[f] or w[f]
    if len(w['t']) > len(m['t']): m['t'] = w['t']
out = dict(papers=PAPERS, works=sorted(merged.values(), key=lambda w: (w['y'] or '9999', w['t'])))
json.dump(out, open(os.path.join(S, 'refs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({P['id']: P['nref'] for P in PAPERS}, len(out['works']), 'distinct works;', sum(1 for w in out['works'] if len(w['by']) > 1), 'cited by 2+ papers;', sum(1 for w in out['works'] if len(w['by']) == 3), 'by all three')
