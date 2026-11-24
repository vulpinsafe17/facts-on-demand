import React from 'react';
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { Rig, RigData, Pose } from '../../lib/rig';

// Motion test: hybrid rig (AI body + code limbs) walks into the London street and points.
export const compositionConfig = { id: 'Film1RigTest', durationInSeconds: 6, fps: 30, width: 1920, height: 1080 };

const rig: RigData = {
  "body": "body.png",
  "w": 355,
  "h": 529,
  "shoulderL": [
    79,
    294
  ],
  "shoulderR": [
    273,
    294
  ],
  "hipL": [
    145,
    523
  ],
  "hipR": [
    208,
    523
  ],
  "armLen": 222,
  "legLen": 155,
  "line": 6,
  "hand": 28,
  "source": "medieval-peasant.png",
  "hose": "#917961",
  "boot": "#67422c",
  "outline": "#141010"
};
const DIR = 'library/characters/main-character/rigs/medieval';

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

export default function RigTest() {
  const f = useCurrentFrame();
  const WALK_END = 72;
  const walking = f < WALK_END;
  const ph = (f / 30) * Math.PI * 2 * 1.6; // 1.6 steps per second
  const amp = interpolate(f, [0, 6, WALK_END - 10, WALK_END], [0, 1, 1, 0], clamp);
  const x = interpolate(f, [0, WALK_END], [-250, 820], { ...clamp, easing: Easing.bezier(0.3, 0.1, 0.4, 1) });
  const sw = Math.sin(ph) * 26 * amp;
  const point = interpolate(f, [88, 100], [0, 1], { ...clamp, easing: Easing.bezier(0.2, 0.8, 0.3, 1) });
  const pose: Pose = {
    legL: sw, legR: -sw,
    kneeL: Math.max(0, -Math.cos(ph)) * 30 * amp, kneeR: Math.max(0, Math.cos(ph)) * 30 * amp,
    armL: -sw * 0.8 - 8, elbowL: -10,
    armR: interpolate(point, [0, 1], [8 - sw * 0.8, 118]), elbowR: interpolate(point, [0, 1], [10, -6]),
    bob: Math.abs(Math.sin(ph)) * 14 * amp,
    lean: interpolate(point, [0, 1], [walking ? 2 * amp : 0, -2]),
  };
  const cam = interpolate(f, [0, 180], [1, 1.08], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${cam})`, transformOrigin: '60% 70%' }}>
        <Img src={staticFile('projects/film-1-football/bg/med-london-street.png')} style={{ width: 1920, height: 1080 }} />
        <div style={{ position: 'absolute', left: x - 85, top: 1010, width: 170, height: 26, borderRadius: '50%', background: 'rgba(60,35,15,0.35)', filter: 'blur(5px)' }} />
        <Rig dir={DIR} rig={rig} pose={pose} x={x} feetY={1030} height={560} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
