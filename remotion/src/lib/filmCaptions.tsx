// Facts on Demand — burned-in "hook" captions for the long-form 16:9 films.
// Owner decision (2026-11-26): captions are ALWAYS in the picture, programmed by us, and
// something is always happening with the text. Driven by Eddie's real word timings
// (tools/gen_voice.py -> beats.json vo[].words), so the text follows the voice exactly.
//
// Every word pops in as it is spoken; the word being spoken is lit yellow.
// Emphasis effects (at most MAX_FX per chunk, so the effects keep their meaning):
//   slot   — any number/year: digits spin like a slot machine, then lock with a pop
//   hero   — key names/things (per film): orange team colour, bigger, bouncy overshoot
//   stamp  — bans, losses, fights: red, slams down from big, the caption block shakes
//   wobble — comic words: keeps wiggling while it is on screen
// The per-film word lists live in captions.json next to the film.
// Placement: TOP of the frame. The characters stand in the lower half, and captions at the
// bottom would cover their legs and boots (see PRODUCTION-RULES: boots always visible).
import React from 'react';
import { Audio, Easing, Sequence, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { loadFont } from '@remotion/fonts';

// Font is a local file (media/library/fonts, SIL OFL) so every render looks identical,
// with or without internet.
const FONT = 'LilitaOne';
loadFont({ family: FONT, url: staticFile('library/fonts/LilitaOne-Regular.woff2'), weight: '400' });

export type TimedWord = { w: string; start: number; end: number };
export type VoLine = { text: string; start: number; end: number; words?: TimedWord[] };
export type Fx = 'pop' | 'slot' | 'hero' | 'stamp' | 'wobble';
export type CaptionStyle = { hero?: string[]; stamp?: string[]; wobble?: string[] };

const MAX_WORDS = 5;
const MAX_FX = 2;
const C = { ink: '#2a170a', white: '#fffaf0', live: '#ffd84a', orange: '#ff8a1f', red: '#e5372b' };
const outB = Easing.bezier(0.34, 1.56, 0.64, 1); // ease-out with ~15% overshoot (rules: playful overshoot)
const out = Easing.bezier(0.33, 1, 0.68, 1);
const p = (t: number, a: number, b: number) => Math.max(0, Math.min(1, (t - a) / Math.max(1e-4, b - a)));
const norm = (w: string) => w.toLowerCase().replace(/[^a-z0-9']/g, '');
const hash = (n: number) => { const x = Math.sin(n * 127.1) * 43758.5453; return x - Math.floor(x); };

type CWord = TimedWord & { fx: Fx };
type Chunk = { words: CWord[]; start: number; hold: number };

export function buildChunks(lines: VoLine[], style: CaptionStyle): Chunk[] {
  const sets: [Fx, Set<string>][] = [
    ['stamp', new Set((style.stamp ?? []).map(norm))],
    ['hero', new Set((style.hero ?? []).map(norm))],
    ['wobble', new Set((style.wobble ?? []).map(norm))],
  ];
  const chunks: Chunk[] = [];
  for (const line of lines) {
    const ws = line.words ?? [];
    let cur: CWord[] = [];
    const flush = () => { if (cur.length) chunks.push({ words: cur, start: cur[0].start, hold: 0 }); cur = []; };
    ws.forEach((w) => {
      const n = norm(w.w);
      let fx: Fx = /\d/.test(w.w) ? 'slot' : 'pop';
      if (fx === 'pop') for (const [k, s] of sets) if (s.has(n)) { fx = k; break; }
      cur.push({ ...w, fx });
      // break on punctuation (natural phrases) or when the chunk is full
      if (/[.,!?;:]["']?$/.test(w.w) || cur.length >= MAX_WORDS) flush();
    });
    flush();
  }
  chunks.forEach((c, i) => {
    let n = 0; // cap the effects per chunk: first ones win, the rest become plain pops
    c.words.forEach((w) => { if (w.fx !== 'pop') { n++; if (n > MAX_FX) w.fx = 'pop'; } });
    const last = c.words[c.words.length - 1].end;
    const next = chunks[i + 1];
    c.hold = next ? Math.min(next.start, last + 0.7) : last + 1.0;
  });
  return chunks;
}

const Word: React.FC<{ w: CWord; t: number; f: number; size: number; i: number }> = ({ w, t, f, size, i }) => {
  const a = p(t, w.start, w.start + 0.2);
  const live = t >= w.start && t < w.end + 0.04;
  let scale = 0.55 + 0.45 * outB(a), rot = 0, dy = (1 - out(a)) * 22, color = live ? C.live : C.white;
  let text = w.w, sz = size;
  if (w.fx === 'hero') {
    sz = size * 1.22; color = C.orange;
    scale = 0.4 + 0.6 * outB(p(t, w.start, w.start + 0.28));
    dy = -Math.sin(p(t, w.start, w.start + 0.35) * Math.PI) * 18;
  }
  if (w.fx === 'stamp') {
    const s = p(t, w.start, w.start + 0.12);
    sz = size * 1.18; color = C.red;
    scale = 2.4 - 1.4 * Easing.in(Easing.quad)(s) + (s >= 1 ? Math.sin(p(t, w.start + 0.12, w.start + 0.3) * Math.PI) * 0.08 : 0);
    rot = -14 + 10 * s; dy = 0;
  }
  if (w.fx === 'slot') {
    sz = size * 1.18; color = C.orange;
    const spin = p(t, w.start, w.start + 0.45);
    if (t >= w.start && spin < 1) text = w.w.replace(/\d/g, (_, k) => String(Math.floor(hash(f * 7 + k * 13 + i) * 10)));
    scale = spin < 1 ? 0.85 + 0.15 * out(a) : 1 + Math.sin(p(t, w.start + 0.45, w.start + 0.62) * Math.PI) * 0.14;
    dy = spin < 1 ? Math.sin(f * 1.7) * 3 : 0;
  }
  if (w.fx === 'wobble') rot = Math.sin(t * 9 + i) * 6 * Math.min(1, a * 2);
  const shown = t >= w.start - 0.02;
  return (
    <span style={{
      display: 'inline-block', fontFamily: FONT, fontSize: sz, lineHeight: 1.05, color,
      opacity: shown ? Math.min(1, a * 3) : 0,
      transform: `translateY(${dy}px) rotate(${rot}deg) scale(${shown ? scale : 0.55})`,
      WebkitTextStroke: `${Math.round(sz * 0.13)}px ${C.ink}`, paintOrder: 'stroke fill',
      textShadow: `0 ${Math.round(sz * 0.09)}px 0 ${C.ink}`,
      fontVariantNumeric: 'tabular-nums', whiteSpace: 'pre',
    }}>{text}</span>
  );
};

export const FilmCaptions: React.FC<{
  lines: VoLine[]; style: CaptionStyle; y?: number; size?: number; sfx?: boolean;
  hideWhen?: (t: number) => boolean;
}> = ({ lines, style, y = 130, size = 84, sfx = true, hideWhen }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const chunks = React.useMemo(() => buildChunks(lines, style), [lines, style]);
  const c = chunks.find((k) => t >= k.start - 0.02 && t < k.hold);
  const visible = c && !(hideWhen && hideWhen(t));
  let shake = 0;
  if (c) for (const w of c.words) if (w.fx === 'stamp') { const s = p(t, w.start + 0.11, w.start + 0.32); if (s > 0 && s < 1) shake = Math.sin(s * 40) * (1 - s) * 9; }
  const exit = c ? p(t, c.hold - 0.12, c.hold) : 0;
  return (
    <>
      {visible && (
        <div style={{ position: 'absolute', left: 80, right: 80, top: y, transform: `translate(${shake}px, ${-50 - exit * 12}%)`, opacity: 1 - exit,
          display: 'flex', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'baseline', columnGap: size * 0.36, rowGap: size * 0.1 }}>
          {c!.words.map((w, i) => <Word key={i} w={w} t={t} f={f} size={size} i={i} />)}
        </div>
      )}
      {sfx && chunks.flatMap((k) => k.words.filter((w) => w.fx === 'stamp' || w.fx === 'slot').map((w, i) => (
        <Sequence key={`${w.start}-${i}`} from={Math.round((w.start + (w.fx === 'slot' ? 0.45 : 0.1)) * fps)} durationInFrames={Math.round(fps * 1.2)}>
          <Audio src={staticFile(`library/sfx/clips/${w.fx === 'stamp' ? 'stamp-hit' : 'ui-click-soft'}.mp3`)} volume={w.fx === 'stamp' ? 0.32 : 0.25} />
        </Sequence>
      )))}
    </>
  );
};
