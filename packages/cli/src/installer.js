import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { mergeManagedEntrypointFile } from './entrypoint.js';
import { loadManifest, saveManifest, createInitialManifest } from './manifest.js';
import { findResourcesDir } from './distribution.js';

export function sha256Content(content) {
  const hasher = crypto.createHash('sha256');
  if (typeof content === 'string') {
    hasher.update(content, 'utf-8');
  } else {
    hasher.update(content);
  }
  return hasher.digest('hex');
}

export function sha256File(filePath) {
  const hasher = crypto.createHash('sha256');
  const buffer = fs.readFileSync(filePath);
  hasher.update(buffer);
  return hasher.digest('hex');
}

export function ensureSafeRelativePath(targetDir, relPath, rejectSymlinks = false) {
  if (typeof relPath !== 'string') {
    throw new Error(`Invalid path type: expected string, got ${typeof relPath}`);
  }
  const trimmed = relPath.trim();
  if (!trimmed) {
    throw new Error('Invalid relative path: path cannot be empty');
  }

  // Reject leading slashes or Windows absolute / drive / UNC
  if (trimmed.startsWith('/') || trimmed.startsWith('\\')) {
    throw new Error(`Path traversal detected: root-relative or absolute path '${relPath}'`);
  }
  if (path.isAbsolute(trimmed) || /^[a-zA-Z]:/.test(trimmed) || trimmed.startsWith('\\\\')) {
    throw new Error(`Path traversal detected: absolute or drive-qualified path '${relPath}'`);
  }

  // Check parts for traversal
  const normalized = path.normalize(trimmed);
  const parts = normalized.split(/[/\\]+/);
  for (const part of parts) {
    if (part === '..' || part.startsWith('..')) {
      throw new Error(`Path traversal detected: '${relPath}' contains parent traversal component`);
    }
  }

  const resolvedTarget = path.resolve(targetDir);
  const resolvedChild = path.resolve(targetDir, normalized);

  // Check containment
  if (!resolvedChild.startsWith(resolvedTarget + path.sep) && resolvedChild !== resolvedTarget) {
    throw new Error(`Destination path escapes target directory: '${relPath}'`);
  }

  // Check symlinks along existing components if rejectSymlinks
  if (rejectSymlinks && fs.existsSync(resolvedChild)) {
    const stat = fs.lstatSync(resolvedChild);
    if (stat.isSymbolicLink()) {
      throw new Error(`Symlink rejected: '${relPath}' is a symbolic link`);
    }
  }

  return resolvedChild;
}

export function planInstallation(targetDir, contract, options = {}) {
  const onConflict = options.onConflict || (options.force ? 'replace' : 'abort');
  const existingManifest = loadManifest(targetDir);
  const existingFiles = existingManifest ? existingManifest.files || {} : {};

  const conflicts = [];
  const warnings = [];
  const filesToCreate = [];
  const filesToUpdate = [];
  const filesToKeep = [];

  const entrypointFile = contract.entrypoint ? contract.entrypoint.file : null;

  for (const fileItem of contract.files) {
    const relDest = fileItem.rel_destination;
    const destFull = ensureSafeRelativePath(targetDir, relDest);
    const exists = fs.existsSync(destFull);

    if (relDest === entrypointFile) {
      if (exists) {
        filesToUpdate.push({ ...fileItem, destFull, reason: 'MERGE_ENTRYPOINT' });
      } else {
        filesToCreate.push({ ...fileItem, destFull });
      }
      continue;
    }

    if (exists) {
      const isManaged = Boolean(existingFiles[relDest]);
      if (isManaged) {
        const currentHash = sha256File(destFull);
        const recordedHash = existingFiles[relDest].sha256;
        if (currentHash !== recordedHash) {
          warnings.push(`Locally modified managed file: ${relDest}`);
        }
        if (onConflict === 'replace' || onConflict === 'abort') {
          filesToUpdate.push({ ...fileItem, destFull, reason: 'UPDATE_MANAGED' });
        } else if (onConflict === 'keep') {
          filesToKeep.push({ ...fileItem, destFull });
        }
      } else {
        // Unmanaged existing file
        const conflictMsg = `Pre-existing unmanaged file: ${relDest}`;
        conflicts.push(conflictMsg);
        if (onConflict === 'replace') {
          filesToUpdate.push({ ...fileItem, destFull, reason: 'REPLACE_UNMANAGED' });
        } else if (onConflict === 'keep') {
          filesToKeep.push({ ...fileItem, destFull });
        }
      }
    } else {
      filesToCreate.push({ ...fileItem, destFull });
    }
  }

  return {
    targetDir: path.resolve(targetDir),
    contract,
    onConflict,
    conflicts,
    warnings,
    filesToCreate,
    filesToUpdate,
    filesToKeep,
  };
}

export function applyInstallation(targetDir, contract, options = {}) {
  const plan = planInstallation(targetDir, contract, options);

  if (plan.conflicts.length > 0 && plan.onConflict === 'abort') {
    const err = new Error(
      `Cannot apply installation due to ${plan.conflicts.length} conflict(s):\n` +
      plan.conflicts.map((c) => `  - ${c}`).join('\n') +
      '\nUse --force or --on-conflict {replace,keep} to resolve.'
    );
    err.conflicts = plan.conflicts;
    throw err;
  }

  const resourcesDir = findResourcesDir(options.resourcesDir);
  let manifest = loadManifest(targetDir);
  if (!manifest) {
    manifest = createInitialManifest(contract, plan.onConflict);
  } else {
    // Merge artifacts
    manifest.installed_at = new Date().toISOString();
    manifest.adapter = contract.adapter;
    if (contract.capability.type === 'profile') {
      manifest.profile = contract.capability.id;
    } else {
      manifest.skill = contract.capability.id;
    }
    const existingArtKeys = new Set((manifest.artifacts || []).map((a) => `${a.group}:${a.id}`));
    for (const art of contract.resolvedArtifacts || []) {
      const k = `${art.group}:${art.id}`;
      if (!existingArtKeys.has(k)) {
        manifest.artifacts.push(art);
        existingArtKeys.add(k);
      }
    }
  }

  const backups = [];
  const created = [];
  const updated = [];

  const entrypointFile = contract.entrypoint ? contract.entrypoint.file : null;

  for (const item of contract.files) {
    const relDest = item.rel_destination;
    const destFull = ensureSafeRelativePath(targetDir, relDest);
    const parentDir = path.dirname(destFull);
    fs.mkdirSync(parentDir, { recursive: true });

    let fileContent = null;
    let fileHash = null;

    if (relDest === entrypointFile) {
      let existingText = null;
      if (fs.existsSync(destFull)) {
        existingText = fs.readFileSync(destFull, 'utf-8');
      }
      const isCursor = contract.adapter === 'cursor';
      fileContent = mergeManagedEntrypointFile(existingText, contract.entrypoint.managedBlock, isCursor);
      fileHash = sha256Content(fileContent);
      fs.writeFileSync(destFull, fileContent, 'utf-8');
      if (existingText !== null) {
        updated.push(relDest);
      } else {
        created.push(relDest);
      }
    } else {
      if (item.content !== undefined && item.content !== null) {
        fileContent = item.content;
        fileHash = sha256Content(fileContent);
      } else if (item.source_path) {
        const srcFull = path.join(resourcesDir, item.source_path);
        if (!fs.existsSync(srcFull)) {
          throw new Error(`Package resource missing: ${item.source_path}`);
        }
        fileContent = fs.readFileSync(srcFull);
        fileHash = sha256Content(fileContent);
      } else {
        throw new Error(`File specification for ${relDest} has neither content nor source_path`);
      }

      const exists = fs.existsSync(destFull);
      if (exists) {
        if (plan.onConflict === 'keep' && !manifest.files[relDest]) {
          // Skip keep
          continue;
        }
        // Backup if unmanaged and replace
        if (!manifest.files[relDest] && plan.onConflict === 'replace') {
          const bakPath = `${destFull}.bak.${Date.now()}`;
          fs.copyFileSync(destFull, bakPath);
          backups.push(path.relative(targetDir, bakPath));
        }
        updated.push(relDest);
      } else {
        created.push(relDest);
      }

      fs.writeFileSync(destFull, fileContent);
    }

    manifest.files[relDest] = {
      sha256: fileHash,
      source: item.source_path || null,
      adapter_specific: Boolean(item.is_adapter_specific),
    };
  }

  manifest.backups = (manifest.backups || []).concat(backups);
  saveManifest(targetDir, manifest);

  return {
    status: 'SUCCESS',
    adapter: contract.adapter,
    capability: contract.capability,
    createdFiles: created,
    updatedFiles: updated,
    backups,
    manifest,
  };
}
