"""Builds art/scripts/refs.json from the bioRxiv preprint
"Autonomous AI agents discover reverse transcriptases with tandem repeat arrays" (Anthropic, 2026).
Usage: python3 extract.py path/to/preprint.pdf   (the PDF from biorxiv.org, DOI 10.64898/2026.10.05.755809)
Reference list and citing sentences come from the PDF text; full author lists are completed from Crossref."""
import sys, os, re, json, time, urllib.request
import fitz

S = os.path.dirname(os.path.abspath(__file__))
pdf = sys.argv[1]
text = ''.join(p.get_text() for p in fitz.open(pdf))
# drop the bioRxiv running header/footer lines that are interleaved with the text
NOISE = re.compile(r'^(?:\(which was not certified.*|The copyright holder.*|this version posted.*|;|https://doi\.org/10\.64898.*|doi:|'
                   r'bioRxiv preprint|\d+|\.|CC-BY 4\.0 International license|available under a)\s*$')
lines = [l for l in text.split('\n') if not NOISE.match(l.strip())]
text = '\n'.join(lines)
i = text.index('\nReferences\n')
body, tail = text[:i], text[i:]
j = tail.find('Acknowledgments')
refs_txt = tail[:j] if j > 0 else tail
body = body + '\n' + (tail[j:] if j > 0 else '')        # the Methods follow the reference list in this preprint
parts = re.split(r'\n\((\d+)\) ', refs_txt)
raw = {int(parts[k]): ' '.join(parts[k + 1].split()) for k in range(1, len(parts) - 1, 2)}

# citing sentences: groups like (61) or (36, 41–47) in the body
flat = ' '.join(body.split())
sents = re.split(r'(?<=[.!?])\s+(?=[A-Z(])', flat)
ctx = {n: [] for n in raw}
def expand(g):
    out = []
    for piece in g.split(','):
        piece = piece.strip()
        m = re.fullmatch(r'(\d+)\s*[–-]\s*(\d+)', piece)
        if m: out += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif piece.isdigit(): out.append(int(piece))
    return out
for s in sents:
    for g in re.findall(r'\((\d+(?:\s*[,–-]\s*\d+)*)\)', s):
        for n in expand(g):
            if n in ctx and s not in [c['s'] for c in ctx[n]] and len(s) < 900:
                ctx[n].append({'s': s})

def crossref(doi):
    try:
        req = urllib.request.Request('https://api.crossref.org/works/' + doi, headers={'User-Agent': 'shoulders (mailto:hongyang.li@uni.lu)'})
        return json.load(urllib.request.urlopen(req, timeout=30))['message']
    except Exception:
        return None

refs = []
for n in sorted(raw):
    r = re.sub(r'([a-z])- ([a-z])', r'\1\2', raw[n])          # words split across lines
    d = re.search(r'doi:\s*(10\..+?)\s*$', r)
    doi = re.sub(r'\s+', '', d.group(1)).rstrip('.') if d else None
    url = re.search(r'(https?://\S+)', r)
    toks = r.split(', ')
    NAME = re.compile(r"^(?:[A-ZÁ-Ž][a-z]?\.(?:-?[A-Z]\.)*\s?)+[A-Za-zÀ-ÿ'’\-–\. ]+?(?: et al\.)?$")
    k = 0
    while k < len(toks) and NAME.match(toks[k]):
        k += 1
    if k == 0:                                                       # corporate or unusual author, e.g. "T. S. Kuhn"
        k = 1
    a_raw, rest_all = ', '.join(toks[:k]), ', '.join(toks[k:])
    mt = re.match(r'(.+?(?:\?|(?=\. )|(?=, in )))', rest_all)
    title = (mt.group(1) if mt else rest_all).strip().rstrip('.')
    rest = rest_all[len(title):].lstrip('.,? ')
    etal = ' et al.' in a_raw
    authors = [x.strip() for x in a_raw.replace(' et al.', '').split(', ') if x.strip()]
    ys = re.findall(r'\((?:[^()]*?\D)?((?:19|20)\d\d)\)', r)
    entry = dict(n=n, a=authors, etal=etal, t=title, y=ys[-1] if ys else '', v=rest.split(' (')[0].split(' doi:')[0][:80],
                 u=('https://doi.org/' + doi) if doi else (url.group(1) if url else ''), raw=r, c=ctx[n])
    if doi:
        cr = crossref(doi)
        time.sleep(0.15)
        if cr and cr.get('author'):
            names = [' '.join(x for x in (p.get('given'), p.get('family')) if x) or p.get('name', '') for p in cr['author']]
            names = [x for x in names if x]
            if names:
                entry['a'], entry['etal'] = names, False
        if cr and cr.get('title'):
            entry['t'] = ' '.join(cr['title'][0].split())
    refs.append(entry)

out = dict(id='art', title='Autonomous AI agents discover reverse transcriptases with tandem repeat arrays', date='2026-10-11',
           url='https://www.biorxiv.org/content/10.64898/2026.10.05.755809v1', doi='10.64898/2026.10.05.755809', refs=refs)
json.dump(out, open(os.path.join(S, 'refs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(refs), 'refs;', sum(1 for r in refs if r['etal']), 'still et al.;', sum(len(r['c']) for r in refs), 'citing sentences')
