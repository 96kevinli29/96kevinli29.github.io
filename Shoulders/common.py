"""Shared page shell for the hub and the topic pages (the math index has its own template)."""
import html as _html

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@600;900'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">')

DARK = '--paper:#11181e;--sheet:#182129;--ink:#e4e9ec;--muted:#93a3ae;--rule:#2b3741;--gold:#e0b351;--gold-soft:#3a3020;--use:#5cc2b6;--use-soft:#183a37;--wolf:#c3a3e6;--bg2:#1f2a33;color-scheme:dark'
BASE = '''
:root{--paper:#eef1f3;--sheet:#fbfcfc;--ink:#14212b;--muted:#5b6b76;--rule:#d3dadf;--gold:#a8791c;--gold-soft:#f3e7c9;--use:#1f6f68;--use-soft:#d6ebe8;--wolf:#7a4fa3;--bg2:#e3e8ec;
--f-display:"Noto Serif SC","Songti SC","STSong",Georgia,serif;--f-body:"IBM Plex Sans","PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){%s}}
:root[data-theme="dark"]{%s}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.7 var(--f-body);-webkit-text-size-adjust:100%%}
main{max-width:56rem;margin:0 auto;padding:2.2rem 16px 4rem}
a{color:var(--use)}
.top{display:flex;justify-content:space-between;align-items:center;gap:1rem;font:500 .75rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.top a{color:var(--muted);text-decoration:none}.top a:hover{color:var(--ink)}
.eyebrow{font:500 .75rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font:900 clamp(2.1rem,6.5vw,3.5rem)/1.12 var(--f-display);margin:2rem 0 .8rem;letter-spacing:-.01em}
h2{font:900 clamp(1.45rem,4vw,1.9rem)/1.25 var(--f-display);margin:0 0 .5rem}
.dek{font-size:1.08rem;color:var(--muted);max-width:40rem;margin:0 0 1rem}
.dek b{color:var(--ink);font-weight:600}
.sec{margin-top:3.2rem}
.sec>.eyebrow{display:block;margin-bottom:.6rem}
.tag{display:inline-block;font:500 .7rem var(--f-mono);letter-spacing:.06em;text-transform:uppercase;background:var(--gold-soft);color:var(--gold);padding:.12rem .5rem;border-radius:3px}
.chip{display:inline-block;font:500 .66rem/1.5 var(--f-mono);letter-spacing:.04em;padding:0 .4rem;border-radius:3px;vertical-align:.12em;margin-left:.3rem;white-space:nowrap}
.chip.fm{background:var(--gold-soft);color:var(--gold)}.chip.ab{background:var(--use-soft);color:var(--use)}.chip.wf{background:var(--bg2);color:var(--wolf)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(8.5rem,1fr));gap:.75rem;margin:1.6rem 0 0}
.stat{border-left:3px solid var(--gold);padding:.1rem .8rem}
.stat b{display:block;font:900 1.8rem/1.15 var(--f-display)}
.stat span{font-size:.84rem;color:var(--muted);line-height:1.4;display:block}
footer{margin-top:3.5rem;padding-top:1rem;border-top:1px solid var(--rule);font-size:.85rem;color:var(--muted)}
footer a{color:var(--muted)}
:focus-visible{outline:2px solid var(--use);outline-offset:2px}
''' % (DARK, DARK)


def page(lang, title, desc, css, body):
    return f'''<!doctype html>
<html lang="{'zh-CN' if lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{_html.escape(title)}</title>
<meta name="description" content="{_html.escape(desc)}">
<meta property="og:title" content="{_html.escape(title)}">
<meta property="og:description" content="{_html.escape(desc)}">
{FONTS}
<style>{BASE}{TRIBUTE_CSS}{css}</style>
</head>
<body>
<main>
{body}
</main>
<script>{TRIBUTE_JS}Tribute.bind();</script>
{GC}
</body>
</html>
'''


def laureates(scripts_dir):
    """{folded 'first last': {'fm': year, 'ab': year, 'wf': year}} from the math index's prize lists."""
    import re, unicodedata
    out = {}
    for key, f in (('fm', 'fields_medal.txt'), ('ab', 'abel.txt'), ('wf', 'wolf.txt')):
        for line in open(f'{scripts_dir}/{f}', encoding='utf-8'):
            if '|' not in line:
                continue
            y, ns = line.strip().split('|')
            for n in ns.split(';'):
                out.setdefault(person_key(n), {}).setdefault(key, int(y))
    return out


def person_key(name):
    """'Charles L. Fefferman' and 'Charles Fefferman' -> 'charles fefferman'."""
    import re, unicodedata
    w = [x for x in name.replace(', Jr.', '').split() if not re.fullmatch(r'[A-Z]\.', x)]
    s = (w[0] + ' ' + w[-1]) if len(w) > 1 else name
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()


PRIZE = {'zh': {'fm': '菲尔兹奖', 'ab': '阿贝尔奖', 'wf': '沃尔夫奖'},
         'en': {'fm': 'Fields', 'ab': 'Abel', 'wf': 'Wolf'}}


def chips(prizes, lang):
    return ''.join(f'<span class="chip {k}">{PRIZE[lang][k]} {prizes[k]}</span>' for k in ('fm', 'ab', 'wf') if k in prizes)


# ---- tributes: counted as GoatCounter events, read back through its public counter -------------
GC = '<script data-goatcounter="https://96kevinli29.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
TRIBUTE_CSS = '''
.tribute{display:inline-flex;align-items:center;gap:.45rem;font:600 .92rem var(--f-body);color:var(--gold);background:transparent;border:1.5px solid var(--gold);border-radius:999px;padding:.42rem 1.1rem;cursor:pointer;transition:background .25s,color .25s}
.tribute:hover{background:var(--gold-soft)}
.tribute[aria-pressed="true"]{background:var(--gold);color:var(--paper);cursor:default}
.tribute .ic{font-size:1.05em;line-height:1}
.tcount{font:.8rem var(--f-mono);color:var(--muted);margin-left:.7rem}
.tcount b{color:var(--ink);font-weight:600}
'''
TRIBUTE_JS = r'''
window.Tribute=(function(){
 const B='https://96kevinli29.goatcounter.com/counter/';
 const key=p=>'tribute:'+p;
 const done=p=>{try{return !!localStorage.getItem(key(p))}catch(e){return false}};
 function read(p,box){fetch(B+encodeURIComponent(p)+'.json').then(r=>r.ok?r.json():null).then(j=>{if(j&&j.count){box.querySelector('b').textContent=j.count;box.hidden=false}}).catch(()=>{})}
 function send(p,t,n){n=n||0;if(window.goatcounter&&window.goatcounter.count)window.goatcounter.count({path:p,title:t,event:true});else if(n<20)setTimeout(()=>send(p,t,n+1),500)}
 function set(b){b.setAttribute('aria-pressed','true');b.querySelector('.lb').textContent=b.dataset.done}
 function bind(root){(root||document).querySelectorAll('.tribute:not([data-bound])').forEach(b=>{
  b.dataset.bound=1;const p=b.dataset.path,box=b.nextElementSibling&&b.nextElementSibling.classList.contains('tcount')?b.nextElementSibling:null;
  if(done(p))set(b);if(box)read(p,box);
  b.addEventListener('click',()=>{if(done(p))return;try{localStorage.setItem(key(p),'1')}catch(e){}
   send(p,b.dataset.title||p);set(b);
   if(box&&!box.hidden){const el=box.querySelector('b'),n=parseInt(el.textContent.replace(/\D/g,''),10);if(!isNaN(n))el.textContent=(n+1).toLocaleString('en-US')}
   b.dispatchEvent(new CustomEvent('tribute',{bubbles:true}))})})}
 return {bind};
})();
'''


def tribute_button(path, label, done, count_label, title=''):
    return (f'<button type="button" class="tribute" data-path="{_html.escape(path)}" data-done="{_html.escape(done)}" data-title="{_html.escape(title or path)}">'
            f'<span class="ic">✦</span><span class="lb">{_html.escape(label)}</span></button>'
            f'<span class="tcount" hidden><b>0</b> {_html.escape(count_label)}</span>')
