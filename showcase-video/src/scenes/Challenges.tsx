import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { Layers, Lock, Search, ShieldAlert } from 'lucide-react';
import { C, EASE, fontFamily, glass } from '../theme';
import { Eyebrow, Kinetic } from '../components/ui';

const CARDS = [
  { icon: Layers, t: 'Fontes dispersas', s: 'Portais e bases oficiais fragmentados, reunidos em um corpus curado e versionado.' },
  { icon: ShieldAlert, t: 'Segurança clínica', s: 'Sem diagnóstico nem prescrição: o guardrail barra o pedido antes do LLM.' },
  { icon: Search, t: 'Termos exatos', s: 'LME, PCDT, “UBS 02”: a busca vetorial é reforçada por regras lexicais.' },
  { icon: Lock, t: 'Privacidade (LGPD)', s: 'Conta opcional; CPF, telefone e localização nunca chegam ao modelo.' },
];

/** Principais desafios do projeto. */
export const Challenges: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ fontFamily, padding: '170px 120px 100px', display: 'flex', flexDirection: 'column' }}>
      <Eyebrow n="04" label="Principais desafios" />
      <Kinetic words={['O', 'que', 'tornou', 'o', 'problema', { b: 'difícil.' }]} delay={4} size={76} style={{ marginTop: 26 }} />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 28, marginTop: 'auto', marginBottom: 'auto' }}>
        {CARDS.map((c, i) => {
          const d = 20 + i * 15;
          const p = interpolate(f, [d, d + 18], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
          const Icon = c.icon;
          return (
            <div
              key={c.t}
              style={{ ...glass, borderRadius: 32, padding: '38px 34px', minHeight: 400, opacity: p, transform: `translateY(${(1 - p) * 26}px)`, display: 'flex', flexDirection: 'column', gap: 22 }}
            >
              <span style={{ width: 84, height: 84, borderRadius: 26, display: 'grid', placeItems: 'center', color: '#fff', background: `linear-gradient(150deg, ${C.b3}, ${C.b2})` }}>
                <Icon size={42} strokeWidth={1.8} />
              </span>
              <div style={{ fontSize: 36, fontWeight: 600, color: C.ink, letterSpacing: '-0.02em' }}>{c.t}</div>
              <div style={{ fontSize: 27, lineHeight: 1.45, color: C.mut }}>{c.s}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
