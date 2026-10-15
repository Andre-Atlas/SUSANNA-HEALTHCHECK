'use client';

import React, { useState } from 'react';
import { 
  Calendar as CalendarIcon, 
  MapPin, 
  Clock, 
  CheckCircle, 
  Search, 
  ChevronLeft, 
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { Appointment } from '@/components/Views/InicioView';
import { TabId } from '@/components/Navigation/Sidebar';

interface ServicosViewProps {
  onNavigate: (tab: TabId) => void;
  onAddAppointment: (apt: Appointment) => void;
  preselectedSpecialty?: string;
}

interface Unit {
  id: string;
  name: string;
  address: string;
  distance: string;
  specialties: string[];
  hours: string;
}

const UNITS: Unit[] = [
  {
    id: 'ubs1',
    name: 'UBS 1 Asa Norte',
    address: 'EQN 114/115, Asa Norte, Brasília - DF',
    distance: '1.2 km',
    specialties: ['clinico', 'vacinacao', 'odonto'],
    hours: 'Seg a Sex · 07h às 19h',
  },
  {
    id: 'ubs2',
    name: 'UBS 2 Ceilândia Sul',
    address: 'QNN 15, Área Especial, Ceilândia - DF',
    distance: '18 km',
    specialties: ['clinico', 'pediatria', 'vacinacao'],
    hours: 'Seg a Sex · 07h às 18h',
  },
  {
    id: 'hran',
    name: 'HRAN - Hospital Regional da Asa Norte',
    address: 'SMHN Quadra 101, Asa Norte, Brasília - DF',
    distance: '2.5 km',
    specialties: ['clinico', 'especialistas', 'soros'],
    hours: 'Emergência 24h · Ambulatório 08h às 18h',
  },
  {
    id: 'ceaf',
    name: 'Farmácia de Alto Custo (CEAF Asa Sul)',
    address: 'Estação Metrô 102 Sul, Brasília - DF',
    distance: '3.8 km',
    specialties: ['medicamentos'],
    hours: 'Seg a Sex · 07h às 19h',
  },
];

// October 2026 Calendar days data
const CALENDAR_DAYS = [
  // Sept placeholders
  { day: 28, inMonth: false },
  { day: 29, inMonth: false },
  { day: 30, inMonth: false },
  // Oct 1 to 31 (Oct 1 2026 is a Thursday)
  { day: 1, inMonth: true, status: 'few' },
  { day: 2, inMonth: true, status: 'full' },
  { day: 3, inMonth: true, status: 'closed' },
  { day: 4, inMonth: true, status: 'closed' },
  { day: 5, inMonth: true, status: 'full' },
  { day: 6, inMonth: true, status: 'available' },
  { day: 7, inMonth: true, status: 'available' },
  { day: 8, inMonth: true, status: 'few' },
  { day: 9, inMonth: true, status: 'full' },
  { day: 10, inMonth: true, status: 'closed' },
  { day: 11, inMonth: true, status: 'closed' },
  { day: 12, inMonth: true, status: 'closed' }, // Feriado
  { day: 13, inMonth: true, status: 'available' },
  { day: 14, inMonth: true, status: 'available' },
  { day: 15, inMonth: true, status: 'available' },
  { day: 16, inMonth: true, status: 'few' },
  { day: 17, inMonth: true, status: 'closed' },
  { day: 18, inMonth: true, status: 'closed' },
  { day: 19, inMonth: true, status: 'available' },
  { day: 20, inMonth: true, status: 'available' },
  { day: 21, inMonth: true, status: 'available' },
  { day: 22, inMonth: true, status: 'few' },
  { day: 23, inMonth: true, status: 'full' },
  { day: 24, inMonth: true, status: 'closed' },
  { day: 25, inMonth: true, status: 'closed' },
  { day: 26, inMonth: true, status: 'available' },
  { day: 27, inMonth: true, status: 'available' },
  { day: 28, inMonth: true, status: 'available' },
  { day: 29, inMonth: true, status: 'available' },
  { day: 30, inMonth: true, status: 'few' },
  { day: 31, inMonth: true, status: 'closed' },
];

const TIME_SLOTS = ['08:30', '10:00', '11:15', '14:00', '15:30', '16:45'];

export function ServicosView({ onNavigate, onAddAppointment, preselectedSpecialty }: ServicosViewProps) {
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>(preselectedSpecialty || 'todos');
  const [selectedUnit, setSelectedUnit] = useState<Unit>(UNITS[0]);
  const [selectedDay, setSelectedDay] = useState<number>(20);
  const [selectedTime, setSelectedTime] = useState<string>('14:00');
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);

  const filteredUnits = selectedSpecialty === 'todos'
    ? UNITS
    : UNITS.filter(u => u.specialties.includes(selectedSpecialty));

  const handleConfirm = () => {
    const specialtyName = 
      selectedSpecialty === 'vacinacao' ? 'Vacinação (Imunização)' :
      selectedSpecialty === 'pediatria' ? 'Consulta Pediátrica' :
      selectedSpecialty === 'odonto' ? 'Saúde Bucal (Odontologia)' :
      'Clínico Geral';

    const newAppointment: Appointment = {
      id: 'apt_' + Date.now(),
      title: `${specialtyName} · ${selectedUnit.name}`,
      unit: selectedUnit.address,
      date: `Ter, ${selectedDay} out · ${selectedTime}`,
      type: selectedSpecialty === 'vacinacao' ? 'medicamento' : 'consulta',
    };

    onAddAppointment(newAppointment);
    setIsSuccessModalOpen(true);
  };

  return (
    <div className="space-y-8 text-left max-w-5xl mx-auto pb-12">
      {/* Title */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0A1B3D] tracking-tight">
          Serviços e <span className="text-[#2563EB]">agendamentos</span>
        </h1>
        <p className="text-sm text-[#5B6B8C] mt-1">
          Encontre unidades públicas da SES-DF e reserve seu horário de atendimento.
        </p>
      </div>

      {/* Specialty Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        {[
          { id: 'todos', label: 'Todos os Serviços' },
          { id: 'clinico', label: 'Clínico Geral' },
          { id: 'vacinacao', label: 'Vacinação' },
          { id: 'pediatria', label: 'Pediatria' },
          { id: 'odonto', label: 'Odontologia' },
        ].map(item => (
          <button
            key={item.id}
            onClick={() => setSelectedSpecialty(item.id)}
            className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition active:scale-[0.98] ${
              selectedSpecialty === item.id
                ? 'bg-[#2563EB] text-white shadow-sm'
                : 'bg-white hover:bg-slate-100 text-[#0A1B3D] border border-slate-200'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Grid: Unit Selection & Calendar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Select Unit (Col-5) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-[#0A1B3D]">
              1. Selecione a Unidade de Saúde
            </h2>
            <span className="text-xs text-[#5B6B8C]">{filteredUnits.length} encontradas</span>
          </div>

          <div className="space-y-3">
            {filteredUnits.map((u) => {
              const isSelected = selectedUnit.id === u.id;
              return (
                <div
                  key={u.id}
                  onClick={() => setSelectedUnit(u)}
                  className={`p-4 rounded-2xl cursor-pointer transition border text-left ${
                    isSelected
                      ? 'bg-blue-50/80 border-[#2563EB] shadow-sm'
                      : 'bg-white hover:border-slate-300 border-slate-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-bold text-[#0A1B3D]">{u.name}</p>
                    <span className="text-[11px] font-semibold text-[#2563EB] bg-blue-100 px-2 py-0.5 rounded-full flex-shrink-0">
                      {u.distance}
                    </span>
                  </div>
                  <p className="text-xs text-[#5B6B8C] mt-1 flex items-center gap-1">
                    <MapPin size={12} className="flex-shrink-0" />
                    <span>{u.address}</span>
                  </p>
                  <p className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
                    <Clock size={11} className="flex-shrink-0" />
                    <span>{u.hours}</span>
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Calendar & Time Slots (Col-7) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass-card rounded-3xl p-6 border border-slate-200/90 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-[#0A1B3D] flex items-center gap-2">
                  <CalendarIcon size={18} className="text-[#2563EB]" />
                  <span>2. Escolha a Data · Outubro 2026</span>
                </h2>
                <p className="text-xs text-[#5B6B8C] mt-0.5">
                  Selecione um dos dias destacados com vagas abertas.
                </p>
              </div>
              <div className="flex items-center gap-1 text-slate-400">
                <span className="text-xs font-semibold text-[#0A1B3D]">Outubro</span>
              </div>
            </div>

            {/* Calendar Grid */}
            <div className="mb-4">
              <div className="grid grid-cols-7 gap-1 text-center text-xs font-semibold text-[#5B6B8C] mb-2">
                <span>Dom</span>
                <span>Seg</span>
                <span>Ter</span>
                <span>Qua</span>
                <span>Qui</span>
                <span>Sex</span>
                <span>Sáb</span>
              </div>
              <div className="grid grid-cols-7 gap-1.5 text-center">
                {CALENDAR_DAYS.map((d, i) => {
                  const isSelected = d.day === selectedDay && d.inMonth;
                  const isSelectable = d.inMonth && (d.status === 'available' || d.status === 'few');

                  let dotClass = 'hidden';
                  if (d.status === 'available') dotClass = 'bg-emerald-500';
                  if (d.status === 'few') dotClass = 'bg-amber-500';

                  return (
                    <button
                      key={i}
                      disabled={!isSelectable}
                      onClick={() => isSelectable && setSelectedDay(d.day)}
                      className={`h-10 rounded-xl flex flex-col items-center justify-center relative text-xs font-medium transition ${
                        !d.inMonth ? 'text-slate-300 cursor-default' :
                        !isSelectable ? 'text-slate-400 bg-slate-50 cursor-not-allowed opacity-60' :
                        isSelected ? 'bg-[#2563EB] text-white font-bold shadow-md scale-105' :
                        'bg-white hover:bg-blue-50 text-[#0A1B3D] border border-slate-200'
                      }`}
                    >
                      <span>{d.day}</span>
                      {d.inMonth && (
                        <span className={`w-1.5 h-1.5 rounded-full absolute bottom-1 ${isSelected ? 'bg-white' : dotClass}`} />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Calendar Legend */}
            <div className="flex items-center justify-center gap-4 text-[11px] text-[#5B6B8C] pt-2 border-t border-slate-100">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>Vagas Abertas</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>Poucas Vagas</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-slate-300" />
                <span>Sem Vagas</span>
              </div>
            </div>

            {/* Time Slot Picker */}
            <div className="mt-6 pt-5 border-t border-slate-200/80">
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#0A1B3D] mb-3">
                3. Escolha o Horário
              </h3>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {TIME_SLOTS.map((slot) => {
                  const isSelected = selectedTime === slot;
                  return (
                    <button
                      key={slot}
                      onClick={() => setSelectedTime(slot)}
                      className={`py-2 px-1 text-xs font-semibold rounded-xl transition ${
                        isSelected
                          ? 'bg-[#2563EB] text-white shadow-sm'
                          : 'bg-white hover:bg-blue-50 text-[#0A1B3D] border border-slate-200'
                      }`}
                    >
                      {slot}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Submit Bar */}
            <div className="mt-6 pt-4 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-left">
                <p className="text-xs text-slate-400">Resumo da seleção</p>
                <p className="text-sm font-bold text-[#0A1B3D]">
                  Dia {selectedDay} de Outubro · {selectedTime}
                </p>
              </div>
              <button
                onClick={handleConfirm}
                className="w-full sm:w-auto px-6 py-3 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold text-xs tracking-wide shadow-md active:scale-[0.98] transition flex items-center justify-center gap-2"
              >
                <span>Confirmar Agendamento</span>
                <CheckCircle size={15} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Success Confirmation Modal */}
      {isSuccessModalOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-white rounded-3xl p-6 max-w-md w-full text-center shadow-2xl border border-slate-100 space-y-4">
            <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle size={32} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-[#0A1B3D]">Agendamento Confirmado!</h3>
              <p className="text-xs text-slate-500 mt-1">
                Sua solicitação foi registrada no sistema unificado do SUS-DF.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-4 text-left text-xs space-y-2 border border-slate-200/80">
              <p><b className="text-slate-700">Paciente:</b> Maria Silva de Oliveira</p>
              <p><b className="text-slate-700">Unidade:</b> {selectedUnit.name}</p>
              <p><b className="text-slate-700">Endereço:</b> {selectedUnit.address}</p>
              <p><b className="text-slate-700">Data e Hora:</b> Terça-feira, {selectedDay} de outubro de 2026 às {selectedTime}</p>
            </div>

            <p className="text-[11px] text-slate-400">
              Apresente seu Cartão SUS e documento com foto no guichê de acolhimento com 15 min de antecedência.
            </p>

            <button
              onClick={() => {
                setIsSuccessModalOpen(false);
                onNavigate('inicio');
              }}
              className="w-full py-3 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold text-sm shadow-md transition flex items-center justify-center gap-2"
            >
              <span>Ver em Próximos Compromissos</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
