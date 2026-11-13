import { clamp } from './motion.js';

function hash(text) {
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 16777619);
  return h >>> 0;
}

export function layoutGraph(nodes, edges, options = {}) {
  const maxNodes = options.maxNodes ?? 96;
  if (nodes.length > maxNodes) throw new Error(`view has ${nodes.length} nodes; maximum ${maxNodes}. Navigate to a smaller scope.`);
  const count = nodes.length;
  if (!count) return new Map();
  const radius = (n) => ['storage','gateway','service','broker','stream'].includes(n.role) ? 1.75 : 1.55;
  const ranks = new Map(nodes.map(n => [n.id, 0]));
  for (let k = 0; k < Math.min(5, count); k++) {
    for (const e of edges) {
      if (!ranks.has(e.from) || !ranks.has(e.to) || e.to === e.from) continue;
      const candidate = Math.min(5, ranks.get(e.from) + 1);
      if (candidate > ranks.get(e.to) && e.direction !== 'bidirectional') ranks.set(e.to, candidate);
    }
  }
  const maxRank = Math.max(...ranks.values(), 0);
  const byRank = new Map();
  for (const n of nodes) {
    const r = ranks.get(n.id);
    if (!byRank.has(r)) byRank.set(r, []);
    byRank.get(r).push(n.id);
  }
  const positions = new Map();
  const velocities = new Map();
  for (const n of nodes) {
    const peers = byRank.get(ranks.get(n.id)).sort();
    const index = peers.indexOf(n.id);
    const jitter = ((hash(n.id) % 1000) / 1000 - 0.5) * 0.22;
    positions.set(n.id, { x: (ranks.get(n.id) - maxRank / 2) * 6.2 + jitter, z: (index - (peers.length - 1) / 2) * 5.2 + jitter });
    velocities.set(n.id, { x: 0, z: 0 });
  }
  const springs = edges.filter(e => positions.has(e.from) && positions.has(e.to) && e.from !== e.to);
  const iterations = options.iterations ?? 240;
  for (let step = 0; step < iterations; step++) {
    const forces = new Map(nodes.map(n => [n.id, { x: 0, z: 0 }]));
    for (let i = 0; i < count; i++) {
      for (let j = i + 1; j < count; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const pa = positions.get(a.id);
        const pb = positions.get(b.id);
        let dx = pb.x - pa.x;
        let dz = pb.z - pa.z;
        const distSq = dx * dx + dz * dz + 0.01;
        const dist = Math.sqrt(distSq);
        if (dist < 1e-6) { dx = 0.01; dz = 0.01; }
        const repel = 13.5 / distSq + Math.max(0, radius(a) + radius(b) + 0.55 - dist) * 3.7;
        const fx = dx / dist * repel;
        const fz = dz / dist * repel;
        forces.get(a.id).x -= fx;
        forces.get(a.id).z -= fz;
        forces.get(b.id).x += fx;
        forces.get(b.id).z += fz;
      }
    }
    for (const e of springs) {
      const pa = positions.get(e.from);
      const pb = positions.get(e.to);
      const dx = pb.x - pa.x;
      const dz = pb.z - pa.z;
      const distance = Math.sqrt(dx * dx + dz * dz) + 1e-6;
      const f = clamp((distance - 6.4) * 0.055, -0.35, 0.35);
      forces.get(e.from).x += dx / distance * f;
      forces.get(e.from).z += dz / distance * f;
      forces.get(e.to).x -= dx / distance * f;
      forces.get(e.to).z -= dz / distance * f;
    }
    for (const n of nodes) {
      const p = positions.get(n.id);
      const f = forces.get(n.id);
      const v = velocities.get(n.id);
      f.x += (ranks.get(n.id) - maxRank / 2) * 0.075 - p.x * 0.017;
      f.z -= p.z * 0.022;
      v.x = clamp((v.x + f.x * 0.035) * 0.85, -0.42, 0.42);
      v.z = clamp((v.z + f.z * 0.035) * 0.85, -0.42, 0.42);
      p.x += v.x;
      p.z += v.z;
      if (!Number.isFinite(p.x) || !Number.isFinite(p.z)) throw new Error('layout became nonfinite');
    }
  }
  for (let k = 0; k < 20; k++) {
    for (let i = 0; i < count; i++) {
      for (let j = i + 1; j < count; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const pa = positions.get(a.id);
        const pb = positions.get(b.id);
        let dx = pb.x - pa.x;
        let dz = pb.z - pa.z;
        let d = Math.hypot(dx, dz);
        if (d < 1e-8) { dx = 1; dz = 0; d = 1; }
        const overlap = radius(a) + radius(b) + 0.3 - d;
        if (overlap > 0) {
          const move = overlap / (2 * d) + 1e-5;
          pa.x -= dx * move;
          pa.z -= dz * move;
          pb.x += dx * move;
          pb.z += dz * move;
        }
      }
    }
  }
  const minX = Math.min(...[...positions.values()].map(p => p.x));
  const maxX = Math.max(...[...positions.values()].map(p => p.x));
  const minZ = Math.min(...[...positions.values()].map(p => p.z));
  const maxZ = Math.max(...[...positions.values()].map(p => p.z));
  const cx = (minX + maxX) / 2;
  const cz = (minZ + maxZ) / 2;
  return new Map([...positions].map(([id, p]) => [id, [p.x - cx, 0, p.z - cz]]));
}
