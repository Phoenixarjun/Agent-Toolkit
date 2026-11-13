import test from 'node:test';
import assert from 'node:assert/strict';
import { validateModel } from '../src/core/model.js';
import { resolveTransition, projectedTransition, assessJourney, relatedImpact } from '../src/core/flow.js';

const ref=[{path:'src/api.js',repository:'one',locator:'line 1'}];
const fixture=()=>({schema_version:'1.0.0',scope:{name:'Test'},snapshots:[{repository:'one',revision:'abc',availability:'available'}],components:[
{id:'a',name:'Gateway',role:'gateway',responsibility:'Routes requests',parent_id:null,evidence_status:'SOURCE_VERIFIED',source_refs:ref},
{id:'a1',name:'Validator',role:'module',responsibility:'Validates inputs',parent_id:'a',evidence_status:'SOURCE_VERIFIED',source_refs:ref},
{id:'b',name:'Service',role:'service',responsibility:'Executes requests',parent_id:null,evidence_status:'SOURCE_VERIFIED',source_refs:ref},
{id:'c',name:'Database',role:'storage',responsibility:'Stores records',parent_id:null,evidence_status:'SOURCE_VERIFIED',source_refs:ref}],relations:[
{id:'a-b',from:'a',to:'b',kind:'calls',direction:'forward',source_refs:ref,evidence_status:'SOURCE_VERIFIED',fault_status:'NONE'},
{id:'b-c',from:'b',to:'c',kind:'writes_to',direction:'forward',source_refs:ref,evidence_status:'SOURCE_VERIFIED',fault_status:'NONE'}],journeys:[{id:'login',name:'Login',steps:[
{id:'s1',component_id:'a1',action:'validate',source_refs:ref,certainty:'SOURCE_VERIFIED'},
{id:'s2',component_id:'b',action:'execute',source_refs:ref,certainty:'SOURCE_VERIFIED',via_relation_id:'a-b'},
{id:'s3',component_id:'c',action:'persist',source_refs:ref,certainty:'SOURCE_VERIFIED',via_relation_id:'b-c'}]}],scenarios:[],findings:[],coverage:[]});
const pair=(a,b)=>[{component_id:a},{component_id:b}];

test('declared cross-boundary direction is established without inventing a call from each function',()=>{
 const model=fixture(),index=validateModel(model);
 assert.equal(resolveTransition(...pair('a1','b'),index).state,'connected');
 assert.equal(resolveTransition(...pair('b','a1'),index).state,'mismatch');
 const result=assessJourney(model.journeys[0],index);
 assert.equal(result.complete,true);
});

test('unrelated stages are unresolved, even if a reverse relation exists elsewhere',()=>{
 const index=validateModel(fixture());
 assert.equal(resolveTransition(...pair('a1','c'),index).state,'unresolved');
});

test('missing consumer or broken link is not silently visualized as successful execution',()=>{
 const model=fixture();model.relations[1].fault_status='CONFIRMED';
 model.relations[1].finding_id='fault';
 model.findings.push({id:'fault',verdict:'CONFIRMED',justification:'Contract conflict confirmed',evidence_refs:ref});
 const index=validateModel(model);
 assert.equal(resolveTransition(...pair('b','c'),index).state,'broken');
 assert.equal(assessJourney(model.journeys[0],index).complete,false);
});

test('explicit mismatched route cannot substitute an unrelated relationship',()=>{
 const model=fixture();model.journeys[0].steps[1].via_relation_id='b-c';
 const index=validateModel(model);
 assert.equal(resolveTransition(model.journeys[0].steps[0],model.journeys[0].steps[1],index).state,'mismatch');
});

test('unknown cross-level journey is clearly off-level',()=>{
 const index=validateModel(fixture());
 assert.equal(projectedTransition({visibleId:null,steps:[{component_id:'a1'}],offLevel:true},{visibleId:'b',steps:[{component_id:'b'}],offLevel:false},index).state,'outside');
});

test('impacts include dependents and declaring journeys without claiming outages',()=>{
 const model=fixture(),index=validateModel(model);
 const impact=relatedImpact(index.components.get('a'),model,index);
 assert.equal(impact.dependsOn[0].id,'b');
 assert.equal(impact.journeys[0].id,'login');
});

test('ambiguous parallel routes require an explicit choice',()=>{
 const model=fixture();model.relations.push({...model.relations[0],id:'a-b-2',kind:'async_calls'});
 const index=validateModel(model);
 assert.equal(resolveTransition(...pair('a1','b'),index).state,'uncertain');
});

test('reverse traversal of a bidirectional relation uses the real endpoint distance',()=>{
 const model=fixture();
 model.relations[0].direction='bidirectional';
 model.relations.push({id:'nested-direct',from:'b',to:'a1',kind:'calls',direction:'bidirectional',source_refs:ref,evidence_status:'SOURCE_VERIFIED',fault_status:'NONE'});
 const ix=validateModel(model);
 const transfer=resolveTransition({component_id:'a1'},{component_id:'b'},ix);
 assert.equal(transfer.state,'connected');
 assert.equal(transfer.relation.id,'nested-direct');
});
