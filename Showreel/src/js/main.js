import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { W, H, C, el, css, BEAT } from './core.js';
import open from './s_open.js';
import grid from './s_grid.js';
import cubes from './s_cubes.js';
import typewall from './s_type.js';
import particles from './s_particles.js';
import title from './s_title.js';
import work from './s_work.js';
import words from './s_words.js';
import end from './s_end.js';

export const FPS = 60;
const SCENES = [open, grid, cubes, typewall, particles, title, work, words, end];
export const DURATION = 43;

const $ = id => document.getElementById(id);
const renderer = new THREE.WebGLRenderer({ canvas: $('gl'), antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const pmrem = new THREE.PMREMGenerator(renderer);
const envMap = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const ctx = {
  THREE, renderer, envMap,
  dom: $('dom'), bg: $('bg'), c2d: $('c2d').getContext('2d'),
  glUsed: false, c2dUsed: false,
  setBg(c) { this.bg.style.background = c; },
  renderGL(scene, cam) { renderer.render(scene, cam); this.glUsed = true; },
  flash(v) { $('flash').style.opacity = v; },
  hud: { tone: 'light', chapter: '', show: 1 },
};

// ---------------------------------------------------------------- HUD
const hud = $('hud');
const mk = (style, text = '') => el('div', { cls: 'mono abs', style, text }, hud);
const H_TL = mk({ left: '56px', top: '44px' });
H_TL.innerHTML = '<b style="font-weight:700">TIANCHI FU</b>&nbsp;&nbsp;/&nbsp;&nbsp;SHOWREEL ’26';
const H_TL2 = mk({ left: '56px', top: '64px', opacity: .55 }, 'PRODUCT · MOTION · CODE');
const H_TR = mk({ right: '56px', top: '44px', textAlign: 'right' });
const H_TR2 = mk({ right: '56px', top: '64px', textAlign: 'right', opacity: .55 }, '1920×1080 — 60FPS');
const H_BL = mk({ left: '56px', bottom: '44px' });
const H_BR = mk({ right: '56px', bottom: '44px', textAlign: 'right' }, 'TECHNOLOGY × DESIGN');
const H_REC = el('div', { cls: 'abs', style: { right: '56px', top: '88px', width: '8px', height: '8px', borderRadius: '50%', background: C.orange } }, hud);
const ticks = [];
for (const [x, y, sx, sy] of [[40, 30, 1, 1], [1880, 30, -1, 1], [40, 1050, 1, -1], [1880, 1050, -1, -1]]) {
  ticks.push(el('div', { cls: 'abs', style: { left: x + 'px', top: y + 'px', width: '14px', height: '14px', borderLeft: sx > 0 ? '1px solid' : 'none', borderRight: sx < 0 ? '1px solid' : 'none', borderTop: sy > 0 ? '1px solid' : 'none', borderBottom: sy < 0 ? '1px solid' : 'none', transform: `translate(${sx < 0 ? -14 : 0}px,${sy < 0 ? -14 : 0}px)` } }, hud));
}
const progBar = el('div', { cls: 'abs', style: { left: '56px', right: '56px', bottom: '30px', height: '1px', opacity: .25, background: 'currentColor' } }, hud);
const progFill = el('div', { cls: 'abs', style: { left: '56px', bottom: '30px', height: '1px', background: 'currentColor' } }, hud);
const pad = (n, l = 2) => String(Math.floor(n)).padStart(l, '0');

function drawHud(t, frame) {
  const h = ctx.hud;
  hud.style.color = h.tone === 'dark' ? C.ink : C.paper;
  hud.style.opacity = h.show;
  H_TR.textContent = `TC ${pad(t / 60)}:${pad(t % 60)}:${pad(frame % FPS)}`;
  H_BL.textContent = h.chapter;
  H_REC.style.opacity = Math.floor(t / BEAT) % 2 ? .25 : 1;
  progFill.style.width = (1808 * t / DURATION) + 'px';
}

// ---------------------------------------------------------------- grain
const gctx = $('grain').getContext('2d');
const grains = [];
{
  let s = 7;
  for (let k = 0; k < 8; k++) {
    const img = gctx.createImageData(960, 540);
    for (let i = 0; i < img.data.length; i += 4) {
      s = (s * 1664525 + 1013904223) >>> 0;
      const v = (s >>> 24);
      img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255;
    }
    grains.push(img);
  }
}

// ---------------------------------------------------------------- init
for (const s of SCENES) {
  s.root = el('div', { cls: 'scene' }, ctx.dom);
  s.init(ctx);
}

let lastActive = null;
window.seek = async function (t) {
  const frame = Math.round(t * FPS);
  ctx.glUsed = false; ctx.c2dUsed = false;
  ctx.flash(0);
  ctx.hud.show = 1;
  const active = SCENES.find(s => t >= s.t0 && t < s.t1) || SCENES[SCENES.length - 1];
  for (const s of SCENES) s.root.style.display = s === active ? 'block' : 'none';
  if (active !== lastActive) { renderer.clear(); ctx.c2d.clearRect(0, 0, W, H); lastActive = active; }
  active.render(t - active.t0, t, ctx);
  if (!ctx.glUsed) renderer.clear();
  if (!ctx.c2dUsed) ctx.c2d.clearRect(0, 0, W, H);
  drawHud(t, frame);
  gctx.putImageData(grains[Math.floor(frame / 2) % grains.length], 0, 0);
  await new Promise(r => requestAnimationFrame(() => r()));
  return frame;
};
window.DURATION = DURATION; window.FPS = FPS;

await document.fonts.load('900 100px Archivo');
await document.fonts.load('italic 900 100px Archivo');
await document.fonts.load('500 20px Mono');
await document.fonts.load('400 20px Mono');
await document.fonts.load('700 20px Mono');
await document.fonts.ready;
for (const s of SCENES) if (s.afterFonts) await s.afterFonts(ctx);
window.READY = true;
// preview mode: ?t=12.3 shows a still; ?play plays in realtime
const q = new URLSearchParams(location.search);
if (q.has('t')) window.seek(parseFloat(q.get('t')));
if (q.has('play')) { const t0 = performance.now(); const loop = async () => { await window.seek(((performance.now() - t0) / 1000) % DURATION); requestAnimationFrame(loop); }; loop(); }
