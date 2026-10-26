// Beyond GDP: scoring and charts shared by the zh and en pages. build_page.py inlines this file.
// Each page defines DATA, YEARS, AREASRC, RAIL_MIN, RAIL_MAX, G20, FOCUS, REGIONS, DIMS and L (its strings) first.
const TRIP_KM=8;
const DEFAULT_W=Object.fromEntries(DIMS.map(d=>[d.k,d.w]));
let W={...DEFAULT_W};
const $=id=>document.getElementById(id);
const col=k=>`var(--c-${k})`;
const cl=v=>Math.max(0,Math.min(1,v)), ln=Math.log;
const lin=(x,a,b)=>x==null?null:cl((x-a)/(b-a)), lg=(x,a,b)=>x==null?null:cl((ln(x)-ln(a))/(ln(b)-ln(a)));
const avg=a=>{const v=a.filter(x=>x!=null&&!isNaN(x));return v.length?v.reduce((p,q)=>p+q,0)/v.length:null;};
const fmt=(n,d=0)=>n==null?"—":Number(n).toLocaleString("en-US",{maximumFractionDigits:d,minimumFractionDigits:d});
const popFmt=L.popFmt;

// Dimension scores (0-1) for one economy or region; null where data are missing.
function dimScores(r){
  r.hsrKm=r.hsr? r.hsr*1e6/r.pop : 0;
  r.urbanKm=r.urbanPkm? r.urbanPkm*1e6/r.pop : (r.urbanTrips? r.urbanTrips*1e6*TRIP_KM/r.pop : 0);
  r.railKm=r.hsrKm+r.urbanKm;
  const s={};
  s.elec=r.elec!=null? lg(Math.max(r.elec,100),100,15000):null;
  s.food=avg([lin(r.fruit,0,100),lin(r.veg,0,150),(r.meat!=null||r.egg!=null)?lin((r.meat??0)+(r.egg??0),0,72):null]);
  s.house=lin(r.area,10,50);
  const car=lin(r.cars,0,650), rail=r.railKm>0? lg(Math.max(r.railKm,RAIL_MIN),RAIL_MIN,RAIL_MAX):0;
  s.move= car!=null? .5*car+.5*rail : null;
  s.health=avg([lin(r.life,55,85), r.imr!=null? cl((ln(70)-ln(Math.max(r.imr,1.5)))/(ln(70)-ln(1.5))):null]);
  const access=Math.max(lin(r.bb,0,40)??0, lin(r.g5,0,100)??0);
  s.net= r.net!=null? (lin(r.net,40,100)+access)/2 : null;
  s.edu=lin(r.ter,20,80);
  s.safe=avg([lin(r.night,30,100), r.hom!=null? cl((ln(30)-ln(Math.max(r.hom,0.5)))/(ln(30)-ln(0.5))) : null]);
  return s;
}
DATA.forEach(r=>{ r.s=dimScores(r); });
// A missing dimension takes the average score of the G20 + EU economies that have it.
const G20AVG=Object.fromEntries(DIMS.map(d=>[d.k,avg(DATA.filter(r=>G20.includes(r.code)).map(r=>r.s[d.k]))]));
DATA.forEach(r=>DIMS.forEach(d=>{ if(r.s[d.k]==null) r.s[d.k]=G20AVG[d.k]; }));
REGIONS.forEach(r=>{ r.s=dimScores(r); DIMS.forEach(d=>{ if(r.s[d.k]==null) r.s[d.k]=G20AVG[d.k]; }); r.region=true; r.gdpY=2025; r.carsY=2025; r.areaY=r.code==="JZS"?2020:2024; });
const NATIONS=DATA.slice();
DATA.push(...REGIONS);  // shown everywhere for reference, but not ranked
$("g20house").textContent=Math.round(G20AVG.house*100);
let VIEW="g20", SHOW=DATA, gdpRank={};
const HL=new Set(["CHN","JZS"]);  // set in bold in every chart
const KEY=["JZS","CHN","USA","EUU","JPN","KOR","IND","GBR","DEU","FRA","ITA","RUS","SGP","HKG","SAU","ARE","QAT","CHE","NOR","BRA","MEX","TUR","AUS","CAN","IDN","NGA","VNM","ZAF","GUY","MAC","LUX"];

function weighted(r){
  let ws=0,t=0; DIMS.forEach(d=>{ if(r.s[d.k]!=null){ws+=W[d.k]; t+=W[d.k]*r.s[d.k];} });
  return ws? 100*t/ws : 0;
}
function score(){
  const ws=DIMS.reduce((a,d)=>a+W[d.k],0);
  DATA.forEach(r=>{
    r.contrib={}; DIMS.forEach(d=>{ r.contrib[d.k]= ws? 100*W[d.k]*r.s[d.k]/ws : 0; });
    r.score=weighted(r);
  });
  const pick= VIEW==="g20only"? G20 : VIEW==="g20"? FOCUS : null;
  SHOW= pick? DATA.filter(r=>pick.includes(r.code)||r.region) : DATA;
  const ranked=SHOW.filter(r=>!r.region);
  gdpRank=Object.fromEntries([...ranked].sort((a,b)=>b.gdp-a.gdp).map((r,i)=>[r.code,i+1]));
  [...ranked].sort((a,b)=>b.score-a.score).forEach((r,i)=>r.rank=i+1);
}

// ---------- shared chart helpers
const tip=$("tip");
function showTip(x,y,html){
  tip.innerHTML=html; tip.hidden=false;
  const w=tip.offsetWidth||260, h=tip.offsetHeight||120;
  let l=x+16, t=y+16;
  if(l+w>innerWidth-8) l=x-w-16;
  if(t+h>innerHeight-8) t=y-h-16;
  tip.style.left=Math.max(8,l)+"px"; tip.style.top=Math.max(8,t)+"px";
}
function hideTip(){ tip.hidden=true; }
const widthOf=el=>Math.max(300,Math.round(el.clientWidth||880));
// Approximate text width: CJK glyphs are square, Latin about 0.56 em.
const tw=(s,fs=12)=>[...String(s)].reduce((a,c)=>a+(c.charCodeAt(0)>0x2e80?fs:fs*.58),0);
const clip=(s,fs,w)=>{ if(tw(s,fs)<=w) return s; const t=[...s]; while(t.length>1&&tw(t.join("")+"…",fs)>w) t.pop(); return t.join("")+"…"; };
const svgOpen=(w,h,label)=>`<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" role="img" aria-label="${label}">`;
const nameOf=r=>r.region? r.name+L.regionParen : r.name;
const sw=k=>`<span class="sw" style="background:${col(k)}"></span>`;
// Bar with a square baseline and a 4px rounded data end.
function barPath(x0,y,x1,h){
  const w=Math.max(0,x1-x0), r=Math.min(4,h/2,w);
  return `M${x0},${y}H${x1-r}a${r},${r} 0 0 1 ${r},${r}V${y+h-r}a${r},${r} 0 0 1 ${-r},${r}H${x0}Z`;
}
// Hover the nearest point within reach (hit area much larger than the dot); works for touch too.
function hoverPoints(el,P,tipf){
  const svg=el.querySelector("svg"); if(!svg) return;
  const ring=svg.querySelector(".hl-ring");
  const off=()=>{ ring.style.display="none"; hideTip(); };
  const move=e=>{
    const b=svg.getBoundingClientRect(), k=svg.viewBox.baseVal.width/b.width;
    const mx=(e.clientX-b.left)*k, my=(e.clientY-b.top)*k;
    let best=null, bd=26*k;
    P.forEach(p=>{ const d=Math.hypot(p.X-mx,p.Y-my); if(d<bd){bd=d;best=p;} });
    if(!best) return off();
    ring.setAttribute("cx",best.X); ring.setAttribute("cy",best.Y); ring.style.display="";
    showTip(e.clientX,e.clientY,tipf(best));
  };
  svg.addEventListener("pointermove",move);
  svg.addEventListener("pointerdown",move);
  svg.addEventListener("pointerleave",off);
}

// Scatter with solid hairline grid, optional trend line with residual stems, and greedy direct labels.
function scatter(el,o){
  const Wd=widthOf(el), H=Math.round(Math.min(o.Hmax||560,Math.max(340,Wd*.6)));
  const m={l:46,r:22,t:30,b:44}, pw=Wd-m.l-m.r, ph=H-m.t-m.b;
  const sx=v=>m.l+pw*(o.xlog?(ln(v)-ln(o.xdom[0]))/(ln(o.xdom[1])-ln(o.xdom[0])):(v-o.xdom[0])/(o.xdom[1]-o.xdom[0]));
  const sy=v=>m.t+ph-ph*(o.ylog?(ln(v)-ln(o.ydom[0]))/(ln(o.ydom[1])-ln(o.ydom[0])):(v-o.ydom[0])/(o.ydom[1]-o.ydom[0]));
  const cid=`clip-${el.id}`;
  let s=svgOpen(Wd,H,o.aria)+`<defs><clipPath id="${cid}"><rect x="${m.l}" y="${m.t}" width="${pw}" height="${ph}"/></clipPath></defs>`;
  o.yticks.forEach(t=>{ s+=`<line class="gl" x1="${m.l}" x2="${Wd-m.r}" y1="${sy(t)}" y2="${sy(t)}"/><text x="${m.l-8}" y="${sy(t)+4}" text-anchor="end">${o.yfmt(t)}</text>`; });
  o.xticks.forEach(t=>{ s+=`<line class="gl" x1="${sx(t)}" x2="${sx(t)}" y1="${m.t}" y2="${m.t+ph}"/><text x="${sx(t)}" y="${m.t+ph+18}" text-anchor="middle">${o.xfmt(t)}</text>`; });
  s+=`<text class="at" x="${m.l}" y="${m.t-12}">${o.ylabel}</text><text class="at" x="${Wd-m.r}" y="${H-4}" text-anchor="end">${o.xlabel}</text>`;
  (o.notes||[]).forEach(n=>{ s+=`<text class="note" x="${n.x==="l"?m.l+10:Wd-m.r-10}" y="${n.y==="t"?m.t+20:m.t+ph-12}" text-anchor="${n.x==="l"?"start":"end"}">${n.t}</text>`; });
  const P=o.pts.map(p=>({...p,X:sx(p.x),Y:sy(p.y)}));
  if(o.trend){
    s+=`<g clip-path="url(#${cid})">`;
    P.forEach(p=>{ if(!p.hollow) s+=`<line x1="${p.X}" x2="${p.X}" y1="${p.Y}" y2="${sy(o.trend(p.x))}" stroke="${p.c}" stroke-opacity=".5" stroke-width="1.5"/>`; });
    s+=`<line x1="${sx(o.xdom[0])}" y1="${sy(o.trend(o.xdom[0]))}" x2="${sx(o.xdom[1])}" y2="${sy(o.trend(o.xdom[1]))}" stroke="var(--ink-2)" stroke-width="2"/></g>`;
  }
  P.forEach(p=>{ s+= p.hollow? `<circle cx="${p.X}" cy="${p.Y}" r="5.5" fill="var(--bg)" stroke="var(--ink)" stroke-width="2"/>` : `<circle cx="${p.X}" cy="${p.Y}" r="5" fill="${p.c}" stroke="var(--bg)" stroke-width="2"/>`; });
  // Labels: only the listed economies, placed where they collide with no dot, label or edge.
  const placed=P.map(p=>({x0:p.X-6,x1:p.X+6,y0:p.Y-6,y1:p.Y+6}));
  const hit=b=>b.x0<m.l-4||b.x1>Wd-2||b.y0<m.t||b.y1>m.t+ph||placed.some(q=>b.x0<q.x1&&b.x1>q.x0&&b.y0<q.y1&&b.y1>q.y0);
  const keep=o.keep.slice(0,Wd<560?12:o.keep.length);
  keep.map(c=>P.find(p=>p.code===c)).filter(Boolean).forEach(p=>{
    const key=HL.has(p.code), w=tw(p.name,12)+(key?4:0), h=14;
    for(const [dx,dy,anc] of [[9,4,"start"],[-9,4,"end"],[0,-10,"middle"],[0,19,"middle"],[8,-8,"start"],[-8,-8,"end"],[8,16,"start"],[-8,16,"end"]]){
      const x0=anc==="start"?p.X+dx:anc==="end"?p.X+dx-w:p.X+dx-w/2, b={x0,x1:x0+w,y0:p.Y+dy-11,y1:p.Y+dy-11+h};
      if(!hit(b)){ placed.push(b); s+=`<text class="lb${key?" key":""}" x="${p.X+dx}" y="${p.Y+dy}" text-anchor="${anc}">${p.name}</text>`; break; }
    }
  });
  if(o.trend){ const tx=sx(o.xdom[1]), ty=sy(o.trend(o.xdom[1])); if(ty>m.t+12&&ty<m.t+ph) s+=`<text class="at" x="${tx-4}" y="${ty-8}" text-anchor="end">${L.trend}</text>`; }
  s+=`<circle class="hl-ring" r="9" fill="none" stroke="var(--ink)" stroke-width="1.5" style="display:none"/></svg>`;
  el.innerHTML=s;
  hoverPoints(el,P,o.tipf);
}

// Horizontal bars, sorted, with a full-score line and the value at each bar's end.
function hbar(el,rows,o){
  const Wd=widthOf(el), fs=12, rh=22, bh=12;
  const lw=Math.min(Wd*.36,Math.max(...rows.map(r=>tw(nameOf(r),fs)))+16);
  const m={l:lw,r:58,t:40,b:6}, H=m.t+rows.length*rh+m.b, pw=Wd-m.l-m.r;
  const sx=v=>m.l+pw*Math.min(v,o.max)/o.max;
  let s=svgOpen(Wd,H,o.aria);
  o.ticks.forEach(t=>{ s+=`<line class="gl" x1="${sx(t)}" x2="${sx(t)}" y1="${m.t-6}" y2="${H-m.b}"/><text x="${sx(t)}" y="${m.t-12}" text-anchor="middle">${fmt(t)}</text>`; });
  s+=`<line class="cap" x1="${sx(o.cap)}" x2="${sx(o.cap)}" y1="${8}" y2="${H-m.b}"/><text class="capt" x="${sx(o.cap)+5}" y="${17}">${o.capLabel}</text>`;
  rows.forEach((r,i)=>{
    const y=m.t+i*rh, v=o.val(r), key=HL.has(r.code), x1=sx(v);
    s+=`<g data-i="${i}"><rect x="0" y="${y}" width="${Wd}" height="${rh}" fill="transparent"/>`;
    const paren=r.region?L.regionParen:"";
    s+=`<text class="lb${key?" key":""}" x="${m.l-10}" y="${y+rh/2+4}" text-anchor="end">${clip(r.name,fs,m.l-12-tw(paren,fs))}${paren?`<tspan class="mu" font-weight="400">${paren}</tspan>`:""}</text>`;
    s+=`<path d="${barPath(m.l,y+(rh-bh)/2,x1,bh)}" fill="${o.color}"${o.faint&&o.faint(r)?' style="fill-opacity:var(--faint)"':""}/>`;
    if(v>o.max) s+=`<path d="M${x1-14},${y+(rh-bh)/2-1}l-4,${bh+2}M${x1-9},${y+(rh-bh)/2-1}l-4,${bh+2}" stroke="var(--bg)" stroke-width="2"/>`;
    s+=`<text class="val" x="${x1+6}" y="${y+rh/2+4}">${o.lab(r)}</text></g>`;
  });
  el.innerHTML=s+"</svg>";
  const svg=el.querySelector("svg"); if(!svg) return;
  svg.addEventListener("pointermove",e=>{ const g=e.target.closest&&e.target.closest("g[data-i]"); if(!g) return hideTip(); showTip(e.clientX,e.clientY,o.tipf(rows[+g.dataset.i])); });
  svg.addEventListener("pointerleave",hideTip);
}

// ---------- the charts
function renderSlope(){
  const el=$("slope"), Wd=widthOf(el), R=SHOW.filter(r=>!r.region), n=R.length;
  const rh=n>40?14:n>24?21:24, fs=n>40?10.5:12, top=34;
  // Keep the slopes steep enough to read: the chart is at most 780px wide, centred.
  const cw=Math.min(Wd,780), ox=(Wd-cw)/2;
  const lw=Math.min(cw*.34,Math.max(...R.map(r=>tw(r.name,fs)))+40), x0=ox+lw, x1=ox+cw-lw, H=top+n*rh+6;
  const y=i=>top+(i-.5)*rh;
  const items=R.map(r=>{const g=gdpRank[r.code], l=r.rank, d=g-l; return {r,g,l,d,c:Math.abs(d)<3?"var(--flat)":d>0?"var(--up)":"var(--down)"};})
    .sort((a,b)=>Math.abs(a.d)-Math.abs(b.d));
  let s=svgOpen(Wd,H,L.slopeAria);
  s+=`<text class="at" x="${x0}" y="14" text-anchor="end">${L.slopeL}</text><text class="at" x="${x1}" y="14">${L.slopeR}</text>`;
  s+=`<line class="gl" x1="${x0}" x2="${x0}" y1="${top-8}" y2="${H-4}"/><line class="gl" x1="${x1}" x2="${x1}" y1="${top-8}" y2="${H-4}"/>`;
  items.forEach(it=>{
    const c=it.r.code, ya=y(it.g), yb=y(it.l);
    s+=`<g class="sl" data-c="${c}"><line x1="${x0}" y1="${ya}" x2="${x1}" y2="${yb}" stroke="${it.c}" stroke-width="2"/>`
      +`<circle cx="${x0}" cy="${ya}" r="3.5" fill="${it.c}" stroke="var(--bg)" stroke-width="1.5"/><circle cx="${x1}" cy="${yb}" r="3.5" fill="${it.c}" stroke="var(--bg)" stroke-width="1.5"/>`
      +`<line x1="${x0}" y1="${ya}" x2="${x1}" y2="${yb}" stroke="transparent" stroke-width="${Math.max(10,rh-4)}"/></g>`;
  });
  items.forEach(it=>{
    const c=it.r.code, key=HL.has(c)?" key":"", ya=y(it.g)+fs/3, yb=y(it.l)+fs/3, nm=clip(it.r.name,fs,lw-34);
    s+=`<text class="lb${key}" data-c="${c}" x="${x0-30}" y="${ya}" text-anchor="end" font-size="${fs}">${nm}</text><text data-c="${c}" x="${x0-10}" y="${ya}" text-anchor="end" font-size="${fs-1}">${it.g}</text>`;
    s+=`<text data-c="${c}" x="${x1+10}" y="${yb}" font-size="${fs-1}">${it.l}</text><text class="lb${key}" data-c="${c}" x="${x1+30}" y="${yb}" font-size="${fs}">${nm}</text>`;
  });
  el.innerHTML=s+"</svg>";
  const svg=el.querySelector("svg"); if(!svg) return;
  const off=()=>{ svg.classList.remove("dim"); svg.querySelectorAll(".on").forEach(x=>x.classList.remove("on")); hideTip(); };
  svg.addEventListener("pointermove",e=>{
    const t=e.target.closest&&e.target.closest("[data-c]"); if(!t) return off();
    const c=t.dataset.c, it=items.find(i=>i.r.code===c);
    svg.querySelectorAll(".on").forEach(x=>{ if(x.dataset.c!==c) x.classList.remove("on"); });
    svg.querySelectorAll(`[data-c="${c}"]`).forEach(x=>x.classList.add("on"));
    svg.classList.add("dim");
    showTip(e.clientX,e.clientY,L.slopeTip(it.r.name,it.g,it.l,it.d));
  });
  svg.addEventListener("pointerleave",off);
}

$("slopeleg").innerHTML=[["up","dot"],["down","dot"],["flat","dot"]].map(([c,k],i)=>`<span class="k"><span class="sw ${k}" style="background:var(--${c})"></span>${L.slopeLeg[i]}</span>`).join("");

function rankTip(r){
  const head=r.region? L.notRanked : L.rankLine(r.rank,gdpRank[r.code]);
  return `<div class="tt">${r.name}</div><div>${L.scoreLbl} <b>${r.score.toFixed(1)}</b> · ${head}</div>`
    +`<table><tr><th>${L.tipHead[0]}</th><th>${L.tipHead[1]}</th><th>${L.tipHead[2]}</th></tr>`
    +DIMS.map(d=>`<tr><td>${sw(d.k)}${d.full}</td><td>${Math.round(r.s[d.k]*100)}</td><td>${r.contrib[d.k].toFixed(1)}</td></tr>`).join("")+`</table>`;
}
function renderRank(){
  const rows=[...SHOW].sort((a,b)=>b.score-a.score);
  let h=`<div class="rr hd"><span class="n">#</span><span>${L.rankH[1]}</span><span class="pop">${L.rankH[2]}</span><span class="bc">${L.rankH[3]}</span><span class="sc">${L.rankH[4]}</span><span class="dl">${L.rankH[5]}</span></div>`;
  rows.forEach(r=>{
    const seg=DIMS.filter(d=>r.contrib[d.k]>0.05).map(d=>`<i class="${d.k}" style="flex-grow:${r.contrib[d.k].toFixed(3)};background:${col(d.k)}"></i>`).join("");
    const d=r.region? null : gdpRank[r.code]-r.rank;
    const dl= d==null? `<span class="na">—</span>` : d===0? `<span class="na">=</span>` : `<span class="g ${d>0?"up":"down"}">${d>0?"▲":"▼"}</span>${Math.abs(d)}`;
    h+=`<div class="rr${HL.has(r.code)?" key":""}${r.region?" reg":""}" data-c="${r.code}"><span class="n">${r.region?"·":r.rank}</span>`
      +`<span class="nm">${r.name}${r.region?`<span class="tag">${L.region}</span>`:""}<small>${popFmt(r.pop)}${r.region?" · "+L.region:""}</small></span>`
      +`<span class="pop">${popFmt(r.pop)}</span><span class="bc"><span class="sb" style="width:${r.score.toFixed(2)}%">${seg}</span></span>`
      +`<span class="sc">${r.score.toFixed(1)}</span><span class="dl">${dl}</span></div>`;
  });
  $("rank").innerHTML=h;
}
const rankEl=$("rank");
rankEl.addEventListener("pointermove",e=>{
  const row=e.target.closest&&e.target.closest(".rr[data-c]"); if(!row) return hideTip();
  showTip(e.clientX,e.clientY,rankTip(SHOW.find(r=>r.code===row.dataset.c)));
});
rankEl.addEventListener("pointerleave",hideTip);
// Legend: hover or tap a dimension to see its share of every bar.
let pinned=null;
const setHL=k=>{ if(k){rankEl.dataset.hl=k; rankEl.classList.add("hl");} else {delete rankEl.dataset.hl; rankEl.classList.remove("hl");} };
$("legend").innerHTML=DIMS.map(d=>`<button type="button" class="k" data-k="${d.k}" aria-pressed="false">${sw(d.k)}${d.full}</button>`).join("")+`<span class="hint">${L.legendHint}</span>`;
$("legend").querySelectorAll("button").forEach(b=>{
  b.addEventListener("pointerenter",()=>setHL(b.dataset.k));
  b.addEventListener("pointerleave",()=>setHL(pinned));
  b.addEventListener("click",()=>{ pinned= pinned===b.dataset.k? null : b.dataset.k; $("legend").querySelectorAll("button").forEach(x=>x.setAttribute("aria-pressed",String(x.dataset.k===pinned))); setHL(pinned); });
});

function fit(){
  const pts=SHOW.filter(r=>!r.region), xs=pts.map(r=>ln(r.gdp)), ys=pts.map(r=>r.score), n=xs.length;
  const mx=xs.reduce((a,b)=>a+b)/n, my=ys.reduce((a,b)=>a+b)/n;
  let sxy=0,sxx=0; xs.forEach((x,i)=>{sxy+=(x-mx)*(ys[i]-my);sxx+=(x-mx)**2;});
  const b=sxy/sxx,a=my-b*mx; return g=>a+b*ln(g);
}
function renderScatter(){
  const f=fit();
  SHOW.forEach(r=>r.resid=r.score-f(r.gdp));
  const ymin=Math.max(0,Math.floor(Math.min(...SHOW.map(r=>r.score))/10)*10-10);
  const yt=[];for(let v=ymin;v<=100;v+=10)yt.push(v);
  const nat=SHOW.filter(r=>!r.region).sort((a,b)=>b.resid-a.resid), k=VIEW==="all"?6:3;
  const ends=[...nat.slice(0,3),...nat.slice(-3)].map(r=>r.code);
  scatter($("scatter"),{
    aria:L.sy+" / "+L.sx,
    pts:SHOW.map(r=>({code:r.code,name:r.name,x:r.gdp,y:r.score,r,hollow:!!r.region,c:r.resid>=0?"var(--up)":"var(--down)"})),
    keep:[...new Set(["JZS","CHN","USA",...ends,...KEY])].filter(c=>VIEW!=="all"||ends.includes(c)||KEY.indexOf(c)<16),
    xlog:true,xdom:[6000,180000],ydom:[ymin,100],xticks:[10000,20000,50000,100000],yticks:yt,
    xfmt:t=>"$"+(t/1000)+"k",yfmt:t=>t,xlabel:L.sx,ylabel:L.sy,trend:f,
    tipf:p=>L.scatTip(p.r,p.r.score-p.r.resid,p.r.region?null:[p.r.rank,gdpRank[p.code]])
  });
  $("scatleg").innerHTML=`<span class="k"><span class="sw dot" style="background:var(--up)"></span>${L.scatLeg[0]}</span><span class="k"><span class="sw dot" style="background:var(--down)"></span>${L.scatLeg[1]}</span><span class="k"><span class="sw ring"></span>${L.scatLeg[2]}</span><span class="k"><span class="sw line" style="background:var(--ink-2)"></span>${L.scatLeg[3]}</span>`;
  const li=r=>`<b>${r.name}</b> <span class="num">${r.resid>0?"+":""}${r.resid.toFixed(1)}</span>`;
  $("findings").innerHTML=`<p>${L.findings(nat.slice(0,k).map(li).join(L.sep),nat.slice(-k).reverse().map(li).join(L.sep))}</p>`;
}

function renderMove(){
  const pts=SHOW.filter(r=>r.cars!=null).map(r=>({code:r.code,name:r.name,x:Math.min(r.cars,1000),y:Math.max(r.railKm,1),r,hollow:!!r.region,c:"var(--c-move)"}));
  scatter($("move"),{
    aria:L.my+" / "+L.mx,pts,keep:KEY,Hmax:520,
    xdom:[0,1000],ylog:true,ydom:[1,RAIL_MAX*2],xticks:[0,200,400,600,800,1000],yticks:[1,10,100,1000],
    xfmt:t=>t===1000?"≥1,000":fmt(t),yfmt:t=>t===1?"≈0":fmt(t),xlabel:L.mx,ylabel:L.my,
    notes:[{x:"l",y:"t",t:L.moveNotes[0]},{x:"r",y:"t",t:L.moveNotes[1]},{x:"r",y:"b",t:L.moveNotes[2]}],
    tipf:p=>L.moveTip(p.r)
  });
  const miss=SHOW.filter(r=>r.cars==null).length;
  $("movecap").textContent=L.movecap(miss);
}
function renderElec(){
  const rows=SHOW.filter(r=>r.elec!=null).sort((a,b)=>b.elec-a.elec);
  hbar($("elec"),rows,{aria:L.elecAria,max:30000,ticks:[0,10000,20000,30000],cap:15000,capLabel:L.elecCap,val:r=>r.elec,lab:r=>fmt(r.elec),color:"var(--c-elec)",tipf:L.elecTip});
  const nat=rows.filter(r=>!r.region), cn=DATA.find(r=>r.code==="CHN");
  $("electxt").textContent=L.electxt(nat[nat.length-1],nat[0],cn,nat.indexOf(cn)+1,nat.length);
}
function renderArea(){
  const rows=SHOW.filter(r=>r.area!=null).sort((a,b)=>b.area-a.area);
  hbar($("area"),rows,{aria:L.areaAria,max:90,ticks:[0,30,60,90],cap:50,capLabel:L.areaCap,val:r=>r.area,lab:r=>fmt(r.area,1),color:"var(--c-house)",faint:r=>r.weakArea,tipf:L.areaTip});
}
$("areasrc").innerHTML=AREASRC.map(L.areaSrc).join("");

const DEC={score:1,area:1,life:1,imr:1,net:1,bb:1,g5:1,night:1,hom:1,ter:1,fruit:1,veg:1,meat:1,egg:1};
let sortK="score",sortD=-1;
function renderTable(){
  const rows=[...SHOW].sort((a,b)=>{const x=a[sortK],y=b[sortK];if(x==null)return 1;if(y==null)return -1;return typeof x==="string"?sortD*x.localeCompare(y,L.collate):sortD*(x-y);});
  let h="<thead><tr>"+L.cols.map(([k,l])=>`<th data-k="${k}" ${k===sortK?`aria-sort="${sortD<0?"descending":"ascending"}"`:""}>${l}${k===sortK?(sortD<0?" ↓":" ↑"):""}</th>`).join("")+"</tr></thead><tbody>";
  rows.forEach(r=>{h+=`<tr${r.region?' class="reg"':""}>`+L.cols.map(([k])=>{const v=r[k];return `<td${v==null?' class="na"':""}>${k==="name"?nameOf(r):k==="pop"?popFmt(v):fmt(v,DEC[k]||0)}</td>`;}).join("")+"</tr>";});
  $("tbl").innerHTML=h+"</tbody>";
}
$("tbl").addEventListener("click",e=>{ const th=e.target.closest&&e.target.closest("th[data-k]"); if(!th) return; const k=th.dataset.k; sortD=k===sortK?-sortD:(k==="name"?1:-1); sortK=k; renderTable(); });
$("years").innerHTML=`<thead><tr>${L.yearsH.map(x=>`<th>${x}</th>`).join("")}</tr></thead><tbody>`+YEARS.map(y=>`<tr><td>${y.label}</td><td>${y.years}</td><td>${y.n} / ${NATIONS.length}</td></tr>`).join("")+"</tbody>";

function renderCmp(){
  const by=c=>DATA.find(r=>r.code===c), jz=REGIONS[0], cols=[jz,by("CHN"),by("USA"),by("EUU"),by("JPN")];
  const ref=NATIONS.filter(r=>FOCUS.includes(r.code)).map(weighted);
  const rankIn=v=>1+ref.filter(x=>x>v).length;
  const isNat=(r,tag)=>!!(tag&&r.national&&r.national.includes(tag));
  const vals=[r=>popFmt(r.pop),r=>"$"+fmt(r.gdp),r=>fmt(r.elec),r=>r.area==null?"—":fmt(r.area,1),r=>fmt(r.cars),
    r=>fmt(r.hsr? r.hsr*1e6/r.pop:0),r=>fmt(r.urbanPkm? r.urbanPkm*1e6/r.pop : (r.urbanTrips||0)*1e6*TRIP_KM/r.pop),
    r=>fmt(r.life,1),r=>fmt(r.imr,1),r=>fmt(r.net,1),r=>fmt(r.ter,1),r=>fmt(r.night),r=>fmt(r.hom,1)];
  const td=(j,cls,html)=>`<td class="${j===0?"jz ":""}${cls}">${html}</td>`;
  let h=`<thead><tr><th>${L.cmpH}</th>${cols.map((r,j)=>`<th class="${j===0?"jz":""}">${r.name}${r.nation?"":L.national}</th>`).join("")}</tr></thead><tbody>`;
  L.cmp.forEach(([lab,tag],i)=>{ h+=`<tr><td>${lab}</td>${cols.map((r,j)=>td(j,isNat(r,tag)?"nat":"",vals[i](r))).join("")}</tr>`; });
  DIMS.forEach((d,i)=>{ h+=`<tr class="${i===0?"sub":""}"><td>${L.dimScore(d)}</td>${cols.map((r,j)=>{const v=Math.round(r.s[d.k]*100);return td(j,isNat(r,d.name)||isNat(r,d.full)?"nat":"",`<span class="mb"><i style="width:${v}%;background:${col(d.k)}"></i></span>${v}`);}).join("")}</tr>`; });
  h+=`<tr class="sub tot"><td>${L.overall}</td>${cols.map((r,j)=>td(j,"",weighted(r).toFixed(1))).join("")}</tr>`;
  h+=`<tr><td>${L.rankAmong(FOCUS.length)}</td>${cols.map((r,j)=>td(j,"",L.nth(rankIn(weighted(r))))).join("")}</tr></tbody>`;
  $("cmp").innerHTML=h;
}
$("cmpcap").textContent=L.cmpcap;
$("cmpnotes").innerHTML=REGIONS.map(L.regionNote).join("");

// ---------- controls
$("dims").innerHTML=DIMS.map(d=>`<div class="dim" style="--c:${col(d.k)}"><div class="dh"><span class="dn">${d.full}</span><span class="wt" data-wt="${d.k}"></span></div>${d.desc}</div>`).join("");
$("weights").innerHTML=DIMS.map(d=>`<label class="w" for="w-${d.k}">${sw(d.k)}<span>${d.full}</span><output id="o-${d.k}"></output><input type="range" id="w-${d.k}" min="0" max="50" step="0.25" value="${d.w}" style="accent-color:${col(d.k)}"></label>`).join("");
DIMS.forEach(d=>$("w-"+d.k).addEventListener("input",e=>{W[d.k]=+e.target.value;render();}));
const resetW=()=>{W={...DEFAULT_W};DIMS.forEach(d=>$("w-"+d.k).value=W[d.k]);render();};
$("reset").addEventListener("click",resetW);
const views=L.views(NATIONS.length);
$("viewseg").innerHTML=Object.entries(views).map(([v,t])=>`<button type="button" data-v="${v}">${t}</button>`).join("");
$("viewseg").setAttribute("aria-label",L.viewAria);
$("viewseg").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{VIEW=b.dataset.v;render();}));
$("wstate").innerHTML=`${L.wChanged}<button type="button">${L.reset}</button>`;
$("wstate").querySelectorAll("button").forEach(b=>b.addEventListener("click",resetW));
// Table of contents from the section headings.
const heads=[...document.querySelectorAll("main h2")];
heads.forEach((h,i)=>{ if(!h.id) h.id="s"+(i+1); });
$("toc").innerHTML=heads.map((h,i)=>`<a href="#${h.id}"><span>${String(i+1).padStart(2,"0")}</span>${h.textContent}</a>`).join("");
const tocBtn=$("tocbtn");
const tocOpen=on=>{ $("toc").hidden=!on; tocBtn.setAttribute("aria-expanded",String(on)); };
tocBtn.addEventListener("click",e=>{ e.stopPropagation(); tocOpen($("toc").hidden); });
$("toc").addEventListener("click",e=>{ if(e.target.closest&&e.target.closest("a")) tocOpen(false); });
document.addEventListener("click",e=>{ if(!$("toc").hidden&&!(e.target.closest&&e.target.closest("#toc"))) tocOpen(false); });
document.addEventListener("keydown",e=>{ if(e.key==="Escape"){ tocOpen(false); hideTip(); } });

function renderCharts(){ renderSlope(); renderRank(); renderScatter(); renderMove(); renderElec(); renderArea(); renderTable(); renderCmp(); }
function render(){
  const tot=DIMS.reduce((a,d)=>a+W[d.k],0);
  DIMS.forEach(d=>{ const pct=tot?Math.round(1000*W[d.k]/tot)/10:0; $("o-"+d.k).textContent=pct+"%"; document.querySelector(`[data-wt="${d.k}"]`).innerHTML=`${pct}<small>%</small>`; });
  $("wmix").innerHTML=DIMS.filter(d=>W[d.k]>0).map(d=>`<i style="flex-grow:${W[d.k]};background:${col(d.k)}"></i>`).join("");
  $("wsum").textContent=tot?L.wsum:L.wzero;
  $("wstate").hidden=DIMS.every(d=>W[d.k]===DEFAULT_W[d.k]);
  score();
  $("viewseg").querySelectorAll("button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.v===VIEW)));
  renderCharts();
}
render();
// Charts are drawn at their real width so text stays readable; redraw when the width changes.
if(typeof ResizeObserver!=="undefined"){
  let lastW=$("rank").clientWidth, pend=0;
  new ResizeObserver(()=>{ const w=$("rank").clientWidth; if(w===lastW) return; lastW=w; cancelAnimationFrame(pend); pend=requestAnimationFrame(renderCharts); }).observe($("rank"));
}
