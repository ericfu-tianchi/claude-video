"""Shot list. Each shot builder returns (duration_seconds, update(frame, t))."""
import bpy, math, random
from mathutils import Vector
from lib import *
from props import *

SHOTS = {}
def shot(fn):
    SHOTS[fn.__name__] = fn
    return fn

LAUNDRY = [(0.85, 0.82, 0.75), (0.55, 0.2, 0.18), (0.3, 0.42, 0.58), (0.92, 0.88, 0.6), (0.75, 0.55, 0.6), (0.95, 0.95, 0.93), (0.4, 0.55, 0.42)]

# ================================================================ sets

def set_lane(mood='morning', length=6, wet=False):
    """Alley along X between two shikumen rows. Returns dict of handles."""
    H = {}
    lit = lit_obj_mat('lane_lit')
    H['lit'] = lit
    rows = []
    for side, y, rot, seed in [(1, 0.10, 0.0, 1), (-1, -0.10, math.pi, 2)]:
        for k in range(2):
            r, wins = shikumen_row(f'row{side}{k}', n=length, origin=((k - 0.5) * length * 0.062 + (0.03 if side < 0 else 0), y, 0),
                                   facing=rot, seed=seed * 10 + k, lit=lit)
            rows.append(r)
    pave = ground('pave', (0.42, 0.40, 0.37), wet=0.85 if wet else 0.0)
    box('Ground', (2.0, 0.09, 0.002), (0, 0, -0.002), pave, bev=0)
    box('Base', (3, 3, 0.01), (0, 0, -0.012), wood('table'), bev=0)
    # paving stone joints
    joint = clay('joint', (0.33, 0.31, 0.28), rough=0.9)
    js = [box(f'jt{i}', (0.0004, 0.09, 0.00015), (-0.6 + i * 0.016, 0, 0), joint, bev=0) for i in range(80)]
    js += [box(f'jl{i}', (1.3, 0.0004, 0.00015), (0, -0.04 + i * 0.016, 0), joint, bev=0) for i in range(6)]
    join(js, 'Joints')
    # laundry across the alley
    H['cloth'] = []
    rnd = random.Random(5)
    for i, x in enumerate([-0.22, -0.13, -0.05, 0.04, 0.12, 0.21, 0.3]):
        z = 0.072 + rnd.uniform(-0.006, 0.01)
        pole, cl = laundry_line(f'ld{i}', (x, 0.046, z), (x + rnd.uniform(-0.02, 0.02), -0.046, z + rnd.uniform(-0.004, 0.004)), LAUNDRY, seed=i)
        H['cloth'] += cl
    # overhead wires
    wm = clay('wire', (0.05, 0.05, 0.05), rough=0.6, bump=0)
    for i in range(6):
        x0 = -0.35 + i * 0.12
        curve_wire(f'wire{i}', [(x0, 0.05, 0.104 + 0.004 * (i % 2)), (x0 + 0.08, -0.05, 0.102)], r=0.00025, mat=wm, sag=0.006)
    curve_wire('wireL', [(-0.6, 0.043, 0.098), (0.6, 0.043, 0.098)], r=0.0003, mat=wm, sag=0.01)
    # end of alley: a cross-row so the world doesn't end
    r, w = shikumen_row('endrow', n=5, origin=(0.47, 0, 0), facing=math.pi / 2, seed=33, lit=lit)
    r, w = shikumen_row('endrow2', n=5, origin=(-0.47, 0, 0), facing=-math.pi / 2, seed=34, lit=lit)
    return H


def light_morning(sky=True):
    world((0.95, 0.80, 0.68), 0.25, top=(0.55, 0.68, 0.85))
    sn = sun_from('Sun', (1.0, -0.25, 0.75), power=3.2, color=(1.0, 0.72, 0.48), angle=0.04)
    fill = area('Fill', (0.0, -0.05, 0.6), (0, 0, 0), power=2.0, size=1.0, color=(0.8, 0.86, 1.0))
    return sn, fill


def light_night():
    world((0.05, 0.06, 0.12), 0.25, top=(0.02, 0.025, 0.06))
    moon = area('Moon', (-0.3, -0.5, 0.8), (0, 0, 0), power=2.5, size=1.5, color=(0.55, 0.65, 1.0))
    return moon


# ================================================================ desk

def set_desk(lamp_on=1.0):
    H = {}
    world((0.035, 0.03, 0.03), 1.0)
    bpy.context.scene.view_settings.exposure = 0.0
    box('Desk', (2.4, 1.4, 0.03), (0, 0.1, -0.03), wood('desk', (0.42, 0.24, 0.12), (0.26, 0.13, 0.06), scale=4), bev=0.004)
    H['book'] = open_book('Book', (0, 0, 0))
    pieces, win = paper_city((0.0, 0.0, 0.0185))
    H['pieces'], H['cardwin'] = pieces, win
    lamp, lt, bulb = desk_lamp('Lamp', (-0.36, 0.02, 0), rot=math.radians(-12))
    H['lamp'], H['bulb'] = lt, bulb
    bs, top = book_stack('Stack', (0.33, 0.18, 0), n=4, seed=3, rot=0.25)
    teacup('Cup', (0.26, -0.13, 0))
    H['steam'] = steam_puffs('teasteam', 7, (0.26, -0.13, 0.055), seed=9)
    pencil = cyl('Pencil', 0.0035, 0.17, (0.12, -0.17, 0.0035), paint('pencil', (0.85, 0.65, 0.2)), seg=6, rot=(0, math.pi / 2, 0.3), smooth=False)
    tip = cyl('PencilTip', 0.0035, 0.018, (0.12 + 0.17 * math.cos(0.3), -0.17 + 0.17 * math.sin(0.3), 0.0035), clay('wood_raw', (0.85, 0.7, 0.5)), seg=6, r2=0.0004,
              rot=(0, math.pi / 2, 0.3), smooth=False)
    # glasses-free: a few loose pages
    for k in range(3):
        box(f'Loose{k}', (0.15, 0.2, 0.0004), (-0.2 + k * 0.012, -0.12 - k * 0.01, 0.0004 * k), paper('loose', (0.92, 0.88, 0.8), lines=True), bev=0,
            rot=(0, 0, 0.5 + k * 0.12))
    # far bokeh: a window full of a city at night
    rnd = random.Random(1)
    for k in range(40):
        c = rnd.choice([(1, 0.7, 0.4), (1, 0.85, 0.6), (0.8, 0.5, 0.3), (1, 0.6, 0.45)])
        sphere(f'bok{k}', 0.006, (rnd.uniform(-1.2, 1.2), rnd.uniform(1.4, 1.8), rnd.uniform(0.05, 0.7)), emit(f'bok{c}', c, rnd.uniform(1.5, 5)), seg=8)
    H['fill'] = area('DeskFill', (0.4, -0.6, 0.5), (0, 0, 0), power=0.6, size=1.0, color=(0.6, 0.7, 1.0))
    H['rim'] = area('DeskRim', (0.0, 0.8, 0.4), (0, 0, 0.03), power=1.0, size=0.8, color=(1.0, 0.7, 0.45))
    return H


def lamp_level(H, v):
    H["lamp"].data.energy = 14 * v
    H['bulb'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 25 * v
    H['rim'].data.energy = 1.0 * max(v, 0.25)


@shot
def p1_desk():
    H = set_desk()
    for h in H['pieces']: h.rotation_euler.x = -math.pi / 2
    set_lit(H['cardwin'], 0.0)
    cam = camera((0.42, -0.42, 0.13), (0.0, 0.02, 0.02), lens=40, fstop=2.2)
    jit = Jitter(3, 0.0004)
    def update(f, t):
        on = 0.0 if t < 1.6 else (0.55 if f % 2 == 0 and t < 1.85 else 1.0)
        lamp_level(H, on)
        p = path([(0, (0.42, -0.42, 0.13)), (9.0, (0.26, -0.33, 0.085))], t)
        aim(cam, p + jit.v(f), (0.0, 0.02, 0.02))
        cam.data.dof.focus_distance = (p - Vector((0.0, 0.0, 0.02))).length
        animate_steam(H['steam'], (0.26, -0.13, 0.055), t, rise=0.09, speed=0.12, drift=(0.01, 0.004, 0))
    return 9.0, update


@shot
def p2_popup():
    H = set_desk()
    lamp_level(H, 1.0)
    set_lit(H['cardwin'], 0.0)
    pcs = H['pieces']
    # order: front lanes -> Bund -> Pudong, pearl last
    lanes = [p for p in pcs if p.name.startswith('lane')]
    bund = [p for p in pcs if p.name.startswith('bund')]
    pd = [p for p in pcs if p.name.startswith('pd_')]
    pearl = [p for p in pcs if p.name.startswith('pearl')]
    sched = []
    t = 1.2
    for p in lanes: sched.append((p, t)); t += 0.2
    t += 0.3
    for p in bund: sched.append((p, t)); t += 0.25
    t += 0.3
    for p in pd: sched.append((p, t)); t += 0.25
    t += 0.4
    for p in pearl: sched.append((p, t)); t += 0.08
    cam = camera((0.05, -0.30, 0.10), (0.0, 0.02, 0.03), lens=50, fstop=2.8)
    jit = Jitter(4, 0.0002)
    def update(f, tt):
        for h, t0 in sched: animate_pop(h, tt, t0, dur=0.42)
        p = path([(0, (0.07, -0.30, 0.10)), (10.0, (0.0, -0.27, 0.095))], tt)
        aim(cam, p + jit.v(f), (0.0, 0.03, 0.042))
        cam.data.dof.focus_distance = (p - Vector((0.0, -0.01, 0.03))).length
    return 10.0, update


@shot
def p3_arrive():
    """Claude walks in across the page and looks up at the paper city."""
    H = set_desk()
    lamp_level(H, 1.0)
    for h in H['pieces']: h.rotation_euler.x = 0
    c = Claude((0.14, -0.075, 0.0165), facing=math.pi / 2)
    cam = camera((0.10, -0.26, 0.04), (0.06, -0.07, 0.03), lens=60, fstop=2.4)
    jit = Jitter(5, 0.00015)
    def update(f, t):
        # walk in from the right, stop, look up, two happy hops
        x = path([(0, 0.15), (4.0, 0.035)], t, fn=lambda u: u * (2 - u) if u < 1 else 1)
        walking = t < 4.0
        hop = 0.0
        if 5.6 < t < 6.6: hop = abs(math.sin((t - 5.6) * math.pi * 2)) * 0.012
        zpage = 0.012 + 0.006 * math.sin(min(1, abs(x) / 0.15) * math.pi * 0.9) + 0.0005
        fac = -0.75 if walking else path([(4.0, -0.75), (4.6, 0.25)], t)
        c.pose(f, loc=(x, -0.075, zpage + hop), facing=fac, hop=1.0 if walking else 0.0, phase=t * 2.4,
               tilt=(-0.25 if 4.6 < t < 5.6 else 0.0), squash=(1.0 if 5.55 < t < 5.65 else 0.0), blink=(7.4 < t < 7.55))
        cp = path([(0, (0.13, -0.27, 0.035)), (9.0, (0.05, -0.24, 0.045))], t)
        tgt = path([(0, (0.11, -0.075, 0.03)), (4.0, (0.04, -0.07, 0.03)), (9.0, (0.02, -0.02, 0.045))], t)
        aim(cam, cp + jit.v(f), tgt)
        cam.data.dof.focus_distance = (cp - Vector((x, -0.075, 0.03))).length
    return 9.0, update


@shot
def p4_title():
    H = set_desk()
    lamp_level(H, 1.0)
    for h in H['pieces']: h.rotation_euler.x = 0
    c = Claude((0.03, -0.075, 0.0156), facing=0.15)
    cam = camera((0.0, -0.36, 0.30), (0.0, 0.0, 0.03), lens=45, fstop=3.5)
    jit = Jitter(6, 0.0002)
    def update(f, t):
        c.pose(f, blink=(3.0 < t < 3.15))
        cp = path([(0, (0.0, -0.36, 0.30)), (7.0, (0.0, -0.31, 0.25))], t)
        aim(cam, cp + jit.v(f), (0.0, 0.0, 0.03))
        cam.data.dof.focus_distance = (cp - Vector((0.0, -0.02, 0.03))).length
    return 7.0, update


# ================================================================ lane: morning

def lane_morning_common():
    H = set_lane()
    light_morning()
    fog((1.2, 0.3, 0.35), (0, 0, 0.17), density=0.12, color=(1, 0.88, 0.75))
    set_lit(H['lit'], 0.06)
    H['stall'] = breakfast_stall('stall', (0.09, 0.022, 0), rot=math.pi)
    H['steam'] = steam_puffs('stm', 9, (0.081, 0.022, 0.036))
    bicycle('bike', (-0.05, 0.036, 0), rot=0.1)
    bicycle('bike2', (0.17, -0.036, 0), rot=3.0, color=(0.5, 0.12, 0.1))
    H['cat'] = cat('cat', (0.035, -0.03, 0), rot=2.4)
    H['auntie'] = person('auntie', (0.10, 0.038, 0), rot=math.pi, seed=1, col=(0.62, 0.3, 0.32))
    H['man'] = person('man', (-0.2, -0.01, 0), seed=3, col=(0.3, 0.38, 0.5))
    H['kid'] = person('kid', (0.25, 0.0, 0), seed=4, h=0.022, col=(0.9, 0.7, 0.2))
    for i, x in enumerate((-0.12, 0.0, 0.14, 0.26)):
        cyl(f'pot{i}', 0.004, 0.006, (x, 0.04, 0), clay('pot', (0.6, 0.32, 0.2)), seg=12, r2=0.0034)
        ico(f'potp{i}', 0.006, (x, 0.04, 0.01), felt('plant', (0.22, 0.38, 0.16)), sub=2, jitter=0.3, seed=i, scale=(1, 1, 1.2))
    lan = emit('lantern', (0.9, 0.15, 0.08), 3.0)
    for i, x in enumerate((-0.08, 0.2)):
        cyl(f'lanterncord{i}', 0.0002, 0.012, (x, 0.04, 0.085), clay('wire', (0.05, 0.05, 0.05)), seg=4)
        sphere(f'lantern{i}', 0.0045, (x, 0.04, 0.08), lan, seg=16, scale=(1, 1, 0.85))
    return H


def lane_tick(H, f, t):
    sway(H['cloth'], f, t)
    animate_steam(H['steam'], (0.081, 0.022, 0.036), t, rise=0.06, speed=0.22)
    walker(H['man'], t, [(0, (-0.2, -0.012, 0)), (12, (0.05, -0.016, 0))])
    walker(H['kid'], t, [(0, (0.26, 0.005, 0)), (12, (0.16, 0.0, 0))], step=3.0)


@shot
def l1_lane_wide():
    H = lane_morning_common()
    cam = camera((-0.12, -0.12, 0.40), (0.04, 0.01, 0.0), lens=45, fstop=2.8)
    jit = Jitter(11, 0.0002)
    def update(f, t):
        lane_tick(H, f, t)
        cp = path([(0, (-0.15, -0.085, 0.40)), (8, (-0.08, -0.08, 0.38))], t)
        tg = path([(0, (0.02, 0.01, 0.0)), (8, (0.07, 0.01, 0.0))], t)
        aim(cam, cp + jit.v(f), tg)
        cam.data.dof.focus_distance = (cp - tg).length
    return 8.0, update


@shot
def l2_laundry():
    H = lane_morning_common()
    cam = camera((-0.07, -0.03, 0.035), (0.0, 0.0, 0.08), lens=32, fstop=2.8)
    jit = Jitter(12, 0.00015)
    def update(f, t):
        lane_tick(H, f, t)
        set_lit(H['lit'], max(0.0, 0.06 - t * 0.01))   # night lights switching off as morning arrives
        cp = path([(0, (-0.08, -0.03, 0.034)), (8, (-0.03, -0.025, 0.04))], t)
        tg = path([(0, (0.0, 0.0, 0.08)), (8, (0.06, 0.0, 0.085))], t)
        aim(cam, cp + jit.v(f), tg)
        cam.data.dof.focus_distance = 0.11
    return 8.0, update


@shot
def l3_stall():
    H = lane_morning_common()
    c = Claude((-0.02, -0.012, 0), facing=0)
    cam = camera((-0.09, -0.03, 0.034), (0.07, 0.01, 0.02), lens=45, fstop=2.2)
    jit = Jitter(13, 0.00012)
    def update(f, t):
        lane_tick(H, f, t)
        x = path([(0, 0.022), (4.5, 0.062)], t)
        walking = t < 4.5
        fac = -1.2 if walking else path([(4.5, -1.2), (5.2, math.pi - 0.5)], t)
        hop = 0.0
        if 7.0 < t < 8.0: hop = abs(math.sin((t - 7.0) * math.pi * 2)) * 0.008
        c.pose(f, loc=(x, -0.006, hop), facing=fac, hop=1.0 if walking else 0.0, phase=t * 2.4,
               tilt=(-0.3 if 5.3 < t < 7.0 else 0.0), blink=(9.0 < t < 9.15))
        cp = path([(0, (-0.09, -0.03, 0.034)), (10, (-0.06, -0.032, 0.036))], t)
        tg = path([(0, (0.02, -0.004, 0.018)), (4.5, (0.065, 0.004, 0.024)), (10, (0.075, 0.008, 0.028))], t)
        aim(cam, cp + jit.v(f), tg)
        cam.data.dof.focus_distance = (cp - Vector((x, -0.006, 0.02))).length
    return 10.0, update


@shot
def l4_cat():
    H = lane_morning_common()
    c = Claude((0.014, -0.028, 0), facing=2.3)
    bpy.data.objects['Fog'].hide_render = True   # the haze volume confuses EEVEE's depth of field at this distance
    cat_root, cat_mesh = H['cat']
    cat_root.location = (0.043, -0.03, 0); cat_root.rotation_euler.z = math.pi + 0.5
    cam = camera((0.03, 0.04, 0.022), (0.028, -0.028, 0.017), lens=30, fstop=11)
    bike = bpy.data.objects['bike']
    jit = Jitter(14, 0.0001)
    def update(f, t):
        lane_tick(H, f, t)
        # Claude leans in, cat sniffs, Claude's little wave (body rock)
        lean = path([(0, 0.0), (2.0, 0.0), (2.6, 0.18), (4.0, 0.18), (4.4, 0.0)], t)
        rock = 0.15 * math.sin((t - 4.5) * 9) if 4.5 < t < 5.8 else 0.0
        c.pose(f, tilt=lean, look=rock, squash=(1.0 if 5.9 < t < 6.0 else 0.0), blink=(1.2 < t < 1.3 or 6.3 < t < 6.4))
        cat_mesh.rotation_euler.y = path([(0, 0), (2.4, 0), (3.0, 0.12), (4.2, 0.12), (4.6, 0)], t)
        cp = path([(0, (0.024, 0.042, 0.022)), (7, (0.032, 0.036, 0.021))], t)
        aim(cam, cp + jit.v(f), (0.028, -0.028, 0.018))
        cam.data.dof.focus_distance = (cp - Vector((0.02, -0.027, 0.015))).length
    return 7.0, update


# ================================================================ the river: Bund + Pudong

def sky(c_low, c_top, strength):
    """Animated gradient world: returns a setter(c_low, c_top, strength)."""
    bg = world(c_low, strength, top=c_top)
    nt = bpy.context.scene.world.node_tree
    ramp = [n for n in nt.nodes if n.type == 'VALTORGB'][0]
    def setter(lo, tp, st):
        ramp.color_ramp.elements[0].color = (*lo, 1)
        ramp.color_ramp.elements[1].color = (*tp, 1)
        bg.inputs['Strength'].default_value = st
    return setter


def set_river():
    H = {}
    box('Base', (3, 3, 0.01), (0, 0.3, -0.012), wood('table'), bev=0)
    H['water'] = water('river', (0.07, 0.13, 0.13), wave_scale=40)
    box('River', (2.4, 0.36, 0.004), (0, 0.30, -0.004), H['water'], bev=0)
    stone = clay('embank', (0.6, 0.57, 0.52), rough=0.85)
    box('BundGround', (2.4, 0.5, 0.004), (0, -0.13, -0.004), ground('road', (0.33, 0.32, 0.31)), bev=0)
    box('Promenade', (2.4, 0.04, 0.012), (0, 0.105, -0.004), clay('prom', (0.72, 0.66, 0.58), rough=0.85), bev=0.001)
    box('EmbankB', (2.4, 0.006, 0.014), (0, 0.124, -0.006), stone, bev=0.0008)
    railing('Rail', -1.2, 1.2, 0.121, h=0.008)
    box('PudongGround', (2.4, 0.6, 0.004), (0, 0.78, -0.004), felt('grass', (0.25, 0.36, 0.17)), bev=0)
    box('EmbankP', (2.4, 0.006, 0.01), (0, 0.48, -0.006), stone, bev=0.0008)
    bund, bmats = bund_row(origin=(0, -0.0, 0))
    bund.rotation_euler.z = math.pi
    H['bund_mats'] = bmats
    pd, pmats = pudong(origin=(0.05, 0.64, 0))
    H['pd_mats'] = pmats
    # old town blocks behind the Bund
    rnd = random.Random(8)
    for i in range(14):
        m = windows(f'old{i % 3}', wall=[(0.62, 0.55, 0.48), (0.55, 0.5, 0.46), (0.7, 0.64, 0.55)][i % 3], glass_c=(0.15, 0.13, 0.12),
                    cols=60, rows=60, frame=0.28, lit=(1, 0.75, 0.45), lit_strength=2.5, seed=i % 3)
        H['bund_mats'].append(m)
        box(f'old{i}', (rnd.uniform(0.06, 0.11), 0.08, rnd.uniform(0.08, 0.2)), (-0.55 + i * 0.085, -0.17 - rnd.uniform(0, 0.08), 0), m, bev=0.001)
    # promenade trees & lamps
    H['lamps'] = []
    for i in range(14):
        x = -0.6 + i * 0.09
        if not (-0.02 < x < 0.1): plane_tree(f'pt{i}', (x, 0.07, 0), h=0.05, seed=i + 40, autumn=0.2)
        if 0.06 < x + 0.045 < 0.09: continue
        r, g, l = street_lamp(f'pl{i}', (x + 0.045, 0.112, 0.008), h=0.022, power=0.0)
        H['lamps'].append((g, l))
    # floodlights for the Bund facades (night)
    H['flood'] = []
    for i in range(7):
        H['flood'].append(spot(f'flood{i}', (-0.42 + i * 0.14, 0.10, 0.012), (-0.42 + i * 0.14, 0.0, 0.12), power=0.0, angle=1.2,
                                color=(1.0, 0.72, 0.4), radius=0.01, blend=1.0))
    H['ferry'], H['ferry_win'] = ferry('Ferry', (0.0, 0.2, -0.002), rot=math.pi / 2)
    H['ferry2'], _ = ferry('Ferry2', (0.5, 0.33, -0.002), rot=0.0, color=(0.85, 0.82, 0.74))
    # people on the promenade
    H['folk'] = [person(f'pp{i}', (x, 0.1 + 0.01 * (i % 2), 0.008), rot=random.Random(i).uniform(0, 6), seed=i + 10, h=0.016)
                 for i, x in enumerate([-0.42, -0.33, -0.26, -0.17, -0.09, 0.2, 0.27, 0.36, 0.45])]
    H['sun'] = sun_from('Sun', (0.4, 0.8, 0.6), power=3.5, color=(1.0, 0.85, 0.65), angle=0.03)
    H['fill'] = area('Fill', (0, -0.5, 0.8), (0, 0.3, 0), power=4, size=2.0, color=(0.75, 0.85, 1.0))
    H['sky'] = sky((0.9, 0.82, 0.72), (0.45, 0.62, 0.85), 0.5)
    H['haze'], H['haze_v'] = fog((2.4, 1.2, 0.8), (0, 0.6, 0.4), density=0.08, color=(1.0, 0.9, 0.8))
    H['moon'] = area('Moon', (-0.5, -0.3, 0.9), (0, 0.3, 0), power=0.0, size=2.0, color=(0.5, 0.6, 1.0))
    return H


def river_time(H, u):
    """u: 0 = afternoon, 0.5 = golden dusk, 1 = night. Drives sun, sky, windows, floods, lamps."""
    def k(*vals):
        return path([(0, vals[0]), (0.5, vals[1]), (1.0, vals[2])], u, fn=lambda x: x)
    H['sun'].data.energy = k(3.5, 2.6, 0.0)
    H['sun'].data.color = tuple(k((1.0, 0.85, 0.65), (1.0, 0.55, 0.3), (1.0, 0.4, 0.3)))
    dirv = k((0.4, 0.8, 0.6), (-0.2, 1.0, 0.18), (-0.3, 1.0, -0.05))
    H['sun'].rotation_euler = Vector(dirv).normalized().to_track_quat('Z', 'Y').to_euler()
    H['sky'](tuple(k((0.9, 0.82, 0.72), (1.0, 0.55, 0.38), (0.05, 0.05, 0.11))), tuple(k((0.45, 0.62, 0.85), (0.4, 0.35, 0.55), (0.012, 0.016, 0.045))),
             k(0.5, 0.45, 0.35))
    H['fill'].data.energy = k(4.0, 2.0, 0.8)
    H['fill'].data.color = tuple(k((0.75, 0.85, 1.0), (0.8, 0.7, 0.9), (0.4, 0.5, 1.0)))
    lit = ease((u - 0.35) / 0.55)
    set_city_lit(H['pd_mats'], lit * 0.35)
    set_lit(H['pd_mats']['pearl'], 1.0 if u > 0.55 else 0.0)
    for m in H['bund_mats']: set_lit(m, lit * 0.5)
    set_lit(H['ferry_win'], 1.0 if u > 0.45 else 0.0)
    for i, sp in enumerate(H['flood']):
        sp.data.energy = 0.6 * ease((u - 0.55 - i * 0.03) / 0.15)
    for i, (g, l) in enumerate(H['lamps']):
        on = 1.0 if u > 0.5 + (i % 5) * 0.02 else 0.0
        l.data.energy = 0.012 * on
        g.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 12 * on
    H['haze_v'].inputs['Density'].default_value = k(0.08, 0.12, 0.06)
    H['moon'].data.energy = k(0.0, 0.0, 1.5)
    H['haze_v'].inputs['Color'].default_value = (*k((1.0, 0.9, 0.8), (1.0, 0.7, 0.5), (0.4, 0.45, 0.7)), 1)


def river_tick(H, f, t, ferry_keys=None):
    set_water(H['water'], t * 0.15)
    if ferry_keys:
        H['ferry'].location = path(ferry_keys, t)
    H['ferry2'].location.x = 0.5 - t * 0.012
    for i, p in enumerate(H['folk']):
        p.location.x += (0.0006 if i % 2 else -0.0005)


@shot
def b1_river_wide():
    H = set_river()
    river_time(H, 0.05)
    cam = camera((-0.85, 0.22, 0.28), (0.05, 0.33, 0.06), lens=40, fstop=2.8)
    jit = Jitter(21, 0.0004)
    def update(f, t):
        river_tick(H, f, t, [(0, (0.0, 0.17, -0.002)), (8, (0.02, 0.36, -0.002))])
        cp = path([(0, (-0.85, 0.20, 0.28)), (8, (-0.78, 0.25, 0.25))], t)
        aim(cam, cp + jit.v(f), (0.05, 0.33, 0.06))
        cam.data.dof.focus_distance = (cp - Vector((-0.05, 0.3, 0.05))).length
    return 8.0, update


@shot
def b2_bund_claude():
    """Claude at the railing, back to us; focus racks from Claude to Pudong."""
    H = set_river()
    river_time(H, 0.3)
    c = Claude((0.052, 0.115, 0.008), facing=math.pi, scale=0.8)
    cam = camera((0.04, 0.06, 0.03), (0.06, 0.4, 0.012), lens=28, fstop=2.0)
    jit = Jitter(22, 0.00012)
    def update(f, t):
        river_tick(H, f, t, [(0, (0.06, 0.40, -0.002)), (8, (0.03, 0.25, -0.002))])
        c.pose(f, look=path([(0, 0), (4, 0), (5, -0.25), (6.5, -0.25), (7.2, 0)], t), blink=(2.0 < t < 2.12))
        cp = path([(0, (0.04, 0.058, 0.03)), (8, (0.043, 0.062, 0.031))], t)
        aim(cam, cp + jit.v(f), (0.06, 0.4, 0.012))
        cam.data.dof.focus_distance = path([(0, 0.062), (3.0, 0.062), (5.0, 0.55), (8, 0.55)], t)
    return 8.0, update


@shot
def b3_ferry():
    H = set_river()
    river_time(H, 0.42)
    cam = camera((0.05, 0.13, 0.03), (0.06, 0.6, 0.05), lens=30, fstop=2.8)
    jit = Jitter(23, 0.0002)
    def update(f, t):
        river_tick(H, f, t, [(0, (-0.07, 0.29, -0.002)), (6, (0.16, 0.29, -0.002))])
        H['ferry'].rotation_euler.z = 0.015 * math.sin(t * 2)
        H['ferry'].rotation_euler.x = 0.012 * math.sin(t * 2.7)
        fp = H['ferry'].location
        cp = path([(0, (0.04, 0.125, 0.03)), (6, (0.08, 0.13, 0.032))], t)
        tg = path([(0, (0.02, 0.6, 0.05)), (6, (0.1, 0.6, 0.05))], t)
        aim(cam, cp + jit.v(f), tg)
        cam.data.dof.focus_distance = (cp - Vector((fp.x, 0.29, 0.01))).length
    return 6.0, update


@shot
def d1_lights():
    """Time-lapse: afternoon to night, lights come on one by one."""
    H = set_river()
    cam = camera((-0.95, 0.3, 0.42), (0.15, 0.38, 0.08), lens=40, fstop=3.2)
    jit = Jitter(24, 0.0002)
    def update(f, t):
        u = ease_io(min(1, t / 9.0)) * 0.98 + 0.02
        river_time(H, u)
        river_tick(H, f, t, [(0, (-0.3, 0.2, -0.002)), (10, (-0.25, 0.4, -0.002))])
        cp = path([(0, (-0.96, 0.3, 0.43)), (10, (-0.88, 0.31, 0.39))], t)
        aim(cam, cp + jit.v(f), (0.15, 0.38, 0.08))
        cam.data.dof.focus_distance = (cp - Vector((-0.05, 0.36, 0.08))).length
    return 10.0, update


@shot
def d2_night_claude():
    H = set_river()
    river_time(H, 1.0)
    H['haze'].hide_render = True
    c = Claude((0.052, 0.116, 0.008), facing=math.pi - 0.15, scale=0.8)
    area('ClaudeFill', (0.03, 0.06, 0.05), (0.052, 0.116, 0.02), power=0.015, size=0.05, color=(1.0, 0.72, 0.45))
    cam = camera((0.04, 0.06, 0.03), (0.05, 0.4, 0.012), lens=28, fstop=3.5)
    jit = Jitter(25, 0.0001)
    def update(f, t):
        river_tick(H, f, t, [(0, (-0.1, 0.36, -0.002)), (8, (0.05, 0.36, -0.002))])
        H['ferry'].rotation_euler.z = 0.0
        c.pose(f, look=path([(0, 0.0), (3, 0.0), (3.8, 0.3), (6, 0.3), (6.8, 0.0)], t))
        cp = path([(0, (0.04, 0.058, 0.03)), (8, (0.038, 0.064, 0.029))], t)
        aim(cam, cp + jit.v(f), (0.05, 0.4, 0.012))
        cam.data.dof.focus_distance = path([(0, 0.5), (2.5, 0.5), (4.5, 0.062), (8, 0.062)], t)
    return 8.0, update


# ================================================================ epilogue

@shot
def e1_desk_back():
    H = set_desk()
    lamp_level(H, 1.0)
    for h in H['pieces']: h.rotation_euler.x = 0
    c = Claude((0.03, -0.098, 0.0125), facing=0.1)
    cam = camera((0.04, -0.17, 0.03), (0.03, -0.09, 0.03), lens=55, fstop=2.2)
    jit = Jitter(31, 0.00015)
    def update(f, t):
        set_lit(H['cardwin'], ease((t - 1.0) / 6.0))
        # Claude sits at the page edge, legs dangling
        for i, l in enumerate(c.legs): l.rotation_euler.x = -1.25 + 0.2 * math.sin(t * 3 + i * 2)
        c.pose(f, blink=(4.0 < t < 4.12 or 8.6 < t < 8.72))
        for i, l in enumerate(c.legs): l.rotation_euler.x = -1.25 + 0.2 * math.sin(t * 3 + i * 2); l.location.z = 0.003
        c.body.location.z = 0.0
        cp = path([(0, (0.04, -0.17, 0.03)), (10, (0.09, -0.42, 0.17))], t)
        tg = path([(0, (0.03, -0.095, 0.025)), (10, (0.0, -0.02, 0.04))], t)
        aim(cam, cp + jit.v(f), tg)
        cam.data.dof.focus_distance = (cp - Vector((0.03, -0.095, 0.02))).length
        animate_steam(H['steam'], (0.26, -0.13, 0.055), t, rise=0.09, speed=0.12, drift=(0.01, 0.004, 0))
    return 10.0, update


@shot
def e2_lamp_off():
    H = set_desk()
    for h in H['pieces']: h.rotation_euler.x = 0
    c = Claude((0.03, -0.098, 0.0125), facing=0.1)
    cam = camera((0.09, -0.42, 0.17), (0.0, -0.02, 0.04), lens=55, fstop=2.8)
    jit = Jitter(32, 0.0001)
    def update(f, t):
        set_lit(H['cardwin'], 1.0)
        v = 1.0 if t < 2.0 else (0.4 if t < 2.1 else 0.0)
        lamp_level(H, v)
        H['fill'].data.energy = 0.6 if t < 2 else 0.35
        c.pose(f, blink=(4.5 < t < 4.62))
        for i, l in enumerate(c.legs): l.rotation_euler.x = -1.25 + 0.2 * math.sin(t * 3 + i * 2); l.location.z = 0.003
        c.body.location.z = 0.0
        cp = path([(0, (0.09, -0.42, 0.17)), (7, (0.095, -0.44, 0.18))], t)
        aim(cam, cp + jit.v(f), (0.0, -0.02, 0.04))
        cam.data.dof.focus_distance = (cp - Vector((0.02, -0.06, 0.03))).length
    return 7.0, update
