'use client';

import React, { useState } from 'react';
import { 
  FileText, 
  Calendar, 
  Syringe, 
  Download, 
  Sparkles, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Clock, 
  ArrowRight
} from 'lucide-react';
import { TabId } from '@/components/Navigation/Sidebar';

interface HistoricoViewProps {
  onNavigate: (tab: TabId, payload?: any) => void;
  preselectedFilter?: string;
}

interface RecordItem {
  id: string;
  type: 'exame' | 'vacina' | 'consulta';
  title: string;
  unit: string;
  date: string;
  status: 'concluido' | 'agendado';
  details: {
    summary: string;
    metrics?: { label: string; value: string; status: 'normal' | 'alerta' }[];
    notes?: string;
  };
}

const RECORDS: RecordItem[] = [
  {
    id: 'rec_1',
    type: 'exame',
    title: 'Hemograma Completo com Plaquetas',
    unit: 'Laboratório Central / HRAN Asa Norte',
    date: '28 de Setembro de 2026',
    status: 'concluido',
    details: {
      summary: 'Exame de rotina ambulatorial solicitado por Médico de Família.',
      metrics: [
        { label: 'Hemoglobina', value: '14.2 g/dL', status: 'normal' },
        { label: 'Leucócitos Totais', value: '6.450 /mm³', status: 'normal' },
        { label: 'Plaquetas', value: '240.000 /mm³', status: 'normal' },
        { label: 'Glicemia em Jejum', value: '88 mg/dL', status: 'normal' },
      ],
      notes: 'Laudo assinado digitalmente por Dra. Patrícia Mendes (CRBM 4921-DF). Todos os parâmetros dentro dos intervalos biológicos normais.',
    },
  },
  {
    id: 'rec_2',
    type: 'vacina',
    title: 'Vacina COVID-19 Bivalente (Pfizer/BioNTech)',
    unit: 'UBS 1 Asa Norte · Sala de Vacinas',
    date: '12 de Agosto de 2026',
    status: 'concluido',
    details: {
      summary: 'Dose de reforço anual contra variantes vigentes.',
      metrics: [
        { label: 'Lote', value: 'FP8204-BR', status: 'normal' },
        { label: 'Validade do Lote', value: '11/2027', status: 'normal' },
        { label: 'Profissional Vacinador', value: 'Enf. Carlos Sousa (COREN-DF 932)', status: 'normal' },
      ],
      notes: 'Paciente não relatou histórico de reações adversas a imunobiológicos.',
    },
  },
  {
    id: 'rec_3',
    type: 'consulta',
    title: 'Consulta de Acolhimento e Clínica Geral',
    unit: 'UBS 2 Ceilândia Sul · Equipe Saúde da Família 04',
    date: '10 de Maio de 2026',
    status: 'concluido',
    details: {
      summary: 'Atendimento de rotina e aferição de pressão arterial.',
      metrics: [
        { label: 'Pressão Arterial', value: '120/80 mmHg', status: 'normal' },
        { label: 'Frequência Cardíaca', value: '72 bpm', status: 'normal' },
        { label: 'IMC', value: '23.4 (Normal)', status: 'normal' },
      ],
      notes: 'Encaminhamento administrativo para avaliação oftalmológica inserido no SISREG.',
    },
  },
  {
    id: 'rec_4',
    type: 'exame',
    title: 'Tomografia Computadorizada de Tórax (Sem Contraste)',
    unit: 'Hospital Regional de Taguatinga (HRT) · Radiologia',
    date: 'Solicitado em 15/09/2026',
    status: 'agendado',
    details: {
      summary: 'Solicitação em fila de espera de regulação do Complexo Regulador em Saúde do DF.',
      metrics: [
        { label: 'Protocolo SISREG', value: '#84920194-DF', status: 'normal' },
        { label: 'Prioridade', value: 'Classificação Verde (Eletivo)', status: 'normal' },
      ],
      notes: 'Aguardando liberação de vaga no hospital especializado. Notificação automática via SMS assim que agendado.',
    },
  },
];

export function HistoricoView({ onNavigate, preselectedFilter }: HistoricoViewProps) {
  const [filter, setFilter] = useState<string>(preselectedFilter || 'todos');
  const [expandedId, setExpandedId] = useState<string | null>('rec_1');
  const [downloadSuccessId, setDownloadSuccessId] = useState<string | null>(null);

  const filteredRecords = filter === 'todos' 
    ? RECORDS 
    : RECORDS.filter(r => r.type === filter);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  const handleDownloadPdf = (id: string) => {
    setDownloadSuccessId(id);
    setTimeout(() => setDownloadSuccessId(null), 3000);
  };

  return (
    <div className="space-y-8 text-left max-w-5xl mx-auto pb-12">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0A1B3D] tracking-tight">
          Histórico <span className="text-[#2563EB]">clínico</span>
        </h1>
        <p className="text-sm text-[#5B6B8C] mt-1">
          Seu prontuário digital unificado com registros de consultas, vacinas e exames da rede pública do DF.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        {[
          { id: 'todos', label: 'Todos os Registros' },
          { id: 'exame', label: 'Exames' },
          { id: 'vacina', label: 'Vacinas' },
          { id: 'consulta', label: 'Consultas' },
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setFilter(item.id)}
            className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition active:scale-[0.98] ${
              filter === item.id
                ? 'bg-[#2563EB] text-white shadow-sm'
                : 'bg-white hover:bg-slate-100 text-[#0A1B3D] border border-slate-200'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Timeline Accordion List */}
      <div className="space-y-4">
        {filteredRecords.map((item) => {
          const isExpanded = expandedId === item.id;
          return (
            <div 
              key={item.id} 
              className="glass-card rounded-2xl border border-slate-200/90 shadow-2xs overflow-hidden transition duration-150"
            >
              {/* Accordion Header */}
              <div
                onClick={() => toggleExpand(item.id)}
                className="p-5 cursor-pointer flex items-center justify-between gap-4 hover:bg-slate-50/70 transition"
              >
                <div className="flex items-start gap-3.5">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 ${
                    item.type === 'exame' ? 'bg-emerald-100 text-emerald-700' :
                    item.type === 'vacina' ? 'bg-blue-100 text-blue-700' :
                    'bg-purple-100 text-purple-700'
                  }`}>
                    {item.type === 'exame' && <FileText size={20} />}
                    {item.type === 'vacina' && <Syringe size={20} />}
                    {item.type === 'consulta' && <Calendar size={20} />}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider">
                        {item.type}
                      </span>
                      <span>·</span>
                      <span className="text-xs text-slate-400">{item.date}</span>
                    </div>
                    <h3 className="text-sm sm:text-base font-bold text-[#0A1B3D] mt-0.5">
                      {item.title}
                    </h3>
                    <p className="text-xs text-[#5B6B8C] mt-0.5">{item.unit}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full hidden sm:inline-block ${
                    item.status === 'concluido'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}>
                    {item.status === 'concluido' ? 'Disponível' : 'Em Regulação'}
                  </span>
                  <div className="text-slate-400">
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </div>
                </div>
              </div>

              {/* Accordion Expanded Body */}
              {isExpanded && (
                <div className="px-5 pb-5 pt-1 border-t border-slate-100 bg-white/60 space-y-4 text-xs">
                  <p className="text-[#5B6B8C] leading-relaxed pt-2">
                    {item.details.summary}
                  </p>

                  {/* Metrics Table / Grid */}
                  {item.details.metrics && (
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                      {item.details.metrics.map((m, idx) => (
                        <div key={idx} className="p-3 bg-slate-50/90 rounded-xl border border-slate-200/80">
                          <p className="text-[10px] text-slate-400 font-medium">{m.label}</p>
                          <p className="text-xs font-bold text-[#0A1B3D] mt-0.5">{m.value}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Doctor notes */}
                  {item.details.notes && (
                    <div className="p-3.5 bg-blue-50/60 rounded-xl border border-blue-100 text-[#0A1B3D]">
                      <span className="font-semibold block text-[11px] text-[#2563EB] mb-0.5">
                        Observação Institucional:
                      </span>
                      {item.details.notes}
                    </div>
                  )}

                  {/* Action Buttons Row */}
                  <div className="pt-2 flex flex-wrap items-center gap-3">
                    {/* Ask SUSANNA */}
                    <button
                      onClick={() => onNavigate('assistente', { 
                        prompt: `Pode me explicar os resultados do meu ${item.title} em linguagem simples?` 
                      })}
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-blue-50 text-[#2563EB] border border-blue-200 hover:bg-blue-100 font-semibold text-xs transition active:scale-[0.98]"
                    >
                      <Sparkles size={14} />
                      <span>Pedir explicação à SUSANNA</span>
                      <ArrowRight size={13} />
                    </button>

                    {/* Download PDF simulation */}
                    {item.status === 'concluido' && (
                      <button
                        onClick={() => handleDownloadPdf(item.id)}
                        className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-medium text-xs transition active:scale-[0.98]"
                      >
                        {downloadSuccessId === item.id ? (
                          <>
                            <CheckCircle2 size={14} className="text-emerald-600" />
                            <span className="text-emerald-600 font-semibold">PDF Baixado com Sucesso!</span>
                          </>
                        ) : (
                          <>
                            <Download size={14} />
                            <span>Baixar Laudo Oficial (PDF)</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
