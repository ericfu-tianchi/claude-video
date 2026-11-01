// 8–12s  The grid extrudes into a 3D cube field; an orange sphere rolls through it.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { C, W, H, el, prog, seg, E, noise2, lerp, clamp } from './core.js';
import { GRID, cellColor } from './s_grid.js';

const S = { t0: 8, t1: 12 };
let scene, cam, mesh, sphere, key, cells = [], lab;
const BG = '#121214';
const dummy = new THREE.Object3D();

S.init = (ctx) => {
  scene = new THREE.Scene();
  scene.fog = new THREE.Fog(BG, 30, 75);
  scene.environment = ctx.envMap;
  scene.environmentIntensity = 0.35;
  cam = new THREE.PerspectiveCamera(20, W / H, 0.1, 300);
  scene.add(new THREE.HemisphereLight('#ffffff', '#202024', 0.7));
  key = new THREE.DirectionalLight('#fff4e8', 2.6);
  key.position.set(-8, 30, 7);
  key.castShadow = true;
  key.shadow.mapSize.set(4096, 4096);
  Object.assign(key.shadow.camera, { left: -38, right: 38, top: 38, bottom: -38, near: 1, far: 90 });
  key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02; key.shadow.radius = 4;
  scene.add(key);
  const rim = new THREE.DirectionalLight('#7f8cff', 0.9); rim.position.set(18, 8, -20); scene.add(rim);

  const ci0 = (GRID.cols - 1) / 2, cj0 = (GRID.rows - 1) / 2;
  for (let j = -18; j < GRID.rows + 18; j++) for (let i = -22; i < GRID.cols + 22; i++) cells.push({ i, j, x: i - ci0, z: j - cj0 });
  const geo = new RoundedBoxGeometry(1, 1, 1, 2, 0.06);
  geo.translate(0, 0.5, 0);
  const mat = new THREE.MeshStandardMaterial({ roughness: 0.42, metalness: 0.0 });
  mesh = new THREE.InstancedMesh(geo, mat, cells.length);
  mesh.castShadow = mesh.receiveShadow = true;
  const col = new THREE.Color();
  cells.forEach((c, k) => { col.set(cellColor(c.i, c.j)); if (col.getHex() === 0xECEAE3) col.set('#E4E1DA'); mesh.setColorAt(k, col); });
  scene.add(mesh);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: '#0e0e10', roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

  sphere = new THREE.Mesh(new THREE.SphereGeometry(1.15, 96, 64), new THREE.MeshPhysicalMaterial({ color: C.orange, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 1.2 }));
  sphere.castShadow = true;
  // a faint stripe so rolling reads
  scene.add(sphere);
  lab = el('div', { cls: 'mono abs', style: { left: '56px', top: '120px', color: C.ink, lineHeight: '20px', opacity: .7 } }, S.root);
};

const heightAt = (x, z, t) => {
  const amp = seg(t, 0.15, 1.2, E.inOutCubic);
  const n = noise2(x * 0.13 + t * 0.35, z * 0.13 - t * 0.2);
  const w = Math.sin(x * 0.35 + t * 2.2) * Math.cos(z * 0.3 - t * 1.4);
  return 0.25 + amp * (n * 2.6 + w * 0.6 + 0.6);
};
const spherePath = t => { const u = t - 0.6; return new THREE.Vector3(lerp(-20, 9, E.outCubic(clamp(u / 3.2))), 0, Math.sin(u * 0.9) * 2.2 + 0.5); };

S.render = (lt, t, ctx) => {
  ctx.setBg(BG); ctx.hud.tone = 'dark'; ctx.hud.chapter = '02 — DIMENSION';
  // camera: perfect top-down (matches the 2D grid) -> tilt -> slow orbit -> push into the sphere
  const tilt = seg(lt, 0.05, 1.3, E.inOutQuint);
  const push = E.inExpo(prog(lt, 3.35, 4.0));
  const sp = spherePath(lt);
  const az = lerp(0, -0.55, tilt) + lt * 0.06;
  const el_ = lerp(Math.PI / 2 - 0.0001, 0.62, tilt);
  const dist = lerp(54.7, 30, tilt);
  const tgt = new THREE.Vector3(0, 0, 0).lerp(new THREE.Vector3(sp.x * 0.5, 0.5, sp.z * 0.5), tilt);
  cam.fov = lerp(20, 32, tilt);
  scene.fog.near = dist + 4; scene.fog.far = dist + 48;
  cam.position.set(tgt.x + dist * Math.cos(el_) * Math.sin(az), tgt.y + dist * Math.sin(el_), tgt.z + dist * Math.cos(el_) * Math.cos(az));
  if (tilt < 0.02) cam.up.set(0, 0, -1); else cam.up.set(0, 1, 0);
  cam.lookAt(tgt);
  if (push > 0) { cam.position.lerp(sp.clone().add(new THREE.Vector3(0, 1.2, 0)), push * 0.93); cam.lookAt(new THREE.Vector3().lerpVectors(tgt, sp, push)); }
  cam.updateProjectionMatrix();

  const sx = sp.x, sz = sp.z, sR = 2.6;
  let groundH = 0;
  cells.forEach((c, k) => {
    let h = heightAt(c.x, c.z, lt);
    const d2 = (c.x - sx) ** 2 + (c.z - sz) ** 2;
    const dent = lt > 0.6 ? Math.exp(-d2 / (2 * sR * sR / 4)) : 0;
    h = Math.max(0.12, h * (1 - 0.85 * dent));
    if (d2 < 1.2) groundH = Math.max(groundH, h);
    dummy.position.set(c.x, 0, c.z);
    dummy.scale.set(0.82, h, 0.82);
    dummy.updateMatrix();
    mesh.setMatrixAt(k, dummy.matrix);
  });
  mesh.instanceMatrix.needsUpdate = true;
  sphere.position.set(sx, Math.max(groundH, 0.3) + 1.15, sz);
  sphere.rotation.z = -sx / 1.15;
  sphere.visible = lt > 0.6;
  ctx.renderGL(scene, cam);
  ctx.flash(Math.max(0, 1 - lt / 0.1) * 0.2);
  lab.innerHTML = `INSTANCES&nbsp;${cells.length}<br>CAM&nbsp;${(cam.fov).toFixed(1)}°&nbsp;/&nbsp;EL&nbsp;${(el_ * 57.3).toFixed(1)}°<br>SPHERE&nbsp;[${sx.toFixed(2)}, ${sz.toFixed(2)}]`;
  lab.style.opacity = lt > 1.0 && lt < 3.4 ? .7 : 0;
};
export default S;
