// Tiny deterministic motion-graphics engine: everything is a pure function of time t.
const W = 1920, H = 1080, CX = W / 2, CY = H / 2;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, u) => a + (b - a) * u;
const mix = (a, b, u) => a.map((v, i) => lerp(v, b[i], u));
const TAU = Math.PI * 2;

// Apple-ish easing family
const ease = {
  io: u => u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2,
  out: u => 1 - Math.pow(1 - u, 3),
  in: u => u * u * u,
  expo: u => u === 1 ? 1 : 1 - Math.pow(2, -10 * u),
  expoIn: u => u === 0 ? 0 : Math.pow(2, 10 * u - 10),
  quint: u => u < 0.5 ? 16 * u ** 5 : 1 - Math.pow(-2 * u + 2, 5) / 2,
  back: u => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(u - 1, 3) + c1 * Math.pow(u - 1, 2); },
  spring: u => 1 - Math.cos(u * Math.PI * 4.5) * Math.exp(-u * 6),
};
// keyed interpolation: k = [[t, v], ...] with easing per segment (default io)
function key(t, k, e = ease.io) {
  if (t <= k[0][0]) return k[0][1];
  for (let i = 0; i < k.length - 1; i++) {
    const [t0, v0] = k[i], [t1, v1] = k[i + 1];
    if (t <= t1) {
      const u = (k[i + 1][2] || e)((t - t0) / (t1 - t0));
      return Array.isArray(v0) ? mix(v0, v1, u) : lerp(v0, v1, u);
    }
  }
  return k[k.length - 1][1];
}
const rgb = c => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
const rgba = (c, a) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];

function bg() {
  const g = ctx.createRadialGradient(CX, CY, 0, CX, CY, 1150);
  g.addColorStop(0, '#ecebee'); g.addColorStop(0.45, '#e2e1e4'); g.addColorStop(1, '#cfced2');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

function save(fn) { ctx.save(); fn(); ctx.restore(); }
function at(x, y, rot, s, fn) { ctx.save(); ctx.translate(x, y); if (rot) ctx.rotate(rot); if (s !== undefined && s !== 1) ctx.scale(s, s); fn(); ctx.restore(); }

function circle(x, y, r, fill, stroke, lw) {
  if (r <= 0) return;
  ctx.beginPath(); ctx.arc(x, y, r, 0, TAU);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw || 2; ctx.stroke(); }
}
function rrect(x, y, w, h, r, fill, stroke, lw) {
  r = Math.min(r, w / 2, h / 2);
  ctx.beginPath(); ctx.roundRect(x - w / 2, y - h / 2, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw || 2; ctx.stroke(); }
}
function line(x0, y0, x1, y1, col, lw, cap = 'round') {
  ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1);
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = cap; ctx.stroke();
}
// stroke a sampled polyline [[x,y],...] from fraction a to b (trim-path animation)
function trimmed(pts, a, b, col, lw) {
  if (b <= a || pts.length < 2) return;
  const L = [0];
  for (let i = 1; i < pts.length; i++) L.push(L[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  const tot = L[L.length - 1], A = a * tot, B = b * tot;
  ctx.beginPath(); let started = false;
  for (let i = 1; i < pts.length; i++) {
    const l0 = L[i - 1], l1 = L[i];
    if (l1 < A || l0 > B) continue;
    const u0 = clamp((A - l0) / (l1 - l0 || 1)), u1 = clamp((B - l0) / (l1 - l0 || 1));
    const p0 = [lerp(pts[i - 1][0], pts[i][0], u0), lerp(pts[i - 1][1], pts[i][1], u0)];
    const p1 = [lerp(pts[i - 1][0], pts[i][0], u1), lerp(pts[i - 1][1], pts[i][1], u1)];
    if (!started) { ctx.moveTo(p0[0], p0[1]); started = true; }
    ctx.lineTo(p1[0], p1[1]);
  }
  ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
}
function arcPts(cx, cy, rx, ry, a0, a1, n = 64) {
  const p = [];
  for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); }
  return p;
}
function bezierPts(P, n = 200) {   // Catmull-Rom through control points
  const out = [];
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(0, i - 1)], p1 = P[i], p2 = P[i + 1], p3 = P[Math.min(P.length - 1, i + 2)];
    const m = Math.ceil(n / (P.length - 1));
    for (let j = 0; j < m; j++) {
      const t = j / m, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(k => 0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
    }
  }
  out.push(P[P.length - 1]);
  return out;
}
function softShadow(blur = 30, y = 14, a = 0.12) { ctx.shadowColor = `rgba(0,0,0,${a})`; ctx.shadowBlur = blur; ctx.shadowOffsetY = y; }
function noShadow() { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; ctx.shadowOffsetY = 0; }
function text(s, x, y, size, col, weight = 500, track = 0, align = 'center') {
  ctx.font = `${weight} ${size}px "SF Pro Display", -apple-system, "Helvetica Neue", sans-serif`;
  ctx.fillStyle = col; ctx.textAlign = align; ctx.textBaseline = 'middle';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${track}px`;
  ctx.fillText(s, x, y);
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
}

const SCENES = [];
function scene(a, b, fn) { SCENES.push({ a, b, fn }); }
let MAP = t => t;          // output time -> scene time
window.FPS = 60;
window.DURATION = 10;
window.seek = (T) => {
  const t = MAP(T);
  ctx.setTransform(1, 0, 0, 1, 0, 0); noShadow();
  bg();
  for (const s of SCENES) if (t >= s.a && t < s.b) { ctx.save(); s.fn(t); ctx.restore(); }
  if (window.POST) window.POST(T, t);
};
