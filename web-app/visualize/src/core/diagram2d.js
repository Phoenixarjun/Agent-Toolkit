const ORDER={client:0,gateway:1,router:2,rate_limiter:3,service:4,module:5,decision:6,transform:7,processor:8,worker:9,scheduler:10,broker:11,queue:12,stream:13,pubsub:14,topic:15,cache:16,storage:17,external:18,sandbox:19};

export function layout2D(nodes,edges=[]){
  if(!nodes.length)return new Map();
  const byId=new Map(nodes.map((n,i)=>[n.id,{...n,originalIndex:i}]));
  const ranked=[...byId.values()].sort((a,b)=>(ORDER[a.role]??25)-(ORDER[b.role]??25)||a.originalIndex-b.originalIndex);
  const forwards=new Map(nodes.map(n=>[n.id,new Set()]));
  const backwards=new Map(nodes.map(n=>[n.id,new Set()]));
  const meaningful=edges.filter(e=>byId.has(e.from)&&byId.has(e.to)&&!String(e.kind||'').includes('returns_to'));
  for(const edge of meaningful){
    forwards.get(edge.from).add(edge.to);
    backwards.get(edge.to).add(edge.from);
  }
  const roots=ranked.filter(n=>n.role==='client');
  if(!roots.length)roots.push(...ranked.filter(n=>!backwards.get(n.id).size).slice(0,3));
  if(!roots.length)roots.push(ranked[0]);
  const depths=new Map(roots.map(n=>[n.id,0]));
  const queue=roots.map(n=>n.id);
  for(let i=0;i<queue.length;i++){
    const id=queue[i],distance=depths.get(id);
    for(const next of forwards.get(id)||[]){
      if(depths.has(next))continue;
      depths.set(next,Math.min(5,distance+1));queue.push(next);
    }
  }
  for(const node of ranked){
    if(depths.has(node.id))continue;
    const linked=[...backwards.get(node.id)].map(id=>depths.get(id)).filter(v=>v!==undefined);
    const distance=linked.length?Math.min(...linked)+1:Math.min(5,1+Math.floor(depths.size/5));
    depths.set(node.id,Math.min(5,distance));
  }
  const layers=new Map();
  for(const node of ranked){
    const depth=depths.get(node.id);
    if(!layers.has(depth))layers.set(depth,[]);
    layers.get(depth).push(node.id);
  }
  const orderedLayers=[...layers].sort((a,b)=>a[0]-b[0]);
  const neighbors=new Map(nodes.map(n=>[n.id,new Set()]));
  for(const edge of meaningful){neighbors.get(edge.from).add(edge.to);neighbors.get(edge.to).add(edge.from);}
  const stable=new Map(ranked.map((n,i)=>[n.id,i]));
  for(let pass=0;pass<8;pass++){
    const sweep=pass%2===0?orderedLayers:orderedLayers.toReversed();
    for(const [depth,ids] of sweep){
      const adjacent=layers.get(depth+(pass%2===0?-1:1));
      if(!adjacent)continue;
      const index=new Map(adjacent.map((id,i)=>[id,i]));
      const barycenter=id=>{
        const positions=[...neighbors.get(id)].filter(n=>index.has(n)).map(n=>index.get(n));
        return positions.length?positions.reduce((a,b)=>a+b,0)/positions.length:null;
      };
      const old=new Map(ids.map((id,i)=>[id,i]));
      ids.sort((a,b)=>{
        const va=barycenter(a),vb=barycenter(b);
        if(va!==null&&vb!==null)return va-vb||old.get(a)-old.get(b);
        if(va!==null)return -1;
        if(vb!==null)return 1;
        return stable.get(a)-stable.get(b);
      });
    }
  }
  const maxCount=Math.max(...orderedLayers.map(([,ids])=>ids.length));
  const rowGap=maxCount>6?150:174;
  const columnGap=258;
  const levels=orderedLayers.map(([depth])=>depth);
  const origin=(levels[0]+levels.at(-1))/2;
  return new Map(orderedLayers.flatMap(([depth,ids])=>ids.map((id,i)=>[
    id,{x:(depth-origin)*columnGap,y:(i-(ids.length-1)/2)*rowGap}
  ])));
}

export function connectionPath(from,to,offset=0){
  const dx=to.x-from.x,dy=to.y-from.y;
  const horizontal=Math.abs(dx)>=Math.abs(dy);
  const ux=horizontal?(dx>=0?1:-1):0;
  const uy=horizontal?0:(dy>=0?1:-1);
  const sx=from.x+ux*99,sy=from.y+uy*51,ex=to.x-ux*99,ey=to.y-uy*51;
  const midX=(sx+ex)/2,midY=(sy+ey)/2;
  const normal=horizontal?{x:0,y:1}:{x:1,y:0};
  const cx=midX+normal.x*offset,cy=midY+normal.y*offset;
  return {start:{x:sx,y:sy},control:{x:cx,y:cy},end:{x:ex,y:ey},d:`M ${sx} ${sy} Q ${cx} ${cy} ${ex} ${ey}`};
}

export function quadraticPoint(path,fraction){
  const t=Math.max(0,Math.min(1,fraction)),u=1-t;
  return {x:u*u*path.start.x+2*u*t*path.control.x+t*t*path.end.x,y:u*u*path.start.y+2*u*t*path.control.y+t*t*path.end.y};
}

export function cameraFor(nodes,positions,aspect=1.5){
  const pts=nodes.map(n=>positions.get(typeof n==='string'?n:n.id)).filter(Boolean);
  if(!pts.length)return {x:0,y:0,width:1000,height:650};
  const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y);
  const minX=Math.min(...xs)-150,maxX=Math.max(...xs)+150,minY=Math.min(...ys)-125,maxY=Math.max(...ys)+125;
  const cx=(minX+maxX)/2,cy=(minY+maxY)/2;
  const ratio=Math.max(.4,Math.min(5,aspect));
  const width=Math.max(460,maxX-minX,(maxY-minY)*ratio);
  return {x:cx-width/2,y:cy-width/(2*ratio),width,height:width/ratio};
}

export function zoomAt(camera,point,factor){
  const f=Math.max(.25,Math.min(4,factor));
  const w=camera.width*f,h=camera.height*f;
  const relativeX=(point.x-camera.x)/camera.width,relativeY=(point.y-camera.y)/camera.height;
  return {x:point.x-relativeX*w,y:point.y-relativeY*h,width:w,height:h};
}

export function quadraticArc(path,segments=32){
  const count=Math.max(4,Math.min(128,Math.floor(segments)));
  const samples=[{fraction:0,point:quadraticPoint(path,0),length:0}];
  let total=0;
  for(let i=1;i<=count;i++){
    const point=quadraticPoint(path,i/count),previous=samples[i-1].point;
    total+=Math.hypot(point.x-previous.x,point.y-previous.y);
    samples.push({fraction:i/count,point,length:total});
  }
  return {samples,total};
}

export function pointOnQuadraticArc(path,table,fraction){
  if(table.total<=0)return quadraticPoint(path,0);
  const target=Math.max(0,Math.min(1,fraction))*table.total;
  let lo=0,hi=table.samples.length-1;
  while(hi-lo>1){const mid=(hi+lo)>>1;if(table.samples[mid].length<target)lo=mid;else hi=mid;}
  const a=table.samples[lo],b=table.samples[hi],ratio=(target-a.length)/Math.max(1e-9,b.length-a.length);
  return quadraticPoint(path,a.fraction+(b.fraction-a.fraction)*ratio);
}

function compactRoute(points){
  const clean=[];
  for(const p of points){if(!clean.length||Math.hypot(p.x-clean.at(-1).x,p.y-clean.at(-1).y)>.01)clean.push(p);}
  let i=1;
  while(i<clean.length-1){
    const a=clean[i-1],b=clean[i],c=clean[i+1];
    if(Math.abs((b.x-a.x)*(c.y-b.y)-(b.y-a.y)*(c.x-b.x))<.01)clean.splice(i,1);
    else i++;
  }
  return clean;
}

function segmentHitsRect(a,b,rect){
  const x1=rect.x-104,x2=rect.x+104,y1=rect.y-58,y2=rect.y+58;
  if(Math.abs(a.x-b.x)<.01)return a.x>x1&&a.x<x2&&Math.max(a.y,b.y)>y1&&Math.min(a.y,b.y)<y2;
  if(Math.abs(a.y-b.y)<.01)return a.y>y1&&a.y<y2&&Math.max(a.x,b.x)>x1&&Math.min(a.x,b.x)<x2;
  return true;
}

export function pointOnRoute(route,fraction){
  const points=route.points,distances=route.lengths,total=route.length;
  if(!total)return points[0]||{x:0,y:0};
  const target=Math.max(0,Math.min(1,fraction))*total;
  for(let i=1;i<points.length;i++)if(target<=distances[i]||i===points.length-1){
    const portion=(target-distances[i-1])/Math.max(.0001,distances[i]-distances[i-1]);
    return {x:points[i-1].x+(points[i].x-points[i-1].x)*portion,y:points[i-1].y+(points[i].y-points[i-1].y)*portion};
  }
  return points.at(-1);
}

export function routeConnection(edge,positions,nodes=[],offset=0){
  const from=positions.get(edge.from);
  if(!from)return null;
  const to=positions.get(edge.to)||{x:from.x+275,y:from.y+110};
  const dx=to.x-from.x,dy=to.y-from.y;
  const horizontal=Math.abs(dx)>90||Math.abs(dx)>=Math.abs(dy)*.95;
  const sx=horizontal?(dx>=0?1:-1):0,sy=horizontal?0:(dy>=0?1:-1);
  const start={x:from.x+sx*94,y:from.y+sy*48};
  const end={x:to.x-sx*94,y:to.y-sy*48};
  const obstacles=nodes.filter(n=>n.id!==edge.from&&n.id!==edge.to).map(n=>positions.get(n.id)).filter(p=>p&&p.x>=Math.min(from.x,to.x)-220&&p.x<=Math.max(from.x,to.x)+220&&p.y>=Math.min(from.y,to.y)-200&&p.y<=Math.max(from.y,to.y)+200);
  const all=[start,end,...obstacles];
  const minX=Math.min(...all.map(p=>p.x))-135,maxX=Math.max(...all.map(p=>p.x))+135;
  const minY=Math.min(...all.map(p=>p.y))-110,maxY=Math.max(...all.map(p=>p.y))+110;
  const xValues=[(start.x+end.x)/2+offset,start.x+sx*40,end.x-sx*40,minX,maxX];
  const yValues=[(start.y+end.y)/2+offset,start.y+sy*40,end.y-sy*40,minY,maxY];
  for(const rect of obstacles){xValues.push(rect.x-112,rect.x+112);yValues.push(rect.y-65,rect.y+65);}
  const candidates=[];
  for(const x of xValues)candidates.push([start,{x,y:start.y},{x,y:end.y},end]);
  for(const y of yValues)candidates.push([start,{x:start.x,y},{x:end.x,y},end]);
  for(const y of [minY,maxY])for(const x of [start.x+sx*36,end.x-sx*36])candidates.push([start,{x,y:start.y},{x,y},{x:end.x-sx*36,y},{x:end.x-sx*36,y:end.y},end]);
  let winner=null,best=Infinity;
  for(const candidate of candidates){
    const points=compactRoute(candidate);
    let length=0,hits=0;
    for(let i=1;i<points.length;i++){
      length+=Math.hypot(points[i].x-points[i-1].x,points[i].y-points[i-1].y);
      for(const rect of obstacles)if(segmentHitsRect(points[i-1],points[i],rect))hits++;
    }
    const penalty=hits*100000+length+(points.length-2)*22;
    if(penalty<best){best=penalty;winner=points;}
  }
  const points=winner||[start,end];
  const lengths=[0];
  for(let i=1;i<points.length;i++)lengths.push(lengths.at(-1)+Math.hypot(points[i].x-points[i-1].x,points[i].y-points[i-1].y));
  const d=points.map((p,i)=>`${i?'L':'M'} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' ');
  return {start,end,points,lengths,length:lengths.at(-1),d};
}
