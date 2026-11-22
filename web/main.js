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
const counts=()=>[units.length,state.attempts.length,state.reviews.length]
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
async function extra(){return courses()}
function bind(){}
async function init(){try{units=await api('units');await render()}catch(e){shell('home',heading('连接失败','请确认本地服务正在运行。')+'<button onclick="location.reload()">重试</button>')}}
window.addEventListener('hashchange',()=>{window.scrollTo(0,0);render()})
init()
