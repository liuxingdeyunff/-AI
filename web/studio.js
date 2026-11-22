// Per-attempt tutoring and source-linked model lessons share the local API.
export function studio({api,esc,math,link}) {
 const methods={substitution:"在分子里把 sin(x) 换成 x",expansion:"写了展开式，但不确定保留到几阶",calculation:"用了定义或公式，可能算错了",unsure:"我还不确定"}
 const status=()=>'<p class="status" role="status"></p>'
 const form=(id,html)=>`<form class="stack" id="${id}">${html}${status()}</form>`
 const guided=(id,title)=>link("guide/"+id,esc(title))
 function settings(model) {
  return `<section class="panel"><h2>教学模式</h2><p>${model?'本机模型 · '+esc(model):'离线基础模式 · SymPy 判题、分级提示与复习'}</p>
  <details><summary>设置本机 Ollama</summary><p>选择本机已经安装的模型，可按授权片段生成课程和追问。模型在本机运行。</p>
  <button id="scan-models">查找本机模型</button><span id="scan-status" role="status"></span>
  ${form("choose-model",'<label>模型 <select name="name"><option value="">关闭模型，使用离线课程</option></select></label><button>保存教学模式</button>')}</details></section>`
 }
 function analysis(doc,index,guides,model) {
  const related=guides.filter(g=>g.doc===doc.id)
  return `<section class="panel"><h2>教材研读</h2>${related.map(g=>guided(g.id,g.units.map(u=>u.title).slice(0,2).join(' · '))).join('<br>')}
  ${model?form("analyze",`<p>从当前原文位置开始，选择连续片段。每段最多发送开头 1800 字。</p><label>片段数 <select name="count">${Array.from({length:Math.min(6,doc.sections.length-index)},(_,j)=>`<option>${j+1}</option>`).join('')}</select></label>
  <details><summary>查看将发送的原文</summary><pre id="analysis-preview"></pre></details>
  <label><input type="checkbox" required name="consent"> 同意发送所选原文给本机模型 ${esc(model)}</label><button>生成研读单元</button>`):'启用本机模型后，可根据原文生成章节导读、先修关系和开放练习。'}
  <small>PDF 抽取可能改变上下标、分式和换行。公式及适用条件请对照原件。</small></section>`
 }
 function guidePage(ref,guides,docs,model) {
  const [key,n='0']=ref.split('~'),g=guides.find(g=>g.id===key),i=Number(n),u=g?.units[i]
  if(!u)throw Error('找不到研读单元。')
  const d=docs.find(d=>d.id===g.doc)
  return `<h1>${esc(u.title)}</h1><p class="lead">AI 研读 · ${esc(g.meta.model)} · ${esc(u.chapter)}</p>
  <div class="columns"><section class="panel lesson"><small>由资料生成 · ${esc(u.kind)}</small><h2>阅读目标</h2><p>${esc(u.lesson)}</p>
  ${u.formula?`<h2>原文公式</h2><pre>${esc(u.formula)}</pre>`:''}${u.condition?`<h2>适用条件</h2><p>${esc(u.condition)}</p>`:''}
  <h2>原文依据</h2><blockquote>${esc(u.quote)}</blockquote>${link('library/'+d.id+'~'+u.section,esc(d.name)+' · '+esc(d.sections[u.section].anchor))}<small>${esc(u.warning)}</small>
  <h2>围绕原文练习</h2><p>${esc(u.question)}</p>${form('open-response',`<label>你的论证<textarea name="question" maxlength="360" required></textarea></label><small>开放回答供自评，模型只能提供讨论建议。</small>
  ${model?'<label><input type="checkbox" required> 同意将本题、原文引用与论证发送到本机模型</label><button>请导师追问</button>':''}`)}</section>
  <section class="panel"><h2>本份材料的学习顺序</h2>${g.units.map((v,j)=>`<p>${guided(key+'~'+j,(j+1)+'. '+v.title)}</p>`).join('')}
  <h2>本节建议先修</h2>${u.requires.map(j=>guided(key+'~'+j,g.units[j].title)).join(' · ')||'本组起点'}</section></div>`
 }
 function studyGraph(guides) {
  return guides.length?`<section class="panel"><h2>资料中的知识关联</h2>${guides.map(g=>g.units.map((u,i)=>`<p>${u.requires.map(j=>guided(g.id+'~'+j,g.units[j].title)).join('、')||'起点'} → ${guided(g.id+'~'+i,u.title)}</p>`).join('')).join('')}</section>`:''
 }
 async function coachPage(id,state,qs,units,model) {
  const row=state.attempts.find(a=>a.id===Number(id))
  if(!row)throw Error('找不到作答记录。')
  const q=qs.find(q=>q.id===row.q),u=units[q.unit],result=await api('coach',{attempt:row.id}),e=result.evidence
  const allowed=['1-0','1-4'].includes(row.q)?Object.keys(methods):['calculation','unsure']
  return `<h1>作答复盘</h1><p class="lead">${esc(u.name)} · ${q.choices.length?'选项规则核验':'SymPy 符号核验'}</p>
  <section class="panel"><h2>这次作答留下了什么证据</h2><div class="formula">${q.tex?math(q.tex):esc(q.text)}</div>
  <p>你的答案　${esc(q.choices.length?q.choices[+row.answer]:row.answer)} · ${row.ok?'正确':'需巩固'} · 使用 ${e.hints} 级提示</p><blockquote>${esc(e.steps||'这次没有填写推导步骤。')}</blockquote>
  ${form("method",`<label>你当时采用了哪种思路？ <select name="method">${allowed.map(k=>`<option value="${k}" ${(e.method||'unsure')===k?'selected':''}>${methods[k]}</option>`).join('')}</select></label><button>按我的思路调整练习</button>`)}
  <p id="guidance">${esc(result.guidance)}</p>${u.prereq.map(j=>link('unit/'+j,'复习「'+units[j].name+'」')).join('　')}</section>
  <section class="panel"><h2>针对性变式</h2><small>根据本次方法选择与后续作答调整难度。答案由 SymPy 校验。</small><div id="variant">${variantForm(result.task)}</div>
  <div id="variant-history">${trialHistory(e.trials)}</div></section>
  <section class="panel"><h2>教学追问</h2>${e.conversation.map(c=>`<p><strong>${esc(c.question)}</strong></p><p>${esc(c.answer)}</p>`).join('')}
  ${model?form("tutor-chat",`<details><summary>预览本次发送的学习证据</summary><pre id="chat-preview"></pre></details><label>想问什么？<input name="question" maxlength="400" required></label><label><input type="checkbox" required> 同意将预览中的证据和问题发给 ${esc(model)}</label><button>向导师提问</button>`):link('library','在资料库启用本机模型')}</section>`
 }
 function variantForm(t){return t?form('variant-form',`<input type="hidden" name="index" value="${t.index}"><small>第 ${t.index+1} 次 · 难度 ${t.level}/3</small><div class="formula">${math(t.tex)}</div><label>变式答案 <input required maxlength="120" name="answer"></label><button>校验变式</button>`):'已完成本次变式训练。'}
 function trialHistory(trials){return trials.slice(-8).reverse().map(t=>`<p>第 ${t.index+1} 次 · 难度 ${t.level} · ${esc(t.answer)} · ${t.ok?'正确':'需巩固'}　${esc(t.reason)}</p>`).join('')}
 function handle(id,action) {
  const f=document.getElementById(id);if(!f)return
  f.onsubmit=async ev=>{ev.preventDefault();const b=f.querySelector('button'),msg=f.querySelector('.status');if(!b)return;b.disabled=true;msg.textContent='正在处理…'
   try{const out=await action(new FormData(f),f);msg.textContent=out||''}catch(err){msg.textContent=err.message}finally{b.disabled=false}}
 }
 function bind({page,id,docs,guides,refresh,updateState}) {
  const scan=document.getElementById('scan-models')
  if(scan)scan.onclick=async()=>{scan.disabled=true;const msg=document.getElementById('scan-status');try{const names=await api('available-models'),sel=document.querySelector('#choose-model select');sel.length=1;for(const n of names)sel.add(new Option(n,n));msg.textContent=names.length?'请选择模型':'Ollama 已连接，尚无已安装模型。'}catch(e){msg.textContent=e.message}finally{scan.disabled=false}}
  handle('choose-model',async f=>{await api('configure-model',{name:f.get('name')});await refresh()})
  if(page==='library'&&id&&document.querySelector('#analyze')){
    const [key,num='0']=id.split('~'),d=docs.find(d=>d.id===key),start=Number(num),sel=document.querySelector('#analyze select')
    const preview=()=>document.querySelector('#analysis-preview').textContent=d.sections.slice(start,start+Number(sel.value)).map(s=>s.anchor+'\n'+s.text.slice(0,1800)).join('\n\n')
    preview();sel.onchange=()=>{preview();document.querySelector('#analyze input[type=checkbox]').checked=false}
    handle('analyze',async f=>{const g=await api('analyze',{doc:key,start,count:Number(f.get('count')),consent:f.has('consent')});guides.unshift(g);location.hash='guide/'+g.id})
  }
  if(page==='guide'){
   const [key,num='0']=id.split('~'),u=guides.find(g=>g.id===key).units[+num]
   handle('open-response',async f=>(await api('discuss',{consent:true,context:u.quote+'\n'+u.question,question:f.get('question')})).answer)
  }
  if(page==='coach'){
   const attempt=Number(id)
   handle('method',async f=>{await api('coach',{attempt,method:f.get('method')});await updateState()})
   handle('variant-form',async f=>{await api('coach',{attempt,index:Number(f.get('index')),answer:f.get('answer')});await updateState()})
   const preview=document.getElementById('chat-preview')
   if(preview){api('tutor-chat',{attempt,preview:true}).then(r=>preview.textContent=r.context).catch(e=>preview.textContent=e.message)
    handle('tutor-chat',async f=>{await api('tutor-chat',{attempt,context:preview.textContent,question:f.get('question'),consent:true});await updateState()})}
  }
 }
 return {settings,analysis,guidePage,studyGraph,coachPage,bind}
}
