// 4–8s  Generative grid: dots -> plus -> diamonds/crosses -> squares (top-down of the cube field)
import { C, W, H, el, prog, seg, E, hash2, lerp, clamp } from './core.js';

export const GRID = { cols: 33, rows: 19, sp: 56 };
export const cellColor = (i, j) => { const h = hash2(i * 3.1, j * 7.7); return h < 0.13 ? C.blue : h < 0.19 ? C.orange : C.paper; };

const S = { t0: 4, t1: 8 };
let lab, coord;
S.init = () => {
  lab = el('div', { cls: 'mono abs', style: { left: '50%', top: '44px', transform: 'translateX(-50%)', color: C.paper, opacity: .6 }, text: 'GRID 33 × 19 — 627 NODES — SEED 0x2F3B' }, S.root);
  coord = el('div', { cls: 'mono abs', style: { color: C.ink, background: C.lime, padding: '3px 6px', fontSize: '12px' } }, S.root);
};

function shape(g, kind, x, y, r) {
  g.beginPath();
  if (kind === 0) { g.arc(x, y, r, 0, Math.PI * 2); g.fill(); }
  else if (kind === 1) { const w = r * 0.42; g.rect(x - r, y - w / 2, r * 2, w); g.rect(x - w / 2, y - r, w, r * 2); g.fill(); }
  else if (kind === 2) { g.moveTo(x, y - r * 1.15); g.lineTo(x + r * 1.15, y); g.lineTo(x, y + r * 1.15); g.lineTo(x - r * 1.15, y); g.closePath(); g.fill(); }
  else if (kind === 3) { g.save(); g.translate(x, y); g.rotate(Math.PI / 4); const w = r * 0.42; g.rect(-r, -w / 2, r * 2, w); g.rect(-w / 2, -r, w, r * 2); g.fill(); g.restore(); }
  else { const s = r * 0.95; g.roundRect(x - s, y - s, s * 2, s * 2, Math.min(4, s * 0.2)); g.fill(); }
}

const TARGETS = [[16, 9], [24, 5], [8, 13], [27, 14], [11, 4], [20, 11]];

S.render = (lt, t, ctx) => {
  ctx.setBg(C.ink); ctx.hud.tone = 'light'; ctx.hud.chapter = '01 — SYSTEMS';
  const g = ctx.c2d; ctx.c2dUsed = true;
  g.clearRect(0, 0, W, H);
  const { cols, rows, sp } = GRID;
  const ox = W / 2 - (cols - 1) / 2 * sp, oy = H / 2 - (rows - 1) / 2 * sp;
  const T = [1.0, 1.5, 2.25, 3.0]; // transitions to stage 1..4
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const x = ox + i * sp, y = oy + j * sp;
    const dx = (i - (cols - 1) / 2) / (cols / 2), dy = (j - (rows - 1) / 2) / (cols / 2);
    const d = Math.hypot(dx, dy);
    const h = hash2(i, j);
    const delays = [((i + j) / (cols + rows)) * 0.45, d * 0.4, h * 0.35, (j / rows) * 0.3 + h * 0.08];
    let st = 0, since = 9;
    for (let k = 0; k < 4; k++) { const tk = T[k] + delays[k]; if (lt >= tk) { st = k + 1; since = lt - tk; } }
    // intro: giant orange coverage shrinking to dots
    const intro = seg(lt, 0.02 + d * 0.22, 0.55 + d * 0.22, E.outExpo);
    let r = lerp(44, 7, intro);
    const ripple = Math.sin(d * 13 - lt * 8.5) * clamp((lt - 0.35) * 3) * (1 - prog(lt, 1.4, 2.2));
    r += ripple * 4.5;
    let kind = 0, col = intro < 0.6 ? C.orange : C.paper;
    if (st === 1) { kind = 1; r = 9; const band = ((i - j + lt * 18) % 14 + 14) % 14; if (band < 2.2) col = C.blue; }
    if (st === 2) { kind = h > 0.55 ? 2 : 1; r = kind === 2 ? 8 : 9; if (h > 0.92) { kind = 3; col = C.orange; } else if (h < 0.18) col = C.blue; }
    if (st === 3) { kind = h > 0.45 ? 2 : 3; r = 8; col = cellColor(i, j) === C.paper ? C.paper : cellColor(i, j); if (h > 0.8) kind = 0; }
    if (st === 4) { kind = 4; col = cellColor(i, j); r = lerp(10, 24, E.inOutCubic(prog(lt, 3.3, 3.95))); }
    if (st > 0 && st < 4) { const pop = since < 0.25 ? E.outBack(clamp(since / 0.18)) : 1; r *= clamp(pop, 0, 1.4); }
    if (st === 4 && since < 0.2) r *= E.outBack(clamp(since / 0.16));
    g.fillStyle = col;
    shape(g, kind, x, y, Math.max(0, r));
  }
  // crosshair hopping between nodes on the beat
  const ci = clamp(Math.floor((lt - 0.9) / 0.5), 0, TARGETS.length - 1);
  const show = lt > 0.9 && lt < 3.3;
  coord.style.opacity = show ? 1 : 0;
  if (show) {
    const a = TARGETS[Math.max(0, ci - 1)], b = TARGETS[ci];
    const e = E.outExpo(clamp(((lt - 0.9) % 0.5) / 0.3));
    const fi = ci === 0 ? b[0] : lerp(a[0], b[0], e), fj = ci === 0 ? b[1] : lerp(a[1], b[1], e);
    const x = ox + fi * sp, y = oy + fj * sp;
    g.strokeStyle = 'rgba(236,234,227,.28)'; g.lineWidth = 1;
    g.beginPath(); g.moveTo(0, y + .5); g.lineTo(W, y + .5); g.moveTo(x + .5, 0); g.lineTo(x + .5, H); g.stroke();
    g.strokeStyle = C.lime; g.lineWidth = 2; g.strokeRect(x - 22, y - 22, 44, 44);
    coord.textContent = `[${String(b[0]).padStart(2, '0')}, ${String(b[1]).padStart(2, '0')}]  ${(lt * 1000 | 0)}ms`;
    coord.style.transform = `translate(${x + 28}px,${y + 26}px)`;
  }
  lab.style.opacity = lt < 3.3 ? .6 : 0;
  if (lt > 3.45) ctx.hud.tone = 'dark';
};
export default S;
