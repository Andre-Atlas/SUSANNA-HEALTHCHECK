'use client';

import React, { useEffect, useState } from 'react';
import { Calendar, MapPin, Navigation, Phone } from 'lucide-react';
import { Field, SelectField } from '@/components/Auth/fields';
import { useGeo } from '@/context/GeoProvider';
import { apiFetch } from '@/lib/apiClient';
import { suggestRA } from '@/lib/geo';
import { ageFromBirth, CONDITIONS, maskPhone } from '@/lib/ptBR';
import type { RADistribution } from '@/lib/types';

export interface ProfileDraft {
  data_nascimento: string;
  sexo_biologico: '' | 'M' | 'F';
  ra_residencia: string;
  telefone: string;
  condicoes: string[];
}

let rasCache: RADistribution[] | null = null;
let unitsCache: { ra: string; lat?: number; lng?: number }[] | null = null;

function useRAs(): RADistribution[] {
  const [ras, setRas] = useState<RADistribution[]>(rasCache || []);
  useEffect(() => {
    if (rasCache) return;
    apiFetch<RADistribution[]>('/api/units/ras')
      .then((list) => {
        rasCache = [...list].sort((a, b) => a.ra_display.localeCompare(b.ra_display, 'pt-BR'));
        setRas(rasCache);
      })
      .catch(() => {});
  }, []);
  return ras;
}

async function nearestRA(coords: { lat: number; lng: number }): Promise<string | null> {
  if (!unitsCache) {
    const data = await apiFetch<{ units: { ra: string; lat?: number; lng?: number }[] }>('/api/units');
    unitsCache = data.units || [];
  }
  return suggestRA(unitsCache, coords);
}

const today = () => new Date().toISOString().slice(0, 10);

/** Passo 2 do cadastro e seção "Perfil" do painel: nascimento, sexo, RA e telefone. */
export function ProfileBasicsFields({ draft, onChange }: { draft: ProfileDraft; onChange: (d: Partial<ProfileDraft>) => void }) {
  const ras = useRAs();
  const geo = useGeo();
  const [raSuggested, setRaSuggested] = useState(false);
  const age = ageFromBirth(draft.data_nascimento);

  // Pré-preenche a RA pela localização (só sugestão: o usuário pode alterar)
  useEffect(() => {
    if (draft.ra_residencia || !geo.coords) return;
    nearestRA(geo.coords)
      .then((ra) => {
        if (ra) {
          onChange({ ra_residencia: ra });
          setRaSuggested(true);
        }
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [geo.coords]);

  return (
    <>
      <Field
        label="Data de nascimento"
        type="date"
        icon={<Calendar size={18} aria-hidden />}
        max={today()}
        min="1900-01-01"
        value={draft.data_nascimento}
        onChange={(e) => onChange({ data_nascimento: e.target.value })}
        hint={age !== null ? `${age} ${age === 1 ? 'ano' : 'anos'} — usamos para calcular suas vacinas.` : 'Usada para indicar vacinas e exames da sua idade.'}
      />
      <div>
        <span className="sx-label" id="sexo-label">
          Sexo biológico
        </span>
        <div className="sx-segbtns" role="radiogroup" aria-labelledby="sexo-label">
          {(
            [
              ['F', 'Feminino'],
              ['M', 'Masculino'],
            ] as const
          ).map(([v, l]) => (
            <button
              key={v}
              type="button"
              role="radio"
              className="sx-chip"
              aria-checked={draft.sexo_biologico === v}
              aria-pressed={draft.sexo_biologico === v}
              onClick={() =>
                onChange({
                  sexo_biologico: draft.sexo_biologico === v ? '' : v,
                  condicoes: v === 'M' ? draft.condicoes.filter((c) => c !== 'gestante') : draft.condicoes,
                })
              }
            >
              {l}
            </button>
          ))}
        </div>
        <p className="sx-hint">Ajuda a recomendar vacinas e exames preventivos.</p>
      </div>
      <SelectField
        label="Região onde você mora"
        icon={<MapPin size={18} aria-hidden />}
        value={draft.ra_residencia}
        onChange={(e) => {
          onChange({ ra_residencia: e.target.value });
          setRaSuggested(false);
        }}
        hint={raSuggested ? 'Sugerida pela sua localização — confira.' : 'Para indicar as unidades de saúde mais próximas.'}
      >
        <option value="">Selecione…</option>
        {ras.map((r) => (
          <option key={r.ra} value={r.ra}>
            {r.ra_display}
          </option>
        ))}
      </SelectField>
      <Field
        label="Telefone para contato"
        type="tel"
        inputMode="tel"
        autoComplete="tel"
        icon={<Phone size={18} aria-hidden />}
        placeholder="(61) 90000-0000"
        value={draft.telefone}
        onChange={(e) => onChange({ telefone: maskPhone(e.target.value) })}
      />
    </>
  );
}

/** Checklist opcional de condições de saúde. */
export function ConditionsChecklist({ draft, onChange }: { draft: ProfileDraft; onChange: (d: Partial<ProfileDraft>) => void }) {
  const items = CONDITIONS.filter((c) => !c.onlyF || draft.sexo_biologico !== 'M');
  const toggle = (id: string) =>
    onChange({ condicoes: draft.condicoes.includes(id) ? draft.condicoes.filter((c) => c !== id) : [...draft.condicoes, id] });
  return (
    <div>
      <span className="sx-label">Condições de saúde (opcional)</span>
      <div className="sx-chips" role="group" aria-label="Condições de saúde">
        {items.map((c) => (
          <button key={c.id} type="button" className="sx-chip" aria-pressed={draft.condicoes.includes(c.id)} onClick={() => toggle(c.id)}>
            {c.label}
          </button>
        ))}
      </div>
      <p className="sx-hint">Indicam grupos prioritários de vacinação. Você pode mudar quando quiser.</p>
    </div>
  );
}

/** Permissão de localização — os dados ficam somente neste aparelho. */
export function LocationCard() {
  const geo = useGeo();
  const [asking, setAsking] = useState(false);
  const granted = geo.status === 'granted';
  return (
    <div className="sx-card sx-locate">
      <div className="ico">
        <Navigation size={20} aria-hidden />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <b style={{ fontWeight: 500, fontSize: 14 }}>{granted ? 'Localização ativada' : 'Usar minha localização'}</b>
        <p className="sx-legal" style={{ margin: '2px 0 0' }}>
          {geo.status === 'denied'
            ? 'Permissão negada no navegador. Você pode liberar nas configurações do site.'
            : geo.status === 'unavailable'
            ? 'Este navegador não informou a localização.'
            : 'Fica só neste aparelho. Serve para ordenar as unidades mais próximas e sugerir sua região.'}
        </p>
      </div>
      {granted ? (
        <button type="button" className="sx-btn ghost sm" onClick={geo.forget}>
          Desativar
        </button>
      ) : (
        geo.status !== 'unavailable' && (
          <button
            type="button"
            className="sx-btn sm"
            disabled={asking}
            onClick={async () => {
              setAsking(true);
              await geo.request();
              setAsking(false);
            }}
          >
            {asking ? 'Aguarde…' : 'Permitir'}
          </button>
        )
      )}
    </div>
  );
}

export function draftToPatch(d: ProfileDraft) {
  return {
    data_nascimento: d.data_nascimento || null,
    sexo_biologico: d.sexo_biologico || null,
    ra_residencia: d.ra_residencia || null,
    telefone: d.telefone ? d.telefone.replace(/\D/g, '') : null,
    condicoes: d.condicoes,
  };
}
