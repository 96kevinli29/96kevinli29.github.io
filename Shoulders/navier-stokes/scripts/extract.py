"""Parse the reference lists and in-text citations of OpenAI's Navier–Stokes and Euler papers.

Reads the two PDFs (downloaded to scripts/pdf/ if missing) and writes refs.json:
references with authors, year, title, link, and every sentence in which the paper cites them.
Needs PyMuPDF (pip install pymupdf).
"""
import os, re, json, urllib.request, unicodedata
import fitz

S = os.path.dirname(os.path.abspath(__file__))
PAPERS = [
    dict(id='ns', title='Finite time blowup for Navier–Stokes', date='2026-09-08',
         url='https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf'),
    dict(id='euler', title='Finite time blowup for the Euler equation', date='2026-09-08',
         url='https://cdn.openai.com/pdf/315b36cd-ec98-4023-8342-93345194ece1/euler.pdf'),
]
# Titles whose math or commas do not survive PDF text extraction (checked against the PDFs).
# ^{..} / _{..} are rendered as superscript / subscript by build.py.
TITLES = {
    ('ns', 6): 'Blow-up for the incompressible 3D-Euler equations with uniform C^{1,1/2−ε} ∩ L^2 force',
    ('ns', 8): 'Finite time blow-up for the hypodissipative Navier Stokes equations with a force in L^1_t C^{1,ε}_x ∩ L^∞_t L^2_x',
    ('ns', 11): 'L^{3,∞}-solutions of the Navier–Stokes equations and backward uniqueness',
    ('ns', 21): 'On the theories of the internal friction of fluids in motion, and of the equilibrium and motion of elastic solids',
    ('euler', 5): 'Asymptotically self-similar blowup for 3D incompressible Euler with C^{1,1/3−} velocity II: 3D profiles, blowup, and limiting behavior',
    ('euler', 9): 'Non existence and strong ill-posedness in C^k and Sobolev spaces for SQG',
    ('euler', 10): 'Blow-up for the incompressible 3D-Euler equations with uniform C^{1,1/2−ε} ∩ L^2 force',
    ('euler', 13): 'Finite time singularities to the 3D incompressible Euler equations for solutions in C^∞(ℝ^3 ∖ {0}) ∩ C^{1,α} ∩ L^2',
    ('euler', 15): 'Finite-time singularity formation for C^{1,α} solutions to the incompressible Euler equations on ℝ^3',
    ('euler', 16): 'On the stability of self-similar blow-up for C^{1,α} solutions to the incompressible Euler equations on ℝ^3',
    ('euler', 18): 'L^∞ ill-posedness for a class of equations arising in hydrodynamics',
    ('euler', 24): 'Nonstationary flows of viscous and ideal fluids in ℝ^3',
    ('euler', 29): 'Incompressible Euler blowup at the C^{1,1/3} threshold',
}
PARTICLES = {'de', 'van', 'von', 'der', 'den', 'la', 'le', 'da', 'di', 'du'}


def pdf(p):
    os.makedirs(S + '/pdf', exist_ok=True)
    f = f"{S}/pdf/{p['id']}.pdf"
    if not os.path.exists(f):
        urllib.request.urlretrieve(p['url'], f)
    return fitz.open(f)


ACC = {'˙': '̇', '´': '́', '`': '̀', '¨': '̈', 'ˇ': '̌', '˜': '̃'}


def clean(s):
    s = s.replace('­', '')
    s = re.sub('([˙´`¨ˇ˜])([A-Za-z])', lambda m: m.group(2) + ACC[m.group(1)], s)   # spacing accent before its letter
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'-\s*\n\s*', '-', s)          # hyphen at line end (keeps "Navier–\nStokes" readable below)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def is_name(tok):
    w = tok.replace('Jr.', '').split()
    if not w or len(w) > 5:
        return False
    return all(x[0].isupper() or x.lower() in PARTICLES for x in w if x)


def split_authors(body):
    """'A, B, and C, Title, venue' -> ([A, B, C], 'Title, venue')."""
    parts = [x.strip() for x in body.split(', ')]
    names = []
    i = 0
    while i < len(parts):
        t = parts[i]
        if t.startswith('and '):
            t = t[4:]
        if ' and ' in t and all(is_name(x) for x in t.split(' and ')):
            names += t.split(' and ')
            i += 1
            continue
        if t == 'Jr.' and names:
            names[-1] += ', Jr.'
            i += 1
            continue
        if is_name(t) and i < len(parts) - 1:
            names.append(t)
            i += 1
            continue
        break
    return names, ', '.join(parts[i:])


def references(doc):
    """Numbered entries after the 'References' heading."""
    text = ''
    for pno in range(len(doc) - 1, -1, -1):
        t = doc[pno].get_text()
        text = t + text
        if re.search(r'^References\s*$', t, re.M):
            break
    text = text[re.search(r'^References\s*$', text, re.M).end():]
    text = re.sub(r'^(\d+\s*\n)?(OPENAI|FINITE TIME BLOWUP[^\n]*)\s*\n(\d+\s*\n)?', '', text, flags=re.M)
    ents, pos, n = [], 0, 1
    marks = []
    for m in re.finditer(r'(?:^|\n)(\d+)\.(?=\s)', text):
        if int(m.group(1)) == n:
            marks.append((n, m.end()))
            n += 1
    out, prev = [], []
    for i, (n, st) in enumerate(marks):
        end = marks[i + 1][1] - len(str(n + 1)) - 2 if i + 1 < len(marks) else len(text)
        t = text[st:end]
        while True:                              # URLs broken over lines
            u = re.sub(r'(https?:\S*)\n(\S+)', r'\1\2', t)
            if u == t:
                break
            t = u
        raw = clean(t)
        if raw.startswith(','):                 # "———, Title" = same authors as the previous entry
            names, rest = prev, raw[1:].strip()
        else:
            names, rest = split_authors(raw)
        prev = names
        url = re.findall(r'https?:\S+', raw)
        url = url[-1].rstrip('.') if url else ''
        yr = re.findall(r'\((1[6-9]\d\d|20\d\d)\)|\b(1[6-9]\d\d|20\d\d)\b', re.sub(r'https?:\S+', '', rest))
        yr = next((a or b for a, b in yr), '')
        out.append(dict(n=n, a=names, t=rest.split(', ')[0], y=yr, u=url, raw=raw))
    return out


def fold(s):
    return re.sub(r'[^a-z]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())


def surname(name):
    w = name.replace(', Jr.', '').split()
    i = len(w) - 1
    while i > 0 and w[i - 1].lower() in PARTICLES:
        i -= 1
    return fold(' '.join(w[i:]))


def match_key(key, refs):
    """cite.tao2016 -> the entry by Tao from 2016 (surnames, initials and year in the key)."""
    k = key[5:]
    yr = re.search(r'(1[6-9]\d\d|20\d\d)', k)
    yr = yr.group(1) if yr else ''
    alpha = re.sub(r'[^a-z]', '', k.split(yr)[0] if yr else k)
    best, bs = None, -99
    for r in refs:
        if yr and r['y'] != yr:
            continue
        sn = [surname(a) for a in r['a']]
        hit = sum(1 for x in sn if x and (x in alpha or x.split('zoroa')[0] in alpha))
        if alpha == ''.join(x[0] for x in sn if x):
            hit = len(sn)
        sc = hit * 2 - (len(sn) - hit)
        if hit and sc > bs:
            best, bs = r['n'], sc
    return best


def sentence(page, rect):
    """The sentence around a citation link."""
    blocks = page.get_text('blocks')
    for b in blocks:
        if fitz.Rect(b[:4]).intersects(rect):
            txt = clean(b[4])
            mark = clean(page.get_textbox(rect))
            i = txt.find(mark) if mark else -1
            if i < 0:
                return txt[:400]
            a = txt.rfind('. ', 0, i)
            a = 0 if a < 0 else a + 2
            z = txt.find('. ', i)
            z = len(txt) if z < 0 else z + 1
            return txt[a:z][:500]
    return ''


def main():
    out = []
    for p in PAPERS:
        doc = pdf(p)
        refs = references(doc)
        key2n = {}
        for pg in doc:
            for l in pg.get_links():
                k = l.get('nameddest') or l.get('name') or ''
                if k.startswith('cite.') and k not in key2n:
                    key2n[k] = match_key(k, refs)
        miss = [k for k, v in key2n.items() if v is None]
        assert not miss, miss
        cites = {r['n']: [] for r in refs}
        for pno, page in enumerate(doc):
            for l in page.get_links():
                k = l.get('nameddest') or l.get('name') or ''
                if k in key2n:
                    c = dict(p=pno + 1, s=sentence(page, l['from']))
                    if c not in cites[key2n[k]]:     # the same sentence can carry several links
                        cites[key2n[k]].append(c)
        for r in refs:
            r['c'] = cites[r['n']]
            r['t'] = TITLES.get((p['id'], r['n']), r['t'])
            if not r['y'] and r['a'] == ['Charles L. Fefferman']:
                r['y'] = '2000'                  # Clay's official problem description (2000)
        out.append(dict(p, pages=len(doc), refs=refs))
        print(p['id'], len(refs), 'refs;', sum(len(v) for v in cites.values()), 'in-text citations;',
              len(key2n), 'keys resolved')
    json.dump(out, open(S + '/refs.json', 'w'), ensure_ascii=False, indent=1)


main()
