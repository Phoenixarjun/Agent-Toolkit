import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const css=readFileSync(new URL('../style.css',import.meta.url),'utf8');
const app=readFileSync(new URL('../src/app.js',import.meta.url),'utf8');

test('canvas-first light UI retains contextual inspector and flow controls',()=>{
  for(const id of ['world-canvas','inspector-panel','inspector-content','inspector-overview-tab','inspector-flow-tab','player','play-button','player-steps','rail-flows','close-player','rail-catalog','global-search','rail-coverage','view-2d','view-3d','rail-issues','reset-camera','camera-pan']){
    assert.ok(html.includes(`id="${id}"`),`missing ${id}`);
  }
  assert.ok(html.includes('id="inspector-panel"')&&html.includes('inspector-panel" aria-label="Selection inspector" hidden'));
  assert.ok(html.includes('id="player" class="flow-player" aria-label="Execution journey playback" hidden'));
  assert.ok(css.includes('--surface:#fff'));
  assert.ok(css.includes('.inspector-content{')&&css.includes('overflow-y:auto'));
  assert.ok(!html.includes('WEBGL2'));
  assert.ok(!html.includes('id="flow-picker"'));
  assert.ok(!html.includes('id="catalog-toggle"'));
  assert.ok(html.includes('data-tooltip="Execution flows"'));
  assert.ok(css.includes('.diagram-node'));
});

test('catalog preserves behavioral distinctions without vendor-specific component naming',()=>{
  for(const name of ['API gateway','Load balancer','Rate limiter','Graph database','Vector database','Partitioned event stream','Message broker','Worker','Scheduler','Transformation'])assert.ok(app.includes(`name:'${name}'`),name);
  assert.ok(app.includes('source evidence')||app.includes('Source evidence'));
  assert.ok(app.includes('this.issueRecords()'));
});

test('only local demonstration JSON is fetched automatically and payload inspection remains redacted',()=>{
  assert.ok(app.includes("fetch('./data/demo.json'"));
  assert.ok(app.includes('redactPayload(value??{})'));
  assert.ok(!app.includes('fetch(`http'));
  assert.ok(!app.includes('location.href='));
});
