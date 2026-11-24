import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  loadDistributionIndex,
  normalizeAdapter,
  loadContract,
  findResourcesDir,
} from '../src/distribution.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distResourcesDir = path.resolve(__dirname, '../../../dist/npm/cli/resources');

test('distribution index loads and contains complete canonical inventory', () => {
  const index = loadDistributionIndex(distResourcesDir);
  assert.equal(index.packageName, '@agent-toolkit-core/cli');
  assert.equal(index.skills.length, 16);
  assert.equal(index.profiles.length, 8);
  assert.equal(index.adapters.length, 7);

  const skillIds = index.skills.map((s) => s.id);
  assert.ok(skillIds.includes('code-review'));
  assert.ok(skillIds.includes('career'));
  assert.ok(skillIds.includes('visualize'));
  assert.ok(skillIds.includes('security-audit'));

  const profileIds = index.profiles.map((p) => p.id);
  assert.ok(profileIds.includes('software-engineering'));
  assert.ok(profileIds.includes('career'));
  assert.ok(profileIds.includes('ui-ux'));
});

test('normalizeAdapter resolves exact names and aliases', () => {
  assert.equal(normalizeAdapter('claude-code', distResourcesDir).name, 'claude-code');
  assert.equal(normalizeAdapter('claude', distResourcesDir).name, 'claude-code');
  assert.equal(normalizeAdapter('codex', distResourcesDir).name, 'codex');
  assert.equal(normalizeAdapter('openai-codex', distResourcesDir).name, 'codex');
  assert.equal(normalizeAdapter('cursor', distResourcesDir).name, 'cursor');
  assert.equal(normalizeAdapter('gemini', distResourcesDir).name, 'gemini-cli');
  assert.equal(normalizeAdapter('copilot', distResourcesDir).name, 'github-copilot');
  assert.equal(normalizeAdapter('antigravity', distResourcesDir).name, 'antigravity');
  assert.equal(normalizeAdapter('agy', distResourcesDir).name, 'antigravity');

  assert.throws(() => normalizeAdapter('nonexistent-adapter', distResourcesDir), /Unsupported assistant adapter/);
});

test('loadContract loads valid compiled installation contract', () => {
  const contract = loadContract('skill', 'code-review', 'claude-code', false, distResourcesDir);
  assert.equal(contract.capability.id, 'code-review');
  assert.equal(contract.adapter, 'claude-code');
  assert.ok(contract.files.length >= 3);
  assert.ok(contract.entrypoint.file === 'CLAUDE.md');
  assert.ok(contract.entrypoint.managedBlock.includes('BEGIN AGENT-TOOLKIT MANAGED BLOCK'));
});
