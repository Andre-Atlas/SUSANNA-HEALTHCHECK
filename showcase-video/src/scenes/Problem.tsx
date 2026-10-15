import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { C, EASE, fontFamily, glass } from '../theme';
import { Eyebrow, Kinetic, Rise } from '../components/ui';

const SOURCES = [
  { t: 'saude.df.gov.br', x: 80, y: 40, d: 6 },
  { t: 'gov.br/saude', x: 420, y: 150, d: 10 },
  { t: 'CNES · DATASUS', x: 40, y: 290, d: 14 },
  { t: 'Meu SUS Digital', x: 380, y: 420, d: 18 },
  { t: 'Carta de Serviços SES-DF', x: 60, y: 560, d: 22 },
];

/** Contexto e problema: informação oficial fragmentada e desinformação. */
export const Problem: React.FC = () => {
  const f = useCurrentFrame();
  const strike = interpolate(f, [62, 80], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ fontFamily, padding: '170px 120px 100px' }}>
      <div style={{ display: 'flex', height: '100%', gap: 60 }}>
        <div style={{ flex: 1.15, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 36 }}>
          <Eyebrow n="01" label="Contexto e problema" />
          <Kinetic
            words={['A', 'informação', 'de', 'saúde', 'do', 'DF', 'está', { b: 'espalhada' }, 'e', 'nem', 'sempre', 'é', 'confiável.']}
            delay={4}
            stagger={2}
            size={78}
          />
          <Rise delay={48}>
            <div style={{ ...glass, borderRadius: 24, padding: '24px 30px', fontSize: 30, lineHeight: 1.4, color: C.mut, maxWidth: 900 }}>
              <span style={{ color: C.b1, fontWeight: 600 }}>Pergunta essencial: </span>
              como a IA pode ajudar a avaliar a confiabilidade da informação{' '}
              <span style={{ color: C.ink, fontWeight: 500 }}>sem substituir o pensamento crítico?</span>
            </div>
          </Rise>
        </div>
        <div style={{ flex: 0.85, position: 'relative' }}>
          {SOURCES.map((s, i) => {
            const p = interpolate(f, [s.d, s.d + 20], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const drift = Math.sin(f / 22 + i * 1.7) * 8;
            return (
              <div
                key={s.t}
                style={{
                  ...glass,
                  position: 'absolute',
                  left: s.x,
                  top: s.y + drift,
                  borderRadius: 99,
                  padding: '16px 28px',
                  fontSize: 28,
                  fontWeight: 500,
                  color: C.ink,
                  opacity: p,
                  transform: `translateY(${(1 - p) * 20}px) rotate(${(i % 2 ? 1 : -1) * 2}deg)`,
                  whiteSpace: 'nowrap',
                }}
              >
                <span style={{ display: 'inline-block', width: 12, height: 12, borderRadius: 6, background: C.b3, marginRight: 14, verticalAlign: 2 }} />
                {s.t}
              </div>
            );
          })}
          {/* desinformação */}
          <div
            style={{
              position: 'absolute',
              left: 300,
              top: 690,
              borderRadius: 99,
              padding: '16px 28px',
              fontSize: 28,
              fontWeight: 500,
              background: 'rgba(220,38,38,0.08)',
              border: '1px solid rgba(220,38,38,0.25)',
              color: '#b91c1c',
              opacity: interpolate(f, [30, 46], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
              whiteSpace: 'nowrap',
            }}
          >
            “Chá caseiro cura dengue?”
            <div style={{ position: 'absolute', left: 22, right: 22, top: '50%', height: 3, borderRadius: 2, background: '#b91c1c', transform: `scaleX(${strike})`, transformOrigin: 'left' }} />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
