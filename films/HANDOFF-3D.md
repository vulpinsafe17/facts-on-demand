# Handoff: 3D pipeline (written 2026-11-28 by the cloud session, for Claude Code on the PC)

Read `films/PRODUCTION-RULES.md` first (owner decisions, never regress), then this file.

## State
- 3D films are built 100 % in code with Blender 4.5 (`tools/blender_path.txt` = blender.exe):
  - `blender/fod3d.py`: scene setup, materials, primitives, sky/mist/compositor.
  - `blender/cast3d.py` + `blender/face3d.py`: the 3 locked characters (main / two / king) + NPCs + era costumes,
    ONE blended face (mouth shape keys + lip-sync to the narrator's word times), strand hair (hair curves).
  - `blender/film1_3d/`: `sets.py` (one builder per era backdrop), `acting.py` (walk/kick/talk/point/...),
    `shots.py` (test film), `shots_full.py` (full film, 89 scenes), `render.py` (`--plan full`, resumable),
    `plan_full.py` (timings from `films/film-1-football-full/beats.json`).
  - Remotion assembles: `remotion/src/shots/film-1/Film1Full.tsx` (clips + cards + owl + captions + voice + music).
  - Run: `make-film1-full-3d.bat` (Blender, ~2.5 h) then `node remotion/scripts/render-film.mjs Film1Full`.
    The Remotion sound pass times out on the caption font -> premixed `remotion/out/parts/Film1Full/audio.m4a` is used.
- Output: `remotion/out/Film1Full.mp4` (10:12). Voice is DONE and paid: `films/film-1-football-full/voice/voice.wav`
  (Eddie Starling, ~8,100 credits). Do NOT regenerate it. The script is approved as recorded.
- Nothing of the 3D work is on GitHub yet (this folder is not a git clone). First job: make it a git repo
  connected to vulpinsafe17/facts-on-demand (branch film-1-football) and commit (never .env, never media/reference/).

## Owner verdict on Film1Full (2026-11-28): NOT good enough
1. Environments look bad (primitive boxes/cones).
2. Characters look bad; in many scenes they face the wrong way and you cannot see their faces.
3. Kicks don't touch the ball (ball paths are hand-keyed, not tied to the foot).

## Plan (agreed direction)
1. Fast loop on THIS PC: render test frames with EEVEE on the GPU and LOOK at them after every change.
2. Automatic shot checks before any render (fail the shot, don't render it):
   - a character who talks/acts or is the focus must face the camera within ~70 degrees (3/4 view at worst);
   - every kick/header/catch: the ball must be within ~0.15 m of the foot/head/hand at the contact frame ->
     derive the ball path FROM the limb position at contact (compute the foot's world position in bpy), never by hand;
   - nothing intersects (characters, ball, props), feet never below the ground, nothing important out of frame.
3. Replace self-made environments with professional CC0 low-poly kits (check each licence first):
   Quaternius, Kenney, Poly Haven (materials/HDRIs). Characters: Mixamo account DONE 2026-11-28 (see PRODUCTION-RULES "Mixamo motion"); still ask the owner
   the owner creates it) for real motion, and about a 3D artist for the 3 locked characters (one-time cost).
4. Make ONE 30-60 s scene at the reference quality (media/reference/, analysis only) and get the owner's approval
   before producing whole films again.
