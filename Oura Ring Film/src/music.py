"""Rhythmic alternative scores for the Oura film, synthesized in code (no samples, no AI).
All three sit on the film's grid: 96 BPM, one bar = 2.5 s, sections at 5 / 12.5 / 17.5 / 22.5 / 30 / 35 / 40 / 50 s.

python3 music_alt.py A|B|C   -> out/alt_<X>.wav
"""
import sys, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BEAT = 60 / 96
BAR = 4 * BEAT
S16 = BEAT / 4
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
rng = np.random.default_rng(11)


def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(n): return np.arange(n) / SR


class Bus:
    def __init__(self): self.L = np.zeros(N); self.R = np.zeros(N)
    def add(self, sig, t, pan=0.0, gain=1.0):
        i = int(round(t * SR))
        if i >= N or i < 0: return
        sig = sig[:N - i] * gain
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.L[i:i + len(sig)] += sig * l; self.R[i:i + len(sig)] += sig * r
    def stereo(self): return np.stack([self.L, self.R], 1)

# ---------------------------------------------------------------- drums

def kick(vel=1.0, punch=1.0, dec=9.0):
    n = int(0.45 * SR); t = tt(n)
    f = 45 + 110 * np.exp(-t * 38) * punch
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * dec)
    s += signal.lfilter(*signal.butter(2, 4000 / (SR / 2), 'high'), rng.normal(0, 1, n)) * np.exp(-t * 400) * 0.25
    return np.tanh(s * 1.6) * vel * 0.9


def k808(m=38, dur=1.2, vel=1.0, slide_from=None):
    n = int(dur * SR); t = tt(n)
    f = np.full(n, mtof(m))
    if slide_from is not None:
        f = mtof(m) + (mtof(slide_from) - mtof(m)) * np.exp(-t * 14)
    f = f + 60 * np.exp(-t * 50)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    s *= np.minimum(1, (dur - t) / 0.05)
    return np.tanh(s * 2.2) * vel * 0.55


def clap(vel=1.0):
    n = int(0.35 * SR); t = tt(n)
    nz = signal.lfilter(*signal.butter(2, [900 / (SR / 2), 5200 / (SR / 2)], 'band'), rng.normal(0, 1, n))
    env = np.zeros(n)
    for d in (0.0, 0.011, 0.022):
        env += np.exp(-np.clip(t - d, 0, None) * 160) * (t >= d)
    env += np.exp(-t * 18) * 0.35
    return nz * env * vel * 0.32


def snare(vel=1.0):
    n = int(0.3 * SR); t = tt(n)
    nz = signal.lfilter(*signal.butter(2, [1500 / (SR / 2), 9000 / (SR / 2)], 'band'), rng.normal(0, 1, n)) * np.exp(-t * 22)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35)
    return (nz * 0.8 + tone * 0.6) * vel * 0.35


def hat(vel=1.0, open_=False):
    d = 0.22 if open_ else 0.045
    n = int(d * SR); t = tt(n)
    nz = signal.lfilter(*signal.butter(2, 7500 / (SR / 2), 'high'), rng.normal(0, 1, n))
    return nz * np.exp(-t * (14 if open_ else 90)) * vel * 0.24


def shaker(vel=1.0):
    n = int(0.07 * SR); t = tt(n)
    nz = signal.lfilter(*signal.butter(2, [5000 / (SR / 2), 12000 / (SR / 2)], 'band'), rng.normal(0, 1, n))
    return nz * np.sin(np.pi * t / t[-1]) ** 2 * vel * 0.09


def rim(vel=1.0):
    n = int(0.08 * SR); t = tt(n)
    return (np.sin(2 * np.pi * 820 * t) + 0.5 * np.sin(2 * np.pi * 1660 * t)) * np.exp(-t * 70) * vel * 0.18

# ---------------------------------------------------------------- tonal

def supersaw(ms, dur, vel=1.0, cutoff=2400, att=0.01, rel=0.25):
    n = int(dur * SR); t = tt(n)
    s = np.zeros(n)
    for m in ms:
        for d in np.linspace(-0.22, 0.22, 7):
            f = mtof(m) * 2 ** (d / 12)
            s += 2 * ((f * t + rng.random()) % 1.0) - 1
    s = signal.lfilter(*signal.butter(2, min(0.99, cutoff / (SR / 2))), s)
    env = np.minimum(1, t / att) * np.minimum(1, np.clip(dur - t, 0, None) / rel)
    return s * env * vel * 0.012


def pluck(m, dur=0.5, vel=1.0, bright=6000):
    n = int(dur * SR); t = tt(n)
    f = mtof(m)
    s = (2 * ((f * t) % 1.0) - 1) + 0.6 * np.sign(np.sin(2 * np.pi * f * 1.005 * t))
    # filter envelope: bright attack, quick close
    # one-pole low-pass with a smoothly closing cutoff, state carried sample to sample (no block clicks)
    fc = 300 + bright * np.exp(-t * 14)
    g = 1 - np.exp(-2 * np.pi * fc / SR)
    out = np.zeros(n); y = 0.0
    for i in range(n):
        y += g[i] * (s[i] - y); out[i] = y
    return out * np.exp(-t * 6) * vel * 0.14


def bell(m, dur=1.6, vel=1.0):
    n = int(dur * SR); t = tt(n); f = mtof(m)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 3), (2.0, 0.4, 5), (3.01, 0.25, 7), (4.2, 0.12, 10)])
    return s * np.minimum(1, t / 0.002) * vel * 0.12


def rhodes(m, dur=1.6, vel=1.0):
    n = int(dur * SR); t = tt(n); f = mtof(m)
    idx = 1.8 * np.exp(-t * 4)
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t * 1.6)
    s *= 1 + 0.15 * np.sin(2 * np.pi * 5 * t)
    return s * np.minimum(1, t / 0.003) * np.minimum(1, (dur - t) / 0.05) * vel * 0.11


def subbass(m, dur, vel=1.0):
    n = int(dur * SR); t = tt(n); f = mtof(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.008) * np.minimum(1, (dur - t) / 0.03)
    return np.tanh(s * 1.4) * env * vel * 0.32


def riser(dur, vel=1.0):
    n = int(dur * SR); t = tt(n)
    nz = rng.normal(0, 1, n)
    fc = 400 + 9000 * (t / dur) ** 2
    g = 1 - np.exp(-2 * np.pi * fc / SR)
    out = np.zeros(n); y1 = y2 = 0.0
    for i in range(n):
        y1 += g[i] * (nz[i] - y1); y2 += g[i] * (y1 - y2); out[i] = y2
    return out * (t / dur) ** 2.2 * vel * 0.12


def impact(vel=1.0):
    n = int(2.5 * SR); t = tt(n)
    boom = np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 10)) * t) * np.exp(-t * 2.2)
    nz = signal.lfilter(*signal.butter(2, 2500 / (SR / 2)), rng.normal(0, 1, n)) * np.exp(-t * 3) * 0.3
    return np.tanh((boom + nz) * 1.5) * vel * 0.6


def ui(m=86, vel=1.0):
    n = int(0.35 * SR); t = tt(n); f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t * 18) * vel * 0.06

def heartbeat_intro(bus, vel=1.0):
    # a 'lub-dub' heartbeat under the ring's opening turn: the hook in the first second
    for t in (0.15, 1.4, 2.65, 3.9):
        bus.add(kick(1.0 * vel, 0.5, 11), t); bus.add(kick(0.65 * vel, 0.4, 13), t + 0.2)


# ---------------------------------------------------------------- helpers

def reverb(x, sec=1.8, mix=0.2):
    n = int(sec * SR); t = tt(n)
    ir = rng.normal(0, 1, n) * np.exp(-t * 6.9 / sec)
    ir = signal.lfilter(*signal.butter(1, 6000 / (SR / 2)), ir); ir[:int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    wet = np.stack([signal.fftconvolve(x[:, c], ir)[:len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix * 1.4


def sidechain(kick_times, depth=0.65, rel=0.18):
    g = np.ones(N)
    for kt in kick_times:
        i = int(kt * SR); n = int(rel * 2.5 * SR)
        e = 1 - depth * np.exp(-tt(n) / rel * 2.5)
        j = min(N, i + n); g[i:j] = np.minimum(g[i:j], e[:j - i])
    return g


def master(stem_buses, gains, sc=None):
    mix = np.zeros((N, 2))
    for b, g in zip(stem_buses, gains):
        x = b.stereo() * g
        if sc is not None and b is not stem_buses[0]: x *= sc[:, None]
        mix += x
    mix = reverb(mix, mix=0.12)
    mix *= np.minimum(1, np.arange(N) / (SR * 0.05))[:, None]
    mix *= np.clip((DUR - np.arange(N) / SR) / 1.5, 0, 1)[:, None]
    mix = mix / (np.percentile(np.abs(mix), 99.9) + 1e-9)
    mix = np.tanh(mix * 1.15) * 0.92                       # glue + soft limit
    return mix


ACCENTS = [(4.4, 86), (13.4, 88), (19.0, 83), (23.8, 88), (24.25, 90), (24.7, 93), (31.0, 85), (37.0, 88),
           (43.0, 86), (45.2, 83), (47.6, 88)]

ACCENTS_A = [(5.625, 86), (6.875, 81), (12.5, 88), (17.5, 83), (25.0, 86), (26.25, 88), (27.5, 90), (28.75, 84), (30.0, 81),
             (36.25, 86), (36.875, 88), (41.25, 90), (43.125, 84), (43.75, 86), (44.375, 88), (45.0, 91),
             (47.5, 86), (47.8125, 88), (48.125, 90), (48.4375, 91), (48.75, 93), (49.0625, 95), (51.875, 93)]

# ---------------------------------------------------------------- A: "Pulse" — bright future-house, keynote energy

def variant_A():
    drums, music, bass, fx = Bus(), Bus(), Bus(), Bus()
    heartbeat_intro(drums)
    PROG = [[59, 62, 66, 69], [55, 59, 62, 66], [50, 54, 57, 62], [57, 61, 64, 69]]   # Bm  G  D  A  (one bar each)
    ROOT = [35, 31, 38, 33]
    LEAD = [(0, 78), (0.75, 76), (1.5, 74), (2.5, 74), (3, 76), (3.5, 78)]   # beats in a bar, hook
    ANSWER = [(0, 76), (0.75, 73), (1.5, 69), (2.5, 71), (3, 73)]
    kicks = []
    nb = int(DUR / BEAT)
    for b in range(nb):
        t = b * BEAT; bar = int(t / BAR)
        build = 20.0 <= t < 22.5 or 37.5 <= t < 40.0
        main = (5.0 <= t < 50.0) and not (35.0 <= t < 37.5)
        if main and not build:
            drums.add(kick(1.0), t); kicks.append(t)
        if build:   # snare roll accelerates into the drops
            k = 4 if t % BAR < 2 * BEAT else 8
            for j in range(k // 2):
                drums.add(snare(0.35 + 0.6 * ((t % BAR) / BAR)), t + j * BEAT / (k // 2))
        if 12.5 <= t < 50.0 and b % 4 in (1, 3) and not build and not (35.0 <= t < 37.5):
            drums.add(clap(0.9), t)
        if 5.0 <= t < 50.0 and not build:
            drums.add(hat(0.9, open_=True), t + BEAT / 2, pan=0.25)
            if t >= 22.5: drums.add(hat(0.55), t + BEAT / 4, pan=-0.3); drums.add(hat(0.55), t + 3 * BEAT / 4, pan=-0.3)
    # chords: supersaw stabs on the off-beats once the scores hit, sustained pads before
    for bar in range(int(DUR / BAR)):
        t0 = bar * BAR; ch = PROG[bar % 4]
        if t0 < 5.0:
            music.add(supersaw(ch, BAR + 0.4, 0.7, 1500, att=0.3), t0)
        elif t0 < 22.5:
            music.add(supersaw(ch, BAR + 0.2, 0.55, 1600 + 300 * (t0 > 12), att=0.02), t0)
        elif t0 < 50.0 and not (35.0 <= t0 < 37.5):
            for k in range(4):
                music.add(supersaw(ch, BEAT * 0.45, 0.9, 3800), t0 + k * BEAT + BEAT / 2)
        elif 35.0 <= t0 < 37.5:
            music.add(supersaw(ch, BAR + 0.5, 0.6, 900, att=0.3), t0)
        # bass: offbeat 8ths, root
        if 12.5 <= t0 < 50.0 and not (35.0 <= t0 < 37.5):
            for k in range(8):
                if k % 2 == 1: bass.add(subbass(ROOT[bar % 4] + 12, S16 * 1.8, 1.0), t0 + k * BEAT / 2)
        # lead hook: from the scores on, and over the hardware section
        if (22.5 <= t0 < 35.0) or (40.0 <= t0 < 50.0):
            if bar % 4 != 3:
                for b_, m in LEAD:
                    music.add(pluck(m, 0.45, 0.9), t0 + b_ * BEAT, pan=0.15)
                    music.add(pluck(m + 12, 0.3, 0.18), t0 + b_ * BEAT + 0.002, pan=-0.3)
            else:
                # answer phrase on the A chord: lower, rounder, resolving down instead of the shrill +2 lift
                for b_, m in ANSWER:
                    music.add(pluck(m, 0.6, 0.8, bright=2600), t0 + b_ * BEAT, pan=0.1)
                    music.add(bell(m + 12, 1.0, 0.35), t0 + b_ * BEAT, pan=-0.2)
    # intro arp (ring turning) and sleep arp
    for i in range(int(12.5 / S16)):
        t = i * S16; ch = PROG[int(t / BAR) % 4]
        if t >= 1.25:
            music.add(pluck(ch[i % 4] + 12, 0.25, 0.8 if t < 5 else 0.7, 3500), t, pan=0.4 * np.sin(i))
    for th in (22.5, 40.0, 50.0):
        fx.add(riser(2.5), th - 2.5); fx.add(impact(0.8), th)
    for t, m in ACCENTS_A: fx.add(ui(m), t, 0.1)
    for i in range(28): fx.add(hat(0.5), 35.0 + i * 0.032, pan=-0.6 + 1.2 * i / 27)   # cycle dots pop one by one
    for k in range(3): fx.add(ui(79 + 2 * k, 0.8), 45.0 + k * BEAT, -0.1)                 # water steps
    # end: "Subtle." / "Power." hits, then the ring rings out
    for th in (52.0, 53.1):
        drums.add(kick(1.0), th); drums.add(clap(0.8), th); music.add(supersaw(PROG[0], 0.5, 1.0, 3000), th)
    music.add(supersaw([50, 57, 62, 66, 69], 6.0, 0.7, 1500, att=0.05, rel=3), 55.0)
    for k, m in enumerate([74, 78, 81, 86]): music.add(bell(m, 3.0, 0.8), 55.0 + k * 0.09)
    sc = sidechain(kicks + [52.0, 53.1])
    return master([drums, music, bass, fx], [1.0, 0.9, 1.0, 0.8], sc)

# ---------------------------------------------------------------- B: "Rest" — neo-soul / lo-fi hip-hop groove

def variant_B():
    drums, music, bass, fx = Bus(), Bus(), Bus(), Bus()
    heartbeat_intro(drums)
    PROG = [[55, 59, 62, 66], [54, 57, 61, 64], [52, 55, 59, 62], [57, 60, 64, 67]]   # Gmaj7  F#m7  Em7  A7sus-ish
    ROOT = [43, 42, 40, 45]
    swing = 0.07
    kicks = []
    for bar in range(int(DUR / BAR)):
        t0 = bar * BAR; ch = PROG[bar % 4]
        on = 5.0 <= t0 < 50.0
        full = 12.5 <= t0 < 50.0 and not (35.0 <= t0 < 37.5)
        # Rhodes comping: chord on 1, a pushed hit on the "and" of 2
        music.add(sum([rhodes(m, BAR * 0.9, 0.8) for m in ch]), t0, pan=-0.1)
        if t0 >= 5.0: music.add(sum([rhodes(m + 12, 0.5, 0.35) for m in ch[1:]]), t0 + 1.5 * BEAT + swing, pan=0.2)
        if on:
            for kt in (0, 2.5 * BEAT + swing) if full else (0,):
                drums.add(kick(0.95, 0.8, 7), t0 + kt); kicks.append(t0 + kt)
            if full:
                drums.add(snare(1.0), t0 + BEAT); drums.add(snare(1.0), t0 + 3 * BEAT)
                drums.add(clap(0.4), t0 + 3 * BEAT)
            for k in range(8):
                sw = swing if k % 2 else 0
                drums.add(hat(0.7 if k % 2 == 0 else 0.45), t0 + k * BEAT / 2 + sw, pan=0.3)
            if t0 >= 22.5: drums.add(rim(0.6), t0 + 3.5 * BEAT + swing, pan=-0.4)
        if full:
            bass.add(subbass(ROOT[bar % 4], BEAT * 1.4, 0.9), t0)
            bass.add(subbass(ROOT[bar % 4] + 7, BEAT * 0.5, 0.6), t0 + 2.5 * BEAT + swing)
            bass.add(subbass(ROOT[bar % 4] + 12, BEAT * 0.8, 0.7), t0 + 3 * BEAT)
        # bell melody over scores / hardware
        if (22.5 <= t0 < 35.0) or (40.0 <= t0 < 50.0):
            mel = [(0, ch[3] + 12), (0.75, ch[2] + 12), (1.5, ch[3] + 12), (3, ch[1] + 24)]
            for b_, m in mel: music.add(bell(m, 1.4, 0.7), t0 + b_ * BEAT + (swing if b_ % 1 else 0), pan=0.25)
    # vinyl-ish texture
    crackle = (rng.random(N) < 0.0006) * rng.normal(0, 1, N) * 0.05
    fx.L += crackle; fx.R += np.roll(crackle, 300)
    for th in (22.5, 40.0): fx.add(riser(2.5, 0.7), th - 2.5)
    for t, m in ACCENTS: fx.add(ui(m, 0.8), t, 0.1)
    for th in (52.0, 53.1): drums.add(kick(0.9, 0.8, 7), th); drums.add(snare(0.9), th)
    for k, m in enumerate([55, 59, 62, 66, 69]): music.add(rhodes(m, 5.0, 0.8), 55.0 + k * 0.06)
    sc = sidechain(kicks, depth=0.3, rel=0.12)
    return master([drums, music, bass, fx], [1.0, 1.0, 1.0, 0.7], sc)

# ---------------------------------------------------------------- C: "Signal" — modern trap-pop, 808s and rolling hats

def variant_C():
    drums, music, bass, fx = Bus(), Bus(), Bus(), Bus()
    heartbeat_intro(drums)
    PROG = [[59, 62, 66], [55, 59, 62], [50, 54, 57], [57, 61, 64]]
    ROOT = [35, 31, 38, 33]
    kicks = []
    for bar in range(int(DUR / BAR)):
        t0 = bar * BAR; ch = PROG[bar % 4]
        on = 5.0 <= t0 < 50.0
        drop = (12.5 <= t0 < 35.0) or (40.0 <= t0 < 50.0)
        # bell/pluck motif (always on, carries the melody)
        if t0 >= 1.25:
            for k, (b_, d) in enumerate([(0, 0), (0.75, 1), (1.5, 2), (2.5, 1), (3, 0), (3.5, 2)]):
                music.add(bell(ch[d] + 24, 0.9, 0.8 if t0 < 12.5 else 0.75), t0 + b_ * BEAT, pan=0.3 * (1 if k % 2 else -1))
        music.add(supersaw([m + 12 for m in ch], BAR + 0.3, 0.35, 1100, att=0.4), t0)
        if on and drop:
            # 808 pattern with a slide into bar 3 and 4
            pat = [(0, 1.2), (1.75, 0.6), (2.5, 1.2)]
            for b_, d in pat:
                sl = ROOT[(bar + 1) % 4] if (b_ == 2.5 and bar % 2) else None
                bass.add(k808(ROOT[bar % 4] + 12, d * BEAT * 1.6, 1.0, slide_from=sl), t0 + b_ * BEAT)
                drums.add(kick(0.8, 1.2, 12), t0 + b_ * BEAT); kicks.append(t0 + b_ * BEAT)
            drums.add(clap(1.0), t0 + 2 * BEAT); drums.add(snare(0.6), t0 + 2 * BEAT)
            # hats: 8ths with 16th / triplet rolls at the end of every other bar
            for k in range(8):
                drums.add(hat(0.6 if k % 2 == 0 else 0.4), t0 + k * BEAT / 2, pan=0.2)
            if bar % 2:
                for j in range(6): drums.add(hat(0.35 + 0.05 * j), t0 + 3 * BEAT + j * BEAT / 6, pan=0.2)
            if bar % 4 == 3: drums.add(hat(0.6, open_=True), t0 + 3.5 * BEAT, pan=-0.2)
        elif on:
            drums.add(kick(0.7, 1.0, 10), t0); kicks.append(t0)
            for k in range(4): drums.add(shaker(0.8), t0 + k * BEAT + BEAT / 2, pan=0.3)
            if 37.5 <= t0 < 40.0:
                for j in range(16): drums.add(snare(0.2 + 0.05 * j), t0 + j * S16)
    for th in (12.5, 22.5, 40.0, 50.0): fx.add(riser(2.0, 0.8), th - 2.0)
    for th in (12.5, 40.0): fx.add(impact(0.7), th)
    for t, m in ACCENTS: fx.add(ui(m, 0.8), t, 0.1)
    for th in (52.0, 53.1): bass.add(k808(38, 1.0, 1.0), th); drums.add(clap(0.9), th)
    for k, m in enumerate([62, 66, 69, 74]): music.add(bell(m + 12, 3.0, 0.7), 55.0 + k * 0.1)
    sc = sidechain(kicks, depth=0.4, rel=0.15)
    return master([drums, music, bass, fx], [1.0, 0.9, 1.0, 0.75], sc)


if __name__ == '__main__':
    v = sys.argv[1].upper()
    mix = {'A': variant_A, 'B': variant_B, 'C': variant_C}[v]()
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'score.wav' if v == 'A' else f'alt_{v}.wav')
    wavfile.write(p, SR, (mix * 32767).astype(np.int16))
    print('wrote', p)
