import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { layoutGraph } from '../src/core/layout.js';
import { FIXED_STEP, FixedClock, pointOnCurve, arcLengthTable, pointAtArcDistance, motionProfile, traveledAt, distance } from '../src/core/motion.js';
import { compose, lookAt, perspective, multiply, transformPoint, cylinderBetween } from '../src/graphics/math.js';
import { connectionGeometry, relationColor } from '../src/graphics/primitives.js';
import { viewGraph, validateModel } from '../src/core/model.js';
const model=JSON.parse(readFileSync(new URL('../data/demo.json',import.meta.url),'utf8'));

test('force layout is deterministic, finite, and collision-separated',()=>{
 const graph=viewGraph(model,null,validateModel(model));
 const a=layoutGraph(graph.nodes,graph.edges);
 const b=layoutGraph(graph.nodes,graph.edges);
 assert.deepEqual([...a],[...b]);
 for(const [id,p] of a){
   assert.ok(p.every(Number.isFinite),`bad position for ${id}`);
   for(const [other,q] of a)if(other!==id)assert.ok(distance(p,q)>=2.95,`overlap ${id} ${other}: ${distance(p,q)}`);
 }
});

test('force layout rejects unbounded graph requests',()=>{
 const nodes=Array.from({length:100},(_,i)=>({id:`n${i}`,role:'service'}));
 assert.throws(()=>layoutGraph(nodes,[]),/maximum/);
});

test('arc-length sampling preserves endpoints and monotonic travel',()=>{
 const a=[0,2,0],b=[10,2,4],bend=[5,5,8];
 const table=arcLengthTable(a,b,bend);
 assert.deepEqual(pointAtArcDistance(a,b,bend,table,0),a);
 assert.ok(distance(pointAtArcDistance(a,b,bend,table,table.length),b)<1e-8);
 assert.ok(table.length>distance(a,b));
 assert.ok(table.entries.every((v,i)=>i===0||v.length>=table.entries[i-1].length));
 assert.deepEqual(pointOnCurve(a,b,bend,.5),[5,3.5,5]);
});

test('trapezoid and triangle motion profiles never overshoot',()=>{
 for(const length of [0,.1,1,3,10,100]){
   const p=motionProfile(length,5,12);
   assert.ok(Number.isFinite(p.duration));
   assert.ok(Math.abs(traveledAt(p,p.duration)-length)<1e-8);
   let prev=-1;
   for(let i=0;i<=100;i++){
     const position=traveledAt(p,p.duration*i/100);
     assert.ok(position>=prev-1e-8&&position<=length+1e-8);
     prev=position;
   }
 }
});

test('fixed time step produces identical progression under different frame rates',()=>{
 const a=new FixedClock(),b=new FixedClock();let ticksA=0,ticksB=0;
 for(let i=0;i<60;i++)a.advance(1/60,()=>ticksA++);
 for(let i=0;i<120;i++)b.advance(1/120,()=>ticksB++);
 assert.equal(ticksA,60);assert.equal(ticksB,60);
 assert.ok(Math.abs(a.time-b.time)<1e-12);
});

test('bidirectional links retain direction while undefined consumer does not invent a node',()=>{
 const indexes=validateModel(model);
 const graph=viewGraph(model,null,indexes);
 const positions=layoutGraph(graph.nodes,graph.edges);
 const cache=graph.edges.find(e=>e.id==='r-factory-cache');
 const geom=connectionGeometry(cache,positions);
 assert.equal(cache.direction,'bidirectional');
 assert.ok(geom.table.length>0);
 const unknown=graph.edges.find(e=>e.id==='r-billing-missing');
 assert.ok(unknown);
 assert.equal(unknown.to,null);
 const inner=viewGraph(model,'events',indexes);
 const bad=inner.edges.find(e=>e.id==='r-billing-missing');
 assert.ok(bad);
 assert.equal(bad.to,null);
 assert.ok(connectionGeometry(bad,layoutGraph(inner.nodes,inner.edges)));
});

test('3D camera math maintains target at viewport center and edge transforms finite',()=>{
 const camera=[10,20,30],target=[0,1,0];
 const vp=multiply(perspective(1.1,1.4,.1,100),lookAt(camera,target));
 const p=transformPoint(vp,target);
 assert.ok(Math.abs(p[0])<1e-8);
 assert.ok(Math.abs(p[1])<1e-8);
 assert.ok(p[2]>=-1&&p[2]<=1);
 const matrix=cylinderBetween([0,0,0],[10,10,10],.2);
 assert.equal(matrix.length,16);
 assert.ok(matrix.every(Number.isFinite));
});
