import { validateModel, viewGraph, projectJourney, redactPayload, visibleAtLevel } from './core/model.js';
import { projectedTransition, assessJourney, relatedImpact, sliceGraph, playbackSteps, playbackNeedsPath, enumerateJourneyPaths } from './core/flow.js';
import { flowFocus, focusAppearance } from './core/focus.js';
import { layoutGraph } from './core/layout.js';
import { FixedClock, clamp, motionProfile, traveledAt, arcLengthTable, pointOnCurve } from './core/motion.js';
import { runSyntheticScenario, changesBetween } from './core/simulation.js';
import { WebGLSceneRenderer } from './graphics/webgl.js';
import { Diagram2D } from './graphics/diagram2d.js';
import { multiply, perspective, lookAt, orbitPosition, transformPoint, compose } from './graphics/math.js';
import { emitComponent, emitConnection, emitGrid, emitPacket, connectionGeometry, componentColor, C } from './graphics/primitives.js';

const $=id=>document.getElementById(id);
const MAX_UPLOAD=8*1024*1024;
const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const ICONS={
  cube:'<rect x="4" y="4" width="16" height="16" rx="3"/><path d="m4.5 8 7.5 4 7.5-4M12 12v8"/>',
  route:'<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7 6h10M5 8v4a6 6 0 0 0 6 6"/>',
  search:'<circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/>',
  grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  layers:'<path d="m12 3 9 5-9 5-9-5 9-5Zm-9 9 9 5 9-5M3 16l9 5 9-5"/>',
  alert:'<path d="M10.1 3.6 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.9 3.6a2.1 2.1 0 0 0-3.8 0Z"/><path d="M12 9v5m0 3h.01"/>',
  help:'<circle cx="12" cy="12" r="9"/><path d="M9.7 9.1a2.6 2.6 0 1 1 3.6 2.4c-.8.5-1.3.9-1.3 1.9m0 3.3h.01"/>',
  orbit:'<ellipse cx="12" cy="12" rx="9" ry="5" transform="rotate(-30 12 12)"/><circle cx="12" cy="12" r="2"/>',
  move:'<path d="M12 2v20M2 12h20m-14-6 4-4 4 4M8 18l4 4 4-4M6 8l-4 4 4 4M18 8l4 4-4 4"/>',
  focus:'<path d="M4 9V4h5m6 0h5v5M4 15v5h5m6 0h5v-5"/><circle cx="12" cy="12" r="3"/>',
  minus:'<path d="M5 12h14"/>',
  plus:'<path d="M12 5v14M5 12h14"/>',
  play:'<path d="m8 5 11 7-11 7V5Z"/>',
  pause:'<path d="M8 5v14M16 5v14"/>',
  next:'<path d="m5 5 10 7-10 7V5Zm12 0v14"/>',
  restart:'<path d="M3 11a9 9 0 1 1 2 6M3 5v6h6"/>',
  close:'<path d="M5 5l14 14M19 5 5 19"/>',
  package:'<path d="m3 7 9-4 9 4-9 5-9-5Zm0 0v10l9 5 9-5V7M12 12v10"/>',
  database:'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
  worker:'<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M9 10h6v5H9zM12 4v3M12 17v3"/>',
  chevron:'<path d="m9 5 7 7-7 7"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  shield:'<path d="M12 2 4 5v6c0 5 3 8 8 11 5-3 8-6 8-11V5l-8-3Z"/><path d="m8 12 3 3 5-6"/>',
  moon:'<path d="M20.7 13.2A9 9 0 0 1 10.8 3.3a9 9 0 1 0 9.9 9.9Z"/>',
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>',
  upload:'<path d="M12 17V3m-5 5 5-5 5 5M4 17v3h16v-3"/>'
};
const CATALOG=[
  {group:'Boundaries & routing',name:'Client',role:'client',icon:'cube',description:'Originates requests and receives responses. Can carry symbolic payload data through a journey.'},
  {group:'Boundaries & routing',name:'API gateway',role:'gateway',icon:'route',description:'Handles entry into the platform and routes requests to responsible capabilities.'},
  {group:'Boundaries & routing',name:'Load balancer',role:'gateway',variant:'load_balancer',icon:'route',description:'Distributes incoming work across eligible instances using a defined selection policy.'},
  {group:'Boundaries & routing',name:'Router',role:'router',icon:'route',description:'Chooses a destination or processing branch according to routing rules.'},
  {group:'Boundaries & routing',name:'Rate limiter',role:'rate_limiter',icon:'alert',description:'Admits or rejects work based on a quota, window or token-budget rule.'},
  {group:'Compute & execution',name:'Service',role:'service',icon:'cube',description:'Owns an application responsibility and its externally visible interactions.'},
  {group:'Compute & execution',name:'Module',role:'module',icon:'layers',description:'Represents a logical capability contained inside a larger service or runtime.'},
  {group:'Compute & execution',name:'Worker',role:'worker',icon:'worker',description:'Processes bounded tasks, often triggered by events, queues or scheduling.'},
  {group:'Compute & execution',name:'Scheduler',role:'scheduler',icon:'clock',description:'Triggers work at specified times or according to a scheduling policy.'},
  {group:'Compute & execution',name:'Decision',role:'decision',icon:'route',description:'Evaluates a condition or policy and selects one of several outcomes.'},
  {group:'Compute & execution',name:'Transformation',role:'transform',icon:'layers',description:'Changes the shape or meaning of data between processing steps.'},
  {group:'Compute & execution',name:'Sandbox',role:'sandbox',icon:'cube',description:'Defines a bounded execution environment separated from the surrounding runtime.'},
  {group:'Data & storage',name:'Relational database',role:'storage',variant:'relational',icon:'database',description:'Persists structured records linked by relational keys and queryable relationships.'},
  {group:'Data & storage',name:'Document database',role:'storage',variant:'document',icon:'database',description:'Persists and retrieves documents with flexible structured fields.'},
  {group:'Data & storage',name:'Column database',role:'storage',variant:'column',icon:'database',description:'Organizes stored values by columns for analytical access patterns.'},
  {group:'Data & storage',name:'Graph database',role:'storage',variant:'graph',icon:'database',description:'Models connected entities and their traversable relationships.'},
  {group:'Data & storage',name:'Vector database',role:'storage',variant:'vector',icon:'database',description:'Supports retrieval by embedding similarity, often with metadata filters.'},
  {group:'Data & storage',name:'Key-value storage',role:'storage',variant:'key_value',icon:'database',description:'Provides retrieval and updates by unique keys.'},
  {group:'Data & storage',name:'Time-series database',role:'storage',variant:'time_series',icon:'database',description:'Stores time-indexed measurements and supports temporal queries.'},
  {group:'Data & storage',name:'Object storage',role:'storage',variant:'object',icon:'database',description:'Holds binary or structured objects referenced by identifiers.'},
  {group:'Data & storage',name:'Cache',role:'cache',icon:'layers',description:'Retains reusable values or results under a defined expiry and invalidation policy.'},
  {group:'Messaging & coordination',name:'Queue',role:'queue',variant:'fifo',icon:'layers',description:'Buffers work for consumption, often with ordering and acknowledgement rules.'},
  {group:'Messaging & coordination',name:'Partitioned event stream',role:'stream',variant:'partitioned_log',icon:'route',description:'Maintains append-only event sequences distributed across partitions.'},
  {group:'Messaging & coordination',name:'Message broker',role:'broker',variant:'routing',icon:'layers',description:'Routes messages between producers and consumers through declared routing semantics.'},
  {group:'Messaging & coordination',name:'Publish / subscribe',role:'pubsub',variant:'pubsub',icon:'route',description:'Fans events out from publishers to subscribed consumers.'},
  {group:'Messaging & coordination',name:'Topic',role:'topic',variant:'partitioned_log',icon:'route',description:'Declared event destination consumed by subscribers or consumer groups.'},
  {group:'Messaging & coordination',name:'Subscription',role:'subscription',icon:'layers',description:'A consumer binding to messages or events according to a subscription contract.'},
  {group:'Messaging & coordination',name:'Dead-letter queue',role:'queue',variant:'delayed',icon:'alert',description:'Retains messages that could not be processed under the configured delivery policy.'},
  {group:'Reliability & protection',name:'DNS / service naming',role:'dns',icon:'route',description:'Resolves logical destinations into reachable endpoints under a declared naming policy.'},
  {group:'Reliability & protection',name:'CDN',role:'cdn',icon:'layers',description:'Delivers edge-cached content to geographically distributed clients.'},
  {group:'Reliability & protection',name:'Ingress / reverse proxy',role:'ingress',icon:'route',description:'Forwards entry traffic into the appropriate application boundary.'},
  {group:'Reliability & protection',name:'Firewall / WAF',role:'firewall',icon:'shield',description:'Enforces inbound or outbound security constraints on traffic.'},
  {group:'Reliability & protection',name:'Identity provider',role:'identity',icon:'shield',description:'Establishes identity and issues or verifies authentication assertions.'},
  {group:'Reliability & protection',name:'Service discovery',role:'discovery',icon:'search',description:'Resolves service instances available for a requested capability.'},
  {group:'Reliability & protection',name:'Workflow coordinator',role:'workflow',icon:'route',description:'Coordinates tasks, transitions, waiting, and recovery across distributed steps.'},
  {group:'Compute & execution',name:'Function runtime',role:'function',icon:'worker',description:'Executes an invoked function in a bounded runtime context.'},
  {group:'Compute & execution',name:'Processor',role:'processor',icon:'worker',description:'Performs a processing operation inside a pipeline.'},
  {group:'Infrastructure & observation',name:'Observability collector',role:'observability',icon:'layers',description:'Receives logs, metrics, or spans from instrumented components.'},
  {group:'Infrastructure & observation',name:'Compute cluster',role:'cluster',icon:'grid',description:'Groups execution resources with a shared scheduling or placement boundary.'},
  {group:'Messaging & coordination',name:'External dependency',role:'external',icon:'cube',description:'Represents a system outside the ownership boundary of the inspected application.'}
];
const ROLE_ICONS={dns:'route',cdn:'layers',ingress:'route',firewall:'shield',identity:'shield',discovery:'search',workflow:'route',function:'worker',observability:'layers',cluster:'grid',subscription:'route',storage:'database',cache:'layers',gateway:'route',router:'route',rate_limiter:'alert',worker:'worker',scheduler:'clock',stream:'route',queue:'layers',broker:'route',pubsub:'route',decision:'route',transform:'layers'};
const ROLE_TITLES={dns:'DNS / naming',cdn:'Content delivery',ingress:'Ingress gateway',firewall:'Firewall / WAF',identity:'Identity provider',discovery:'Service discovery',workflow:'Workflow coordinator',function:'Function runtime',observability:'Observability',cluster:'Compute cluster',subscription:'Subscription',rate_limiter:'Rate limiter',storage:'Data storage',pubsub:'Publish / subscribe',stream:'Event stream',broker:'Message broker',external:'External integration',sandbox:'Sandbox runtime'};
const create=(tag,className,text)=>{const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=String(text);return node;};
const append=(parent,...nodes)=>{parent.append(...nodes);return parent;};
const safeJSON=value=>{const json=JSON.stringify(redactPayload(value??{}),null,2)||'{}';return json.length>7000?`${json.slice(0,7000)}\n…`:json;};
const stateLabel=status=>String(status||'UNKNOWN').replaceAll('_',' ').toLowerCase();
const finite=(v,fallback=0)=>Number.isFinite(v)?v:fallback;
function setIcon(node,name){node.replaceChildren();const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.innerHTML=ICONS[name]||ICONS.cube;node.append(svg);}
function initIcons(){document.querySelectorAll('[data-icon]').forEach(node=>setIcon(node,node.dataset.icon));}
function section(parent,title){const block=create('section','inspector-section');block.append(create('h3','section-title',title));parent.append(block);return block;}
function paragraph(parent,text,cls='role-description'){parent.append(create('p',cls,text));}
function chip(parent,text,kind=''){parent.append(create('span',`info-chip ${kind}`,text));}
function showPair(parent,label,value){const field=create('div','metric-item');append(field,create('div','metric-label',label),create('div','metric-value',value));parent.append(field);}
function codeCard(parent,label,value){const block=create('div');append(block,create('div','payload-label',label),create('pre','payload-code',safeJSON(value)));parent.append(block);}
function sourceBlock(parent,refs){if(!refs?.length)return;const group=section(parent,'Source evidence');for(const ref of refs.slice(0,8))group.append(create('div','source-item',`${ref.repository||'repository'} / ${ref.path}${ref.locator?' · '+ref.locator:''}`));}
function evidenceChip(parent,status){const kind=['CONFIRMED','CONTRADICTED'].includes(status)?'danger':['UNRESOLVED','SUSPECTED'].includes(status)?'warn':'evidence-chip';chip(parent,stateLabel(status),`evidence-chip ${kind}`);}

class VisualizeApp{
  constructor(){
    this.model=null;this.indexes=null;this.viewParentId=null;this.graph=null;this.positions=new Map();this.edgePaths=new Map();
    this.activeJourneyId=null;this.synthetic=null;this.playback={steps:[],index:0,phase:0,running:false,speed:1};
    this.selection={kind:'none',id:null};this.inspectorTab='overview';this.pointer={active:false,x:0,y:0,dragged:false,mode:'orbit'};
    this.camera={target:[0,.8,0],radius:30,azimuth:.62,elevation:.62};this.cameraGoal=null;this.cameraMode='orbit';
    this.renderer=null;this.clock=new FixedClock();this.lastFrame=0;this.animatedTime=0;this.labels=new Map();
    this.vp=null;this.viewport={width:1,height:1};this.hoverRelation=null;this.activePacketWorld=null;this.notificationTimeout=null;
    this.renderError=null;this.overlayKind=null;this.lastOverlayFocus=null;this.lastUIRefresh=0;
    this.fullGraph=null;this.slicePage=0;this.layoutCache=new Map();this.transitionCache=new Map();this.lastRenderTime=0;
    this.visualMode='3d';this.flowFocused=true;this.navExpanded=false;this.flowFocus=null;this.playbackSelection=new Map();
    this.diagram=new Diagram2D($('diagram-2d'),{
      onInspect:id=>this.inspectSceneNode(id),
      onEnter:id=>{if(this.model?.components.some(c=>c.parent_id===id))this.openLevel(id);},
      onRelation:id=>this.inspect({kind:'relation',id}),
      onPacket:()=>this.inspect({kind:'packet',id:this.playback.index},'flow')
    });
    this.theme=this.readTheme();this.setTheme(this.theme);
    initIcons();this.connectControls();this.setVisualMode('3d');
  }
  async start(){
    try{
      const response=await fetch('./data/demo.json',{cache:'no-store'});
      if(!response.ok)throw new Error(`Demo model HTTP ${response.status}`);
      this.loadModel(await response.json());
      try{
        this.renderer=new WebGLSceneRenderer($('world-canvas'));
        this.renderer.setTheme(this.theme);
      }catch(error){
        this.renderError=error.message;
        this.setVisualMode('2d');
        this.notify('WebGL2 is unavailable. Switched to the fully interactive 2D architecture view.');
      }
      this.raf=requestAnimationFrame(time=>this.loop(time));
      window.__visualizeReady=true;
      window.__visualizeDiagnostics=()=>({ready:true,model:this.model?.scope?.name,nodes:this.graph?.nodes.length,edges:this.graph?.edges.length,selected:this.selection,level:this.viewParentId,flow:this.activeJourneyId,inspectorOpen:!$('inspector-panel').hidden,overlay:this.overlayKind,drawCalls:this.renderer?.drawCalls,error:this.renderError,view:this.visualMode,diagramNodes:this.diagram.nodeElements.size});
    }catch(error){this.showFailure(error);}
  }
  showFailure(error){
    this.renderError=error.message;
    this.renderFallback();
    window.__visualizeReady=false;window.__visualizeDiagnostics=()=>({ready:false,error:error.message});
  }
  setVisualMode(mode){
    if(mode==='3d'&&this.renderError&&this.model){this.notify('3D graphics unavailable. Use the interactive 2D view.');mode='2d';}
    this.visualMode=mode==='2d'?'2d':'3d';
    if(this.visualMode==='2d'){$('diagram-2d').removeAttribute('hidden');$('world-fallback').hidden=true;}else $('diagram-2d').setAttribute('hidden','');
    $('world-canvas').hidden=this.visualMode!=='3d';
    $('world-labels').hidden=this.visualMode!=='3d';
    $('packet-chip').hidden=this.visualMode!=='3d';
    $('connection-chip').hidden=this.visualMode!=='3d';
    $('camera-orbit').hidden=this.visualMode==='2d';
    $('camera-pan').hidden=this.visualMode==='2d';
    for(const [id,value] of [['view-3d','3d'],['view-2d','2d']]){
      $(id).classList.toggle('active',this.visualMode===value);
      $(id).setAttribute('aria-pressed',String(this.visualMode===value));
    }
    $('scene-hint').textContent=this.visualMode==='2d'?'Drag components to move · Drag canvas to pan · Scroll to zoom':'Drag to orbit · Shift-drag to pan · Double-click to enter';
    $('reset-camera').setAttribute('aria-label',this.visualMode==='2d'?'Fit 2D diagram':'Fit 3D camera');
    if(this.visualMode==='2d'&&this.graph){this.diagram.fit(false);this.syncDiagram();}
    if(this.visualMode==='3d'&&this.graph)this.fitCamera(false);
  }
  syncDiagram(){
    if(this.visualMode!=='2d'||!this.graph)return;
    const current=this.playback.steps[this.playback.index],next=this.playback.steps[this.playback.index+1];
    const transfer=this.transitionFor(current,next);
    const edge=transfer.state==='connected'?this.graph.edges.find(e=>e.id===transfer.relation?.id):null;
    const all=[...new Set(this.playback.steps.map(group=>group.visibleId).filter(Boolean))];
    const reversed=edge&&current&&edge.from!==current.visibleId;
    this.diagram.setFocus(this.flowFocus);
    this.diagram.setActivity(this.activeJourneyId?{state:transfer.state,relationId:edge?.id,currentId:current?.visibleId,visibleIds:all,fraction:this.playback.phase,reverse:reversed}:null);
  }
  renderFallback(){
    const fallback=$('world-fallback');fallback.hidden=false;fallback.replaceChildren();
    const group=create('div','fallback-content');
    group.append(create('h2','','Architecture could not be displayed'));
    paragraph(group,`The architecture model could not be loaded or rendered. ${this.renderError||''}`);
    const list=create('div','fallback-list');
    for(const component of this.graph?.nodes||[]){
      const button=create('button','fallback-button',component.name);button.type='button';
      button.addEventListener('click',()=>this.inspectSceneNode(component.id));
      list.append(button);
    }
    group.append(list);fallback.append(group);
  }
  notify(text){
    const box=$('notification');box.textContent=text;box.hidden=false;
    clearTimeout(this.notificationTimeout);this.notificationTimeout=setTimeout(()=>{box.hidden=true;},3900);
  }
  loadModel(model){
    const indexes=validateModel(model);
    this.model=model;this.indexes=indexes;this.viewParentId=null;this.activeJourneyId=null;this.synthetic=null;this.slicePage=0;this.layoutCache.clear();this.transitionCache.clear();this.diagram.layouts.clear();
    this.playback={steps:[],index:0,phase:0,running:false,speed:1,requiresPath:false};this.playbackSelection.clear();this.selection={kind:'none',id:null};
    $('model-badge').textContent=model.scope.demo?'Demo · illustrative':`Local model · ${model.snapshots[0]?.revision?.slice(0,8)||'revision unknown'}`;
    this.hideSearchResults();
    $('rail-issue-count').textContent=String(this.issueRecords().length);
    $('rail-issue-count').hidden=this.issueRecords().length===0;
    this.openLevel(null);this.updatePlayer();this.closeInspector();
  }
  openLevel(parentId){
    if(parentId!==null&&!this.indexes.components.has(parentId))return;
    const previousStep=this.playback.steps[this.playback.index]?.steps.at(-1)?.id;
    this.viewParentId=parentId;this.slicePage=0;
    this.fullGraph=viewGraph(this.model,parentId,this.indexes);
    this.displaySlice(0);
    this.playback.running=false;this.rebuildPlayback();
    if(previousStep){const stage=this.playback.steps.findIndex(group=>group.steps.some(step=>step.id===previousStep));if(stage>=0)this.playback.index=stage;}
    this.ensureStageVisible();this.camera.azimuth=.62;this.camera.elevation=.62;
    if(this.visualMode==='2d')this.diagram.fit(false);else this.fitCamera(false);this.renderBreadcrumb();this.closeInspector();this.updatePlayer();this.syncDiagram();
  }
  displaySlice(page){
    const graph=sliceGraph(this.fullGraph,page,40);
    const key=`${this.viewParentId||'root'}:${graph.page}`;
    let positions=this.layoutCache.get(key);
    if(!positions){
      positions=layoutGraph(graph.nodes,graph.edges,{maxNodes:64,iterations:180});
      if(this.layoutCache.size>=24)this.layoutCache.delete(this.layoutCache.keys().next().value);
      this.layoutCache.set(key,positions);
    }
    this.slicePage=graph.page;this.graph=graph;this.positions=positions;this.edgePaths=new Map();
    this.refreshFocus();
    for(const edge of graph.edges)this.edgePaths.set(edge.id,connectionGeometry(edge,positions));
    this.buildLabels();this.diagram.setGraph(graph,key);if(this.visualMode==='2d')this.diagram.fit(false);else this.fitCamera(false);
    if(this.renderError&&this.visualMode==='3d')this.renderFallback();
    $('slice-controls').hidden=graph.pages<2;
    $('slice-label').textContent=`${graph.groupLabel||'Architecture'} · ${graph.page+1} / ${graph.pages} · ${graph.totalNodes} components`;
    $('slice-prev').disabled=graph.page===0;$('slice-next').disabled=graph.page===graph.pages-1;
    $('scene-context').textContent=(this.viewParentId?this.indexes.components.get(this.viewParentId)?.name||'Component':'System architecture')+(graph.pages>1?' · grouped view':'');
  }
  showComponent(id){
    const component=this.indexes.components.get(id);
    if(!component)return;
    const parent=component.parent_id??null;
    if(this.viewParentId!==parent)this.openLevel(parent);
    const position=this.fullGraph.nodes.findIndex(node=>node.id===id);
    if(position>=0&&!this.graph.nodes.some(n=>n.id===id))this.displaySlice(this.pageForNode(id));
    this.inspect({kind:'component',id});this.focusComponent(id);
  }
  ensureStageVisible(){
    const stage=this.playback.steps[this.playback.index];
    const id=stage?.visibleId;
    if(!id||this.positions.has(id))return;
    const position=this.fullGraph?.nodes.findIndex(node=>node.id===id)??-1;
    if(position>=0){this.displaySlice(this.pageForNode(id));this.focusComponent(id);}
  }
  pageForNode(id){const groups=this.graph?.groups||[];const p=groups.findIndex(g=>g.ids.includes(id));return p>=0?p:0;}
  refreshFocus(){
    const journey=this.activeJourneyId?this.indexes?.journeys.get(this.activeJourneyId):null;
    this.flowFocus=this.graph&&this.indexes?flowFocus(journey,this.graph,this.viewParentId,this.indexes,this.flowFocused):null;
    if(this.visualMode==='2d')this.diagram.setFocus(this.flowFocus);
  }
  framePositions(ids=[],smooth=true){
    const coords=ids.length?ids.map(id=>this.positions.get(id)).filter(Boolean):[...this.positions.values()];
    if(!coords.length)return;
    const xs=coords.map(p=>p[0]),zs=coords.map(p=>p[2]);
    const cx=(Math.max(...xs)+Math.min(...xs))/2,cz=(Math.max(...zs)+Math.min(...zs))/2;
    const extentX=Math.max(...xs)-Math.min(...xs)+5.4,extentZ=Math.max(...zs)-Math.min(...zs)+6;
    const canvas=$('world-canvas'),aspect=Math.max(.6,canvas.clientWidth/Math.max(1,canvas.clientHeight));
    const radius=clamp(Math.max(12,extentZ*.87,extentX*.68/Math.max(.65,aspect))*(coords.length===1?.88:1.18)+6,12,135);
    const target=[cx,.8,cz];
    if(!smooth||reducedMotion){this.camera.target=target;this.camera.radius=radius;this.cameraGoal=null;}
    else this.cameraGoal={target,radius};
  }
  fitCamera(smooth=true){if(this.visualMode==='2d'){this.diagram.fit(smooth);return;}this.framePositions([],smooth);}
  focusFlow(){
    const ids=[...new Set(this.playback.steps.map(item=>item.visibleId).filter(id=>id&&this.positions.has(id)))];
    if(this.visualMode==='2d'){this.diagram.fit(true,ids);return;}
    if(ids.length)this.framePositions(ids);
    else this.fitCamera();
  }
  focusComponent(id){if(this.visualMode==='2d'){this.diagram.focus(id);return;}if(this.positions.has(id))this.framePositions([id]);}
  renderBreadcrumb(){
    const out=$('crumbs');out.replaceChildren();
    const chain=[];let current=this.viewParentId;
    while(current){const component=this.indexes.components.get(current);if(!component)break;chain.unshift(component);current=component.parent_id;}
    const entries=[{id:null,name:this.model.scope.name||'Overview'},...chain];
    entries.forEach((entry,i)=>{
      if(i)out.append(create('span','crumb-sep','/'));
      const button=create('button',`crumb ${i===entries.length-1?'active':''}`,entry.name);
      button.type='button';button.addEventListener('click',()=>this.openLevel(entry.id));out.append(button);
    });
  }
  selectJourney(id){
    if(id&&!this.indexes.journeys.has(id))return;
    this.activeJourneyId=id;this.synthetic=null;this.playback.index=0;this.playback.phase=0;this.playback.running=false;
    this.rebuildPlayback();this.updatePlayer();this.closeOverlay();
    this.refreshFocus();if(id){this.ensureStageVisible();this.focusFlow();if(this.playback.steps.length)this.inspect({kind:'packet',id:0},'flow');}
    else{if(this.selection.kind==='packet'||this.selection.kind==='scenario')this.closeInspector();this.fitCamera();}
  }
  rebuildPlayback(){
    const journey=this.activeJourneyId?this.indexes.journeys.get(this.activeJourneyId):null;
    const selected=this.playbackSelection.get(this.activeJourneyId);
    const steps=selected?selected.ids.map((id,i)=>{
      const original=journey.steps.find(s=>s.id===id);
      const route=i?selected.edges[i-1]?.via_relation_id:null;
      return route?{...original,via_relation_id:route}:original;
    }):playbackSteps(journey);
    this.playback.steps=journey?projectJourney({...journey,steps},this.viewParentId,this.indexes.components):[];
    this.playback.requiresPath=playbackNeedsPath(journey)&&!selected;
    this.playback.index=clamp(this.playback.index,0,Math.max(0,this.playback.steps.length-1));
    this.playback.phase=0;
  }
  stepTitle(step){
    if(!step)return 'No stage available';
    const stage=step.steps.at(-1);
    const name=stage?this.indexes.components.get(stage.component_id)?.name:'Unknown';
    return `${name||'Outside this view'} · ${stage?.action||'Processing'}`;
  }
  updatePlayer(){
    const active=Boolean(this.activeJourneyId),name=active?this.indexes.journeys.get(this.activeJourneyId)?.name:'Choose a flow';
    $('player').hidden=!active;
    $('rail-focus').disabled=!active;
    $('rail-focus').setAttribute('aria-pressed',String(this.flowFocused));
    $('rail-focus').classList.toggle('active',active&&this.flowFocused);
    $('rail-focus').dataset.tooltip=this.flowFocused?'Show full architecture':'Focus selected flow';
    $('rail-focus').setAttribute('aria-label',this.flowFocused?'Show full architecture':'Focus selected flow');
    $('rail-flows').classList.toggle('active',active);
    if(!active){this.syncDiagram();return;}
    const steps=this.playback.steps,n=steps.length,index=clamp(this.playback.index,0,Math.max(0,n-1));
    $('playback-name').textContent=name||'Execution journey';
    $('player-path').hidden=!this.indexes.journeys.get(this.activeJourneyId)?.execution_edges?.length;
    $('player-path').textContent=this.playback.requiresPath?'Choose path':this.playbackSelection.has(this.activeJourneyId)?'Change path':'Paths';
    $('playback-step').textContent=n?`Step ${index+1} of ${n} · ${this.stepTitle(steps[index])}`:'No stages visible at this level';
    $('playback-progress').textContent=`${n?index+1:0} / ${n}`;
    const transition=this.transitionFor(steps[index],steps[index+1]);
    $('playback-step').title=transition.label;
    $('flow-announcement').textContent=n?`${name}. ${this.stepTitle(steps[index])}. ${transition.label}.`:'';
    $('player-progress-input').max=String(Math.max(n-1,1));$('player-progress-input').value=String(index);
    $('player-progress-input').disabled=n<2;
    setIcon($('play-button'),this.playback.running?'pause':'play');
    $('play-button').setAttribute('aria-label',this.playback.running?'Pause flow':'Play flow');
    $('play-button').disabled=n<2;
    $('speed-button').textContent=`${this.playback.speed}×`;
    this.syncDiagram();
    const dots=$('player-steps');dots.replaceChildren();
    const visible=Math.min(n,24);
    for(let i=0;i<visible;i++){
      const at=visible===n?i:Math.round(i*(n-1)/(visible-1));
      const dot=create('button',`step-dot ${at<index?'completed':at===index?'current':''}`,at<index?'✓':'');
      dot.type='button';dot.title=`Go to step ${at+1}: ${this.stepTitle(steps[at])}`;
      dot.setAttribute('aria-label',dot.title);
      dot.addEventListener('click',()=>this.seekStep(at));dots.append(dot);
    }
  }
  seekStep(index){
    if(!this.playback.steps.length)return;
    this.playback.running=false;this.playback.index=clamp(index,0,this.playback.steps.length-1);this.playback.phase=0;
    this.ensureStageVisible();this.updatePlayer();
    if(this.selection.kind==='packet')this.inspect({kind:'packet',id:this.playback.index},'flow');
  }
  nextStep(){this.seekStep(this.playback.index+1);}
  playPause(){
    if(!this.playback.steps.length)return;
    if(this.playback.requiresPath){this.notify('This journey branches or runs concurrently. Specify a supported playback path; the full causal relationships are available in Steps.');this.openJourneyStory();return;}
    if(this.playback.index>=this.playback.steps.length-1){this.playback.index=0;this.playback.phase=0;}
    if(!this.playback.running&&this.playback.steps[this.playback.index+1]){
      const transfer=this.transitionFor(this.playback.steps[this.playback.index],this.playback.steps[this.playback.index+1]);
      if(['broken','mismatch','unresolved','uncertain','internal-unverified'].includes(transfer.state)){this.notify(`Playback paused: ${transfer.label}. Advance manually to inspect the next declared stage.`);return;}
    }
    this.playback.running=!this.playback.running;this.focusFlow();this.updatePlayer();
  }
  selectedStage(){return this.playback.steps[this.playback.index]?.steps.at(-1)||null;}
  closeInspector(){
    this.selection={kind:'none',id:null};$('inspector-panel').hidden=true;
    for(const label of this.labels.values())label.classList.remove('selected');
    this.diagram.setSelection(null);
  }
  inspect(selection,tab='overview'){
    this.selection=selection;this.inspectorTab=tab;
    $('inspector-panel').hidden=false;
    this.renderInspector();
    for(const [id,label] of this.labels)label.classList.toggle('selected',selection.kind==='component'&&id===selection.id);
    this.diagram.setSelection(selection.kind==='component'?selection.id:null);
  }
  renderInspector(){
    const selection=this.selection;
    const selected=this.resolveSelection(selection);
    $('inspector-name').textContent=selected.title;
    $('inspector-type').textContent=selected.type;
    setIcon($('inspector-symbol'),selected.icon);
    for(const [tab,id] of [['overview','inspector-overview-tab'],['flow','inspector-flow-tab']]){
      $(id).classList.toggle('active',this.inspectorTab===tab);
      $(id).setAttribute('aria-selected',String(this.inspectorTab===tab));
    }
    const out=$('inspector-content');out.replaceChildren();
    if(this.inspectorTab==='flow'&&selection.kind==='component')this.inspectComponentFlow(out,this.indexes.components.get(selection.id));
    else if(selection.kind==='component')this.inspectComponent(out,this.indexes.components.get(selection.id));
    else if(selection.kind==='relation'&&this.inspectorTab==='flow')this.inspectRelationFlow(out,this.indexes.relations.get(selection.id));
    else if(selection.kind==='relation')this.inspectRelation(out,this.indexes.relations.get(selection.id));
    else if(selection.kind==='packet'&&this.inspectorTab==='overview')this.inspectPacketOverview(out,this.playback.steps[selection.id]);
    else if(selection.kind==='packet')this.inspectPacket(out,this.playback.steps[selection.id]);
    else if(selection.kind==='scenario'&&this.inspectorTab==='flow')this.inspectScenarioFlow(out,this.indexes.scenarios.get(selection.id));
    else if(selection.kind==='scenario')this.inspectScenario(out,this.indexes.scenarios.get(selection.id),selection.result);
    $('inspector-verification').textContent=this.model.scope.demo?'Fictional demo · no source verification':'Read-only · claims require source evidence';
  }
  resolveSelection(selection){
    if(selection.kind==='component'){
      const c=this.indexes.components.get(selection.id);
      return {title:c?.name||'Component',type:c?.variant?c.variant.replaceAll('_',' '):ROLE_TITLES[c?.role]||c?.role||'Component',icon:ROLE_ICONS[c?.role]||'cube'};
    }
    if(selection.kind==='relation')return {title:'Connection',type:'Interaction',icon:'route'};
    if(selection.kind==='packet')return {title:'Request data',type:'Journey inspection',icon:'package'};
    if(selection.kind==='scenario')return {title:this.indexes.scenarios.get(selection.id)?.name||'Scenario',type:'Synthetic scenario',icon:'route'};
    return {title:'Architecture',type:'Inspection',icon:'cube'};
  }
  inspectComponent(out,c){
    if(!c)return;
    const introduction=section(out,'Role in this system');
    paragraph(introduction,c.responsibility);
    const chips=create('div','info-chip-row');evidenceChip(chips,c.evidence_status);introduction.append(chips);
    const children=this.model.components.filter(item=>item.parent_id===c.id);
    const attributes=c.attributes||{};
    const operations=Array.isArray(c.operations)?c.operations:Array.isArray(attributes.operations)?attributes.operations:[];
    if(operations.length){const block=section(out,'Operations used');const row=create('div','info-chip-row');for(const operation of operations.slice(0,12))chip(row,operation);block.append(row);}
    if(children.length){
      const block=section(out,'Inside this component');
      paragraph(block,`${children.length} discovered internal ${children.length===1?'capability':'capabilities'}. Enter to inspect their responsibilities and connections.`,'detail-note');
      block.append(this.primaryButton(`Explore ${c.name}`,()=>this.openLevel(c.id)));
    }
    const connections=this.graph.edges.filter(r=>r.from===c.id||r.to===c.id);
    if(connections.length){
      const block=section(out,'Connections and dependencies');
      for(const r of connections.slice(0,14)){
        const outward=r.from===c.id;
        const peer=r.to?this.indexes.components.get(outward?r.to:r.from)?.name:r.unresolved_target||'Unresolved target';
        const btn=create('button','dependency-row');btn.type='button';
        const direction=r.direction==='bidirectional'?'↔':outward?'→':'←';
        append(btn,create('span','dependency-direction',direction));
        const content=create('div','dependency-content');
        append(content,create('div','dependency-name',peer||'Unknown'),create('div','dependency-detail',`${r.kind.replaceAll('_',' ')} · ${r.fault_status==='CONFIRMED'?'confirmed fault':stateLabel(r.evidence_status)}`));
        append(btn,content,create('span','dependency-chevron','›'));
        btn.addEventListener('click',()=>this.inspect({kind:'relation',id:r.id}));block.append(btn);
      }
    }
    const related=this.playback.steps.find(group=>group.visibleId===c.id);
    if(related){const block=section(out,'In the selected flow');paragraph(block,`${related.steps.length} ${related.steps.length===1?'step passes':'steps pass'} through this component at the current view level.`,'detail-note');block.append(this.primaryButton('Inspect flow stages',()=>this.inspect({kind:'component',id:c.id},'flow')));}
    const special=Object.entries(attributes).filter(([key,value])=>key!=='fixture'&&key!=='operations'&&value!==null&&['string','number','boolean'].includes(typeof value)).slice(0,6);
    if(special.length){const block=section(out,'Relevant configuration');const grid=create('div','metric-grid');for(const [key,value] of special)showPair(grid,key.replaceAll('_',' '),String(value));block.append(grid);}
    const impact=relatedImpact(c,this.model,this.indexes);
    if(impact.dependedOnBy.length||impact.journeys.length){
      const block=section(out,'If this component is unavailable');
      paragraph(block,'The following declared connections and journeys could require investigation. This is dependency exposure, not a prediction of an outage.','detail-note');
      for(const item of impact.dependedOnBy.slice(0,6))paragraph(block,`${this.indexes.components.get(item.id)?.name||item.id} depends on this component via ${item.kind.replaceAll('_',' ')} (${stateLabel(item.evidence)}).`,'impact-line');
      if(impact.journeys.length){const row=create('div','info-chip-row');for(const j of impact.journeys.slice(0,6))chip(row,j.name||j.id);block.append(row);}
    }
    if(c.source_refs?.length)sourceBlock(out,c.source_refs);
  }
  inspectComponentFlow(out,c){
    const group=this.playback.steps.find(item=>item.visibleId===c.id);
    if(!group){const block=section(out,'Flow involvement');paragraph(block,this.activeJourneyId?'No stages of this journey are mapped to this component at the current level.':'Choose an execution flow to inspect how this component processes data.');return;}
    const first=group.steps[0],last=group.steps.at(-1);
    const block=section(out,'Why this step happens');paragraph(block,this.explainStage(last));
    if(group.steps.length>1)paragraph(block,`${group.steps.length} internal steps are summarized at this architectural level. Enter the component to inspect its internal capabilities.`,'detail-note');
    const status=section(out,'Current stage');status.append(this.statusLine(this.playback.steps[this.playback.index]?.visibleId===c.id?'Current flow component':'Part of selected journey',`${group.steps.length} stage${group.steps.length===1?'':'s'}`));
    const payload=section(out,'Data transformation');const boxes=create('div','payload-grid');codeCard(boxes,'Input shape',first.input_shape);codeCard(boxes,'Output shape',last.output_shape);payload.append(boxes);
    sourceBlock(out,last.source_refs);
  }
  inspectRelation(out,r){
    if(!r)return;
    const source=this.indexes.components.get(r.from)?.name||'Unknown source';
    const target=r.to?this.indexes.components.get(r.to)?.name:r.unresolved_target;
    const block=section(out,'Communication');
    paragraph(block,`${source} ${r.direction==='bidirectional'?'exchanges data with':'sends to'} ${target||'an unresolved target'} through a ${r.kind.replaceAll('_',' ')} relationship. The arrow shows the declared communication direction, not confirmed runtime availability.`);
    if(r.interaction){const sem=section(out,'Interaction semantics');paragraph(sem,r.interaction.replaceAll('_',' '));}
    if(r.protocol||r.channel||r.contract){const details=create('div','info-chip-row');for(const field of ['protocol','channel','contract'])if(r[field])chip(details,`${field}: ${r[field]}`);block.append(details);}
    const chips=create('div','info-chip-row');chip(chips,r.direction==='bidirectional'?'Bidirectional':'Directed');evidenceChip(chips,r.evidence_status);if(r.fault_status!=='NONE')evidenceChip(chips,r.fault_status);block.append(chips);
    const details=section(out,'Connection state');
    if(r.fault_status==='CONFIRMED')details.append(this.statusLine('Confirmed issue','Independent evidence required'));
    else if(!r.to)details.append(this.statusLine('Unresolved target','Not evidence of an outage'));
    else details.append(this.statusLine('Relationship documented',r.projected?'Projected across levels':'Declared in the model'));
    if(r.finding_id){const finding=this.indexes.findings.get(r.finding_id);if(finding){const info=section(out,'Verifier finding');paragraph(info,finding.justification||finding.claim||'No justification provided.');}}
    sourceBlock(out,r.source_refs);
  }
  inspectRelationFlow(out,r){
    if(!r)return;
    const block=section(out,'Execution involvement');
    const journey=this.activeJourneyId?this.indexes.journeys.get(this.activeJourneyId):null;
    const included=journey?.steps.some(s=>s.via_relation_id===r.id);
    if(included)paragraph(block,`The selected ${journey.name} journey references this relationship. Its declared direction is ${r.direction==='bidirectional'?'bidirectional':'forward'}.`);
    else paragraph(block,journey?'This relationship is not explicitly referenced in the selected journey.':'Select a journey to inspect how this connection participates in execution.');
    const source=this.indexes.components.get(r.from)?.name||r.from,target=r.to?this.indexes.components.get(r.to)?.name:r.unresolved_target;
    const details=section(out,'Transfer boundary');
    const grid=create('div','metric-grid');showPair(grid,'From',source);showPair(grid,'To',target||'Unresolved');showPair(grid,'Mechanism',r.kind.replaceAll('_',' '));showPair(grid,'Evidence',stateLabel(r.evidence_status));details.append(grid);
    if(r.fault_status==='CONFIRMED'){const issue=section(out,'Flow restriction');paragraph(issue,'A confirmed fault is recorded. Simulated packets cannot cross the verified broken link.');}
    sourceBlock(out,r.source_refs);
  }
  inspectPacketOverview(out,group){
    if(!group)return;
    const step=group.steps.at(-1),component=this.indexes.components.get(step.component_id);
    const block=section(out,'Position in the journey');
    paragraph(block,`The selected data object is currently associated with ${component?.name||'an external stage'}. The modeled action is ${step.action||'processing'}. Its payload can be inspected under the Flow tab.`);
    block.append(this.statusLine(`Stage ${this.playback.index+1} of ${this.playback.steps.length}`,step.mode||'Illustrative'));
    const metadata=section(out,'Stage information');
    const grid=create('div','metric-grid');showPair(grid,'Component',component?.name||'External');showPair(grid,'Outcome',step.outcome||'Not declared');showPair(grid,'Scope',group.offLevel?'Outside this level':'Visible');showPair(grid,'Evidence',stateLabel(step.certainty));metadata.append(grid);
    sourceBlock(out,step.source_refs);
  }
  inspectScenarioFlow(out,scenario){
    if(!scenario)return;
    const linked=this.indexes.journeys.get(scenario.journey_id);
    const block=section(out,'Associated journey');paragraph(block,linked?`${linked.name} includes ${linked.steps.length} declared execution steps. The scenario models selected behaviors; it does not measure actual service execution.`:'The referenced journey is unavailable.');
    const steps=section(out,'Modeled rules');
    for(const rule of scenario.rules||[]){const row=create('div','field-change');append(row,create('strong','',String(rule.type||'Unspecified behavior').replaceAll('_',' ')),create('span','',rule.component_id?this.indexes.components.get(rule.component_id)?.name||rule.component_id:'No component bound'));steps.append(row);}
  }
  inspectPacket(out,group){
    if(!group)return;
    const step=group.steps.at(-1),component=this.indexes.components.get(step.component_id);
    const summary=section(out,'What happens at this step');
    paragraph(summary,this.explainStage(step));
    const next=this.playback.steps[this.playback.index+1];
    const transfer=this.transitionFor(group,next);
    const handoff=section(out,'What happens next');
    paragraph(handoff,next?`${this.stepTitle(next)}. ${transfer.label}.`:`The declared journey ends here. ${step.outcome?'Reported outcome: '+step.outcome+'.':'No additional outcome was declared.'}`);
    if(['unresolved','mismatch','broken','uncertain','internal-unverified'].includes(transfer.state))handoff.append(this.statusLine('Not verified',transfer.state.replaceAll('-',' ')));
    summary.append(this.statusLine(`Stage ${this.playback.index+1} of ${this.playback.steps.length}`,step.mode||'Illustrative'));
    if(Array.isArray(step.conditions)&&step.conditions.length){const conditions=section(out,'Conditions and branches');for(const condition of step.conditions.slice(0,8))paragraph(conditions,typeof condition==='string'?condition:JSON.stringify(redactPayload(condition)),'detail-note');}
    if(step.branch){const branch=section(out,'Selected branch');paragraph(branch,String(step.branch));}
    const block=section(out,'Data before and after');const grid=create('div','payload-grid');codeCard(grid,'Input shape',step.input_shape);codeCard(grid,'Output shape',step.output_shape);block.append(grid);
    const changes=step.field_changes?.length?step.field_changes:changesBetween(step.input_shape||{},step.output_shape||{});
    if(changes.length){const diff=section(out,'Field changes');for(const change of changes.slice(0,20)){const row=create('div','field-change');append(row,create('strong','',change.field),create('span','',`${JSON.stringify(change.before)??'not present'} → ${JSON.stringify(change.after)??'not present'}`));diff.append(row);}}
    const state=section(out,'Evidence');const pills=create('div','info-chip-row');evidenceChip(pills,step.certainty||'INFERRED');chip(pills,group.offLevel?'Outside current scope':'At current level');state.append(pills);
    sourceBlock(out,step.source_refs);
  }
  explainStage(step){
    const component=this.indexes.components.get(step.component_id);
    const action=(step.action||'processes the available input').replace(/^[A-Z]/,c=>c.toLowerCase());
    const role=component?.responsibility||'Its responsibility has not been established in this model.';
    const qualification=step.certainty==='SOURCE_VERIFIED'?'The implementation is supported by source references.':'This is modeled behavior and is not proof of a running deployment.';
    if(typeof step.explanation==='string'&&step.explanation.trim())return `${step.explanation.trim()} ${qualification}`;
    const conditions=Array.isArray(step.conditions)&&step.conditions.length?` The modeled conditions are ${step.conditions.slice(0,3).map(c=>typeof c==='string'?c:JSON.stringify(redactPayload(c))).join('; ')}.`:'';
    return `${component?.name||'This component'} ${action}. ${role}${conditions} ${qualification}`;
  }
  chooseFlowPath(){
    const journey=this.indexes.journeys.get(this.activeJourneyId);if(!journey)return;
    const paths=enumerateJourneyPaths(journey);
    this.showOverlay('Choose an execution path','Explicitly modeled alternatives','paths');
    const body=$('overlay-body');
    paragraph(body,'Selecting a path explores one declared possibility. Parallel branches may occur concurrently; this view does not claim an actual execution order or runtime observation.');
    if(!paths.length){paragraph(body,'No bounded path can be constructed from the supplied execution relationships. Inspect the step explanations instead.');return;}
    paths.forEach((path,i)=>{
      const row=create('button','dialog-row');row.type='button';
      const title=path.ids.map(id=>journey.steps.find(s=>s.id===id)?.action||id).join(' → ');
      const conditions=path.edges.filter(e=>e.condition).map(e=>e.condition).slice(0,3).join('; ');
      const icon=create('span','catalog-glyph');setIcon(icon,'route');
      const text=create('div','dialog-copy');append(text,create('div','dialog-title',`Path ${i+1}: ${title}`),create('div','dialog-description',`${conditions||'No branch condition declared'}${path.truncated?' · truncated for safety':''}`));
      append(row,icon,text);
      row.addEventListener('click',()=>{this.playbackSelection.set(journey.id,path);this.playback.index=0;this.playback.phase=0;this.playback.running=false;this.rebuildPlayback();this.refreshFocus();this.closeOverlay();this.ensureStageVisible();this.focusFlow();this.updatePlayer();this.inspect({kind:'packet',id:0},'flow');});
      body.append(row);
    });
  }
  openJourneyStory(){
    const journey=this.indexes.journeys.get(this.activeJourneyId);
    if(!journey)return;
    this.showOverlay(journey.name,'Step-by-step journey · accessible text view','story');
    const body=$('overlay-body');
    const assessment=assessJourney(journey,this.indexes);
    const intro=create('div','story-intro');
    paragraph(intro,`This journey contains ${journey.steps.length} declared stages. Coverage: ${journey.coverage||'unknown'}. ${assessment.complete?'Every checked transition has an identified relationship or stays in one component.':'Some transitions remain unsupported, internally unverified, or broken.'} ${playbackNeedsPath(journey)?'This non-linear journey needs an explicit selected playback path; steps below are not necessarily sequential.':''} These steps are descriptions, not recorded runtime activity.`);
    body.append(intro);
    if(assessment.edges.length){
      const topology=section(body,'Execution relationships');
      for(const edge of assessment.edges){
        const from=journey.steps.find(s=>s.id===edge.from_step_id),to=journey.steps.find(s=>s.id===edge.to_step_id);
        const card=create('div','story-transfer',`${from?.action||edge.from_step_id} → ${to?.action||edge.to_step_id} · ${edge.type.replaceAll('_',' ')} · ${edge.condition||'No condition declared'} · ${edge.transfer.label}`);
        if(edge.transfer.state!=='connected'&&edge.transfer.state!=='internal')card.classList.add('warn');
        topology.append(card);
      }
    }
    journey.steps.forEach((step,index)=>{
      const card=create('div','story-step');
      const heading=create('div','story-step-title',`${index+1}. ${this.indexes.components.get(step.component_id)?.name||'Unknown'} · ${step.action||'Process'}`);
      card.append(heading);paragraph(card,this.explainStage(step));
      if(index>0&&assessment.transitions[index-1]){const t=assessment.transitions[index-1];const label=create('div',`story-transfer ${['broken','mismatch','unresolved','uncertain','internal-unverified'].includes(t.state)?'warn':''}`,`From previous: ${t.label}`);card.append(label);}
      if(step.outcome)paragraph(card,`Declared outcome: ${step.outcome}`,'detail-note');
      const inspect=create('button','story-go','Inspect in workspace');inspect.type='button';inspect.addEventListener('click',()=>{
        this.closeOverlay();const component=this.indexes.components.get(step.component_id);this.openLevel(component.parent_id??null);
        const at=this.playback.steps.findIndex(g=>g.steps.some(s=>s.id===step.id));
        if(at>=0)this.seekStep(at);
        this.inspect({kind:'packet',id:this.playback.index},'flow');this.focusComponent(component.id);
      });card.append(inspect);body.append(card);
    });
  }
  openCoverage(){
    this.showOverlay('Model scope and evidence','Architecture coverage','coverage');
    const body=$('overlay-body');
    paragraph(body,'This page shows what was declared or inspected. An unavailable repository or unverified integration must not be interpreted as a broken connection.');
    const snapshots=section(body,`Repository snapshots (${this.model.snapshots.length})`);
    for(const item of this.model.snapshots){const card=create('div','coverage-row');
      append(card,create('strong','',item.repository||'Unnamed repository'),create('span','',`Revision: ${item.revision||'not pinned'} · ${item.availability||'availability unknown'} · ${item.dirty_state||'dirty state unknown'}`));snapshots.append(card);}
    const scope=section(body,'Authorized boundaries');
    const roots=this.model.scope.authorized_roots||[];
    paragraph(scope,roots.length?`Authorized source roots: ${roots.join(', ')}`:'No authorized source roots were declared for this model.');
    if(this.model.scope.environment)paragraph(scope,`Environment: ${this.model.scope.environment}`);
    if(this.model.scope.excluded_roots?.length)paragraph(scope,`Excluded roots: ${this.model.scope.excluded_roots.join(', ')}`);
    const coverage=section(body,'Analysis completeness');
    for(const item of this.model.coverage){const row=create('div','coverage-row');append(row,create('strong','',`${item.boundary||'Unspecified boundary'} · ${item.status||'unknown'}`),create('span','',item.reason||'No explanation supplied'));coverage.append(row);}
    const findings=section(body,'Evidence summary');
    const verified=this.model.components.filter(c=>c.evidence_status==='SOURCE_VERIFIED').length;
    paragraph(findings,`${verified} of ${this.model.components.length} components are marked source-verified; ${this.model.journeys.filter(j=>j.coverage==='covered').length} of ${this.model.journeys.length} journeys report complete coverage. These are model declarations, not independent measurement.`);
  }
  readTheme(){
    try{const value=localStorage.getItem('visualize-theme');if(value==='light'||value==='dark')return value;}catch{}
    return 'light';
  }
  setTheme(value){
    this.theme=value==='dark'?'dark':'light';
    document.documentElement.dataset.theme=this.theme;
    const button=$('theme-toggle');
    if(button){setIcon(button,this.theme==='dark'?'sun':'moon');button.setAttribute('aria-label',this.theme==='dark'?'Switch to light theme':'Switch to dark theme');button.dataset.tooltip=button.getAttribute('aria-label');}
    this.renderer?.setTheme(this.theme);
    try{localStorage.setItem('visualize-theme',this.theme);}catch{}
  }
  inspectScenario(out,scenario,result){
    if(!scenario||!result)return;
    const intro=section(out,'What this calculates');paragraph(intro,'Runs deterministic rules against declared synthetic inputs. No real requests, broker messages, services or production measurements are involved.');
    const bucket=result.outputs.tokenBucket;
    if(bucket){const results=section(out,'Modeled outcomes');const grid=create('div','metric-grid');showPair(grid,'Requests',bucket.total.toLocaleString());showPair(grid,'Accepted',bucket.accepted.toLocaleString());showPair(grid,'Rejected',bucket.rejected.toLocaleString());showPair(grid,'Arrival rate',`${scenario.inputs.arrival_rate_per_second}/s`);results.append(grid);}
    const block=section(out,'Scenario result');codeCard(block,'Calculated output',result.outputs);
    if(result.assumptions.length){const sectionEl=section(out,'Assumptions');for(const value of result.assumptions.slice(0,10))paragraph(sectionEl,value,'detail-note');}
  }
  statusLine(title,meta){const line=create('div','status-card');append(line,create('span','status-dot'),create('span','',title),create('span','',meta));return line;}
  primaryButton(label,fn){const button=create('button','primary-action');button.type='button';append(button,create('span','',label),create('span','','↗'));button.addEventListener('click',fn);return button;}
  inspectSceneNode(id){
    const node=this.indexes.components.get(id);
    if(node?.role==='client'&&this.activeJourneyId){const index=this.playback.steps.findIndex(step=>step.visibleId===id);if(index>=0){this.inspect({kind:'packet',id:index},'flow');return;}}
    this.inspect({kind:'component',id});
  }
  buildLabels(){
    const root=$('world-labels');root.replaceChildren();this.labels.clear();
    for(const node of this.graph.nodes){
      const button=create('button','node-label');button.type='button';button.dataset.nodeId=node.id;
      if(this.model.components.some(c=>c.parent_id===node.id))button.classList.add('expandable');
      append(button,create('span','tag',node.name));
      button.title=`Inspect ${node.name}${button.classList.contains('expandable')?' · double-click to enter':''}`;
      button.addEventListener('click',()=>this.inspectSceneNode(node.id));
      button.addEventListener('dblclick',()=>{if(this.model.components.some(c=>c.parent_id===node.id))this.openLevel(node.id);});
      root.append(button);this.labels.set(node.id,button);
    }
  }
  updateLabels(){
    const placed=[];
    const visibleFlow=this.flowFocus?.enabled?this.flowFocus.nodeIds:new Set(this.playback.steps.map(step=>step.visibleId));
    const ordered=[...this.labels].sort((a,b)=>Number(b[0]===this.selection.id)-Number(a[0]===this.selection.id)||Number(visibleFlow.has(b[0]))-Number(visibleFlow.has(a[0])));
    for(const [id,label] of ordered){
      const p=this.positions.get(id);if(!p)continue;
      const projected=transformPoint(this.vp,[p[0],3.75,p[2]]);
      const visible=projected[2]>-1&&projected[2]<1&&Math.abs(projected[0])<1.18&&Math.abs(projected[1])<1.18;
      const x=(projected[0]*.5+.5)*this.viewport.width,y=(-projected[1]*.5+.5)*this.viewport.height;
      const width=Math.min(175,label.textContent.length*7+30),height=33;
      const box=[x-width/2-6,y-height/2-6,x+width/2+6,y+height/2+6];
      const collision=placed.some(other=>box[0]<other[2]&&box[2]>other[0]&&box[1]<other[3]&&box[3]>other[1]);
      label.hidden=!visible||(collision&&id!==this.selection.id);
      if(!label.hidden){placed.push(box);label.style.left=`${x}px`;label.style.top=`${y}px`;label.classList.toggle('dimmed',Boolean(this.activeJourneyId)&&!visibleFlow.has(id));}
    }
    const packet=$('packet-chip');
    if(this.activeJourneyId&&this.activePacketWorld){
      const p=transformPoint(this.vp,this.activePacketWorld);
      packet.hidden=!(p[2]>-1&&p[2]<1&&Math.abs(p[0])<.96&&Math.abs(p[1])<.9);
      if(!packet.hidden){packet.style.left=`${(p[0]*.5+.5)*this.viewport.width}px`;packet.style.top=`${(-p[1]*.5+.5)*this.viewport.height-12}px`;}
    }else packet.hidden=true;
    const relationId=this.hoverRelation||(this.selection.kind==='relation'?this.selection.id:this.activeRelation()?.id);
    const edge=this.graph.edges.find(e=>e.id===relationId);
    const label=$('connection-chip');const path=edge?this.edgePaths.get(edge.id):null;
    if(path){
      const mid=pointOnCurve(path.start,path.end,path.bend,.5),p=transformPoint(this.vp,mid);
      label.hidden=!(p[2]>-1&&p[2]<1&&Math.abs(p[0])<.94&&Math.abs(p[1])<.94);
      if(!label.hidden){label.textContent=`${edge.kind.replaceAll('_',' ')} · ${edge.direction==='bidirectional'?'both ways':'one way'}`;label.style.left=`${(p[0]*.5+.5)*this.viewport.width}px`;label.style.top=`${(-p[1]*.5+.5)*this.viewport.height}px`;}
    }else label.hidden=true;
  }
  transitionFor(a,b){
    if(!a||!b)return {state:'end',label:'End of journey',relation:null};
    const key=`${a.steps.at(-1)?.id||'none'}:${b.steps[0]?.id||'none'}:${a.visibleId||'outside'}:${b.visibleId||'outside'}`;
    let value=this.transitionCache.get(key);
    if(!value){value=projectedTransition(a,b,this.indexes);this.transitionCache.set(key,value);}
    return value;
  }
  activeRelation(){
    const a=this.playback.steps[this.playback.index],b=this.playback.steps[this.playback.index+1];
    if(!a?.visibleId||!b?.visibleId||a.visibleId===b.visibleId)return null;
    const transfer=this.transitionFor(a,b);
    if(transfer.state!=='connected')return null;
    return this.graph.edges.find(e=>e.id===transfer.relation?.id)||null;
  }
  segmentGeometry(a,b){
    if(!a?.visibleId||!b?.visibleId||a.visibleId===b.visibleId)return null;
    const transfer=this.transitionFor(a,b);
    if(transfer.state!=='connected')return null;
    const edge=this.graph.edges.find(e=>e.id===transfer.relation?.id&&((e.from===a.visibleId&&e.to===b.visibleId)||(e.direction==='bidirectional'&&e.to===a.visibleId&&e.from===b.visibleId)));
    if(!edge||edge.fault_status==='CONFIRMED')return null;
    const path=this.edgePaths.get(edge.id);
    if(!path)return null;
    if(edge.from===a.visibleId)return path;
    return {start:path.end,end:path.start,bend:path.bend,table:arcLengthTable(path.end,path.start,path.bend),perp:path.perp};
  }
  tickPlayback(dt){
    if(!this.playback.running||!this.playback.steps.length)return;
    const current=this.playback.steps[this.playback.index],next=this.playback.steps[this.playback.index+1];
    if(!next){this.playback.running=false;this.playback.phase=1;this.updatePlayer();return;}
    const transition=this.transitionFor(current,next);
    if(['broken','mismatch','unresolved','uncertain','internal-unverified'].includes(transition.state)){this.playback.running=false;this.notify(`Playback paused: ${transition.label}. Advance manually to inspect the next stage.`);this.updatePlayer();return;}
    const path=this.segmentGeometry(current,next);
    const duration=path?Math.max(.7,motionProfile(path.table.length,5.2,10).duration):.75;
    this.playback.phase+=dt*this.playback.speed/duration;
    if(this.playback.phase>=1){
      this.playback.index++;this.playback.phase=0;this.ensureStageVisible();this.updatePlayer();
      if(this.selection.kind==='packet')this.inspect({kind:'packet',id:this.playback.index},'flow');
    }
  }
  composeScene(time){
    this.renderer.clear();
    const coords=[...this.positions.values()];
    const span=coords.length?Math.max(...coords.map(p=>Math.max(Math.abs(p[0]),Math.abs(p[2]))))+10:12;
    emitGrid(this.renderer,span,this.theme==='dark');
    const active=this.activeRelation();
    for(const edge of this.graph.edges){
      const emphasized=Boolean((active&&edge.id===active.id)||(this.selection.kind==='relation'&&this.selection.id===edge.id));
      const appearance=focusAppearance(this.flowFocus,'edge',edge.id,emphasized);
      this.renderer.intensity=appearance==='muted'?.14:appearance==='alternative'?.42:1;
      emitConnection(this.renderer,edge,this.edgePaths.get(edge.id),time,emphasized);
    }
    for(const node of this.graph.nodes){
      const selected=this.selection.kind==='component'&&this.selection.id===node.id;
      const appearance=focusAppearance(this.flowFocus,'node',node.id,selected);
      this.renderer.intensity=appearance==='muted'?.16:1;
      emitComponent(this.renderer,node,this.positions.get(node.id),reducedMotion?0:time,selected);
    }
    this.renderer.intensity=1;
    if(this.synthetic?.result?.outputs?.tokenBucket){
      const rule=this.synthetic.scenario.rules.find(item=>item.type==='token_bucket');
      const id=rule?.component_id?visibleAtLevel(rule.component_id,this.viewParentId,this.indexes.components):null;
      const pos=this.positions.get(id),data=this.synthetic.result.outputs.tokenBucket;
      if(pos){const frac=Math.min(1,data.accepted/Math.max(1,data.total));this.renderer.add('sphere',compose([pos[0]-1.3,3.3,pos[2]],[.22+frac*.24,.22+frac*.24,.22+frac*.24]),C.green);this.renderer.add('sphere',compose([pos[0]+1.3,3.3,pos[2]],[.22+(1-frac)*.24,.22+(1-frac)*.24,.22+(1-frac)*.24]),C.red);}
    }
    if(this.synthetic?.result?.outputs?.selected){
      const rule=this.synthetic.scenario.rules.find(item=>item.type==='select_candidate');
      const id=rule?.component_id?visibleAtLevel(rule.component_id,this.viewParentId,this.indexes.components):null;
      const pos=this.positions.get(id),candidates=this.synthetic.scenario.inputs?.candidates||[];
      if(pos)for(let i=0;i<Math.min(8,candidates.length);i++){
        const selected=candidates[i].id===this.synthetic.result.outputs.selected?.id;
        const angle=time*.45+i*Math.PI*2/candidates.length;
        const x=pos[0]+Math.cos(angle)*2.15,z=pos[2]+Math.sin(angle)*2.15;
        this.renderer.add('sphere',compose([x,2.55+Math.sin(time+i)*.08,z],selected?[.34,.34,.34]:[.22,.22,.22]),selected?C.green:C.violet);
      }
    }
    this.activePacketWorld=null;
    if(this.activeJourneyId){
      const current=this.playback.steps[this.playback.index],next=this.playback.steps[this.playback.index+1];
      if(current&&next){
        const path=this.segmentGeometry(current,next);
        if(path&&path.table.length){
          const profile=motionProfile(path.table.length,5.2,10);
          const fraction=traveledAt(profile,profile.duration*clamp(this.playback.phase,0,1))/path.table.length;
          this.activePacketWorld=emitPacket(this.renderer,path,fraction,C.violet,.37);
        }
      }else if(current?.visibleId&&this.positions.has(current.visibleId)){
        const p=this.positions.get(current.visibleId);
        const marker={start:[p[0],2.9,p[2]],end:[p[0],2.9,p[2]],bend:[p[0],2.9,p[2]],table:{length:0}};
        this.activePacketWorld=emitPacket(this.renderer,marker,0,C.violet,.28);
      }
    }
  }
  loop(timestamp){
    if(!this.model)return;
    const dt=this.lastFrame?Math.min(.1,(timestamp-this.lastFrame)/1000):0;
    this.lastFrame=timestamp;
    try{
      this.clock.advance(dt,delta=>this.tickPlayback(delta));
      if(!reducedMotion)this.animatedTime+=dt;
      if(this.lastRenderTime&&timestamp-this.lastRenderTime<(this.graph.nodes.length>24?32:16)) {this.raf=requestAnimationFrame(time=>this.loop(time));return;}
      this.lastRenderTime=timestamp;
      if(this.visualMode==='2d'){if(this.playback.running)this.syncDiagram();this.raf=requestAnimationFrame(time=>this.loop(time));return;}
      if(!this.renderer){this.setVisualMode('2d');this.raf=requestAnimationFrame(time=>this.loop(time));return;}
      if(this.cameraGoal){
        const factor=reducedMotion?1:1-Math.exp(-dt*6);
        this.camera.target=this.camera.target.map((n,i)=>n+(this.cameraGoal.target[i]-n)*factor);
        this.camera.radius+=(this.cameraGoal.radius-this.camera.radius)*factor;
        if(Math.abs(this.camera.radius-this.cameraGoal.radius)<.03&&Math.hypot(...this.camera.target.map((n,i)=>n-this.cameraGoal.target[i]))<.03)this.cameraGoal=null;
      }
      const aspect=this.renderer.resize();
      const eye=orbitPosition(this.camera.target,this.camera.radius,this.camera.azimuth,this.camera.elevation);
      this.vp=multiply(perspective(Math.PI/3.3,aspect,.1,500),lookAt(eye,this.camera.target));
      this.viewport={width:$('world-canvas').clientWidth,height:$('world-canvas').clientHeight};
      this.composeScene(this.animatedTime);this.renderer.draw(this.vp,eye);this.updateLabels();
      this.raf=requestAnimationFrame(time=>this.loop(time));
    }catch(error){this.renderError=error.message;this.setVisualMode('2d');this.notify('3D view encountered a rendering error; 2D remains available.');this.raf=requestAnimationFrame(time=>this.loop(time));}
  }
  pickAt(clientX,clientY){
    if(!this.vp)return null;
    const rect=$('world-canvas').getBoundingClientRect(),x=clientX-rect.left,y=clientY-rect.top;
    if(this.activePacketWorld){
      const p=transformPoint(this.vp,this.activePacketWorld);
      if(Math.hypot((p[0]*.5+.5)*rect.width-x,(-p[1]*.5+.5)*rect.height-y)<22)return {kind:'packet',id:this.playback.index};
    }
    let closest=null,min=Infinity;
    for(const node of this.graph.nodes){
      const position=this.positions.get(node.id),p=transformPoint(this.vp,[position[0],1.45,position[2]]);
      if(p[2]<-1||p[2]>1)continue;
      const d=Math.hypot((p[0]*.5+.5)*rect.width-x,(-p[1]*.5+.5)*rect.height-y);
      if(d<55&&d<min){closest={kind:'component',id:node.id};min=d;}
    }
    if(closest)return closest;
    for(const edge of this.graph.edges){
      const path=this.edgePaths.get(edge.id);if(!path)continue;
      for(let i=1;i<13;i++){
        const p=transformPoint(this.vp,pointOnCurve(path.start,path.end,path.bend,i/13));
        if(p[2]<-1||p[2]>1)continue;
        const d=Math.hypot((p[0]*.5+.5)*rect.width-x,(-p[1]*.5+.5)*rect.height-y);
        if(d<18&&d<min){closest={kind:'relation',id:edge.id};min=d;}
      }
    }
    return closest;
  }
  onCanvasPick(x,y){const found=this.pickAt(x,y);if(found){if(found.kind==='component')this.inspectSceneNode(found.id);else this.inspect(found,found.kind==='packet'?'flow':'overview');}else this.closeInspector();}
  issueRecords(){
    if(!this.model)return [];
    return this.model.relations.filter(r=>r.fault_status==='CONFIRMED'||r.fault_status==='SUSPECTED'||r.evidence_status==='UNRESOLVED'||r.to===null);
  }
  showOverlay(title,eyebrow,kind){
    this.overlayKind=kind;this.lastOverlayFocus=document.activeElement;
    $('overlay-title').textContent=title;$('overlay-eyebrow').textContent=eyebrow;
    $('overlay-body').replaceChildren();$('overlay').hidden=false;
    document.body.classList.add('dialog-open');
    $('overlay-close').focus();
  }
  closeOverlay(){
    if(!this.overlayKind)return;
    this.overlayKind=null;$('overlay').hidden=true;document.body.classList.remove('dialog-open');
    this.lastOverlayFocus?.focus?.();
  }
  openCatalog(search=''){
    this.showOverlay('Component catalog','Reference library','catalog');
    const body=$('overlay-body'),input=create('input','overlay-search');input.type='search';input.placeholder='Search components or behaviors';input.setAttribute('aria-label','Search component catalog');body.append(input);
    const results=create('div');body.append(results);input.value=search;
    const render=()=>{
      results.replaceChildren();
      const q=input.value.trim().toLowerCase();const shown=CATALOG.filter(x=>`${x.name} ${x.description} ${x.group}`.toLowerCase().includes(q));
      for(const groupName of [...new Set(shown.map(x=>x.group))]){
        results.append(create('div','overlay-section',groupName));
        const grid=create('div','overlay-grid');
        for(const item of shown.filter(x=>x.group===groupName)){
          const card=create('button','catalog-card');card.type='button';
          const glyph=create('span','catalog-glyph');setIcon(glyph,item.icon);
          append(card,glyph,create('div','catalog-name',item.name),create('div','catalog-description',item.description));
          const present=this.model.components.filter(c=>c.role===item.role&&(!item.variant||c.variant===item.variant));
          if(present.length){card.append(create('div','dialog-meta',`${present.length} in current model · select to inspect`));card.addEventListener('click',()=>{const c=present[0];this.closeOverlay();this.showComponent(c.id);});}
          else card.addEventListener('click',()=>this.notify('This primitive is not used in the current architecture model.'));
          grid.append(card);
        }
        results.append(grid);
      }
      if(!shown.length)results.append(create('p','empty-message','No matching component types.'));
    };
    input.addEventListener('input',render);render();input.focus();
  }
  openFlows(mode='journeys'){
    this.showOverlay('Explore execution flows','Journeys and scenarios','flows');
    const body=$('overlay-body'),tabs=create('div','overlay-tabs'),results=create('div');
    const render=selected=>{
      tabs.replaceChildren();results.replaceChildren();
      for(const key of ['journeys','scenarios']){
        const button=create('button',`overlay-tab ${selected===key?'active':''}`,key==='journeys'?'Discovered journeys':'Synthetic scenarios');button.type='button';
        button.addEventListener('click',()=>render(key));tabs.append(button);
      }
      if(selected==='journeys'){
        for(const j of this.model.journeys){
          const row=create('button','dialog-row');row.type='button';
          const glyph=create('span','catalog-glyph');setIcon(glyph,'route');
          const content=create('div','dialog-copy');append(content,create('div','dialog-title',j.name||j.id),create('div','dialog-description',`${j.steps.length} steps · ${j.coverage||'unknown'} coverage`));
          append(row,glyph,content,create('span','dialog-badge',j.id===this.activeJourneyId?'Selected':'Explore'));
          row.addEventListener('click',()=>this.selectJourney(j.id));results.append(row);
        }
        if(!this.model.journeys.length)results.append(create('p','empty-message','No execution journeys are established in the current model.'));
      }else{
        for(const s of this.model.scenarios){
          const row=create('button','dialog-row');row.type='button';
          const glyph=create('span','catalog-glyph');setIcon(glyph,'worker');
          const content=create('div','dialog-copy');append(content,create('div','dialog-title',s.name||s.id),create('div','dialog-description',`${s.rules?.length||0} model rules · no application execution`));
          append(row,glyph,content,create('span','dialog-badge',s.mode));
          row.addEventListener('click',()=>{
            if(s.mode!=='synthetic'){this.notify('Illustrative scenarios have no deterministic execution rules.');return;}
            try{const result=runSyntheticScenario(s);this.selectJourney(s.journey_id);this.synthetic={scenario:s,result};this.inspect({kind:'scenario',id:s.id,result},'overview');this.notify('Synthetic model evaluated locally. No application requests were sent.');}
            catch(error){this.notify(`Scenario rejected: ${error.message}`);}
          });results.append(row);
        }
        if(!this.model.scenarios.length)results.append(create('p','empty-message','No modeled scenarios are available.'));
      }
    };
    append(body,tabs,results);render(mode);
  }
  connectSearch(){
    const input=$('global-search');
    input.addEventListener('focus',()=>this.renderSearchResults());
    input.addEventListener('input',()=>this.renderSearchResults());
    input.addEventListener('keydown',e=>{
      const list=[...$('search-results').querySelectorAll('button')];
      if(e.key==='ArrowDown'&&list.length){e.preventDefault();list[0].focus();}
      if(e.key==='Enter'&&list.length){e.preventDefault();list[0].click();}
      if(e.key==='Escape'){this.hideSearchResults();input.blur();}
    });
    $('search-results').addEventListener('keydown',e=>{
      const list=[...$('search-results').querySelectorAll('button')],idx=list.indexOf(document.activeElement);
      if(e.key==='ArrowDown'&&idx<list.length-1){e.preventDefault();list[idx+1].focus();}
      if(e.key==='ArrowUp'){e.preventDefault();if(idx>0)list[idx-1].focus();else input.focus();}
      if(e.key==='Escape'){e.preventDefault();this.hideSearchResults();input.focus();}
    });
    document.addEventListener('pointerdown',e=>{if(!e.target.closest('.global-search-wrap'))this.hideSearchResults();});
  }
  hideSearchResults(){
    $('search-results').hidden=true;
    $('global-search').setAttribute('aria-expanded','false');
  }
  renderSearchResults(){
    const input=$('global-search'),results=$('search-results');
    if(!this.model)return;
    results.replaceChildren();
    const query=input.value.trim().toLowerCase();
    if(!query){
      results.append(create('div','search-empty','Search by component, purpose, or execution flow.'));
    }else{
      const components=this.model.components.filter(c=>`${c.name} ${c.responsibility} ${c.role} ${c.variant||''}`.toLowerCase().includes(query)).slice(0,9);
      const journeys=this.model.journeys.filter(j=>`${j.name} ${j.id} ${j.description||''}`.toLowerCase().includes(query)).slice(0,5);
      for(const component of components){
        const row=this.searchRow(component.name,component.responsibility,ROLE_ICONS[component.role]||'cube');
        row.addEventListener('click',()=>{this.hideSearchResults();input.value='';this.showComponent(component.id);});
        results.append(row);
      }
      for(const journey of journeys){
        const row=this.searchRow(journey.name,`${journey.steps.length} stages · execution journey`,'route');
        row.addEventListener('click',()=>{this.hideSearchResults();input.value='';this.selectJourney(journey.id);});
        results.append(row);
      }
      if(!components.length&&!journeys.length)results.append(create('div','search-empty','No matching components or journeys.'));
    }
    results.hidden=false;
    input.setAttribute('aria-expanded','true');
  }
  openSearch(){
    $('global-search').focus();$('global-search').select();
  }
  searchRow(title,description,icon){
    const row=create('button','dialog-row');row.type='button';
    const glyph=create('span','catalog-glyph');setIcon(glyph,icon);
    const text=create('div','dialog-copy');append(text,create('div','dialog-title',title),create('div','dialog-description',description));
    append(row,glyph,text,create('span','dependency-chevron','›'));return row;
  }
  openIssues(){
    this.showOverlay('Connection findings','Evidence and uncertainty','issues');
    const records=this.issueRecords(),body=$('overlay-body');
    if(!records.length){body.append(create('p','empty-message','No connection issues are reported in the inspected model. This does not guarantee the running system is healthy.'));return;}
    const caption=create('p','empty-message','Only confirmed defects have supporting verifier findings. Missing consumers and inaccessible systems remain unresolved.');body.append(caption);
    for(const r of records){
      const from=this.indexes.components.get(r.from)?.name||r.from,to=r.to?this.indexes.components.get(r.to)?.name:r.unresolved_target;
      const row=create('button','dialog-row');row.type='button';
      const glyph=create('span','catalog-glyph');setIcon(glyph,'alert');
      const text=create('div','dialog-copy');append(text,create('div','dialog-title',`${from} → ${to||'Unresolved'}`),create('div','dialog-description',`${r.kind.replaceAll('_',' ')} · ${stateLabel(r.evidence_status)}`));
      const tag=create('span',`dialog-badge ${r.fault_status==='CONFIRMED'?'danger':'warn'}`,r.fault_status==='CONFIRMED'?'Confirmed':'Unresolved');
      append(row,glyph,text,tag);
      row.addEventListener('click',()=>{this.closeOverlay();this.showComponent(r.from);this.inspect({kind:'relation',id:r.id});});body.append(row);
    }
  }
  openHelp(){
    this.showOverlay('Navigate the architecture','Controls','help');
    const body=$('overlay-body');
    for(const [title,detail] of [
      ['3D and 2D','Use the scene switch to choose a 3D world or a movable 2D graph; both use the same validated model.'],
      ['Move 2D components','In 2D, drag a component to rearrange it locally. Drag the empty diagram to pan, scroll to zoom, or fit to reset the view.'],
      ['Orbit','In 3D, drag on the scene or select the orbit tool to rotate the camera.'],
      ['Pan','In 3D, Shift-drag, right-drag, or select the pan tool to move across the plane.'],
      ['Zoom and fit','Scroll to zoom. Use the bottom-left buttons to zoom or fit the current view.'],
      ['Inspect','Click a component, connection, or moving data object to see its project-specific details.'],
      ['Enter a component','Double-click a component with internal capabilities. Use the breadcrumb to return.'],
      ['Flows','Choose a discovered journey to follow its stages. Playback is illustrative, not live traffic. Use Steps for a complete text explanation.'],
      ['Scope','Coverage shows inspected repository snapshots, excluded boundaries, and evidence gaps.'],
      ['Groups','Large architecture levels are displayed by discovered domain or connected scope; cross-group links remain visible as handoffs.'],
      ['Flow focus','Focus flow dims unrelated architecture while keeping confirmed failures visible. Toggle it from the sidebar.'],
      ['Reset 2D layout','Reset positions from the sidebar or use Ctrl/⌘ + Z inside the 2D canvas to undo a dragged node.'],
      ['Execution branches','Fan-out, retries, timeouts and alternatives are explained by causal relationships. Non-linear flows require an explicit playback path.'],
      ['Shortcuts','Ctrl/⌘ + K searches. Escape closes panels or moves one level up. Space toggles playback.']]){const row=create('div','dialog-row');const glyph=create('span','catalog-glyph');setIcon(glyph,'help');const content=create('div','dialog-copy');append(content,create('div','dialog-title',title),create('div','dialog-description',detail));append(row,glyph,content);body.append(row);}
  }
  panCamera(dx,dy){
    this.cameraGoal=null;
    const aspect=Math.max(.6,this.viewport.width/Math.max(1,this.viewport.height));
    const scale=this.camera.radius*.0014/Math.max(.7,aspect);
    const a=this.camera.azimuth;
    this.camera.target[0]+=(-Math.cos(a)*dx+Math.sin(a)*dy*.65)*scale;
    this.camera.target[2]+=(Math.sin(a)*dx+Math.cos(a)*dy*.65)*scale;
  }
  connectControls(){
    $('import-model').addEventListener('change',async e=>{
      const file=e.target.files?.[0];if(!file)return;
      try{if(file.size>MAX_UPLOAD)throw new Error('Model exceeds 8 MB');this.loadModel(JSON.parse(await file.text()));this.closeOverlay();this.notify('Model imported locally. No code was changed or executed.');}
      catch(error){this.notify(`Import rejected: ${error.message}`);}e.target.value='';
    });
    $('rail-expand').addEventListener('click',()=>{
      this.navExpanded=!this.navExpanded;
      $('tool-rail').classList.toggle('expanded',this.navExpanded);
      $('rail-expand').setAttribute('aria-expanded',String(this.navExpanded));
      $('rail-expand').querySelector('.rail-label').textContent=this.navExpanded?'Collapse sidebar':'Expand sidebar';
      $('rail-expand').setAttribute('aria-label',this.navExpanded?'Collapse navigation':'Expand navigation');
      $('rail-expand').dataset.tooltip=this.navExpanded?'Collapse navigation':'Expand navigation';
    });
    $('rail-focus').addEventListener('click',()=>{this.flowFocused=!this.flowFocused;this.refreshFocus();this.updatePlayer();});
    $('rail-reset-layout').addEventListener('click',()=>{if(this.visualMode==='2d')this.diagram.resetLayout();else this.notify('Switch to 2D to reset diagram positions.');});
    $('rail-catalog').addEventListener('click',()=>this.openCatalog());
    $('rail-flows').addEventListener('click',()=>this.openFlows());
    $('rail-coverage').addEventListener('click',()=>this.openCoverage());
    $('rail-import').addEventListener('click',()=>$('import-model').click());
    $('view-3d').addEventListener('click',()=>this.setVisualMode('3d'));
    $('view-2d').addEventListener('click',()=>this.setVisualMode('2d'));
    this.connectSearch();
    $('theme-toggle').addEventListener('click',()=>this.setTheme(this.theme==='light'?'dark':'light'));
    $('journey-story').addEventListener('click',()=>this.openJourneyStory());
    $('player-path').addEventListener('click',()=>this.chooseFlowPath());
    $('slice-prev').addEventListener('click',()=>this.displaySlice(this.slicePage-1));
    $('slice-next').addEventListener('click',()=>this.displaySlice(this.slicePage+1));
    $('rail-issues').addEventListener('click',()=>this.openIssues());
    $('rail-help').addEventListener('click',()=>this.openHelp());
    $('rail-overview').addEventListener('click',()=>{this.selectJourney(null);this.openLevel(null);});
    $('overlay-close').addEventListener('click',()=>this.closeOverlay());
    $('overlay-shade').addEventListener('click',()=>this.closeOverlay());
    $('close-inspector').addEventListener('click',()=>this.closeInspector());
    $('inspector-overview-tab').addEventListener('click',()=>{this.inspectorTab='overview';this.renderInspector();});
    $('inspector-flow-tab').addEventListener('click',()=>{this.inspectorTab='flow';this.renderInspector();});
    $('reset-camera').addEventListener('click',()=>this.activeJourneyId?this.focusFlow():this.fitCamera());
    $('zoom-in').addEventListener('click',()=>{if(this.visualMode==='2d')this.diagram.zoom(.82);else{this.cameraGoal=null;this.camera.radius=clamp(this.camera.radius*.82,6,150);}});
    $('zoom-out').addEventListener('click',()=>{if(this.visualMode==='2d')this.diagram.zoom(1.22);else{this.cameraGoal=null;this.camera.radius=clamp(this.camera.radius*1.22,6,150);}});
    for(const [id,mode] of [['camera-orbit','orbit'],['camera-pan','pan']])$(id).addEventListener('click',()=>{
      this.cameraMode=mode;$('camera-orbit').classList.toggle('selected',mode==='orbit');$('camera-pan').classList.toggle('selected',mode==='pan');
    });
    $('play-button').addEventListener('click',()=>this.playPause());
    $('step-button').addEventListener('click',()=>this.nextStep());
    $('reset-flow').addEventListener('click',()=>this.seekStep(0));
    $('close-player').addEventListener('click',()=>this.selectJourney(null));
    $('speed-button').addEventListener('click',()=>{this.playback.speed=this.playback.speed===1?1.5:this.playback.speed===1.5?2:.5===this.playback.speed?1:.5;this.updatePlayer();});
    $('player-progress-input').addEventListener('input',e=>this.seekStep(Number(e.target.value)));
    $('packet-chip').addEventListener('click',()=>this.inspect({kind:'packet',id:this.playback.index},'flow'));
    const canvas=$('world-canvas');
    canvas.addEventListener('contextmenu',e=>e.preventDefault());
    canvas.addEventListener('pointerdown',e=>{
      this.pointer={active:true,x:e.clientX,y:e.clientY,dragged:false,mode:e.shiftKey||e.button===2||this.cameraMode==='pan'?'pan':'orbit'};
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener('pointermove',e=>{
      if(!this.pointer.active){const found=this.pickAt(e.clientX,e.clientY);this.hoverRelation=found?.kind==='relation'?found.id:null;canvas.style.cursor=found?'pointer':'grab';return;}
      const dx=e.clientX-this.pointer.x,dy=e.clientY-this.pointer.y;
      if(Math.abs(dx)+Math.abs(dy)>1)this.pointer.dragged=true;
      this.cameraGoal=null;
      if(this.pointer.mode==='pan')this.panCamera(dx,dy);
      else{this.camera.azimuth-=dx*.007;this.camera.elevation=clamp(this.camera.elevation+dy*.005,.12,1.42);}
      this.pointer.x=e.clientX;this.pointer.y=e.clientY;
    });
    canvas.addEventListener('pointerup',e=>{if(!this.pointer.dragged&&e.button!==2)this.onCanvasPick(e.clientX,e.clientY);this.pointer.active=false;});
    canvas.addEventListener('pointercancel',()=>{this.pointer.active=false;});
    canvas.addEventListener('pointerleave',()=>{this.hoverRelation=null;});
    canvas.addEventListener('dblclick',e=>{const found=this.pickAt(e.clientX,e.clientY);if(found?.kind==='component'&&this.model.components.some(c=>c.parent_id===found.id))this.openLevel(found.id);});
    canvas.addEventListener('wheel',e=>{e.preventDefault();this.cameraGoal=null;this.camera.radius=clamp(this.camera.radius*Math.exp(e.deltaY*.001),6,150);},{passive:false});
    window.addEventListener('keydown',e=>{
      if(this.overlayKind&&e.key==='Tab'){
        const focusable=[...document.querySelectorAll('#overlay-panel button, #overlay-panel input, .overlay-panel button, .overlay-panel input')].filter(element=>!element.disabled&&element.getClientRects().length);
        if(focusable.length){
          const first=focusable[0],last=focusable.at(-1);
          if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
          else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
        }
      }
      const typing=/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName||'');
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('global-search').focus();$('global-search').select();return;}
      if(e.key==='Escape'){
        if(this.overlayKind){this.closeOverlay();return;}
        if(!$('search-results').hidden){this.hideSearchResults();$('global-search').blur();return;}
        if(!$('inspector-panel').hidden){this.closeInspector();return;}
        if(this.viewParentId)this.openLevel(this.indexes.components.get(this.viewParentId)?.parent_id??null);
        return;
      }
      if(typing||this.overlayKind)return;
      if(e.code==='Space'&&this.activeJourneyId){e.preventDefault();this.playPause();}
      if(e.key==='ArrowRight'&&this.activeJourneyId){e.preventDefault();this.nextStep();}
      if(e.key==='f'&&e.target===document.body)this.activeJourneyId?this.focusFlow():this.fitCamera();
    });
    window.addEventListener('pagehide',()=>{if(this.raf)cancelAnimationFrame(this.raf);this.renderer?.dispose();});
  }
}

new VisualizeApp().start();
