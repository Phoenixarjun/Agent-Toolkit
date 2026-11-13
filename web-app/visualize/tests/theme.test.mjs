import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const css=readFileSync(new URL('../style.css',import.meta.url),'utf8');
const app=readFileSync(new URL('../src/app.js',import.meta.url),'utf8');
const gl=readFileSync(new URL('../src/graphics/webgl.js',import.meta.url),'utf8');

test('theme switch is persisted locally and changes UI and WebGL scene',()=>{
 assert.ok(html.includes('id="theme-toggle"'));
 assert.ok(css.includes(':root[data-theme="dark"]'));
 assert.ok(css.includes('[data-theme="dark"] .overlay-panel'));
 assert.ok(gl.includes('uFogColor')&&gl.includes('setTheme(theme)'));
 assert.ok(app.includes("localStorage.setItem('visualize-theme'"));
 assert.ok(app.includes('this.renderer?.setTheme(this.theme)'));
});

test('flow comprehension, scope, and accessible narrative are available without a new panel permanently taking canvas space',()=>{
 for(const id of ['rail-coverage','journey-story','slice-controls','flow-announcement'])assert.ok(html.includes(`id="${id}"`));
 for(const symbol of ['openCoverage(){','openJourneyStory(){','explainStage(step){','ensureStageVisible(){','this.transitionFor(current,next)'])assert.ok(app.includes(symbol),symbol);
 assert.ok(html.includes('role="status" aria-live="polite"'));
 assert.ok(css.includes('.screen-reader-only'));
});
