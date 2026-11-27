"""3D demo (10 s): medieval London street (c. 1314, the year Edward II banned football in the
city), mob football. Built and animated 100 % in code.  v2: better figures + full background.
  blender -b -P blender/scenes/london_demo.py -- --out blender/out/london_demo_v2.mp4 [--engine eevee|cycles]
        [--samples 96] [--frames 300] [--w 1920 --h 1080] [--stills 30,120]
"""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy
import fod3d as k
from fod3d import hexrgb, mat, box, ball, cyl, cone, ico, prism_roof, key, sec

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(n, d=None):
    return argv[argv.index("--" + n) + 1] if "--" + n in argv else d

FRAMES = int(arg("frames", 300))
sc = k.reset(FRAMES, int(arg("w", 1920)), int(arg("h", 1080)), arg("engine", "eevee"),
             int(arg("samples")) if arg("samples") else None)
k.world_sky()
k.sun()
k.post()
rnd = random.Random(7)  # fixed seed: the same city every render

# ------------------------------------------------------------------ ground
cobble = k.mat_pattern("cobble", "#b89c72", "#6a5236", "cobble", scale=2.4, bump=0.5)
box("street", (9.2, 92, 0.2), (0, 36, -0.1), cobble)
box("cityground", (70, 100, 0.2), (0, 36, -0.12), mat("dirt", "#9a8262", noise=0.15, nscale=0.3))
meadow = mat("meadow", "#93ad5c", noise=0.18, nscale=0.08)
box("meadow", (600, 600, 0.2), (0, 150, -0.16), meadow)
box("gutter", (0.35, 92, 0.03), (0, 36, 0.005), mat("gutter", "#6e5a42", noise=0.2, nscale=3))

# ------------------------------------------------------------------ the street (hero houses)
plaster = ("#f1dca8", "#efd59a", "#f4e3bb", "#e9cf94", "#f0e6cf")
timber = mat("timber", "#5a3a22", noise=0.15, nscale=6)
roofs = [k.mat_pattern(f"roof{i}", c, "#5a2a18", "tiles", scale=9, bump=0.3)
         for i, c in enumerate(("#b2452c", "#9c3a26", "#c56a3a", "#8b6a3e"))]
win = mat("window", "#3b4a52", 0.25)
shutter = mat("shutter", "#5f7a5a", noise=0.1, nscale=5)
door = k.mat_pattern("door", "#6a4426", "#3a2414", "planks", scale=12, bump=0.2)
awn = [mat(f"awn{i}", c, noise=0.08, nscale=5) for i, c in enumerate(("#c4462f", "#3f7a52", "#d9a33a", "#f4ecd8"))]
fruit = [mat(f"fruit{j}", c, 0.5) for j, c in enumerate(("#e0802a", "#c33a2a", "#7da13a", "#e8c33a"))]
stone = mat("stone", "#c9bfae", noise=0.12, nscale=2, bump=0.2)
slate = mat("slate", "#6c6a72", noise=0.1, nscale=4)
chim = mat("chimney", "#9a6a52", noise=0.15, nscale=5)


def house(x, y, w, d, floors, side, seed):
    r = random.Random(seed)
    h = floors * 1.6
    m = mat(f"plaster{seed % 5}", plaster[seed % 5], noise=0.1, nscale=1.5, bump=0.15)
    front = lambda f: x + f * 0.25 * -side - side * (w / 2 + 0.01)   # street-facing x of floor f
    for f in range(floors):  # upper floors jut out over the street (jetties)
        jut = f * 0.25 * -side
        box(f"h{seed}f{f}", (w, d, 1.6), (x + jut, y, 0.8 + f * 1.6), m)
        for b in (-1, 0, 1):  # timber posts + beam
            box(f"h{seed}f{f}b{b}", (0.14, 0.14, 1.6), (front(f), y + b * d * 0.46, 0.8 + f * 1.6), timber)
        box(f"h{seed}f{f}r", (0.14, d + 0.02, 0.12), (front(f), y, 1.55 + f * 1.6), timber)
        if f > 0:  # cross brace
            box(f"h{seed}f{f}x", (0.1, 0.1, 1.5), (front(f), y + d * 0.23, 0.8 + f * 1.6), timber, rot=(0.6, 0, 0))
        for wv in (-1, 1):
            if f == 0 and wv == 1:
                box(f"h{seed}door", (0.1, 0.8, 1.25), (front(0) - side * 0.02, y + d * 0.22, 0.62), door)
                continue
            wy = y + wv * d * 0.22
            box(f"h{seed}f{f}w{wv}", (0.08, 0.55, 0.65), (front(f) - side * 0.02, wy, 0.95 + f * 1.6), win)
            box(f"h{seed}f{f}s{wv}", (0.06, 0.22, 0.7), (front(f) - side * 0.04, wy - 0.4, 0.95 + f * 1.6), shutter)
    rh = 1.4 + r.random() * 0.6
    rx = x + (floors - 1) * 0.25 * -side
    prism_roof(f"h{seed}roof", d + 0.4, w + 0.6, rh, (rx, y, h), roofs[seed % 4], rotz=math.pi / 2)
    if r.random() < 0.6:
        box(f"h{seed}ch", (0.4, 0.4, 1.4), (rx + side * 0.6, y + 0.6, h + rh * 0.6), chim)
    if r.random() < 0.6:  # market stall with a striped awning
        sx = x - side * (w / 2 + 0.6)
        box(f"h{seed}aw", (1.3, d * 0.8, 0.06), (sx, y, 2.0), awn[seed % 4], rot=(0, side * 0.35, 0))
        box(f"h{seed}tb", (1.0, d * 0.7, 0.1), (sx, y, 0.85), timber)
        for lg in (-1, 1):
            box(f"h{seed}lg{lg}", (0.08, 0.08, 0.8), (sx, y + lg * d * 0.3, 0.4), timber)
        for j in range(6):
            ball(f"h{seed}fr{j}", 0.11, (sx + (j % 2) * 0.2 - 0.1, y - d * 0.25 + (j // 2) * d * 0.25, 1.0), fruit[(seed + j) % 4])


y = -2.0
for i in range(14):
    for side in (-1, 1):
        w = 2.4 + rnd.random() * 0.6
        house(side * (4.6 + w / 2), y + (0.3 if side > 0 else 0), w, 3.0, 2 + (i % 2), side, i * 2 + (side > 0))
    y += 3.1
for i in range(14):  # barrels
    side = -1 if i % 2 else 1
    cyl(f"barrel{i}", 0.32, 0.8, (side * (3.3 + rnd.random() * 0.4), i * 2.6 - 1, 0.4), mat("barrel", "#7a5230", noise=0.15, nscale=8), verts=14)

# ------------------------------------------------------------------ the city behind: rooftops to the horizon
def simple_house(name, x, y, w, d, h, rseed):
    r = random.Random(rseed)
    box(name, (w, d, h), (x, y, h / 2), mat(f"plaster{rseed % 5}", plaster[rseed % 5], noise=0.1, nscale=1.5, bump=0.15))
    prism_roof(name + "r", w + 0.3, d + 0.3, 1.2 + r.random() * 0.8, (x, y, h), roofs[rseed % 4], rotz=(0 if r.random() < 0.5 else math.pi / 2))
    if r.random() < 0.35:
        box(name + "c", (0.35, 0.35, 1.2), (x + w * 0.25, y, h + 1.0), chim)


n = 0
for gy in range(-3, 24):       # blocks either side, behind the hero houses
    for gx in range(5):
        for side in (-1, 1):
            if rnd.random() < 0.15:
                continue  # an alley / yard
            x = side * (9.2 + gx * 3.6 + rnd.random() * 0.6)
            yy = gy * 3.5 + rnd.random() * 0.8
            simple_house(f"bh{n}", x, yy, 2.8 + rnd.random() * 0.6, 3.0, 2.6 + rnd.random() * 2.4, n); n += 1
for gy in range(13, 24):       # beyond the end of the street, around the cathedral
    for gx in range(-2, 3):
        x, yy = gx * 3.6 + rnd.random() * 0.6, 42 + (gy - 13) * 3.6
        if yy < 52 or (abs(x) < 15 and yy < 74):
            continue  # the plaza + cathedral close
        simple_house(f"eh{n}", x, yy, 2.8, 3.0, 2.6 + rnd.random() * 2.4, n); n += 1

# Old St Paul's, seen side-on across the plaza: long nave, crossing tower, very tall spire
stone = mat("stone2", "#c8b79a", noise=0.15, nscale=0.6, bump=0.2)
box("nave", (26, 7, 9), (0, 64, 4.5), stone)
prism_roof("naveroof", 26.4, 7.4, 3.6, (0, 64, 9), slate)
box("transept", (7, 16, 8), (2, 64, 4), stone)
prism_roof("transroof", 7.4, 16.4, 3.2, (2, 64, 8), slate, rotz=math.pi / 2)
box("tower", (5, 5, 17), (2, 64, 8.5), stone)
for cx in (-1, 1):
    for cy in (-1, 1):
        cone(f"pinn{cx}{cy}", 0.4, 2.4, (2 + cx * 2.3, 64 + cy * 2.3, 18.2), slate, verts=6)
cone("spire", 2.6, 26, (0 + 2, 64, 30), slate, verts=8)
for wx in range(-5, 6):
    if abs(wx * 2.3 - 2) < 3.5:
        continue
    box(f"navewin{wx}", (0.9, 7.1, 3.4), (wx * 2.3, 64, 5.2), win)
    box(f"buttress{wx}", (0.6, 8.2, 6), (wx * 2.3 + 1.15, 64, 3), stone)
box("southdoor", (2.2, 7.2, 3.6), (2, 64, 1.8), door)
box("plaza", (30, 20, 0.04), (0, 54, 0.01), k.mat_pattern("flag", "#b8a68a", "#6a5a44", "cobble", scale=0.9, bump=0.3))
cyl("well", 1.2, 0.9, (-6, 52, 0.45), stone, verts=12)  # the plaza well

# city wall with towers, then meadows, trees and hills to the horizon
wallm = mat("wall", "#b8ad98", noise=0.15, nscale=1, bump=0.2)
box("citywall", (70, 1.6, 6), (0, 86, 3), wallm)
for i in range(-4, 5):
    cyl(f"wt{i}", 2.0, 9, (i * 8, 86, 4.5), wallm, verts=10)
    cone(f"wtr{i}", 2.4, 3.5, (i * 8, 86, 10.7), roofs[i % 4], verts=10)
for side in (-1, 1):
    box(f"sidewall{side}", (1.6, 100, 6), (side * 34, 36, 3), wallm)
leaf = [mat(f"leaf{i}", c, noise=0.12, nscale=3) for i, c in enumerate(("#5f8a3c", "#6f9a44", "#4f7a36"))]
bark = mat("bark", "#5a3e2a")
for i in range(120):
    a = rnd.uniform(-1.2, 1.2) + (0 if rnd.random() < 0.7 else math.pi)
    dist = rnd.uniform(62, 150)
    tx, ty = math.sin(a) * dist, 36 + math.cos(a) * dist
    if abs(tx) < 36 and -15 < ty < 88:
        continue
    s_ = rnd.uniform(1.6, 3.2)
    cyl(f"trunk{i}", 0.25 * s_, 2 * s_, (tx, ty, s_), bark, verts=6)
    ico(f"tree{i}", 1.4 * s_, (tx, ty, 2.6 * s_), leaf[i % 3], scale=(1, 1, 1.15))
hill = [mat(f"hill{i}", c, noise=0.15, nscale=0.05) for i, c in enumerate(("#86a457", "#7c9a52", "#94b064"))]
for i in range(16):
    a = -1.4 + i * 0.19
    dist = 190 + rnd.uniform(0, 60)
    ico(f"hillb{i}", 60 + rnd.uniform(0, 40), (math.sin(a) * dist, 36 + math.cos(a) * dist, -30), hill[i % 3],
        scale=(1.4, 1, 0.55), sub=2)
for i in range(12):  # hills behind the camera side as well (the camera rises at the end)
    a = math.pi - 1.0 + i * 0.18
    ico(f"hillf{i}", 70, (math.sin(a) * 220, 36 + math.cos(a) * 220, -30), hill[i % 3], scale=(1.4, 1, 0.5), sub=2)

# drifting clouds (no outlines, soft)
cloudm = mat("cloud", (1, 0.98, 0.95), 1.0, emit=0.25)
for i in range(9):
    c = k.empty(f"cloud{i}", (-60 + i * 15 + rnd.uniform(-4, 4), 90 + rnd.uniform(0, 60), 28 + rnd.random() * 10))
    for j in range(6):
        ball(f"cl{i}{j}", 3.0 + rnd.random() * 2.2, (j * 3.2 - 8, rnd.uniform(-1.5, 1.5), rnd.random() * 1.6), cloudm, c, scale=(1, 0.6, 0.65), seg=16)
    key(c, "location", 1, c.location.copy())
    key(c, "location", FRAMES, (c.location.x + 6, c.location.y, c.location.z))
    k.nolines(c)
# dust motes floating in the sunlight (no outlines)
mote = mat("mote", "#fff3d6", 0.5, emit=1.5)
for i in range(40):
    x0, y0, z0 = rnd.uniform(-3.5, 3.5), rnd.uniform(-2, 12), rnd.uniform(0.3, 3.5)
    p = ball(f"mote{i}", 0.008, (x0, y0, z0), mote, seg=8)
    key(p, "location", 1, (x0, y0, z0))
    key(p, "location", FRAMES, (x0 + rnd.uniform(0.3, 0.9), y0 + rnd.uniform(-0.3, 0.3), z0 + rnd.uniform(0.2, 0.6)))
    k.nolines(p)
# birds circling the spire
birdm = mat("bird", "#3a3030")
for i in range(4):
    b = k.empty(f"bird{i}", (2, 64, 30))
    for side in (-1, 1):
        wng = box(f"wing{i}{side}", (0.9, 0.28, 0.05), (side * 0.45, 0, 0), birdm, b)
        for f in range(1, FRAMES + 1, 6):
            key(wng, "rotation_euler", f, (0, side * (0.5 if (f // 6) % 2 else -0.3), 0))
    R, ph = 9 + i * 2.5, i * 1.6
    for f in range(1, FRAMES + 1, 10):
        t = ph + f / FRAMES * 2.2
        key(b, "location", f, (2 + math.cos(t) * R, 64 + math.sin(t) * R, 30 + i * 1.5 + math.sin(t * 2)))
        key(b, "rotation_euler", f, (0, 0, t + math.pi / 2))
    k.nolines(b)

# NPCs: the street is alive (free-looking extras, no team scarf)
npcs = [
    (k.npc("#8a4a3a", hat="coif", skin="#f4dcc4"), (4.05, 6.6, 0), -math.pi / 2, None),           # stall woman
    (k.npc("#4a5a7a", hair="#7a5a3a", beard="#7a5a3a"), (-4.0, 9.8, 0), math.pi / 2, None),        # stall man
    (k.npc("#6a7a4a", hat="hood"), None, None, ((1.8, 22, 0), (1.4, 10, 0), 1, 300)),             # walks towards us
    (k.npc("#9a7a4a", hat="cap", hair="#2a1a10"), None, None, ((-2.0, 7.5, 0), (-2.4, 21, 0), 1, 300)),  # walks away
    (k.npc("#7a3a5a", hat="coif", skin="#e8c8a8", body=0.27), None, None, ((-1.2, 26, 0), (2.2, 15, 0), 30, 300)),
    (k.npc("#5a6a6a", hair="#3a2a1e"), (2.8, 13.5, 0), -2.6, None),                               # idle onlooker
]
for i, (spec, loc, rz, wk) in enumerate(npcs):
    f = k.Figure("npc", loc or wk[0], name=f"npc{i}", spec=spec)
    if wk:
        f.walk(wk[2], wk[3], wk[0], wk[1], step=9)
    else:
        f.root.rotation_euler = (0, 0, rz)
        f.blink(40 + i * 37); f.blink(190 + i * 23)
        if i == 0:
            f.talk(sec(1.0), sec(2.6)); f.talk(sec(6), sec(7.5))

# ------------------------------------------------------------------ cast + ball
main = k.Figure("main", (-1.2, 2.0, 0))
two = k.Figure("two", (1.6, 3.2, 0))
two.root.rotation_euler = (0, 0, math.radians(-65))
leather = mat("leather", hexrgb("#8a5a2e"), 0.7)
fb = ball("football", 0.22, (-0.4, 2.6, 0.22), leather, seg=20)
cyl("seam", 0.222, 0.03, (0, 0, 0), mat("seam", hexrgb("#3a2414")), fb, rot=(0, math.pi / 2, 0), verts=20)

# 0-2.5 s: main strolls in   2.6-3.1: kick   3.1-4.0: ball flies, BONK on two's head
main.walk(sec(0.3), sec(2.4), (-3.5, 0.6, 0), (-0.9, 2.4, 0))
kick = sec(2.9)
main.at(sec(2.4), rotz=main.root.rotation_euler.z)
main.at(sec(2.6), rotz=1.1)
key(main.legs[1], "rotation_euler", sec(2.5), (0, 0, 0))
key(main.legs[1], "rotation_euler", sec(2.75), (0.9, 0, 0))     # wind up (leg back)
key(main.legs[1], "rotation_euler", kick, (-1.2, 0, 0))         # strike
key(main.legs[1], "rotation_euler", sec(3.3), (0, 0, 0))
key(main.torso, "rotation_euler", sec(2.75), (-0.15, 0, 0))
key(main.torso, "rotation_euler", kick, (0.2, 0, 0))
key(main.torso, "rotation_euler", sec(3.4), (0, 0, 0))
key(fb, "location", sec(0), (-0.5, 2.7, 0.22))
key(fb, "location", kick, (-0.5, 2.7, 0.22))
bonk = sec(3.7)
key(fb, "location", sec(3.3), (0.5, 3.0, 2.6))
key(fb, "location", bonk, (1.58, 3.2, 2.45))                     # top of two's head
key(fb, "location", sec(4.2), (2.6, 3.6, 2.9))
key(fb, "location", sec(4.8), (3.6, 4.6, 0.22))
key(fb, "rotation_euler", kick, (0, 0, 0))
key(fb, "rotation_euler", sec(4.8), (14, 3, 0))
# two: hit on the head -> squash, stagger, angry brows, blink
key(two.head, "scale", bonk - 1, (1, 1, 1))
key(two.head, "scale", bonk + 1, (1.15, 1.15, 0.78))
key(two.head, "scale", bonk + 6, (0.95, 0.95, 1.08))
key(two.head, "scale", bonk + 10, (1, 1, 1))
key(two.root, "rotation_euler", bonk, (0, 0, math.radians(-65)))
key(two.root, "rotation_euler", sec(4.6), (0, 0, math.radians(-25)))   # turns to glare at us
key(two.torso, "rotation_euler", bonk + 2, (0.25, 0, 0))
key(two.torso, "rotation_euler", sec(4.4), (0, 0, 0))
two.brows_angry(sec(4.3))
two.blink(sec(5.6))
two.blink(sec(7.9))
two.talk(sec(6.0), sec(7.4))
for a, s in ((two.arms[0], -1), (two.arms[1], 1)):          # hands on hips in anger
    key(a, "rotation_euler", sec(4.6), (0, s * 0.2, 0))
    key(a, "rotation_euler", sec(5.0), (0.2, s * 0.9, 0))
# main: laughs (bounces), then the sheepish shrug
for i in range(8):
    f = sec(3.8) + i * 5
    key(main.hips, "location", f, (0, 0, 0.72 + (0.06 if i % 2 else 0)))
main.blink(sec(6.6))
key(main.arms[0], "rotation_euler", sec(7.2), (0, -0.2, 0))
key(main.arms[1], "rotation_euler", sec(7.2), (0, 0.2, 0))
key(main.arms[0], "rotation_euler", sec(7.6), (0, -1.3, 0))
key(main.arms[1], "rotation_euler", sec(7.6), (0, 1.3, 0))
key(main.head, "rotation_euler", sec(7.6), (0, 0.25, 0))

# dust puffs at the kick and where the ball lands
dust = mat("dust", "#d9c39c", 1.0, emit=0.2)
for (cx, cy, f0) in ((-0.5, 2.6, kick), (3.6, 4.6, sec(4.8))):
    for j in range(6):
        a = j / 6 * math.tau
        p = ball(f"dust{f0}{j}", 0.12, (cx, cy, 0.1), dust)
        key(p, "scale", f0 - 1, (0.01, 0.01, 0.01))
        key(p, "scale", f0 + 4, (1.6, 1.6, 1.2))
        key(p, "scale", f0 + 16, (0.01, 0.01, 0.01))
        key(p, "location", f0 - 1, (cx, cy, 0.1))
        key(p, "location", f0 + 16, (cx + math.cos(a) * 0.7, cy + math.sin(a) * 0.4, 0.45))
        k.nolines(p)

# ------------------------------------------------------------------ camera: never still
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 35
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 2.8
cam = bpy.data.objects.new("cam", cam_d)
bpy.context.collection.objects.link(cam)
sc.camera = cam
target = k.empty("cam-target", (0, 8, 2))
tr = cam.constraints.new("TRACK_TO"); tr.target = target; tr.track_axis = "TRACK_NEGATIVE_Z"; tr.up_axis = "UP_Y"
cam_d.dof.focus_object = target
# 0-2.4: fly in from above the roofs down to street level, following main
key(cam, "location", sec(0), (0.5, -9, 9))
key(target, "location", sec(0), (0, 14, 3))
key(cam, "location", sec(2.4), (-1.5, -3.2, 1.8))
key(target, "location", sec(2.4), (-0.6, 2.4, 1.0))
# kick + ball flight: whip pan to two
key(cam, "location", sec(3.2), (-0.5, -2.6, 1.8))
key(target, "location", sec(3.2), (0.6, 2.9, 1.6))
key(target, "location", sec(3.8), (1.5, 3.2, 1.7))
# reaction: push into two's angry face
key(cam, "location", sec(4.6), (0.4, 0.4, 1.6))
key(cam, "location", sec(6.8), (1.0, 1.4, 1.75))
key(target, "location", sec(6.8), (1.6, 3.2, 1.75))
# pull back to main's shrug, then rise up as the scene ends
key(cam, "location", sec(7.2), (-0.6, -0.8, 1.6))
key(target, "location", sec(7.4), (-0.9, 2.4, 1.45))
key(cam, "location", sec(10), (-2.5, -4.5, 3.6))
key(target, "location", sec(10), (0, 4, 1.6))

# ------------------------------------------------------------------ render
out = os.path.abspath(arg("out", "blender/out/london_demo_v2.mp4"))
if arg("stills"):
    sc.render.image_settings.file_format = "PNG"
    for f in [int(x) for x in arg("stills").split(",")]:
        sc.frame_set(f)
        sc.render.filepath = out.replace(".mp4", f"_f{f:04d}.png")
        bpy.ops.render.render(write_still=True)
else:
    k.render_mp4(out)
print("DONE", out)
