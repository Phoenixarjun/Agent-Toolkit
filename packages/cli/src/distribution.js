import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function findResourcesDir(customPath = null) {
  if (customPath) {
    if (fs.existsSync(customPath)) return customPath;
  }
  const candidates = [
    path.resolve(__dirname, '../resources'),
    path.resolve(__dirname, '../../resources'),
    path.resolve(process.cwd(), 'resources'),
    path.resolve(process.cwd(), 'dist/npm/cli/resources'),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, 'distribution-index.json'))) {
      return c;
    }
  }
  throw new Error(`Unable to locate Agent Toolkit distribution resources. Checked: ${candidates.join(', ')}`);
}

let cachedIndex = null;
let cachedResourcesDir = null;

export function loadDistributionIndex(resourcesDir = null) {
  const dir = findResourcesDir(resourcesDir);
  if (cachedIndex && cachedResourcesDir === dir) {
    return cachedIndex;
  }
  const indexPath = path.join(dir, 'distribution-index.json');
  const raw = fs.readFileSync(indexPath, 'utf-8');
  cachedIndex = JSON.parse(raw);
  cachedResourcesDir = dir;
  return cachedIndex;
}

export function normalizeAdapter(nameOrAlias, resourcesDir = null) {
  if (!nameOrAlias || typeof nameOrAlias !== 'string') {
    throw new Error('Adapter must be specified as a non-empty string.');
  }
  const index = loadDistributionIndex(resourcesDir);
  const target = nameOrAlias.trim().toLowerCase();
  for (const ad of index.adapters) {
    if (ad.name.toLowerCase() === target) {
      return ad;
    }
    if (ad.aliases && ad.aliases.some((a) => a.toLowerCase() === target)) {
      return ad;
    }
  }
  const available = index.adapters.map((a) => a.name).join(', ');
  throw new Error(`Unsupported assistant adapter '${nameOrAlias}'. Available adapters: ${available}`);
}

export function loadContract(type, id, adapterName, allOptional = false, resourcesDir = null) {
  const dir = findResourcesDir(resourcesDir);
  const index = loadDistributionIndex(resourcesDir);
  const ad = normalizeAdapter(adapterName, resourcesDir);
  const normalizedType = type.toLowerCase().trim();
  const normalizedId = id.toLowerCase().trim();

  const key = `${normalizedType}:${normalizedId}:${ad.name}:${allOptional ? 'all_opt' : 'default'}`;
  let contractRelPath = index.contractsIndex[key];
  if (!contractRelPath && allOptional) {
    // Fall back to default if all_opt is identical
    const fallbackKey = `${normalizedType}:${normalizedId}:${ad.name}:default`;
    contractRelPath = index.contractsIndex[fallbackKey];
  }
  if (!contractRelPath) {
    throw new Error(`No compiled installation contract found for ${normalizedType} '${id}' on adapter '${adapterName}'.`);
  }
  const contractFullPath = path.join(dir, contractRelPath);
  if (!fs.existsSync(contractFullPath)) {
    throw new Error(`Compiled contract missing on disk: ${contractFullPath}`);
  }
  const raw = fs.readFileSync(contractFullPath, 'utf-8');
  return JSON.parse(raw);
}
