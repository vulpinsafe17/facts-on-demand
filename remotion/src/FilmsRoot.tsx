import React from 'react';
import { Composition } from 'remotion';
import RigTest, { compositionConfig as rigTest } from './shots/film-1/RigTest';
import RigLineup, { compositionConfig as rigLineup } from './shots/film-1/RigLineup';
import Film1, { compositionConfig as film1 } from './shots/film-1/Film1';
import PuppetTest, { compositionConfig as puppetTest } from './shots/film-1/PuppetTest';
import Film1Full, { compositionConfig as film1Full } from './shots/film-1/Film1Full';
import Film1_3D, { compositionConfig as film1_3d } from './shots/film-1/Film1_3D';
import Film1Rough, { compositionConfig as film1Rough } from './shots/film-1/Film1Rough';

const films = [{ Comp: RigTest, config: rigTest }, { Comp: Film1Rough, config: film1Rough }, { Comp: RigLineup, config: rigLineup }, { Comp: Film1, config: film1 }, { Comp: PuppetTest, config: puppetTest }, { Comp: Film1_3D, config: film1_3d }, { Comp: Film1Full, config: film1Full }];

export const FilmsRoot: React.FC = () => (
  <>
    {films.map(({ Comp, config }) => (
      <Composition key={config.id} id={config.id} component={Comp} durationInFrames={Math.round(config.durationInSeconds * config.fps)} fps={config.fps} width={config.width} height={config.height} />
    ))}
  </>
);
