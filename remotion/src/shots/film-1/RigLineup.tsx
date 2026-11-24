import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Rig, RigData } from '../../lib/rig';
import rigs from './rigs.json';
export const compositionConfig = { id: 'Film1RigLineup', durationInSeconds: 1, fps: 30, width: 2600, height: 1100 };
export default function RigLineup() {
  const keys = Object.keys(rigs);
  return (
    <AbsoluteFill style={{ background: '#8fb0c8' }}>
      {keys.map((k, i) => (
        <React.Fragment key={k}>
          <Rig dir={`library/characters/${k.split('/')[0]}/rigs/${k.split('/')[1]}`} rig={(rigs as any)[k] as RigData} pose={{ armL: -10, armR: 10, legL: 0, legR: 0 }} x={110 + i * 195} feetY={1040} height={420} />
          <div style={{ position: 'absolute', left: 20 + i * 195, top: 20 + (i % 2) * 30, width: 180, fontSize: 18, fontFamily: 'sans-serif' }}>{k}</div>
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
}
