// 22–34s  Selected work — six portfolio projects, 2s each, poster layout + a bespoke visual per project
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import { C, W, H, el, css, prog, seg, E, lerp, clamp, spring, hash } from './core.js';

const S = { t0: 22, t1: 34 };
const CARD = 2;
const CARDS = [
  { slug: 'homesoffcampus', name: 'HomesOffCampus', year: '2021', bg: C.lime, fg: C.ink, acc: C.ink, lines: ['FIND HOME.', 'SAFELY.'],
    meta: [['Role', 'UX design, research, dev'], ['Stack', 'Figma · React Native · Firebase'], ['Origin', 'I got scammed. So I fixed it.']] },
  { slug: 'connectr', name: 'Connectr', year: '2021', bg: C.ink, fg: C.paper, acc: C.lime, lines: ['FRIENDS,', 'BY DESIGN.'],
    meta: [['Role', 'UX lead · Business plan'], ['Context', 'U-M Ross Tech & Business Jam'], ['Idea', 'MBTI-based group matching']] },
  { slug: 'neurobot', name: 'NeuroBot', year: '2022', bg: C.paper, fg: C.ink, acc: C.orange, lines: ['BRAINS,', 'DEMYSTIFIED.'],
    meta: [['Client', 'Backyard Brains'], ['Role', 'UX designer, team of 5'], ['Goal', 'Make neuroscience intuitive']] },
  { slug: 'huawei', name: 'Huawei', year: '2022', bg: C.ink, fg: C.paper, acc: C.orange, lines: ['FOLD THE', 'WORKSPACE.'],
    meta: [['Company', 'Huawei — Shenzhen'], ['Role', 'UX design intern'], ['Focus', 'Window management, foldable PCs']] },
  { slug: 'subtension', name: 'SubTension', year: '2022', bg: C.blue, fg: C.paper, acc: C.lime, lines: ['DIVE', 'DEEPER.'],
    meta: [['Studio', 'WolverineSoft'], ['Team', '40 people · 2 semesters'], ['Role', 'Narrative, flows, tutorials']] },
  { slug: 'rutabagga', name: 'Rutabagga', year: '2022', bg: C.orange, fg: C.ink, acc: C.paper, lines: ['LOCAL.', 'NATURAL.', 'SUSTAINABLE.'],
    meta: [['Role', 'Brand & logo design'], ['Tool', 'Adobe Illustrator'], ['Brief', 'Seasonal, plant-based eating']] },
];

let scene, cam, groups = [], phone, wipe, wbar, blobGeo, blobBase, sonar = [], bubbles = [], prop, orbiters = [];

// ------------------------------------------------------------ DOM per card
function buildCard(k, c) {
  const root = el('div', { cls: 'abs', style: { inset: 0, color: c.fg } }, S.root);
  c.root = root;
  c.idx = el('div', { cls: 'mono abs', style: { left: '120px', top: '150px', fontSize: '14px' }, html: `<span style="opacity:.55">${String(k + 1).padStart(2, '0')} / 06 —</span>&nbsp; ${c.name.toUpperCase()}` }, root);
  c.yr = el('div', { cls: 'mono abs', style: { left: '1040px', top: '150px', fontSize: '14px', opacity: .55 }, text: c.year }, root);
  c.hl = el('div', { cls: 'abs', style: { left: '112px', top: '290px' } }, root);
  c.lineEls = c.lines.map((s, i) => {
    const m = el('div', { cls: 'disp', style: { overflow: 'hidden', fontSize: '150px', paddingBottom: '0.04em', color: i === c.lines.length - 1 && c.acc !== c.fg ? c.acc : c.fg } }, c.hl);
    return el('span', { text: s, style: { display: 'inline-block' } }, m);
  });
  c.metaEls = c.meta.map(([a, b], i) => {
    const m = el('div', { cls: 'abs', style: { left: 120 + i * 320 + 'px', top: '760px', width: '300px' } }, root);
    el('div', { cls: 'abs', style: { left: 0, top: '-16px', width: '280px', height: '1px', background: c.fg, opacity: .3 } }, m);
    el('div', { cls: 'mono', style: { fontSize: '12px', opacity: .55, marginBottom: '8px' }, text: a }, m);
    el('div', { style: { fontFamily: 'Mono', fontSize: '16px', lineHeight: '22px', whiteSpace: 'normal' }, text: b }, m);
    return m;
  });
  c.link = el('div', { cls: 'mono abs', style: { left: '120px', top: '930px', fontSize: '14px' }, html: `↗&nbsp;&nbsp;TIANCHI-FU.COM/${c.slug.toUpperCase()}` }, root);
}

function buildPhone(root) {
  const wrap = el('div', { cls: 'abs', style: { left: '1250px', top: '150px', width: '380px', height: '780px', perspective: '1600px' } }, root);
  const ph = el('div', { cls: 'abs', style: { inset: 0, background: '#111', borderRadius: '58px', padding: '12px', boxShadow: '0 60px 120px rgba(0,0,0,.35), inset 0 0 0 2px #333', transformStyle: 'preserve-3d' } }, wrap);
  const scr = el('div', { cls: 'abs', style: { inset: '12px', background: '#F7F6F1', borderRadius: '46px', overflow: 'hidden', fontFamily: 'Archivo', color: C.ink } }, ph);
  el('div', { cls: 'abs', style: { left: '50%', top: '12px', width: '110px', height: '30px', marginLeft: '-55px', background: '#111', borderRadius: '20px' } }, scr);
  el('div', { cls: 'abs', style: { left: '30px', top: '16px', fontSize: '15px', fontWeight: 700 }, text: '9:41' }, scr);
  const head = el('div', { cls: 'abs', style: { left: '24px', top: '66px', right: '24px' } }, scr);
  el('div', { style: { fontSize: '13px', fontWeight: 500, opacity: .5, fontStretch: '100%' }, text: 'Ann Arbor · North Campus' }, head);
  el('div', { style: { fontSize: '34px', fontWeight: 800, fontStretch: '110%', letterSpacing: '-0.02em', marginTop: '4px' }, text: 'Find your place' }, head);
  const search = el('div', { style: { marginTop: '14px', height: '44px', borderRadius: '22px', background: '#fff', boxShadow: '0 1px 0 rgba(0,0,0,.06), 0 0 0 1px rgba(0,0,0,.06)', display: 'flex', alignItems: 'center', padding: '0 16px', fontSize: '14px', color: '#888', fontStretch: '100%' }, text: '⌕  Search 128 verified listings' }, head);
  const chips = el('div', { style: { display: 'flex', gap: '8px', marginTop: '12px' } }, head);
  ['Verified', '< $1.2k', 'Near bus', '2BR'].forEach((t, i) => el('div', { style: { fontSize: '12px', fontWeight: 600, padding: '7px 11px', borderRadius: '16px', background: i === 0 ? C.ink : '#ECEBE6', color: i === 0 ? C.lime : C.ink, fontStretch: '100%' }, text: t }, chips));
  const list = [
    ['Packard St · 2BR', '$1,150/mo · 0.4 mi', 'linear-gradient(135deg,#FF8A5B,#FF4D1A)'],
    ['Plymouth Rd · Studio', '$980/mo · 0.2 mi', 'linear-gradient(135deg,#7D87FF,#2F3BFF)'],
    ['Broadway · 3BR', '$1,420/mo · 0.9 mi', 'linear-gradient(135deg,#E8FF8A,#9BC21A)'],
  ];
  const cards = list.map((l, i) => {
    const cd = el('div', { cls: 'abs', style: { left: '16px', right: '16px', top: 262 + i * 112 + 'px', height: '100px', background: '#fff', borderRadius: '22px', boxShadow: '0 8px 24px rgba(0,0,0,.07)', display: 'flex', alignItems: 'center', padding: '10px', gap: '14px' } }, scr);
    el('div', { style: { width: '80px', height: '80px', borderRadius: '16px', background: l[2], flex: 'none' } }, cd);
    const tx = el('div', { style: { flex: 1, fontStretch: '100%' } }, cd);
    el('div', { style: { fontSize: '16px', fontWeight: 700 }, text: l[0] }, tx);
    el('div', { style: { fontSize: '13px', opacity: .55, marginTop: '4px' }, text: l[1] }, tx);
    el('div', { style: { display: 'inline-block', marginTop: '8px', fontSize: '11px', fontWeight: 700, color: '#1C7C3C', background: '#DDF5E3', padding: '3px 8px', borderRadius: '10px' }, text: '✓ Verified landlord' }, tx);
    const heart = el('div', { style: { width: '34px', height: '34px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', color: '#bbb' }, text: '♥' }, cd);
    return { cd, heart };
  });
  const bubble = el('div', { cls: 'abs', style: { left: '16px', right: '16px', top: '600px', background: C.ink, color: C.paper, borderRadius: '22px', padding: '14px 16px', fontStretch: '100%' } }, scr);
  el('div', { style: { fontSize: '11px', fontFamily: 'Mono', opacity: .6, marginBottom: '6px' }, text: 'FORUM · 2 REPLIES' }, bubble);
  el('div', { style: { fontSize: '15px', fontWeight: 600 }, text: 'Is the Packard landlord legit?' }, bubble);
  el('div', { style: { fontSize: '14px', marginTop: '6px', color: C.lime }, text: '“Lived there 2 years. Zero issues.”' }, bubble);
  const toast = el('div', { cls: 'abs', style: { left: '50%', top: '-70px', transform: 'translateX(-50%)', background: '#fff', color: C.ink, padding: '12px 18px', borderRadius: '30px', fontSize: '15px', fontWeight: 700, whiteSpace: 'nowrap', boxShadow: '0 20px 40px rgba(0,0,0,.18)', fontFamily: 'Archivo', fontStretch: '100%' }, html: `<span style="color:#1C7C3C">●</span>&nbsp; Lease verified` }, wrap);
  const cursorDot = el('div', { cls: 'abs', style: { width: '44px', height: '44px', borderRadius: '50%', background: 'rgba(12,12,13,.18)', border: '2px solid rgba(12,12,13,.5)' } }, scr);
  return { wrap, ph, cards, bubble, toast, cursorDot, search };
}

// ------------------------------------------------------------ 3D objects
function screenTex(kind) {
  const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 680;
  const g = cv.getContext('2d');
  g.fillStyle = '#0d0e12'; g.fillRect(0, 0, 1024, 680);
  const grad = g.createLinearGradient(0, 0, 1024, 680); grad.addColorStop(0, '#1b1f3a'); grad.addColorStop(1, '#3a1a10');
  g.fillStyle = grad; g.fillRect(0, 0, 1024, 680);
  const win = (x, y, w, h, col) => {
    g.fillStyle = '#f1efe8'; g.beginPath(); g.roundRect(x, y, w, h, 14); g.fill();
    g.fillStyle = col; g.beginPath(); g.roundRect(x, y, w, 36, [14, 14, 0, 0]); g.fill();
    g.fillStyle = 'rgba(0,0,0,.12)'; for (let i = 0; i < 6; i++) g.fillRect(x + 24, y + 62 + i * 30, (w - 48) * (0.4 + 0.6 * hash(i + x)), 12);
  };
  if (kind === 'top') { win(40, 40, 600, 380, C.orange); win(670, 40, 314, 600, C.blue); win(40, 450, 600, 190, '#2a2a2a'); }
  else {
    g.fillStyle = 'rgba(255,255,255,.08)';
    for (let r = 0; r < 4; r++) for (let c = 0; c < 12; c++) { g.beginPath(); g.roundRect(60 + c * 76, 210 + r * 80, 66, 66, 10); g.fill(); }
    g.fillStyle = 'rgba(255,255,255,.14)'; g.beginPath(); g.roundRect(300, 560, 424, 60, 12); g.fill();
    [C.orange, C.blue, C.lime, '#f1efe8'].forEach((c, i) => { g.fillStyle = c; g.beginPath(); g.roundRect(360 + i * 160, 50, 120, 120, 28); g.fill(); });
  }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
}

function build3D(ctx) {
  scene = new THREE.Scene();
  scene.environment = ctx.envMap;
  cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 100);
  cam.position.set(0, 0, 12);
  const key = new THREE.DirectionalLight('#ffffff', 2.4); key.position.set(-4, 6, 8); scene.add(key);
  const fill = new THREE.DirectionalLight('#ffd9c7', 0.8); fill.position.set(6, -2, 4); scene.add(fill);
  scene.add(new THREE.AmbientLight('#ffffff', 0.25));
  const chrome = new THREE.MeshPhysicalMaterial({ color: '#ffffff', metalness: 1, roughness: 0.07, envMapIntensity: 1.4 });
  const lime = new THREE.MeshPhysicalMaterial({ color: C.lime, roughness: 0.16, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.1 });
  const X = 2.95;
  // 0: none (phone is DOM)
  groups[0] = new THREE.Group();
  // 1: Connectr — interlocked rings
  {
    const g = new THREE.Group();
    const a = new THREE.Mesh(new THREE.TorusGeometry(1.05, 0.3, 64, 220), chrome);
    const b = new THREE.Mesh(new THREE.TorusGeometry(1.05, 0.3, 64, 220), lime);
    a.position.x = -0.55; b.position.x = 0.55; b.rotation.x = Math.PI / 2;
    g.add(a, b); g.userData = { a, b }; groups[1] = g;
  }
  // 2: NeuroBot — living blob + orbiting nodes
  {
    const g = new THREE.Group();
    let geo = new THREE.IcosahedronGeometry(1.35, 32); geo.deleteAttribute('normal'); geo.deleteAttribute('uv');
    geo = mergeVertices(geo); geo.computeVertexNormals();
    blobGeo = geo; blobBase = geo.attributes.position.array.slice();
    const mat = new THREE.MeshPhysicalMaterial({ color: '#FF5A22', roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.06, sheen: 0.3 });
    g.add(new THREE.Mesh(geo, mat));
    for (let i = 0; i < 4; i++) { const m = new THREE.Mesh(new THREE.SphereGeometry(0.16, 48, 32), chrome); g.add(m); orbiters.push(m); }
    groups[2] = g;
  }
  // 3: Huawei — foldable PC
  {
    const g = new THREE.Group();
    const shell = new THREE.MeshPhysicalMaterial({ color: '#2a2b30', metalness: 0.85, roughness: 0.32 });
    const base = new THREE.Mesh(new RoundedBoxGeometry(3.4, 0.07, 2.2, 3, 0.03), shell);
    const bs = new THREE.Mesh(new THREE.PlaneGeometry(3.25, 2.05), new THREE.MeshBasicMaterial({ map: screenTex('bottom'), toneMapped: false }));
    bs.rotation.x = -Math.PI / 2; bs.position.y = 0.037; base.add(bs);
    const pivot = new THREE.Group(); pivot.position.set(0, 0.04, -1.1);
    const top = new THREE.Mesh(new RoundedBoxGeometry(3.4, 2.2, 0.07, 3, 0.03), shell); top.position.y = 1.1;
    const ts = new THREE.Mesh(new THREE.PlaneGeometry(3.25, 2.05), new THREE.MeshBasicMaterial({ map: screenTex('top'), toneMapped: false })); ts.position.z = 0.037; top.add(ts);
    pivot.add(top); g.add(base, pivot); g.userData = { pivot }; groups[3] = g;
  }
  // 4: SubTension — submarine + sonar
  {
    const g = new THREE.Group();
    const sub = new THREE.Group();
    const hull = new THREE.Mesh(new THREE.CapsuleGeometry(0.52, 2.4, 16, 64), chrome); hull.rotation.z = Math.PI / 2; sub.add(hull);
    const tower = new THREE.Mesh(new RoundedBoxGeometry(0.75, 0.62, 0.36, 4, 0.12), chrome); tower.position.set(0.25, 0.62, 0); sub.add(tower);
    const peri = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.5, 16), chrome); peri.position.set(0.4, 1.1, 0); sub.add(peri);
    const band = new THREE.Mesh(new THREE.TorusGeometry(0.53, 0.05, 16, 80), lime); band.rotation.y = Math.PI / 2; band.position.x = -0.6; sub.add(band);
    const finV = new THREE.Mesh(new RoundedBoxGeometry(0.5, 0.9, 0.05, 2, 0.02), chrome); finV.position.set(-1.6, 0, 0); sub.add(finV);
    const finH = new THREE.Mesh(new RoundedBoxGeometry(0.5, 0.05, 0.9, 2, 0.02), chrome); finH.position.set(-1.6, 0, 0); sub.add(finH);
    prop = new THREE.Group(); prop.position.x = -1.95;
    for (let i = 0; i < 3; i++) { const b = new THREE.Mesh(new RoundedBoxGeometry(0.04, 0.5, 0.14, 2, 0.015), lime); b.position.y = 0.22; const h = new THREE.Group(); h.add(b); h.rotation.x = i * Math.PI * 2 / 3; prop.add(h); }
    sub.add(prop);
    g.add(sub); g.userData = { sub };
    for (let i = 0; i < 4; i++) { const r = new THREE.Mesh(new THREE.RingGeometry(0.98, 1, 128), new THREE.MeshBasicMaterial({ color: C.lime, transparent: true, side: THREE.DoubleSide })); r.position.z = -1.5; g.add(r); sonar.push(r); }
    for (let i = 0; i < 14; i++) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.04 + hash(i) * 0.07, 24, 16), new THREE.MeshPhysicalMaterial({ color: '#cfd6ff', roughness: 0.05, transmission: 0.0, metalness: 0.2, transparent: true, opacity: 0.8 })); g.add(b); bubbles.push(b); }
    groups[4] = g;
  }
  // 5: Rutabagga — glossy turnip
  {
    const g = new THREE.Group();
    const prof = [];
    for (let i = 0; i <= 60; i++) {
      const u = i / 60; // 0 bottom tip -> 1 top
      const y = lerp(-1.55, 0.95, u);
      const r = Math.sin(Math.pow(u, 0.75) * Math.PI) * 1.18 * (u > 0.85 ? 1 : 1) + (u > 0.97 ? 0 : 0);
      prof.push(new THREE.Vector2(Math.max(0.001, r * (1 - Math.pow(1 - u, 6) * 0.9)), y));
    }
    const lg = new THREE.LatheGeometry(prof, 160);
    const cols = []; const pa = lg.attributes.position;
    const purple = new THREE.Color('#8A3FB0'), cream = new THREE.Color('#F4EAD2'), tmp = new THREE.Color();
    for (let i = 0; i < pa.count; i++) { const y = pa.getY(i); tmp.copy(cream).lerp(purple, clamp((y - 0.0) / 0.55)); cols.push(tmp.r, tmp.g, tmp.b); }
    lg.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
    const body = new THREE.Mesh(lg, new THREE.MeshPhysicalMaterial({ vertexColors: true, roughness: 0.28, clearcoat: 1, clearcoatRoughness: 0.1 }));
    g.add(body);
    for (let i = 0; i < 3; i++) {
      const leaf = new THREE.Mesh(new THREE.SphereGeometry(0.5, 48, 32), lime);
      leaf.scale.set(0.42, 1.25, 0.12);
      const h = new THREE.Group(); h.position.y = 0.95; leaf.position.y = 0.55; h.add(leaf);
      h.rotation.y = i * Math.PI * 2 / 3; h.rotation.z = 0.42; g.add(h);
    }
    groups[5] = g;
  }
  groups.forEach(g => { g.position.x = X; scene.add(g); });
}

S.init = (ctx) => {
  CARDS.forEach((c, k) => buildCard(k, c));
  phone = buildPhone(CARDS[0].root);
  wipe = el('div', { cls: 'abs', style: { left: 0, top: 0, width: W + 'px', height: H + 'px' } }, S.root);
  wbar = el('div', { cls: 'abs', style: { left: '-18px', top: 0, width: '18px', height: H + 'px' } }, wipe);
  build3D(ctx);
};
S.afterFonts = () => {
  S.root.style.display = 'block';
  CARDS.forEach(c => {
    c.root.style.display = 'block';
    let size = 168;
    for (const l of c.lineEls) { const w = l.getBoundingClientRect().width; size = Math.min(size, 150 * 1040 / w); }
    if (c.lines.length > 2) size = Math.min(size, 128);
    c.lineEls.forEach(l => l.parentNode.style.fontSize = size + 'px');
    c.root.style.display = 'none';
  });
  S.root.style.display = 'none';
};

S.render = (lt, t, ctx) => {
  const k = clamp(Math.floor(lt / CARD), 0, 5);
  const cl = lt - k * CARD;
  const c = CARDS[k];
  ctx.setBg(c.bg);
  ctx.hud.tone = (c.bg === C.ink || c.bg === C.blue) ? 'light' : 'dark';
  ctx.hud.chapter = `06 — SELECTED WORK  ${String(k + 1).padStart(2, '0')}/06`;
  CARDS.forEach((cc, i) => cc.root.style.display = i === k ? 'block' : 'none');
  // text in
  c.lineEls.forEach((l, i) => { const e = seg(cl, 0.04 + i * 0.07, 0.6 + i * 0.07, E.outExpo); l.style.transform = `translateY(${(1 - e) * 105}%)`; });
  c.metaEls.forEach((m, i) => { const e = seg(cl, 0.3 + i * 0.06, 0.8 + i * 0.06, E.outExpo); m.style.opacity = e; m.style.transform = `translateY(${(1 - e) * 24}px)`; });
  [c.idx, c.yr, c.link].forEach((e, i) => e.style.opacity = cl > 0.12 + i * 0.1 ? 1 : 0);
  // Rutabagga: tagline words swap in on the beat
  if (k === 5) c.lineEls.forEach((l, i) => { l.parentNode.style.color = Math.floor(cl / 0.5) % 3 === i ? C.paper : C.ink; });

  // visuals
  groups.forEach((g, i) => g.visible = i === k);
  const g = groups[k];
  const pop = clamp(spring(cl - 0.05, 1.6, 0.42), 0, 1.2);
  g.scale.setScalar(lerp(0.4, 1, pop));
  if (k === 0) {
    const e = spring(cl, 1.4, 0.5);
    phone.wrap.style.transform = `translateY(${(1 - e) * 180 + Math.sin(cl * 2) * 8}px)`;
    phone.ph.style.transform = `rotateY(${lerp(-34, -14, e) + cl * 3}deg) rotateX(${lerp(14, 6, e)}deg) rotateZ(${lerp(4, 1.5, e)}deg)`;
    phone.cards.forEach((cd, i) => {
      const s = spring(cl - 0.25 - i * 0.08, 2.4, 0.45);
      cd.cd.style.opacity = clamp(s * 2); cd.cd.style.transform = `translateY(${(1 - s) * 50}px)`;
      const hp = cl - 0.95;
      if (i === 0) { cd.heart.style.color = hp > 0 ? C.orange : '#bbb'; cd.heart.style.transform = `scale(${hp > 0 ? 1 + (1 - spring(hp, 3, 0.25)) * 0.8 + (spring(hp, 3, 0.25) - 1) * 0 : 1})`; }
    });
    const tap = cl - 0.8;
    phone.cursorDot.style.opacity = tap > 0 && tap < 0.35 ? 1 : 0;
    phone.cursorDot.style.transform = `translate(${272 - 22}px,${262 + 50 - 22}px) scale(${tap > 0 ? 1 - 0.3 * Math.sin(clamp(tap / 0.3) * Math.PI) : 1})`;
    const b = spring(cl - 1.05, 2.2, 0.5);
    phone.bubble.style.opacity = clamp(b * 2); phone.bubble.style.transform = `translateY(${(1 - b) * 60}px)`;
    const ts = spring(cl - 1.25, 2.5, 0.45);
    phone.toast.style.opacity = clamp(ts * 2); phone.toast.style.transform = `translate(-50%, ${(1 - ts) * 40 + 20}px) scale(${lerp(0.8, 1, clamp(ts))})`;
  }
  if (k === 1) { const { a, b } = g.userData; g.rotation.set(0.5 + Math.sin(cl) * 0.2, cl * 1.1 - 0.6, 0.3); a.rotation.y = cl * 0.4; }
  if (k === 2) {
    const pa = blobGeo.attributes.position.array;
    const tt = cl * 1.6;
    for (let i = 0; i < pa.length; i += 3) {
      const x = blobBase[i], y = blobBase[i + 1], z = blobBase[i + 2];
      const d = 1 + 0.13 * Math.sin(x * 2.6 + tt) * Math.sin(y * 2.9 + tt * 1.3) * Math.sin(z * 2.3 - tt * 0.8) + 0.07 * Math.sin(x * 5.5 - y * 4.1 + tt * 2.2);
      pa[i] = x * d; pa[i + 1] = y * d; pa[i + 2] = z * d;
    }
    blobGeo.attributes.position.needsUpdate = true; blobGeo.computeVertexNormals();
    g.rotation.set(0.3, cl * 0.6, 0);
    orbiters.forEach((o, i) => { const a = cl * (1.4 + i * 0.3) + i * 1.7, r = 1.95 + i * 0.12; o.position.set(Math.cos(a) * r, Math.sin(a * 0.7 + i) * 0.9, Math.sin(a) * r); });
  }
  if (k === 3) {
    const open = seg(cl, 0.2, 1.2, E.inOutCubic);
    g.userData.pivot.rotation.x = lerp(Math.PI / 2 - 0.02, -0.22, open);
    g.rotation.set(lerp(0.75, 0.42, open), -0.55 + cl * 0.18, 0);
    g.position.y = -0.35;
  }
  if (k === 4) {
    const { sub } = g.userData;
    sub.position.y = Math.sin(cl * 2.2) * 0.12; sub.rotation.set(Math.sin(cl * 1.3) * 0.08, -0.5 + cl * 0.25, Math.sin(cl * 1.7) * 0.06);
    prop.rotation.x = cl * 14;
    sonar.forEach((r, i) => { const p = ((cl * 0.55 + i / 4) % 1); r.scale.setScalar(0.4 + p * 3.4); r.material.opacity = (1 - p) * 0.7; });
    bubbles.forEach((b, i) => { const p = (cl * (0.25 + hash(i * 3) * 0.3) + hash(i)) % 1; b.position.set(-2.4 + hash(i * 7) * 1.2, -1.4 + p * 3.2, (hash(i * 11) - 0.5) * 1.2); b.material.opacity = Math.sin(p * Math.PI) * 0.8; });
  }
  if (k === 5) { g.rotation.set(0.12, cl * 1.2, Math.sin(cl * 2) * 0.08); g.position.y = 0.15 + Math.sin(cl * 2.2) * 0.06; }
  ctx.renderGL(scene, cam);

  // wipe to next card (last one wipes to ink for the next section)
  const next = k < 5 ? CARDS[k + 1].bg : C.ink;
  const w = seg(cl, 1.68, 2.0, E.inOutExpo);
  wipe.style.background = next;
  wbar.style.background = next === C.orange || next === C.lime ? C.blue : C.orange;
  wipe.style.transform = `translateX(${(1 - w) * (W + 40)}px)`;
  if (w > 0.6) ctx.hud.tone = (next === C.ink || next === C.blue) ? 'light' : 'dark';
};
export default S;
