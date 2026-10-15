'use client';

import React from 'react';
import { ArrowRight } from 'lucide-react';
import { TypeIcon } from '@/components/Agenda/agendaUi';
import { nextOccurrence, useAgenda } from '@/context/AgendaProvider';
import { useAuth } from '@/context/AuthProvider';
import { shortDate, toISODate } from '@/lib/ptBR';

/** Resumo da agenda na tela Início (ou convite suave para criar conta). */
export function UpcomingCard({ onOpenAgenda }: { onOpenAgenda: () => void }) {
  const { status, openAuth } = useAuth();
  const { events, pendingVaccines } = useAgenda();

  if (status !== 'authed') {
    return (
      <div className="c g" style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 220 }}>
          <h3 style={{ marginBottom: 4 }}>Lembretes e vacinas personalizados</h3>
          <p className="mut" style={{ margin: 0 }}>
            Crie uma conta opcional para a SUSANNA acompanhar suas vacinas e lembrar de consultas e exames.
          </p>
        </div>
        <button type="button" className="sx-btn ghost sm" onClick={() => openAuth('register')}>
          Criar conta
        </button>
      </div>
    );
  }

  const now = new Date();
  const upcoming = events
    .map((e) => ({ e, when: nextOccurrence(e, now) }))
    .filter((x): x is { e: typeof x.e; when: Date } => x.when !== null)
    .sort((a, b) => a.when.getTime() - b.when.getTime())
    .slice(0, 3);
  const urgent = pendingVaccines.filter((v) => v.status !== 'proxima').length;

  return (
    <div className="c g" style={{ gridColumn: '1 / -1' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 10 }}>
        <h3 style={{ margin: 0 }}>Próximos compromissos</h3>
        <button type="button" className="sx-link" onClick={onOpenAgenda} style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
          Ver agenda <ArrowRight size={14} aria-hidden />
        </button>
      </div>
      {upcoming.length === 0 ? (
        <p className="mut" style={{ margin: '0 0 6px' }}>Nada marcado. Peça um lembrete no chat ou crie pela agenda.</p>
      ) : (
        upcoming.map(({ e, when }) => (
          <div key={e.id} className="ag-item">
            <TypeIcon tipo={e.tipo} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <b>{e.titulo}</b>
              <small>
                {shortDate(toISODate(when))} · {e.horario || 'sem horário'}
                {e.unidade_saude ? ` · ${e.unidade_saude}` : ''}
              </small>
            </div>
          </div>
        ))
      )}
      {pendingVaccines.length > 0 && (
        <button type="button" className="ag-banner" onClick={onOpenAgenda} style={{ all: 'unset', cursor: 'pointer', display: 'block', marginTop: 8 }}>
          <span className="pill" style={{ background: urgent ? 'rgba(220,38,38,0.1)' : undefined, color: urgent ? '#b91c1c' : undefined }}>
            {pendingVaccines.length} vacina{pendingVaccines.length > 1 ? 's' : ''} pendente{pendingVaccines.length > 1 ? 's' : ''}
            {urgent ? ` · ${urgent} para tomar agora` : ''}
          </span>
        </button>
      )}
    </div>
  );
}
