// 0–4s  Cold open: DESIGN / MEETS / CODE / i
import { C, W, H, el, css, prog, seg, E, spring, maskLetters, lerp, clamp } from './core.js';

const FIG = '#0D99FF';
const S = { t0: 0, t1: 4 };
let A, B, Bt, box, handles, pill, cursor, Cw, Cchars, Cline, Cok, D, stem, dot, Dcap, labA, labB, labC;
let w62 = 0, w125 = 0, bLeft = 0;

S.init = (ctx) => {
  const r = S.root;
  // A — DESIGN
  A = el('div', { cls: 'abs', style: { inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' } }, r);
  const aw = el('div', { cls: 'disp', style: { fontSize: '330px', color: C.ink } }, A);
  A.letters = maskLetters(aw, 'DESIGN');
  A.word = aw;
  labA = el('div', { cls: 'mono abs', style: { left: '50%', top: '330px', transform: 'translateX(-50%)', color: C.ink, fontSize: '14px' }, text: '[ 01 ]  INTENT' }, A);

  // B — MEETS with Figma selection
  B = el('div', { cls: 'abs', style: { inset: 0 } }, r);
  Bt = el('div', { cls: 'disp abs', style: { fontSize: '330px', color: C.orange, top: '392px' }, text: 'MEETS' }, B);
  box = el('div', { cls: 'abs', style: { border: `2px solid ${FIG}` } }, B);
  handles = [...Array(8)].map(() => el('div', { cls: 'abs', style: { width: '14px', height: '14px', background: '#fff', border: `2px solid ${FIG}`, marginLeft: '-7px', marginTop: '-7px' } }, B));
  pill = el('div', { cls: 'mono abs', style: { background: FIG, color: '#fff', padding: '5px 9px', borderRadius: '4px', fontSize: '15px', letterSpacing: '0.02em' } }, B);
  labB = el('div', { cls: 'mono abs', style: { color: FIG, fontSize: '14px' }, text: 'Frame 02 — Type / Display' }, B);
  cursor = el('div', { cls: 'abs', html: `<svg width="36" height="36" viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.6 14.6 L11.6 21.4 L14.4 20.2 L11.4 13.5 L18 13.5 Z" fill="#fff" stroke="#000" stroke-width="1.4" stroke-linejoin="round"/></svg>` }, B);

  // C — CODE typed, then compiled into display type
  Cw = el('div', { cls: 'abs', style: { inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' } }, r);
  const cRow = el('div', { style: { display: 'flex', alignItems: 'baseline', color: C.paper, height: '300px' } }, Cw);
  Cchars = [...'CODE'].map(ch => {
    const wrap = el('span', { style: { position: 'relative', display: 'inline-block' } }, cRow);
    const m = el('span', { text: ch, style: { fontFamily: 'Mono', fontWeight: 700, fontSize: '300px', lineHeight: '300px', display: 'inline-block' } }, wrap);
    const d = el('span', { cls: 'disp', text: ch, style: { fontSize: '330px', lineHeight: '300px', display: 'none' } }, wrap);
    return { wrap, m, d };
  });
  Cw.caret = el('span', { style: { display: 'inline-block', width: '26px', height: '250px', background: C.lime, marginLeft: '18px', transform: 'translateY(30px)' } }, cRow);
  Cline = el('div', { cls: 'mono abs', style: { left: '50%', top: '300px', transform: 'translateX(-50%)', color: C.paper, fontSize: '16px', textTransform: 'none', opacity: .8 } }, Cw);
  Cok = el('div', { cls: 'mono abs', style: { left: '50%', top: '760px', transform: 'translateX(-50%)', color: C.lime, fontSize: '16px' }, text: '✓ BUILD 200 — 16ms' }, Cw);

  // D — the dot of the i
  D = el('div', { cls: 'abs', style: { inset: 0 } }, r);
  stem = el('div', { cls: 'abs', style: { left: '905px', top: '470px', width: '110px', height: '340px', background: C.ink, borderRadius: '6px' } }, D);
  dot = el('div', { cls: 'abs', style: { width: '130px', height: '130px', borderRadius: '50%', background: C.orange, left: 0, top: 0 } }, D);
  Dcap = el('div', { cls: 'mono abs', style: { left: '1060px', top: '790px', color: C.ink, fontSize: '14px' }, text: 'i — INTERACTION / 120BPM' }, D);
};

S.afterFonts = () => {
  S.root.style.display = 'block'; B.style.display = 'block';
  Bt.style.fontStretch = '62%'; w62 = Bt.getBoundingClientRect().width;
  Bt.style.fontStretch = '125%'; w125 = Bt.getBoundingClientRect().width;
  bLeft = (W - w125) / 2;
  S.root.style.display = 'none';
};

S.render = (lt, t, ctx) => {
  const ph = Math.min(3, Math.floor(lt));
  const p = lt - ph;
  A.style.display = ph === 0 ? 'flex' : 'none';
  B.style.display = ph === 1 ? 'block' : 'none';
  Cw.style.display = ph === 2 ? 'flex' : 'none';
  D.style.display = ph === 3 ? 'block' : 'none';
  ctx.hud.chapter = '00 — INTRO';

  if (ph === 0) {
    ctx.setBg(C.orange); ctx.hud.tone = 'dark';
    A.letters.forEach((l, i) => {
      const e = seg(p, 0.02 + i * 0.035, 0.52 + i * 0.035, E.outExpo);
      l.style.transform = `translateY(${(1 - e) * 105}%)`;
    });
    A.word.style.letterSpacing = lerp(0.03, -0.025, E.outCubic(p)) + 'em';
    A.word.style.transform = `scale(${lerp(0.97, 1.02, E.outCubic(p))})`;
    labA.style.opacity = p > 0.3 ? 1 : 0;
  }

  if (ph === 1) {
    ctx.setBg(C.ink); ctx.hud.tone = 'light';
    const drag = E.inOutCubic(prog(p, 0.24, 0.72));
    const wd = lerp(62, 125, drag);
    Bt.style.fontStretch = wd + '%';
    Bt.style.left = bLeft + 'px';
    const r = Bt.getBoundingClientRect();
    const x0 = r.left - 10, y0 = 392 + 24, x1 = r.right + 10, y1 = 392 + 300;
    css(box, { left: x0 + 'px', top: y0 + 'px', width: (x1 - x0) + 'px', height: (y1 - y0) + 'px' });
    const hp = [[x0, y0], [(x0 + x1) / 2, y0], [x1, y0], [x1, (y0 + y1) / 2], [x1, y1], [(x0 + x1) / 2, y1], [x0, y1], [x0, (y0 + y1) / 2]];
    handles.forEach((h, i) => { h.style.left = hp[i][0] + 'px'; h.style.top = hp[i][1] + 'px'; h.style.background = (i === 3 && p > 0.22 && p < 0.76) ? FIG : '#fff'; });
    pill.textContent = `${Math.round(x1 - x0)} × ${Math.round(y1 - y0)}`;
    css(pill, { left: ((x0 + x1) / 2 - 50) + 'px', top: (y1 + 16) + 'px' });
    css(labB, { left: x0 + 'px', top: (y0 - 30) + 'px' });
    const vis = p > 0.04;
    [box, pill, labB, ...handles].forEach(e => e.style.opacity = vis ? 1 : 0);
    // cursor path: approach handle, drag, leave
    const hx = hp[3][0], hy = hp[3][1];
    let cx, cy;
    if (p < 0.24) { const e = E.outCubic(prog(p, 0, 0.22)); cx = lerp(1700, hx, e); cy = lerp(980, hy, e); }
    else if (p < 0.78) { cx = hx; cy = hy; }
    else { const e = E.inCubic(prog(p, 0.78, 1)); cx = lerp(hx, hx + 260, e); cy = lerp(hy, hy + 300, e); }
    const press = p > 0.22 && p < 0.76 ? 0.88 : 1;
    cursor.style.transform = `translate(${cx - 6}px,${cy - 4}px) scale(${press})`;
  }

  if (ph === 2) {
    ctx.setBg(C.blue); ctx.hud.tone = 'light';
    const typed = [0.04, 0.11, 0.18, 0.25];
    const swap = i => 0.5 + i * 0.055;
    Cchars.forEach((c, i) => {
      c.wrap.style.display = p >= typed[i] ? 'inline-block' : 'none';
      const sw = p >= swap(i);
      c.m.style.display = sw ? 'none' : 'inline-block';
      c.d.style.display = sw ? 'inline-block' : 'none';
      const k = sw ? spring(p - swap(i), 4, 0.35) : 1;
      c.wrap.style.transform = sw ? `translateY(${(1 - k) * -60}px) scaleY(${0.6 + 0.4 * k})` : 'none';
    });
    const nTyped = typed.filter(x => p >= x).length;
    Cline.textContent = p < 0.5 ? `> type("${'CODE'.slice(0, nTyped)}")` : '> compile --font Archivo/Black/Expanded';
    Cw.caret.style.opacity = (p < 0.5 ? Math.floor(p * 12) % 2 === 0 || p < 0.3 : p < 0.72 && Math.floor(p * 16) % 2 === 0) ? 1 : 0;
    Cok.style.opacity = p > 0.78 ? 1 : 0;
  }

  if (ph === 3) {
    ctx.setBg(C.paper); ctx.hud.tone = 'dark';
    // dot drop with two bounces, squash on contact
    const restY = 470 - 30 - 130; // top of dot at rest
    const T1 = 0.2, T2 = 0.34, T3 = 0.44;
    let y, sx = 1, sy = 1;
    if (p < T1) { const e = (p / T1) ** 2; y = lerp(-180, restY, e); sy = 1 + 0.25 * e; sx = 1 - 0.12 * e; }
    else if (p < T2) { const q = (p - T1) / (T2 - T1); y = restY - 140 * 4 * q * (1 - q); }
    else if (p < T3) { const q = (p - T2) / (T3 - T2); y = restY - 46 * 4 * q * (1 - q); }
    else y = restY;
    const contact = [T1, T2, T3].map(c => Math.max(0, 1 - Math.abs(p - c) / 0.03)).reduce((a, b) => Math.max(a, b));
    if (contact > 0) { sx = 1 + 0.32 * contact; sy = 1 - 0.28 * contact; }
    const grow = E.inExpo(prog(p, 0.62, 1));
    const sc = 1 + grow * 30;
    const cy = y + 65 + (sy < 1 ? (1 - sy) * 65 : 0);
    dot.style.transform = `translate(${960 - 65}px,${cy - 65}px) scale(${sx * sc},${sy * sc})`;
    stem.style.transform = `translateY(${(1 - E.outExpo(prog(p, 0, 0.25))) * 400}px)`;
    Dcap.style.opacity = p > 0.15 && p < 0.7 ? 1 : 0;
    if (grow > 0.5) ctx.hud.tone = 'dark';
  }
};
export default S;
