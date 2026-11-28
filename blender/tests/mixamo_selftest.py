"""Self-test for blender/mixamo3d.py without real Mixamo files.
Builds a Mixamo-named T-pose skeleton, animates a wave (left arm) and a kick (right leg), exports it as FBX
(like a Mixamo download), imports it back through mixamo3d.load and drives the main character with it.
Checks: feet never below the ground, hanging arms keep a gap, the raised arm really goes up, the kick swings
the leg forward. Renders a few stills to blender/out/mixamo-test/ to look at.

    blender -b -P blender/tests/mixamo_selftest.py          (or: python blender/tests/mixamo_selftest.py with pip bpy)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE), os.path.join(os.path.dirname(HERE), "film1_3d")]
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import fod3d  # noqa: E402
import cast3d  # noqa: E402
import mixamo3d  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "out", "mixamo-test")
os.makedirs(OUT, exist_ok=True)
FBX = os.path.join(OUT, "fake-wave-kick.fbx")

J = {  # joint heads (m), character faces -Y, its LEFT is +X
    "Hips": (0, 0, 1.0), "Spine": (0, 0, 1.1), "Spine1": (0, 0, 1.2), "Spine2": (0, 0, 1.3),
    "Neck": (0, 0, 1.45), "Head": (0, 0, 1.55), "HeadTop_End": (0, 0, 1.75),
}
for S, x in (("Left", 1), ("Right", -1)):
    J.update({f"{S}Shoulder": (0.05 * x, 0, 1.4), f"{S}Arm": (0.15 * x, 0, 1.4), f"{S}ForeArm": (0.43 * x, 0, 1.4),
              f"{S}Hand": (0.68 * x, 0, 1.4), f"{S}HandEnd": (0.78 * x, 0, 1.4),
              f"{S}UpLeg": (0.09 * x, 0, 0.95), f"{S}Leg": (0.09 * x, 0, 0.52), f"{S}Foot": (0.09 * x, 0, 0.08),
              f"{S}ToeBase": (0.09 * x, -0.12, 0.02), f"{S}Toe_End": (0.09 * x, -0.2, 0.02)})
PARENT = {"Spine": "Hips", "Spine1": "Spine", "Spine2": "Spine1", "Neck": "Spine2", "Head": "Neck", "HeadTop_End": "Head"}
for S in ("Left", "Right"):
    PARENT.update({f"{S}Shoulder": "Spine2", f"{S}Arm": f"{S}Shoulder", f"{S}ForeArm": f"{S}Arm", f"{S}Hand": f"{S}ForeArm",
                   f"{S}HandEnd": f"{S}Hand", f"{S}UpLeg": "Hips", f"{S}Leg": f"{S}UpLeg", f"{S}Foot": f"{S}Leg",
                   f"{S}ToeBase": f"{S}Foot", f"{S}Toe_End": f"{S}ToeBase"})
CHILD = {"Hips": "Spine", "Spine2": "Neck", "Head": "HeadTop_End"}
for S in ("Left", "Right"):
    CHILD.update({f"{S}Shoulder": f"{S}Arm", f"{S}Arm": f"{S}ForeArm", f"{S}ForeArm": f"{S}Hand", f"{S}Hand": f"{S}HandEnd",
                  f"{S}UpLeg": f"{S}Leg", f"{S}Leg": f"{S}Foot", f"{S}Foot": f"{S}ToeBase", f"{S}ToeBase": f"{S}Toe_End"})
N = 60
WAVE = 1.0  # sign of a bone-local X swing that lifts +X arm bones (checked by the test)


def make_fake_fbx():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = 30
    sc.frame_start, sc.frame_end = 1, N
    ad = bpy.data.armatures.new("fake")
    arm = bpy.data.objects.new("Armature", ad)
    sc.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for b, h in J.items():
        e = ad.edit_bones.new("mixamorig:" + b)
        e.head = h
        c = CHILD.get(b)
        e.tail = J[c] if c else (h[0], h[1], h[2] + 0.08) if "End" in b else (h[0], h[1], h[2] + 0.1)
        if (Vector(e.tail) - Vector(e.head)).length < 1e-4:
            e.tail = (h[0], h[1] - 0.05, h[2])
        eb[b] = e
    for b, p in PARENT.items():
        eb[b].parent = eb[p]
        eb[b].use_connect = False
    bpy.ops.object.mode_set(mode="POSE")
    pb = {b.name.split(":")[1]: b for b in arm.pose.bones}
    for b in pb.values():
        b.rotation_mode = "XYZ"
    # wave: left arm from T-pose up over the head, forearm waving. Bone axes: Y along the bone.
    for fr in range(1, N + 1):
        u = fr / N
        up = math.sin(min(1, u * 2) * math.pi / 2)
        pb["LeftArm"].rotation_euler = (WAVE * up * 1.2, 0, 0)       # swing the bone upward
        pb["LeftForeArm"].rotation_euler = (WAVE * (0.6 + 0.4 * math.sin(fr / 4)), 0, 0)
        pb["RightArm"].rotation_euler = (-WAVE * 1.35, 0, 0)         # right arm down by the side
        k = max(0, math.sin((u - 0.3) / 0.5 * math.pi)) if 0.3 < u < 0.8 else 0
        pb["RightUpLeg"].rotation_euler = (-1.0 * k, 0, 0)          # kick forward
        pb["RightLeg"].rotation_euler = (0.6 * k, 0, 0)
        pb["Hips"].location = (0, 0, -0.05 * k)
        for b in ("LeftArm", "LeftForeArm", "RightArm", "RightUpLeg", "RightLeg"):
            pb[b].keyframe_insert("rotation_euler", frame=fr)
        pb["Hips"].keyframe_insert("location", frame=fr)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.export_scene.fbx(filepath=FBX, object_types={"ARMATURE"}, add_leaf_bones=False, bake_anim=True,
                             bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False)


def run():
    make_fake_fbx()
    fod3d.reset(N + 10, w=640, h=360, engine="eevee", samples=8)
    clip = mixamo3d.load(FBX)
    assert len(clip) >= N - 1, len(clip)
    ch = cast3d.Character("main", loc=(0, 0, 0))
    frames = mixamo3d.apply(ch, clip, t=0.0)
    sc = bpy.context.scene
    soles = [o for o in bpy.data.objects if o.name.startswith("main-sole")]
    hands = {s: next(o for o in bpy.data.objects if o.name == f"main-hand{s}") for s in (-1, 1)}
    head = ch.head
    worst = 9.0
    raised = False
    gaps = []
    for i, fr in frames.items():
        sc.frame_set(fr)
        low = min((o.matrix_world @ Vector(c)).z for o in soles for c in o.bound_box)
        worst = min(worst, low)
        if hands[1].matrix_world.translation.z > head.matrix_world.translation.z:
            raised = True
        gaps.append(abs(hands[-1].matrix_world.translation.x))
    kick_i = mixamo3d.contact_frame(clip, "RightFoot")
    sc.frame_set(frames[kick_i])
    toe = (ch.knees[0].matrix_world @ Vector((0, -0.12, -0.25)))
    print(f"lowest sole point {worst:+.4f} m | left hand above head: {raised} | right hand min |x| {min(gaps):.3f} m"
          f" | kick frame {kick_i}, right toe y {toe.y:+.3f} (forward is -y)")
    assert worst > -0.005, "feet sank into the ground"
    assert raised, "wave did not raise the arm"
    assert min(gaps) > 0.25, "hanging arm touches the body"
    assert toe.y < -0.15, "kick did not swing the foot forward"

    # stills to look at
    bpy.ops.mesh.primitive_plane_add(size=6)
    bpy.context.object.data.materials.append(fod3d.mat("ground", "#d9c29a", 0.9))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.location = (2.2, -3.6, 1.1)
    cam.rotation_euler = (math.radians(83), 0, math.radians(31))
    sc.camera = cam
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.rotation_euler = (0.7, 0.2, 0.5)
    if os.environ.get("MIXAMO_TEST_CPU"):   # no GPU (cloud): Cycles on the CPU
        sc.render.engine = "CYCLES"
        sc.cycles.samples = 16
        sc.cycles.device = "CPU"
    for fr in (1, frames[kick_i], 30, N):
        sc.frame_set(fr)
        sc.render.filepath = os.path.join(OUT, f"f{fr:03d}.png")
        bpy.ops.render.render(write_still=True)
    print("OK, stills in", OUT)


if __name__ == "__main__":
    run()
