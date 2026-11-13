import {layout2D,connectionPath,quadraticPoint,quadraticArc,pointOnQuadraticArc,cameraFor,zoomAt,routeConnection,pointOnRoute} from '../core/diagram2d.js';

const NS='http://www.w3.org/2000/svg';
const svgNode=(tag,attributes={},text)=>{
  const el=document.createElementNS(NS,tag);
  for(const [key,value] of Object.entries(attributes))el.setAttribute(key,String(value));
  if(text!==undefined)el.textContent=String(text);
  return el;
};
const nameRole=role=>String(role||'component').replaceAll('_',' ');
const shortName=value=>value.length>23?`${value.slice(0,22)}…`:value;
const severity=edge=>edge.fault_status==='CONFIRMED'||edge.evidence_status==='CONTRADICTED'?'broken':edge.fault_status==='SUSPECTED'||edge.evidence_status==='UNRESOLVED'||(!edge.to&&!edge.boundary)?'uncertain':'normal';
const EDGE_COLORS={normal:'var(--diagram-edge)',broken:'var(--red)',uncertain:'var(--amber)'};

export class Diagram2D{
  constructor(svg,callbacks={}){
    this.svg=svg;this.callbacks=callbacks;this.graph={nodes:[],edges:[]};this.positions=new Map();this.layouts=new Map();this.nodeElements=new Map();this.edgeElements=new Map();this.paths=new Map();
    this.camera={x:-500,y:-325,width:1000,height:650};this.pointer=null;this.active=null;this.packet=null;this.key='';this.selectedId=null;this.focus=null;this.undoStack=[];this.clickTimer=null;this.lastClickedNode=null;
    this.initialize();
    if(typeof ResizeObserver!=='undefined'){
      this.observer=new ResizeObserver(()=>this.updateAspect());
      this.observer.observe(this.svg);
    }
  }
  initialize(){
    const defs=svgNode('defs');
    for(const [name,color] of Object.entries(EDGE_COLORS)){
      const marker=svgNode('marker',{id:`arrow-${name}`,viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:4,markerHeight:4,orient:'auto-start-reverse'});
      marker.append(svgNode('path',{d:'M 1 1 L 9 5 L 1 9 z',fill:color,stroke:'none'}));defs.append(marker);
    }
    this.svg.append(defs);
    this.grid=svgNode('g',{'class':'diagram-grid'});
    this.edges=svgNode('g',{'class':'diagram-connections'});
    this.nodes=svgNode('g',{'class':'diagram-components'});
    this.layer=svgNode('g',{'class':'diagram-activity'});
    this.svg.append(this.grid,this.edges,this.nodes,this.layer);
    this.packet=svgNode('circle',{r:9,'class':'diagram-packet',tabindex:0,role:'button','aria-label':'Inspect moving request'});
    this.packet.setAttribute('visibility','hidden');this.layer.append(this.packet);
    this.packet.addEventListener('click',()=>this.callbacks.onPacket?.());
    this.packet.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();this.callbacks.onPacket?.();}});
    this.svg.addEventListener('pointerdown',e=>this.pointerDown(e));
    this.svg.addEventListener('pointermove',e=>this.pointerMove(e));
    this.svg.addEventListener('pointerup',e=>this.pointerUp(e));
    this.svg.addEventListener('pointercancel',()=>this.pointer=null);
    this.svg.addEventListener('dblclick',e=>{const id=e.target.closest('[data-node-id]')?.dataset.nodeId||this.lastClickedNode;if(id){clearTimeout(this.clickTimer);this.clickTimer=null;this.lastClickedNode=null;this.callbacks.onEnter?.(id);}});
    this.svg.addEventListener('wheel',e=>{e.preventDefault();this.zoom(Math.exp(e.deltaY*.001),e.clientX,e.clientY);},{passive:false});
    this.svg.addEventListener('keydown',e=>{
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();this.undo();return;}
      const node=e.target.closest('[data-node-id]');
      if(node){
        if(e.key==='Enter'&&!e.altKey){e.preventDefault();this.callbacks.onInspect?.(node.dataset.nodeId);}
        if(e.key==='Enter'&&e.altKey){e.preventDefault();this.callbacks.onEnter?.(node.dataset.nodeId);}
        if(e.shiftKey&&['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){
          e.preventDefault();e.stopPropagation();
          const p=this.positions.get(node.dataset.nodeId);
          if(p){p.x+=(e.key==='ArrowLeft'?-16:e.key==='ArrowRight'?16:0);p.y+=(e.key==='ArrowUp'?-16:e.key==='ArrowDown'?16:0);this.redraw(node.dataset.nodeId);}
        }
      }else if(e.target===this.svg&&['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){
        e.preventDefault();e.stopPropagation();
        const step=28;
        this.camera.x+=(e.key==='ArrowLeft'?-step:e.key==='ArrowRight'?step:0);
        this.camera.y+=(e.key==='ArrowUp'?-step:e.key==='ArrowDown'?step:0);
        this.paintCamera();
      }
    });
  }
  setGraph(graph,key){
    this.graph=graph;this.key=key;this.undoStack=[];
    const old=this.layouts.get(key);
    this.positions=old||layout2D(graph.nodes,graph.edges);
    if(!old)this.layouts.set(key,this.positions);
    if(this.layouts.size>40)this.layouts.delete(this.layouts.keys().next().value);
    this.nodes.replaceChildren();this.edges.replaceChildren();this.nodeElements.clear();this.edgeElements.clear();this.paths.clear();
    const pairCount=new Map();
    for(const edge of graph.edges){
      const sev=severity(edge);
      const lineGroup=svgNode('g',{'class':`diagram-edge edge-${sev}`,'data-edge-id':edge.id,tabindex:0,role:'button','aria-label':`${edge.kind.replaceAll('_',' ')} from ${edge.from} to ${edge.to||edge.unresolved_target||'unknown'}`});
      const line=svgNode('path',{'class':'diagram-edge-line'});
      if(edge.boundaryDirection==='incoming')line.setAttribute('marker-start',`url(#arrow-${sev})`);
      else line.setAttribute('marker-end',`url(#arrow-${sev})`);
      if(edge.direction==='bidirectional'||edge.boundaryDirection==='bidirectional')line.setAttribute('marker-start',`url(#arrow-${sev})`);
      if(edge.boundary)lineGroup.classList.add('edge-boundary');
      const hit=svgNode('path',{'class':'diagram-edge-hit'});
      const label=svgNode('text',{'class':'diagram-edge-text','text-anchor':'middle'},edge.protocol?`${(edge.interaction||edge.kind).replaceAll('_',' ')} · ${edge.protocol}`:(edge.interaction||edge.kind).replaceAll('_',' '));
      const tip=svgNode('title',{},`${edge.kind.replaceAll('_',' ')} · ${edge.direction==='bidirectional'?'both directions':'one direction'} · ${sev}`);
      lineGroup.append(line,hit,label,tip);this.edges.append(lineGroup);
      this.edgeElements.set(edge.id,{group:lineGroup,line,hit,label});
      lineGroup.addEventListener('click',()=>this.callbacks.onRelation?.(edge.id));
      lineGroup.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();this.callbacks.onRelation?.(edge.id);}});
      const pair=[edge.from,edge.to||'outside'].sort().join('::');
      const n=pairCount.get(pair)||0;pairCount.set(pair,n+1);
      lineGroup.dataset.offset=String(n===0?0:(n%2?1:-1)*Math.ceil(n/2)*24);
    }
    for(const node of graph.nodes){
      const g=svgNode('g',{'class':`diagram-node role-${node.role}`,'data-node-id':node.id,role:'button',tabindex:0,'aria-label':`${node.name}, ${nameRole(node.role)}. Click to inspect. Double click to enter.`});
      g.append(svgNode('rect',{x:-90,y:-44,width:180,height:88,rx:16,'class':'diagram-card'}));
      const icon=svgNode('g',{'class':'diagram-icon'});this.icon(icon,node);
      const title=svgNode('text',{x:0,y:12,'text-anchor':'middle','class':'diagram-title'},shortName(node.name));
      const subtitle=svgNode('text',{x:0,y:30,'text-anchor':'middle','class':'diagram-subtitle'},node.variant?shortName(node.variant.replaceAll('_',' ')):nameRole(node.role));
      const hint=svgNode('title',{},`${node.name} · ${nameRole(node.role)} · ${node.responsibility}`);
      g.append(icon,title,subtitle,hint);
      this.nodes.append(g);this.nodeElements.set(node.id,g);
    }
    this.redraw();this.fit(false);
  }
  icon(group,node){
    const role=node.role,variant=node.variant;
    const line=d=>group.append(svgNode('path',{d}));
    const rect=(x,y,width,height,rx=3)=>group.append(svgNode('rect',{x,y,width,height,rx}));
    const circle=(cx,cy,r)=>group.append(svgNode('circle',{cx,cy,r}));
    if(role==='storage'){
      group.append(svgNode('ellipse',{cx:0,cy:-24,rx:19,ry:6}));
      line('M -19 -24 V -6 C -19 2 19 2 19 -6 V -24 M -19 -13 C -19 -5 19 -5 19 -13');
      if(variant==='relational')line('M -9 -22 V -16 M 0 -22 V -16 M 9 -22 V -16 M -12 -19 H 12');
      else if(variant==='document'){rect(-7,-22,14,10,1);line('M -4 -19 H 4 M -4 -16 H 3');}
      else if(variant==='column'||variant==='columnar'||variant==='wide_column')line('M -8 -21 V -15 M 0 -23 V -15 M 8 -20 V -15');
      else if(variant==='graph'){circle(-8,-20,2.2);circle(1,-23,2.2);circle(9,-18,2.2);line('M -6 -21 L -1 -23 M 3 -22 L 7 -19');}
      else if(variant==='vector'){circle(-8,-20,2);circle(7,-20,2);circle(0,-16,2);line('M -6 -19 L -2 -17 M 2 -17 L 5 -19');}
      else if(variant==='key_value'){line('M -8 -21 H 7 M -8 -17 H 2');circle(10,-18,2);}
      else if(variant==='time_series')line('M -12 -19 L -7 -20 L -3 -15 L 2 -24 L 7 -19 L 12 -21');
      else if(variant==='object')line('M -8 -22 L 0 -26 L 8 -22 L 0 -18 Z M -8 -22 V -15 L 0 -11 L 8 -15 V -22 M 0 -18 V -11');
    }else if(role==='dns'||role==='discovery'){
      circle(0,-18,13);line('M -12 -18 H 12 M 0 -31 V -5 M -11 -25 H 11 M -11 -11 H 11');
    }else if(role==='firewall'||role==='identity'){
      line('M 0 -32 L 17 -25 V -16 C 17 -9 9 -4 0 0 C -9 -4 -17 -9 -17 -16 V -25 Z');line('M -7 -17 L -1 -11 L 9 -23');
    }else if(role==='cdn'||role==='cluster'){
      rect(-18,-29,16,18,3);rect(2,-29,16,18,3);rect(-8,-9,16,13,3);
    }else if(role==='workflow'){
      rect(-21,-31,15,15,4);rect(7,-31,15,15,4);rect(-7,-7,15,13,4);line('M -6 -23 H 7 M 14 -16 L 2 -7');
    }else if(role==='subscription'){
      circle(-12,-20,5);circle(12,-20,5);line('M -7 -20 H 7 M 0 -20 V -5');
    }else if(role==='queue'){
      rect(-20,-28,40,25,5);for(let i=0;i<3;i++)circle(-12+i*10,-15,3);
      line('M 9 -15 H 17 M 13 -19 L 17 -15 L 13 -11');
    }else if(role==='stream'){
      rect(-21,-28,42,25,5);for(let i=0;i<3;i++)line(`M -14 -${23-i*7} H 13 M 9 -${26-i*7} L 13 -${23-i*7} L 9 -${20-i*7}`);
    }else if(role==='pubsub'){
      circle(0,-19,5);circle(-18,-8,3.5);circle(18,-8,3.5);circle(0,-32,3.5);line('M -4 -16 L -15 -9 M 4 -16 L 15 -9 M 0 -24 V -28');
    }else if(role==='broker'){
      rect(-21,-28,42,24,5);line('M -12 -16 H 12 M -4 -22 L 0 -16 L -4 -10 M 5 -22 L 9 -16 L 5 -10');
    }else if(role==='topic'){
      rect(-20,-28,40,24,5);line('M -12 -22 H 12 M -12 -16 H 12 M -12 -10 H 5');circle(13,-10,2);
    }else if(role==='cache'){
      for(let i=0;i<3;i++)line(`M -18 -${25-i*7} L 0 -${32-i*7} L 18 -${25-i*7} L 0 -${18-i*7} Z`);
    }else if(role==='gateway'||role==='router'||role==='decision'||role==='rate_limiter'){
      if(role==='decision'){
        line('M 0 -33 L 18 -18 L 0 -3 L -18 -18 Z');circle(0,-18,3);
      }else if(role==='rate_limiter'){
        rect(-16,-30,32,25,4);line('M -9 -17 H 9 M -4 -23 L 3 -17 L -4 -11');
      }else{
        circle(0,-26,5);circle(-18,-8,4);circle(18,-8,4);line('M -3 -22 L -15 -10 M 3 -22 L 15 -10');
        if(variant==='load_balancer')circle(0,-8,3);
      }
    }else if(role==='worker'||role==='scheduler'||role==='processor'||role==='transform'){
      rect(-17,-28,34,25,5);
      if(role==='scheduler'){circle(0,-16,8);line('M 0 -21 V -16 L 4 -13');}
      else if(role==='transform')line('M -9 -19 H 8 M 3 -24 L 8 -19 L 3 -14 M 9 -9 H -8 M -3 -14 L -8 -9 L -3 -4');
      else line('M -9 -17 H 9 M 0 -23 V -11');
    }else if(role==='sandbox'){
      line('M 0 -33 L -17 -27 V -14 L 0 -4 L 17 -14 V -27 Z');rect(-6,-25,12,11,2);
    }else if(role==='client'){
      rect(-21,-29,42,25,4);line('M -12 1 H 12 M 0 -4 V 1 M -14 -25 H 14');
    }else if(role==='external'){
      line('M -14 -8 C -24 -9 -25 -23 -14 -26 C -13 -35 1 -36 6 -28 C 17 -31 23 -19 16 -14 C 22 -6 12 -4 6 -4 H -13 C -21 -4 -23 -8 -14 -8 Z');
    }else if(role==='module'){
      rect(-21,-29,42,26,5);rect(-12,-24,24,17,3);line('M -7 -18 H 7 M -7 -12 H 1');
    }else{
      rect(-19,-28,38,26,6);line('M -18 -19 L 0 -10 L 18 -19 M 0 -10 V -3');
    }
  }
  relationPoints(edge){
    const from=this.positions.get(edge.from);
    const to=edge.to?this.positions.get(edge.to):null;
    if(!from)return null;
    const offset=Number(this.edgeElements.get(edge.id)?.group.dataset.offset)||0;
    return routeConnection(edge,this.positions,this.graph.nodes,offset);
  }
  redraw(changedId=null){
    for(const edge of this.graph.edges){
      if(changedId&&edge.from!==changedId&&edge.to!==changedId)continue;
      const parts=this.edgeElements.get(edge.id);if(!parts)continue;
      const path=this.relationPoints(edge);if(!path)continue;
      this.paths.set(edge.id,path);
      parts.line.setAttribute('d',path.d);parts.hit.setAttribute('d',path.d);
      const mid=pointOnRoute(path,.5);parts.label.setAttribute('x',mid.x);parts.label.setAttribute('y',mid.y-9);
    }
    for(const [id,g] of this.nodeElements){const p=this.positions.get(id);if(p)g.setAttribute('transform',`translate(${p.x} ${p.y})`);}
    this.applyState();
  }
  applyState(){
    for(const [id,node] of this.nodeElements)node.classList.toggle('is-selected',id===this.selectedId);
    const step=this.active;
    const involved=this.focus?.enabled?this.focus.nodeIds:new Set();
    for(const [id,node] of this.nodeElements)node.classList.toggle('flow-muted',involved.size>0&&!involved.has(id));
    for(const [id,item] of this.edgeElements){
      item.group.classList.toggle('flow-active',id===step?.relationId);
      const onPath=this.focus?.enabled?this.focus.edgeIds.has(id):false;
      const fault=this.focus?.faultIds.has(id);
      item.group.classList.toggle('flow-muted',Boolean(this.focus?.enabled)&&!onPath&&!fault);
      item.group.classList.toggle('flow-participating',onPath);
      item.group.classList.toggle('flow-alternative',Boolean(this.focus?.alternatives.has(id)));
    }
    const edgePath=step?.relationId?this.paths.get(step.relationId):null;
    let position=null;
    if(step?.state==='connected'&&edgePath){position=pointOnRoute(edgePath,step.reverse?1-step.fraction:step.fraction);}
    else if(step?.currentId){const p=this.positions.get(step.currentId);if(p)position={x:p.x,y:p.y-53};}
    if(position){this.packet.setAttribute('visibility','visible');this.packet.setAttribute('cx',position.x);this.packet.setAttribute('cy',position.y);}
    else this.packet.setAttribute('visibility','hidden');
  }
  setFocus(focus){this.focus=focus;this.applyState();}
  resetLayout(){this.positions=layout2D(this.graph.nodes,this.graph.edges);this.layouts.set(this.key,this.positions);this.undoStack=[];this.redraw();this.fit(false);}
  undo(){const saved=this.undoStack.pop();if(saved&&this.positions.has(saved.id)){this.positions.set(saved.id,saved.position);this.redraw(saved.id);return true;}return false;}
  setSelection(id){this.selectedId=id;this.applyState();}
  setActivity(activity){this.active=activity;this.applyState();}
  aspect(){const r=this.svg.getBoundingClientRect();return Math.max(.5,r.width/Math.max(1,r.height));}
  updateAspect(){
    const rect=this.svg.getBoundingClientRect();
    if(!rect.width||!rect.height)return;
    const height=this.camera.width/this.aspect(),centerY=this.camera.y+this.camera.height/2;
    if(Math.abs(this.camera.height-height)>.5){this.camera.height=height;this.camera.y=centerY-height/2;this.paintCamera();}
  }
  fit(animate=true,ids=[]){
    const nodes=ids.length?ids:this.graph.nodes.map(n=>n.id);
    this.camera=cameraFor(nodes,this.positions,this.aspect());this.paintCamera();
  }
  focus(id){if(this.positions.has(id))this.fit(true,[id]);}
  paintCamera(){const c=this.camera;this.svg.setAttribute('viewBox',`${c.x} ${c.y} ${c.width} ${c.height}`);}
  toWorld(clientX,clientY){
    const rect=this.svg.getBoundingClientRect();const px=(clientX-rect.left)/Math.max(1,rect.width),py=(clientY-rect.top)/Math.max(1,rect.height);
    return {x:this.camera.x+px*this.camera.width,y:this.camera.y+py*this.camera.height};
  }
  zoom(factor,x,y){
    const r=this.svg.getBoundingClientRect();const p=x===undefined?this.toWorld(r.left+r.width/2,r.top+r.height/2):this.toWorld(x,y);
    this.camera=zoomAt(this.camera,p,factor);this.paintCamera();
  }
  pointerDown(e){
    if(e.button!==0&&e.button!==2)return;
    const node=e.target.closest('[data-node-id]');
    const start=this.toWorld(e.clientX,e.clientY);
    const nodeId=e.button===0?node?.dataset.nodeId:null;
    this.pointer={id:e.pointerId,nodeId,original:nodeId?{...this.positions.get(nodeId)}:null,edgeId:e.target.closest('[data-edge-id]')?.dataset.edgeId,previous:start,startX:e.clientX,startY:e.clientY,dragged:false};
    this.svg.setPointerCapture(e.pointerId);
  }
  pointerMove(e){
    if(!this.pointer||this.pointer.id!==e.pointerId)return;
    const p=this.toWorld(e.clientX,e.clientY),delta={x:p.x-this.pointer.previous.x,y:p.y-this.pointer.previous.y};
    if(Math.abs(e.clientX-this.pointer.startX)+Math.abs(e.clientY-this.pointer.startY)>4)this.pointer.dragged=true;
    if(this.pointer.dragged){
      if(this.pointer.nodeId){
        const current=this.positions.get(this.pointer.nodeId);
        if(current){current.x+=delta.x;current.y+=delta.y;this.redraw(this.pointer.nodeId);}
      }else{
        this.camera.x-=delta.x;this.camera.y-=delta.y;this.paintCamera();
      }
    }
    this.pointer.previous=this.toWorld(e.clientX,e.clientY);
  }
  pointerUp(e){
    if(!this.pointer||this.pointer.id!==e.pointerId)return;
    const {nodeId,edgeId,dragged,original}=this.pointer;this.pointer=null;
    if(dragged&&nodeId&&original){
      const current=this.positions.get(nodeId);
      if(current){
        current.x=Math.round(current.x/16)*16;current.y=Math.round(current.y/16)*16;
        const anchor={...current};
        const free=point=>![...this.positions].some(([id,p])=>id!==nodeId&&Math.abs(point.x-p.x)<204&&Math.abs(point.y-p.y)<114);
        if(!free(current)){
          let found=false;
          for(let radius=1;radius<=16&&!found;radius++){
            const candidates=[];
            for(let x=-radius;x<=radius;x++)for(const y of [-radius,radius])candidates.push({x:anchor.x+x*32,y:anchor.y+y*32});
            for(let y=-radius+1;y<=radius-1;y++)for(const x of [-radius,radius])candidates.push({x:anchor.x+x*32,y:anchor.y+y*32});
            candidates.sort((a,b)=>Math.hypot(a.x-anchor.x,a.y-anchor.y)-Math.hypot(b.x-anchor.x,b.y-anchor.y));
            for(const candidate of candidates)if(free(candidate)){Object.assign(current,candidate);found=true;break;}
          }
        }
        this.undoStack.push({id:nodeId,position:original});if(this.undoStack.length>30)this.undoStack.shift();this.redraw();
      }
    }
    try{this.svg.releasePointerCapture(e.pointerId);}catch{}
    if(!dragged){if(nodeId){clearTimeout(this.clickTimer);this.lastClickedNode=nodeId;this.clickTimer=setTimeout(()=>{this.clickTimer=null;this.lastClickedNode=null;this.callbacks.onInspect?.(nodeId);},250);}else if(edgeId)this.callbacks.onRelation?.(edgeId);}
  }
}
