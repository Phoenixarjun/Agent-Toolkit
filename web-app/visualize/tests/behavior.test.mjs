import test from 'node:test';
import assert from 'node:assert/strict';
import { simulateQueue, simulatePartitionedLog, simulateCache, simulateWorkerPool } from '../src/core/simulation.js';

test('FIFO queue preserves depth and enforces bounded capacity',()=>{
 const result=simulateQueue([
  {time:0,type:'enqueue',id:'a'},
  {time:1,type:'enqueue',id:'b'},
  {time:2,type:'enqueue',id:'c'},
  {time:3,type:'dequeue'},
  {time:4,type:'dequeue'},
  {time:5,type:'dequeue'}
 ],2);
 assert.equal(result.enqueued,2);
 assert.equal(result.rejected,1);
 assert.equal(result.dequeued,2);
 assert.equal(result.emptyReads,1);
 assert.equal(result.depth,0);
});

test('partitioned append log gives stable per-key partition and increasing offsets',()=>{
 const r=simulatePartitionedLog([{key:'team-a'},{key:'team-b'},{key:'team-a'}],4);
 assert.equal(r.eventCount,3);
 assert.equal(r.samples[0].partition,r.samples[2].partition);
 assert.equal(r.samples[2].offset,r.samples[0].offset+1+(r.samples[1].partition===r.samples[0].partition?1:0));
 assert.equal(r.offsets.reduce((a,b)=>a+b,0),3);
});

test('cache TTL expires exactly at boundary and never reads stale entries',()=>{
 const r=simulateCache([
  {time:0,type:'set',key:'a',value:1,ttl:5},
  {time:4.999,type:'get',key:'a'},
  {time:5,type:'get',key:'a'},
  {time:6,type:'delete',key:'a'}
 ]);
 assert.equal(r.hits,1);
 assert.equal(r.misses,1);
 assert.equal(r.deletes,0);
 assert.equal(r.entries,0);
});

test('worker pool schedules on first free worker without inventing latency',()=>{
 const r=simulateWorkerPool([{arrival:0,duration:2},{arrival:0,duration:3},{arrival:1,duration:1},{arrival:2,duration:1}],2);
 assert.equal(r.jobs,4);
 assert.equal(r.delayed,2);
 assert.equal(r.samples[2].started,2);
 assert.equal(r.finishedAt,4);
 assert.equal(r.samples[3].started,3);
});

test('invalid behavior inputs fail rather than silently auto-correct',()=>{
 assert.throws(()=>simulateQueue([{time:1,type:'enqueue'},{time:0,type:'dequeue'}],1),/time-ordered/);
 assert.throws(()=>simulatePartitionedLog([{unknown:'key'}],3),/requires a key/);
 assert.throws(()=>simulateCache([{time:0,type:'set',key:'a',ttl:-1}]),/positive TTL/);
 assert.throws(()=>simulateWorkerPool([{arrival:0,duration:-1}],1),/nonnegative/);
});
