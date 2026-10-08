import React from 'react';
import { ShieldAlert, AlertTriangle, Siren } from 'lucide-react';
import { motion } from 'framer-motion';

interface Source {
  title: string;
  url?: string;
}

interface Citation {
  ref: number;
  title: string;
  url?: string | null;
}

interface MessageBubbleProps {
  text: string;
  isUser: boolean;
  isBlocked?: boolean;
  isWarning?: boolean;
  isEmergency?: boolean;
  source?: Source;
  citations?: Citation[];
}

/** Lista as fontes citadas pela resposta: link quando houver URL; senão, referência textual. */
export function CitationList({ citations }: { citations: Citation[] }) {
  return (
    <div className="mt-2 text-xs border-t border-gray-200 pt-2">
      <span className="font-semibold text-[var(--susana-blue)]">
        {citations.length > 1 ? 'Fontes Oficiais:' : 'Fonte Oficial:'}
      </span>
      <ul className="mt-1 space-y-1">
        {citations.map((c) => (
          <li key={c.ref} className="flex gap-1">
            <span className="text-gray-500">[{c.ref}]</span>
            {c.url ? (
              <a href={c.url} target="_blank" rel="noreferrer" className="text-blue-600 underline break-all">
                {c.title}
              </a>
            ) : (
              <span className="text-gray-600">{c.title}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function SourceCitation({ source }: { source: Source }) {
  return (
    <div className="mt-2 text-xs border-t border-gray-200 pt-2 flex items-center gap-1">
      <span className="font-semibold text-[var(--susana-blue)]">Fonte Oficial:</span>
      {source.url ? (
        <a href={source.url} target="_blank" rel="noreferrer" className="text-blue-600 underline">
          {source.title}
        </a>
      ) : (
        <span className="text-gray-600">{source.title}</span>
      )}
    </div>
  );
}

export function MessageBubble({ text, isUser, isBlocked, isWarning, isEmergency, source, citations }: MessageBubbleProps) {
  const bgClass = isUser ? 'bg-[var(--susana-blue-light)]' : 'bg-white shadow-sm';
  const alignClass = isUser ? 'justify-end' : 'justify-start';
  
  // Scopes: 
  // isBlocked (Caso C) = Red border
  // isWarning (Caso B) = Yellow border
  let borderClass = 'border-transparent';
  if (isBlocked) borderClass = 'border-[var(--danger)] border-2';
  if (isWarning) borderClass = 'border-[var(--warning)] border-2';
  if (isEmergency) borderClass = 'border-[var(--danger)] border-2 bg-red-50';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex w-full ${alignClass} mb-4`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-[var(--susana-blue)] flex-shrink-0 flex items-center justify-center mr-2 text-white font-bold text-sm">
          S
        </div>
      )}
      
      <div className={`max-w-[80%] rounded-2xl p-4 text-[var(--text)] ${bgClass} ${borderClass}`}>
        {isBlocked && (
          <div className="flex items-center gap-2 text-[var(--danger)] mb-2 font-bold text-sm">
            <ShieldAlert size={16} />
            <span>Fora de Escopo / Não Clínico</span>
          </div>
        )}
        {isEmergency && (
          <div className="flex items-center gap-2 text-[var(--danger)] mb-2 font-bold text-sm" role="alert">
            <Siren size={16} />
            <span>Possível emergência — ligue 192</span>
          </div>
        )}
        {isWarning && (
          <div className="flex items-center gap-2 text-[var(--warning)] mb-2 font-bold text-sm">
            <AlertTriangle size={16} />
            <span>Informação Ausente</span>
          </div>
        )}
        
        <div className="text-[16px] leading-relaxed whitespace-pre-wrap">{text}</div>
        
        {!isUser && citations && citations.length > 0 ? (
          <CitationList citations={citations} />
        ) : (
          source && !isUser && <SourceCitation source={source} />
        )}
      </div>
      
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-300 flex-shrink-0 flex items-center justify-center ml-2 text-gray-700">
          U
        </div>
      )}
    </motion.div>
  );
}
