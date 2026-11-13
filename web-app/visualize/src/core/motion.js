export const FIXED_STEP = 1 / 60;
export const MAX_FRAME_DELTA = 0.1;

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

export function add(a, b) { return a.map((n, i) => n + b[i]); }
export function subtract(a, b) { return a.map((n, i) => n - b[i]); }
export function scale(a, factor) { return a.map(n => n * factor); }
export function dot(a, b) { return a.reduce((s, n, i) => s + n * b[i], 0); }
export function magnitude(a) { return Math.sqrt(dot(a, a)); }
export function unit(a) { const m = magnitude(a); return m < 1e-8 ? [0, 1, 0] : scale(a, 1 / m); }
export function distance(a, b) { return magnitude(subtract(a, b)); }
export function lerp(a, b, t) { return add(scale(a, 1 - t), scale(b, t)); }

export function pointOnCurve(start, end, bend, t) {
  const a = lerp(start, bend, t);
  const b = lerp(bend, end, t);
  return lerp(a, b, t);
}

export function arcLengthTable(start, end, bend, samples = 40) {
  if (samples < 2 || samples > 256) throw new Error('arc sample count must be 2..256');
  const entries = [{ t: 0, length: 0 }];
  let prior = start;
  let sum = 0;
  for (let i = 1; i <= samples; i++) {
    const t = i / samples;
    const p = pointOnCurve(start, end, bend, t);
    sum += distance(prior, p);
    entries.push({ t, length: sum });
    prior = p;
  }
  return { entries, length: sum };
}

export function pointAtArcDistance(start, end, bend, table, traveled) {
  const d = clamp(traveled, 0, table.length);
  let low = 0;
  let high = table.entries.length - 1;
  while (low + 1 < high) {
    const mid = (low + high) >> 1;
    if (table.entries[mid].length < d) low = mid;
    else high = mid;
  }
  const a = table.entries[low];
  const b = table.entries[high];
  const f = b.length === a.length ? 0 : (d - a.length) / (b.length - a.length);
  return pointOnCurve(start, end, bend, a.t + (b.t - a.t) * f);
}

export function motionProfile(length, speed = 5, acceleration = 12) {
  if (![length, speed, acceleration].every(Number.isFinite) || length < 0 || speed <= 0 || acceleration <= 0) throw new Error('invalid motion profile parameters');
  const accelTime = Math.min(speed / acceleration, Math.sqrt(length / acceleration));
  const peakSpeed = accelTime * acceleration;
  const accelLength = acceleration * accelTime * accelTime / 2;
  const cruiseTime = peakSpeed ? Math.max(0, (length - 2 * accelLength) / peakSpeed) : 0;
  return { length, acceleration, accelTime, accelLength, peakSpeed, cruiseTime, duration: 2 * accelTime + cruiseTime };
}

export function traveledAt(profile, time) {
  const t = clamp(time, 0, profile.duration);
  if (t <= profile.accelTime) return 0.5 * profile.acceleration * t * t;
  if (t <= profile.accelTime + profile.cruiseTime) return profile.accelLength + profile.peakSpeed * (t - profile.accelTime);
  const remaining = profile.duration - t;
  return profile.length - 0.5 * profile.acceleration * remaining * remaining;
}

export class FixedClock {
  constructor(step = FIXED_STEP) {
    this.step = step;
    this.accumulator = 0;
    this.time = 0;
  }
  advance(delta, tick) {
    if (!Number.isFinite(delta) || delta < 0) return 0;
    this.accumulator += clamp(delta, 0, MAX_FRAME_DELTA);
    let iterations = 0;
    while (this.accumulator + 1e-10 >= this.step && iterations < 8) {
      tick(this.step, this.time + this.step);
      this.time += this.step;
      this.accumulator -= this.step;
      iterations++;
    }
    return iterations;
  }
  reset() { this.time = 0; this.accumulator = 0; }
}
