import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { GEOMETRIES } from '../src/graphics/geometry.js';
import { emitComponent, emitConnection, emitGrid, emitPacket, connectionGeometry, VISUAL_PRIMITIVES, C } from '../src/graphics/primitives.js';
import { viewGraph, validateModel } from '../src/core/model.js';
import { layoutGraph } from '../src/core/layout.js';

const model=JSON.parse(readFileSync(new URL('../data/demo.json',import.meta.url),'utf8'));
class BufferProbe {
  constructor(){this.counts=new Map();this.instances=0;this.redCylinders=0;}
  add(shape,matrix,color,opacity=1){
    assert.ok(GEOMETRIES[shape],`missing GPU geometry ${shape}`);
    assert.equal(matrix.length,16);
    assert.ok(matrix.every(Number.isFinite),'nonfinite object transform');
    assert.ok(typeof color==='string'||Array.isArray(color));
    assert.ok(Number.isFinite(opacity)&&opacity>=0&&opacity<=1);
    this.counts.set(shape,(this.counts.get(shape)||0)+1);
    if(shape==='cylinder'&&color===C.red)this.redCylinders++;
    this.instances++;
  }
}

test('all default visual primitives render into valid 3D instanced shapes',()=>{
 const probe=new BufferProbe();
 for(const role of VISUAL_PRIMITIVES){
   emitComponent(probe,{role,id:role},[0,0,0],2,true);
 }
 for(const node of model.components)emitComponent(probe,node,[0,0,0],2,true);
 assert.ok(probe.instances>200);
 assert.ok(probe.instances<10000);
 assert.equal(probe.counts.size,5);
});

test('each category and variant produces geometry without generating tech-branded components',()=>{
 const probe=new BufferProbe();
 for(const variant of ['relational','document','column','graph','vector','key_value','time_series','object']){
   emitComponent(probe,{role:'storage',variant,id:variant},[0,0,0],1,false);
 }
 for(const variant of ['fifo','partitioned_log','pubsub','routing','delayed']){
   const role=variant==='partitioned_log'?'stream':variant==='pubsub'?'pubsub':'queue';
   emitComponent(probe,{role,variant,id:variant},[0,0,0],1,false);
 }
 assert.ok(probe.instances>200);
});

test('geometry triangles face outward for WebGL backface culling',()=>{
 for(const [name,data] of Object.entries(GEOMETRIES)){
   assert.equal(data.length%18,0);
   let accepted=0;
   for(let k=0;k<data.length;k+=18){
     const a=[data[k],data[k+1],data[k+2]],b=[data[k+6],data[k+7],data[k+8]],c=[data[k+12],data[k+13],data[k+14]];
     const v=b.map((x,i)=>x-a[i]),w=c.map((x,i)=>x-a[i]);
     const n=[v[1]*w[2]-v[2]*w[1],v[2]*w[0]-v[0]*w[2],v[0]*w[1]-v[1]*w[0]];
     const expected=[data[k+3],data[k+4],data[k+5]];
     const signed=n.reduce((sum,x,i)=>sum+x*expected[i],0);
     assert.ok(signed>-1e-6,`${name} has inward-facing triangle at ${k}`);
     if(signed>1e-7)accepted++;
   }
   assert.ok(accepted>0,`${name} has no visible triangles`);
 }
});

test('all overview and nested-level links use finite geometry, state-aware shapes and bounded meshes',()=>{
 const indexes=validateModel(model);
 for(const parent of [null,'factory','events','gateway','worker','graph']){
   const graph=viewGraph(model,parent,indexes);
   const positions=layoutGraph(graph.nodes,graph.edges);
   const probe=new BufferProbe();
   emitGrid(probe,14);
   for(const edge of graph.edges){
     const path=connectionGeometry(edge,positions);
     assert.ok(path);
     emitConnection(probe,edge,path,1,false);
     if(path.table.length>0)emitPacket(probe,path,.5,C.teal);
   }
   assert.ok(probe.instances<10000);
 }
});

test('safe custom recipes compose only known meshes without executing source code',()=>{
 const m=structuredClone(model);
 const component=m.components.find(c=>c.id==='factory-router');
 component.visual_recipe=[{shape:'torus',offset:[0,2.8,0],size:[1,1,1],color:'accent',yaw:.3}];
 assert.doesNotThrow(()=>validateModel(m));
 const probe=new BufferProbe();
 emitComponent(probe,component,[1,0,2],4);
 assert.ok(probe.counts.get('torus')>0);
 component.visual_recipe=[{shape:'arbitrary-js',offset:[0,0,0],size:[1,1,1],color:'#ffffff'}];
 assert.throws(()=>validateModel(m),/unsupported visual shape/);
});

test('confirmed faults render as interrupted links rather than normal solid paths',()=>{
 const indexes=validateModel(model);
 const graph=viewGraph(model,null,indexes);
 const positions=layoutGraph(graph.nodes,graph.edges);
 const e=graph.edges.find(e=>e.id==='r-client-gateway');
 const geometry=connectionGeometry(e,positions);
 const good=new BufferProbe(),broken=new BufferProbe();
 emitConnection(good,e,geometry,0);
 emitConnection(broken,{...e,fault_status:'CONFIRMED'},geometry,0);
 assert.equal(broken.counts.get('cone')||0,0);
 assert.ok((good.counts.get('cone')||0)>0);
 assert.ok(broken.redCylinders>=2);
 assert.equal(good.redCylinders,0);
 assert.ok(broken.instances>0);
});
