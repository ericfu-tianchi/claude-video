"""Shared helpers: scene setup, handmade materials, primitives, camera, lights.

Everything is built at true miniature scale (1 unit = 1 m, a lane house is ~0.17 m tall)
so depth of field falls off the way it does on a real tabletop set.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler

CLAUDE_ORANGE = (0.85, 0.40, 0.25)

# ---------------------------------------------------------------- scene

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    s.eevee.taa_render_samples = 64
    s.eevee.use_raytracing = True
    s.eevee.use_shadows = True
    s.eevee.shadow_ray_count = 2
    s.eevee.shadow_step_count = 8
    s.eevee.use_fast_gi = True
    s.eevee.fast_gi_method = 'GLOBAL_ILLUMINATION'
    s.eevee.volumetric_tile_size = '4'
    s.eevee.volumetric_samples = 64
    s.eevee.bokeh_max_size = 160
    s.render.film_transparent = False
    s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'AgX - Medium High Contrast'
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_depth = '8'
    s.render.fps = 12
    w = bpy.data.worlds.new('World'); s.world = w
    return s


def world(color=(0.9, 0.8, 0.7), strength=0.4, top=None):
    """Soft studio sky. Optional vertical gradient (top color)."""
    w = bpy.context.scene.world
    w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    if top is None:
        bg.inputs['Color'].default_value = (*color, 1)
    else:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.45
        ramp.color_ramp.elements[0].color = (*color, 1)
        ramp.color_ramp.elements[1].position = 0.75
        ramp.color_ramp.elements[1].color = (*top, 1)
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = -1; mr.inputs['From Max'].default_value = 1
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
        nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs[0], out.inputs[0])
    return bg


def link(obj, coll=None):
    (coll or bpy.context.scene.collection).objects.link(obj)
    return obj

# ---------------------------------------------------------------- materials

_mats = {}

def _principled(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    return m, nt, p


def _hand_variation(nt, p, color, var=0.08, bump=0.25, scale=180.0, rough=0.6):
    """Clay/painted look: per-object tint jitter + fine fingerprint bump."""
    n = nt.nodes
    oi = n.new('ShaderNodeObjectInfo')
    hsv = n.new('ShaderNodeHueSaturation')
    hsv.inputs['Color'].default_value = (*color, 1)
    mr = n.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 1 - var; mr.inputs['To Max'].default_value = 1 + var
    nt.links.new(oi.outputs['Random'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], hsv.inputs['Value'])
    # low-frequency mottling
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; nz.inputs['Detail'].default_value = 3
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = n.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 0.18
    nt.links.new(hsv.outputs['Color'], mix.inputs['A'])
    nt.links.new(nz.outputs['Color'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    if bump > 0:
        nz2 = n.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = scale; nz2.inputs['Detail'].default_value = 6
        vor = n.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = scale * 0.6
        nt.links.new(tc.outputs['Object'], nz2.inputs['Vector'])
        nt.links.new(tc.outputs['Object'], vor.inputs['Vector'])
        add = n.new('ShaderNodeMath'); add.operation = 'ADD'
        nt.links.new(nz2.outputs['Fac'], add.inputs[0])
        vm = n.new('ShaderNodeMath'); vm.operation = 'MULTIPLY'; vm.inputs[1].default_value = 0.4
        nt.links.new(vor.outputs['Distance'], vm.inputs[0])
        nt.links.new(vm.outputs[0], add.inputs[1])
        b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = 0.0004
        nt.links.new(add.outputs[0], b.inputs['Height'])
        nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    rr = n.new('ShaderNodeMapRange')
    rr.inputs['To Min'].default_value = rough - 0.08; rr.inputs['To Max'].default_value = rough + 0.08
    nt.links.new(nz.outputs['Fac'], rr.inputs['Value'])
    nt.links.new(rr.outputs['Result'], p.inputs['Roughness'])


def clay(name, color, rough=0.55, var=0.08, bump=0.3, sss=0.15):
    key = ('clay', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    _hand_variation(nt, p, color, var, bump, rough=rough)
    p.inputs['Subsurface Weight'].default_value = sss
    p.inputs['Subsurface Radius'].default_value = (0.004, 0.002, 0.0015)
    p.inputs['Subsurface Scale'].default_value = 1.0
    _mats[key] = m
    return m


def paint(name, color, rough=0.45, var=0.05, bump=0.12):
    key = ('paint', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    _hand_variation(nt, p, color, var, bump, scale=260, rough=rough)
    _mats[key] = m
    return m


def felt(name, color, var=0.1):
    key = ('felt', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    _hand_variation(nt, p, color, var, bump=0.5, scale=900, rough=0.95)
    p.inputs['Sheen Weight'].default_value = 0.8
    p.inputs['Sheen Roughness'].default_value = 0.4
    p.inputs['Sheen Tint'].default_value = (1, 0.95, 0.85, 1)
    p.inputs['Specular IOR Level'].default_value = 0.2
    _mats[key] = m
    return m


def emit(name, color, strength=4.0):
    key = ('emit', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Emission Color'].default_value = (*color, 1)
    p.inputs['Emission Strength'].default_value = strength
    _mats[key] = m
    return m


def glass(name, color=(0.9, 0.95, 1.0), rough=0.05):
    key = ('glass', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Transmission Weight'].default_value = 1.0
    _mats[key] = m
    return m


def metal(name, color, rough=0.3):
    key = ('metal', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough
    _mats[key] = m
    return m


def brick(name, c1=(0.42, 0.40, 0.38), c2=(0.30, 0.29, 0.28), mortar=(0.62, 0.6, 0.56), scale=90.0, red=False):
    """Painted-card brick wall (the kind you'd print and glue onto a set)."""
    key = ('brick', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    n = nt.nodes
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    # use object coords projected on vertical walls: combine x+y as u, z as v
    sep = n.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    addxy = n.new('ShaderNodeMath'); addxy.operation = 'ADD'
    nt.links.new(sep.outputs['X'], addxy.inputs[0]); nt.links.new(sep.outputs['Y'], addxy.inputs[1])
    comb = n.new('ShaderNodeCombineXYZ')
    nt.links.new(addxy.outputs[0], comb.inputs['X']); nt.links.new(sep.outputs['Z'], comb.inputs['Y'])
    br = n.new('ShaderNodeTexBrick')
    br.inputs['Scale'].default_value = scale
    br.inputs['Color1'].default_value = (*c1, 1)
    br.inputs['Color2'].default_value = (*c2, 1)
    br.inputs['Mortar'].default_value = (*mortar, 1)
    br.inputs['Mortar Size'].default_value = 0.012
    br.inputs['Brick Width'].default_value = 0.5
    br.inputs['Row Height'].default_value = 0.2
    br.offset = 0.5
    nt.links.new(comb.outputs[0], br.inputs['Vector'])
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 25
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = n.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 0.3
    nt.links.new(br.outputs['Color'], mix.inputs['A']); nt.links.new(nz.outputs['Color'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], p.inputs['Base Color'])
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.35; b.inputs['Distance'].default_value = 0.0006
    b.invert = True
    nt.links.new(br.outputs['Fac'], b.inputs['Height'])
    nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = 0.85
    _mats[key] = m
    return m


def windows(name, wall=(0.8, 0.75, 0.65), glass_c=(0.15, 0.17, 0.2), lit=(1.0, 0.72, 0.38),
            cols=40.0, rows=60.0, lit_frac=0.0, lit_strength=3.0, frame=0.25, seed=0.0):
    """Facade with a grid of windows. lit_frac (0..1) is exposed as node 'LIT' so it can be animated:
    each window gets a random threshold, so lights switch on one by one as LIT rises."""
    key = ('win', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    n = nt.nodes
    tc = n.new('ShaderNodeTexCoord')
    sep = n.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    # u = x + y (wraps around box), v = z
    u = n.new('ShaderNodeMath'); u.operation = 'ADD'
    nt.links.new(sep.outputs['X'], u.inputs[0]); nt.links.new(sep.outputs['Y'], u.inputs[1])
    um = n.new('ShaderNodeMath'); um.operation = 'MULTIPLY'; um.inputs[1].default_value = cols
    vm = n.new('ShaderNodeMath'); vm.operation = 'MULTIPLY'; vm.inputs[1].default_value = rows
    nt.links.new(u.outputs[0], um.inputs[0]); nt.links.new(sep.outputs['Z'], vm.inputs[0])
    # cell id & fractional position
    fu = n.new('ShaderNodeMath'); fu.operation = 'FRACT'; nt.links.new(um.outputs[0], fu.inputs[0])
    fv = n.new('ShaderNodeMath'); fv.operation = 'FRACT'; nt.links.new(vm.outputs[0], fv.inputs[0])
    flu = n.new('ShaderNodeMath'); flu.operation = 'FLOOR'; nt.links.new(um.outputs[0], flu.inputs[0])
    flv = n.new('ShaderNodeMath'); flv.operation = 'FLOOR'; nt.links.new(vm.outputs[0], flv.inputs[0])
    # window mask: inside margins
    def band(src, lo, hi):
        a = n.new('ShaderNodeMath'); a.operation = 'GREATER_THAN'; a.inputs[1].default_value = lo
        b = n.new('ShaderNodeMath'); b.operation = 'LESS_THAN'; b.inputs[1].default_value = hi
        nt.links.new(src, a.inputs[0]); nt.links.new(src, b.inputs[0])
        c = n.new('ShaderNodeMath'); c.operation = 'MULTIPLY'
        nt.links.new(a.outputs[0], c.inputs[0]); nt.links.new(b.outputs[0], c.inputs[1])
        return c.outputs[0]
    mu = band(fu.outputs[0], frame, 1 - frame)
    mv = band(fv.outputs[0], frame * 0.8, 1 - frame * 0.8)
    mask = n.new('ShaderNodeMath'); mask.operation = 'MULTIPLY'
    nt.links.new(mu, mask.inputs[0]); nt.links.new(mv, mask.inputs[1])
    # random per cell + per object
    comb = n.new('ShaderNodeCombineXYZ')
    nt.links.new(flu.outputs[0], comb.inputs['X']); nt.links.new(flv.outputs[0], comb.inputs['Y'])
    oi = n.new('ShaderNodeObjectInfo')
    sz = n.new('ShaderNodeMath'); sz.operation = 'MULTIPLY_ADD'; sz.inputs[1].default_value = 97.0; sz.inputs[2].default_value = seed
    nt.links.new(oi.outputs['Random'], sz.inputs[0]); nt.links.new(sz.outputs[0], comb.inputs['Z'])
    wn = n.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '3D'
    nt.links.new(comb.outputs[0], wn.inputs['Vector'])
    lit_v = n.new('ShaderNodeValue'); lit_v.name = 'LIT'; lit_v.label = 'LIT'
    lit_v.outputs[0].default_value = lit_frac
    on = n.new('ShaderNodeMath'); on.operation = 'LESS_THAN'
    nt.links.new(wn.outputs['Value'], on.inputs[0]); nt.links.new(lit_v.outputs[0], on.inputs[1])
    litmask = n.new('ShaderNodeMath'); litmask.operation = 'MULTIPLY'
    nt.links.new(on.outputs[0], litmask.inputs[0]); nt.links.new(mask.outputs[0], litmask.inputs[1])
    # warmth variation per window
    hue = n.new('ShaderNodeMix'); hue.data_type = 'RGBA'
    hue.inputs['A'].default_value = (*lit, 1); hue.inputs['B'].default_value = (1.0, 0.9, 0.7, 1)
    nt.links.new(wn.outputs['Color'], hue.inputs['Factor'])
    # base color: wall vs glass
    col = n.new('ShaderNodeMix'); col.data_type = 'RGBA'
    col.inputs['A'].default_value = (*wall, 1); col.inputs['B'].default_value = (*glass_c, 1)
    nt.links.new(mask.outputs[0], col.inputs['Factor'])
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 30
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mul = n.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 0.2
    nt.links.new(col.outputs['Result'], mul.inputs['A']); nt.links.new(nz.outputs['Color'], mul.inputs['B'])
    nt.links.new(mul.outputs['Result'], p.inputs['Base Color'])
    nt.links.new(hue.outputs['Result'], p.inputs['Emission Color'])
    es = n.new('ShaderNodeMath'); es.operation = 'MULTIPLY'; es.inputs[1].default_value = lit_strength
    es.name = 'LITSTR'
    nt.links.new(litmask.outputs[0], es.inputs[0])
    nt.links.new(es.outputs[0], p.inputs['Emission Strength'])
    rg = n.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.8; rg.inputs['To Max'].default_value = 0.15
    nt.links.new(mask.outputs[0], rg.inputs['Value'])
    nt.links.new(rg.outputs['Result'], p.inputs['Roughness'])
    _mats[key] = m
    return m


def set_lit(mat, v):
    mat.node_tree.nodes['LIT'].outputs[0].default_value = v


def wood(name, c1=(0.45, 0.27, 0.14), c2=(0.30, 0.16, 0.08), scale=6.0, rough=0.4):
    key = ('wood', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    n = nt.nodes
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (14, 1.2, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    wv = n.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = scale
    wv.inputs['Distortion'].default_value = 2.5; wv.inputs['Detail'].default_value = 3; wv.inputs['Detail Scale'].default_value = 1.5
    nt.links.new(mp.outputs[0], wv.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*c2, 1); ramp.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(wv.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = 0.3
    p.inputs['Coat Roughness'].default_value = 0.25
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.1
    nt.links.new(wv.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    _mats[key] = m
    return m


def paper(name, color=(0.93, 0.89, 0.80), lines=False, rough=0.9):
    """Cream paper; lines=True prints faint rows of 'text' on it."""
    key = ('paper', name, lines)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    n = nt.nodes
    tc = n.new('ShaderNodeTexCoord')
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 400; nz.inputs['Detail'].default_value = 8
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    base = n.new('ShaderNodeMix'); base.data_type = 'RGBA'; base.blend_type = 'MULTIPLY'; base.inputs['Factor'].default_value = 0.08
    base.inputs['A'].default_value = (*color, 1)
    nt.links.new(nz.outputs['Color'], base.inputs['B'])
    out_col = base.outputs['Result']
    if lines:
        sep = n.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
        # rows
        ym = n.new('ShaderNodeMath'); ym.operation = 'MULTIPLY'; ym.inputs[1].default_value = 260
        nt.links.new(sep.outputs['Y'], ym.inputs[0])
        fy = n.new('ShaderNodeMath'); fy.operation = 'FRACT'; nt.links.new(ym.outputs[0], fy.inputs[0])
        row = n.new('ShaderNodeMath'); row.operation = 'LESS_THAN'; row.inputs[1].default_value = 0.45
        nt.links.new(fy.outputs[0], row.inputs[0])
        # word gaps along x
        fl = n.new('ShaderNodeMath'); fl.operation = 'FLOOR'; nt.links.new(ym.outputs[0], fl.inputs[0])
        cx = n.new('ShaderNodeCombineXYZ')
        xm = n.new('ShaderNodeMath'); xm.operation = 'MULTIPLY'; xm.inputs[1].default_value = 1.0
        nt.links.new(sep.outputs['X'], xm.inputs[0])
        nt.links.new(xm.outputs[0], cx.inputs['X']); nt.links.new(fl.outputs[0], cx.inputs['Y'])
        vn = n.new('ShaderNodeTexNoise'); vn.inputs['Scale'].default_value = 140; vn.inputs['Detail'].default_value = 0
        nt.links.new(cx.outputs[0], vn.inputs['Vector'])
        wg = n.new('ShaderNodeMath'); wg.operation = 'GREATER_THAN'; wg.inputs[1].default_value = 0.42
        nt.links.new(vn.outputs['Fac'], wg.inputs[0])
        ink = n.new('ShaderNodeMath'); ink.operation = 'MULTIPLY'
        nt.links.new(row.outputs[0], ink.inputs[0]); nt.links.new(wg.outputs[0], ink.inputs[1])
        ink2 = n.new('ShaderNodeMath'); ink2.operation = 'MULTIPLY'; ink2.inputs[1].default_value = 0.55
        nt.links.new(ink.outputs[0], ink2.inputs[0])
        mx = n.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        mx.inputs['B'].default_value = (0.18, 0.15, 0.13, 1)
        nt.links.new(ink2.outputs[0], mx.inputs['Factor'])
        nt.links.new(base.outputs['Result'], mx.inputs['A'])
        out_col = mx.outputs['Result']
    nt.links.new(out_col, p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rough
    p.inputs['Subsurface Weight'].default_value = 0.1
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.08
    nt.links.new(nz.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    _mats[key] = m
    return m


def water(name, color=(0.10, 0.20, 0.22), rough=0.06, wave_scale=60.0):
    """Poured-resin water: glossy, with a ripple bump whose phase is node 'W' (animate it)."""
    key = ('water', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    n = nt.nodes
    tc = n.new('ShaderNodeTexCoord')
    val = n.new('ShaderNodeValue'); val.name = 'W'
    comb = n.new('ShaderNodeCombineXYZ')
    nt.links.new(val.outputs[0], comb.inputs['Z'])
    add = n.new('ShaderNodeVectorMath'); add.operation = 'ADD'
    nt.links.new(tc.outputs['Object'], add.inputs[0]); nt.links.new(comb.outputs[0], add.inputs[1])
    mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 3, 1)
    nt.links.new(add.outputs[0], mp.inputs['Vector'])
    nz = n.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'
    nz.inputs['Scale'].default_value = wave_scale; nz.inputs['Detail'].default_value = 4
    nt.links.new(mp.outputs[0], nz.inputs['Vector'])
    nt.links.new(val.outputs[0], nz.inputs['W'])
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.25; b.inputs['Distance'].default_value = 0.001
    nt.links.new(nz.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = 1.0
    p.inputs['Coat Roughness'].default_value = 0.02
    p.inputs['Specular IOR Level'].default_value = 0.8
    _mats[key] = m
    return m


def set_water(mat, t):
    mat.node_tree.nodes['W'].outputs[0].default_value = t


def ground(name, color=(0.5, 0.48, 0.45), wet=0.0):
    """Road / pavement. wet>0 makes it glossy for rain reflections."""
    key = ('ground', name, wet)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    _hand_variation(nt, p, color, 0.05, bump=0.3, scale=300, rough=0.85 - 0.75 * wet)
    p.inputs['Coat Weight'].default_value = wet
    p.inputs['Coat Roughness'].default_value = 0.05
    _mats[key] = m
    return m

# ---------------------------------------------------------------- geometry

def _obj_from_bm(name, bm, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    if smooth:
        for poly in me.polygons: poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    if mat: me.materials.append(mat)
    link(o)
    return o


def bevel(o, w=0.0015, seg=2):
    md = o.modifiers.new('bev', 'BEVEL'); md.width = w; md.segments = seg
    md.limit_method = 'ANGLE'
    return o


def box(name, size, loc, mat=None, bev=0.0012, rot=(0, 0, 0), origin='bottom'):
    """Box with size (x,y,z); origin 'bottom' puts loc at the bottom center."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
        if origin == 'bottom': v.co.z += sz / 2
    o = _obj_from_bm(name, bm, mat)
    o.location = loc; o.rotation_euler = rot
    if bev: bevel(o, min(bev, min(size) * 0.3))
    return o


def cyl(name, r, h, loc, mat=None, seg=24, r2=None, rot=(0, 0, 0), bev=0.0, smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=h)
    for v in bm.verts: v.co.z += h / 2
    o = _obj_from_bm(name, bm, mat, smooth)
    o.location = loc; o.rotation_euler = rot
    if smooth:
        o.data.shade_auto_smooth() if hasattr(o.data, 'shade_auto_smooth') else None
    if bev: bevel(o, bev)
    return o


def sphere(name, r, loc, mat=None, seg=24, scale=(1, 1, 1), smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=r)
    o = _obj_from_bm(name, bm, mat, smooth)
    o.location = loc; o.scale = scale
    return o


def ico(name, r, loc, mat=None, sub=2, smooth=True, jitter=0.0, scale=(1, 1, 1), seed=0):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    if jitter:
        rnd = random.Random(seed)
        for v in bm.verts:
            v.co *= 1 + rnd.uniform(-jitter, jitter)
    o = _obj_from_bm(name, bm, mat, smooth)
    o.location = loc; o.scale = scale
    return o


def torus(name, R, r, loc, mat=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=32, minor_segments=8,
                                     location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    if mat: o.data.materials.append(mat)
    for poly in o.data.polygons: poly.use_smooth = True
    return o


def prism_roof(name, w, d, h, loc, mat=None, overhang=0.004, rot=(0, 0, 0)):
    """Gable roof: ridge along x."""
    bm = bmesh.new()
    W, D = w / 2 + overhang, d / 2 + overhang
    vs = [bm.verts.new(p) for p in [(-W, -D, 0), (W, -D, 0), (W, D, 0), (-W, D, 0), (-W, 0, h), (W, 0, h)]]
    bm.faces.new([vs[0], vs[1], vs[5], vs[4]]); bm.faces.new([vs[2], vs[3], vs[4], vs[5]])
    bm.faces.new([vs[0], vs[4], vs[3]]); bm.faces.new([vs[1], vs[2], vs[5]])
    bm.faces.new([vs[3], vs[2], vs[1], vs[0]])
    o = _obj_from_bm(name, bm, mat)
    sol = o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.002
    o.location = loc; o.rotation_euler = rot
    return o


def tile_roof_mat(name, color=(0.30, 0.18, 0.13)):
    """Terracotta tile rows via wave bump."""
    key = ('tile', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    _hand_variation(nt, p, color, 0.1, bump=0.0, rough=0.7)
    n = nt.nodes
    tc = n.new('ShaderNodeTexCoord')
    wv = n.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 2.0; wv.inputs['Distortion'].default_value = 0
    mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (60, 60, 60)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], wv.inputs['Vector'])
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.6; b.inputs['Distance'].default_value = 0.001
    nt.links.new(wv.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
    _mats[key] = m
    return m


def curve_wire(name, pts, r=0.0003, mat=None, sag=0.0):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = r; cu.bevel_resolution = 2
    sp = cu.splines.new('BEZIER')
    pts = [Vector(p) for p in pts]
    if sag and len(pts) == 2:
        a, b = pts; mid = (a + b) / 2; mid.z -= sag; pts = [a, mid, b]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    if mat: cu.materials.append(mat)
    link(o)
    return o


def join(objs, name):
    """Join meshes (keeps modifiers applied) to reduce object count."""
    objs = [o for o in objs if o.type == 'MESH']
    if not objs: return None
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    mats = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
        me.transform(o.matrix_world)
        # remap material indices
        idx_map = []
        for mt in me.materials:
            if mt not in mats: mats.append(mt)
            idx_map.append(mats.index(mt))
        for poly in me.polygons:
            poly.material_index = idx_map[poly.material_index] if idx_map else 0
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    for o in objs: bpy.data.objects.remove(o)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for mt in mats: me.materials.append(mt)
    o = bpy.data.objects.new(name, me); link(o)
    return o

# ---------------------------------------------------------------- camera / light

def camera(loc, target, lens=50, fstop=2.8, focus=None, sensor=36):
    cd = bpy.data.cameras.new('Cam'); cd.lens = lens; cd.sensor_width = sensor
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    cd.dof.aperture_blades = 7
    cd.clip_start = 0.005; cd.clip_end = 60
    c = bpy.data.objects.new('Cam', cd); link(c)
    bpy.context.scene.camera = c
    aim(c, loc, target)
    cd.dof.focus_distance = (Vector(target) - Vector(loc)).length if focus is None else focus
    return c


def aim(c, loc, target, roll=0.0):
    c.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    q = d.to_track_quat('-Z', 'Y')
    c.rotation_euler = q.to_euler()
    if roll: c.rotation_euler.rotate_axis('Z', roll)


def area(name, loc, target, power=20, size=0.5, color=(1, 0.9, 0.8), shape='DISK'):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power; ld.size = size; ld.color = color
    ld.shape = shape
    o = bpy.data.objects.new(name, ld); link(o)
    aim(o, loc, target)
    return o


def point(name, loc, power=1.0, color=(1, 0.75, 0.45), radius=0.005):
    ld = bpy.data.lights.new(name, 'POINT'); ld.energy = power; ld.color = color
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld); o.location = loc; link(o)
    return o


def spot(name, loc, target, power=20, angle=0.8, color=(1, 0.85, 0.65), radius=0.02, blend=0.6):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = power; ld.color = color
    ld.spot_size = angle; ld.spot_blend = blend; ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld); link(o)
    aim(o, loc, target)
    return o


def sun(name, rot, power=3.0, color=(1, 0.9, 0.75), angle=0.05):
    ld = bpy.data.lights.new(name, 'SUN'); ld.energy = power; ld.color = color; ld.angle = angle
    o = bpy.data.objects.new(name, ld); o.rotation_euler = rot; link(o)
    return o


def fog(size, loc, density=0.3, color=(1, 0.95, 0.9), anisotropy=0.3):
    """Volume box for atmospheric haze (scale-adjusted for miniature)."""
    o = box('Fog', size, loc, None, bev=0, origin='center')
    m = bpy.data.materials.new('FogMat'); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    v = nt.nodes.new('ShaderNodeVolumePrincipled')
    v.inputs['Density'].default_value = density
    v.inputs['Color'].default_value = (*color, 1)
    v.inputs['Anisotropy'].default_value = anisotropy
    nt.links.new(v.outputs[0], nt.nodes['Material Output'].inputs['Volume'])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o, v

# ---------------------------------------------------------------- easing / animation

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease_io(x):
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)


def lerp(a, b, t):
    if isinstance(a, (tuple, list, Vector)):
        return Vector(a).lerp(Vector(b), t)
    return a + (b - a) * t


def path(keys, t, fn=ease_io):
    """keys: [(time, value)], piecewise eased interpolation."""
    if t <= keys[0][0]: return keys[0][1] if not isinstance(keys[0][1], tuple) else Vector(keys[0][1])
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, fn((t - t0) / (t1 - t0)))
    v = keys[-1][1]
    return Vector(v) if isinstance(v, tuple) else v


class Jitter:
    """Stop-motion 'boil': tiny per-frame offsets, deterministic per frame index."""
    def __init__(self, seed=1, amp=0.00015):
        self.seed = seed; self.amp = amp
    def v(self, frame, k=0, amp=None):
        r = random.Random(self.seed * 100003 + frame * 31 + k)
        a = self.amp if amp is None else amp
        return Vector((r.uniform(-a, a), r.uniform(-a, a), r.uniform(-a, a)))
    def s(self, frame, k=0, amp=1.0):
        r = random.Random(self.seed * 7919 + frame * 17 + k)
        return r.uniform(-amp, amp)


def lit_obj_mat(name, color=(1.0, 0.7, 0.38), strength=6.0, off=(0.08, 0.07, 0.06)):
    """Window-pane material: each object switches on when its random < node 'LIT'."""
    key = ('litobj', name)
    if key in _mats: return _mats[key]
    m, nt, p = _principled(name)
    n = nt.nodes
    oi = n.new('ShaderNodeObjectInfo')
    v = n.new('ShaderNodeValue'); v.name = 'LIT'; v.outputs[0].default_value = 0.0
    lt = n.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'
    nt.links.new(oi.outputs['Random'], lt.inputs[0]); nt.links.new(v.outputs[0], lt.inputs[1])
    s = n.new('ShaderNodeMath'); s.operation = 'MULTIPLY'; s.inputs[1].default_value = strength
    nt.links.new(lt.outputs[0], s.inputs[0])
    hue = n.new('ShaderNodeMix'); hue.data_type = 'RGBA'
    hue.inputs['A'].default_value = (*color, 1); hue.inputs['B'].default_value = (1.0, 0.88, 0.65, 1)
    nt.links.new(oi.outputs['Random'], hue.inputs['Factor'])
    nt.links.new(hue.outputs['Result'], p.inputs['Emission Color'])
    nt.links.new(s.outputs[0], p.inputs['Emission Strength'])
    p.inputs['Base Color'].default_value = (*off, 1)
    p.inputs['Roughness'].default_value = 0.15
    _mats[key] = m
    return m


def sun_from(name, toward_src, power=3.0, color=(1, 0.9, 0.75), angle=0.05):
    """Sun whose light comes FROM the direction toward_src (vector pointing at the sun)."""
    ld = bpy.data.lights.new(name, 'SUN'); ld.energy = power; ld.color = color; ld.angle = angle
    o = bpy.data.objects.new(name, ld); link(o)
    o.rotation_euler = Vector(toward_src).normalized().to_track_quat('Z', 'Y').to_euler()
    return o
