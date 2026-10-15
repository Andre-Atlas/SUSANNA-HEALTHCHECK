import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, EASE, fontFamily, glass } from '../theme';
import { Counter, Eyebrow, Kinetic, Rise } from '../components/ui';

const STATS = [
  { n: 151, t: 'testes automatizados', s: 'backend, sem dados mockados' },
  { n: 43, t: 'requisitos', s: '25 funcionais · 18 não funcionais' },
  { n: 383, t: 'unidades de saúde', s: 'no mapa, com dados oficiais' },
  { n: 33, t: 'regiões administrativas', s: 'todo o Distrito Federal' },
];

/** Resultados e conclusão. Números conferidos no repositório. */
export const Results: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily, padding: '170px 120px 100px', display: 'flex', flexDirection: 'column' }}>
      <Eyebrow n="05" label="Conclusão e resultados" />
      <Kinetic words={['Pronta', 'para', 'o', { b: 'cidadão.' }]} delay={4} size={76} style={{ marginTop: 26 }} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 28, marginTop: 64 }}>
        {STATS.map((x, i) => {
          const d = 15 + i * 15;
          const p = interpolate(f, [d, d + 18], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
          return (
            <div key={x.t} style={{ ...glass, borderRadius: 32, padding: '34px 34px 38px', opacity: p, transform: `translateY(${(1 - p) * 26}px)` }}>
              <Counter to={x.n} delay={d} size={124} />
              <div style={{ fontSize: 32, fontWeight: 600, color: C.ink, marginTop: 6 }}>{x.t}</div>
              <div style={{ fontSize: 24, color: C.mut, marginTop: 6 }}>{x.s}</div>
            </div>
          );
        })}
      </div>
      <Rise delay={150} style={{ marginTop: 'auto' }}>
        <div style={{ ...glass, borderRadius: 30, padding: '30px 40px', fontSize: 40, fontWeight: 300, letterSpacing: '-0.02em', color: C.ink, lineHeight: 1.3 }}>
          IA que orienta com <b style={{ fontWeight: 600, color: C.b2 }}>evidências</b> e deixa a decisão com o cidadão.
        </div>
      </Rise>
    </AbsoluteFill>
  );
};

/** Encerramento: mascote, marca e repositório. */
export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const up = spring({ frame: f, fps, config: { damping: 18, mass: 0.8 } });
  return (
    <AbsoluteFill style={{ fontFamily, alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <Img
        src={staticFile('suzanna-hero.webp')}
        style={{ height: 400, transform: `translateY(${(1 - up) * 60 + Math.sin(f / 18) * 5}px)`, filter: 'drop-shadow(0 30px 40px rgba(30,64,175,.22))' }}
      />
      <div style={{ fontSize: 110, letterSpacing: '-0.05em', lineHeight: 1, marginTop: 18 }}>
        <span style={{ fontWeight: 600, color: C.b2 }}>SUS</span>
        <span style={{ fontWeight: 300, color: C.ink }}>ANNA</span>
      </div>
      <Rise delay={10}>
        <div style={{ fontSize: 30, color: C.mut, marginTop: 14 }}>Residência em Inteligência Artificial · Instituto Eldorado</div>
      </Rise>
      <Rise delay={18}>
        <div style={{ ...glass, borderRadius: 99, padding: '14px 30px', fontSize: 28, fontWeight: 500, color: C.b1, marginTop: 26 }}>
          github.com/Andre-Atlas/SUSANNA-HEALTHCHECK
        </div>
      </Rise>
    </AbsoluteFill>
  );
};
