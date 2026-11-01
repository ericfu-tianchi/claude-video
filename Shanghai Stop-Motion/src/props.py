"""Miniature set pieces for 'Shanghai, as I read it'."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler
from lib import *
from lib import _obj_from_bm

# ================================================================ the narrator

def spark_mesh(name, r=0.016, thick=0.005, rays=11, seed=3, mat=None):
    """Claude's spark: an irregular starburst of rounded rays."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    pts = []
    base = [i * 2 * math.pi / rays + rnd.uniform(-0.12, 0.12) for i in range(rays)]
    for i, a in enumerate(base):
        ro = r * rnd.uniform(0.82, 1.0)
        nxt = base[(i + 1) % rays] + (2 * math.pi if i == rays - 1 else 0)
        mid = (a + nxt) / 2
        w = 0.11
        pts.append((math.cos(a - w) * ro * 0.92, math.sin(a - w) * ro * 0.92))
        pts.append((math.cos(a) * ro, math.sin(a) * ro))
        pts.append((math.cos(a + w) * ro * 0.92, math.sin(a + w) * ro * 0.92))
        pts.append((math.cos(mid) * r * 0.30, math.sin(mid) * r * 0.30))
    n = len(pts)
    front = [bm.verts.new((x, -thick / 2, z)) for x, z in pts]
    back = [bm.verts.new((x, thick / 2, z)) for x, z in pts]
    cf = bm.verts.new((0, -thick / 2, 0)); cb = bm.verts.new((0, thick / 2, 0))
    for k in range(n):
        a, b = k, (k + 1) % n
        bm.faces.new([cf, front[b], front[a]])
        bm.faces.new([cb, back[a], back[b]])
        bm.faces.new([front[a], front[b], back[b], back[a]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    bm.to_mesh(o.data); bm.free(); link(o)
    if mat: o.data.materials.append(mat)
    md = o.modifiers.new('bev', 'BEVEL'); md.width = thick * 0.42; md.segments = 4; md.limit_method = 'ANGLE'; md.angle_limit = 0.6
    for p in o.data.polygons: p.use_smooth = True
    return o


class Claude:
    """A small terracotta-clay spark on two stubby legs. ~3.4 cm tall."""
    def __init__(self, loc=(0, 0, 0), facing=0.0, scale=1.0):
        orange = clay('claude_clay', CLAUDE_ORANGE, rough=0.5, var=0.02, bump=0.35, sss=0.25)
        dark = clay('claude_eye', (0.05, 0.035, 0.03), rough=0.25, var=0, bump=0)
        legm = clay('claude_leg', (0.62, 0.27, 0.16), rough=0.6, var=0.02)
        self.root = bpy.data.objects.new('ClaudeRoot', None); link(self.root)
        self.body = bpy.data.objects.new('ClaudeBody', None); link(self.body)
        self.body.parent = self.root
        self.spark = spark_mesh('ClaudeSpark', mat=orange)
        self.spark.parent = self.body; self.spark.location = (0, 0, 0.0165)
        self.eyes = []
        for i, x in enumerate((-0.0042, 0.0042)):
            e = sphere(f'ClaudeEye{i}', 0.0013, (x, -0.0032, 0.018), dark, seg=12, scale=(1, 0.5, 1.25))
            e.parent = self.body; self.eyes.append(e)
        self.legs = []
        for i, x in enumerate((-0.0035, 0.0035)):
            l = cyl(f'ClaudeLeg{i}', 0.0016, 0.006, (x, 0, 0.0), legm, seg=12, r2=0.0013)
            l.parent = self.root
            f = sphere(f'ClaudeFoot{i}', 0.0021, (0, -0.0006, 0.0006), legm, seg=12, scale=(1, 1.4, 0.55))
            f.parent = l
            self.legs.append(l)
        self.root.location = loc; self.root.rotation_euler = (0, 0, facing)
        self.root.scale = (scale,) * 3
        self.jit = Jitter(seed=77, amp=0.00012)

    def pose(self, frame, loc=None, facing=None, hop=0.0, phase=0.0, squash=0.0, look=0.0, blink=False, tilt=0.0):
        """hop: 0..1 height factor of a little bounce; phase drives the walk cycle."""
        if loc is not None: self.root.location = Vector(loc)
        if facing is not None: self.root.rotation_euler.z = facing
        lift = abs(math.sin(phase * math.pi)) * 0.004 * hop
        sq = 1 - 0.12 * squash
        self.body.location = Vector((0, 0, 0.005 + lift)) + self.jit.v(frame)
        self.body.scale = (1 + 0.06 * squash, 1, sq)
        self.body.rotation_euler = (tilt, 0, look)
        sw = math.sin(phase * math.pi * 2) * 0.35 * hop
        for i, l in enumerate(self.legs):
            s = sw if i == 0 else -sw
            l.rotation_euler = (s, 0, 0)
            l.location.z = 0.0008 + max(0, math.sin(phase * math.pi * 2 + (0 if i else math.pi))) * 0.0022 * hop
        for e in self.eyes:
            e.scale = (1, 0.5, 0.15 if blink else 1.25)
        # rays shimmer very slightly, like clay re-pressed between frames
        self.spark.rotation_euler = (0, 0.03 * self.jit.s(frame, 5), 0)

# ================================================================ townsfolk

PEOPLE_COLORS = [(0.55, 0.22, 0.18), (0.25, 0.32, 0.45), (0.78, 0.68, 0.5), (0.35, 0.42, 0.3),
                 (0.85, 0.82, 0.76), (0.6, 0.45, 0.55), (0.2, 0.2, 0.22), (0.72, 0.5, 0.25)]
SKIN = (0.86, 0.66, 0.5)


def person(name, loc, rot=0.0, h=0.032, col=None, seed=0, hair=(0.08, 0.06, 0.05), sit=False, umbrella=None):
    rnd = random.Random(seed)
    col = col or rnd.choice(PEOPLE_COLORS)
    root = bpy.data.objects.new(name, None); link(root)
    body_m = clay(f'cloth_{col}', col, rough=0.75, var=0.05)
    pants_m = clay(f'pants_{seed % 3}', [(0.15, 0.15, 0.18), (0.3, 0.27, 0.24), (0.22, 0.25, 0.32)][seed % 3], rough=0.8)
    skin_m = clay('skin', SKIN, rough=0.5, sss=0.3)
    hair_m = clay(f'hair_{hair}', hair, rough=0.6)
    parts = []
    leg_h = h * (0.25 if sit else 0.42)
    parts.append(cyl(name + '_legs', h * 0.11, leg_h, (0, 0, 0), pants_m, seg=12, r2=h * 0.12))
    torso = cyl(name + '_torso', h * 0.15, h * 0.36, (0, 0, leg_h), body_m, seg=16, r2=h * 0.11)
    parts.append(torso)
    head = sphere(name + '_head', h * 0.12, (0, 0, leg_h + h * 0.36 + h * 0.12), skin_m, seg=16)
    parts.append(head)
    hr = sphere(name + '_hair', h * 0.125, (0, h * 0.02, leg_h + h * 0.36 + h * 0.15), hair_m, seg=16, scale=(1, 1, 0.8))
    parts.append(hr)
    for p in parts: p.parent = root
    if umbrella:
        um = clay(f'umb_{umbrella}', umbrella, rough=0.4, var=0.03)
        u = cyl(name + '_umb', h * 0.55, h * 0.12, (h * 0.05, 0, h * 1.05), um, seg=10, r2=0.0003, smooth=False)
        st = cyl(name + '_stick', 0.0004, h * 0.5, (h * 0.05, 0, h * 0.58), metal('stick', (0.2, 0.2, 0.2)), seg=6)
        u.parent = root; st.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root

# ================================================================ lane (lilong / shikumen)

def shikumen_row(name, n=5, origin=(0, 0, 0), unit_w=0.062, depth=0.11, floors=2, floor_h=0.058, seed=1,
                 facing=0.0, lit=None):
    """A row of attached shikumen houses whose front faces -Y. Returns (root, window objects)."""
    rnd = random.Random(seed)
    root = bpy.data.objects.new(name, None); link(root)
    grey = brick(name + 'grey', (0.50, 0.47, 0.43), (0.42, 0.40, 0.37), (0.56, 0.53, 0.49), scale=150)
    red = brick(name + 'red', (0.58, 0.27, 0.18), (0.48, 0.22, 0.15), (0.6, 0.5, 0.44), scale=150)
    stone = clay('stone', (0.74, 0.70, 0.63), rough=0.8, var=0.04)
    door = paint('door_black', (0.05, 0.045, 0.045), rough=0.35)
    brass = metal('brass', (0.8, 0.6, 0.3), 0.35)
    frame_m = paint('win_frame', (0.32, 0.18, 0.1), rough=0.5)
    roof_m = tile_roof_mat('roof_tile', (0.16, 0.10, 0.08))
    lit = lit or lit_obj_mat('lane_lit')
    ac_m = paint('ac', (0.88, 0.87, 0.84), rough=0.4)
    plant_m = felt('plant', (0.22, 0.38, 0.16))
    pot_m = clay('pot', (0.6, 0.32, 0.2))
    parts, wins = [], []
    H = floors * floor_h
    for i in range(n):
        x = (i - (n - 1) / 2) * unit_w
        hvar = rnd.uniform(-0.003, 0.003)
        parts.append(box(f'{name}_wall{i}', (unit_w - 0.0006, depth, H + hvar), (x, 0, 0), grey, bev=0.0008))
        # red brick bands
        for k in range(floors):
            parts.append(box(f'{name}_band{i}{k}', (unit_w - 0.0004, 0.002, 0.006), (x, -depth / 2 - 0.0008, k * floor_h + floor_h - 0.006), red, bev=0.0004))
        # gate: stone frame + black double door + pediment
        gw, gh = 0.026, 0.040
        parts.append(box(f'{name}_gf{i}', (gw + 0.008, 0.004, gh + 0.004), (x, -depth / 2 - 0.0015, 0), stone, bev=0.0008))
        for s in (-1, 1):
            parts.append(box(f'{name}_dl{i}{s}', (gw / 2 - 0.0006, 0.002, gh - 0.002), (x + s * gw / 4, -depth / 2 - 0.0034, 0.0004), door, bev=0.0004))
            parts.append(torus(f'{name}_ring{i}{s}', 0.0013, 0.00025, (x + s * 0.0022, -depth / 2 - 0.0048, gh * 0.55), brass, rot=(math.pi / 2, 0, 0)))
        ped = cyl(f'{name}_ped{i}', gw * 0.62, 0.004, (x, -depth / 2 - 0.0015, gh + 0.002), stone, seg=24, rot=(math.pi / 2, 0, 0))
        ped.scale = (1, 0.45, 1); ped.location.y += 0.002
        parts.append(ped)
        parts.append(box(f'{name}_lintel{i}', (gw + 0.012, 0.006, 0.004), (x, -depth / 2 - 0.002, gh), stone, bev=0.0006))
        # windows on upper floors
        for k in range(1, floors):
            for j, wx in enumerate((-0.016, 0.016)):
                z = k * floor_h + 0.014
                ww, wh = 0.016, 0.024
                parts.append(box(f'{name}_wf{i}{k}{j}', (ww + 0.003, 0.003, wh + 0.003), (x + wx, -depth / 2 - 0.0008, z - 0.0015), frame_m, bev=0.0005))
                pane = box(f'{name}_wp{i}{k}{j}', (ww, 0.0012, wh), (x + wx, -depth / 2 - 0.0022, z), lit, bev=0)
                wins.append(pane)
                # mullions
                parts.append(box(f'{name}_mu{i}{k}{j}', (0.0008, 0.002, wh), (x + wx, -depth / 2 - 0.0028, z), frame_m, bev=0))
                parts.append(box(f'{name}_mh{i}{k}{j}', (ww, 0.002, 0.0008), (x + wx, -depth / 2 - 0.0028, z + wh * 0.62), frame_m, bev=0))
                # sill + occasional plant
                parts.append(box(f'{name}_sill{i}{k}{j}', (ww + 0.005, 0.006, 0.0015), (x + wx, -depth / 2 - 0.003, z - 0.003), stone, bev=0.0004))
                if rnd.random() < 0.35:
                    parts.append(cyl(f'{name}_pot{i}{k}{j}', 0.0025, 0.004, (x + wx + rnd.uniform(-0.004, 0.004), -depth / 2 - 0.004, z - 0.0016), pot_m, seg=10, r2=0.0021))
                    parts.append(ico(f'{name}_pl{i}{k}{j}', 0.004, (x + wx + rnd.uniform(-0.004, 0.004), -depth / 2 - 0.004, z + 0.0038), plant_m, sub=2, jitter=0.25, seed=i * 9 + j, scale=(1, 0.8, 0.9)))
            if rnd.random() < 0.55:
                parts.append(box(f'{name}_ac{i}{k}', (0.014, 0.008, 0.009), (x + rnd.choice((-0.016, 0.016)), -depth / 2 - 0.004, k * floor_h + 0.042), ac_m, bev=0.0008))
        # back facade: kitchen windows + AC
        for k in range(floors):
            for wx in (-0.015, 0.017):
                z = k * floor_h + 0.016
                parts.append(box(f'{name}_bwf{i}{k}{wx}', (0.015, 0.003, 0.02), (x + wx, depth / 2 + 0.0008, z - 0.0015), frame_m, bev=0.0005))
                pane = box(f'{name}_bwp{i}{k}{wx}', (0.012, 0.0012, 0.016), (x + wx, depth / 2 + 0.0022, z + 0.0005), lit, bev=0)
                wins.append(pane)
            if rnd.random() < 0.5:
                parts.append(box(f'{name}_bac{i}{k}', (0.014, 0.008, 0.009), (x, depth / 2 + 0.004, k * floor_h + 0.04), ac_m, bev=0.0008))
        # roof
        parts.append(prism_roof(f'{name}_roof{i}', unit_w, depth, 0.03, (x, 0, H + hvar), roof_m, overhang=0.003))
        # ground floor window by the gate
    j = join(parts, name + '_mesh'); j.parent = root
    for w in wins: w.parent = root
    root.location = origin; root.rotation_euler = (0, 0, facing)
    return root, wins


def laundry_line(name, a, b, colors, seed=0, sag=0.004):
    """Bamboo pole with hanging clothes. Returns list of cloth objects for sway animation."""
    rnd = random.Random(seed)
    bamboo = clay('bamboo', (0.72, 0.62, 0.38), rough=0.5)
    a, b = Vector(a), Vector(b)
    d = (b - a); L = d.length
    pole = cyl(name + '_pole', 0.0007, L, a, bamboo, seg=8)
    pole.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    cloths = []
    nclo = max(2, int(L / 0.011))
    for k in range(nclo):
        t = (k + 0.5) / nclo + rnd.uniform(-0.02, 0.02)
        p = a.lerp(b, t)
        c = rnd.choice(colors)
        w = rnd.uniform(0.006, 0.010); h = rnd.uniform(0.009, 0.016)
        m = felt(f'cloth_{c}', c, var=0.08)
        kind = rnd.choice(['shirt', 'pants', 'towel', 'shirt'])
        if kind == 'shirt':
            pts = [(-w * 0.5, 0), (-w * 0.95, -h * 0.25), (-w * 0.75, -h * 0.4), (-w * 0.45, -h * 0.28), (-w * 0.45, -h),
                   (w * 0.45, -h), (w * 0.45, -h * 0.28), (w * 0.75, -h * 0.4), (w * 0.95, -h * 0.25), (w * 0.5, 0), (w * 0.15, 0), (0, -h * 0.1), (-w * 0.15, 0)]
        elif kind == 'pants':
            pts = [(-w * 0.45, 0), (w * 0.45, 0), (w * 0.5, -h * 1.3), (w * 0.08, -h * 1.3), (0, -h * 0.4), (-w * 0.08, -h * 1.3), (-w * 0.5, -h * 1.3)]
        else:
            pts = [(-w * 0.4, 0), (w * 0.4, 0), (w * 0.4, -h * 1.1), (-w * 0.4, -h * 1.1)]
        o = flat_shape(f'{name}_c{k}', pts, 0.0005, m)
        for v in o.data.vertices:
            v.co.y += math.sin(v.co.x / w * 3 + k) * 0.0005
        o.rotation_euler = (0, 0, math.atan2(d.y, d.x))
        o.location = p
        o['base_rot'] = tuple(o.rotation_euler)
        cloths.append(o)
    return pole, cloths


def sway(objs, frame, t, amp=0.15, speed=1.3):
    for i, o in enumerate(objs):
        br = o['base_rot']
        o.rotation_euler = (br[0] + amp * math.sin(t * speed + i * 1.7) * 0.6, br[1], br[2] + amp * 0.3 * math.sin(t * speed * 0.7 + i))


def bicycle(name, loc, rot=0.0, color=(0.15, 0.25, 0.22)):
    root = bpy.data.objects.new(name, None); link(root)
    fm = metal(f'bike_{color}', color, 0.35)
    tyre = clay('tyre', (0.05, 0.05, 0.05), rough=0.8, bump=0)
    R = 0.0085
    parts = []
    for i, x in enumerate((-0.012, 0.012)):
        parts.append(torus(f'{name}_w{i}', R, 0.0008, (x, 0, R + 0.0008), tyre, rot=(math.pi / 2, 0, 0)))
        parts.append(torus(f'{name}_h{i}', 0.0012, 0.0004, (x, 0, R + 0.0008), fm, rot=(math.pi / 2, 0, 0)))
    z = R + 0.0008
    pts = [(-0.012, 0, z), (-0.002, 0, z + 0.011), (0.009, 0, z + 0.011), (0, 0, z), (-0.012, 0, z)]
    for k in range(len(pts) - 1):
        a, b = Vector(pts[k]), Vector(pts[k + 1]); d = b - a
        c = cyl(f'{name}_f{k}', 0.0006, d.length, a, fm, seg=8)
        c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); parts.append(c)
    for a, b in [((0.009, 0, z + 0.011), (0.012, 0, z)), ((0.009, 0, z + 0.011), (0.0085, 0, z + 0.016)),
                 ((-0.002, 0, z + 0.011), (-0.0025, 0, z + 0.014))]:
        a, b = Vector(a), Vector(b); d = b - a
        c = cyl(f'{name}_g', 0.0006, d.length, a, fm, seg=8); c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); parts.append(c)
    parts.append(box(f'{name}_bar', (0.0012, 0.009, 0.0012), (0.0085, 0, z + 0.016), fm, bev=0.0003))
    parts.append(box(f'{name}_seat', (0.005, 0.0028, 0.0014), (-0.0025, 0, z + 0.014), clay('seat', (0.25, 0.15, 0.1)), bev=0.0006))
    parts.append(box(f'{name}_basket', (0.006, 0.006, 0.004), (0.0125, 0, z + 0.012), clay('wicker', (0.6, 0.45, 0.25), rough=0.9), bev=0.0006))
    j = join(parts, name + '_m'); j.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root


def steam_puffs(name, n, base, seed=0, density=60.0):
    m = bpy.data.materials.new(name + '_m'); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    # radial falloff so each puff is soft-edged
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    nt.links.new(tc.outputs['Object'], ln.inputs[0])
    fall = nt.nodes.new('ShaderNodeMapRange'); fall.inputs['From Min'].default_value = 0.0; fall.inputs['From Max'].default_value = 1.0
    fall.inputs['To Min'].default_value = 1.0; fall.inputs['To Max'].default_value = 0.0
    nt.links.new(ln.outputs['Value'], fall.inputs['Value'])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    nt.links.new(fall.outputs['Result'], mul.inputs[0]); nt.links.new(nz.outputs['Fac'], mul.inputs[1])
    d = nt.nodes.new('ShaderNodeMath'); d.operation = 'MULTIPLY'; d.inputs[1].default_value = density; d.name = 'DENS'
    nt.links.new(mul.outputs[0], d.inputs[0])
    v = nt.nodes.new('ShaderNodeVolumePrincipled'); v.inputs['Color'].default_value = (1, 0.98, 0.95, 1)
    v.inputs['Anisotropy'].default_value = 0.4
    nt.links.new(d.outputs[0], v.inputs['Density'])
    nt.links.new(v.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
    puffs = []
    for i in range(n):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        o = _obj_from_bm(f'{name}{i}', bm, m)
        o.location = base; o['ph'] = i / n; o['r'] = 0.0045; o.scale = (0.004,) * 3
        o.visible_shadow = False
        puffs.append(o)
    return puffs


def animate_steam(puffs, base, t, rise=0.05, speed=0.25, drift=(0.006, 0.0, 0)):
    base = Vector(base)
    for i, o in enumerate(puffs):
        ph = (t * speed + o['ph']) % 1.0
        o.location = base + Vector((drift[0] * ph + 0.003 * math.sin(i * 2.1 + t), drift[1] * ph, rise * ph))
        s = (0.5 + 1.8 * ph) * o.get('r', 0.004)
        fade = min(1, ph * 5) * (1 - ph) ** 0.5
        o.scale = (s * (0.4 + 0.6 * fade) + 1e-5,) * 3
        o.rotation_euler = (i, ph * 3, i * 0.5)


def breakfast_stall(name, loc, rot=0.0):
    root = bpy.data.objects.new(name, None); link(root)
    parts = []
    cart = paint('stall_blue', (0.32, 0.48, 0.55), rough=0.5)
    steel = metal('steel', (0.75, 0.74, 0.72), 0.25)
    wok = metal('wok', (0.12, 0.11, 0.1), 0.4)
    bun = clay('bun', (0.95, 0.9, 0.8), rough=0.6, sss=0.4)
    crisp = clay('bun_base', (0.75, 0.48, 0.22), rough=0.5)
    sign = paint('sign_red', (0.7, 0.12, 0.08), rough=0.4)
    parts.append(box(name + '_cart', (0.05, 0.026, 0.026), (0, 0, 0.004), cart, bev=0.0012))
    for x in (-0.022, 0.022):
        for y in (-0.011, 0.011):
            parts.append(cyl(name + '_leg', 0.0008, 0.004, (x, y, 0), steel, seg=8))
    parts.append(box(name + '_top', (0.052, 0.028, 0.002), (0, 0, 0.03), steel, bev=0.0005))
    pan = cyl(name + '_pan', 0.012, 0.0035, (-0.008, 0, 0.032), wok, seg=32, r2=0.011)
    parts.append(pan)
    rnd = random.Random(4)
    for k in range(12):
        a = k * 2.4; rr = 0.0035 + 0.0055 * math.sqrt(k / 12)
        bx, by = -0.008 + math.cos(a) * rr * 1.2, math.sin(a) * rr * 1.2
        parts.append(sphere(name + f'_bun{k}', 0.0021, (bx, by, 0.0365), bun, seg=12, scale=(1, 1, 0.7)))
    # bamboo steamers stacked
    bam = clay('steamer', (0.78, 0.64, 0.4), rough=0.8)
    for k in range(3):
        parts.append(cyl(name + f'_st{k}', 0.0085, 0.0045, (0.013, 0, 0.032 + k * 0.0046), bam, seg=24, bev=0.0004))
    parts.append(cyl(name + '_lid', 0.0087, 0.002, (0.013, 0, 0.0458), bam, seg=24, r2=0.006))
    # canopy + sign
    for x in (-0.024, 0.024):
        parts.append(cyl(name + '_pole', 0.0006, 0.03, (x, 0.012, 0.03), steel, seg=6))
    parts.append(box(name + '_awn', (0.06, 0.036, 0.002), (0, 0.0, 0.06), felt('awning', (0.85, 0.75, 0.55)), bev=0.0006, rot=(0.15, 0, 0)))
    parts.append(box(name + '_sign', (0.03, 0.002, 0.008), (0, 0.013, 0.048), sign, bev=0.0005))
    j = join(parts, name + '_m'); j.parent = root
    # little glowing bulb
    bulb = sphere(name + '_bulb', 0.0016, (0.0, 0.004, 0.055), emit('bulb', (1, 0.75, 0.45), 30), seg=10)
    bulb.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root

# ================================================================ cats, plants, lamps

def cat(name, loc, rot=0.0, color=(0.85, 0.55, 0.25)):
    root = bpy.data.objects.new(name, None); link(root)
    m = clay(f'cat_{color}', color, rough=0.7, sss=0.2)
    white = clay('cat_white', (0.95, 0.92, 0.86), rough=0.7)
    parts = [sphere(name + '_b', 0.006, (0, 0, 0.005), m, seg=16, scale=(1.5, 0.9, 0.8)),
             sphere(name + '_h', 0.0042, (0.008, 0, 0.0095), m, seg=16),
             sphere(name + '_m', 0.0022, (0.0115, 0, 0.0085), white, seg=12, scale=(0.8, 1, 0.7))]
    for s in (-1, 1):
        e = cyl(name + '_ear', 0.0016, 0.0028, (0.0085, s * 0.0024, 0.0128), m, seg=4, r2=0.0001, smooth=False)
        e.rotation_euler = (s * 0.3, 0, 0); parts.append(e)
    tail = curve_wire(name + '_tail', [(-0.008, 0, 0.004), (-0.012, 0.003, 0.002), (-0.011, 0.008, 0.001)], r=0.0011, mat=m)
    j = join(parts, name + '_m'); j.parent = root; tail.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root, j


def street_lamp(name, loc, h=0.07, on=True, power=0.04):
    root = bpy.data.objects.new(name, None); link(root)
    pm = metal('lamp_pole', (0.08, 0.1, 0.09), 0.4)
    parts = [cyl(name + '_p', 0.0009, h, (0, 0, 0), pm, seg=8), cyl(name + '_base', 0.0022, 0.004, (0, 0, 0), pm, seg=12)]
    j = join(parts, name + '_m'); j.parent = root
    gl = sphere(name + '_g', 0.004, (0, 0, h + 0.003), emit('lampglow', (1, 0.78, 0.5), 12), seg=16, scale=(1, 1, 1.25))
    gl.parent = root
    lt = point(name + '_l', (0, 0, h + 0.003), power=power, color=(1, 0.72, 0.42), radius=0.004)
    lt.parent = root
    root.location = loc
    return root, gl, lt

# ================================================================ plane trees (Wukang Road)

def plane_tree(name, loc, h=0.13, seed=0, autumn=0.5):
    rnd = random.Random(seed)
    root = bpy.data.objects.new(name, None); link(root)
    bark = clay('bark', (0.58, 0.55, 0.45), rough=0.8, var=0.12, bump=0.6)
    parts = [cyl(name + '_t', 0.004, h * 0.55, (0, 0, 0), bark, seg=12, r2=0.0028)]
    tip = Vector((0, 0, h * 0.55))
    for k in range(4):
        a = k * math.pi / 2 + rnd.uniform(-0.4, 0.4)
        end = tip + Vector((math.cos(a) * h * 0.22, math.sin(a) * h * 0.22, h * rnd.uniform(0.18, 0.3)))
        d = end - tip
        c = cyl(name + f'_br{k}', 0.0022, d.length, tip, bark, seg=8, r2=0.001)
        c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); parts.append(c)
    j = join(parts, name + '_m'); j.parent = root
    greens = [(0.36, 0.45, 0.16), (0.48, 0.52, 0.18), (0.62, 0.55, 0.16), (0.75, 0.55, 0.15), (0.55, 0.42, 0.12)]
    leaves = []
    nclust = 22
    for k in range(nclust):
        a = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(0, h * 0.32)
        p = Vector((math.cos(a) * rr, math.sin(a) * rr, h * 0.72 + rnd.uniform(-0.02, 0.05) * h / 0.13 - rr * 0.25))
        idx = min(len(greens) - 1, int(rnd.random() * (2 + autumn * 3)))
        m = felt(f'leaf_{idx}', greens[idx], var=0.12)
        o = ico(name + f'_c{k}', rnd.uniform(0.016, 0.026) * h / 0.13, p, m, sub=2, jitter=0.22, seed=seed * 50 + k,
                scale=(1, 1, 0.75))
        leaves.append(o)
    cj = join(leaves, name + '_canopy'); cj.parent = root
    root.location = loc
    return root


def falling_leaves(name, n, area_c, area_s, seed=0):
    rnd = random.Random(seed)
    cols = [(0.82, 0.58, 0.15), (0.7, 0.4, 0.12), (0.88, 0.7, 0.25), (0.6, 0.52, 0.18)]
    out = []
    for i in range(n):
        m = felt(f'fleaf_{i % 4}', cols[i % 4], var=0.1)
        bm = bmesh.new()
        pts = []
        for k in range(10):
            a = k / 10 * 2 * math.pi
            r = 0.0035 * (1.0 if k % 2 == 0 else 0.55)
            pts.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, 0)))
        bm.faces.new(pts)
        o = bpy.data.objects.new(f'{name}{i}', bpy.data.meshes.new(f'{name}{i}'))
        bm.to_mesh(o.data); bm.free(); link(o); o.data.materials.append(m)
        sol = o.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.0004
        o['x0'] = area_c[0] + rnd.uniform(-area_s[0], area_s[0])
        o['y0'] = area_c[1] + rnd.uniform(-area_s[1], area_s[1])
        o['z0'] = area_c[2] + rnd.uniform(0, area_s[2])
        o['ph'] = rnd.random(); o['sp'] = rnd.uniform(0.7, 1.3)
        out.append(o)
    return out


def animate_leaves(leaves, t, fall=0.12, period=9.0, ground_z=0.0):
    for i, o in enumerate(leaves):
        ph = (t / period * o['sp'] + o['ph']) % 1.0
        z = o['z0'] - ph * fall
        if z < ground_z + 0.0005:
            z = ground_z + 0.0005
            rot = (0, 0, i)
        else:
            rot = (math.sin(t * 2 + i) * 0.8, math.cos(t * 1.7 + i) * 0.6, t + i)
        o.location = (o['x0'] + 0.01 * math.sin(t * 1.3 + i * 2), o['y0'] + 0.006 * math.cos(t + i), z)
        o.rotation_euler = rot


def wukang_mansion(name, loc, rot=0.0):
    """The flatiron on Wukang Road: wedge plan, arcade at street level, red-brown brick with cream bands."""
    root = bpy.data.objects.new(name, None); link(root)
    wall = windows(name + '_w', wall=(0.55, 0.30, 0.22), glass_c=(0.12, 0.12, 0.13), cols=55, rows=60, frame=0.28, lit_strength=2.5)
    cream = clay('cream', (0.86, 0.80, 0.68), rough=0.7)
    base = paint('arcade', (0.82, 0.76, 0.64))
    L, W, H = 0.36, 0.11, 0.26
    bm = bmesh.new()
    poly = [(-L / 2, -W / 2), (L / 2 - 0.02, -0.008), (L / 2, 0), (L / 2 - 0.02, 0.008), (-L / 2, W / 2)]
    vs = [bm.verts.new((x, y, 0.035)) for x, y in poly]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z = H
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = _obj_from_bm(name + '_body', bm, wall); bevel(body, 0.0015)
    body.parent = root
    # arcade base with arches
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in poly]
    f = bm.faces.new(vs); ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z = 0.035
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    arc = _obj_from_bm(name + '_arc', bm, base); bevel(arc, 0.001); arc.parent = root
    dark = clay('arch_dark', (0.12, 0.09, 0.07), rough=0.9)
    lit = emit('arch_glow', (1, 0.7, 0.4), 1.2)
    # arches along the south face
    import math as _m
    pA, pB = Vector((-L / 2, -W / 2, 0)), Vector((L / 2 - 0.02, -0.008, 0))
    dirv = (pB - pA); ang = _m.atan2(dirv.y, dirv.x)
    nrm = Vector((-dirv.y, dirv.x, 0)).normalized()
    for k in range(10):
        p = pA.lerp(pB, (k + 0.5) / 10) - nrm * 0.0008
        a = box(name + f'_a{k}', (0.022, 0.003, 0.024), p, dark if k % 3 else lit, bev=0.0008, rot=(0, 0, ang))
        a.parent = root
    # cream horizontal bands
    for z in (0.035, 0.10, 0.18, H):
        bm = bmesh.new()
        vs = [bm.verts.new((x * 1.02, y * 1.06, z)) for x, y in poly]
        f = bm.faces.new(vs); ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z = z + 0.004
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        b = _obj_from_bm(name + f'_band{z}', bm, cream); bevel(b, 0.0008); b.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root, wall

# ================================================================ the Bund

def bund_building(name, x, w, d, h, kind, seed=0, lit=0.0):
    rnd = random.Random(seed)
    stone_cols = [(0.82, 0.76, 0.64), (0.76, 0.72, 0.64), (0.86, 0.82, 0.72), (0.72, 0.66, 0.56)]
    sc = stone_cols[seed % 4]
    wall = windows(f'bund_w{seed}', wall=sc, glass_c=(0.16, 0.14, 0.12), cols=70, rows=70, frame=0.3, lit_frac=lit,
                   lit=(1.0, 0.75, 0.42), lit_strength=3.0, seed=seed)
    stone = clay(f'bund_s{seed}', tuple(c * 0.95 for c in sc), rough=0.75)
    parts = []
    body = box(name, (w, d, h), (x, 0, 0), wall, bev=0.001)
    parts.append(body)
    parts.append(box(name + '_base', (w + 0.004, d + 0.004, 0.022), (x, 0, 0), stone, bev=0.001))
    parts.append(box(name + '_cor', (w + 0.006, d + 0.006, 0.004), (x, 0, h), stone, bev=0.0008))
    # colonnade
    ncol = max(4, int(w / 0.014))
    for k in range(ncol):
        cx = x - w / 2 + (k + 0.5) * w / ncol
        parts.append(cyl(name + f'_col{k}', 0.0018, h * 0.32, (cx, -d / 2 - 0.003, h * 0.4), stone, seg=12))
    parts.append(box(name + '_ent', (w * 0.9, 0.006, 0.004), (x, -d / 2 - 0.003, h * 0.4 - 0.002), stone, bev=0.0006))
    parts.append(box(name + '_ent2', (w * 0.9, 0.006, 0.004), (x, -d / 2 - 0.003, h * 0.72), stone, bev=0.0006))
    green = clay('patina', (0.30, 0.50, 0.42), rough=0.5)
    if kind == 'clock':   # Customs House
        for k, (tw, th) in enumerate([(0.05, 0.05), (0.04, 0.045), (0.03, 0.03)]):
            z = h + sum(t[1] for t in [(0.05, 0.05), (0.04, 0.045), (0.03, 0.03)][:k])
            parts.append(box(name + f'_tw{k}', (tw, tw, th), (x, 0, z), stone, bev=0.001))
        face = cyl(name + '_clock', 0.012, 0.002, (x, -0.0255, h + 0.07), clay('clockface', (0.95, 0.93, 0.86)), seg=32, rot=(math.pi / 2, 0, 0))
        parts.append(face)
        parts.append(cyl(name + '_sp', 0.006, 0.02, (x, 0, h + 0.125), stone, seg=4, r2=0.0005, smooth=False))
    elif kind == 'dome':  # HSBC
        parts.append(cyl(name + '_drum', 0.028, 0.02, (x, 0, h), stone, seg=32))
        dm = sphere(name + '_dome', 0.028, (x, 0, h + 0.02), green, seg=32, scale=(1, 1, 0.8))
        parts.append(dm)
        parts.append(cyl(name + '_lan', 0.004, 0.012, (x, 0, h + 0.04), stone, seg=12))
    elif kind == 'pyramid':  # Peace Hotel
        parts.append(box(name + '_tw', (0.04, 0.04, 0.05), (x, 0, h), stone, bev=0.001))
        parts.append(cyl(name + '_pyr', 0.031, 0.04, (x, 0, h + 0.05), green, seg=4, r2=0.0008, smooth=False, rot=(0, 0, math.pi / 4)))
    elif kind == 'stepped':
        parts.append(box(name + '_t1', (w * 0.7, d * 0.7, 0.03), (x, 0, h), wall, bev=0.001))
        parts.append(box(name + '_t2', (w * 0.4, d * 0.4, 0.03), (x, 0, h + 0.03), stone, bev=0.001))
    elif kind == 'gable':
        parts.append(prism_roof(name + '_roof', w, d, 0.03, (x, 0, h), green, overhang=0.003))
    j = join(parts[1:], name + '_trim')
    return body, j, wall


def bund_row(origin=(0, 0, 0), lit=0.0):
    spec = [(0.10, 'gable', 0.16), (0.13, 'dome', 0.15), (0.11, 'clock', 0.17), (0.09, 'flat', 0.14),
            (0.12, 'stepped', 0.17), (0.10, 'pyramid', 0.18), (0.08, 'flat', 0.15), (0.11, 'gable', 0.14), (0.09, 'flat', 0.13)]
    root = bpy.data.objects.new('Bund', None); link(root)
    x = -sum(s[0] for s in spec) / 2
    mats = []
    for i, (w, kind, h) in enumerate(spec):
        b, t, m = bund_building(f'bund{i}', x + w / 2, w - 0.004, 0.10, h, kind, seed=i, lit=lit)
        b.parent = root; t.parent = root; mats.append(m)
        x += w
    root.location = origin
    return root, mats

# ================================================================ Pudong

def _twist_tower(name, r0, r1, h, twist, mat, rings=40, sides=3, round_=0.45):
    """Shanghai Tower: rounded triangle that tapers and rotates as it rises."""
    bm = bmesh.new()
    prof = []
    N = 36
    for k in range(N):
        a = k / N * 2 * math.pi
        rr = 1 + round_ * 0.0 - 0.18 * math.cos(sides * a)
        prof.append((math.cos(a) * rr, math.sin(a) * rr))
    # notch (the tower's characteristic slot)
    layers = []
    for i in range(rings + 1):
        t = i / rings
        r = r0 + (r1 - r0) * t ** 1.2
        ang = twist * t
        ca, sa = math.cos(ang), math.sin(ang)
        layers.append([bm.verts.new((r * (x * ca - y * sa), r * (x * sa + y * ca), h * t)) for x, y in prof])
    for a, b in zip(layers, layers[1:]):
        for k in range(N):
            bm.faces.new([a[k], a[(k + 1) % N], b[(k + 1) % N], b[k]])
    bm.faces.new(layers[-1]); bm.faces.new(list(reversed(layers[0])))
    o = _obj_from_bm(name, bm, mat, smooth=True)
    return o


def pudong(origin=(0, 0, 0), lit=0.0):
    root = bpy.data.objects.new('Pudong', None); link(root)
    mats = {}
    glass_t = windows('pd_glass', wall=(0.55, 0.62, 0.66), glass_c=(0.3, 0.36, 0.42), cols=120, rows=110, frame=0.2,
                      lit=(1.0, 0.78, 0.5), lit_strength=0.4, seed=3)
    mats['glass'] = glass_t
    st = _twist_tower('ShanghaiTower', 0.042, 0.022, 0.62, math.radians(120), glass_t)
    st.location = (0.16, 0.06, 0); st.parent = root
    crown = cyl('ST_crown', 0.022, 0.03, (0.16, 0.06, 0.62), metal('crownm', (0.7, 0.72, 0.72), 0.3), seg=24, r2=0.018)
    crown.parent = root
    # Jin Mao: stepped pagoda
    jm_m = windows('pd_jm', wall=(0.45, 0.48, 0.5), glass_c=(0.25, 0.27, 0.3), cols=90, rows=120, frame=0.18,
                   lit=(1.0, 0.72, 0.42), lit_strength=0.45, seed=5)
    mats['jm'] = jm_m
    tiers = []
    z = 0; w = 0.06
    for k in range(13):
        th = 0.034 - k * 0.0012
        tiers.append(box(f'JM{k}', (w, w, th), (0.02, 0.10, z), jm_m, bev=0.002, rot=(0, 0, math.pi / 4)))
        z += th; w *= 0.93
    tiers.append(cyl('JMspire', 0.004, 0.06, (0.02, 0.10, z), metal('spire', (0.75, 0.75, 0.72)), seg=8, r2=0.0005))
    jm = join(tiers, 'JinMao'); jm.parent = root
    # SWFC: tapered with an opening at the top
    sw_m = windows('pd_sw', wall=(0.6, 0.66, 0.7), glass_c=(0.32, 0.38, 0.44), cols=100, rows=120, frame=0.12,
                   lit=(1.0, 0.8, 0.55), lit_strength=0.4, seed=7)
    mats['sw'] = sw_m
    bm = bmesh.new()
    lo = [(-0.04, -0.04), (0.04, -0.04), (0.04, 0.04), (-0.04, 0.04)]
    hi = [(-0.035, -0.002), (0.035, -0.002), (0.035, 0.002), (-0.035, 0.002)]
    vl = [bm.verts.new((x, y, 0)) for x, y in lo]; vh = [bm.verts.new((x, y, 0.5)) for x, y in hi]
    for k in range(4): bm.faces.new([vl[k], vl[(k + 1) % 4], vh[(k + 1) % 4], vh[k]])
    bm.faces.new(vh); bm.faces.new(list(reversed(vl)))
    sw = _obj_from_bm('SWFC', bm, sw_m)
    cut = box('SWcut', (0.03, 0.2, 0.035), (0, 0, 0.44), None, bev=0)
    bo = sw.modifiers.new('cut', 'BOOLEAN'); bo.object = cut; bo.operation = 'DIFFERENCE'
    cut.hide_render = True; cut.hide_viewport = True
    sw.location = (0.27, 0.13, 0); sw.rotation_euler = (0, 0, 0.3); sw.parent = root
    cut.parent = sw
    # Oriental Pearl
    pink = clay('pearl_pink', (0.78, 0.22, 0.38), rough=0.25, var=0.03, bump=0.1, sss=0.1)
    pink_lit = lit_obj_mat('pearl_lit', color=(1.0, 0.25, 0.5), strength=0.35, off=(0.78, 0.22, 0.38))
    mats['pearl'] = pink_lit
    for nd in pink_lit.node_tree.nodes:
        if nd.type == 'MIX': nd.inputs['B'].default_value = (1.0, 0.3, 0.55, 1)
    silver = metal('pearl_frame', (0.78, 0.78, 0.76), 0.35)
    OP = Vector((-0.17, -0.02, 0))
    parts = []
    for k in range(3):
        a = k * 2 * math.pi / 3
        foot = OP + Vector((math.cos(a) * 0.07, math.sin(a) * 0.07, 0))
        top = OP + Vector((math.cos(a) * 0.012, math.sin(a) * 0.012, 0.12))
        d = top - foot
        c = cyl(f'OPleg{k}', 0.0045, d.length, foot, silver, seg=12); c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); parts.append(c)
        parts.append(cyl(f'OPcol{k}', 0.0065, 0.33, OP + Vector((math.cos(a) * 0.012, math.sin(a) * 0.012, 0)), silver, seg=16))
    j = join(parts, 'OPframe'); j.parent = root
    balls = []
    for nm, r, z in [('OPbig', 0.042, 0.135), ('OPmid', 0.018, 0.29), ('OPtop', 0.0125, 0.375)]:
        b = sphere(nm, r, OP + Vector((0, 0, z)), pink_lit, seg=40); b.parent = root; balls.append(b)
    for k in range(5):
        b = sphere(f'OPsm{k}', 0.008, OP + Vector((0, 0, 0.19 + k * 0.02)), pink_lit, seg=20); b.parent = root; balls.append(b)
    sp = cyl('OPneck', 0.005, 0.07, OP + Vector((0, 0, 0.30)), silver, seg=12); sp.parent = root
    sp2 = cyl('OPspire', 0.003, 0.09, OP + Vector((0, 0, 0.385)), silver, seg=10, r2=0.0006); sp2.parent = root
    for b in balls: b.pass_index = 1
    # filler towers
    rnd = random.Random(11)
    fill_m = []
    for i in range(16):
        m = windows(f'pd_f{i % 4}', wall=[(0.62, 0.6, 0.56), (0.5, 0.56, 0.6), (0.7, 0.68, 0.62), (0.45, 0.5, 0.52)][i % 4],
                    glass_c=(0.2, 0.24, 0.28), cols=90, rows=100, frame=0.26, lit=(1.0, 0.74, 0.45), lit_strength=0.45, seed=i % 4)
        if m not in fill_m: fill_m.append(m)
        x = rnd.uniform(-0.45, 0.5); y = rnd.uniform(0.16, 0.35)
        if abs(x + 0.17) < 0.09 and y < 0.2: y += 0.1
        h = rnd.uniform(0.12, 0.3)
        w = rnd.uniform(0.04, 0.07)
        if rnd.random() < 0.4:
            o = cyl(f'pdf{i}', w / 2, h, (x, y, 0), m, seg=24)
        else:
            o = box(f'pdf{i}', (w, w * rnd.uniform(0.7, 1.2), h), (x, y, 0), m, bev=0.002, rot=(0, 0, rnd.uniform(0, 1.5)))
        o.parent = root
    mats['fill'] = fill_m
    root.location = origin
    return root, mats


def set_city_lit(mats, v):
    for k, m in mats.items():
        if isinstance(m, list):
            for mm in m: set_lit(mm, v)
        else:
            set_lit(m, v)


def ferry(name, loc, rot=0.0, color=(0.92, 0.9, 0.84)):
    root = bpy.data.objects.new(name, None); link(root)
    hull = paint('ferry_hull', (0.18, 0.28, 0.36), rough=0.4)
    top = paint('ferry_top', color, rough=0.5)
    red = paint('ferry_red', (0.7, 0.15, 0.1))
    winm = lit_obj_mat('ferry_win', (1, 0.78, 0.45), 6.0)
    parts = []
    bm = bmesh.new()
    L, W = 0.09, 0.026
    poly = [(-L / 2, -W / 2), (L / 2 - 0.012, -W / 2), (L / 2, 0), (L / 2 - 0.012, W / 2), (-L / 2, W / 2)]
    vs = [bm.verts.new((x, y, 0)) for x, y in poly]; f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z = 0.01; v.co.x *= 1.03; v.co.y *= 1.08
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    h = _obj_from_bm(name + '_hull', bm, hull); bevel(h, 0.001); parts.append(h)
    parts.append(box(name + '_deck', (0.07, 0.024, 0.012), (-0.005, 0, 0.01), top, bev=0.001))
    parts.append(box(name + '_deck2', (0.04, 0.02, 0.009), (-0.008, 0, 0.022), top, bev=0.001))
    parts.append(box(name + '_stripe', (0.071, 0.0245, 0.0015), (-0.005, 0, 0.0115), red, bev=0))
    parts.append(cyl(name + '_fun', 0.003, 0.012, (-0.018, 0, 0.031), red, seg=12))
    j = join(parts, name + '_m'); j.parent = root
    wins = []
    for k in range(8):
        for s in (-1, 1):
            w = box(name + f'_w{k}{s}', (0.005, 0.001, 0.004), (-0.036 + k * 0.0085, s * 0.0124, 0.0155), winm, bev=0)
            w.parent = root; wins.append(w)
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root, winm


def rain(name, n, center, size, seed=0):
    rnd = random.Random(seed)
    m = bpy.data.materials.new('rain_m'); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.9, 0.95, 1, 1)
    p.inputs['Transmission Weight'].default_value = 1.0; p.inputs['Roughness'].default_value = 0.05
    p.inputs['Emission Color'].default_value = (0.8, 0.85, 1.0, 1); p.inputs['Emission Strength'].default_value = 0.25
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=0.00028, radius2=0.00012, depth=0.012)
    me = bpy.data.meshes.new('drop'); bm.to_mesh(me); bm.free(); me.materials.append(m)
    drops = []
    for i in range(n):
        o = bpy.data.objects.new(f'{name}{i}', me); link(o)
        o['x'] = center[0] + rnd.uniform(-size[0], size[0]); o['y'] = center[1] + rnd.uniform(-size[1], size[1])
        o['ph'] = rnd.random(); o['sp'] = rnd.uniform(0.9, 1.15)
        o.rotation_euler = (0.08, 0.05, 0)
        o.visible_shadow = False
        drops.append(o)
    return drops


def animate_rain(drops, frame, top, bottom, period=0.9):
    for o in drops:
        r = random.Random(hash((o.name, frame)) & 0xffffffff)
        ph = (frame / 12.0 / period * o['sp'] + o['ph']) % 1.0
        o.location = (o['x'] + r.uniform(-0.002, 0.002), o['y'] + r.uniform(-0.002, 0.002), top - (top - bottom) * ph)

# ================================================================ the desk (prologue / epilogue)

def flat_shape(name, pts, thick=0.0006, mat=None):
    """Extrude a 2D outline (x, z) into a card cut-out lying in the XZ plane (y = thickness)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.y += thick
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); link(o)
    if mat: me.materials.append(mat)
    return o


def circle_pts(cx, cz, r, n=28):
    return [(cx + math.cos(a) * r, cz + math.sin(a) * r) for a in [k / n * 2 * math.pi for k in range(n)]]


def rect_pts(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def open_book(name, loc, w=0.15, h=0.21, rot=0.0):
    root = bpy.data.objects.new(name, None); link(root)
    pg = paper('page_text', (0.93, 0.89, 0.80), lines=True)
    pg_plain = paper('page_plain', (0.92, 0.88, 0.79))
    cover = clay('book_cover', (0.36, 0.13, 0.1), rough=0.6, var=0.03)
    parts = []
    for side in (-1, 1):
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=24, y_segments=2, size=0.5)
        for v in bm.verts:
            u = v.co.x + 0.5   # 0..1 across the page
            v.co.x = side * u * w
            v.co.y *= h
            v.co.z = 0.012 + 0.006 * math.sin(u * math.pi * 0.9) - 0.010 * (1 - u) ** 6
        o = bpy.data.objects.new(f'{name}_page{side}', bpy.data.meshes.new('pg')); bm.to_mesh(o.data); bm.free(); link(o)
        o.data.materials.append(pg)
        for p in o.data.polygons: p.use_smooth = True
        o.parent = root; parts.append(o)
        # page block
        blk = box(f'{name}_blk{side}', (w * 0.98, h * 0.98, 0.011), (side * w * 0.5, 0, 0.0015), pg_plain, bev=0.002)
        blk.parent = root
        cv = box(f'{name}_cov{side}', (w * 1.02, h * 1.04, 0.0025), (side * w * 0.51, 0, 0), cover, bev=0.001)
        cv.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root


def book_stack(name, loc, n=3, seed=0, rot=0.0):
    rnd = random.Random(seed)
    root = bpy.data.objects.new(name, None); link(root)
    cols = [(0.22, 0.30, 0.38), (0.55, 0.42, 0.25), (0.3, 0.36, 0.26), (0.5, 0.18, 0.14), (0.8, 0.74, 0.6)]
    z = 0
    for i in range(n):
        th = rnd.uniform(0.018, 0.032); w = rnd.uniform(0.13, 0.17); d = rnd.uniform(0.19, 0.23)
        c = box(f'{name}_c{i}', (w, d, th), (rnd.uniform(-0.006, 0.006), 0, z), clay(f'bc{seed}{i}', rnd.choice(cols), rough=0.55, var=0.03), bev=0.002,
                rot=(0, 0, rnd.uniform(-0.08, 0.08)))
        p = box(f'{name}_p{i}', (w - 0.006, d - 0.004, th - 0.004), (c.location.x + 0.004, 0, z + 0.002), paper('pblock', (0.9, 0.86, 0.76)), bev=0.0008,
                rot=c.rotation_euler)
        c.parent = root; p.parent = root
        z += th
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root, z


def desk_lamp(name, loc, rot=0.0):
    root = bpy.data.objects.new(name, None); link(root)
    brass = metal('lamp_brass', (0.75, 0.55, 0.3), 0.3)
    shade_m = paint('lamp_shade', (0.12, 0.25, 0.2), rough=0.35)
    parts = [cyl(name + '_base', 0.06, 0.012, (0, 0, 0), brass, seg=40, r2=0.05),
             cyl(name + '_stem', 0.006, 0.36, (0, 0, 0.012), brass, seg=16)]
    arm = cyl(name + '_arm', 0.005, 0.22, (0, 0, 0.37), brass, seg=16); arm.rotation_euler = (0, math.radians(70), 0); parts.append(arm)
    j = join(parts, name + '_m'); j.parent = root
    shade = cyl(name + '_shade', 0.075, 0.08, (0, 0, 0), shade_m, seg=40, r2=0.03)
    shade.data.materials.append(shade_m)
    sol = shade.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.002
    shade.location = (0.205, 0, 0.36); shade.parent = root
    bulb_m = emit('lamp_bulb', (1, 0.82, 0.6), 0.0)
    bulb = sphere(name + '_bulb', 0.018, (0.205, 0, 0.37), bulb_m, seg=20); bulb.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    bpy.context.view_layer.update()
    sp = bulb.matrix_world.translation.copy()
    lt = spot(name + '_light', sp - Vector((0, 0, 0.02)), (sp.x + 0.08, sp.y, 0.0), power=0, angle=math.radians(110), color=(1, 0.78, 0.52), radius=0.03, blend=0.9)
    return root, lt, bulb_m


def teacup(name, loc):
    root = bpy.data.objects.new(name, None); link(root)
    por = clay('porcelain', (0.93, 0.92, 0.88), rough=0.15, var=0.01, bump=0.05, sss=0.2)
    blue = clay('porc_blue', (0.15, 0.25, 0.55), rough=0.2, var=0.0, bump=0)
    cup = cyl(name + '_cup', 0.032, 0.06, (0, 0, 0.004), por, seg=40, r2=0.04)
    sol = cup.modifiers.new('s', 'SOLIDIFY'); sol.thickness = 0.003
    tea = cyl(name + '_tea', 0.037, 0.001, (0, 0, 0.05), clay('tea', (0.45, 0.28, 0.08), rough=0.05, bump=0), seg=40)
    band = cyl(name + '_band', 0.0395, 0.006, (0, 0, 0.048), blue, seg=40, r2=0.0402)
    saucer = cyl(name + '_sau', 0.06, 0.004, (0, 0, 0), por, seg=40, r2=0.055)
    for o in (cup, tea, band, saucer): o.parent = root
    root.location = loc
    return root


def pop_piece(name, pts, hinge_loc, mat, thick=0.0006, windows_pts=None, win_mat=None):
    """A pop-up card piece on a hinge; rotate hinge.rotation_euler.x from -pi/2 (flat) to 0 (standing)."""
    hinge = bpy.data.objects.new(name + '_hinge', None); link(hinge)
    hinge.location = hinge_loc
    o = flat_shape(name, pts, thick, mat); o.parent = hinge
    if windows_pts:
        for k, (x0, z0, x1, z1) in enumerate(windows_pts):
            w = flat_shape(f'{name}_w{k}', rect_pts(x0, z0, x1, z1), thick * 0.5, win_mat)
            w.location.y = -0.00005; w.parent = hinge
    hinge.rotation_euler.x = -math.pi / 2
    return hinge


def paper_city(origin=(0, 0, 0), scale=1.0, seed=2):
    """Pop-up Shanghai on the open book: three rows of card cut-outs. Returns [(hinge, start_time)]."""
    rnd = random.Random(seed)
    card_cols = [(0.94, 0.90, 0.82), (0.90, 0.84, 0.74), (0.86, 0.80, 0.70)]
    mats = [paper(f'card{i}', c) for i, c in enumerate(card_cols)]
    win = lit_obj_mat('card_win', (1.0, 0.72, 0.4), 8.0, off=(0.3, 0.25, 0.2))
    pink = paper('card_pink', (0.85, 0.45, 0.5))
    pieces = []
    S = scale
    # back row: Pudong
    yb = 0.05 * S
    pudong_pieces = [
        ('pd_st', [(-0.006, 0), (0.006, 0), (0.0045, 0.11), (0.0, 0.122), (-0.0045, 0.11)], 0.03),
        ('pd_sw', [(-0.007, 0), (0.007, 0), (0.0055, 0.098), (-0.0055, 0.098)], 0.045),
        ('pd_jm', [(-0.006, 0), (0.006, 0), (0.0045, 0.06), (0.003, 0.075), (0.0015, 0.088), (0, 0.098), (-0.0015, 0.088), (-0.003, 0.075), (-0.0045, 0.06)], 0.018),
        ('pd_a', rect_pts(-0.01, 0, 0.01, 0.05), 0.058),
        ('pd_b', rect_pts(-0.008, 0, 0.008, 0.065), -0.045),
        ('pd_c', rect_pts(-0.009, 0, 0.009, 0.04), 0.072),
    ]
    for nm, pts, x in pudong_pieces:
        pts = [(px * S, pz * S) for px, pz in pts]
        wins = []
        xs = [p[0] for p in pts]; zs = [p[1] for p in pts]
        for k in range(10):
            wx = rnd.uniform(min(xs) * 0.6, max(xs) * 0.6); wz = rnd.uniform(0.008, max(zs) * 0.8)
            wins.append((wx, wz, wx + 0.0012 * S, wz + 0.002 * S))
        pieces.append(pop_piece(nm, pts, (origin[0] + x * S, origin[1] + yb, origin[2]), rnd.choice(mats), windows_pts=wins, win_mat=win))
    # Oriental Pearl as layered pieces
    px = origin[0] - 0.02 * S
    pearl_shaft = rect_pts(-0.0012 * S, 0, 0.0012 * S, 0.105 * S)
    legs = [(-0.012 * S, 0), (-0.009 * S, 0), (0.0, 0.03 * S), (0.009 * S, 0), (0.012 * S, 0), (0.002 * S, 0.04 * S), (-0.002 * S, 0.04 * S)]
    pieces.append(pop_piece('pearl_legs', legs, (px, origin[1] + yb - 0.004, origin[2]), mats[0]))
    pieces.append(pop_piece('pearl_shaft', pearl_shaft, (px, origin[1] + yb - 0.004, origin[2]), mats[0]))
    for k, (r, z) in enumerate([(0.0105, 0.042), (0.0055, 0.075), (0.0038, 0.098)]):
        pieces.append(pop_piece(f'pearl_b{k}', circle_pts(0, z * S, r * S), (px, origin[1] + yb - 0.005, origin[2]), pink))
    # middle row: the Bund
    ym = 0.0
    x = -0.07
    for i, (w, h, top) in enumerate([(0.016, 0.04, 'gable'), (0.02, 0.038, 'dome'), (0.018, 0.045, 'clock'), (0.014, 0.034, 'flat'),
                                     (0.018, 0.04, 'pyr'), (0.016, 0.036, 'flat'), (0.02, 0.038, 'gable'), (0.015, 0.033, 'flat')]):
        pts = [(-w / 2, 0), (w / 2, 0), (w / 2, h)]
        if top == 'gable': pts += [(0, h + 0.008)]
        elif top == 'dome': pts += [(math.cos(a) * w * 0.3, h + math.sin(a) * w * 0.3) for a in [k / 8 * math.pi for k in range(9)]]
        elif top == 'clock': pts += [(w * 0.2, h), (w * 0.2, h + 0.016), (0, h + 0.024), (-w * 0.2, h + 0.016), (-w * 0.2, h)]
        elif top == 'pyr': pts += [(w * 0.22, h), (0, h + 0.014), (-w * 0.22, h)]
        pts += [(-w / 2, h)]
        pts = [(a * S, b * S) for a, b in pts]
        wins = []
        for r_ in range(3):
            for c_ in range(3):
                wx = (-w / 2 + w * (c_ + 0.5) / 3 - 0.0008) * S; wz = (0.008 + r_ * 0.01) * S
                wins.append((wx, wz, wx + 0.0016 * S, wz + 0.004 * S))
        pieces.append(pop_piece(f'bund{i}', pts, (origin[0] + (x + w / 2) * S, origin[1] + ym, origin[2]), rnd.choice(mats), windows_pts=wins, win_mat=win))
        x += w + 0.002
    # front row: lane houses (zig-zag gables)
    yf = -0.045 * S
    x = -0.07
    for i in range(9):
        w = 0.016
        h = 0.018 + rnd.uniform(-0.002, 0.003)
        pts = [(-w / 2, 0), (w / 2, 0), (w / 2, h), (0, h + 0.008), (-w / 2, h)]
        pts = [(a * S, b * S) for a, b in pts]
        wins = [((-0.002) * S, 0.008 * S, 0.002 * S, 0.013 * S)]
        pieces.append(pop_piece(f'lane{i}', pts, (origin[0] + (x + w / 2) * S, origin[1] + yf, origin[2]), rnd.choice(mats), windows_pts=wins, win_mat=win))
        x += w + 0.0003
    return pieces, win


def animate_pop(hinge, t, t0, dur=0.5):
    """Card stands up with a little overshoot, the way a pop-up page springs open."""
    x = (t - t0) / dur
    if x <= 0: a = -math.pi / 2
    elif x >= 1.6: a = 0.0
    else:
        a = -math.pi / 2 * (1 - x) if x < 1 else 0.0
        if x >= 1: a = math.radians(9) * math.sin((x - 1) / 0.6 * math.pi) * math.exp(-(x - 1) * 3)
        else: a = -math.pi / 2 * (1 - ease(x)) + math.radians(9) * ease(x) ** 6
    hinge.rotation_euler.x = a


def walker(obj, t, keys, h_bob=0.0008, step=2.2):
    """Move a townsperson along keyed points [(t, (x,y,z))] with a little stop-motion bob, facing travel direction."""
    p = path(keys, t, fn=lambda x: x)
    p2 = path(keys, t + 0.05, fn=lambda x: x)
    d = p2 - p
    if d.length > 1e-6:
        obj.rotation_euler.z = math.atan2(d.y, d.x) - math.pi / 2
        p = p + Vector((0, 0, abs(math.sin(t * step * math.pi)) * h_bob))
    obj.location = p


def villa(name, loc, w=0.12, d=0.09, h=0.08, rot=0.0, seed=0):
    rnd = random.Random(seed)
    root = bpy.data.objects.new(name, None); link(root)
    wallc = [(0.88, 0.82, 0.70), (0.80, 0.74, 0.62), (0.86, 0.78, 0.66)][seed % 3]
    wm = windows(f'villa_w{seed % 3}', wall=wallc, glass_c=(0.2, 0.2, 0.2), cols=45, rows=40, frame=0.3, lit_strength=2.0, seed=seed)
    roof = tile_roof_mat('villa_roof', (0.45, 0.18, 0.12))
    parts = [box(name + '_b', (w, d, h), (0, 0, 0), wm, bev=0.0015),
             prism_roof(name + '_r', w, d, 0.035, (0, 0, h), roof, overhang=0.006)]
    parts.append(box(name + '_ch', (0.01, 0.01, 0.03), (w * 0.3, 0, h + 0.01), clay('chimney', (0.55, 0.3, 0.22)), bev=0.001))
    j = join(parts, name + '_m'); j.parent = root
    # garden wall + hedge
    gw = join([box(name + '_gw', (w + 0.04, 0.008, 0.022), (0, -d / 2 - 0.03, 0), clay('gwall', (0.78, 0.72, 0.6), rough=0.8), bev=0.001),
               ico(name + '_hedge', 0.02, (rnd.uniform(-0.04, 0.04), -d / 2 - 0.015, 0.02), felt('hedge', (0.2, 0.32, 0.14)), sub=2, jitter=0.25, seed=seed, scale=(2.5, 0.8, 0.9))],
              name + '_g')
    gw.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot)
    return root, wm


def railing(name, x0, x1, y, h=0.012, mat=None):
    mat = mat or metal('rail', (0.2, 0.22, 0.2), 0.4)
    parts = [box(name + '_top', (x1 - x0, 0.0012, 0.0012), ((x0 + x1) / 2, y, h), mat, bev=0)]
    n = int((x1 - x0) / 0.008)
    for k in range(n + 1):
        parts.append(box(name + f'_p{k}', (0.0008, 0.0008, h), (x0 + k * (x1 - x0) / n, y, 0), mat, bev=0))
    return join(parts, name)
