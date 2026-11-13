import { redactPayload } from './model.js';

const MAX_EVENTS = 250000;
const MAX_PACKET_SAMPLES = 48;

function validInteger(value, name, min, max) {
  if (!Number.isSafeInteger(value) || value < min || value > max) throw new Error(`${name} must be an integer from ${min} to ${max}`);
  return value;
}

export function runTokenBucket({ count, arrivalRatePerSecond, capacity, refillPerSecond, initialTokens = capacity }) {
  validInteger(count, 'count', 1, MAX_EVENTS);
  for (const [name, value] of Object.entries({ arrivalRatePerSecond, capacity, refillPerSecond, initialTokens })) {
    if (!Number.isFinite(value) || value < 0) throw new Error(`${name} must be a finite nonnegative number`);
  }
  if (arrivalRatePerSecond <= 0 || capacity <= 0 || initialTokens > capacity) throw new Error('invalid token bucket settings');
  let tokens = initialTokens;
  let accepted = 0;
  let rejected = 0;
  const samples = [];
  let previousTime = 0;
  const stride = Math.max(1, Math.ceil(count / MAX_PACKET_SAMPLES));
  for (let i = 0; i < count; i++) {
    const now = i / arrivalRatePerSecond;
    tokens = Math.min(capacity, tokens + (now - previousTime) * refillPerSecond);
    const allowed = tokens + 1e-9 >= 1;
    if (allowed) { tokens = Math.max(0, tokens - 1); accepted++; }
    else rejected++;
    if (i % stride === 0 || i === count - 1) samples.push({ index: i, time: now, allowed, tokens: Number(tokens.toFixed(5)) });
    previousTime = now;
  }
  return { mode: 'synthetic', total: count, accepted, rejected, durationSeconds: (count - 1) / arrivalRatePerSecond, samples, finalTokens: tokens };
}

function copy(value) { return structuredClone(value); }

export function transformPayload(input, operations) {
  if (!input || Array.isArray(input) || typeof input !== 'object') throw new Error('payload must be a plain object');
  if (!Array.isArray(operations) || operations.length > 50) throw new Error('operations must be a bounded array');
  const out = copy(input);
  for (const op of operations) {
    if (!op || !['set', 'delete', 'copy', 'increment'].includes(op.type)) throw new Error('unsupported payload operation');
    if (!/^[A-Za-z_][A-Za-z0-9_]{0,63}$/.test(op.field || '')) throw new Error('invalid payload field');
    if (op.type === 'delete') delete out[op.field];
    if (op.type === 'set') out[op.field] = copy(op.value);
    if (op.type === 'copy') {
      if (!/^[A-Za-z_][A-Za-z0-9_]{0,63}$/.test(op.from || '') || !(op.from in out)) throw new Error('invalid copy source');
      out[op.field] = copy(out[op.from]);
    }
    if (op.type === 'increment') {
      const current = out[op.field] ?? 0;
      if (!Number.isFinite(current) || !Number.isFinite(op.by)) throw new Error('invalid numeric increment');
      out[op.field] = current + op.by;
    }
  }
  return out;
}

export function selectCandidate(candidates, rule) {
  if (!Array.isArray(candidates) || candidates.length > 10000 || !candidates.length) throw new Error('candidate list must be nonempty and bounded');
  if (rule?.type !== 'max_numeric_field' || !/^[A-Za-z_][A-Za-z0-9_]{0,63}$/.test(rule.field || '')) throw new Error('unsupported candidate selection rule');
  const qualified = candidates.filter(c => c && typeof c === 'object' && Number.isFinite(c[rule.field]));
  if (!qualified.length) return null;
  let best = qualified[0];
  for (const item of qualified.slice(1)) if (item[rule.field] > best[rule.field]) best = item;
  return copy(best);
}

export function simulateQueue(operations, capacity = 32) {
  validInteger(capacity, 'capacity', 1, 100000);
  if (!Array.isArray(operations) || operations.length > MAX_EVENTS) throw new Error('queue operations exceed bounds');
  const queue = [];
  const history = [];
  const counts = { enqueued: 0, dequeued: 0, rejected: 0, emptyReads: 0 };
  let priorTime = -Infinity;
  for (const op of operations) {
    if (!op || !Number.isFinite(op.time) || op.time < priorTime || !['enqueue', 'dequeue'].includes(op.type)) throw new Error('queue operations must be time-ordered and supported');
    priorTime = op.time;
    if (op.type === 'enqueue') {
      if (queue.length >= capacity) counts.rejected++;
      else { queue.push({ id: op.id ?? `q${counts.enqueued}`, payload: redactPayload(op.payload || {}) }); counts.enqueued++; }
    } else if (queue.length) { queue.shift(); counts.dequeued++; }
    else counts.emptyReads++;
    if (history.length < MAX_PACKET_SAMPLES) history.push({ time: op.time, type: op.type, depth: queue.length });
  }
  return { mode: 'synthetic', ...counts, depth: queue.length, capacity, history };
}

function hashKey(key) {
  let h = 2166136261;
  for (const ch of String(key)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return h >>> 0;
}

export function simulatePartitionedLog(events, partitionCount) {
  validInteger(partitionCount, 'partitionCount', 1, 64);
  if (!Array.isArray(events) || events.length > MAX_EVENTS) throw new Error('stream events exceed bounds');
  const offsets = Array(partitionCount).fill(0);
  const samples = [];
  for (const event of events) {
    if (!event || !['string', 'number'].includes(typeof event.key)) throw new Error('partitioned event requires a key');
    const partition = hashKey(event.key) % partitionCount;
    const offset = offsets[partition]++;
    if (samples.length < MAX_PACKET_SAMPLES) samples.push({ key: String(event.key).slice(0, 64), partition, offset });
  }
  return { mode: 'synthetic', eventCount: events.length, partitionCount, offsets, samples };
}

export function simulateCache(operations) {
  if (!Array.isArray(operations) || operations.length > MAX_EVENTS) throw new Error('cache operations exceed bounds');
  const store = new Map();
  let hits = 0, misses = 0, writes = 0, deletes = 0;
  let priorTime = -Infinity;
  const samples = [];
  for (const op of operations) {
    if (!op || !Number.isFinite(op.time) || op.time < priorTime || typeof op.key !== 'string' || op.key.length > 128 || !['set','get','delete'].includes(op.type)) throw new Error('cache operations must be time-ordered and supported');
    priorTime = op.time;
    const record = store.get(op.key);
    const alive = record && record.expiresAt > op.time;
    if (record && !alive) store.delete(op.key);
    if (op.type === 'set') {
      if (!Number.isFinite(op.ttl) || op.ttl <= 0) throw new Error('cache write requires positive TTL');
      store.set(op.key,{ expiresAt:op.time+op.ttl, value:redactPayload(op.value) });
      writes++;
    } else if (op.type === 'delete') { if (store.delete(op.key)) deletes++; }
    else if (alive) hits++;
    else misses++;
    if (samples.length < MAX_PACKET_SAMPLES) samples.push({ time:op.time, key:op.key, type:op.type, hit:op.type==='get'?!!alive:null });
  }
  return { mode:'synthetic', hits, misses, writes, deletes, entries:store.size, samples };
}

export function simulateWorkerPool(jobs, workerCount) {
  validInteger(workerCount, 'workerCount', 1, 128);
  if (!Array.isArray(jobs) || jobs.length > MAX_EVENTS) throw new Error('worker jobs exceed bounds');
  const workers = Array(workerCount).fill(0);
  const samples = [];
  let delayed = 0, totalWait = 0, finishedAt = 0;
  let priorArrival = -Infinity;
  for (let index = 0; index < jobs.length; index++) {
    const job = jobs[index];
    if (!job || !Number.isFinite(job.arrival) || job.arrival < priorArrival || !Number.isFinite(job.duration) || job.duration < 0) throw new Error('jobs must have ordered arrivals and finite nonnegative durations');
    priorArrival = job.arrival;
    let selected = 0;
    for (let i = 1; i < workerCount; i++) if (workers[i] < workers[selected]) selected = i;
    const started = Math.max(job.arrival, workers[selected]);
    const completed = started + job.duration;
    const wait = started - job.arrival;
    if (wait > 0) delayed++;
    totalWait += wait;
    finishedAt = Math.max(finishedAt, completed);
    workers[selected] = completed;
    if (samples.length < MAX_PACKET_SAMPLES) samples.push({ index, worker: selected, arrival: job.arrival, started, completed, wait });
  }
  return { mode:'synthetic', jobs:jobs.length, workerCount, delayed, averageWait:jobs.length?totalWait/jobs.length:0, finishedAt, samples };
}

export function runSyntheticScenario(scenario) {
  if (scenario.mode !== 'synthetic') throw new Error('only declared synthetic scenarios can be evaluated');
  const rules = Array.isArray(scenario.rules) ? scenario.rules : [];
  const initial = scenario.inputs || {};
  const state = scenario.initial_state || {};
  const outputs = {};
  let payload = copy(initial.payload || {});
  for (const rule of rules) {
    if (rule.type === 'token_bucket') {
      outputs.tokenBucket = runTokenBucket({ count: initial.event_count, arrivalRatePerSecond: initial.arrival_rate_per_second, capacity: rule.capacity, refillPerSecond: rule.refill_per_second, initialTokens: state.tokens ?? rule.capacity });
    } else if (rule.type === 'transform') {
      payload = transformPayload(payload, rule.operations);
      outputs.payload = redactPayload(payload);
    } else if (rule.type === 'select_candidate') {
      outputs.selected = redactPayload(selectCandidate(initial.candidates, rule.strategy));
    } else if (rule.type === 'fifo_queue') {
      outputs.queue = simulateQueue(initial.operations, rule.capacity);
    } else if (rule.type === 'partitioned_log') {
      outputs.stream = simulatePartitionedLog(initial.events, rule.partitions);
    } else if (rule.type === 'cache_ttl') {
      outputs.cache = simulateCache(initial.operations);
    } else if (rule.type === 'worker_pool') {
      outputs.workers = simulateWorkerPool(initial.jobs, rule.workers);
    } else throw new Error(`unknown rule type ${rule.type}`);
  }
  return { mode: 'synthetic', outputs, assumptions: scenario.assumptions || [], provenance: scenario.provenance || 'model-only' };
}

export function changesBetween(before, after) {
  const first = redactPayload(before || {});
  const second = redactPayload(after || {});
  const changed = [];
  for (const key of new Set([...Object.keys(first), ...Object.keys(second)])) {
    if (JSON.stringify(first[key]) !== JSON.stringify(second[key])) changed.push({ field: key, before: first[key] ?? null, after: second[key] ?? null });
  }
  return changed;
}
