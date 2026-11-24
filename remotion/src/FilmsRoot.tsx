import React from 'react';
import { Composition } from 'remotion';
import RigTest, { compositionConfig as rigTest } from './shots/film-1/RigTest';
import Film1Rough, { compositionConfig as film1Rough } from './shots/film-1/Film1Rough';

const films = [{ Comp: RigTest, config: rigTest }, { Comp: Film1Rough, config: film1Rough }];

export const FilmsRoot: React.FC = () => (
  <>
    {films.map(({ Comp, config }) => (
      <Composition key={config.id} id={config.id} component={Comp} durationInFrames={Math.round(config.durationInSeconds * config.fps)} fps={config.fps} width={config.width} height={config.height} />
    ))}
  </>
);
