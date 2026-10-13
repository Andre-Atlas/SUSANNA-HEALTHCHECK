'use client';

import React from 'react';
import { 
  Home, 
  MessageSquare, 
  CalendarClock, 
  Activity, 
  FileText, 
  LogOut,
  Sparkles
} from 'lucide-react';
import { SuzannaAvatar } from '@/components/Landing/MascotDisplay';

export type TabId = 'inicio' | 'assistente' | 'servicos' | 'monitoramento' | 'historico';

interface SidebarProps {
  activeTab: TabId;
  onSelectTab: (tab: TabId) => void;
  onExit: () => void;
}

const navItems: { id: TabId; label: string; icon: React.ElementType; badge?: string }[] = [
  { id: 'inicio', label: 'Início', icon: Home },
  { id: 'assistente', label: 'Assistente', icon: MessageSquare, badge: 'IA' },
  { id: 'servicos', label: 'Serviços', icon: CalendarClock },
  { id: 'monitoramento', label: 'Monitoramento', icon: Activity },
  { id: 'historico', label: 'Histórico', icon: FileText },
];

export function Sidebar({ activeTab, onSelectTab, onExit }: SidebarProps) {
  return (
    <aside 
      className="hidden lg:flex flex-col w-64 h-screen sticky top-0 glass-panel border-r border-slate-200/80 p-5 select-none z-30"
      aria-label="Navegação Principal"
    >
      {/* Brand Header */}
      <div className="flex items-center gap-3 pb-6 border-b border-slate-200/60">
        <SuzannaAvatar size={42} />
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#2563EB] block">
            SUS Digital
          </span>
          <h1 className="text-base font-bold text-[#0A1B3D] leading-tight">
            Distrito Federal
          </h1>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-6 space-y-1.5" role="navigation">
        <p className="px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
          Plataforma
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-3 rounded-2xl text-sm font-medium transition duration-150 ${
                isActive 
                  ? 'bg-[#2563EB] text-white shadow-md shadow-blue-500/20' 
                  : 'text-slate-600 hover:text-[#0A1B3D] hover:bg-white/80 active:scale-[0.99]'
              }`}
              aria-current={isActive ? 'page' : undefined}
            >
              <div className="flex items-center gap-3">
                <Icon size={19} className={isActive ? 'text-white' : 'text-slate-500'} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  isActive ? 'bg-white/20 text-white' : 'bg-blue-100 text-[#2563EB]'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Mini Suzanna AI Card */}
      <div className="p-3.5 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100/80 mb-4 text-left">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles size={14} className="text-[#2563EB]" />
          <span className="text-xs font-bold text-[#0A1B3D]">Suzanna IA</span>
        </div>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          Tire dúvidas e consulte unidades oficiais do DF em tempo real.
        </p>
      </div>

      {/* Footer / User Profile & Exit */}
      <div className="pt-4 border-t border-slate-200/60 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center font-bold text-xs text-slate-700">
            M
          </div>
          <div className="text-left">
            <p className="text-xs font-semibold text-[#0A1B3D] leading-tight">Maria Silva</p>
            <p className="text-[10px] text-slate-400">CNS: 700.123...4</p>
          </div>
        </div>

        <button
          onClick={onExit}
          className="p-2 text-slate-400 hover:text-rose-600 rounded-xl hover:bg-rose-50 transition"
          title="Sair para a página inicial"
          aria-label="Sair da plataforma"
        >
          <LogOut size={17} />
        </button>
      </div>
    </aside>
  );
}
