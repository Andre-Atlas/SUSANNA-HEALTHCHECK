import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { C } from '../theme';

/**
 * Fundo persistente (nunca corta): céu Ice Serene Blue com orbes radiais que derivam devagar.
 * Fica fora das cenas, o que torna as trocas de conteúdo contínuas.
 */
export const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = frame / 30;
  const wake = interpolate(frame, [0, 45], [0, 1], { extrapolateRight: 'clamp' });
  const sleep = interpolate(frame, [durationInFrames - 40, durationInFrames], [1, 0.75], { extrapolateLeft: 'clamp' });
  const orb = (x: number, y: number, size: number, color: string, opacity: number, phase: number) => (
    <div
      style={{
        position: 'absolute',
        left: x + Math.sin(t * 0.18 + phase) * 60,
        top: y + Math.cos(t * 0.15 + phase) * 40,
        width: size,
        height: size,
        borderRadius: '50%',
        background: color,
        opacity: opacity * wake * sleep,
        filter: 'blur(110px)',
      }}
    />
  );
  return (
    <AbsoluteFill style={{ background: C.bg, overflow: 'hidden' }}>
      {orb(1240, -260, 900, C.b3, 0.55, 0)}
      {orb(-300, 560, 760, C.b2, 0.28, 2)}
      {orb(620, 760, 520, C.b4, 0.9, 4)}
      {/* brilho especular superior */}
      <AbsoluteFill style={{ background: 'radial-gradient(120% 60% at 50% -10%, rgba(255,255,255,0.7), transparent 60%)' }} />
    </AbsoluteFill>
  );
};
