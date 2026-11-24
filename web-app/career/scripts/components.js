(function(g){
'use strict';
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const str=x=>typeof x==='string';
const id=x=>str(x)&&/^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$/.test(x);
const date=x=>str(x)&&/^\d{4}-\d{2}-\d{2}$/.test(x)&&!isNaN(Date.parse(x))&&new Date(x).toISOString().slice(0,10)===x;
const own=(o,k)=>Object.hasOwn(o,k);
const scalar=x=>x===null||str(x)||typeof x==='boolean'||(typeof x==='number'&&Number.isFinite(x));
const text=x=>x===null||x===undefined||x===''?'Not recorded':String(x);
const pages=[['overview','Overview'],['roadmap','Roadmap'],['tasks','Tasks'],['projects','Projects'],['presence','Presence'],['content','Content'],['resumes','Résumés'],['opportunities','Opportunities'],['companies','Companies'],['applications','Applications'],['interviews','Interviews'],['offers','Offers'],['research','Research'],['activity','Activity']];
const reserved=new Set(pages.map(p=>p[0]));
const defaultSections=pages.slice(3,12).map(p=>p[0]);
function validate(data){
 const errors=[]; const check=(v,p)=>{if(!v&&errors.length<30)errors.push(p);return v};
 const arr=(x,p)=>check(Array.isArray(x),p)?x:[];
 const objs=(x,p)=>arr(x,p).filter((r,i)=>check(object(r),`${p}[${i}]`));
 const unique=(xs,p)=>{const seen=new Set();for(const x of xs){check(id(x.id)&&!seen.has(x.id),`${p}: invalid or duplicate id`);seen.add(x.id)}return seen};
 const fields=(x,p)=>{if(x!==undefined)for(const f of objs(x,p))check(str(f.label)&&scalar(f.value),`${p}: invalid field`)};
 function blocks(x,p){if(x===undefined)return;for(const b of objs(x,p)){
  check(str(b.title),`${p}: title`);
  if(b.type==='text')check(str(b.text),`${p}: text`);
  else if(b.type==='list')check(arr(b.items,p).every(str),`${p}: list items`);
  else if(b.type==='metrics')for(const m of objs(b.items,p))check(str(m.label)&&scalar(m.value)&&(m.detail===undefined||str(m.detail)),`${p}: metric`);
  else if(b.type==='table'){const cols=arr(b.columns,p);check(cols.length>0&&cols.every(str),`${p}: columns`);for(const r of arr(b.rows,p))check(Array.isArray(r)&&r.length===cols.length&&r.every(scalar),`${p}: row`)}
  else if(b.type==='document')check(id(b.document_id),`${p}: document ID`);
  else if(b.type==='quiz'){
   const qs=objs(b.questions,p);unique(qs,p);check(qs.length>=1&&qs.length<=50,`${p}: quiz length`);
   for(const q of qs){check(str(q.prompt)&&q.prompt.trim().length>0&&str(q.competency)&&q.competency.trim().length>0&&str(q.explanation)&&q.explanation.trim().length>0,`${p}: quiz question`);
    if(q.kind==='choice'){const opts=arr(q.options,p);check(opts.length>=2&&opts.length<=8&&opts.every(v=>str(v)&&v.trim().length>0)&&new Set(opts.map(v=>str(v)?v.trim().toLowerCase():v)).size===opts.length,`${p}: quiz options`);check(Number.isInteger(q.correct_index)&&q.correct_index>=0&&q.correct_index<opts.length,`${p}: quiz answer`)}
    else if(q.kind==='written'){const criteria=arr(q.criteria,p);check(criteria.length>0&&criteria.every(v=>str(v)&&v.trim().length>0),`${p}: quiz criteria`)}
    else check(false,`${p}: quiz kind`);
   }
  }
  else check(false,`${p}: unsupported block type`);
 }}
 if(!check(object(data),'snapshot must be an object'))return errors;
 check(data.schema_version===1,'schema_version must be 1');check(['demo','workspace'].includes(data.mode),'mode must be demo or workspace');check(date(data.as_of),'as_of must be an ISO date');check(str(data.generated_at)&&/T.*(Z|[+-]\d\d:\d\d)$/.test(data.generated_at)&&!isNaN(Date.parse(data.generated_at)),'generated_at must be a timestamp with timezone');
 check(object(data.candidate),'candidate object');if(object(data.candidate))for(const k of ['current_role','target'])check(data.candidate[k]===null||str(data.candidate[k]),`candidate.${k}`);
 const docs=objs(data.documents,'documents'), docIds=unique(docs,'documents');
 for(const d of docs){check(str(d.title)&&str(d.category)&&date(d.updated)&&str(d.markdown),`document ${d.id}`);for(const s of objs(d.sources===undefined?[]:d.sources,'sources'))check(str(s.label)&&safeUrl(s.url)!==null,'invalid source link')}
 const docRefs=(refs,p)=>{if(refs!==undefined)check(arr(refs,p).every(r=>docIds.has(r)),`${p}: unknown document`)};
 const checkBlocks=(xs,p)=>{blocks(xs,p);if(Array.isArray(xs))for(const b of xs)if(object(b)&&b.type==='document')check(docIds.has(b.document_id),`${p}: unknown document`)};
 if(check(object(data.sections),'sections object'))for(const k of Object.keys(data.sections)){
  check(defaultSections.includes(k),`unknown default section ${k}`);const rs=objs(data.sections[k],k);unique(rs,k);for(const r of rs){check(str(r.title)&&str(r.status)&&date(r.updated)&&str(r.summary),`invalid record ${k}/${r.id}`);fields(r.fields,k);docRefs(r.document_ids,k);checkBlocks(r.blocks,k)}
 }
 const ex=objs(data.extensions===undefined?[]:data.extensions,'extensions');unique(ex,'extensions');for(const p of ex){check(!reserved.has(p.id)&&str(p.title)&&str(p.description),'invalid extension');checkBlocks(p.blocks,'extension')}
 const acts=objs(data.activity,'activity');unique(acts,'activity');for(const a of acts){check(str(a.agent)&&str(a.summary)&&str(a.status)&&str(a.timestamp)&&/T.*(Z|[+-]\d\d:\d\d)$/.test(a.timestamp)&&!isNaN(Date.parse(a.timestamp)),'invalid activity');docRefs(a.document_ids,'activity')}
 const p=data.plan;if(p!==null){if(check(object(p),'plan object or null')){
  check(p.schema_version===1&&id(p.plan_id)&&str(p.target)&&date(p.start_date)&&date(p.deadline)&&p.start_date<=p.deadline,'plan header');
  if(date(p.start_date)&&date(p.deadline))check((Date.parse(p.deadline)-Date.parse(p.start_date))/86400000<=3660,'plan horizon too large');
  check(p.assumptions===undefined||(Array.isArray(p.assumptions)&&p.assumptions.every(str)),'plan assumptions');check(p.evidence_refs===undefined||(Array.isArray(p.evidence_refs)&&p.evidence_refs.every(str)),'plan evidence references');check(p.review_rationale===undefined||str(p.review_rationale),'plan review rationale');const pillars=objs(p.pillars,'pillars'), pi=unique(pillars,'pillars');for(const v of pillars)check(str(v.outcome)&&str(v.rationale),'pillar text');
  const caps=objs(p.capabilities,'capabilities'), ci=unique(caps,'capabilities');for(const v of caps)check(str(v.outcome)&&arr(v.pillar_ids,'pillar_ids').every(r=>pi.has(r)),'capability references');
  const ms=objs(p.milestones,'milestones'), mi=unique(ms,'milestones');for(const m of ms){check(str(m.title)&&date(m.start_date)&&date(m.due_date)&&p.start_date<=m.start_date&&m.start_date<=m.due_date&&m.due_date<=p.deadline&&str(m.acceptance)&&['ACTIVE','SCHEDULED','CONDITIONAL'].includes(m.activation),'milestone fields');check(arr(m.capability_ids,'capability_ids').every(r=>ci.has(r)),'milestone capability');check(arr(m.depends_on,'depends_on').every(r=>mi.has(r)&&r!==m.id),'milestone dependencies')}
 }}
 if(check(object(data.progress),'progress object'))for(const [k,v] of Object.entries(data.progress)){check(id(k)&&object(v)&&['NOT_STARTED','IN_PROGRESS','COMPLETED','BLOCKED'].includes(v.status),'progress entry');if(object(v)&&(v.activation_confirmed_at!==undefined||v.activation_evidence_refs!==undefined))check(date(v.activation_confirmed_at)&&v.activation_confirmed_at<=data.as_of&&Array.isArray(v.activation_evidence_refs)&&v.activation_evidence_refs.length>0&&v.activation_evidence_refs.every(x=>str(x)&&x.trim()),'conditional activation requires dated evidence');if(object(v)&&v.status==='COMPLETED')check(date(v.completed_at)&&v.completed_at<=data.as_of&&Array.isArray(v.evidence_refs)&&v.evidence_refs.length>0&&v.evidence_refs.every(str),'completion requires dated evidence')}
 if(data.routines!==undefined){const rs=objs(data.routines,'routines');unique(rs,'routines');for(const v of rs){check(str(v.title)&&str(v.summary)&&id(v.plan_id)&&(v.workflow_id===null||id(v.workflow_id))&&Number.isInteger(v.cadence_days)&&v.cadence_days>=1&&v.cadence_days<=366&&date(v.next_due)&&['ACTIVE','PAUSED','ENDED','BLOCKED'].includes(v.status),'invalid routine');docRefs(v.document_ids,'routine');}}
 check(data.next_review===null||date(data.next_review),'next_review date or null');
 check(['APPROVED','PROPOSED','UNKNOWN'].includes(data.plan_state),'plan_state');check(data.plan!==null||data.plan_state==='UNKNOWN','plan state requires a plan');
 checkBlocks(data.overview_blocks,'overview');return errors;
}
function safeUrl(x){try{if(!str(x))return null;const u=new URL(x);return ['https:','http:'].includes(u.protocol)&&!u.username&&!u.password?u.href:null}catch{return null}}
function el(tag,cls,content){const n=document.createElement(tag);if(cls)n.className=cls;if(content!==undefined)n.textContent=text(content);return n}
function add(parent,...nodes){for(const n of nodes.flat())if(n!==null&&n!==undefined)parent.append(n);return parent}
function link(label,href){const a=el('a','',label);a.href=href;return a}
function external(label,url){const safe=safeUrl(url);if(!safe)return el('span','muted',label);const a=link(label,safe);a.target='_blank';a.rel='noopener noreferrer';return a}
function status(s){const v=text(s);return el('span','status '+(['COMPLETED','PUBLISHED','VERIFIED','PASS','APPROVED','APPLIED'].includes(v.toUpperCase())?'good':['BLOCKED','CONTRADICTED','REJECTED'].includes(v.toUpperCase())?'bad':['PROPOSED','IN_PROGRESS','NEEDS_USER','REVISE','HOLD'].includes(v.toUpperCase())?'warn':''),v.replaceAll('_',' '))}
function empty(msg='No records in this snapshot.'){return el('p','empty',msg)}
function panel(title,description,children=[],action=null){const head=add(el('div','panel-head'),el('h2','',title),action);return add(el('section','panel'),head,description?el('p','desc',description):null,children)}
function metrics(items){return add(el('div','metrics'),items.map(m=>add(el('div','metric'),el('div','label',m.label),el('div','value',m.value),m.detail?el('div','detail',m.detail):null)))}
function table(columns,rows){if(!rows.length)return empty();const t=el('table');const head=add(el('tr'),columns.map(c=>{const h=el('th','',c);h.scope='col';return h}));add(t,add(el('thead'),head),add(el('tbody'),rows.map(r=>add(el('tr'),r.map(c=>add(el('td'),c instanceof Node?c:document.createTextNode(text(c))))))));return add(el('div','table-wrap'),t)}
function progress(done,total){const n=total?Math.round(done/total*100):null;const wrap=el('div','progress');if(n===null)return add(wrap,el('span','muted','Not planned'));const fill=el('div','fill');fill.style.width=n+'%';const track=add(el('div','track'),fill);track.setAttribute('role','progressbar');track.setAttribute('aria-label','Completed milestones');track.setAttribute('aria-valuenow',n);track.setAttribute('aria-valuemin','0');track.setAttribute('aria-valuemax','100');return add(wrap,track,el('span','',n+'%'))}
function markdown(src){const root=el('article','doc');let lines=src.split(/\r?\n/), i=0;while(i<lines.length){const l=lines[i++];if(!l.trim())continue;if(l.startsWith('```')){let buf=[];while(i<lines.length&&!lines[i].startsWith('```'))buf.push(lines[i++]);if(i<lines.length)i++;add(root,el('pre','',buf.join('\n')));continue}const h=l.match(/^(#{1,6})\s+(.+)$/);if(h){add(root,el('h'+Math.min(6,h[1].length+1),'',h[2]));continue}if(/^[-*] /.test(l)){const ul=el('ul');add(ul,el('li','',l.slice(2)));while(i<lines.length&&/^[-*] /.test(lines[i]))add(ul,el('li','',lines[i++].slice(2)));add(root,ul);continue}if(/^\d+\. /.test(l)){const ol=el('ol');add(ol,el('li','',l.replace(/^\d+\. /,'')));while(i<lines.length&&/^\d+\. /.test(lines[i]))add(ol,el('li','',lines[i++].replace(/^\d+\. /,'')));add(root,ol);continue}if(l.includes('|')&&i<lines.length&&/^\s*\|?\s*:?-{3,}/.test(lines[i])){const cells=x=>x.trim().replace(/^\||\|$/g,'').split('|').map(y=>y.trim());const cols=cells(l);i++;let rows=[];while(i<lines.length&&lines[i].includes('|')){const r=cells(lines[i]);if(r.length!==cols.length)break;rows.push(r);i++}add(root,table(cols,rows));continue}let buf=[l];while(i<lines.length&&lines[i].trim()&&!/^(#|```|[-*] |\d+\. )/.test(lines[i]))buf.push(lines[i++]);add(root,el('p','',buf.join('\n')))}return root}
function quiz(b){
 const root=el('div','quiz'), states=b.questions.map(()=>({answer:'',checked:false}));
 const summary=el('p','small');summary.setAttribute('aria-live','polite');
 function update(){const choices=b.questions.map((q,i)=>({q,s:states[i]})).filter(v=>v.q.kind==='choice');const checked=choices.filter(v=>v.s.checked);const correct=checked.filter(v=>Number(v.s.answer)===v.q.correct_index).length;summary.textContent=`Objective self-check: ${correct} correct / ${checked.length} checked (${choices.length} available). Written answers are not graded.`;}
 const reset=el('button','','Reset practice');reset.type='button';reset.addEventListener('click',()=>root.replaceWith(quiz(b)));
 add(root,el('p','desc','Offline self-practice. Answers stay in this view only; navigating away, importing or refreshing discards them. Not a live interview or an AI assessment.'),summary,reset);
 b.questions.forEach((q,i)=>{
  const s=states[i], fs=el('fieldset','quiz-question'), form=el('form','quiz-form'), feedback=el('div','quiz-feedback'), button=el('button','','Check answer');button.type='button';button.disabled=true;feedback.setAttribute('aria-live','polite');
  add(fs,el('legend','',`${i+1}. ${q.prompt}`),el('p','small',q.competency));
  const change=v=>{s.answer=v;s.checked=false;feedback.replaceChildren();button.disabled=!v.trim();copyText.hidden=true;copyText.value='';update()};
  if(q.kind==='choice'){q.options.forEach((opt,j)=>{const input=el('input');input.type='radio';input.name=`quiz-${i}`;input.value=String(j);input.addEventListener('change',()=>change(input.value));add(fs,add(el('label','quiz-option'),input,el('span','',opt)))});}
  else{const input=el('textarea','quiz-answer');input.rows=5;input.placeholder='Write your answer here';input.setAttribute('aria-label',`Answer to question ${i+1}`);input.addEventListener('input',()=>change(input.value));button.textContent='Show review criteria';add(fs,input);}
  button.addEventListener('click',()=>{s.checked=true;feedback.replaceChildren();if(q.kind==='choice'){add(feedback,el('strong','',Number(s.answer)===q.correct_index?'Correct':'Review this answer'),el('p','',`Reference answer: ${q.options[q.correct_index]}`));}else add(feedback,el('strong','','Self-review criteria'),add(el('ul'),q.criteria.map(c=>el('li','',c))));add(feedback,el('p','',q.explanation));update()});
  add(fs,button,feedback);form.addEventListener('submit',e=>e.preventDefault());add(root,add(form,fs));
 });
 const copyText=el('textarea','quiz-answer');copyText.readOnly=true;copyText.rows=6;copyText.hidden=true;copyText.setAttribute('aria-label','Practice responses to copy');const prepare=el('button','','Prepare responses to copy');prepare.type='button';prepare.addEventListener('click',()=>{copyText.value=b.questions.map((q,i)=>`${i+1}. ${q.prompt}\nAnswer: ${states[i].answer===''?'Not answered':q.kind==='choice'?q.options[Number(states[i].answer)]:states[i].answer}`).join('\n\n');copyText.hidden=false;copyText.focus();copyText.select()});add(root,prepare,copyText);update();return root;
}
function blocks(items,documents){return (items||[]).map(b=>{let body;if(b.type==='text')body=markdown(b.text);else if(b.type==='list')body=add(el('ul'),b.items.map(i=>el('li','',i)));else if(b.type==='metrics')body=metrics(b.items);else if(b.type==='table')body=table(b.columns,b.rows);else if(b.type==='quiz')body=quiz(b);else if(b.type==='document'){const d=documents.find(x=>x.id===b.document_id);body=d?link(d.title,'#research/'+d.id):empty('Document unavailable')}return panel(b.title,null,[body])})}
function timeline(plan,asOf,states){if(!plan||!plan.milestones.length)return empty('No milestone schedule recorded.');const start=new Date(plan.start_date+'T00:00:00Z'),end=new Date(plan.deadline+'T00:00:00Z');const startMonth=new Date(Date.UTC(start.getUTCFullYear(),start.getUTCMonth(),1));const endMonth=new Date(Date.UTC(end.getUTCFullYear(),end.getUTCMonth()+1,1));const monthCount=(endMonth.getUTCFullYear()-startMonth.getUTCFullYear())*12+endMonth.getUTCMonth()-startMonth.getUTCMonth();const step=Math.max(1,Math.ceil(monthCount/18));const ticks=[];for(let i=0;i<monthCount;i+=step)ticks.push(new Date(Date.UTC(startMonth.getUTCFullYear(),startMonth.getUTCMonth()+i,1)));const grid=el('div','timeline');grid.style.setProperty('--months',ticks.length);grid.style.minWidth=Math.max(640,190+ticks.length*55)+'px';const total=endMonth-startMonth;const pct=x=>Math.max(0,Math.min(100,(new Date(x+'T00:00:00Z')-startMonth)/total*100));const pos=x=>{const d=new Date(x+'T00:00:00Z');d.setUTCDate(d.getUTCDate()+1);return Math.max(0,Math.min(100,(d-startMonth)/total*100))};const labelPct=d=>(d-startMonth)/total*100;const labels=add(el('div','months'),ticks.map((d,i)=>{const n=el('div','month',d.toLocaleDateString('en',{month:'short',year:'2-digit',timeZone:'UTC'}));n.style.position='absolute';n.style.left=labelPct(d)+'%';n.style.width=(labelPct(ticks[i+1]||endMonth)-labelPct(d))+'%';return n}));add(grid,add(el('div','timeline-row'),el('div','timeline-name','Milestone'),labels));for(const m of plan.milestones){const lane=el('div','lane'),bar=el('div','bar '+(states[m.id]?.status==='COMPLETED'?'done':m.activation==='CONDITIONAL'?'conditional':''));bar.style.left=pct(m.start_date)+'%';bar.style.width=Math.max(.2,pos(m.due_date)-pct(m.start_date))+'%';bar.title=`${m.title}: ${m.start_date} to ${m.due_date}`;for(const tick of ticks){const mark=el('div','tick');mark.style.left=labelPct(tick)+'%';add(lane,mark)}add(lane,bar);if(asOf>=plan.start_date&&asOf<=plan.deadline){const line=el('div','today');line.style.left=pct(asOf)+'%';line.title='Snapshot date '+asOf;add(lane,line)}add(grid,add(el('div','timeline-row'),el('div','timeline-name',m.title),lane))}return add(el('div','timeline-wrap'),grid)}
g.CareerUI={validate,safeUrl,el,add,link,external,status,empty,panel,metrics,table,progress,markdown,blocks,timeline,pages,defaultSections,text,own};
})(globalThis);
