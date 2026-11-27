"""Facts on Demand 3D kit for Blender (4.5 LTS), driven 100% by code.
Everything in a scene is built and animated from Python, so a scene renders the same way
every time. Style target: the reference Shorts (owner, 2026-11-27): low-poly cartoon world,
big round heads, soft light, ink outlines, depth haze, a camera that never stands still.
v2 (owner feedback 2026-11-27): better figures (eyes with pupils + shine, nose, ears, shaped
hair, real beard), full background to the horizon, textured surfaces, higher quality.
"""
import math
import bpy

FPS = 30
HORIZON = (0.99, 0.91, 0.76)  # warm haze colour (linear), also used for the mist


# ------------------------------------------------------------------ scene setup
def reset(frames, w=1920, h=1080, engine="eevee", samples=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    if engine == "eevee":
        for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                sc.render.engine = name
                break
            except TypeError:
                pass
        ee = sc.eevee
        for attr, val in (("taa_render_samples", samples or 96), ("use_shadows", True), ("use_gtao", True),
                          ("shadow_ray_count", 2), ("shadow_step_count", 8), ("use_raytracing", True)):
            if hasattr(ee, attr):
                try:
                    setattr(ee, attr, val)
                except Exception:
                    pass
    else:
        sc.render.engine = "CYCLES"
        sc.cycles.samples = samples or 16
        sc.cycles.use_denoising = True
        sc.cycles.device = "CPU"
    sc.render.use_motion_blur = True
    try:   # hair strands as camera-facing strips (full width in EEVEE, no thin gaps)
        sc.render.hair_type = "STRIP"
        sc.render.hair_subdiv = 1
    except Exception:
        pass
    sc.render.motion_blur_shutter = 0.35
    # cartoon ink lines (particles/haze live in the "nolines" collection and get none)
    sc.render.use_freestyle = True
    sc.render.line_thickness_mode = "ABSOLUTE"
    sc.render.line_thickness = 1.8 * w / 1920
    fs = sc.view_layers[0].freestyle_settings
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new("ink")
    ls.select_by_visibility = True
    ls.select_silhouette = ls.select_border = True
    ls.select_crease = False
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("ink")
    ls.linestyle.color = (0.16, 0.09, 0.04)
    nol = bpy.data.collections.new("nolines")
    sc.collection.children.link(nol)
    ls.select_by_collection = True
    ls.collection = nol
    ls.collection_negation = "EXCLUSIVE"
    sc.view_settings.view_transform = "Standard"
    return sc


def nolines(o):
    """Move an object (and its children) into the no-outline collection."""
    nol = bpy.data.collections["nolines"]
    for c in list(o.users_collection):
        c.objects.unlink(o)
    nol.objects.link(o)
    for ch in o.children:
        nolines(ch)
    return o


def world_sky(top="#7fb6e0", horizon=HORIZON, strength=1.0, mist=(22, 110)):
    """Blue sky that fades into a warm haze at the horizon."""
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    horizon = hexrgb(horizon)
    ramp.color_ramp.elements[0].color = (*horizon, 1)
    ramp.color_ramp.elements[1].position = 0.45
    ramp.color_ramp.elements[1].color = (*hexrgb(top), 1)
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    w.mist_settings.start, w.mist_settings.depth, w.mist_settings.falloff = mist[0], mist[1], "QUADRATIC"


def post(haze=0.6, glow=True, color=None):
    """Compositor: depth haze (mist pass) + a soft glow."""
    sc = bpy.context.scene
    sc.view_layers[0].use_pass_mist = True
    sc.use_nodes = True
    nt = sc.node_tree
    rl, comp = nt.nodes["Render Layers"], nt.nodes["Composite"]
    mul = nt.nodes.new("CompositorNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = haze
    mix = nt.nodes.new("CompositorNodeMixRGB")
    mix.inputs[2].default_value = (*(color or HORIZON), 1)
    nt.links.new(rl.outputs["Mist"], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(rl.outputs["Image"], mix.inputs[1])
    last = mix
    if glow:
        try:
            g = nt.nodes.new("CompositorNodeGlare")
            for t in ("BLOOM", "FOG_GLOW"):
                try:
                    g.glare_type = t
                    break
                except TypeError:
                    pass
            if hasattr(g, "threshold"):
                g.threshold = 0.85
            if hasattr(g, "mix"):
                g.mix = -0.75
            if hasattr(g, "quality"):
                g.quality = "HIGH"
            nt.links.new(mix.outputs[0], g.inputs[0])
            last = g
        except Exception as e:
            print("glare skipped:", e)
    nt.links.new(last.outputs[0], comp.inputs[0])


def sun(rot=(math.radians(52), 0, math.radians(35)), energy=3.6, color=(1, 0.92, 0.8)):
    d = bpy.data.lights.new("sun", "SUN")
    d.energy, d.color = energy, color
    d.angle = math.radians(6)
    o = bpy.data.objects.new("sun", d)
    o.rotation_euler = rot
    bpy.context.collection.objects.link(o)
    return o


# ------------------------------------------------------------------ materials
_mats = {}


def hexrgb(h):
    if not isinstance(h, str):
        return h
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def _shade(rgb, f):
    return tuple(min(1, c * f) for c in rgb)


def mat(name, rgb, rough=0.9, emit=0.0, noise=0.0, bump=0.0, nscale=4.0):
    """Flat cartoon material. noise>0 adds soft colour variation (painted look), bump>0 relief."""
    rgb = hexrgb(rgb)
    key_ = (name, rgb, rough, emit, noise, bump, nscale)
    if key_ in _mats:
        return _mats[key_]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if noise or bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = nscale
        nz.inputs["Detail"].default_value = 3
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        if noise:
            r = nt.nodes.new("ShaderNodeValToRGB")
            r.color_ramp.elements[0].position, r.color_ramp.elements[1].position = 0.35, 0.65
            r.color_ramp.elements[0].color = (*_shade(rgb, 1 - noise), 1)
            r.color_ramp.elements[1].color = (*_shade(rgb, 1 + noise * 0.6), 1)
            nt.links.new(nz.outputs["Fac"], r.inputs["Fac"])
            nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
        if bump:
            bp = nt.nodes.new("ShaderNodeBump")
            bp.inputs["Strength"].default_value = bump
            nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
            nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    _mats[key_] = m
    return m


def mat_pattern(name, base, line, kind="cobble", scale=2.2, bump=0.4):
    """Procedural pattern: cobble (voronoi stones + mortar), tiles (roof rows), planks."""
    base, line = hexrgb(base), hexrgb(line)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.92
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    if kind == "cobble":
        v = nt.nodes.new("ShaderNodeTexVoronoi")
        v.feature = "DISTANCE_TO_EDGE"
        v.inputs["Scale"].default_value = scale
        nt.links.new(tc.outputs["Object"], v.inputs["Vector"])
        edge = v.outputs["Distance"]
        lo, hi = 0.02, 0.07
    else:  # tiles / planks: bands
        wv = nt.nodes.new("ShaderNodeTexWave")
        wv.bands_direction = "Z" if kind == "tiles" else "X"
        wv.inputs["Scale"].default_value = scale
        wv.wave_profile = "SAW"
        nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
        edge = wv.outputs["Fac"]
        lo, hi = 0.05, 0.16
    er = nt.nodes.new("ShaderNodeValToRGB")
    er.color_ramp.elements[0].position, er.color_ramp.elements[1].position = lo, hi
    er.color_ramp.elements[0].color, er.color_ramp.elements[1].color = (0, 0, 0, 1), (1, 1, 1, 1)
    nt.links.new(edge, er.inputs["Fac"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*_shade(base, 0.82), 1)
    cr.color_ramp.elements[1].color = (*_shade(base, 1.12), 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
    mx = nt.nodes.new("ShaderNodeMixRGB")
    mx.inputs[1].default_value = (*line, 1)
    nt.links.new(er.outputs["Color"], mx.inputs[0])
    nt.links.new(cr.outputs["Color"], mx.inputs[2])
    nt.links.new(mx.outputs[0], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
    nt.links.new(er.outputs["Color"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


# ------------------------------------------------------------------ primitives
def _done(o, m=None, parent=None, smooth=True):
    if m is not None:
        o.data.materials.append(m)
    if parent is not None:
        o.parent = parent
    if smooth and hasattr(o.data, "polygons"):
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def box(name, size, loc, m, parent=None, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)  # textures keep real-world size
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL"); b.width = bevel; b.segments = 2
    return _done(o, m, parent, smooth=False)


def ball(name, r, loc, m, parent=None, scale=(1, 1, 1), seg=24, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, scale
    return _done(o, m, parent)


def ico(name, r, loc, m, parent=None, scale=(1, 1, 1), sub=1):
    """Faceted low-poly blob (trees, bushes, hills)."""
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, location=loc, subdivisions=sub)
    o = bpy.context.object
    o.name, o.scale = name, scale
    return _done(o, m, parent, smooth=False)


def cyl(name, r, depth, loc, m, parent=None, rot=(0, 0, 0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object
    o.name = name
    return _done(o, m, parent, smooth=verts > 8)


def cone(name, r, depth, loc, m, parent=None, verts=12, r2=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=depth, location=loc, vertices=verts, rotation=rot)
    o = bpy.context.object
    o.name = name
    return _done(o, m, parent, smooth=verts > 12)


def torus(name, R, r, loc, m, parent=None, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, scale
    return _done(o, m, parent)


def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    if parent is not None:
        o.parent = parent
    return o


def prism_roof(name, w, d, h, loc, m, rotz=0.0):
    """Pitched roof: a triangular prism along x (w), ridge height h."""
    me = bpy.data.meshes.new(name)
    v = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0), (-w / 2, 0, h), (w / 2, 0, h)]
    f = [(0, 1, 5, 4), (3, 4, 5, 2), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]
    me.from_pydata(v, [], f)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (0, 0, rotz)
    o.data.materials.append(m)
    return o


# ------------------------------------------------------------------ keyframes
def key(o, path, frame, value, interp="BEZIER"):
    setattr(o, path, value)
    o.keyframe_insert(data_path=path, frame=frame)


def sec(s):
    return int(round(s * FPS)) + 1


# ------------------------------------------------------------------ the cast
# hair styles: clumps (x, y, z, r, sx, sy, sz) on top of the base cap, in head space
HAIR = {
    "swept": [(-0.13, -0.2, 0.69, 0.17, 1.5, 0.85, 0.62), (0.14, -0.22, 0.67, 0.13, 1.25, 0.85, 0.6),
              (0.0, 0.0, 0.8, 0.2, 1.4, 1.2, 0.5), (-0.3, -0.05, 0.6, 0.12, 0.8, 1.2, 1.0),
              (0.3, -0.03, 0.6, 0.11, 0.8, 1.2, 1.0)],
    "curly": [(x * 0.13, -0.22 + abs(x) * 0.03, 0.67 + (x % 2) * 0.03, 0.105, 1, 0.9, 0.9) for x in range(-3, 4)]
             + [(-0.36, 0.02, 0.58, 0.12, 1, 1, 1.1), (0.36, 0.02, 0.58, 0.12, 1, 1, 1.1),
                (-0.18, 0.12, 0.8, 0.15, 1, 1, 0.8), (0.18, 0.12, 0.8, 0.15, 1, 1, 0.8), (0, 0.3, 0.7, 0.16, 1.3, 1, 0.9)],
    "short": [(0, -0.15, 0.72, 0.15, 2.2, 0.8, 0.5)],
}
CAST = {
    # the three main characters (PRODUCTION-RULES): two short compact ones + the round ruler.
    "main": dict(hair="#3b2a1e", style="swept", beard="#3b2a1e", glasses=False, tunic="#6d6253", hose="#4a4038", body=0.25, scarf=True),
    "two": dict(hair="#d0662a", style="curly", beard=None, glasses=True, tunic="#55626a", hose="#3e4448", body=0.25, scarf=True),
    "king": dict(hair="#dcd7cf", style="short", beard="#dcd7cf", glasses=False, tunic="#a8262a", hose="#5a2020", body=0.34, scarf=True),
}


def npc(tunic, hose="#5a5048", hair="#5a3a22", style="short", hat=None, body=0.26, beard=None, skin="#f6e7d4"):
    return dict(hair=hair, style=style, beard=beard, glasses=False, tunic=tunic, hose=hose, body=body, scarf=False, hat=hat, skin=skin)


class Figure:
    """Big-head cartoon figure, built from primitives. Every joint is an empty you can key.
    Exactly two arms and two legs, always (PRODUCTION-RULES). Faces -Y (towards camera).
    Boots are whole, soles sit exactly on z=0 (feet never sink)."""

    def __init__(self, who, loc=(0, 0, 0), name=None, spec=None):
        c = dict(spec or CAST[who])
        n = name or who
        skin = mat("skin-" + c.get("skin", "#fbf1e4"), c.get("skin", "#fbf1e4"), 0.75)
        cheek = mat("cheek", "#f2a48e", 0.8)
        ink = mat("ink", "#1c120a", 0.4)
        white = mat("eyewhite", "#ffffff", 0.3)
        shine = mat("shine", "#ffffff", 0.2, emit=2.0)
        lips = mat("mouth", "#5a1a14", 0.6)
        tunic = mat(f"tunic-{n}", c["tunic"], 0.95, noise=0.12, nscale=9)
        hose = mat(f"hose-{n}", c["hose"], 0.9)
        boot, sole = mat("boot", "#4a2e1a", 0.55), mat("sole", "#24160c", 0.7)
        leather = mat("beltleather", "#3a2618", 0.6)
        brass = mat("brass", "#d9a63a", 0.3)
        self.root = empty(f"{n}-root", loc)
        self.hips = empty(f"{n}-hips", (0, 0, 0.72), self.root)
        bw = c["body"]
        # ---- legs (pivot at the hip) + whole boots; sole bottom at hip-0.72 = ground
        self.legs = []
        for side in (-1, 1):
            p = empty(f"{n}-leg{side}", (side * 0.105, 0, 0), self.hips)
            cyl(f"{n}-thigh{side}", 0.068, 0.62, (0, 0, -0.31), hose, p)
            cyl(f"{n}-shaft{side}", 0.078, 0.2, (0, 0, -0.6), boot, p)
            box(f"{n}-boot{side}", (0.17, 0.2, 0.11), (0, -0.02, -0.645), boot, p, bevel=0.04)
            ball(f"{n}-toe{side}", 0.085, (0, -0.12, -0.655), boot, p, scale=(1, 1.15, 0.72))
            box(f"{n}-sole{side}", (0.18, 0.32, 0.03), (0, -0.06, -0.705), sole, p, bevel=0.01)
            self.legs.append(p)
        # ---- body (pivot at the hips so it can lean)
        self.torso = empty(f"{n}-torso", (0, 0, 0), self.hips)
        ball(f"{n}-body", 1, (0, 0, 0.32), tunic, self.torso, scale=(bw, bw * 0.86, 0.36), seg=32)
        cone(f"{n}-hem", bw * 1.12, 0.26, (0, 0, 0.04), tunic, self.torso, verts=32, r2=bw * 0.82)
        torus(f"{n}-belt", bw * 0.96, 0.032, (0, 0, 0.15), leather, self.torso, scale=(1, 0.87, 1))
        box(f"{n}-buckle", (0.08, 0.03, 0.07), (0, -bw * 0.86 - 0.02, 0.15), brass, self.torso, bevel=0.01)
        cyl(f"{n}-neck", 0.085, 0.16, (0, 0, 0.66), skin, self.torso)
        # ---- arms (pivot at the shoulder): sleeve, cuff, mitten hand with thumb
        self.arms = []
        for side in (-1, 1):
            p = empty(f"{n}-arm{side}", (side * (bw + 0.01), 0, 0.5), self.torso)
            ball(f"{n}-shoulder{side}", 0.082, (0, 0, 0), tunic, p)
            cone(f"{n}-sleeve{side}", 0.07, 0.46, (0, 0, -0.23), tunic, p, verts=16, r2=0.075, rot=(math.pi, 0, 0))
            torus(f"{n}-cuff{side}", 0.068, 0.02, (0, 0, -0.45), tunic, p)
            ball(f"{n}-hand{side}", 0.075, (0, 0, -0.53), skin, p, scale=(0.85, 0.7, 1.1))
            ball(f"{n}-thumb{side}", 0.032, (-side * 0.06, -0.035, -0.5), skin, p)
            p.rotation_euler = (0, side * math.radians(12), 0)
            self.arms.append(p)
        if c.get("scarf"):  # the team colour, on every main character
            orange = mat("scarf", "#ef7a1d", 0.85, noise=0.08, nscale=14)
            torus(f"{n}-scarf", 0.15, 0.065, (0, 0, 0.66), orange, self.torso, scale=(1, 0.92, 1))
            ball(f"{n}-knot", 0.065, (0.08, -0.13, 0.62), orange, self.torso)
            box(f"{n}-tail1", (0.085, 0.035, 0.24), (0.1, -0.17, 0.5), orange, self.torso, rot=(0.12, 0.22, 0), bevel=0.015)
            box(f"{n}-tail2", (0.08, 0.035, 0.19), (0.03, -0.18, 0.52), orange, self.torso, rot=(0.12, -0.12, 0), bevel=0.015)
        # ---- head (pivot at the neck)
        self.head = empty(f"{n}-head", (0, 0, 0.72), self.torso)
        H = self.head
        ball(f"{n}-skull", 0.4, (0, 0, 0.38), skin, H, scale=(1, 0.95, 0.98), seg=48)
        for side in (-1, 1):
            ball(f"{n}-ear{side}", 0.08, (side * 0.385, 0.02, 0.36), skin, H, scale=(0.5, 0.75, 1))
            ball(f"{n}-cheek{side}", 0.07, (side * 0.22, -0.3, 0.27), cheek, H, scale=(1, 0.35, 0.65))
        ball(f"{n}-nose", 0.065, (0, -0.385, 0.33), skin, H, scale=(1, 0.8, 0.9))
        # eyes: white + pupil + shine, grouped so a blink squashes the whole eye
        self.eyes, self.brows = [], []
        browc = "#8a8580" if c["hair"] == "#dcd7cf" else c["hair"]
        for side in (-1, 1):
            e = empty(f"{n}-eye{side}", (side * 0.14, -0.32, 0.43), H)
            ball(f"{n}-white{side}", 0.088, (0, 0, 0), white, e, scale=(1, 0.6, 1.2))
            ball(f"{n}-pupil{side}", 0.047, (side * -0.008, -0.036, -0.01), ink, e, scale=(1, 0.6, 1.2))
            nolines(ball(f"{n}-shine{side}", 0.016, (side * -0.024, -0.064, 0.03), shine, e))
            self.eyes.append(e)
            b = ball(f"{n}-brow{side}", 0.07, (side * 0.14, -0.35, 0.565), mat(f"brow-{n}", browc, 0.8), H,
                     scale=(1.15, 0.38, 0.3), rot=(0, side * 0.1, 0))
            self.brows.append(b)
            if c["glasses"]:
                torus(f"{n}-lens{side}", 0.105, 0.014, (side * 0.14, -0.4, 0.43), ink, H, rot=(math.pi / 2, 0, 0))
                box(f"{n}-arm-g{side}", (0.012, 0.36, 0.014), (side * 0.25, -0.22, 0.44), ink, H)
        if c["glasses"]:
            box(f"{n}-bridge", (0.07, 0.015, 0.015), (0, -0.405, 0.44), ink, H)
        self.mouth = ball(f"{n}-mouth", 0.06, (0, -0.355, 0.235), lips, H, scale=(1.3, 0.3, 0.42))
        # hair: base cap + style clumps
        hair = mat(f"hair-{n}", c["hair"], 0.85, noise=0.15, nscale=12)
        if c.get("hat") != "coif":
            ball(f"{n}-hair", 0.43, (0, 0.1, 0.47), hair, H, scale=(1.03, 1.0, 0.86), seg=32)
            for i, (x, y, z, r, sx, sy, sz) in enumerate(HAIR[c["style"]]):
                ball(f"{n}-hc{i}", r, (x, y, z), hair, H, scale=(sx, sy, sz), seg=20)
        if c["beard"]:
            bm = mat(f"beard-{n}", c["beard"], 0.95, noise=0.15, nscale=14)
            ball(f"{n}-chin", 0.15, (0, -0.27, 0.09), bm, H, scale=(1.3, 0.8, 0.85))
            for side in (-1, 1):
                ball(f"{n}-jaw{side}", 0.12, (side * 0.22, -0.2, 0.17), bm, H, scale=(1, 0.95, 1.15))
                ball(f"{n}-burn{side}", 0.08, (side * 0.345, -0.06, 0.3), bm, H, scale=(0.6, 1, 1.5))
                ball(f"{n}-stache{side}", 0.06, (side * 0.065, -0.375, 0.288), bm, H, scale=(1.6, 0.6, 0.55), rot=(0, side * -0.25, 0))
        hat = c.get("hat")
        if hat == "coif":  # white linen coif (women, period-correct)
            linen = mat("linen", "#efe4cc", 0.9, noise=0.08, nscale=10)
            ball(f"{n}-coif", 0.45, (0, 0.1, 0.47), linen, H, scale=(1.02, 1.0, 0.95), seg=32)
        elif hat == "hood":
            hm = mat(f"hood-{n}", c["tunic"], 0.95, noise=0.1, nscale=9)
            ball(f"{n}-hood", 0.47, (0, 0.1, 0.47), hm, H, scale=(1.02, 1, 0.92), seg=32)
            cone(f"{n}-liri", 0.12, 0.5, (0, 0.42, 0.55), hm, H, verts=12, rot=(-1.9, 0, 0))
        elif hat == "cap":
            cm = mat(f"cap-{n}", "#7a2a22", 0.9)
            cyl(f"{n}-brim", 0.44, 0.05, (0, 0, 0.66), cm, H, verts=24)
            ball(f"{n}-crown", 0.36, (0, 0.02, 0.7), cm, H, scale=(1, 1, 0.55))
        self._brow_base = [b.location.copy() for b in self.brows]

    # ---- acting helpers (frames are 1-based Blender frames)
    def at(self, frame, loc=None, rotz=None):
        if loc is not None:
            key(self.root, "location", frame, loc)
        if rotz is not None:
            key(self.root, "rotation_euler", frame, (0, 0, rotz))

    def walk(self, f0, f1, start, end, step=8):
        """Walk from start to end (x,y,z): legs and arms swing, hips bob."""
        dx, dy = end[0] - start[0], end[1] - start[1]
        self.at(f0, start, math.atan2(dx, -dy) if (dx or dy) else None)
        self.at(f1, end)
        for f in range(f0, f1 + 1, max(1, step // 2)):
            ph = (f - f0) / step * math.pi
            s = math.sin(ph)
            key(self.legs[0], "rotation_euler", f, (s * 0.5, 0, 0))
            key(self.legs[1], "rotation_euler", f, (-s * 0.5, 0, 0))
            key(self.arms[0], "rotation_euler", f, (-s * 0.6, -0.2, 0))
            key(self.arms[1], "rotation_euler", f, (s * 0.6, 0.2, 0))
            key(self.hips, "location", f, (0, 0, 0.72 + abs(math.cos(ph)) * 0.04))
        for i, p in enumerate(self.legs + self.arms):
            key(p, "rotation_euler", f1 + 3, (0, 0, 0) if i < 2 else (0, (-0.2, 0.2)[i - 2], 0))

    def blink(self, frame):
        for e in self.eyes:
            key(e, "scale", frame - 1, (1, 1, 1))
            key(e, "scale", frame + 1, (1, 1, 0.1))
            key(e, "scale", frame + 4, (1, 1, 1))

    def brows_angry(self, frame, on=True):
        for i, b in enumerate(self.brows):
            side = -1 if i == 0 else 1
            base = self._brow_base[i]
            key(b, "rotation_euler", frame, (0, side * (-0.5 if on else 0.1), 0))
            key(b, "location", frame, (base.x, base.y, base.z - (0.03 if on else 0)))

    def talk(self, f0, f1):
        for f in range(f0, f1, 3):
            open_ = ((f - f0) // 3) % 3
            key(self.mouth, "scale", f, (1.3 - open_ * 0.12, 0.3, 0.42 + open_ * 0.45))
        key(self.mouth, "scale", f1, (1.3, 0.3, 0.42))


# ------------------------------------------------------------------ render
def render_mp4(out):
    import os
    sc = bpy.context.scene
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    try:
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
        sc.render.filepath = out
        bpy.ops.render.render(animation=True)
    except Exception as e:  # newer Blender changed the video API: fall back to PNG frames
        print("video output failed, writing PNG frames instead:", e)
        sc.render.image_settings.file_format = "PNG"
        sc.render.filepath = out.replace(".mp4", "_frames/f_")
        bpy.ops.render.render(animation=True)
