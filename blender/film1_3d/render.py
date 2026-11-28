"""Render film 1's picture scenes in 3D (Blender 4.5, EEVEE on the GPU).
  blender -b -P blender/film1_3d/render.py -- [--scenes 0-55|0,3,9] [--out media/projects/film-1-football/3d]
        [--engine eevee|cycles] [--w 1920 --h 1080] [--samples 64] [--stills] [--force]
Resumable: a scene whose clip already exists is skipped (unless --force). One clip per segment:
scene{i:02d}.mp4, or scene{i:02d}_{j}.mp4 for multi-segment scenes. plan.py writes the manifest Remotion reads."""
import math, os, sys, time, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import bpy
import fod3d as k
import cast3d as c3
import acting as A
import sets as SETS
_PLAN = (sys.argv[sys.argv.index("--plan") + 1] if "--plan" in sys.argv else "test")
if _PLAN == "full":
    import plan_full as plan
    from shots_full import SHOTS
else:
    import plan
    from shots import SHOTS

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(n, d=None):
    return argv[argv.index("--" + n) + 1] if "--" + n in argv else d
def flag(n):
    return ("--" + n) in argv

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.abspath(arg("out", os.path.join(ROOT, "media", "projects", "film-1-football-full" if _PLAN == "full" else "film-1-football", "3d")))
W, H = int(arg("w", 1920)), int(arg("h", 1080))
ENGINE = arg("engine", "eevee")
SAMPLES = int(arg("samples", 64))


def parse_scenes(s):
    if not s:
        return sorted(SHOTS)
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-"); out += [i for i in range(int(a), int(b) + 1) if i in SHOTS]
        else:
            out.append(int(part))
    return out


# ------------------------------------------------------------------ props
def _hand(ch, which):
    i = 1 if which == "hand1" else 0
    return ch.elbows[i]


def build_props(seg, cast, F, info):
    def res(v):
        if isinstance(v, str) and v.startswith("top"):
            return info.get("top", 0.8) + float(v[3:] or 0)
        return v
    for p in seg.get("props", []):
        kind, name = p[0], p[1]
        a = p[2:]
        if kind == "scroll":                      # attached to a hand
            ch = cast[a[0]]
            o = SETS.scroll(name, (0, 0, 0), length=0.45, r=0.045, rot=(0, 0, 0))
            o.parent = _hand(ch, a[1]); o.location = (0, -0.06, -0.3); o.rotation_euler = (0, math.pi / 2, 0)
        elif kind in ("scroll_open", "scroll_open_hand"):
            paper = k.mat("parchment", "#f1e2bc", 0.8, noise=0.12, nscale=10)
            o = k.box(name, (0.7, 0.01, 0.5), (0, 0, 0), paper)
            k.box(name + "txt", (0.5, 0.012, 0.03), (0, -0.002, 0.12), k.mat("inkline", "#3a2414"), o)
            k.box(name + "txt2", (0.4, 0.012, 0.03), (0, -0.002, 0.0), k.mat("inkline", "#3a2414"), o)
            k.cyl(name + "seal", 0.06, 0.02, (0, -0.012, -0.16), k.mat("wax", "#a8141a", 0.3), o, rot=(math.pi / 2, 0, 0))
            if kind == "scroll_open_hand":
                o.parent = _hand(cast[a[0]], a[1]); o.location = (0, -0.12, -0.25)
            else:
                o.location = a[0]; o.rotation_euler = (-1.2, 0, 0)
        elif kind.startswith("cujuball") or kind.startswith("leatherball"):
            mk = SETS.cuju_ball if kind.startswith("cuju") else SETS.leather_ball
            mode = kind.split("_")[1]
            if mode == "path":
                b = mk(name, a[0][0][1])
                A.path(b, a[0], spin=(6, 2, 0))
            elif mode == "still":
                mk(name, a[0])
            elif mode == "spin":
                b = mk(name, a[0], r=0.2)
                k.key(b, "rotation_euler", 1, (0, 0, 0)); k.key(b, "rotation_euler", F, (0.3, 0, 2.4))
                k.key(b, "location", 1, a[0]); k.key(b, "location", F // 2, (a[0][0], a[0][1], a[0][2] + 0.08)); k.key(b, "location", F, a[0])
            elif mode in ("hand", "carry"):
                b = mk(name, (0, 0, 0))
                b.parent = _hand(cast[a[0]], a[1]); b.location = (0, -0.05, -0.33)
            elif mode == "drop":
                start, end, t = a[0], (a[1][0], a[1][1], res(a[1][2])), a[2]
                b = mk(name, start, r=0.16)
                k.key(b, "location", 1, start); k.key(b, "location", A.f(t), start)
                k.key(b, "location", A.f(t + 0.45), end)
                k.key(b, "location", A.f(t + 0.6), (end[0], end[1], end[2] + 0.12))
                k.key(b, "location", A.f(t + 0.75), end)
        elif kind == "pedestal":
            m = k.mat("marble", "#f2eee6", 0.35, noise=0.05, nscale=3)
            k.cyl(name, 0.35, 1.0, (a[0][0], a[0][1], 0.5), m, verts=24)
            k.cyl(name + "top", 0.45, 0.1, (a[0][0], a[0][1], 1.05), m, verts=24)
            SETS.area((0, -1, 5), (0.2, 0, 0), 220, 1.2, (1, 0.95, 0.8))
        elif kind == "table":
            SETS.table(name, a[0], a[1], a[2], a[3])
        elif kind == "cart":
            wood = k.mat("cartwood", "#8a5a32", noise=0.15, nscale=6)
            c = k.empty(name, a[0])
            k.box(name + "bed", (1.6, 1.0, 0.25), (0, 0, 0.65), wood, c)
            for sx in (-1, 1):
                k.torus(name + f"w{sx}", 0.42, 0.06, (sx * 0.85, 0, 0.45), k.mat("wheel", "#3a2a1a"), c, rot=(0, math.pi / 2, 0))
            for j in range(6):
                k.ball(name + f"cab{j}", 0.13, (-0.5 + j * 0.2, 0, 0.9), k.mat("cabbage", "#7da13a", 0.6), c)
            k.key(c, "rotation_euler", A.f(a[1]), (0, 0, 0))
            k.key(c, "rotation_euler", A.f(a[1] + 0.5), (-1.1, 0, 0.2))   # tips over
        elif kind == "chickens":
            for j in range(4):
                ch = k.empty(name + str(j), (a[0][0] + j * 0.4, a[0][1] - j * 0.2, 0))
                k.ball(name + f"b{j}", 0.16, (0, 0, 0.25), k.mat("hen", "#f4f0e4", 0.7), ch, scale=(0.8, 1.2, 0.9))
                k.ball(name + f"h{j}", 0.08, (0, -0.18, 0.42), k.mat("hen", "#f4f0e4", 0.7), ch)
                k.cone(name + f"c{j}", 0.04, 0.08, (0, -0.2, 0.52), k.mat("comb", "#c8282a"), ch, verts=6)
                k.cone(name + f"bk{j}", 0.025, 0.06, (0, -0.27, 0.41), k.mat("beak", "#e8a83a"), ch, verts=6, rot=(math.pi / 2, 0, 0))
                t0 = a[1] + j * 0.15
                k.key(ch, "location", A.f(t0), (a[0][0] + j * 0.4, a[0][1] - j * 0.2, 0))
                for s in range(8):
                    k.key(ch, "location", A.f(t0 + 0.2 + s * 0.2), (a[0][0] + j * 0.4 + 0.5 * (s + 1) * (1 if j % 2 else -1), a[0][1] - j * 0.2 - 0.4 * (s + 1),
                                                                   0.3 if s % 2 else 0))
        elif kind == "longbow":
            ch = cast[a[0]]
            o = c3.tube(name, [(0, -0.05, 0.55), (0, -0.18, 0), (0, -0.05, -0.55)], 0.018, k.mat("yew", "#8a5a2a", 0.5))
            o.parent = _hand(ch, a[1]); o.location = (0, -0.05, -0.25)
        elif kind == "arrows":
            for j, (t, p0, p1) in enumerate(a[0]):
                ar = c3.tube(name + str(j), [(0, 0, 0), (0, 0.6, 0)], 0.01, k.mat("arrow", "#7a5a3a"))
                k.key(ar, "location", 1, (p0[0], p0[1], -5)); k.key(ar, "location", A.f(t) - 1, (p0[0], p0[1], -5))
                k.key(ar, "location", A.f(t), p0); k.key(ar, "location", A.f(t + 0.5), (p1[0], p1[1] - 0.6, p1[2]))
        elif kind == "trophy":          # FA Cup: little silver cup with handles, held up by a hand
            silver = k.mat("silver", "#d8dce0", 0.15)
            o = c3.lathe(name, [(0, 0), (0.07, 0), (0.07, 0.02), (0.025, 0.05), (0.02, 0.12), (0.09, 0.2), (0.1, 0.32), (0.085, 0.33), (0, 0.31)], silver)
            for sx in (-1, 1):
                k.torus(name + f"h{sx}", 0.04, 0.008, (sx * 0.1, 0, 0.26), silver, o, rot=(math.pi / 2, 0, 0))
            o.parent = _hand(cast[a[0]], a[1]); o.location = (0, -0.06, -0.25); o.rotation_euler = (math.pi, 0, 0)
        elif kind == "boot":            # Henry VIII's football boot, held up
            lea = k.mat("tudorboot", "#5a3420", 0.5)
            o = k.empty(name, (0, 0, 0))
            c3.lathe(name + "s", [(0, 0), (0.06, 0), (0.065, 0.12), (0.06, 0.2), (0, 0.2)], lea, o)
            c3.sphere(name + "t", 0.06, (0, -0.07, 0.02), lea, o, scale=(1, 1.5, 0.6))
            o.parent = _hand(cast[a[0]], a[1]); o.location = (0, -0.08, -0.3)
        elif kind == "golfclub":
            o = c3.tube(name, [(0, 0, 0), (0, -0.02, -0.75), (0, -0.09, -0.8)], 0.012, k.mat("hickory", "#7a5a3a", 0.5))
            o.parent = _hand(cast[a[0]], a[1]); o.location = (0, -0.03, -0.2)
        elif kind == "goal":            # a[0] loc, a[1] 'tape'|'bar'|'net'
            white = k.mat("line", "#f4f4f4", 0.6)
            x, y, z = a[0]
            for sx in (-1, 1):
                k.cyl(name + f"p{sx}", 0.06, 2.44, (x + sx * 3.66, y, 1.22), white, verts=10)
            if a[1] == "tape":
                k.cyl(name + "tape", 0.015, 7.32, (x, y, 2.44), white, rot=(0, math.pi / 2, 0), verts=6)
            else:
                k.cyl(name + "bar", 0.06, 7.32, (x, y, 2.44), white, rot=(0, math.pi / 2, 0), verts=10)
            if a[1] == "net":
                net = bpy.data.materials.new("netm"); net.use_nodes = True
                nt = net.node_tree; bsdf = nt.nodes["Principled BSDF"]
                br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 18
                br.inputs["Mortar Size"].default_value = 0.08
                nt.links.new(br.outputs["Fac"], bsdf.inputs["Alpha"])
                bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1)
                try:
                    net.blend_method = "HASHED"
                except Exception:
                    pass
                for o in (k.box(name + "nb", (7.32, 0.02, 2.44), (x, y + 1.5, 1.22), net), k.box(name + "nt", (7.32, 1.5, 0.02), (x, y + 0.75, 2.44), net)):
                    pass
                for sx in (-1, 1):
                    k.box(name + f"ns{sx}", (0.02, 1.5, 2.44), (x + sx * 3.66, y + 0.75, 1.22), net)
        # "breath", "door_open": decorative, skipped


# ------------------------------------------------------------------ shot checks (owner rules 2026-11-28)
def cam_mid(cam):
    """Rough camera position in the middle of the shot (for the facing check)."""
    if cam["kind"] == "push":
        return tuple((a + b) / 2 for a, b in zip(cam["p0"], cam["p1"]))
    if cam["kind"] == "orbit":
        a = (cam["a0"] + cam["a1"]) / 2
        c = cam["c"]
        return (c[0] + math.sin(a) * cam["r"], c[1] - math.cos(a) * cam["r"], c[2] + cam["h"])
    ks = cam["k"]
    return tuple(sum(k_[1][i] for k_ in ks) / len(ks) for i in range(3))


MAX_TURN = math.radians(55)   # faces must be visible: at worst a 3/4 view


def face_camera(seg):
    """Turn every standing character (not walking) so its face is within MAX_TURN of the camera.
    Keeps the intended direction as much as allowed; logs every correction."""
    cm = cam_mid(seg["cam"])
    walkers = {a[0] for a in seg.get("acts", []) if a[1] == "walk"}
    for c in seg.get("cast", []):
        if c["id"] in walkers:
            continue
        x, y = c["loc"][0], c["loc"][1]
        want = math.atan2(cm[0] - x, -(cm[1] - y))          # rz that faces the camera exactly
        d = (c["rz"] - want + math.pi) % math.tau - math.pi
        if abs(d) > MAX_TURN:
            new = want + math.copysign(MAX_TURN, d)
            print(f"  check: {c['id']} turned towards the camera ({math.degrees(d):.0f} -> {math.degrees(MAX_TURN * (1 if d > 0 else -1)):.0f} deg)")
            c["rz"] = new


def _toe_world(ch, leg, frame):
    sc = bpy.context.scene
    sc.frame_set(frame)
    side = -1 if leg == 0 else 1
    toe = bpy.data.objects.get(f"{ch.n}-toe{side}")
    return tuple(toe.matrix_world.translation) if toe else None


def ball_contacts(seg, cast):
    """Every kick touches the ball: the ball's key at the kick (and its rest point just before) is moved
    to the kicking foot's real position at the contact frame."""
    kicks = [(a[0], a[2], (a[3] if len(a) > 3 else 1)) for a in seg.get("acts", []) if a[1] == "kick" and a[0] in cast]
    for p in seg.get("props", []):
        if not p[0].endswith("_path"):
            continue
        pts = p[2]
        for cid, t, leg in kicks:
            hit = [i for i, (tt, _) in enumerate(pts) if abs(tt - t) <= 0.08]
            if not hit:
                continue
            toe = _toe_world(cast[cid], leg, A.f(t))
            if not toe:
                continue
            ch = cast[cid]
            rz = ch.root.rotation_euler.z
            fwd = (math.sin(rz), -math.cos(rz))
            r = 0.12
            spot = (toe[0] + fwd[0] * 0.1, toe[1] + fwd[1] * 0.1, max(r, toe[2]))
            i = hit[0]
            old = pts[i][1]
            pts[i] = (pts[i][0], spot)
            if i > 0 and pts[i - 1][1][2] <= r + 0.05 and abs(pts[i - 1][1][0] - old[0]) < 0.3 and abs(pts[i - 1][1][1] - old[1]) < 0.3:
                pts[i - 1] = (pts[i - 1][0], spot)          # the ball waits at the foot
            print(f"  check: ball meets {cid}'s foot at {t:.2f}s")
    bpy.context.scene.frame_set(1)


# ------------------------------------------------------------------ camera
def build_camera(cam, F):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cd.lens = cam.get("lens", 35)
    cd.dof.use_dof = True; cd.dof.aperture_fstop = 4.0
    co = bpy.data.objects.new("cam", cd); sc.collection.objects.link(co); sc.camera = co
    tg = k.empty("cam-target", (0, 0, 1))
    tr = co.constraints.new("TRACK_TO"); tr.target = tg; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
    cd.dof.focus_object = tg
    kind = cam["kind"]
    if kind == "push":
        k.key(co, "location", 1, cam["p0"]); k.key(co, "location", F, cam["p1"])
        k.key(tg, "location", 1, cam["t0"]); k.key(tg, "location", F, cam["t1"])
    elif kind == "orbit":
        c, r, h = cam["c"], cam["r"], cam["h"]
        for fr in range(1, F + 1, 6):
            u = (fr - 1) / max(1, F - 1)
            u = u * u * (3 - 2 * u)
            a = cam["a0"] + (cam["a1"] - cam["a0"]) * u
            k.key(co, "location", fr, (c[0] + math.sin(a) * r, c[1] - math.cos(a) * r, c[2] + h - 1.0 + 0.4))
        k.key(co, "location", F, (c[0] + math.sin(cam["a1"]) * r, c[1] - math.cos(cam["a1"]) * r, c[2] + h - 0.6))
        k.key(tg, "location", 1, c); k.key(tg, "location", F, c)
    else:
        last = None
        for t, p, tt in cam["k"]:
            fr = min(F, A.f(t))
            k.key(co, "location", fr, p); k.key(tg, "location", fr, tt)
            last = (fr, p, tt)
        if last and last[0] < F:   # never a frozen camera: keep drifting slowly towards the subject
            fr, p, tt = last
            u = min(0.25, 0.012 * (F - fr) / 30 * 4)
            k.key(co, "location", F, tuple(p[i] + (tt[i] - p[i]) * u for i in range(3)))
    return co


# ------------------------------------------------------------------ one segment
BEATS = os.path.join(ROOT, "films", "film-1-football-full" if _PLAN == "full" else "film-1-football", "beats.json")


def _words():
    import json
    out = []
    for v in json.load(open(BEATS, encoding="utf-8"))["vo"]:
        out += v.get("words", [])
    return out


WORDS = _words()


def build_segment(seg, F, shot_start=0.0):
    sc = k.reset(F, W, H, ENGINE, SAMPLES)
    sc.render.use_freestyle = False          # owner: pure 3D shading, no outlines
    import copy
    seg = copy.deepcopy(seg)
    face_camera(seg)
    info = SETS.SETS[seg["set"]](F) or {}
    cast = {}
    for i, c in enumerate(seg.get("cast", [])):
        if c["who"] == "npc":
            ch = c3.Character("npc", c["loc"], c["rz"], name=c["id"], spec=c3.npc_spec(c["npc"], c.get("npc_era") or "medieval"))
        elif c["who"] == "woman":
            ch = c3.Character("npc", c["loc"], c["rz"], name=c["id"], spec=c3.woman_spec(c["npc"], c.get("kit") or "#c8282a", era=c.get("npc_era") or "modern"))
        else:
            ch = c3.Character(c["who"], c["loc"], c["rz"], expr=c.get("expr"), name=c["id"], era=c.get("era"), king=c.get("king"), exprs=c.get("exprs"))
        A.idle(ch, F, seed=i)
        cast[c["id"]] = ch
    dur = F / 30.0
    A.WORDS, A.SHOT_START = WORDS, shot_start
    for act in seg.get("acts", []):
        cid, name, *args = act
        if cid not in cast:
            continue
        if name in ("cheer", "ears", "angry", "talk", "write") and len(args) >= 2:
            args[1] = min(args[1], dur - 0.3)
            if args[1] <= args[0]:
                continue
        try:
            A.ACTS[name](cast[cid], *args)
        except Exception as e:
            print("act failed", act, e)
    ball_contacts(seg, cast)
    build_props(seg, cast, F, info)
    build_camera(seg["cam"], F)
    frame_check(seg, cast)
    return sc


def frame_check(seg, cast):
    """Warn when a kick happens outside the picture (the viewer must see foot meet ball)."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    for a in seg.get("acts", []):
        if a[1] != "kick" or a[0] not in cast:
            continue
        leg = a[3] if len(a) > 3 else 1
        f = A.f(a[2])
        sc.frame_set(f)
        toe = bpy.data.objects.get(f"{cast[a[0]].n}-toe{-1 if leg == 0 else 1}")
        if not toe:
            continue
        v = world_to_camera_view(sc, sc.camera, toe.matrix_world.translation)
        if not (0.03 < v.x < 0.97 and 0.03 < v.y < 0.97 and v.z > 0):
            print(f"  WARN check: kick by {a[0]} at {a[2]:.2f}s is outside the picture")
        else:
            print(f"  check: kick by {a[0]} at {a[2]:.2f}s is in the picture")
    sc.frame_set(1)


def render_scene(i, force=False, stills=False):
    shot = SHOTS[i]
    segs = plan.segments(i)
    start = plan.scene_start(i)
    for j, (seg, F, fname) in enumerate(segs):
        out = os.path.join(OUT, fname)
        if stills:
            out = out.replace(".mp4", ".png")
        if os.path.exists(out) and not force:
            print("skip", fname); continue
        t0 = time.time()
        sc = build_segment(seg, F, start)
        if stills:
            sc.frame_set(max(1, int(F * 0.55)))
            sc.render.image_settings.file_format = "PNG"
            sc.render.filepath = out
            bpy.ops.render.render(write_still=True)
        else:
            tmp = out.replace(".mp4", ".part.mp4")
            sc.render.image_settings.file_format = "FFMPEG"
            sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
            sc.render.ffmpeg.constant_rate_factor = "HIGH"
            sc.render.filepath = tmp
            bpy.ops.render.render(animation=True)
            os.replace(tmp, out)
        print(f"RENDERED {fname} {F} frames in {time.time() - t0:.0f}s", flush=True)
        start += F / 30.0


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    plan.write_manifest(os.path.join(OUT, "manifest.json"))
    for i in parse_scenes(arg("scenes")):
        try:
            render_scene(i, force=flag("force"), stills=flag("stills"))
        except Exception:
            print("SCENE FAILED", i); traceback.print_exc()
    print("ALL DONE")
