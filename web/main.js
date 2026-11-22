import katex from 'katex'
import 'katex/dist/katex.min.css'
import './style.css'
import {surface,graph} from './plot.js'
import {createIcons, BookOpen, LayoutDashboard, Network, ClipboardList, Library, History, ChartNoAxesColumnIncreasing, ArrowRight, ChevronRight, GraduationCap, Target, Activity, Layers, CalendarDays, CircleHelp, Menu, Sigma, BookMarked, PencilRuler, Check, Upload, CornerDownRight, ListChecks} from 'lucide/dist/esm/lucide/src/lucide.js'
const icons={BookOpen,LayoutDashboard,Network,ClipboardList,Library,History,ChartNoAxesColumnIncreasing,ArrowRight,ChevronRight,GraduationCap,Target,Activity,Layers,CalendarDays,CircleHelp,Menu,Sigma,BookMarked,PencilRuler,Check,Upload,CornerDownRight,ListChecks}
export const ico=n=>`<i data-lucide="${n}"></i>`
export const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
export const math=v=>katex.renderToString(v,{throwOnError:false,output:'htmlAndMathml'})
export async function api(path,body) {const r=await fetch('/api/'+path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok)throw Error(d.error||'请求失败');return d}
let units=[],state={attempts:[],reviews:[],scores:{}}
const nav=[['home','学习总览','LayoutDashboard'],['courses','课程单元','BookOpen'],['map','知识图谱','Network'],['quiz','诊断测试','ClipboardList'],['review','错题与复习','History'],['library','资料库','Library'],['progress','个人进度','ChartNoAxesColumnIncreasing']]
const groups=['极限与连续','导数与微分','中值与展开']
const glyph=['lim','ƒ ′','Σ']
const counts=()=>[units.length,state.attempts.length,state.reviews.filter(r=>r.ready).length]
const link=(href,label,cls='')=>`<a class="${cls}" href="#${href}">${label}</a>`
const inner=id=>units[id]
function shell(page,content) {
 const section=page==='unit'?'courses':page
 document.querySelector('#app').innerHTML=`<aside><a href="#home" class="brand"><b>∑</b><strong>知序 <em>AI</em></strong></a><small class="subbrand">高等数学私人导师</small><p class="navhead">学习空间</p><nav>${nav.map(([id,t,i])=>link(id,ico(i)+t,section===id?'active':'')).join('')}</nav><div class="profile"><span>知</span><div>本地学习者<small><i></i> 离线学习空间</small></div></div></aside><main><header><button aria-label="切换导航" id="menu">${ico('Menu')}</button>学习空间 <b>/</b> <strong>${nav.find(n=>n[0]===section)?.[1]||'学习单元'}</strong><time>${ico('CalendarDays')} ${new Date().toLocaleDateString('zh-CN',{month:'long',day:'numeric',weekday:'long'})}</time></header><article>${content}</article></main>`
 document.querySelector('#menu').onclick=()=>document.body.classList.toggle('open')
 createIcons({icons})
}
const heading=(t,s)=>`<h1>${t}</h1><p class="lead">${s}</p>`
const startLink=()=>link('quiz','开始诊断 '+ico('ArrowRight'),'button light')
function tile(u){return link('unit/'+u.id,`<span class="symbol g${groups.indexOf(u.group)}">${glyph[groups.indexOf(u.group)]}</span><div><strong>${u.name}</strong><small>${u.summary}</small></div>${ico('ChevronRight')}`,'unitrow')}
function home(){return heading('学习总览','从一次诊断开始，找到适合你的高数学习路径。')+`<section class="hero"><canvas id="surface" aria-label="二元函数的曲面网格图"></canvas><div><label>${ico('GraduationCap')} 高等数学 · 第一学期</label><h2>高等数学能力诊断</h2><p>从极限到泰勒展开，定位薄弱环节。<br>用 10 道题，生成你的专属学习建议。</p>${startLink()}</div></section><div class="metrics">${['课程单元','已答题次','待巩固错题'].map((t,i)=>`<section><span class="metricicon g${i}">${ico(['Layers','ListChecks','Target'][i])}</span><div><small>${t}</small><strong>${counts()[i]} <em>${['个','次','道'][i]}</em></strong></div></section>`).join('')}</div><div class="columns"><section class="panel"><div class="sect"><h2>推荐学习单元</h2>${link('courses','全部课程 '+ico('ChevronRight'))}</div>${(state.reviews.length?[...new Set([...(inner(state.reviews[0].unit).prereq),state.reviews[0].unit,8,0])].slice(0,3):[0,3,8]).map(i=>tile(inner(i))).join('')}</section><section class="panel route"><div class="sect"><h2>学习路径</h2>${ico('Network')}</div>${[['能力诊断','识别当前掌握与薄弱点','quiz'],['针对性学习','梳理概念，尝试递进提示','courses'],['复习巩固','重做错题，记录学习证据','review']].map(([t,s,l],i)=>link(l,`<b>0${i+1}</b><div><strong>${t}</strong><small>${s}</small></div>`,'step')).join('')}</section></div>`}
function courses(){return heading('课程单元','第一学期期中 · 10 个内置原创知识单元')+groups.map(g=>`<section class="panel"><h2>${g}</h2>${units.filter(u=>u.group===g).map(tile).join('')}</section>`).join('')}
function unit(id){const u=inner(id);if(!u)throw Error('找不到课程')
return heading(u.name,u.summary)+`<section class="panel lesson"><small>${u.source} · 高数讲义 `+(u.id+1)+`</small><div class="formula">${math(u.formula)}</div><h2>推导与理解</h2><p>${u.note}</p><h2>典型误区</h2><p>${u.trap}</p><p>建议先修　${u.prereq.map(i=>link('unit/'+i,inner(i).name)).join(' · ')||'起点单元'}</p>${link('practice/'+id,'开始单元练习 '+ico('ArrowRight'),'button')}</section>`+([8,9].includes(u.id)?`<section class="panel"><h2>局部逼近实验</h2><label>正弦函数（蓝）与泰勒多项式（橙） <select id="degree"><option>1</option><option selected>3</option><option>5</option></select> 阶</label><canvas id="curve" width="650" height="200"></canvas></section>`:'')}
async function render(){document.body.classList.remove('open')
 const [page='home',id]=location.hash.slice(1).split('/')
 try {
 let content
 if(page==='home'||!page)content=home()
 else if(page==='courses')content=courses()
 else if(page==='unit')content=unit(Number(id))
 else content=await extra(page,id)
 shell(page,content)
 if(document.querySelector('#surface'))surface(document.querySelector('#surface'))
 if(document.querySelector('#curve')){const draw=()=>graph(document.querySelector('#curve'),Number(document.querySelector('#degree').value));draw();document.querySelector('#degree').onchange=draw}
 bind(page,id)
 }catch(e){shell(page,heading('暂时无法打开',esc(e.message))+'<button onclick="location.reload()">重新加载</button>')}
}
let questions=[], current=null, feedback=null, hint=0, activeRoute=''
const findQ=k=>questions.find(q=>q.id===k)
const score=u=>state.scores[u.id]===undefined?'尚无作答证据':`估计掌握度 ${state.scores[u.id]}%`
function summary(){return `<section class="panel"><h2>诊断报告</h2><p>已完成 10 个单元的诊断。掌握度按每道不同题目的最近一次结果计算。</p>${link('review','查看错题与复习','button')} ${link('map','查看知识图谱','button muted')}</section>`}
function exercise(mode,id){
 const route=mode+'/'+id
 if(route!==activeRoute){feedback=null;hint=0;current=null;activeRoute=route}
 if(!current){
 const done=new Set(state.attempts.filter(r=>r.mode==='quiz').map(r=>r.q))
 if(mode==='quiz')current=questions.find(q=>q.diagnostic&&!done.has(q.id))
 else if(mode==='redo')current=findQ(id)
 else {const qs=questions.filter(q=>q.unit===Number(id)&&!q.diagnostic);current=qs.find(q=>!state.attempts.some(r=>r.q===q.id))||qs.slice().sort((a,b)=>last(a)-last(b))[0]}
 }
 if(!current)return heading('能力诊断','逐单元识别需要巩固的知识。')+summary()
 const q=current,u=inner(q.unit)
 return heading(mode==='quiz'?'能力诊断':mode==='redo'?'错题重做':'单元练习',u.name+' · '+q.source)+`<section class="panel lesson"><small>${mode==='quiz'?'诊断 '+(q.unit+1)+' / 10':q.level}</small><h2>${q.text}</h2>${q.tex?`<div class="formula">${math(q.tex)}</div>`:''}${feedback?`<div class="feedback"><h3>${feedback.ok?'回答正确':'这一步需要再检查'}</h3><p>${feedback.reason}</p>${feedback.ok?'':`<strong>建议排查 · ${feedback.error}</strong><p>下一步　${link('unit/'+feedback.prereq,'复习「'+inner(feedback.prereq).name+'」')}</p>`}</div><button id="next">${mode==='redo'?'返回复习计划':mode==='quiz'&&q.unit===9?'查看诊断报告':'继续下一题'}</button>`:`<form id="response"><div class="answer">${q.choices.length?q.choices.map((v,i)=>`<label class="opt"><input type="radio" name="answer" value="${i}" required>${v}</label>`).join(''):'<label>你的答案 <input name="answer" required maxlength="120" autocomplete="off" placeholder="如 -1/6 或 x^2+2*x"></label>'}</div><button>提交答案</button><button type="button" class="muted" id="hint" ${hint===2?'disabled':''}>提示 ${hint}/2</button><div id="hints" aria-live="polite"></div><p role="alert" id="error"></p></form>`}</section>`
}
function last(q){return state.attempts.filter(r=>r.q===q.id).at(-1)?.id||0}
function knowledge(){return heading('知识图谱','先修连线表示建议学习顺序。点击知识点可以查看讲义与练习。')+units.map(u=>`<section class="panel"><small>${u.group} · ${u.source}</small><h2>${link('unit/'+u.id,u.name)}</h2><p>${score(u)}　·　建议先修　${u.prereq.map(i=>link('unit/'+i,inner(i).name)).join(' → ')||'起点'}</p><p>${state.reviews.filter(r=>r.unit===u.id).map(r=>link('redo/'+r.q,'关联错题 '+r.q)).join('　')}</p>${materialLinks(u.id)}</section>`).join('')}
function reviews(){return heading('错题与复习','答错的题当天复习，重做正确后间隔 3 天再次巩固。')+`<section class="panel"><h2>复习计划</h2>${state.reviews.map(r=>`<div class="unitrow"><span class="symbol g2">↻</span><div><strong>${inner(r.unit).name} · ${r.error}</strong><small>${r.ready?'到期可复习':'下次巩固'} · ${r.due} · ${r.q}</small>${link('redo/'+r.q,'重做这道题')}　${link('unit/'+(inner(r.unit).prereq[0]??r.unit),'回看前置知识')}</div></div>`).join('')||'<p>还没有错题。完成诊断后，需要巩固的题会出现在这里。</p>'}</section>`}
function progress(){return heading('个人进度','按不同题目的最近一次作答估计掌握度，重复答同一题只更新该题证据。')+`<section class="panel"><h2>单元掌握情况</h2>${units.map(u=>`<div class="unitrow"><strong>${u.name}</strong><progress max="100" value="${state.scores[u.id]||0}"></progress><small>${score(u)}</small></div>`).join('')}</section><section class="panel"><h2>学习记录</h2>${state.attempts.slice(-40).reverse().map(r=>`<p>${r.day} · ${inner(findQ(r.q).unit).name} · ${{quiz:'诊断',practice:'练习',review:'复习'}[r.mode]} · ${r.ok?'正确':'需巩固'}</p>`).join('')||'完成第一题后即可查看记录。'}</section>`+backupUI()}
async function extra(page,id){
 if(['practice','quiz','redo'].includes(page))return exercise(page,id)
 if(page==='map')return knowledge()
 if(page==='review')return reviews()
 if(page==='progress')return progress()
 return library(id)
}
function bind(page,id){
 if(!['quiz','practice','redo'].includes(page))activeRoute=''
 const form=document.querySelector('#response')
 if(form){
 const h=document.querySelector('#hint')
 h.onclick=()=>{hint=Math.min(2,hint+1);h.textContent='提示 '+hint+'/2';h.disabled=hint===2;document.querySelector('#hints').textContent=current.hints.slice(0,hint).join('　')}
 form.onsubmit=async e=>{e.preventDefault();const btn=form.querySelector('button');btn.disabled=true
 try{feedback=await api('answer',{q:current.id,answer:new FormData(form).get('answer'),mode:page==='redo'?'review':page});state=await api('state');await render()}
 catch(e){document.querySelector('#error').textContent=e.message;btn.disabled=false}}
 }
 const next=document.querySelector('#next')
 if(next)next.onclick=()=>{current=null;feedback=null;hint=0;if(page==='redo')location.hash='review';else render()}
 bindMaterials(page,id)
}
function library(){return heading('资料库','内置原创示例')+courses()}
function materialLinks(){return ''}
function backupUI(){return ''}
function bindMaterials(){}

async function init(){try{[units,state,questions]=await Promise.all([api('units'),api('state'),api('questions')]);await render()}catch(e){shell('home',heading('连接失败','请确认本地服务正在运行。')+'<button onclick="location.reload()">重试</button>')}}
window.addEventListener('hashchange',()=>{window.scrollTo(0,0);render()})
init()
