(function(){
const D=JSON.parse(document.getElementById('data').textContent);
const A=D.authors, P=D.papers, F=D.fields;
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=n=>n.toLocaleString('en-US');
let LANG=window.__LANG__||'zh';
if(!window.__ALT__){try{const s=localStorage.getItem('shoulders-lang');if(s==='zh'||s==='en')LANG=s}catch(e){}}
const I={
zh:{eyebrow:'<a href="../../zh/" style="color:inherit">← 巨人之肩</a> · 数学 · OpenAI Math Release',h1:'巨人之肩',
 thesis:'AI 在数学前沿的每一项成果，都建立在几代数学家的积累之上。OpenAI 公开了由其内部模型撰写的全部数学稿件及其 LaTeX 源码；我们逐条整理它们的参考文献：引用了谁、哪一篇、在正文中怎样使用。让这些名字被看见，向 AI 时代的人类数学家致敬。 <a class="essay" href="../../blog/zh/">阅读文章：AI 的数学，建立在什么之上 →</a>',
 searchLabel:'搜索数学家',searchPh:'搜索数学家：陶哲轩、Hong Wang、Bourgain……',
 st1:'篇 AI 预印本',st2:'条参考文献',st4:'的预印本引用了同批 OpenAI 预印本',st5:'数据重建',updT:'Update',mT:'正文引用',mR:'参考文献条目',mP:'引用篇数',metL:'排名依据',metMore:'更多排名方式',metLess:'收起',inTextN:n=>`正文引用 ${n} 次`,metNote:{t:'按正文引用次数排序：每处 \\cite 计一次，同一篇论文在正文中被引多次会多计。',r:'按参考文献条目数排序：一篇预印本列出某人一篇论文计一次。',p:'按引用篇数排序：引用过某人的预印本数量。'},updAll:n=>`全部更新记录（${n}）`,updAuto:d=>`数据每天自动检查，最近一次重建 ${d}`,
 featH:'被引最多的数学家',featP:'金色、绿色、紫色标签分别为菲尔兹奖、阿贝尔奖、沃尔夫奖。点卡片可查看每篇论文和正文原句。',
 y26:'2026 年获奖者：菲尔兹奖（7 月 23 日，费城 ICM）、阿贝尔奖与沃尔夫奖',
 fieldsH:'按领域看',fieldsP:'领域取自 OpenAI 目录的学科分类。',
 boardT:f=>f+'：被引最多的前 300 位数学家',matT:f=>f+'：谁出现在哪篇论文里',
 boardNote:'金色 ★ 菲尔兹奖，绿色 ◆ 阿贝尔奖，紫色 ▲ 沃尔夫奖。悬停数字可看三种计数。',
 matNote:'每列是该领域的一篇预印本，每行是一位数学家；有色格表示这篇预印本引用了他。最多显示 60 列。',
 papersH:'全部预印本',papersP:'点一行查看这篇论文的完整参考文献，作者名可以点开。',pqLabel:'搜索论文',pqPh:'按标题搜索，例如 Kakeya、Penrose、Bochner',pfLabel:'领域',psLabel:'排序',
 sortD:'按日期',sortR:'按参考文献数',sortT:'按标题',thPaper:'论文',thField:'领域',thDate:'日期',thRefs:'引文',thSelf:'自引',more:'显示更多',
 none:'没有匹配的论文。换个关键词试试。',noName:'没有找到这个名字。可以试试英文拼写。',
 methodH:'数据与口径',footer:'巨人之肩 · 由 <a href="https://huggingface.co/SeaFill2025" target="_blank" rel="noopener">Sea-Fill 开源科学社区</a>制作，记录 AI 数学成果所依赖的人类工作。发现错误或漏掉的引用，欢迎通过<a href="../../zh/#contact">首页的联系表单</a>告诉我们。',
 method:g=>`<p style="margin:0">数据来自 <a href="https://github.com/openai/math" target="_blank" rel="noopener">github.com/openai/math</a>（Apache 2.0 许可）的全部 ${P.length} 篇预印本源文件，最近一次重建于 ${g}，之后每天自动检查更新。每篇论文的参考文献从 BibTeX 或 <span class="m">\\bibitem</span> 中解析，正文引用句从 LaTeX 源码的 <span class="m">\\cite</span> 位置截取。</p><ul>
 <li><b>引用 ≠ 依赖。</b>人类论文同样大量引用前人；这里记录的是"站在谁的肩膀上"，不评判 AI 结果是否原创。</li>
 <li><b>人名消歧。</b>按"姓 + 名"合并，只有缩写的条目在无歧义时并入全名。常见姓氏（Wang、Li、Zhang 等）的缩写条目单独列出，不强行合并；少数学者的缩写条目按合作者和题目领域人工规则判定。</li>
 <li><b>引用方式</b>（直接使用 / 背景 / 提及）是按句子关键词的启发式分类，会有误判，请以原句为准。正文原句只为被引最多的约 60 位与菲尔兹奖、阿贝尔奖、沃尔夫奖得主抽取。</li>
 <li><b>自引</b>指引用同批 OpenAI 预印本的条目数，不计入数学家排行。</li>
 <li><b>验证状态。</b>OpenAI 说明部分未形式化的结果可能有错，引用本站数据时请回到原论文核对。</li></ul>`,
 all:'全部',allF:'全部领域',ha:'调和分析',papersCited:'篇预印本引用',refEntries:'次被引',ctxN:'处正文原句',
 use:'直接使用',bg:'背景',men:'提及',fields:'菲尔兹奖',abel:'阿贝尔奖',wolf:'沃尔夫奖',cited:'被引',coauth:'合作者',seeRefs:'查看全部参考文献',
 who:'被引数学家',fieldDist:'领域分布',noCtx:'正文原句只为被引最多的约 60 位与菲尔兹奖、阿贝尔奖、沃尔夫奖得主抽取。',close:'关闭',
 aiPaper:'AI 预印本',family:'论文族',openPdf:'在 GitHub 打开 PDF',humans:'位人类作者',selfRefs:'条引用同批预印本',unparsed:'OpenAI / 未解析作者',notitle:'（无题名）',pp:'篇',places:'处',cites:'次被引',
 atlasH:'基石地图',atlasP:'每个小点是一篇 AI 预印本，按学科聚成"大陆"；带圈的大点是被多篇预印本共同引用的人类论文，大小表示被引篇数，位置落在引用它的论文之间。悬停查看，点击打开详情，可拖动和缩放。',
 tgHA:'突出调和分析',tgEdges:'显示全部连线',tgReset:'复位',lgPP:'AI 预印本',lgStone:'人类基石论文',lgLau:'作者含获奖者',
 atlasNote:'基石论文取被引最多的约 110 篇，加上各学科和调和分析内部被引最多的若干篇。教材和经典专著也会出现在这里。',
 ctyH:'各国数学家',ctyP:'被引最多的 300 位数学家与全部获奖者按出生地或原国籍标注（出生与成长地不同时，部分取成长地），长条为他们按当前排名依据的计数之和。点一行查看名单。',
 ctyNote:n=>`已标注 ${n} 位；标注依据公开资料，可能有误或不全。`,ctySheet:'按国家/地区',cnL:'工作单位',cn_only:'仅中国大陆',cn_all:'全部按引用',mlTag:'中国大陆',ctyWho:'位被标注的数学家',stoneK:'人类基石论文',citedBy:'被以下 AI 预印本引用',authorsK:'作者'},
en:{eyebrow:'<a href="../" style="color:inherit">← On Whose Shoulders</a> · Mathematics · OpenAI Math Release',h1:'On Whose Shoulders',
 thesis:'Every result AI reaches at the frontier of mathematics is built on generations of mathematicians. OpenAI has published all the mathematics manuscripts written by its internal model, with their LaTeX sources; we go through their references entry by entry: whom they cite, which work, and how it is used in the text. A tribute to the human mathematicians of the AI era, so their names stay visible. <a class="essay" href="../blog/">Read the essay: What AI’s mathematics is built on →</a>',
 searchLabel:'Search mathematicians',searchPh:'Search mathematicians: Terence Tao, Hong Wang, Bourgain…',
 st1:'AI preprints',st2:'reference entries',st4:'of preprints cite other OpenAI preprints',st5:'data rebuilt',updT:'Update',mT:'in-text citations',mR:'reference entries',mP:'citing preprints',metL:'Rank by',metMore:'More ranking options',metLess:'Fewer options',inTextN:n=>`cited ${n}× in text`,metNote:{t:'Ranked by in-text citations: every \\cite counts, so a work cited several times in one paper counts several times.',r:'Ranked by reference entries: one preprint listing one of their papers counts once.',p:'Ranked by citing preprints: how many preprints cite them.'},updAll:n=>`All updates (${n})`,updAuto:d=>`Data checked daily; last rebuilt ${d}`,
 featH:'Most-cited mathematicians',featP:'Gold, green and purple tags mark Fields Medal, Abel Prize and Wolf Prize laureates. Open a card to see each paper and the sentences that cite them.',
 y26:'2026 laureates: Fields Medal (23 July, ICM Philadelphia), Abel Prize and Wolf Prize',
 fieldsH:'By field',fieldsP:'Fields follow the subject classes of OpenAI’s catalogue.',
 boardT:f=>f+': top 300 most-cited mathematicians',matT:f=>f+': who appears in which paper',
 boardNote:'Gold ★ Fields Medal, green ◆ Abel Prize, purple ▲ Wolf Prize. Hover a number to see all three counts.',
 matNote:'Each column is one preprint in the field, each row one mathematician; a filled cell means that preprint cites them. Up to 60 columns.',
 papersH:'All preprints',papersP:'Open a row to see the full reference list. Author names are clickable.',pqLabel:'Search papers',pqPh:'Search titles, e.g. Kakeya, Penrose, Bochner',pfLabel:'Field',psLabel:'Sort',
 sortD:'By date',sortR:'By references',sortT:'By title',thPaper:'Paper',thField:'Field',thDate:'Date',thRefs:'Refs',thSelf:'Self',more:'Show more',
 none:'No papers match. Try another keyword.',noName:'No one by that name. Try the Latin spelling.',
 methodH:'Data and method',footer:'On Whose Shoulders · made by the <a href="https://huggingface.co/SeaFill2025" target="_blank" rel="noopener">Sea-Fill open-source science community</a>, recording the human work behind AI-produced mathematics. Found an error or a missing citation? Tell us through the <a href="../#contact">contact form</a>.',
 method:g=>`<p style="margin:0">Data come from the source files of all ${P.length} preprints in <a href="https://github.com/openai/math" target="_blank" rel="noopener">github.com/openai/math</a> (Apache 2.0), last rebuilt on ${g} and checked for updates daily. References are parsed from BibTeX or <span class="m">\\bibitem</span>; citing sentences are taken from the <span class="m">\\cite</span> positions in the LaTeX source.</p><ul>
 <li><b>A citation is not dependence.</b> Human papers cite heavily too. This index records whose shoulders the work stands on; it does not judge whether the AI results are original.</li>
 <li><b>Name disambiguation.</b> Names merge on surname plus given name; initial-only entries join a full name only when unambiguous. Initial-only entries with common surnames (Wang, Li, Zhang, …) stay separate, except for a few people resolved by co-author and topic rules.</li>
 <li><b>Usage labels</b> (uses / background / mention) come from keyword rules on the citing sentence and can be wrong; read the sentence itself. Sentences are extracted only for the ~60 most-cited people and Fields, Abel and Wolf laureates.</li>
 <li><b>Self</b> counts references to other OpenAI preprints; these are left out of the rankings.</li>
 <li><b>Verification.</b> OpenAI notes that some unformalised results may contain errors. Check the original paper before relying on these data.</li></ul>`,
 all:'All',allF:'All fields',ha:'Harmonic analysis',papersCited:'citing preprints',refEntries:'citations',ctxN:'citing sentences',
 use:'uses',bg:'background',men:'mention',fields:'Fields',abel:'Abel',wolf:'Wolf',cited:'Cited',coauth:'with',seeRefs:'see all references',
 who:'Cited mathematician',fieldDist:'By field',noCtx:'Sentences are extracted only for the ~60 most-cited people and Fields, Abel and Wolf laureates.',close:'Close',
 aiPaper:'AI preprint',family:'family',openPdf:'Open the PDF on GitHub',humans:'human authors',selfRefs:'OpenAI self-references',unparsed:'OpenAI / unparsed authors',notitle:'(untitled)',pp:'papers',places:'sentences',cites:'citations',
 atlasH:'Foundations map',atlasP:'Each small dot is an AI preprint, grouped into "continents" by subject. Ringed nodes are human papers cited by several preprints; size shows how many, and each sits among the preprints that cite it. Hover to inspect, click for details, drag and zoom to explore.',
 tgHA:'Highlight harmonic analysis',tgEdges:'Show all links',tgReset:'Reset',lgPP:'AI preprint',lgStone:'Human cornerstone paper',lgLau:'Laureate author',
 atlasNote:'Cornerstones are the ~110 most-cited human works, plus the most-cited works inside each field and inside harmonic analysis. Textbooks and classic monographs appear too.',
 ctyH:'Mathematicians by country',ctyP:'The 300 most-cited mathematicians and all laureates are tagged by country of birth or original nationality (for some, where they grew up). Bars sum their counts under the current ranking. Open a row for the list.',
 ctyNote:n=>`${n} people tagged from public sources; some tags may be wrong or missing.`,ctySheet:'Country or region',cnL:'Affiliation',cn_only:'Mainland China only',cn_all:'All by citations',mlTag:'Mainland China',ctyWho:'tagged mathematicians',stoneK:'Human cornerstone paper',citedBy:'Cited by these AI preprints',authorsK:'Authors'}};
const T=k=>I[LANG][k];
const CN={US:['美国','United States'],HU:['匈牙利','Hungary'],NZ:['新西兰','New Zealand'],BE:['比利时','Belgium'],AU:['澳大利亚','Australia'],FR:['法国','France'],JP:['日本','Japan'],IL:['以色列','Israel'],CN:['中国','China'],RU:['俄罗斯','Russia'],GB:['英国','United Kingdom'],DE:['德国','Germany'],IR:['伊朗','Iran'],RO:['罗马尼亚','Romania'],NL:['荷兰','Netherlands'],FI:['芬兰','Finland'],IT:['意大利','Italy'],CH:['瑞士','Switzerland'],IN:['印度','India'],RS:['塞尔维亚','Serbia'],CA:['加拿大','Canada'],GR:['希腊','Greece'],DK:['丹麦','Denmark'],SE:['瑞典','Sweden'],AT:['奥地利','Austria'],UA:['乌克兰','Ukraine'],AR:['阿根廷','Argentina'],PL:['波兰','Poland'],ES:['西班牙','Spain'],NO:['挪威','Norway'],KR:['韩国','South Korea'],VN:['越南','Vietnam'],BR:['巴西','Brazil'],SI:['斯洛文尼亚','Slovenia'],HR:['克罗地亚','Croatia'],PT:['葡萄牙','Portugal'],ZA:['南非','South Africa'],HK:['中国香港','Hong Kong'],TW:['中国台湾','Taiwan'],BG:['保加利亚','Bulgaria'],BY:['白俄罗斯','Belarus'],CL:['智利','Chile'],EE:['爱沙尼亚','Estonia'],GE:['格鲁吉亚','Georgia'],IS:['冰岛','Iceland'],LB:['黎巴嫩','Lebanon'],MA:['摩洛哥','Morocco'],MX:['墨西哥','Mexico'],SK:['斯洛伐克','Slovakia'],TJ:['塔吉克斯坦','Tajikistan'],TN:['突尼斯','Tunisia'],MD:['摩尔多瓦','Moldova'],LT:['立陶宛','Lithuania']};
const cName=c=>CN[c]?CN[c][LANG==='zh'?0:1]:c;
const ctag=a=>a.c?`<span class="ctag">${esc(cName(a.c))}</span>`:'';
const aff=a=>a.af?`<small class="affs">${esc(a.af[LANG==='zh'?0:1])}</small>`:'';
// indexes
const aPapers=A.map(()=>new Set()), aRefs=new Int32Array(A.length);
const aTxt=new Int32Array(A.length);
P.forEach((p,pi)=>p.r.forEach(r=>r[0].forEach(a=>{aPapers[a].add(pi);aRefs[a]++;aTxt[a]+=(r[5]||0)})));
let MET='r';
const score=i=>MET==='t'?aTxt[i]:MET==='r'?aRefs[i]:aPapers[i].size;
const HA=-1;
const inField=(pi,f)=>f===null?true:f===HA?P[pi].ha===1:P[pi].f===f;
const nm=i=>LANG==='zh'&&A[i].zh?A[i].zh:A[i].n;
const fName=k=>LANG==='zh'?F[k][1]:F[k][0];
const CTX=D.ctx||{};
const LAUR=[];A.forEach((a,i)=>{if(aPapers[i].size&&!/^init:/.test(a.n))LAUR.push(i)});
const sortLaur=()=>LAUR.sort((x,y)=>score(y)-score(x)||aRefs[y]-aRefs[x]);sortLaur();
let curF=null,pcount=40;

function mixFor(i){const L=CTX[i]||[];const c=[0,0,0];L.forEach(x=>c[x[2]]++);return {c,n:L.length}}
function mixBar(m){if(!m.n)return '';const w=k=>(m.c[k]/m.n*100).toFixed(1)+'%';
 return `<div class="mix" role="img" aria-label="${T('use')} ${m.c[2]}, ${T('bg')} ${m.c[1]}, ${T('men')} ${m.c[0]}"><i class="k2" style="width:${w(2)}"></i><i class="k1" style="width:${w(1)}"></i><i class="k0" style="width:${w(0)}"></i></div>
 <div class="mixkey"><span><i class="dot k2"></i>${T('use')} ${m.c[2]}</span><span><i class="dot k1"></i>${T('bg')} ${m.c[1]}</span><span><i class="dot k0"></i>${T('men')} ${m.c[0]}</span></div>`}
function badges(a){let h='';if(a.fm)h+=`<span class="medal${a.fm===2026?' new':''}">${T('fields')} ${a.fm}</span>`;if(a.ab)h+=`<span class="medal abel">${T('abel')} ${a.ab}</span>`;if(a.wf)h+=`<span class="medal wolf">${T('wolf')} ${a.wf}</span>`;return h}
function stars(a){return (a.fm?` <small style="color:var(--gold)">★${a.fm}</small>`:'')+(a.ab?` <small style="color:var(--use)">◆${a.ab}</small>`:'')+(a.wf?` <small style="color:var(--wolf)">▲${a.wf}</small>`:'')}
function cleanTex(s){return esc(s).replace(/\\\(|\\\)|\\\[|\\\]/g,'').replace(/\\([a-zA-Z]+)/g,'$1')}
function surname(i){const n=A[i].n.split(/\s+/);return n[n.length-1]}
function hlName(html,i){const s=surname(i).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');try{return html.replace(new RegExp('\\b('+s+')\\b','g'),'<mark>$1</mark>')}catch(e){return html}}

let METX=false;
function renderMet(){document.querySelectorAll('.metsw').forEach(el=>{const ks=METX?['r','t','p']:[MET];el.innerHTML=`<span class="eyebrow">${T('metL')}</span>`+ks.map(k=>`<button type="button" data-met="${k}" aria-pressed="${k===MET}">${T(k==='t'?'mT':k==='r'?'mR':'mP')}</button>`).join('')+`<button type="button" class="metmore" data-metmore="1">${METX?T('metLess'):T('metMore')}</button>`});document.querySelectorAll('.metnote').forEach(el=>el.textContent=T('metNote')[MET])}
function renderStatic(){renderMet();
 document.documentElement.lang=LANG==='zh'?'zh-CN':'en';if(window.__ALT__)document.title=LANG==='zh'?'巨人之肩':'On Whose Shoulders';
 document.querySelectorAll('[data-i]').forEach(el=>{const v=T(el.dataset.i);if(typeof v==='string')el.innerHTML=v});
 document.querySelectorAll('[data-ph]').forEach(el=>el.placeholder=T(el.dataset.ph));
 document.querySelectorAll('.lang button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.lang===LANG));
 $('#methodBody').innerHTML=T('method')(D.gen);
 const U=D.upd||[];const ut=u=>LANG==='zh'?u[1]:u[2];
 $('#upd').innerHTML=U.length?`<span class="ut">${T('updT')}</span><span class="ud num">${esc(U[0][0])}</span><span class="ux">${esc(ut(U[0]))}</span><span class="auto">${T('updAuto')(D.gen)}</span>`+(U.length>1?`<details><summary>${T('updAll')(U.length)}</summary><ol>${U.map(u=>`<li><span class="ud num">${esc(u[0])}</span> ${esc(ut(u))}</li>`).join('')}</ol></details>`:''):'';
 const selfP=P.filter(p=>p.o>0).length;
 $('#stats').innerHTML=[[fmt(P.length),T('st1')],[Math.round(selfP/P.length*100)+'%',T('st4')],[D.gen,T('st5')]].map(([b,s])=>`<div class="stat"><b class="num">${b}</b><span>${s}</span></div>`).join('');
}
function trio(i){const c=[['t',aTxt[i],T('mT')],['r',aRefs[i],T('mR')],['p',aPapers[i].size,T('mP')]];return c.map(([k,v,l])=>`<div class="${k===MET?'on':''}"><b class="num">${v}</b><span>${l}</span></div>`).join('')}
function card(i){const a=A[i],m=mixFor(i);
 return `<button class="card" type="button" data-a="${i}">
  <div class="who"><div style="min-width:0"><h3>${esc(nm(i))}</h3><div class="en">${LANG==='zh'&&a.zh?esc(a.n):''}${ctag(a)}</div></div><div class="badges">${badges(a)}</div></div>
  ${a.af?`<div class="aff">${esc(a.af[LANG==='zh'?0:1])}</div>`:''}<div class="trio">${trio(i)}</div>
  ${mixBar(m)}</button>`}
function renderFeat(){sortLaur();
 $('#feat').innerHTML=LAUR.slice(0,12).map(card).join('');
 const y=A.map((a,i)=>i).filter(i=>(A[i].fm===2026||A[i].ab===2026||A[i].wf===2026)).sort((x,y)=>score(y)-score(x));
 $('#f26').innerHTML=y.map(i=>`<button class="mini" type="button" data-a="${i}"><b>${esc(nm(i))}</b><span class="num">${A[i].fm===2026?T('fields'):A[i].ab===2026?T('abel'):T('wolf')} · ${score(i)} ${T(MET==='t'?'mT':MET==='r'?'mR':'mP')}</span></button>`).join('');
}
const fCount=f=>P.filter((p,pi)=>inField(pi,f)).length;
const fieldLabel=f=>f===null?T('allF'):f===HA?T('ha'):fName(f);
function rail(){
 const items=[[null,T('all'),false]].concat(F.map((f,k)=>[k,fName(k),false]).concat([[HA,T('ha'),false]]).sort((a,b)=>fCount(b[0])-fCount(a[0])));
 $('#rail').innerHTML=items.map(([f,l,star])=>`<button type="button" class="chip${star?' star':''}" aria-pressed="${f===curF}" data-f="${f===null?'all':f}">${esc(l)}<span class="num">${fCount(f)}</span></button>`).join('');
}
function board(){
 const ent=new Map(),pc=new Map(),tx=new Map();
 P.forEach((p,pi)=>{if(!inField(pi,curF))return;const seen=new Set();p.r.forEach(r=>r[0].forEach(a=>{ent.set(a,(ent.get(a)||0)+1);tx.set(a,(tx.get(a)||0)+(r[5]||0));if(!seen.has(a)){seen.add(a);pc.set(a,(pc.get(a)||0)+1)}}))});
 const cnt=MET==='t'?tx:MET==='r'?ent:pc;
 const top=[...cnt.entries()].filter(x=>!/^init:/.test(A[x[0]].n)).sort((a,b)=>b[1]-a[1]||ent.get(b[0])-ent.get(a[0])).slice(0,300);
 const max=top.length?top[0][1]:1;
 $('#boardTitle').textContent=T('boardT')(fieldLabel(curF));
 $('#board').innerHTML=top.map(([a,c],k)=>`<li class="${A[a].fm?'fm':A[a].ab?'ab':A[a].wf?'wf':''}" data-a="${a}" tabindex="0"><span class="rk">${k+1}</span><span class="nm">${esc(nm(a))}${LANG==='zh'&&A[a].zh?`<small>${esc(A[a].n)}</small>`:''}${stars(A[a])}${ctag(A[a])}${aff(A[a])}</span><span class="bar"><i style="width:${(c/max*100).toFixed(1)}%"></i></span><span class="ct num" title="${tx.get(a)} ${T('mT')} · ${ent.get(a)} ${T('mR')} · ${pc.get(a)} ${T('mP')}">${c}</span></li>`).join('');
 matrix(top.slice(0,15).map(x=>x[0]));
}
function matrix(rows){
 const C=[];P.forEach((p,pi)=>{if(inField(pi,curF)&&C.length<60)C.push(pi)});
 $('#matTitle').textContent=T('matT')(fieldLabel(curF));
 $('#matrix').innerHTML='<tr><th></th>'+C.map(pi=>`<th class="colh" title="${esc(P[pi].t)}"></th>`).join('')+'</tr>'+rows.map(a=>`<tr><th class="rowh" data-a="${a}">${esc(nm(a))}</th>`+C.map(pi=>{const on=aPapers[a].has(pi);return `<td class="${on?'on':''}${on&&(A[a].fm||A[a].ab||A[a].wf)?' fmc':''}" ${on?`title="${esc(P[pi].t)}" data-p="${pi}"`:''}></td>`}).join('')+'</tr>').join('');
}
function pfOptions(){const v=$('#pf').value;$('#pf').innerHTML=`<option value="all">${T('allF')}</option><option value="-1">${T('ha')}</option>`+F.map((f,k)=>`<option value="${k}">${esc(fName(k))}</option>`).join('');$('#pf').value=v||'all'}
function plist(){
 const q=$('#pq').value.trim().toLowerCase(), fv=$('#pf').value, sv=$('#ps').value;
 const f=fv==='all'?null:+fv;
 let L=P.map((p,pi)=>pi).filter(pi=>inField(pi,f)&&(!q||P[pi].t.toLowerCase().includes(q)));
 L.sort(sv==='r'?(a,b)=>P[b].r.length-P[a].r.length:sv==='t'?(a,b)=>P[a].t.localeCompare(P[b].t):(a,b)=>P[b].d.localeCompare(P[a].d)||P[a].t.localeCompare(P[b].t));
 $('#ptb').innerHTML=L.slice(0,pcount).map(pi=>{const p=P[pi];return `<tr data-p="${pi}"><td>${esc(p.t)} ${p.ha?`<span class="tag ha">${T('ha')}</span>`:''}</td><td class="hide-s"><span class="tag">${esc(fName(p.f))}</span></td><td class="hide-s num">${p.d.slice(5)}</td><td class="r">${p.r.length}</td><td class="r hide-s">${p.o||''}</td></tr>`}).join('')||`<tr><td colspan="5" style="color:var(--muted)">${T('none')}</td></tr>`;
 $('#pmore').hidden=L.length<=pcount;
}
function renderAll(){renderStatic();renderFeat();rail();board();pfOptions();plist();drawMap();renderCountries();if(!sheet.hidden&&cur){const[k,v]=cur;k==='a'?showA(v,true):k==='p'?showP(v,true):k==='s'?showS(v,true):openSheet(countryHTML(v),true)}}
document.addEventListener('click',e=>{const mm=e.target.closest('[data-metmore]');if(mm){METX=!METX;if(!METX&&MET!=='r'){MET='r';renderFeat();board();renderCountries()}renderMet();return}});
document.addEventListener('click',e=>{const m=e.target.closest('[data-met]');if(!m)return;MET=m.dataset.met;renderMet();renderFeat();board();renderCountries()});
document.addEventListener('click',e=>{const b=e.target.closest('.lang button');if(!b)return;if(window.__ALT__){if(b.dataset.lang!==LANG)location.href=window.__ALT__;return}LANG=b.dataset.lang;try{localStorage.setItem('shoulders-lang',LANG)}catch(err){}renderAll()});
$('#rail').addEventListener('click',e=>{const b=e.target.closest('.chip');if(!b)return;const v=b.dataset.f;curF=v==='all'?null:+v;rail();board();$('#pf').value=v==='all'?'all':String(v);pcount=40;plist()});
$('#pq').addEventListener('input',()=>{pcount=40;plist()});
$('#pf').addEventListener('change',()=>{pcount=40;plist()});
$('#ps').addEventListener('change',plist);
$('#pmore').addEventListener('click',()=>{pcount+=80;plist()});
const sugg=$('#sugg');
$('#q').addEventListener('input',()=>{const q=$('#q').value.trim().toLowerCase();if(!q){sugg.hidden=true;return}
 const norm=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();const nq=norm(q);
 const hits=[];for(let i=0;i<A.length&&hits.length<12;i++){const a=A[i];if(!aPapers[i].size)continue;if(norm(a.n).includes(nq)||(a.zh&&a.zh.includes(q)))hits.push(i)}
 hits.sort((x,y)=>aRefs[y]-aRefs[x]);
 sugg.innerHTML=hits.map(i=>`<button type="button" data-a="${i}"><span>${esc(A[i].zh?A[i].zh+' '+A[i].n:A[i].n)}${stars(A[i])}</span><span class="num" style="color:var(--muted)">${aRefs[i]} ${T('cites')}</span></button>`).join('')||`<div style="padding:8px 12px;color:var(--muted)">${T('noName')}</div>`;
 sugg.hidden=false});
document.addEventListener('click',e=>{if(!e.target.closest('.search'))sugg.hidden=true});
const sheet=$('#sheet'),scrim=$('#scrim');let lastFocus=null,cur=null;
function openSheet(html,keep){if(!keep)lastFocus=document.activeElement;sheet.innerHTML=`<button class="close" type="button" id="xclose">${T('close')}</button>`+html;sheet.hidden=false;scrim.hidden=false;if(!keep){sheet.scrollTop=0;$('#xclose').focus()}}
function closeSheet(){sheet.hidden=true;scrim.hidden=true;cur=null;try{history.replaceState(null,'',location.pathname+location.search)}catch(e){}if(lastFocus)lastFocus.focus()}
scrim.addEventListener('click',closeSheet);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!sheet.hidden)closeSheet()});
const LAB=()=>[T('men'),T('bg'),T('use')];
function coauth(list,self){const o=list.filter(a=>a!==self);if(!o.length)return '';return `<span class="meta">　${T('coauth')}: `+o.map(a=>`<span class="au${A[a].fm||A[a].ab||A[a].wf?' fmn':''}" data-a="${a}">${esc(nm(a))}</span>`).join(LANG==='zh'?'、':', ')+'</span>'}
function authorHTML(i){
 const a=A[i];const ps=[...aPapers[i]].sort((x,y)=>P[y].d.localeCompare(P[x].d));const m=mixFor(i);
 const ctxBy={};(CTX[i]||[]).forEach(x=>{(ctxBy[x[0]]=ctxBy[x[0]]||[]).push(x)});
 const fc={};ps.forEach(pi=>{const k=P[pi].ha?T('ha'):fName(P[pi].f);fc[k]=(fc[k]||0)+1});
 const fl=Object.entries(fc).sort((x,y)=>y[1]-x[1]).map(([k,v])=>`${esc(k)} ${v}`).join(' · ');
 const L=LAB();
 let h=`<div class="eyebrow">${T('who')}</div><h2>${esc(nm(i))}</h2><div class="sub">${LANG==='zh'&&a.zh?esc(a.n):''} ${ctag(a)} ${badges(a)}</div>${a.af?`<div class="aff" style="margin-top:4px">${esc(a.af[LANG==='zh'?0:1])}</div>`:''}
 <div class="trio">${trio(i)}</div>
 <p class="meta" style="margin-top:10px">${T('fieldDist')}: ${fl}</p>${m.n?mixBar(m):`<p class="meta">${T('noCtx')}</p>`}`;
 h+=ps.map(pi=>{const p=P[pi];const works=p.r.filter(r=>r[0].includes(i));const cx=(ctxBy[pi]||[]).slice().sort((x,y)=>y[2]-x[2]);
  return `<div class="entry"><h4><a href="${esc(p.u)}" target="_blank" rel="noopener">${esc(p.t)}</a></h4>
  <div class="meta">${esc(fName(p.f))}${p.ha?' · '+T('ha'):''} · ${p.d} · <a href="#" data-p="${pi}" class="openp">${T('seeRefs')}</a></div>
  <ul class="cw">${works.map(r=>`<li>${T('cited')}${r[5]?` <span class="meta">(${T('inTextN')(r[5])})</span>`:''}: ${r[3]?`<a href="${esc(r[3])}" target="_blank" rel="noopener">${esc(r[1]||T('notitle'))}</a>`:esc(r[1]||T('notitle'))}${r[2]?', '+esc(r[2]):''}${coauth(r[0],i)}</li>`).join('')}</ul>
  ${cx.length?`<ul class="ctx">${cx.map(x=>`<li><span class="lab l${x[2]}">${L[x[2]]}</span>${hlName(cleanTex(x[1]),i)}</li>`).join('')}</ul>`:''}</div>`}).join('');
 return h}
function paperHTML(pi){const p=P[pi];
 return `<div class="eyebrow">${T('aiPaper')} · ${esc(fName(p.f))}${p.ha?' · '+T('ha'):''}</div><h2>${esc(p.t)}</h2><div class="sub">${p.d} · OpenAI · ${T('family')} ${esc(p.fam)}</div>
 <p class="meta" style="margin-top:8px">${esc(p.ft)}</p><p><a href="${esc(p.u)}" target="_blank" rel="noopener">${T('openPdf')}</a></p>
 <div class="trio"><div><b class="num">${p.r.length}</b><span>${T('refEntries')}</span></div><div><b class="num">${new Set(p.r.flatMap(r=>r[0])).size}</b><span>${T('humans')}</span></div><div><b class="num">${p.o}</b><span>${T('selfRefs')}</span></div></div>
 <ol class="refs">${p.r.map(r=>{const names=r[0].length?r[0].map(a=>`<span class="au${A[a].fm||A[a].ab||A[a].wf?' fmn':''}" data-a="${a}">${esc(A[a].n)}</span>`).join(', '):`<span class="self">${T('unparsed')}</span>`;
   const t=r[3]?`<a href="${esc(r[3])}" target="_blank" rel="noopener">${esc(r[1])}</a>`:esc(r[1]);
   return `<li><span>${names}. ${t}${r[4]?'. <span class="meta">'+esc(r[4])+'</span>':''}${r[2]?' ('+esc(r[2])+')':''}</span></li>`}).join('')}</ol>`}
function showA(i,keep){cur=['a',i];openSheet(authorHTML(i),keep);try{history.replaceState(null,'','#a'+i)}catch(e){}}
function showP(pi,keep){cur=['p',pi];openSheet(paperHTML(pi),keep);try{history.replaceState(null,'','#p'+pi)}catch(e){}}
document.addEventListener('click',e=>{
 if(e.target.closest('.lang'))return;
 const op=e.target.closest('.openp');if(op){e.preventDefault();showP(+op.dataset.p);return}
 if(e.target.id==='xclose'){closeSheet();return}
 const t=e.target.closest('[data-a]');if(t&&!e.target.closest('a')){sugg.hidden=true;showA(+t.dataset.a);return}
 const p=e.target.closest('[data-p]');if(p&&!e.target.closest('a'))showP(+p.dataset.p);
});
document.addEventListener('keydown',e=>{if(e.key==='Enter'){const t=e.target.closest('li[data-a]');if(t)showA(+t.dataset.a)}});

// ---------- foundations map ----------
const ORDER=['Number theory','Algebraic and complex geometry','Algebra','Group theory','Topology','Differential geometry','Partial differential equations','Real and complex analysis','Functional analysis','Operator algebras','Mathematical physics','Probability and statistical mechanics','Dynamical systems and ergodic theory','Combinatorics','Theoretical computer science','Mathematical logic','Convex and metric geometry'];
const fOrder=ORDER.map(n=>F.findIndex(f=>f[0]===n)).filter(k=>k>=0);
F.forEach((f,k)=>{if(!fOrder.includes(k))fOrder.push(k)});
const W0=1200,H0=780,CX=600,CY=395;
const anchor={};fOrder.forEach((k,j)=>{const th=-Math.PI/2+j/fOrder.length*2*Math.PI;anchor[k]=[CX+455*Math.cos(th),CY+300*Math.sin(th)]});
const raK=F.findIndex(f=>f[0]==='Real and complex analysis');
const haAnchor=raK>=0?[CX+(anchor[raK][0]-CX)*0.62,CY+(anchor[raK][1]-CY)*0.62-20]:[CX,CY];
const fColor=k=>{const j=fOrder.indexOf(k);return `hsl(${Math.round(j/fOrder.length*330+12)} 42% 52%)`};
const STONES=(D.W||[]).map((w,s)=>({s,t:w[0],a:w[1],y:w[2],l:w[3],ps:w[4],n:w[4].length,lau:w[1].some(x=>A[x].fm||A[x].ab||A[x].wf),ha:w[4].filter(i=>P[i].ha).length}));
let MAP=null,MAPJOB=false;
// The force layout (320 ticks) takes over a second on a laptop, so it runs in ~12 ms slices
// after the rest of the page is drawn; the result is the same as running it in one go.
function layout(done){
 const rnd=d3.randomLcg(42);
 const pn=P.map((p,pi)=>{const an=p.ha?haAnchor:anchor[p.f];return {kind:'p',i:pi,ax:an[0],ay:an[1],x:an[0]+(rnd()-.5)*60,y:an[1]+(rnd()-.5)*60,r:2.6}});
 const sn=STONES.map(st=>{let x=0,y=0;st.ps.forEach(i=>{x+=pn[i].ax;y+=pn[i].ay});return {kind:'s',st,x:x/st.n+(rnd()-.5)*20,y:y/st.n+(rnd()-.5)*20,r:3+2.1*Math.sqrt(st.n)}});
 const nodes=pn.concat(sn);const links=[];sn.forEach(s=>s.st.ps.forEach(i=>links.push({source:s,target:pn[i]})));
 const sim=d3.forceSimulation(nodes).randomSource(rnd)
  .force('x',d3.forceX(d=>d.kind==='p'?d.ax:CX).strength(d=>d.kind==='p'?0.22:0))
  .force('y',d3.forceY(d=>d.kind==='p'?d.ay:CY).strength(d=>d.kind==='p'?0.22:0))
  .force('link',d3.forceLink(links).strength(0.06).distance(18))
  .force('collide',d3.forceCollide(d=>d.r+(d.kind==='s'?2.5:0.8)).iterations(2))
  .force('charge',d3.forceManyBody().strength(d=>d.kind==='s'?-10:-2.5).distanceMax(90)).stop();
 let k=0;
 (function step(){const t0=performance.now();while(k<320&&performance.now()-t0<12){sim.tick();k++}
  if(k<320){setTimeout(step,0);return}
  nodes.forEach(d=>{d.x=Math.max(14,Math.min(W0-14,d.x));d.y=Math.max(14,Math.min(H0-14,d.y))});
  done({pn,sn,links});})();
}
function shortLabel(st){const a=st.a.map(x=>A[x].n.split(/\s+/).pop());return (a.length>2?a[0]+' et al.':a.join('–')||'?')+(st.y?' '+st.y:'')}
function drawMap(){
 if(typeof d3==='undefined'){$('#mapbox').innerHTML='<p class="note" style="padding:16px">'+(LANG==='zh'?'地图需要加载 d3 脚本，当前网络无法加载。':'The map needs the d3 script, which could not load.')+'</p>';return}
 if(!MAP){
  if(!MAPJOB){MAPJOB=true;
   d3.select('#map').attr('viewBox',`0 0 ${W0} ${H0}`).append('text').attr('x',CX).attr('y',CY).attr('text-anchor','middle').attr('fill','currentColor').attr('opacity',.5).style('font-size','18px').text(LANG==='zh'?'基石地图生成中…':'Laying out the map…');
   setTimeout(()=>layout(m=>{MAP=m;drawMap()}),30)}
  return}
 const {pn,sn,links}=MAP;
 const svg=d3.select('#map').attr('viewBox',`0 0 ${W0} ${H0}`);svg.selectAll('*').remove();
 const g=svg.append('g');
 // regions
 const groups={};pn.forEach(d=>{const k=P[d.i].ha?'ha':P[d.i].f;(groups[k]=groups[k]||[]).push(d)});
 const regionG=g.append('g');
 const regionData=Object.entries(groups).map(([k,L])=>{const x=d3.mean(L,d=>d.x),y=d3.mean(L,d=>d.y);const dx=x-CX,dy=y-CY,len=Math.hypot(dx,dy)||1;const ext=d3.max(L,d=>Math.hypot(d.x-x,d.y-y))||20;
  return {k,x:Math.max(70,Math.min(W0-70,x+dx/len*(ext+16))),y:Math.max(24,Math.min(H0-16,y+dy/len*(ext+14))),n:L.length}});
 const edgeG=g.append('g');
 const edges=edgeG.selectAll('line').data(links).join('line').attr('class','edge').attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
 const ppG=g.append('g').selectAll('circle').data(pn).join('circle').attr('class','pp').attr('cx',d=>d.x).attr('cy',d=>d.y).attr('r',d=>d.r).attr('fill',d=>fColor(P[d.i].f));
 const stG=g.append('g').selectAll('circle').data(sn).join('circle').attr('class',d=>'stone'+(d.st.lau?' lau':'')).attr('cx',d=>d.x).attr('cy',d=>d.y).attr('r',d=>d.r).attr('fill','var(--sheet)');
 const regionG2=g.append('g');regionData.forEach(r=>{r.fs=Math.max(15,Math.min(30,9+Math.sqrt(r.n)*2))*(LANG==='zh'?1:0.72);const lab=r.k==='ha'?T('ha'):fName(+r.k);r.w=lab.length*r.fs*(LANG==='zh'?1:0.55);r.x=Math.max(r.w/2+8,Math.min(W0-r.w/2-8,r.x))});
 regionData.sort((p,q)=>q.n-p.n).forEach((r,j)=>{for(let it=0;it<8;it++){const hit=regionData.slice(0,j).find(o=>Math.abs(o.x-r.x)<(o.w+r.w)/2+6&&Math.abs(o.y-r.y)<(o.fs+r.fs)/2+4);if(!hit)break;r.y+=(r.y>=hit.y?1:-1)*((hit.fs+r.fs)/2+6)}r.y=Math.max(r.fs,Math.min(H0-r.fs/2-4,r.y))});
 regionData.forEach(r=>{regionG2.append('text').attr('class','region').attr('x',r.x).attr('y',r.y).attr('font-size',r.fs).attr('dominant-baseline','middle').text(r.k==='ha'?T('ha'):fName(+r.k))});
 const toLabel=sn.slice().sort((a,b)=>b.st.n-a.st.n).slice(0,30);sn.filter(d=>d.st.ha>=4).sort((a,b)=>b.st.ha-a.st.ha).forEach(d=>{if(!toLabel.includes(d))toLabel.push(d)});
 const placed=[];const keepL=[];toLabel.forEach(d=>{const w=shortLabel(d.st).length*5.6,bx=[d.x+d.r+2,d.y-6,d.x+d.r+2+w,d.y+6];if(!placed.some(q=>!(bx[2]<q[0]||bx[0]>q[2]||bx[3]<q[1]||bx[1]>q[3]))){placed.push(bx);keepL.push(d)}});toLabel.length=0;keepL.forEach(d=>toLabel.push(d));
 const lblG=g.append('g').selectAll('text').data(toLabel).join('text').attr('class','lbl').attr('x',d=>d.x+d.r+3).attr('y',d=>d.y+3.5).text(d=>shortLabel(d.st));
 const tip=$('#tip'),box=$('#mapbox');
 function showTip(ev,html){tip.innerHTML=html;tip.hidden=false;const r=box.getBoundingClientRect();let x=ev.clientX-r.left+12,y=ev.clientY-r.top+12;if(x>r.width-310)x=Math.max(4,x-324);tip.style.left=x+'px';tip.style.top=y+'px'}
 function focusStone(d){const set=new Set(d.st.ps);edges.classed('on',e=>e.source===d);ppG.classed('dim',p=>!set.has(p.i));stG.classed('dim',s=>s!==d)}
 function clearFocus(){edges.classed('on',false);applyHA()}
 stG.on('mouseenter',(ev,d)=>{focusStone(d);showTip(ev,`<b>${esc(d.st.t)}</b><br>${esc(d.st.a.slice(0,4).map(x=>A[x].n).join(', '))}${d.st.a.length>4?' et al.':''}${d.st.y?' · '+d.st.y:''}<br>${d.st.n} ${T('papersCited')}`)})
   .on('mousemove',(ev)=>{tip.style.left;})
   .on('mouseleave',()=>{tip.hidden=true;clearFocus()})
   .on('click',(ev,d)=>{tip.hidden=true;showS(d.st.s)});
 ppG.on('mouseenter',(ev,d)=>{const p=P[d.i];showTip(ev,`${esc(p.t)}<br><span style="opacity:.75">${esc(fName(p.f))}${p.ha?' · '+T('ha'):''}</span>`);const mine=new Set(sn.filter(s=>s.st.ps.includes(d.i)));edges.classed('on',e=>e.target===d)})
   .on('mouseleave',()=>{tip.hidden=true;edges.classed('on',false)})
   .on('click',(ev,d)=>{tip.hidden=true;showP(d.i)});
 function applyHA(){const on=false;ppG.classed('dim',d=>on&&!P[d.i].ha);stG.classed('dim',d=>on&&d.st.ha<2);lblG.classed('dim',d=>on&&d.st.ha<2)}
 MAP.applyHA=applyHA;applyHA();
 const zoom=d3.zoom().scaleExtent([0.8,8]).on('zoom',ev=>{g.attr('transform',ev.transform);const k=ev.transform.k;lblG.attr('font-size',10.5/Math.sqrt(k)).attr('x',d=>d.x+d.r+3/k)});
 svg.call(zoom);MAP.reset=()=>svg.transition().duration(300).call(zoom.transform,d3.zoomIdentity);
 // legend
 $('#legend').innerHTML=`<span><svg width="10" height="10"><circle cx="5" cy="5" r="3" fill="hsl(200 42% 52%)"/></svg>${T('lgPP')}</span><span><svg width="16" height="16"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>${T('lgStone')}</span><span><svg width="16" height="16"><circle cx="8" cy="8" r="6" fill="none" stroke="var(--gold)" stroke-width="2"/></svg>${T('lgLau')}</span>`;
}
$('#tgEdges').addEventListener('click',e=>{const b=e.currentTarget;const on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on);document.getElementById('map').classList.toggle('showedges',on)});
$('#tgReset').addEventListener('click',()=>{if(MAP&&MAP.reset)MAP.reset()});
function stoneHTML(s){const st=STONES[s];
 return `<div class="eyebrow">${T('stoneK')}</div><h2>${esc(st.t)}</h2><div class="sub">${st.y||''}</div>
 <p>${T('authorsK')}: ${st.a.map(a=>`<span class="au${A[a].fm||A[a].ab||A[a].wf?' fmn':''}" data-a="${a}">${esc(nm(a))}</span>${ctag(A[a])}`).join(LANG==='zh'?'、':', ')}</p>
 ${st.l?`<p><a href="${esc(st.l)}" target="_blank" rel="noopener">${esc(st.l)}</a></p>`:''}
 <div class="trio"><div><b class="num">${st.n}</b><span>${T('papersCited')}</span></div><div><b class="num">${st.ha}</b><span>${T('ha')}</span></div><div><b class="num">${new Set(st.ps.map(i=>P[i].f)).size}</b><span>${T('fieldDist')}</span></div></div>
 <h3 style="font-size:16px;margin-top:18px">${T('citedBy')}</h3>
 ${st.ps.map(pi=>`<div class="entry"><h4><a href="#" class="openp" data-p="${pi}">${esc(P[pi].t)}</a></h4><div class="meta">${esc(fName(P[pi].f))}${P[pi].ha?' · '+T('ha'):''} · ${P[pi].d}</div></div>`).join('')}`}
function showS(s,keep){cur=['s',s];openSheet(stoneHTML(s),keep)}
// ---------- countries ----------
function renderCountries(){
 const agg={};let tagged=0;
 A.forEach((a,i)=>{if(!a.c||!aPapers[i].size)return;tagged++;const g=agg[a.c]=agg[a.c]||{n:0,people:[]};g.n+=score(i);g.people.push(i)});
 const rows=Object.entries(agg).sort((x,y)=>y[1].n-x[1].n);const max=rows.length?rows[0][1].n:1;
 $('#cty').innerHTML=rows.map(([c,g])=>{g.people.sort((x,y)=>score(y)-score(x));
  return `<button type="button" class="crow" data-c="${c}"><span>${esc(cName(c))}</span><span class="cb"><i style="width:${(g.n/max*100).toFixed(1)}%"></i></span><span class="cn">${g.n}</span><small>${g.people.slice(0,4).map(i=>esc(nm(i))).join(LANG==='zh'?'、':', ')}${g.people.length>4?' …':''}</small></button>`}).join('')+`<p class="note" style="grid-column:1/-1">${T('ctyNote')(tagged)}</p>`;
}
let CNMODE='all';
function countryHTML(c){let L=A.map((a,i)=>i).filter(i=>A[i].c===c&&aPapers[i].size).sort((x,y)=>score(y)-score(x));
 if(c==='CN'&&CNMODE==='only')L=L.filter(i=>A[i].ml);
 const cnsw=c==='CN'?`<div class="metbar" style="margin-top:12px"><div class="metsw" role="group"><span class="eyebrow">${T('cnL')}</span>${['all','only'].map(k=>`<button type="button" data-cn="${k}" aria-pressed="${k===CNMODE}">${T('cn_'+k)}</button>`).join('')}</div></div>`:'';
 return `<div class="eyebrow">${T('ctySheet')}</div><h2>${esc(cName(c))}</h2><div class="sub">${L.length} ${T('ctyWho')}</div>${cnsw}
 <ol class="board" style="margin-top:14px">${L.map((a,k)=>`<li class="${A[a].fm?'fm':A[a].ab?'ab':A[a].wf?'wf':''}" data-a="${a}" tabindex="0"><span class="rk">${k+1}</span><span class="nm">${esc(nm(a))}${LANG==='zh'&&A[a].zh?`<small>${esc(A[a].n)}</small>`:''}${stars(A[a])}${A[a].ml?`<span class="ctag ml">${T('mlTag')}</span>`:''}${aff(A[a])}</span><span class="bar"><i style="width:${(score(a)/(Math.max(...L.map(score))||1)*100).toFixed(1)}%"></i></span><span class="ct num">${score(a)}</span></li>`).join('')}</ol>`}
document.addEventListener('click',e=>{const b=e.target.closest('[data-cn]');if(b){CNMODE=b.dataset.cn;openSheet(countryHTML('CN'),true)}});
document.addEventListener('click',e=>{const r=e.target.closest('.crow');if(r){cur=['c',r.dataset.c];openSheet(countryHTML(r.dataset.c))}});
renderAll();
const h=location.hash.slice(1);if(/^a\d+$/.test(h))showA(+h.slice(1));else if(/^p\d+$/.test(h))showP(+h.slice(1));
})();
