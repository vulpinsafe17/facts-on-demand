import React from 'react';
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { Rig, RigData, Pose, SideRig, SideRigData, stepLength } from '../../lib/rig';

// Motion test v2: side-view walk with planted feet (phase driven by distance),
// AI boots kept as sprites, then he turns to camera and points.
export const compositionConfig = { id: 'Film1RigTest', durationInSeconds: 7, fps: 30, width: 1920, height: 1080 };

const side: SideRigData = {
  "view": "side",
  "body": "body.png",
  "boot": "boot.png",
  "w": 290,
  "h": 521,
  "hip": [
    154,
    508
  ],
  "shoulder": [
    154,
    300
  ],
  "legLen": 116,
  "legW": 52,
  "armLen": 198,
  "hand": 24,
  "line": 6,
  "bootPivot": [
    36,
    6
  ],
  "bootW": 107,
  "bootH": 63,
  "hose": "#917860",
  "bootColor": "#66422c",
  "outline": "#141010",
  "source": "medieval-peasant.png"
};
const front: RigData = {
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
const SIDE = 'library/characters/main-character/rigs/medieval-side';
const FRONT = 'library/characters/main-character/rigs/medieval';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const H = 560, GROUND = 1030;
const STEPS = 10;
const WALK_END = 110; // frames

export default function RigTest() {
  const f = useCurrentFrame();
  const stepLen = stepLength(side, H);
  const x0 = -150;
  const dist = STEPS * stepLen;
  // ease in/out on distance; phase follows distance => feet never slide
  const d = interpolate(f, [0, WALK_END], [0, dist], { ...clamp, easing: Easing.bezier(0.35, 0, 0.45, 1) });
  const x = x0 + d;
  const phase = (d / stepLen) * Math.PI;
  const amp = interpolate(f, [0, 8, WALK_END - 14, WALK_END], [0.5, 1, 1, 0], clamp);
  // turn to camera: squash side view to 0 width, then open the front view
  const T0 = WALK_END + 2;
  const turn = interpolate(f, [T0, T0 + 4, T0 + 8], [1, 0, 1], clamp);
  const showFront = f >= T0 + 4;
  const point = interpolate(f, [T0 + 16, T0 + 26], [0, 1], { ...clamp, easing: Easing.bezier(0.2, 0.8, 0.3, 1) });
  const pose: Pose = { legL: 0, legR: 0, armL: -8, elbowL: -8, armR: interpolate(point, [0, 1], [8, 118]), elbowR: interpolate(point, [0, 1], [8, -6]), lean: interpolate(point, [0, 1], [0, -2]) };
  const cam = interpolate(f, [0, 210], [1, 1.07], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${cam})`, transformOrigin: '55% 75%' }}>
        <Img src={staticFile('projects/film-1-football/bg/med-london-street.png')} style={{ width: 1920, height: 1080 }} />
        <div style={{ position: 'absolute', left: x - 80, top: GROUND - 14, width: 160, height: 26, borderRadius: '50%', background: 'rgba(60,35,15,0.35)', filter: 'blur(5px)' }} />
        <div style={{ position: 'absolute', inset: 0, transform: `scaleX(${turn})`, transformOrigin: `${x}px 0px` }}>
          {showFront
            ? <Rig dir={FRONT} rig={front} pose={pose} x={x} feetY={GROUND} height={H} />
            : <SideRig dir={SIDE} rig={side} x={x} groundY={GROUND} height={H} phase={phase} amp={amp} />}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
