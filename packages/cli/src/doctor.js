import fs from 'node:fs';
import path from 'node:path';
import { loadManifest } from './manifest.js';
import { sha256File } from './installer.js';

export function runDoctor(targetDir) {
  const resolvedTarget = path.resolve(targetDir);
  const result = {
    status: 'PASS',
    target_dir: resolvedTarget,
    manifest_present: false,
    adapter: null,
    profile: null,
    skill: null,
    verified_files: 0,
    missing_files: [],
    corrupted_files: [],
    shadowed_skills: [],
    warnings: [],
    errors: [],
  };

  if (!fs.existsSync(resolvedTarget)) {
    result.status = 'FAIL';
    result.errors.push(`Target directory does not exist: ${resolvedTarget}`);
    return result;
  }

  let manifest = null;
  try {
    manifest = loadManifest(resolvedTarget);
  } catch (err) {
    result.status = 'FAIL';
    result.errors.push(err.message);
    return result;
  }

  if (!manifest) {
    result.status = 'FAIL';
    result.errors.push('No .agent-toolkit/manifest.json found. Target directory does not appear to be an installed Agent Toolkit workspace.');
    return result;
  }

  result.manifest_present = true;
  result.adapter = manifest.adapter || null;
  result.profile = manifest.profile || null;
  result.skill = manifest.skill || null;

  const files = manifest.files || {};
  for (const [relDest, meta] of Object.entries(files)) {
    const fullPath = path.resolve(resolvedTarget, relDest);
    if (!fs.existsSync(fullPath)) {
      result.missing_files.push(relDest);
      continue;
    }

    try {
      const currentHash = sha256File(fullPath);
      const recordedHash = meta ? meta.sha256 : null;
      if (recordedHash && currentHash !== recordedHash) {
        result.corrupted_files.push(relDest);
      } else {
        result.verified_files += 1;
      }
    } catch (err) {
      result.errors.push(`Cannot read ${relDest}: ${err.message}`);
    }
  }

  if (result.missing_files.length > 0 || result.corrupted_files.length > 0 || result.errors.length > 0) {
    result.status = 'FAIL';
  }

  return result;
}
