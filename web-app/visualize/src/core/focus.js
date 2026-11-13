import { visibleAtLevel } from './model.js';
import { resolveTransition } from './flow.js';

export function flowFocus(journey,graph,viewParentId,indexes,enabled=true){
  const nodeIds=new Set(),edgeIds=new Set(),alternatives=new Set(),faultIds=new Set();
  if(!enabled||!journey)return {enabled:false,nodeIds,edgeIds,alternatives,faultIds};
  for(const step of journey.steps){
    const id=visibleAtLevel(step.component_id,viewParentId,indexes.components);
    if(id)nodeIds.add(id);
    if(step.via_relation_id)edgeIds.add(step.via_relation_id);
  }
  if(!journey.execution_edges?.length)for(let i=1;i<journey.steps.length;i++){
    const result=resolveTransition(journey.steps[i-1],journey.steps[i],indexes);
    if(result.state==='connected'&&result.relation)edgeIds.add(result.relation.id);
  }
  for(const edge of journey.execution_edges||[]){
    if(edge.via_relation_id){
      if(edge.type==='branch'||edge.type==='fallback')alternatives.add(edge.via_relation_id);
      edgeIds.add(edge.via_relation_id);
    }
    const a=journey.steps.find(s=>s.id===edge.from_step_id);
    const b=journey.steps.find(s=>s.id===edge.to_step_id);
    if(a&&b){
      const transfer=resolveTransition(a,{...b,via_relation_id:edge.via_relation_id||b.via_relation_id},indexes);
      if(transfer.relation)edgeIds.add(transfer.relation.id);
    }
  }
  for(const edge of graph.edges){
    if(edge.fault_status==='CONFIRMED'||edge.evidence_status==='CONTRADICTED')faultIds.add(edge.id);
  }
  return {enabled:true,nodeIds,edgeIds,alternatives,faultIds};
}

export function focusAppearance(focus,kind,id,selected=false){
  if(!focus?.enabled||selected)return 'normal';
  if(kind==='edge'&&focus.faultIds.has(id))return 'fault';
  if(kind==='edge'&&focus.edgeIds.has(id))return focus.alternatives.has(id)?'alternative':'participating';
  if(kind==='node'&&focus.nodeIds.has(id))return 'participating';
  return 'muted';
}
