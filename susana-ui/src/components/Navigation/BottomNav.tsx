'use client';

import React from 'react';
import { 
  Home, 
  MessageSquare, 
  CalendarClock, 
  Activity, 
  FileText, 
  LogOut 
} from 'lucide-react';
import { TabId } from '@/components/Navigation/Sidebar';
import { SuzannaAvatar } from '@/components/Landing/MascotDisplay';

interface BottomNavProps {
  activeTab: TabId;
  onSelectTab: (tab: TabId) => void;
  onExit: () => void;
}

const navItems: { id: TabId; label: string; icon: React.ElementType }[] = [
  { id: 'inicio', label: 'Início', icon: Home },
  { id: 'assistente', label: 'Assistente', icon: MessageSquare },
  { id: 'servicos', label: 'Serviços', icon: CalendarClock },
  { id: 'monitoramento', label: 'Monitor', icon: Activity },
  { id: 'historico', label: 'Histórico', icon: FileText },
];

export function MobileHeader({ onExit }: { onExit: () => void }) {
  return (
    <header className="lg:hidden sticky top-0 z-40 glass-panel border-b border-slate-200/80 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2.5">
        <SuzannaAvatar size={34} />
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#2563EB] block">
            SUS Digital
          </span>
          <p className="text-xs font-bold text-[#0A1B3D]">Distrito Federal</p>
        </div>
      </div>

      <button
        onClick={onExit}
        className="p-2 text-slate-500 hover:text-rose-600 rounded-lg active:bg-slate-100"
        aria-label="Sair da plataforma"
      >
        <LogOut size={18} />
      </button>
    </header>
  );
}

export function BottomNav({ activeTab, onSelectTab }: BottomNavProps) {
  return (
    <nav 
      className="lg:hidden fixed bottom-0 left-0 right-0 z-40 glass-panel border-t border-slate-200/90 px-2 py-1.5 flex items-center justify-around shadow-lg"
      aria-label="Navegação mobile"
    >
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            className={`flex flex-col items-center justify-center min-w-[54px] min-h-[48px] px-1 py-1 rounded-xl transition ${
              isActive 
                ? 'text-[#2563EB] font-bold' 
                : 'text-slate-500 hover:text-slate-800'
            }`}
            aria-current={isActive ? 'page' : undefined}
          >
            <div className={`p-1 rounded-xl transition ${isActive ? 'bg-blue-100/70' : ''}`}>
              <Icon size={20} className={isActive ? 'text-[#2563EB]' : 'text-slate-500'} />
            </div>
            <span className="text-[10px] tracking-tight mt-0.5">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
