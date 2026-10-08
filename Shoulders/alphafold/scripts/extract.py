"""References and in-text citations of the AlphaFold 2 paper (Jumper et al., Nature 2021).

Reads the open-access JATS full text from Europe PMC (PMC8371605) and completes author lists
that the journal cut short with "et al." from Crossref. Writes refs.json.
"""
import os, re, json, time, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

S = os.path.dirname(os.path.abspath(__file__))
PMC = 'PMC8371605'
PAPER = dict(id='af2', title='Highly accurate protein structure prediction with AlphaFold', date='2021-07-15',
             url='https://www.nature.com/articles/s41586-021-03819-2', doi='10.1038/s41586-021-03819-2')
UA = {'User-Agent': 'OnWhoseShoulders/1.0 (https://96kevinli29.github.io/Shoulders/)'}


def get(url, cache):
    f = f'{S}/cache/{cache}'
    if not os.path.exists(f):
        os.makedirs(f'{S}/cache', exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
            open(f, 'wb').write(r.read())
        time.sleep(0.2)
    return open(f, 'rb').read()


def text(el):
    return re.sub(r'\s+', ' ', ''.join(el.itertext())).strip() if el is not None else ''


def crossref_authors(doi):
    try:
        m = json.loads(get('https://api.crossref.org/works/' + urllib.parse.quote(doi), 'cr_' + re.sub(r'\W', '_', doi)))['message']
    except Exception:
        return None
    out = []
    for a in m.get('author', []):
        if a.get('family'):
            out.append((a.get('given', '') + ' ' + a['family']).strip())
        elif a.get('name'):
            out.append(a['name'])
    return out or None


# Fixes for entries that are wrong in the journal's own reference list.
FIX = {70: dict(a=['Martín Abadi'], etal=True, t='TensorFlow: large-scale machine learning on heterogeneous systems')}


def parse_mixed(raw):
    """'Carreira, J., Agrawal, P. & Malik, J. Title. In Proc. … (2016).' -> (names, title, year, etal)."""
    raw = re.sub(r'^\d+\.\s*', '', raw)
    m = re.match(r'^(.*?(?:&\s*[^,&]+?,\s*(?:[A-Z][a-z]?\.[\s-]?)+|\bet al\.|^[^,&]+?,\s*(?:[A-Z][a-z]?\.[\s-]?)+))\s+(?=[A-Z0-9])(.*)$', raw)
    if not m:
        return [], raw.split('. ')[0], '', False
    auth, rest = m.group(1), m.group(2)
    etal = auth.endswith('et al.')
    auth = auth.replace('et al.', '').replace('&', ',')
    parts = [x.strip() for x in auth.split(',') if x.strip()]
    names = [f'{parts[i + 1]} {parts[i]}' if i + 1 < len(parts) else parts[i] for i in range(0, len(parts), 2)]
    yr = re.findall(r'\((\d{4})\)', rest)
    return names, re.split(r'\.\s', rest)[0], yr[-1] if yr else '', etal


def main():
    root = ET.fromstring(get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{PMC}/fullTextXML', 'paper.xml'))
    refs, order = {}, []
    for ref in root.iter('ref'):
        rid = ref.get('id')
        ec = ref.find('.//element-citation')
        names = []
        collab = False
        if ec is not None:
            for n in ec.findall('./person-group/name'):
                names.append((text(n.find('given-names')) + ' ' + text(n.find('surname'))).strip())
            cl = [text(c) for c in ec.findall('./person-group/collab')]
            collab = bool(cl)
            names = cl + names
        etal = ec is not None and ec.find('./person-group/etal') is not None
        doi = text(ec.find("./pub-id[@pub-id-type='doi']")) if ec is not None else ''
        full = crossref_authors(doi) if doi and not collab else None   # consortia keep their name, not 100+ members
        if full and (etal or len(full) >= len(names)):
            names = full
        title = text(ec.find('article-title')) or text(ec.find('source')) if ec is not None else ''
        year = text(ec.find('year')) if ec is not None else ''
        if ec is None:
            names, title, year, etal = parse_mixed(text(ref.find('.//mixed-citation')))
        refs[rid] = dict(n=int(text(ref.find('label')).rstrip('.')), a=names, etal=etal and not full,
                         t=title, y=year,
                         v=text(ec.find('source')) if ec is not None and text(ec.find('article-title')) else '',
                         u=f'https://doi.org/{doi}' if doi else '', raw=text(ref.find('.//mixed-citation')), c=[])
        order.append(rid)

    # in-text citations: every paragraph and caption outside the reference list; ranges "10–14" expanded
    num = {r['n']: rid for rid, r in refs.items()}
    for p in root.iter('p'):
        raw = ET.tostring(p, encoding='unicode')
        if 'ref-type="bibr"' not in raw:
            continue
        raw = re.sub(r'<xref ref-type="bibr" rid="CR(\d+)"[^>]*>[^<]*</xref>', r' ⟦\1⟧', raw)
        raw = re.sub(r'⟦(\d+)⟧\s*[–-]\s*⟦(\d+)⟧', lambda m: ' '.join(f'⟦{i}⟧' for i in range(int(m.group(1)), int(m.group(2)) + 1)), raw)
        plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', raw)).strip()
        # split into sentences, keeping the markers that follow a full stop with the sentence before it
        sents, cur = [], ''
        for tok in re.split(r'(\.\s*(?:\s*⟦\d+⟧[\s,]*)*\s+)(?=[A-Z(])', plain):
            cur += tok
            if re.match(r'\.\s', tok):
                sents.append(cur); cur = ''
        if cur:
            sents.append(cur)
        for sent in sents:
            ids = [int(x) for x in re.findall(r'⟦(\d+)⟧', sent)]
            clean = re.sub(r'\s*⟦\d+⟧[\s,]*', ' ', sent)
            clean = re.sub(r'\s+([.,;:)])', r'\1', re.sub(r'\s+', ' ', clean)).strip()
            for n in dict.fromkeys(ids):
                c = dict(s=clean[:500])
                if n in num and c not in refs[num[n]]['c']:
                    refs[num[n]]['c'].append(c)
    for r in refs.values():
        r.update(FIX.get(r['n'], {}))
    out = [refs[r] for r in order]
    json.dump(dict(PAPER, refs=out), open(S + '/refs.json', 'w'), ensure_ascii=False, indent=1)
    print(len(out), 'refs;', sum(len(r['c']) for r in out), 'citing sentences;', sum(1 for r in out if r['etal']), 'still et al.')


main()
