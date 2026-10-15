import React from 'react';
import { AbsoluteFill, Img, interpolate, Sequence, staticFile, useCurrentFrame } from 'remotion';
import { CalendarDays, Check, MapPin, Navigation, Stethoscope, Syringe } from 'lucide-react';
import { C, EASE, fontFamily, glass } from '../theme';
import { T, XF } from '../timing';
import { Eyebrow, Glass, Kinetic, Pill, Rise } from '../components/ui';

// Relógio da cena começa no corte de entrada (SceneShell)
const MAP_AT = T.productMap - T.product;
const AGENDA_AT = T.productAgenda - T.product;
const LEN = T.ai - T.product + XF / 2;
const XB = 16; // transição interna entre batidas (8 quadros de saída + 8 de entrada)

/** Crossfade interno: o painel não sai, só o conteúdo se transforma. */
const Beat: React.FC<{ from: number; to: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ from, to, children, style }) => {
  const start = Math.max(0, from - XB / 2);
  const end = to >= LEN ? LEN : to + XB / 2;
  return (
    <Sequence from={start} durationInFrames={end - start} layout="none">
      <BeatFade len={end - start} first={from === 0} last={to >= LEN} style={style}>
        {children}
      </BeatFade>
    </Sequence>
  );
};
const BeatFade: React.FC<{ len: number; first: boolean; last: boolean; style?: React.CSSProperties; children: React.ReactNode }> = ({ len, first, last, style, children }) => {
  const f = useCurrentFrame();
  const a = first ? 1 : interpolate(f, [XB / 2, XB], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const b = last ? 1 : interpolate(f, [len - XB, len - XB / 2], [1, 0], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const o = a * b;
  return <div style={{ position: 'absolute', inset: 0, opacity: o, transform: `scale(${0.985 + 0.015 * o})`, ...style }}>{children}</div>;
};

const Bubble: React.FC<{ me?: boolean; children: React.ReactNode; delay?: number }> = ({ me, children, delay = 0 }) => (
  <Rise delay={delay} style={{ display: 'flex', justifyContent: me ? 'flex-end' : 'flex-start', gap: 14, alignItems: 'flex-end' }}>
    {!me && <Img src={staticFile('suzanna-avatar.webp')} style={{ width: 56, height: 56, borderRadius: '50%' }} />}
    <div
      style={{
        maxWidth: 560,
        padding: '18px 24px',
        fontSize: 26,
        lineHeight: 1.45,
        borderRadius: me ? '26px 26px 6px 26px' : '26px 26px 26px 6px',
        background: me ? C.b2 : 'rgba(255,255,255,.92)',
        color: me ? '#fff' : C.ink,
        boxShadow: me ? '0 10px 24px rgba(37,99,235,.28)' : '0 6px 18px rgba(30,64,175,.08)',
      }}
    >
      {children}
    </div>
  </Rise>
);

const ANSWER =
  'A vacina contra a gripe está disponível nas salas de vacinação das UBSs de Ceilândia. Leve documento com foto e o Cartão SUS.';

const Chat: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.round(interpolate(f, [26, 92], [0, ANSWER.length], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 22, padding: 40, height: '100%' }}>
      <Bubble me delay={6}>Onde tomar vacina da gripe em Ceilândia?</Bubble>
      <Bubble delay={20}>
        {ANSWER.slice(0, n)}
        {n < ANSWER.length && <span style={{ opacity: 0.4 }}>▍</span>}
        <div style={{ marginTop: 16, opacity: interpolate(f, [92, 104], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
          <Pill tone="soft" style={{ fontSize: 20, padding: '8px 16px' }}>
            Fontes oficiais · SES-DF ↗
          </Pill>
        </div>
      </Bubble>
    </div>
  );
};

// Pinos determinísticos (mesmas cores do mapa real: UBS, UPA, hospital, CAPS)
const PIN_COLORS = [C.b2, C.b2, C.b2, '#ea580c', '#dc2626', '#059669'];
const PINS = Array.from({ length: 64 }, (_, i) => {
  const r = (k: number) => {
    const v = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
    return v - Math.floor(v);
  };
  return { x: 60 + r(1) * 640, y: 50 + r(2) * 470, c: PIN_COLORS[i % PIN_COLORS.length], d: 4 + r(3) * 46 };
});

const MapView: React.FC = () => {
  const f = useCurrentFrame();
  const pulse = (f % 40) / 40;
  return (
    <div style={{ position: 'absolute', inset: 30 }}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 24,
          overflow: 'hidden',
          background: 'linear-gradient(135deg, #eaf2ff, #cfe1fd)',
          backgroundImage:
            'linear-gradient(rgba(37,99,235,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(37,99,235,.06) 1px, transparent 1px), linear-gradient(135deg, #eaf2ff, #cfe1fd)',
          backgroundSize: '48px 48px, 48px 48px, 100% 100%',
        }}
      >
        {PINS.map((p, i) => {
          const o = interpolate(f, [p.d, p.d + 10], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: p.x,
                top: p.y,
                width: 16,
                height: 16,
                borderRadius: '50% 50% 50% 0',
                transform: `rotate(-45deg) scale(${o})`,
                background: p.c,
                border: '2px solid #fff',
                boxShadow: '0 2px 6px rgba(0,0,0,.15)',
              }}
            />
          );
        })}
        {/* você está aqui */}
        <div style={{ position: 'absolute', left: 372, top: 300, opacity: interpolate(f, [40, 52], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
          <div style={{ position: 'absolute', left: -30, top: -30, width: 80, height: 80, borderRadius: '50%', background: C.b2, opacity: 0.25 * (1 - pulse), transform: `scale(${0.4 + pulse})` }} />
          <div style={{ width: 22, height: 22, borderRadius: '50%', background: C.b2, border: '4px solid #fff', boxShadow: '0 4px 12px rgba(37,99,235,.5)' }} />
        </div>
      </div>
      <Rise delay={54} style={{ position: 'absolute', left: 24, bottom: 24 }}>
        <div style={{ ...glass, background: 'rgba(255,255,255,.9)', borderRadius: 22, padding: '18px 22px', display: 'flex', gap: 16, alignItems: 'center', fontFamily }}>
          <span style={{ width: 52, height: 52, borderRadius: 16, display: 'grid', placeItems: 'center', background: C.b2, color: '#fff' }}>
            <MapPin size={26} />
          </span>
          <div>
            <div style={{ fontSize: 24, fontWeight: 600, color: C.ink }}>UBS 1 de Ceilândia</div>
            <div style={{ fontSize: 20, color: C.mut, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Navigation size={16} /> 1,2 km de você · ordenado por distância
            </div>
          </div>
        </div>
      </Rise>
    </div>
  );
};

const Agenda: React.FC = () => {
  const f = useCurrentFrame();
  const press = interpolate(f, [62, 66, 70], [1, 0.94, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const done = interpolate(f, [70, 82], [0, 1], { easing: EASE, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 20, padding: 40, height: '100%', fontFamily }}>
      <Bubble me delay={4}>marca consulta no dentista terça às 14h</Bubble>
      <Rise delay={18}>
        <div style={{ background: '#fff', borderRadius: 24, border: `1px solid ${C.b4}`, boxShadow: '0 10px 26px rgba(37,99,235,.10)', padding: '22px 26px', position: 'relative', overflow: 'hidden' }}>
          <div style={{ opacity: 1 - done }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 22, fontWeight: 600, color: C.b1 }}>
              <CalendarDays size={22} /> Novo lembrete
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 14 }}>
              <span style={{ width: 52, height: 52, borderRadius: 16, display: 'grid', placeItems: 'center', background: C.b2, color: '#fff' }}>
                <Stethoscope size={26} />
              </span>
              <div>
                <div style={{ fontSize: 28, fontWeight: 600, color: C.ink }}>Consulta – Dentista</div>
                <div style={{ fontSize: 22, color: C.mut }}>ter, 20 out · 14:00 · UBS 1 de Ceilândia</div>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 18 }}>
              <Pill tone="soft" style={{ fontSize: 22 }}>Cancelar</Pill>
              <Pill tone="blue" style={{ fontSize: 22, transform: `scale(${press})` }}>Confirmar</Pill>
            </div>
          </div>
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', gap: 14, padding: '0 26px', opacity: done, color: C.ok, fontSize: 28, fontWeight: 600 }}>
            <span style={{ width: 48, height: 48, borderRadius: '50%', display: 'grid', placeItems: 'center', background: C.ok, color: '#fff', transform: `scale(${0.6 + 0.4 * done})` }}>
              <Check size={28} strokeWidth={3} />
            </span>
            Adicionado à agenda
          </div>
        </div>
      </Rise>
      <Rise delay={80}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 8 }}>
          {['D', 'S', 'T', 'Q', 'Q', 'S', 'S'].map((d, i) => {
            const day = 18 + i;
            const hit = day === 20;
            return (
              <div
                key={i}
                style={{
                  borderRadius: 16,
                  padding: '10px 0 12px',
                  textAlign: 'center',
                  background: hit ? C.b2 : 'rgba(255,255,255,.7)',
                  color: hit ? '#fff' : C.ink,
                  boxShadow: hit ? '0 8px 18px rgba(37,99,235,.3)' : undefined,
                }}
              >
                <div style={{ fontSize: 18, opacity: 0.7 }}>{d}</div>
                <div style={{ fontSize: 26, fontWeight: 600 }}>{day}</div>
                <div style={{ width: 8, height: 8, borderRadius: 4, margin: '4px auto 0', background: hit ? '#fff' : 'transparent' }} />
              </div>
            );
          })}
        </div>
      </Rise>
      <Rise delay={92}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <Pill tone="ok" style={{ fontSize: 22 }}>
            <Syringe size={20} /> Vacinas pendentes: Influenza · dT
          </Pill>
          <Pill tone="soft" style={{ fontSize: 22 }}>Avisos no app e no navegador</Pill>
        </div>
      </Rise>
    </div>
  );
};

const Copy: React.FC<{ words: (string | { b: string })[]; sub: string }> = ({ words, sub }) => (
  <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 28 }}>
    <Kinetic words={words} delay={2} size={74} />
    <Rise delay={18}>
      <div style={{ fontSize: 32, lineHeight: 1.45, color: C.mut, maxWidth: 760 }}>{sub}</div>
    </Rise>
  </div>
);

/** Produto: chat com fontes, mapa de unidades e agenda com lembretes confirmados. */
export const Product: React.FC = () => (
  <AbsoluteFill style={{ fontFamily, padding: '170px 120px 100px' }}>
    <div style={{ display: 'flex', height: '100%', gap: 80 }}>
      <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column' }}>
        <div style={{ position: 'absolute', top: 70 }}>
          <Eyebrow n="02" label="Produto e solução" />
        </div>
        <div style={{ position: 'relative', flex: 1 }}>
          <Beat from={0} to={MAP_AT}>
            <Copy words={['Uma', 'assistente', 'que', 'responde', 'com', { b: 'fontes' }, { b: 'oficiais.' }]} sub="Perguntas em linguagem natural sobre a rede pública do DF, com o link de cada fonte." />
          </Beat>
          <Beat from={MAP_AT} to={AGENDA_AT}>
            <Copy words={['383', 'unidades', 'de', 'saúde,', { b: 'perto' }, { b: 'de' }, { b: 'você.' }]} sub="Mapa das 33 regiões administrativas, ordenado pela sua localização, que fica só no aparelho." />
          </Beat>
          <Beat from={AGENDA_AT} to={LEN}>
            <Copy words={['Conta', 'opcional,', 'agenda', 'e', { b: 'lembretes' }, { b: 'pelo' }, { b: 'chat.' }]} sub="Vacinas pendentes calculadas pelo perfil. Nada entra na agenda sem a sua confirmação." />
          </Beat>
        </div>
      </div>
      <Glass radius={36} style={{ width: 820, position: 'relative', overflow: 'hidden', alignSelf: 'center', height: 580 }}>
        <Beat from={0} to={MAP_AT}>
          <Chat />
        </Beat>
        <Beat from={MAP_AT} to={AGENDA_AT}>
          <MapView />
        </Beat>
        <Beat from={AGENDA_AT} to={LEN}>
          <Agenda />
        </Beat>
      </Glass>
    </div>
  </AbsoluteFill>
);
