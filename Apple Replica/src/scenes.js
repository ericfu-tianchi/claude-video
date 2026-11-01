// Recreation of the Apple product-morph film. Scene times are in SOURCE seconds of the reference;
// the output plays source 1.6–37.0, then cuts (through a morph) to source 84.0–94.8.
const A0 = 1.6, A1 = 37.0, B0 = 84.0, B1 = 94.8;
MAP = T => (T < A1 - A0 ? A0 + T : B0 + (T - (A1 - A0)));
window.DURATION = (A1 - A0) + (B1 - B0);

const GREY_D = hex('#5c5b5f'), GREY_L = hex('#aaa9ad'), WHITE = [255, 255, 255], INK = hex('#1d1d1f');
const PINK = hex('#e6286a'), BLUE = hex('#4b4ee6');

// ---------------------------------------------------------------- 1. iPod click wheel (1.6 – 6.4)
scene(1.6, 6.45, t => {
  const R = key(t, [[2.45, 0], [3.0, 333, ease.expo], [3.9, 333], [4.25, 435, ease.out], [4.65, 338, ease.io], [6.0, 338], [6.25, 215, ease.io], [6.42, 0, ease.in]]);
  const col = key(t, [[4.25, GREY_D], [4.75, GREY_L]]);
  const sq = key(t, [[2.45, 0.7], [3.0, 1, ease.out]]);       // starts as a tilted disc, rotates face-on
  at(CX, CY, 0, 1, () => {
    ctx.scale(1, sq);
    if (R > 0) circle(0, 0, R, rgb(col));
    // rings (dark phase)
    const ringA = seg(t, 2.6, 3.0) * (1 - seg(t, 4.3, 4.6));
    if (ringA > 0) {
      ctx.globalAlpha = ringA;
      circle(0, 0, R * 0.84, null, 'rgba(255,255,255,0.9)', 2.5);
      circle(0, 0, R * 0.30, null, 'rgba(255,255,255,0.9)', 2.5);
      const tick = seg(t, 3.9, 4.2);
      for (let k = 0; k < 4; k++) {
        const a = Math.PI / 4 + k * Math.PI / 2;
        if (tick > 0) line(Math.cos(a) * R * 0.86, Math.sin(a) * R * 0.86, Math.cos(a) * R * lerp(0.86, 1.0, tick), Math.sin(a) * R * lerp(0.86, 1.0, tick), 'rgba(255,255,255,0.9)', 2.5);
      }
      ctx.globalAlpha = 1;
    }
  });
  // orbiting white balls that settle into the centre button
  const orb = seg(t, 1.9, 3.8);
  if (orb > 0 && t < 4.0) {
    for (let k = 0; k < 3; k++) {
      const a = -1.4 + k * 2.1 + ease.out(orb) * 5.2 + k * 0.3;
      const rr = lerp(190 + k * 40, 0, ease.io(seg(t, 3.0 + k * 0.15, 3.9)));
      const br = [18, 60, 34][k] * (k === 1 ? key(t, [[2.6, 0.3], [3.2, 1], [3.8, 0.3]]) : 1);
      circle(CX + Math.cos(a) * rr, CY + Math.sin(a) * rr * sq, br, '#fff');
    }
  }
  if (t > 3.75 && t < 4.4) circle(CX, CY, key(t, [[3.75, 20], [4.4, 18]]), '#fff');
  // centre button grows; light rays burst
  const btn = key(t, [[4.3, 18], [4.85, 120, ease.back], [6.0, 120], [6.3, 140, ease.io]]);
  if (t >= 4.3) circle(CX, CY, btn, '#fff');
  const ray = seg(t, 4.55, 5.1);
  if (ray > 0 && ray < 1) for (let k = 0; k < 4; k++) {
    const a = Math.PI / 4 + k * Math.PI / 2, d0 = lerp(320, 560, ease.out(ray)), d1 = d0 + 90 * (1 - ray);
    line(CX + Math.cos(a) * d0, CY + Math.sin(a) * d0, CX + Math.cos(a) * d1, CY + Math.sin(a) * d1, `rgba(255,255,255,${1 - ray})`, 2);
  }
  // click-wheel labels
  const lab = seg(t, 4.85, 5.3) * (1 - seg(t, 6.0, 6.2));
  if (lab > 0) {
    ctx.globalAlpha = lab;
    text('MENU', CX, CY - R * 0.79, 42, '#fff', 700, 1.5);
    const g = '#fff', yy = CY, xs = R * 0.79;
    // ⏮ ⏭ ▶❚❚ as drawn glyphs
    const tri = (x, y, dir, s) => { ctx.beginPath(); ctx.moveTo(x - dir * s, y - s); ctx.lineTo(x + dir * s, y); ctx.lineTo(x - dir * s, y + s); ctx.closePath(); ctx.fillStyle = g; ctx.fill(); };
    tri(CX - xs + 10, yy, -1, 13); tri(CX - xs + 30, yy, -1, 13); ctx.fillRect(CX - xs - 13, yy - 13, 5, 26);
    tri(CX + xs - 30, yy, 1, 13); tri(CX + xs - 10, yy, 1, 13); ctx.fillRect(CX + xs + 8, yy - 13, 5, 26);
    tri(CX - 16, CY + R * 0.79, 1, 13); ctx.fillRect(CX + 6, CY + R * 0.79 - 13, 6, 26); ctx.fillRect(CX + 17, CY + R * 0.79 - 13, 6, 26);
    ctx.globalAlpha = 1;
  }
});

// ---------------------------------------------------------------- 2. home button -> Touch ID (6.2 – 10.1)
function blob(x, y, r, wob, ph, fill) {
  ctx.beginPath();
  for (let i = 0; i <= 80; i++) {
    const a = i / 80 * TAU, rr = r * (1 + wob * (0.12 * Math.sin(3 * a + ph) + 0.08 * Math.sin(5 * a - ph * 1.3)));
    const px = x + Math.cos(a) * rr, py = y + Math.sin(a) * rr;
    i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
  }
  ctx.fillStyle = fill; ctx.fill();
}
scene(6.3, 8.0, t => {
  // white button squishes, inverts to black, becomes the iPhone home button
  const r = key(t, [[6.3, 140], [6.75, 72, ease.out], [7.35, 72], [7.75, 70]]);
  const c = key(t, [[6.35, WHITE], [6.7, INK]]);
  const wob = Math.sin(seg(t, 6.3, 6.8) * Math.PI) * 1.0;
  const fillA = 1 - seg(t, 7.35, 7.75);
  ctx.globalAlpha = fillA;
  blob(CX, CY, r, wob, t * 9, rgb(c));
  const sqA = seg(t, 6.65, 6.85) * (1 - seg(t, 7.05, 7.2));
  if (sqA > 0) { ctx.globalAlpha = sqA * fillA; rrect(CX, CY, 44, 44, 11, null, 'rgba(255,255,255,0.75)', 2.5); }
  ctx.globalAlpha = 1;
  // a magenta ring traces around the button (the Touch ID sensor ring)
  const ring = seg(t, 7.0, 7.45);
  if (ring > 0) trimmed(arcPts(CX, CY, r + 1, r + 1, -Math.PI / 2, -Math.PI / 2 + TAU, 90), 0, ease.io(ring), rgba(PINK, 1 - seg(t, 7.7, 7.95)), 5);
  if (ring > 0.2 && fillA > 0) { ctx.globalAlpha = fillA; trimmed(arcPts(CX, CY, r * 0.55, r * 0.55, 0.3, 0.3 + ease.io(ring) * 4.6, 60), 0, 1, 'rgba(255,255,255,0.8)', 2.5); ctx.globalAlpha = 1; }
});

// fingerprint: concentric, gapped, slightly tall arcs
const FP = (() => {
  const arcs = [];
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let k = 1; k <= 12; k++) {
    const r = 10 + k * 14.5;
    let a = Math.PI * 0.55 + rnd() * 0.5;
    const end = a + TAU - 0.5 - (k > 9 ? 1.2 + 0.35 * (k - 9) : 0);
    while (a < end) {                       // each ridge is broken into 1-3 strokes
      const len = Math.min(end - a, 1.4 + rnd() * 3.2);
      arcs.push({ r, start: a, end: a + len, ox: 3 * Math.sin(k), oy: k * 1.4, k });
      a += len + 0.22 + rnd() * 0.25;
    }
  }
  return arcs;
})();
function fingerprint(prog, s, col, breakU = 0) {
  at(CX, CY, 0, s, () => {
    FP.forEach((a, i) => {
      const spin = breakU * (i % 2 ? 1 : -1) * (1.0 + a.k * 0.12);
      const pts = arcPts(a.ox, a.oy - 8, a.r, a.r * 1.13, a.start + spin, a.end + spin, 40);
      const p0 = breakU * 0.5, p1 = clamp(prog * 1.3 - a.k * 0.025) * (1 - breakU * 0.8);
      trimmed(pts, p0, Math.max(p0, p1), rgb(col), 7);
    });
  });
}
scene(7.6, 9.9, t => {
  const prog = ease.io(seg(t, 7.65, 8.35));
  const s = key(t, [[7.6, 0.85], [8.4, 0.95, ease.out], [9.2, 1.1, ease.io], [9.85, 0.9]]);
  const br = ease.io(seg(t, 9.35, 9.85));
  const col = key(t, [[9.4, PINK], [9.75, BLUE]]);
  ctx.globalAlpha = 1 - seg(t, 9.7, 9.9);
  fingerprint(prog, s, col, br);
  ctx.globalAlpha = 1;
});

// ---------------------------------------------------------------- 3. Face ID -> check (10.0 – 12.5)
function faceId(u, s, a = 1, feat = 1) {
  at(CX, CY, 0, s, () => {
    ctx.globalAlpha = a;
    const c = rgb(BLUE), lw = 8, h = 135, k = 48, r = 26;
    for (let q = 0; q < 4; q++) {
      const sx = q % 2 ? 1 : -1, sy = q < 2 ? -1 : 1;
      let a0 = sx > 0 ? 0 : Math.PI, a1 = sy > 0 ? Math.PI / 2 : -Math.PI / 2;
      if (a1 - a0 > Math.PI) a1 -= TAU; if (a0 - a1 > Math.PI) a1 += TAU;
      const pts = [[sx * h, sy * (h - k)], ...arcPts(sx * (h - r), sy * (h - r), r, r, a0, a1, 14), [sx * (h - k), sy * h]];
      trimmed(pts, 0, ease.io(clamp(u * 1.3 - q * 0.08)), c, lw);
    }
    const f = ease.io(seg(u, 0.35, 1)) * feat;
    trimmed([[-40, -44], [-40, -18]], 0, f, c, lw);
    trimmed([[40, -44], [40, -18]], 0, f, c, lw);
    trimmed([[5, -44], [5, 10], [-9, 10]], 0, f, c, lw);
    trimmed(arcPts(0, 2, 46, 38, 0.33 * Math.PI, 0.67 * Math.PI, 30).reverse(), 0, f, c, lw);
    ctx.globalAlpha = 1;
  });
}
scene(9.75, 11.1, t => {
  const u = seg(t, 9.8, 10.1);
  const out = ease.io(seg(t, 10.45, 10.65));
  faceId(u, lerp(1, 0.6, out), 1 - out, 1 - seg(t, 10.22, 10.38));
  // a glowing ring tumbles in 3D, then settles face-on as the check circle
  const sc = seg(t, 10.5, 11.0);
  if (sc > 0 && sc < 1) {   // two interlocked rings tumbling (a gyroscope) that resolve into one circle
    const e = ease.io(sc);
    ctx.save(); ctx.translate(CX, CY); ctx.rotate(lerp(-0.5, 0, e));
    ctx.shadowColor = 'rgba(90,220,255,0.5)'; ctx.shadowBlur = 30 * (1 - e);
    ctx.strokeStyle = rgb(BLUE); ctx.lineWidth = 7;
    const R = lerp(95, 150, e);
    ctx.beginPath(); ctx.ellipse(0, 0, R * lerp(0.55, 1, e), R, 0, 0, TAU); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0, 0, R, R * lerp(0.4, 1, e), lerp(0.4, 0, e), 0, TAU); ctx.stroke();
    ctx.restore();
  }
});
scene(10.98, 12.45, t => {
  const r = 150;
  trimmed(arcPts(CX, CY, r, r, -Math.PI * 0.75, -Math.PI * 0.75 + TAU, 120), 0, 1, rgb(BLUE), 7);
  const ck = ease.out(seg(t, 11.05, 11.35)) * (1 - seg(t, 11.85, 12.05));
  if (ck > 0) trimmed([[CX - 52, CY + 2], [CX - 15, CY + 40], [CX + 55, CY - 34]], 0, ck, rgb(BLUE), 8);
});

// ---------------------------------------------------------------- 4. toggles (12.3 – 14.3)
scene(12.3, 14.4, t => {
  // the check circle opens into two brackets around a toggle; the toggle splits into a white and a black pill
  const grow = ease.out(seg(t, 12.3, 12.6));
  const ph = lerp(20, 112, grow), pw = lerp(30, 250, grow);
  const split = ease.io(seg(t, 12.85, 13.25));
  const sp = lerp(pw / 2 - 1, 235, split);
  const orbit = ease.io(seg(t, 13.5, 14.4));
  const ang = orbit * 2.4, rad = sp + orbit * 90;
  const pos = s => [CX + s * Math.cos(ang) * rad, CY + s * Math.sin(ang) * rad];
  const [wx, wy] = pos(-1), [bx, by] = pos(1);
  ctx.globalAlpha = 1 - seg(t, 14.15, 14.4);
  const w = lerp(pw, 215, split), h = lerp(ph, 100, split);
  softShadow(18, 6, 0.06);
  at(wx, wy, ang, 1, () => rrect(0, 0, w, h, h / 2, '#fbfbfc'));
  at(bx, by, ang, 1, () => rrect(0, 0, w, h, h / 2, rgb(INK)));
  noShadow();
  const brk = 1 - seg(t, 12.75, 13.0);
  if (brk > 0) {
    ctx.globalAlpha = brk;
    const g = lerp(0.0, 0.28, ease.io(seg(t, 12.3, 12.55)));
    trimmed(arcPts(CX, CY, 150, 150, Math.PI * (0.5 + g), Math.PI * (1.5 - g), 60), 0, 1, rgb(BLUE), 7);
    trimmed(arcPts(CX, CY, 150, 150, Math.PI * (-0.5 + g), Math.PI * (0.5 - g), 60), 0, 1, rgb(BLUE), 7);
    ctx.globalAlpha = 1;
  }
  const dots = seg(t, 13.2, 13.4);
  if (dots > 0) { at(wx, wy, ang, 1, () => circle(55, 0, 4 * dots, '#2a2a2c')); at(bx, by, ang, 1, () => circle(-55, 0, 4 * dots, '#e8e8ea')); }
  if (orbit > 0.2) { ctx.globalAlpha = 0.5 * Math.sin(orbit * Math.PI); circle(CX, CY, 330, null, 'rgba(120,120,125,0.5)', 1.5); ctx.globalAlpha = 1; }
});

// ---------------------------------------------------------------- 5. iMac G3 flavors -> iMac G4 -> strokes (13.9 – 19.9)
const FLAV = ['#f36f21', '#62ab3f', '#d6195b', '#2f80d8', '#7b4cba'].map(hex);
function cup(col, a, s, white) {
  // a gumdrop iMac seen from above-ish: tapered body + lighter opening ellipse + logo dot
  at(0, 0, a, s, () => {
    const c = white ? WHITE : col, light = white ? [235, 235, 238] : mix(col, WHITE, 0.45);
    ctx.beginPath();
    ctx.moveTo(-56, -40); ctx.quadraticCurveTo(0, -62, 56, -40);
    ctx.lineTo(40, 50); ctx.quadraticCurveTo(0, 66, -40, 50); ctx.closePath();
    ctx.fillStyle = rgb(c); ctx.fill();
    if (!white) {
      ctx.beginPath(); ctx.ellipse(0, 46, 40, 14, 0, 0, TAU); ctx.fillStyle = rgb(light); ctx.fill();
      circle(0, 2, 13, 'rgba(255,255,255,0.9)'); line(-6, 8, 6, -4, rgb(col), 4);
    }
  });
}
scene(13.9, 16.25, t => {
  const g = ease.back(seg(t, 13.9, 14.45));
  const spin = ease.out(seg(t, 13.9, 15.7)) * 2.2 + 0.2;
  const wh = seg(t, 15.55, 15.8);
  const R = key(t, [[13.9, 80], [14.4, 205, ease.out], [15.2, 140, ease.io], [15.6, 140], [16.2, 330]]);
  FLAV.forEach((c, k) => {
    const a = spin + k * TAU / 5;
    at(CX + Math.cos(a) * R, CY + Math.sin(a) * R, 0, 1, () => {
      ctx.globalAlpha = 1 - seg(t, 15.9, 16.2);
      if (wh < 0.5) cup(c, a + Math.PI / 2 + 0.5, 1.45 * g, false);
      else at(0, 0, a + Math.PI / 2, 1, () => { ctx.beginPath(); ctx.arc(0, 0, 66, 0, Math.PI); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill(); });
    });
  });
});
function g4(a, s, dome, arm, screen) {
  at(0, 0, a, s, () => {
    if (dome > 0) { ctx.beginPath(); ctx.arc(0, 0, 66 * dome, 0, Math.PI); ctx.closePath(); ctx.fillStyle = '#fff'; ctx.fill(); ctx.strokeStyle = 'rgba(0,0,0,0.05)'; ctx.lineWidth = 1; ctx.stroke(); }
    if (arm > 0) { line(0, -4, 0, -4 - 95 * arm, '#b4b3b7', 10); }
    if (screen > 0) { line(-62 * screen, -104, 62 * screen, -112, '#fff', 9); }
  });
}
scene(15.9, 18.3, t => {
  const spin = 2.0 + ease.io(seg(t, 15.9, 18.3)) * 1.9;
  const R = key(t, [[15.9, 330], [16.6, 380, ease.out], [18.2, 330]]);
  const dome = 1 - ease.in(seg(t, 17.2, 17.6));
  const arm = ease.out(seg(t, 15.85, 16.3)) * (1 - seg(t, 17.6, 17.9));
  const scr = ease.out(seg(t, 16.25, 16.65));
  const dark = seg(t, 17.3, 17.7);
  for (let k = 0; k < 5; k++) {
    const a = spin + k * TAU / 5;
    at(CX + Math.cos(a) * R, CY + Math.sin(a) * R, 0, 1, () => {
      g4(a + Math.PI / 2 + 0.6 * Math.sin(t * 2 + k), 1, dome, arm, scr * (1 - dark));
      if (dark > 0) at(0, 0, a + Math.PI / 2, 1, () => {   // screens turn to black 'V' strokes
        const open = lerp(0.35, 0.1, seg(t, 17.6, 18.3));
        line(0, 0, Math.cos(-Math.PI / 2 - open) * 170 * dark, Math.sin(-Math.PI / 2 - open) * 170 * dark, '#1d1d1f', 7);
        line(0, 0, Math.cos(-Math.PI / 2 + open) * 120 * dark, Math.sin(-Math.PI / 2 + open) * 120 * dark, 'rgba(60,60,64,0.7)', 2);
      });
    });
  }
});
scene(18.3, 20.05, t => {
  // five black dashes spin inward and collapse to the centre
  const spin = 3.9 + ease.io(seg(t, 18.3, 19.7)) * 2.4;
  const R = key(t, [[18.3, 330], [19.25, 300], [19.65, 0, ease.in]]);
  const L = key(t, [[18.3, 170], [19.25, 150], [19.65, 10]]);
  for (let k = 0; k < 5; k++) {
    const a = spin + k * TAU / 5, x = CX + Math.cos(a) * R, y = CY + Math.sin(a) * R, d = a + Math.PI / 2 + 0.35;
    line(x - Math.cos(d) * L / 2, y - Math.sin(d) * L / 2, x + Math.cos(d) * L / 2, y + Math.sin(d) * L / 2, '#1d1d1f', 6);
  }
  const c = ease.back(seg(t, 19.55, 19.95));
  if (c > 0) circle(CX, CY, 220 * c, '#b7b6ba');
});

// ---------------------------------------------------------------- 6. Mac Pro (19.9 – 22.9)
function macProHoles(scale, alpha) {
  // body 250x330 at scale 1, centred; hole lattice r=4.6, pitch 13, offset rows
  const bw = 250, bh = 330, pitch = 27, hr = 9;
  ctx.save(); ctx.translate(CX, CY); ctx.scale(scale, scale);
  ctx.globalAlpha = alpha;
  rrect(0, 0, bw, bh, 8, '#f6f6f8');
  ctx.beginPath(); ctx.roundRect(-bw / 2, -bh / 2, bw, bh, 8); ctx.clip();
  // only draw holes visible on screen
  const vx = (W / 2) / scale + 20, vy = (H / 2) / scale + 20;
  for (let j = -Math.ceil(bh / pitch / 2); j <= Math.ceil(bh / pitch / 2); j++) {
    const y = j * pitch * 0.87; if (Math.abs(y) > vy) continue;
    for (let i = -Math.ceil(bw / pitch / 2) - 1; i <= Math.ceil(bw / pitch / 2) + 1; i++) {
      const x = i * pitch + (j % 2 ? pitch / 2 : 0); if (Math.abs(x) > vx) continue;
      ctx.beginPath(); ctx.arc(x, y, hr, 0, TAU); ctx.fillStyle = (i === 0 && j === 0) ? '#b7b6ba' : '#c4c3c8'; ctx.fill();
    }
  }
  ctx.restore();
}
function macProFrame(a, front) {
  ctx.save(); ctx.translate(CX, CY); ctx.globalAlpha = a;
  ctx.strokeStyle = '#c9c8cc'; ctx.lineWidth = 5; ctx.lineCap = 'round';
  for (const s of [-1, 1]) {
    ctx.beginPath(); ctx.moveTo(s * 110, -165); ctx.lineTo(s * 110, -185); ctx.quadraticCurveTo(s * 110, -198, s * 97, -198); ctx.lineTo(s * 85, -198); ctx.quadraticCurveTo(s * 72, -198, s * 72, -185); ctx.lineTo(s * 72, -165); ctx.stroke();
    line(s * 92, 165, s * 92, 180, '#c9c8cc', 5); line(s * 60, 165, s * 60, 180, '#c9c8cc', 5);
  }
  ctx.restore();
}
scene(20.05, 22.95, t => {
  // camera pull-out: the grey circle is one perforation in the Mac Pro lattice
  const scale = Math.exp(key(t, [[20.05, Math.log(220 / 9)], [20.3, Math.log(14), ease.in], [20.8, Math.log(3.4), (u) => u], [21.15, 0, ease.out]]));
  const turn = seg(t, 21.12, 21.38);        // rotate to the side panel with the Apple logo
  const sx = Math.abs(Math.cos(turn * Math.PI));
  const collapse = ease.io(seg(t, 22.55, 23.0));
  if (turn < 0.5) {
    ctx.save(); ctx.translate(CX, CY); ctx.scale(sx || 0.001, 1 - collapse); ctx.translate(-CX, -CY);
    macProHoles(scale, 1);
    macProFrame(seg(t, 20.85, 21.15), false);
    ctx.restore();
  } else {
    ctx.save(); ctx.translate(CX, CY); ctx.scale(sx * lerp(1, 2.0, collapse), lerp(1, 0.12, collapse)); ctx.translate(-CX, -CY);
    softShadow(30, 10, 0.06 * (1 - collapse));
    rrect(CX, CY, 210, 210, 9, '#f7f7f9'); noShadow();
    // orange wedge slides in from the corner as the box flattens into a bar
    const o = ease.io(seg(t, 22.45, 23.0));
    if (o > 0) { ctx.beginPath(); ctx.moveTo(CX + 105, CY + 105); ctx.lineTo(CX + 105 - 170 * o, CY + 105); ctx.lineTo(CX + 105, CY + 105 - 170 * o); ctx.closePath(); ctx.fillStyle = '#ff6a1f'; ctx.fill(); }
    ctx.globalAlpha = 1 - collapse;
    text('', CX, CY + 4, 56, '#1d1d1f', 400);
    ctx.globalAlpha = 1;
    macProFrame(1 - collapse, true);
    ctx.restore();
  }
});

// ---------------------------------------------------------------- 7. colour blades (22.7 – 26.0)
const BLADE = ['#ff6a1f', '#3cc3d8', '#59e3a6', '#7d7d82'].map(hex);
function blade(len, w, col) {
  ctx.beginPath(); ctx.moveTo(0, -w / 2); ctx.quadraticCurveTo(len * 0.6, -w * 0.9, len, 0); ctx.quadraticCurveTo(len * 0.6, w * 0.9, 0, w / 2); ctx.closePath();
  ctx.fillStyle = col; ctx.fill();
}
scene(22.95, 26.1, t => {
  // the white/orange bar fans out like a swatch book, swings into a cross, then whitens into an X
  const fan = ease.io(seg(t, 23.3, 23.95));
  const cross = ease.io(seg(t, 23.9, 24.35));
  const spin = ease.io(seg(t, 24.2, 25.7)) * 1.2;
  const toWhite = ease.io(seg(t, 25.0, 25.5));
  const L = key(t, [[22.95, 360], [23.3, 330], [24.0, 300], [25.0, 300], [25.6, 340]]);
  const piv = [lerp(CX - 160, CX, cross), CY + lerp(20, 0, cross)];
  const n = 8;
  for (let k = 0; k < n; k++) {
    const fanA = -k * 0.24 * fan;                                  // half-fan from a pivot
    const crossA = Math.floor(k / 2) * Math.PI / 2 + (k % 2 ? 0.16 : -0.16) - 0.7;   // four pairs
    let a = lerp(fanA, crossA, cross) + spin;
    const merge = ease.io(seg(t, 25.35, 25.85));                    // pairs collapse into one stick
    if (merge > 0) a = lerp(a, Math.floor(k / 2) * Math.PI / 2 - 0.7 + spin, merge);
    const col = k === 0 && t < 23.3 ? WHITE : mix(BLADE[k % 4], WHITE, toWhite);
    const off = lerp(0, 0.5, cross);
    at(piv[0], piv[1], a, 1, () => {
      const len = L * lerp(1, 1.7, cross) * (k > 0 ? Math.max(fan, cross) : 1);
      ctx.translate(-len * off, 0);
      if (len < 2) return;
      if (t < 23.3 && k === 0) { rrect(len / 2, 0, len, 22, 11, '#fbfbfc'); rrect(len * 0.75, 0, len * 0.5, 22, 11, rgb(BLADE[0])); }
      else { rrect(len * 0.25, 0, len * 0.5, 16, 8, '#fbfbfc'); ctx.save(); ctx.translate(len, 0); ctx.scale(-1, 1); blade(len * 0.62, lerp(26, 22, toWhite), rgb(col)); ctx.restore(); }
    });
  }
});

// ---------------------------------------------------------------- 8. MacBooks (25.8 – 28.7)
function macbook(len, open, dir) {
  // side profile: base bar + lid bar hinged at the centre-side end
  const th = 13;
  rrect(dir * len / 2, 0, len, th, th / 2, '#fbfbfc');
  at(0, 0, dir > 0 ? -open : Math.PI + open, 1, () => rrect(len / 2, -th, len, th * 0.8, th / 2, '#fbfbfc'));
  // ports
  ctx.fillStyle = '#2a2a2c';
  for (let i = 0; i < 2; i++) ctx.fillRect(dir * (26 + i * 16) - 5, -2, 10, 3);
}
scene(25.8, 28.75, t => {
  const g = ease.out(seg(t, 25.8, 26.6));
  const len = lerp(240, 560, g);
  const open = key(t, [[25.8, 1.2], [26.6, 0.55, ease.out], [27.2, 0.55], [27.75, 0.0, ease.io]]);
  const gap = key(t, [[25.8, 0], [26.6, 34, ease.out], [27.6, 34], [28.0, 14], [28.4, 0]]);
  const merge = ease.io(seg(t, 27.9, 28.5));
  at(CX, CY, 0, 1, () => {
    for (const s of [-1, 1]) {
      at(s * 6, -gap / 2, 0, 1, () => macbook(len, open, s));
      if (merge < 1) { ctx.globalAlpha = 1 - merge; at(s * 6, gap / 2, 0, 1, () => { ctx.scale(1, -1); macbook(len, open, s); }); ctx.globalAlpha = 1; }
    }
  });
});

// ---------------------------------------------------------------- 9. stands & stroke (28.5 – 32.5)
function standGlyph(u, col) {
  // laptop-on-stand profile: long screen diagonal, double keyboard line, small hinge triangle
  trimmed([[-150, 0], [150, 0]], 0.5 - 0.5 * u, 0.5 + 0.5 * u, col, 5);
  trimmed([[-150, 10], [120, 10]], 0.5 - 0.5 * u, 0.5 + 0.5 * u, col, 3);
  trimmed([[150, 0], [270, -230]], 0, u, col, 6);
  trimmed([[205, -105], [235, -20], [175, 0]], 0, u, col, 3);
}
scene(28.5, 31.6, t => {
  const u = ease.io(seg(t, 28.55, 29.3));
  const rot = key(t, [[28.5, 0.0], [29.3, -0.08], [30.8, -0.5, ease.io], [31.5, -1.0]]);
  const s = key(t, [[28.5, 1.0], [29.3, 1.2], [30.9, 1.3], [31.5, 0.45, ease.in]]);
  const col = '#3a3a3e';
  at(CX, CY, rot, s, () => {
    standGlyph(u, col);
    ctx.scale(-1, -1); standGlyph(u, col);
  });
});
scene(31.2, 32.95, t => {
  // two slanted bars rotate, lengthen and turn into one white line that sweeps off
  const u = ease.io(seg(t, 31.2, 32.2));
  const a = lerp(-1.25, -0.95, u);
  const L = key(t, [[31.2, 90], [31.8, 220], [32.2, 520]]);
  const off = key(t, [[31.2, 14], [31.9, 6], [32.2, 0]]);
  const white = seg(t, 31.6, 32.0);
  const exit = ease.in(seg(t, 32.45, 32.95));
  at(CX, CY, a, 1, () => {
    const c = rgb(mix(hex('#3a3a3e'), WHITE, white));
    line(-L / 2 + exit * 900, -off, L / 2 + exit * 1400, -off, c, 7);
    if (off > 0.5) line(-L / 2, off, L / 2, off, c, 7);
  });
});

// ---------------------------------------------------------------- 10. EarPods -> AirPods -> case (32.6 – 37.0)
const CABLE = bezierPts([[1180, 230], [990, 300], [960, 420], [1040, 520], [990, 640], [905, 590], [930, 470], [1050, 470], [1070, 640], [990, 760], [880, 830]], 400);
function bud(x, y, a, s = 1) {
  at(x, y, a, s * 2.4, () => {
    softShadow(10, 3, 0.08);
    ctx.beginPath(); ctx.ellipse(0, 0, 17, 13, 0, 0, TAU); ctx.fillStyle = '#fdfdfd'; ctx.fill(); noShadow();
    rrect(10, 10, 9, 36, 4.5, '#f8f8fa');
    circle(-5, -2, 2.4, '#3a3a3c');
  });
}
scene(32.5, 35.2, t => {
  const draw = ease.io(seg(t, 32.55, 33.6));
  const retract = ease.io(seg(t, 34.25, 34.85));
  trimmed(CABLE, retract * 0.5, Math.max(retract * 0.5, draw - retract * 0.5), '#ffffff', 4.5);
  const budA = seg(t, 33.4, 33.65);
  if (budA > 0) {
    const n = CABLE.length - 1;
    const pa = CABLE[Math.floor(lerp(0, n * 0.5, retract))], pb = CABLE[Math.floor(lerp(n, n * 0.5, retract))];
    const j = ease.io(seg(t, 34.6, 35.1));
    const tgtL = [CX - 50, CY - 250], tgtR = [CX + 50, CY - 250];
    bud(lerp(pa[0], tgtL[0], j), lerp(pa[1], tgtL[1], j), lerp(0.5, -0.3, j), budA);
    bud(lerp(pb[0], tgtR[0], j), lerp(pb[1], tgtR[1], j), lerp(-0.8, 0.3, j), budA);
  }
});
scene(35.05, 37.0, t => {
  // AirPods hover, the charging case rises beneath, pods drop in, lid closes; the case then turns red
  const caseIn = ease.out(seg(t, 35.05, 35.45));
  const drop = ease.io(seg(t, 35.45, 35.95));
  const lid = ease.io(seg(t, 36.0, 36.35));
  const toPhone = ease.io(seg(t, 36.55, 37.0));
  const cy = lerp(CY + 260, CY + 10, caseIn);
  const podY = lerp(CY - 250, CY - 120, drop);
  const podClip = drop;
  if (lid < 1) {
    for (const s of [-1, 1]) {
      ctx.save();
      if (podClip > 0.5) { ctx.beginPath(); ctx.rect(0, 0, W, cy - 128); ctx.clip(); }
      bud(CX + s * 50, podY, s * 0.3 * (1 - drop), 1);
      ctx.restore();
    }
  }
  const w = lerp(270, 150, toPhone), h = lerp(315, 300, toPhone), r = lerp(72, 26, toPhone);
  const col = mix([252, 252, 253], hex('#f4463f'), toPhone);
  softShadow(24, 10, 0.07);
  rrect(CX, cy, w, h, r, rgb(col)); noShadow();
  if (toPhone < 0.5) {
    ctx.globalAlpha = 1 - toPhone * 2;
    line(CX - w / 2 + 4, cy - h / 2 + 95 * lid + 2, CX + w / 2 - 4, cy - h / 2 + 95 * lid + 2, 'rgba(0,0,0,0.08)', 1.5);
    circle(CX, cy - h / 2 + 112, 3.5, `rgba(255,170,60,${seg(t, 36.3, 36.4)})`);
    ctx.globalAlpha = 1;
  }
  if (toPhone > 0.5) {  // XR camera bump appears
    const a = (toPhone - 0.5) * 2;
    rrect(CX - w / 2 + 24, cy - h / 2 + 24, 30 * a, 30 * a, 9, 'rgba(0,0,0,0.12)');
    circle(CX - w / 2 + 24, cy - h / 2 + 24, 9 * a, '#1d1d1f');
  }
});

// ---------------------------------------------------------------- 11. iPhone XR colours (84.0 – 87.8)
const XR = ['#f4463f', '#f2a487', '#fbfbfd', '#1f1f22', '#36b7e8', '#8c0e14', '#f9d23c', '#1f1f22', '#f4f4f6'].map(hex);
function xr(col, s, a = 0) {
  at(0, 0, a, s, () => {
    softShadow(16, 6, 0.08);
    rrect(0, 0, 150, 300, 26, rgb(col)); noShadow();
    const g = ctx.createLinearGradient(-75, -150, 75, 150);
    g.addColorStop(0, 'rgba(255,255,255,0.10)'); g.addColorStop(0.5, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(0,0,0,0.04)');
    rrect(0, 0, 150, 300, 26, g);
    rrect(-51, -126, 30, 30, 9, 'rgba(0,0,0,0.10)'); circle(-51, -126, 9, '#1d1d1f'); circle(-51, -103, 3, 'rgba(255,240,200,0.9)');
  });
}
scene(84.0, 86.0, t => {
  // the red XR deals out the other colours, they wheel round into a ring, then thin into sticks
  const s = key(t, [[84.0, 1.0], [84.5, 0.9, ease.io]]);
  const mv = ease.io(seg(t, 84.0, 84.5));
  const deal = ease.io(seg(t, 84.55, 85.15));
  const ring = ease.io(seg(t, 85.2, 85.65));
  const thin = ease.io(seg(t, 85.55, 85.98));
  const spin = ease.out(seg(t, 85.0, 86.3)) * 0.8;
  for (let k = XR.length - 1; k >= 0; k--) {
    if (k > 0 && deal <= 0 && mv < 1) continue;
    const ringA = -Math.PI / 2 + k * TAU / XR.length + spin;  // evenly around the centre
    // fanned stack at the upper right, hinged at each phone's lower-left corner
    const fx = CX + 200 * mv, fy = CY - 230 * mv, fr = k * 0.15 * deal;
    const pvx = fx - 140, pvy = fy + 360;                     // fan pivot below-left of the stack
    const hx = pvx + (fx - pvx) * Math.cos(fr) - (fy - pvy) * Math.sin(fr);
    const hy = pvy + (fx - pvx) * Math.sin(fr) + (fy - pvy) * Math.cos(fr);
    const rx = CX + Math.cos(ringA) * 330, ry = CY + Math.sin(ringA) * 330;
    const x = lerp(hx, rx, ring), y = lerp(hy, ry, ring);
    const rot = lerp(fr, ringA - Math.PI / 2 + 0.45, ring);
    at(x, y, rot, 1, () => {
      ctx.scale(lerp(1, 0.09, thin), lerp(1, 0.42, thin)); xr(XR[k], s);
    });
  }
});
scene(86.0, 88.0, t => {
  // radial sticks in the XR colours, slowly turning and dissolving
  const u = seg(t, 85.9, 88.0);
  const spin = 0.8 + ease.out(u) * 0.7;
  const fade = 1 - seg(t, 87.2, 87.85);
  const R = key(t, [[85.9, 330], [87.8, 350]]);
  const n = 9;
  for (let k = 0; k < n; k++) {
    const a = spin + k * TAU / n - Math.PI / 2;
    const x = CX + Math.cos(a) * R, y = CY + Math.sin(a) * R, d = a + 0.45;
    ctx.globalAlpha = fade;
    const L = 175 * (1 - 0.4 * seg(t, 87.2, 87.85));
    line(x - Math.cos(d) * L / 2, y - Math.sin(d) * L / 2, x + Math.cos(d) * L / 2, y + Math.sin(d) * L / 2, rgb(XR[k]), 9);
  }
  ctx.globalAlpha = 1;
});

// ---------------------------------------------------------------- 12. words + logo (87.6 – 94.8)
scene(87.6, 94.8, t => {
  const a1 = seg(t, 87.75, 88.25) * (1 - seg(t, 90.3, 90.5));
  const tr = key(t, [[87.75, -6], [88.6, 0, ease.out]]);
  if (a1 > 0) { ctx.globalAlpha = a1; text('Give people wonderful tools', CX, CY, 44, '#1d1d1f', 500, tr); }
  const a2 = seg(t, 90.5, 90.75) * (1 - seg(t, 93.35, 93.6));
  if (a2 > 0) { ctx.globalAlpha = a2; text('And they’ll do wonderful things', CX, CY, 44, '#1d1d1f', 500, 0); }
  const a3 = seg(t, 93.75, 94.15);
  if (a3 > 0) { ctx.globalAlpha = a3; text('', CX, CY - 6, 120, '#1d1d1f', 400); }
  ctx.globalAlpha = 1;
});

window.READY = true;
