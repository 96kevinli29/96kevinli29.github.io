"""Builds the hub pages (index.html = English, zh/index.html) from the topic data. Run from anywhere."""
import os, sys, json, collections, html
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
from common import page, laureates, person_key, tribute_button
import common
common.FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
    '&family=IBM+Plex+Sans:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;900'
    '&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">')

esc = html.escape

# ---- math: OpenAI Math Release (data embedded in math/index.html) -------------
_h = open(H + '/math/index.html', encoding='utf-8').read()
M, _ = json.JSONDecoder().raw_decode(_h[_h.index('{"gen"'):].replace('<\\/', '</'))
A = M['authors']
ent = collections.Counter()                     # reference entries per author (the default ranking)
for p in M['papers']:
    for r in p['r']:
        ent.update(r[0])
ent = collections.Counter({k: v for k, v in ent.items() if not A[k]['n'].startswith('init:')})
M_LAUR = sum(1 for k in ent if any(x in A[k] for x in ('fm', 'ab', 'wf')))
NP = len(M['papers'])
NF = len({p['fam'] for p in M['papers']})   # OpenAI groups the manuscripts into result families
RELEASED = 722   # manuscripts in OpenAI's original release (6 Oct 2026); headlines keep this number, a note gives the current count
# ---- the pyramid: the best-known names among those cited --------------------------
# Laureates (Fields / Abel / Wolf) cited most, the most-cited names without those prizes,
# and a few names chosen by hand; ordered by reference entries, a few placed side by side.
LAUR_N, OTHER_N = 50, 20                        # about a third of the names carry none of these prizes
EXTRA = ['Grigori Perelman', 'Shiing-Shen Chern', 'Chenyang Xu', 'Gang Tian', 'Shaoming Guo']
_k = {a['n']: i for i, a in enumerate(A)}
_is_laur = lambda k: any(x in A[k] for x in ('fm', 'ab', 'wf'))
_laur = [k for k, _ in ent.most_common() if _is_laur(k)][:LAUR_N]
_other = [k for k, _ in ent.most_common() if not _is_laur(k)][:OTHER_N]
_sel = list(dict.fromkeys(_laur + _other + [_k[n] for n in EXTRA if n in _k]))
TOP = sorted(((k, ent[k]) for k in _sel), key=lambda x: -x[1])
PINNED = {}                                     # names drawn at their neighbours' size


def place(names, after=None, row=None):
    """Move names (in order) right after `after`, or into the middle of pyramid row `row`."""
    ks = [_k[n] for n in names if n in _k]
    for k in ks:
        for j, (x, _) in enumerate(TOP):
            if x == k:
                TOP.pop(j)
                break
    if after is not None:
        at = next(j for j, (x, _) in enumerate(TOP) if x == _k[after]) + 1
        PINNED[_k[after]] = ent[_k[after]]      # the anchor belongs to the group
    else:
        at = sum(ROWS[:row]) + ROWS[row] // 2
    size = TOP[min(at, len(TOP) - 1)][1]
    for i, k in enumerate(ks):
        TOP.insert(at + i, (k, ent[k]))
        PINNED[k] = size


ROWS = [3, 4, 5, 7, 9, 11, 13]
place(['Shing-Tung Yau', 'Shiing-Shen Chern'], after='Terence Tao')
place(['Gang Tian'], row=3)
place(['Yu Deng', 'Hong Wang', 'Shaoming Guo'], row=4)
ROWS.append(len(TOP) - sum(ROWS))

# ---- Navier–Stokes / Euler -----------------------------------------------------
NS = json.load(open(H + '/navier-stokes/scripts/refs.json', encoding='utf-8'))
NS_REFS = sum(len(p['refs']) for p in NS)
MILESTONES = [('Leonhard Euler', '欧拉', 1757), ('Claude Navier', '纳维', 1827), ('George Gabriel Stokes', '斯托克斯', 1845),
              ('Jean Leray', '勒雷', 1934), ('Elias M. Stein', '斯坦', 1970), ('Tosio Kato', '加藤敏夫', 1972),
              ('Caffarelli–Kohn–Nirenberg', '卡法雷利–科恩–尼伦伯格', 1982), ('Terence Tao', '陶哲轩', 2016)]


# ---- AlphaFold 2 (chemistry / life sciences) ---------------------------------------
AF = json.load(open(H + '/alphafold/scripts/refs.json', encoding='utf-8'))
AF_REFS = len(AF['refs'])
AF_MS = [('Christian Anfinsen', '安芬森', 1973), ('Altschuh · Klug', 'Altschuh · 克鲁格', 1987), ('CASP · Moult', 'CASP · Moult', 1995),
         ('Marks et al.', 'Marks 等', 2011), ('AlphaFold 1', 'AlphaFold 1', 2020), ('trRosetta · Baker', 'trRosetta · 大卫·贝克', 2020)]
AF_NOBEL = {'anfinsen c': 1972, 'klug a': 1982, 'wuthrich k': 2002, 'baker d': 2024, 'hassabis d': 2024, 'jumper j': 2024}
AF_ZH = {'Christian B. Anfinsen': '安芬森', 'Aaron Klug': '克鲁格', 'Kurt Wüthrich': '维特里希', 'David Baker': '大卫·贝克',
         'Demis Hassabis': '哈萨比斯', 'John Jumper': '江珀', 'Yang Zhang': '张阳', 'Jinbo Xu': '许锦波', 'Jianyi Yang': '杨建益'}


def af_people():
    """Canonical AlphaFold-cited names (surname + initial merged, longest spelling kept) with their works."""
    import unicodedata
    f = lambda x: unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
    out = {}
    for r in AF['refs']:
        for a in r['a']:
            a = {'A. Klug': 'Aaron Klug'}.get(a, a)
            w = a.replace(',', ' ').split()
            k = f(w[-1]) + ' ' + f(w[0])[:1] if len(w) > 1 else f(a)
            q = out.setdefault(k, dict(n=a, e=0, w=[], nb=AF_NOBEL.get(k)))
            if len(a) > len(q['n']):
                q['n'] = a
            q['e'] += 1
            q['w'].append([r['t'], r['y']])
    return out.values()


# ---- search index for "on whose shoulders?" (fetched by the page on first use) --
def search_index():
    works = collections.defaultdict(lambda: collections.defaultdict(lambda: [None, None, set()]))
    papers = collections.defaultdict(set)
    for pi, p in enumerate(M['papers']):
        for r in p['r']:
            for a in r[0]:
                w = works[a][(r[1] or '').strip().lower()[:80]]
                w[0], w[1] = r[1], r[2]
                w[2].add(pi)
                papers[a].add(pi)
    people = {}
    for k, v in ent.items():
        a = A[k]
        top = sorted(works[k].values(), key=lambda w: (-len(w[2]), w[1] or ''))[:3]
        people[person_key(a['n'])] = dict(
            n=a['n'], zh=a.get('zh', ''), pz={x: a[x] for x in ('fm', 'ab', 'wf') if x in a},
            me=v, mp=len(papers[k]), i=k, mw=[[(w[0] or '')[:110], w[1] or '', len(w[2])] for w in top if w[0]],
            ne=0, nw=[])
    zh_ns = {'Leonhard Euler': '欧拉', 'Claude Louis Marie Henri Navier': '纳维', 'George Gabriel Stokes': '斯托克斯',
             'Tosio Kato': '加藤敏夫', 'Thomas Y. Hou': '侯一钊'}
    for p in NS:
        for r in p['refs']:
            for a in r['a']:
                k = person_key(a)
                q = people.setdefault(k, dict(n=a, zh=zh_ns.get(a, ''), pz=NS_LAUR.get(k, {}), me=0, mp=0, i=-1, mw=[], ne=0, nw=[]))
                q['zh'] = q['zh'] or zh_ns.get(a, '')
                q['ne'] += 1
                if [r['t'], r['y']] not in q['nw']:
                    q['nw'].append([r['t'], r['y']])
    # AlphaFold names stay separate from the mathematicians unless known to be the same person:
    # common names (Yang Li, H. Wang, X. Zhang …) belong to different people across the fields.
    same_person = {'Riccardo Zecchina'}
    for a in af_people():
        k = person_key(a['n']) if a['n'] in same_person else 'af:' + person_key(a['n'])
        q = people.setdefault(k, dict(n=a['n'], zh='', pz={}, me=0, mp=0, i=-1, mw=[], ne=0, nw=[]))
        q['zh'] = q['zh'] or AF_ZH.get(a['n'], '')
        if a['nb']:
            q['pz'] = dict(q['pz'], nc=a['nb'])
        q['ae'], q['aw'] = a['e'], a['w']
    out = sorted(people.values(), key=lambda q: -(q['me'] + q['ne'] * 3 + q.get('ae', 0) * 3))
    pz = lambda d: ' '.join(f'{k}{v}' for k, v in d.items())
    return [[q['n'], q['zh'], pz(q['pz']), q['me'], q['mp'], q['i'], q['mw'], q['ne'], q['nw'], q.get('ae', 0), q.get('aw', [])] for q in out]


NS_LAUR = laureates(H + '/math/scripts')
with open(H + '/search.json', 'w', encoding='utf-8') as f:
    json.dump(search_index(), f, ensure_ascii=False, separators=(',', ':'))


# On the Chinese page, Chinese mathematicians keep their Chinese names; everyone else keeps the original spelling.
CHINESE_ALSO = {'Terence Tao'}
# Known by surname alone in English, so narrow screens may shorten them; other Chinese names stay in full.
SURNAME_OK = {'Terence Tao', 'Shing-Tung Yau', 'Shiing-Shen Chern'}
chinese = lambda a: a.get('c') in ('CN', 'TW', 'HK', 'MO') or a['n'] in CHINESE_ALSO



GROUPS = [['Terence Tao', 'Shing-Tung Yau', 'Shiing-Shen Chern'], ['Yu Deng', 'Hong Wang', 'Shaoming Guo']]
# Three packings of the same mound, one per screen width (CSS shows the one that fits):
# (Latin px/char, CJK px/char, gap px, top line px, base line widths tried, surnames only)
MOUND_LAYOUTS = {
    'wide':   (8.9, 18.3, 17.6, 380, range(700, 806, 5), False),   # card content ~ 816 px; full names
    'mid':    (8.9, 18.3, 17.6, 150, range(400, 446, 5), True),    # 521–860 px screens; surnames
    'narrow': (6.95, 14.2, 11.2, 110, range(280, 318, 2), True),   # phones (font x0.78, CJK x0.87); surnames
}


def pyramid(lang):
    """A mound of names: one size, shuffled (fixed seed), so position says nothing about rank."""
    import random
    units = [[_k[n] for n in g if n in _k] for g in GROUPS]
    grouped = {k for u in units for k in u}
    units += [[k] for k, _ in TOP if k not in grouped]
    random.Random(2026).shuffle(units)
    # groups of names are never at the very top of the mound
    for g in [u for u in units if len(u) > 1]:
        if units.index(g) < len(units) // 4:
            units.remove(g)
            units.insert(len(units) // 3, g)
    label = lambda k: A[k]['zh'] if lang == 'zh' and A[k].get('zh') and chinese(A[k]) else A[k]['n']

    def pack(widths, lo, hi):
        total = sum(widths)
        n = max(1, round(total / ((lo + hi) / 2)))
        lines, cur, cw, li = [], [], 0, 0
        for u, uw in zip(units, widths):
            target = lo + (hi - lo) * min(li, n - 1) / max(n - 1, 1)
            if cur and cw + uw > target:
                lines.append((cur, cw)); cur, cw, li = [], 0, li + 1
            cur, cw = cur + u, cw + uw
        lines.append((cur, cw))
        return lines

    def short(k):
        """Surname for narrow screens; Chinese mathematicians keep their full name."""
        a = A[k]
        if chinese(a) and (lang == 'zh' or a['n'] not in SURNAME_OK):
            return label(k)
        w = a['n'].split()
        sn = ' '.join(w[next((i for i in range(len(w) - 1, 0, -1) if not w[i - 1][:1].islower()), 0):]) if len(w) > 1 else a['n']
        return sn

    def span(k, sur=False):
        a = A[k]
        nm = short(k) if sur else label(k)
        prize = [lab for x, lab in (('fm', 'Fields'), ('ab', 'Abel'), ('wf', 'Wolf')) if x in a]
        tip = a['n'] + (' · ' + ' / '.join(prize) if prize else '')
        cls = 'g' + (' laur' if prize else '') + (' cjk' if any(ord(c) > 0x2e80 for c in nm) else '')
        return f'<span class="{cls}" title="{esc(tip)}">{esc(nm)}</span>'

    out = []
    for name, (lw, cw_, gap, lo, his, sur) in MOUND_LAYOUTS.items():
        lab = short if sur else label
        w = lambda s: sum(cw_ if ord(c) > 0x2e80 else lw for c in s) + gap
        widths = [sum(w(lab(k)) for k in u) for u in units]
        # the widest-base fit: the last line should be nearly full
        best = max((pack(widths, lo, hi) for hi in his),
                   key=lambda L: (L[-1][1] / max(x for _, x in L)) - 0.002 * len(L))
        rows = ''.join('<div class="row">' + ''.join(span(k, sur) for k in ks) + '</div>' for ks, _ in best)
        out.append(f'<div class="mound {name}">{rows}</div>')
    return '\n'.join(out)


def timeline(lang):
    items = [f'<span class="ms"><b>{esc(zh if lang == "zh" else en)}</b><i>{y}</i></span>' for en, zh, y in MILESTONES]
    return '<div class="tl">' + '<span class="arr">→</span>'.join(items) + '<span class="arr">→</span><span class="ms ai"><b>AI</b><i>2026</i></span></div>'


# Web3Forms access key for the contact form (from web3forms.com; it maps to the inbox, which never appears in the page).
WEB3FORMS_KEY = '52178693-3a18-435c-84d2-5e32494c379e'

SEAFILL = 'https://huggingface.co/SeaFill2025'
SEAFILL_LOGO = 'https://cdn-avatars.huggingface.co/v1/production/uploads/68d669e121785bf79dec4f7a/HN8cIsNLsI8vrUUvv4sva.png'

CSS = '''
.finder{background:var(--sheet);border:1px solid var(--rule);border-radius:6px;padding:1.3rem 1.4rem;margin-top:1.1rem}
.finder h2{margin-bottom:.3rem}.finder>p{color:var(--muted);margin:0 0 .9rem}
.qwrap{position:relative}
.qwrap input{width:100%;font:1rem var(--f-body);padding:.7rem .9rem;border:1px solid var(--rule);border-radius:5px;background:var(--paper);color:var(--ink)}
.qwrap input:focus{outline:2px solid var(--use);outline-offset:0;border-color:var(--use)}
.sug{position:absolute;left:0;right:0;top:calc(100% + 4px);background:var(--sheet);border:1px solid var(--rule);border-radius:5px;box-shadow:0 8px 24px rgba(0,0,0,.12);z-index:5;max-height:22rem;overflow:auto}
.sug button{display:flex;justify-content:space-between;gap:1rem;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--rule);padding:.5rem .9rem;font:.95rem var(--f-body);color:var(--ink);cursor:pointer}
.sug button:last-child{border-bottom:0}
.sug button:hover,.sug button.on{background:var(--paper)}
.sug small{color:var(--muted);font:.75rem var(--f-mono);white-space:nowrap}
.try{margin-top:.6rem;font-size:.85rem;color:var(--muted)}
.try button{background:none;border:0;padding:0 .15rem;color:var(--use);font:inherit;cursor:pointer;text-decoration:underline;text-decoration-color:var(--rule)}
.res{margin-top:1rem}
.res .who{font:900 1.5rem/1.3 var(--f-display)}.res .who small{font:400 .85rem var(--f-body);color:var(--muted);margin-left:.4rem}
.res .line{margin:.6rem 0 .2rem}
.res .line b{font-family:var(--f-display);font-size:1.15rem}
.res ul{margin:.2rem 0 0;padding-left:1.2rem;font-size:.9rem;color:var(--muted)}
.res li i{color:var(--ink)}
.res .go{font-weight:600;font-size:.9rem}
.contact{max-width:34rem;background:var(--sheet);border:1px solid var(--rule);border-radius:6px;padding:1rem 1.1rem}
.contact h2{font-size:1.25rem;margin:0}
.contact>p{color:var(--muted);margin:.15rem 0 .7rem;font-size:.9rem}
.contact form{display:grid;grid-template-columns:1fr 1fr;gap:.55rem}
.contact label{display:flex;flex-direction:column;gap:.25rem;font:.78rem var(--f-mono);color:var(--muted);letter-spacing:.03em}
.contact .full{grid-column:1/-1}
.contact input,.contact select,.contact textarea{font:.9rem var(--f-body);padding:.4rem .6rem;border:1px solid var(--rule);border-radius:5px;background:var(--paper);color:var(--ink)}
.contact textarea{min-height:4.5rem;resize:vertical}
.contact button[type=submit]{justify-self:start;font:600 .88rem var(--f-body);background:var(--ink);color:var(--paper);border:0;border-radius:5px;padding:.45rem 1.1rem;cursor:pointer}
.contact button[disabled]{opacity:.5;cursor:default}
.contact .msg{grid-column:1/-1;font-size:.88rem;margin:0}
.contact .msg.ok{color:var(--use)}.contact .msg.err{color:#c25a4a}
.contact .fine{grid-column:1/-1;font-size:.78rem;color:var(--muted);margin:0}
.hp{position:absolute;left:-9999px}
@media (max-width:520px){.contact form{grid-template-columns:1fr}.finder,.contact{padding:1.1rem 1rem}}
.team{display:inline-flex;align-items:center;gap:.6rem;margin-top:1.3rem;text-decoration:none;color:var(--ink)}
.team img{width:34px;height:34px;border-radius:8px;flex:none}
.team b{display:block;font:700 1.05rem/1.2 var(--f-display)}
.team small{display:block;font:.72rem var(--f-mono);color:var(--muted);letter-spacing:.04em}
.team:hover b{color:var(--use)}
.essay{display:block;width:fit-content;margin-top:.9rem;font-weight:600;color:var(--use);text-decoration:none;border-bottom:1px solid var(--use-soft)}
.essay:hover{border-bottom-color:var(--use)}
.hero{padding-bottom:.5rem}
.hero h1{font-size:clamp(2.3rem,7vw,3.9rem)}
.manifesto{font:600 clamp(1.05rem,2.6vw,1.25rem)/1.6 var(--f-display);border-left:3px solid var(--gold);padding:.1rem 0 .1rem 1rem;margin:1.4rem 0 0;max-width:40rem}
.card{display:block;background:var(--sheet);border:1px solid var(--rule);border-top:4px solid var(--gold);border-radius:6px;padding:1.5rem 1.4rem;margin-top:1.1rem;text-decoration:none;color:inherit}
a.card:hover,a.card:focus-visible{border-color:var(--gold);outline:none}
.card h2{margin:.6rem 0 .4rem}
.card p{margin:.3rem 0;max-width:44rem}
.card .go{display:inline-block;margin-top:.9rem;font-weight:600;color:var(--use)}
.card .upd{margin-top:.9rem;font-size:.82rem;color:var(--muted);border-left:2px solid var(--rule);padding-left:.6rem}
.card .src{margin-top:.9rem;font:.78rem var(--f-mono);color:var(--muted)}
.card .stats{margin-top:1.1rem}
.tl{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .5rem;margin:1.1rem 0 .2rem}
.ms{display:inline-flex;flex-direction:column;align-items:center;line-height:1.2;padding:.3rem .55rem;border:1px solid var(--rule);border-radius:4px;background:var(--paper)}
.ms b{font:600 .95rem var(--f-display)}
.ms i{font:.68rem var(--f-mono);font-style:normal;color:var(--muted)}
.ms.ai{background:var(--ink);border-color:var(--ink)}.ms.ai b,.ms.ai i{color:var(--paper)}
.arr{color:var(--muted);font-size:.8rem}
.viz{margin:1.2rem 0 .4rem;text-align:center}
.aiblk{display:inline-block;font:600 .85rem var(--f-mono);letter-spacing:.08em;color:var(--paper);background:var(--ink);padding:.4rem 1rem;border-radius:4px 4px 0 0}
.aiblk small{display:block;font-size:.66rem;opacity:.75;letter-spacing:.04em}
.pyr{--s:1.02;border-top:3px solid var(--ink);padding-top:.7rem}
.row{display:flex;flex-wrap:wrap;justify-content:center;align-items:baseline;gap:.15rem 1.1rem;padding:.16rem 0;margin:0 auto}

.g{font-size:calc(var(--s)*1rem);font-family:var(--f-display);font-weight:600;color:var(--ink);line-height:1.25;white-space:nowrap}
.g.laur{color:var(--gold);font-weight:900}
.g.cjk{font-size:calc(var(--s)*1.12rem)}
.thanks{text-align:center;margin:1.1rem 0 .2rem}
.res .tb{margin-top:.8rem}
.legend{font:.74rem var(--f-mono);color:var(--muted);margin-top:.7rem}
.legend b{color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.75rem}
.soon{border:1px dashed var(--rule);border-radius:6px;padding:1rem;color:var(--muted)}
.soon b{display:block;color:var(--ink);font:600 1.1rem var(--f-display)}
.mound.mid,.mound.narrow{display:none}
@media (max-width:860px){.mound.wide{display:none}.mound.mid{display:block}}
@media (max-width:520px){.mound.mid{display:none}.mound.narrow{display:block}
 .g{font-size:calc(var(--s)*.78rem)}.g.cjk{font-size:calc(var(--s)*.87rem)}.row{gap:.1rem .7rem}.card{padding:1.2rem 1rem}
 .ms b{font-size:.85rem}.ms{padding:.25rem .45rem}.tl{gap:.35rem}.tl .arr{display:none}
 .hero h1{font-size:1.7rem}}

/* ===== 新版首页 · 与博客、数学页同一设计系统（墨色 · 纸白 · 朱红） ===== */
:root{--paper:#FAFAF8;--sheet:#FFFFFF;--ink:#12161C;--muted:#5C636B;--rule:#E3E1DC;--bg2:#F0EFEB;
--accent:#B8321C;--accent-soft:#F8E6E1;--gold:#8E6410;--gold-soft:#F6EDD8;--use:#1D6A63;--use-soft:#DCEDEA;--wolf:#6B4797;
--hero:#12161C;--on-hero:#F5F3EE;--on-hero-2:#B4BAC1;--hero-rule:#343C46;--hero-accent:#F06A4E;
--shadow:0 1px 2px rgba(18,22,28,.05),0 8px 24px rgba(18,22,28,.07);--shadow-lg:0 2px 6px rgba(18,22,28,.08),0 24px 60px rgba(18,22,28,.18);
--f-display:"Source Serif 4","Noto Serif SC","Songti SC","STSong",Georgia,serif;
--f-body:"IBM Plex Sans","Noto Sans SC","PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#12161C;--sheet:#1A1F26;--ink:#ECEAE5;--muted:#A3AAB2;--rule:#2C333C;--bg2:#232A32;
--accent:#F06A4E;--accent-soft:#3B231E;--gold:#E2B654;--gold-soft:#3A3020;--use:#5CC2B6;--use-soft:#183A37;--wolf:#C3A3E6;--hero:#0B0E12;--hero-rule:#2C333C;
--shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.25);--shadow-lg:0 24px 60px rgba(0,0,0,.5);color-scheme:dark}}
:root[data-theme="dark"]{--paper:#12161C;--sheet:#1A1F26;--ink:#ECEAE5;--muted:#A3AAB2;--rule:#2C333C;--bg2:#232A32;
--accent:#F06A4E;--accent-soft:#3B231E;--gold:#E2B654;--gold-soft:#3A3020;--use:#5CC2B6;--use-soft:#183A37;--wolf:#C3A3E6;--hero:#0B0E12;--hero-rule:#2C333C;color-scheme:dark}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased;overflow-x:clip}
main{max-width:none;margin:0;padding:0}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.wrap{max-width:1120px;margin:0 auto;padding:0 16px}
@media (min-width:720px){.wrap{padding:0 32px}}
h1,h2{font-family:var(--f-display);font-weight:900;letter-spacing:.005em}
html[lang="en"] h1,html[lang="en"] h2{font-weight:600;letter-spacing:-.01em}

/* ---------- 首屏 ---------- */
.hero{background:var(--hero);color:var(--on-hero);position:relative;isolation:isolate;overflow:hidden;padding:0 0 56px}
.hero::before{content:"";position:absolute;inset:0;z-index:-1;opacity:.55;background-image:radial-gradient(circle at 1px 1px,var(--hero-rule) 1px,transparent 1.4px);background-size:22px 22px;
 -webkit-mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent);mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent)}
.hero .top{padding:22px 0;color:var(--on-hero-2)}
.hero .top a{display:inline-flex;align-items:center;min-height:36px;padding:0 14px;border:1px solid var(--hero-rule);border-radius:999px;color:var(--on-hero);text-transform:none;letter-spacing:0;font-size:.82rem}
.hero .top a:hover{border-color:var(--hero-accent)}
.hero :focus-visible{outline-color:var(--hero-accent)}
.hgrid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:40px 64px;align-items:end;margin-top:28px}
.hero h1{font-size:clamp(2.5rem,6.2vw,4.6rem);line-height:1.1;margin:0 0 1.2rem;color:var(--on-hero)}
html[lang="en"] .hero h1{font-size:clamp(2.3rem,5.4vw,4.1rem);line-height:1.06}
.hero .dek{color:#C9CED4;font-size:1.1rem;line-height:1.75;max-width:36em;margin:0}

/* 搜索（首屏主交互） */
.finder{background:none;border:0;padding:0;margin-top:2rem;max-width:640px}
.flabel{display:block;font:500 .75rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--hero-accent);margin-bottom:.6rem}
.qwrap{position:relative}
.qwrap::before{content:"";position:absolute;left:18px;top:29px;width:17px;height:17px;transform:translateY(-50%);z-index:1;pointer-events:none;background:#6B737C;
 -webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-3.5-3.5'/%3E%3C/svg%3E") center/contain no-repeat;
 mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-3.5-3.5'/%3E%3C/svg%3E") center/contain no-repeat}
.qwrap input{height:58px;padding:0 52px 0 48px;font:1.05rem var(--f-body);border:1px solid transparent;border-radius:12px;background:#FAFAF8;color:#12161C;transition:box-shadow .2s,border-color .2s}
.qwrap input::placeholder{color:#6B737C}
.qwrap input:focus{outline:none;border-color:var(--hero-accent);box-shadow:0 0 0 4px rgba(240,106,78,.28)}
.kbd{position:absolute;right:14px;top:29px;transform:translateY(-50%);font:12px/1 var(--f-mono);color:#5C636B;border:1px solid #D7D4CE;border-bottom-width:2px;border-radius:5px;padding:4px 7px;background:#fff;pointer-events:none}
.qwrap:focus-within .kbd{opacity:0}
.sug{top:calc(100% + 6px);border-radius:12px;box-shadow:var(--shadow-lg);padding:6px;border-color:var(--rule);background:var(--sheet)}
.sug button{border:0;border-radius:8px;min-height:44px;padding:.55rem .8rem;align-items:center;color:var(--ink)}
.sug button:hover,.sug button.on{background:var(--bg2)}
.try{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:14px;font-size:.84rem;color:var(--on-hero-2)}
.try button{border:1px solid var(--hero-rule);background:rgba(255,255,255,.04);color:var(--on-hero);border-radius:999px;padding:0 14px;min-height:34px;font:.88rem var(--f-body);text-decoration:none;cursor:pointer;transition:border-color .15s,background .15s}
.try button:hover{border-color:var(--hero-accent);background:rgba(240,106,78,.12)}
.res{margin-top:14px}
.res:not(:empty){background:var(--sheet);color:var(--ink);border-radius:12px;padding:1.1rem 1.25rem;box-shadow:var(--shadow-lg);animation:rise .3s cubic-bezier(.2,.8,.2,1)}
@keyframes rise{from{opacity:0;transform:translateY(6px)}}
@media (prefers-reduced-motion:reduce){.res:not(:empty){animation:none}}
.res .who{font-weight:900}
html[lang="en"] .res .who{font-weight:600}
.res .line b{color:var(--accent)}
.res .go{color:var(--accent);text-decoration:none}
.res .go:hover{text-decoration:underline}
.res li i{color:var(--ink)}

/* 首屏数字 */
.hstats{border-top:1px solid var(--hero-rule)}
.hstats .stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0;margin:0}
.hstats .stat{border:0;border-bottom:1px solid var(--hero-rule);padding:18px 0 16px}
.hstats .stat:nth-child(odd){padding-right:18px;border-right:1px solid var(--hero-rule)}
.hstats .stat:nth-child(even){padding-left:18px}
.hstats .stat b{font:600 clamp(2.2rem,4.2vw,3.2rem)/1.02 var(--f-display);color:var(--on-hero);font-variant-numeric:tabular-nums lining-nums}
.hstats .stat:first-child b{color:var(--hero-accent)}
.hstats .stat span{color:var(--on-hero-2);font-size:.84rem;margin-top:6px}
.hcap{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:12px;font:.75rem var(--f-mono);letter-spacing:.04em;color:var(--on-hero-2)}
.hcap a{color:var(--hero-accent);text-decoration:none;font-family:var(--f-body);font-size:.85rem;letter-spacing:0}
.hcap a:hover{text-decoration:underline}

.hfoot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px 40px;margin-top:48px;padding-top:28px;border-top:1px solid var(--hero-rule)}
.manifesto{flex:1 1 420px;margin:0;border:0;padding:0;max-width:40rem;font:600 clamp(1.05rem,2.2vw,1.25rem)/1.65 var(--f-display);color:var(--on-hero)}
.hlinks{display:flex;flex-direction:column;gap:12px;align-items:flex-start}
.team{margin:0;color:var(--on-hero)}
.team small{color:var(--on-hero-2)}
.team:hover b{color:var(--hero-accent)}
.essay{display:inline-flex;align-items:center;min-height:44px;margin:0;padding:0 18px;border-radius:8px;background:var(--hero-accent);color:#12161C;border:0;text-decoration:none;font-weight:600}
.essay:hover{background:#FF8B73}

/* ---------- 分区 ---------- */
.sec{margin-top:88px}
.sechead{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;border-top:2px solid var(--ink);padding-top:18px;margin-bottom:22px;position:relative}
.sechead::before{content:attr(data-n);position:absolute;top:-1px;left:0;transform:translateY(-100%);font:500 12px var(--f-mono);letter-spacing:.08em;color:#fff;background:var(--accent);padding:3px 8px 2px;border-radius:3px 3px 0 0}
.sechead h2{font-size:clamp(1.9rem,3.6vw,2.6rem);margin:0}
.sechead span{font:500 .75rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}

.card{position:relative;display:block;background:var(--sheet);border:1px solid var(--rule);border-top:1px solid var(--rule);border-radius:14px;padding:clamp(1.3rem,3vw,2.2rem);margin-top:20px;color:inherit;text-decoration:none;transition:border-color .18s,box-shadow .18s,transform .18s}
a.card:hover,a.card:focus-visible{border-color:var(--ink);box-shadow:var(--shadow);transform:translateY(-2px);outline:none}
.card h2{font-size:clamp(1.5rem,3vw,2.1rem);line-height:1.25;margin:.8rem 0 .5rem}
.card h2 a:hover{color:var(--accent)!important}
.card p{color:var(--muted);max-width:46rem;margin:.4rem 0}
.tag{background:var(--bg2);color:var(--muted);border-radius:999px;padding:.18rem .7rem;font-size:.7rem}
.tag.new{background:var(--accent);color:#fff}
.card .go{display:inline-flex;align-items:center;gap:6px;margin-top:1.1rem;font-weight:600;color:var(--accent);text-decoration:none}
a.card .go::after,.card a.go::after{content:"→";transition:transform .18s}
a.card:hover .go::after,.card a.go:hover::after{transform:translateX(4px)}
.card a.go{min-height:44px;padding:0 18px;border-radius:8px;background:var(--ink);color:var(--paper)}
.card a.go:hover{background:var(--accent);color:#fff}
.card.feature{padding-top:clamp(1.5rem,3.4vw,2.6rem)}
.card .upd{border-left:2px solid var(--accent);color:var(--muted)}
.card .src a{color:var(--muted)}

/* 时间线 */
.tl{gap:8px 6px;margin:1.4rem 0 .2rem}
.ms{border:1px solid var(--rule);border-radius:8px;background:var(--paper);padding:.4rem .7rem;transition:border-color .15s}
a.card:hover .ms{border-color:color-mix(in srgb,var(--ink) 25%,var(--rule))}
.ms b{font-weight:600}
.ms i{color:var(--accent)}
.ms.ai{background:var(--ink);border-color:var(--ink)}
.ms.ai i{color:var(--hero-accent)}
.arr{color:var(--rule);font-size:.9rem}

/* 人名堆 */
.viz{margin:1.8rem auto .6rem;max-width:880px}
.aiblk{background:var(--ink);color:var(--paper);border-radius:8px 8px 0 0;padding:.5rem 1.2rem}
.pyr{border-top:3px solid var(--ink);padding-top:.9rem}
.g{transition:color .15s;cursor:default}
.g:hover{color:var(--accent)}
.g.laur{color:var(--gold)}
.legend b{color:var(--gold)}

/* 下一期 */
.next{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.soon{border:1px dashed var(--rule);border-radius:14px;padding:1.3rem 1.4rem;color:var(--muted);background:transparent}
.soon b{font-size:1.3rem;margin-bottom:.2rem}
.soon.ask{border:1px solid var(--accent);background:var(--accent-soft);color:var(--ink);text-decoration:none;display:flex;flex-direction:column;justify-content:space-between;gap:.6rem;transition:transform .15s}
.soon.ask:hover{transform:translateY(-2px)}
.soon.ask span{color:var(--accent);font-weight:600}
@media (max-width:760px){.next{grid-template-columns:1fr 1fr}.soon.ask{grid-column:1/-1}}

/* 联系表单 */
.contact{max-width:none;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:24px 48px;border-radius:14px;padding:clamp(1.3rem,3vw,2.2rem)}
.contact h2{font-size:clamp(1.6rem,3vw,2.1rem)}
.contact>p{font-size:1rem;line-height:1.7}
.contact .intro{grid-column:1}
.contact form{grid-column:2;grid-row:1/span 2;gap:.8rem}
.contact label{font-size:.72rem;letter-spacing:.06em;text-transform:uppercase}
.contact input,.contact select,.contact textarea{font-size:.98rem;padding:.65rem .8rem;border-radius:8px;min-height:44px;text-transform:none;letter-spacing:0;transition:border-color .15s,box-shadow .15s}
.contact input:focus,.contact select:focus,.contact textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.contact textarea{min-height:7rem}
.contact button[type=submit]{min-height:46px;padding:0 1.6rem;border-radius:8px;font-size:.95rem;transition:background .15s}
.contact button[type=submit]:hover{background:var(--accent)}
.contact .msg.ok{color:var(--use)}
@media (max-width:820px){.contact{grid-template-columns:1fr}.contact form{grid-column:1;grid-row:auto}}

footer.foot{margin-top:96px;padding:40px 0 calc(40px + env(safe-area-inset-bottom,0px));border:0;background:var(--hero);color:#C9CED4;font-size:.9rem}
footer.foot a{color:var(--hero-accent)}

@media (max-width:900px){.hgrid{grid-template-columns:1fr}}
@media (max-width:560px){
 .hero{padding-bottom:40px}.hgrid{margin-top:12px}
 .hero h1{font-size:2.3rem}
 html[lang="en"] .hero h1{font-size:2.1rem}
 .qwrap input{height:54px}.qwrap::before,.kbd{top:27px}.kbd{display:none}
 .sec{margin-top:72px}
 .hfoot{margin-top:36px}
}
'''

JS = r'''
(function(){
const C=window.__CFG__,S=C.s,$=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fold=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const fill=(s,o)=>s.replace(/\{(\w+)\}/g,(m,k)=>o[k]);
// ---- finder ----
let IDX=null;
const load=()=>IDX||(IDX=fetch(C.idx).then(r=>r.json()).then(d=>d.map(x=>({x,k:fold(x[0]+' '+x[1])}))));
const q=$('#q'),sug=$('#sug'),res=$('#res');let hits=[],on=0;
const label=x=>C.zh&&x[1]?x[1]+' · '+x[0]:x[0];
function find(v){v=fold(v.trim());if(!v)return Promise.resolve([]);
 return load().then(L=>{const a=[],b=[];for(const e of L){const i=e.k.indexOf(v);if(i<0)continue;(i===0||e.k[i-1]===' '?a:b).push(e.x);if(a.length>=8)break}return a.concat(b).slice(0,8)})}
function showSug(){sug.hidden=!hits.length;sug.innerHTML=hits.map((x,i)=>`<button type="button" data-i="${i}" class="${i===on?'on':''}"><span>${esc(label(x))}</span><small>${x[3]+x[7]+(x[9]||0)}</small></button>`).join('')}
function card(x){
 const pz=x[2]?x[2].split(' ').map(p=>`<span class="chip ${p.slice(0,2)}">${S.prize[p.slice(0,2)]} ${p.slice(2)}</span>`).join(''):'';
 let h=`<div class="who">${esc(C.zh&&x[1]?x[1]:x[0])}${C.zh&&x[1]?`<small>${esc(x[0])}</small>`:''}${pz}</div>`;
 if(x[3]){h+=`<p class="line">${fill(S.fMath,{mp:x[4],me:x[3]})}</p>`;
  if(x[6].length)h+=`<div>${S.fTop}</div><ul>${x[6].map(w=>`<li><i>${esc(w[0])}</i>${w[1]?' ('+esc(w[1])+')':''} · ${w[2]} ${S.fPp}</li>`).join('')}</ul>`;
  h+=`<p><a class="go" href="${C.math}#a${x[5]}">${S.fGoM}</a></p>`}
 if(x[7]){h+=`<p class="line">${fill(S.fNs,{ne:x[7]})}</p><ul>${x[8].map(w=>`<li><i>${esc(w[0])}</i>${w[1]?' ('+esc(w[1])+')':''}</li>`).join('')}</ul><p><a class="go" href="${C.ns}">${S.fGoN}</a></p>`}
 if(x[9]){h+=`<p class="line">${fill(S.fAf,{ae:x[9]})}</p><ul>${x[10].map(w=>`<li><i>${esc(w[0])}</i>${w[1]?' ('+esc(w[1])+')':''}</li>`).join('')}</ul><p><a class="go" href="${C.af}">${S.fGoA}</a></p>`}
 res.innerHTML=h;sug.hidden=true}
function pick(x){q.value=label(x);card(x)}
q.addEventListener('focus',load,{once:true});
q.addEventListener('input',()=>{const v=q.value;if(!IDX)res.textContent=S.fLoading;find(v).then(h=>{if(q.value!==v)return;if(res.textContent===S.fLoading)res.textContent='';hits=h;on=0;showSug();if(v.trim()&&!h.length)res.textContent=S.fNone})});
q.addEventListener('keydown',e=>{if(sug.hidden)return;if(e.key==='ArrowDown'){on=Math.min(on+1,hits.length-1);showSug();e.preventDefault()}else if(e.key==='ArrowUp'){on=Math.max(on-1,0);showSug();e.preventDefault()}else if(e.key==='Enter'&&hits[on]){pick(hits[on]);e.preventDefault()}else if(e.key==='Escape')sug.hidden=true});
sug.addEventListener('click',e=>{const b=e.target.closest('button');if(b)pick(hits[+b.dataset.i])});
document.addEventListener('click',e=>{if(!e.target.closest('.qwrap'))sug.hidden=true});
document.querySelectorAll('[data-q]').forEach(b=>b.addEventListener('click',()=>{q.value=b.dataset.q;find(b.dataset.q).then(h=>{if(h[0])pick(h[0]);else res.textContent=S.fNone})}));
// ---- contact (Web3Forms) ----
const f=$('#cform'),m=$('#cmsg'),btn=f.querySelector('button[type=submit]');
if(!C.key){btn.disabled=true;m.textContent=S.cOff}
f.addEventListener('submit',e=>{e.preventDefault();if(!C.key)return;
 if(!f.reportValidity())return;
 const d=Object.fromEntries(new FormData(f));if(d.botcheck)return;
 btn.disabled=true;btn.textContent=S.cSending;m.className='msg';m.textContent='';
 fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},
  body:JSON.stringify({access_key:C.key,subject:'[巨人之肩 / On Whose Shoulders] '+d.topic,from_name:d.name||'Shoulders visitor',name:d.name,email:d.email,replyto:d.email,topic:d.topic,message:d.message,page:location.href})})
 .then(r=>r.json()).then(j=>{if(!j.success)throw 0;m.className='msg ok';m.textContent=S.cOk;f.reset()})
 .catch(()=>{m.className='msg err';m.textContent=S.cErr})
 .finally(()=>{btn.disabled=false;btn.textContent=S.cSend})});
})();
'''

T = {
 'zh': dict(
  lang='zh-CN', title='巨人之肩 · On Whose Shoulders', alt=('English', '../'), ns='../navier-stokes/zh/', math='../math/zh/', af='../alphafold/zh/', idx='../search.json',
  desc='向 AI 时代的人类科学家致敬：逐条记录 AI 前沿成果引用的人类科学家，按学科分开，随每一次突破更新。',
  eyebrow='巨人之肩 · On Whose Shoulders',
  h1='AI 的科学突破，<br>站在人类科学家的肩膀上',
  dek='AI 与超级智能正在走向科学前沿。它们迈出的每一步，用到的概念、方法与工具，都来自几代科学家一生的积累。',
  manifesto='我们找出 AI 成果引用的每一位科学家，写下他们的名字。他们是连接人类知识与 AI 的桥梁，也是我们永远尊敬的人。',
  team=('Sea-Fill 开源科学团队', '我们是 Sea-Fill，一个开源科学团队'),
  essay=('阅读我们的文章：AI 的数学，建立在什么之上 →', '../blog/zh/'),
  tAll='向他们致敬', tDone='已致敬 · 谢谢你', tCount='次致敬', tOne='向 {n} 致敬',
  fH='寻找一位巨人', fP='输入一位科学家的名字，看看 AI 站在了他们的哪些工作之上。',
  fPh='输入名字：陶哲轩、Grothendieck、欧拉……', fTry='试试：', fTries=['陶哲轩', 'Grothendieck', '欧拉', '王虹'],
  fLoading='正在载入索引…', fNone='没有找到。这个名字暂未出现在已收录的 AI 论文参考文献中。',
  fMath='数学全景：被 <b>{mp}</b> 篇 AI 数学预印本引用，共 <b>{me}</b> 条参考文献。', fTop='被引最多的著作：', fPp='篇引用',
  fNs='流体方程：OpenAI 的 Navier–Stokes / Euler 论文引用了 <b>{ne}</b> 条。', fGoM='在数学专题中查看 →', fGoN='查看流体方程专题 →',
  prize={'fm': '菲尔兹奖', 'ab': '阿贝尔奖', 'wf': '沃尔夫奖', 'nc': '诺贝尔化学奖'},
  fAf='蛋白质结构：AlphaFold 2 论文引用了 <b>{ae}</b> 条。', fGoA='查看 AlphaFold 专题 →',
  cH='写信给我们', cP='纠正一处引用，推荐下一项值得铭记的 AI 科学突破，或与我们一起把这件事做下去。',
  cName='称呼（可选）', cEmail='你的邮箱（用于回复）', cType='类型', cTypes=['纠错', '推荐下一期 AI 突破', '合作', '其他'], cMsg='内容',
  cSend='发送', cSending='发送中…', cOk='已发送，谢谢！我们会尽快回复。', cErr='发送失败，请稍后再试。', cOff='表单尚未启用。',
  cFine='提交的内容经 Web3Forms 转发给 Sea-Fill 团队，只用于回复你。',
  secMath='数学',
  nsTag='2026 年 9 月 · 流体方程', nsH='从欧拉到 AI：Navier–Stokes 与 Euler 方程',
  nsP=f'OpenAI 发布的 Navier–Stokes 与 Euler 方程两篇论文，附 Lean 形式化。它们的 {NS_REFS} 条参考文献，从 1757 年的欧拉一直延续到 2026 年。',
  nsGo='进入流体方程专题 →',
  mTag='最新 · 2026 年 10 月 · 数学全景', mH=f'OpenAI Math Release：{NP} 篇 AI 数学稿件',
  mP=(f'OpenAI 于 2026 年 10 月 6 日发布了由其内部模型撰写的 {RELEASED} 篇数学稿件，现存 {NP} 篇，归为 {NF} 个成果。托起它们的，是下面这些名字。' if NP != RELEASED else f'OpenAI 发布了由其内部模型撰写的 {RELEASED} 篇数学稿件，归为 {NF} 个成果。托起它们的，是下面这些名字。'),
  fLabel='寻找一位巨人', kbdHint='按 / 搜索', hCap='OpenAI Math Release · 每天自动更新', hGo='查看数学全景 →',
  nMath='01', nChem='02', nNext='03', nContact='04', more2='下一期',
  askH='推荐下一项突破', askP='你觉得下一项值得记录的 AI 科学突破是什么？', askGo='告诉我们 →',
  aiS=f'{NP} 篇稿件 · {NF} 个成果',
  upd=f'注：2026 年 10 月 7 日，OpenAI 撤回 3 篇稿件并修订了另外 14 篇。以上数字按当前的 {NP} 篇稿件统计，每天自动更新。' if NP != RELEASED else '',
  legend='<b>金色</b> = 菲尔兹 / 阿贝尔 / 沃尔夫奖得主。',
  st=[(NP, f'篇当前稿件（{NF} 个成果）'), (M['works'], '部被引用的人类著作'), (len(A), '位人类作者'), (M_LAUR, '位获奖数学家被引用')],
  mGo='进入数学专题 →', src='数据来源',
  secChem='化学 · 生命科学',
  afTag='2021 年 7 月 · 蛋白质结构', afH='从安芬森到 AlphaFold：蛋白质结构预测',
  afP=f'DeepMind 的 AlphaFold 2 以接近实验的精度预测蛋白质结构，并因此获得 2024 年诺贝尔化学奖的一半。它的 {AF_REFS} 条参考文献，从 1973 年安芬森的“序列决定结构”延续到 2021 年。',
  afGo='进入 AlphaFold 专题 →',
  more='其他学科', soon='即将推出', subs=['物理', '计算机科学'],
  foot='引用不等于依赖；本项目不评判 AI 结果的正确性、原创性或归属，只记下名字，向他们致敬。',
 ),
 'en': dict(
  lang='en', title='On Whose Shoulders · 巨人之肩', alt=('中文', 'zh/'), ns='navier-stokes/', math='math/', af='alphafold/', idx='search.json',
  desc='A tribute to the human scientists of the AI era: every human scientist cited by frontier AI results, field by field, updated with each breakthrough.',
  eyebrow='On Whose Shoulders · 巨人之肩',
  h1='AI’s scientific breakthroughs<br>stand on human shoulders',
  dek='AI and superintelligence are reaching the frontier of science. Every step they take uses ideas, methods and tools that generations of scientists spent their lives building.',
  manifesto='We find every scientist an AI result cites and write down their name. They are the bridge between human knowledge and AI, and the people we will always honour.',
  team=('Sea-Fill · open-source science team', 'We are Sea-Fill, an open-source science team'),
  essay=('Read our essay: What AI’s mathematics is built on →', 'blog/'),
  tAll='Pay tribute to them', tDone='Tribute paid · thank you', tCount='tributes', tOne='Pay tribute to {n}',
  fH='Find a giant', fP='Type a scientist’s name to see which of their works AI has built upon.',
  fPh='Type a name: Terence Tao, Grothendieck, Euler…', fTry='Try: ', fTries=['Terence Tao', 'Grothendieck', 'Euler', 'Hong Wang'],
  fLoading='Loading the index…', fNone='No match. This name does not appear in the references of the AI papers covered so far.',
  fMath='Mathematics overview: cited by <b>{mp}</b> AI-written preprints, <b>{me}</b> reference entries in all.', fTop='Most-cited works:', fPp='citing preprints',
  fNs='Fluid equations: cited <b>{ne}</b> times in OpenAI’s Navier–Stokes / Euler papers.', fGoM='Open in the mathematics index →', fGoN='Open the fluid equations page →',
  prize={'fm': 'Fields', 'ab': 'Abel', 'wf': 'Wolf', 'nc': 'Nobel Chemistry'},
  fAf='Protein structure: cited <b>{ae}</b> times in the AlphaFold 2 paper.', fGoA='Open the AlphaFold page →',
  cH='Write to us', cP='Correct a citation, suggest the next AI breakthrough worth remembering, or join us in carrying this on.',
  cName='Name (optional)', cEmail='Your email (for our reply)', cType='Topic', cTypes=['Correction', 'Suggest the next AI breakthrough', 'Collaboration', 'Other'], cMsg='Message',
  cSend='Send', cSending='Sending…', cOk='Sent, thank you! We will reply soon.', cErr='Sending failed; please try again later.', cOff='The form is not enabled yet.',
  cFine='Your message is forwarded to the Sea-Fill team by Web3Forms and used only to reply to you.',
  secMath='Mathematics',
  nsTag='September 2026 · Fluid equations', nsH='From Euler to AI: Navier–Stokes and Euler',
  nsP=f'OpenAI’s two papers on the Navier–Stokes and Euler equations, released with Lean formalizations. Their {NS_REFS} references run from Euler in 1757 to 2026.',
  nsGo='Open the fluid equations page →',
  mTag='Latest · October 2026 · Mathematics overview', mH=f'OpenAI Math Release: {NP} AI-written math manuscripts',
  mP=(f'On 6 October 2026 OpenAI released {RELEASED} mathematics manuscripts written by its internal model; {NP} remain current, grouped into {NF} results. Holding them up are the names below.' if NP != RELEASED else f'OpenAI released {RELEASED} mathematics manuscripts written by its internal model, grouped into {NF} results. Holding them up are the names below.'),
  fLabel='Find a giant', kbdHint='Press / to search', hCap='OpenAI Math Release · updated daily', hGo='Open the mathematics index →',
  nMath='01', nChem='02', nNext='03', nContact='04', more2='Next',
  askH='Suggest the next breakthrough', askP='Which AI result in science should we record next?', askGo='Tell us →',
  aiS=f'{NP} manuscripts · {NF} results',
  upd=f'Note: on 7 October 2026 OpenAI withdrew 3 manuscripts and revised 14 others. The figures above count the {NP} current manuscripts and update daily.' if NP != RELEASED else '',
  legend='<b>Gold</b> = Fields / Abel / Wolf laureate.',
  st=[(NP, f'current manuscripts ({NF} results)'), (M['works'], 'human works cited'), (len(A), 'human authors'), (M_LAUR, 'laureates cited')],
  mGo='Open the mathematics index →', src='Source',
  secChem='Chemistry · Life sciences',
  afTag='July 2021 · Protein structure', afH='From Anfinsen to AlphaFold: protein structure prediction',
  afP=f'DeepMind’s AlphaFold 2 predicts protein structures with near-experimental accuracy, work recognised with half of the 2024 Nobel Prize in Chemistry. Its {AF_REFS} references run from Anfinsen’s “sequence determines structure” in 1973 to 2021.',
  afGo='Open the AlphaFold page →',
  more='Other fields', soon='Coming soon', subs=['Physics', 'Computer science'],
  foot='Citation is not dependence; this project does not judge the correctness, originality or attribution of AI results. It records names, in tribute.',
 ),
}

for k, t in T.items():
    stats_html = ''.join(f'<div class="stat"><b>{n:,}</b><span>{esc(l)}</span></div>' for n, l in t['st'])
    body = f'''<div class="hero"><div class="wrap">
<div class="top"><span>{t['eyebrow']}</span><a href="{t['alt'][1]}" hreflang="{'en' if k == 'zh' else 'zh'}">{t['alt'][0]}</a></div>
<div class="hgrid">
<div>
<h1>{t['h1']}</h1>
<p class="dek">{t['dek']}</p>
<section class="finder" id="finder" aria-label="{esc(t['fH'])}">
<label class="flabel" for="q">{t['fLabel']}</label>
<div class="qwrap"><input id="q" type="search" autocomplete="off" placeholder="{esc(t['fPh'])}" aria-describedby="fhelp"><span class="kbd" aria-hidden="true">/</span><div class="sug" id="sug" hidden></div></div>
<p id="fhelp" hidden>{t['fP']}</p>
<div class="try"><span>{t['fTry']}</span>{''.join(f'<button type="button" data-q="{esc(x)}">{esc(x)}</button>' for x in t['fTries'])}</div>
<div class="res" id="res" aria-live="polite"></div>
</section>
</div>
<aside class="hstats">
<div class="stats">{stats_html}</div>
<div class="hcap"><span>{t['hCap']}</span><a href="{t['math']}">{t['hGo']}</a></div>
</aside>
</div>
<div class="hfoot">
<p class="manifesto">{t['manifesto']}</p>
<div class="hlinks">
<a class="team" href="{SEAFILL}"><img src="{SEAFILL_LOGO}" alt="" width="34" height="34"><span><b>{t['team'][0]}</b><small>{t['team'][1]}</small></span></a>
<a class="essay" href="{t['essay'][1]}">{t['essay'][0]}</a>
</div>
</div>
</div></div>

<div class="wrap">
<section class="sec" id="math">
<div class="sechead" data-n="{t['nMath']}"><h2>{t['secMath']}</h2></div>

<div class="card feature">
<span class="tag new">{t['mTag']}</span>
<h2><a href="{t['math']}" style="color:inherit;text-decoration:none">{t['mH']}</a></h2>
<p>{t['mP']}</p>
<figure class="viz">
<div class="aiblk">AI · OpenAI Math Release<small>{t['aiS']}</small></div>
<div class="pyr">
{pyramid(k)}
</div>
<figcaption class="legend">{t['legend']}</figcaption>
</figure>
<a class="go" href="{t['math']}">{t['mGo'].rstrip(' →')}</a>
{f'<p class="upd">{t["upd"]}</p>' if t['upd'] else ''}
<p class="src">{t['src']}: <a href="https://github.com/openai/math">github.com/openai/math</a> (Apache 2.0)</p>
</div>

<a class="card" href="{t['ns']}">
<span class="tag">{t['nsTag']}</span>
<h2>{t['nsH']}</h2>
<p>{t['nsP']}</p>
{timeline(k)}
<span class="go">{t['nsGo'].rstrip(' →')}</span>
</a>
</section>

<section class="sec" id="chem">
<div class="sechead" data-n="{t['nChem']}"><h2>{t['secChem']}</h2></div>
<a class="card" href="{t['af']}">
<span class="tag">{t['afTag']}</span>
<h2>{t['afH']}</h2>
<p>{t['afP']}</p>
<div class="tl">{'<span class="arr">→</span>'.join(f'<span class="ms"><b>{esc(zh if k == "zh" else en)}</b><i>{y}</i></span>' for en, zh, y in AF_MS)}<span class="arr">→</span><span class="ms ai"><b>AlphaFold 2</b><i>2021</i></span></div>
<span class="go">{t['afGo'].rstrip(' →')}</span>
</a>
</section>

<section class="sec" id="next">
<div class="sechead" data-n="{t['nNext']}"><h2>{t['more2']}</h2><span>{t['more']}</span></div>
<div class="next">{''.join(f'<div class="soon"><b>{s}</b>{t["soon"]}</div>' for s in t['subs'])}<a class="soon ask" href="#contact"><b>{t['askH']}</b>{t['askP']}<span>{t['askGo']}</span></a></div>
</section>

<section class="sec" id="contact">
<div class="sechead" data-n="{t['nContact']}"><h2>{t['cH']}</h2></div>
<div class="contact">
<p class="intro">{t['cP']}</p>
<form id="cform" novalidate>
<label>{t['cName']}<input name="name" autocomplete="name" maxlength="80"></label>
<label>{t['cEmail']}<input name="email" type="email" required autocomplete="email" maxlength="120"></label>
<label class="full">{t['cType']}<select name="topic">{''.join(f'<option>{esc(x)}</option>' for x in t['cTypes'])}</select></label>
<label class="full">{t['cMsg']}<textarea name="message" required maxlength="5000"></textarea></label>
<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<button type="submit">{t['cSend']}</button>
<p class="msg" id="cmsg" role="status"></p>
<p class="fine">{t['cFine']}</p>
</form>
</div>
</section>
</div>

<footer class="foot"><div class="wrap">{t['foot']} · <a href="{SEAFILL}">Sea-Fill</a></div></footer>
<script>document.addEventListener('keydown',function(e){{if(e.key!=='/'||e.metaKey||e.ctrlKey||e.altKey)return;var t=e.target;if(/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)||t.isContentEditable)return;e.preventDefault();var q=document.getElementById('q');q.focus({{preventScroll:true}});q.scrollIntoView({{block:'center',behavior:'smooth'}})}});</script>'''
    cfg = dict(idx=t['idx'], math=t['math'], ns=t['ns'], af=t['af'], key=WEB3FORMS_KEY, zh=k == 'zh',
               s={x: t[x] for x in ('fAf', 'fGoA', 'tOne', 'tDone', 'tCount', 'fLoading', 'fNone', 'fMath', 'fTop', 'fPp', 'fNs', 'fGoM', 'fGoN', 'prize',
                                    'cSending', 'cSend', 'cOk', 'cErr', 'cOff')})
    body += '<script>window.__CFG__=' + json.dumps(cfg, ensure_ascii=False).replace('</', '<\\/') + ';</script>\n<script>' + JS + '</script>'
    f = os.path.join(H, 'zh/index.html' if k == 'zh' else 'index.html')
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(page(k, t['title'], t['desc'], CSS, body))
