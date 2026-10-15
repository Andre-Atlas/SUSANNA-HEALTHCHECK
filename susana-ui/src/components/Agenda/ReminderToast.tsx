'use client';

import React, { useEffect } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { BellRing, X } from 'lucide-react';
import { useAgenda } from '@/context/AgendaProvider';

/** Aviso dentro do app quando um lembrete vence (complementa a notificação do navegador). */
export function ReminderToast({ onOpenAgenda }: { onOpenAgenda: () => void }) {
  const { activeReminder, dismissReminder } = useAgenda();
  const reduce = useReducedMotion();

  useEffect(() => {
    if (!activeReminder) return;
    const t = window.setTimeout(dismissReminder, 20000);
    return () => window.clearTimeout(t);
  }, [activeReminder, dismissReminder]);

  return (
    <AnimatePresence>
      {activeReminder && (
        <motion.div
          key={activeReminder.key}
          className="sx sx-toast"
          role="alert"
          initial={reduce ? { opacity: 0 } : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={reduce ? { opacity: 0 } : { opacity: 0, y: 16 }}
        >
          <div className="ico">
            <BellRing size={18} aria-hidden />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <b style={{ fontWeight: 600, fontSize: 14 }}>{activeReminder.event.titulo}</b>
            <p className="sx-legal" style={{ margin: '2px 0 6px' }}>
              {activeReminder.when.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
              {activeReminder.event.unidade_saude ? ` · ${activeReminder.event.unidade_saude}` : ''}
            </p>
            <button
              type="button"
              className="sx-link"
              onClick={() => {
                dismissReminder();
                onOpenAgenda();
              }}
            >
              Abrir agenda
            </button>
          </div>
          <button type="button" className="sx-eye" onClick={dismissReminder} aria-label="Dispensar lembrete">
            <X size={16} aria-hidden />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
