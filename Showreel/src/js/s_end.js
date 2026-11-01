// 38–43s  End card
import { C, W, H, el, prog, seg, E, lerp, clamp, maskLetters, spring } from './core.js';

const S = { t0: 38, t1: 43 };
let name, letters, dot, rule, cols = [], foot, kick;
const INFO = [['Portfolio', 'tianchi-fu.com'], ['Email', 'tianchi@umich.edu'], ['GitHub', 'github.com/ericfu666'], ['LinkedIn', 'in/tianchi-fu']];

S.init = () => {
  const r = S.root;
  kick = el('div', { cls: 'mono abs', style: { left: '124px', top: '330px', color: C.lime, fontSize: '16px' }, text: 'LET’S MAKE SOMETHING PEOPLE LOVE.' }, r);
  name = el('div', { cls: 'disp abs', style: { left: '120px', top: '372px', fontSize: '196px', color: C.paper } }, r);
  letters = maskLetters(name, 'TIANCHI FU');
  dot = el('span', { style: { display: 'inline-block', width: '0.2em', height: '0.2em', borderRadius: '50%', background: C.orange, marginLeft: '0.04em' } }, name);
  rule = el('div', { cls: 'abs', style: { left: '120px', top: '600px', height: '1px', width: '1680px', background: C.paper, opacity: .35, transformOrigin: 'left' } }, r);
  INFO.forEach(([a, b], i) => {
    const c = el('div', { cls: 'abs', style: { left: 124 + i * 420 + 'px', top: '636px', color: C.paper } }, r);
    el('div', { cls: 'mono', style: { fontSize: '12px', opacity: .5, marginBottom: '10px' }, text: a }, c);
    el('div', { style: { fontFamily: 'Mono', fontSize: '22px' }, text: b }, c);
    cols.push(c);
  });
  foot = el('div', { cls: 'mono abs', style: { left: '124px', top: '900px', color: C.paper, opacity: .5, fontSize: '13px' }, text: 'DESIGNED, ANIMATED & RENDERED IN CODE — THANKS FOR WATCHING' }, r);
};

S.render = (lt, t, ctx) => {
  ctx.setBg(C.ink); ctx.hud.tone = 'light'; ctx.hud.chapter = '08 — CONTACT';
  letters.forEach((l, i) => { const e = seg(lt, 0.05 + i * 0.03, 0.6 + i * 0.03, E.outExpo); l.style.transform = `translateY(${(1 - e) * 110}%)`; });
  const d = spring(lt - 0.45, 2.5, 0.3);
  dot.style.transform = `scale(${clamp(d, 0, 2)})`;
  kick.style.opacity = lt > 0.3 ? 1 : 0;
  rule.style.transform = `scaleX(${seg(lt, 0.3, 1.0, E.inOutExpo)})`;
  cols.forEach((c, i) => { const e = seg(lt, 0.55 + i * 0.08, 1.1 + i * 0.08, E.outExpo); c.style.opacity = e; c.style.transform = `translateY(${(1 - e) * 20}px)`; });
  foot.style.opacity = lt > 1.2 ? .5 : 0;
  // breathing dot, then fade to black
  if (lt > 1.2) dot.style.transform = `scale(${1 + 0.08 * Math.sin((lt - 1.2) * Math.PI * 2)})`;
  const out = seg(lt, 4.2, 4.95, E.inOutCubic);
  S.root.style.opacity = 1 - out;
  ctx.hud.show = 1 - out;
};
export default S;
