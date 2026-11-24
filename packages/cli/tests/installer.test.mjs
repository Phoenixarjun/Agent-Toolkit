import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import {
  ensureSafeRelativePath,
  planInstallation,
  applyInstallation,
  sha256File,
} from '../src/installer.js';
import { mergeManagedEntrypointFile } from '../src/entrypoint.js';
import { loadContract } from '../src/distribution.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distResourcesDir = path.resolve(__dirname, '../../../dist/npm/cli/resources');

test('ensureSafeRelativePath enforces containment and rejects path traversal', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atk-test-path-'));
  try {
    // Valid
    const p1 = ensureSafeRelativePath(tmpDir, 'skills/code-review/SKILL.md');
    assert.ok(p1.startsWith(path.resolve(tmpDir)));

    // Rejections
    assert.throws(() => ensureSafeRelativePath(tmpDir, '../outside.txt'), /Path traversal/);
    assert.throws(() => ensureSafeRelativePath(tmpDir, '/etc/passwd'), /Path traversal/);
    assert.throws(() => ensureSafeRelativePath(tmpDir, '\\windows\\system32'), /Path traversal/);
    assert.throws(() => ensureSafeRelativePath(tmpDir, 'C:\\escape'), /Path traversal/);
    assert.throws(() => ensureSafeRelativePath(tmpDir, '\\\\server\\share'), /Path traversal/);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('mergeManagedEntrypointFile preserves user instructions and merges managed blocks', () => {
  const managedBlock = '<!-- BEGIN AGENT-TOOLKIT MANAGED BLOCK -->\nManaged v1\n<!-- END AGENT-TOOLKIT MANAGED BLOCK -->';
  
  // 1. Initial creation
  const created = mergeManagedEntrypointFile(null, managedBlock);
  assert.equal(created, managedBlock + '\n');

  // 2. Existing file with custom user instructions
  const userText = '# User Guidelines\nAlways be helpful.\n';
  const merged = mergeManagedEntrypointFile(userText, managedBlock);
  assert.ok(merged.includes(managedBlock));
  assert.ok(merged.includes('# User Guidelines'));
  assert.ok(merged.includes('Always be helpful.'));

  // 3. Update managed block in existing file
  const updatedManagedBlock = '<!-- BEGIN AGENT-TOOLKIT MANAGED BLOCK -->\nManaged v2 Updated\n<!-- END AGENT-TOOLKIT MANAGED BLOCK -->';
  const updated = mergeManagedEntrypointFile(merged, updatedManagedBlock);
  assert.ok(updated.includes('Managed v2 Updated'));
  assert.ok(!updated.includes('Managed v1'));
  assert.ok(updated.includes('# User Guidelines'));
});

test('applyInstallation creates files, entrypoint, and manifest', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atk-test-inst-'));
  try {
    const contract = loadContract('skill', 'code-review', 'claude-code', false, distResourcesDir);
    const result = applyInstallation(tmpDir, contract, { resourcesDir: distResourcesDir });

    assert.equal(result.status, 'SUCCESS');
    assert.ok(result.createdFiles.length >= 3);

    const manifestPath = path.join(tmpDir, '.agent-toolkit/manifest.json');
    assert.ok(fs.existsSync(manifestPath));
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
    assert.equal(manifest.adapter, 'claude-code');
    assert.equal(manifest.skill, 'code-review');
    assert.ok(Object.keys(manifest.files).length >= 3);

    // Verify entrypoint exists
    const entryPath = path.join(tmpDir, 'CLAUDE.md');
    assert.ok(fs.existsSync(entryPath));
    const entryContent = fs.readFileSync(entryPath, 'utf-8');
    assert.ok(entryContent.includes('BEGIN AGENT-TOOLKIT MANAGED BLOCK'));
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('conflict policy abort blocks unmanaged pre-existing file', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'atk-test-conflict-'));
  try {
    const conflictFile = path.join(tmpDir, '.claude/skills/code-review/SKILL.md');
    fs.mkdirSync(path.dirname(conflictFile), { recursive: true });
    fs.writeFileSync(conflictFile, '# Unmanaged custom content\n', 'utf-8');

    const contract = loadContract('skill', 'code-review', 'claude-code', false, distResourcesDir);

    // Should throw with abort
    assert.throws(
      () => applyInstallation(tmpDir, contract, { onConflict: 'abort', resourcesDir: distResourcesDir }),
      /Cannot apply installation due to \d+ conflict/
    );

    // Should succeed with force / replace and create backup
    const forceResult = applyInstallation(tmpDir, contract, {
      onConflict: 'replace',
      force: true,
      resourcesDir: distResourcesDir,
    });
    assert.equal(forceResult.status, 'SUCCESS');
    assert.ok(forceResult.backups.length >= 1);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});
