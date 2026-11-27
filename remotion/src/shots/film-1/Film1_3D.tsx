import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile } from 'remotion';
import timeline from './timeline.json';
import beats from '../../../../films/film-1-football/beats.json';
import capStyle from './captions.json';
import manifest from './manifest3d.json';
import { FilmCaptions, VoLine } from '../../lib/filmCaptions';
import { SceneView, Scene, MUSIC, Bed } from './Film1';

// Film 1 in 3D: every picture scene is a Blender clip (blender/film1_3d), cards/maps/owl stay as in Film1.
// Same voice, captions and music beds as Film1. Clip lengths come from manifest3d.json (blender/film1_3d/plan.py).
export const compositionConfig = { id: 'Film1Blender', durationInSeconds: 280.84, fps: 30, width: 1920, height: 1080 };

const FPS = 30, XF = 8;
const M = manifest as Record<string, { file: string; frames: number }[]>;

export default function Film1_3D() {
  const scenes = (timeline as { scenes: Scene[] }).scenes;
  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {scenes.map((sc) => {
        const from = Math.round(sc.start * FPS);
        const len = Math.round(sc.end * FPS) - from + XF;
        const clips = M[String(sc.i)];
        if (!clips) {
          return <Sequence key={sc.i} from={from} durationInFrames={len}><SceneView sc={sc} len={len} /></Sequence>;
        }
        let at = from;
        return clips.map((c, j) => {
          const s = at; at += c.frames;
          return (
            <Sequence key={`${sc.i}-${j}`} from={s} durationInFrames={c.frames}>
              <OffthreadVideo src={staticFile(`projects/film-1-football/3d/${c.file}`)} muted />
            </Sequence>
          );
        });
      })}
      <FilmCaptions lines={(beats as { vo: VoLine[] }).vo} style={capStyle} />
      <Audio src={staticFile('projects/film-1-football/audio/voice.wav')} />
      {MUSIC.map(([a, b, id]) => {
        const from = Math.round(a * FPS), len = Math.round((b - a) * FPS) + 30;
        return <Sequence key={id} from={from} durationInFrames={len}><Bed id={id} len={len} /></Sequence>;
      })}
    </AbsoluteFill>
  );
}
