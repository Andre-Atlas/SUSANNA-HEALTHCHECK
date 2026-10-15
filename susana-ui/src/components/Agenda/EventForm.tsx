'use client';

import React, { useState } from 'react';
import type { NewEvent } from '@/context/AgendaProvider';
import { toISODate } from '@/lib/ptBR';
import type { AgendaEventType } from '@/lib/types';

interface EventFormProps {
  initial?: Partial<NewEvent>;
  onSubmit: (e: NewEvent) => Promise<void>;
  onCancel: () => void;
}

const REMINDER_OPTIONS: [number, string][] = [
  [0, 'Na hora'],
  [15, '15 min antes'],
  [60, '1 hora antes'],
  [24 * 60, '1 dia antes'],
];

/** Formulário compacto para criar/editar um lembrete manualmente. */
export function EventForm({ initial, onSubmit, onCancel }: EventFormProps) {
  const [tipo, setTipo] = useState<AgendaEventType>(initial?.tipo || 'consulta');
  const [titulo, setTitulo] = useState(initial?.titulo || '');
  const [data, setData] = useState(initial?.data_evento || toISODate(new Date()));
  const [hora, setHora] = useState(initial?.horario || '');
  const [unidade, setUnidade] = useState(initial?.unidade_saude || '');
  const [lembrete, setLembrete] = useState(initial?.lembrete_min_antes ?? 60);
  const [recorrencia, setRecorrencia] = useState<'' | 'diaria' | 'semanal'>(initial?.recorrencia || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (titulo.trim().length < 2) {
      setError('Dê um nome ao lembrete.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSubmit({
        tipo,
        titulo: titulo.trim(),
        data_evento: data,
        horario: hora || null,
        unidade_saude: unidade.trim() || null,
        lembrete_min_antes: lembrete,
        recorrencia: recorrencia || null,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível salvar.');
      setBusy(false);
    }
  };

  return (
    <form className="pc" onSubmit={submit} style={{ marginTop: 0 }}>
      <div className="pc-grid" style={{ marginTop: 0 }}>
        <div>
          <label htmlFor="ev-tipo">Tipo</label>
          <select id="ev-tipo" value={tipo} onChange={(e) => setTipo(e.target.value as AgendaEventType)}>
            <option value="consulta">Consulta</option>
            <option value="exame">Exame</option>
            <option value="vacina">Vacina</option>
            <option value="medicamento">Medicamento</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div>
          <label htmlFor="ev-rec">Repetir</label>
          <select id="ev-rec" value={recorrencia} onChange={(e) => setRecorrencia(e.target.value as '' | 'diaria' | 'semanal')}>
            <option value="">Não repetir</option>
            <option value="diaria">Todos os dias</option>
            <option value="semanal">Toda semana</option>
          </select>
        </div>
        <div className="full">
          <label htmlFor="ev-tit">Descrição</label>
          <input id="ev-tit" value={titulo} onChange={(e) => setTitulo(e.target.value)} placeholder="Ex.: Retorno com a clínica geral" autoFocus />
        </div>
        <div>
          <label htmlFor="ev-data">Data</label>
          <input id="ev-data" type="date" value={data} onChange={(e) => setData(e.target.value)} required />
        </div>
        <div>
          <label htmlFor="ev-hora">Horário</label>
          <input id="ev-hora" type="time" value={hora} onChange={(e) => setHora(e.target.value)} />
        </div>
        <div>
          <label htmlFor="ev-uni">Unidade (opcional)</label>
          <input id="ev-uni" value={unidade} onChange={(e) => setUnidade(e.target.value)} placeholder="UBS, hospital…" />
        </div>
        <div>
          <label htmlFor="ev-lem">Lembrar</label>
          <select id="ev-lem" value={lembrete} onChange={(e) => setLembrete(Number(e.target.value))}>
            {REMINDER_OPTIONS.map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </select>
        </div>
      </div>
      {error && (
        <p className="mut" role="alert" style={{ color: '#b91c1c', margin: '0 0 10px' }}>
          {error}
        </p>
      )}
      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <button type="button" className="sx-btn ghost sm" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className="sx-btn sm" disabled={busy}>
          {busy ? 'Salvando…' : 'Salvar'}
        </button>
      </div>
    </form>
  );
}
