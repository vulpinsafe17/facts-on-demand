"""3D sets for film 1 (football), one builder per background. 100 % code, fixed seeds.
Convention: the action happens around the origin, the camera looks from -Y towards +Y,
the backdrop always reaches the horizon (owner rule) or closes in a full room."""
import math, random
import bpy
import fod3d as k
from fod3d import mat, box, ball, cyl, cone, ico, prism_roof, hexrgb
import cast3d as c3

# ------------------------------------------------------------------ light + sky presets
PRESETS = {
    "day":     dict(top="#7fb6e0", hor="#fbe8c4", sun=(52, 35), energy=3.6, scol=(1, 0.93, 0.82), mist=(25, 140), haze=0.55),
    "warm":    dict(top="#8cc0e4", hor="#fde3b0", sun=(40, -40), energy=3.8, scol=(1, 0.88, 0.7), mist=(25, 140), haze=0.5),
    "dusk":    dict(top="#5a5a9a", hor="#f6a45a", sun=(12, 160), energy=3.0, scol=(1, 0.6, 0.35), mist=(20, 120), haze=0.6),
    "night":   dict(top="#0e1530", hor="#2a3458", sun=(35, 60), energy=0.35, scol=(0.6, 0.7, 1.0), mist=(15, 80), haze=0.5),
    "frost":   dict(top="#a8c4dc", hor="#eef0ee", sun=(14, -30), energy=2.6, scol=(1, 0.9, 0.8), mist=(12, 90), haze=0.7),
    "interior": dict(top="#3a2a1a", hor="#5a4028", sun=(55, 30), energy=0.0, scol=(1, 0.9, 0.7), mist=(40, 200), haze=0.0),
    "grey":    dict(top="#9aa6b0", hor="#d8d4c8", sun=(45, 20), energy=2.4, scol=(1, 0.95, 0.9), mist=(18, 110), haze=0.6),
}


def light(preset, mist=None):
    p = dict(PRESETS[preset])
    if mist:
        p["mist"] = mist
    k.world_sky(top=p["top"], horizon=p["hor"], strength=1.0 if preset != "interior" else 0.6, mist=p["mist"])
    if p["energy"]:
        k.sun(rot=(math.radians(90 - p["sun"][0]), 0, math.radians(p["sun"][1])), energy=p["energy"], color=p["scol"])
    k.post(haze=p["haze"], color=hexrgb(p["hor"]))


def point(loc, energy=60, color=(1, 0.75, 0.45), radius=0.1):
    L = bpy.data.lights.new("pt", "POINT"); L.energy, L.color = energy, color
    L.shadow_soft_size = radius
    o = bpy.data.objects.new("pt", L); bpy.context.collection.objects.link(o); o.location = loc
    return o


def area(loc, rot, energy=300, size=4, color=(1, 0.95, 0.88)):
    L = bpy.data.lights.new("ar", "AREA"); L.energy, L.size, L.color = energy, size, color
    o = bpy.data.objects.new("ar", L); bpy.context.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    return o


# ------------------------------------------------------------------ shared pieces
def ground(color="#93ad5c", size=600, noise=0.18, z=-0.1):
    return box("ground", (size, size, 0.2), (0, 0, z), mat("ground" + color, color, noise=noise, nscale=0.15))


def hills(rnd, colors=("#86a457", "#7c9a52", "#94b064"), dist=(170, 230), n=22, zoff=-30):
    hm = [mat(f"hill{c}", c, noise=0.15, nscale=0.05) for c in colors]
    for i in range(n):
        a = -math.pi + i * math.tau / n
        d = rnd.uniform(*dist)
        ico(f"hill{i}", 60 + rnd.uniform(0, 40), (math.sin(a) * d, math.cos(a) * d, zoff), hm[i % len(hm)], scale=(1.4, 1, 0.5), sub=2)


def trees(rnd, n=60, rmin=30, rmax=120, kind="round", exclude=None, leafc=("#5f8a3c", "#6f9a44", "#4f7a36")):
    leaf = [mat(f"leaf{c}", c, noise=0.12, nscale=3) for c in leafc]
    bark = mat("bark", "#5a3e2a")
    for i in range(n):
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(rmin, rmax)
        x, y = math.sin(a) * d, math.cos(a) * d
        if exclude and exclude(x, y):
            continue
        s = rnd.uniform(1.4, 3.0)
        tree(f"t{i}", x, y, s, leaf[i % 3], bark, kind)


def tree(name, x, y, s, leafm, bark, kind="round"):
    cyl(name + "tr", 0.22 * s, 2 * s, (x, y, s), bark, verts=7)
    if kind == "pine":
        for j in range(3):
            cone(name + f"c{j}", (1.5 - j * 0.35) * s, 1.8 * s, (x, y, (2.2 + j * 1.1) * s), leafm, verts=8)
    elif kind == "bare":
        for j in range(5):
            a = j * 1.3
            cyl(name + f"b{j}", 0.07 * s, 1.4 * s, (x + math.cos(a) * 0.4 * s, y + math.sin(a) * 0.4 * s, (1.9 + j * 0.15) * s), bark,
                rot=(math.cos(a) * 0.8, math.sin(a) * 0.8, 0), verts=5)
    else:
        ico(name + "cn", 1.4 * s, (x, y, 2.6 * s), leafm, scale=(1, 1, 1.15))


def clouds(rnd, n=8, z=(28, 38), col=(1, 0.98, 0.95), emit=0.25, frames=300):
    cm = mat("cloud" + str(col), col, 1.0, emit=emit)
    for i in range(n):
        c = k.empty(f"cloud{i}", (-70 + i * 18 + rnd.uniform(-5, 5), 80 + rnd.uniform(0, 70), rnd.uniform(*z)))
        for j in range(6):
            ball(f"cl{i}{j}", 3.0 + rnd.random() * 2.2, (j * 3.2 - 8, rnd.uniform(-1.5, 1.5), rnd.random() * 1.6), cm, c, scale=(1, 0.6, 0.65), seg=16)
        k.key(c, "location", 1, c.location.copy())
        k.key(c, "location", frames, (c.location.x + 5, c.location.y, c.location.z))


def crowd_mat(name="crowd", scale=55):
    """Colourful dots (voronoi cells) = a packed crowd seen from afar. Cheap and lively."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.9
    tc = nt.nodes.new("ShaderNodeTexCoord"); v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], v.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB"); cr = r.color_ramp
    cols = ["#c83a2a", "#2a5ac8", "#f0e0c0", "#3a8a4a", "#e8c83a", "#f4f4f4", "#2a2a2a", "#ef7a1d", "#7a3a8a"]
    cr.elements[0].color = (*hexrgb(cols[0]), 1); cr.elements[1].color = (*hexrgb(cols[-1]), 1); cr.elements[1].position = 1.0
    for i, c in enumerate(cols[1:-1]):
        e = cr.elements.new((i + 1) / (len(cols) - 1)); e.color = (*hexrgb(c), 1)
    cr.interpolation = "CONSTANT"
    nt.links.new(v.outputs["Color"], r.inputs["Fac"]) if "Color" in v.outputs else None
    sep = nt.nodes.new("ShaderNodeSeparateColor") if hasattr(bpy.types, "ShaderNodeSeparateColor") else None
    if sep:
        nt.links.new(v.outputs["Color"], sep.inputs[0]); nt.links.new(sep.outputs[0], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    return m


def scroll(name, loc, m_paper=None, length=0.5, r=0.05, rot=(0, math.pi / 2, 0), seal=True):
    m_paper = m_paper or mat("paper", "#f1e4c4", 0.8, noise=0.1, nscale=12)
    o = cyl(name, r, length, loc, m_paper, rot=rot, verts=16)
    if seal:
        cyl(name + "seal", r * 0.9, 0.025, (loc[0], loc[1] - r - 0.01, loc[2]), mat("wax", "#a8141a", 0.3), rot=(math.pi / 2, 0, 0), verts=16)
    return o


def ball_mat(name, color, panels=2.2, seam="#3a2414"):
    """Stitched leather: panels (voronoi cells) with sunken seams, worn colour variation, soft sheen."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    rgb = hexrgb(color)
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.68
    if "Sheen Weight" in b.inputs:
        b.inputs["Sheen Weight"].default_value = 0.15
    tc = nt.nodes.new("ShaderNodeTexCoord")
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"; v.inputs["Scale"].default_value = panels
    nt.links.new(tc.outputs["Generated"], v.inputs["Vector"])
    vc = nt.nodes.new("ShaderNodeTexVoronoi"); vc.inputs["Scale"].default_value = panels
    nt.links.new(tc.outputs["Generated"], vc.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9; nz.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Generated"], nz.inputs["Vector"])
    er = nt.nodes.new("ShaderNodeValToRGB"); er.color_ramp.elements[0].position = 0.0; er.color_ramp.elements[1].position = 0.03
    nt.links.new(v.outputs["Distance"], er.inputs["Fac"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*_sh(rgb, 0.6), 1); cr.color_ramp.elements[1].color = (*_sh(rgb, 1.25), 1)
    mxn = nt.nodes.new("ShaderNodeMath"); mxn.operation = "MULTIPLY_ADD"; mxn.inputs[1].default_value = 0.5
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(vc.outputs["Color"], sep.inputs[0])
    nt.links.new(nz.outputs["Fac"], mxn.inputs[0]); nt.links.new(sep.outputs[0], mxn.inputs[2])
    nt.links.new(mxn.outputs[0], cr.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMixRGB"); mix.inputs[1].default_value = (*hexrgb(seam), 1)
    nt.links.new(er.outputs["Color"], mix.inputs[0]); nt.links.new(cr.outputs["Color"], mix.inputs[2])
    nt.links.new(mix.outputs[0], b.inputs["Base Color"])
    hb = nt.nodes.new("ShaderNodeMath"); hb.operation = "MULTIPLY_ADD"; hb.inputs[1].default_value = 0.15
    nt.links.new(nz.outputs["Fac"], hb.inputs[0]); nt.links.new(er.outputs["Color"], hb.inputs[2])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(hb.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def _sh(rgb, f):
    return tuple(min(1, c * f) for c in rgb)


def cuju_ball(name, loc, r=0.13):
    """Han cuju ball: a smooth leather ball of stitched panels, stuffed (slightly lumpy). No feathers sticking out."""
    b = ball(name, r, loc, ball_mat("cujuleather3", "#6e4424", panels=2.0), seg=48)
    tex = bpy.data.textures.get("balllumps") or bpy.data.textures.new("balllumps", "CLOUDS")
    tex.noise_scale = 0.6
    d = b.modifiers.new("lumps", "DISPLACE"); d.texture = tex; d.strength = r * 0.06; d.mid_level = 0.5
    return b


def leather_ball(name, loc, r=0.12, color="#8a5a2e"):
    """Laced leather ball (medieval to Victorian): panels, seams and a lace."""
    b = ball(name, r, loc, ball_mat("lball3" + color, "#7a4c2a", panels=2.6), seg=48)
    c3.tube(name + "lace", [(0, -r * 1.01, 0.04), (0, -r * 1.02, 0), (0, -r * 1.01, -0.04)], 0.006, mat("lace", "#e8dcc4"), b)
    for j in range(4):
        z = -0.03 + j * 0.02
        c3.tube(name + f"x{j}", [(-0.012, -r * 1.015, z), (0.012, -r * 1.015, z)], 0.003, mat("lace", "#e8dcc4"), b)
    return b


def table(name, loc, w=2.2, d=1.0, h=0.8, m=None):
    m = m or k.mat_pattern("planks" + name, "#7a5232", "#3a2414", "planks", scale=9, bump=0.25)
    x, y, z = loc
    box(name + "top", (w, d, 0.08), (x, y, z + h), m, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(name + f"leg{sx}{sy}", (0.08, 0.08, h), (x + sx * (w / 2 - 0.12), y + sy * (d / 2 - 0.1), z + h / 2), m)
    return z + h + 0.04


def candle(name, loc, h=0.18, light_=True, e=25):
    cyl(name, 0.03, h, (loc[0], loc[1], loc[2] + h / 2), mat("wax2", "#f4ead0", 0.6), verts=12)
    ball(name + "fl", 0.018, (loc[0], loc[1], loc[2] + h + 0.03), mat("flame", "#ffb040", 0.5, emit=12), scale=(1, 1, 1.8), seg=12)
    if light_:
        point((loc[0], loc[1], loc[2] + h + 0.08), e, (1, 0.7, 0.4), 0.05)


def room(w, d, h, wall="#c8b89a", floor=None, back_windows=0, side=True, wall_m=None, ceiling=True, window_col="#9ac4e8", window_emit=1.0):
    """Box room open towards the camera (-Y)."""
    wm = wall_m or mat("wall" + wall, wall, 0.9, noise=0.1, nscale=1.5, bump=0.1)
    fm = floor or k.mat_pattern("floorplanks", "#6a4428", "#3a2414", "planks", scale=4, bump=0.2)
    box("floor", (w, d + 6, 0.2), (0, d / 2 - 3, -0.1), fm)
    box("backwall", (w, 0.3, h), (0, d, h / 2), wm)
    if side:
        for sx in (-1, 1):
            box(f"sidewall{sx}", (0.3, d + 6, h), (sx * w / 2, d / 2 - 3, h / 2), wm)
    if ceiling:
        box("ceiling", (w, d + 6, 0.2), (0, d / 2 - 3, h), mat("ceil", "#5a3a22"))
    for i in range(back_windows):
        x = (i - (back_windows - 1) / 2) * (w / max(back_windows, 1))
        box(f"win{i}", (1.0, 0.1, 1.6), (x, d - 0.12, h * 0.55), mat("winglass" + window_col, window_col, 0.3, emit=window_emit))
        box(f"winf{i}", (1.15, 0.12, 0.08), (x, d - 0.14, h * 0.55 - 0.82), mat("winframe", "#4a3020"))


# ------------------------------------------------------------------ medieval houses (shared by London + villages)
PLASTER = ("#f1dca8", "#efd59a", "#f4e3bb", "#e9cf94", "#f0e6cf")


def _house_mats():
    if "timber" in bpy.data.materials:
        return
    pass


def med_house(x, y, w, d, floors, side, seed, stalls=True):
    r = random.Random(seed)
    timber = mat("timber", "#5a3a22", noise=0.15, nscale=6)
    roofs = [k.mat_pattern(f"roof{i}", c, "#5a2a18", "tiles", scale=9, bump=0.3) if f"roof{i}" not in bpy.data.materials else bpy.data.materials[f"roof{i}"]
             for i, c in enumerate(("#b2452c", "#9c3a26", "#c56a3a", "#8b6a3e"))]
    win = mat("window", "#3b4a52", 0.25)
    door = bpy.data.materials.get("door") or k.mat_pattern("door", "#6a4426", "#3a2414", "planks", scale=12, bump=0.2)
    h = floors * 1.6
    m = mat(f"plaster{seed % 5}", PLASTER[seed % 5], noise=0.1, nscale=1.5, bump=0.15)
    front = lambda f: x + f * 0.25 * -side - side * (w / 2 + 0.01)
    for f in range(floors):
        jut = f * 0.25 * -side
        box(f"h{seed}f{f}", (w, d, 1.6), (x + jut, y, 0.8 + f * 1.6), m)
        for b in (-1, 0, 1):
            box(f"h{seed}f{f}b{b}", (0.14, 0.14, 1.6), (front(f), y + b * d * 0.46, 0.8 + f * 1.6), timber)
        box(f"h{seed}f{f}r", (0.14, d + 0.02, 0.12), (front(f), y, 1.55 + f * 1.6), timber)
        for wv in (-1, 1):
            if f == 0 and wv == 1:
                box(f"h{seed}door", (0.1, 0.8, 1.25), (front(0) - side * 0.02, y + d * 0.22, 0.62), door)
                continue
            box(f"h{seed}f{f}w{wv}", (0.08, 0.55, 0.65), (front(f) - side * 0.02, y + wv * d * 0.22, 0.95 + f * 1.6), win)
    rx = x + (floors - 1) * 0.25 * -side
    prism_roof(f"h{seed}roof", d + 0.4, w + 0.6, 1.4 + r.random() * 0.6, (rx, y, h), roofs[seed % 4], rotz=math.pi / 2)
    if stalls and r.random() < 0.5:
        sx = x - side * (w / 2 + 0.6)
        awn = mat(f"awn{seed % 4}", ("#c4462f", "#3f7a52", "#d9a33a", "#f4ecd8")[seed % 4], noise=0.08, nscale=5)
        box(f"h{seed}aw", (1.3, d * 0.8, 0.06), (sx, y, 2.0), awn, rot=(0, side * 0.35, 0))
        box(f"h{seed}tb", (1.0, d * 0.7, 0.1), (sx, y, 0.85), timber)
        for j in range(5):
            ball(f"h{seed}fr{j}", 0.11, (sx, y - d * 0.25 + j * d * 0.12, 1.0), mat(f"fruit{j % 3}", ("#e0802a", "#c33a2a", "#7da13a")[j % 3], 0.5))


def simple_house(name, x, y, w, d, h, seed, rotz=0.0):
    r = random.Random(seed)
    box(name, (w, d, h), (x, y, h / 2), mat(f"plaster{seed % 5}", PLASTER[seed % 5], noise=0.1, nscale=1.5, bump=0.15))
    rm = bpy.data.materials.get(f"roof{seed % 4}") or mat("rooffallback", "#a8452c")
    prism_roof(name + "r", w + 0.3, d + 0.3, 1.2 + r.random() * 0.8, (x, y, h), rm, rotz=rotz)


# ------------------------------------------------------------------ the sets
def s_throne_hall(F):
    light("interior")
    stone = k.mat_pattern("flag", "#a89a84", "#5a4c3c", "cobble", scale=0.9, bump=0.3)
    wall = mat("hallstone", "#b8a888", noise=0.15, nscale=0.8, bump=0.25)
    room(16, 9, 8, wall_m=wall, floor=stone, back_windows=0)
    for x in (-5, -2, 2, 5):   # tall arched windows with daylight
        box(f"hw{x}", (1.0, 0.1, 3.4), (x, 8.82, 4.6), mat("hallglass", "#ffe7b0", 0.3, emit=1.4))
        ball(f"hwa{x}", 0.5, (x, 8.82, 6.3), mat("hallglass", "#ffe7b0", 0.3, emit=1.4), scale=(1, 0.2, 1))
    box("carpet", (2.2, 14, 0.02), (0, 2, 0.01), mat("carpet", "#9a1e22", noise=0.1, nscale=6))
    box("dais", (5, 3, 0.5), (0, 6.8, 0.25), wall)
    box("dais2", (3.6, 2.2, 0.3), (0, 7.0, 0.65), wall)
    gold, red = mat("gold", "#e0b23a", 0.25), mat("throne-red", "#8a1a1e", 0.6)
    box("throneseat", (1.4, 1.0, 0.5), (0, 7.1, 1.05), gold, bevel=0.05)
    box("throneback", (1.4, 0.25, 2.6), (0, 7.55, 2.1), gold, bevel=0.06)
    box("throneinner", (1.1, 0.05, 2.0), (0, 7.41, 2.0), red)
    cone("thronepeak", 0.3, 0.5, (0, 7.55, 3.65), gold, verts=4)
    for x in (-3.6, 3.6):
        box(f"banner{x}", (1.1, 0.05, 3.6), (x, 8.75, 4.3), red)
        box(f"bannerg{x}", (0.5, 0.06, 0.5), (x, 8.72, 4.8), gold)
        cyl(f"pillar{x}", 0.45, 8, (x * 1.6, 5.0, 4), wall, verts=16)
    for x in (-2.3, 2.3):
        cyl(f"torch{x}", 0.06, 0.6, (x, 7.9, 2.6), mat("iron", "#2a2420"), verts=8)
        ball(f"torchf{x}", 0.1, (x, 7.9, 3.0), mat("flame", "#ffb040", 0.5, emit=12), scale=(1, 1, 1.6))
        point((x, 7.6, 3.1), 300, (1, 0.7, 0.4), 0.2)
    area((0, -4, 6), (math.radians(60), 0, 0), 700, 10, (1, 0.9, 0.75))
    area((0, 8.5, 5), (math.radians(-90), 0, 0), 300, 8, (1, 0.92, 0.75))
    return dict(focus=(0, 6.6, 1.6))


def s_decree_table(F):
    light("interior")
    room(8, 4, 4, wall="#6a4a30", back_windows=1, window_col="#ffe2a8", window_emit=2.5)
    top = table("dt", (0, 1.0, 0), 2.6, 1.3, 0.8)
    rnd = random.Random(2)
    for i in range(26):  # a tall pile of torn decrees with red seals
        lvl = i // 5
        scroll(f"dec{i}", (rnd.uniform(-0.5, 0.5), 1.0 + rnd.uniform(-0.3, 0.3), top + 0.05 + lvl * 0.09), length=rnd.uniform(0.45, 0.6), r=0.045,
               rot=(0, math.pi / 2, rnd.uniform(-0.6, 0.6)))
    for i in range(6):
        box(f"sheet{i}", (0.4, 0.3, 0.005), (rnd.uniform(-1.1, 1.1), 1.0 + rnd.uniform(-0.5, 0.5), top + 0.005), mat("paper", "#f1e4c4", 0.8, noise=0.1, nscale=12),
            rot=(0, 0, rnd.uniform(-1, 1)))
    candle("dtc", (0.95, 1.2, top), e=40)
    area((0, -3, 3), (math.radians(65), 0, 0), 700, 5, (1, 0.88, 0.7))
    return dict(focus=(0, 1.0, top + 0.25), top=top)


def s_stadium(F, kind="modern"):
    light("warm" if kind != "1930" else "day", mist=(90, 420))
    rnd = random.Random(11)
    stripes = bpy.data.materials.new("pitch"); stripes.use_nodes = True
    nt = stripes.node_tree; b = nt.nodes["Principled BSDF"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.6; wv.wave_profile = "SAW"
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeValToRGB"); rr.color_ramp.interpolation = "CONSTANT"
    rr.color_ramp.elements[0].color = (*hexrgb("#4a8a3a"), 1); rr.color_ramp.elements[1].color = (*hexrgb("#5a9a44"), 1); rr.color_ramp.elements[1].position = 0.5
    nt.links.new(wv.outputs["Fac"], rr.inputs["Fac"]); nt.links.new(rr.outputs["Color"], b.inputs["Base Color"])
    L, W = 105, 68
    box("pitch", (L + 10, W + 10, 0.2), (0, 0, -0.1), stripes)
    ground("#6a8a4a" if kind != "1930" else "#8a7a5a", z=-0.16)
    white = mat("line", "#f4f4f4", 0.6)
    for (sx, sy, x, y) in ((L, 0.12, 0, W / 2), (L, 0.12, 0, -W / 2), (0.12, W, L / 2, 0), (0.12, W, -L / 2, 0), (0.12, W, 0, 0)):
        box(f"ln{x}{y}", (sx, sy, 0.02), (x, y, 0.01), white)
    k.torus("circle", 9.15, 0.06, (0, 0, 0.01), white, scale=(1, 1, 0.1)) if hasattr(k, "torus") else None
    for gx in (-1, 1):
        for gy in (-1, 1):
            cyl(f"post{gx}{gy}", 0.07, 2.44, (gx * L / 2, gy * 3.66, 1.22), white, verts=10)
        cyl(f"bar{gx}", 0.07, 7.32, (gx * L / 2, 0, 2.44), white, rot=(math.pi / 2, 0, 0), verts=10)
    crowd = crowd_mat("crowd", 2.4)
    concrete = mat("concrete", "#bcb6aa", noise=0.1, nscale=0.5)
    tiers = 14 if kind == "modern" else 10
    for side in range(4):
        for t in range(tiers):
            off = 8 + t * 1.6
            zz = 1 + t * 1.15
            if side < 2:
                y = (W / 2 + off) * (1 if side == 0 else -1)
                box(f"tier{side}{t}", (L + 2 * off, 1.6, 0.4), (0, y, zz), crowd)
                box(f"riser{side}{t}", (L + 2 * off, 0.1, 1.15), (0, y + (0.8 if side == 0 else -0.8), zz - 0.4), concrete)
            else:
                x = (L / 2 + off) * (1 if side == 2 else -1)
                box(f"tier{side}{t}", (1.6, W + 2 * off, 0.4), (x, 0, zz), crowd)
    if kind == "modern":
        roofm = mat("stadroof", "#d8dce0", 0.4)
        for y in (1,):   # only the far stand has a roof: the near one would block the aerial shots
            box(f"roof{y}", (L + 50, 26, 0.4), (0, y * (W / 2 + 22), tiers * 1.15 + 5), roofm)
        for x, y in ((-60, -45), (60, -45), (-60, 45), (60, 45)):
            cyl(f"flood{x}{y}", 0.5, 40, (x, y, 20), concrete, verts=8)
            box(f"floodlamp{x}{y}", (5, 0.5, 3), (x, y, 41), mat("lamp", "#fffbe8", 0.3, emit=6))
    if kind == "1930":  # Estadio Centenario: the Tower of Homage over the stands
        box("tower", (5, 5, 45), (0, W / 2 + 22, 22), mat("towerw", "#e8e2d4", 0.6))
        for z in range(6, 44, 6):
            box(f"towerwin{z}", (5.2, 5.2, 0.4), (0, W / 2 + 22, z), mat("towerband", "#a8a294"))
        for i in range(14):
            box(f"flag{i}", (2.2, 0.05, 1.4), (-55 + i * 8.5, W / 2 + 8 + tiers * 1.6, tiers * 1.15 + 3.5),
                mat(f"fl{i % 3}", ("#6ab4e8", "#f4f4f4", "#e8c83a")[i % 3]))
    city = [mat(f"cityb{i}", c, noise=0.1, nscale=0.2) for i, c in enumerate(("#d8d0c0", "#c8b8a0", "#b8c0c8", "#e0d8c8"))]
    for i in range(140):   # the city around the stadium, out to the horizon
        a = rnd.uniform(0, math.tau); d = rnd.uniform(95, 260)
        hh = rnd.uniform(8, 30)
        box(f"cb{i}", (rnd.uniform(8, 18), rnd.uniform(8, 18), hh), (math.sin(a) * d, math.cos(a) * d, hh / 2), city[i % 4])
    hills(rnd, dist=(300, 360))
    clouds(rnd, frames=F)
    return dict(focus=(0, 0, 1))


def s_cricket_1872(F):
    """1872: Hamilton Crescent, Glasgow. Grass oval, a timber pavilion, a standing Victorian crowd, no stands."""
    light("grey")
    rnd = random.Random(4)
    ground("#6f9a4a", noise=0.1)
    box("pitchstrip", (3, 20, 0.02), (0, 6, 0.01), mat("strip", "#a8a868"))
    crowd = crowd_mat("crowd1872", 2.4)
    for i in range(36):
        a = math.radians(-90 + i * 10)
        r_ = 42
        box(f"crowdring{i}", (8, 2.5, 1.8), (math.sin(a) * r_, 20 + math.cos(a) * r_ * 0.7, 0.9), crowd, )
        bpy.context.object.rotation_euler = (0, 0, -a)
    pav = mat("pavilion", "#e8dcc0", noise=0.1, nscale=2)
    box("pavilion", (14, 6, 5), (-18, 48, 2.5), pav)
    prism_roof("pavroof", 14.6, 6.6, 3, (-18, 48, 5), mat("pavroofm", "#7a3a2a"))
    box("pavbalc", (14, 1.5, 0.2), (-18, 44.5, 2.6), mat("timber", "#5a3a22", noise=0.15, nscale=6))
    white = mat("line", "#f4f4f4", 0.6)
    for gx in (-1, 1):  # 1872 goals: posts and a tape, no net, no crossbar
        for gy in (-1, 1):
            cyl(f"post{gx}{gy}", 0.07, 2.5, (gy * 3.66, 6 + gx * 45, 1.25), white, verts=10)
        cyl(f"tape{gx}", 0.02, 7.32, (0, 6 + gx * 45, 2.44), white, rot=(0, math.pi / 2, 0), verts=6)
    for i in range(10):
        simple_house(f"tenement{i}", -60 + i * 13, 95 + rnd.uniform(-5, 5), 10, 6, 9 + rnd.uniform(0, 4), i)
    hills(rnd, colors=("#7c8a6a", "#8a9478", "#6c7a5c"))
    trees(rnd, 40, 70, 140)
    clouds(rnd, col=(0.92, 0.92, 0.92), emit=0.1, frames=F)
    return dict(focus=(0, 6, 1))


def s_study(F):
    light("interior")
    room(9, 5, 4.2, wall="#6a4a30", back_windows=0)
    spines = bpy.data.materials.new("spines"); spines.use_nodes = True
    nt = spines.node_tree; b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.7
    wv = nt.nodes.new("ShaderNodeTexVoronoi"); wv.inputs["Scale"].default_value = 1.0
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (12, 0.05, 0.05)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    rr = nt.nodes.new("ShaderNodeValToRGB"); cr = rr.color_ramp; cr.interpolation = "CONSTANT"
    for j, c in enumerate(("#6a2a22", "#2a3a5a", "#3a4a2a", "#7a5a2a", "#4a2a3a", "#8a6a4a")):
        e = cr.elements[0] if j == 0 else (cr.elements[1] if j == 1 else cr.elements.new(0))
        e.position = j / 6; e.color = (*hexrgb(c), 1)
    nt.links.new(wv.outputs["Distance"], rr.inputs["Fac"]); nt.links.new(rr.outputs["Color"], b.inputs["Base Color"])
    for z in (0.5, 1.4, 2.3, 3.2):
        box(f"shelf{z}", (8.4, 0.6, 0.06), (0, 4.6, z - 0.42), mat("timber", "#5a3a22", noise=0.15, nscale=6))
        box(f"books{z}", (8.2, 0.4, 0.75), (0, 4.65, z), spines)
    top = table("st", (0, 1.4, 0), 3.0, 1.4, 0.8)
    rnd = random.Random(5)
    for i in range(9):
        box(f"tb{i}", (rnd.uniform(0.3, 0.5), rnd.uniform(0.22, 0.32), rnd.uniform(0.05, 0.1)), (rnd.uniform(-1.2, 1.2), 1.4 + rnd.uniform(-0.4, 0.4), top + 0.05 + (i % 3) * 0.08),
            mat(f"book{i % 4}", ("#7a2a22", "#2a4a6a", "#3a5a2a", "#6a4a2a")[i % 4]), rot=(0, 0, rnd.uniform(-0.5, 0.5)))
    g = ball("globe", 0.28, (1.15, 1.6, top + 0.45), mat("globe", "#4a8ab0", 0.4, noise=0.4, nscale=3), seg=32)
    cyl("globestand", 0.04, 0.3, (1.15, 1.6, top + 0.15), mat("gold", "#e0b23a", 0.25))
    k.key(g, "rotation_euler", 1, (0, 0.4, 0)); k.key(g, "rotation_euler", F, (0, 0.4, 1.2))
    for x in (-1.3, 0.4):
        candle(f"sc{x}", (x, 1.1, top), e=45)
    area((0, -3, 3.4), (math.radians(65), 0, 0), 600, 6, (1, 0.85, 0.65))
    return dict(focus=(0, 1.4, top + 0.3), top=top)


def chinese_roof(name, w, d, h, loc, m, eave=0.6):
    """Hip roof with upswept corners (Han/Song halls)."""
    x, y, z = loc
    prism_roof(name, w + eave, d + eave, h, (x, y, z), m)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cone(name + f"tip{sx}{sy}", 0.18, 0.7, (x + sx * (w + eave) / 2, y + sy * (d + eave) / 2, z + 0.1), m, verts=6,
                 rot=(sy * -0.9, sx * 0.9, 0))
    box(name + "ridge", (w * 0.8, 0.2, 0.2), (x, y, z + h), m)


def s_han_city(F, dusk=True):
    light("dusk" if dusk else "day")
    rnd = random.Random(6)
    ground("#9a8a5a", noise=0.15)
    earth = mat("rammed", "#b8966a", noise=0.18, nscale=0.6, bump=0.3)
    tile = k.mat_pattern("ctile", "#3a3a40", "#1d1d22", "tiles", scale=10, bump=0.3)
    red = mat("lacquer", "#a82a22", 0.4)
    # city wall with a gate tower, seen across the valley
    box("cwall", (120, 6, 9), (0, 60, 4.5), earth)
    for x in range(-58, 60, 4):
        box(f"cren{x}", (2, 6.2, 1.2), (x, 60, 9.6), earth)
    box("gatebase", (16, 8, 12), (0, 58, 6), earth)
    box("gatehall", (12, 6, 5), (0, 58, 14.5), red)
    chinese_roof("gateroof", 13, 7, 3, (0, 58, 17), tile, eave=2)
    for i in range(30):  # houses inside, roofs over the wall
        x = rnd.uniform(-55, 55)
        if abs(x) < 10:
            continue
        hh = rnd.uniform(7, 12)
        box(f"ch{i}", (6, 5, hh), (x, 70 + rnd.uniform(0, 30), hh / 2), mat("chwall", "#d8c8a8", noise=0.1, nscale=1))
        chinese_roof(f"chr{i}", 6, 5, 2, (x, 70 + rnd.uniform(0, 30), hh), tile)
    pag = mat("pagoda", "#8a3a2a", 0.5)
    for j in range(5):
        box(f"pag{j}", (5 - j * 0.7, 5 - j * 0.7, 3), (-25, 85, 3 + j * 4), pag)
        chinese_roof(f"pagr{j}", 5 - j * 0.7, 5 - j * 0.7, 1.2, (-25, 85, 4.5 + j * 4), tile, eave=1.6)
    lantern = mat("lantern", "#ff8a3a", 0.4, emit=8)
    for x in (-6, -3, 3, 6):
        ball(f"lan{x}", 0.5, (x, 53.5, 10), lantern, scale=(1, 1, 1.2))
    # road through the valley, fields + hills
    box("road", (6, 70, 0.04), (0, 25, 0.02), mat("road", "#b8a070", noise=0.2, nscale=0.5))
    for i in range(12):
        box(f"field{i}", (14, 10, 0.05), ((-1) ** i * 16, i * 6 - 5, 0.025), mat(f"crop{i % 3}", ("#a8a050", "#7a9a40", "#c8b060")[i % 3], noise=0.2, nscale=1))
    hills(rnd, colors=("#6a6a8a", "#7a6a7a", "#5a5a7a") if dusk else ("#86a457", "#7c9a52", "#94b064"), dist=(200, 260), zoff=-30)
    trees(rnd, 50, 20, 100, exclude=lambda x, y: abs(x) < 5 or 50 < y < 105)
    return dict(focus=(0, 40, 6))


def s_han_court(F):
    light("warm")
    rnd = random.Random(7)
    ground("#c8b088", noise=0.12)
    earth = mat("rammed", "#b8966a", noise=0.18, nscale=0.6, bump=0.3)
    tile = k.mat_pattern("ctile", "#3a3a40", "#1d1d22", "tiles", scale=10, bump=0.3)
    red = mat("lacquer", "#a82a22", 0.4)
    # the walled cuju court (ju cheng) with crescent goals
    for sx in (-1, 1):
        box(f"courtwall{sx}", (0.8, 30, 2.2), (sx * 10, 6, 1.1), earth)
    box("courtwallb", (20.8, 0.8, 2.2), (0, 21, 1.1), earth)
    goal = mat("goalwood", "#6a3a1e", 0.6)
    for gy in (-8, 19):
        for gx in (-4, 0, 4):
            k.torus(f"crescent{gx}{gy}", 0.9, 0.08, (gx, gy, 1.3), goal, rot=(math.pi / 2, 0, 0), scale=(1, 1, 1)) if hasattr(k, "torus") else None
            box(f"goalcut{gx}{gy}", (2.2, 0.4, 1.0), (gx, gy, 0.5), mat("courtfloor", "#c8b088"))
    # palace: raised platform, red columns, big hip roof
    box("platform", (36, 14, 2.4), (0, 34, 1.2), mat("terrace", "#c8c0b0", noise=0.1, nscale=1))
    for x in range(-14, 15, 4):
        cyl(f"col{x}", 0.45, 6, (x, 29, 5.4), red, verts=12)
    box("hallwall", (30, 8, 6), (0, 34, 5.4), mat("hallwall", "#e8dcc0", noise=0.08, nscale=1))
    chinese_roof("hallroof", 32, 12, 5, (0, 34, 8.4), tile, eave=3)
    for x in range(-12, 13, 3):
        box(f"step{x}", (6, 0.6, 0.4), (0, 26.6 - (x + 12) * 0.0, 0.2), earth) if x == -12 else None
    for i in range(4):
        box(f"stair{i}", (8, 0.8, 0.6 * (i + 1)), (0, 26.4 + i * 0.8 - 1.6, 0.3 * (i + 1)), mat("terrace", "#c8c0b0", noise=0.1, nscale=1))
    for x in (-16, 16):
        box(f"banner{x}", (0.1, 1.2, 4), (x, 27, 5), red)
    hills(rnd, dist=(120, 180), zoff=-25)
    trees(rnd, 40, 45, 120, kind="pine")
    clouds(rnd, frames=F)
    return dict(focus=(0, 6, 1))


def s_han_field(F):
    light("warm")
    rnd = random.Random(8)
    ground("#c8a878", noise=0.2)
    red = mat("lacquer", "#a82a22", 0.4)
    for i in range(6):  # banners on poles
        x = -12 + i * 4.8
        cyl(f"pole{i}", 0.06, 6, (x, 14, 3), mat("polewood", "#5a3a22"), verts=8)
        box(f"flagb{i}", (1.4, 0.05, 2.2), (x + 0.75, 14, 4.8), red)
    for i in range(5):  # tents
        cone(f"tent{i}", 2.2, 3, (-20 + i * 10, 24 + rnd.uniform(-2, 2), 1.5), mat("tentcloth", "#d8c8a0", noise=0.1, nscale=2), verts=6)
    rack = mat("rack", "#5a3a22")
    for x in (-7, 7):
        box(f"rack{x}", (3, 0.15, 0.15), (x, 9, 1.4), rack)
        for j in range(6):
            cyl(f"spear{x}{j}", 0.025, 2.6, (x - 1.2 + j * 0.5, 9.1, 1.3), mat("spearwood", "#7a5a3a"), verts=6, rot=(0.2, 0, 0))
    earth = mat("rammed", "#b8966a", noise=0.18, nscale=0.6, bump=0.3)
    box("farwall", (160, 4, 7), (0, 70, 3.5), earth)
    hills(rnd, dist=(120, 180), zoff=-25)
    trees(rnd, 30, 35, 120, exclude=lambda x, y: y > 60 and y < 75)
    clouds(rnd, frames=F)
    return dict(focus=(0, 2, 1))


def s_song_street(F):
    light("warm")
    rnd = random.Random(9)
    ground("#b8a888", noise=0.1)
    box("street", (8, 80, 0.04), (0, 30, 0.02), k.mat_pattern("stoneslab", "#b8aa90", "#7a6a54", "cobble", scale=0.8, bump=0.3))
    tile = k.mat_pattern("ctile", "#3a3a40", "#1d1d22", "tiles", scale=10, bump=0.3)
    wood = mat("songwood", "#7a4a2a", noise=0.12, nscale=4)
    lantern = mat("lantern", "#ff6a2a", 0.4, emit=5)
    signc = [mat(f"sign{i}", c) for i, c in enumerate(("#c8282a", "#2a6a4a", "#e8c84a", "#f4ece0"))]
    for side in (-1, 1):
        y = -4
        i = 0
        while y < 60:
            w = rnd.uniform(4, 6)
            hh = rnd.uniform(3.5, 5.5)
            x = side * (6 + 2)
            box(f"shop{side}{i}", (4, w, hh), (x, y, hh / 2), mat("songwall", "#e8d8b8", noise=0.08, nscale=1))
            box(f"shopfront{side}{i}", (0.2, w * 0.8, 2.2), (x - side * 2.05, y, 1.1), wood)
            chinese_roof(f"shoproof{side}{i}", 4, w, 1.4, (x, y, hh), tile, eave=1.0)
            box(f"vsign{side}{i}", (0.06, 0.5, 1.6), (x - side * 2.4, y + w * 0.3, 2.6), signc[i % 4])
            ball(f"slan{side}{i}", 0.25, (x - side * 2.6, y - w * 0.3, 2.9), lantern, scale=(1, 1, 1.3))
            y += w + 0.3
            i += 1
    for j in range(3):  # a gate tower at the end of the street
        pass
    box("streetgate", (10, 3, 6), (0, 62, 3), mat("rammed", "#b8966a", noise=0.18, nscale=0.6, bump=0.3))
    chinese_roof("streetgateroof", 10, 3, 2, (0, 62, 6), tile, eave=1.5)
    hills(rnd, colors=("#7a8a6a", "#6a7a5a", "#8a9a6a"))
    clouds(rnd, frames=F)
    return dict(focus=(0, 4, 1))


def s_greek_field(F):
    light("warm")
    rnd = random.Random(10)
    ground("#d8c49a", noise=0.15)
    marble = mat("marble", "#f2eee6", 0.35, noise=0.05, nscale=3)
    for x in range(-18, 19, 3):   # a stoa colonnade behind the field
        cyl(f"col{x}", 0.4, 6, (x, 16, 3.4), marble, verts=16)
        box(f"cap{x}", (1, 1, 0.3), (x, 16, 6.5), marble)
    box("stoabase", (40, 5, 0.4), (0, 17, 0.2), marble)
    box("entab", (40, 1.2, 1.0), (0, 16, 7.1), marble)
    box("stoaback", (40, 0.4, 7), (0, 19, 3.5), mat("stoawall", "#d8c8a8"))
    prism_roof("stoaroof", 41, 4.5, 1.6, (0, 17.4, 7.6), mat("terracotta", "#b8603a"))
    box("temple", (14, 24, 8), (30, 70, 10), marble)
    prism_roof("templeroof", 15, 25, 3, (30, 70, 14), marble, rotz=math.pi / 2)
    box("acropolis", (40, 40, 6), (30, 70, 3), mat("rock", "#b8a888", noise=0.2, nscale=0.2))
    olive = [mat("olive", "#7a8a4a", noise=0.15, nscale=3)]
    trees(rnd, 40, 25, 120, leafc=("#7a8a4a", "#6a7a40", "#8a9a5a"), exclude=lambda x, y: 10 < y < 22 and abs(x) < 22)
    hills(rnd, colors=("#a8a070", "#b8aa80", "#98906a"))
    clouds(rnd, n=5, frames=F)
    return dict(focus=(0, 2, 1))


def s_heian_garden(F):
    light("warm")
    rnd = random.Random(12)
    ground("#7a9a5a", noise=0.12)
    box("kemaricourt", (12, 12, 0.06), (0, 3, 0.03), mat("gravel", "#e8e2d4", 0.95, noise=0.15, nscale=40, bump=0.2))
    fence = mat("fence", "#a8603a", 0.6)
    for side in (-1, 1):
        for j in range(13):
            cyl(f"fp{side}{j}", 0.05, 0.8, (side * 6.1, -3 + j, 0.4), fence, verts=6)
        box(f"frail{side}", (0.06, 12.2, 0.06), (side * 6.1, 3, 0.75), fence)
    # the four corner trees of a kemari court: pine, cherry, willow, maple
    bark = mat("bark", "#5a3e2a")
    tree("pine", -5, -2, 1.2, mat("pinel", "#3a6a3a", noise=0.1, nscale=3), bark, "pine")
    tree("cherry", 5, -2, 1.2, mat("cherryl", "#f4b8c8", noise=0.1, nscale=3, emit=0.1), bark)
    tree("willow", -5, 8, 1.2, mat("willowl", "#8ab860", noise=0.1, nscale=3), bark)
    tree("maple", 5, 8, 1.2, mat("maplel", "#d84a2a", noise=0.1, nscale=3), bark)
    # a shinden-style hall: raised wooden floor, bark roof
    wood = mat("heianwood", "#8a5a3a", noise=0.1, nscale=4)
    box("hallfloor", (20, 7, 0.8), (0, 15, 0.9), wood)
    for x in range(-9, 10, 3):
        cyl(f"hcol{x}", 0.18, 4, (x, 12, 3), mat("hcolor", "#c8482a", 0.5), verts=10)
    box("hallwalls", (19, 5, 3.4), (0, 16, 3.0), mat("shoji", "#f4ece0", 0.7))
    prism_roof("hallroofb", 23, 9, 3.2, (0, 15.5, 4.7), mat("hinoki", "#5a3a2a", noise=0.15, nscale=6))
    for i in range(10):
        x = rnd.uniform(-30, 30)
        if abs(x) < 12:
            continue
        tree(f"bg{i}", x, rnd.uniform(25, 50), rnd.uniform(1.2, 2), mat("pinel", "#3a6a3a", noise=0.1, nscale=3), bark, "pine")
    hills(rnd, colors=("#5a7a5a", "#6a8a6a", "#4a6a4a"), dist=(100, 160), zoff=-15)
    clouds(rnd, n=5, frames=F)
    return dict(focus=(0, 3, 1.2))


def s_muddy_field(F):
    light("grey")
    rnd = random.Random(13)
    ground("#7a9a4a", noise=0.15)
    box("mud", (30, 60, 0.05), (0, 10, 0.02), mat("mud", "#6a4a2a", 0.6, noise=0.25, nscale=0.6, bump=0.3))
    for j in range(5):
        for side in (-1, 1):
            med_house(side * (rnd.uniform(14, 26)), 40 + j * 4 * side, 3, 3, 1 + j % 2, side, 100 + j * 2 + (side > 0), stalls=False)
    for j in range(5):
        simple_house(f"vil{j}", -10 + j * 5, 46 + rnd.uniform(0, 4), 3, 3, 2.5, 200 + j)
        simple_house(f"vil2{j}", -10 + j * 5, -26 - rnd.uniform(0, 4), 3, 3, 2.5, 210 + j)
    box("church", (3, 6, 6), (12, 52, 3), mat("stone2", "#c8b79a", noise=0.15, nscale=0.6, bump=0.2))
    cone("churchspire", 1.8, 7, (12, 49, 9.5), mat("slate", "#6c6a72"), verts=8)
    hedge = mat("hedge", "#4a6a2a", noise=0.15, nscale=2)
    for side in (-1, 1):
        box(f"hedge{side}", (1.2, 70, 1.4), (side * 16, 10, 0.7), hedge)
    hills(rnd)
    trees(rnd, 60, 30, 130)
    clouds(rnd, col=(0.9, 0.9, 0.9), emit=0.1, frames=F)
    return dict(focus=(0, 5, 1))


def s_london_street(F):
    light("day")
    rnd = random.Random(7)
    cobble = k.mat_pattern("cobble", "#b89c72", "#6a5236", "cobble", scale=2.4, bump=0.5)
    box("street", (9.2, 92, 0.2), (0, 36, -0.1), cobble)
    ground("#93ad5c", noise=0.18, z=-0.16)
    box("cityground", (70, 100, 0.2), (0, 36, -0.12), mat("dirt", "#9a8262", noise=0.15, nscale=0.3))
    y = -6.0
    for i in range(15):
        for side in (-1, 1):
            w = 2.4 + rnd.random() * 0.6
            med_house(side * (4.6 + w / 2), y + (0.3 if side > 0 else 0), w, 3.0, 2 + (i % 2), side, i * 2 + (side > 0))
        y += 3.1
    n = 0
    for gy in range(-3, 24):
        for gx in range(4):
            for side in (-1, 1):
                if rnd.random() < 0.15:
                    continue
                simple_house(f"bh{n}", side * (9.2 + gx * 3.6 + rnd.random() * 0.6), gy * 3.5 + rnd.random() * 0.8, 2.8 + rnd.random() * 0.6, 3.0,
                             2.6 + rnd.random() * 2.4, n, rotz=0 if rnd.random() < 0.5 else math.pi / 2); n += 1
    stone = mat("stone2", "#c8b79a", noise=0.15, nscale=0.6, bump=0.2)
    slate = mat("slate", "#6c6a72", noise=0.1, nscale=4)
    box("nave", (26, 7, 9), (0, 64, 4.5), stone)
    prism_roof("naveroof", 26.4, 7.4, 3.6, (0, 64, 9), slate)
    box("tower", (5, 5, 17), (2, 64, 8.5), stone)
    cone("spire", 2.6, 26, (2, 64, 30), slate, verts=8)
    for i in range(12):
        cyl(f"barrel{i}", 0.32, 0.8, ((-1 if i % 2 else 1) * (3.3 + rnd.random() * 0.4), i * 3.6 - 3, 0.4), mat("barrel", "#7a5230", noise=0.15, nscale=8), verts=14)
    wallm = mat("wall", "#b8ad98", noise=0.15, nscale=1, bump=0.2)
    box("citywall", (70, 1.6, 6), (0, 86, 3), wallm)
    hills(rnd)
    trees(rnd, 80, 62, 150, exclude=lambda x, y: abs(x) < 36 and -15 < y < 88)
    clouds(rnd, frames=F)
    return dict(focus=(0, 4, 1.2))


def s_archery_field(F):
    light("day")
    rnd = random.Random(14)
    ground("#7aa04a", noise=0.15)
    straw = mat("straw", "#d8b860", noise=0.2, nscale=8, bump=0.3)
    for i, x in enumerate((-6, -2, 2, 6)):
        t = cyl(f"butt{i}", 0.9, 0.5, (x, 14, 1.2), straw, rot=(math.pi / 2, 0, 0), verts=24)
        for j, (rr, c) in enumerate(((0.75, "#f4f0e4"), (0.55, "#2a2a2a"), (0.38, "#2a5ac8"), (0.22, "#c8282a"), (0.1, "#e8c83a"))):
            cyl(f"ring{i}{j}", rr, 0.02, (x, 13.74 - j * 0.004, 1.2), mat(f"ring{c}", c, 0.6), rot=(math.pi / 2, 0, 0), verts=24)
        for leg in (-1, 1):
            cyl(f"tleg{i}{leg}", 0.05, 1.6, (x + leg * 0.6, 14.4, 0.7), mat("timber", "#5a3a22", noise=0.15, nscale=6), rot=(0.4, 0, 0), verts=6)
    stone = mat("stone2", "#c8b79a", noise=0.15, nscale=0.6, bump=0.2)
    box("castle", (30, 10, 10), (-10, 80, 5), stone)
    for x in (-25, -10, 5):
        cyl(f"ctower{x}", 3, 16, (x, 80, 8), stone, verts=12)
        cone(f"ctowerr{x}", 3.6, 5, (x, 80, 18.5), mat("slate", "#6c6a72"), verts=12)
    box("fence", (40, 0.1, 0.1), (0, 22, 0.9), mat("timber", "#5a3a22", noise=0.15, nscale=6))
    hills(rnd)
    trees(rnd, 60, 30, 140, exclude=lambda x, y: 70 < y < 90 and -30 < x < 10)
    clouds(rnd, frames=F)
    return dict(focus=(0, 4, 1))


def s_school_field(F):
    light("day")
    rnd = random.Random(15)
    ground("#7aa84a", noise=0.12)
    brick = k.mat_pattern("brick", "#a84a32", "#d8c8b0", "tiles", scale=14, bump=0.25)
    box("school", (40, 10, 9), (0, 45, 4.5), brick)
    for x in range(-18, 19, 4):
        box(f"swin{x}", (1.6, 0.2, 3), (x, 39.9, 5), mat("winglass", "#8aa8c8", 0.3))
        cone(f"sarch{x}", 0.8, 0.8, (x, 39.9, 6.9), mat("winglass", "#8aa8c8", 0.3), verts=4)
    prism_roof("schoolroof", 41, 11, 4, (0, 45, 9), mat("slate", "#6c6a72", noise=0.1, nscale=4))
    box("schooltower", (6, 6, 18), (14, 44, 9), brick)
    for x in (-13, 1):
        box(f"chim{x}", (1, 1, 3), (x, 45, 12), brick)
    white = mat("line", "#f4f4f4", 0.6)
    for gx in (-1, 1):
        for gy in (-1, 1):
            cyl(f"post{gx}{gy}", 0.06, 2.6, (gy * 2.5 + gx * 18, 14, 1.3), white, verts=8)
    trees(rnd, 50, 25, 130, exclude=lambda x, y: 35 < y < 55 and abs(x) < 25)
    hills(rnd)
    clouds(rnd, frames=F)
    return dict(focus=(0, 4, 1))


def s_cambridge_room(F):
    light("interior")
    panel = k.mat_pattern("panel", "#6a4428", "#3a2414", "planks", scale=3, bump=0.3)
    room(8, 4.5, 4, wall_m=panel, back_windows=1, window_col="#1a2a4a", window_emit=0.6)
    top = table("cr", (0, 1.3, 0), 2.6, 1.3, 0.8)
    rnd = random.Random(16)
    for i in range(8):
        box(f"page{i}", (0.3, 0.4, 0.004), (rnd.uniform(-1, 1), 1.3 + rnd.uniform(-0.4, 0.4), top + 0.004 * i), mat("paper", "#f1e4c4", 0.8, noise=0.1, nscale=12),
            rot=(0, 0, rnd.uniform(-0.6, 0.6)))
    cyl("inkwell", 0.06, 0.09, (0.8, 1.5, top + 0.045), mat("ink", "#141018", 0.2), verts=12)
    c3.tube("quill", [(0.8, 1.5, top + 0.08), (0.75, 1.45, top + 0.35)], 0.012, mat("quill", "#f4f0e8"), radii=[0.5, 1.4])
    for x in (-0.9, 0.2, 1.1):
        candle(f"cc{x}", (x, 1.6, top), e=55)
    box("fireplace", (2.4, 0.6, 2), (-2.6, 4.2, 1), mat("brick2", "#8a3a2a", noise=0.15, nscale=2))
    box("fire", (1.2, 0.2, 0.6), (-2.6, 3.95, 0.4), mat("fire", "#ff7a2a", 0.5, emit=8))
    point((-2.6, 3.4, 0.8), 80, (1, 0.55, 0.25), 0.4)
    area((0, -3, 3.2), (math.radians(65), 0, 0), 250, 6, (1, 0.8, 0.6))
    return dict(focus=(0, 1.3, top + 0.3), top=top)


def s_frosty_field(F):
    light("frost")
    rnd = random.Random(17)
    ground("#c8d4c4", noise=0.15)
    bark = mat("bark", "#4a3a2e")
    for i in range(40):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(20, 100)
        tree(f"bare{i}", math.sin(a) * d, abs(math.cos(a)) * d + 10, rnd.uniform(1.4, 2.6), None, bark, "bare")
    fence = mat("timber", "#5a3a22", noise=0.15, nscale=6)
    for j in range(30):
        cyl(f"fpost{j}", 0.06, 1.1, (-30 + j * 2, 18, 0.55), fence, verts=6)
    box("frail", (60, 0.06, 0.06), (0, 18, 0.95), fence)
    for i in range(12):  # Sheffield: works chimneys on the horizon
        x = -70 + i * 12
        cyl(f"works{i}", 1.2, 18 + rnd.uniform(0, 10), (x, 110, 9), mat("brick2", "#7a3a2a", noise=0.15, nscale=2), verts=10)
    hills(rnd, colors=("#b8c0bc", "#a8b4b0", "#c8d0cc"))
    return dict(focus=(0, 3, 1))


def s_victorian_street(F):
    light("night")
    rnd = random.Random(18)
    cobble = k.mat_pattern("cobblen", "#5a5a62", "#2a2a30", "cobble", scale=2.6, bump=0.5)
    box("street", (10, 90, 0.2), (0, 30, -0.1), cobble)
    ground("#2a2a2e", noise=0.05, z=-0.15)
    brick = k.mat_pattern("brickn", "#6a3a2e", "#3a2a24", "tiles", scale=14, bump=0.25)
    lit = mat("litwin", "#ffc870", 0.3, emit=4)
    dark = mat("darkwin", "#1a2030", 0.3)
    for side in (-1, 1):
        y = -6
        i = 0
        while y < 70:
            w = rnd.uniform(5, 7); hh = rnd.uniform(8, 11)
            box(f"terr{side}{i}", (5, w, hh), (side * 8.5, y, hh / 2), brick)
            for f in range(3):
                for wv in (-1, 1):
                    box(f"tw{side}{i}{f}{wv}", (0.1, 1.0, 1.4), (side * 5.95, y + wv * w * 0.25, 1.6 + f * 2.8), lit if rnd.random() < 0.5 else dark)
            y += w; i += 1
    # the tavern with a lit door and a hanging sign
    box("tavdoor", (0.1, 1.4, 2.4), (5.94, 6, 1.2), mat("tavdoorlit", "#ffb050", 0.3, emit=5))
    box("tavsign", (0.08, 1.4, 0.9), (5.2, 4.6, 3.6), mat("signwood", "#6a4426"))
    point((5.0, 6, 2.0), 300, (1, 0.7, 0.4), 0.5)
    iron = mat("iron", "#1e2024", 0.4)
    glow = mat("gaslight", "#ffe0a0", 0.2, emit=12)
    for i in range(8):
        for side in (-1, 1):
            y = i * 9 - 3 + (4.5 if side > 0 else 0)
            cyl(f"lamp{i}{side}", 0.08, 3.6, (side * 4.8, y, 1.8), iron, verts=8)
            box(f"lampg{i}{side}", (0.35, 0.35, 0.5), (side * 4.8, y, 3.8), glow)
            if i < 4:
                point((side * 4.6, y, 3.6), 220, (1, 0.8, 0.5), 0.3)
    # a horse cab
    cab = mat("cab", "#1a1a22", 0.4)
    box("cab", (1.4, 2.0, 1.4), (-3, 12, 1.4), cab, bevel=0.1)
    for wy in (-0.7, 0.7):
        for wx in (-0.75, 0.75):
            k.torus(f"wheel{wx}{wy}", 0.5, 0.05, (-3 + wx, 12 + wy, 0.55), mat("wheel", "#3a2a1a"), rot=(0, math.pi / 2, 0)) if hasattr(k, "torus") else None
    horse = mat("horse", "#4a2e1e", 0.6)
    ball("horsebody", 0.6, (-3, 9.6, 1.4), horse, scale=(0.7, 1.4, 0.75))
    ball("horsehead", 0.3, (-3, 8.4, 2.0), horse, scale=(0.6, 1.2, 0.7))
    for lx in (-0.25, 0.25):
        for ly in (-0.6, 0.6):
            cyl(f"hleg{lx}{ly}", 0.08, 1.0, (-3 + lx, 9.6 + ly, 0.5), horse, verts=8)
    ball("moon", 3, (-30, 120, 45), mat("moon", "#f4f0e0", 0.5, emit=3))
    hills(rnd, colors=("#1a1e2e", "#20243a", "#181c2a"), dist=(150, 200))
    return dict(focus=(0, 5, 1.2))


def s_office(F):
    light("interior")
    room(7, 4, 3.8, wall="#6a5a44", back_windows=1, window_col="#ffe8b8", window_emit=2.0)
    top = table("of", (0, 1.4, 0), 2.2, 1.1, 0.8)
    rnd = random.Random(19)
    for i in range(5):
        box(f"opage{i}", (0.3, 0.4, 0.004), (rnd.uniform(-0.8, 0.6), 1.3 + rnd.uniform(-0.3, 0.3), top + 0.004 * i), mat("paper", "#f1e4c4", 0.8, noise=0.1, nscale=12),
            rot=(0, 0, rnd.uniform(-0.5, 0.5)))
    cyl("oinkwell", 0.06, 0.09, (0.7, 1.6, top + 0.045), mat("ink", "#141018", 0.2), verts=12)
    cyl("lamp", 0.12, 0.35, (-0.8, 1.7, top + 0.17), mat("brass", "#c8963a", 0.3), verts=16)
    ball("lampglass", 0.14, (-0.8, 1.7, top + 0.45), mat("lampglow", "#ffd890", 0.2, emit=6), scale=(1, 1, 1.3))
    point((-0.8, 1.6, top + 0.6), 90, (1, 0.75, 0.45), 0.1)
    spines = mat("spines2", "#6a2a22", noise=0.5, nscale=6)
    box("bookcase", (3, 0.5, 3), (2.2, 3.7, 1.5), spines)
    area((0, -3, 3), (math.radians(65), 0, 0), 500, 6, (1, 0.88, 0.7))
    return dict(focus=(0, 1.4, top + 0.3), top=top)


def s_tavern(F):
    light("interior")
    wood = k.mat_pattern("tavwall", "#7a5232", "#3a2414", "planks", scale=4, bump=0.3)
    room(10, 6, 3.6, wall_m=wood, back_windows=0)
    beam = mat("beam", "#3a2414")
    for y in (0, 2, 4):
        box(f"beam{y}", (10, 0.3, 0.3), (0, y, 3.4), beam)
    top = table("tv", (0, 1.6, 0), 3.4, 1.2, 0.8)
    for i, x in enumerate((-1.2, -0.4, 0.4, 1.2)):
        cyl(f"mug{i}", 0.06, 0.12, (x, 1.3, top + 0.06), mat("pewter", "#8a8a88", 0.35), verts=12)
    for i in range(4):
        box(f"tpaper{i}", (0.3, 0.4, 0.004), (-0.6 + i * 0.4, 1.8, top + 0.002 * i), mat("paper", "#f1e4c4", 0.8, noise=0.1, nscale=12), rot=(0, 0, i * 0.3 - 0.4))
    for x in (-1.0, 0.2, 1.3):
        candle(f"tc{x}", (x, 1.9, top), e=50)
    box("hearth", (2.4, 0.6, 2), (3.0, 5.6, 1), mat("brick2", "#8a3a2a", noise=0.15, nscale=2))
    box("tfire", (1.2, 0.2, 0.6), (3.0, 5.35, 0.4), mat("fire", "#ff7a2a", 0.5, emit=8))
    point((3.0, 4.8, 0.9), 90, (1, 0.55, 0.25), 0.4)
    box("tdoor", (1.2, 0.2, 2.3), (-3.6, 5.85, 1.15), k.mat_pattern("door", "#6a4426", "#3a2414", "planks", scale=12, bump=0.2))
    for i in range(6):
        cyl(f"keg{i}", 0.35, 0.8, (-4.3, 1 + i * 0.85, 0.4), mat("barrel", "#7a5230", noise=0.15, nscale=8), rot=(0, math.pi / 2, 0), verts=14)
    area((0, -3, 3.2), (math.radians(65), 0, 0), 350, 6, (1, 0.82, 0.6))
    return dict(focus=(0, 1.6, top + 0.3), top=top)


def s_ballcourt(F):
    """Mesoamerican ball court: long alley between sloped stone walls, a stone ring high on each wall."""
    light("warm")
    rnd = random.Random(21)
    ground("#7a9a4a", noise=0.15)
    stone = mat("mesostone", "#c8b490", noise=0.18, nscale=0.8, bump=0.3)
    plaster = mat("mesoplaster", "#e2d2b0", noise=0.1, nscale=1)
    box("alley", (6, 34, 0.05), (0, 4, 0.025), plaster)
    for sx in (-1, 1):
        b = box(f"slope{sx}", (3, 34, 2.2), (sx * 4.4, 4, 1.0), stone)
        b.rotation_euler = (0, sx * -0.45, 0)
        box(f"wall{sx}", (2, 34, 5), (sx * 6.6, 4, 2.5), stone)
        k.torus(f"ring{sx}", 0.45, 0.12, (sx * 5.55, 4, 4.0), stone, rot=(0, math.pi / 2, 0))
        for j in range(5):
            box(f"step{sx}{j}", (2.6 - j * 0.4, 34, 0.5), (sx * (8.0 + j * 0.3), 4, 5.2 + j * 0.5), stone)
    for i in range(3):   # a temple pyramid at the end
        box(f"pyr{i}", (16 - i * 4, 16 - i * 4, 3), (0, 40, 1.5 + i * 3), stone)
    box("pyrtop", (5, 5, 3), (0, 40, 10.5), plaster)
    trees(rnd, 70, 25, 130, leafc=("#3f7a36", "#4f8a3c", "#2f6a2e"), exclude=lambda x, y: abs(x) < 12 and -14 < y < 50)
    hills(rnd, colors=("#5a8a4a", "#4a7a3e", "#6a9a52"))
    clouds(rnd, frames=F)
    return dict(focus=(0, 2, 1))


SETS = {
    "med-throne-hall": s_throne_hall, "decree-table": s_decree_table,
    "modern-stadium": lambda F: s_stadium(F, "modern"), "montevideo-1930": lambda F: s_stadium(F, "1930"),
    "scholar-study": s_study, "han-city-dusk": s_han_city, "han-palace-court": s_han_court,
    "han-training-field": s_han_field, "song-street": s_song_street, "greek-field": s_greek_field,
    "heian-garden": s_heian_garden, "med-muddy-field": s_muddy_field, "med-london-street": s_london_street,
    "med-archery-field": s_archery_field, "school-field-1840s": s_school_field, "cambridge-room": s_cambridge_room,
    "frosty-field": s_frosty_field, "victorian-street-night": s_victorian_street, "solicitor-office": s_office,
    "tavern-interior": s_tavern, "cricket-ground-1872": s_cricket_1872, "ballcourt": s_ballcourt,
}
