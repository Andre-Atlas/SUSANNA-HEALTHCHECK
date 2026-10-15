'use client';

import React, { useState } from 'react';
import { 
  ShieldAlert, 
  AlertTriangle, 
  ExternalLink, 
  ThumbsUp, 
  ThumbsDown, 
  ArrowRight,
  Check
} from 'lucide-react';
import { motion } from 'framer-motion';
import { SuzannaAvatar } from '@/components/Landing/MascotDisplay';

export interface ActionButton {
  label: string;
  targetTab: 'inicio' | 'assistente' | 'servicos' | 'monitoramento' | 'historico';
  payload?: any;
}

export interface Source {
  title: string;
  url?: string;
}

export interface MessageProps {
  id?: string;
  text: string;
  isUser: boolean;
  isBlocked?: boolean;
  isWarning?: boolean;
  source?: Source;
  actions?: ActionButton[];
  onActionClick?: (action: ActionButton) => void;
}

export function MessageBubble({ 
  text, 
  isUser, 
  isBlocked, 
  isWarning, 
  source, 
  actions,
  onActionClick 
}: MessageProps) {
  const [feedback, setFeedback] = useState<'liked' | 'disliked' | null>(null);

  if (isUser) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="flex w-full justify-end mb-4"
      >
        <div className="max-w-[85%] md:max-w-[70%] rounded-2xl rounded-tr-sm px-4 py-3 bg-[#2563EB] text-white shadow-sm text-sm md:text-base leading-relaxed">
          {text}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex w-full justify-start mb-5 gap-3"
    >
      {/* Suzanna Avatar */}
      <div className="flex-shrink-0 pt-0.5">
        <SuzannaAvatar size={34} />
      </div>

      <div className="max-w-[88%] md:max-w-[75%] space-y-2">
        {/* Main message bubble */}
        <div className={`rounded-2xl rounded-tl-sm p-4 text-sm md:text-base leading-relaxed glass-card text-[#0A1B3D] shadow-sm ${
          isBlocked ? 'border-l-4 border-l-rose-500 bg-rose-50/40' : 
          isWarning ? 'border-l-4 border-l-amber-500 bg-amber-50/40' : 
          'border-slate-200/90 bg-white'
        }`}>
          {/* Header warning or block badges */}
          {isBlocked && (
            <div className="flex items-center gap-2 text-rose-600 mb-2 font-semibold text-xs">
              <ShieldAlert size={16} />
              <span>Limite Institucional / Não Clínico</span>
            </div>
          )}
          {isWarning && (
            <div className="flex items-center gap-2 text-amber-600 mb-2 font-semibold text-xs">
              <AlertTriangle size={16} />
              <span>Informação Parcial ou Ausente</span>
            </div>
          )}

          {/* Text content */}
          <div className="whitespace-pre-wrap">{text}</div>

          {/* Official Source */}
          {source && (
            <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <div className="flex items-center gap-1.5 truncate">
                <span className="font-semibold text-[#2563EB]">Fonte Oficial:</span>
                {source.url ? (
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noreferrer" 
                    className="text-[#2563EB] hover:underline flex items-center gap-1 truncate"
                  >
                    <span>{source.title}</span>
                    <ExternalLink size={12} />
                  </a>
                ) : (
                  <span className="truncate">{source.title}</span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons within Assistant response */}
        {actions && actions.length > 0 && (
          <div className="flex flex-wrap gap-2 pt-1">
            {actions.map((act, idx) => (
              <button
                key={idx}
                onClick={() => onActionClick && onActionClick(act)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-blue-50 text-[#2563EB] border border-blue-200/80 hover:bg-blue-100 hover:border-blue-300 transition active:scale-[0.98] shadow-2xs"
              >
                <span>{act.label}</span>
                <ArrowRight size={13} />
              </button>
            ))}
          </div>
        )}

        {/* Helpful Feedback Toolbar */}
        <div className="flex items-center gap-2 text-[11px] text-slate-400 pl-1">
          <span>Esta resposta foi útil?</span>
          <button
            onClick={() => setFeedback('liked')}
            className={`p-1 rounded-md hover:bg-slate-100 transition ${feedback === 'liked' ? 'text-emerald-600 font-bold' : ''}`}
            title="Útil"
            aria-label="Avaliar como útil"
          >
            {feedback === 'liked' ? <Check size={13} /> : <ThumbsUp size={13} />}
          </button>
          <button
            onClick={() => setFeedback('disliked')}
            className={`p-1 rounded-md hover:bg-slate-100 transition ${feedback === 'disliked' ? 'text-rose-600 font-bold' : ''}`}
            title="Não foi útil"
            aria-label="Avaliar como não útil"
          >
            <ThumbsDown size={13} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
