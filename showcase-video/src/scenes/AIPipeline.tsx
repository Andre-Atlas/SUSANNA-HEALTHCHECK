import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { BadgeCheck, Cpu, Database, MapPinned, MessageSquare, ShieldCheck } from 'lucide-react';
import { C, EASE, fontFamily, glass } from '../theme';
import { Eyebrow, Kinetic, Rise } from '../components/ui';

const NODES = [
  { icon: MessageSquare, t: 'Pergunta', s: 'linguagem natural' },
  { icon: ShieldCheck, t: 'Guardrail clínico', s: 'TF-IDF + regressão logística (MLflow)' },
  { icon: MapPinned, t: 'NLU do DF', s: 'intenção e 33 regiões' },
  { icon: Database, t: 'Busca vetorial', s: 'ChromaDB + MiniLM multilíngue, filtro por região' },
  { icon: Cpu, t: 'Llama 3.1 8B', s: 'local, via Ollama' },
  { icon: BadgeCheck, t: 'Resposta', s: 'com fontes oficiais' },
];
const W = 252;
const GAP = 30;
const STEP = 15; // um nó a cada meia batida

/** IA aplicada: RAG local aterrado em fontes oficiais. */
export const AIPipeline: React.FC = () => {
  const f = useCurrentFrame();
  const totalW = NODES.length * W + (NODES.length - 1) * GAP;
  // pulso que percorre o pipeline depois que todos os nós aparecem
  const travel = interpolate(f, [24 + NODES.length * STEP, 24 + NODES.length * STEP + 75], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const lineGrow = interpolate(f, [24, 24 + NODES.length * STEP], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ fontFamily, padding: '170px 120px 90px', display: 'flex', flexDirection: 'column' }}>
      <Eyebrow n="03" label="Aplicação e técnicas de IA" />
      <Kinetic words={['RAG', 'local,', 'aterrado', 'em', { b: 'fontes' }, { b: 'oficiais.' }]} delay={4} size={76} style={{ marginTop: 26 }} />

      <div style={{ position: 'relative', width: totalW, margin: '70px auto 0' }}>
        {/* trilho */}
        <div style={{ position: 'absolute', left: W / 2, top: 64, height: 4, borderRadius: 2, width: (totalW - W) * lineGrow, background: `linear-gradient(90deg, ${C.b3}, ${C.b2})`, opacity: 0.5 }} />
        <div
          style={{
            position: 'absolute',
            left: W / 2 + (totalW - W) * travel - 14,
            top: 52,
            width: 28,
            height: 28,
            borderRadius: '50%',
            background: '#fff',
            boxShadow: `0 0 0 6px rgba(96,165,250,.35), 0 0 28px 8px rgba(37,99,235,.45)`,
            opacity: travel > 0 && travel < 1 ? 1 : 0,
          }}
        />
        <div style={{ display: 'flex', gap: GAP, position: 'relative' }}>
          {NODES.map((n, i) => {
            const d = 24 + i * STEP;
            const p = interpolate(f, [d, d + 16], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const lit = interpolate(travel * (NODES.length - 1), [i - 0.4, i, i + 0.6], [0, 1, 0.35], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const Icon = n.icon;
            return (
              <div key={n.t} style={{ width: W, opacity: p, transform: `translateY(${(1 - p) * 18}px)`, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <div
                  style={{
                    ...glass,
                    width: 128,
                    height: 128,
                    borderRadius: 36,
                    display: 'grid',
                    placeItems: 'center',
                    color: lit > 0.5 ? '#fff' : C.b2,
                    background: lit > 0.5 ? C.b2 : 'rgba(255,255,255,.75)',
                    boxShadow: lit > 0.5 ? '0 14px 30px rgba(37,99,235,.38)' : glass.boxShadow,
                  }}
                >
                  <Icon size={54} strokeWidth={1.8} />
                </div>
                <div style={{ marginTop: 22, fontSize: 30, fontWeight: 600, color: C.ink }}>{n.t}</div>
                <div style={{ marginTop: 6, fontSize: 22, lineHeight: 1.35, color: C.mut }}>{n.s}</div>
              </div>
            );
          })}
        </div>
        {/* ramo do guardrail */}
        <Rise delay={150} style={{ position: 'absolute', left: W + GAP - 10, top: 360, width: 560 }}>
          <div style={{ display: 'flex', gap: 14, alignItems: 'center', fontSize: 24, color: '#b91c1c' }}>
            <span style={{ fontSize: 30 }}>↳</span>
            <span style={{ background: 'rgba(220,38,38,.08)', border: '1px solid rgba(220,38,38,.22)', borderRadius: 99, padding: '10px 20px' }}>
              Pedido clínico? Bloqueado antes do modelo · UBS ou SAMU 192
            </span>
          </div>
        </Rise>
      </div>

      <div style={{ marginTop: 'auto', display: 'flex', gap: 24 }}>
        {[
          { d: 190, t: 'Sem evidência relevante, ela diz que não sabe em vez de inventar.' },
          { d: 215, t: 'Lembretes por intenção determinística e confirmação: o modelo nunca grava na agenda.' },
        ].map((x) => (
          <Rise key={x.d} delay={x.d} style={{ flex: 1 }}>
            <div style={{ ...glass, borderRadius: 24, padding: '22px 28px', fontSize: 27, lineHeight: 1.4, color: C.ink }}>{x.t}</div>
          </Rise>
        ))}
      </div>
    </AbsoluteFill>
  );
};
