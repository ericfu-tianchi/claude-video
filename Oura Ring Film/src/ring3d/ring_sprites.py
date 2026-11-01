"""Oura Ring 5 in Blender -> transparent sprite sheets the canvas film draws in place of its flat ring.

Real proportions (mm): 2.28 thick, 6.09 wide, inner Ø 18.2 (size 8), smooth rounded profile,
three low-profile sensor domes (0.7 mm) on the inside. One sprite per degree of rotation about the
vertical axis, lit by a fixed studio rig, so the film can turn the ring to any angle.

blender -b -P ring_sprites.py -- TONE SIZE AMAX OUTDIR [--still DEG]
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
TONE, SIZE, AMAX, OUT = argv[0], int(argv[1]), int(argv[2]), argv[3]
STILL = int(argv[argv.index('--still') + 1]) if '--still' in argv else None
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception as e:
    print('GPU setup failed, CPU fallback', e)
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = SIZE
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'

# ---------------------------------------------------------------- geometry
R_IN, T, WID = 9.1, 2.28, 6.09
RC, A, B, NEXP = R_IN + T / 2, T / 2, WID / 2, 3.2


def profile(n=72):
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        c, s = math.cos(a), math.sin(a)
        x = RC + A * math.copysign(abs(c) ** (2 / NEXP), c)
        y = B * math.copysign(abs(s) ** (2 / NEXP), s)
        if c > 0: x += 0.12 * (1 - (y / B) ** 2)       # outer face very slightly domed
        pts.append((x, y))
    return pts


bm = bmesh.new()
prof = profile()
SEG = 256
rings = []
for k in range(SEG):
    th = k / SEG * 2 * math.pi
    # ring lies in the XZ plane, its axis along Y (towards the camera)
    rings.append([bm.verts.new((x * math.cos(th), y, x * math.sin(th))) for x, y in prof])
n = len(prof)
for k in range(SEG):
    a, b = rings[k], rings[(k + 1) % SEG]
    for i in range(n):
        bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('ring'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
ring = bpy.data.objects.new('Ring', me); sc.collection.objects.link(ring)

# sensor domes on the inner surface, at the bottom of the ring
domes = []
for k, ang in enumerate((-0.32, 0.0, 0.32)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16)
    d = bpy.context.active_object
    d.scale = (0.85, 1.2 if k == 1 else 0.9, 0.7 * 0.55)
    a = -math.pi / 2 + ang
    d.location = (math.cos(a) * R_IN * 0.985, 0, math.sin(a) * R_IN * 0.985)
    d.rotation_euler = (0, -(a + math.pi / 2), 0)
    for p in d.data.polygons: p.use_smooth = True
    d.parent = ring
    domes.append(d)

# ---------------------------------------------------------------- materials
TONES = {   # base color, roughness, anisotropy
    'silver': ((0.86, 0.86, 0.88), 0.10, 0.0),
    'black': ((0.035, 0.035, 0.04), 0.14, 0.0),
    'gold': ((0.98, 0.79, 0.50), 0.12, 0.0),
    'rose': ((0.93, 0.66, 0.58), 0.13, 0.0),
    'stealth': ((0.05, 0.05, 0.055), 0.48, 0.0),
    'brushed': ((0.82, 0.82, 0.84), 0.30, 0.85),
}
base, rough, aniso = TONES[TONE]
m = bpy.data.materials.new('ti'); m.use_nodes = True
p = m.node_tree.nodes['Principled BSDF']
p.inputs['Base Color'].default_value = (*base, 1)
p.inputs['Metallic'].default_value = 1.0
p.inputs['Roughness'].default_value = rough
p.inputs['Anisotropic'].default_value = aniso
if TONE == 'black':
    p.inputs['Coat Weight'].default_value = 0.6; p.inputs['Coat Roughness'].default_value = 0.05
ring.data.materials.append(m)
dm = bpy.data.materials.new('dome'); dm.use_nodes = True
dp = dm.node_tree.nodes['Principled BSDF']
dp.inputs['Base Color'].default_value = (0.02, 0.02, 0.025, 1); dp.inputs['Roughness'].default_value = 0.08
dp.inputs['Coat Weight'].default_value = 1.0
for d in domes: d.data.materials.append(dm)

# ---------------------------------------------------------------- studio
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
nt = w.node_tree; bgn = nt.nodes['Background']
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[0].color = (0.07, 0.07, 0.08, 1)
ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.97, 1)
mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1; mr.inputs['From Max'].default_value = 1
nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], bgn.inputs['Color'])
bgn.inputs['Strength'].default_value = 0.9


def softbox(name, loc, size, power, rot_to=(0, 0, 0)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'
    ld.size, ld.size_y = size; ld.energy = power
    o = bpy.data.objects.new(name, ld); sc.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(rot_to) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


softbox('key', (-40, 60, 50), (60, 25), 9000)      # big top-left strip -> long highlight on the band
softbox('rim', (55, 30, -10), (12, 70), 5000)       # tall right strip -> crisp edge line
softbox('fill', (0, 80, -45), (80, 20), 2500)       # low fill -> lifts the lower curve
softbox('top', (0, 10, 80), (40, 40), 3000)

cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cd.ortho_scale = (R_IN + T) * 2 / 0.9
cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam)
cam.location = (0, 100, 0)
cam.rotation_euler = (Vector((0, 0, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam

angles = [STILL] if STILL is not None else range(-AMAX, AMAX + 1)
for deg in angles:
    ring.rotation_euler = (0, 0, math.radians(deg))
    sc.render.filepath = os.path.join(OUT, f'{TONE}_{deg + 90:03d}.png')
    if STILL is None and os.path.exists(sc.render.filepath): continue
    bpy.ops.render.render(write_still=True)
    print('SPRITE', TONE, deg, flush=True)
