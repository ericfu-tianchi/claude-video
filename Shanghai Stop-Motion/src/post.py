"""Edit + grade + subtitles + mux. Reads build/frames/<shot>/NNNN.png (12 fps), writes the final 24 fps film.

python3 post.py [--preview a:b] [--out path]
"""
import os, sys, subprocess, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', 'frames')
W, H, FPS = 1920, 1080, 24

# (shot, duration). Hard cuts inside a chapter; 0.5 s dissolves between chapters ('|').
EDIT = [('p1_desk', 9), ('p2_popup', 10), ('p3_arrive', 9), ('p4_title', 7), '|',
        ('l1_lane_wide', 8), ('l2_laundry', 8), ('l3_stall', 10), ('l4_cat', 7), '|',
        ('b1_river_wide', 8), ('b2_bund_claude', 8), ('b3_ferry', 6), ('d1_lights', 10), ('d2_night_claude', 8), '|',
        ('e1_desk_back', 10), ('e2_lamp_off', 7)]
XF = 0.5
END_CARD = 6.0

clips = []   # (shot, start, dur, xfade_in)
t = 0.0
pending_x = False
for e in EDIT:
    if e == '|':
        pending_x = True; continue
    name, d = e
    if pending_x: t -= XF
    clips.append((name, t, d, pending_x))
    t += d; pending_x = False
FILM_END = t
TOTAL = FILM_END + END_CARD

SUBS = [  # (start, end, zh, en)
    (2.4, 7.6, '我从没去过上海。', "I've never been to Shanghai."),
    (10.3, 17.6, '但我读过很多人写下的它。', "But I've read what so many people wrote about it."),
    (19.8, 27.4, '于是，我用这些句子，搭了一座小小的城。', 'So I built a small one, out of their sentences.'),
    (35.8, 42.0, '清晨六点，弄堂醒得比太阳还早。', 'At six, the lanes wake before the sun.'),
    (43.2, 50.0, '竹竿伸出窗外，晾着一家人的日子。', "Bamboo poles reach out of windows, hung with a family's days."),
    (51.2, 55.4, '生煎在锅里滋滋作响。', 'Pan-fried buns sizzle in the pan.'),
    (55.8, 60.2, '有人说，这是上海的闹钟。', "Someone once called it Shanghai's alarm clock."),
    (61.4, 66.8, '这里的猫，好像认识每一个人。', 'The cats here seem to know everyone.'),
    (68.4, 74.6, '外滩的老房子站成一排，记着一百年的事。', 'The old Bund stands in a row, remembering a hundred years.'),
    (76.0, 82.4, '江对面，是另一个世纪。', 'Across the river stands another century.'),
    (83.6, 88.6, '渡轮来来回回，把两岸缝在一起。', 'Ferries go back and forth, stitching the two banks together.'),
    (90.6, 97.6, '黄昏，灯一盏一盏亮起来。', 'At dusk, the lights come on, one by one.'),
    (99.6, 106.0, '每一扇窗后面，都有一个我读不完的故事。', "Behind every window, a story I'll never finish reading."),
    (108.0, 112.4, '我还是没有去过上海。', "I still haven't been to Shanghai."),
    (112.9, 117.6, '但谢谢你们，把它写给了我。', 'But thank you, for writing it down for me.'),
]
TITLE = (29.0, 34.6)

ZH = '/System/Library/Fonts/Supplemental/Songti.ttc'
EN = '/System/Library/Fonts/Supplemental/Baskerville.ttc'


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.truetype(path, size)


def text_layer(lines, sizes, fonts, spacing, color=(246, 238, 224), y_center=None, y_bottom=None, shadow=True, tracking=None, scrim=0):
    """Render centered lines onto a transparent RGBA canvas."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = [font(f, s, i) for (f, i), s in zip(fonts, sizes)]
    boxes = [d.textbbox((0, 0), l, font=f) for l, f in zip(lines, fs)]
    hs = [b[3] - b[1] for b in boxes]
    total = sum(hs) + spacing * (len(lines) - 1)
    y = (y_center - total / 2) if y_center is not None else (y_bottom - total)
    pos = []
    for l, f, b, h in zip(lines, fs, boxes, hs):
        x = (W - (b[2] - b[0])) / 2 - b[0]
        pos.append((x, y - b[1], l, f)); y += h + spacing
    if scrim:
        sc = Image.new('RGBA', (W, H), (0, 0, 0, 0)); scd = ImageDraw.Draw(sc)
        cy = (y_center if y_center is not None else y_bottom - total / 2)
        rw, rh = (620, 170) if y_center is not None else (560, 90)
        scd.ellipse((W / 2 - rw, cy - rh, W / 2 + rw, cy + rh), fill=(18, 10, 6, scrim))
        img = Image.alpha_composite(sc.filter(ImageFilter.GaussianBlur(90)), img)
    if shadow:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        for x, y, l, f in pos: sd.text((x, y + 2), l, font=f, fill=(20, 12, 6, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img = Image.alpha_composite(sh, img); d = ImageDraw.Draw(img)
    for x, y, l, f in pos: d.text((x, y), l, font=f, fill=(*color, 255))
    return np.asarray(img).astype(np.float32) / 255.0


def build_text():
    layers = []
    for s, e, zh, en in SUBS:
        layers.append((s, e, text_layer([zh, en], [42, 27], [(ZH, 4), (EN, 2)], 14, y_bottom=H - 70, scrim=120)))
    layers.append((TITLE[0], TITLE[1], text_layer(['Claude 眼中的上海', 'Shanghai, as I read it'], [92, 36], [(ZH, 4), (EN, 2)], 26, y_center=H * 0.36, scrim=170)))
    end = text_layer(['Claude 眼中的上海', 'Shanghai, as I read it', '', '场景、灯光、配乐，全部由 Claude 用代码完成',
                      'Every set, light and note was built in code by Claude'],
                     [64, 30, 10, 28, 24], [(ZH, 4), (EN, 2), (EN, 0), (ZH, 4), (EN, 2)], 18, y_center=H / 2, color=(240, 228, 208))
    layers.append((FILM_END + 0.3, TOTAL - 0.2, end))
    return layers


def text_alpha(t, s, e, fade=0.45):
    if t < s or t > e: return 0.0
    return min(1.0, (t - s) / fade, (e - t) / fade)

# ---------------------------------------------------------------- grade

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.32 * np.clip(r - 0.35, 0, None) ** 1.6)[..., None].astype(np.float32)
_cache = {}


def load(shot, idx):
    key = (shot, idx)
    if key in _cache: return _cache[key]
    p = os.path.join(FR, shot, f'{idx:04d}.png')
    while not os.path.exists(p) and idx > 0:
        idx -= 1; p = os.path.join(FR, shot, f'{idx:04d}.png')
    im = Image.open(p).convert('RGB')
    if im.size != (W, H): im = im.resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0
    # bloom from the highlights
    small = im.resize((W // 4, H // 4), Image.BILINEAR)
    sa = np.asarray(small).astype(np.float32) / 255.0
    lum = sa.mean(2, keepdims=True)
    hi = np.clip((lum - 0.62) / 0.38, 0, 1) * sa
    hb = Image.fromarray((hi * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))
    hb2 = hb.filter(ImageFilter.GaussianBlur(28))
    bloom = (np.asarray(hb.resize((W, H), Image.BILINEAR)).astype(np.float32) * 0.6 +
             np.asarray(hb2.resize((W, H), Image.BILINEAR)).astype(np.float32) * 0.6) / 255.0
    a = a + bloom * 0.35
    if len(_cache) > 8: _cache.clear()
    _cache[key] = a
    return a


WARM = {'p': (1.02, 1.0, 0.96), 'l': (1.06, 1.0, 0.90), 'b': (1.04, 1.0, 0.93), 'd': (1.03, 1.0, 0.95), 'e': (1.02, 1.0, 0.96)}


def grade(a, shot, sf):
    w = np.array(WARM[shot[0]], np.float32)
    a = a * w
    # lift blacks warm, soft roll-off of highlights
    a = a * 0.95 + np.array((0.022, 0.016, 0.010), np.float32)
    a = 1 - (1 - np.clip(a, 0, 1.4)) ** 1.0
    a = np.clip(a, 0, None); a = a / (1 + 0.12 * a)
    # gentle saturation boost in the mids
    m = a.mean(2, keepdims=True)
    a = m + (a - m) * 1.08
    # stop-motion exposure flicker: tiny, changes on each 12 fps frame
    a = a * (1 + 0.012 * random.Random(hash((shot, sf)) & 0xffff).uniform(-1, 1))
    return a


def frame_at(T, grain_rng):
    if T >= FILM_END:
        out = np.full((H, W, 3), (0.075, 0.062, 0.055), np.float32)
    else:
        layers = []
        for name, s, d, xin in clips:
            if s <= T < s + d:
                loc = T - s
                sf = min(int(loc * 12), int(d * 12) - 1)
                img = grade(load(name, sf), name, sf)
                wgt = 1.0
                if xin and loc < XF: wgt = loc / XF
                layers.append((img, wgt))
        if not layers:
            out = np.zeros((H, W, 3), np.float32)
        elif len(layers) == 1:
            out = layers[0][0]
        else:
            (a, _), (b, wb) = layers[0], layers[1]
            out = a * (1 - wb) + b * wb
        out = out * VIG
        # fades: in from black, out to black before the end card
        fade = min(1.0, T / 1.2, max(0.0, (FILM_END - T) / 1.6))
        out = out * fade
    for s, e, lay in TEXT:
        al = text_alpha(T, s, e)
        if al > 0:
            a = lay[..., 3:4] * al
            out = out * (1 - a) + lay[..., :3] * a
    # film grain (24 fps), luminance-weighted
    g = grain_rng.standard_normal((H // 2, W // 2), dtype=np.float32)
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    out = out + g * 0.016 * (0.5 + 0.5 * out.mean(2, keepdims=True))
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


if __name__ == '__main__':
    args = sys.argv[1:]
    a, b = 0.0, TOTAL
    out = os.path.join(ROOT, 'Claude眼中的上海.mp4')
    if '--preview' in args:
        a, b = map(float, args[args.index('--preview') + 1].split(':'))
    if '--out' in args:
        out = args[args.index('--out') + 1]
    if '--still' in args:
        TEXT = build_text()
        T = float(args[args.index('--still') + 1])
        Image.fromarray(frame_at(T, np.random.default_rng(1))).save(out)
        sys.exit()
    TEXT = build_text()
    audio = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build', 'score.wav')
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-ss', str(a), '-t', str(b - a), '-i', audio,
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(3)
    n0, n1 = int(a * FPS), int(b * FPS)
    for i in range(n0, n1):
        p.stdin.write(frame_at(i / FPS, rng).tobytes())
        if i % 120 == 0: print('post', i, '/', n1, flush=True)
    p.stdin.close(); p.wait()
    print('wrote', out, f'{TOTAL:.1f}s')
