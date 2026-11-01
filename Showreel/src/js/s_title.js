// 20–22s  Name card. The collapsed particle becomes the period of "FU."
import { C, W, H, el, prog, seg, E, lerp, clamp, maskLetters, spring } from './core.js';

const S = { t0: 20, t1: 22 };
let name, letters, spacer, dot, hi, sub, sub2, rule, wipe, bar;
const SUB = 'PRODUCT DESIGNER — ENGINEER — MOTION';
const SUB2 = 'COMPUTER ENGINEERING → UX → PRODUCT  /  2021—2026';
let target = [0, 0];

S.init = () => {
  const r = S.root;
  name = el('div', { cls: 'disp abs', style: { left: '120px', top: '400px', fontSize: '196px', color: C.paper } }, r);
  letters = maskLetters(name, 'TIANCHI FU');
  spacer = el('span', { style: { display: 'inline-block', width: '0.24em', height: '10px' } }, name);
  hi = el('div', { cls: 'mono abs', style: { left: '124px', top: '360px', color: C.lime, fontSize: '16px' }, text: "HI, I'M" }, r);
  rule = el('div', { cls: 'abs', style: { left: '120px', top: '600px', height: '1px', width: '1680px', background: C.paper, transformOrigin: 'left', opacity: .4 } }, r);
  sub = el('div', { cls: 'mono abs', style: { left: '124px', top: '628px', color: C.paper, fontSize: '18px' } }, r);
  sub2 = el('div', { cls: 'mono abs', style: { left: '124px', top: '660px', color: C.paper, fontSize: '14px', opacity: .55 } }, r);
  dot = el('div', { cls: 'abs', style: { left: 0, top: 0, width: '36px', height: '36px', borderRadius: '50%', background: C.orange } }, r);
  wipe = el('div', { cls: 'abs', style: { left: 0, top: 0, width: W + 'px', height: H + 'px', background: C.lime } }, r);
  bar = el('div', { cls: 'abs', style: { left: '-20px', top: 0, width: '20px', height: H + 'px', background: C.orange } }, wipe);
};
S.afterFonts = () => {
  S.root.style.display = 'block';
  const rr = spacer.getBoundingClientRect(), nr = name.getBoundingClientRect();
  target = [rr.left + rr.width * 0.55, nr.top + nr.height * 0.80];
  S.root.style.display = 'none';
};

S.render = (lt, t, ctx) => {
  ctx.setBg(C.ink); ctx.hud.tone = 'light'; ctx.hud.chapter = '05 — HELLO';
  letters.forEach((l, i) => { const e = seg(lt, 0.1 + i * 0.03, 0.6 + i * 0.03, E.outExpo); l.style.transform = `translateY(${(1 - e) * 110}%)`; });
  // dot travels on an arc from screen center to the period slot, with a squash on landing
  const m = seg(lt, 0, 0.42, E.inOutCubic);
  const x = lerp(960, target[0], m), y = lerp(540, target[1], m) - Math.sin(m * Math.PI) * 220;
  const land = lt > 0.42 ? spring(lt - 0.42, 3.5, 0.28) : 0;
  const sq = lt > 0.42 ? 1 + (1 - land) * 0.35 : 1;
  const ds = lerp(1, 1.25, m);
  dot.style.transform = `translate(${x - 18}px,${y - 18}px) scale(${ds * sq},${ds / sq})`;
  hi.style.opacity = lt > 0.25 ? 1 : 0;
  rule.style.transform = `scaleX(${seg(lt, 0.3, 0.9, E.inOutExpo)})`;
  sub.textContent = SUB.slice(0, Math.floor(clamp((lt - 0.45) / 0.5) * SUB.length));
  sub2.textContent = SUB2.slice(0, Math.floor(clamp((lt - 0.7) / 0.5) * SUB2.length));
  const w = seg(lt, 1.62, 2.0, E.inOutExpo);
  wipe.style.transform = `translateX(${(1 - w) * (W + 40)}px)`;
  if (w > 0.6) ctx.hud.tone = 'dark';
};
export default S;
