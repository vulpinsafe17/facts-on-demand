import React from 'react';
import { AbsoluteFill, Audio, Easing, Img, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame } from 'remotion';
import timeline from './timeline_full.json';
import beats from '../../../../films/film-1-football-full/beats.json';
import capStyle from './captions.json';
import manifest from './manifest_full.json';
import { FilmCaptions, VoLine } from '../../lib/filmCaptions';
import { OwlPuppet } from '../../lib/owlPuppet';
import { Bed } from './Film1';

// Film 1, full version (10:12) in 3D. Picture scenes = Blender clips (blender/film1_3d --plan full),
// cards + owl drawn here. Voice: films/film-1-football-full (Eddie Starling), captions from its word times.
export const compositionConfig = { id: 'Film1Full', durationInSeconds: 612, fps: 30, width: 1920, height: 1080 };

const FPS = 30, XF = 8;
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
type Sc = { i: number; start: number; end: number; kind: string; bg: string | null; label: string };
const M = manifest as Record<string, { file: string; frames: number }[]>;
const VO = (beats as { vo: (VoLine & { chapterStart?: boolean })[] }).vo;

const Card: React.FC<{ sc: Sc; len: number }> = ({ sc, len }) => {
  const f = useCurrentFrame();
  const fade = interpolate(f, [0, XF, len - XF, len], [0, 1, 1, 0], clamp);
  const pop = interpolate(f, [0, 10, 16], [0.85, 1.04, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: fade, background: '#f3e6c8', alignItems: 'center', justifyContent: 'center' }}>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(110,70,30,0.35) 100%)' }} />
      {sc.kind === 'owl' ? (
        <div style={{ position: 'relative', marginTop: 130, transform: `scale(${pop})` }}>
          <div style={{ position: 'absolute', left: '22%', right: '22%', bottom: -6, height: 34, borderRadius: '50%', background: 'rgba(60,35,15,0.3)', filter: 'blur(6px)' }} />
          <OwlPuppet height={700} startSec={sc.start} lines={VO} seed={sc.i} />
        </div>
      ) : sc.label === 'RED CARD' ? (
        <Img src={staticFile('projects/film-1-football/props/red-card.png')}
          style={{ height: 600, transform: `scale(${pop}) rotate(${interpolate(f, [0, 12], [-25, 8], clamp)}deg)` }} />
      ) : (
        <div style={{ fontFamily: 'Georgia, serif', fontWeight: 700, fontSize: 104, color: '#3a2412', textAlign: 'center', whiteSpace: 'pre-line',
          transform: `scale(${pop})`, lineHeight: 1.15, padding: 80, border: '10px solid #3a2412', borderRadius: 30, background: '#fbf1da' }}>
          {sc.label}
        </div>
      )}
    </AbsoluteFill>
  );
};

const TRACKS = ['yt-sprightly-pursuit', 'yt-in-the-temple-garden', 'yt-oud-dance', 'yt-invitation-to-the-castle-ball', 'yt-tiptoe',
  'yt-the-thunderer-march', 'yt-we-march-together', 'yt-sprightly-pursuit', 'yt-monument'];

export default function Film1Full() {
  const scenes = (timeline as { scenes: Sc[] }).scenes;
  const total = (timeline as { durationSec: number }).durationSec;
  const chStarts = VO.filter((v) => v.chapterStart).map((v) => Math.max(0, v.start - 0.4));
  chStarts[0] = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {scenes.map((sc) => {
        const from = Math.round(sc.start * FPS);
        const len = Math.round(sc.end * FPS) - from + XF;
        const clips = M[String(sc.i)];
        if (!clips) {
          return <Sequence key={sc.i} from={from} durationInFrames={len}><Card sc={sc} len={len} /></Sequence>;
        }
        let at = from;
        return clips.map((c, j) => {
          const s = at; at += c.frames;
          return (
            <Sequence key={`${sc.i}-${j}`} from={s} durationInFrames={c.frames}>
              <OffthreadVideo src={staticFile(`projects/film-1-football-full/3d/${c.file}`)} muted />
            </Sequence>
          );
        });
      })}
      <FilmCaptions lines={VO} style={capStyle} />
      <Audio src={staticFile('projects/film-1-football-full/audio/voice.wav')} />
      {chStarts.map((a, k) => {
        const b = k + 1 < chStarts.length ? chStarts[k + 1] : total;
        const from = Math.round(a * FPS), len = Math.round((b - a) * FPS) + 30;
        return <Sequence key={k} from={from} durationInFrames={len}><Bed id={TRACKS[k % TRACKS.length]} len={len} /></Sequence>;
      })}
    </AbsoluteFill>
  );
}
