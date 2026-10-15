'use client';

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useAuth } from '@/context/AuthProvider';
import { apiFetch } from '@/lib/apiClient';
import { toISODate } from '@/lib/ptBR';
import type { AgendaEvent, AgendaOverview, PendingVaccine } from '@/lib/types';

export type NewEvent = Pick<AgendaEvent, 'tipo' | 'titulo' | 'data_evento'> &
  Partial<Pick<AgendaEvent, 'horario' | 'unidade_saude' | 'notas' | 'lembrete_min_antes' | 'recorrencia'>>;

export interface ReminderHit {
  key: string;
  event: AgendaEvent;
  when: Date;
}

interface AgendaContextValue {
  events: AgendaEvent[];
  pendingVaccines: PendingVaccine[];
  pendencias: number;
  perfilIncompleto: boolean;
  loading: boolean;
  refresh: () => Promise<void>;
  createEvent: (e: NewEvent) => Promise<AgendaEvent>;
  updateEvent: (id: string, patch: Partial<AgendaEvent>) => Promise<void>;
  deleteEvent: (id: string) => Promise<void>;
  markVaccineTaken: (v: PendingVaccine, date?: string) => Promise<void>;
  scheduleVaccine: (v: PendingVaccine, date: string, horario?: string) => Promise<void>;
  // Lembretes
  notificationPermission: NotificationPermission | 'unsupported';
  requestNotifications: () => Promise<void>;
  activeReminder: ReminderHit | null;
  dismissReminder: () => void;
}

const AgendaContext = createContext<AgendaContextValue | null>(null);
const NOTIFIED_KEY = 'susana_notified';

/** Próxima ocorrência (hoje em diante) de um evento, considerando recorrência. */
export function nextOccurrence(e: AgendaEvent, from: Date = new Date()): Date | null {
  if (e.status !== 'agendado') return null;
  // Eventos sem horário (ex.: vacina) são lembrados como se fossem às 8h
  const [h, m] = (e.horario || '08:00').split(':').map(Number);
  const base = new Date(e.data_evento + 'T00:00:00');
  base.setHours(h, m, 0, 0);
  if (!e.recorrencia || base >= from) return base;
  const step = e.recorrencia === 'diaria' ? 1 : 7;
  const cand = new Date(from);
  cand.setHours(h, m, 0, 0);
  while (cand < from || (Math.round((cand.getTime() - base.getTime()) / 86400000) % step !== 0)) {
    cand.setDate(cand.getDate() + 1);
  }
  return cand;
}

function loadNotified(): Record<string, number> {
  try {
    const raw = JSON.parse(localStorage.getItem(NOTIFIED_KEY) || '{}') as Record<string, number>;
    const cutoff = Date.now() - 3 * 86400000;
    return Object.fromEntries(Object.entries(raw).filter(([, t]) => t > cutoff));
  } catch {
    return {};
  }
}

function saveNotified(map: Record<string, number>) {
  try {
    localStorage.setItem(NOTIFIED_KEY, JSON.stringify(map));
  } catch {
    /* ignora */
  }
}

export function AgendaProvider({ children }: { children: React.ReactNode }) {
  const { status, citizen } = useAuth();
  // Vacinas pendentes dependem do perfil: recalcula quando ele muda
  const profileKey = citizen
    ? [citizen.id, citizen.data_nascimento, citizen.sexo_biologico, citizen.condicoes.join(',')].join('|')
    : '';
  const [events, setEvents] = useState<AgendaEvent[]>([]);
  const [overview, setOverview] = useState<AgendaOverview | null>(null);
  const [loading, setLoading] = useState(false);
  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>('unsupported');
  const [activeReminder, setActiveReminder] = useState<ReminderHit | null>(null);
  const eventsRef = useRef<AgendaEvent[]>([]);

  const refresh = useCallback(async () => {
    if (status !== 'authed') return;
    setLoading(true);
    try {
      const from = new Date();
      from.setMonth(from.getMonth() - 2);
      const [list, ov] = await Promise.all([
        apiFetch<AgendaEvent[]>(`/api/agenda?from=${toISODate(from)}`),
        apiFetch<AgendaOverview>('/api/agenda/overview'),
      ]);
      setEvents(list);
      setOverview(ov);
    } catch {
      /* mantém o último estado */
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    // Busca inicial ao entrar na conta (refresh marca loading antes do fetch)
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (status === 'authed') refresh();
  }, [status, profileKey, refresh]);

  useEffect(() => {
    eventsRef.current = events;
  }, [events]);

  useEffect(() => {
    // Permissão do navegador só existe no cliente (não no SSR)
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (typeof window !== 'undefined' && 'Notification' in window) setPermission(Notification.permission);
  }, []);

  // Verificação de lembretes a cada minuto e ao voltar para a aba
  useEffect(() => {
    if (status !== 'authed') return;
    const check = () => {
      const now = new Date();
      const notified = loadNotified();
      for (const ev of eventsRef.current) {
        const when = nextOccurrence(ev, new Date(now.getTime() - 30 * 60000));
        if (!when) continue;
        const fireAt = when.getTime() - ev.lembrete_min_antes * 60000;
        const key = `${ev.id}@${toISODate(when)}`;
        if (now.getTime() >= fireAt && now.getTime() < when.getTime() + 30 * 60000 && !notified[key]) {
          notified[key] = Date.now();
          const hit = { key, event: ev, when };
          setActiveReminder(hit);
          if ('Notification' in window && Notification.permission === 'granted') {
            const hora = ev.horario ? ` às ${ev.horario}` : '';
            try {
              new Notification('SUSANNA · Lembrete', {
                body: `${ev.titulo}${hora}${ev.unidade_saude ? ` — ${ev.unidade_saude}` : ''}`,
                tag: key,
                icon: '/images/suzanna-avatar.webp',
              });
            } catch {
              /* alguns navegadores móveis exigem service worker */
            }
          }
        }
      }
      saveNotified(notified);
    };
    check();
    const timer = window.setInterval(check, 60000);
    const onVisible = () => document.visibilityState === 'visible' && check();
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      window.clearInterval(timer);
      document.removeEventListener('visibilitychange', onVisible);
    };
  }, [status, events]);

  const requestNotifications = useCallback(async () => {
    if (!('Notification' in window)) return;
    setPermission(await Notification.requestPermission());
  }, []);

  const createEvent = useCallback(
    async (e: NewEvent) => {
      const ev = await apiFetch<AgendaEvent>('/api/agenda/events', { method: 'POST', json: e });
      await refresh();
      return ev;
    },
    [refresh],
  );

  const updateEvent = useCallback(
    async (id: string, patch: Partial<AgendaEvent>) => {
      setEvents((prev) => prev.map((e) => (e.id === id ? { ...e, ...patch } : e)));
      await apiFetch(`/api/agenda/events/${id}`, { method: 'PATCH', json: patch });
      await refresh();
    },
    [refresh],
  );

  const deleteEvent = useCallback(
    async (id: string) => {
      setEvents((prev) => prev.filter((e) => e.id !== id));
      await apiFetch(`/api/agenda/events/${id}`, { method: 'DELETE' });
      await refresh();
    },
    [refresh],
  );

  const markVaccineTaken = useCallback(
    async (v: PendingVaccine, date?: string) => {
      setOverview((ov) => (ov ? { ...ov, vacinas_pendentes: ov.vacinas_pendentes.filter((x) => x.vaccine_id !== v.vaccine_id) } : ov));
      await apiFetch('/api/agenda/vaccines/records', {
        method: 'POST',
        json: { vaccine_id: v.vaccine_id, dose_num: v.dose_num, data_aplicacao: date || toISODate(new Date()) },
      });
      await refresh();
    },
    [refresh],
  );

  const scheduleVaccine = useCallback(
    async (v: PendingVaccine, date: string, horario?: string) => {
      await apiFetch(`/api/agenda/vaccines/${v.vaccine_id}/schedule`, {
        method: 'POST',
        json: { dose_num: v.dose_num, data_evento: date, horario: horario || null },
      });
      await refresh();
    },
    [refresh],
  );

  // Ao sair da conta, nada da agenda anterior continua visível
  const authed = status === 'authed';
  const value = useMemo<AgendaContextValue>(
    () => ({
      events: authed ? events : [],
      pendingVaccines: authed ? overview?.vacinas_pendentes ?? [] : [],
      pendencias: authed ? overview?.pendencias ?? 0 : 0,
      perfilIncompleto: authed ? overview?.perfil_incompleto ?? false : false,
      loading,
      refresh,
      createEvent,
      updateEvent,
      deleteEvent,
      markVaccineTaken,
      scheduleVaccine,
      notificationPermission: permission,
      requestNotifications,
      activeReminder: authed ? activeReminder : null,
      dismissReminder: () => setActiveReminder(null),
    }),
    [authed, events, overview, loading, refresh, createEvent, updateEvent, deleteEvent, markVaccineTaken, scheduleVaccine, permission, requestNotifications, activeReminder],
  );

  return <AgendaContext.Provider value={value}>{children}</AgendaContext.Provider>;
}

export function useAgenda(): AgendaContextValue {
  const ctx = useContext(AgendaContext);
  if (!ctx) throw new Error('useAgenda deve ser usado dentro de <AgendaProvider>');
  return ctx;
}
