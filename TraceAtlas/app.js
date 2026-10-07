// TraceAtlas（原 Cot-trace）：静态页面，数据在 data/ 下（由 src/corpus/export_site.py 导出）。中英双语。
// 路由：#/ 列表；#/t/<traj_id> 单条轨迹；#/review 人工核对列表；#/review/<traj_id> 核对一条；#/about 说明
const REVIEW_KEY = "cot-review-v1";
const LANG_KEY = "cot-lang";
const REVIEW_BASE = "27B·v4";   // 核对时的默认值来自哪份标注
let INDEX = null;
const cache = {};

const I18N = {
  zh: {
    nav_list: "轨迹列表", nav_review: "人工核对", nav_about: "说明", nav_blog: "博客", switch: "English",
    list_title: "轨迹列表", n_items: n => `（${n} 条）`,
    tier: "难度", correct: "对错", length: "长度", set: "集合", all: "全部", right: "正确", wrong: "错误",
    set_api: "有 API 参照", set_human: "人工核对", set_pilot: "试点", set_corpus: "全量打标（第四版）抽样", sort_by: "按", sort_suffix: "的探索占比排序",
    col_traj: "轨迹", col_tokens: "token", col_paras: "段数", col_exp: "探索占比", col_ann: "标注", col_status: "状态",
    ok: "对", bad: "错", back: "← 返回", review_mode: "核对模式", answered_right: "答对", answered_wrong: "答错",
    paras: n => `${n} 段`, leak: "泄露", problem: "题目", gold: "标准答案", pred: "教师答案", none: "（无）",
    how_title: "怎么核对：",
    how: "只看一件事——每段是不是<b>探索</b>，即没有进入最终推导的尝试（换掉的方法、算错重来、试了没用上的计算或猜测）。最终推导用到的、答案之前的设定/复述/计划算主路径；灰色的“答案之后”不用管。默认值是 27B 第四版的标注，不同意就改。改过的段落会有虚线框。全部看完点“标记为已完成”。",
    lg_main: "主路径", lg_exp: "探索（A+D）", lg_post: "答案之后（P）", done_btn: "标记为已完成",
    final_answer: "正式回答", note: "备注", method: "方法摘要", exp_cb: "探索",
    base_exp: p => `27B：探索（${p}）`, base_post: "27B：答案之后", base_main: "27B：主路径",
    review_title: n => `人工核对（${n} 条）`,
    review_hint: "进度只存在这个浏览器里。全部完成后点“导出”，把下载的 JSON 文件交给 Agent。",
    done_count: (a, b) => `已完成 ${a} / ${b}`, export: "导出核对结果", reset: "清空本地进度",
    st_done: "已完成", st_doing: "进行中", st_todo: "未开始", confirm_reset: "清空本浏览器里的全部核对进度？",
    about_title: "说明", load_fail: "加载失败：",
    labels: {SU: "设定", PL: "计划", RC: "引用", CP: "计算", EX: "探索", VF: "验证", MB: "监控", CS: "汇总", AN: "答案"},
  },
  en: {
    nav_list: "Traces", nav_review: "Human review", nav_about: "About", nav_blog: "Blog", switch: "中文",
    list_title: "Traces", n_items: n => ` (${n} traces)`,
    tier: "Difficulty", correct: "Correct", length: "Length", set: "Subset", all: "All", right: "Correct", wrong: "Wrong",
    set_api: "With API reference", set_human: "Human review", set_pilot: "Pilot", set_corpus: "Full run (v4) sample", sort_by: "Sort by", sort_suffix: "exploration share",
    col_traj: "Trace", col_tokens: "Tokens", col_paras: "Paragraphs", col_exp: "Exploration", col_ann: "Annotations", col_status: "Status",
    ok: "✓", bad: "✗", back: "← Back", review_mode: "Review mode", answered_right: "Correct", answered_wrong: "Wrong",
    paras: n => `${n} paragraphs`, leak: "Leak", problem: "Problem", gold: "Gold answer", pred: "Teacher answer", none: "(none)",
    how_title: "How to review: ",
    how: "Judge one thing only — is each paragraph <b>exploration</b>, i.e. an attempt that did not make it into the final derivation (a dropped method, a wrong computation that was redone, a computation or guess that was tried and never used)? What the final derivation uses, and setup/restating/planning before the answer, is the main path; ignore the grey “post-answer” part. Defaults come from the 27B v4 labels; change any you disagree with. Changed paragraphs get a dashed outline. When done, click “Mark as done”.",
    lg_main: "Main path", lg_exp: "Exploration (A+D)", lg_post: "Post-answer (P)", done_btn: "Mark as done",
    final_answer: "Final response", note: "Notes", method: "Method summary", exp_cb: "Exploration",
    base_exp: p => `27B: exploration (${p})`, base_post: "27B: post-answer", base_main: "27B: main path",
    review_title: n => `Human review (${n} traces)`,
    review_hint: "Progress is stored only in this browser. When finished, click “Export” and send the downloaded JSON file to the agent.",
    done_count: (a, b) => `Done ${a} / ${b}`, export: "Export results", reset: "Clear local progress",
    st_done: "Done", st_doing: "In progress", st_todo: "Not started", confirm_reset: "Clear all review progress stored in this browser?",
    about_title: "About", load_fail: "Failed to load: ",
    labels: {SU: "Setup", PL: "Plan", RC: "Recall", CP: "Compute", EX: "Explore", VF: "Verify", MB: "Monitor", CS: "Consolidate", AN: "Answer"},
  },
};
function getLang() {
  try { const v = localStorage.getItem(LANG_KEY); if (v === "zh" || v === "en") return v; } catch (e) {}
  return (navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";
}
let LANG = getLang();
const T = k => I18N[LANG][k];

const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));

function store() {
  try { return JSON.parse(localStorage.getItem(REVIEW_KEY)) || {items: {}}; } catch (e) { return {items: {}}; }
}
function save(s) { try { localStorage.setItem(REVIEW_KEY, JSON.stringify(s)); } catch (e) {} }

async function getIndex() {
  if (!INDEX) INDEX = await (await fetch("data/index.json?v=" + Date.now())).json();
  return INDEX;
}
async function getTrace(id) {
  if (!cache[id]) cache[id] = await (await fetch(`data/traces/${encodeURIComponent(id)}.json`)).json();
  return cache[id];
}
function math(el) {
  if (el && window.renderMathInElement) {
    renderMathInElement(el, {delimiters: [
      {left: "$$", right: "$$", display: true}, {left: "\\[", right: "\\]", display: true},
      {left: "\\(", right: "\\)", display: false}, {left: "$", right: "$", display: false}], throwOnError: false});
  }
}
// 每段属于哪个节点（按标注）
function paraMap(ann, n) {
  const out = Array(n).fill(null);
  if (!ann || !ann.nodes) return out;
  for (const nd of ann.nodes) for (let p = nd.p_start; p <= nd.p_end && p < n; p++)
    out[p] = {...nd, first: p === nd.p_start};
  return out;
}
function fmtPct(x) { return x == null ? "—" : (100 * x).toFixed(0) + "%"; }

function renderNav() {
  $("#nav-list").textContent = T("nav_list");
  $("#nav-review").textContent = T("nav_review");
  $("#nav-about").textContent = T("nav_about");
  $("#nav-blog").textContent = T("nav_blog");
  $("#lang").textContent = T("switch");
  document.documentElement.lang = LANG === "zh" ? "zh" : "en";
}

// ---------------- 列表 ----------------
async function viewList() {
  const idx = await getIndex();
  const app = $("#app");
  const annNames = idx.annotators;
  const desc = LANG === "en" ? (idx.description_en || idx.description) : idx.description;
  app.innerHTML = `
    <h1>${T("list_title")}</h1>
    <p class="muted small">${esc(desc)}${T("n_items")(idx.items.length)}</p>
    <div class="filters">
      <label>${T("tier")} <select id="f-tier"><option value="">${T("all")}</option><option>easy</option><option>medium</option><option>hard</option><option>zero</option></select></label>
      <label>${T("correct")} <select id="f-cor"><option value="">${T("all")}</option><option value="1">${T("right")}</option><option value="0">${T("wrong")}</option></select></label>
      <label>${T("length")} <select id="f-len"><option value="">${T("all")}</option><option>short</option><option>mid</option><option>long</option></select></label>
      <label>${T("set")} <select id="f-set"><option value="">${T("all")}</option><option value="api">${T("set_api")}</option><option value="human">${T("set_human")}</option><option value="pilot">${T("set_pilot")}</option><option value="corpus">${T("set_corpus")}</option></select></label>
      <label>${T("sort_by")} <select id="f-ann">${annNames.map(a => `<option>${esc(a)}</option>`).join("")}</select> ${T("sort_suffix")}</label>
    </div>
    <div class="tablewrap"><table><thead><tr><th>${T("col_traj")}</th><th>${T("tier")}</th><th>${T("correct")}</th><th>${T("col_tokens")}</th><th>${T("col_paras")}</th><th>${T("col_exp")}</th><th>${T("col_ann")}</th></tr></thead><tbody id="rows"></tbody></table></div>`;
  const draw = () => {
    const t = $("#f-tier").value, c = $("#f-cor").value, l = $("#f-len").value, s = $("#f-set").value, a = $("#f-ann").value;
    const rows = idx.items.filter(r => (!t || r.tier === t) && (!c || String(+r.is_correct) === c) && (!l || r.len_bin === l)
      && (!s || (s === "api" ? r.in_api : s === "human" ? r.in_human : (r.set || "pilot") === s)))
      .sort((x, y) => (y.fsf_tok?.[a] ?? -1) - (x.fsf_tok?.[a] ?? -1));
    $("#rows").innerHTML = rows.map(r => `<tr>
      <td><a href="#/t/${encodeURIComponent(r.traj_id)}">${esc(r.traj_id)}</a></td>
      <td>${esc(r.tier)}</td><td>${r.is_correct ? `<span class="chip ok">${T("ok")}</span>` : `<span class="chip bad">${T("bad")}</span>`}</td>
      <td>${r.n_tokens.toLocaleString()}</td><td>${r.n_paras}</td><td>${fmtPct(r.fsf_tok?.[a])}</td>
      <td>${Object.keys(r.fsf_tok || {}).map(k => `<span class="chip">${esc(k)}</span>`).join("")}</td></tr>`).join("");
  };
  app.querySelectorAll("select").forEach(e => e.onchange = draw);
  draw();
}

// ---------------- 单条轨迹（浏览 / 核对） ----------------
async function viewTrace(id, review) {
  const tr = await getTrace(id);
  const names = Object.keys(tr.annotations);
  let cur = review ? REVIEW_BASE : (names.includes(REVIEW_BASE) ? REVIEW_BASE : names[0]);
  const st = store();
  const n = tr.paragraphs.length;
  const isExp = x => x && (x.path === "A" || x.path === "D");   // 探索 = 明确放弃 A + 死胡同 D
  const baseMap = paraMap(tr.annotations[REVIEW_BASE], n);
  const base = baseMap.map(x => !!isExp(x));
  if (review && !st.items[id]) { st.items[id] = {abandoned: base.slice(), note: "", done: false}; save(st); }
  const app = $("#app");
  app.innerHTML = `
    <p class="small"><a href="${review ? "#/review" : "#/"}">${T("back")}</a></p>
    <h1>${esc(tr.traj_id)} ${review ? `<span class="chip warn">${T("review_mode")}</span>` : ""}</h1>
    <div class="meta">
      <span class="chip">${esc(tr.tier)}</span>
      <span class="chip ${tr.is_correct ? "ok" : "bad"}">${tr.is_correct ? T("answered_right") : T("answered_wrong")}</span>
      <span class="chip">${tr.n_tokens.toLocaleString()} token</span><span class="chip">${T("paras")(n)}</span>
      ${tr.meta_leak?.length ? `<span class="chip warn">${T("leak")}: ${esc(tr.meta_leak.join(", "))}</span>` : ""}
    </div>
    <div class="card"><b>${T("problem")}</b><div class="text">${esc(tr.problem)}</div>
      <p class="small muted">${T("gold")}: <span>${esc(tr.gold)}</span>　${T("pred")}: <span>${esc(tr.pred ?? T("none"))}</span></p></div>
    ${review ? `<div class="card small"><b>${T("how_title")}</b>${T("how")}</div>` : ""}
    <div class="toolbar">
      ${review ? "" : names.map(a => `<button data-a="${esc(a)}" class="${a === cur ? "on" : ""}">${esc(a)}</button>`).join("")}
      <span class="legend"><span><i class="sw" style="background:var(--main-bar)"></i>${T("lg_main")}</span><span><i class="sw" style="background:var(--aband-bar)"></i>${T("lg_exp")}</span><span><i class="sw" style="background:var(--post-bar)"></i>${T("lg_post")}</span></span>
      ${review ? `<button id="done" class="btn primary">${T("done_btn")}</button>` : ""}
    </div>
    <div id="paras"></div>
    <h2>${T("final_answer")}</h2><div class="card answer" id="answer">${esc(tr.answer_text)}</div>
    ${review ? `<h2>${T("note")}</h2><textarea id="note" rows="3" style="width:100%">${esc(st.items[id].note)}</textarea>` : ""}
    <h2>${T("method")}</h2><div class="card small">${names.map(a => `<div><b>${esc(a)}</b>: ${esc(tr.annotations[a].method || "—")}</div>`).join("")}</div>`;
  const draw = () => {
    const pm = paraMap(tr.annotations[cur], n);
    const s = store().items[id];
    const L = T("labels");
    $("#paras").innerHTML = tr.paragraphs.map((p, i) => {
      const nd = pm[i];
      const ab = review ? s.abandoned[i] : isExp(nd);
      const post = nd && nd.path === "P";
      const cls = review ? (ab ? "A" : post ? "P" : "M") : (nd ? (nd.path === "D" ? "A" : nd.path) : "");
      const tags = nd && nd.first ? `<div class="tags"><span class="chip">n${nd.node_id}</span><span class="chip">${esc(L[nd.label] || nd.label)}</span>
        <span class="chip">b=${nd.branch}</span>${nd.flags ? `<span class="chip warn">${esc(nd.flags)}</span>` : ""}</div>` : "";
      const bn = baseMap[i];
      const rv = review ? `<div class="review"><label><input type="checkbox" data-i="${i}" ${ab ? "checked" : ""}> ${T("exp_cb")}</label>
        <span class="muted">${base[i] ? T("base_exp")(bn.path) : bn && bn.path === "P" ? T("base_post") : T("base_main")}</span></div>` : "";
      return `<div class="para ${cls} ${nd && nd.first ? "nodestart" : ""} ${review && ab !== base[i] ? "changed" : ""}">
        <div class="pid">p${i}</div><div>${tags}<div class="text">${esc(p)}</div>${rv}</div></div>`;
    }).join("");
    math($("#paras"));
    if (review) $("#paras").querySelectorAll("input[type=checkbox]").forEach(cb => cb.onchange = () => {
      const s2 = store(); s2.items[id].abandoned[+cb.dataset.i] = cb.checked; save(s2); draw();
    });
  };
  app.querySelectorAll(".toolbar button[data-a]").forEach(b => b.onclick = () => {
    cur = b.dataset.a; app.querySelectorAll(".toolbar button[data-a]").forEach(x => x.classList.toggle("on", x === b)); draw();
  });
  if (review) {
    $("#note").oninput = e => { const s2 = store(); s2.items[id].note = e.target.value; save(s2); };
    $("#done").onclick = () => { const s2 = store(); s2.items[id].done = true; save(s2); location.hash = "#/review"; };
  }
  draw(); math($("#answer")); math(app.querySelector(".card"));
}

// ---------------- 核对列表 + 导出 ----------------
async function viewReview() {
  const idx = await getIndex();
  const items = idx.items.filter(r => r.in_human);
  const st = store();
  const nDone = items.filter(r => st.items[r.traj_id]?.done).length;
  $("#app").innerHTML = `
    <h1>${T("review_title")(items.length)}</h1>
    <p class="muted small">${T("review_hint")}</p>
    <div class="progress"><div style="width:${100 * nDone / Math.max(items.length, 1)}%"></div></div>
    <p>${T("done_count")(nDone, items.length)}　<button class="btn primary" id="export">${T("export")}</button>
       <button class="btn" id="reset">${T("reset")}</button></p>
    <div class="tablewrap"><table><thead><tr><th>${T("col_traj")}</th><th>${T("tier")}</th><th>${T("correct")}</th><th>${T("col_paras")}</th><th>${T("col_status")}</th></tr></thead><tbody>
    ${items.map(r => { const s = st.items[r.traj_id]; return `<tr><td><a href="#/review/${encodeURIComponent(r.traj_id)}">${esc(r.traj_id)}</a></td>
      <td>${esc(r.tier)}</td><td>${r.is_correct ? T("ok") : T("bad")}</td><td>${r.n_paras}</td>
      <td>${s?.done ? `<span class="chip ok">${T("st_done")}</span>` : s ? `<span class="chip warn">${T("st_doing")}</span>` : `<span class="chip">${T("st_todo")}</span>`}</td></tr>`; }).join("")}
    </tbody></table></div>`;
  $("#export").onclick = () => {
    const out = {schema: "human_review_v2", base_annotation: REVIEW_BASE, exported_at: new Date().toISOString(), items: store().items};
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], {type: "application/json"}));
    a.download = `human_review_${new Date().toISOString().slice(0, 10)}.json`; a.click();
  };
  $("#reset").onclick = () => { if (confirm(T("confirm_reset"))) { save({items: {}}); viewReview(); } };
}

async function viewAbout() {
  const idx = await getIndex();
  const html = LANG === "en" ? (idx.about_html_en || idx.about_html) : idx.about_html;
  $("#app").innerHTML = `<h1>${T("about_title")}</h1><div class="card">${html || ""}</div>`;
}

async function route() {
  renderNav();
  const h = location.hash.replace(/^#/, "") || "/";
  try {
    if (h.startsWith("/t/")) await viewTrace(decodeURIComponent(h.slice(3)), false);
    else if (h.startsWith("/review/")) await viewTrace(decodeURIComponent(h.slice(8)), true);
    else if (h === "/review") await viewReview();
    else if (h === "/about") await viewAbout();
    else await viewList();
  } catch (e) { $("#app").innerHTML = `<p class="muted">${T("load_fail")}${esc(e.message)}</p>`; }
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);
window.addEventListener("DOMContentLoaded", () => {
  $("#lang").onclick = () => {
    LANG = LANG === "zh" ? "en" : "zh";
    try { localStorage.setItem(LANG_KEY, LANG); } catch (e) {}
    route();
  };
  route();
});
