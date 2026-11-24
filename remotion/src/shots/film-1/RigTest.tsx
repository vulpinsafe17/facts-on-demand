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
const front: RigData = {   "body": "body.png",   "w": 355,   "h": 529,   "shoulderL": [     79,     294   ],   "shoulderR": [     273,     294   ],   "hipL": [     145,     523   ],   "hipR": [     208,     523   ],   "armLen": 222,   "legLen": 97,   "line": 6,   "hand": 28,   "source": "medieval-peasant.png",   "bootL": {     "file": "bootL.png",     "w": 92,     "h": 64,     "pivot": [       61,       6     ]   },   "bootR": {     "file": "bootR.png",     "w": 91,     "h": 64,     "pivot": [       29,       6     ]   },   "hose": "#917961",   "boot": "#67422c",   "outline": "#141010" };
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
  // turn to camera: a clean one-frame swap (no see-through ghost) with a small
  // squash-and-stretch 'pop' so the turn reads as a movement
  const showFront = f >= T0 + 1;
  const popX = interpolate(f, [T0 + 1, T0 + 3, T0 + 6, T0 + 9], [0.86, 1.05, 0.98, 1], clamp);
  const popY = interpolate(f, [T0 + 1, T0 + 3, T0 + 6, T0 + 9], [1.04, 0.97, 1.01, 1], clamp);
  const sideOp = showFront ? 0 : 1, frontOp = showFront ? 1 : 0;
  const sideScale = 1, frontScale = popX;
  const point = interpolate(f, [T0 + 16, T0 + 26], [0, 1], { ...clamp, easing: Easing.bezier(0.2, 0.8, 0.3, 1) });
  const pose: Pose = { legL: 0, legR: 0, armL: -8, elbowL: -8, armR: interpolate(point, [0, 1], [8, 118]), elbowR: interpolate(point, [0, 1], [8, -6]), lean: interpolate(point, [0, 1], [0, -2]) };
  const cam = interpolate(f, [0, 210], [1, 1.07], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${cam})`, transformOrigin: '55% 75%' }}>
        <Img src={staticFile('projects/film-1-football/bg/med-london-street.png')} style={{ width: 1920, height: 1080 }} />
        <div style={{ position: 'absolute', left: x - 80, top: GROUND - 14, width: 160, height: 26, borderRadius: '50%', background: 'rgba(60,35,15,0.35)', filter: 'blur(5px)' }} />
        {sideOp > 0 && (
          <div style={{ position: 'absolute', inset: 0, opacity: sideOp, transform: `scaleX(${sideScale})`, transformOrigin: `${x}px 0px` }}>
            <SideRig dir={SIDE} rig={side} x={x} groundY={GROUND} height={H} phase={phase} amp={amp} />
          </div>
        )}
        {frontOp > 0 && (
          <div style={{ position: 'absolute', inset: 0, opacity: frontOp, transform: `scale(${frontScale}, ${popY})`, transformOrigin: `${x}px ${GROUND}px` }}>
            <Rig dir={FRONT} rig={front} pose={pose} x={x} feetY={GROUND} height={H} />
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
}
