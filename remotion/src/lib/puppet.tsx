import React from 'react';
import { Img, staticFile } from 'remotion';

// Cut-out puppet: every piece is AI pixels from the character sheet (tools/puppet_parts.py).
// Code only rotates the pieces around their joints. Angles in degrees, CSS direction
// (positive = clockwise). armL up/out = +, armR up/out = -, legR kick forward(right) = -.
export type PuppetPart = { file: string; x: number; y: number; w: number; h: number; pivot?: [number, number] };
export type PuppetData = { W: number; H: number; parts: Record<string, PuppetPart> };
export type PuppetPose = { armL?: number; armR?: number; legL?: number; legR?: number; rot?: number; dy?: number; sx?: number; sy?: number };

export const Puppet: React.FC<{ dir: string; data: PuppetData; pose: PuppetPose; x: number; feetY: number; height: number; flip?: boolean }> = ({ dir, data, pose, x, feetY, height, flip }) => {
  const s = height / data.H;
  const piece = (name: string, ang = 0) => {
    const p = data.parts[name];
    if (!p) return null;
    const pv = p.pivot ?? [p.w / 2, 0];
    return (
      <Img key={name} src={staticFile(`${dir}/${p.file}`)} style={{ position: 'absolute', left: p.x * s, top: p.y * s, width: p.w * s, height: p.h * s,
        transformOrigin: `${pv[0] * s}px ${pv[1] * s}px`, transform: `rotate(${ang}deg)` }} />
    );
  };
  return (
    <div style={{ position: 'absolute', left: x - (data.W * s) / 2, top: feetY - data.H * s + (pose.dy ?? 0), width: data.W * s, height: data.H * s,
      transformOrigin: '50% 100%', transform: `${flip ? 'scaleX(-1) ' : ''}rotate(${pose.rot ?? 0}deg) scale(${pose.sx ?? 1}, ${pose.sy ?? 1})` }}>
      {piece('legL', pose.legL)}{piece('legR', pose.legR)}
      {piece('body')}
      {piece('armL', pose.armL)}{piece('armR', pose.armR)}
    </div>
  );
};
