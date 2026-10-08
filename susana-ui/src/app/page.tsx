'use client';

import React, { useState } from 'react';
import { MessageBubble } from '@/components/Chat/MessageBubble';
import { Info } from 'lucide-react';

interface ChatMessage {
  text: string;
  isUser: boolean;
  isBlocked?: boolean;
  isWarning?: boolean;
  source?: { title: string; url?: string };
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      text: 'Olá! Sou a Susana, sua assistente de saúde do SUS-DF.\nComo posso ajudar você hoje?',
      isUser: false,
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages(prev => [...prev, { text: userMsg, isUser: true }]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const chatHistory = messages.slice(1).map(m => ({ text: m.text, isUser: m.isUser }));
      
      const res = await fetch(`${apiUrl}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history: chatHistory }),
      });

      if (!res.body) throw new Error("Sem corpo na resposta");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let streamedText = '';
      let buffer = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          
          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const data = JSON.parse(line);
              
              if (data.type === 'chunk') {
                streamedText += data.content;
              } else if (data.type === 'done') {
                setIsLoading(false);
                setMessages(prev => [
                  ...prev, 
                  {
                    text: streamedText,
                    isUser: false,
                    isBlocked: data.is_blocked,
                    isWarning: !data.is_blocked && !data.source,
                    source: data.citations?.length > 0 ? { title: data.citations[0].title, url: data.citations[0].url } : (data.source ? { title: data.source } : undefined)
                  }
                ]);
              }
            } catch (e) {
              console.error("Erro no parse do JSON chunk", e);
            }
          }
        }
      }
    } catch (e) {
      setIsLoading(false);
      setMessages(prev => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1] = {
          text: 'Desculpe, não consegui conectar aos servidores no momento.',
          isUser: false,
          isWarning: true
        };
        return newMsgs;
      });
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-[#E0F2FE] shadow-sm px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#0284C7] flex items-center justify-center text-white font-bold text-lg">S</div>
          <div>
            <h1 className="text-[#0284C7] font-bold text-lg leading-tight">Susana</h1>
            <p className="text-gray-600 text-xs">Assistente de Saúde SUS-DF</p>
          </div>
        </div>
      </div>

      {/* Warning scope banner */}
      <div className="bg-yellow-50 border-b border-yellow-200 px-6 py-2 flex items-center gap-2 text-sm text-yellow-800">
        <Info size={16} />
        A Susana fornece <b>apenas informações administrativas e institucionais</b>. Não realiza diagnósticos ou avaliações clínicas.
      </div>

      {/* Chat Area */}
      <div 
        className="flex-1 overflow-y-auto p-6 space-y-4"
        role="log"
        aria-live="polite"
      >
        {messages.map((m, i) => (
          <MessageBubble key={i} {...m} />
        ))}
        {isLoading && (
          <div className="flex w-full justify-start mb-4" role="status" aria-label="Carregando">
            <div className="w-8 h-8 rounded-full bg-[#0284C7] flex-shrink-0 flex items-center justify-center mr-2 text-white font-bold text-sm">
              S
            </div>
            <div className="max-w-[80%] rounded-2xl p-4 bg-white shadow-sm border border-transparent">
              <div className="animate-pulse flex flex-col gap-2 w-32">
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                <div className="h-3 bg-gray-200 rounded w-4/6"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <label htmlFor="chat-input" className="sr-only">Digite sua mensagem</label>
          <input 
            id="chat-input"
            type="text" 
            className="flex-1 border border-gray-300 rounded-full px-6 py-3 focus:outline-none focus:border-[#0284C7] text-gray-800"
            placeholder="Pergunte sobre vacinação, UBS, ou medicamentos..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
          />
          <button 
            onClick={sendMessage}
            className="bg-[#0284C7] text-white px-6 py-3 rounded-full font-semibold"
            aria-label="Enviar mensagem"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}
