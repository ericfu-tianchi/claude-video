// 34–38s  Beat-cut values: BOLD. PRECISE. PLAYFUL. HUMAN. -> NOT JUST COLD CODE. -> BUT JOY.
import { C, W, H, el, prog, seg, E, lerp, clamp, spring, maskLetters, hash, rng } from './core.js';

const S = { t0: 34, t1: 38 };
let bold, echoes = [], prec, guides = [], precLab, play, playL, human, humanL, cold, strike, joy, joyL;
const center = (parent, extra = {}) => el('div', { cls: 'abs', style: { inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', ...extra } }, parent);

S.init = () => {
  const r = S.root;
  bold = center(r);
  for (let i = -3; i <= 3; i++) {
    const e = el('div', { cls: 'disp abs', text: 'BOLD.', style: { fontSize: '300px', color: i === 0 ? C.paper : 'transparent', WebkitTextStroke: i === 0 ? '0' : `2px ${C.paper}` } }, bold);
    e.k = i; echoes.push(e);
  }
  prec = center(r);
  const pw = el('div', { cls: 'disp', text: 'PRECISE.', style: { fontSize: '250px', color: C.ink, position: 'relative' } }, prec);
  for (const [y, lab] of [[22, 'CAP 0.72'], [212, 'BASELINE'], [100, 'X-HEIGHT 0.53']]) {
    const g = el('div', { cls: 'abs', style: { left: '-200px', right: '-200px', top: y + 'px', height: '1px', background: C.blue, transformOrigin: 'left' } }, pw);
    el('div', { cls: 'mono abs', text: lab, style: { right: '0', top: '-20px', color: C.blue, fontSize: '12px' } }, g);
    guides.push(g);
  }
  precLab = el('div', { cls: 'mono abs', style: { left: '50%', top: '760px', transform: 'translateX(-50%)', color: C.blue, fontSize: '14px' }, text: '← 8PX GRID · OPTICAL KERNING −20 →' }, prec);
  play = center(r);
  const plw = el('div', { cls: 'disp', style: { fontSize: '280px', color: C.ink } }, play);
  playL = [...'PLAYFUL.'].map(ch => el('span', { text: ch, style: { display: 'inline-block' } }, plw));
  human = center(r);
  const hw = el('div', { cls: 'disp', style: { fontSize: '300px', color: C.paper } }, human);
  humanL = [...'HUMAN.'].map(ch => el('span', { text: ch, style: { display: 'inline-block' } }, hw));
  cold = center(r, { flexDirection: 'column' });
  const cw = el('div', { style: { position: 'relative', fontFamily: 'Mono', fontWeight: 500, fontSize: '96px', color: '#77777A', whiteSpace: 'nowrap' }, text: 'NOT JUST COLD CODE.' }, cold);
  strike = el('div', { cls: 'abs', style: { left: '-20px', right: '-20px', top: '52%', height: '12px', background: C.orange, transformOrigin: 'left' } }, cw);
  cold.note = el('div', { cls: 'mono', style: { color: C.paper, opacity: .5, marginTop: '40px', fontSize: '14px' }, text: '// tech isn’t just cold math and code —' }, cold);
  joy = center(r);
  const jw = el('div', { cls: 'disp', style: { fontSize: '300px', color: C.orange } }, joy);
  joyL = [...'BUT JOY.'].map(ch => el('span', { text: ch === ' ' ? ' ' : ch, style: { display: 'inline-block' } }, jw));
};

function burst(g, p, cx, cy) {
  const R = rng(9);
  const cols = [C.lime, C.blue, C.paper, C.ink];
  for (let i = 0; i < 90; i++) {
    const a = R() * Math.PI * 2, sp = 300 + R() * 900, kind = Math.floor(R() * 3), s = 8 + R() * 18, rot = R() * 6;
    const e = E.outExpo(clamp(p * 1.4));
    const x = cx + Math.cos(a) * sp * e, y = cy + Math.sin(a) * sp * e + p * p * 260;
    const al = 1 - clamp((p - 0.5) / 0.5);
    if (al <= 0) continue;
    g.globalAlpha = al; g.fillStyle = cols[i % 4];
    g.save(); g.translate(x, y); g.rotate(rot + p * 4);
    g.beginPath();
    if (kind === 0) g.arc(0, 0, s / 2, 0, 7);
    else if (kind === 1) { g.rect(-s / 2, -s / 7, s, s / 3.5); g.rect(-s / 7, -s / 2, s / 3.5, s); }
    else { g.moveTo(0, -s / 2); g.lineTo(s / 2, 0); g.lineTo(0, s / 2); g.lineTo(-s / 2, 0); }
    g.fill(); g.restore();
  }
  g.globalAlpha = 1;
}

S.render = (lt, t, ctx) => {
  ctx.hud.chapter = '07 — PRINCIPLES';
  const ph = lt < 2 ? Math.floor(lt / 0.5) : lt < 3 ? 4 : 5;
  const p = ph < 4 ? (lt % 0.5) / 0.5 : ph === 4 ? lt - 2 : lt - 3;
  [bold, prec, play, human, cold, joy].forEach((e, i) => e.style.display = i === ph ? 'flex' : 'none');
  const bgs = [C.ink, C.paper, C.orange, C.blue, C.ink, C.ink];
  ctx.setBg(bgs[ph]); ctx.hud.tone = bgs[ph] === C.paper || bgs[ph] === C.orange ? 'dark' : 'light';
  if (ph === 0) echoes.forEach(e => { const s = E.outExpo(p); e.style.transform = `translateY(${e.k * 175 * s}px)`; e.style.opacity = e.k === 0 ? 1 : (1 - Math.abs(e.k) * 0.22) * s; });
  if (ph === 1) { guides.forEach((g, i) => g.style.transform = `scaleX(${seg(p, i * 0.08, 0.5 + i * 0.08, E.outExpo)})`); precLab.style.opacity = p > 0.35 ? 1 : 0; prec.firstChild.style.letterSpacing = lerp(0.06, -0.02, E.outExpo(p)) + 'em'; }
  if (ph === 2) playL.forEach((l, i) => { const s = spring(p * 0.5 - i * 0.025, 3.2, 0.25); l.style.transform = `translateY(${(1 - s) * -260}px) rotate(${(1 - s) * (i % 2 ? 24 : -24)}deg)`; });
  if (ph === 3) humanL.forEach((l, i) => { const e = E.outExpo(p); l.style.transform = `translateX(${(i - 2.5) * 140 * (1 - e)}px)`; l.style.opacity = clamp(p * 4); });
  if (ph === 4) { strike.style.transform = `scaleX(${seg(p, 0.45, 0.75, E.inOutExpo)})`; cold.style.opacity = 1; cold.note.style.opacity = p > 0.1 ? .5 : 0; }
  if (ph === 5) {
    joyL.forEach((l, i) => { const s = spring(p - i * 0.03, 2.6, 0.3); l.style.transform = `scale(${clamp(s, 0, 2)})`; });
    const g = ctx.c2d; ctx.c2dUsed = true; g.clearRect(0, 0, W, H);
    burst(g, prog(p, 0.12, 1), 960, 540);
  }
};
export default S;
