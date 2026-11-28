"""Animated faces + strand hair for the 3D cast (owner feedback 2026-11-27):
- ONE mouth per character, shaped by shape keys (open / smile-frown / round / wide / grin), lip-synced
  syllable by syllable to the narrator's word timings. Never two mouths.
- Expressions BLEND (brows tilt/lift, lids, squint, mouth) over ~0.25 s instead of swapping heads.
- Real hair: thousands of strands (Blender hair curves), clumped into locks, on a smooth base mass.
Head space: skull centre at (0, 0, SKULL_Z), radius R, the face looks towards -Y."""
import math, random
import bpy
from fod3d import mat, empty, hexrgb, _shade
import cast3d as C
from cast3d import R, SKULL_Z, sphere, tube, surf

FPS = 30

# expression = facial parameters (blended)
FACE = {
    #               brow L (inner_dz, lift), brow R,  eye scale z, lids L/R, mouth keys
    "neutral":    dict(bl=(0, 0), br=(0, 0), eye=1.0, lid=(0, 0), m=dict(smile=0.15)),
    "happy":      dict(bl=(0.01, 0.02), br=(0.01, 0.02), eye=0.45, lid=(0, 0), m=dict(smile=1.0, exopen=0.45, teeth=0.8)),
    "sad":        dict(bl=(0.03, 0.0), br=(0.03, 0.0), eye=0.95, lid=(0.25, 0.25), m=dict(smile=-0.85)),
    "surprised":  dict(bl=(0, 0.045), br=(0, 0.045), eye=1.3, lid=(0, 0), m=dict(round=1.0, exopen=0.55)),
    "angry":      dict(bl=(-0.035, -0.01), br=(-0.035, -0.01), eye=0.85, lid=(0.15, 0.15), m=dict(smile=-0.45, wide=0.5, exopen=0.22, teeth=1.0)),
    "suspicious": dict(bl=(-0.01, -0.015), br=(0.0, 0.025), eye=1.0, lid=(0.55, 0.0), m=dict(smile=-0.1, wide=-0.3)),
    "grumpy":     dict(bl=(-0.005, -0.01), br=(-0.005, -0.01), eye=1.0, lid=(0.5, 0.5), m=dict(smile=-0.5, wide=-0.2)),
    "smug":       dict(bl=(0.0, 0.0), br=(-0.01, -0.01), eye=1.0, lid=(0.45, 0.45), m=dict(smile=0.75, wide=0.2)),
}
MOUTH_KEYS = ("smile", "open", "exopen", "round", "wide", "teeth")


# ------------------------------------------------------------------ mouth geometry
def _mouth_curves(u, p, mz):
    """Top/bottom lip line z at u in [-1, 1] for parameters p; returns (x, z_top, z_bot)."""
    smile, op = p.get("smile", 0), p.get("open", 0) + p.get("exopen", 0)
    rnd_, wide = p.get("round", 0), p.get("wide", 0)
    w = 0.072 * (1 + 0.35 * wide - 0.5 * rnd_)
    x = u * w
    bend = smile * 0.028 * (u * u) - smile * 0.006
    env = max(0.0, 1 - u * u) ** 0.6
    oz = op * (0.032 + 0.02 * rnd_) * env
    thick = 0.0035 + 0.0035 * env
    top = mz + bend + thick + oz * 0.45
    bot = mz + bend - thick - oz * 1.0
    return x, top, bot


def _strip(name, H, m, mz, frac_top, frac_bot, off, cols=28):
    """A mouth layer between fractions of the opening (0 = top lip, 1 = bottom lip). Shape keys per param."""
    def verts(p):
        vs = []
        for i in range(cols + 1):
            u = -1 + 2 * i / cols
            x, t, b = _mouth_curves(u, p, mz)
            for fr in (frac_top, frac_bot):
                z = t + (b - t) * fr
                vs.append(surf(x, z - SKULL_Z * 0, off))
        return vs
    base = verts({})
    faces = [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(cols)]
    me = bpy.data.meshes.new(name)
    me.from_pydata([(v[0], v[1], v[2]) for v in base], [], faces)
    for poly in me.polygons:
        poly.use_smooth = True
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(m)
    o.parent = H
    o.shape_key_add(name="Basis", from_mix=False)
    for kname in MOUTH_KEYS:
        if kname == "teeth":
            continue
        kb = o.shape_key_add(name=kname, from_mix=False)
        kb.slider_min = -1.0
        for i, v in enumerate(verts({kname: 1.0})):
            kb.data[i].co = v
    return o


# ------------------------------------------------------------------ the face rig
class Face:
    def __init__(self, n, spec, H, expr="neutral"):
        self.n, self.spec, self.H = n, spec, H
        ink = mat("eye-ink", "#141010", 0.18)
        skin = mat(f"skin-{n}", spec["skin"], 0.55)
        self.eyes, self.lids, self.brows = [], [], []
        # eyes: a group per eye (dot + shine), scaled for blink / squint / surprise
        for side in (-1, 1):
            c = surf(side * 0.085, 0.035, -0.004)
            E = empty(f"{n}-eyeg{side}", c, H)
            sphere(f"{n}-eye{side}", 0.031, (0, 0, 0), ink, E, scale=(0.82, 0.5, 1.25), seg=24)
            g = surf(side * 0.085 - side * 0.008, 0.051, 0.011)
            sphere(f"{n}-glint{side}", 0.007, (g[0] - c[0], g[1] - c[1], g[2] - c[2]), mat("glint", "#ffffff", 0.1, emit=1.0), E, seg=12)
            self.eyes.append(E)
            # upper lid: skin-coloured cap with a lash line, grows down over the dot
            L = empty(f"{n}-lidg{side}", surf(side * 0.085, 0.07, 0.0), H)
            sphere(f"{n}-lid{side}", 0.047, (0, -0.002, -0.022), skin, L, scale=(1.05, 0.55, 0.62), seg=24)
            tube(f"{n}-lash{side}", [(-0.042, -0.024, -0.04), (0, -0.03, -0.047), (0.042, -0.024, -0.04)], 0.0055, ink, L)
            L.scale = (1, 1, 0.001)
            self.lids.append(L)
        # brows: built around their own centre so they can tilt and lift
        bm = mat(f"brow-{n}", spec["brows"], 0.7)
        bw = spec["brow_w"]
        king = spec.get("hairstyle") == "sides"
        for side in (-1, 1):
            bz = 0.115 + (0.02 if spec["glasses"] else 0)
            pts = [surf(side * 0.045, bz, 0.007), surf(side * 0.09, bz + 0.008, 0.009), surf(side * 0.135, bz, 0.007)]
            if king:
                pts.append(surf(side * 0.165, bz + 0.03, 0.008))
            cx = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
            Bp = empty(f"{n}-browg{side}", tuple(cx), H)
            Bp.rotation_mode = "AXIS_ANGLE"
            nrm = [cx[0], cx[1], cx[2] - SKULL_Z]
            ln = math.sqrt(sum(v * v for v in nrm))
            Bp.rotation_axis_angle = (0, nrm[0] / ln, nrm[1] / ln, nrm[2] / ln)
            rel = [(p[0] - cx[0], p[1] - cx[1], p[2] - cx[2]) for p in pts]
            tube(f"{n}-brow{side}", rel, bw * (1.3 if king else 1.0), bm, Bp, radii=[0.85, 1.15, 1.0, 0.45][:len(rel)] if king else [0.85, 1.0, 0.7])
            Bp["base"] = tuple(cx)
            self.brows.append(Bp)
        # one mouth: dark opening + teeth + tongue layers, all driven by the same shape keys
        mz = spec["mouth_z"]
        self.mouth = [
            _strip(f"{n}-mouth", H, mat("mouth-dark", "#3a1412", 0.5), mz, 0.0, 1.0, 0.004),
            _strip(f"{n}-teeth", H, mat("teeth", "#fbf8f2", 0.3), mz, 0.06, 0.34, 0.0065),
            _strip(f"{n}-tongue", H, mat("tongue", "#c4545a", 0.5), mz, 0.72, 0.96, 0.0055),
        ]
        self.teeth = self.mouth[1]
        self.cur = None
        self.set(1, expr, dur=0)

    # ---- keyframing helpers
    def _k(self, o, path, frame, value):
        setattr(o, path, value)
        o.keyframe_insert(data_path=path, frame=frame)

    def _mk(self, kname, frame, value):
        for o in self.mouth:
            kb = o.data.shape_keys.key_blocks.get(kname)
            if kb is None:
                continue
            kb.value = value
            kb.keyframe_insert("value", frame=frame)

    def set(self, frame, expr, dur=0.25):
        """Blend to an expression: holds the old pose at frame, reaches the new one dur seconds later."""
        e = FACE.get(expr, FACE["neutral"])
        f1 = frame + int(round(dur * FPS))
        if self.cur and dur:
            self._apply(frame, FACE[self.cur])
        self._apply(f1, e)
        self.cur = expr

    def _apply(self, fr, e):
        for i, (Bp, (din, lift)) in enumerate(zip(self.brows, (e["bl"], e["br"]))):
            side = -1 if i == 0 else 1
            b = Bp["base"]
            self._k(Bp, "location", fr, (b[0], b[1], b[2] + lift))
            aa = list(Bp.rotation_axis_angle)
            aa[0] = side * -din * 9.0          # inner end down = angry, up = sad
            self._k(Bp, "rotation_axis_angle", fr, tuple(aa))
        for E in self.eyes:
            self._k(E, "scale", fr, (1.0 if e["eye"] < 1.1 else e["eye"], 1, e["eye"]))
        for L, v in zip(self.lids, e["lid"]):
            self._k(L, "scale", fr, (1, 1, max(0.001, v * 1.6)))
        m = e["m"]
        for kname in MOUTH_KEYS:
            if kname == "open":
                continue
            v = m.get(kname, 0.0)
            if kname == "teeth":
                self._k(self.teeth, "hide_render", fr, v < 0.3)
                continue
            self._mk(kname, fr, v)

    def blink(self, fr):
        cur = FACE.get(self.cur or "neutral")["eye"]
        for E in self.eyes:
            sx = 1.0 if cur < 1.1 else cur
            self._k(E, "scale", fr - 1, (sx, 1, cur))
            self._k(E, "scale", fr + 1, (sx, 1, 0.08))
            self._k(E, "scale", fr + 4, (sx, 1, cur))

    def talk(self, t0, t1, words, shot_start=0.0):
        """Lip-sync to the narrator's words (absolute times, shifted by shot_start) inside [t0, t1]."""
        f = lambda t: int(round(t * FPS)) + 1
        said = [(w["start"] - shot_start, w["end"] - shot_start, w["w"]) for w in words
                if t0 <= w["start"] - shot_start < t1]
        if not said:  # no narration here: a gentle generic rhythm
            t, said = t0, []
            while t < t1 - 0.2:
                said.append((t, t + 0.28, "ba")); t += 0.4
        self._mk("open", f(t0) - 1, 0.0)
        for s, e, w in said:
            vowels = sum(1 for i, ch in enumerate(w.lower()) if ch in "aeiouy" and (i == 0 or w.lower()[i - 1] not in "aeiouy"))
            n = max(1, min(4, vowels))
            seg = (e - s) / n
            for j in range(n):
                a = s + j * seg
                self._mk("open", f(a), 0.08)
                peak = 0.75 if any(c in w.lower() for c in "ao") else 0.55
                self._mk("open", f(a + seg * 0.45), peak)
                self._mk("open", f(a + seg * 0.9), 0.1)
            self._mk("open", f(e) + 1, 0.0)
        self._mk("open", f(t1), 0.0)


# ------------------------------------------------------------------ strand hair
def strand_mat(n, color):
    key_ = f"strands-{n}-{color}"
    if key_ in bpy.data.materials:
        return bpy.data.materials[key_]
    rgb = hexrgb(color)
    m = bpy.data.materials.new(key_); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    # EEVEE on the PC turned white sheen + sharp specular into white patches on top of the head (owner 2026-11-28):
    # soft, low specular, no sheen.
    b.inputs["Roughness"].default_value = 0.62
    for k_, v in (("Sheen Weight", 0.0), ("Specular IOR Level", 0.22), ("Coat Weight", 0.0)):
        if k_ in b.inputs:
            b.inputs[k_].default_value = v
    hi = nt.nodes.new("ShaderNodeHairInfo")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40
    rr = nt.nodes.new("ShaderNodeValToRGB")
    rr.color_ramp.elements[0].color = (*_shade(rgb, 0.6), 1)
    rr.color_ramp.elements[1].color = (*_shade(rgb, 1.2), 1)
    mix = nt.nodes.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"; mix.inputs[1].default_value = 0.75
    nt.links.new(hi.outputs["Intercept"], mix.inputs[0])
    nt.links.new(hi.outputs["Random"], mix.inputs[2]) if "Random" in hi.outputs else None
    sc = nt.nodes.new("ShaderNodeMath"); sc.operation = "MULTIPLY"; sc.inputs[1].default_value = 0.85
    nt.links.new(mix.outputs[0], sc.inputs[0])
    nt.links.new(sc.outputs[0], rr.inputs["Fac"])
    nt.links.new(rr.outputs["Color"], b.inputs["Base Color"])
    return m


def _nrm(v):
    L = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / L for c in v)


def _fib(N):
    g = math.pi * (3 - math.sqrt(5))
    for i in range(N):
        z = 1 - 2 * (i + 0.5) / N
        r = math.sqrt(1 - z * z)
        yield (math.cos(g * i) * r, math.sin(g * i) * r, z)


def _in_hair(p, style, margin=0.0):
    x, y, z = p
    if style == "sides":
        return -0.5 < z < 0.4 and (abs(x) > 0.6 or y > 0.4) and y > -0.2
    front = 0.62 if style == "messy" else 0.66      # in units of R: hairline height at the front
    return z > front - (0.45 if y < 0 else 0.8) * y - 0.22 - 0.35 * abs(x) - margin


def _flow(p, style, rnd):
    """Combing direction at scalp point p (unit) -> (direction, length, lift)."""
    x, y, z = p
    down = _nrm((-x * z, -y * z, 1 - z * z)); down = tuple(-c for c in down)
    if style == "messy":
        if y < -0.5 and z > 0.5:            # short ragged fringe: forward and down over the hairline
            return _nrm((x * 0.3 + rnd.uniform(-0.15, 0.15), -0.75, -0.65)), rnd.uniform(0.08, 0.11), 0.25
        flick = abs(x) > 0.55 and z < 0.65
        d = _nrm((down[0] + (x * 0.5 if flick else 0) + rnd.uniform(-0.15, 0.15), down[1] + rnd.uniform(-0.15, 0.15), down[2]))
        return d, rnd.uniform(0.17, 0.23), 0.35 if flick else 0.2
    if style == "tousled":
        if y < -0.3 and z > 0.45:            # fringe swept to the viewer's left
            return _nrm((-0.65, -0.55, -0.45)), rnd.uniform(0.1, 0.13), 0.25
        d = _nrm((down[0] + rnd.uniform(-0.28, 0.28), down[1] + rnd.uniform(-0.28, 0.28), down[2] + rnd.uniform(0.0, 0.2)))
        return d, rnd.uniform(0.18, 0.24), 0.3
    out = _nrm((x, y, -0.3))                 # king: puffs at the sides
    return out, rnd.uniform(0.05, 0.08), 0.9


def build_strands(n, spec, H, density=14000):
    """Hair curves: clumped strands that follow the style's flow; deterministic per style."""
    style = spec["hairstyle"]
    rnd = random.Random(style + "strands")
    guides = [p for p in _fib(160 if style != "sides" else 90) if _in_hair(p, style)]
    gdata = {}
    for gi, p in enumerate(guides):
        gdata[gi] = _flow(p, style, rnd)
    roots = [p for p in _fib(density) if _in_hair(p, style)]
    NP = 7
    curves = bpy.data.hair_curves.new(f"{n}-strands")
    curves.add_curves([NP] * len(roots))
    pos = []
    radii = []
    for p in roots:
        gi = min(range(len(guides)), key=lambda i: (guides[i][0] - p[0]) ** 2 + (guides[i][1] - p[1]) ** 2 + (guides[i][2] - p[2]) ** 2)
        d, L, lift = gdata[gi]
        L *= rnd.uniform(0.85, 1.1)
        g = guides[gi]
        gtip = None
        pts = []
        for k in range(NP):
            t = k / (NP - 1)
            # march over the scalp along d, lifted off it (volume), clumping towards the guide's path
            q = _nrm(tuple(p[i] + d[i] * t * L / R for i in range(3)))
            qg = _nrm(tuple(g[i] + d[i] * t * L / R for i in range(3)))
            cl = 0.32 * t * t
            q = _nrm(tuple(q[i] * (1 - cl) + qg[i] * cl for i in range(3)))
            r_ = R * (0.99 + (0.05 + 0.07 * lift) * math.sin(min(1.0, t * 1.6) * math.pi / 2) - 0.02 * t)
            if style == "sides":
                a = t * 4.0 + rnd.random()
                q = _nrm((q[0] + 0.05 * math.cos(a), q[1] + 0.05 * math.sin(a), q[2] + 0.04 * math.sin(a * 1.3)))
                r_ = R * (1.0 + 0.16 * math.sin(t * math.pi * 0.9))
            pts.append((q[0] * r_, q[1] * r_, q[2] * r_ + SKULL_Z))
            radii.append(0.0072 * (1 - t) ** 0.5 + 0.0026)   # fuller tips: EEVEE showed skin through thin tips
        pos += pts
    for i, v in enumerate(pos):
        curves.position_data[i].vector = v
    ra = curves.attributes.get("radius") or curves.attributes.new("radius", "FLOAT", "POINT")
    for i, r in enumerate(radii):
        ra.data[i].value = r
    o = bpy.data.objects.new(f"{n}-strands", curves)
    bpy.context.collection.objects.link(o)
    o.parent = H
    curves.materials.append(strand_mat(n, spec["hair"]))
    return o


def build_base_mass(n, spec, H):
    """Smooth, darker volume under the strands so no scalp shows through."""
    style = spec["hairstyle"]
    m = mat(f"hairbase-{n}", tuple(c * 0.75 for c in hexrgb(spec["hair"])), 0.6, noise=0.15, nscale=30)
    el = []
    for p in _fib(110):
        if _in_hair(p, style, margin=0.0 if style == "sides" else -0.06):
            el.append(("BALL", (p[0] * R * 0.86, p[1] * R * 0.86, p[2] * R * 0.86 + SKULL_Z), 0.125 if style != "sides" else 0.085, None))
    if el and style != "sides":
        el.append(("BALL", (0, 0, SKULL_Z + R * 0.88), 0.12, None))   # crown: no scalp peeking through at the top
    if el:
        C._mball(n + "base", H, m, el)


def build_head(n, spec, expr, parent, loc=(0, 0, 0)):
    """Head with one animated face and strand hair. Returns the head empty; the Face is H['face_rig']."""
    H = empty(f"{n}-head", loc, parent)
    skin = mat(f"skin-{n}", spec["skin"], 0.55)
    sphere(f"{n}-skull", R, (0, 0, SKULL_Z), skin, H, seg=64)
    if spec.get("cheeks"):
        for side in (-1, 1):
            sphere(f"{n}-cheek{side}", 0.045, surf(side * 0.15, -0.045, -0.02), mat("rosy", "#f2a0a0", 0.6), H, scale=(1, 0.5, 0.8), seg=24)
    face = Face(n, spec, H, expr or spec["default"])
    FACES[H.name] = face
    if spec.get("facial") == "handlebar":
        hm = mat(f"stache-{n}", spec["hair"], 0.55)
        for side in (-1, 1):
            s = side
            pts = [surf(0.0, -0.06, 0.012), surf(s * 0.06, -0.075, 0.018), surf(s * 0.125, -0.085, 0.016),
                   surf(s * 0.175, -0.06, 0.012), surf(s * 0.19, -0.02, 0.01), surf(s * 0.165, -0.005, 0.012)]
            tube(f"{n}-stache{side}", pts, 0.032, hm, H, radii=[0.95, 1.1, 0.85, 0.55, 0.38, 0.22])
    if spec.get("glasses"):
        rim = mat("rim", "#141010", 0.3)
        for side in (-1, 1):
            c = surf(side * 0.085, 0.035, 0.028)
            pts = [(c[0] + 0.07 * math.cos(a), c[1] + 0.008 * math.cos(a) * side, c[2] + 0.07 * math.sin(a)) for a in (i / 8 * math.tau for i in range(8))]
            tube(f"{n}-lens{side}", pts, 0.009, rim, H, cyclic=True)
            tube(f"{n}-temple{side}", [surf(side * 0.155, 0.045, 0.02), surf(side * 0.24, 0.05, 0.004), (side * 0.27, 0.05, SKULL_Z + 0.05)], 0.007, rim, H)
        tube(f"{n}-bridge", [surf(-0.02, 0.045, 0.03), surf(0, 0.052, 0.034), surf(0.02, 0.045, 0.03)], 0.007, rim, H)
    if spec.get("hairstyle") not in (None, "bald"):
        build_base_mass(n, spec, H)
        build_strands(n, spec, H)
    if spec.get("crown"):
        C.build_crown(n, H)
    if spec.get("hat"):
        C.build_hat(n, spec["hat"], H, spec)
    if spec.get("beard"):
        bm_ = C.hair_mat(n + "b", spec["beard"])
        el = [("ELLIPSOID", (0, -0.17, SKULL_Z - 0.17), 0.13, (1.4, 0.9, 1.0))] + \
             [("BALL", (side * 0.18, -0.15, SKULL_Z - 0.1), 0.09, None) for side in (-1, 1)]
        C._mball(n + "Beard", H, bm_, el)
    return H


FACES = {}
