import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { applyInstallation } from '../src/installer.js';
import { runDoctor } from '../src/doctor.js';
import { loadContract } from '../src/distribution.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distResourcesDir = path.resolve(__dirname, '../../../dist/npm/cli/resources');

test('doctor passes on freshly installed workspace', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atk-test-doc-'));
  try {
    const contract = loadContract('skill', 'code-review', 'claude-code', false, distResourcesDir);
    applyInstallation(tmpDir, contract, { resourcesDir: distResourcesDir });

    const doc = runDoctor(tmpDir);
    assert.equal(doc.status, 'PASS');
    assert.equal(doc.manifest_present, true);
    assert.ok(doc.verified_files >= 3);
    assert.equal(doc.missing_files.length, 0);
    assert.equal(doc.corrupted_files.length, 0);
    assert.equal(doc.errors.length, 0);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('doctor detects missing file and fails', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atk-test-doc-miss-'));
  try {
    const contract = loadContract('skill', 'code-review', 'claude-code', false, distResourcesDir);
    applyInstallation(tmpDir, contract, { resourcesDir: distResourcesDir });

    const fileToDelete = path.join(tmpDir, '.claude/skills/code-review/SKILL.md');
    fs.rmSync(fileToDelete);

    const doc = runDoctor(tmpDir);
    assert.equal(doc.status, 'FAIL');
    assert.ok(doc.missing_files.some((f) => f.includes('SKILL.md')));
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('doctor detects corrupted or modified file and fails', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atk-test-doc-mod-'));
  try {
    const contract = loadContract('skill', 'code-review', 'claude-code', false, distResourcesDir);
    applyInstallation(tmpDir, contract, { resourcesDir: distResourcesDir });

    const fileToCorrupt = path.join(tmpDir, '.claude/skills/code-review/SKILL.md');
    fs.writeFileSync(fileToCorrupt, '# TAMPERED BY OUTSIDE PROCESS\n', 'utf-8');

    const doc = runDoctor(tmpDir);
    assert.equal(doc.status, 'FAIL');
    assert.ok(doc.corrupted_files.some((f) => f.includes('SKILL.md')));
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});
