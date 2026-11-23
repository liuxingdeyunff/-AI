import {studio} from "./studio.js";
import katex from "katex";
import "katex/dist/katex.min.css";
import "./style.css";
import { surface, graph } from "./plot.js";
import {
  createIcons,
  BookOpen,
  LayoutDashboard,
  Network,
  ClipboardList,
  Library,
  History,
  ChartNoAxesColumnIncreasing,
  ArrowRight,
  ChevronRight,
  GraduationCap,
  Target,
  Activity,
  Layers,
  CalendarDays,
  CircleHelp,
  Menu,
  Sigma,
  BookMarked,
  PencilRuler,
  Check,
  Upload,
  CornerDownRight,
  ListChecks,
} from "lucide/dist/esm/lucide/src/lucide.js";
const icons = {
  BookOpen,
  LayoutDashboard,
  Network,
  ClipboardList,
  Library,
  History,
  ChartNoAxesColumnIncreasing,
  ArrowRight,
  ChevronRight,
  GraduationCap,
  Target,
  Activity,
  Layers,
  CalendarDays,
  CircleHelp,
  Menu,
  Sigma,
  BookMarked,
  PencilRuler,
  Check,
  Upload,
  CornerDownRight,
  ListChecks,
};
export const ico = (n) => `<i data-lucide="${n}"></i>`;
export const esc = (v) =>
  String(v).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
export const math = (v) =>
  katex.renderToString(v, { throwOnError: false, output: "htmlAndMathml" });
export async function api(path, body) {
  const r = await fetch(
    "/api/" + path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
  );
  const d = await r.json();
  if (!r.ok) throw Error(d.error || "请求失败");
  return d;
}
let units = [],
  state = { attempts: [], reviews: [], scores: {} };
const nav = [
  ["home", "学习总览", "LayoutDashboard"],
  ["courses", "课程单元", "BookOpen"],
  ["map", "知识图谱", "Network"],
  ["quiz", "诊断测试", "ClipboardList"],
  ["review", "错题与复习", "History"],
  ["library", "资料库", "Library"],
  ["progress", "个人进度", "ChartNoAxesColumnIncreasing"],
];
const groups = ["极限与连续", "导数与微分", "中值与展开"];
const glyph = ["lim", "ƒ ′", "Σ"];
const counts = () => [
  units.length,
  state.attempts.length,
  state.reviews.filter((r) => r.ready).length,
];
const link = (href, label, cls = "") =>
  `<a class="${cls}" href="#${href}">${label}</a>`;
const teaching=studio({api,esc,math,link});
let generated=[];
const inner = (id) => units[id];
function shell(page, content) {
  const section =
    { unit: "courses", practice: "courses", redo: "review", coach:"review", guide:"library" }[page] ||
    page ||
    "home";
  document.querySelector("#app").innerHTML =
    `<aside><a href="#home" class="brand"><b>∑</b><strong>知序 <em>AI</em></strong></a><small class="subbrand">高等数学私人导师</small><p class="navhead">学习空间</p><nav>${nav.map(([id, t, i]) => link(id, ico(i) + t, section === id ? "active" : "")).join("")}</nav><div class="profile"><span>知</span><div>本地学习者<small><i></i> ${modelName?(modelName.startsWith("云端")?"云端模型已启用":"本机模型已启用"):"离线基础模式"}</small></div></div></aside><main><header><button aria-label="切换导航" id="menu">${ico("Menu")}</button>学习空间 <b>/</b> <strong>${nav.find((n) => n[0] === section)?.[1] || "学习单元"}</strong><time>${ico("CalendarDays")} ${new Date().toLocaleDateString("zh-CN", { month: "long", day: "numeric", weekday: "long" })}</time></header><article>${content}</article></main>`;
  document.querySelector("#menu").onclick = () =>
    document.body.classList.toggle("open");
  createIcons({ icons });
}
const heading = (t, s) => `<h1>${t}</h1><p class="lead">${s}</p>`;
function startLink() {
  const round = diagnosticRound();
  const label =
    round.size === 10 ? "查看诊断报告" : round.size ? "继续诊断" : "开始诊断";
  return link("quiz", label + " " + ico("ArrowRight"), "button light");
}
function tile(u) {
  return link(
    "unit/" + u.id,
    `<span class="symbol g${groups.indexOf(u.group)}">${glyph[groups.indexOf(u.group)]}</span><div><strong>${u.name}</strong><small>${u.summary}</small></div>${ico("ChevronRight")}`,
    "unitrow",
  );
}
function today() {
  const due = state.reviews.filter(r=>r.ready)
  if(due.length) return {title:"今天先复习"+inner(due[0].unit).name,why:"有 "+due.length+" 道错题到期。先检验上次的薄弱点，再开始新题。",action:link("redo/"+due[0].q,"开始到期复习 "+ico("ArrowRight"),"button light")}
  const round=diagnosticRound()
  if(round.size===10){const weak=[...units].sort((a,b)=>(state.scores[a.id]??0)-(state.scores[b.id]??0))[0];return {title:"今天巩固"+weak.name,why:"根据不同题目的最近作答，这个单元值得优先练习。",action:link("practice/"+weak.id,"开始针对性练习 "+ico("ArrowRight"),"button light")}}
  return {title:round.size?"继续高数能力诊断":"高等数学能力诊断",why:round.size?"已完成 "+round.size+" / 10 道题，继续补全今天的学习建议。":"先用 10 道题定位薄弱环节，再安排今天的学习。",action:startLink()}
}
function home() { const plan=today();
  return (
    heading("学习总览", "从一次诊断开始，找到适合你的高数学习路径。") +
    `<section class="hero"><canvas id="surface" aria-label="二元函数的曲面网格图"></canvas><div><label>${ico("GraduationCap")} 高等数学 · 第一学期</label><h2>${plan.title}</h2><p>${plan.why}</p>${plan.action}</div></section><div class="metrics">${["课程单元", "已答题次", "待巩固错题"].map((t, i) => `<section><span class="metricicon g${i}">${ico(["Layers", "ListChecks", "Target"][i])}</span><div><small>${t}</small><strong>${counts()[i]} <em>${["个", "次", "道"][i]}</em></strong></div></section>`).join("")}</div><div class="columns"><section class="panel"><div class="sect"><h2>推荐学习单元</h2>${link("courses", "全部课程 " + ico("ChevronRight"))}</div>${(state.reviews.length ? [...new Set([...inner(state.reviews[0].unit).prereq, state.reviews[0].unit, 8, 0])].slice(0, 3) : [0, 3, 8]).map((i) => tile(inner(i))).join("")}</section><section class="panel route"><div class="sect"><h2>学习路径</h2>${ico("Network")}</div>${[
      ["能力诊断", "识别当前掌握与薄弱点", "quiz"],
      ["针对性学习", "梳理概念，尝试递进提示", "courses"],
      ["复习巩固", "重做错题，记录学习证据", "review"],
    ]
      .map(([t, s, l], i) =>
        link(
          l,
          `<b>0${i + 1}</b><div><strong>${t}</strong><small>${s}</small></div>`,
          "step",
        ),
      )
      .join("")}</section></div>`
  );
}
function courses() {
  return (
    heading("课程单元", "第一学期期中 · 10 个内置原创知识单元") +
    groups
      .map(
        (g) =>
          `<section class="panel"><h2>${g}</h2>${units
            .filter((u) => u.group === g)
            .map(tile)
            .join("")}</section>`,
      )
      .join("")
  );
}
function unit(id) {
  const u = inner(id);
  if (!u) throw Error("找不到课程");
  return (
    heading(u.name, u.summary) +
    `<section class="panel lesson"><small>${u.source} · 高数讲义 ` +
    (u.id + 1) +
    `</small><div class="formula">${math(u.formula)}</div>${materialLinks(u.id)}<h2>推导与理解</h2><p>${u.note}</p><h2>例题推演</h2><div class="formula">${math(u.worked)}</div><p>${u.explanation}</p><h2>典型误区</h2><p>${u.trap}</p><p>建议先修　${u.prereq.map((i) => link("unit/" + i, inner(i).name)).join(" · ") || "起点单元"}</p>${link("practice/" + id, "开始单元练习 " + ico("ArrowRight"), "button")}</section>` +
    ([8, 9].includes(u.id)
      ? `<section class="panel"><h2>局部逼近实验</h2><label>正弦函数（蓝）与泰勒多项式（橙） <select id="degree"><option>1</option><option selected>3</option><option>5</option></select> 阶</label><canvas id="curve" width="650" height="200"></canvas></section>`
      : "")
  );
}
async function render() {
  document.body.classList.remove("open");
  const [page = "home", id] = location.hash.slice(1).split("/");
  try {
    let content;
    if (page === "home" || !page) content = home();
    else if (page === "courses") content = courses();
    else if (page === "unit") content = unit(Number(id));
    else content = await extra(page, id);
    shell(page, content);
    if (document.querySelector("#surface"))
      surface(document.querySelector("#surface"));
    if (document.querySelector("#curve")) {
      const draw = () =>
        graph(
          document.querySelector("#curve"),
          Number(document.querySelector("#degree").value),
        );
      draw();
      document.querySelector("#degree").onchange = draw;
    }
    bind(page, id);
    teaching.bind({page,id,docs,guides:generated,model:modelName,refresh:init,updateState:async()=>{state=await api('state');await render()}});
  } catch (e) {
    shell(
      page,
      heading("暂时无法打开", esc(e.message)) +
        '<button onclick="location.reload()">重新加载</button>',
    );
  }
}
let repeatQuiz = false,
  questions = [],
  current = null,
  feedback = null,
  hint = 0,
  activeRoute = "";
const findQ = (k) => questions.find((q) => q.id === k);
const score = (u) =>
  state.scores[u.id] === undefined
    ? "尚无作答证据"
    : `估计掌握度 ${state.scores[u.id]}%`;
function summary() {
  const weak = units.filter((u) => (state.scores[u.id] ?? 100) < 60);
  return `<section class="panel"><h2>诊断报告</h2><p>${weak.length ? "优先巩固　" + weak.map((u) => link("unit/" + u.id, u.name)).join("、") : "当前各单元均已获得正确作答证据。"}</p><p>已完成 10 个单元的诊断。掌握度按每道不同题目的最近一次结果计算。</p>${link("review", "查看错题与复习", "button")} ${link("map", "查看知识图谱", "button muted")} <button id="repeat" class="muted">重新诊断</button></section>`;
}
function diagnosticRound() {
  const seen = new Set();
  for (const r of state.attempts) {
    if (r.mode !== "quiz") continue;
    if (seen.size === 10) seen.clear();
    seen.add(r.q);
  }
  return seen;
}
function exercise(mode, id) {
  const done = diagnosticRound();
  const route = mode + "/" + id;
  if (route !== activeRoute) {
    feedback = null;
    hint = 0;
    current = null;
    activeRoute = route;
  }
  if (!current) {
    const completed = done.size === 10 && !repeatQuiz;
    if (done.size === 10 && repeatQuiz) done.clear();
    if (mode === "quiz") {
      current = completed
        ? null
        : suggestedDiagnostic(id).find((q) => !done.has(q.id));
      repeatQuiz = false;
    } else if (mode === "redo") current = findQ(id);
    else {
      const qs = questions.filter(
        (q) => q.unit === Number(id) && !q.diagnostic,
      );
      current =
        qs.find((q) => !state.attempts.some((r) => r.q === q.id)) ||
        qs.slice().sort((a, b) => last(a) - last(b))[0];
    }
  }
  if (!current)
    return heading("能力诊断", "逐单元识别需要巩固的知识。") + summary();
  const q = current,
    u = inner(q.unit),
    doc = docs.find((d) => d.id === id),
    sourceIndex = doc?.sections.findIndex((s) => s.matches[q.unit]);
  const number = feedback ? done.size : (done.size % 10) + 1;
  return (
    heading(
      mode === "quiz" ? "能力诊断" : mode === "redo" ? "错题重做" : "单元练习",
      u.name + " · " + q.source,
    ) +
    `<section class="panel lesson"><small>${mode === "quiz" ? "诊断 " + number + " / 10" : q.level}</small>${sourceIndex >= 0 ? "<p>对应原文　" + link("library/" + id + "~" + sourceIndex, esc(doc.name) + " · " + esc(doc.sections[sourceIndex].anchor)) + "</p>" : ""}<h2>${q.text}</h2>${q.tex ? `<div class="formula">${math(q.tex)}</div>` : ""}${feedback ? `<div class="feedback"><h3>${feedback.ok ? "回答正确" : "这一步需要再检查"}</h3><details><summary>核对参考步骤与答案</summary><p>${feedback.reason}</p><p>参考答案　${esc(feedback.solution)}</p></details>${link("coach/"+feedback.attempt,"复盘思路与针对性变式","button muted")}${feedback.ok ? "" : `<strong>建议排查 · ${feedback.error}<small>仅据最终结果推测，可通过方法追问进一步核对。</small></strong><p>下一步　${link("unit/" + feedback.prereq, "复习「" + inner(feedback.prereq).name + "」")}</p>`}</div><button id="next">${mode === "redo" ? "返回复习计划" : mode === "quiz" && number === 10 ? "查看诊断报告" : "继续下一题"}</button>` : `<form id="response"><div class="answer">${q.choices.length ? q.choices.map((v, i) => `<label class="opt"><input type="radio" name="answer" value="${i}" required>${v}</label>`).join("") : '<label>你的答案 <input name="answer" required maxlength="120" autocomplete="off" placeholder="如 -1/6 或 x^2+2*x"></label>'}</div><label class="steps">我的推导步骤（选填）<textarea name="steps" maxlength="800" rows="2" placeholder="写下用到的公式、代换或卡住的地方"></textarea></label><button>提交答案</button><button type="button" class="muted" id="hint" ${hint === 2 ? "disabled" : ""}>提示 ${hint}/2</button><div id="hints" aria-live="polite"></div><p role="alert" id="error"></p></form>`}</section>`
  );
}
function last(q) {
  return state.attempts.filter((r) => r.q === q.id).at(-1)?.id || 0;
}
function graphOverview() {
  const points = [
    [86, 62],
    [265, 38],
    [265, 150],
    [440, 150],
    [616, 217],
    [616, 137],
    [615, 60],
    [790, 60],
    [438, 38],
    [790, 215],
  ];
  return `<section class="panel"><h2>先修关系</h2><div class="dagwrap"><svg class="dag" viewBox="0 0 884 252" role="group" aria-label="先修关系图"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#8996bc"/></marker></defs>${units
    .flatMap((u) =>
      u.prereq.map((k) => {
        const [x, y] = points[k],
          [xx, yy] = points[u.id];
        const vertical = Math.abs(y - yy) > 55 && Math.abs(x - xx) < 360;
        const dir = Math.sign(yy - y);
        const sx = vertical ? x : x + 62,
          sy = vertical ? y + dir * 18 : y,
          ex = vertical ? xx : xx - 63,
          ey = vertical ? yy - dir * 18 : yy;
        return `<path d="M${sx} ${sy} Q${(sx + ex) / 2} ${vertical ? sy + (ey - sy) * 0.82 : sy - 12} ${ex} ${ey}" fill="none" stroke="#aeb9d5" marker-end="url(#arrow)"/>`;
      }),
    )
    .join("")}${units
    .map((u) => {
      const [x, y] = points[u.id];
      return `<a href="#unit/${u.id}" aria-label="${u.name}，${score(u)}"><rect x="${x - 61}" y="${y - 17}" width="122" height="34" rx="9" fill="${state.scores[u.id] === undefined ? "#f0f2fc" : state.scores[u.id] < 60 ? "#faeadb" : "#e0f2e8"}"/><text x="${x}" y="${y + 5}" text-anchor="middle" font-size="13" fill="#263455">${u.name}</text></a>`;
    })
    .join(
      "",
    )}</svg></div><small>箭头从先修单元指向后续单元。点击节点可查看讲义。</small></section>`;
}
function suggestedDiagnostic(id) {
  const doc = docs.find((d) => d.id === id);
  const weights = new Map();
  if (doc)
    for (const section of doc.sections)
      for (const key of Object.keys(section.matches))
        weights.set(+key, (weights.get(+key) || 0) + 1);
  return questions
    .filter((q) => q.diagnostic)
    .sort(
      (a, b) =>
        (weights.get(b.unit) || 0) - (weights.get(a.unit) || 0) ||
        (state.scores[a.unit] ?? -1) - (state.scores[b.unit] ?? -1) ||
        a.unit - b.unit,
    );
}

function knowledge() {
  return (
    heading(
      "知识图谱",
      "先修连线表示建议学习顺序。点击知识点可以查看讲义与练习。",
    ) +
    graphOverview() +
    units
      .map(
        (u) =>
          `<section class="panel"><small>${u.group} · ${u.source}</small><h2>${link("unit/" + u.id, u.name)}</h2><p>${score(u)}　·　建议先修　${u.prereq.map((i) => link("unit/" + i, inner(i).name)).join(" → ") || "起点"}</p><p>${state.reviews
            .filter((r) => r.unit === u.id)
            .map((r) => link("redo/" + r.q, "关联错题 " + r.q))
            .join("　")}</p>${materialLinks(u.id)}</section>`,
      )
      .join("")
  );
}
function reviews() {
  return (
    heading("错题与复习", "答错的题当天复习，重做正确后间隔 3 天再次巩固。") +
    `<section class="panel"><h2>复习计划</h2>${state.reviews.map((r) => `<div class="unitrow"><span class="symbol g2">↻</span><div><strong>${inner(r.unit).name} · ${r.error}</strong><small>${r.ready ? "到期可复习" : "下次巩固"} · ${r.due} · ${r.q}</small>${link("redo/" + r.q, "重做这道题")}　${link("unit/" + (inner(r.unit).prereq[0] ?? r.unit), "回看前置知识")}</div></div>`).join("") || "<p>还没有错题。完成诊断后，需要巩固的题会出现在这里。</p>"}</section>`
  );
}
function progress() {
  return (
    heading(
      "个人进度",
      "按不同题目的最近一次作答估计掌握度，重复答同一题只更新该题证据。",
    ) +
    `<section class="panel"><h2>单元掌握情况</h2>${units.map((u) => `<div class="unitrow"><strong>${u.name}</strong><progress max="100" value="${state.scores[u.id] || 0}"></progress><small>${score(u)}</small></div>`).join("")}</section><section class="panel"><h2>学习记录</h2>${
      state.attempts
        .slice(-40)
        .reverse()
        .map(
          (r) =>
            `<p>${r.day} · ${inner(findQ(r.q).unit).name} · ${{ quiz: "诊断", practice: "练习", review: "复习" }[r.mode]} · ${r.ok ? "正确" : "需巩固"}　${link("coach/"+r.id,"查看作答证据")}</p>`,
        )
        .join("") || "完成第一题后即可查看记录。"
    }</section>` +
    backupUI()
  );
}
async function extra(page, id) {
  if (["practice", "quiz", "redo"].includes(page)) return exercise(page, id);
  if(page==="guide")return teaching.guidePage(id,generated,docs,modelName)
  if(page==="coach")return teaching.coachPage(id,state,questions,units,modelName)
  if (page === "map") return teaching.studyGraph(generated)+knowledge();
  if (page === "review") return reviews();
  if (page === "progress") return progress();
  return library(id);
}
function bind(page, id) {
  if (!["quiz", "practice", "redo"].includes(page)) activeRoute = "";
  const form = document.querySelector("#response");
  if (form) {
    const h = document.querySelector("#hint");
    h.onclick = () => {
      hint = Math.min(2, hint + 1);
      h.textContent = "提示 " + hint + "/2";
      h.disabled = hint === 2;
      document.querySelector("#hints").textContent = current.hints
        .slice(0, hint)
        .join("　");
    };
    const requestId = crypto.randomUUID();
    form.onsubmit = async (e) => {
      e.preventDefault();
      const btn = form.querySelector("button");
      btn.disabled = true;
      try {
        feedback = await api("answer", {
          request_id: requestId,steps:new FormData(form).get("steps"),hints:hint,
          q: current.id,
          answer: new FormData(form).get("answer"),
          mode: page === "redo" ? "review" : page,
        });
        state = await api("state");
        await render();
      } catch (e) {
        document.querySelector("#error").textContent = e.message;
        btn.disabled = false;
      }
    };
  }
  const again = document.querySelector("#repeat");
  if (again)
    again.onclick = () => {
      repeatQuiz = true;
      render();
    };
  const next = document.querySelector("#next");
  if (next)
    next.onclick = () => {
      current = null;
      feedback = null;
      hint = 0;
      if (page === "redo") location.hash = "review";
      else render();
    };
  bindMaterials(page, id);
}
let docs = [],
  modelName = "";
function materialLinks(id) {
  return docs
    .flatMap((d) =>
      d.sections
        .map((s, i) =>
          s.matches[id]
            ? link(
                "library/" + d.id + "~" + i,
                esc(d.name) + " · " + esc(s.anchor),
              )
            : null,
        )
        .filter(Boolean),
    )
    .join("　");
}
function readingTask(doc, section, index, ids) {
  if (!ids.length) return "";
  const uid = ids[0],
    word = section.matches[uid];
  const quote = cite(section.text, word);
  const masked = quote.replaceAll(word, "〔　　〕");
  return `<section class="panel"><small>由资料生成 · ${esc(doc.name)} · ${esc(section.anchor)}</small>
    <h2>原文回忆</h2><p>补全引用中的术语，再解释它在这段材料中的作用。</p>
    <blockquote>${esc(masked)}</blockquote><label>你的解释（自评）<textarea rows="2" placeholder="用自己的话复述…"></textarea></label>
    <details><summary>提示 1 · 知识范围</summary>${inner(uid).group}</details>
    <details><summary>提示 2 · 回到概念</summary>${inner(uid).summary}</details>
    <details><summary>对照来源，自行核对</summary><p>原文术语：${esc(word)}</p><blockquote>${esc(quote)}</blockquote><small>开放解释需要人工或模型评估。此处仅供自评。</small></details>
    ${link("practice/" + uid, "检验相关数学技能 " + ico("ArrowRight"), "button muted")}</section>`;
}

function library(ref) {
  if (ref) {
    const [key, index = "0"] = ref.split("~"),
      d = docs.find((d) => d.id === key),
      i = Number(index),
      s = d?.sections[i];
    if (!s) throw Error("找不到此资料片段");
    const ids = Object.keys(s.matches)
      .map(Number)
      .sort((a, b) => (state.scores[a] ?? -1) - (state.scores[b] ?? -1));
    return (
      heading(esc(d.name), "原文与离线知识索引") +
      link("quiz/" + d.id, "按此资料优先诊断", "button docquiz") + teaching.analysis(d,i,generated,modelName)+
      `<section class="panel"><label>原文位置 <select id="anchor">${d.sections.map((v, j) => `<option value="${j}" ${i === j ? "selected" : ""}>${esc(v.anchor)}</option>`).join("")}</select></label><pre>${esc(s.text)}</pre>${d.empty.length ? `<p>第 ${d.empty.join("、")} 页无可提取文本，OCR 不可用，请补充文字版。</p>` : ""}</section><section class="panel"><h2>本节学习单元</h2><p>按原文术语关联，并优先列出缺少证据或掌握度较低的单元。</p>${ids.map((n) => `<div class="unitrow"><div><small>原文命中「${esc(s.matches[n])}」 · ${esc(s.anchor)}</small><strong>${inner(n).name}</strong><p>${esc(cite(s.text, s.matches[n]))}</p>${link("unit/" + n, "学习讲义")}　${link("practice/" + n, "练习 · 内置原创示例")}</div></div>`).join("") || "未识别到内置术语，可以阅读原文或自行选择课程。"}</section>${readingTask(d, s, i, ids)}<section class="panel"><h2>向模型追问</h2>${modelName ? `<form id="ask"><label>授权片段（可编辑）<textarea name="excerpt" maxlength="1000" required>${esc(s.text.slice(0, 500))}</textarea></label><label>问题 <input name="question" maxlength="400" required></label><label><input name="consent" type="checkbox" required> 同意将以上片段和问题发送到${esc(modelName)}${modelName.startsWith("云端")?"（api.deepseek.com，服务商可能计费）":"（本机）"}</label><button>获取提示</button></form><pre id="model-result"></pre>` : "未启用模型。在资料库选择模型后可针对选定片段提问。"}</section>`
    );
  }
  return (
    heading("资料库", "导入自己的高数材料，从原文回到知识点。") + teaching.settings(modelName)+
    `<section class="panel"><h2>导入学习资料</h2><p>支持文本 PDF、UTF-8 Markdown 与 TXT，每个文件最多 4 MB。</p><form id="upload"><input type="file" required name="file" accept=".pdf,.md,.txt"><button>导入资料</button><p role="status" class="status"></p></form></section><section class="panel"><h2>我的资料</h2>${docs.map((d) => link("library/" + d.id, `<div><strong>${esc(d.name)}</strong><small>由资料生成 · ${d.sections.length} 个原文片段</small></div>${ico("ChevronRight")}`, "unitrow")).join("") || "尚未导入资料。可先使用下方原创讲义。"}</section><section class="panel"><h2>高数期中讲义 · 内置原创示例</h2>${units.map(tile).join("")}</section>`
  );
}
function cite(text, word) {
  const i = text.toLowerCase().indexOf(word.toLowerCase());
  return text.slice(Math.max(0, i - 25), i + word.length + 60);
}
function backupUI() {
  return `<section class="panel"><h2>学习进度备份</h2><p>含诊断、练习与复习记录。资料原件请单独保管。</p><button id="export">导出 JSON</button><form id="restore"><input name="file" required type="file" accept=".json"><label><input type="checkbox" required> 用备份替换当前学习记录</label><button>恢复进度</button><p role="status" class="status"></p></form></section>`;
}
function bindMaterials(page, ref) {
  const anchor = document.querySelector("#anchor");
  if (anchor)
    anchor.onchange = () =>
      (location.hash = "library/" + ref.split("~")[0] + "~" + anchor.value);
  const exp = document.querySelector("#export");
  if (exp)
    exp.onclick = () => {
      const url = URL.createObjectURL(
        new Blob([JSON.stringify({ version: 1, attempts: state.attempts })], {
          type: "application/json",
        }),
      );
      const a = document.createElement("a");
      a.href = url;
      a.download = "知序-学习进度.json";
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    };
  for (const id of ["upload", "restore", "ask"]) {
    const f = document.getElementById(id);
    if (!f) continue;
    f.onsubmit = async (e) => {
      e.preventDefault();
      const btn = f.querySelector("button"),
        msg =
          f.querySelector(".status") || document.querySelector("#model-result");
      btn.disabled = true;
      msg.textContent = "正在处理…";
      try {
        const fields = new FormData(f),
          file = fields.get("file");
        if (id === "ask") {
          const r = await api("ask", {
            excerpt: fields.get("excerpt"),
            question: fields.get("question"),
            consent: fields.has("consent"),destination:modelName,cloud_ok:modelName.startsWith("云端")&&fields.has("consent"),
          });
          msg.textContent = r.answer;
        }
        if (id === "upload") {
          if (file.size > 4000000) throw Error("单个文件限 4 MB");
          const content = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = () => reject(Error("文件读取失败"));
            reader.readAsDataURL(file);
          });
          const d = await api("upload", { name: file.name, content });
          docs = await api("documents");
          location.hash = "library/" + d.id;
        }
        if (id === "restore") {
          if (file.size > 8000000) throw Error("备份文件超过限制");
          const result = await api("restore", JSON.parse(await file.text()));
          state = await api("state");
          await render();
          document.querySelector("#restore .status").textContent =
            "已恢复 " + result.count + " 条记录";
        }
      } catch (e) {
        msg.textContent = e.message;
      } finally {
        btn.disabled = false;
      }
    };
  }
}
async function init() {
  try {
    [units, state, questions, docs, modelName,generated] = await Promise.all([
      api("units"),
      api("state"),
      api("questions"),
      api("documents"),
      api("model"),api("guides"),
    ]);
    await render();
  } catch (e) {
    shell(
      "home",
      heading("连接失败", "请确认本地服务正在运行。") +
        '<button onclick="location.reload()">重试</button>',
    );
  }
}
window.addEventListener("hashchange", () => {
  window.scrollTo(0, 0);
  render();
});
init();
