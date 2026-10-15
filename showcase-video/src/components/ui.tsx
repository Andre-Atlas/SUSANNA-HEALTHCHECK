import React from 'react';
import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, EASE, fontFamily, glass } from '../theme';

/** Progresso 0→1 com easing padrão a partir de `delay` quadros, durando `dur`. */
export const useRise = (delay = 0, dur = 18) => {
  const f = useCurrentFrame();
  return interpolate(f, [delay, delay + dur], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
};

export const Glass: React.FC<{ style?: React.CSSProperties; radius?: number; children?: React.ReactNode }> = ({ style, radius = 28, children }) => (
  <div style={{ ...glass, borderRadius: radius, ...style }}>{children}</div>
);

/** Sobe e aparece (sem exageros), para blocos inteiros. */
export const Rise: React.FC<{ delay?: number; dist?: number; style?: React.CSSProperties; children: React.ReactNode }> = ({ delay = 0, dist = 18, style, children }) => {
  const p = useRise(delay);
  return <div style={{ opacity: p, transform: `translateY(${(1 - p) * dist}px)`, ...style }}>{children}</div>;
};

type Word = string | { b: string };
/**
 * Texto cinético sóbrio: palavras surgem em sequência curta. Use {b: 'palavra'} para o destaque
 * em azul (peso 600), como nos títulos da plataforma.
 */
export const Kinetic: React.FC<{ words: Word[]; delay?: number; stagger?: number; size?: number; weight?: number; color?: string; style?: React.CSSProperties }> = ({
  words,
  delay = 0,
  stagger = 2,
  size = 76,
  weight = 300,
  color = C.ink,
  style,
}) => {
  const f = useCurrentFrame();
  return (
    <div style={{ fontFamily, fontSize: size, fontWeight: weight, color, letterSpacing: '-0.035em', lineHeight: 1.08, ...style }}>
      {words.map((w, i) => {
        const p = interpolate(f, [delay + i * stagger, delay + i * stagger + 16], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const bold = typeof w !== 'string';
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              opacity: p,
              transform: `translateY(${(1 - p) * 0.35}em)`,
              marginRight: '0.24em',
              fontWeight: bold ? 600 : weight,
              color: bold ? C.b2 : color,
            }}
          >
            {bold ? w.b : w}
          </span>
        );
      })}
    </div>
  );
};

export const Eyebrow: React.FC<{ n: string; label: string; delay?: number }> = ({ n, label, delay = 0 }) => (
  <Rise delay={delay} dist={10}>
    <div style={{ fontFamily, display: 'inline-flex', alignItems: 'center', gap: 14, fontSize: 24, fontWeight: 500, color: C.b1, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
      <span style={{ ...glass, borderRadius: 99, padding: '6px 16px', color: C.b2, fontWeight: 600, letterSpacing: 0 }}>{n}</span>
      {label}
    </div>
  </Rise>
);

export const Pill: React.FC<{ children: React.ReactNode; tone?: 'blue' | 'soft' | 'ok'; style?: React.CSSProperties }> = ({ children, tone = 'soft', style }) => {
  const tones = {
    blue: { background: `linear-gradient(180deg, ${C.b3}, ${C.b2} 60%, ${C.b1})`, color: '#fff', boxShadow: '0 8px 20px rgba(37,99,235,.32), inset 0 1px 0 rgba(255,255,255,.5)' },
    soft: { background: C.b4, color: C.b1 },
    ok: { background: 'rgba(22,163,74,.12)', color: C.ok },
  } as const;
  return (
    <span style={{ fontFamily, display: 'inline-flex', alignItems: 'center', gap: 10, borderRadius: 99, padding: '10px 22px', fontSize: 24, fontWeight: 500, ...tones[tone], ...style }}>
      {children}
    </span>
  );
};

/** Contador numérico com mola suave. */
export const Counter: React.FC<{ to: number; delay?: number; size?: number }> = ({ to, delay = 0, size = 120 }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - delay, fps, config: { damping: 200, mass: 0.9 }, durationInFrames: 40 });
  return (
    <span style={{ fontFamily, fontSize: size, fontWeight: 600, color: C.b2, letterSpacing: '-0.04em', fontVariantNumeric: 'tabular-nums' }}>
      {Math.round(to * p).toLocaleString('pt-BR')}
    </span>
  );
};
