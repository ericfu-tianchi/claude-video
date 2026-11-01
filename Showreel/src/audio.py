"""Procedural score + sound design, locked to the 120 BPM picture edit. Writes out/score.wav"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 43.0
N = int(SR * DUR)
B = 0.5  # beat
rng = np.random.default_rng(7)
L = {k: np.zeros(N) for k in ['drums', 'bass', 'music', 'fx', 'send']}

def t_(d): return np.arange(int(d * SR)) / SR
def place(bus, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[:N - i]
    L[bus][i:i + len(sig)] += sig * gain
def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output='sos'); return sosfilt(sos, x)
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-5)) * np.exp(-t / d)
def note(m): return 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------- instruments
def kick(gain=1.0, d=0.32):
    t = t_(0.5); f = 42 + 120 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / d)
    click = filt(rng.standard_normal(len(t)), 'highpass', 3000) * np.exp(-t / 0.004) * 0.3
    return np.tanh((s + click) * 1.6) * gain
def clap():
    t = t_(0.4); n = rng.standard_normal(len(t))
    e = sum(np.exp(-np.maximum(0, t - o) / 0.01) * (t >= o) for o in (0, 0.011, 0.022)) + np.exp(-t / 0.12) * 0.6
    return filt(n, 'bandpass', [900, 3500]) * e * 0.55
def hat(open_=False):
    t = t_(0.25 if open_ else 0.06); n = rng.standard_normal(len(t))
    return filt(n, 'highpass', 7500) * np.exp(-t / (0.08 if open_ else 0.015)) * 0.22
def saw(f, d, cutoff=900, decay=0.4):
    t = t_(d); x = 2 * ((t * f) % 1) - 1
    x += 2 * ((t * f * 1.007) % 1) - 1
    return filt(x * 0.5, 'lowpass', cutoff) * env(len(t), 0.004, decay)
def pluck(f, d=0.35, bright=4000):
    t = t_(d); x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * 2 * f * t) * 0.3
    return filt(x, 'lowpass', bright) * env(len(t), 0.001, d / 4)
def pad(freqs, d, cutoff=1800):
    t = t_(d); x = np.zeros(len(t))
    for f in freqs:
        for det in (-0.004, 0, 0.004):
            x += 2 * (((t * f * (1 + det)) + rng.random()) % 1) - 1
    x = filt(x / (len(freqs) * 3), 'lowpass', cutoff)
    a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return x * np.clip(a, 0, 1)
def impact(gain=1.0, tail=1.2):
    t = t_(tail + 0.3)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 80 * np.exp(-t / 0.08)) / SR) * np.exp(-t / (tail * 0.5))
    n = filt(rng.standard_normal(len(t)), 'lowpass', 6000) * np.exp(-t / 0.18) * 0.5
    return np.tanh((sub * 1.2 + n) * 1.3) * gain
def riser(d, f0=300, f1=9000):
    t = t_(d); n = rng.standard_normal(len(t)); out = np.zeros(len(t))
    seg = int(SR * 0.05)
    for i in range(0, len(t), seg):
        p = i / len(t); fc = f0 * (f1 / f0) ** p
        out[i:i + seg] = filt(n[i:i + seg + 2000], 'bandpass', [fc * 0.7, min(fc * 1.4, 23000)])[:len(out[i:i + seg])]
    return out * (t / d) ** 2 * 0.5
def whoosh(d=0.35, f0=500, f1=5000):
    t = t_(d); n = rng.standard_normal(len(t))
    lo = filt(n, 'bandpass', [f0, f1]); a = np.sin(np.pi * t / d) ** 2
    return lo * a * 0.45
def tick(f=2400, d=0.03):
    t = t_(d); return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) * 0.35
def blip(f, d=0.12):
    t = t_(d); return np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.02)) * np.exp(-t / 0.04) * 0.3

# ------------------------------------------------------------- harmony (A minor: Am F C G per bar)
ROOTS = [45, 41, 48, 43]  # A2 F2 C3 G2
CHORDS = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]
ARP = [69, 72, 76, 79, 76, 72, 74, 71]
bar = lambda t: int(t // 2) % 4

# ------------------------------------------------------------- arrangement
# 0–4 intro: a hit per word, typing, bounce
for s in (0, 1, 2, 3): place('drums', s, kick(0.9, 0.4)); place('fx', s, impact(0.35, 0.5))
place('music', 0, pad([note(m) for m in CHORDS[0]], 4, 1200), 0.35)
for k, s in enumerate((2.04, 2.11, 2.18, 2.25)): place('fx', s, tick(1800 + k * 150))
place('fx', 2.5, whoosh(0.3, 1500, 9000), 0.7)
for k, s in enumerate((3.2, 3.34, 3.44)): place('fx', s, blip(note(76 + k * 5), 0.15), 0.9 - k * 0.2)
place('fx', 3.3, riser(0.7, 400, 12000), 0.8)
place('fx', 4.0, impact(1.0, 1.4))

def groove(t0, t1, clapon=True, hats=True, bass=True, arp=False, kickgain=1.0):
    t = t0
    while t < t1 - 1e-6:
        b = round(t / B)
        place('drums', t, kick(kickgain))
        if clapon and b % 2 == 1: place('drums', t, clap())
        if hats:
            for q in range(4):
                place('drums', t + q * B / 4, hat(open_=(q == 2)), 0.9 if q == 2 else 0.6)
        if bass:
            r = ROOTS[bar(t)]
            place('bass', t + B / 2, saw(note(r), 0.24, 700, 0.12), 0.8)
            place('bass', t + B * 3 / 4, saw(note(r + 12), 0.12, 900, 0.06), 0.4)
        if arp:
            for q in range(2):
                m = ARP[(b * 2 + q) % 8] + (0 if bar(t) in (0, 3) else -4 if bar(t) == 1 else -2)
                place('music', t + q * B / 2, pluck(note(m), 0.3), 0.32)
        t += B

# 4–8 systems: kick + hats + arp bleeps
groove(4, 8, clapon=False, bass=False, arp=True, kickgain=0.85)
for k in range(6): place('fx', 4.9 + k * 0.5, tick(3200, 0.02), 0.8)
place('fx', 7.3, riser(0.7, 500, 10000), 0.6)
place('fx', 8.0, impact(0.9, 1.0))
# 8–16 full groove
groove(8, 16, arp=True)
for k in range(4): place('music', 8 + k * 2, pad([note(m) for m in CHORDS[k]], 2.0, 1600), 0.28)
for k in range(8):  # type wall stabs on each palette swap
    ch = CHORDS[bar(12 + k * 0.5)]
    for m in ch: place('music', 12 + k * 0.5, saw(note(m + 12), 0.18, 3000, 0.08), 0.18)
place('fx', 11.4, riser(0.6, 800, 14000), 0.5)
place('fx', 12.0, impact(0.6, 0.6))
place('fx', 15.0, whoosh(0.5, 300, 3000), 0.8)
place('fx', 15.5, riser(0.5), 0.5)
# 16–20 breakdown: no drums, wide pad, shimmer, suck into the dot
place('music', 16, pad([note(m) for m in [57, 64, 67, 72, 76]], 4.0, 2400), 0.5)
place('bass', 16, pad([note(33), note(45)], 3.7, 300), 0.7)
for k in range(32):
    place('music', 16 + k * 0.125, pluck(note([81, 84, 88, 91][k % 4] + (0 if k < 16 else 2)), 0.25, 8000), 0.12 * (0.4 + k / 40))
place('fx', 18.0, riser(1.6, 200, 9000), 0.9)
place('fx', 19.66, impact(0.5, 0.4)); place('fx', 19.66, blip(note(88), 0.2), 0.8)
place('fx', 20.0, impact(1.1, 1.6))
# 20–22 title
groove(20, 22, clapon=False, hats=False, bass=True, kickgain=0.9)
place('music', 20, pad([note(m) for m in CHORDS[0] + [72]], 2.0, 1800), 0.35)
place('fx', 21.6, whoosh(0.42, 400, 6000), 0.9)
# 22–34 work: full groove, a whoosh on every wipe, UI blips on the phone
groove(22, 34, arp=True)
for k in range(6):
    place('music', 22 + k * 2, pad([note(m) for m in CHORDS[k % 4]], 2.0, 1500), 0.22)
    place('fx', 22 + k * 2 + 1.66, whoosh(0.36, 600, 7000), 0.85)
    place('fx', 22 + k * 2, impact(0.35, 0.4))
for s, f in ((22.25, 72), (22.33, 76), (22.41, 79), (22.8, 84), (22.95, 88), (23.05, 79), (23.25, 91)): place('fx', s, blip(note(f)), 0.7)
for k in range(6): place('fx', 30.0 + k * 0.33, blip(note(60 - k), 0.25), 0.25)  # sonar pings
# 34–38 principles: hit per word, then cold -> JOY
for k in range(4):
    s = 34 + k * 0.5; place('drums', s, kick(1.0)); place('fx', s, impact(0.5, 0.45))
    for m in CHORDS[k]: place('music', s, saw(note(m + 12), 0.35, 2600, 0.15), 0.2)
place('music', 36, pad([note(m) for m in [45, 52, 57]], 1.0, 500), 0.4)
for k in range(8): place('fx', 36 + k * 0.06, tick(900, 0.02), 0.4)
place('fx', 36.45, whoosh(0.3, 1000, 8000), 0.9)
place('fx', 36.6, riser(0.4, 1000, 14000), 0.6)
place('fx', 37.0, impact(1.2, 1.5))
place('music', 37, pad([note(m) for m in [57, 64, 69, 72, 76, 81]], 1.4, 5000), 0.5)
for k in range(12): place('fx', 37.05 + k * 0.045, blip(note(84 + (k * 7) % 12), 0.1), 0.25)
# 38–43 end card
place('drums', 38, kick(1.0, 0.6)); place('fx', 38, impact(0.8, 2.5))
place('music', 38, pad([note(m) for m in [45, 57, 60, 64, 71]], 5.0, 1400), 0.5)
for k in range(16): place('music', 38.5 + k * 0.25, pluck(note(ARP[k % 8] + 12), 0.4, 3000), 0.12 * (1 - k / 18))

# ------------------------------------------------------------- mix
kick_env = np.ones(N)
tk = np.arange(int(0.25 * SR)) / SR; duck = 1 - 0.75 * np.exp(-tk / 0.08)
for b in range(int(DUR / B)):
    s0 = b * B
    if 4 <= s0 < 16 or 20 <= s0 < 34:
        i = int(s0 * SR); seg_ = kick_env[i:i + len(duck)]; seg_[:] = np.minimum(seg_, duck[:len(seg_)])
music = (L['music'] + L['bass']) * kick_env
L['send'] = music * 0.5 + L['fx'] * 0.35 + L['drums'] * 0.06
ir_t = np.arange(int(2.2 * SR)) / SR
irL = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55); irR = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55)
irL = filt(irL, 'lowpass', 6000); irR = filt(irR, 'lowpass', 6000)
irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
wetL = fftconvolve(L['send'], irL)[:N]; wetR = fftconvolve(L['send'], irR)[:N]
dry = L['drums'] + music + L['fx']
# slight stereo width on music
wid = np.roll(music, int(0.012 * SR)) * 0.25
outL = dry + wid + wetL * 0.35
outR = dry - wid + wetR * 0.35
out = np.stack([outL, outR], 1)
out = filt(out.T, 'highpass', 25).T
fade = np.ones(N); fs = int(42.0 * SR); fade[fs:] = np.linspace(1, 0, N - fs) ** 2
out *= fade[:, None]
out = np.tanh(out / np.max(np.abs(out)) * 1.8) * 0.89  # soft-clip master
wavfile.write('out/score.wav', SR, (out * 32767).astype(np.int16))
print('ok', out.shape, 'peak', np.abs(out).max())
