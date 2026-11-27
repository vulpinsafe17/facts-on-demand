"""Frame plan for the 3D scenes of film 1 (no bpy needed): which clips exist and how long each is.
Clip lengths follow remotion/src/shots/film-1/timeline.json exactly (+8 frames of overlap, XF in Film1.tsx)."""
import json, os
from shots import SHOTS

HERE = os.path.dirname(os.path.abspath(__file__))
TIMELINE = os.path.join(HERE, "..", "..", "remotion", "src", "shots", "film-1", "timeline.json")
FPS, XF = 30, 8


def scene_frames(i):
    sc = {s["i"]: s for s in json.load(open(TIMELINE))["scenes"]}[i]
    frm = round(sc["start"] * FPS)
    return round(sc["end"] * FPS) - frm + XF


def scene_start(i):
    sc = {s["i"]: s for s in json.load(open(TIMELINE))["scenes"]}[i]
    return round(sc["start"] * FPS) / FPS


def segments(i):
    shot = SHOTS[i]
    total = scene_frames(i)
    if "segments" not in shot:
        return [(shot, total, f"scene{i:02d}.mp4")]
    out, used = [], 0
    for j, seg in enumerate(shot["segments"]):
        n = total - used if j == len(shot["segments"]) - 1 else round(seg["dur"] * FPS)
        out.append((seg, n, f"scene{i:02d}_{j}.mp4"))
        used += n
    return out


def manifest():
    return {str(i): [{"file": f, "frames": n} for _, n, f in segments(i)] for i in sorted(SHOTS)}


def write_manifest(path):
    with open(path, "w") as fh:
        json.dump(manifest(), fh, indent=1)


if __name__ == "__main__":
    m = manifest()
    print(len(m), "scenes,", sum(c["frames"] for v in m.values() for c in v), "frames")
    write_manifest(os.path.join(HERE, "..", "..", "remotion", "src", "shots", "film-1", "manifest3d.json"))
