// Shared helpers: easing, timing, DOM building. Everything is a pure function of time.
export const W = 1920, H = 1080, BPM = 120, BEAT = 60 / BPM;
export const C = { ink: '#0C0C0D', paper: '#ECEAE3', orange: '#FF4D1A', blue: '#2F3BFF', lime: '#D4FF3A', gray: '#8A8A86' };

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const prog = (t, a, b) => clamp((t - a) / (b - a));
export const smooth = t => t * t * (3 - 2 * t);
export const E = {
  outExpo: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  inExpo: t => (t <= 0 ? 0 : Math.pow(2, 10 * t - 10)),
  inOutExpo: t => (t <= 0 ? 0 : t >= 1 ? 1 : t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2),
  outCubic: t => 1 - Math.pow(1 - t, 3),
  inCubic: t => t * t * t,
  inOutCubic: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  outQuint: t => 1 - Math.pow(1 - t, 5),
  inOutQuint: t => (t < 0.5 ? 16 * t ** 5 : 1 - Math.pow(-2 * t + 2, 5) / 2),
  outBack: (t, s = 1.70158) => 1 + (s + 1) * Math.pow(t - 1, 3) + s * Math.pow(t - 1, 2),
};
// damped spring 0 -> 1, t in seconds
export const spring = (t, freq = 2.2, damp = 0.32) => (t <= 0 ? 0 : 1 - Math.exp(-damp * 2 * Math.PI * freq * t) * Math.cos(2 * Math.PI * freq * Math.sqrt(1 - damp * damp) * t));
// eased segment: value of ease(prog(t,a,b))
export const seg = (t, a, b, ease = E.outExpo) => ease(prog(t, a, b));

// deterministic hash / noise
export const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const hash2 = (a, b) => hash(a * 57.31 + b * 113.7);
export function noise2(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
  const u = smooth(xf), v = smooth(yf);
  const a = hash2(xi, yi), b = hash2(xi + 1, yi), c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1);
  return lerp(lerp(a, b, u), lerp(c, d, u), v);
}
export function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }

// DOM
export function el(tag, props = {}, parent) {
  const e = document.createElement(tag);
  const { style, cls, html, text, ...rest } = props;
  if (cls) e.className = cls;
  if (style) Object.assign(e.style, style);
  if (html != null) e.innerHTML = html;
  if (text != null) e.textContent = text;
  Object.assign(e, rest);
  if (parent) parent.appendChild(e);
  return e;
}
// split a string into masked letters; returns array of inner spans
export function maskLetters(parent, str, extraStyle = {}) {
  return [...str].map(ch => {
    const m = el('span', { cls: 'mask' }, parent);
    return el('span', { text: ch === ' ' ? ' ' : ch, style: extraStyle }, m);
  });
}
export const css = (e, s) => { for (const k in s) e.style[k] = s[k]; };
export const tf = (e, x = 0, y = 0, s = 1, r = 0, extra = '') => { e.style.transform = `translate(${x}px,${y}px) scale(${s}) rotate(${r}deg) ${extra}`; };
export const fvs = (e, wdth, wght) => { e.style.fontStretch = wdth + '%'; e.style.fontWeight = wght; };
