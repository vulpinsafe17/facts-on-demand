import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import timeline from './timeline.json';
import figJson from './figures.json';
import beats from '../../../../films/film-1-football/beats.json';
import capStyle from './captions.json';
import { FilmCaptions, VoLine } from '../../lib/filmCaptions';
import { OwlPuppet, OwlBeat } from '../../lib/owlPuppet';

// FILM 1 — "Where did football come from?" (test film, 4:41).
// Scenes on approved plates, timed to Eddie's word timings; era-correct cast from the
// locked characters (hybrid rigs: AI bodies + AI boots, code limbs); props; era music.
// Rules: films/PRODUCTION-RULES.md
export const compositionConfig = { id: 'Film1', durationInSeconds: 280.84, fps: 30, width: 1920, height: 1080 };

const FPS = 30, XF = 8;
const P = (f: string) => staticFile(`projects/film-1-football/${f}`);
const figs = figJson as Record<string, { file: string; w: number; h: number }>;
type Scene = { i: number; start: number; end: number; kind: string; bg: string | null; label: string };
type Actor = { r: string; x: number; h?: number; flip?: boolean; act?: 'idle' | 'talk' | 'point' | 'cheer' | 'shrug'; enter?: 'left' | 'right' };
type Prop = { p: string; x: number; y: number; w: number; spin?: boolean; drop?: boolean };

const M1 = 'main-character', M2 = 'character-2', K = 'character-3';
const CAST: Record<number, { actors?: Actor[]; props?: Prop[]; feet?: number }> = {
  0: { actors: [{ r: `${K}/edward-ii`, x: 980, h: 600, act: 'talk' }], props: [{ p: 'decree-scroll', x: 1240, y: 640, w: 230 }] },
  1: { props: [{ p: 'feather-ball', x: 1500, y: 760, w: 180, drop: true }] },
  3: { actors: [{ r: `${M1}/greek-athlete`, x: 520, act: 'talk' }, { r: `${M2}/victorian-gentleman`, x: 1400, flip: true, act: 'point' }, { r: `${M1}/han-soldier`, x: 960, act: 'shrug' }], feet: 1060 },
  6: { actors: [{ r: `${M1}/han-soldier`, x: 1250, h: 430, act: 'cheer' }, { r: `${M2}/han-soldier`, x: 1500, h: 430, flip: true, act: 'cheer' }], feet: 1050 },
  8: { props: [{ p: 'feather-ball', x: 960, y: 520, w: 420 }] },
  9: { props: [{ p: 'feather-ball', x: 960, y: 560, w: 380, spin: true }] },
  10: { actors: [{ r: `${K}/han-gaozu`, x: 330, h: 470, act: 'point' }], feet: 700 },
  11: { actors: [{ r: `${M1}/han-soldier`, x: 760, act: 'cheer', enter: 'left' }, { r: `${M2}/han-soldier`, x: 1180, flip: true, act: 'talk', enter: 'right' }], props: [{ p: 'feather-ball', x: 970, y: 820, w: 110, spin: true }] },
  14: { actors: [{ r: `${K}/ming-hongwu`, x: 640, h: 600, act: 'point' }], props: [{ p: 'feather-ball', x: 1250, y: 940, w: 120 }], feet: 1050 },
  18: { actors: [{ r: `${M1}/greek-athlete`, x: 700, act: 'cheer', enter: 'left' }, { r: `${M2}/greek-athlete`, x: 1250, flip: true, act: 'talk' }] },
  19: { actors: [{ r: `${M1}/greek-athlete`, x: 860, act: 'shrug' }, { r: `${M2}/greek-athlete`, x: 1120, flip: true, act: 'point' }], props: [{ p: 'lace-ball', x: 990, y: 860, w: 0 }] },
  20: { actors: [{ r: `${M1}/heian-noble`, x: 720, act: 'cheer' }, { r: `${M2}/heian-noble`, x: 1200, flip: true, act: 'cheer' }], props: [{ p: 'feather-ball', x: 960, y: 420, w: 100, spin: true }] },
  21: { actors: [{ r: `${M1}/heian-noble`, x: 780, act: 'idle' }, { r: `${M2}/heian-noble`, x: 1140, flip: true, act: 'idle' }], props: [{ p: 'feather-ball', x: 960, y: 960, w: 100 }] },
  22: { actors: [{ r: `${M1}/medieval-peasant`, x: 600, act: 'cheer', enter: 'left' }, { r: `${M2}/medieval-peasant`, x: 1320, flip: true, act: 'cheer', enter: 'right' }] },
  23: { actors: [{ r: `${M1}/medieval-peasant`, x: 820, act: 'cheer' }, { r: `${M2}/medieval-peasant`, x: 1100, flip: true, act: 'cheer' }], props: [{ p: 'feather-ball', x: 960, y: 900, w: 120, spin: true }] },
  24: { actors: [{ r: `${M2}/medieval-peasant`, x: 700, act: 'shrug' }], props: [{ p: 'cart', x: 1250, y: 860, w: 380 }, { p: 'chicken', x: 1550, y: 930, w: 150, spin: true }] },
  25: { actors: [{ r: `${M1}/medieval-peasant`, x: 1150, act: 'shrug' }] },
  26: { actors: [{ r: `${M2}/medieval-peasant`, x: 960, act: 'talk' }], props: [{ p: 'decree-scroll', x: 1150, y: 700, w: 200 }] },
  27: { actors: [{ r: `${M2}/medieval-peasant`, x: 760, act: 'talk' }, { r: `${M1}/medieval-peasant`, x: 1350, act: 'cheer' }], props: [{ p: 'feather-ball', x: 1450, y: 900, w: 110, spin: true }] },
  28: { actors: [{ r: `${K}/edward-ii`, x: 980, h: 600, act: 'point' }] },
  29: { actors: [{ r: `${M1}/medieval-peasant`, x: 600, act: 'point' }], props: [{ p: 'longbow', x: 380, y: 740, w: 260 }, { p: 'feather-ball', x: 900, y: 980, w: 100 }] },
  31: { props: [{ p: 'feather-ball', x: 900, y: 330, w: 200, drop: true }] },
  35: { actors: [{ r: `${M1}/victorian-gentleman`, x: 560, h: 460, act: 'talk' }, { r: `${M2}/victorian-gentleman`, x: 1500, h: 460, flip: true, act: 'idle' }], feet: 1050 },
  36: { actors: [{ r: `${M1}/victorian-gentleman`, x: 700, act: 'cheer' }, { r: `${M2}/victorian-gentleman`, x: 1250, flip: true, act: 'cheer' }], props: [{ p: 'lace-ball', x: 990, y: 940, w: 0 }] },
  37: { actors: [{ r: `${M1}/victorian-gentleman`, x: 820, act: 'idle' }, { r: `${M2}/victorian-gentleman`, x: 1100, act: 'idle' }] },
  38: { actors: [{ r: `${M1}/victorian-gentleman`, x: 560, h: 460, act: 'idle', enter: 'left' }], feet: 1040 },
  39: { actors: [{ r: `${M1}/victorian-gentleman`, x: 1350, h: 520, act: 'talk' }], feet: 1050 },
  40: { actors: [{ r: `${M1}/victorian-gentleman`, x: 700, h: 470, act: 'talk' }, { r: `${M2}/victorian-gentleman`, x: 1200, h: 470, flip: true, act: 'idle' }], feet: 1050 },
  41: { actors: [{ r: `${M1}/victorian-gentleman`, x: 760, h: 520, act: 'point' }, { r: `${M2}/victorian-gentleman`, x: 1160, h: 520, flip: true, act: 'shrug' }], feet: 1050 },
  42: { actors: [{ r: `${M2}/victorian-gentleman`, x: 1350, h: 460, act: 'idle', enter: 'left' }], feet: 1040 },
  44: { actors: [{ r: `${M1}/victorian-gentleman`, x: 760, h: 450, act: 'talk' }, { r: `${M2}/victorian-gentleman`, x: 1000, h: 450, act: 'idle' }], feet: 1040 },
};

const MOVES = [
  { s0: 1.0, s1: 1.08, x0: 0, x1: -1.5, y0: 0, y1: -1 },
  { s0: 1.1, s1: 1.02, x0: -1.5, x1: 1, y0: -1, y1: 0 },
  { s0: 1.03, s1: 1.1, x0: 1.5, x1: -1, y0: 0.5, y1: -1 },
  { s0: 1.06, s1: 1.06, x0: -2, x1: 2, y0: 0, y1: 0 },
];
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

// Whole-figure motion only: the arms, legs and boots are the AI drawing (owner's rule:
// never code-drawn arms). Acting = sway, bob, hop, lean and squash of the cut-out.
function motion(act: Actor['act'], f: number, seed: number) {
  const t = f / FPS + seed;
  let rot = Math.sin(t * 1.4) * 1.2, dy = 0, sx = 1, sy = 1 + Math.sin(t * 2.2) * 0.006;
  if (act === 'talk') { const b = Math.abs(Math.sin(t * 4.2)); dy = -b * 6; rot = Math.sin(t * 2.1) * 2.5; sy = 1 + b * 0.012; }
  if (act === 'cheer') { const h = Math.abs(Math.sin(t * 5)); dy = -h * 38; sy = 1 + (1 - h) * -0.04 + h * 0.02; sx = 1 + (1 - h) * 0.03; }
  if (act === 'shrug') { const k = (Math.sin(t * 2.5) + 1) / 2; sy = 1 - k * 0.035; sx = 1 + k * 0.025; rot = Math.sin(t * 1.2) * 1.5; }
  if (act === 'point') { const k = interpolate(f, [4, 14], [0, 1], clamp); rot = -4 * k + Math.sin(t * 1.4) * 0.8; dy = -k * 4; }
  return { rot, dy, sx, sy };
}

// owl acting per owl shot: talks in front-base, then the action pose the storyboard asks for
const OWL_BEATS: Record<number, (dur: number) => OwlBeat[]> = {
  17: (d) => [{ at: d * 0.45, pose: 'point-glass' }],  // points the magnifying glass west
  49: () => [{ at: 0.5, pose: 'shrug' }],               // the owl shrugs
};

const SceneView: React.FC<{ sc: Scene; len: number }> = ({ sc, len }) => {
  const f = useCurrentFrame();
  const fade = interpolate(f, [0, XF], [0, 1], clamp);
  const t = interpolate(f, [0, len], [0, 1], { ...clamp, easing: Easing.bezier(0.4, 0, 0.6, 1) });
  const mv = MOVES[sc.i % MOVES.length];
  const s = mv.s0 + (mv.s1 - mv.s0) * t, x = mv.x0 + (mv.x1 - mv.x0) * t, y = mv.y0 + (mv.y1 - mv.y0) * t;
  const night = sc.bg === 'victorian-street-night';
  const cast = CAST[sc.i] ?? {};
  const feet = cast.feet ?? 1030;
  if (sc.kind === 'bg' && sc.bg) {
    return (
      <AbsoluteFill style={{ opacity: fade, overflow: 'hidden' }}>
        <AbsoluteFill style={{ transform: `scale(${s}) translate(${x}%, ${y}%)` }}>
          <Img src={P(`bg/${sc.bg}.png`)} style={{ width: 1920, height: 1080, objectFit: 'cover' }} />
          {night && <AbsoluteFill style={{ background: 'rgba(20,24,60,0.38)', mixBlendMode: 'multiply' }} />}
          {(cast.props ?? []).map((pr, k) => {
            const drop = pr.drop ? interpolate(f, [4, 18], [-500, 0], { ...clamp, easing: Easing.bezier(0.5, 0, 1, 0.6) }) : 0;
            const bounce = pr.drop ? Math.max(0, Math.sin(interpolate(f, [18, 30], [0, Math.PI], clamp))) * -40 : 0;
            const rot = pr.spin ? f * 6 : 0;
            const bob = pr.spin ? Math.abs(Math.sin(f / 7)) * -30 : 0;
            if (pr.w === 0) return <div key={k} style={{ position: 'absolute', left: pr.x - 40, top: pr.y - 40 + bob, width: 80, height: 80, borderRadius: '50%', background: 'radial-gradient(circle at 35% 35%, #c9894e, #7a4a24)', border: '6px solid #141010', transform: `rotate(${rot}deg)` }} />;
            return <Img key={k} src={P(`props/${pr.p}.png`)} style={{ position: 'absolute', left: pr.x - pr.w / 2, top: pr.y - pr.w / 2 + drop + bounce + bob, width: pr.w, transform: `rotate(${rot}deg)` }} />;
          })}
          {(cast.actors ?? []).map((a, k) => {
            const fig = figs[a.r];
            if (!fig) return null;
            const [ch, era] = a.r.split('/');
            const enter = a.enter ? interpolate(f, [0, 20], [a.enter === 'left' ? -700 : 700, 0], { ...clamp, easing: Easing.bezier(0.2, 0.7, 0.3, 1) }) : 0;
            const pop = interpolate(f, [0, 6, 11], [0.94, 1.03, 1], clamp);
            const m = motion(a.act, f, k * 1.7 + sc.i);
            const h = (a.h ?? 520) * pop, w = (fig.w / fig.h) * h;
            const left = a.x + enter - w / 2;
            return (
              <React.Fragment key={k}>
                <div style={{ position: 'absolute', left: a.x + enter - w * 0.32, top: feet - 12, width: w * 0.64, height: 24, borderRadius: '50%', background: 'rgba(50,30,10,0.33)', filter: 'blur(5px)', transform: `scaleX(${1 + m.dy / 200})` }} />
                <Img src={staticFile(`library/characters/${ch}/rigs/${era}/${fig.file}`)}
                  style={{ position: 'absolute', left, top: feet - h + m.dy, width: w, height: h, transformOrigin: '50% 100%',
                    transform: `${a.flip ? 'scaleX(-1) ' : ''}rotate(${m.rot}deg) scale(${m.sx}, ${m.sy})` }} />
              </React.Fragment>
            );
          })}
        </AbsoluteFill>
      </AbsoluteFill>
    );
  }
  const pop = interpolate(f, [0, 10, 16], [0.85, 1.04, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: fade, background: '#f3e6c8', alignItems: 'center', justifyContent: 'center' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(110,70,30,0.35) 100%)' }} />
      {sc.kind === 'owl' ? (
        <div style={{ position: 'relative', marginTop: 130, transform: `scale(${pop})` }}>
          <div style={{ position: 'absolute', left: '22%', right: '22%', bottom: -6, height: 34, borderRadius: '50%', background: 'rgba(60,35,15,0.3)', filter: 'blur(6px)' }} />
          <OwlPuppet height={700} startSec={sc.start} lines={(beats as { vo: VoLine[] }).vo} seed={sc.i} beats={OWL_BEATS[sc.i]?.(sc.end - sc.start)} />
        </div>
      ) : sc.i === 15 ? (
        <Img src={P('props/red-card.png')} style={{ height: 600, transform: `scale(${pop}) rotate(${interpolate(f, [0, 12], [-25, 8], clamp)}deg)` }} />
      ) : (
        <div style={{ fontFamily: 'Georgia, serif', fontWeight: 700, fontSize: 110, color: '#3a2412', textAlign: 'center', whiteSpace: 'pre-line', transform: `scale(${pop})`, lineHeight: 1.15, padding: 80, border: '10px solid #3a2412', borderRadius: 30, background: '#fbf1da' }}>
          {sc.label}
        </div>
      )}
    </AbsoluteFill>
  );
};

// era music: one bed per chapter, faded in/out, low under the voice
const MUSIC: [number, number, string][] = [
  [0, 21.4, 'yt-sprightly-pursuit'], [21.4, 83.3, 'yt-in-the-temple-garden'], [83.3, 104.6, 'yt-oud-dance'],
  [104.6, 151.4, 'yt-invitation-to-the-castle-ball'], [151.4, 184.3, 'yt-tiptoe'], [184.3, 228.5, 'yt-the-thunderer-march'],
  [228.5, 254.1, 'yt-we-march-together'], [254.1, 280.84, 'yt-monument'],
];
const Bed: React.FC<{ id: string; len: number }> = ({ id, len }) => {
  return <Audio src={staticFile(`library/music/clips/${id}.mp3`)} loop volume={(f) => interpolate(f, [0, 30, len - 30, len], [0, 0.085, 0.085, 0], clamp)} />;
};

export default function Film1() {
  const scenes = (timeline as { scenes: Scene[] }).scenes;
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {scenes.map((sc) => {
        const from = Math.round(sc.start * FPS);
        const len = Math.round(sc.end * FPS) - from + XF;
        return (
          <Sequence key={sc.i} from={from} durationInFrames={len}>
            <SceneView sc={sc} len={len} />
          </Sequence>
        );
      })}
      <FilmCaptions lines={(beats as { vo: VoLine[] }).vo} style={capStyle} />
      <Audio src={P('audio/voice.wav')} />
      {MUSIC.map(([a, b, id]) => {
        const from = Math.round(a * FPS), len = Math.round((b - a) * FPS) + 30;
        return <Sequence key={id} from={from} durationInFrames={len}><Bed id={id} len={len} /></Sequence>;
      })}
    </AbsoluteFill>
  );
}
