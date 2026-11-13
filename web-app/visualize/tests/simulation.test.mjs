import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runTokenBucket, runSyntheticScenario, transformPayload, selectCandidate, changesBetween } from '../src/core/simulation.js';
const model=JSON.parse(readFileSync(new URL('../data/demo.json',import.meta.url),'utf8'));

test('10,000 requests are simulated deterministically with exact counters and bounded particles',()=>{
 const s=model.scenarios.find(s=>s.id==='burst');
 const a=runSyntheticScenario(s),b=runSyntheticScenario(s);
 assert.deepEqual(a,b);
 const output=a.outputs.tokenBucket;
 assert.equal(output.total,10000);
 assert.equal(output.accepted+output.rejected,10000);
 assert.ok(output.rejected>0);
 assert.ok(output.samples.length<=49);
 assert.equal(output.mode,'synthetic');
});

test('full bucket and zero refill allow at most initial capacity',()=>{
 const r=runTokenBucket({count:100,arrivalRatePerSecond:10,capacity:5,refillPerSecond:0});
 assert.equal(r.accepted,5);assert.equal(r.rejected,95);
});

test('negative rates, oversized request counts, and non-finite inputs fail closed',()=>{
 assert.throws(()=>runTokenBucket({count:9999999,arrivalRatePerSecond:1,capacity:100,refillPerSecond:10}),/count/);
 assert.throws(()=>runTokenBucket({count:10,arrivalRatePerSecond:0,capacity:100,refillPerSecond:10}),/invalid/);
 assert.throws(()=>runTokenBucket({count:10,arrivalRatePerSecond:10,capacity:100,refillPerSecond:Infinity}),/finite/);
});

test('synthetic candidate selection is deterministic with stable tie priority',()=>{
 const a=runSyntheticScenario(model.scenarios.find(s=>s.id==='selection'));
 assert.equal(a.outputs.selected.id,'candidate-b');
 assert.deepEqual(selectCandidate([{id:'a',score:5},{id:'b',score:5}],{type:'max_numeric_field',field:'score'}),{id:'a',score:5});
});

test('declared transforms are immutable, and only allowlisted operations execute',()=>{
 const start={count:1,state:'PENDING'};
 const result=transformPayload(start,[{type:'increment',field:'count',by:2},{type:'set',field:'state',value:'DONE'}]);
 assert.deepEqual(result,{count:3,state:'DONE'});
 assert.deepEqual(start,{count:1,state:'PENDING'});
 assert.throws(()=>transformPayload(start,[{type:'eval',field:'state',code:'anything'}]),/unsupported/);
 assert.deepEqual(changesBetween(start,result).map(x=>x.field),['count','state']);
});

test('illustrative scenario cannot be accidentally executed',()=>{
 const bad={...model.scenarios[0],mode:'illustrative'};
 assert.throws(()=>runSyntheticScenario(bad),/only declared synthetic/);
});
