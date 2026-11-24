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
- AI draws head, face, hair, beard and clothes (from the sheets) and all backgrounds. Code draws and moves the stick arms and legs.
- **Boots: ALWAYS the AI-drawn boots** cut from the sheet (`bootL/bootR.png`, `boot.png`). Never code-drawn boots. They must be whole, sole included.
- Feet stand ON the ground, never sunk into it, with a soft contact shadow.
- Cut-outs: every gap enclosed by the body (between arm and body, between the legs) must be transparent so the background shows through (`tools/cut_sheet.py` handles this).
- Walking: side view, the figure faces the way it walks; the stance foot stays planted (phase follows distance), knees bend, the hip dips, the arms swing calmly (`SideRig` in `remotion/src/lib/rig.tsx`).
- Turning to camera: a one-frame swap with a small squash-and-stretch pop. Never squash the figure to a thin line, and never crossfade (it looks like a ghost).
- QA: render frames and look at them (feet, boots, gaps, turns) before sending any video.

## Backgrounds
- Flat 2D cartoon, bold outlines, warm ochre palette; empty foreground for the characters; background people are tiny stick figures.
- Image prompts and approved plates for film 1: `films/film-1-football/backgrounds.json`, `media/projects/film-1-football/bg/`.

## Money
- Gemini images cost about 0.95 kr each (Nano Banana 2, 2K). Run a small test (1-2 images) before a big batch, and state the cost first.
- The owner runs image jobs by double-clicking `.bat` files; batch files skip images that already exist.

## Music and sound
- YouTube Audio Library only, **attribution not required** (`media/library/music/clips/yt-*.mp3`, catalog says which era each fits). Not yet auditioned by the owner.

## Default guidelines (Claude's proposals, the owner had no preference - change any time)
- Facts: every claim in a script needs two reliable sources; the source list goes in the video description.
- Pacing: something new on screen (cut, movement, graphic) every 4-6 s; a hook in the first 10 s; no shot longer than 8 s without movement.
- Characters: at least one of the three main characters in every story scene; the ruler (#3) only when a ruler is in the story.
- Sound: music always low under the voice, a different track per era; no CTA/subscribe outro.

## Later (agreed, not done yet)
- Film 1 long version (14-20 min) with more detail; cut to the owl talking at about 4:18.
- Blinking and talking mouths for the characters.
