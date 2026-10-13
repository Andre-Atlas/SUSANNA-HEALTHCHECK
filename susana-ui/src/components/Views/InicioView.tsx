'use client';

import React from 'react';
import { 
  Calendar, 
  FileText, 
  Pill, 
  Syringe, 
  Clock, 
  MapPin, 
  ArrowRight,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { TabId } from '@/components/Navigation/Sidebar';

export interface Appointment {
  id: string;
  title: string;
  unit: string;
  date: string;
  type: 'consulta' | 'medicamento' | 'exame';
}

interface InicioViewProps {
  onNavigate: (tab: TabId, payload?: any) => void;
  appointments: Appointment[];
}

export function InicioView({ onNavigate, appointments }: InicioViewProps) {
  return (
    <div className="space-y-8 text-left max-w-5xl mx-auto pb-12">
      {/* Top Greeting */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0A1B3D] tracking-tight">
          Olá, <span className="text-[#2563EB]">Maria</span>
        </h1>
        <p className="text-sm text-[#5B6B8C] mt-1">
          Seu resumo de saúde e as campanhas ativas na sua região administrativa.
        </p>
      </div>

      {/* 3 Quick Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Card 1: Agendar Consulta */}
        <button
          onClick={() => onNavigate('servicos', { specialty: 'clinico' })}
          className="glass-card rounded-2xl p-5 text-left transition hover:-translate-y-0.5 group active:scale-[0.99] border border-slate-200/90 shadow-2xs"
        >
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center mb-3 group-hover:bg-[#2563EB] group-hover:text-white transition">
            <Calendar size={20} />
          </div>
          <h3 className="text-base font-bold text-[#0A1B3D] flex items-center justify-between">
            <span>Agendar consulta</span>
            <ArrowRight size={16} className="text-slate-300 group-hover:text-[#2563EB] transition" />
          </h3>
          <p className="text-xs text-[#5B6B8C] mt-1">
            Clínico, pediatria, odonto e vacinas
          </p>
        </button>

        {/* Card 2: Ver Exames */}
        <button
          onClick={() => onNavigate('historico', { filter: 'exames' })}
          className="glass-card rounded-2xl p-5 text-left transition hover:-translate-y-0.5 group active:scale-[0.99] border border-slate-200/90 shadow-2xs"
        >
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3 group-hover:bg-emerald-600 group-hover:text-white transition">
            <FileText size={20} />
          </div>
          <h3 className="text-base font-bold text-[#0A1B3D] flex items-center justify-between">
            <span>Ver exames</span>
            <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
              2 novos
            </span>
          </h3>
          <p className="text-xs text-[#5B6B8C] mt-1">
            Resultados e laudos liberados
          </p>
        </button>

        {/* Card 3: Buscar Medicamentos */}
        <button
          onClick={() => onNavigate('assistente', { prompt: 'Como retirar medicamentos na Farmácia de Alto Custo CEAF?' })}
          className="glass-card rounded-2xl p-5 text-left transition hover:-translate-y-0.5 group active:scale-[0.99] border border-slate-200/90 shadow-2xs"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3 group-hover:bg-indigo-600 group-hover:text-white transition">
            <Pill size={20} />
          </div>
          <h3 className="text-base font-bold text-[#0A1B3D] flex items-center justify-between">
            <span>Buscar medicamentos</span>
            <ArrowRight size={16} className="text-slate-300 group-hover:text-indigo-600 transition" />
          </h3>
          <p className="text-xs text-[#5B6B8C] mt-1">
            Consulte estoques com a Suzanna
          </p>
        </button>
      </div>

      {/* Grid: Avisos da Região & Próximos Compromissos */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Avisos da Região (Col-7) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#0A1B3D] flex items-center gap-2">
              <AlertCircle size={18} className="text-[#2563EB]" />
              <span>Avisos da sua Região</span>
            </h2>
            <span className="text-xs text-[#5B6B8C]">Plano Piloto · Asa Norte</span>
          </div>

          {/* Regional Alert Banner Card */}
          <div className="rounded-2xl p-5 bg-gradient-to-br from-blue-50/90 to-indigo-50/60 border border-blue-200/70 text-left shadow-2xs">
            <div className="flex items-start gap-3.5">
              <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                <Syringe size={18} />
              </div>
              <div className="space-y-2 flex-1">
                <div>
                  <span className="text-[11px] font-bold text-[#2563EB] uppercase tracking-wider">
                    Campanha Ativa
                  </span>
                  <h4 className="text-sm font-bold text-[#0A1B3D]">
                    Campanha de vacinação na Asa Norte
                  </h4>
                  <p className="text-xs text-[#5B6B8C] mt-0.5 leading-relaxed">
                    Vacinas contra gripe (Influenza) e sarampo disponíveis na UBS 1 da Asa Norte (EQN 114/115), de segunda a sexta, das 8h às 17h, até 31/10.
                  </p>
                </div>

                <div className="pt-1">
                  <button
                    onClick={() => onNavigate('servicos', { specialty: 'vacinacao', unit: 'ubs1' })}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-[#2563EB] text-white hover:bg-[#1D4ED8] transition shadow-2xs active:scale-[0.98]"
                  >
                    <span>Ver unidades com vacina</span>
                    <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Dengue Watch Alert */}
          <div className="rounded-2xl p-4 bg-amber-50/80 border border-amber-200/80 text-left flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-amber-200 text-amber-800 flex items-center justify-center font-bold text-xs">
                ⚠️
              </div>
              <div>
                <p className="text-xs font-bold text-amber-900">Vigilância Epidemiológica</p>
                <p className="text-[11px] text-amber-700">Aplicação de Fumacê programada para esta semana na sua RA.</p>
              </div>
            </div>
            <button
              onClick={() => onNavigate('monitoramento')}
              className="text-xs font-semibold text-amber-900 hover:underline flex items-center gap-1 flex-shrink-0"
            >
              <span>Ver dados</span>
              <ArrowRight size={12} />
            </button>
          </div>
        </div>

        {/* Próximos Compromissos (Col-5) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#0A1B3D] flex items-center gap-2">
              <Clock size={18} className="text-[#2563EB]" />
              <span>Próximos Compromissos</span>
            </h2>
            <span className="text-xs text-[#5B6B8C]">{appointments.length} agendados</span>
          </div>

          <div className="glass-card rounded-2xl p-4 divide-y divide-slate-100">
            {appointments.length === 0 ? (
              <p className="text-xs text-slate-400 py-6 text-center">Nenhum compromisso agendado no momento.</p>
            ) : (
              appointments.map((item) => (
                <div key={item.id} className="py-3.5 first:pt-1 last:pb-1 text-left flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${
                    item.type === 'consulta' ? 'bg-blue-100 text-blue-700' :
                    item.type === 'medicamento' ? 'bg-purple-100 text-purple-700' :
                    'bg-emerald-100 text-emerald-700'
                  }`}>
                    {item.type === 'consulta' && <Calendar size={16} />}
                    {item.type === 'medicamento' && <Pill size={16} />}
                    {item.type === 'exame' && <FileText size={16} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-[#0A1B3D] truncate">{item.title}</p>
                    <p className="text-[11px] text-[#5B6B8C] flex items-center gap-1 mt-0.5">
                      <MapPin size={11} />
                      <span className="truncate">{item.unit}</span>
                    </p>
                    <p className="text-[11px] font-semibold text-[#2563EB] mt-1">{item.date}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
