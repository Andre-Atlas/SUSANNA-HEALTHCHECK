'use client';

import React, { useMemo, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { Bell, Check, MessageCircle, Plus, Trash, UserRound } from 'lucide-react';
import { EventForm } from '@/components/Agenda/EventForm';
import { MonthCalendar } from '@/components/Agenda/MonthCalendar';
import { STATUS_LABEL, TypeIcon } from '@/components/Agenda/agendaUi';
import { nextOccurrence, useAgenda } from '@/context/AgendaProvider';
import { useAuth } from '@/context/AuthProvider';
import { longDate, shortDate, toISODate } from '@/lib/ptBR';
import type { AgendaEvent, PendingVaccine } from '@/lib/types';

interface AgendaViewProps {
  onAskSusanna: (prompt: string) => void;
}

const RECUR_LABEL = { diaria: 'todos os dias', semanal: 'toda semana' } as const;

function occursOn(e: AgendaEvent, iso: string): boolean {
  if (!e.recorrencia) return e.data_evento === iso;
  if (iso < e.data_evento) return false;
  const diff = Math.round((new Date(iso + 'T00:00:00').getTime() - new Date(e.data_evento + 'T00:00:00').getTime()) / 86400000);
  return e.recorrencia === 'diaria' || diff % 7 === 0;
}

function EventRow({ e, onToggle, onDelete }: { e: AgendaEvent; onToggle: () => void; onDelete: () => void }) {
  const next = nextOccurrence(e);
  const dateIso = e.recorrencia && next ? toISODate(next) : e.data_evento;
  const done = e.status === 'concluido';
  return (
    <motion.div layout className={`ag-item${done ? ' done' : ''}`} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, x: -12 }}>
      <TypeIcon tipo={e.tipo} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <b>{e.titulo}</b>
        <small>
          {e.recorrencia ? `${RECUR_LABEL[e.recorrencia]} · ` : `${shortDate(dateIso)} · `}
          {e.horario || 'sem horário'}
          {e.unidade_saude ? ` · ${e.unidade_saude}` : ''}
          {e.origem === 'chat' ? ' · via chat' : ''}
        </small>
      </div>
      <button type="button" className="ag-act" onClick={onToggle} aria-label={done ? 'Marcar como pendente' : 'Marcar como concluído'} title={done ? 'Reabrir' : 'Concluir'}>
        <Check size={17} aria-hidden />
      </button>
      <button type="button" className="ag-act del" onClick={onDelete} aria-label={`Excluir ${e.titulo}`} title="Excluir">
        <Trash size={16} aria-hidden />
      </button>
    </motion.div>
  );
}

function VaccineRow({ v, onTaken, onSchedule }: { v: PendingVaccine; onTaken: () => void; onSchedule: () => void }) {
  return (
    <motion.div layout className="ag-item" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.96 }}>
      <TypeIcon tipo="vacina" />
      <div style={{ flex: 1, minWidth: 0 }}>
        <b>{v.nome}</b>
        <small>
          {v.dose_label} · {v.status === 'proxima' ? `a partir de ${shortDate(v.data_sugerida)}` : v.motivo}
        </small>
      </div>
      <span className={`ag-badge ${v.status}`}>{STATUS_LABEL[v.status]}</span>
      <button type="button" className="sx-btn ghost sm" onClick={onSchedule}>
        Agendar
      </button>
      <button type="button" className="ag-act" onClick={onTaken} aria-label={`Já tomei ${v.nome}`} title="Já tomei">
        <Check size={17} aria-hidden />
      </button>
    </motion.div>
  );
}

export function AgendaView({ onAskSusanna }: AgendaViewProps) {
  const { status, citizen, openAuth, setProfileOpen } = useAuth();
  const agenda = useAgenda();
  const reduce = useReducedMotion();
  const [selected, setSelected] = useState<string | null>(null);
  const [formFor, setFormFor] = useState<null | { vaccine?: PendingVaccine }>(null);

  const [todayIso, weekIso] = useMemo(() => {
    const d = new Date();
    const w = new Date(d);
    w.setDate(d.getDate() + 7);
    return [toISODate(d), toISODate(w)];
  }, []);

  const groups = useMemo(() => {
    const active = agenda.events.filter((e) => e.status !== 'cancelado');
    if (selected) return [{ title: longDate(selected), items: active.filter((e) => occursOn(e, selected)) }];
    const upcoming = active.filter((e) => e.status === 'agendado' && (e.recorrencia || e.data_evento >= todayIso));
    return [
      { title: 'Hoje', items: upcoming.filter((e) => occursOn(e, todayIso)) },
      { title: 'Próximos 7 dias', items: upcoming.filter((e) => !occursOn(e, todayIso) && !e.recorrencia && e.data_evento <= weekIso) },
      { title: 'Depois', items: upcoming.filter((e) => !e.recorrencia && e.data_evento > weekIso) },
      { title: 'Recorrentes', items: upcoming.filter((e) => e.recorrencia && !occursOn(e, todayIso)) },
      { title: 'Concluídos', items: active.filter((e) => e.status === 'concluido').slice(-5) },
    ].filter((g) => g.items.length > 0);
  }, [agenda.events, selected, todayIso, weekIso]);

  if (status !== 'authed') {
    return (
      <div className="c g ag-empty">
        <img src="/images/suzanna-avatar.webp" alt="" />
        <h3 style={{ marginBottom: 6 }}>Sua agenda de saúde, personalizada</h3>
        <p style={{ maxWidth: 440, margin: '0 auto 18px' }}>
          Com uma conta (opcional e gratuita), a SUSANNA calcula as vacinas indicadas para o seu perfil e guarda lembretes de
          consultas, exames e medicamentos que você pedir no chat.
        </p>
        <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button type="button" className="sx-btn" onClick={() => openAuth('register')}>
            Criar conta
          </button>
          <button type="button" className="sx-btn ghost" onClick={() => openAuth('login')}>
            Já tenho conta
          </button>
        </div>
      </div>
    );
  }

  const submitForm = async (ev: Parameters<typeof agenda.createEvent>[0]) => {
    if (formFor?.vaccine) await agenda.scheduleVaccine(formFor.vaccine, ev.data_evento, ev.horario || undefined);
    else await agenda.createEvent(ev);
    setFormFor(null);
  };

  return (
    <div>
      {agenda.perfilIncompleto && (
        <div className="ag-banner" role="note">
          <UserRound size={18} aria-hidden />
          <span style={{ flex: 1 }}>Informe sua data de nascimento para ver as vacinas indicadas para você.</span>
          <button type="button" className="sx-btn sm" onClick={() => setProfileOpen(true)}>
            Completar perfil
          </button>
        </div>
      )}
      {agenda.notificationPermission === 'default' && (
        <div className="ag-banner" role="note">
          <Bell size={18} aria-hidden />
          <span style={{ flex: 1 }}>Ative as notificações para receber lembretes enquanto a SUSANNA estiver aberta.</span>
          <button type="button" className="sx-btn ghost sm" onClick={agenda.requestNotifications}>
            Ativar lembretes
          </button>
        </div>
      )}

      <div className="ag">
        <div className="c g">
          <MonthCalendar events={agenda.events} selected={selected} onSelect={setSelected} />
        </div>

        <div style={{ display: 'grid', gap: 16 }}>
          <div className="c g">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>{selected ? 'Compromissos do dia' : 'Próximos compromissos'}</h3>
              <button type="button" className="sx-btn sm" onClick={() => setFormFor({})} aria-expanded={!!formFor && !formFor.vaccine}>
                <Plus size={15} aria-hidden /> Lembrete
              </button>
            </div>

            <AnimatePresence initial={false}>
              {formFor && (
                <motion.div
                  key="form"
                  initial={{ opacity: 0, height: reduce ? 'auto' : 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: reduce ? 'auto' : 0 }}
                  style={{ overflow: 'hidden', marginBottom: 12 }}
                >
                  <EventForm
                    initial={
                      formFor.vaccine
                        ? { tipo: 'vacina', titulo: `Vacina – ${formFor.vaccine.nome}`.slice(0, 120), data_evento: formFor.vaccine.data_sugerida < todayIso ? todayIso : formFor.vaccine.data_sugerida, lembrete_min_antes: 24 * 60 }
                        : { data_evento: selected || todayIso }
                    }
                    onSubmit={submitForm}
                    onCancel={() => setFormFor(null)}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {groups.length === 0 ? (
              <div className="ag-empty" style={{ padding: '14px 0' }}>
                <p style={{ margin: '0 0 12px' }}>{selected ? 'Nada marcado para este dia.' : 'Nenhum compromisso por enquanto.'}</p>
                <button
                  type="button"
                  className="sx-btn ghost sm"
                  onClick={() => onAskSusanna('Me lembra de uma consulta na UBS na próxima semana')}
                >
                  <MessageCircle size={15} aria-hidden /> Pedir à SUSANNA
                </button>
              </div>
            ) : (
              groups.map((g) => (
                <div key={g.title} style={{ marginBottom: 8 }}>
                  <p className="ag-group">{g.title}</p>
                  <AnimatePresence initial={false}>
                    {g.items.map((e) => (
                      <EventRow
                        key={e.id}
                        e={e}
                        onToggle={() => agenda.updateEvent(e.id, { status: e.status === 'concluido' ? 'agendado' : 'concluido' })}
                        onDelete={() => agenda.deleteEvent(e.id)}
                      />
                    ))}
                  </AnimatePresence>
                </div>
              ))
            )}
            <p className="mut" style={{ margin: '6px 0 0', fontSize: 12 }}>
              Dica: no chat, diga “marca consulta no dentista terça às 14h” e confirme o cartão.
            </p>
          </div>

          <div className="c g">
            <h3>Vacinas pendentes{citizen?.faixa_etaria ? ` · ${citizen.idade_anos} anos` : ''}</h3>
            {agenda.pendingVaccines.length === 0 ? (
              <p className="mut" style={{ margin: 0 }}>
                {agenda.perfilIncompleto ? 'Complete o perfil para calcular.' : 'Nenhuma vacina pendente para o seu perfil agora. 🎉'}
              </p>
            ) : (
              <AnimatePresence initial={false}>
                {agenda.pendingVaccines.map((v) => (
                  <VaccineRow
                    key={`${v.vaccine_id}-${v.dose_num}`}
                    v={v}
                    onTaken={() => agenda.markVaccineTaken(v)}
                    onSchedule={() => setFormFor({ vaccine: v })}
                  />
                ))}
              </AnimatePresence>
            )}
            <p className="mut" style={{ margin: '8px 0 0', fontSize: 12 }}>
              Orientação baseada no Calendário Nacional de Vacinação. Confirme sempre na sua UBS com a caderneta.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
