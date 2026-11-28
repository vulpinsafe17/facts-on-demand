"""CC0 model kits (Quaternius Medieval Village MegaKit, Standard/free) used as real building pieces.

Download once on the PC with make-download-kits.bat -> media/library/kits/medieval-village/glTF/*.gltf
Each piece is imported once into a hidden library collection; every placement is a linked copy
(shared mesh), so a whole street costs little memory.

Kit units: 1 wall module = 2 m wide, 3.12 m high. SCALE shrinks the kit to our cast (~1.4 m tall).
"""
import math
import os
import random

import bpy

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "media", "library", "kits"))
MV = os.path.join(ROOT, "medieval-village", "glTF")
SCALE = 0.72
MOD = 2.0            # wall module width (kit units)
STOREY = 3.12        # wall height (kit units)
WALL_OUT = 0.0       # kit walls already face their outside to -y (verified in test renders)

_lib = {}


def available():
    return os.path.isfile(os.path.join(MV, "Wall_Plaster_Straight.gltf"))


def _libcol():
    col = bpy.data.collections.get("KITLIB")
    if not col:
        col = bpy.data.collections.new("KITLIB")
        bpy.context.scene.collection.children.link(col)
        bpy.context.view_layer.layer_collection.children["KITLIB"].exclude = True
    return col


def load(name, kit=MV):
    """Import <name>.gltf once; returns a single joined mesh object kept out of the render."""
    ob = _lib.get(name)
    if ob is not None:
        try:
            if ob.name in bpy.data.objects:      # still alive (a new scene's reset() deletes everything)
                return ob
        except ReferenceError:
            pass
        _lib.clear()
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(kit, name + ".gltf"))
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    for o in meshes:                                   # bake parent transforms into the mesh
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for o in new:
        if o != ob and o.name in bpy.data.objects:
            bpy.data.objects.remove(o)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    _libcol().objects.link(ob)
    ob.name = "KIT_" + name
    _lib[name] = ob
    return ob


def place(name, loc=(0, 0, 0), rotz=0.0, parent=None, scale=1.0, mirror=False):
    src = load(name)
    o = src.copy()                                     # linked duplicate: shares the mesh
    o.name = name
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_mode = "XYZ"          # glTF imports use quaternions; euler would be ignored
    o.rotation_euler = (0, 0, rotz)
    o.scale = (-scale if mirror else scale, scale, scale)
    if parent:
        o.parent = parent
    return o


def _empty(name, loc, rotz, s):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    e.rotation_euler = (0, 0, rotz)
    e.scale = (s, s, s)
    return e


GROUND = ["Wall_UnevenBrick_Door_Flat", "Wall_UnevenBrick_Window_Wide_Flat", "Wall_UnevenBrick_Window_Wide_Round",
          "Wall_UnevenBrick_Window_Thin_Round", "Wall_UnevenBrick_Straight", "Wall_UnevenBrick_Door_Round"]
UPPER = ["Wall_Plaster_Window_Wide_Flat", "Wall_Plaster_Window_Wide_Round", "Wall_Plaster_Window_Thin_Round",
         "Wall_Plaster_WoodGrid", "Wall_Plaster_Window_Wide_Flat2", "Wall_Plaster_Straight"]


def house(name, loc, rotz, w=2, d=3, floors=2, seed=0, s=SCALE, chimney=True):
    """A gable-fronted house. Local frame: front (street side) faces -y, w modules wide (2 or 3), d deep.
    loc is the middle of the front wall at street level."""
    r = random.Random(seed)
    W, D = w * MOD, d * MOD
    root = _empty(name, loc, rotz, s)
    hold = _empty(name + "_c", (0, D / 2, 0), 0, 1.0)  # centre of the footprint
    hold.parent = root
    for f in range(floors):
        z = f * STOREY
        row = GROUND if f == 0 else UPPER
        for i in range(w):                                    # front
            x = -W / 2 + MOD / 2 + i * MOD
            is_door = f == 0 and i == (seed % w)
            pick = row[0] if is_door else row[1 + r.randrange(len(row) - 1)]
            place(pick, (x, -D / 2, z), WALL_OUT, hold)
            if is_door:
                place("Door_1_Flat", (x, -D / 2, z), WALL_OUT, hold)
            place(row[1 + r.randrange(len(row) - 1)] if f else row[4], (x, D / 2, z), WALL_OUT + math.pi, hold)
        for j in range(d):                                    # sides
            y = -D / 2 + MOD / 2 + j * MOD
            for sx in (-1, 1):
                pick = (row[4] if f == 0 else row[3 + r.randrange(3)])
                place(pick, (sx * W / 2, y, z), WALL_OUT + sx * math.pi / 2, hold)
        for cx in (-1, 1):
            for cy in (-1, 1):
                place("Corner_Exterior_Brick" if f == 0 else "Corner_Exterior_Wood", (cx * W / 2, cy * D / 2, z),
                      math.atan2(cy, cx) + math.pi * 3 / 4, hold)
    zt = floors * STOREY
    # dark inside so open windows read as rooms, not as holes to the sky
    bpy.ops.mesh.primitive_cube_add(size=1)
    core = bpy.context.active_object
    core.name = name + "_inside"
    core.scale = (W - 0.6, D - 0.6, zt - 0.1)
    core.location = (0, 0, zt / 2)
    core.parent = hold
    m = bpy.data.materials.get("kit_inside")
    if not m:
        m = bpy.data.materials.new("kit_inside")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.05, 0.035, 0.025, 1)
        b.inputs["Roughness"].default_value = 1.0
    core.data.materials.append(m)
    place(f"Roof_RoundTiles_{W:.0f}x{D:.0f}", (0, 0, zt), 0, hold)
    place(f"Roof_Front_Brick{W:.0f}", (0, -D / 2, zt), 0, hold)
    place(f"Roof_Front_Brick{W:.0f}", (0, D / 2, zt), math.pi, hold)
    if chimney and r.random() < 0.6:
        place("Prop_Chimney" if r.random() < 0.5 else "Prop_Chimney2", (W / 4 * (1 if r.random() < 0.5 else -1), D / 6, zt + 1.0), 0, hold)
    return root


def street(y0, y1, half, seed=3, gap=0.3, back_row=True):
    """Two facing rows of kit houses along the y axis. half = half street width (world m)."""
    rnd = random.Random(seed)
    out = []
    for side in (-1, 1):
        y = y0
        n = 0
        while y < y1:
            w = 2 if rnd.random() < 0.6 else 3
            fl = 2 if rnd.random() < 0.65 else 3
            ww = w * MOD * SCALE
            rz = -side * math.pi / 2               # front (-y local) faces the street
            out.append(house(f"kh{side}_{n}", (side * half, y + ww / 2, 0), rz, w, 3, fl, seed * 100 + n * 2 + (side > 0)))
            if back_row:
                out.append(house(f"kb{side}_{n}", (side * (half + 3 * MOD * SCALE + 1.2), y + ww / 2 + 0.4, 0), rz, w, 3,
                                 fl + (1 if rnd.random() < 0.4 else 0), seed * 100 + n * 2 + 51, chimney=False))
            y += ww + gap
            n += 1
    return out


def props(spots, seed=5):
    """Crates, wagons, fences at the given (x, y, rotz) spots."""
    rnd = random.Random(seed)
    for i, (x, y, rz) in enumerate(spots):
        k = rnd.choice(["Prop_Crate", "Prop_Crate", "Prop_Wagon", "Prop_WoodenFence_Single"])
        if k == "Prop_Wagon":                 # long side along the wall
            place(k, (x * 0.96, y, 0), 0, scale=SCALE)
        elif k == "Prop_WoodenFence_Single":
            place(k, (x * 1.03, y, 0), math.pi / 2, scale=SCALE)
        else:
            place(k, (x, y, 0), rz + rnd.uniform(-0.2, 0.2), scale=SCALE * rnd.uniform(0.75, 0.95))


def floor_tiles(x0, x1, y0, y1, name="Floor_Brick"):
    """Paves a rectangle with the kit's 2x2 floor tile."""
    step = MOD * SCALE
    x = x0
    while x < x1:
        y = y0
        while y < y1:
            place(name, (x + step / 2, y + step / 2, 0.0), 0, scale=SCALE)
            y += step
        x += step
