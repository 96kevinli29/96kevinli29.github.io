"""Figures for the essay, as HTML/SVG snippets. Text-heavy diagrams are HTML so they reflow on phones."""
import json, os, html

B = os.path.dirname(os.path.abspath(__file__))
esc = html.escape

CSS = '''
figure.fig{margin:2rem 0 2.2rem;padding:1.1rem 1.1rem .9rem;background:var(--sheet);border:1px solid var(--rule);border-radius:8px}
figure.fig figcaption{margin-top:.8rem;font-size:.84rem;line-height:1.55;color:var(--muted)}
figure.fig figcaption b{color:var(--ink);font-weight:600}
.fig-key{display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;font:.74rem var(--f-mono);color:var(--muted);margin-bottom:.8rem}
.fig-key i{display:inline-block;width:.7rem;height:.7rem;border-radius:2px;margin-right:.35rem;vertical-align:-.05rem}
.k-eng{background:var(--ink)}.k-sci{background:var(--gold)}
/* stages */
.stages{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem}
.stage{display:flex;flex-direction:column;gap:.45rem}
.stage h4{margin:0;font:600 .95rem var(--f-display)}
.stage h4 small{display:block;font:.68rem var(--f-mono);color:var(--muted);letter-spacing:.04em;text-transform:uppercase}
.cell{border-radius:6px;padding:.55rem .65rem;font-size:.82rem;line-height:1.45}
.cell b{display:block;font:500 .66rem var(--f-mono);letter-spacing:.05em;text-transform:uppercase;margin-bottom:.15rem}
.cell.eng{border:1px solid var(--rule);background:var(--paper)}
.cell.eng b{color:var(--muted)}
.cell.sci{background:var(--gold-soft);border:1px solid var(--gold-soft)}
.cell.sci b{color:var(--gold)}
.loop{font:.72rem var(--f-mono);color:var(--muted);text-align:center}
@media (max-width:620px){.stages{grid-template-columns:1fr}}
/* sampling */
.samp{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.samp h4{margin:0 0 .45rem;font:600 .9rem var(--f-display)}
.dots{display:grid;grid-template-columns:repeat(16,1fr);gap:3px;max-width:15rem}
.dots i{aspect-ratio:1;border-radius:50%;border:1.5px solid var(--rule);background:transparent}
.dots i.ok{background:var(--use);border-color:var(--use)}
.samp p{margin:.5rem 0 0;font-size:.8rem;line-height:1.45;color:var(--muted)}
.samp p b{color:var(--ink)}
@media (max-width:520px){.samp{grid-template-columns:1fr}}
/* relay */
.relay{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:.5rem;align-items:stretch}
.relay li{flex:1 1 7.5rem;line-height:1.35;margin:0;border:1px solid var(--rule);border-radius:6px;padding:.45rem .55rem;background:var(--paper)}
.relay li b{display:block;font:.7rem var(--f-mono);color:var(--muted)}
.relay li span{display:block;font:600 .86rem/1.35 var(--f-display)}
.relay li.ai{background:var(--ink);border-color:var(--ink)}.relay li.ai b,.relay li.ai span{color:var(--paper)}
/* decades */
.hist svg{width:100%;height:auto;display:block}
.hist .bar{fill:var(--gold)}
.hist .bar:hover{fill:var(--ink)}
.hist .ax{stroke:var(--rule)}
.hist text{fill:var(--muted);font:20px var(--f-mono)}
.hist text.v{fill:var(--ink)}
'''

T = {
 'en': dict(
  key_eng='Engineers build', key_sci='Scientists supply',
  stages=[('Pretraining', 'next-token prediction',
           'The model, the training code, data pipelines, compute.',
           'Papers, textbooks, proofs: the written record of human knowledge.'),
          ('Supervised fine-tuning', 'the cold start',
           'Fine-tuning runs and the tools that synthesise reasoning chains.',
           'Worked solutions, and the problems, instructions and checks behind synthetic chains.'),
          ('Reinforcement learning', 'rollouts and rewards',
           'The loop: many attempts, a verifier, updates toward what worked.',
           'Problems worth solving, a precise definition of correct (e.g. Lean’s Mathlib), judgement of results.')],
  loop='↻ successful attempts seed the next round',
  cap1='<b>Figure 1.</b> Two groups are most closely tied to a model capable of scientific breakthroughs. In each stage of training, engineers make learning possible; much of what there is to learn comes from scientists.',
  weak='Weak starting point', strong='Strong starting point',
  weak_p='<b>0 of 64</b> attempts correct. Every reward is zero, so there is no gradient: nothing to learn from.',
  strong_p='<b>9 of 64</b> attempts correct. The successful paths can be reinforced and seed the next round.',
  cap2='<b>Figure 2.</b> Illustration, not data: 64 attempts at the same problem by two models. Reinforcement learning can only strengthen what a model already samples. High-quality scientific data in pretraining and fine-tuning is a large part of what moves a model from the left panel to the right.',
  relay=[('1928', 'Besicovitch'), ('1971', 'Davies'), ('1995', 'Wolff'), ('2000', 'Katz · Łaba · Tao'),
         ('2006', 'Bennett · Carbery · Tao'), ('2010', 'Guth'), ('2025–26', 'Hong Wang · Joshua Zahl')],
  relay_ai=('2026', 'AI manuscript on four-dimensional Kakeya sets'),
  cap4='<b>Figure 4.</b> A selection of the human works cited by OpenAI’s manuscript on four-dimensional Kakeya sets, in order. The manuscript has 34 references in all.',
  hist_y='works', cap3='<b>Figure 3.</b> The {n:,} cited human works with a known year, by decade of publication. The oldest is Descartes’s <i>La Géométrie</i> (1637); the most recent decades hold the most, but the shoulders reach back centuries. Hover a bar for its count.',
 ),
}


def stages(t):
    cols = ''.join(
        f'<div class="stage"><h4>{esc(n)}<small>{esc(sub)}</small></h4>'
        f'<div class="cell eng"><b>{esc(t["key_eng"])}</b>{esc(e)}</div>'
        f'<div class="cell sci"><b>{esc(t["key_sci"])}</b>{esc(s)}</div></div>'
        for n, sub, e, s in t['stages'])
    return (f'<figure class="fig"><div class="fig-key"><span><i class="k-eng"></i>{esc(t["key_eng"])}</span>'
            f'<span><i class="k-sci"></i>{esc(t["key_sci"])}</span></div>'
            f'<div class="stages">{cols}</div><div class="loop">{esc(t["loop"])}</div>'
            f'<figcaption>{t["cap1"]}</figcaption></figure>')


def sampling(t):
    def dots(ok):
        on = {3, 12, 18, 27, 33, 41, 46, 55, 60} if ok else set()
        return '<div class="dots" role="img" aria-label="64 attempts">' + ''.join(
            f'<i class="{"ok" if i in on else ""}"></i>' for i in range(64)) + '</div>'
    return (f'<figure class="fig"><div class="samp">'
            f'<div><h4>{esc(t["weak"])}</h4>{dots(False)}<p>{t["weak_p"]}</p></div>'
            f'<div><h4>{esc(t["strong"])}</h4>{dots(True)}<p>{t["strong_p"]}</p></div>'
            f'</div><figcaption>{t["cap2"]}</figcaption></figure>')


def relay(t):
    items = ''.join(f'<li><b>{esc(y)}</b><span>{esc(n)}</span></li>' for y, n in t['relay'])
    y, n = t['relay_ai']
    items += f'<li class="ai"><b>{esc(y)}</b><span>{esc(n)}</span></li>'
    return f'<figure class="fig"><ol class="relay">{items}</ol><figcaption>{t["cap4"]}</figcaption></figure>'


def decades(t):
    d = json.load(open(os.path.join(B, 'decades.json')))
    data = [(y, n) for y, n in d['decades'] if y >= 1850]            # earlier decades: a handful of works, noted in the caption
    W, H, L, R, TOP, BOT = 640, 300, 70, 8, 14, 40
    bw = (W - L - R) / len(data)
    mx = max(n for _, n in data)
    bars, labels = [], []
    for i, (y, n) in enumerate(data):
        h = (H - TOP - BOT) * n / mx
        x = L + i * bw
        bars.append(f'<rect class="bar" x="{x + 1:.1f}" y="{H - BOT - h:.1f}" width="{bw - 2:.1f}" height="{max(h, 1):.1f}" rx="2">'
                    f'<title>{y}s: {n:,} {t["hist_y"]}</title></rect>')
        if y % 50 == 0:
            labels.append(f'<text x="{x + bw / 2:.1f}" y="{H - 12}" text-anchor="middle">{y}</text>')
    ticks = ''.join(f'<line class="ax" x1="{L}" x2="{W - R}" y1="{H - BOT - (H - TOP - BOT) * v / mx:.1f}" y2="{H - BOT - (H - TOP - BOT) * v / mx:.1f}"/>'
                    f'<text x="{L - 6}" y="{H - BOT - (H - TOP - BOT) * v / mx + 7:.1f}" text-anchor="end">{v:,}</text>'
                    for v in (1000, 2000))
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(t["cap3"].split("</b>")[0][3:])}">'
           f'{ticks}<line class="ax" x1="{L}" x2="{W - R}" y1="{H - BOT}" y2="{H - BOT}"/>{"".join(bars)}{"".join(labels)}</svg>')
    return f'<figure class="fig hist">{svg}<figcaption>{t["cap3"].format(n=d["with_year"])}</figcaption></figure>'


FIGS = {'stages': stages, 'sampling': sampling, 'relay': relay, 'decades': decades}


def render(name, lang):
    return FIGS[name](T[lang])
