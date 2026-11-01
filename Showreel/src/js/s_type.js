// 12–16s  Kinetic type wall: MOTION rows, variable-width breathing, beat-synced palette swaps
import { C, W, H, el, prog, seg, E, lerp, clamp } from './core.js';

const S = { t0: 12, t1: 16 };
const N = 7, RH = H / N, MID = 3;
let rows = [], solo, solo2;
const SCHEMES = [
  { bg: C.blue, fg: C.paper, mbg: C.orange, mfg: C.ink },
  { bg: C.ink, fg: C.paper, mbg: C.lime, mfg: C.ink },
  { bg: C.paper, fg: C.blue, mbg: C.blue, mfg: C.paper },
];
const ORDER = [0, 1, 0, 2, 0, 1, 2, 0];
export const SOLO = { size: 210, text: 'MOTION' };

S.init = () => {
  for (let r = 0; r < N; r++) {
    const row = el('div', { cls: 'abs', style: { left: 0, width: W + 'px', top: r * RH + 'px', height: RH + 1 + 'px', overflow: 'hidden' } }, S.root);
    const strip = el('div', { cls: 'disp abs', style: { left: 0, top: 0, height: RH + 'px', display: 'flex', alignItems: 'center', fontSize: (r === MID ? 150 : 140) + 'px', fontStyle: r % 3 === 1 ? 'italic' : 'normal' } }, row);
    const words = [];
    for (let k = 0; k < 14; k++) {
      words.push(el('span', { text: 'MOTION', style: { display: 'inline-block' } }, strip));
      el('span', { text: '·', style: { display: 'inline-block', margin: '0 0.18em', fontWeight: 400 } }, strip);
    }
    rows.push({ row, strip, words, dir: r % 2 ? 1 : -1, speed: 160 + (r * 53) % 140 });
  }
  solo = el('div', { cls: 'disp abs', style: { left: 0, top: 0, width: W + 'px', height: H + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: SOLO.size + 'px', color: C.paper }, text: SOLO.text }, S.root);
  solo2 = el('div', { cls: 'mono abs', style: { left: '50%', top: '640px', transform: 'translateX(-50%)', color: C.paper, opacity: .6 }, text: 'TYPE — ARCHIVO VARIABLE / WDTH 62→125' }, S.root);
};

S.render = (lt, t, ctx) => {
  ctx.hud.chapter = '03 — TYPOGRAPHY';
  const beat = clamp(Math.floor(lt / 0.5), 0, 7);
  const sc = SCHEMES[ORDER[beat]];
  ctx.setBg(sc.bg);
  ctx.hud.tone = sc.bg === C.paper ? 'dark' : 'light';
  const endPhase = lt > 3.75;
  rows.forEach((R, r) => {
    const isMid = r === MID;
    const enter = seg(lt, Math.abs(r - MID) * 0.03, 0.45 + Math.abs(r - MID) * 0.03, E.outExpo);
    const scroll = R.dir * R.speed * lt + R.dir * (1 - enter) * W * 1.1;
    R.strip.style.transform = `translateX(${-900 + scroll}px)`;
    R.row.style.background = isMid ? sc.mbg : sc.bg;
    R.strip.style.color = isMid ? sc.mfg : sc.fg;
    R.words.forEach((w, k) => {
      const ph = k * 1.3 + r * 0.9;
      const wd = 62 + 63 * (0.5 + 0.5 * Math.sin(ph + lt * 3.2));
      w.style.fontStretch = wd.toFixed(1) + '%';
      w.style.fontWeight = isMid ? 900 : (k + r) % 3 === 0 ? 300 : 900;
    });
    // collapse: outer rows fold away first, then the middle bar shrinks horizontally
    const col = seg(lt, 3.0 + (MID - Math.abs(r - MID)) * 0.05, 3.3 + (MID - Math.abs(r - MID)) * 0.05, E.inOutCubic);
    if (!isMid) { R.row.style.transform = `scaleY(${1 - col})`; R.row.style.transformOrigin = r < MID ? 'top' : 'bottom'; R.row.style.display = endPhase ? 'none' : 'block'; }
    else {
      const shrink = seg(lt, 3.35, 3.75, E.inOutExpo);
      R.row.style.clipPath = `inset(0 ${shrink * 50}% 0 ${shrink * 50}%)`;
      R.row.style.display = endPhase ? 'none' : 'block';
    }
  });
  if (lt > 3.0) ctx.setBg(C.ink), ctx.hud.tone = 'light';
  const so = seg(lt, 3.5, 3.75, E.outCubic);
  solo.style.opacity = so; solo2.style.opacity = so * .6;
  solo.style.letterSpacing = lerp(0.12, -0.02, so) + 'em';
};
export default S;
