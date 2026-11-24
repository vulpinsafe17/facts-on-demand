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

// ---------------------------------------------------------------------------
// SIDE-VIEW WALKING RIG (tools/rig_side.py): AI head+torso, AI boot sprite,
// code-drawn legs/arms. Walk is driven by distance travelled so the stance foot
// stays planted (no sliding): phase = PI per step, step length = 2 L sin(A).
// ---------------------------------------------------------------------------
export type SideRigData = {
  body: string; boot: string; w: number; h: number;
  hip: [number, number]; shoulder: [number, number];
  legLen: number; legW: number; armLen: number; hand: number; line: number;
  bootPivot: [number, number]; bootW: number; bootH: number;
  hose: string; outline: string;
};

export const WALK_AMP = 30; // thigh swing, degrees
export const sideTotalH = (r: SideRigData) => r.hip[1] + r.legLen + (r.bootH - r.bootPivot[1]);
export const stepLength = (r: SideRigData, height: number) => 2 * r.legLen * Math.sin(rad(WALK_AMP)) * (height / sideTotalH(r));

export const SideRig: React.FC<{ dir: string; rig: SideRigData; x: number; groundY: number; height: number; phase: number; amp?: number; flip?: boolean; armOverride?: number }> = ({ dir, rig, x, groundY, height, phase, amp = 1, flip, armOverride }) => {
  const s = height / sideTotalH(rig);
  const L = rig.legLen, half = L / 2, A = WALK_AMP * amp, K = 55 * amp;
  const thA = A * Math.sin(phase), thB = -thA;
  const kA = Math.max(0, Math.cos(phase)) * K, kB = Math.max(0, -Math.cos(phase)) * K;
  const stanceTh = Math.cos(phase) < 0 ? thA : thB;
  const hipLift = L * (1 - Math.cos(rad(stanceTh))); // hip drops when the legs are apart
  const hip: [number, number] = [rig.hip[0], rig.hip[1] + hipLift];
  const leg = (th: number, k: number, front: boolean) => {
    const [kx, ky] = step(hip[0], hip[1], half, th);
    const shin = th - k;
    const [ax, ay] = step(kx, ky, half, shin);
    const tone = front ? rig.hose : shade(rig.hose, 0.82);
    return (
      <g>
        <polyline points={`${hip[0]},${hip[1]} ${kx},${ky} ${ax},${ay}`} fill="none" stroke={rig.outline} strokeWidth={rig.legW} strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={`${hip[0]},${hip[1]} ${kx},${ky} ${ax},${ay}`} fill="none" stroke={tone} strokeWidth={rig.legW - 12} strokeLinecap="round" strokeLinejoin="round" />
        <image href={staticFile(`${dir}/${rig.boot}`)} x={ax - rig.bootPivot[0]} y={ay - rig.bootPivot[1]} width={rig.bootW} height={rig.bootH}
          transform={`rotate(${(-(shin) * 0.35 + k * 0.25).toFixed(2)} ${ax} ${ay})`} style={front ? undefined : { filter: 'brightness(0.85)' }} />
      </g>
    );
  };
  const arm = (ang: number, front: boolean) => {
    const sh = rig.shoulder, Lh = rig.armLen / 2;
    const [ex, ey] = step(sh[0], sh[1], Lh, ang);
    const [hx, hy] = step(ex, ey, Lh, ang + Math.max(0, ang) * 0.6);
    const lw = rig.line * 2.2;
    return (
      <g opacity={front ? 1 : 0.9}>
        <polyline points={`${sh[0]},${sh[1]} ${ex},${ey} ${hx},${hy}`} fill="none" stroke={rig.outline} strokeWidth={lw} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={hx} cy={hy} r={rig.hand} fill={front ? '#fff' : '#e8e8e8'} stroke={rig.outline} strokeWidth={lw * 0.9} />
      </g>
    );
  };
  const totalH = sideTotalH(rig);
  const pad = 300;
  const bodyDy = hipLift;
  return (
    <div style={{ position: 'absolute', left: x - rig.hip[0] * s, top: groundY - totalH * s, width: rig.w * s, height: totalH * s, transform: flip ? 'scaleX(-1)' : undefined, transformOrigin: `${rig.hip[0] * s}px 100%` }}>
      <svg width={(rig.w + 2 * pad) * s} height={(totalH + 2 * pad) * s} viewBox={`${-pad} ${-pad} ${rig.w + 2 * pad} ${totalH + 2 * pad}`} style={{ position: 'absolute', left: -pad * s, top: -pad * s, overflow: 'visible' }}>
        <g transform={`translate(0 ${bodyDy}) rotate(${2 * amp} ${rig.hip[0]} ${rig.hip[1]})`}>{arm(armOverride ?? thA * 0.6, false)}</g>
        {leg(thB, kB, false)}
        {leg(thA, kA, true)}
        <g transform={`translate(0 ${bodyDy}) rotate(${2 * amp} ${rig.hip[0]} ${rig.hip[1]})`}>
          <image href={staticFile(`${dir}/${rig.body}`)} x={0} y={0} width={rig.w} height={rig.h} />
          {arm(-thA * 0.7 + 4, true)}
        </g>
      </svg>
    </div>
  );
};

function shade(hex: string, f: number) {
  const n = parseInt(hex.slice(1), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => Math.round(v * f));
  return `rgb(${c.join(',')})`;
}
