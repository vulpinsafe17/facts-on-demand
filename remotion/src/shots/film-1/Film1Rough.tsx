import React from 'react';
import { AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import timeline from './timeline.json';

// Film 1 ROUGH CUT: every scene on its approved background, timed to Eddie's real
// word timings, slow camera moves, cards for graphics/maps, music bed under the voice.
// Characters (rigs) are layered in per scene in the next pass.
export const compositionConfig = { id: 'Film1Rough', durationInSeconds: 280.84, fps: 30, width: 1920, height: 1080 };

const FPS = 30, XF = 8; // crossfade frames
const P = (f: string) => staticFile(`projects/film-1-football/${f}`);
type Scene = { i: number; start: number; end: number; kind: string; bg: string | null; label: string };

const MOVES = [
  { s0: 1.0, s1: 1.1, x0: 0, x1: -2, y0: 0, y1: -1 },
  { s0: 1.12, s1: 1.02, x0: -2, x1: 1, y0: -1, y1: 0 },
  { s0: 1.04, s1: 1.12, x0: 2, x1: -1, y0: 1, y1: -1 },
  { s0: 1.08, s1: 1.08, x0: -3, x1: 3, y0: 0, y1: 0 },
];

const SceneView: React.FC<{ sc: Scene; len: number }> = ({ sc, len }) => {
  const f = useCurrentFrame();
  const fade = interpolate(f, [0, XF], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const t = interpolate(f, [0, len], [0, 1], { extrapolateRight: 'clamp', easing: Easing.bezier(0.4, 0, 0.6, 1) });
  const mv = MOVES[sc.i % MOVES.length];
  const s = mv.s0 + (mv.s1 - mv.s0) * t, x = mv.x0 + (mv.x1 - mv.x0) * t, y = mv.y0 + (mv.y1 - mv.y0) * t;
  const night = sc.bg === 'victorian-street-night';
  if (sc.kind === 'bg' && sc.bg) {
    return (
      <AbsoluteFill style={{ opacity: fade, overflow: 'hidden' }}>
        <Img src={P(`bg/${sc.bg}.png`)} style={{ width: 1920, height: 1080, objectFit: 'cover', transform: `scale(${s}) translate(${x}%, ${y}%)` }} />
        {night && <AbsoluteFill style={{ background: 'rgba(20,24,60,0.38)', mixBlendMode: 'multiply' }} />}
      </AbsoluteFill>
    );
  }
  const pop = interpolate(f, [0, 10, 16], [0.85, 1.04, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ opacity: fade, background: '#f3e6c8', alignItems: 'center', justifyContent: 'center' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(110,70,30,0.35) 100%)' }} />
      {sc.kind === 'owl' ? (
        <Img src={P('owl.png')} style={{ height: 820, transform: `scale(${pop}) rotate(${Math.sin(f / 9) * 2}deg)` }} />
      ) : (
        <div style={{ fontFamily: 'Georgia, serif', fontWeight: 700, fontSize: 110, color: '#3a2412', textAlign: 'center', whiteSpace: 'pre-line', transform: `scale(${pop})`, lineHeight: 1.15, padding: 80, border: '10px solid #3a2412', borderRadius: 30, background: '#fbf1da' }}>
          {sc.label}
        </div>
      )}
    </AbsoluteFill>
  );
};

export default function Film1Rough() {
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
      <Audio src={P('audio/voice.wav')} />
      <Audio src={staticFile('library/music/clips/yt-sprightly-pursuit.mp3')} volume={0.09} loop />
    </AbsoluteFill>
  );
}
