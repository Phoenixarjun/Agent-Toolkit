import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateModel, viewGraph, projectJourney, visibleAtLevel, redactPayload } from '../src/core/model.js';
const fixture=JSON.parse(readFileSync(new URL('../data/demo.json',import.meta.url),'utf8'));
const fresh=()=>structuredClone(fixture);

test('demo validates and preserves distinct containment and relation graphs',()=>{
 const ids=validateModel(fixture);
 assert.equal(ids.components.size,35);
 assert.equal(ids.relations.size,37);
 assert.equal(viewGraph(fixture,null,ids).nodes.length,12);
 assert.ok(viewGraph(fixture,'factory',ids).nodes.some(n=>n.id==='factory-selector'));
 assert.ok(!viewGraph(fixture,'factory',ids).nodes.some(n=>n.id==='gateway'));
});

test('visible representative is semantic parent, not source folder',()=>{
 const ids=validateModel(fixture);
 assert.equal(visibleAtLevel('factory-selector',null,ids.components),'factory');
 assert.equal(visibleAtLevel('factory-selector','factory',ids.components),'factory-selector');
 assert.equal(visibleAtLevel('registry-policy','factory',ids.components),'factory-registry');
 assert.equal(visibleAtLevel('gateway-auth','factory',ids.components),null);
});

test('journey projection collapses consecutive same component and preserves return visits',()=>{
 const ids=validateModel(fixture);
 const projected=projectJourney(ids.journeys.get('chat'),null,ids.components);
 assert.deepEqual(projected.map(p=>p.visibleId),['client','gateway','factory','provider','factory','client']);
 assert.equal(projected[1].steps.length,3);
 const internal=projectJourney(ids.journeys.get('chat'),'factory',ids.components);
 assert.ok(internal.some(p=>p.visibleId==='factory-selector'));
 assert.ok(internal.some(p=>p.visibleId===null));
});

test('broken graph must reject orphaned and cyclic parent links',()=>{
 const a=fresh();a.components[0].parent_id='factory';a.components.find(c=>c.id==='factory').parent_id='client';
 assert.throws(()=>validateModel(a),/cycle/);
 const b=fresh();b.relations[0].to='does-not-exist';
 assert.throws(()=>validateModel(b),/dangling destination/);
});

test('verified source claims cannot be fabricated and confirmed faults require findings',()=>{
 const a=fresh();a.relations[0].evidence_status='SOURCE_VERIFIED';
 assert.throws(()=>validateModel(a),/without evidence/);
 const b=fresh();b.relations[0].fault_status='CONFIRMED';
 assert.throws(()=>validateModel(b),/confirmed fault without confirmed finding/);
 const c=fresh();c.relations[0].fault_status='CONFIRMED';c.relations[0].finding_id='f1';
 c.findings.push({id:'f1',verdict:'CONFIRMED',claim:'Synthetic test',justification:'Fixture demonstrates a mismatched declared endpoint',evidence_refs:['fixture:config:A','fixture:config:B']});
 assert.doesNotThrow(()=>validateModel(c));
});

test('missing consumer is unresolved, not automatically broken',()=>{
 const indexes=validateModel(fixture);
 const edge=indexes.relations.get('r-billing-missing');
 assert.equal(edge.to,null);
 assert.equal(edge.evidence_status,'UNRESOLVED');
 assert.equal(edge.fault_status,'INDETERMINATE');
});

test('payload redaction excludes personal, secret and credential fields',()=>{
 assert.deepEqual(redactPayload({tenant_id:'org123',userId:'u9',email:'a@example.com',nested:{apiKey:'pw',safe:'ok'},payload:'good'}),{tenant_id:'[redacted]',userId:'[redacted]',email:'[redacted]',nested:{apiKey:'[redacted]',safe:'ok'},payload:'good'});
});
