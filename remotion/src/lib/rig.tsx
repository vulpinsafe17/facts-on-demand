import React from 'react';
import { Img, staticFile } from 'remotion';

// Hybrid character rig: AI-drawn head+torso (body.png from tools/rig_parts.py)
// + stick arms/legs drawn in code so they can move freely.
// Angles are in degrees, 0 = straight down, +90 = pointing to screen-right.

export type RigData = {
  body: string; w: number; h: number;
  shoulderL: [number, number]; shoulderR: [number, number];
  hipL: [number, number]; hipR: [number, number];
  armLen: number; legLen: number; line: number; hand: number;
  hose: string; boot: string; outline: string;
};

export type Pose = {
  armL: number; armR: number; elbowL?: number; elbowR?: number;
  legL: number; legR: number; kneeL?: number; kneeR?: number;
  bob?: number; lean?: number;
};

const rad = (d: number) => (d * Math.PI) / 180;
const step = (x: number, y: number, len: number, ang: number): [number, number] => [x + len * Math.sin(rad(ang)), y + len * Math.cos(rad(ang))];

export const Rig: React.FC<{ dir: string; rig: RigData; pose: Pose; x: number; feetY: number; height: number; flip?: boolean }> = ({ dir, rig, pose, x, feetY, height, flip }) => {
  const totalH = rig.h + rig.legLen;
  const s = height / totalH;
  const W = rig.w;
  const lw = rig.line * 2.2;
  const legW = rig.line * 5.5;
  const bob = pose.bob ?? 0;
  const leg = (hip: [number, number], ang: number, knee: number, side: 1 | -1) => {
    const L = rig.legLen * 0.46;
    const [kx, ky] = step(hip[0], hip[1] - 4, L, ang);
    const [fx, fy] = step(kx, ky, L, ang - knee);
    const bootPath = `M${fx - 18},${fy - 10} h30 q${side * 14},6 ${side * 22},18 q4,10 -6,12 h${side > 0 ? -58 : -26} q-8,0 -8,-10 z`;
    return (
      <g>
        <polyline points={`${hip[0]},${hip[1] - 4} ${kx},${ky} ${fx},${fy}`} fill="none" stroke={rig.outline} strokeWidth={legW + 9} strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={`${hip[0]},${hip[1] - 4} ${kx},${ky} ${fx},${fy}`} fill="none" stroke={rig.hose} strokeWidth={legW} strokeLinecap="round" strokeLinejoin="round" />
        <path d={bootPath} fill={rig.boot} stroke={rig.outline} strokeWidth={6} strokeLinejoin="round" />
      </g>
    );
  };
  const arm = (sh: [number, number], ang: number, elbow: number) => {
    const L = rig.armLen * 0.5;
    const [ex, ey] = step(sh[0], sh[1], L, ang);
    const [hx, hy] = step(ex, ey, L, ang + elbow);
    return (
      <g>
        <polyline points={`${sh[0]},${sh[1]} ${ex},${ey} ${hx},${hy}`} fill="none" stroke={rig.outline} strokeWidth={lw} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={hx} cy={hy} r={rig.hand} fill="#fff" stroke={rig.outline} strokeWidth={lw * 0.9} />
      </g>
    );
  };
  const pad = 400;
  return (
    <div style={{ position: 'absolute', left: x - (W * s) / 2, top: feetY - totalH * s, width: W * s, height: totalH * s, transform: `${flip ? 'scaleX(-1)' : ''} rotate(${pose.lean ?? 0}deg)`, transformOrigin: '50% 100%' }}>
      <svg width={(W + 2 * pad) * s} height={(totalH + pad) * s} viewBox={`${-pad} ${-pad / 2} ${W + 2 * pad} ${totalH + pad}`} style={{ position: 'absolute', left: -pad * s, top: (-pad / 2) * s, overflow: 'visible' }}>
        <g transform={`translate(0 ${-bob})`}>
          {leg(rig.hipL, pose.legL, pose.kneeL ?? 0, -1)}
          {leg(rig.hipR, pose.legR, pose.kneeR ?? 0, 1)}
          {arm(rig.shoulderL, pose.armL, pose.elbowL ?? 0)}
          {arm(rig.shoulderR, pose.armR, pose.elbowR ?? 0)}
          <image href={staticFile(`${dir}/${rig.body}`)} x={0} y={0} width={W} height={rig.h} />
        </g>
      </svg>
    </div>
  );
};
