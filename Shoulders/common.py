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
.chip.fm,.chip.nc{background:var(--gold-soft);color:var(--gold)}.chip.ab{background:var(--use-soft);color:var(--use)}.chip.wf{background:var(--bg2);color:var(--wolf)}
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


PRIZE = {'zh': {'fm': '菲尔兹奖', 'ab': '阿贝尔奖', 'wf': '沃尔夫奖', 'nc': '诺贝尔化学奖'},
         'en': {'fm': 'Fields', 'ab': 'Abel', 'wf': 'Wolf', 'nc': 'Nobel Chemistry'}}


def chips(prizes, lang):
    return ''.join(f'<span class="chip {k}">{PRIZE[lang][k]} {prizes[k]}</span>' for k in ('nc', 'fm', 'ab', 'wf') if k in prizes)


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
 function set(b){b.setAttribute('aria-pressed','true')}   // keeps its label; the filled gold shows it was given
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


# ---- topic pages (timeline column, ranking, reference lists) ------------------------------
TOPIC_CSS = '''
.thanks{margin:1.6rem 0 0 6rem}
@media (max-width:560px){.thanks{margin-left:4.3rem}}
.tl{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem .5rem;margin:1.4rem 0 .4rem}
.ms{display:inline-flex;flex-direction:column;align-items:center;line-height:1.2;padding:.3rem .55rem;border:1px solid var(--rule);border-radius:4px;background:var(--sheet)}
.ms b{font:600 .95rem var(--f-display)}.ms i{font:.68rem var(--f-mono);font-style:normal;color:var(--muted)}
.ms.now{background:var(--ink);border-color:var(--ink)}.ms.now b,.ms.now i{color:var(--paper)}
.arr{color:var(--muted);font-size:.8rem}
.links{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.2rem 0 0}
.links a{font:.78rem var(--f-mono);color:var(--ink);text-decoration:none;border:1px solid var(--rule);background:var(--sheet);border-radius:4px;padding:.35rem .7rem}
.links a:hover{border-color:var(--use);color:var(--use)}
.lead{color:var(--muted);max-width:42rem;margin:0 0 1.2rem}
.col{position:relative;margin:0;padding:0;list-style:none}
.col:before{content:"";position:absolute;left:4.6rem;top:2.6rem;bottom:1rem;width:2px;background:var(--rule)}
.ai{position:relative;display:flex;align-items:center;gap:1rem;background:var(--ink);color:var(--paper);border-radius:6px;padding:.8rem 1.1rem;margin-bottom:1.2rem}
.ai b{font:600 .95rem var(--f-mono);letter-spacing:.06em}
.ai span{font-size:.88rem;opacity:.8}
.ai em{font:600 .8rem var(--f-mono);font-style:normal;margin-left:auto;opacity:.75}
.era{font:500 .72rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:1.6rem 0 .4rem 6rem;position:relative}
.w{position:relative;display:grid;grid-template-columns:4.6rem 1fr;gap:0 1.4rem;padding:.55rem 0}
.w:before{content:"";position:absolute;left:calc(4.6rem - 4px);top:1.05rem;width:10px;height:10px;border-radius:50%;background:var(--paper);border:2px solid var(--muted)}
.w.laur:before{border-color:var(--gold);background:var(--gold)}
.yr{font:500 .9rem var(--f-mono);color:var(--muted);text-align:right;padding-right:.6rem;padding-top:.2rem}
.who{font:600 1.08rem/1.4 var(--f-display)}
.who .zh{font-weight:900}
.who .lat{font:400 .8rem var(--f-body);color:var(--muted);margin-left:.25rem}
.w.classic .who{font-size:1.5rem}.w.classic .yr{font-size:1.15rem;color:var(--ink);font-weight:600}
.w.laur .who .nm.g{color:var(--gold)}
.ti{font-size:.92rem;color:var(--muted);font-style:italic;margin:.1rem 0 .2rem}
.ti a{color:inherit;text-decoration-color:var(--rule)}
.by{font:.68rem var(--f-mono);color:var(--muted);letter-spacing:.04em}
.by i{font-style:normal;border:1px solid var(--rule);border-radius:3px;padding:0 .35rem;margin-left:.3rem}
details{margin-top:.25rem}
summary{cursor:pointer;font-size:.82rem;color:var(--use);list-style:none}
summary::-webkit-details-marker{display:none}
summary:before{content:"＋ "}details[open] summary:before{content:"－ "}
blockquote{margin:.4rem 0 .2rem;padding:.35rem .8rem;border-left:3px solid var(--use-soft);font-size:.9rem;color:var(--ink);background:var(--sheet)}
blockquote small{display:block;font:.7rem var(--f-mono);color:var(--muted);margin-top:.15rem}
.metsw{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem;margin:.2rem 0 .9rem}
.metsw button{font:.8rem var(--f-body);border:1px solid var(--rule);background:var(--sheet);color:var(--ink);border-radius:999px;padding:.2rem .75rem;cursor:pointer}
.metsw button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.metsw .more{border-style:dashed;color:var(--muted)}
.rank{list-style:none;margin:0;padding:0;counter-reset:r}
.rank li{display:grid;grid-template-columns:2rem 1fr auto;align-items:baseline;gap:.6rem;padding:.42rem 0;border-bottom:1px solid var(--rule)}
.rank li:before{counter-increment:r;content:counter(r);font:.8rem var(--f-mono);color:var(--muted);text-align:right}
.rank .nm{font:600 1rem var(--f-display)}
.rank .nm small{font:400 .78rem var(--f-body);color:var(--muted);margin-left:.3rem}
.rank .ct{font:600 .95rem var(--f-mono)}
.rank li.hide{display:none}
.toggle{margin-top:.7rem;font:.85rem var(--f-body);background:none;border:0;color:var(--use);cursor:pointer;padding:0}
.refs{display:grid;grid-template-columns:repeat(auto-fit,minmax(20rem,1fr));gap:1.5rem}
.refs h3{font:600 1.05rem var(--f-display);margin:0 0 .5rem}
.refs ol{margin:0;padding-left:1.8rem;font-size:.84rem;line-height:1.55}
.refs li{margin:.35rem 0;color:var(--muted)}
.refs li b{color:var(--ink);font-weight:500}
.refs .n{float:right;font:.72rem var(--f-mono);color:var(--use);margin-left:.5rem}
@media (max-width:560px){
 .col:before{left:3.3rem}.w{grid-template-columns:3.3rem 1fr;gap:0 1rem}.w:before{left:calc(3.3rem - 4px)}
 .era{margin-left:4.3rem}.yr{font-size:.8rem;padding-right:.5rem}.w.classic .who{font-size:1.25rem}.w.classic .yr{font-size:.95rem}
 .ai{flex-wrap:wrap;gap:.2rem .8rem}.ai em{margin-left:0}
}
'''

RANK_JS = '''<script>
(function(){
 var L=document.querySelector('.rank'),sw=document.querySelector('.metsw'),tg=document.querySelector('.toggle');
 var M=JSON.parse(sw.dataset.m),met='r',more=false,all=false,TOP=20;
 function draw(){
  var rows=[].slice.call(L.children);
  rows.sort(function(a,b){return b.dataset[met]-a.dataset[met]||b.dataset.r-a.dataset.r||b.dataset.t-a.dataset.t});
  rows.forEach(function(li,i){L.appendChild(li);li.querySelector('.ct').textContent=li.dataset[met];li.classList.toggle('hide',!all&&i>=TOP)});
  var ks=more?(M.ks||['r','t','p']):[met];
  sw.innerHTML='<span class="eyebrow">'+M.l+'</span>'+ks.map(function(k){return '<button type="button" data-k="'+k+'" aria-pressed="'+(k===met)+'">'+M[k]+'</button>'}).join('')+'<button type="button" class="more">'+(more?M.less:M.more)+'</button>';
  tg.textContent=all?tg.dataset.less:tg.dataset.all;
 }
 sw.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;if(b.classList.contains('more')){more=!more;if(!more)met='r'}else met=b.dataset.k;draw()});
 tg.addEventListener('click',function(){all=!all;draw()});
 draw();
})();
</script>'''
