import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startCompanionServer } from '../src/server.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const careerAppDir = path.resolve(__dirname, '../../../web-app/career');

function fetchUrl(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data,
        });
      });
    }).on('error', reject);
  });
}

test('startCompanionServer serves index.html and static files on loopback', async () => {
  const instance = await startCompanionServer(careerAppDir, { port: 4188 });
  try {
    assert.equal(instance.url, 'http://127.0.0.1:4188/');

    // Test GET /
    const rootRes = await fetchUrl(instance.url);
    assert.equal(rootRes.statusCode, 200);
    assert.ok(rootRes.headers['content-type'].includes('text/html'));
    assert.ok(rootRes.body.includes('<!doctype html>'));

    // Test GET /style.css
    const cssRes = await fetchUrl('http://127.0.0.1:4188/style.css');
    assert.equal(cssRes.statusCode, 200);
    assert.ok(cssRes.headers['content-type'].includes('text/css'));

    // Test GET path traversal attempt is blocked
    const escapeRes = await fetchUrl('http://127.0.0.1:4188/..%2f..%2fpackage.json');
    assert.ok(escapeRes.statusCode === 403 || escapeRes.statusCode === 404);
  } finally {
    await instance.close();
  }
});
