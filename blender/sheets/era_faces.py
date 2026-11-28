"""Era faces check: every main character in every era that has an approved 2D era sheet, upper body, one row each.
  python blender/sheets/era_faces.py -- --out blender/out/sheets/era-faces.png   (pip bpy, or blender -b -P)"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy
import fod3d as k
import cast3d as c3

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = os.path.abspath(argv[argv.index("--out") + 1] if "--out" in argv else "blender/out/sheets/era-faces.png")
ROWS = [("main", [("han", None), ("greek", None), ("heian", None), ("medieval", None), ("victorian", None)]),
        ("two", [("han", None), ("greek", None), ("heian", None), ("medieval", None), ("victorian", None)]),
        ("king", [(None, "edward"), (None, "gaozu"), (None, "hongwu")])]
sc = k.reset(2, 2000, 1500, "cycles", 24)
sc.cycles.device = "CPU"
sc.render.use_freestyle = False      # owner: no outlines on the 3D characters
w = bpy.data.worlds.new("paper"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (*k.hexrgb("#f4ede0"), 1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.85
sun = k.sun(rot=(math.radians(40), 0, math.radians(-25)), energy=2.6, color=(1, 0.96, 0.9))
for r, (who, eras) in enumerate(ROWS):
    for i, (era, king) in enumerate(eras):
        c3.Character(who, (-4.4 + i * 2.2, 0, -r * 2.6), 0.2, name=f"{who}{i}", era=era, king=king)
cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"; cd.ortho_scale = 11.6
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam)
cam.location = (0, -30, -1.35); cam.rotation_euler = (math.radians(90), 0, 0); sc.camera = cam
os.makedirs(os.path.dirname(out), exist_ok=True)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("DONE", out)
