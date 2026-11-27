// Facts on Demand owl mascot as a puppet.
// Pixels: the owner-approved ComfyUI poses (media/library/characters/owl/cut, green keyed out).
// Code adds the life: beak synced to Eddie's real word timings, blinking, breathing/bob,
// squash-and-pop when the pose changes. Lip sync + blink only in the front-base pose (the
// overlays are cut to fit exactly that drawing); action poses are short beats in between.
// Rules: exactly two wings (it's the AI drawing, never code-drawn limbs), black feet.
import React from 'react';
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import type { TimedWord, VoLine } from './filmCaptions';

export type OwlPose = 'front-base' | 'point-glass' | 'shrug' | 'side-walk' | 'wave' | 'wings-down';
export type OwlBeat = { at: number; pose: OwlPose }; // at = seconds from the start of the shot

const DIR = 'library/characters/owl/cut';
const CANVAS = { w: 987, h: 948 };
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const hash = (n: number) => { const x = Math.sin(n * 91.7) * 43758.5; return x - Math.floor(x); };

/** 0 = closed, 1 = half, 2 = open, from the spoken words around global time t. */
function mouth(words: TimedWord[], t: number) {
  const w = words.find((x) => t >= x.start && t < x.end);
  if (!w) return 0;
  const ph = Math.floor((t - w.start) / 0.09);   // ~syllable rhythm
  if (w.end - t < 0.05) return 0;                 // close at the end of each word
  return [2, 1, 2, 1, 0][ph % 5];
}

export const OwlPuppet: React.FC<{
  height: number;            // on-screen height of the full canvas in px
  beats?: OwlBeat[];         // pose changes; default: front-base all along
  startSec: number;          // global film time of this shot's frame 0 (for lip sync)
  lines?: VoLine[];          // Eddie's lines with word timings
  talk?: boolean;            // lip-sync while in front-base (default true)
  seed?: number;
}> = ({ height, beats = [], startSec, lines = [], talk = true, seed = 1 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tl = f / fps;
  const t = startSec + tl;
  const words = React.useMemo(() => lines.flatMap((l) => l.words ?? []), [lines]);

  const seq = [{ at: -1, pose: 'front-base' as OwlPose }, ...beats].sort((a, b) => a.at - b.at);
  let cur = seq[0], since = 99;
  for (const b of seq) if (tl >= b.at) { cur = b; since = tl - b.at; }
  const w = (CANVAS.w / CANVAS.h) * height;

  // pop on every pose change: squash down, stretch up, settle
  const pop = interpolate(since, [0, 0.08, 0.2, 0.32], [0.9, 1.06, 0.98, 1], clamp);
  const squashY = interpolate(since, [0, 0.08, 0.2, 0.32], [0.88, 1.06, 0.98, 1], clamp);
  // breathing + bob; a little more bounce while talking
  const m = talk && cur.pose === 'front-base' ? mouth(words, t) : 0;
  const bob = Math.sin(tl * 2.4 + seed) * 5 + (m ? -3 : 0);
  const rot = Math.sin(tl * 1.3 + seed) * 1.6 + (cur.pose === 'shrug' ? Math.sin(tl * 5) * 2 : 0);
  const walk = cur.pose === 'side-walk' ? Math.abs(Math.sin(tl * 7)) * -14 : 0;

  // blink every 2.6-4.4 s, 4 frames closed
  let blink = false;
  for (let k = 0, at = 0.8 + hash(seed) * 1.5; at < tl + 1; k++, at += 2.6 + hash(seed + k) * 1.8) {
    if (tl >= at && tl < at + 4 / fps) blink = true;
  }

  const layer: React.CSSProperties = { position: 'absolute', left: 0, top: 0, width: w, height };
  return (
    <div style={{ position: 'relative', width: w, height, transformOrigin: '50% 100%',
      transform: `translateY(${bob + walk}px) rotate(${rot}deg) scale(${pop}, ${squashY})` }}>
      <Img src={staticFile(`${DIR}/${cur.pose}.png`)} style={layer} />
      {cur.pose === 'front-base' && blink && <Img src={staticFile(`${DIR}/overlay-eyes-closed.png`)} style={layer} />}
      {cur.pose === 'front-base' && m > 0 && <Img src={staticFile(`${DIR}/overlay-beak-${m}.png`)} style={layer} />}
    </div>
  );
};
