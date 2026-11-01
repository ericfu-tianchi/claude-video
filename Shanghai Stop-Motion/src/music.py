"""Score + sound design, synthesized from scratch. Writes build/score.wav (44.1 kHz stereo)."""
import numpy as np
from scipy import signal
from scipy.io import wavfile
import os

SR = 44100
DUR = 130.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', 'score.wav')

L = np.zeros(N); R = np.zeros(N)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[:N - i] * gain
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * l
    R[i:i + len(sig)] += sig * r

# ---------------------------------------------------------------- instruments

def music_box(m, dur=2.5, vel=1.0):
    f = mtof(m); n = int(dur * SR); t = np.arange(n) / SR
    parts = [(1.0, 1.0, 2.2), (2.0, 0.25, 4.0), (3.01, 0.18, 6.5), (5.43, 0.10, 9.0), (8.8, 0.05, 14)]
    s = np.zeros(n)
    for ratio, a, dec in parts:
        if f * ratio < SR / 2:
            s += a * np.sin(2 * np.pi * f * ratio * t + rng.uniform(0, 6)) * np.exp(-t * dec)
    click = rng.normal(0, 1, n) * np.exp(-t * 900) * 0.15
    att = np.minimum(1, t / 0.002)
    return (s + click) * att * vel * 0.22


def piano(m, dur=3.0, vel=1.0):
    f = mtof(m); n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > SR / 2: break
        a = (1.0 / k ** 1.3) * (0.6 + 0.4 * vel)
        dec = 1.2 + 0.7 * k + f / 600
        s += a * (np.sin(2 * np.pi * fk * t) + 0.5 * np.sin(2 * np.pi * fk * 1.0012 * t)) * np.exp(-t * dec)
    ham = signal.lfilter(*signal.butter(2, min(0.99, 3000 / (SR / 2))), rng.normal(0, 1, n)) * np.exp(-t * 200) * 0.3
    att = np.minimum(1, t / 0.004)
    rel = np.ones(n); rel[-2000:] = np.linspace(1, 0, 2000)
    return (s + ham) * att * rel * vel * 0.12


def pad(ms, dur, vel=1.0, bright=1200):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ms:
        for det in (-0.12, 0.0, 0.12):
            f = mtof(m) * 2 ** (det / 12)
            ph = rng.uniform(0, 1)
            saw = 2 * ((f * t + ph) % 1.0) - 1
            s += saw
    b, a = signal.butter(2, bright / (SR / 2))
    s = signal.lfilter(b, a, s)
    env = np.minimum(1, t / 1.8) * np.minimum(1, (dur - t) / 2.0)
    return s * env * vel * 0.018


def pluck(m, vel=1.0, dur=0.9):
    """Karplus-Strong-ish nylon pluck, for the lane's little walking bass."""
    f = mtof(m); n = int(dur * SR); p = int(SR / f)
    buf = rng.uniform(-1, 1, p)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    t = np.arange(n) / SR
    return out * np.exp(-t * 3) * vel * 0.25


def bell(m, dur=4.0, vel=1.0):
    f = mtof(m); n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for ratio, a, dec in [(1, 1, 0.9), (2.4, 0.5, 1.6), (3.0, 0.35, 2.2), (4.5, 0.25, 3.0), (5.98, 0.1, 4.5)]:
        s += a * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    return s * np.minimum(1, t / 0.003) * vel * 0.12

# ---------------------------------------------------------------- score

BPM = 72.0
BEAT = 60 / BPM
BAR = 4 * BEAT

CH_A = [[65, 69, 72], [64, 67, 72], [62, 65, 69], [58, 62, 65], [57, 60, 65], [55, 58, 62, 65], [60, 64, 67], [53, 57, 60, 65]]
MEL_A = [[(0, 72, 1), (1, 69, .5), (1.5, 72, .5), (2, 77, 1.5), (3.5, 76, .5)],
         [(0, 74, 1), (1, 72, 1), (2, 67, 2)],
         [(0, 69, 1), (1, 74, 1), (2, 77, 1), (3, 76, .5), (3.5, 74, .5)],
         [(0, 74, 1.5), (1.5, 72, .5), (2, 70, 2)],
         [(0, 69, 1), (1, 72, 1), (2, 77, 1), (3, 79, .5), (3.5, 81, .5)],
         [(0, 79, 1.5), (1.5, 77, .5), (2, 74, 2)],
         [(0, 76, 1), (1, 77, .5), (1.5, 79, .5), (2, 72, 1), (3, 76, 1)],
         [(0, 77, 4)]]
CH_B = [[58, 62, 65], [60, 64, 67], [57, 60, 64], [62, 65, 69], [55, 58, 62], [60, 64, 67], [53, 57, 60, 65], [53, 57, 60, 65]]
MEL_B = [[(0, 74, .5), (.5, 77, .5), (1, 82, 2), (3, 81, 1)],
         [(0, 79, 1), (1, 76, 1), (2, 72, 2)],
         [(0, 72, .5), (.5, 76, .5), (1, 81, 2), (3, 79, 1)],
         [(0, 77, 1), (1, 74, 1), (2, 69, 2)],
         [(0, 70, 1), (1, 74, 1), (2, 79, 1), (3, 77, 1)],
         [(0, 76, 1.5), (1.5, 74, .5), (2, 72, 2)],
         [(0, 81, 1), (1, 79, 1), (2, 77, 1), (3, 72, 1)],
         [(0, 77, 4)]]


def play_bar(t0, bar, mel, chords, lead='box', acc=None, oct_=0, vel=1.0, bar_len=BAR):
    beat = bar_len / 4
    for b, m, d in mel[bar]:
        if lead == 'box':
            place(music_box(m + oct_, 2.8, vel), t0 + b * beat, pan=0.15)
        elif lead == 'piano':
            place(piano(m + oct_, 3.2, vel), t0 + b * beat, pan=-0.1)
    ch = chords[bar]
    if acc == 'arp_box':
        for k in range(8):
            place(music_box(ch[k % len(ch)] + 12, 1.8, 0.22), t0 + k * beat / 2, pan=-0.3 + 0.6 * (k % 2))
    elif acc == 'piano':
        place(piano(ch[0] - 12, 4.0, 0.7), t0, pan=-0.2)
        for k, m in enumerate(ch[1:]):
            place(piano(m, 3.5, 0.45), t0 + beat * (1 + k * 0.5), pan=0.1 * k)
    elif acc == 'pluck':
        for k in range(4):
            mm = ch[0] - 12 if k % 2 == 0 else ch[-1] - 12
            place(pluck(mm, 0.8 if k == 0 else 0.5), t0 + k * beat, pan=-0.25)
    elif acc == 'sparkle':
        for k in range(8):
            place(music_box(ch[k % len(ch)] + 24, 1.5, 0.22), t0 + k * beat / 2 + 0.02, pan=0.5 * np.sin(k))


def section_pad(t0, chords, bars, vel=1.0, bright=1100, bar_len=BAR):
    for i in range(bars):
        ch = chords[i % len(chords)]
        p = pad([m - 12 for m in ch], bar_len + 2.0, vel, bright)
        place(p, t0 + i * bar_len, pan=0.0)


# prologue: desk at night, music box alone; pad joins as the pop-up city rises
t = 1.2
for k, m in enumerate([65, 69, 72, 77]):
    place(music_box(m, 3.0, 0.5), t + k * BEAT * 0.75, pan=0.2)
t = 3.8
for i in range(8):
    play_bar(t + i * BAR, i, MEL_A, CH_A, 'box', acc=('arp_box' if 2 <= i else None), vel=0.9)
section_pad(3.8 + 4 * BAR, CH_A[4:], 4, vel=0.7)
# title: chime + sustained chord
place(bell(77, 6.0, 1.0), 29.2, pan=0.0)
place(bell(84, 6.0, 0.5), 29.25, pan=0.3)
place(pad([53, 60, 65, 69], 6.5, 1.0, 900), 29.0)

# lanes (34.5 - 67.5): piano melody + music-box counter + pluck walking bass
t = 34.6
for i in range(8):
    play_bar(t + i * BAR, i, MEL_A, CH_A, 'piano', acc='pluck', vel=1.05)
    play_bar(t + i * BAR, i, MEL_A, CH_A, 'box', acc=None, oct_=12, vel=0.25)
section_pad(t, CH_A, 8, vel=0.55, bright=1400)
for i in range(2):  # extra cadence bars
    play_bar(t + (8 + i) * BAR, 6 + i, MEL_A, CH_A, 'piano', acc='piano', vel=0.7)

# the Bund (67 - 89): broader, lower piano, strings pad
t = 67.6
for i in range(6):
    play_bar(t + i * BAR, i, MEL_A, CH_A, 'piano', acc='piano', oct_=-12, vel=0.95)
section_pad(t, CH_A, 7, vel=1.0, bright=900)

# dusk, lights on (89 - 107): theme B with sparkles, swelling
t = 88.0
for i in range(6):
    play_bar(t + i * BAR, i, MEL_B, CH_B, 'piano', acc='sparkle', vel=0.95 + 0.06 * i)
section_pad(t, CH_B, 6, vel=1.2, bright=1400)
# cadence into the epilogue
play_bar(t + 6 * BAR, 7, MEL_B, CH_B, 'piano', acc='piano', vel=0.8)

# epilogue (106.5 - ): music box alone, slowing down; final chord when the lamp goes off (118.5)
t = 108.2
slow = BAR * 1.12
for i in range(3):
    play_bar(t + i * slow, i, MEL_A, CH_A, 'box', acc=None, vel=0.85, bar_len=slow)
section_pad(t, CH_A[:3], 3, vel=0.45, bright=800, bar_len=slow)
for k, m in enumerate([65, 69, 72, 77, 81]):
    place(music_box(m, 6.0, 0.6), 118.6 + k * 0.32, pan=-0.3 + 0.15 * k)
place(pad([53, 60, 65, 69], 9.0, 0.7, 700), 118.4)
place(bell(77, 7.0, 0.5), 124.0)

# ---------------------------------------------------------------- sound design

def noise(n):
    return rng.normal(0, 1, n)


def bandnoise(dur, lo, hi):
    n = int(dur * SR)
    b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return signal.lfilter(b, a, noise(n))


def click(gain=0.6):
    n = int(0.06 * SR); t = np.arange(n) / SR
    s = bandnoise(0.06, 1500, 6000) * np.exp(-t * 120) + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 60) * 0.5
    return s * gain


def paper_flap(gain=0.25):
    d = 0.18; n = int(d * SR); t = np.arange(n) / SR
    s = bandnoise(d, 800, 5000) * np.exp(-((t - 0.04) / 0.03) ** 2) + bandnoise(d, 300, 1200) * np.exp(-t * 40) * 0.5
    return s * gain


def tap(gain=0.12):
    n = int(0.05 * SR); t = np.arange(n) / SR
    f = rng.uniform(380, 520)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + bandnoise(0.05, 1000, 3000) * np.exp(-t * 200) * 0.3) * gain


def chirp(gain=0.05):
    d = rng.uniform(0.08, 0.16); n = int(d * SR); t = np.arange(n) / SR
    f0 = rng.uniform(2800, 4200); f = f0 + 1200 * np.sin(np.pi * t / d) * rng.choice([-1, 1])
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.sin(np.pi * t / d) ** 2 * gain


def ambience(t0, t1, kind, gain):
    d = t1 - t0; n = int(d * SR); t = np.arange(n) / SR
    fade = np.minimum(1, np.minimum(t / 1.5, (d - t) / 1.5))
    if kind == 'room':
        s = signal.lfilter(*signal.butter(2, 400 / (SR / 2)), noise(n))
    elif kind == 'water':
        lap = 0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t + np.sin(2 * np.pi * 0.11 * t) * 2)
        s = signal.lfilter(*signal.butter(2, [200 / (SR / 2), 1200 / (SR / 2)], 'band'), noise(n)) * lap
    elif kind == 'city':
        s = signal.lfilter(*signal.butter(2, 300 / (SR / 2)), noise(n)) + 0.3 * signal.lfilter(*signal.butter(2, [500 / (SR / 2), 2000 / (SR / 2)], 'band'), noise(n))
    elif kind == 'sizzle':
        crack = (rng.random(n) < 0.004) * rng.normal(0, 1, n)
        s = signal.lfilter(*signal.butter(2, [3000 / (SR / 2), 9000 / (SR / 2)], 'band'), noise(n) * 0.4 + crack * 3)
    s = s / (np.abs(s).max() + 1e-9)
    place(s * fade * gain, t0, pan=0.0)


ambience(0.0, 35.0, 'room', 0.03)
place(click(0.5), 1.6, pan=-0.4)                 # lamp on
# pop-up flaps (mirror the schedule in shots.p2_popup, shot starts at 9.0s)
tt = 1.2; sched = []
for i in range(9): sched.append(tt); tt += 0.2
tt += 0.3
for i in range(8): sched.append(tt); tt += 0.25
tt += 0.3
for i in range(6): sched.append(tt); tt += 0.25
tt += 0.4
for i in range(5): sched.append(tt); tt += 0.08
for k, s_ in enumerate(sched):
    place(paper_flap(0.22 * rng.uniform(0.7, 1.0)), 9.0 + s_ + 0.12, pan=-0.5 + (k % 9) / 9)
# Claude's clay footsteps (p3 walk 19-23s, l3 walk 50.5-55s), on the stop-motion beat
for t0, t1 in [(19.0, 23.0), (50.5, 55.0)]:
    x = t0
    while x < t1:
        place(tap(0.10), x, pan=0.1); x += 1 / 2.4 / 2
for x in (24.6, 24.85, 25.1, 25.35):   # little hops
    place(tap(0.13), x + 0.0, pan=0.0)
# morning lanes: birds, sizzle at the stall, a bicycle bell
ambience(34.5, 68.0, 'city', 0.02)
x = 35.0
while x < 66.0:
    for k in range(rng.integers(1, 4)):
        place(chirp(0.035), x + k * 0.12, pan=rng.uniform(-0.8, 0.8))
    x += rng.uniform(1.0, 3.0)
ambience(50.5, 61.0, 'sizzle', 0.05)
for k in range(2):
    n = int(1.2 * SR); t = np.arange(n) / SR
    b = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in [(2200, 3), (3350, 4), (5100, 6)]) * 0.04
    place(b, 63.3 + k * 0.22, pan=0.4)
# river: water, distant city, ferry horn
ambience(67.0, 107.5, 'water', 0.035)
ambience(88.0, 107.5, 'city', 0.02)
n = int(2.4 * SR); t = np.arange(n) / SR
horn = (signal.sawtooth(2 * np.pi * 98 * t) + 0.6 * signal.sawtooth(2 * np.pi * 147 * t))
horn = signal.lfilter(*signal.butter(2, 700 / (SR / 2)), horn) * np.minimum(1, t / 0.25) * np.minimum(1, (2.4 - t) / 0.6) * 0.05
place(horn, 84.0, pan=0.3)
# epilogue
ambience(106.5, 129.0, 'room', 0.025)
place(click(0.5), 118.5, pan=-0.4)               # lamp off

# ---------------------------------------------------------------- mix: reverb, master

def reverb(x, seconds=2.6, mix=0.28):
    n = int(seconds * SR); t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t * 6.9 / seconds)
    ir = signal.lfilter(*signal.butter(1, 5000 / (SR / 2)), ir)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    wet = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - mix) + wet * mix * 1.6


Lr = reverb(L, mix=0.3); Rr = reverb(R[::-1][::-1], mix=0.3)
mixd = np.stack([Lr, Rr], 1)
# warm tilt: gentle high shelf cut
b, a = signal.butter(1, 9000 / (SR / 2))
mixd = signal.lfilter(b, a, mixd, axis=0)
# fade in/out
fi = np.minimum(1, np.arange(N) / (SR * 0.8))
fo = np.clip((DUR - np.arange(N) / SR) / 3.0, 0, 1)
mixd *= (fi * fo)[:, None]
peak = np.abs(mixd).max()
mixd = np.tanh(mixd / peak * 1.1) * 0.85
wavfile.write(OUT, SR, (mixd * 32767).astype(np.int16))
print('wrote', OUT, peak)
