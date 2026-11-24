import fs from 'node:fs';
import path from 'node:path';

export const MANIFEST_REL_PATH = path.join('.agent-toolkit', 'manifest.json');

export function loadManifest(targetDir) {
  const manifestPath = path.join(targetDir, MANIFEST_REL_PATH);
  if (!fs.existsSync(manifestPath)) {
    return null;
  }
  try {
    const raw = fs.readFileSync(manifestPath, 'utf-8');
    return JSON.parse(raw);
  } catch (err) {
    throw new Error(`Corrupt or unreadable manifest at ${manifestPath}: ${err.message}`);
  }
}

export function saveManifest(targetDir, manifestData) {
  const manifestPath = path.join(targetDir, MANIFEST_REL_PATH);
  const dir = path.dirname(manifestPath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(manifestPath, JSON.stringify(manifestData, null, 2) + '\n', 'utf-8');
}

export function createInitialManifest(contract, conflictPolicy = 'abort') {
  return {
    schema_version: '1.1.0',
    installed_at: new Date().toISOString(),
    adapter: contract.adapter,
    profile: contract.capability.type === 'profile' ? contract.capability.id : null,
    skill: contract.capability.type === 'skill' ? contract.capability.id : null,
    artifacts: contract.resolvedArtifacts || [],
    aliases: {},
    conflict_policy: conflictPolicy,
    files: {},
    backups: [],
  };
}
