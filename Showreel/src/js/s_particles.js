// 16–20s  Particles: MOTION text -> sphere -> galaxy swirl -> single point
import * as THREE from 'three';
import { C, W, H, el, prog, seg, E, lerp, clamp, rng, noise2 } from './core.js';
import { SOLO } from './s_type.js';

const S = { t0: 16, t1: 20 };
const N = 26000;
let scene, cam, pts, geo, A, B, Cs, rnd, col, arm, word, dot, lab;
const cPaper = new THREE.Color(C.paper), cBlue = new THREE.Color('#4656ff'), cOrange = new THREE.Color(C.orange);

S.init = () => {
  scene = new THREE.Scene();
  cam = new THREE.PerspectiveCamera(35, W / H, 1, 6000);
  geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
  geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
  geo.setAttribute('aSize', new THREE.BufferAttribute(new Float32Array(N), 1));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uOpacity: { value: 1 } },
    vertexShader: `attribute vec3 color; attribute float aSize; varying vec3 vC; void main(){ vC = color; vec4 mv = modelViewMatrix * vec4(position,1.0); gl_PointSize = aSize * (1712.0 / -mv.z); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform float uOpacity; varying vec3 vC; void main(){ vec2 p = gl_PointCoord - 0.5; float d = length(p); float a = smoothstep(0.5, 0.15, d); gl_FragColor = vec4(vC, a * uOpacity); }`,
  });
  pts = new THREE.Points(geo, mat);
  pts.frustumCulled = false;
  scene.add(pts);
  word = el('div', { cls: 'disp abs', style: { left: 0, top: 0, width: W + 'px', height: H + 'px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: SOLO.size + 'px', color: C.paper }, text: SOLO.text }, S.root);
  dot = el('div', { cls: 'abs', style: { left: '942px', top: '522px', width: '36px', height: '36px', borderRadius: '50%', background: C.orange } }, S.root);
  lab = el('div', { cls: 'mono abs', style: { left: '50%', top: '880px', transform: 'translateX(-50%)', color: C.paper, opacity: .6 } }, S.root);
};

S.afterFonts = () => {
  // sample the word into particle targets
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const g = cv.getContext('2d');
  g.fillStyle = '#fff'; g.font = `900 ${SOLO.size}px Archivo`; g.fontStretch = 'expanded'; g.letterSpacing = (-0.02 * SOLO.size) + 'px';
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(SOLO.text, W / 2, H / 2 + 8);
  const d = g.getImageData(0, 0, W, H).data;
  const cand = [];
  for (let y = 0; y < H; y += 2) for (let x = 0; x < W; x += 2) if (d[(y * W + x) * 4 + 3] > 128) cand.push([x - W / 2, H / 2 - y]);
  const R = rng(42);
  A = new Float32Array(N * 3); B = new Float32Array(N * 3); Cs = new Float32Array(N * 3);
  rnd = new Float32Array(N); arm = new Uint8Array(N);
  const golden = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < N; i++) {
    const c = cand[Math.floor(R() * cand.length)];
    A[i * 3] = c[0] + (R() - .5) * 2; A[i * 3 + 1] = c[1] + (R() - .5) * 2; A[i * 3 + 2] = 0;
    const y = 1 - (i / (N - 1)) * 2, rr = Math.sqrt(1 - y * y), th = golden * i;
    const rs = 330 * (1 + (R() - .5) * 0.03);
    B[i * 3] = Math.cos(th) * rr * rs; B[i * 3 + 1] = y * rs; B[i * 3 + 2] = Math.sin(th) * rr * rs;
    const a = i % 2, u = R();
    const r = 30 + Math.pow(u, 0.75) * 640;
    const t = a * Math.PI + r * 0.011 + (R() - .5) * (0.5 + 140 / (r + 40));
    Cs[i * 3] = Math.cos(t) * r; Cs[i * 3 + 1] = (R() - .5) * (60 * Math.exp(-r / 200) + 8); Cs[i * 3 + 2] = Math.sin(t) * r;
    rnd[i] = R(); arm[i] = r < 90 ? 2 : a;
  }
};

const rotY = (x, z, a) => [x * Math.cos(a) + z * Math.sin(a), -x * Math.sin(a) + z * Math.cos(a)];

S.render = (lt, t, ctx) => {
  ctx.setBg(C.ink); ctx.hud.tone = 'light'; ctx.hud.chapter = '04 — PARTICLES';
  const pos = geo.attributes.position.array, colA = geo.attributes.color.array, sz = geo.attributes.aSize.array;
  const tilt = 1.05; // galaxy disk tilt
  const sphereRot = Math.max(0, lt - 0.5) * 0.9;
  const swirlRot = Math.max(0, lt - 2.2) * 0.8 + Math.pow(Math.max(0, lt - 3.1), 2) * 9;
  const collapse = E.inExpo(prog(lt, 3.15, 3.7));
  for (let i = 0; i < N; i++) {
    const i3 = i * 3;
    const ax = A[i3], ay = A[i3 + 1];
    // text jitter
    const jit = seg(lt, 0.1, 0.6, E.inCubic) * 6;
    let x = ax + Math.sin(i * 1.7 + lt * 9) * jit, y = ay + Math.cos(i * 2.3 + lt * 8) * jit, z = 0;
    // to sphere
    const d1 = (ax + 960) / 1920 * 0.4 + rnd[i] * 0.15;
    const e1 = E.inOutCubic(prog(lt, 0.45 + d1, 1.15 + d1));
    if (e1 > 0) {
      let [bx, bz] = rotY(B[i3], B[i3 + 2], sphereRot);
      const by = B[i3 + 1];
      const turb = Math.sin(e1 * Math.PI) * 160;
      x = lerp(x, bx, e1) + (noise2(i * 0.01, lt) - .5) * turb;
      y = lerp(y, by, e1) + (noise2(lt, i * 0.013) - .5) * turb;
      z = lerp(z, bz, e1) + Math.sin(i) * turb * 0.5;
    }
    // to swirl
    const e2 = E.inOutCubic(prog(lt, 2.1 + rnd[i] * 0.35, 2.9 + rnd[i] * 0.35));
    if (e2 > 0) {
      let [cx, cz] = rotY(Cs[i3], Cs[i3 + 2], swirlRot * (1 + 200 / (Math.hypot(Cs[i3], Cs[i3 + 2]) + 100)));
      let cy = Cs[i3 + 1];
      const yy = cy * Math.cos(tilt) - cz * Math.sin(tilt), zz = cy * Math.sin(tilt) + cz * Math.cos(tilt);
      // rotate disk in screen plane a bit
      const ang = -0.45, rx = cx * Math.cos(ang) - yy * Math.sin(ang), ry = cx * Math.sin(ang) + yy * Math.cos(ang);
      x = lerp(x, rx, e2); y = lerp(y, ry, e2); z = lerp(z, zz, e2);
    }
    if (collapse > 0) { const k = 1 - collapse; x *= k; y *= k; z *= k; }
    pos[i3] = x; pos[i3 + 1] = y; pos[i3 + 2] = z;
    const c = arm[i] === 0 ? cBlue : arm[i] === 1 ? cOrange : cPaper;
    const m = e2 * 0.95;
    colA[i3] = lerp(cPaper.r, c.r, m); colA[i3 + 1] = lerp(cPaper.g, c.g, m); colA[i3 + 2] = lerp(cPaper.b, c.b, m);
    sz[i] = (e1 > 0 ? 3.2 : 2.6) * (0.7 + rnd[i] * 0.6);
  }
  geo.attributes.position.needsUpdate = geo.attributes.color.needsUpdate = geo.attributes.aSize.needsUpdate = true;
  pts.material.uniforms.uOpacity.value = clamp(lt / 0.12) * 0.85 * (1 - prog(lt, 3.6, 3.72));
  // camera: dead-on for the text, then a slow orbit for depth
  const orb = seg(lt, 0.6, 3.0, E.inOutCubic) * 0.35;
  const dist = 1712 - seg(lt, 0.6, 3.2, E.inOutCubic) * 300;
  cam.position.set(Math.sin(orb) * dist, Math.sin(orb) * 120, Math.cos(orb) * dist);
  cam.lookAt(0, 0, 0);
  ctx.renderGL(scene, cam);
  word.style.opacity = 1 - prog(lt, 0.02, 0.2);
  const dp = prog(lt, 3.62, 3.75);
  dot.style.opacity = dp > 0 ? 1 : 0;
  dot.style.transform = `scale(${lt > 3.62 ? 0.3 + spring(lt - 3.62, 3, 0.3) * 0.7 : 0})`;
  ctx.flash(Math.max(0, 1 - Math.abs(lt - 3.66) / 0.06) * 0.35);
  lab.textContent = lt < 2.1 ? `N=${N.toLocaleString('en-US')} — TEXT → SPHERE` : lt < 3.15 ? 'SPHERE → SPIRAL / 2 ARMS' : 'COLLAPSE → 1';
  lab.style.opacity = lt > 0.6 && lt < 3.6 ? .6 : 0;
};
import { spring } from './core.js';
export default S;
