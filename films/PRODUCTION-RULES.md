# Facts on Demand: production rules (READ BEFORE ANY FILM WORK)

Every rule here is a decision the channel owner made or a mistake we must not repeat.
Add to this file whenever something is changed or approved. Never undo a rule silently.

## Language and voice
- Films are in **English**. Narrator: ElevenLabs **Eddie Starling** (`VsQmyFHffusQDewmHB5v`).
- Generate voice with `tools/gen_voice.py --blocks` (one take per chapter). The built-in QA must pass:
  every word present, no line cut off, no silence over ~3 s, even levels. A broken voice track must never reach the owner again.
- Do not waste ElevenLabs credits: reuse cached takes, and test on short text first.

## Characters
- Three locked main characters for the whole series (`media/library/characters/`). Never regenerate them from text; era versions are made from the master sheet with `--ref`.
- Same face, hair colour and body in every era. Only clothes and facial hair change by era. Everyone wears the **orange scarf**.
- #1 and #2 share #1's compact body. #3 is rounder and is **always the king or emperor**.
- **Every scene must fit its era**: correct clothes, the right royal headwear for that ruler, correct buildings.
- Approved era versions and their known flaws are listed in each `character.json` under `eras`.

## Animation (hybrid: AI pixels + code motion)
- AI draws the WHOLE figure (head, clothes, ARMS, legs, boots) from the sheets, and all backgrounds.
- **ARMS: always the arms from the AI image. Never code-DRAWN arms** (they caused figures with extra arms). The AI-drawn arm pieces may be cut loose and rotated (puppet, below); a figure always shows exactly its own two drawn arms.
- Walking (side view) may still use code-drawn legs with the AI boots, but the arm stays the AI arm.
- **Figures must ACT** (wave, point, kick, throw, cheer), not just bob. Method: cut-out puppet (`tools/puppet_parts.py` + `remotion/src/lib/puppet.tsx`): the AI-drawn arms and legs are cut loose and rotated at shoulder/hip.
- **The era being talked about must be on screen**: every scene shows the era (and place) the narration is about, with the main characters dressed for it.
- **Boots: ALWAYS the AI-drawn boots** cut from the sheet (`bootL/bootR.png`, `boot.png`). Never code-drawn boots. They must be whole, sole included.
- Feet stand ON the ground, never sunk into it, with a soft contact shadow.
- Cut-outs: every gap enclosed by the body (between arm and body, between the legs) must be transparent so the background shows through (`tools/cut_sheet.py` handles this).
- Walking: side view, the figure faces the way it walks; the stance foot stays planted (phase follows distance), knees bend, the hip dips, the arms swing calmly (`SideRig` in `remotion/src/lib/rig.tsx`).
- Turning to camera: a one-frame swap with a small squash-and-stretch pop. Never squash the figure to a thin line, and never crossfade (it looks like a ghost).
- QA: render frames and look at them (feet, boots, gaps, turns) before sending any video.

## Motion principles (adapted from LottieFiles motion-design-skill, MIT)
- Every scene has three motion layers: PRIMARY (the character's action), SECONDARY (shadow, props, ball, cloth reacting), AMBIENT (background life: crowd figures, flags, smoke, slow camera drift). A flat scene is missing a layer.
- Every action is a micro-story: anticipation (wind-up) -> action -> follow-through/settle. A kick pulls the leg back first; a point leans in, overshoots slightly, then settles.
- Never linear easing for movement: entrances decelerate (ease-out), exits accelerate (ease-in), on-screen moves ease-in-out. Playful overshoot ~10-20% for our cartoon style.
- With 3+ characters, at most about a third act at the same moment; the hero acts first.
- Emotion drives motion: joy = bouncy arcs upward; tension/ban = sharp and fast; calm history narration = slow smooth drift.

## Captions (owner decision 2026-11-26)
- Every film has **burned-in hook captions** in the picture (not YouTube's CC), programmed by us: `remotion/src/lib/filmCaptions.tsx`, word lists per film in `captions.json` next to the film.
- Something always happens with the text: every word pops in exactly when Eddie says it (real word timings from `gen_voice.py`), the spoken word is lit yellow.
- Emphasis, max 2 per caption chunk so it keeps its meaning: numbers/years spin like a slot machine (orange), key names/things = orange team colour and bigger (`hero`), bans/losses/fights slam down in red with a shake and a stamp sound (`stamp`), comic words wiggle (`wobble`).
- Placement: TOP of the frame, because the characters stand in the lower half and their legs/boots must never be covered.
- Font: Lilita One, a local file in `media/library/fonts/` (SIL OFL), so every render looks the same, online or not.

## Backgrounds
- Flat 2D cartoon, bold outlines, warm ochre palette; empty foreground for the characters; background people are tiny stick figures.
- Image prompts and approved plates for film 1: `films/film-1-football/backgrounds.json`, `media/projects/film-1-football/bg/`.

## Money
- Gemini images cost about 0.95 kr each (Nano Banana 2, 2K). Run a small test (1-2 images) before a big batch, and state the cost first.
- The owner runs image jobs by double-clicking `.bat` files; batch files skip images that already exist.

## Hardware and local image generation
- Owner's PC: Windows, NVIDIA RTX 5070 with 12 GB VRAM (Blackwell: use NVFP4/FP8 model versions).
- PC has 16 GB system RAM (tight): GGUF model versions, close other apps while generating.
- ComfyUI is the main image tool (owner decision 2026-11-26: free, and locked workflow + fixed seed = the same picture every time). Gemini stays as backup.
- Setup: `comfy/README.md`. Qwen-Image-Edit-2511 GGUF + Lightning 4-step LoRA, fed the approved reference picture and prompted to change only pose/clothes. Jobs in `comfy/jobs/*.json`, run by `tools/comfy_run.py` from `make-*-comfy.bat` (skips finished pictures, writes a `.json` sidecar per picture).

## Music and sound
- YouTube Audio Library only, **attribution not required** (`media/library/music/clips/yt-*.mp3`, catalog says which era each fits). Not yet auditioned by the owner.

## Default guidelines (Claude's proposals, the owner had no preference - change any time)
- Facts: every claim in a script needs two reliable sources; the source list goes in the video description.
- Pacing: something new on screen (cut, movement, graphic) every 4-6 s; a hook in the first 10 s; no shot longer than 8 s without movement.
- Characters: at least one of the three main characters in every story scene; the ruler (#3) only when a ruler is in the story.
- Sound: music always low under the voice, a different track per era; no CTA/subscribe outro.

## 3D characters in Blender (owner decisions 2026-11-27)
- Direction under test: 3D scenes built and animated 100 % in code with Blender (bpy), rendered on the owner's GPU. Camera style of the London demo (fly-in, whip pan to the reaction, push-in close-up, rise out) is APPROVED.
- The 3D characters are a FAITHFUL 3D copy of the locked AI master sheets (`media/library/characters/*/master-sheet.jpg`): big round white head, NO ears, NO nose, black DOT eyes, the sheet's brows/hair/facial hair, orange scarf. Main character = big curled handlebar MUSTACHE (no full beard).
- Arms and legs: THICKER, with sleeves and trouser legs in the costume (owner chose this over thin stick limbs). Round white mitten hands, boots as on the sheet.
- No black outlines on the 3D characters: pure soft 3D shading.
- Every 3D character gets its own turnaround sheet (front, three-quarter, side, back + 6 expressions) approved by the owner BEFORE it is used in any film.
- Owner feedback on demo v1/v2: the first 3D figures looked bad; the backdrop must reach the horizon (no empty far end).

- 3D scene checks (owner, 2026-11-28, after Film1Full): every acting/talking/focus character faces the camera (3/4 at worst, faces always visible);
  every kick/header/catch really touches the ball (ball path derived from the limb at the contact frame); no intersections;
  environments from professional low-poly kits, not primitive boxes. One reference-quality scene must be approved before whole films.

## Job queue (remote work on the owner's PC, owner decision 2026-11-26)
- The owner asks from the phone; Claude drops `queue/inbox/<id>.json` into the PC's repo folder and reads `queue/logs/<id>.log`, `queue/done/<id>.json` and `queue/heartbeat.json`.
- `tools/job_runner.py` (started by `start-job-runner.bat`, autostart via `install-job-runner-autostart.bat`) runs ONLY its fixed actions with checked arguments: ping, comfy_models (downloads the ComfyUI model files, resumable), update (git fast-forward + npm ci when needed), comfy, voice (Eddie, costs credits: state the cost first), render, stills, bat (repo `make-*.bat` only).
- Always `update` before other jobs, and look at `stills` before a full `render`.

## Owl mascot (puppet)
- Reference: `media/library/characters/owl/reference.png` (the approved profile picture). ComfyUI job `comfy/jobs/owl-parts.json`, flat green background for keying.
- Owner approved (2026-11-27): all 8 poses (front-base, front-talk, front-blink, wings-down, point-glass, shrug, side-walk, wave).
- Puppet: `remotion/src/lib/owlPuppet.tsx` on the keyed poses in `media/library/characters/owl/cut/` (made by tools/key_owl.py, owl_overlays.py, owl_beak.py). Beak synced to Eddie's word timings and blinking in front-base; action poses switch in with a squash-pop (`OWL_BEATS` per shot). Replaces the still owl image everywhere. Feet are black, never orange. The owl always has exactly two wings (no extra arms or hands); the hand holding the glass is a wing tip.

## Quality standard
- The YouTube Short "Why Astronauts Can't Flush in Space" (@RicksClips3000, youtube.com/shorts/NpRAk-5VKlo) is the bar for how our animation looks and how watching feels (not its facts or its 9:16 format).

## Later (agreed, not done yet)
- The owl mascot becomes an animated puppet (ComfyUI draws the parts from the profile picture; code animates beak synced to the voice, blinking, wings, pointing, hopping) and replaces the still owl image in every film.
- Film 1 long version (14-20 min) with more detail; cut to the owl talking at about 4:18.
- Blinking and talking mouths for the characters.

## Automatic shot checks + real model kits (2026-11-28)
- `render.py` now runs two checks on every 3D scene before it renders:
  - **Faces visible:** every standing (not walking) character is turned so its face is at most 55° from the camera (a 3/4 view at worst). Each correction is logged as `check: <id> turned towards the camera`.
  - **Ball contact:** at every `kick`, the ball's path point is moved to the kicking foot's real world position at that frame, so the foot always touches the ball. Logged as `check: ball meets <id>'s foot`.
- Environments are built from **CC0 model kits** instead of primitive boxes, starting with the Quaternius *Medieval Village MegaKit* (Standard, free, CC0 1.0 — licence file `License_Standard.txt` in the kit).
  - Download on the PC with `make-download-kits.bat` → `media/library/kits/` (gitignored, re-downloadable).
  - `blender/kit3d.py` builds houses and streets from the pieces. Kit scale 0.72 to match the cast.
  - The medieval London street (scenes 30–36) is the first set rebuilt with the kit. If the kit is missing, the old primitive set is used.
- Only CC0 assets may be used. Check the licence before any new kit is added.
- **Faces never hidden by hats:** hoods and coifs are open shells with the face cut out (`open_cap` in `cast3d.py`). Before this fix, NPCs in hoods and coifs had no visible face at all.
- **Kicks must be in the picture:** `render.py` warns (`WARN check: kick … outside the picture`) when the kicking foot is out of frame at contact. Fix the camera when it warns. Scene T[23] (full-plan scene 30) was fixed this way.
- **Hair in EEVEE:** strand material has no sheen, low specular and roughness 0.62, and strand tips are thicker. Before this, the PC's EEVEE showed white patches on top of the hair.
- Street props (crates, wagons, fences) stand tight against the house walls, never in the play area.

## Mixamo motion (owner decision 2026-11-28)
- The owner has created the free Adobe account: 3D characters get real motion-capture animation from **Mixamo** instead of hand-keyed rotations.
- Only the owner logs in to mixamo.com (on the PC). Claude never asks for or stores the password; there is no Mixamo API.
- Download settings: **FBX Binary, Without Skin, 30 fps, Keyframe Reduction none**, on the default X Bot. "In Place" ON for walk/run cycles (the code moves the character along its path).
- Files go to `media/library/mixamo/<name>.fbx` (same name as on Mixamo, lowercase with dashes). The folder is **gitignored**: Mixamo animations may be used in our videos, but the raw files may not be redistributed.
- Pipeline: our characters get a Mixamo-named armature (`mixamorig:*` bones) with the costume pieces parented to their bones; the clip's bone rotations are retargeted onto it by bone name in bpy. The existing shot checks (faces visible, ball touches the foot, kick in frame, feet on the ground) still run on every scene.
