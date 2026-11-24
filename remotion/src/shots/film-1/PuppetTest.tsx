import React from 'react';
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, Easing } from 'remotion';
import { Puppet, PuppetData } from '../../lib/puppet';
import puppets from './puppets.json';
export const compositionConfig = { id: 'Film1PuppetTest', durationInSeconds: 6, fps: 30, width: 1920, height: 1080 };
const c = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export default function PuppetTest() {
  const f = useCurrentFrame();
  const d = (puppets as any)['main-character/medieval-peasant'] as PuppetData;
  // wave (0-60), wind-up + kick (60-100), arms up cheer (110-180)
  const wave = f < 60 ? -110 + Math.sin(f / 4) * 25 : 0;
  const kick = interpolate(f, [60, 78, 86, 100], [0, 25, -70, 0], { ...c, easing: Easing.bezier(0.4, 0, 0.6, 1) });
  const cheer = interpolate(f, [105, 115], [0, 1], c);
  const hop = f > 110 ? Math.abs(Math.sin((f - 110) / 5)) * -30 : 0;
  const armR = f < 60 ? wave : interpolate(cheer, [0, 1], [interpolate(f, [60, 86], [0, 35], c), -130]);
  const armL = interpolate(cheer, [0, 1], [interpolate(f, [60, 86], [0, -30], c), 130]);
  const ballT = interpolate(f, [86, 130], [0, 1], c);
  const bx = 1040 + ballT * 700, by = 1000 - Math.sin(ballT * Math.PI) * 420;
  return (
    <AbsoluteFill>
      <Img src={staticFile('projects/film-1-football/bg/med-london-street.png')} style={{ width: 1920, height: 1080 }} />
      <div style={{ position: 'absolute', left: 860 - 90, top: 1018, width: 180, height: 26, borderRadius: '50%', background: 'rgba(50,30,10,0.33)', filter: 'blur(5px)' }} />
      <Puppet dir="library/characters/main-character/rigs/medieval-peasant" data={d} pose={{ armL, armR, legR: kick, dy: hop, rot: kick < -20 ? -4 : 0 }} x={860} feetY={1030} height={560} />
      <Img src={staticFile('projects/film-1-football/props/feather-ball.png')} style={{ position: 'absolute', left: bx - 50, top: by - 90, width: 100, transform: `rotate(${f * 9}deg)` }} />
    </AbsoluteFill>
  );
}
