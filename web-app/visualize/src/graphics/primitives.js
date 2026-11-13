import { compose, quatAxisAngle, quatYaw, cylinderBetween, colorToRgb } from './math.js';
import { add, subtract, unit, scale, magnitude, pointOnCurve, arcLengthTable, pointAtArcDistance } from '../core/motion.js';

const C=Object.freeze({
  teal:'#319FBD',cyan:'#5C9DF2',blue:'#647CDD',violet:'#8970E6',gold:'#DBA34E',red:'#E96178',green:'#40B5A0',white:'#FFFFFF',slate:'#BAC7E1',dark:'#E8EDFA',steel:'#9DAFCF',faded:'#DDE5F2',pink:'#C48EDC'
});
const ROLE_COLORS=Object.freeze({client:C.gold,gateway:C.teal,router:C.cyan,rate_limiter:C.gold,service:C.blue,module:C.cyan,worker:C.green,scheduler:C.gold,storage:C.violet,cache:C.green,broker:C.blue,queue:C.gold,stream:C.violet,pubsub:C.pink,decision:C.gold,transform:C.teal,external:C.slate,sandbox:C.violet,processor:C.cyan,topic:C.pink,dns:C.blue,cdn:C.teal,ingress:C.blue,firewall:C.gold,identity:C.violet,discovery:C.teal,workflow:C.violet,function:C.blue,observability:C.green,cluster:C.slate,subscription:C.pink});
const VARIANT_COLORS=Object.freeze({relational:C.violet,document:C.cyan,column:C.gold,graph:C.pink,vector:C.teal,key_value:C.green,time_series:C.blue,object:C.slate,partitioned_log:C.violet,fifo:C.gold,pubsub:C.pink,routing:C.cyan,delayed:C.gold});

export function componentColor(node){return VARIANT_COLORS[node.variant] || ROLE_COLORS[node.role] || C.cyan;}
export function relationColor(edge){
  if(edge.fault_status==='CONFIRMED'||edge.evidence_status==='CONTRADICTED')return C.red;
  if(edge.fault_status==='SUSPECTED'||edge.evidence_status==='UNRESOLVED')return C.gold;
  if(edge.evidence_status==='INFERRED')return C.violet;
  return C.teal;
}

function tool(renderer,origin){
  const put=(mesh,point,size,color,rotation=[0,0,0,1],opacity=1)=>renderer.add(mesh,compose(add(origin,point),size,rotation),color,opacity);
  return {
    box:(p,s,c,r)=>put('box',p,s,c,r),
    cylinder:(p,s,c,r)=>put('cylinder',p,s,c,r),
    sphere:(p,s,c,r)=>put('sphere',p,s,c,r),
    torus:(p,s,c,r)=>put('torus',p,s,c,r),
    cone:(p,s,c,r)=>put('cone',p,s,c,r),
    segment:(a,b,w,c)=>renderer.add('cylinder',cylinderBetween(add(origin,a),add(origin,b),w),c)
  };
}

function foundation(t,color,time,selected){
  t.cylinder([0,.12,0],[3.15,.22,3.15],C.dark);
  t.cylinder([0,.26,0],[2.86,.09,2.86],C.steel);
  t.cylinder([0,.315,0],[2.55,.055,2.55],color);
  t.cylinder([0,.35,0],[2.34,.12,2.34],C.dark);
  if(selected){
    t.torus([0,.21,0],[3.6,.24,3.6],C.gold,quatAxisAngle([1,0,0],Math.PI/2));
    t.torus([0,.29,0],[3.92,.19,3.92],C.white,quatAxisAngle([1,0,0],Math.PI/2));
  }
  for(let i=0;i<4;i++){
    const a=i*Math.PI/2+Math.PI/4;
    t.sphere([Math.cos(a)*1.14,.39,Math.sin(a)*1.14],[.16,.16,.16],color);
  }
}

function server(t,color,time){
  t.box([0,1.4,0],[1.65,2.2,1.45],C.slate);
  t.box([0,1.48,.755],[1.43,1.88,.09],C.dark);
  for(let i=0;i<4;i++){
    const y=.86+i*.38;
    t.box([0,y,.82],[1.22,.22,.08],i%2?C.steel:color);
    t.sphere([.43,y,.89],[.08,.08,.08],C.green);
  }
  t.box([0,2.6,0],[1.87,.14,1.66],color);
  t.cylinder([0,2.86,0],[.16,.34,.16],C.white);
  t.sphere([0,3.08,0],[.25,.25,.25],color);
}

function client(t,color,time){
  const bob=Math.sin(time*2.1)*.06;
  t.cylinder([0,.85+bob,0],[.24,1,.24],C.gold);
  t.sphere([0,1.8+bob,0],[.76,.76,.76],C.white);
  t.box([0,1.12+bob,0],[.76,.82,.46],C.steel);
  t.segment([-.3,1.35+bob,0],[-.62,.93+bob,.08],.09,C.white);
  t.segment([.3,1.35+bob,0],[.68,1.13+bob,.12],.09,C.white);
  t.segment([-.2,.7+bob,0],[-.28,.27+bob,0],.11,C.white);
  t.segment([.2,.7+bob,0],[.28,.27+bob,0],.11,C.white);
  t.sphere([.77,1.16+bob,.12],[.37,.37,.37],color);
  t.torus([.77,1.16+bob,.12],[.94,.94,.94],C.gold,quatYaw(time*.65));
}

function gateway(t,color,time){
  t.box([-0.92,1.35,0],[.35,1.9,.5],C.steel);
  t.box([.92,1.35,0],[.35,1.9,.5],C.steel);
  t.box([0,2.42,0],[2.2,.4,.55],color);
  t.box([0,.58,0],[2.25,.22,.7],C.steel);
  t.torus([0,1.42,0],[2.5,2.5,2.5],color);
  t.sphere([0,1.42,0],[.45,.45,.45],C.white);
}

function router(t,color,time){
  t.sphere([0,1.46,0],[1.26,1.26,1.26],C.slate);
  t.torus([0,1.46,0],[2.65,2.65,2.65],color,quatYaw(time*.22));
  for(let i=0;i<5;i++){
    const angle=i*Math.PI*2/5;
    const end=[Math.cos(angle)*1.16,1.46,Math.sin(angle)*1.16];
    t.segment([0,1.46,0],end,.13,color);
    t.sphere(end,[.34,.34,.34],C.white);
  }
}

function limiter(t,color,time){
  t.torus([0,1.48,0],[3.2,3.2,3.2],color,quatAxisAngle([0,0,1],Math.PI/2));
  t.box([0,1.48,0],[.19,2.28,.16],C.white,quatAxisAngle([0,0,1],Math.sin(time*.5)*.18));
  t.box([-.76,1.47,0],[.18,1.75,.2],C.gold);
  t.box([.76,1.47,0],[.18,1.75,.2],C.gold);
  for(let i=0;i<3;i++)t.sphere([-1.05+i*.3,2.45,.2],[.17,.17,.17],i===0?C.red:C.green);
}

function module(t,color,time){
  t.box([0,1.25,0],[1.68,.65,1.54],C.steel);
  t.box([0,1.61,0],[1.38,.12,1.3],color);
  t.sphere([0,1.7,0],[.58,.58,.58],C.white);
  for(let i=0;i<5;i++){
    const q=-.7+i*.35;
    t.box([q,.85,.87],[.1,.34,.18],color);
    t.box([q,.85,-.87],[.1,.34,.18],color);
  }
  t.torus([0,2.07,0],[1.55,1.55,1.55],color,quatYaw(time*.6));
}

function worker(t,color,time){
  t.cylinder([0,.84,0],[1.3,.74,1.3],C.steel);
  t.sphere([0,1.32,0],[.66,.66,.66],color);
  const swing=Math.sin(time)*.23;
  t.segment([0,1.36,0],[.65,1.92+swing,0],.19,C.white);
  t.segment([.65,1.92+swing,0],[.96,2.48+swing,.12],.15,color);
  t.box([1.04,2.61+swing,.14],[.44,.48,.22],C.white);
  t.segment([.97,2.75+swing,.1],[.84,3,.1],.065,color);
  t.segment([1.13,2.75+swing,.1],[1.25,3,.1],.065,color);
}

function scheduler(t,color,time){
  t.cylinder([0,1.5,0],[2.18,.35,2.18],C.steel,quatAxisAngle([1,0,0],Math.PI/2));
  t.cylinder([0,1.5,.29],[1.9,.11,1.9],C.white,quatAxisAngle([1,0,0],Math.PI/2));
  t.segment([0,1.5,.4],[Math.sin(time*.12)*.75,1.5+Math.cos(time*.12)*.75,.42],.07,C.slate);
  t.segment([0,1.5,.42],[Math.sin(time*.6)*.52,1.5+Math.cos(time*.6)*.52,.45],.09,C.gold);
  t.sphere([0,1.5,.51],[.2,.2,.2],color);
  t.box([0,.65,0],[.44,.64,.44],C.steel);
}

function storage(t,color,time,variant){
  t.cylinder([0,1.21,0],[2.2,1.65,2.2],C.steel);
  t.cylinder([0,2.06,0],[2.25,.2,2.25],color);
  t.cylinder([0,.39,0],[2.25,.2,2.25],color);
  for(let i=0;i<3;i++)t.torus([0,.6+i*.42,0],[2.7,.65,2.7],color,quatAxisAngle([1,0,0],Math.PI/2));
  if(variant==='graph'){
    const pts=[[-.58,2.4,0],[.55,2.72,0],[0,3.1,.38],[.75,3.32,.22]];
    for(const [a,b] of [[0,1],[1,2],[2,3],[0,2]])t.segment(pts[a],pts[b],.055,C.white);
    for(const p of pts)t.sphere(p,[.24,.24,.24],color);
  }else if(variant==='vector'){
    for(let i=0;i<4;i++){
      const a=i*Math.PI/2;
      t.segment([0,2.44,0],[Math.cos(a)*.78,2.65,Math.sin(a)*.78],.065,C.white);
      t.cone([Math.cos(a)*.81,2.74,Math.sin(a)*.81],[.26,.34,.26],color);
    }
  }else if(variant==='column'){
    for(let i=0;i<4;i++)t.box([-.63+i*.42,2.45+(i%3)*.14,0],[.25,.62+(i%3)*.25,.4],i%2?color:C.white);
  }else if(variant==='document'){
    for(let i=0;i<3;i++)t.box([-.21+i*.22,2.4+i*.22,0],[.68,.08,.88],i%2?C.white:color);
  }else if(variant==='key_value'){
    for(let i=0;i<3;i++)t.box([-.65+i*.53,2.57,0],[.33,.33,.33],i%2?color:C.white);
  }else if(variant==='time_series'){
    for(let i=0;i<5;i++)t.segment([-.85+i*.4,2.35,0],[-.85+i*.4,2.75+Math.sin(i*1.5)*.22,0],.06,color);
  }else if(variant==='object'){
    t.box([0,2.64,0],[1.15,.75,1],color);
    t.box([0,3.07,0],[1.32,.09,1.15],C.white);
  }else{
    for(let r=0;r<2;r++)for(let col=0;col<3;col++)t.box([-.52+col*.51,2.48+r*.3,0],[.37,.2,.22],r?color:C.white);
  }
}

function queue(t,color,time,variant){
  t.box([0,.78,0],[2.15,.4,1.04],C.steel);
  t.box([0,1.03,0],[2.28,.1,1.1],color);
  for(let i=0;i<3;i++){
    const offset=((time*.27+i/3)%1)*1.9-.95;
    t.box([offset,1.29,0],[.43,.45,.5],i===1?C.white:color);
  }
  if(variant==='routing'){
    for(let i=0;i<3;i++)t.segment([0,1.65,0],[(i-1)*.72,2.3,0],.065,C.white);
  }else if(variant==='delayed'){
    t.torus([0,2.14,0],[1.45,1.45,1.45],C.gold,quatAxisAngle([1,0,0],Math.PI/2));
  }else{
    t.segment([-1.3,1.35,0],[-1.7,1.35,0],.08,color);
    t.cone([-1.74,1.35,0],[.25,.34,.25],color,quatAxisAngle([0,0,1],Math.PI/2));
  }
}

function stream(t,color,time){
  t.box([0,.7,0],[2.34,.48,1.55],C.slate);
  for(let row=0;row<3;row++){
    const z=-.52+row*.52;
    t.box([0,1.01,z],[2.08,.1,.28],row===1?C.steel:color);
    for(let col=0;col<5;col++){
      const x=-.77+col*.39;
      t.box([x,1.22,z],[.22,.25,.22],(col+row)%3===0?C.white:color);
    }
  }
  t.box([0,1.88,0],[1.36,.45,.42],C.steel);
  for(let i=0;i<4;i++)t.sphere([-.46+i*.3,1.89,.25],[.13,.13,.13],i===Math.floor(time*1.5)%4?C.white:color);
}

function pubsub(t,color,time){
  t.sphere([0,1.65,0],[1.04,1.04,1.04],C.slate);
  t.sphere([0,1.65,0],[.55,.55,.55],C.white);
  for(let i=0;i<6;i++){
    const a=i*Math.PI/3;
    const p=[Math.cos(a)*1.05,1.65+Math.sin(time*.7+i)*.12,Math.sin(a)*1.05];
    t.segment([0,1.65,0],p,.075,color);
    t.sphere(p,[.3,.3,.3],color);
  }
}

function decision(t,color,time){
  t.box([0,1.48,0],[1.3,1.3,1.3],C.steel,quatYaw(Math.PI/4));
  t.torus([0,1.45,0],[2.08,2.08,2.08],color,quatYaw(time*.32));
  t.segment([0,1.5,0],[-1,2.22,0],.08,C.green);
  t.segment([0,1.5,0],[1,2.22,0],.08,C.red);
  t.sphere([-1,2.22,0],[.25,.25,.25],C.green);
  t.sphere([1,2.22,0],[.25,.25,.25],C.red);
}

function transform(t,color,time){
  t.cylinder([0,1.37,0],[1.3,1.37,1.3],C.steel);
  t.torus([0,1.37,0],[2.8,2.8,2.8],color,quatYaw(time*.3));
  for(let i=0;i<3;i++){
    const a=time*.36+i*Math.PI*2/3;
    t.sphere([Math.cos(a)*.74,1.44,Math.sin(a)*.74],[.28,.28,.28],i===0?C.white:color);
  }
  t.segment([-1.15,1.2,0],[1.15,1.2,0],.055,C.white);
}

function sandbox(t,color,time){
  t.box([0,.39,0],[2.4,.16,2.4],C.steel);
  for(const x of [-1.03,1.03])for(const z of [-1.03,1.03])t.segment([x,.5,z],[x,2.77,z],.06,color);
  for(const y of [.53,2.77]){
    t.segment([-1.03,y,-1.03],[1.03,y,-1.03],.055,color);
    t.segment([1.03,y,-1.03],[1.03,y,1.03],.055,color);
    t.segment([1.03,y,1.03],[-1.03,y,1.03],.055,color);
    t.segment([-1.03,y,1.03],[-1.03,y,-1.03],.055,color);
  }
  t.sphere([0,1.61,0],[.8,.8,.8],C.white);
  t.torus([0,1.61,0],[1.9,1.9,1.9],color,quatYaw(time*.2));
}

function external(t,color,time){
  t.sphere([0,1.44,0],[1.22,1.22,1.22],C.steel);
  t.torus([0,1.44,0],[2.84,2.84,2.84],C.white,quatAxisAngle([0,0,1],Math.PI/3));
  t.sphere([-.92,2.35,0],[.23,.23,.23],C.white);
  t.sphere([.92,.6,0],[.23,.23,.23],C.white);
}

function broker(t,color,time,variant){
  if(variant==='routing'||variant==='fifo'||variant==='delayed')queue(t,color,time,variant);
  else pubsub(t,color,time);
}

const BUILDERS={client,gateway,router,rate_limiter:limiter,service:server,module,worker,scheduler,storage,cache:module,broker,queue,stream,pubsub,decision,transform,external,sandbox,processor:module,topic:stream,dns:router,cdn:storage,ingress:gateway,firewall:limiter,identity:sandbox,discovery:router,workflow:router,function:worker,observability:broker,cluster:server,subscription:pubsub};
export const VISUAL_PRIMITIVES=Object.freeze(Object.keys(BUILDERS));

export function emitComponent(renderer,node,position,time=0,selected=false){
  const color=componentColor(node);
  const t=tool(renderer,position);
  foundation(t,color,time,selected);
  (BUILDERS[node.role]||module)(t,color,time,node.variant||'generic');
  if(node.role==='gateway'&&node.variant==='load_balancer'){
    for(let i=0;i<3;i++){
      const a=i*Math.PI*2/3;
      t.sphere([Math.sin(a)*.85,2.75,Math.cos(a)*.85],[.2,.2,.2],color);
    }
  }
  if(node.role==='cache'){
    t.torus([0,2.55,0],[1.5,1.5,1.5],C.green,quatAxisAngle([0,0,1],.2));
  }
  if(Array.isArray(node.visual_recipe)){
    for(const part of node.visual_recipe){
      const rotate=quatYaw(part.yaw||0);
      renderer.add(part.shape,compose(add(position,part.offset),part.size,rotate),part.color==='accent'?color:part.color);
    }
  }
}

export function connectionGeometry(edge,positions){
  if(!positions.has(edge.from))return null;
  const start=add(positions.get(edge.from),[0,1.53,0]);
  const radial=unit([start[0],0,start[2]]);
  const end=edge.to && positions.has(edge.to)?add(positions.get(edge.to),[0,1.53,0]):add(start,scale(radial[1]===1?[1,0,-.35]:radial,4.2));
  const heading=unit(subtract(end,start));
  const begin=add(start,scale(heading,edge.to?1.68:1.1));
  const finish=edge.to?add(end,scale(heading,-1.68)):end;
  const dir=unit(subtract(finish,begin));
  const perp=[-dir[2],0,dir[0]];
  const lane=edge.direction==='bidirectional'?.32:0;
  const bend=add(scale(add(begin,finish),.5),add([0,1.12,0],scale(perp,1.3+lane)));
  return {start:begin,end:finish,bend,table:arcLengthTable(begin,finish,bend),perp};
}

export function emitConnection(renderer,edge,geometry,time,selected=false){
  if(!geometry)return;
  const color=selected&&edge.fault_status!=='CONFIRMED'?C.violet:relationColor(edge);
  const broken=edge.fault_status==='CONFIRMED';
  const pending=!broken&&(edge.evidence_status==='UNRESOLVED'||edge.evidence_status==='INFERRED'||edge.fault_status==='SUSPECTED'||edge.evidence_status==='CONTRADICTED');
  const n=32;
  for(let i=0;i<n;i++){
    const t0=i/n,t1=(i+1)/n;
    if(broken && (i===14||i===15||i===16||i===17))continue;
    const a=pointOnCurve(geometry.start,geometry.end,geometry.bend,t0);
    const b=pointOnCurve(geometry.start,geometry.end,geometry.bend,t1);
    if(pending)renderer.add('cylinder',cylinderBetween(a,b,.021),C.faded);
    if(pending && i%4>=2)continue;
    renderer.add('cylinder',cylinderBetween(a,b,selected?.11:.046),color);
  }
  if(broken){
    const p=pointOnCurve(geometry.start,geometry.end,geometry.bend,.5);
    renderer.add('cylinder',cylinderBetween(add(p,[-.22,-.24,0]),add(p,[.22,.24,0]),.1),C.red);
    renderer.add('cylinder',cylinderBetween(add(p,[-.22,.24,0]),add(p,[.22,-.24,0]),.1),C.red);
  }else if(edge.boundaryDirection!=='incoming'){
    const p=pointOnCurve(geometry.start,geometry.end,geometry.bend,.93);
    const tangent=unit(subtract(pointOnCurve(geometry.start,geometry.end,geometry.bend,.95),pointOnCurve(geometry.start,geometry.end,geometry.bend,.9)));
    const q=quatFromY(tangent);
    renderer.add('cone',compose(p,[.28,.44,.28],q),color);
    if(edge.direction==='bidirectional'){
      const startP=pointOnCurve(geometry.start,geometry.end,geometry.bend,.07);
      const backward=unit(subtract(pointOnCurve(geometry.start,geometry.end,geometry.bend,.04),pointOnCurve(geometry.start,geometry.end,geometry.bend,.09)));
      renderer.add('cone',compose(startP,[.25,.38,.25],quatFromY(backward)),color);
    }
  }
  if(!edge.to){
    const terminalColor=edge.boundary?C.cyan:C.gold;
    renderer.add('torus',compose(geometry.end,[.68,.68,.68],quatAxisAngle([1,0,0],Math.PI/2)),terminalColor);
    renderer.add('sphere',compose(geometry.end,[.23,.23,.23]),terminalColor);
  }
  if(edge.boundaryDirection==='incoming'||edge.boundaryDirection==='bidirectional'){
    const p=pointOnCurve(geometry.start,geometry.end,geometry.bend,.07);
    const back=unit(subtract(pointOnCurve(geometry.start,geometry.end,geometry.bend,.03),pointOnCurve(geometry.start,geometry.end,geometry.bend,.11)));
    renderer.add('cone',compose(p,[.3,.45,.3],quatFromY(back)),color);
  }
}

function quatFromY(vector){
  const b=unit(vector),v=[b[2],0,-b[0]],d=b[1];
  if(d < -.999999)return quatAxisAngle([1,0,0],Math.PI);
  if(d > .999999)return [0,0,0,1];
  const q=[v[0],v[1],v[2],1+d];
  const norm=Math.hypot(...q);
  return q.map(x=>x/norm);
}

export function emitPacket(renderer,geometry,fraction,color=C.gold,size=.22){
  if(!geometry)return null;
  const p=geometry.table.length===0?geometry.start:pointAtArcDistance(geometry.start,geometry.end,geometry.bend,geometry.table,geometry.table.length*fraction);
  renderer.add('box',compose(p,[size*1.65,size*1.65,size*1.65],quatYaw(fraction*3)),color);
  renderer.add('torus',compose(p,[size*1.7,size*1.7,size*1.7],quatAxisAngle([1,0,0],Math.PI/2)),C.white,.84);
  return p;
}

export function emitGrid(renderer,span=50,dark=false){
  const gridStep=4;
  const range=Math.max(8,Math.min(64,Math.ceil(span/gridStep)*gridStep));
  for(let i=-range;i<=range;i+=gridStep){
    renderer.add('box',compose([i,-.15,0],[.016,.012,range*2]),dark?'#344563':C.faded,dark?.28:.55);
    renderer.add('box',compose([0,-.15,i],[range*2,.012,.016]),dark?'#344563':C.faded,dark?.28:.55);
  }
  for(let x=-range;x<=range;x+=gridStep*2)for(let z=-range;z<=range;z+=gridStep*2){
    renderer.add('sphere',compose([x,-.13,z],[.07,.07,.07]),dark?'#405677':C.steel);
  }
}

export { C };
