import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateModel,viewGraph,projectJourney} from '../src/core/model.js';
import {projectedTransition,resolveTransition} from '../src/core/flow.js';
import {layout2D,connectionPath,quadraticPoint,quadraticArc,pointOnQuadraticArc,cameraFor,zoomAt} from '../src/core/diagram2d.js';

const model=JSON.parse(readFileSync(new URL('../data/demo.json',import.meta.url),'utf8'));
const indexes=validateModel(model);

test('2D layout includes every component exactly once, deterministically, with separated cards',()=>{
 const graph=viewGraph(model,null,indexes);
 const a=layout2D(graph.nodes),b=layout2D(graph.nodes);
 assert.deepEqual([...a],[...b]);
 assert.equal(a.size,graph.nodes.length);
 for(const [id,p] of a){
  assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));
  for(const [other,q] of a)if(id!==other)assert.ok(Math.abs(p.x-q.x)>=180||Math.abs(p.y-q.y)>=88);
 }
});

test('2D connector endpoints are stable and directional and packet motion stays finite',()=>{
 const path=connectionPath({x:-200,y:-100},{x:210,y:250},30);
 assert.deepEqual(quadraticPoint(path,0),path.start);
 assert.deepEqual(quadraticPoint(path,1),path.end);
 for(let i=0;i<=100;i++){
  const p=quadraticPoint(path,i/100);
  assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));
 }
 assert.match(path.d,/^M /);
});

test('2D camera zoom preserves the point under the pointer, and graph frame covers all components',()=>{
 const graph=viewGraph(model,null,indexes),points=layout2D(graph.nodes);
 const c=cameraFor(graph.nodes,points,1.5);
 assert.ok(c.width>0&&c.height>0);
 for(const p of points.values())assert.ok(p.x>=c.x&&p.x<=c.x+c.width&&p.y>=c.y&&p.y<=c.y+c.height);
 const target={x:c.x+c.width*.37,y:c.y+c.height*.63};
 const zoomed=zoomAt(c,target,.67);
 assert.ok(Math.abs((target.x-c.x)/c.width-(target.x-zoomed.x)/zoomed.width)<1e-10);
 assert.ok(Math.abs((target.y-c.y)/c.height-(target.y-zoomed.y)/zoomed.height)<1e-10);
});

test('fictional demo journeys specify complete top-level transfer routes without claiming source verification',()=>{
 for(const j of model.journeys){
  const projection=projectJourney(j,null,indexes.components);
  for(let i=1;i<projection.length;i++){
   assert.equal(projectedTransition(projection[i-1],projection[i],indexes).state,'connected',`${j.name} stage ${i}`);
  }
 }
 assert.ok(model.relations.every(r=>r.evidence_status!=='SOURCE_VERIFIED'));
});

test('direct relationship wins over less-specific ancestor match, but equally specific paths remain ambiguous',()=>{
 const fixture=structuredClone(model);
 fixture.relations.push({id:'specific-path',from:'events-requests',to:'worker-consumer',kind:'consumes_from',direction:'forward',source_refs:[],evidence_status:'INFERRED',fault_status:'NONE'});
 const ix=validateModel(fixture);
 assert.equal(resolveTransition({component_id:'events-requests'},{component_id:'worker-consumer'},ix).state,'uncertain');
 const specific=resolveTransition({component_id:'events-requests'},{component_id:'worker-consumer',via_relation_id:'specific-path'},ix);
 assert.equal(specific.state,'connected');
 const broader=resolveTransition({component_id:'events-requests'},{component_id:'worker'},ix);
 assert.ok(['connected','uncertain'].includes(broader.state));
});

test('2D request animation uses arc length rather than uneven quadratic parameter speed',()=>{
 const path=connectionPath({x:-500,y:-140},{x:140,y:340},100),table=quadraticArc(path,64);
 assert.ok(table.total>0);
 assert.deepEqual(pointOnQuadraticArc(path,table,0),path.start);
 assert.deepEqual(pointOnQuadraticArc(path,table,1),path.end);
 let previous=pointOnQuadraticArc(path,table,0),min=Infinity,max=0;
 for(let i=1;i<=20;i++){
  const current=pointOnQuadraticArc(path,table,i/20),delta=Math.hypot(current.x-previous.x,current.y-previous.y);
  min=Math.min(min,delta);max=Math.max(max,delta);previous=current;
 }
 assert.ok(max/min<1.09);
});

test('2D directed layout keeps entry points before processing stages while separating all components',()=>{
 const graph=viewGraph(model,null,indexes);
 const positions=layout2D(graph.nodes,graph.edges);
 assert.ok(positions.get('client').x<positions.get('gateway').x);
 assert.ok(positions.get('gateway').x<positions.get('factory').x);
 assert.equal(positions.size,graph.nodes.length);
 for(const [id,p] of positions){
  assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));
  for(const [other,q] of positions)if(id!==other)assert.ok(Math.abs(p.x-q.x)>=180||Math.abs(p.y-q.y)>=88);
 }
});
