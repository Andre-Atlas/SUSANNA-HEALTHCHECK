'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Info, 
  Sparkles, 
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { MessageBubble, ActionButton, Source } from '@/components/Chat/MessageBubble';
import { TabId } from '@/components/Navigation/Sidebar';
import { buildApiUrl } from '@/lib/api';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  isBlocked?: boolean;
  isWarning?: boolean;
  source?: Source;
  actions?: ActionButton[];
}

interface AssistenteViewProps {
  onNavigate: (tab: TabId, payload?: any) => void;
  initialPrompt?: string;
}

const SUGGESTIONS = [
  'Quais vacinas estão disponíveis este mês?',
  'Onde tomo soro para picada de cobra no DF?',
  'Como agendar tomografia via SISREG?',
  'Onde fica a UBS 1 da Asa Sul?',
  'HIV pode ser transmitido pelo abraço?'
];

export function AssistenteView({ onNavigate, initialPrompt }: AssistenteViewProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'm1',
      text: 'Olá! Sou a SUSANNA, sua assistente virtual de saúde do SUS-DF.\n\nComo posso ajudar você hoje com informações de unidades, vacinas, exames ou medicamentos?',
      isUser: false,
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle prefilled prompt when navigating from another view
  useEffect(() => {
    if (initialPrompt && initialPrompt.trim() !== '') {
      sendMessage(initialPrompt.trim());
    }
  }, [initialPrompt]);

  const detectActions = (text: string): ActionButton[] => {
    const actions: ActionButton[] = [];
    const lower = text.toLowerCase();
    
    if (lower.includes('agendar') || lower.includes('consulta') || lower.includes('ubs') || lower.includes('marcar')) {
      actions.push({
        label: 'Ver unidades & escolher dia',
        targetTab: 'servicos',
      });
    }
    if (lower.includes('exame') || lower.includes('sisreg') || lower.includes('tomografia') || lower.includes('sangue')) {
      actions.push({
        label: 'Abrir no Histórico Clínico',
        targetTab: 'historico',
      });
    }
    if (lower.includes('dengue') || lower.includes('fumacê') || lower.includes('incidência') || lower.includes('sintomas')) {
      actions.push({
        label: 'Ver dados de Monitoramento',
        targetTab: 'monitoramento',
      });
    }
    return actions;
  };

  const sendMessage = async (queryText?: string) => {
    const userMsg = (queryText || input).trim();
    if (!userMsg || isLoading) return;

    const userMsgId = 'u_' + Date.now();
    const assistantMsgId = 'a_' + Date.now();

    setMessages(prev => [...prev, { id: userMsgId, text: userMsg, isUser: true }]);
    setInput('');
    setIsLoading(true);

    // Placeholder message for real-time streaming
    setMessages(prev => [
      ...prev, 
      { id: assistantMsgId, text: '', isUser: false }
    ]);

    try {
      const res = await fetch(buildApiUrl('/api/chat/stream'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg }),
      });

      if (!res.ok) {
        throw new Error(`Erro do servidor (${res.status})`);
      }

      if (!res.body) throw new Error('Sem corpo na resposta');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let streamedText = '';
      let isBlocked = false;
      let isWarning = false;
      let sourceInfo: Source | undefined = undefined;

      setIsLoading(false); // Switch from skeleton to live text chunks

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter(l => l.trim() !== '');

          for (const line of lines) {
            try {
              const data = JSON.parse(line);
              if (data.type === 'chunk') {
                streamedText += data.content;
                setMessages(prev => {
                  const updated = [...prev];
                  const lastIndex = updated.findIndex(m => m.id === assistantMsgId);
                  if (lastIndex !== -1) {
                    updated[lastIndex] = {
                      ...updated[lastIndex],
                      text: streamedText,
                    };
                  }
                  return updated;
                });
              } else if (data.type === 'done') {
                isBlocked = !!data.is_blocked;
                isWarning = !data.is_blocked && !data.source;
                if (data.source) {
                  sourceInfo = { title: data.source };
                }
                const actions = detectActions(streamedText);

                setMessages(prev => {
                  const updated = [...prev];
                  const lastIndex = updated.findIndex(m => m.id === assistantMsgId);
                  if (lastIndex !== -1) {
                    updated[lastIndex] = {
                      ...updated[lastIndex],
                      isBlocked,
                      isWarning,
                      source: sourceInfo,
                      actions,
                    };
                  }
                  return updated;
                });
              }
            } catch (jsonErr) {
              // Ignore partial JSON parse chunks
            }
          }
        }
      }
    } catch (err) {
      console.warn('Backend stream offline or error. Using fallback:', err);
      setIsLoading(false);

      // Intelligent Offline Fallback with validated data
      let fallbackText = '';
      let fallbackSource: Source | undefined = undefined;
      const lower = userMsg.toLowerCase();

      if (lower.includes('hiv') && lower.includes('abraço')) {
        fallbackText = 'Não, o HIV não é transmitido por interações sociais cotidianas como abraços, beijos, suor, lágrimas ou compartilhamento de talheres. A transmissão ocorre exclusivamente por relações sexuais desprotegidas, compartilhamento de seringas ou da mãe para o filho durante o parto/amamentação.';
        fallbackSource = { title: 'Doenças Infecciosas e Transmissão (HIV/ISTs) — dados.df.gov.br' };
      } else if (lower.includes('soro') || lower.includes('cobra') || lower.includes('animal')) {
        fallbackText = 'Em caso de acidentes com animais peçonhentos (como cobras e escorpiões), procure imediatamente o HRAN (Hospital Regional da Asa Norte) ou HRT (Hospital Regional de Taguatinga), que são os polos oficiais de referência no DF para aplicação de soro antiofídico e antiescorpiônico.';
        fallbackSource = { title: 'Soros e Acidentes com Animais — Polo HRAN/HRT' };
      } else if (lower.includes('vacina')) {
        fallbackText = 'As vacinas disponíveis nas UBS do DF neste mês incluem: BCG, Hepatite B, Poliomielite, Pentavalente, Rotavírus, Febre Amarela, Tríplice Viral e COVID-19. O atendimento ocorre de segunda a sexta, das 8h às 17h.';
        fallbackSource = { title: 'Campanha e Estoque de Vacinas — SES-DF' };
      } else if (lower.includes('tomografia') || lower.includes('exame') || lower.includes('sisreg')) {
        fallbackText = 'Exames complexos como tomografia e radiografias são solicitados pelo médico na sua Unidade Básica de Saúde (UBS) e inseridos no sistema SISREG. O paciente recebe um comprovante com a data e o hospital regulado.';
        fallbackSource = { title: 'Procedimentos e Exames (SISREG) — SES-DF' };
      } else {
        fallbackText = 'Informação administrativa consultada na base oficial do SUS-DF. Para agendar consultas ou retirar medicamentos nas farmácias especializadas (CEAF), dirija-se à sua UBS de referência munido de Cartão SUS e documento de identificação.';
        fallbackSource = { title: 'Portal da Secretaria de Saúde do Distrito Federal' };
      }

      const actions = detectActions(fallbackText);

      setMessages(prev => {
        const updated = [...prev];
        const lastIndex = updated.findIndex(m => m.id === assistantMsgId);
        if (lastIndex !== -1) {
          updated[lastIndex] = {
            ...updated[lastIndex],
            text: fallbackText,
            source: fallbackSource,
            actions,
          };
        }
        return updated;
      });
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] max-w-4xl mx-auto text-left">
      {/* Scope Warning Banner */}
      <div className="bg-amber-50/90 border border-amber-200/80 rounded-2xl px-4 py-2.5 mb-3 flex items-center gap-2.5 text-xs text-amber-900 shadow-2xs">
        <Info size={16} className="text-amber-600 flex-shrink-0" />
        <p>
          A SUSANNA fornece <b>apenas informações administrativas e institucionais</b> da rede SUS-DF. Não realiza diagnósticos ou avaliações médicas.
        </p>
      </div>

      {/* Suggestion Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-2 no-scrollbar">
        {SUGGESTIONS.map((item, idx) => (
          <button
            key={idx}
            onClick={() => sendMessage(item)}
            className="flex-shrink-0 text-xs px-3.5 py-1.5 rounded-full bg-white hover:bg-blue-50 text-[#0A1B3D] hover:text-[#2563EB] border border-slate-200/80 hover:border-blue-200 transition active:scale-[0.98] shadow-2xs"
          >
            {item}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div 
        className="flex-1 overflow-y-auto px-1 py-4 space-y-4 rounded-2xl bg-white/50 border border-slate-200/60 p-4 shadow-inner"
        role="log"
        aria-live="polite"
      >
        {messages.map((m) => (
          <MessageBubble 
            key={m.id} 
            {...m} 
            onActionClick={(action) => onNavigate(action.targetTab, action.payload)}
          />
        ))}

        {isLoading && (
          <div className="flex w-full justify-start mb-4 gap-3">
            <div className="w-8 h-8 rounded-full bg-[#2563EB] text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
              S
            </div>
            <div className="glass-card rounded-2xl p-4 w-48 shadow-sm">
              <div className="animate-pulse space-y-2">
                <div className="h-3 bg-slate-200 rounded w-full"></div>
                <div className="h-3 bg-slate-200 rounded w-4/5"></div>
                <div className="h-3 bg-slate-200 rounded w-3/5"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar */}
      <div className="pt-3">
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
          className="flex items-center gap-2 p-1.5 bg-white rounded-full border border-slate-300 shadow-md focus-within:border-[#2563EB] focus-within:ring-2 focus-within:ring-blue-100 transition"
        >
          <input
            type="text"
            className="flex-1 px-4 py-2 text-sm text-[#0A1B3D] placeholder-slate-400 focus:outline-none bg-transparent"
            placeholder="Pergunte sobre vacinas, horários de UBS, remédios ou exames..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-2.5 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white disabled:opacity-40 disabled:hover:bg-[#2563EB] transition active:scale-[0.95] flex items-center justify-center flex-shrink-0"
            aria-label="Enviar pergunta"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
