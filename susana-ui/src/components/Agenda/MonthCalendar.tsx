'use client';

import React, { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { monthName, toISODate } from '@/lib/ptBR';
import type { AgendaEvent } from '@/lib/types';

interface MonthCalendarProps {
  events: AgendaEvent[];
  selected: string | null;
  onSelect: (iso: string | null) => void;
}

/** Tipos de evento por dia, já expandindo recorrências dentro do mês exibido. */
function typesByDay(events: AgendaEvent[], year: number, month: number): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>();
  const add = (iso: string, tipo: string) => {
    if (!map.has(iso)) map.set(iso, new Set());
    map.get(iso)!.add(tipo);
  };
  const last = new Date(year, month + 1, 0).getDate();
  for (const e of events) {
    if (e.status === 'cancelado') continue;
    if (!e.recorrencia) {
      add(e.data_evento, e.tipo);
      continue;
    }
    const start = new Date(e.data_evento + 'T00:00:00');
    for (let d = 1; d <= last; d++) {
      const day = new Date(year, month, d);
      if (day < start) continue;
      const diff = Math.round((day.getTime() - start.getTime()) / 86400000);
      if (e.recorrencia === 'diaria' || diff % 7 === 0) add(toISODate(day), e.tipo);
    }
  }
  return map;
}

export function MonthCalendar({ events, selected, onSelect }: MonthCalendarProps) {
  const now = new Date();
  const [cursor, setCursor] = useState({ y: now.getFullYear(), m: now.getMonth() });
  const todayIso = toISODate(now);
  const marks = useMemo(() => typesByDay(events, cursor.y, cursor.m), [events, cursor]);

  const first = new Date(cursor.y, cursor.m, 1);
  const pad = first.getDay();
  const days = new Date(cursor.y, cursor.m + 1, 0).getDate();
  const shift = (delta: number) =>
    setCursor(({ y, m }) => {
      const d = new Date(y, m + delta, 1);
      return { y: d.getFullYear(), m: d.getMonth() };
    });

  return (
    <div>
      <div className="ag-head">
        <button type="button" className="ag-nav" onClick={() => shift(-1)} aria-label="Mês anterior">
          <ChevronLeft size={18} aria-hidden />
        </button>
        <b aria-live="polite">
          {monthName(cursor.m)} {cursor.y}
        </b>
        <button type="button" className="ag-nav" onClick={() => shift(1)} aria-label="Próximo mês">
          <ChevronRight size={18} aria-hidden />
        </button>
      </div>
      <div className="cal" role="grid" aria-label="Calendário do mês">
        {['D', 'S', 'T', 'Q', 'Q', 'S', 'S'].map((d, i) => (
          <span key={i} className="h" aria-hidden>
            {d}
          </span>
        ))}
        {Array.from({ length: pad }, (_, i) => (
          <span key={`p${i}`} aria-hidden />
        ))}
        {Array.from({ length: days }, (_, i) => {
          const iso = toISODate(new Date(cursor.y, cursor.m, i + 1));
          const types = marks.get(iso);
          const cls = ['d', iso === todayIso ? 'today' : '', selected === iso ? 's' : ''].filter(Boolean).join(' ');
          return (
            <span
              key={iso}
              role="gridcell"
              tabIndex={0}
              className={cls}
              aria-selected={selected === iso}
              aria-label={`${i + 1} de ${monthName(cursor.m)}${types ? `, ${types.size} tipo(s) de compromisso` : ''}`}
              onClick={() => onSelect(selected === iso ? null : iso)}
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), onSelect(selected === iso ? null : iso))}
            >
              {i + 1}
              {types && (
                <span className="dots">
                  {[...types].slice(0, 3).map((t) => (
                    <i key={t} className={`t-${t}`} />
                  ))}
                </span>
              )}
            </span>
          );
        })}
      </div>
      <div className="ag-legend" aria-hidden>
        <span><i className="t-consulta" /> Consulta</span>
        <span><i className="t-exame" /> Exame</span>
        <span><i className="t-vacina" /> Vacina</span>
        <span><i className="t-medicamento" /> Medicamento</span>
      </div>
    </div>
  );
}
