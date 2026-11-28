"""Mixamo motion for cast3d characters (PRODUCTION-RULES "Mixamo motion", owner decision 2026-11-28).

A Mixamo clip (FBX Binary, Without Skin, 30 fps, on X Bot) is imported, sampled once, and its motion is
written as keyframes onto a cast3d Character's pivot chain:
    root > hips > torso > arm(shoulder) > elbow ; torso > head ; hips > leg > knee
No skinning is needed: our costume pieces already hang off those pivots.

How each pivot is driven
- hips / torso / head: the bone's ROTATION change from its rest pose (Hips, Spine2 vs Hips, Head vs Spine2).
- arms, elbows, legs, knees: DIRECTION matching. The limb is swung so it points where the Mixamo limb points.
  This makes Mixamo's T-pose rest irrelevant (our arms hang down at rest) and keeps proportions our own.
- knees also get the foot's twist, so the AI-sheet boots point where the Mixamo foot points.
- hips height follows the clip, scaled from Mixamo's leg length to ours (0.5 m hips).

Rules kept here (never regress)
- Feet never below the ground: per frame the lowest boot point is measured and the hips are lifted
  (ground="clamp"), or every frame is planted with the lowest foot exactly on the ground (ground="plant").
- Gap between arm and body: hanging arms keep at least `gap` of outward swing so the background shows.
- The character's facing and travel stay with the scene code (root). Use "In Place" clips; move the root
  with acting.walk-style keys, or pass root_motion=True to let the clip's hips travel.

Usage (inside a shot):
    import mixamo3d
    clip = mixamo3d.load("soccer-pass")                    # media/library/mixamo/soccer-pass.fbx
    mixamo3d.apply(ch, clip, t=2.0)                         # start at 2.0 s into the shot
    mixamo3d.contact_frame(clip, "RightFoot")             # clip frame where the foot moves fastest
"""
import math
import os

import bpy
from mathutils import Matrix, Quaternion, Vector

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.normpath(os.path.join(HERE, "..", "media", "library", "mixamo"))

# our pivots -> the Mixamo bones that drive them
DIR_MAP = {  # (from bone head, to bone head): limb direction
    "arm": ("{s}Arm", "{s}ForeArm"),
    "elbow": ("{s}ForeArm", "{s}Hand"),
    "leg": ("{s}UpLeg", "{s}Leg"),
    "knee": ("{s}Leg", "{s}Foot"),
}
BONES = ["Hips", "Spine", "Spine1", "Spine2", "Neck", "Head"] + [
    f"{s}{b}" for s in ("Left", "Right") for b in ("Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot", "ToeBase")]


def _side_name(side):
    # our side +1 is +X; the character faces -Y, so +X is its LEFT (Mixamo "Left")
    return "Left" if side > 0 else "Right"


def _norm(name):
    return name.split(":")[-1]


class Clip:
    """One sampled Mixamo clip: per frame, world-space matrices of every bone we use (already turned so the
    character faces -Y, hips rest at the origin on the ground)."""

    def __init__(self, name, frames, rest, scale_leg):
        self.name, self.frames, self.rest, self.leg_len = name, frames, rest, scale_leg

    def __len__(self):
        return len(self.frames)

    @property
    def seconds(self):
        return len(self.frames) / FPS


_cache = {}


def load(name_or_path, keep=False):
    """Import a Mixamo FBX and sample it. The imported armature is deleted afterwards (keep=True to inspect)."""
    path = name_or_path if name_or_path.lower().endswith(".fbx") else os.path.join(LIB, name_or_path + ".fbx")
    if path in _cache:
        return _cache[path]
    if not os.path.exists(path):
        raise FileNotFoundError(f"Mixamo clip missing: {path} (the owner downloads it from mixamo.com, see PRODUCTION-RULES)")
    before = set(bpy.data.objects)
    sc = bpy.context.scene
    keep_frame = sc.frame_current
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False, ignore_leaf_bones=True)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE")
    pb = {_norm(b.name): b for b in arm.pose.bones}
    missing = [b for b in BONES if b not in pb]
    if missing:
        raise ValueError(f"{path}: not a Mixamo skeleton, missing bones {missing}")
    act = arm.animation_data.action if arm.animation_data else None
    f0, f1 = (int(act.frame_range[0]), int(act.frame_range[1])) if act else (1, 1)

    mw = arm.matrix_world.copy()
    rest = {b: mw @ arm.data.bones[pb[b].name].matrix_local for b in BONES}
    # face -Y: forward = hips -> toes, flattened
    fwd = ((rest["LeftToeBase"].translation + rest["RightToeBase"].translation) / 2
           - (rest["LeftFoot"].translation + rest["RightFoot"].translation) / 2)
    fwd.z = 0
    ang = math.atan2(fwd.x, -fwd.y) if fwd.length > 1e-6 else 0.0
    C = Matrix.Rotation(-ang, 4, "Z")
    hip0 = rest["Hips"].translation.copy()
    ground = min(rest["LeftToeBase"].translation.z, rest["RightToeBase"].translation.z,
                 rest["LeftFoot"].translation.z, rest["RightFoot"].translation.z)
    T = Matrix.Translation(Vector((-hip0.x, -hip0.y, -ground)))
    fix = C @ T
    rest = {b: fix @ m for b, m in rest.items()}
    leg_len = rest["Hips"].translation.z

    frames = []
    for fr in range(f0, f1 + 1):
        sc.frame_set(fr)
        frames.append({b: fix @ mw @ pb[b].matrix for b in BONES})
    sc.frame_set(keep_frame)
    if not keep:
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
        if act:
            bpy.data.actions.remove(act)
    clip = Clip(os.path.splitext(os.path.basename(path))[0], frames, rest, leg_len)
    _cache[path] = clip
    return clip


def _delta(m, m0):
    """Rotation change of a bone from rest, in world axes."""
    return (m.to_3x3() @ m0.to_3x3().inverted()).to_quaternion()


def _swing(rest_dir, target):
    return Vector(rest_dir).rotation_difference(target.normalized())


def _q2e(q, prev):
    e = q.to_euler("XYZ", prev) if prev is not None else q.to_euler("XYZ")
    return e


def _pos(m):
    return m.translation


def contact_frame(clip, bone="RightFoot", lo=0.2, hi=0.85):
    """Clip frame (0-based) where `bone` moves fastest, searched in the middle of the clip: the strike of a
    kick/header. Ball paths are tied to this frame (PRODUCTION-RULES: kicks really touch the ball)."""
    n = len(clip)
    best, bi = -1.0, n // 2
    for i in range(max(1, int(n * lo)), min(n - 1, int(n * hi))):
        v = (_pos(clip.frames[i][bone]) - _pos(clip.frames[i - 1][bone])).length
        if v > best:
            best, bi = v, i
    return bi


def apply(ch, clip, t, speed=1.0, ground="clamp", gap=0.2, root_motion=False, start=0, end=None,
          parts=("hips", "torso", "head", "arms", "legs"), key_fn=None):
    """Write `clip` onto Character `ch`, starting `t` seconds into the shot.
    speed: >1 plays faster. start/end: clip frame range (0-based, end exclusive).
    parts: which pivots to drive (e.g. drop "head" while the character talks to camera).
    Returns the shot frame of every written clip frame, as {clip_index: shot_frame}."""
    from fod3d import key as _key
    key = key_fn or _key
    end = len(clip) if end is None else end
    gap = max(gap, getattr(ch, "arm_rest", 0.22) * 0.9)
    s = 0.5 / max(clip.leg_len, 1e-6)       # Mixamo -> our scale (hips 0.5 m)
    R = clip.rest
    prev = {}
    out = {}
    hip_rest = Vector(ch.hips.location)
    hips_rest_z = 0.5
    sole_pts = [Vector((0, -0.2, -0.27)), Vector((0, 0.08, -0.28)), Vector((0, -0.045, -0.28))]
    f0 = int(round(t * FPS)) + 1
    last_fr = None
    for i in range(start, end):
        fr = f0 + int(round((i - start) / speed))
        if fr == last_fr:
            continue
        last_fr = fr
        M = clip.frames[i]
        q_h = _delta(M["Hips"], R["Hips"])
        q_sp = _delta(M["Spine2"], R["Spine2"])
        q_hd = _delta(M["Head"], R["Head"])
        hips_w = q_h if "hips" in parts else Quaternion()
        torso_l = (q_h.inverted() @ q_sp) if "torso" in parts else Quaternion()
        torso_w = hips_w @ torso_l
        head_l = (q_sp.inverted() @ q_hd) if "head" in parts else Quaternion()

        hp = (_pos(M["Hips"]) - _pos(R["Hips"])) * s
        loc = Vector((hip_rest.x, hip_rest.y, hips_rest_z + hp.z))
        if root_motion:
            loc.x += hp.x
            loc.y += hp.y

        vals = {}
        if "hips" in parts:
            vals[ch.hips] = hips_w
        if "torso" in parts:
            vals[ch.torso] = torso_l
        if "head" in parts:
            vals[ch.head] = head_l

        feet = []
        for idx, side in enumerate((-1, 1)):
            S = _side_name(side)
            if "arms" in parts:
                a, e = ch.arms[idx], ch.elbows[idx]
                d = _pos(M[S + "ForeArm"]) - _pos(M[S + "Arm"])
                dl = torso_w.inverted() @ d.normalized()
                if dl.z < -0.3 and side * dl.x < gap * 0.8:        # hanging arm: keep the gap to the body
                    dl.x = side * gap * 0.8
                    dl.normalize()
                qa = _swing((0, 0, -1), dl)
                arm_w = torso_w @ qa
                d2 = _pos(M[S + "Hand"]) - _pos(M[S + "ForeArm"])
                qe = _swing((0, 0, -1), arm_w.inverted() @ d2)
                vals[a], vals[e] = qa, qe
            if "legs" in parts:
                lg, kn = ch.legs[idx], ch.knees[idx]
                d = _pos(M[S + "Leg"]) - _pos(M[S + "UpLeg"])
                ql = _swing((0, 0, -1), hips_w.inverted() @ d)
                leg_w = hips_w @ ql
                d2 = _pos(M[S + "Foot"]) - _pos(M[S + "Leg"])
                shin_l = (leg_w.inverted() @ d2).normalized()
                qk = _swing((0, 0, -1), shin_l)
                # twist around the shin so the boot toe points like the Mixamo foot
                toe = _pos(M[S + "ToeBase"]) - _pos(M[S + "Foot"])
                toe_l = leg_w.inverted() @ toe
                cur = qk @ Vector((0, -1, 0))
                toe_l -= shin_l * toe_l.dot(shin_l)
                cur -= shin_l * cur.dot(shin_l)
                if toe_l.length > 1e-4 and cur.length > 1e-4:
                    tw = cur.normalized().rotation_difference(toe_l.normalized())
                    qk = tw @ qk
                vals[lg], vals[kn] = ql, qk
                base = Vector(lg.location)
                for p in sole_pts:
                    feet.append((hips_w @ (base + ql @ (Vector(kn.location) + qk @ p))).z)
        # feet never sink into the ground (and optionally always touch it)
        if feet:
            low = loc.z + min(feet)
            if ground == "plant" or (ground == "clamp" and low < 0):
                loc.z -= low
        for o, q in vals.items():
            e = _q2e(q, prev.get(o))
            prev[o] = e
            key(o, "rotation_euler", fr, tuple(e))
        if "hips" in parts:
            key(ch.hips, "location", fr, tuple(loc))
        out[i] = fr
    return out


def rest(ch, fr, key_fn=None):
    """Key every driven pivot back to its rest pose at shot frame `fr` (arms keep the outward gap)."""
    from fod3d import key as _key
    key = key_fn or _key
    for o in (ch.hips, ch.torso, ch.head, *ch.legs, *ch.knees, *ch.elbows):
        key(o, "rotation_euler", fr, (0, 0, 0))
    for idx, side in enumerate((-1, 1)):
        key(ch.arms[idx], "rotation_euler", fr, (0, -side * getattr(ch, "arm_rest", 0.22), 0))
    key(ch.hips, "location", fr, (0, 0, 0.5))


def foot_world(ch, side_i, fr):
    """World position of a boot's toe at shot frame `fr` (for tying the ball path to the foot)."""
    sc = bpy.context.scene
    keep = sc.frame_current
    sc.frame_set(fr)
    kn = ch.knees[side_i]
    p = kn.matrix_world @ Vector((0, -0.12, -0.25))
    sc.frame_set(keep)
    return p
