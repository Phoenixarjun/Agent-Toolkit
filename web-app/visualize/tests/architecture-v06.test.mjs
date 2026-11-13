import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateModel,viewGraph} from '../src/core/model.js';
import {flowFocus,focusAppearance} from '../src/core/focus.js';
import {sliceGraph,semanticGroups,enumerateJourneyPaths,playbackNeedsPath,assessJourney} from '../src/core/flow.js';
import {layout2D,routeConnection,pointOnRoute} from '../src/core/diagram2d.js';

const demo=JSON.parse(readFileSync(new URL('../data/demo.json',import.meta.url),'utf8'));
const indices=validateModel(demo);
const refs=[{path:'app/entry.ts',repository:'a'}];

function branched(){
  const fixture=structuredClone(demo);
  const steps=[
    {id:'entry',component_id:'client',action:'start'},
    {id:'route',component_id:'gateway',action:'route'},
    {id:'option-a',component_id:'factory',action:'try model A'},
    {id:'option-b',component_id:'provider',action:'try model B'},
  ];
  const all=fixture.relations;
  const between=(from,to)=>all.find(r=>r.from===from&&r.to===to)?.id;
  fixture.scenarios=[];
  fixture.journeys=[{id:'branch',name:'Alternative model selection',steps,execution_edges:[
    {id:'a',from_step_id:'entry',to_step_id:'route',type:'sequence',via_relation_id:between('client','gateway')},
    {id:'b',from_step_id:'route',to_step_id:'option-a',type:'branch',condition:'candidate A allowed',via_relation_id:between('gateway','factory')},
    {id:'c',from_step_id:'route',to_step_id:'option-b',type:'branch',condition:'candidate B allowed'},
  ]}];
  return fixture;
}

test('flow focus includes inferred unique routes and fades unrelated nodes without concealing a confirmed fault',()=>{
  const graph=viewGraph(demo,null,indices);
  const focus=flowFocus(demo.journeys[0],graph,null,indices,true);
  assert.equal(focus.enabled,true);
  assert.ok(focus.nodeIds.has('factory'));
  assert.equal(focusAppearance(focus,'node','cache'),focus.nodeIds.has('cache')?'participating':'muted');
  assert.ok(focus.edgeIds.size>0);
  assert.equal(focusAppearance(focus,'edge','unlisted-edge'),'muted');
  assert.equal(focusAppearance(focus,'node','unlisted-node',true),'normal');
  assert.equal(focusAppearance(flowFocus(null,graph,null,indices,false),'node','anything'),'normal');
});

test('semantic grouping honors explicit domains and retains inbound and outbound cross-group handoffs',()=>{
  const components=[],relations=[];
  for(let i=0;i<85;i++)components.push({id:`s${i}`,name:`Service ${i}`,role:'service',domain:i<35?'Identity':i<65?'Analytics':'Billing'});
  for(let i=1;i<85;i++)relations.push({id:`e${i}`,from:`s${i-1}`,to:`s${i}`,direction:'forward',kind:'calls',evidence_status:'INFERRED',fault_status:'NONE'});
  const graph={nodes:components,edges:relations};
  const groups=semanticGroups(graph,40);
  assert.equal(groups.reduce((n,g)=>n+g.nodes.length,0),85);
  assert.deepEqual(new Set(groups.flatMap(g=>g.nodes.map(n=>n.id))).size,85);
  assert.ok(groups.every(g=>new Set(g.nodes.map(n=>n.domain)).size===1));
  const pages=groups.map((_,i)=>sliceGraph(graph,i,40));
  assert.ok(pages.some(p=>p.edges.some(e=>e.boundaryDirection==='incoming')));
  assert.ok(pages.some(p=>p.edges.some(e=>e.boundaryDirection==='outgoing')));
  assert.ok(pages.every(p=>p.nodes.length<=40));
});

test('orthogonal routing avoids an unrelated card and packet advances by actual route distance',()=>{
  const nodes=[{id:'a',role:'gateway'},{id:'b',role:'service'},{id:'obstacle',role:'worker'}];
  const positions=new Map([['a',{x:-300,y:0}],['b',{x:300,y:0}],['obstacle',{x:0,y:0}]]);
  const edge={id:'edge',from:'a',to:'b',kind:'calls',direction:'forward'};
  const route=routeConnection(edge,positions,nodes);
  assert.match(route.d,/L/);
  assert.ok(route.length>0);
  for(let i=1;i<route.points.length;i++){
    const a=route.points[i-1],b=route.points[i];
    const vertical=Math.abs(a.x-b.x)<.01,horizontal=Math.abs(a.y-b.y)<.01;
    assert.ok(vertical||horizontal);
    if(vertical)assert.ok(!(a.x>-104&&a.x<104&&Math.max(a.y,b.y)>-58&&Math.min(a.y,b.y)<58));
    if(horizontal)assert.ok(!(a.y>-58&&a.y<58&&Math.max(a.x,b.x)>-104&&Math.min(a.x,b.x)<104));
  }
  const origin=pointOnRoute(route,0),target=pointOnRoute(route,1);
  assert.deepEqual(origin,route.start);assert.deepEqual(target,route.end);
  const segmentDistances=[];
  for(let i=1;i<30;i++){
    const a=pointOnRoute(route,(i-1)/30),b=pointOnRoute(route,i/30);
    assert.ok(Number.isFinite(b.x)&&Number.isFinite(b.y));
    segmentDistances.push(Math.hypot(b.x-a.x,b.y-a.y));
  }
  assert.ok(Math.max(...segmentDistances)<route.length/30*1.01);
});

test('branched execution graph is explicit, validates, and never autoplays a guessed branch',()=>{
  const model=branched();const ix=validateModel(model);const journey=model.journeys[0];
  assert.equal(playbackNeedsPath(journey),true);
  const paths=enumerateJourneyPaths(journey);
  assert.equal(paths.length,2);
  assert.ok(paths.every(p=>p.ids[0]==='entry'&&p.ids[1]==='route'));
  assert.deepEqual(new Set(paths.map(p=>p.ids.at(-1))),new Set(['option-a','option-b']));
  assert.ok(assessJourney(journey,ix).edges.length===3);
  journey.playback_path=paths[0].ids;
  assert.doesNotThrow(()=>validateModel(model));
  assert.equal(playbackNeedsPath(journey),false);
  journey.playback_path=['entry','option-b'];
  assert.throws(()=>validateModel(model),/undeclared transition/);
});

test('new behavioral roles can be used without forcing vendor-specific nodes',()=>{
  const fixture=structuredClone(demo);
  for(const [i,role] of ['dns','cdn','ingress','firewall','identity','discovery','workflow','function','observability','cluster','subscription'].entries()){
    fixture.components.push({id:`extra-role-${i}`,name:role,role,responsibility:`Performs ${role} work`,parent_id:null,evidence_status:'INFERRED',source_refs:refs,capabilities:['inspect','route']});
  }
  const ix=validateModel(fixture);
  assert.equal(ix.components.size,46);
  fixture.components.at(-1).capabilities=[''];
  assert.throws(()=>validateModel(fixture),/invalid behavior capabilities/);
});

test('2D layout remains deterministic and component-separated at the current group size',()=>{
  const graph=viewGraph(demo,null,indices);
  const positions=layout2D(graph.nodes,graph.edges);
  assert.deepEqual([...positions],[...layout2D(graph.nodes,graph.edges)]);
  for(const [id,p] of positions)for(const [other,q] of positions)if(id!==other)assert.ok(Math.abs(p.x-q.x)>=180||Math.abs(p.y-q.y)>=88);
});


test('single-page scope preserves nodes and metadata for ordinary small repositories',()=>{
  const graph=viewGraph(demo,null,indices);
  const slice=sliceGraph(graph,0,40);
  assert.equal(slice.pages,1);
  assert.equal(slice.nodes.length,graph.nodes.length);
  assert.equal(slice.groups[0].ids.length,graph.nodes.length);
  assert.equal(slice.groupLabel,'System architecture');
});
