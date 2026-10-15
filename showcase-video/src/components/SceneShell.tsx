import React from 'react';
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from 'remotion';
import { EASE } from '../theme';
import { HALF, XF } from '../timing';

interface Props {
  /** Corte de entrada (quadro absoluto). */
  from: number;
  /** Corte de saída (quadro absoluto). */
  to: number;
  children: React.ReactNode;
  /** Sem animação de saída (última cena). */
  holdOut?: boolean;
}

/** Transição única e discreta: a cena sai (fade, 16 px, desfoque) antes do corte e a próxima entra depois dele. */
const Shell: React.FC<{ duration: number; holdOut?: boolean; first: boolean; children: React.ReactNode }> = ({ duration, holdOut, first, children }) => {
  const f = useCurrentFrame();
  // O corte fica em XF/2: a cena só aparece depois dele e some antes do próximo, sem sobreposição de textos
  const lead = first ? 0 : XF / 2;
  const enter = interpolate(f, [lead, lead + HALF], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const exit = holdOut
    ? 0
    : interpolate(f, [duration - XF / 2 - HALF, duration - XF / 2], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const opacity = enter * (1 - exit);
  const y = (1 - enter) * 24 - exit * 16;
  const blur = (1 - enter) * 8 + exit * 6;
  return (
    <AbsoluteFill style={{ opacity, transform: `translateY(${y}px)`, filter: blur > 0.05 ? `blur(${blur}px)` : undefined }}>
      {/* o relógio interno da cena começa no corte */}
      <Sequence from={lead} layout="none">
        {children}
      </Sequence>
    </AbsoluteFill>
  );
};

export const SceneShell: React.FC<Props> = ({ from, to, children, holdOut }) => {
  const start = Math.max(0, from - XF / 2);
  const duration = to - from + (from === 0 ? XF / 2 : XF);
  return (
    <Sequence from={start} durationInFrames={duration} layout="none">
      <Shell duration={duration} holdOut={holdOut} first={from === 0}>
        {children}
      </Shell>
    </Sequence>
  );
};
