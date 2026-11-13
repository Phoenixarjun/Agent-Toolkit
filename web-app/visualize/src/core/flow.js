import { ancestors } from './model.js';

const within=(id,parent,index)=>id!=null&&parent!=null&&ancestors(id,index).includes(parent);

export function resolveTransition(previous,next,indexes){
  if(!previous||!next)return {state:'end',label:'End of journey',relation:null};
  const from=previous.component_id,to=next.component_id;
  if(from===to)return {state:'internal',label:'Continues inside the same component',relation:null};
  const {relations,components}=indexes;
  const matching=[];
  const reverse=[];
  for(const edge of relations.values()){
    if(edge.to==null)continue;
    const forward=within(from,edge.from,components)&&within(to,edge.to,components);
    const backwards=within(from,edge.to,components)&&within(to,edge.from,components);
    if(forward)matching.push(edge);
    else if(backwards){if(edge.direction==='bidirectional')matching.push(edge);else reverse.push(edge);}
  }
  const explicit=next.via_relation_id?relations.get(next.via_relation_id):null;
  if(next.via_relation_id&&!explicit)return {state:'unresolved',label:'Referenced connection was not found',relation:null};
  if(explicit&&!matching.some(edge=>edge.id===explicit.id))return {state:'mismatch',label:'Declared connection does not link these stages in the required direction',relation:explicit};
  const sourcePath=ancestors(from,components),targetPath=ancestors(to,components);
  const distance=edge=>{
    const forward=sourcePath.indexOf(edge.from)+targetPath.indexOf(edge.to);
    if(sourcePath.includes(edge.from)&&targetPath.includes(edge.to))return forward;
    if(edge.direction==='bidirectional'&&sourcePath.includes(edge.to)&&targetPath.includes(edge.from))return sourcePath.indexOf(edge.to)+targetPath.indexOf(edge.from);
    return Infinity;
  };
  const leastDistance=matching.length?Math.min(...matching.map(distance)):Infinity;
  const nearest=matching.filter(edge=>distance(edge)===leastDistance);
  if(!explicit&&nearest.length>1)return {state:'uncertain',label:'Several equally specific connections match these stages; the model needs an explicit via_relation_id to establish the transfer',relation:null,candidates:nearest.map(edge=>edge.id)};
  const relation=explicit||nearest[0];
  if(relation){
    if(relation.fault_status==='CONFIRMED'||relation.evidence_status==='CONTRADICTED')return {state:'broken',label:'Connection has a confirmed issue or contradictory evidence',relation};
    if(relation.fault_status==='SUSPECTED'||relation.evidence_status==='UNRESOLVED'||relation.fault_status==='INDETERMINATE')return {state:'uncertain',label:'Connection needs investigation before it can be animated as working',relation};
    return {state:'connected',label:relation.evidence_status==='SOURCE_VERIFIED'?'Source-backed connection':'Modeled connection, not observed runtime traffic',relation};
  }
  if(reverse.length)return {state:'mismatch',label:'Known relationship is directed the other way',relation:reverse[0]};
  const shared=ancestors(from,components).find(id=>ancestors(to,components).includes(id));
  if(shared)return {state:'internal-unverified',label:'Stages share a parent, but no direct internal communication was established',relation:null};
  return {state:'unresolved',label:'No supported connection links these stages',relation:null};
}

export function projectedTransition(current,next,indexes){
  if(!current||!next)return {state:'end',label:'End of journey',relation:null};
  if(current.offLevel||next.offLevel||!current.visibleId||!next.visibleId)return {state:'outside',label:'The next step is outside the current architecture level',relation:null};
  if(current.visibleId===next.visibleId)return {state:'internal',label:'Continues inside this component; enter it to inspect internal stages',relation:null};
  return resolveTransition(current.steps.at(-1),next.steps[0],indexes);
}

export function playbackSteps(journey) {
  if (!journey) return [];
  if (!journey.playback_path) return journey.steps;
  const byId = new Map(journey.steps.map(step => [step.id, step]));
  return journey.playback_path.map(id => byId.get(id));
}

export function playbackNeedsPath(journey) {
  if (!journey?.execution_edges?.length || journey.playback_path) return false;
  const outgoing = new Map(),incoming=new Map();
  const links = new Set();
  for(const edge of journey.execution_edges){
    links.add(`${edge.from_step_id}:${edge.to_step_id}`);
    outgoing.set(edge.from_step_id,(outgoing.get(edge.from_step_id)||0)+1);
    incoming.set(edge.to_step_id,(incoming.get(edge.to_step_id)||0)+1);
    if(['fan_out','fan_in','branch','retry','fallback','compensate'].includes(edge.type))return true;
  }
  if([...outgoing.values(),...incoming.values()].some(count=>count>1))return true;
  return journey.steps.slice(1).some((step,i)=>!links.has(`${journey.steps[i].id}:${step.id}`));
}

export function assessJourney(journey,indexes){
  const transitions=[];
  const trace=playbackSteps(journey);
  if(!journey.execution_edges?.length || !playbackNeedsPath(journey))for(let i=1;i<trace.length;i++)transitions.push(resolveTransition(trace[i-1],trace[i],indexes));
  const edges = (journey.execution_edges || []).map(edge => {
    const from = journey.steps.find(step => step.id === edge.from_step_id);
    const to = journey.steps.find(step => step.id === edge.to_step_id);
    const transfer = resolveTransition(from, {...to, via_relation_id: edge.via_relation_id || to.via_relation_id}, indexes);
    return {...edge, transfer};
  });
  const counts={connected:0,internal:0,'internal-unverified':0,broken:0,mismatch:0,unresolved:0,uncertain:0,outside:0};
  for(const transition of transitions)counts[transition.state]=(counts[transition.state]||0)+1;
  return {transitions,edges,counts,complete:![...transitions,...edges.map(e=>e.transfer)].some(t=>['broken','mismatch','unresolved','uncertain','internal-unverified'].includes(t.state))};
}

export function relatedImpact(component,model,indexes){
  const dependsOn=[],dependedOnBy=[];
  for(const r of model.relations){
    const isSource=within(r.from,component.id,indexes.components);
    const isTarget=within(r.to,component.id,indexes.components);
    if(isTarget&&!isSource)dependedOnBy.push({id:r.from,kind:r.kind,evidence:r.evidence_status});
    if(isSource&&!isTarget&&r.to)dependsOn.push({id:r.to,kind:r.kind,evidence:r.evidence_status});
  }
  const journeys=model.journeys.filter(j=>j.steps.some(s=>within(s.component_id,component.id,indexes.components)));
  return {dependsOn,dependedOnBy,journeys};
}

export function semanticGroups(graph,limit=40){
  const size=Math.max(8,Math.min(64,Math.floor(limit)));
  const nodes=graph.nodes;
  if(nodes.length<=size)return [{label:graph.parentId?"Component internals":"System architecture",nodes}];
  const nodeMap=new Map(nodes.map(n=>[n.id,n]));
  const adjacency=new Map(nodes.map(n=>[n.id,new Set()]));
  for(const edge of graph.edges){
    if(adjacency.has(edge.from)&&adjacency.has(edge.to)){
      adjacency.get(edge.from).add(edge.to);
      adjacency.get(edge.to).add(edge.from);
    }
  }
  const buckets=new Map();
  for(const node of nodes){
    const key=node.domain||node.group_id||node.owner||null;
    if(key){if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(node);}
  }
  const groups=[],used=new Set();
  for(const [key,items] of [...buckets].sort((a,b)=>a[0].localeCompare(b[0]))){
    for(let i=0;i<items.length;i+=size){const group=items.slice(i,i+size);groups.push({label:key,nodes:group});for(const n of group)used.add(n.id);}
  }
  const remaining=nodes.filter(n=>!used.has(n.id));
  const seen=new Set(),communities=[];
  for(const node of remaining){
    if(seen.has(node.id))continue;
    const queue=[node.id],component=[];seen.add(node.id);
    for(let i=0;i<queue.length;i++){
      const id=queue[i];component.push(nodeMap.get(id));
      for(const neighbor of [...adjacency.get(id)].sort())if(!used.has(neighbor)&&!seen.has(neighbor)){seen.add(neighbor);queue.push(neighbor);}
    }
    communities.push(component);
  }
  let batch=[];
  for(const community of communities){
    if(batch.length&&batch.length+community.length>size){groups.push({label:'Connected architecture',nodes:batch});batch=[];}
    for(let i=0;i<community.length;i+=size){
      const chunk=community.slice(i,i+size);
      if(chunk.length===size){if(batch.length){groups.push({label:'Connected architecture',nodes:batch});batch=[];}groups.push({label:'Connected architecture',nodes:chunk});}
      else batch.push(...chunk);
    }
  }
  if(batch.length)groups.push({label:'Connected architecture',nodes:batch});
  return groups.length?groups.map(g=>({...g,nodes:g.nodes.sort((a,b)=>a.id.localeCompare(b.id))})):[];
}

export function sliceGraph(graph,page=0,limit=40){
  const groups=semanticGroups(graph,limit);
  const total=Math.max(1,groups.length);
  const selected=Math.min(total-1,Math.max(0,Math.floor(page)));
  const group=groups[selected]||{nodes:[],label:'Empty view'};
  const nodes=group.nodes;
  const ids=new Set(nodes.map(node=>node.id));
  const edges=[];
  for(const r of graph.edges){
    const fromHere=ids.has(r.from),toHere=ids.has(r.to);
    if(fromHere&&toHere)edges.push(r);
    else if(fromHere)edges.push({...r,to:null,boundary:true,boundaryDirection:r.direction==='bidirectional'?'bidirectional':'outgoing',unresolved_target:r.to||r.unresolved_target||'Outside current group',outsideSlice:!!r.to});
    else if(toHere)edges.push({...r,from:r.to,to:null,boundary:true,boundaryDirection:r.direction==='bidirectional'?'bidirectional':'incoming',unresolved_target:r.from,outsideSlice:true});
  }
  return {...graph,nodes,edges,page:selected,pages:total,totalNodes:graph.nodes.length,limit:Math.max(8,Math.min(64,Math.floor(limit))),groupLabel:group.label,groups:groups.map(g=>({label:g.label,ids:g.nodes.map(n=>n.id)}))};
}

export function enumerateJourneyPaths(journey,maxPaths=12,maxSteps=48){
  if(!journey?.execution_edges?.length)return [];
  const stepMap=new Map(journey.steps.map(s=>[s.id,s]));
  const edges=new Map(journey.steps.map(s=>[s.id,[]]));
  const incoming=new Map(journey.steps.map(s=>[s.id,0]));
  for(const edge of journey.execution_edges){
    edges.get(edge.from_step_id).push(edge);
    incoming.set(edge.to_step_id,incoming.get(edge.to_step_id)+1);
  }
  const roots=journey.steps.filter(s=>incoming.get(s.id)===0).map(s=>s.id);
  if(!roots.length)roots.push(journey.steps[0].id);
  const result=[],limit=Math.max(1,Math.min(24,maxPaths)),depth=Math.max(2,Math.min(120,maxSteps));
  function walk(id,ids,route,visits){
    if(result.length>=limit)return;
    const next=edges.get(id)||[];
    if(!next.length||ids.length>=depth){result.push({ids:[...ids],edges:[...route],truncated:ids.length>=depth});return;}
    for(const edge of next){
      if(result.length>=limit)break;
      const count=visits.get(edge.to_step_id)||0;
      if(count>= (edge.type==='retry'?2:1)){
        result.push({ids:[...ids],edges:[...route],truncated:true});continue;
      }
      const updated=new Map(visits);updated.set(edge.to_step_id,count+1);
      walk(edge.to_step_id,[...ids,edge.to_step_id],[...route,edge],updated);
    }
  }
  for(const root of roots){if(result.length>=limit)break;walk(root,[root],[],new Map([[root,1]]));}
  return result.filter(path=>path.ids.every(id=>stepMap.has(id)));
}
