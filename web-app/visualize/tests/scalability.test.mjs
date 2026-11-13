import test from 'node:test';
import assert from 'node:assert/strict';
import { validateModel, viewGraph } from '../src/core/model.js';
import { sliceGraph } from '../src/core/flow.js';
import { layoutGraph } from '../src/core/layout.js';

function thirtyRepositoryFixture(){
 const components=[],relations=[],snapshots=[];
 for(let r=0;r<30;r++){
  snapshots.push({repository:`repository-${r}`,revision:`revision-${r}`,availability:'available'});
  components.push({id:`s${r}`,name:`Service ${r}`,role:'service',parent_id:null,responsibility:`Processes responsibility ${r}`,source_refs:[{path:'src/main.js',repository:`repository-${r}`}],evidence_status:'SOURCE_VERIFIED'});
  for(let m=0;m<5;m++)components.push({id:`s${r}-m${m}`,name:`Capability ${r}.${m}`,role:'module',parent_id:`s${r}`,responsibility:'Executes a bounded operation',source_refs:[{path:'src/main.js',repository:`repository-${r}`}],evidence_status:'SOURCE_VERIFIED'});
  if(r>0)relations.push({id:`r${r}`,from:`s${r-1}`,to:`s${r}`,kind:'calls',direction:'forward',evidence_status:'SOURCE_VERIFIED',fault_status:'NONE',source_refs:[{path:'src/main.js',repository:`repository-${r}`}]});
 }
 return {schema_version:'1.0.0',scope:{name:'30-repo test'},snapshots,components,relations,journeys:[],scenarios:[],findings:[],coverage:[]};
}

test('30 repositories and 180 discovered components can be validated and navigated hierarchically',()=>{
 const model=thirtyRepositoryFixture();const indexes=validateModel(model);
 const graph=viewGraph(model,null,indexes);
 assert.equal(graph.nodes.length,30);
 assert.equal(graph.edges.length,29);
 const positions=layoutGraph(graph.nodes,graph.edges,{iterations:90,maxNodes:64});
 assert.equal(positions.size,30);
 const inside=viewGraph(model,'s14',indexes);
 assert.equal(inside.nodes.length,5);
 for(const v of positions.values())assert.ok(v.every(Number.isFinite));
});

test('oversized architectural levels are paged without fabricating missing links',()=>{
 const model=thirtyRepositoryFixture();
 for(let r=30;r<141;r++)model.components.push({...model.components[0],id:`extra-${r}`,name:`Independent service ${r}`});
 model.relations.push({id:'cross-page',from:'s0',to:'extra-40',kind:'calls',direction:'forward',evidence_status:'INFERRED',fault_status:'NONE',source_refs:[]});
 const graph=viewGraph(model,null,validateModel(model));
 const first=sliceGraph(graph,0,40),last=sliceGraph(graph,3,40);
 assert.equal(first.pages,4);
 assert.ok(first.nodes.length>0&&first.nodes.length<=40);
 assert.ok(last.nodes.length>0&&last.nodes.length<=40);
 assert.equal([0,1,2,3].reduce((sum,page)=>sum+sliceGraph(graph,page,40).nodes.length,0),141);
 assert.equal(first.totalNodes,141);
 assert.ok(first.edges.every(edge=>edge.to===null||first.nodes.some(node=>node.id===edge.to)));
 assert.ok([0,1,2,3].some(page=>sliceGraph(graph,page,40).edges.some(edge=>edge.boundary&&edge.outsideSlice)) || graph.edges.some(edge=>edge.id==='cross-page'&&first.edges.some(e=>e.id===edge.id&&!e.boundary))); 
});
