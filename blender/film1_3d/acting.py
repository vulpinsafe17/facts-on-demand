"""Acting vocabulary for cast3d characters. Times are seconds from the shot start.
Every action = anticipation -> action -> settle (PRODUCTION-RULES motion principles)."""
import math
import bpy
from fod3d import key

FPS = 30


def f(t):
    return int(round(t * FPS)) + 1


def _rest_arm(ch, side_i):
    side = -1 if side_i == 0 else 1
    return (0, -side * getattr(ch, "arm_rest", 0.22), 0)


def idle(ch, F, seed=0, blink=True):
    """Breathing, a slow weight shift, blinks every few seconds. Never a frozen figure."""
    for fr in range(1, F + 1, 20):
        ph = (fr + seed * 13) / 20.0
        key(ch.torso, "scale", fr, (1, 1, 1 + 0.012 * math.sin(ph)))
        key(ch.head, "rotation_euler", fr, (0.03 * math.sin(ph * 0.7), 0, 0.05 * math.sin(ph * 0.45 + seed)))
    if blink:
        t = 0.8 + (seed % 5) * 0.37
        while t * FPS < F - 6:
            _blink(ch, f(t))
            t += 2.6 + (seed % 3) * 0.6


def _eyes(ch):
    return [o for o in bpy.data.objects if o.name.startswith(ch.n + "-") and ("-eye" in o.name or "-glint" in o.name) and o.type == "MESH"]


def _blink(ch, fr):
    ch.face.blink(fr)


WORDS = []          # narrator word timings for the current shot (set by the renderer)
SHOT_START = 0.0


def talk(ch, t0, t1, gesture=True):
    """Lip-sync to the narration (one mouth, shape keys) + small head bobs + a hand gesture."""
    ch.face.talk(t0, t1, WORDS, SHOT_START)
    t, i = t0, 0
    while t < t1:
        key(ch.head, "rotation_euler", f(t), (0.04 * (1 if i % 2 else -1), 0, 0.035 * math.sin(i)))
        t += 0.45
        i += 1
    if gesture:
        a = ch.arms[1]
        key(a, "rotation_euler", f(t0), _rest_arm(ch, 1))
        key(a, "rotation_euler", f(t0 + 0.35), (-0.9, -0.5, 0))
        key(ch.elbows[1], "rotation_euler", f(t0 + 0.35), (-0.9, 0, 0))
        key(a, "rotation_euler", f(t0 + 0.8), (-0.7, -0.35, 0))
        key(a, "rotation_euler", f(min(t1, t0 + 1.6)), _rest_arm(ch, 1))
        key(ch.elbows[1], "rotation_euler", f(min(t1, t0 + 1.6)), (0, 0, 0))


def point(ch, t, hold=1.4, side=1, up=0.0):
    i = 0 if side < 0 else 1
    a, e = ch.arms[i], ch.elbows[i]
    key(a, "rotation_euler", f(t), _rest_arm(ch, i))
    key(a, "rotation_euler", f(t + 0.12), (0.3, side * 0.1, 0))          # anticipation: pull back
    key(a, "rotation_euler", f(t + 0.35), (-1.55 - up, -side * 0.15, 0))  # thrust, slight overshoot
    key(a, "rotation_euler", f(t + 0.5), (-1.4 - up, -side * 0.12, 0))
    key(e, "rotation_euler", f(t + 0.35), (0, 0, 0))
    key(ch.torso, "rotation_euler", f(t + 0.35), (0.08, 0, 0))
    key(a, "rotation_euler", f(t + hold), (-1.4 - up, -side * 0.12, 0))
    key(a, "rotation_euler", f(t + hold + 0.4), _rest_arm(ch, i))
    key(ch.torso, "rotation_euler", f(t + hold + 0.4), (0, 0, 0))


def cheer(ch, t0, t1, jump=True):
    for i, side in enumerate((-1, 1)):
        a = ch.arms[i]
        key(a, "rotation_euler", f(t0), _rest_arm(ch, i))
        key(a, "rotation_euler", f(t0 + 0.25), (0, -side * 2.7, 0))
        key(a, "rotation_euler", f(t1), (0, -side * 2.6, 0))
        key(a, "rotation_euler", f(t1 + 0.4), _rest_arm(ch, i))
    if jump:
        t = t0
        while t < t1:
            key(ch.hips, "location", f(t), (0, 0, 0.5))
            key(ch.hips, "location", f(t + 0.2), (0, 0, 0.72))
            key(ch.hips, "location", f(t + 0.4), (0, 0, 0.5))
            t += 0.5


def shrug(ch, t, hold=1.0):
    for i, side in enumerate((-1, 1)):
        a, e = ch.arms[i], ch.elbows[i]
        key(a, "rotation_euler", f(t), _rest_arm(ch, i))
        key(e, "rotation_euler", f(t), (0, 0, 0))
        key(a, "rotation_euler", f(t + 0.3), (-0.3, -side * 0.9, 0))
        key(e, "rotation_euler", f(t + 0.3), (-1.4, 0, 0))
        key(a, "rotation_euler", f(t + 0.3 + hold), (-0.3, -side * 0.9, 0))
        key(a, "rotation_euler", f(t + 0.7 + hold), _rest_arm(ch, i))
        key(e, "rotation_euler", f(t + 0.7 + hold), (0, 0, 0))
    key(ch.head, "rotation_euler", f(t + 0.3), (0, 0.25, 0))
    key(ch.head, "rotation_euler", f(t + 0.7 + hold), (0, 0, 0))
    key(ch.hips, "location", f(t + 0.3), (0, 0, 0.53))
    key(ch.hips, "location", f(t + 0.7 + hold), (0, 0, 0.5))


def walk(ch, t0, t1, to, run=False):
    """Move the root to `to`, facing the direction of travel, legs/arms swinging."""
    start = tuple(ch.root.location)
    dx, dy = to[0] - start[0], to[1] - start[1]
    rz = math.atan2(dx, -dy)
    key(ch.root, "location", f(t0), start)
    key(ch.root, "rotation_euler", f(t0), tuple(ch.root.rotation_euler))
    key(ch.root, "rotation_euler", f(t0 + 0.15), (0, 0, rz))
    key(ch.root, "location", f(t1), (to[0], to[1], 0))
    step = 0.28 if run else 0.4
    amp = 0.8 if run else 0.5
    t = t0
    n = 0
    while t <= t1:
        s = math.sin(n * math.pi / 2)
        key(ch.legs[0], "rotation_euler", f(t), (s * amp, 0, 0))
        key(ch.legs[1], "rotation_euler", f(t), (-s * amp, 0, 0))
        key(ch.knees[0], "rotation_euler", f(t), (-max(0, -s) * amp * 0.9, 0, 0))
        key(ch.knees[1], "rotation_euler", f(t), (-max(0, s) * amp * 0.9, 0, 0))
        ar = getattr(ch, "arm_rest", 0.22)
        key(ch.arms[0], "rotation_euler", f(t), (-s * amp * 1.1, ar, 0))
        key(ch.arms[1], "rotation_euler", f(t), (s * amp * 1.1, -ar, 0))
        key(ch.hips, "location", f(t), (0, 0, 0.5 + (0.035 if n % 2 else 0) + (0.04 if run else 0)))
        t += step / 2
        n += 1
    for i, p in enumerate(ch.legs + ch.knees):
        key(p, "rotation_euler", f(t1 + 0.15), (0, 0, 0))
    for i in range(2):
        key(ch.arms[i], "rotation_euler", f(t1 + 0.2), _rest_arm(ch, i))
    key(ch.hips, "location", f(t1 + 0.15), (0, 0, 0.5))


def turn(ch, t, rz, dur=0.35):
    key(ch.root, "rotation_euler", f(t), tuple(ch.root.rotation_euler))
    key(ch.root, "rotation_euler", f(t + dur), (0, 0, rz))


def kick(ch, t, leg=1):
    lg, kn = ch.legs[leg], ch.knees[leg]
    key(lg, "rotation_euler", f(t - 0.35), (0, 0, 0))
    key(lg, "rotation_euler", f(t - 0.12), (0.7, 0, 0))     # wind up
    key(kn, "rotation_euler", f(t - 0.12), (-1.0, 0, 0))
    key(lg, "rotation_euler", f(t), (-1.0, 0, 0))           # strike
    key(kn, "rotation_euler", f(t), (0, 0, 0))
    key(lg, "rotation_euler", f(t + 0.3), (-0.6, 0, 0))     # follow-through
    key(lg, "rotation_euler", f(t + 0.6), (0, 0, 0))
    key(ch.torso, "rotation_euler", f(t - 0.12), (-0.12, 0, 0))
    key(ch.torso, "rotation_euler", f(t), (0.15, 0, 0))
    key(ch.torso, "rotation_euler", f(t + 0.6), (0, 0, 0))
    key(ch.arms[0], "rotation_euler", f(t), (-0.6, 0.5, 0))
    key(ch.arms[0], "rotation_euler", f(t + 0.6), _rest_arm(ch, 0))


def bow(ch, t, hold=0.8):
    key(ch.torso, "rotation_euler", f(t), (0, 0, 0))
    key(ch.torso, "rotation_euler", f(t + 0.4), (0.55, 0, 0))
    key(ch.torso, "rotation_euler", f(t + 0.4 + hold), (0.55, 0, 0))
    key(ch.torso, "rotation_euler", f(t + 0.9 + hold), (0, 0, 0))


def jump(ch, t, h=0.5):
    z0 = ch.root.location.z
    loc = tuple(ch.root.location)
    key(ch.hips, "location", f(t - 0.15), (0, 0, 0.5))
    key(ch.hips, "location", f(t - 0.05), (0, 0, 0.42))       # crouch
    key(ch.root, "location", f(t - 0.05), loc)
    key(ch.root, "location", f(t + 0.3), (loc[0], loc[1], z0 + h))
    key(ch.root, "location", f(t + 0.6), loc)
    key(ch.hips, "location", f(t + 0.65), (0, 0, 0.44))
    key(ch.hips, "location", f(t + 0.8), (0, 0, 0.5))


def write(ch, t0, t1):
    a, e = ch.arms[1], ch.elbows[1]
    key(a, "rotation_euler", f(t0), (-1.0, -0.1, 0))
    key(e, "rotation_euler", f(t0), (-0.9, 0, 0))
    t = t0
    i = 0
    while t < t1:
        key(a, "rotation_euler", f(t), (-1.0 + (0.08 if i % 2 else 0), -0.1 - (0.06 if i % 3 else 0), 0))
        t += 0.2
        i += 1
    key(ch.torso, "rotation_euler", f(t0), (0.25, 0, 0))
    key(ch.head, "rotation_euler", f(t0), (0.3, 0, 0))


def angry(ch, t0, t1):
    """Stomping, fists on hips."""
    for i, side in enumerate((-1, 1)):
        key(ch.arms[i], "rotation_euler", f(t0), (0.3, -side * 0.6, 0))
        key(ch.elbows[i], "rotation_euler", f(t0), (-1.8, 0, 0))
        key(ch.arms[i], "rotation_euler", f(t1), (0.3, -side * 0.6, 0))
        key(ch.arms[i], "rotation_euler", f(t1 + 0.4), _rest_arm(ch, i))
        key(ch.elbows[i], "rotation_euler", f(t1 + 0.4), (0, 0, 0))
    t = t0
    n = 0
    while t < t1:
        key(ch.legs[n % 2], "rotation_euler", f(t), (-0.5, 0, 0))
        key(ch.legs[n % 2], "rotation_euler", f(t + 0.15), (0, 0, 0))
        t += 0.4
        n += 1


def cover_ears(ch, t0, t1):
    for i, side in enumerate((-1, 1)):
        key(ch.arms[i], "rotation_euler", f(t0), _rest_arm(ch, i))
        key(ch.arms[i], "rotation_euler", f(t0 + 0.3), (0, -side * 2.2, 0))
        key(ch.elbows[i], "rotation_euler", f(t0 + 0.3), (0, 0, side * 0.0))
        key(ch.elbows[i], "rotation_euler", f(t0 + 0.3), (0, side * 1.3, 0))
        key(ch.arms[i], "rotation_euler", f(t1), (0, -side * 2.2, 0))
    t = t0 + 0.3
    while t < t1:
        key(ch.head, "rotation_euler", f(t), (0, 0.15, 0))
        key(ch.head, "rotation_euler", f(t + 0.2), (0, -0.15, 0))
        t += 0.4


def hold_up(ch, t, side=1):
    """Raise one hand high (holding a decree / reading)."""
    i = 0 if side < 0 else 1
    key(ch.arms[i], "rotation_euler", f(t), _rest_arm(ch, i))
    key(ch.arms[i], "rotation_euler", f(t + 0.35), (-1.2, -side * 0.6, 0))
    key(ch.elbows[i], "rotation_euler", f(t + 0.35), (-0.6, 0, 0))


def throw(ch, t):
    a, e = ch.arms[1], ch.elbows[1]
    key(a, "rotation_euler", f(t - 0.3), _rest_arm(ch, 1))
    key(a, "rotation_euler", f(t - 0.1), (0.9, -0.3, 0))
    key(e, "rotation_euler", f(t - 0.1), (-1.2, 0, 0))
    key(a, "rotation_euler", f(t + 0.1), (-1.8, -0.3, 0))
    key(e, "rotation_euler", f(t + 0.1), (0, 0, 0))
    key(a, "rotation_euler", f(t + 0.6), _rest_arm(ch, 1))


def look(ch, t, yaw=0.0, pitch=0.0):
    key(ch.head, "rotation_euler", f(t), tuple(ch.head.rotation_euler))
    key(ch.head, "rotation_euler", f(t + 0.3), (pitch, 0, yaw))


def path(obj, pts, spin=None):
    """Keyframe an object (ball) through [(t, (x,y,z)), ...]."""
    for t, p in pts:
        key(obj, "location", f(t), p)
    if spin:
        key(obj, "rotation_euler", f(pts[0][0]), (0, 0, 0))
        key(obj, "rotation_euler", f(pts[-1][0]), spin)


ACTS = {"talk": talk, "point": point, "cheer": cheer, "shrug": shrug, "walk": walk, "turn": turn, "kick": kick, "bow": bow,
        "jump": jump, "write": write, "angry": angry, "ears": cover_ears, "holdup": hold_up, "throw": throw, "look": look}
