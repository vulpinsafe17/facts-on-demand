"""Frame plan for film 1 FULL (no bpy): scene timing from the narration (beats.json word times),
written for Remotion as timeline_full.json + manifest_full.json."""
import json, os
from shots_full import SCENE_LIST, SHOTS

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
BEATS = os.path.join(ROOT, "films", "film-1-football-full", "beats.json")
FPS, XF = 30, 8


def _timeline():
    b = json.load(open(BEATS, encoding="utf-8"))
    vo, total = b["vo"], b["format"]["durationSec"]
    starts = [0.0 if j == 0 else max(0.0, vo[first]["start"] - 0.25) for j, (i, first, sh) in enumerate(SCENE_LIST)]
    out = []
    for j, (i, first, sh) in enumerate(SCENE_LIST):
        end = starts[j + 1] if j + 1 < len(SCENE_LIST) else total
        out.append(dict(i=i, start=round(starts[j], 3), end=round(end, 3), kind=sh["kind"], bg=sh.get("set"), label=sh.get("label", "")))
    return out, total


TL, TOTAL = _timeline()
_BY = {s["i"]: s for s in TL}


def scene_start(i):
    return round(_BY[i]["start"] * FPS) / FPS


def scene_frames(i):
    sc = _BY[i]
    frm = round(sc["start"] * FPS)
    return round(sc["end"] * FPS) - frm + XF


def segments(i):
    shot = SHOTS[i]
    total = scene_frames(i)
    if "segments" not in shot:
        return [(shot, total, f"scene{i:03d}.mp4")]
    out, used = [], 0
    for j, seg in enumerate(shot["segments"]):
        n = total - used if j == len(shot["segments"]) - 1 else round(seg["dur"] * FPS)
        out.append((seg, n, f"scene{i:03d}_{j}.mp4"))
        used += n
    return out


def manifest():
    return {str(i): [{"file": f, "frames": n} for _, n, f in segments(i)] for i in sorted(SHOTS)}


def write_manifest(path):
    json.dump(manifest(), open(path, "w"), indent=1)


if __name__ == "__main__":
    rem = os.path.join(ROOT, "remotion", "src", "shots", "film-1")
    json.dump({"scenes": TL, "durationSec": TOTAL}, open(os.path.join(rem, "timeline_full.json"), "w"), indent=1, ensure_ascii=False)
    write_manifest(os.path.join(rem, "manifest_full.json"))
    m = manifest()
    print(len(TL), "scenes,", len(m), "3D,", sum(c["frames"] for v in m.values() for c in v), "3D frames, total", TOTAL, "s")
    for s in TL:
        if s["end"] - s["start"] > 9:
            print("long scene", s)
