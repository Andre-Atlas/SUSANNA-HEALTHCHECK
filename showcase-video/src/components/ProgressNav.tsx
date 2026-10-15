import React from 'react';
import { Img, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { C, EASE, fontFamily, glass } from '../theme';
import { SECTIONS, T, XF } from '../timing';

const ITEM_W = 190;
const GAP = 6;

/** Barra superior persistente: orienta o espectador sem competir com o conteúdo. */
export const ProgressNav: React.FC = () => {
  const f = useCurrentFrame();
  const visible =
    interpolate(f, [T.problem - XF / 2, T.problem + XF / 2], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) *
    interpolate(f, [T.outro - XF / 2, T.outro + XF / 2], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  if (visible <= 0) return null;

  // Posição contínua da pílula ativa, deslizando em cada corte
  let pos = 0;
  SECTIONS.forEach((s, i) => {
    if (i === 0) return;
    pos += interpolate(f, [s.from - XF / 2, s.from + XF / 2], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  });

  return (
    <div style={{ position: 'absolute', top: 44, left: 120, right: 120, display: 'flex', alignItems: 'center', justifyContent: 'space-between', opacity: visible, fontFamily }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 26, fontWeight: 600, color: C.ink }}>
        <Img src={staticFile('suzanna-avatar.webp')} style={{ width: 48, height: 48, borderRadius: '50%' }} />
        SUSANNA <span style={{ fontWeight: 300, color: C.mut }}>· SUS Digital</span>
      </div>
      <div style={{ ...glass, position: 'relative', display: 'flex', gap: GAP, padding: 6, borderRadius: 99 }}>
        <div
          style={{
            position: 'absolute',
            top: 6,
            left: 6 + pos * (ITEM_W + GAP),
            width: ITEM_W,
            height: 46,
            borderRadius: 99,
            background: C.b2,
            boxShadow: '0 6px 16px rgba(37,99,235,.35)',
          }}
        />
        {SECTIONS.map((s, i) => {
          const active = Math.max(0, 1 - Math.abs(pos - i));
          return (
            <div
              key={s.label}
              style={{
                position: 'relative',
                width: ITEM_W,
                height: 46,
                display: 'grid',
                placeItems: 'center',
                fontSize: 20,
                fontWeight: 500,
                color: active > 0.5 ? '#fff' : C.mut,
              }}
            >
              {s.label}
            </div>
          );
        })}
      </div>
    </div>
  );
};
