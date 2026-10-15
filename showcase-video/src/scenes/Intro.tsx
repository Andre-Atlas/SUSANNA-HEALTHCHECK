import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { C, fontFamily } from '../theme';
import { Kinetic, Rise } from '../components/ui';

/** 0–2,4 s: a mascote sobe e acena; marca e tagline. */
export const Intro: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const up = spring({ frame: f - 4, fps, config: { damping: 18, mass: 0.8 } });
  const float = Math.sin(f / 18) * 6;
  return (
    <AbsoluteFill style={{ fontFamily, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 90 }}>
        <Img
          src={staticFile('suzanna-hero.webp')}
          style={{
            height: 480,
            transform: `translateY(${(1 - up) * 120 + float}px)`,
            opacity: interpolate(up, [0, 0.4], [0, 1], { extrapolateRight: 'clamp' }),
            filter: 'drop-shadow(0 30px 40px rgba(30,64,175,.22))',
          }}
        />
        <div>
          <Rise delay={8}>
            <div style={{ fontSize: 26, fontWeight: 500, color: C.b1, letterSpacing: '0.14em', textTransform: 'uppercase' }}>
              SUS Digital · Distrito Federal
            </div>
          </Rise>
          <div style={{ fontSize: 170, letterSpacing: '-0.05em', lineHeight: 1, margin: '14px 0 18px' }}>
            <Kinetic words={[{ b: 'SUS' }]} delay={12} size={170} style={{ display: 'inline-block' }} />
            <Kinetic words={['ANNA']} delay={16} size={170} style={{ display: 'inline-block', marginLeft: '-0.24em' }} />
          </div>
          <Kinetic words={['Saúde', 'pública,', { b: 'clara' }, 'como', 'água.']} delay={24} size={52} color={C.mut} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
