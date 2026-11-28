"""The three locked Facts on Demand characters, rebuilt in 3D (Blender 4.5, 100 % code).
Faithful copies of media/library/characters/*/master-sheet.jpg (owner decisions 2026-11-27):
big round white head, NO ears, NO nose, black dot eyes, the sheet's hair/brows/facial hair,
orange scarf, THICK sleeved arms + trouser legs, round white mitten hands, sheet boots,
soft 3D shading without outlines.

Rig = a tree of empties you key directly (root > hips > torso > arm/elbow/head, hips > leg/knee).
Faces -Y. Boot soles end exactly at z = 0 of the root (feet never sink).
"""
import math
import bmesh
import bpy
from fod3d import mat, empty, key

R = 0.28          # skull radius
SKULL_Z = 0.27    # skull centre above the neck pivot
SCARF = "#ef7a1d"

SPECS = {
    "main": dict(build="compact", skin="#f7f5f0", tunic="#c9b28e", trim=None, belt="#7a4a2a", buckle="#b8893a",
                 hose="#2f2723", boot="#8a5430", sole="#3a2416", hair="#4a3020", hairstyle="messy",
                 brows="#3a2418", brow_w=0.022, facial="handlebar", glasses=False, cheeks=False, crown=False,
                 default="neutral", mouth_z=-0.15),
    "two": dict(build="compact", skin="#f7f5f0", tunic="#8f9397", trim=None, belt="#4a4440", buckle="#9a9a9a",
                hose="#2f2b2a", boot="#2c2826", sole="#161312", hair="#c8723a", hairstyle="tousled",
                brows="#a85a2a", brow_w=0.013, facial=None, glasses=True, cheeks=False, crown=False,
                default="grumpy", mouth_z=-0.12),
    "king": dict(build="round", skin="#f7f5f0", tunic="#8c2024", trim="#d9a83a", belt=None, buckle=None,
                 hose="#2f2723", boot="#2c2826", sole="#161312", hair="#aeb0b3", hairstyle="sides",
                 brows="#e4e4df", brow_w=0.026, facial=None, glasses=False, cheeks=True, crown=True,
                 default="smug", mouth_z=-0.11),
}

# expression = brows (inner_dz, outer_dz, lift) per side, eyes per side, mouth shape
EXPR = {
    "neutral":    dict(brow=((0, 0, 0), (0, 0, 0)), eye=("dot", "dot"), mouth="hidden"),
    "happy":      dict(brow=((0.01, 0, 0.02), (0.01, 0, 0.02)), eye=("arc", "arc"), mouth="grin"),
    "sad":        dict(brow=((0.03, -0.015, 0), (0.03, -0.015, 0)), eye=("dot", "dot"), mouth="frown"),
    "surprised":  dict(brow=((0, 0, 0.045), (0, 0, 0.045)), eye=("big", "big"), mouth="O"),
    "angry":      dict(brow=((-0.035, 0.015, -0.01), (-0.035, 0.015, -0.01)), eye=("dot", "dot"), mouth="grit"),
    "suspicious": dict(brow=((-0.01, -0.01, -0.015), (0.0, 0.02, 0.025)), eye=("half", "dot"), mouth="side"),
    "grumpy":     dict(brow=((-0.005, -0.005, -0.01), (-0.005, -0.005, -0.01)), eye=("half", "half"), mouth="frown_small"),
    "smug":       dict(brow=((0.0, 0.02, 0.0), (-0.01, -0.005, -0.01)), eye=("half", "half"), mouth="smirk"),
}


# ------------------------------------------------------------------ mesh helpers
def _link(o, m, parent):
    bpy.context.collection.objects.link(o)
    if m is not None:
        o.data.materials.append(m)
    if parent is not None:
        o.parent = parent
    return o


def lathe(name, prof, m, parent=None, loc=(0, 0, 0), segs=40, sy=1.0, subsurf=0):
    """Surface of revolution around Z from a (radius, z) profile, listed bottom to top."""
    verts, faces, rings = [], [], []
    for r, z in prof:
        if r < 1e-6:
            rings.append([len(verts)]); verts.append((0, 0, z))
        else:
            ring = []
            for i in range(segs):
                a = math.tau * i / segs
                ring.append(len(verts)); verts.append((r * math.cos(a), r * math.sin(a) * sy, z))
            rings.append(ring)
    for A, B in zip(rings, rings[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(segs):
            j = (i + 1) % segs
            if len(A) == 1:
                faces.append((A[0], B[j], B[i]))
            elif len(B) == 1:
                faces.append((A[i], A[j], B[0]))
            else:
                faces.append((A[i], A[j], B[j], B[i]))
    if len(rings[0]) > 1:
        faces.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1:
        faces.append(tuple(rings[-1]))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    o.location = loc
    _link(o, m, parent)
    if subsurf:
        md = o.modifiers.new("sub", "SUBSURF"); md.levels = md.render_levels = subsurf
    return o


def capsule(L, r0, r1, n=8):
    """Profile (bottom->top) of a limb hanging down from z=0 to z=-L, rounded ends."""
    bot = [(r1 * math.sin(t), -L - r1 * math.cos(t)) for t in (i / n * math.pi / 2 for i in range(n + 1))]
    top = [(r0 * math.cos(t), r0 * math.sin(t)) for t in (i / n * math.pi / 2 for i in range(n + 1))]
    return bot + top


def sphere(name, r, loc, m, parent=None, scale=(1, 1, 1), seg=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, scale
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(m)
    if parent is not None:
        o.parent = parent
    return o


def open_cap(name, r, loc, m, parent=None, face_top=0.45, scale=(1, 1, 1)):
    """Hood / coif: a shell around the head with the FACE CUT OPEN (owner 2026-11-28: every face must show).
    The opening is an oval on the -y side, from below the chin up to face_top*r above the centre."""
    import bmesh
    o = sphere(name, r, loc, m, parent, scale=scale, seg=72)
    bm = bmesh.new(); bm.from_mesh(o.data)
    cut = [v for v in bm.verts if v.co.y < -0.2 * r and (v.co.x / (0.78 * r)) ** 2 + (max(0.0, v.co.z - (face_top - 1.0) * r * 0.5) / (face_top * r + 0.001)) ** 2 < 1.0
           and v.co.z < face_top * r]
    bmesh.ops.delete(bm, geom=cut, context="VERTS")
    bm.to_mesh(o.data); bm.free()
    sol = o.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.018; sol.offset = 1.0
    return o


def slab(name, size, loc, m, parent=None, rot=(0, 0, 0), sub=2):
    """Soft rounded slab (scarf tails, soles): a subdivided cube."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name, o.scale = name, size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    md = o.modifiers.new("sub", "SUBSURF"); md.levels = md.render_levels = sub
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.append(m)
    if parent is not None:
        o.parent = parent
    return o


def tube(name, pts, width, m, parent=None, radii=None, res=6, cyclic=False):
    """Smooth tube along points (hair tufts, brows, mustache, mouth lines, glasses)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = width
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    cu.resolution_u = 12
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    sp.use_cyclic_u = cyclic
    for i, bp in enumerate(sp.bezier_points):
        bp.co = pts[i]
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = radii[i] if radii else 1.0
    o = bpy.data.objects.new(name, cu)
    return _link(o, m, parent)


def surf(x, z, off=0.0, r=R):
    """Point on the front of the skull (head space, skull centre at SKULL_Z), pushed out by off."""
    d = r * r - x * x - z * z
    y = -math.sqrt(max(d, 0.0))
    n = math.sqrt(x * x + y * y + z * z) or 1
    k = (n + off) / n
    return (x * k, y * k, z * k + SKULL_Z)


# ------------------------------------------------------------------ head
def build_head(n, spec, expr, parent, loc=(0, 0, 0)):
    import face3d
    return face3d.build_head(n, spec, expr, parent, loc)


def build_head_v1(n, spec, expr, parent, loc=(0, 0, 0)):
    """Head with face. Returns the head empty (pivot at the neck)."""
    H = empty(f"{n}-head", loc, parent)
    skin = mat(f"skin-{n}", spec["skin"], 0.55)
    ink = mat("eye-ink", "#141010", 0.18)
    sphere(f"{n}-skull", R, (0, 0, SKULL_Z), skin, H, seg=64)
    e = EXPR[expr]
    # ---- eyes
    for i, side in enumerate((-1, 1)):
        kind = e["eye"][i]
        ex, ez = side * 0.085, 0.035
        if kind in ("dot", "half", "big"):
            big = kind == "big"
            p = surf(ex, ez, -0.004)
            sphere(f"{n}-eye{side}", 0.038 if big else 0.03, p, ink, H, scale=(0.82, 0.5, 1.25), seg=24)
            sphere(f"{n}-glint{side}", 0.007, surf(ex - side * 0.008, ez + 0.016, 0.011), mat("glint", "#ffffff", 0.1, emit=1.0), H, seg=12)
            if kind == "half":  # heavy upper lid covering the top half of the dot
                lid = sphere(f"{n}-lid{side}", 0.044, surf(ex, ez + 0.022, 0.004), skin, H, scale=(1.05, 0.55, 0.62), seg=24)
                tube(f"{n}-lidline{side}", [surf(ex - 0.038, ez + 0.006, 0.012), surf(ex, ez + 0.0, 0.016), surf(ex + 0.038, ez + 0.006, 0.012)],
                     0.006, ink, H)
        elif kind == "arc":  # happy closed eye: ^
            tube(f"{n}-eye{side}", [surf(ex - 0.035, ez - 0.012, 0.004), surf(ex, ez + 0.018, 0.006), surf(ex + 0.035, ez - 0.012, 0.004)],
                 0.009, ink, H)
    # ---- brows
    bm = mat(f"brow-{n}", spec["brows"], 0.7)
    bw = spec["brow_w"]
    for i, side in enumerate((-1, 1)):
        di, do, lift = e["brow"][i]
        bz = 0.115 + (0.02 if spec["glasses"] else 0) + lift
        inner, outer = side * 0.045, side * 0.135
        if spec["hairstyle"] == "sides":  # king: big bushy brows with a flick
            pts = [surf(inner, bz + di, 0.01), surf(side * 0.09, bz + 0.012 + (di + do) / 2, 0.014),
                   surf(outer, bz + do, 0.012), surf(side * 0.165, bz + do + 0.03, 0.008)]
            tube(f"{n}-brow{side}", pts, bw, bm, H, radii=[0.8, 1.15, 1.0, 0.45])
            tube(f"{n}-brow2{side}", [surf(inner + side * 0.01, bz + di + 0.018, 0.012), surf(side * 0.1, bz + 0.03 + (di + do) / 2, 0.012),
                                     surf(outer + side * 0.01, bz + do + 0.025, 0.008)], bw * 0.7, bm, H, radii=[0.6, 1, 0.3])
        else:
            pts = [surf(inner, bz + di, 0.006), surf(side * 0.09, bz + 0.008 + (di + do) / 2, 0.008), surf(outer, bz + do, 0.006)]
            tube(f"{n}-brow{side}", pts, bw, bm, H, radii=[0.85, 1.0, 0.7])
    # ---- cheeks (king)
    if spec["cheeks"]:
        for side in (-1, 1):
            sphere(f"{n}-cheek{side}", 0.045, surf(side * 0.15, -0.045, -0.02), mat("rosy", "#f2a0a0", 0.6), H, scale=(1, 0.5, 0.8), seg=24)
    # ---- facial hair
    if spec["facial"] == "handlebar":
        hm = mat(f"stache-{n}", spec["hair"], 0.65)
        for side in (-1, 1):
            s = side
            pts = [surf(0.0, -0.06, 0.012), surf(s * 0.06, -0.075, 0.018), surf(s * 0.125, -0.085, 0.016),
                   surf(s * 0.175, -0.06, 0.012), surf(s * 0.19, -0.02, 0.01), surf(s * 0.165, -0.005, 0.012)]
            tube(f"{n}-stache{side}", pts, 0.032, hm, H, radii=[0.95, 1.1, 0.85, 0.55, 0.38, 0.22])
    # ---- mouth
    mz = spec["mouth_z"]
    mouth_m = mat("mouth-ink", "#3a1a14", 0.5)
    mo = e["mouth"]
    if mo == "hidden" and spec["facial"] != "handlebar":
        mo = "flat"
    if mo == "grin":
        tube(f"{n}-mouth", [surf(-0.075, mz + 0.025, 0.004), surf(0, mz - 0.025, 0.006), surf(0.075, mz + 0.025, 0.004)], 0.01, mouth_m, H)
        sphere(f"{n}-mouthin", 0.05, surf(0, mz - 0.005, -0.012), mouth_m, H, scale=(1.4, 0.4, 0.55), seg=24)
    elif mo in ("frown", "frown_small"):
        w = 0.06 if mo == "frown" else 0.04
        tube(f"{n}-mouth", [surf(-w, mz - 0.015, 0.004), surf(0, mz + 0.008, 0.006), surf(w, mz - 0.015, 0.004)], 0.009, mouth_m, H)
    elif mo == "O":
        sphere(f"{n}-mouth", 0.03, surf(0, mz - 0.01, -0.002), mouth_m, H, scale=(0.9, 0.45, 1.15), seg=24)
    elif mo == "grit":
        sphere(f"{n}-teeth", 0.05, surf(0, mz, -0.01), mat("teeth", "#ffffff", 0.3), H, scale=(1.45, 0.42, 0.6), seg=24)
        tube(f"{n}-teethline", [surf(-0.06, mz, 0.012), surf(0, mz + 0.002, 0.016), surf(0.06, mz, 0.012)], 0.005, mouth_m, H)
        tube(f"{n}-teethrim", [surf(-0.072, mz, 0.004), surf(0, mz + 0.03, 0.008), surf(0.072, mz, 0.004), surf(0, mz - 0.03, 0.008)],
             0.006, mouth_m, H, cyclic=True)
    elif mo == "side":
        tube(f"{n}-mouth", [surf(-0.05, mz + 0.0, 0.004), surf(0.02, mz - 0.006, 0.006), surf(0.06, mz + 0.012, 0.004)], 0.009, mouth_m, H)
    elif mo == "smirk":
        tube(f"{n}-mouth", [surf(-0.08, mz + 0.012, 0.004), surf(-0.01, mz - 0.022, 0.006), surf(0.09, mz + 0.03, 0.004)], 0.01, mouth_m, H)
    elif mo == "flat":
        tube(f"{n}-mouth", [surf(-0.045, mz, 0.004), surf(0.045, mz, 0.004)], 0.009, mouth_m, H)
    # ---- glasses (character 2: identity marker)
    if spec["glasses"]:
        rim = mat("rim", "#141010", 0.3)
        for side in (-1, 1):
            c = surf(side * 0.085, 0.035, 0.028)
            pts = [(c[0] + 0.07 * math.cos(a), c[1] + 0.008 * math.cos(a) * side, c[2] + 0.07 * math.sin(a)) for a in
                   (i / 8 * math.tau for i in range(8))]
            tube(f"{n}-lens{side}", pts, 0.009, rim, H, cyclic=True)
            tube(f"{n}-temple{side}", [surf(side * 0.155, 0.045, 0.02), surf(side * 0.24, 0.05, 0.004), (side * 0.27, 0.05, SKULL_Z + 0.05)], 0.007, rim, H)
        tube(f"{n}-bridge", [surf(-0.02, 0.045, 0.03), surf(0, 0.052, 0.034), surf(0.02, 0.045, 0.03)], 0.007, rim, H)
    if spec.get("hairstyle") != "bald":
        build_hair(n, spec, H)
    if spec.get("crown"):
        build_crown(n, H)
    if spec.get("hat"):
        build_hat(n, spec["hat"], H, spec)
    if spec.get("beard"):
        bm_ = hair_mat(n + "b", spec["beard"])
        el = [("ELLIPSOID", (0, -0.17, SKULL_Z - 0.17), 0.13, (1.4, 0.9, 1.0))] + \
             [("BALL", (side * 0.18, -0.15, SKULL_Z - 0.1), 0.09, None) for side in (-1, 1)] + \
             [("BALL", (side * 0.25, -0.06, SKULL_Z - 0.02), 0.07, None) for side in (-1, 1)]
        _mball(n + "Beard", H, bm_, el)
    return H


def _tuft(n, i, base_dir, length, width, gravity, m, H, curl=0.0, r=R):
    """One hair tuft: starts on the scalp, sticks out along base_dir and droops by gravity."""
    d = base_dir
    L = math.sqrt(sum(c * c for c in d)) or 1
    d = tuple(c / L for c in d)
    b = (d[0] * r * 0.97, d[1] * r * 0.97, d[2] * r * 0.97 + SKULL_Z)
    m1 = (b[0] + d[0] * length * 0.5, b[1] + d[1] * length * 0.5, b[2] + d[2] * length * 0.5 - gravity * 0.3)
    t = (b[0] + d[0] * length + curl * d[1], b[1] + d[1] * length - curl * d[0], b[2] + d[2] * length - gravity)
    return tube(f"{n}-tuft{i}", [b, m1, t], width, m, H, radii=[1.0, 0.75, 0.12])


def hair_mat(n, color):
    """Sculpted-hair look: deep lock grooves running down from the crown (angle bands around the
    head, wobbled by noise), darker in the grooves, soft sheen on the locks."""
    key_ = f"hair-{n}-{color}"
    if key_ in bpy.data.materials:
        return bpy.data.materials[key_]
    from fod3d import hexrgb, _shade
    rgb = hexrgb(color)
    m = bpy.data.materials.new(key_)
    m.use_nodes = True
    nt = m.node_tree
    N = nt.nodes.new
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.55
    for nm, v in (("Sheen Weight", 0.35), ("Sheen Roughness", 0.4)):
        if nm in b.inputs:
            b.inputs[nm].default_value = v
    tc = N("ShaderNodeTexCoord")
    sep = N("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    ang = N("ShaderNodeMath"); ang.operation = "ARCTAN2"
    nt.links.new(sep.outputs["Y"], ang.inputs[0]); nt.links.new(sep.outputs["X"], ang.inputs[1])
    nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; nz.inputs["Detail"].default_value = 0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    wob = N("ShaderNodeMath"); wob.operation = "MULTIPLY_ADD"; wob.inputs[1].default_value = 0.35
    nt.links.new(nz.outputs["Fac"], wob.inputs[0]); nt.links.new(ang.outputs[0], wob.inputs[2])
    bands = N("ShaderNodeMath"); bands.operation = "MULTIPLY"; bands.inputs[1].default_value = 8.0
    nt.links.new(wob.outputs[0], bands.inputs[0])
    sn = N("ShaderNodeMath"); sn.operation = "SINE"; nt.links.new(bands.outputs[0], sn.inputs[0])
    ab = N("ShaderNodeMath"); ab.operation = "ABSOLUTE"; nt.links.new(sn.outputs[0], ab.inputs[0])
    pw = N("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 0.6
    nt.links.new(ab.outputs[0], pw.inputs[0])                    # wide rounded locks, narrow grooves
    fine = N("ShaderNodeTexWave"); fine.bands_direction = "X"; fine.inputs["Scale"].default_value = 70
    fine.inputs["Distortion"].default_value = 5
    nt.links.new(tc.outputs["Object"], fine.inputs["Vector"])
    h = N("ShaderNodeMath"); h.operation = "MULTIPLY_ADD"; h.inputs[1].default_value = 0.08
    nt.links.new(fine.outputs["Fac"], h.inputs[0]); nt.links.new(pw.outputs[0], h.inputs[2])
    cr = N("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*_shade(rgb, 0.72), 1)
    cr.color_ramp.elements[1].color = (*_shade(rgb, 1.08), 1)
    nt.links.new(pw.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    bp = N("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.015
    nt.links.new(h.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def _norm(v):
    L = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / L for c in v)


def _lock_profile():
    o = bpy.data.objects.get("lock-profile")
    if o:
        return o
    cu = bpy.data.curves.new("lock-profile", "CURVE")
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(3); sp.use_cyclic_u = True
    for bp, (x, y) in zip(sp.bezier_points, ((0.04, 0), (0, 0.016), (-0.04, 0), (0, -0.016))):
        bp.co = (x, y, 0); bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new("lock-profile", cu)
    return o


def _clump(n, i, p, flow, L, w, droop, m, H, puff=0.25, curl=0.0):
    """One hair lock: rooted under the scalp at unit dir p, hugs the head and flows along flow.
    Flat (ellipse) cross-section, wide root, tapered tip."""
    d = _norm(flow)
    base = tuple(c * R * 0.92 for c in p)
    mid = tuple(p[k] * R * (1.06 + puff * 0.25) + d[k] * L * 0.45 for k in range(3))
    tip = tuple(p[k] * R * (1.02 + puff * 0.15) + d[k] * L for k in range(3))
    tip = (tip[0] + curl * d[1], tip[1] - curl * d[0], tip[2] - droop)
    pts = [(q[0], q[1], q[2] + SKULL_Z) for q in (base, mid, tip)]
    o = tube(f"{n}-hair{i}", pts, w, m, H, radii=[w / 0.04, 0.95 * w / 0.04, 0.15 * w / 0.04], res=3)
    o.data.bevel_mode = "OBJECT"
    o.data.bevel_object = _lock_profile()
    o.data.bevel_depth = 0
    o.scale = (1, 1, 1)
    o.data.use_fill_caps = True
    o.data.resolution_u = 8
    o.data.twist_mode = "TANGENT"
    return o


def _fib(N):
    g = math.pi * (3 - math.sqrt(5))
    for i in range(N):
        z = 1 - 2 * (i + 0.5) / N
        r = math.sqrt(1 - z * z)
        yield (math.cos(g * i) * r, math.sin(g * i) * r, z)


def _mball(n, H, m, elems, res=0.012):
    """One smooth blended hair mass from metaball elements [(type, (x,y,z), radius, (sx,sy,sz))] in head space."""
    mb = bpy.data.metaballs.new(f"{n}HairMass")
    mb.resolution, mb.render_resolution, mb.threshold = res * 1.6, res, 0.6
    from mathutils import Vector
    for typ, co, r, sz in elems:
        e = mb.elements.new(type="ELLIPSOID" if typ == "LOCK" else typ)
        e.co, e.radius, e.stiffness = co, r, 2.0
        if typ == "ELLIPSOID":
            e.size_x, e.size_y, e.size_z = sz
        elif typ == "LOCK":   # sz = flow direction: an ellipsoid stretched along it
            e.size_x, e.size_y, e.size_z = 0.55, 0.55, 2.0
            e.rotation = Vector((0, 0, 1)).rotation_difference(Vector(sz))
    o = bpy.data.objects.new(f"{n}HairMass", mb)   # unique base name per head: masses never merge across heads
    mb.materials.append(m)
    _link(o, None, H)
    try:   # bake to a mesh now, so it is not re-tessellated on every frame of an animation
        for ob in bpy.context.selected_objects:
            ob.select_set(False)
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.convert(target="MESH")
        o = bpy.context.view_layer.objects.active
        for p in o.data.polygons:
            p.use_smooth = True
        o.select_set(False)
    except Exception as e:
        print("metaball convert skipped:", e)
    return o


def _flick(n, i, p, flow, L, w, m, H, droop=0.0):
    """A pointed lock sticking out of the mass (the spiky ends of the sheet's hair). Round, tapered."""
    d = _norm(flow)
    base = tuple(c * R * 1.02 for c in p)
    mid = tuple(p[k] * R * 1.1 + d[k] * L * 0.5 for k in range(3))
    tip = tuple(p[k] * R * 1.08 + d[k] * L for k in range(3))
    tip = (tip[0], tip[1], tip[2] - droop)
    pts = [(q[0], q[1], q[2] + SKULL_Z) for q in (base, mid, tip)]
    return tube(f"{n}-flick{i}", pts, w * 1.5, m, H, radii=[1.0, 0.75, 0.1], res=6)


def _sph(theta, phi):
    """Unit direction: theta = around (0 = front -Y, +90 = viewer's right +X), phi = elevation."""
    t, f = math.radians(theta), math.radians(phi)
    return (math.sin(t) * math.cos(f), -math.cos(t) * math.cos(f), math.sin(f))


def build_hair(n, spec, H):
    """Sculpted cartoon hair: one smooth blended volume (metaballs) + pointed locks at the edges.
    Deterministic (fixed seed per style), so every head of a character has identical hair."""
    import random
    hs = spec["hairstyle"]
    hm = hair_mat(n, spec["hair"])
    rnd = random.Random(hs)
    el = []
    if hs in ("messy", "tousled"):
        front = 0.2 if hs == "messy" else 0.22
        for p in _fib(110):                       # shell over the scalp, kept off the face
            x, y, z = p
            if z * R < front - 0.06 - (0.45 if y < 0 else 0.75) * y * R:
                continue
            el.append(("BALL", tuple(c * R * 0.9 for c in p) + (0,), 0.14, None))
        locks = []                                 # long locks flowing down from the crown: ridges + grooves
        for p in _fib(46):
            x, y, z = p
            if z * R < front + 0.0 - (0.45 if y < 0 else 0.75) * y * R or z < 0.0:
                continue
            down = _norm((x * z, y * z, -(1 - z * z)))
            fl = _norm((down[0] + rnd.uniform(-0.2, 0.2), down[1] + rnd.uniform(-0.2, 0.2), down[2] - 0.15))
            c = tuple(p[k] * R * 1.1 + fl[k] * 0.05 for k in range(3))
            locks.append((c, fl))
        el = [(t, (c[0], c[1], c[2] + SKULL_Z), r, sz) for t, c, r, sz in el]
        el += [("LOCK", (c[0], c[1], c[2] + SKULL_Z), 0.075, fl) for c, fl in locks]
        top = SKULL_Z + R
        if hs == "messy":
            # chunky lumps: a bit of height on top, fuller at the sides like the sheet
            el += [("ELLIPSOID", (-0.12, -0.05, top - 0.02), 0.12, (1.3, 1.0, 0.7)), ("ELLIPSOID", (0.12, 0.02, top - 0.01), 0.12, (1.2, 1.0, 0.7)),
                   ("ELLIPSOID", (-0.27, 0.0, SKULL_Z + 0.08), 0.1, (0.7, 1.2, 1.0)), ("ELLIPSOID", (0.27, 0.0, SKULL_Z + 0.08), 0.1, (0.7, 1.2, 1.0)),
                   ("ELLIPSOID", (0.0, 0.22, SKULL_Z + 0.02), 0.12, (1.6, 0.8, 1.0))]
            _mball(n, H, hm, el)
            i = 0
            for th, ph, L, dr in ((-95, 0, 0.12, 0.03), (-108, -8, 0.11, 0.03), (-125, -12, 0.1, 0.03), (95, 0, 0.12, 0.03), (108, -8, 0.11, 0.03), (125, -12, 0.1, 0.03)):
                p = _sph(th, ph)
                _flick(n, i, p, (p[0] * 0.55, p[1] * 0.3, -0.8), L * 0.75, 0.034, hm, H, dr * 0.5); i += 1
            for th in (150, 165, 180, 195, 210):                 # ragged ends at the back
                p = _sph(th, -16 + rnd.uniform(-6, 6))
                _flick(n, i, p, (p[0] * 0.4, 0.35, -1), rnd.uniform(0.05, 0.09), 0.034, hm, H); i += 1
            for th in (-35, -15, 5, 22, 38):                     # short ragged fringe at the hairline
                p = _sph(th, 52 - abs(th) * 0.25)
                _flick(n, i, p, (th * 0.004, -0.7, -0.75), 0.07, 0.03, hm, H); i += 1
            for th, ph in ((-40, 78), (30, 76)):                    # two messy strands on top
                p = _sph(th, ph)
                _flick(n, i, tuple(c * 1.12 for c in p), (rnd.uniform(-0.5, 0.5), 0.5, 0.25), 0.06, 0.03, hm, H); i += 1
        else:
            # character 2: tousled ginger with a heavy fringe swept to the viewer's left over the forehead
            el += [("ELLIPSOID", (0.0, 0.0, top), 0.13, (1.4, 1.2, 0.7)),
                   ("ELLIPSOID", (-0.06, -0.2, SKULL_Z + 0.2), 0.1, (1.8, 0.7, 0.75)),          # fringe mass
                   ("ELLIPSOID", (-0.17, -0.2, SKULL_Z + 0.14), 0.08, (1.0, 0.7, 1.0)),
                   ("ELLIPSOID", (-0.28, -0.02, SKULL_Z + 0.06), 0.09, (0.7, 1.2, 1.2)), ("ELLIPSOID", (0.28, -0.02, SKULL_Z + 0.06), 0.09, (0.7, 1.2, 1.2)),
                   ("ELLIPSOID", (0.0, 0.24, SKULL_Z - 0.02), 0.12, (1.6, 0.8, 1.1))]
            _mball(n, H, hm, el)
            i = 0
            for th, ph, L in ((-45, 40, 0.12), (-25, 46, 0.13), (-5, 50, 0.13), (15, 50, 0.12), (35, 45, 0.1)):   # fringe locks
                p = _sph(th, ph)
                _flick(n, i, p, (-0.6, -0.5, -0.65), L, 0.038, hm, H, 0.01); i += 1
            for th, ph in ((-95, 2), (-110, -8), (-128, -14), (95, 2), (110, -8), (128, -14)):
                p = _sph(th, ph)
                _flick(n, i, p, (p[0] * 0.5, p[1] * 0.3, -0.85), 0.085, 0.036, hm, H, 0.01); i += 1
            for th in (145, 165, 185, 205, 220):
                p = _sph(th, -12 + rnd.uniform(-6, 6))
                _flick(n, i, p, (p[0] * 0.4, 0.35, -1), rnd.uniform(0.06, 0.1), 0.036, hm, H); i += 1
            for th, ph in ((-30, 75), (40, 72), (170, 70)):          # tousled bits on top
                p = _sph(th, ph)
                _flick(n, i, tuple(c * 1.12 for c in p), (rnd.uniform(-0.6, 0.6), 0.4, 0.3), 0.07, 0.032, hm, H); i += 1
    elif hs == "sides":
        # king: soft cloud-like grey-white puffs over the ears' place and around the back, bald on top
        for side in (-1, 1):
            for (th, ph, r) in ((86, 12, 0.1), (98, 32, 0.085), (100, -10, 0.1), (118, 18, 0.1), (122, -14, 0.095), (140, 5, 0.1),
                                (92, -25, 0.08), (130, 30, 0.08), (110, 5, 0.12), (130, -5, 0.11)):
                p = _sph(side * th, ph)
                el.append(("BALL", (p[0] * R * 1.02, p[1] * R * 1.02, p[2] * R * 1.02 + SKULL_Z), r, None))
        for th in (155, 170, 180, 190, 205):
            p = _sph(th, 0)
            el.append(("BALL", (p[0] * R * 1.0, p[1] * R * 1.0, p[2] * R + SKULL_Z), 0.1, None))
        for th in (160, 180, 200):
            p = _sph(th, -20)
            el.append(("BALL", (p[0] * R, p[1] * R, p[2] * R + SKULL_Z), 0.09, None))
        _mball(n, H, hm, el, res=0.01)
        i = 0
        for side in (-1, 1):
            for th, ph in ((112, -22),):
                p = _sph(side * th, ph)
                _flick(n, i, tuple(c * 1.2 for c in p), (p[0], p[1] * 0.4, 0.5 if ph > 0 else -0.6), 0.06, 0.03, hm, H); i += 1


def build_crown(n, H):
    gold = mat("gold", "#e0b23a", 0.25)
    base = SKULL_Z + 0.205
    lathe(f"{n}-crownband", [(0.175, base), (0.18, base + 0.005), (0.185, base + 0.06), (0.18, base + 0.065)], gold, H, segs=48)
    for i in range(5):
        a = math.tau * i / 5 - math.pi / 2
        x, y = math.cos(a) * 0.178, math.sin(a) * 0.178
        bpy.ops.mesh.primitive_cone_add(radius1=0.045, radius2=0.0, depth=0.1, vertices=4, location=(x, y, base + 0.11),
                                        rotation=(0, 0, a + math.pi / 4))
        c = bpy.context.object; c.name = f"{n}-spike{i}"; c.data.materials.append(gold); c.parent = H
        c.scale = (1, 0.35, 1)
        c.rotation_euler = (0, 0, a + math.pi / 2)
        sphere(f"{n}-gem{i}", 0.014, (x, y, base + 0.165), gold, H, seg=12)
    for i in range(10):
        a = math.tau * i / 10
        sphere(f"{n}-jewel{i}", 0.011, (math.cos(a) * 0.186, math.sin(a) * 0.186, base + 0.033),
               mat("ruby", "#b0202a", 0.2) if i % 2 else mat("emerald", "#2a8a4a", 0.2), H, seg=10)


# ------------------------------------------------------------------ body
HATS = {}


def build_hat(n, hat, H, spec):
    """Era headwear, in head space (skull centre at SKULL_Z, radius R)."""
    black = mat("hat-black", "#1d1a1a", 0.45)
    top = SKULL_Z + R - (0.03 if hat in ("tophat", "bowler") else 0.0)   # sits down on the hair
    if hat == "tophat":
        lathe(f"{n}-tophat", [(0, top + 0.02), (0.3, top + 0.0), (0.31, top + 0.025), (0.2, top + 0.03), (0.19, top + 0.33), (0.2, top + 0.34), (0, top + 0.345)], black, H)
        lathe(f"{n}-hatband", [(0.192, top + 0.04), (0.197, top + 0.042), (0.197, top + 0.09), (0.192, top + 0.092)], mat("hatband", "#3a3030", 0.6), H)
    elif hat == "bowler":
        lathe(f"{n}-bowler", [(0, top + 0.0), (0.29, top - 0.01), (0.3, top + 0.01), (0.21, top + 0.03), (0.22, top + 0.12), (0.16, top + 0.2), (0, top + 0.22)], black, H)
    elif hat == "cap":   # 1840s schoolboy cap
        cm = mat(f"cap-{n}", spec.get("hatcolor", "#2a3a6a"), 0.7)
        sphere(f"{n}-capdome", 0.27, (0, 0.02, top - 0.12), cm, H, scale=(1.08, 1.08, 0.6))
        sphere(f"{n}-peak", 0.16, (0, -0.25, top - 0.13), cm, H, scale=(1.1, 0.7, 0.12))
    elif hat == "eboshi":  # Heian court cap: tall, black, lacquered
        lathe(f"{n}-eboshi", [(0, top - 0.06), (0.2, top - 0.07), (0.21, top + 0.05), (0.17, top + 0.25), (0.1, top + 0.36), (0, top + 0.38)], black, H, sy=0.8,
              loc=(0, 0.04, 0))
    elif hat == "futou":   # Song dynasty soft black cap with two tails
        sphere(f"{n}-futou", 0.26, (0, 0.02, top - 0.1), black, H, scale=(1.08, 1.05, 0.7))
        for side in (-1, 1):
            slab(f"{n}-futail{side}", (0.05, 0.25, 0.02), (side * 0.12, 0.32, top - 0.12), black, H, rot=(0.5, 0, side * 0.3))
    elif hat == "han_helmet":
        steel = mat("bronze", "#8a6a3a", 0.35)
        sphere(f"{n}-helm", 0.3, (0, 0.0, top - 0.11), steel, H, scale=(1.05, 1.05, 0.72))
        lathe(f"{n}-helmrim", [(0.31, top - 0.15), (0.33, top - 0.14), (0.33, top - 0.11), (0.31, top - 0.1)], steel, H)
        bpy.ops.mesh.primitive_cone_add(radius1=0.04, depth=0.12, location=(0, 0, top + 0.12)); c = bpy.context.object
        c.data.materials.append(mat("helmred", "#a82a22", 0.6)); c.parent = H
    elif hat == "mianguan":  # Han emperor: flat board on top with bead strings at the front
        cap = mat("mian-cap", "#1d1a1a", 0.4)
        sphere(f"{n}-mcap", 0.2, (0, 0.03, top - 0.03), cap, H, scale=(1, 1.1, 0.8))
        slab(f"{n}-board", (0.5, 0.32, 0.025), (0, 0.0, top + 0.12), cap, H)
        cyl_m = mat("jade", "#3aa86a", 0.3)
        for j in range(7):
            x = -0.21 + j * 0.07
            for k_ in range(4):
                sphere(f"{n}-bead{j}{k_}", 0.012, (x, -0.165, top + 0.09 - k_ * 0.04), cyl_m if k_ % 2 else mat("redbead", "#c23a2a", 0.3), H, seg=10)
    elif hat == "ming":      # Ming emperor: black winged hat
        sphere(f"{n}-mhat", 0.27, (0, 0.03, top - 0.08), black, H, scale=(1.05, 1.05, 0.75))
        sphere(f"{n}-mhat2", 0.16, (0, 0.13, top + 0.02), black, H, scale=(1.4, 0.8, 1))
        for side in (-1, 1):
            sphere(f"{n}-wing{side}", 0.1, (side * 0.3, 0.2, top + 0.02), black, H, scale=(1.3, 0.12, 0.45), rot=(0, side * -0.25, 0))
    elif hat == "headband":
        lathe(f"{n}-band", [(R * 0.98, SKULL_Z + 0.12), (R * 1.02, SKULL_Z + 0.125), (R * 1.0, SKULL_Z + 0.17), (R * 0.97, SKULL_Z + 0.175)],
              mat("bandcol", spec.get("hatcolor", "#c84a2a"), 0.6), H)
    elif hat == "hood":
        hm = mat(f"hood-{n}", spec.get("hatcolor", "#6a5a3a"), 0.9, noise=0.08, nscale=20)
        open_cap(f"{n}-hood", R * 1.18, (0, 0.04, SKULL_Z + 0.03), hm, H, face_top=0.42, scale=(1.02, 1.02, 1.05))
    elif hat == "coif":
        open_cap(f"{n}-coif", R * 1.12, (0, 0.05, SKULL_Z + 0.04), mat("linen", "#efe6d2", 0.8), H, face_top=0.5)


# era costumes (applied over the locked character: only clothes change by era, PRODUCTION-RULES)
COSTUMES = {
    "medieval":  dict(),
    "han":       dict(tunic="#8a2a24", sleeve="#8a2a24", armor="#6a6a6a", belt="#3a2418", hose="#3a3030", boot="#3a2a20", hat="han_helmet"),
    "song":      dict(tunic="#4a6a8a", robe="long", belt="#c8a24a", hat="futou"),
    "greek":     dict(tunic="#f4efe4", sleeve="skin", belt="#b8893a", hose="skin", boot="#a8743a", robe="short", hat="headband"),
    "heian":     dict(tunic="#e8d8f0", trim="#9a6ac8", robe="long", sleeve="#e8d8f0", belt=None, hat="eboshi", boot="#1d1a1a"),
    "school":    dict(tunic="#2a3a6a", belt=None, hose="#3a3a44", boot="#1d1a1a", hat="cap", robe="jacket", trim="#f0ead8"),
    "victorian": dict(tunic="#26262e", belt=None, hose="#5a5a62", boot="#1a1616", hat="tophat", robe="coat", trim="#e8e2d4"),
    "cricket":   dict(tunic="#f2efe6", belt="#2a3a6a", hose="#f2efe6", boot="#e8e2d6", hat="cap", hatcolor="#2a3a6a", robe="jacket"),
    "winter":    dict(tunic="#5a4a3a", belt="#2a1a10", hose="#3a3030", boot="#2a1a10", hat="bowler", robe="coat", trim="#7a3a2a"),
    "modern":    dict(tunic="#ef7a1d", belt=None, hose="#1d1a1a", boot="#f4f4f4", robe="jacket"),
}
_CLEAN = dict(facial=None, goatee=None, beard=None, beard_style=None, stubble=None)
# facial hair by era, from the approved 2D era sheets (media/library/characters/*/eras/*.prompt.txt).
# Eras without an approved 2D sheet borrow the nearest one: school/cricket/winter = victorian (same decades), song = han.
_MAIN = dict(
    han=dict(_CLEAN, facial="droop"),
    greek=dict(_CLEAN, beard="#4a3020", beard_style="short"),
    heian=dict(_CLEAN, facial="thin", goatee="#4a3020"),
    medieval=dict(_CLEAN, stubble="#4a3020"),
    victorian=dict(_CLEAN, facial="handlebar"),
)
_TWO = dict(
    han=dict(_CLEAN), heian=dict(_CLEAN),
    greek=dict(_CLEAN, beard="#c8723a", beard_style="short"),
    medieval=dict(_CLEAN, stubble="#b0602e"),
    victorian=dict(_CLEAN, facial="thin"),
)
for _d in (_MAIN, _TWO):
    _d.update(school=_d["victorian"], cricket=_d["victorian"], winter=_d["victorian"], song=_d["han"])
ERA_FACE = {"main": _MAIN, "two": _TWO}

KINGS = {   # the ruler (#3) of each era: robe + the right royal headwear (+ facial hair from his 2D era sheet)
    "edward":  dict(beard="#a9abae", beard_style="short"),
    "james":   dict(tunic="#24356e", trim="#d9a83a"),                        # James I of Scotland
    "henry":   dict(tunic="#5a1a3a", trim="#d9a83a"),                        # Henry VIII
    "huizong": dict(tunic="#e0b030", trim="#b8282a", crown=False, hat="futou", robe="long"),   # Song emperor
    "gaozu":   dict(tunic="#1d1a1a", trim="#b8282a", crown=False, hat="mianguan", robe="long", facial="thin", facial_color="#2a2420", goatee="#2a2420"),
    "hongwu":  dict(tunic="#e0b030", trim="#b8282a", crown=False, hat="ming", robe="long", beard="#4a4848", beard_style="full"),
}


def woman_spec(seed, kit="#c8282a", hair=None, era="modern"):
    """A woman player / extra (no team scarf): longer tousled hair, kit colours."""
    import random
    r = random.Random(seed)
    hair = hair or r.choice(["#3a2618", "#7a4a22", "#c8a060", "#2a1a10", "#b86a3a"])
    sp = npc_spec(seed, era)
    sp.update(dict(hair=hair, hairstyle="tousled", brows=hair, facial=None, beard=None, cheeks=True, tunic=kit, sleeve=None,
                   robe="jacket", hose="#f2efe6" if era == "1920" else "#1d1a1a", boot="#2a1a10", hat=None, default="happy"))
    if era == "1920":
        sp.update(hat="cap", hatcolor="#f4f0e6", robe="short", tunic="#f4f0e6", trim=kit)
    return sp


def npc_spec(seed, era="medieval", **over):
    """A free-looking extra (no team scarf), deterministic from the seed."""
    import random
    r = random.Random(seed)
    hair = r.choice(["#3a2618", "#5a3a22", "#2a1a10", "#8a5a2a", "#c8a060", "#9a9a9a", "#b86a3a"])
    sp = dict(build="compact", skin=r.choice(["#f7f5f0", "#f4ece0", "#efe2cf"]), tunic=r.choice(["#7a5a3a", "#5a6a4a", "#6a4a5a", "#8a7a5a", "#4a5a6a", "#9a6a3a"]),
              trim=None, belt="#3a2618", buckle="#9a7a3a", hose=r.choice(["#3a3030", "#4a4038", "#2a2a30"]), boot=r.choice(["#5a3a22", "#2a1a10"]),
              sole="#1d1612", hair=hair, hairstyle=r.choice(["messy", "tousled", "messy", "sides", "bald"]), brows=hair, brow_w=0.015,
              facial=r.choice([None, None, "handlebar"]), beard=r.choice([None, None, None, hair]), glasses=False, cheeks=r.random() < 0.3,
              crown=False, default=r.choice(["neutral", "happy", "surprised"]), mouth_z=-0.13, scarf=False)
    if sp["beard"]:
        sp["facial"] = None
    c = dict(COSTUMES.get(era, {}))
    if "tunic" in c and era not in ("victorian", "school", "cricket", "heian", "greek"):
        c["tunic"] = sp["tunic"]; c.pop("sleeve", None)
    if era == "medieval" and r.random() < 0.4:
        c["hat"] = r.choice(["hood", "coif"]); c["hatcolor"] = r.choice(["#6a5a3a", "#5a4a6a", "#4a5a3a"])
    sp.update(c)
    sp.update(over)
    return sp


class Character:
    """root (ground) > hips (z 0.5) > torso > arms(elbow) + head ; hips > legs(knee).
    who: 'main' | 'two' | 'king' (or pass spec=npc_spec(...)). era: COSTUMES key; king: KINGS key.
    exprs: [(frame, expression), ...] to switch faces during a shot."""

    def __init__(self, who="main", loc=(0, 0, 0), rotz=0.0, expr=None, name=None, era=None, king=None, spec=None, exprs=None):
        spec = dict(spec or SPECS[who])
        if who == "woman":
            pass
        spec.setdefault("scarf", True)
        if era and who in ("main", "two") and spec is not None:
            spec.update(COSTUMES.get(era, {}))
            spec.update(ERA_FACE.get(who, {}).get(era, {}))
        if king:
            spec.update(KINGS[king])
        n = name or who
        self.spec, self.n = spec, n
        round_ = spec["build"] == "round"
        robe = spec.get("robe", "short" if not round_ else "round")
        tunic = mat(f"tunic-{n}", spec["tunic"], 0.85, noise=0.06, nscale=25)
        skin = mat(f"skin-{n}", spec["skin"], 0.55)
        sl = spec.get("sleeve")
        sleeve = skin if sl == "skin" else (mat(f"sleeve-{n}", sl, 0.85, noise=0.06, nscale=25) if sl else tunic)
        hose = skin if spec["hose"] == "skin" else mat(f"hose-{n}", spec["hose"], 0.8)
        boot = mat(f"boot-{n}", spec["boot"], 0.45)
        sole = mat(f"sole-{n}", spec.get("sole", "#161312"), 0.7)
        white = mat("mitten", "#fbfaf7", 0.5)
        self.root = empty(f"{n}-root", loc)
        self.root.rotation_euler = (0, 0, rotz)
        self.hips = empty(f"{n}-hips", (0, 0, 0.5), self.root)
        self.torso = empty(f"{n}-torso", (0, 0, 0), self.hips)
        # ---- tunic / robe (profile in ground space, shifted down by the hips height)
        if round_:
            hem = 0.12 if robe == "long" else 0.23
            # egg-shaped like the sheet: the belly is the widest part, narrow shoulders (owner: no boxy coat)
            prof = [(0, hem), (0.3, hem), (0.33, hem + 0.05), (0.365, 0.4), (0.37, 0.5), (0.35, 0.62), (0.3, 0.74), (0.24, 0.84),
                    (0.17, 0.92), (0.08, 0.97), (0, 0.985)]
            sy = 0.95
        else:
            hem = {"long": 0.1, "coat": 0.3, "jacket": 0.46, "short": 0.34}.get(robe, 0.34)
            flare = 0.3 if robe == "long" else 0.252
            prof = [(0, hem), (flare - 0.02, hem), (flare, hem + 0.03), (0.248 if robe != "jacket" else 0.235, max(hem + 0.06, 0.45)),
                    (0.228, 0.55), (0.214, 0.7), (0.216, 0.82), (0.198, 0.9), (0.14, 0.95), (0.06, 0.978), (0, 0.985)]
            prof = sorted(prof, key=lambda p: p[1]) if robe != "long" else prof
            sy = 0.82
        lathe(f"{n}-tunic", [(r, z - 0.5) for r, z in prof], tunic, self.torso, sy=sy, segs=48)
        if spec.get("armor"):  # Han lamellar vest
            am = mat(f"armor-{n}", spec["armor"], 0.4, noise=0.1, nscale=40, bump=0.3)
            lathe(f"{n}-armor", [(0.24, 0.5 - 0.5), (0.245, 0.55 - 0.5), (0.232, 0.7 - 0.5), (0.232, 0.82 - 0.5), (0.215, 0.9 - 0.5), (0.0, 0.92 - 0.5)], am, self.torso, sy=0.86)
        if spec.get("belt"):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.231, minor_radius=0.02, location=(0, 0, 0.03), major_segments=48)
            b = bpy.context.object; b.name = f"{n}-belt"; b.scale = (1, 0.83, 1)
            for p in b.data.polygons:
                p.use_smooth = True
            b.data.materials.append(mat(f"belt-{n}", spec["belt"], 0.5)); b.parent = self.torso
            slab(f"{n}-buckle", (0.06, 0.02, 0.05), (0, -0.231 * 0.83 - 0.012, 0.03), mat(f"buckle-{n}", spec.get("buckle") or "#b8893a", 0.3), self.torso)
        if spec.get("trim"):  # hem + front opening stripe (king's robe, coats, jackets)
            gold = mat(f"trim-{n}", spec["trim"], 0.35)
            hr = prof[1][0] if not round_ else 0.293
            bpy.ops.mesh.primitive_torus_add(major_radius=hr + 0.003, minor_radius=0.016, location=(0, 0, hem - 0.5 + 0.01), major_segments=48)
            t = bpy.context.object; t.name = f"{n}-hemtrim"; t.scale = (1, sy + 0.02, 1); t.data.materials.append(gold); t.parent = self.torso
            for p in t.data.polygons:
                p.use_smooth = True
            pts = [(0.02, -r * sy - 0.004, z - 0.5) for r, z in prof[1:-2]]
            tube(f"{n}-fronttrim", pts, 0.014, gold, self.torso)
            if round_:
                for z in (0.62, 0.74):
                    sphere(f"{n}-button{z}", 0.016, (0.055, -[r for r, zz in prof if zz >= z][0] * sy + 0.004, z - 0.5), gold, self.torso, seg=12)
        # ---- scarf (team colour) with a hanging tail on the viewer's right — main characters only
        if spec.get("scarf", True):
            orange = mat("scarf", SCARF, 0.8, noise=0.06, nscale=30)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.075, location=(0, 0, 0.49), major_segments=40, minor_segments=16)
            s_ = bpy.context.object; s_.name = f"{n}-scarf"; s_.scale = (1.05, 0.95, 0.9); s_.data.materials.append(orange); s_.parent = self.torso
            for p in s_.data.polygons:
                p.use_smooth = True
            sphere(f"{n}-knot", 0.062, (0.08, -0.16, 0.46), orange, self.torso, scale=(1, 0.8, 1))
            self.tail = slab(f"{n}-tail", (0.1, 0.035, 0.34), (0.09, -0.2 - (0.06 if round_ else 0), 0.3), orange, self.torso, rot=(0.1, 0.06, 0))
        else:
            sphere(f"{n}-neck", 0.08, (0, 0, 0.5), skin, self.torso, scale=(1, 1, 0.8))
        # ---- arms: shoulder > upper sleeve > elbow > forearm sleeve > white mitten
        shoulder_x = 0.25 if round_ else 0.215
        self.arm_rest = 0.42 if round_ else 0.22   # outward rest angle: a gap between arm and body (the king's belly is wide)
        if robe == "long" and not round_:
            shoulder_x = 0.225
        self.arms, self.elbows = [], []
        for side in (-1, 1):
            a = empty(f"{n}-arm{side}", (side * shoulder_x, 0, 0.38 if not round_ else 0.33), self.torso)
            lathe(f"{n}-upper{side}", capsule(0.2, 0.06, 0.052), tunic if sl == "skin" else sleeve, a, segs=24) if sl != "skin" else \
                lathe(f"{n}-upper{side}", capsule(0.08, 0.065, 0.06), tunic, a, segs=24)
            if sl == "skin":
                lathe(f"{n}-uparm{side}", capsule(0.2, 0.05, 0.047), skin, a, segs=24)
            e = empty(f"{n}-elbow{side}", (0, 0, -0.21), a)
            lathe(f"{n}-fore{side}", capsule(0.15, 0.052, 0.054), skin if sl == "skin" else sleeve, e, segs=24)
            if sl != "skin":
                bpy.ops.mesh.primitive_torus_add(major_radius=0.052, minor_radius=0.014, location=(0, 0, -0.15), major_segments=24, minor_segments=8)
                cf = bpy.context.object; cf.name = f"{n}-cuff{side}"; cf.data.materials.append(sleeve); cf.parent = e
                for p in cf.data.polygons:
                    p.use_smooth = True
            sphere(f"{n}-hand{side}", 0.068, (0, 0, -0.215), white, e, seg=32)
            a.rotation_euler = (0, -side * self.arm_rest, 0)   # outward: a gap between arm and body
            self.arms.append(a); self.elbows.append(e)
        # ---- legs: hip > thigh > knee > shin + whole boot; sole bottom exactly at ground
        self.legs, self.knees = [], []
        hip_x = 0.095 if not round_ else 0.11
        for side in (-1, 1):
            lg = empty(f"{n}-leg{side}", (side * hip_x, 0, 0), self.hips)
            lathe(f"{n}-thigh{side}", capsule(0.2, 0.062, 0.056), hose, lg, segs=24)
            kn = empty(f"{n}-knee{side}", (0, 0, -0.22), lg)
            lathe(f"{n}-shin{side}", capsule(0.12, 0.056, 0.055), hose, kn, segs=24)
            lathe(f"{n}-bootshaft{side}", [(0, -0.27), (0.072, -0.27), (0.08, -0.24), (0.079, -0.16), (0.074, -0.12),
                                           (0.065, -0.115), (0, -0.115)], boot, kn, segs=32)
            sphere(f"{n}-toe{side}", 0.072, (0, -0.075, -0.23), boot, kn, scale=(1, 1.35, 0.62), seg=32)
            slab(f"{n}-sole{side}", (0.16, 0.27, 0.022), (0, -0.045, -0.269), sole, kn)
            self.legs.append(lg); self.knees.append(kn)
        # ---- head: ONE head whose face blends between expressions (no head swapping, one mouth)
        import face3d
        exprs = exprs or [(1, expr or spec["default"])]
        self.head = empty(f"{n}-headpivot", (0, 0, 0.5), self.torso)
        h = build_head(f"{n}", spec, exprs[0][1], self.head, loc=(0, 0, 0))
        h.scale = (1.22, 1.22, 1.22)
        self.face = face3d.FACES[h.name]
        for fr, e in exprs[1:]:
            self.face.set(fr, e)


def _all_children(o):
    out = [o]
    for c in o.children:
        out += _all_children(c)
    return out


def _vis(h, frame, on):
    for o in _all_children(h):
        if o.type == "EMPTY":
            continue
        o.hide_render = not on
        o.keyframe_insert("hide_render", frame=frame)
        o.hide_viewport = not on
        o.keyframe_insert("hide_viewport", frame=frame)
