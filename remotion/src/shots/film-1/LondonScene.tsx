// Demo of the "everything moves" standard (owner, 2026-11-27): the medieval London street
// (film 1, shots 23-27) as ONE continuous animated scene instead of five still pictures.
// Pixels are still the AI drawings (background, characters, props); code makes them live:
// a moving camera, sky layer behind the roofs (drifting clouds, birds), a scrum with the
// cut-out puppets (AI arms/legs rotated, never code-drawn limbs), a bouncing ball, a cart that
// tips over, fleeing chickens, dust, angry merchants with comic marks, a proclamation that
// unrolls, and the game carrying on behind it.
import React from 'react';
import { AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { Puppet, PuppetData } from '../../lib/puppet';
import puppets from './puppets.json';

const P = (f: string) => staticFile(`projects/film-1-football/${f}`);
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = Easing.bezier(0.45, 0, 0.55, 1);
const outB = Easing.bezier(0.34, 1.56, 0.64, 1);
const hash = (n: number) => { const x = Math.sin(n * 127.1) * 43758.5; return x - Math.floor(x); };
const INK = '#2a170a';

// beats, in seconds from the start of shot 23
const T = { cartHit: 5.6, merchants: 9.9, crier: 15.9, sneak: 19.8 };

const Cloud: React.FC<{ x: number; y: number; s: number }> = ({ x, y, s }) => (
  <svg style={{ position: 'absolute', left: x, top: y, overflow: 'visible' }} width={220 * s} height={90 * s} viewBox="0 0 220 90">
    <path d="M20 70 Q5 70 8 55 Q10 38 32 42 Q36 18 64 22 Q80 2 108 14 Q130 0 150 20 Q178 14 184 38 Q212 38 210 58 Q210 72 192 72 Z"
      fill="#fff8ea" stroke={INK} strokeWidth={4} strokeLinejoin="round" />
  </svg>
);

const Bird: React.FC<{ x: number; y: number; t: number; s?: number }> = ({ x, y, t, s = 1 }) => {
  const w = Math.sin(t * 14) * 9;
  return (
    <svg style={{ position: 'absolute', left: x, top: y, overflow: 'visible' }} width={40 * s} height={20 * s} viewBox="-20 -10 40 20">
      <path d={`M-16 ${w} Q-8 -4 0 2 Q8 -4 16 ${w}`} fill="none" stroke={INK} strokeWidth={3.5} strokeLinecap="round" />
    </svg>
  );
};

// a little ink-outlined dust cloud that puffs up and fades
const Dust: React.FC<{ x: number; y: number; age: number; size?: number }> = ({ x, y, age, size = 1 }) => {
  if (age < 0 || age > 0.7) return null;
  const k = age / 0.7, r = (14 + 30 * Easing.out(Easing.quad)(k)) * size;
  return (
    <svg style={{ position: 'absolute', left: x - r * 2, top: y - r * 1.4, overflow: 'visible', opacity: 1 - k }} width={r * 4} height={r * 2}>
      {[-1, 0, 1].map((i) => <circle key={i} cx={r * 2 + i * r * 0.9} cy={r * (1.2 - Math.abs(i) * 0.2) - k * 20} r={r * (i === 0 ? 0.8 : 0.6)} fill="#d9c09a" stroke={INK} strokeWidth={3} />)}
    </svg>
  );
};

// comic anger mark that pops and throbs above a merchant
const Anger: React.FC<{ x: number; y: number; age: number }> = ({ x, y, age }) => {
  if (age < 0) return null;
  const s = interpolate(age, [0, 0.15, 0.3], [0, 1.3, 1], clamp) * (1 + Math.sin(age * 18) * 0.08);
  return (
    <svg style={{ position: 'absolute', left: x - 40, top: y - 40, overflow: 'visible', transform: `scale(${s}) rotate(${Math.sin(age * 25) * 6}deg)` }} width={80} height={80} viewBox="-40 -40 80 80">
      {[0, 90, 180, 270].map((a) => (
        <path key={a} transform={`rotate(${a})`} d="M6 -30 Q8 -10 28 -8" fill="none" stroke="#d8352a" strokeWidth={9} strokeLinecap="round" />
      ))}
    </svg>
  );
};

const Steam: React.FC<{ x: number; y: number; t: number; seed: number }> = ({ x, y, t, seed }) => (
  <>
    {[0, 1, 2].map((i) => {
      const age = (t * 1.6 + i / 3 + hash(seed)) % 1;
      return <div key={i} style={{ position: 'absolute', left: x + (i - 1) * 26 + Math.sin(age * 6) * 8, top: y - age * 90, width: 26 + age * 30, height: 26 + age * 30,
        borderRadius: '50%', background: '#fffaf0', border: `3px solid ${INK}`, opacity: 1 - age, transform: 'translate(-50%,-50%)' }} />;
    })}
  </>
);

export const LondonScene: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const fade = interpolate(f, [0, 8, len - 8, len], [0, 1, 1, 0], clamp);
  const main = (puppets as unknown as Record<string, PuppetData>)['main-character/medieval-peasant'];
  const c2 = (puppets as unknown as Record<string, PuppetData>)['character-2/medieval-peasant'];

  // ---- camera: shake in the scrum, punch in on the cart, pan the angry merchants, settle
  const scrum = t < T.merchants;
  const shake = scrum ? 4 : 0;
  const camS = interpolate(t, [0, T.cartHit - 0.2, T.cartHit + 0.15, T.cartHit + 1.6, T.merchants, T.merchants + 2.5, T.crier, T.crier + 1, 23],
    [1.04, 1.07, 1.14, 1.1, 1.08, 1.12, 1.12, 1.02, 1.05], { ...clamp, easing: ease });
  const camX = interpolate(t, [0, T.cartHit - 0.2, T.cartHit + 0.15, T.merchants, T.merchants + 2.5, T.merchants + 3.2, T.crier - 0.3, T.crier + 1, 23],
    [0, -20, -120, -80, -160, 160, 160, 0, -20], { ...clamp, easing: ease });
  // never show the edge of the picture: keep the pan inside what the zoom gives us
  const maxX = (1920 * (camS - 1)) / 2 - 12;
  const camXc = Math.max(-maxX, Math.min(maxX, camX));
  const sx = Math.sin(t * 37) * shake + Math.sin(t * 23) * shake * 0.6;
  const sy = Math.cos(t * 31) * shake * 0.7;

  // ---- scrum: two puppets hustling, the ball bouncing between them
  const runPh = t * 2 * Math.PI * 3.2;
  const inScrum = t < T.cartHit + 1.2;
  const stepL = inScrum ? Math.sin(runPh) * 24 : Math.sin(t * 2) * 3;
  const hop = (k: number) => (inScrum ? -Math.abs(Math.sin(runPh / 2 + k)) * 22 : 0);
  const mainX = interpolate(t, [0, T.cartHit, T.merchants, 23], [700, 760, 760, 740], clamp) + (inScrum ? Math.sin(t * 2.3) * 40 : 0);
  const c2X = interpolate(t, [0, T.cartHit, T.merchants, 23], [1220, 1160, 1160, 1180], clamp) + (inScrum ? Math.sin(t * 2.3 + 2) * 40 : 0);
  // climbing over each other right after the cart: main hops high, c2 dives
  const climb = interpolate(t, [T.cartHit + 0.3, T.cartHit + 0.7, T.cartHit + 1.1], [0, 1, 0], clamp);
  const flail = inScrum ? Math.sin(t * 17) * 50 : 0;
  // sheepish after the merchants explode, cheering at the very end
  const cheer = interpolate(t, [T.sneak + 1.1, T.sneak + 1.4], [0, 1], clamp);
  const shy = interpolate(t, [T.merchants, T.merchants + 0.4], [0, 1], clamp) * (1 - cheer);

  // ball: arcs between the players, then smashes into the cart, then sneaks behind the scroll
  let ballX = 960, ballY = 960, ballS = 1, ballOn = true, ballRot = f * 12;
  if (t < T.cartHit) {
    const k = (t % 1.1) / 1.1, dir = Math.floor(t / 1.1) % 2;
    const a = dir ? mainX + 90 : c2X - 90, b = dir ? c2X - 90 : mainX + 90;
    ballX = a + (b - a) * k; ballY = 975 - Math.sin(k * Math.PI) * 230;
    ballS = 1 + (Math.abs(Math.sin(k * Math.PI)) < 0.15 ? -0.12 : 0);
  } else if (t < T.cartHit + 0.25) {
    const k = (t - (T.cartHit - 0.1)) / 0.35;
    ballX = interpolate(k, [0, 1], [c2X - 60, 1500], clamp); ballY = interpolate(k, [0, 1], [930, 820], clamp);
  } else if (t < T.sneak + 0.6) {
    ballOn = t < T.cartHit + 2.5;
    const k = (t - T.cartHit - 0.25) / 2.2;
    ballX = 1500 + k * 380; ballY = 860 + Math.abs(Math.sin(k * 9)) * -90 * (1 - k) + k * 120; ballRot = f * 20;
  } else {
    const k = interpolate(t, [T.sneak + 0.6, T.sneak + 1.6], [0, 1], clamp);
    ballX = interpolate(k, [0, 1], [600, 1400]); ballY = 690 - Math.sin(k * Math.PI) * 160; ballS = 0.55;
  }

  // cart tipping over when the ball hits it
  const tip = interpolate(t, [T.cartHit + 0.05, T.cartHit + 0.45, T.cartHit + 0.6, T.cartHit + 0.75], [0, -78, -70, -74], { ...clamp, easing: Easing.out(Easing.quad) });
  const cartJolt = t > T.cartHit && t < T.cartHit + 0.12 ? 10 : 0;

  // chickens running away (AI chicken prop), flipped to the way they run
  const chickens = [
    { x0: 640, x1: -200, y: 985, t0: 0.6, dur: 3.2, s: 120 },
    { x0: 1300, x1: 2150, y: 1000, t0: 1.4, dur: 3.0, s: 110 },
    { x0: 1480, x1: 1700, y: 760, t0: T.cartHit + 0.1, dur: 1.4, s: 100, fly: true },
  ];

  // proclamation scroll
  const scrollIn = interpolate(t, [T.crier, T.crier + 0.35], [-700, 0], { ...clamp, easing: outB });
  const unroll = interpolate(t, [T.crier + 0.3, T.crier + 0.8], [0.08, 1], { ...clamp, easing: outB });
  const scrollOut = interpolate(t, [22.2, 22.6], [0, -900], clamp);
  const scrollShake = t > T.sneak + 0.6 && t < T.sneak + 1.0 ? Math.sin(t * 60) * 6 : 0;
  const text = 'BY ORDER OF THE KING\nNO FOOTBALL\nIN THE CITY!';
  const shown = Math.floor(interpolate(t, [T.crier + 0.8, T.crier + 2.4], [0, text.length], clamp));

  const feetY = 1015;
  return (
    <AbsoluteFill style={{ opacity: fade, backgroundColor: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transformOrigin: '50% 60%', transform: `translate(${camXc + sx}px, ${sy}px) scale(${camS})` }}>
        {/* sky layer behind the roofs: clouds drift, birds cross */}
        <AbsoluteFill style={{ background: 'linear-gradient(#fde9c4, #fbdcae)' }}>
          <Cloud x={520 + t * 14} y={30} s={1.1} />
          <Cloud x={1000 + t * 9} y={70} s={0.8} />
          <Cloud x={300 + t * 18} y={110} s={0.6} />
          {[0, 1, 2].map((i) => <Bird key={i} x={((t * (90 + i * 25) + i * 300) % 1100) + 450} y={90 + i * 35 + Math.sin(t * 2 + i) * 8} t={t + i} s={0.9 - i * 0.15} />)}
        </AbsoluteFill>
        {/* the street (AI background); its sky is cut away so the live sky shows through */}
        <Img src={P('bg/med-london-street.png')} style={{ position: 'absolute', width: 1920, height: 1080,
          WebkitMaskImage: `url(${P('bg/med-london-street.nosky.png')})`, maskImage: `url(${P('bg/med-london-street.nosky.png')})`,
          WebkitMaskSize: '1920px 1080px', maskSize: '1920px 1080px' } as React.CSSProperties} />

        {/* angry merchants (the stick figures in the stalls) */}
        <Anger x={372} y={540} age={t - T.merchants - 0.2} />
        {t > T.merchants + 0.4 && t < T.crier && <Steam x={372} y={560} t={t} seed={1} />}
        <Anger x={1552} y={530} age={t - T.merchants - 0.9} />
        {t > T.merchants + 1.1 && t < T.crier && <Steam x={1552} y={550} t={t} seed={2} />}

        {/* ball in the back street at the end (small, behind the scroll) */}
        {ballOn && ballS < 1 && <Img src={P('props/feather-ball.png')} style={{ position: 'absolute', left: ballX - 30, top: ballY - 25, width: 60, transform: `rotate(${ballRot}deg)` }} />}

        {/* cart in the foreground, tips over on the hit */}
        <Img src={P('props/cart.png')} style={{ position: 'absolute', left: 1380, top: 760 + cartJolt, width: 380, transformOrigin: '12% 92%', transform: `rotate(${tip}deg)` }} />
        <Dust x={1460} y={1000} age={t - T.cartHit - 0.4} size={1.6} />

        {/* shadows + puppets */}
        {[mainX, c2X].map((x, i) => <div key={i} style={{ position: 'absolute', left: x - 85, top: feetY - 12, width: 170, height: 24, borderRadius: '50%', background: 'rgba(50,30,10,0.33)', filter: 'blur(5px)' }} />)}
        <Puppet dir="library/characters/main-character/rigs/medieval-peasant" data={main} x={mainX} feetY={feetY} height={470}
          pose={{ legL: stepL, legR: -stepL, armL: flail + shy * 20 + cheer * 130, armR: -flail - shy * 20 - cheer * 130,
            dy: hop(0) - climb * 150 - (cheer ? Math.abs(Math.sin(t * 9)) * 30 : 0), rot: climb * -12 + shy * -3 }} />
        <Puppet dir="library/characters/character-2/rigs/medieval-peasant" data={c2} x={c2X} feetY={feetY} height={470}
          pose={{ legL: -stepL, legR: stepL + (t > T.sneak + 0.3 && t < T.sneak + 0.7 ? -60 : 0), dy: hop(1) + climb * 20, rot: climb * 18 + shy * 3 }} />

        {/* dust at every footfall during the scrum */}
        {inScrum && [0, 1, 2, 3].map((i) => {
          const per = 1 / 3.2, ph = (t + i * per * 0.5) % (per * 2);
          return <Dust key={i} x={(i % 2 ? c2X : mainX) + (i < 2 ? -40 : 40)} y={feetY} age={ph} size={0.8} />;
        })}

        {/* chickens */}
        {chickens.map((c, i) => {
          const k = (t - c.t0) / c.dur;
          if (k < 0 || k > 1) return null;
          const x = c.x0 + (c.x1 - c.x0) * k;
          const y = c.y - Math.abs(Math.sin(k * 30)) * 18 - (c.fly ? Math.sin(k * Math.PI) * 260 : 0);
          return <Img key={i} src={P('props/chicken.png')} style={{ position: 'absolute', left: x - c.s / 2, top: y - c.s, width: c.s,
            transform: `${c.x1 < c.x0 ? '' : 'scaleX(-1) '}rotate(${Math.sin(k * 40) * 10}deg)` }} />;
        })}

        {/* the ball in the foreground */}
        {ballOn && ballS >= 0.85 && <Img src={P('props/feather-ball.png')} style={{ position: 'absolute', left: ballX - 50, top: ballY - 80, width: 100, transform: `rotate(${ballRot}deg) scale(${ballS}, ${2 - ballS})` }} />}
      </AbsoluteFill>

      {/* proclamation (screen space, so it stays readable while the camera moves) */}
      {t > T.crier - 0.1 && (
        <div style={{ position: 'absolute', left: 960 - 300, top: 190 + scrollIn + scrollOut, width: 600, height: 300, transform: `rotate(${scrollShake}deg)` }}>
          <div style={{ position: 'absolute', left: 30, right: 30, top: 0, height: 300, transformOrigin: '50% 0%', transform: `scaleY(${unroll})`,
            background: 'linear-gradient(#f6e7c4, #efd9ab)', border: `6px solid ${INK}`, borderRadius: 14, boxShadow: '0 12px 0 rgba(42,23,10,0.25)' }} />
          {[0, 1].map((e) => (
            <div key={e} style={{ position: 'absolute', left: 0, right: 0, top: e ? 300 * unroll - 22 : -22, height: 44, borderRadius: 22,
              background: 'linear-gradient(#e9cf99, #c9a467)', border: `6px solid ${INK}` }} />
          ))}
          {unroll > 0.95 && (
            <div style={{ position: 'absolute', left: 80, right: 80, top: 55, textAlign: 'center', fontFamily: 'Georgia, serif', fontWeight: 700, fontSize: 38, lineHeight: 1.3, color: '#3a2412', whiteSpace: 'pre-line' }}>
              {text.slice(0, shown)}
            </div>
          )}
          {shown >= text.length && (
            <div style={{ position: 'absolute', right: 70, bottom: 36, width: 80, height: 80, borderRadius: '50%', background: '#b8261c', border: `5px solid ${INK}`,
              transform: `scale(${interpolate(t, [T.crier + 2.5, T.crier + 2.65, T.crier + 2.8], [2, 0.9, 1], clamp)}) rotate(-12deg)` }} />
          )}
        </div>
      )}
    </AbsoluteFill>
  );
};
