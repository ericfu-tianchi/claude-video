// Oura Ring 5 — "Subtle. Power."  v2: every morph is locked to the score (music_alt.py, variant A).
// 96 BPM: one beat = 0.625 s, one bar = 2.5 s. Kicks run on every beat 5.0–50.0 except the builds
// (20.0–22.5, 37.5–40.0) and the breakdown (35.0–37.5). Impacts land at 22.5, 40.0 and 50.0.
window.DURATION = 60;
const BEAT = 0.625, BAR = 2.5;
const R = 200, BW = 36;
const INK = [29, 29, 31], GREY = [134, 134, 139], TRACK = [214, 213, 218];
const C = {
  deep: [35, 48, 94], light: [79, 111, 176], rem: [143, 176, 227], awake: [178, 172, 204],
  heart: [229, 72, 77], warm: [242, 146, 58], cool: [80, 140, 220],
  ready: [34, 170, 155], sleep: [91, 108, 240], act: [242, 163, 58],
  rose: [229, 103, 127], lilac: [167, 139, 250], dot: [200, 199, 205], water: [70, 140, 225], batt: [52, 199, 89],
};
const X0 = 560, X1 = 1360;
const LUBS = [0.15, 1.4, 2.65, 3.9];                  // heartbeat intro in the score (lub, dub = +0.2)

// ---------------------------------------------------------------- rhythm helpers
const kickOn = t => (t >= 5.0 && t < 50.0) && !(t >= 20.0 && t < 22.5) && !(t >= 35.0 && t < 40.0);
function beatPulse(t, k = 9) {        // 1 on each kick, decaying
  if (!kickOn(t)) return 0;
  const b = Math.floor(t / BEAT) * BEAT;
  return Math.exp(-(t - b) * k);
}
function heartPulse(t) {
  let v = 0;
  for (const L of LUBS) {
    if (t >= L) v += Math.exp(-(t - L) * 10);
    if (t >= L + 0.2) v += 0.55 * Math.exp(-(t - L - 0.2) * 12);
  }
  return v;
}
// step-reveal: jumps to the next value on each beat, with a snappy settle
function stepped(t, t0, n, dur = 0.22) {
  const k = Math.floor((t - t0) / BEAT);
  if (t < t0) return 0;
  if (k >= n) return 1;
  const u = ease.expo(clamp((t - t0 - k * BEAT) / dur));
  return (k + u) / n;
}
const land = (t, a, d = 0.35) => ease.expo(seg(t, a, a + d));            // hits exactly on a beat
const leave = (t, a, d = 0.3) => ease.in(seg(t, a, a + d));

function label(t, a, b, s, eyebrow = '', ecol = GREY, y = 868) {
  const u = Math.min(land(t, a, 0.5), 1 - ease.in(seg(t, b - 0.3, b)));
  if (u <= 0) return;
  ctx.globalAlpha = u;
  if (eyebrow) text(eyebrow.toUpperCase(), CX, y - 48 + (1 - u) * 8, 17, rgb(ecol), 600, 3.4);
  text(s, CX, y + (1 - u) * 12, 34, rgb(INK), 400, -0.4);
  ctx.globalAlpha = 1;
}

// ---------------------------------------------------------------- materials
function metal(cx, cy, rad, tone = 'silver', rot = 0) {
  const g = ctx.createConicGradient(rot, cx, cy);
  const T = {
    silver: ['#f4f4f6', '#a9aab0', '#e6e7ea', '#8e9097', '#f7f7f8', '#b4b5bb', '#f4f4f6'],
    black: ['#5a5a60', '#1c1c1f', '#3f3f45', '#121214', '#55555b', '#222226', '#5a5a60'],
    gold: ['#f6e3b8', '#c7a46a', '#ecd3a0', '#a98448', '#f8e8c4', '#c9a874', '#f6e3b8'],
    rose: ['#f3d2c6', '#c48e80', '#e9bfb1', '#a8705f', '#f6dacf', '#c7968a', '#f3d2c6'],
    stealth: ['#6c6c70', '#38383c', '#58585d', '#2a2a2e', '#646469', '#3c3c40', '#6c6c70'],
    brushed: ['#e1e2e5', '#b9babf', '#d6d7db', '#a7a8ae', '#e3e4e7', '#bdbec3', '#e1e2e5'],
  }[tone];
  T.forEach((c, i) => g.addColorStop(i / (T.length - 1), c));
  return g;
}
// The ring itself is a Blender render (ring3d/ring_sprites.py): one transparent sprite per degree of turn.
const SPR = {}, SPR_RANGE = { silver: 90, black: 35, gold: 35, rose: 35, stealth: 35, brushed: 35 };
const SPR_SIZE = { silver: 600 }, SPR_R = 0.45;     // outer radius = 45% of the sprite width
function loadSprites() {
  const jobs = [];
  for (const [tone, amax] of Object.entries(SPR_RANGE)) {
    SPR[tone] = [];
    for (let d = -amax; d <= amax; d++) {
      const img = new Image(); img.src = `sprites/${tone}_${String(d + 90).padStart(3, '0')}.png`;
      SPR[tone][d + amax] = img; jobs.push(img.decode());
    }
  }
  return Promise.all(jobs);
}
function ring(cx, cy, r, bw, theta, tone = 'silver', alpha = 1, shine = 0, shadow = 1) {
  if (r < 1 || alpha <= 0) return;
  const amax = SPR_RANGE[tone];
  const df = Math.max(-amax, Math.min(amax, theta * 180 / Math.PI));
  const d0 = Math.floor(df), d1 = Math.min(amax, d0 + 1), fr = df - d0;
  const size = r / SPR_R;
  ctx.save(); ctx.globalAlpha *= alpha;
  if (shadow) {   // soft contact shadow under the ring
    const c = Math.max(0.3, Math.abs(Math.cos(theta)));
    const g = ctx.createRadialGradient(cx, cy + r * 1.12, 0, cx, cy + r * 1.12, r * 0.9 * c + r * 0.25);
    g.addColorStop(0, 'rgba(0,0,0,0.16)'); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.save(); ctx.translate(cx, cy + r * 1.12); ctx.scale(1, 0.16); ctx.translate(-cx, -(cy + r * 1.12));
    ctx.fillStyle = g; ctx.fillRect(cx - r * 1.6, cy + r * 1.12 - r * 1.6, r * 3.2, r * 3.2); ctx.restore();
  }
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  const A = ctx.globalAlpha;
  ctx.drawImage(SPR[tone][d0 + amax], cx - size / 2, cy - size / 2, size, size);
  if (fr > 0.01 && d1 !== d0) { ctx.globalAlpha = A * fr; ctx.drawImage(SPR[tone][d1 + amax], cx - size / 2, cy - size / 2, size, size); }
  ctx.restore();
}
// line <-> circle as a curl: the line bends into an ever tighter arc until it closes (no self-crossing)
function lineToCircle(u, rad, y = CY, n = 240, x0 = X0, x1 = X1) {
  const L0 = x1 - x0, mxl = (x0 + x1) / 2;
  const phi = Math.max(1e-4, u * TAU);
  const L = lerp(L0, TAU * rad, u);
  const r = L / phi;
  const ymid = lerp(y, CY + rad, u), cxm = lerp(mxl, CX, u);
  const p = [];
  for (let i = 0; i <= n; i++) {
    const a = Math.PI / 2 - phi / 2 + phi * (i / n);
    p.push([cxm + Math.cos(a) * r, ymid - r + Math.sin(a) * r]);
  }
  return p;
}

// ---------------------------------------------------------------- 1. the ring beats (0 – 5.0)
scene(0, 5.32, t => {
  const hp = heartPulse(t);
  const intro = ease.out(seg(t, 0, 0.5));
  const theta = key(t, [[0, 1.15], [4.375, 0.55], [5.0, 0.0, ease.expoIn]]) + 0.22 * Math.sin(t * 1.4) * (1 - seg(t, 4.0, 4.6));
  const sc = lerp(0.82, 1, ease.io(seg(t, 0, 4.4))) * (1 + 0.045 * hp);
  // pulse ripples leave the ring on each 'lub'
  for (const L of LUBS) {
    const u = seg(t, L, L + 1.1);
    if (u > 0 && u < 1) { ctx.globalAlpha = 0.5 * (1 - u) * intro; circle(CX, CY, R * sc * lerp(1.0, 1.7, ease.out(u)), null, 'rgba(150,150,158,0.9)', 2.5); ctx.globalAlpha = 1; }
  }
  const fill = land(t, 5.0, 0.28);          // first kick: the band floods into a navy disc
  if (fill <= 0) {
    at(CX, CY, 0, sc, () => ring(0, 0, R, BW, theta, 'silver', intro, t * 0.9));
  } else {
    const inner = lerp(R - BW, 0, fill);
    ctx.beginPath(); ctx.arc(CX, CY, R, 0, TAU); if (inner > 0.5) ctx.arc(CX, CY, inner, 0, TAU);
    ctx.fillStyle = rgb(mix([200, 201, 206], C.deep, Math.min(1, fill * 1.6))); ctx.fill('evenodd');
  }
  label(t, 2.65, 4.85, 'The world’s smallest smart ring.', 'Oura Ring 5');
});

// ---------------------------------------------------------------- 2. sleep (5.0 – 12.5)
const STAGES = [['awake', 1], ['light', 3], ['deep', 4], ['light', 2], ['rem', 2], ['light', 3], ['deep', 3], ['light', 2], ['rem', 3],
  ['light', 2], ['deep', 1.5], ['light', 2], ['rem', 4], ['awake', 0.6], ['light', 2], ['rem', 3], ['awake', 1]];
const LEVEL = { awake: 430, rem: 505, light: 580, deep: 655 };
const STOT = STAGES.reduce((a, s) => a + s[1], 0);
function hypno(prog, collapse, t) {
  let x = X0, prev = null;
  const bp = beatPulse(t, 11);
  for (const [st, d] of STAGES) {
    const w = (X1 - X0) * d / STOT;
    const reveal = clamp((prog * (X1 - X0) - (x - X0)) / w);
    if (prev && reveal > 0) {
      ctx.globalAlpha = 0.5 * (1 - collapse);
      line(x, lerp(LEVEL[prev], CY, collapse), x, lerp(LEVEL[st], CY, collapse), rgb(mix(C[prev], C[st], 0.5)), 3);
      ctx.globalAlpha = 1;
    }
    if (reveal > 0) {
      const y = lerp(LEVEL[st], CY, collapse), h = lerp(26, 7, collapse);
      rrect(x + w * reveal / 2, y, Math.max(1, w * reveal + 1 + 4 * collapse), h, lerp(7, 3, collapse), rgb(mix(C[st], C.heart, collapse)));
    }
    prev = st; x += w;
  }
}
scene(5.0, 13.0, t => {
  const toMoon = land(t, 5.625, 0.4);                 // beat 2: the crescent cuts in
  const fly = ease.expo(seg(t, 6.25, 6.95));          // beat 3: moon lifts to the top-left
  const mx = lerp(CX, key(t, [[6.875, X0 - 20], [11.25, X1 + 20]], ease.io), fly);
  const my = lerp(CY, key(t, [[6.875, 340], [9.0, 312], [11.25, 340]], ease.io), fly);
  const rad = lerp(R, 46, ease.io(seg(t, 5.3, 6.875)));
  // dawn arrives before waking: while still travelling right, the crescent fills out and warms into the sun
  const dawn = ease.io(seg(t, 9.4, 11.0));
  const fade = ease.io(seg(t, 11.6, 12.2));            // sun and glow leave a clean beat before the heart line
  const sx = mx, sy = my - 30 * ease.io(seg(t, 9.4, 11.25));
  const r0 = rad * lerp(1, 1.12, dawn);
  if (dawn > 0) {
    const g = ctx.createRadialGradient(sx, sy, 0, sx, sy, 650);
    g.addColorStop(0, `rgba(255,200,130,${0.18 * dawn * (1 - fade)})`); g.addColorStop(1, 'rgba(255,200,130,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  if (fade < 1) {
    // colour travels the way a dawn sky does: indigo -> violet -> rose -> amber (hue path, never through grey)
    const moonHSL = [222, 45, lerp(34, 50, seg(t, 6.875, 8.5))];
    const warm = ease.io(seg(t, 9.6, 11.0));
    const hue = lerp(moonHSL[0], 398, warm) % 360, sat = lerp(moonHSL[1], 92, warm * warm), lig = lerp(moonHSL[2], 64, warm) + 9 * Math.sin(Math.PI * warm);
    const col = `hsl(${hue}, ${sat}%, ${lig}%)`;
    const cut = lerp(lerp(2.3, 0.55, toMoon), 2.6, ease.io(seg(t, 9.4, 10.6)));   // shadow slides off
    const rr = r0 * (1 - ease.in(seg(t, 11.6, 12.2)));                               // the sun sets by shrinking, staying saturated
    if (rr > 0.5) {
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, W, H);
      ctx.arc(sx + rr * cut, sy - rr * 0.25 * (1 - dawn), rr * 0.92, 0, TAU);
      ctx.clip('evenodd');
      if (warm > 0) { ctx.shadowColor = `rgba(255,175,70,${0.4 * warm})`; ctx.shadowBlur = 34 * warm; }
      circle(sx, sy, rr, col);
      ctx.restore();
    }
  }
  const prog = stepped(t, 6.875, 7);                  // a chunk of the night lands on every kick
  const collapse = land(t, 12.5, 0.32);               // claps arrive: the night collapses into one line
  const lift = Math.sin(Math.PI * seg(t, 12.0, 12.5)) * 0;   // (kept flat: Apple-style hold before the hit)
  ctx.globalAlpha = 1 - seg(t, 12.7, 12.85);
  if (prog > 0) at(0, -lift, 0, 1, () => hypno(prog, collapse, t));
  ctx.globalAlpha = 1;
  const la = Math.min(land(t, 6.875, 0.4), 1 - seg(t, 11.9, 12.4));
  if (la > 0) {
    ctx.globalAlpha = la;
    for (const [n, y] of [['Awake', 430], ['REM', 505], ['Light', 580], ['Deep', 655]]) text(n, X0 - 30, y, 21, rgb(GREY), 500, 0, 'right');
    ctx.globalAlpha = 1;
  }
  label(t, 7.5, 12.2, 'Light, deep and REM, through the night.', 'Sleep', C.light);
});

// ---------------------------------------------------------------- 3. heart rate & HRV (12.5 – 17.5)
// A trace written by a pen at the right edge. Every kick writes one heartbeat, so the peaks ARE the beat.
const PEN_X = X1, SPEED = 230;                   // px per second the trace scrolls left
function beatShape(dt, amp) {                    // PPG-like systolic bump + dicrotic wave, dt seconds after a beat
  return amp * (Math.exp(-(((dt - 0.06) / 0.045) ** 2)) + 0.3 * Math.exp(-(((dt - 0.2) / 0.05) ** 2)));
}
function traceY(tx) {
  if (tx < 12.5) return 0;
  const b = Math.floor(tx / BEAT), dt = tx - b * BEAT;
  const calm = ease.io(seg(tx, 15.0, 17.0));
  const amp = lerp(120, 80, calm) * (1 + calm * 0.28 * Math.sin(b * 2.1));    // HRV: beat-to-beat variation
  return beatShape(dt, amp);
}
scene(12.5, 18.4, t => {
  const toTemp = ease.expo(seg(t, 17.5, 18.2));
  const pts = [];
  for (let x = X0; x <= PEN_X; x += 2.5) {
    const tx = t - (PEN_X - x) / SPEED;
    const env = Math.min(1, (x - X0) / 120);
    let y = CY - traceY(tx) * env;
    y = lerp(y, CY - tempCurve(x, t) * ease.expo(seg(t, 17.5, 18.4)), toTemp);
    pts.push([x, y]);
  }
  const col = mix(C.heart, C.warm, toTemp);
  ctx.globalAlpha = seg(t, 12.62, 12.8);
  trimmed(pts, 0, 1, rgb(col), 6);
  ctx.globalAlpha = 1;
  // the pen: glows on every beat
  const bp = beatPulse(t, 7) * (1 - toTemp);
  const py = pts[pts.length - 1][1];
  if (t > 12.6) { circle(PEN_X, py, (9 + 10 * bp) * (1 - toTemp), rgba(col, 1)); circle(PEN_X, py, (22 + 26 * bp) * (1 - toTemp), rgba(col, 0.12 * bp)); }
  label(t, 13.125, 17.3, 'Heart rate and HRV, around the clock.', 'Heart', C.heart);
});

// ---------------------------------------------------------------- 4. body temperature (17.5 – 22.5)
function tempCurve(x, t) {
  const s = (x - X0) / (X1 - X0);
  return (70 * Math.sin(s * Math.PI * 2.2 + 0.6 + t * 0.8) + 18 * Math.sin(s * 9 + t * 1.6)) * Math.sin(s * Math.PI);
}
scene(18.4, 22.5, t => {
  // build (20.0–22.5): the curve is drawn in toward the centre, faster and faster, then fires the scores
  const pinch = ease.io(seg(t, 20.65, 21.95));   // collapse early, then hold a tense dot until the drop
  const half = lerp((X1 - X0) / 2, 6, pinch);
  const amp = (1 - pinch);
  const pts = [];
  for (let i = 0; i <= 320; i++) {
    const x = lerp(CX - half, CX + half, i / 320), sx = lerp(X0, X1, i / 320);
    pts.push([x, CY - tempCurve(sx, t) * amp]);
  }
  for (const [above, col] of [[true, C.warm], [false, C.cool]]) {
    ctx.save();
    ctx.beginPath(); ctx.rect(0, above ? 0 : CY, W, above ? CY : H); ctx.clip();
    ctx.beginPath(); ctx.moveTo(pts[0][0], CY); pts.forEach(p => ctx.lineTo(p[0], p[1])); ctx.lineTo(pts[pts.length - 1][0], CY); ctx.closePath();
    const g = ctx.createLinearGradient(0, CY - 110, 0, CY + 110);
    g.addColorStop(above ? 0 : 1, rgba(col, 0.34 * amp * seg(t, 18.4, 19.0))); g.addColorStop(0.5, rgba(col, 0.02));
    ctx.fillStyle = g; ctx.fill(); ctx.restore();
  }
  const ba = Math.min(land(t, 18.75, 0.4), 1 - seg(t, 20.45, 20.85));
  if (ba > 0) {
    ctx.save(); ctx.setLineDash([6, 10]); ctx.globalAlpha = ba; line(X0, CY, X1, CY, rgb(GREY), 2, 'butt'); ctx.restore();
    ctx.globalAlpha = ba;
    text('Your baseline', X1 + 24, CY, 19, rgb(GREY), 500, 0, 'left');
    text('Warmer', X0 - 24, CY - 66, 19, rgb(C.warm), 600, 0, 'right');
    text('Cooler', X0 - 24, CY + 66, 19, rgb(C.cool), 600, 0, 'right');
    ctx.globalAlpha = 1;
  }
  if (pinch < 0.97) trimmed(pts, 0, 1, rgb(C.warm), lerp(6, 14, pinch));
  if (pinch > 0.6) circle(CX, CY, lerp(0, 20, ease.out((pinch - 0.6) / 0.4)) * lerp(1, 0.55, ease.in(seg(t, 22.0, 22.5))), rgb(C.warm));   // held, gathering, then fires on the drop
  label(t, 18.75, 20.85, 'Measured against your own baseline.', 'Temperature', C.warm);
});

// ---------------------------------------------------------------- 5. three scores (22.5 – 30.0)
const SCORES = [['Readiness', C.ready, 236, 0.88, 'How ready are you for the day?'],
  ['Sleep', C.sleep, 192, 0.84, 'How well did you sleep last night?'],
  ['Activity', C.act, 148, 0.80, 'Are you balancing activity, inactivity and rest?']];
const SC_T = [25.0, 26.25, 27.5];                   // spotlight on half-bars
scene(22.5, 30.4, t => {
  const bp = beatPulse(t, 10);
  const unwind = ease.io(seg(t, 28.75, 30.0));       // the rings spin out and lay down as the stress line
  // impact flash at 22.5
  const fl = 1 - seg(t, 22.5, 22.9);
  const spot = t < SC_T[0] ? -1 : t < SC_T[1] ? 0 : t < SC_T[2] ? 1 : t < 28.75 ? 2 : -1;
  SCORES.forEach(([name, col, rad, val], i) => {
    const pop = i === 0 ? ease.expo(seg(t, 22.5, 22.85)) : ease.back(seg(t, 22.5 + i * BEAT / 2, 22.5 + i * BEAT / 2 + 0.5));
    if (pop <= 0) return;
    let r = rad * pop, sw = Math.min(1, pop * 1.5);
    let trackCol = TRACK;
    if (i === 0) {   // grows straight out of the orange temperature dot
      const g = ease.expo(seg(t, 22.5, 22.95));
      r = lerp(11, rad, g); sw = lerp(14 / 18, 1, g);
      trackCol = mix(C.warm, TRACK, ease.io(seg(t, 22.55, 22.85)));
    }
    const fill = ease.expo(seg(t, 23.125 + i * BEAT, 23.125 + i * BEAT + 0.9)) * val;
    const dim = spot >= 0 && spot !== i ? 0.32 : 1;
    const w = 18;
    if (unwind > 0) {
      // ring -> line: each ring unrolls to a stacked horizontal stroke, then they merge into one baseline
      const yy = CY + (i - 1) * 36 * (1 - ease.io(seg(t, 29.4, 30.0)));
      const p = lineToCircle(1 - unwind, r, yy, 240);
      trimmed(p, 0, 1, rgb(mix(TRACK, [150, 150, 156], unwind)), lerp(18, 6, unwind));
      trimmed(p, 0, fill * (1 - unwind), rgba(col, dim), lerp(18, 6, unwind));
      return;
    }
    const rot = (1 - pop) * -1.2 + (t - 22.5) * 0.06 * (i % 2 ? -1 : 1);
    ctx.beginPath(); ctx.arc(CX, CY, Math.max(1, r), 0, TAU); ctx.strokeStyle = rgb(trackCol); ctx.lineWidth = 18 * sw; ctx.stroke();
    if (fill > 0) {
      ctx.beginPath(); ctx.arc(CX, CY, r, -Math.PI / 2 + rot, -Math.PI / 2 + rot + TAU * fill);
      ctx.strokeStyle = rgba(col, dim); ctx.lineWidth = w * sw; ctx.lineCap = 'round'; ctx.stroke();
    }
  });
  if (spot >= 0) {
    const a = SC_T.concat([28.75])[spot];
    const u = Math.min(land(t, a, 0.3), 1 - ease.in(seg(t, (SC_T.concat([28.75]))[spot + 1] - 0.18, (SC_T.concat([28.75]))[spot + 1])));
    ctx.globalAlpha = u;
    text(SCORES[spot][0].toUpperCase(), CX, 820 + (1 - u) * 8, 17, rgb(SCORES[spot][1]), 600, 3.4);
    text(SCORES[spot][4], CX, 868 + (1 - u) * 12, 34, rgb(INK), 400, -0.4);
    ctx.globalAlpha = 1;
  }
});

// ---------------------------------------------------------------- 6. daytime stress (30.0 – 35.0)
function stressY(x, t, settle) {
  const s = (x - X0) / (X1 - X0);
  const v = Math.sin(s * 13 + 0.4 + t * 1.3) * 0.6 + Math.sin(s * 5.3 + 1.7 - t * 0.5) * 0.5 + Math.sin(s * 23 + t * 2.5) * 0.12;
  const bias = lerp(0.15, -0.55, s) * settle;
  return CY - 92 * (v * (1 - 0.35 * settle) + bias);
}
scene(30.0, 35.4, t => {
  const amp = land(t, 30.0, 0.5) * (1 - ease.io(seg(t, 34.0, 34.7)));
  const settle = ease.io(seg(t, 31.25, 33.75));
  const toCircle = ease.in(seg(t, 34.4, 35.0));
  const bp = beatPulse(t, 9);
  if (toCircle > 0) {
    trimmed(lineToCircle(toCircle, R), 0, 1, rgb(mix([150, 150, 156], C.dot, toCircle)), 6);
    return;
  }
  const pts = [];
  for (let i = 0; i <= 240; i++) { const x = lerp(X0, X1, i / 240); pts.push([x, lerp(CY, stressY(x, t, settle), amp)]); }
  for (const [above, col] of [[true, C.warm], [false, C.ready]]) {
    ctx.save();
    ctx.beginPath(); ctx.rect(X0, above ? 0 : CY, X1 - X0, above ? CY : H); ctx.clip();
    ctx.beginPath(); ctx.moveTo(X0, CY); pts.forEach(p => ctx.lineTo(p[0], p[1])); ctx.lineTo(X1, CY); ctx.closePath();
    ctx.fillStyle = rgba(col, 0.88); ctx.fill(); ctx.restore();
  }
  const la = Math.min(land(t, 30.625, 0.4), 1 - seg(t, 33.9, 34.3));
  if (la > 0) {
    ctx.globalAlpha = la;
    text('Stressed', X1 + 24, CY - 66, 19, rgb(C.warm), 600, 0, 'left');
    text('Restored', X1 + 24, CY + 66, 19, rgb(C.ready), 600, 0, 'left');
    ctx.globalAlpha = 1;
  }
  trimmed([[X0, CY], [X1, CY]], 0, 1, rgba([150, 150, 156], 1 - amp * 0.7), 3);
  label(t, 30.625, 34.2, 'See when you’re stressed, and when you recover.', 'Daytime stress', C.ready);
});

// ---------------------------------------------------------------- 7. cycle insights (35.0 – 40.0): breakdown, then build
scene(35.0, 40.6, t => {
  const N = 28;
  const spin = (t - 35.0) * 0.12 + Math.pow(seg(t, 37.5, 39.85), 2.2) * TAU * 1.5;      // drifts in the breakdown, winds up in the build
  const gather = ease.in(seg(t, 39.5, 40.0));
  for (let i = 0; i <= N - 1; i++) {
    const a = -Math.PI / 2 + TAU * i / N + spin;
    const pop = ease.back(seg(t, 35.0 + i * 0.032, 35.4 + i * 0.032));
    let col = C.dot;
    const day = i + 1;
    if (day <= 5) col = mix(C.dot, C.rose, land(t, 36.25 + i * 0.06, 0.3));
    else if (day >= 11 && day <= 16) col = mix(C.dot, C.lilac, land(t, 36.875 + (day - 11) * 0.06, 0.3));
    const rr = lerp(R, R - BW / 2, gather);
    circle(CX + Math.cos(a) * rr, CY + Math.sin(a) * rr, lerp(3, 13, pop) * (1 - 0.55 * gather), rgb(mix(col, [180, 181, 187], gather)));
  }
  const split = seg(t, 35.0, 35.3);
  if (split < 1) trimmed(lineToCircle(1, R), 0, 1, rgba(C.dot, 1 - split), 6);
  // today marker
  const mk = Math.min(land(t, 37.5, 0.3), 1 - seg(t, 39.2, 39.5));
  if (false && mk > 0) {
    const ti = 13.5 + 0 * t;
    const a = -Math.PI / 2 + TAU * ti / N + spin;
    circle(CX + Math.cos(a) * R, CY + Math.sin(a) * R, 21, null, rgba(INK, mk), 3);
  }
  const ca = Math.min(land(t, 36.25, 0.4), 1 - seg(t, 37.3, 37.6));
  if (ca > 0) {
    ctx.globalAlpha = ca;
    text('Period', CX, CY - 22, 24, rgb(C.rose), 600, 0);
    text('Fertile window', CX, CY + 20, 24, rgb(C.lilac), 600, 0);
    ctx.globalAlpha = 1;
  }
  label(t, 35.625, 39.3, 'Know where you are in your cycle.', 'Cycle insights', C.rose);
  if (gather > 0.7) ring(CX, CY, R, BW, 0, 'silver', (gather - 0.7) / 0.3, 0, 1);
});

// ---------------------------------------------------------------- 8. hardware (40.0 – 50.0)
scene(40.0, 50.05, t => {
  const bp = beatPulse(t, 10);
  // 40.0 impact: ring slams in
  const slam = 1 + 0.14 * (1 - land(t, 40.0, 0.45));
  // 40.625 – 42.5: turn edge-on to show how thin it is; turn back on 42.5
  const theta = key(t, [[40.625, 0], [41.7, 1.38, ease.io], [42.35, 1.30, (u) => u], [43.0, 0, ease.io]]);
  if (t < 45.0) {
    const sh = t * 0.9;
    at(CX, CY, 0, slam, () => ring(0, 0, R, BW, theta, 'silver', 1, sh));
    const da = Math.min(land(t, 41.25, 0.35), 1 - seg(t, 42.3, 42.55));
    if (da > 0) {
      ctx.globalAlpha = da;
      text('2.28 mm', CX + 150 + (1 - da) * 20, CY - 14, 96, rgb(INK), 300, -2.5, 'left');
      text('Thin. From 2 g.', CX + 156 + (1 - da) * 20, CY + 52, 24, rgb(GREY), 400, 0, 'left');
      ctx.globalAlpha = 1;
    }
    // battery: four segments charge on four kicks
    const segs = [43.125, 43.75, 44.375, 45.0];
    const ba = Math.min(seg(t, 43.0, 43.2), 1 - seg(t, 44.7, 45.0));
    if (ba > 0) {
      ctx.globalAlpha = ba;
      for (let k = 0; k < 4; k++) {
        const u = land(t, segs[k] - 0.62, 0.25);
        if (u <= 0) continue;
        const a0 = -Math.PI / 2 + k * TAU / 4 + 0.06, a1 = a0 + (TAU / 4 - 0.12) * u;
        ctx.beginPath(); ctx.arc(CX, CY, R - BW - 34, a0, a1);
        ctx.strokeStyle = rgb(C.batt); ctx.lineWidth = 12; ctx.lineCap = 'round'; ctx.stroke();
      }
      const ta = land(t, 43.125, 0.35);
      ctx.globalAlpha = ba * ta;
      text('6–9 days', CX, CY - 10, 60, rgb(INK), 300, -1.5);
      text('Typical battery life', CX, CY + 40, 20, rgb(GREY), 400, 0);
      ctx.globalAlpha = 1;
    }
  }
  if (t >= 45.0 && t < 47.5) {        // water rises in steps with the kicks
    ring(CX, CY, R, BW, 0, 'silver', 1, t * 0.9);
    const lvl = stepped(t, 45.0, 3, 0.3) * (1 - ease.io(seg(t, 47.0, 47.5)));
    const inner = R - BW - 6;
    ctx.save(); ctx.beginPath(); ctx.arc(CX, CY, inner, 0, TAU); ctx.clip();
    const top = CY + inner - lvl * inner * 2 * 0.64;
    ctx.beginPath(); ctx.moveTo(CX - inner, CY + inner);
    for (let x = -inner; x <= inner; x += 4) ctx.lineTo(CX + x, top + 5 * Math.sin(x / 24 + t * 4));
    ctx.lineTo(CX + inner, CY + inner); ctx.closePath();
    const g = ctx.createLinearGradient(0, top, 0, CY + inner); g.addColorStop(0, rgba(C.water, 0.55)); g.addColorStop(1, rgba(C.water, 0.88));
    ctx.fillStyle = g; ctx.fill(); ctx.restore();
    const a = Math.min(land(t, 45.625, 0.35), 1 - seg(t, 47.1, 47.45));
    ctx.globalAlpha = a;
    text('100 m', CX, CY - 40, 60, rgb(INK), 300, -1.5);
    text('Waterproof · IP68', CX, CY + 8, 20, rgb(GREY), 400, 0);
    ctx.globalAlpha = 1;
  }
  if (t >= 47.5) {                    // six finishes deal out on the eighth-notes
    const F = [['Silver', 'silver'], ['Black', 'black'], ['Gold', 'gold'], ['Deep Rose', 'rose'], ['Stealth', 'stealth'], ['Brushed Silver', 'brushed']];
    const merge = ease.expoIn(seg(t, 49.375, 50.0));
    const us = F.map((_, i) => i === 0 ? 1 : ease.expo(seg(t, 47.5 + i * BEAT / 2, 47.5 + i * BEAT / 2 + 0.4)));
    const nv = us.reduce((a, b) => a + b, 0);            // the row re-centres as each finish arrives
    F.forEach(([n, tone], i) => {
      const u = us[i];
      const spread = ease.expo(seg(t, 47.5, 48.0));
      if (u <= 0) return;
      const tx = CX + (i - (nv - 1) / 2) * 245;
      const x = tx * (1 - merge) + CX * merge;
      const r = (i === 0 ? lerp(R, 82, spread) : 82 * u) * (1 - merge) + merge * 120;
      const th = 0.32 * Math.sin(t * 1.4 + i) * (1 - merge);
      ring(x, CY - 20, r, lerp(BW, 16, i === 0 ? spread : 1), th, tone, i === 0 ? 1 : u * (1 - merge * 0.9), i * 1.3 + t);
      const la = (i === 0 ? spread : u) * (1 - seg(t, 49.2, 49.45));
      if (la > 0) { ctx.globalAlpha = la; text(n, x, CY + 92, 21, rgb(INK), 500, 0); ctx.globalAlpha = 1; }
    });
    label(t, 48.125, 49.4, 'Titanium, inside and out.', 'Six finishes');
  }
});

// ---------------------------------------------------------------- 9. end (50.0 – 60.0)
scene(50.0, 60.0, t => {
  // 50.0 impact: one ring; it shrinks and travels to become the full stop of "Power."
  ctx.font = '600 104px SFPro, -apple-system, sans-serif';
  if ('letterSpacing' in ctx) ctx.letterSpacing = '-3px';
  const wA = ctx.measureText('Subtle. ').width, wB = ctx.measureText('Power').width, wDot = ctx.measureText('.').width;
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
  const x0 = CX - (wA + wB + wDot) / 2;
  const dotX = x0 + wA + wB + wDot * 0.5 + 6, dotY = CY + 31;
  const flash = 1 - seg(t, 50.0, 50.5);
  const sz = key(t, [[50.0, 120], [50.625, 120], [51.875, 30, ease.io], [52.6, 30], [53.1, 12, ease.expoIn]]);
  const pos = [key(t, [[51.25, CX], [51.875, dotX, ease.io]]), key(t, [[51.25, CY], [51.875, dotY, ease.io]])];
  const out = 1 - ease.in(seg(t, 54.7, 55.0));
  if (t < 53.1) ring(pos[0], pos[1], sz, Math.max(3, sz * 0.19), 0.6 * Math.sin((t - 50) * 2.0) * (1 - seg(t, 51.25, 52.0)), 'silver', 1, t * 1.5, sz > 40 ? 1 : 0);
  if (flash > 0) { ctx.globalAlpha = 0.4 * flash; circle(CX, CY, lerp(120, 420, 1 - flash), null, 'rgba(255,255,255,1)', 14 * flash); ctx.globalAlpha = 1; }
  const w1 = land(t, 52.0, 0.4), w2 = land(t, 53.1, 0.4);
  ctx.globalAlpha = w1 * out;
  text('Subtle.', x0, CY + (1 - w1) * 22, 104, rgb(INK), 600, -3, 'left');
  ctx.globalAlpha = w2 * out;
  text('Power', x0 + wA, CY + (1 - w2) * 22, 104, rgb(INK), 600, -3, 'left');
  ctx.globalAlpha = out;
  if (t >= 53.1) { const k = ease.io(seg(t, 53.1, 53.5)); ring(dotX, dotY, 13, 5, 0, 'silver', out * (1 - k), t, 0); ring(dotX, dotY, 13, 5, 0, 'black', out * k, t, 0); }   // the ring is the full stop
  ctx.globalAlpha = 1;
  // 55.0: product line with the bells
  const p = land(t, 55.0, 0.6) * (1 - ease.io(seg(t, 59.0, 59.9)));
  if (p > 0) {
    ring(CX, CY - 64 + (1 - p) * 10, 50, 11, 0.5 * (1 - p) + 0.12 * Math.sin(t * 1.2), 'silver', p, t * 0.6);
    ctx.globalAlpha = p;
    text('Oura Ring 5', CX, CY + 52 + (1 - p) * 10, 54, rgb(INK), 500, -1.0);
    ctx.globalAlpha = 1;
  }
});

// ---------------------------------------------------------------- motion blur: average sub-frames across a 180° shutter
(() => {
  const base = window.seek;
  const acc = document.createElement('canvas'); acc.width = W; acc.height = H;
  const actx = acc.getContext('2d');
  window.seek = T => {
    const n = window.MB || 1;
    if (n <= 1) return base(T);
    for (let k = 0; k < n; k++) {
      base(T + ((k + 0.5) / n - 0.5) * (0.5 / window.FPS));
      actx.globalAlpha = 1 / (k + 1); actx.drawImage(cv, 0, 0);
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.drawImage(acc, 0, 0);
  };
})();
const sf = new FontFace('SFPro', 'url(fonts/SFPro.ttf)', { weight: '1 1000' });
document.fonts.add(sf);
Promise.all([loadSprites(), sf.load()]).then(() => { window.READY = true; });
