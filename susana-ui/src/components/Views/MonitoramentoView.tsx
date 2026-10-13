'use client';

import React, { useState } from 'react';
import { 
  Activity, 
  MapPin, 
  TrendingDown, 
  ShieldAlert, 
  Sparkles, 
  ArrowRight,
  Droplets,
  Bug,
  Info
} from 'lucide-react';
import { TabId } from '@/components/Navigation/Sidebar';

interface MonitoramentoViewProps {
  onNavigate: (tab: TabId, payload?: any) => void;
}

interface RegionData {
  name: string;
  cases: number[];
  weeks: string[];
  totalCases: number;
  trend: string;
  infestation: string;
  fumaceRoutes: number;
}

const REGION_STATS: Record<string, RegionData> = {
  todas: {
    name: 'Distrito Federal (Total)',
    cases: [412, 380, 310, 270, 215],
    weeks: ['SE 38', 'SE 39', 'SE 40', 'SE 41', 'SE 42'],
    totalCases: 1587,
    trend: '-20.3%',
    infestation: '1.2% (Médio Risco)',
    fumaceRoutes: 34,
  },
  planopiloto: {
    name: 'Plano Piloto (Asa Norte / Sul)',
    cases: [85, 78, 62, 54, 41],
    weeks: ['SE 38', 'SE 39', 'SE 40', 'SE 41', 'SE 42'],
    totalCases: 320,
    trend: '-24.0%',
    infestation: '0.8% (Baixo Risco)',
    fumaceRoutes: 8,
  },
  ceilandia: {
    name: 'Ceilândia',
    cases: [142, 130, 112, 98, 80],
    weeks: ['SE 38', 'SE 39', 'SE 40', 'SE 41', 'SE 42'],
    totalCases: 562,
    trend: '-18.3%',
    infestation: '1.6% (Alerta)',
    fumaceRoutes: 14,
  },
  taguatinga: {
    name: 'Taguatinga',
    cases: [95, 88, 71, 62, 49],
    weeks: ['SE 38', 'SE 39', 'SE 40', 'SE 41', 'SE 42'],
    totalCases: 365,
    trend: '-20.9%',
    infestation: '1.1% (Médio Risco)',
    fumaceRoutes: 6,
  },
  samambaia: {
    name: 'Samambaia',
    cases: [90, 84, 65, 56, 45],
    weeks: ['SE 38', 'SE 39', 'SE 40', 'SE 41', 'SE 42'],
    totalCases: 340,
    trend: '-19.6%',
    infestation: '1.3% (Médio Risco)',
    fumaceRoutes: 6,
  },
};

export function MonitoramentoView({ onNavigate }: MonitoramentoViewProps) {
  const [selectedRegion, setSelectedRegion] = useState<string>('todas');
  const [hoveredWeek, setHoveredWeek] = useState<number | null>(null);

  const data = REGION_STATS[selectedRegion] || REGION_STATS['todas'];
  const maxCase = Math.max(...data.cases);

  return (
    <div className="space-y-8 text-left max-w-5xl mx-auto pb-12">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0A1B3D] tracking-tight">
          Monitoramento <span className="text-[#2563EB]">epidemiológico</span>
        </h1>
        <p className="text-sm text-[#5B6B8C] mt-1">
          Casos de dengue por semana e ações de vigilância ambiental no Distrito Federal.
        </p>
      </div>

      {/* RA Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        {[
          { id: 'todas', label: 'Todo o DF' },
          { id: 'planopiloto', label: 'Plano Piloto' },
          { id: 'ceilandia', label: 'Ceilândia' },
          { id: 'taguatinga', label: 'Taguatinga' },
          { id: 'samambaia', label: 'Samambaia' },
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setSelectedRegion(item.id)}
            className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition active:scale-[0.98] ${
              selectedRegion === item.id
                ? 'bg-[#2563EB] text-white shadow-sm'
                : 'bg-white hover:bg-slate-100 text-[#0A1B3D] border border-slate-200'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Metric 1 */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200/90 shadow-2xs">
          <div className="flex items-center justify-between text-xs font-semibold text-[#5B6B8C] mb-2">
            <span>Casos Notificados (5 semanas)</span>
            <Bug size={17} className="text-[#2563EB]" />
          </div>
          <p className="text-2xl font-black text-[#0A1B3D]">{data.totalCases}</p>
          <p className="text-xs text-emerald-600 font-semibold flex items-center gap-1 mt-1">
            <TrendingDown size={14} />
            <span>{data.trend} em relação ao mês anterior</span>
          </p>
        </div>

        {/* Metric 2 */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200/90 shadow-2xs">
          <div className="flex items-center justify-between text-xs font-semibold text-[#5B6B8C] mb-2">
            <span>Índice de Infestação Predial</span>
            <Droplets size={17} className="text-amber-500" />
          </div>
          <p className="text-2xl font-black text-[#0A1B3D]">{data.infestation}</p>
          <p className="text-xs text-slate-500 mt-1">
            Meta sanitária de controle: abaixo de 1.0%
          </p>
        </div>

        {/* Metric 3 */}
        <div className="glass-card rounded-2xl p-5 border border-slate-200/90 shadow-2xs">
          <div className="flex items-center justify-between text-xs font-semibold text-[#5B6B8C] mb-2">
            <span>Rotas de Fumacê</span>
            <Activity size={17} className="text-indigo-600" />
          </div>
          <p className="text-2xl font-black text-[#0A1B3D]">{data.fumaceRoutes} ativas</p>
          <p className="text-xs text-slate-500 mt-1">
            Aplicação semanal nos setores com maior foco
          </p>
        </div>
      </div>

      {/* Interactive Bar Chart Section */}
      <div className="glass-card rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-6">
          <div>
            <h2 className="text-base font-bold text-[#0A1B3D]">
              Casos por Semana Epidemiológica (SE 38 a SE 42)
            </h2>
            <p className="text-xs text-[#5B6B8C]">
              Dados consolidados do Boletim Epidemiológico SES-DF · {data.name}
            </p>
          </div>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            Tendência de Queda Contínua
          </span>
        </div>

        {/* SVG/CSS Bar Chart */}
        <div className="h-64 flex items-end justify-between gap-3 sm:gap-6 pt-8 pb-4 px-2 sm:px-8 border-b border-slate-200">
          {data.cases.map((val, idx) => {
            const heightPercent = Math.round((val / maxCase) * 100);
            const isHovered = hoveredWeek === idx;

            return (
              <div 
                key={idx}
                onMouseEnter={() => setHoveredWeek(idx)}
                onMouseLeave={() => setHoveredWeek(null)}
                className="flex-1 flex flex-col items-center h-full justify-end group cursor-pointer relative"
              >
                {/* Floating Tooltip */}
                {isHovered && (
                  <div className="absolute -top-7 bg-[#0A1B3D] text-white text-[11px] font-bold px-2.5 py-1 rounded-lg shadow-md whitespace-nowrap animate-fade-in z-20">
                    {val} casos
                  </div>
                )}

                {/* Number above bar */}
                <span className={`text-[11px] font-bold mb-1.5 transition ${isHovered ? 'text-[#2563EB]' : 'text-slate-400'}`}>
                  {val}
                </span>

                {/* Animated Bar */}
                <div 
                  style={{ height: `${heightPercent}%` }}
                  className={`w-full max-w-[56px] rounded-t-xl transition-all duration-300 ${
                    idx === data.cases.length - 1
                      ? 'bg-gradient-to-t from-[#1D4ED8] to-[#2563EB]'
                      : 'bg-gradient-to-t from-blue-300 to-blue-400 group-hover:from-blue-400 group-hover:to-blue-500'
                  } ${isHovered ? 'brightness-110 shadow-md' : ''}`}
                />

                {/* Week Label */}
                <span className="text-[11px] font-semibold text-[#5B6B8C] mt-2">
                  {data.weeks[idx]}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dicas de Prevenção & Direct CTA to Suzanna */}
      <div className="rounded-3xl p-6 sm:p-7 bg-gradient-to-br from-blue-50/80 to-indigo-50/70 border border-blue-200/80">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-base font-bold text-[#0A1B3D] flex items-center gap-2">
              <ShieldAlert size={18} className="text-[#2563EB]" />
              <span>Dicas de Prevenção e Cuidados</span>
            </h3>
            <p className="text-xs text-[#5B6B8C]">
              Recomendações da Diretoria de Vigilância Ambiental do DF.
            </p>
          </div>

          <button
            onClick={() => onNavigate('assistente', { prompt: 'Quais os principais sintomas da dengue e o que devo fazer?' })}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold bg-[#2563EB] text-white hover:bg-[#1D4ED8] transition shadow-sm active:scale-[0.98]"
          >
            <Sparkles size={14} />
            <span>Perguntar à Suzanna</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-[#0A1B3D]">
          <div className="p-3.5 bg-white rounded-2xl border border-blue-100 shadow-2xs">
            <span className="font-bold text-[#2563EB] block mb-1">1. Água Parada</span>
            Elimine recipientes, limpe calhas e pratos de vasos pelo menos uma vez por semana.
          </div>
          <div className="p-3.5 bg-white rounded-2xl border border-blue-100 shadow-2xs">
            <span className="font-bold text-[#2563EB] block mb-1">2. Proteção Individual</span>
            Use repelente em áreas abertas e telas de proteção nas janelas de sua residência.
          </div>
          <div className="p-3.5 bg-white rounded-2xl border border-blue-100 shadow-2xs">
            <span className="font-bold text-[#2563EB] block mb-1">3. Sintomas de Alerta</span>
            Febre alta súbita, dor atrás dos olhos e manchas vermelhas: procure imediatamente uma UBS.
          </div>
        </div>
      </div>
    </div>
  );
}
