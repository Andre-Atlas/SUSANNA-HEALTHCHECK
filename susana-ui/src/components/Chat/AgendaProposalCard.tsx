'use client';

import React, { useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { CalendarDays, Check } from 'lucide-react';
import { useAgenda } from '@/context/AgendaProvider';
import { apiFetch } from '@/lib/apiClient';
import type { AgendaEventType, AgendaProposal } from '@/lib/types';

export type ProposalState = 'open' | 'confirmed' | 'dismissed';

interface Props {
  proposal: AgendaProposal;
  state: ProposalState;
  onStateChange: (s: ProposalState) => void;
  onOpenAgenda: () => void;
}

/** Cartão editável que transforma a sugestão do chat em evento só após "Confirmar". */
export function AgendaProposalCard({ proposal, state, onStateChange, onOpenAgenda }: Props) {
  const { refresh } = useAgenda();
  const reduce = useReducedMotion();
  const [tipo, setTipo] = useState<AgendaEventType>(proposal.tipo);
  const [titulo, setTitulo] = useState(proposal.titulo);
  const [data, setData] = useState(proposal.data_evento || '');
  const [hora, setHora] = useState(proposal.horario || '');
  const [unidade, setUnidade] = useState(proposal.unidade_saude || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (state === 'confirmed') {
    return (
      <motion.div className="pc pc-done" initial={reduce ? false : { scale: 0.97, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} role="status">
        <Check size={18} aria-hidden /> Adicionado à agenda
        <button type="button" className="sx-link" style={{ marginLeft: 'auto' }} onClick={onOpenAgenda}>
          Ver agenda
        </button>
      </motion.div>
    );
  }
  if (state === 'dismissed') {
    return <p className="mut" style={{ margin: '8px 0 0', fontSize: 12 }}>Lembrete descartado.</p>;
  }

  const confirm = async () => {
    setBusy(true);
    setError(null);
    try {
      await apiFetch(`/api/agenda/proposals/${proposal.proposal_id}/confirm`, {
        method: 'POST',
        json: { tipo, titulo: titulo.trim(), data_evento: data, horario: hora || null, unidade_saude: unidade.trim() || null },
      });
      onStateChange('confirmed');
      refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível adicionar.');
    } finally {
      setBusy(false);
    }
  };

  const dismiss = async () => {
    onStateChange('dismissed');
    apiFetch(`/api/agenda/proposals/${proposal.proposal_id}/dismiss`, { method: 'POST' }).catch(() => {});
  };

  return (
    <motion.div className="pc" initial={reduce ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, fontSize: 13, color: 'var(--b1)' }}>
        <CalendarDays size={16} aria-hidden /> Novo lembrete
      </div>
      <div className="pc-grid">
        <div className="full">
          <label htmlFor={`pt-${proposal.proposal_id}`}>Descrição</label>
          <input id={`pt-${proposal.proposal_id}`} value={titulo} onChange={(e) => setTitulo(e.target.value)} />
        </div>
        <div>
          <label htmlFor={`pd-${proposal.proposal_id}`}>Data</label>
          <input id={`pd-${proposal.proposal_id}`} type="date" value={data} data-missing={!data} onChange={(e) => setData(e.target.value)} />
        </div>
        <div>
          <label htmlFor={`ph-${proposal.proposal_id}`}>Horário</label>
          <input
            id={`ph-${proposal.proposal_id}`}
            type="time"
            value={hora}
            data-missing={!hora && tipo !== 'vacina'}
            onChange={(e) => setHora(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor={`py-${proposal.proposal_id}`}>Tipo</label>
          <select id={`py-${proposal.proposal_id}`} value={tipo} onChange={(e) => setTipo(e.target.value as AgendaEventType)}>
            <option value="consulta">Consulta</option>
            <option value="exame">Exame</option>
            <option value="vacina">Vacina</option>
            <option value="medicamento">Medicamento</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div>
          <label htmlFor={`pu-${proposal.proposal_id}`}>Unidade</label>
          <input id={`pu-${proposal.proposal_id}`} value={unidade} placeholder="Opcional" onChange={(e) => setUnidade(e.target.value)} />
        </div>
      </div>
      {proposal.recorrencia && (
        <p className="mut" style={{ margin: '-4px 0 10px', fontSize: 12 }}>
          Repete {proposal.recorrencia === 'diaria' ? 'todos os dias' : 'toda semana'}.
        </p>
      )}
      {error && (
        <p role="alert" style={{ margin: '0 0 10px', fontSize: 12, color: '#b91c1c' }}>
          {error}
        </p>
      )}
      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button type="button" className="sx-btn ghost sm" onClick={dismiss}>
          Cancelar
        </button>
        <button type="button" className="sx-btn sm" disabled={busy || !data || titulo.trim().length < 2} onClick={confirm}>
          {busy ? 'Salvando…' : 'Confirmar'}
        </button>
      </div>
    </motion.div>
  );
}
