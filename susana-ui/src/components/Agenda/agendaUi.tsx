'use client';

import React from 'react';
import { Bell, FlaskConical, Pill, Stethoscope, Syringe } from 'lucide-react';
import type { AgendaEventType } from '@/lib/types';

const ICONS: Record<AgendaEventType, React.ComponentType<{ size?: number }>> = {
  consulta: Stethoscope,
  exame: FlaskConical,
  vacina: Syringe,
  medicamento: Pill,
  outro: Bell,
};

export function TypeIcon({ tipo, size = 18 }: { tipo: AgendaEventType; size?: number }) {
  const Icon = ICONS[tipo] || Bell;
  return (
    <span className={`ag-ico t-${tipo}`} aria-hidden>
      <Icon size={size} />
    </span>
  );
}

export const STATUS_LABEL: Record<string, string> = {
  atrasada: 'Atrasada',
  agora: 'Tomar agora',
  proxima: 'Em breve',
};
