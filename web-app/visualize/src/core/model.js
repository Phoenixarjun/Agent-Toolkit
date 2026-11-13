export const EVIDENCE = Object.freeze(['SOURCE_VERIFIED', 'INFERRED', 'UNRESOLVED', 'CONTRADICTED']);
export const FAULTS = Object.freeze(['NONE', 'SUSPECTED', 'CONFIRMED', 'DISPROVEN', 'INDETERMINATE']);
export const ROLES = Object.freeze(['client', 'gateway', 'router', 'rate_limiter', 'service', 'module', 'worker', 'scheduler', 'storage', 'cache', 'broker', 'queue', 'stream', 'pubsub', 'decision', 'transform', 'external', 'sandbox', 'processor', 'topic', 'dns', 'cdn', 'ingress', 'firewall', 'identity', 'discovery', 'workflow', 'function', 'observability', 'cluster', 'subscription']);
export const STORAGE_VARIANTS = Object.freeze(['relational', 'document', 'column', 'graph', 'vector', 'key_value', 'time_series', 'object', 'wide_column', 'columnar', 'generic']);
export const MESSAGE_VARIANTS = Object.freeze(['fifo', 'partitioned_log', 'pubsub', 'routing', 'delayed', 'generic']);
const MAX_COMPONENTS = 2000;
const MAX_RELATIONS = 10000;
const MAX_JOURNEYS = 400;
const MAX_STEPS = 5000;

function fail(message) {
  throw new Error(`Model rejected: ${message}`);
}

function requiredString(value, path) {
  if (typeof value !== 'string' || !value.trim() || value.length > 256) fail(`${path} must be a nonempty string (max 256 characters)`);
  return value;
}

function uniqueRecords(records, label, limit) {
  if (!Array.isArray(records) || records.length > limit) fail(`${label} must be an array of at most ${limit}`);
  const index = new Map();
  for (const record of records) {
    if (!record || typeof record !== 'object' || Array.isArray(record)) fail(`${label} includes an invalid record`);
    const id = requiredString(record.id, `${label}.id`);
    if (index.has(id)) fail(`duplicate ${label} id ${id}`);
    index.set(id, record);
  }
  return index;
}

function validateRefs(record, id) {
  if (!Array.isArray(record.source_refs)) fail(`${id} is missing source_refs array`);
  if (record.evidence_status === 'SOURCE_VERIFIED' && !record.source_refs.length) fail(`${id} claims source verification without evidence`);
  for (const ref of record.source_refs) {
    if (!ref || typeof ref !== 'object' || typeof ref.path !== 'string' || !ref.path || ref.path.startsWith('/') || ref.path.includes('..') || ref.path.includes('\\')) fail(`${id} includes an unsafe source reference`);
  }
}

export function validateModel(model) {
  if (!model || typeof model !== 'object' || Array.isArray(model)) fail('root must be an object');
  if (model.schema_version !== '1.0.0') fail(`unsupported schema_version ${model.schema_version}`);
  for (const field of ['scope', 'snapshots', 'components', 'relations', 'journeys', 'scenarios', 'findings', 'coverage']) {
    if (!(field in model)) fail(`missing ${field}`);
  }
  if (!model.scope || !Array.isArray(model.snapshots) || !Array.isArray(model.scenarios) || !Array.isArray(model.findings) || !Array.isArray(model.coverage)) fail('invalid document metadata');
  const components = uniqueRecords(model.components, 'components', MAX_COMPONENTS);
  const relations = uniqueRecords(model.relations, 'relations', MAX_RELATIONS);
  const journeys = uniqueRecords(model.journeys, 'journeys', MAX_JOURNEYS);
  const scenarios = uniqueRecords(model.scenarios, 'scenarios', 400);
  const findings = uniqueRecords(model.findings, 'findings', 1000);
  for (const c of model.components) {
    requiredString(c.name, `${c.id}.name`);
    requiredString(c.responsibility, `${c.id}.responsibility`);
    requiredString(c.role, `${c.id}.role`);
    if (!ROLES.includes(c.role)) fail(`${c.id} uses unknown role ${c.role}`);
    if (!EVIDENCE.includes(c.evidence_status)) fail(`${c.id} has invalid evidence_status`);
    validateRefs(c, c.id);
    for (const field of ['domain', 'group_id', 'owner', 'repository']) if (c[field] !== undefined) requiredString(c[field], `${c.id}.${field}`);
    if (c.capabilities !== undefined && (!Array.isArray(c.capabilities) || c.capabilities.length > 32 || c.capabilities.some(v => typeof v !== 'string' || !v.trim() || v.length > 64))) fail(`${c.id} has invalid behavior capabilities`);
    if (c.parent_id != null && !components.has(c.parent_id)) fail(`${c.id} has missing parent ${c.parent_id}`);
    if (c.parent_id === c.id) fail(`${c.id} is its own parent`);
    if (c.visual_recipe !== undefined) {
      if (!Array.isArray(c.visual_recipe) || c.visual_recipe.length > 24) fail(`${c.id} has an oversized visual recipe`);
      for (const part of c.visual_recipe) {
        if (!['box', 'cylinder', 'sphere', 'cone', 'torus'].includes(part.shape)) fail(`${c.id} has an unsupported visual shape`);
        if (!Array.isArray(part.offset) || !Array.isArray(part.size) || part.offset.length !== 3 || part.size.length !== 3) fail(`${c.id} has invalid visual dimensions`);
        if (part.offset.some(v => !Number.isFinite(v) || Math.abs(v) > 6) || part.size.some(v => !Number.isFinite(v) || v <= 0 || v > 5)) fail(`${c.id} has unsafe visual dimensions`);
        if (part.color !== 'accent' && (typeof part.color !== 'string' || !/^#[0-9a-fA-F]{6}$/.test(part.color))) fail(`${c.id} has invalid visual color`);
        if (part.yaw !== undefined && (!Number.isFinite(part.yaw) || Math.abs(part.yaw) > 6.283185307179586)) fail(`${c.id} has invalid visual rotation`);
      }
    }
    if (c.role === 'storage' && c.variant && !STORAGE_VARIANTS.includes(c.variant)) fail(`${c.id} uses unsupported storage variant`);
    if (['queue', 'stream', 'pubsub', 'broker', 'topic'].includes(c.role) && c.variant && !MESSAGE_VARIANTS.includes(c.variant)) fail(`${c.id} uses unsupported message variant`);
  }
  const visited = new Set();
  const active = new Set();
  function visit(id) {
    if (active.has(id)) fail(`containment cycle at ${id}`);
    if (visited.has(id)) return;
    active.add(id);
    const parent = components.get(id).parent_id;
    if (parent != null) visit(parent);
    active.delete(id);
    visited.add(id);
  }
  for (const id of components.keys()) visit(id);
  for (const r of model.relations) {
    if (!components.has(r.from)) fail(`${r.id} has missing source component`);
    if (r.to != null && !components.has(r.to)) fail(`${r.id} has dangling destination`);
    if (r.to == null && (!r.unresolved_target || typeof r.unresolved_target !== 'string')) fail(`${r.id} lacks unresolved target description`);
    if (r.interaction !== undefined && !['request_response','request','response','publish','consume','read','write','replicate','route','schedule','stream','notify','discover','authenticate','authorize','other'].includes(r.interaction)) fail(`${r.id} has unknown interaction semantics`);
    if (!['forward', 'bidirectional'].includes(r.direction || 'forward')) fail(`${r.id} has invalid direction`);
    if (!EVIDENCE.includes(r.evidence_status) || !FAULTS.includes(r.fault_status || 'NONE')) fail(`${r.id} has invalid status`);
    if (r.finding_id && !findings.has(r.finding_id)) fail(`${r.id} references unknown finding`);
    validateRefs(r, r.id);
    if (r.fault_status === 'CONFIRMED') {
      const finding = findings.get(r.finding_id);
      if (!finding || finding.verdict !== 'CONFIRMED') fail(`${r.id} claims confirmed fault without confirmed finding`);
      if (typeof finding.justification !== 'string' || !finding.justification.trim() || !Array.isArray(finding.evidence_refs) || !finding.evidence_refs.length) fail(`${r.id} has a confirmed finding lacking explicit justification and evidence pointers`);
    }
  }
  for (const j of model.journeys) {
    if (!Array.isArray(j.steps) || j.steps.length > MAX_STEPS || !j.steps.length) fail(`${j.id} needs 1..${MAX_STEPS} steps`);
    if (j.coverage && !['covered', 'partial', 'unknown', 'blocked', 'out_of_scope'].includes(j.coverage)) fail(`${j.id} has invalid coverage`);
    const stepIds = new Set();
    for (const s of j.steps) {
      const id = requiredString(s.id, `${j.id}.step.id`);
      if (stepIds.has(id)) fail(`${j.id} repeats step id ${id}`);
      stepIds.add(id);
      if (!components.has(s.component_id)) fail(`${j.id}.${id} references unknown component`);
      if (s.via_relation_id && !relations.has(s.via_relation_id)) fail(`${j.id}.${id} references unknown relation`);
      if (s.certainty && !EVIDENCE.includes(s.certainty)) fail(`${j.id}.${id} has invalid certainty`);
      if (s.explanation !== undefined && (typeof s.explanation !== 'string' || s.explanation.length > 1200)) fail(`${j.id}.${id} has invalid explanation`);
    }
    if (j.execution_edges !== undefined) {
      if (!Array.isArray(j.execution_edges) || j.execution_edges.length > MAX_STEPS * 3) fail(`${j.id} has invalid execution edges`);
      const ids = new Set();
      for (const edge of j.execution_edges) {
        const eid = requiredString(edge.id, `${j.id}.edge.id`);
        if (ids.has(eid)) fail(`${j.id} repeats execution edge ${eid}`);
        ids.add(eid);
        if (!stepIds.has(edge.from_step_id) || !stepIds.has(edge.to_step_id)) fail(`${j.id}.${eid} has unknown execution stage`);
        if (edge.from_step_id === edge.to_step_id && edge.type !== 'retry') fail(`${j.id}.${eid} must not loop without retry semantics`);
        if (!['sequence','request_response','publish','consume','branch','fan_out','fan_in','retry','timeout','fallback','compensate','return','async'].includes(edge.type)) fail(`${j.id}.${eid} has invalid execution type`);
        if (edge.via_relation_id && !relations.has(edge.via_relation_id)) fail(`${j.id}.${eid} references unknown relationship`);
        if (edge.condition !== undefined && (typeof edge.condition !== 'string' || edge.condition.length > 512)) fail(`${j.id}.${eid} has invalid condition`);
      }
    }
    if (j.playback_path !== undefined) {
      if (!Array.isArray(j.playback_path) || !j.playback_path.length || j.playback_path.length > MAX_STEPS || j.playback_path.some(id => !stepIds.has(id))) fail(`${j.id} has invalid playback path`);
      if (j.execution_edges && j.playback_path.some((id, i) => i > 0 && !j.execution_edges.some(e => e.from_step_id === j.playback_path[i-1] && e.to_step_id === id))) fail(`${j.id} playback path includes undeclared transition`);
    }
  }
  for (const s of model.scenarios) {
    if (!journeys.has(s.journey_id)) fail(`${s.id} references missing journey`);
    if (!['illustrative', 'synthetic'].includes(s.mode)) fail(`${s.id} has unsupported scenario mode`);
    if (s.rules !== undefined && !Array.isArray(s.rules)) fail(`${s.id} has invalid rules`);
    for (const rule of s.rules || []) if (rule.component_id && !components.has(rule.component_id)) fail(`${s.id} has a rule targeting a nonexistent component`);
  }
  return Object.freeze({ components, relations, journeys, scenarios, findings });
}

export function ancestors(componentId, components) {
  const chain = [];
  let id = componentId;
  while (id != null && components.has(id)) {
    chain.push(id);
    id = components.get(id).parent_id;
  }
  return chain;
}

export function visibleAtLevel(componentId, viewParentId, components) {
  const chain = ancestors(componentId, components);
  if (!chain.length) return null;
  if (viewParentId === null) return chain.at(-1);
  const i = chain.indexOf(viewParentId);
  return i > 0 ? chain[i - 1] : null;
}

export function projectJourney(journey, viewParentId, components) {
  const result = [];
  for (const step of journey.steps) {
    const visibleId = visibleAtLevel(step.component_id, viewParentId, components);
    const last = result.at(-1);
    if (last && last.visibleId === visibleId && last.branch === (step.branch ?? null)) {
      last.steps.push(step);
    } else {
      result.push({ visibleId, branch: step.branch ?? null, steps: [step], offLevel: visibleId === null });
    }
  }
  return result;
}

export function viewGraph(model, viewParentId, indexes = validateModel(model)) {
  const nodes = model.components.filter(c => (c.parent_id ?? null) === viewParentId);
  const visibleIds = new Set(nodes.map(n => n.id));
  const result = new Map();
  for (const r of model.relations) {
    const localFrom = visibleAtLevel(r.from, viewParentId, indexes.components);
    const localTo = r.to == null ? null : visibleAtLevel(r.to, viewParentId, indexes.components);
    const fromInside = visibleIds.has(localFrom);
    const toInside = visibleIds.has(localTo);
    if (fromInside && toInside && localFrom !== localTo) {
      const key = `${r.id}:${localFrom}:${localTo}`;
      result.set(key, { ...r, from: localFrom, to: localTo, projected: localFrom !== r.from || localTo !== r.to });
    } else if (fromInside && r.to == null) {
      result.set(`${r.id}:${localFrom}:?`, { ...r, from: localFrom, to: null, projected: localFrom !== r.from });
    } else if (viewParentId !== null && fromInside && r.to != null && !toInside) {
      result.set(`${r.id}:${localFrom}:out`, { ...r, from: localFrom, to: null, boundary: true, boundaryDirection: r.direction === 'bidirectional' ? 'bidirectional' : 'outgoing', unresolved_target: `Outside: ${indexes.components.get(r.to).name}`, projected: true });
    } else if (viewParentId !== null && toInside && !fromInside) {
      result.set(`${r.id}:${localTo}:in`, { ...r, from: localTo, to: null, boundary: true, boundaryDirection: r.direction === 'bidirectional' ? 'bidirectional' : 'incoming', unresolved_target: `Outside: ${indexes.components.get(r.from).name}`, projected: true });
    }
  }
  return { nodes, edges: [...result.values()], parentId: viewParentId };
}

export function redactPayload(value, depth = 0) {
  if (depth > 6) return '[nested]';
  if (Array.isArray(value)) return value.slice(0, 30).map(v => redactPayload(v, depth + 1));
  if (!value || typeof value !== 'object') return typeof value === 'string' ? value.slice(0, 200) : value;
  const output = {};
  for (const [key, item] of Object.entries(value).slice(0, 50)) {
    if (/(secret|token|password|credential|api.?key|cookie|authorization|email|phone|address|ssn|tenant.?id|user.?id)/i.test(key)) output[key] = '[redacted]';
    else output[key] = redactPayload(item, depth + 1);
  }
  return output;
}
