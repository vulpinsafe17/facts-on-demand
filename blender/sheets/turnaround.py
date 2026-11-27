"""Turnaround sheet for a 3D character, laid out like the AI master sheets:
front / three-quarter / side / back on a ground line, 6 expression heads, a big face close-up.
  blender -b -P blender/sheets/turnaround.py -- --who main --out blender/out/sheet-main.png [--engine cycles|eevee] [--w 1920 --h 1080]
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy
import fod3d as k
import cast3d as c3

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(n, d=None):
    return argv[argv.index("--" + n) + 1] if "--" + n in argv else d

who = arg("who", "main")
W, H = int(arg("w", 1920)), int(arg("h", 1080))
sc = k.reset(2, W, H, arg("engine", "cycles"), int(arg("samples", 48)))
sc.render.use_freestyle = False          # owner: no outlines on the 3D characters
sc.render.use_motion_blur = False
w = bpy.data.worlds.new("paper"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (*k.hexrgb("#f4ede0"), 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.85
sun = k.sun(rot=(math.radians(40), 0, math.radians(-25)), energy=2.6, color=(1, 0.96, 0.9)); sun.data.angle = math.radians(25)
fill = bpy.data.lights.new("fill", "AREA"); fill.energy = 400; fill.size = 8
fo = bpy.data.objects.new("fill", fill); sc.collection.objects.link(fo); fo.location = (6, -10, 6); fo.rotation_euler = (math.radians(60), 0, math.radians(30))

# floor strip for the top row (catches the contact shadows) + the ground line like the sheets
floor = k.box("floor", (15, 3, 0.02), (0, 0.8, 2.79), k.mat("floor", "#f4ede0", 0.9))
k.box("groundline", (13.5, 0.02, 0.02), (0, -0.9, 2.8), k.mat("line", "#2a2420", 0.5))

for i, (x, rz) in enumerate(((-4.6, 0.0), (-1.7, 0.55), (1.2, math.pi / 2), (4.2, math.pi))):
    ch = c3.Character(who, (x, 0, 2.8), rz, name=f"{who}{i}")
    ch.root.scale = (1.45, 1.45, 1.45)

exprs = ["neutral", "happy", "sad", "surprised", "angry", "suspicious"]
for i, e in enumerate(exprs):
    x, z = (-5.0, -2.6, -0.2)[i % 3], (1.55, 0.05)[i // 3]
    holder = k.empty(f"eh{i}", (x, 0, z))
    holder.scale = (1.9, 1.9, 1.9)
    c3.build_head(f"{who}-e{i}", c3.SPECS[who], e, holder, loc=(0, 0, -c3.SKULL_Z))
big = k.empty("bigface", (4.0, 0, 0.75)); big.scale = (3.6, 3.6, 3.6)
c3.build_head(f"{who}-big", c3.SPECS[who], c3.SPECS[who]["default"], big, loc=(0, 0, -c3.SKULL_Z))

cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = 13.2
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam)
cam.location = (0, -30, 2.05); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
out = os.path.abspath(arg("out", f"blender/out/sheet-{who}.png"))
os.makedirs(os.path.dirname(out), exist_ok=True)
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("DONE", out)
