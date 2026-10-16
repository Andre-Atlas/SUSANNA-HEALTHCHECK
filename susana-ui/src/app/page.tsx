'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Navigation } from 'lucide-react';
import { buildApiUrl, createApiUrl } from '@/lib/api';
import { authHeaders } from '@/lib/apiClient';
import type { AgendaProposal, CitizenProfile } from '@/lib/types';
import { AuthProvider, useAuth } from '@/context/AuthProvider';
import { GeoProvider, useGeo } from '@/context/GeoProvider';
import { AgendaProvider, useAgenda } from '@/context/AgendaProvider';
import { AuthDialog } from '@/components/Auth/AuthDialog';
import { ProfileSheet } from '@/components/Auth/ProfileSheet';
import { AgendaView } from '@/components/Agenda/AgendaView';
import { UpcomingCard } from '@/components/Agenda/UpcomingCard';
import { ReminderToast } from '@/components/Agenda/ReminderToast';
import { AgendaProposalCard, type ProposalState } from '@/components/Chat/AgendaProposalCard';
import { EpidemiologicalDashboard } from '@/components/Surveillance/EpidemiologicalDashboard';
import { HealthUnitsInteractiveMap } from '@/components/UnitsMap/HealthUnitsInteractiveMap';

// =========================================================================
// Tipos e Interfaces da Plataforma SUS Digital
// =========================================================================
interface InteractiveOption {
  label: string;
  query?: string;
  action?: 'open_auth';
}

interface CitationItem {
  title: string;
  url?: string;
}

interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  source?: string;
  options?: InteractiveOption[];
  citations?: CitationItem[];
  proposal?: AgendaProposal;
  proposalState?: ProposalState;
}

interface ChatSessionItem {
  id: string;
  title: string;
  last_preview: string;
  updated_at: string;
}

interface HealthUnitItem {
  id: string;
  nome: string;
  ra: string;
  ra_display: string;
  tipo: string;
  tipo_display: string;
  cluster: string;
  endereco: string;
  horario: string;
  servicos: string[];
  referencia_emergencia?: string;
  telefone?: string;
  atendimento_24h?: boolean;
  bairro?: string;
  url?: string;
  lat?: number;
  lng?: number;
  svg_x: number;
  svg_y: number;
}

interface RADistribution {
  ra: string;
  ra_display: string;
  unit_count: number;
}

interface VaccineItem {
  id: string;
  nome: string;
  sigla?: string;
  faixa_etaria: string;
  faixa_etaria_display: string;
  idade_recomendada: string;
  doses: string;
  doencas_prevenidas: string;
  orientacoes: string;
  onde_tomar: string;
}


// Clinical Records
const RECORDS = [
  {
    title: '12 set 2026 · Consulta clínica',
    desc: 'UBS 1 Asa Norte. Pressão 12/8. Retorno em 30 dias.',
    file: 'Receita.pdf',
  },
  {
    title: '02 set 2026 · Exame de sangue',
    desc: 'Hemograma e glicemia dentro dos valores de referência.',
    file: 'Laudo.pdf',
  },
  {
    title: '20 ago 2026 · Vacina contra gripe',
    desc: 'Dose única aplicada. Lote de exemplo 0000.',
    file: 'Carteira.pdf',
  },
];

// Ordem das abas (índice ↔ hash)
const TAB_HASHES = ['inicio', 'assistente', 'agenda', 'servicos', 'monitoramento', 'historico'];
const TAB_AGENDA = 2;

export default function Page() {
  return (
    <AuthProvider>
      <GeoProvider>
        <AgendaProvider>
          <Home />
        </AgendaProvider>
      </GeoProvider>
    </AuthProvider>
  );
}

function Home() {
  // Navigation State
  const [viewMode, setViewMode] = useState<'landing' | 'app'>('landing');
  const [activeTab, setActiveTab] = useState<number>(0);

  // Conta opcional, agenda e localização (compartilhadas via contexto)
  const { citizen, status: authStatus, openAuth, setProfileOpen, logout } = useAuth();
  const agenda = useAgenda();
  const geo = useGeo();

  // Multi-Session Chat State
  const [sessions, setSessions] = useState<ChatSessionItem[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSessionsDrawerOpen, setIsSessionsDrawerOpen] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isBotTyping, setIsBotTyping] = useState(false);
  const msgsEndRef = useRef<HTMLDivElement>(null);

  // Services View State: Units Map & Vaccines Guide
  const [serviceSubTab, setServiceSubTab] = useState<'mapa' | 'vacinas'>('mapa');
  const [activeUnitTab, setActiveUnitTab] = useState<string>('todas');
  const [mapSearchQuery, setMapSearchQuery] = useState<string>('');
  const [units, setUnits] = useState<HealthUnitItem[]>([]);
  const [raList, setRaList] = useState<RADistribution[]>([]);
  const [selectedRA, setSelectedRA] = useState<string>('todas');
  const [selectedPin, setSelectedPin] = useState<HealthUnitItem | null>(null);

  // Vaccines Guide State
  const [vaccines, setVaccines] = useState<VaccineItem[]>([]);
  const [vaccineFilter, setVaccineFilter] = useState<string>('todas');
  const [recVaccines, setRecVaccines] = useState<VaccineItem[]>([]);
  const [recAlert, setRecAlert] = useState<string | null>(null);
  const [showOnlyRecs, setShowOnlyRecs] = useState(false);

  // Clinical History State
  const [openAccordion, setOpenAccordion] = useState<number | null>(0);
  const [downloadNotice, setDownloadNotice] = useState<string | null>(null);

  // -------------------------------------------------------------------------
  // Carregamento Inicial do Cidadão e RAs
  // -------------------------------------------------------------------------
  useEffect(() => {
    // 1. Carregar lista de RAs oficiais do DF
    fetchRasList();

    // 2. Carregar guia oficial de vacinas
    fetchVaccineGuide('todas');
  }, []);

  // Sessões de chat: recarrega ao entrar/sair da conta (visitante usa sessão anônima)
  useEffect(() => {
    if (authStatus === 'loading') return;
    fetchChatSessions(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authStatus]);

  const fetchRasList = async () => {
    try {
      const res = await fetch(buildApiUrl('/api/units/ras'));
      if (res.ok) {
        const data: RADistribution[] = await res.json();
        setRaList(data);
      }
    } catch (err) {
      console.warn('Erro ao carregar RAs do backend:', err);
    }
  };

  // -------------------------------------------------------------------------
  // Multi-Sessões de Chat
  // -------------------------------------------------------------------------
  const fetchChatSessions = async (selectFirst = false) => {
    try {
      const res = await fetch(buildApiUrl('/api/chat/sessions'), { headers: authHeaders() });
      if (res.ok) {
        const list: ChatSessionItem[] = await res.json();
        setSessions(list);
        if (list.length > 0 && (selectFirst || !currentSessionId)) {
          loadSessionMessages(list[0].id);
        } else if (list.length === 0 && (selectFirst || !currentSessionId)) {
          createNewSession();
        }
      }
    } catch (err) {
      console.warn('Erro ao carregar sessões de chat:', err);
    }
  };

  const createNewSession = async () => {
    // Cancela stream ativo se houver
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    try {
      const res = await fetch(buildApiUrl('/api/chat/sessions'), {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ title: 'Nova conversa' }),
      });

      if (res.ok) {
        const s: ChatSessionItem = await res.json();
        setSessions((prev) => [s, ...prev]);
        setCurrentSessionId(s.id);
        setIsSessionsDrawerOpen(false);

        // Mensagem de boas-vindas personalizada
        const welcomeText = `Olá, ${
          citizen ? citizen.primeiro_nome : 'Cidadão'
        }! Sou a SUSANNA, assistente virtual oficial da Secretaria de Saúde do DF. Como posso ajudar com vacinas, unidades de saúde ou agendamentos na sua região?`;

        setMessages([
          {
            id: 'init_' + Date.now(),
            text: welcomeText,
            isUser: false,
            source: 'Secretaria de Saúde do Distrito Federal (SES-DF)',
          },
        ]);
      }
    } catch {
      // Fallback local
      const tempId = 'sess_' + Date.now();
      setCurrentSessionId(tempId);
      setMessages([
        {
          id: 'm0',
          text: `Olá, ${
            citizen ? citizen.primeiro_nome : 'Cidadão'
          }! Sou a SUSANNA. Como posso orientar você hoje?`,
          isUser: false,
        },
      ]);
    }
  };

  const loadSessionMessages = async (sessionId: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setCurrentSessionId(sessionId);
    setIsSessionsDrawerOpen(false);

    try {
      const res = await fetch(buildApiUrl(`/api/chat/sessions/${sessionId}/messages`), { headers: authHeaders() });
      if (res.ok) {
        const msgs = await res.json();
        if (msgs.length === 0) {
          const welcomeText = `Olá, ${
            citizen ? citizen.primeiro_nome : 'Cidadão'
          }! Sou a SUSANNA. Como posso ajudar nesta conversa?`;
          setMessages([
            {
              id: 'init_' + Date.now(),
              text: welcomeText,
              isUser: false,
            },
          ]);
        } else {
          setMessages(
            msgs.map((m: any) => ({
              id: m.id,
              text: m.content,
              isUser: m.role === 'user',
              source: m.source,
              options: m.options,
              citations: m.citations,
            }))
          );
        }
      }
    } catch (err) {
      console.warn('Erro ao carregar mensagens da sessão:', err);
    }
  };

  const deleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await fetch(buildApiUrl(`/api/chat/sessions/${sessionId}`), { method: 'DELETE', headers: authHeaders() });
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        const remaining = sessions.filter((s) => s.id !== sessionId);
        if (remaining.length > 0) {
          loadSessionMessages(remaining[0].id);
        } else {
          createNewSession();
        }
      }
    } catch (err) {
      console.warn('Erro ao excluir sessão:', err);
    }
  };

  // -------------------------------------------------------------------------
  // Carregamento de Unidades de Saúde Reais
  // -------------------------------------------------------------------------
  useEffect(() => {
    let isCancelled = false;

    const fetchUnits = async () => {
      try {
        let tipoParam = '';
        const tabLower = activeUnitTab.toLowerCase();
        if (tabLower === 'ubs') tipoParam = 'ubs';
        else if (tabLower === 'hospitais' || tabLower === 'hospital') tipoParam = 'hospital';
        else if (tabLower === 'upa') tipoParam = 'upa';
        else if (tabLower === 'caps') tipoParam = 'caps';
        else if (tabLower === 'policlinica' || tabLower === 'policlinicas') tipoParam = 'policlinica';
        else if (tabLower === 'farmacia' || tabLower === 'farmacias') tipoParam = 'farmacia';
        else if (tabLower === 'laboratorio' || tabLower === 'laboratorios') tipoParam = 'laboratorio';
        else if (tabLower !== 'todas') tipoParam = tabLower;

        const url = createApiUrl('/api/units');
        if (selectedRA && selectedRA !== 'todas') {
          url.searchParams.set('ra', selectedRA);
        }
        if (tipoParam) {
          url.searchParams.set('tipo', tipoParam);
        }
        if (mapSearchQuery.trim()) {
          url.searchParams.set('q', mapSearchQuery.trim());
        }

        const res = await fetch(url.toString());
        if (res.ok && !isCancelled) {
          const data = await res.json();
          setUnits(data.units || []);
        }
      } catch (err) {
        if (!isCancelled) {
          console.warn('Erro ao carregar unidades de saúde:', err);
        }
      }
    };

    const timer = setTimeout(() => {
      fetchUnits();
    }, 250);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [activeUnitTab, selectedRA, mapSearchQuery]);

  // -------------------------------------------------------------------------
  // Carregamento do Guia Oficial de Vacinação e Recomendações
  // -------------------------------------------------------------------------
  const fetchVaccineGuide = async (faixa: string) => {
    try {
      const url = createApiUrl('/api/vaccines/guide');
      if (faixa && faixa !== 'todas') {
        url.searchParams.set('faixa_etaria', faixa);
      }
      const res = await fetch(url.toString());
      if (res.ok) {
        const data = await res.json();
        setVaccines(data.vacinas || []);
      }
    } catch (err) {
      console.warn('Erro ao carregar guia vacinal:', err);
    }
  };

  useEffect(() => {
    fetchVaccineGuide(vaccineFilter);
  }, [vaccineFilter]);

  // Atualiza recomendações personalizadas sempre que o cidadão mudar
  useEffect(() => {
    if (!citizen?.data_nascimento) return;
    const fetchRecs = async () => {
      try {
        const url = createApiUrl('/api/vaccines/recommendations');
        url.searchParams.set('data_nascimento', citizen.data_nascimento!);
        url.searchParams.set('gestante', String(citizen.gestante));
        if (citizen.condicoes?.length) url.searchParams.set('condicoes', citizen.condicoes.join(','));

        const res = await fetch(url.toString());
        if (res.ok) {
          const data = await res.json();
          setRecVaccines(data.vacinas_recomendadas || []);
          setRecAlert(data.proxima_dose_alerta || null);
        }
      } catch (err) {
        console.warn('Erro ao buscar recomendações personalizadas:', err);
      }
    };
    fetchRecs();
  }, [citizen]);

  // Recomendações só valem para quem está conectado
  const myRecVaccines = citizen ? recVaccines : [];
  const myRecAlert = citizen ? recAlert : null;

  // -------------------------------------------------------------------------
  // Sync com Hash Routing
  // -------------------------------------------------------------------------
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      if (!hash || hash === 'landing') {
        setViewMode('landing');
      } else {
        setViewMode('app');
        const idx = TAB_HASHES.indexOf(hash);
        if (idx >= 0) {
          setActiveTab(idx);
        }
      }
    };

    handleHash();
    window.addEventListener('hashchange', handleHash);
    return () => window.removeEventListener('hashchange', handleHash);
  }, []);

  // IntersectionObserver para animar #L .rv
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('on');
          }
        });
      },
      { threshold: 0.15 }
    );

    document.querySelectorAll('#L .rv').forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, [viewMode]);

  const navigateToTab = (index: number) => {
    setActiveTab(index);
    window.location.hash = `#/${TAB_HASHES[index]}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const enterApp = (tabIndex: number = 0) => {
    setViewMode('app');
    navigateToTab(tabIndex);
  };

  const exitApp = () => {
    setViewMode('landing');
    window.location.hash = '#/landing';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Chat auto-scroll
  useEffect(() => {
    if (activeTab === 1) {
      msgsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isBotTyping, activeTab]);

  // -------------------------------------------------------------------------
  // Envio de Mensagem com Streaming e Persistência Multi-Sessão
  // -------------------------------------------------------------------------
  const handleSendMessage = async (textToSend?: string) => {
    const q = (textToSend || inputQuery).trim();
    if (!q || isBotTyping) return;

    // Cancela stream anterior se existente
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const userMsgId = 'u_' + Date.now();
    const botMsgId = 'b_' + Date.now();

    setMessages((prev) => [...prev, { id: userMsgId, text: q, isUser: true }]);
    setInputQuery('');
    setIsBotTyping(true);

    // Salva mensagem do usuário na sessão ativa
    if (currentSessionId) {
      fetch(buildApiUrl('/api/chat/sessions/messages'), {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          session_id: currentSessionId,
          role: 'user',
          content: q,
        }),
      }).catch(() => {});
    }

    // Se a última proposta de agenda ainda espera data/horário, a resposta completa a mesma proposta
    const lastBot = [...messages].reverse().find((m) => !m.isUser);
    const pendingProposalId =
      lastBot?.proposal && lastBot.proposalState === 'open' && lastBot.proposal.faltando.length > 0
        ? lastBot.proposal.proposal_id
        : null;

    try {
      const res = await fetch(buildApiUrl('/api/chat/stream'), {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        signal: abortController.signal,
        body: JSON.stringify({
          message: q,
          question: q,
          history: messages.slice(-4).map((m) => ({
            text: m.text,
            isUser: m.isUser,
            role: m.isUser ? 'user' : 'assistant',
            content: m.text,
          })),
          pending_proposal_id: pendingProposalId,
        }),
      });

      if (!res.ok) throw new Error('Falha no streaming do servidor');

      const reader = res.body?.getReader();
      if (!reader) throw new Error('Não foi possível ler o stream');

      const decoder = new TextDecoder();
      let accumulatedText = '';
      let botSources = '';
      let botOptions: InteractiveOption[] = [];
      let botCitations: CitationItem[] = [];
      let botProposal: AgendaProposal | undefined;

      setMessages((prev) => [
        ...prev.map((m) =>
          pendingProposalId && m.proposal?.proposal_id === pendingProposalId ? { ...m, proposalState: 'dismissed' as ProposalState } : m
        ),
        { id: botMsgId, text: '', isUser: false, source: 'Consultando base SES-DF…' },
      ]);
      // O streaming chega em pacotes que podem cortar uma linha JSON ao meio (comum pela internet).
      // A parte final incompleta fica no buffer até o resto chegar.
      let lineBuffer = '';

      const processLine = (line: string) => {
        const trimmed = line.trim();
        if (!trimmed) return;
        let jsonStr = trimmed;
        if (trimmed.startsWith('data: ')) {
          jsonStr = trimmed.slice(6).trim();
        }
        if (jsonStr === '[DONE]') return;
        try {
          const data = JSON.parse(jsonStr);
          if (data.type === 'agenda_proposal' && data.proposal) {
            botProposal = data.proposal as AgendaProposal;
            return;
          }
          if (data.token) {
            accumulatedText += data.token;
          } else if (data.content) {
            accumulatedText += data.content;
          }
          if (data.sources && Array.isArray(data.sources)) {
            botSources = 'Fonte: ' + data.sources.join(', ');
          } else if (data.source) {
            botSources = 'Fonte: ' + data.source;
          }
          if (data.options && Array.isArray(data.options)) {
            botOptions = data.options;
          }
          if (data.citations && Array.isArray(data.citations)) {
            botCitations = data.citations;
          }
        } catch {
          // Linha completa que não é JSON: texto puro. Fragmentos de JSON nunca entram no texto.
          if (!trimmed.startsWith('{') && !trimmed.endsWith('}')) {
            accumulatedText += jsonStr;
          }
        }
      };

      const renderBotMessage = () =>
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMsgId
              ? {
                  ...msg,
                  text: accumulatedText || 'Processando resposta…',
                  source: botSources || 'Fonte: Ministério da Saúde / SES-DF',
                  options: botOptions.length > 0 ? botOptions : msg.options,
                  citations: botCitations.length > 0 ? botCitations : msg.citations,
                  proposal: botProposal ?? msg.proposal,
                  proposalState: botProposal ? msg.proposalState ?? 'open' : msg.proposalState,
                }
              : msg
          )
        );

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        lineBuffer += decoder.decode(value, { stream: true });
        const lines = lineBuffer.split('\n');
        lineBuffer = lines.pop() ?? '';
        for (const line of lines) processLine(line);

        renderBotMessage();
      }

      // Último trecho, caso o stream termine sem quebra de linha
      lineBuffer += decoder.decode();
      if (lineBuffer.trim()) {
        processLine(lineBuffer);
        renderBotMessage();
      }

      // Salva mensagem do bot na sessão ativa
      if (currentSessionId && accumulatedText) {
        fetch(buildApiUrl('/api/chat/sessions/messages'), {
          method: 'POST',
          headers: authHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({
            session_id: currentSessionId,
            role: 'assistant',
            content: accumulatedText,
            source: botSources || 'SES-DF',
            citations: botCitations,
            options: botOptions,
          }),
        }).then(() => fetchChatSessions());
      }
    } catch (err: any) {
      if (err.name === 'AbortError') return;

      // Fallback inteligente
      setTimeout(() => {
        setIsBotTyping(false);
        const lower = q.toLowerCase();
        let reply =
          'Ainda não achei isso nos meus dados. Pergunte sobre vacinas do PNI, consultas, exames, medicamentos ou dengue no DF.';
        let src = 'Fonte: base de dados SES-DF (demonstração)';

        if (/vacina|gripe/i.test(lower)) {
          reply =
            'A vacina contra a gripe está disponível em todas as salas de vacinação das UBSs do DF. Apresente seu documento oficial com foto e o Cartão SUS.';
          src = 'Fonte: Diretoria de Imunização SES-DF';
        } else if (/agend|consulta|cl[ií]nico/i.test(lower)) {
          reply =
            'Acesse a aba Serviços para consultar a UBS mais próxima da sua Região Administrativa e agendar o acolhimento.';
          src = 'Fonte: Atenção Primária à Saúde SES-DF';
        } else if (/dengue/i.test(lower)) {
          reply =
            'Elimine água parada em recipientes. Se apresentar febre alta e dores no corpo ou atrás dos olhos, procure a UBS ou UPA mais próxima para hidratação precoce.';
          src = 'Fonte: Vigilância Ambiental SES-DF';
        } else if (/exame|resultado/i.test(lower)) {
          reply =
            'Seus laudos e exames laboratoriais ficam salvos na aba Histórico Clínico do seu prontuário digital.';
          src = 'Fonte: Laboratório Central do DF (LACEN)';
        }

        setMessages((prev) => [
          ...prev,
          { id: botMsgId, text: reply, isUser: false, source: src },
        ]);

        if (currentSessionId) {
          fetch(buildApiUrl('/api/chat/sessions/messages'), {
            method: 'POST',
            headers: authHeaders({ 'Content-Type': 'application/json' }),
            body: JSON.stringify({
              session_id: currentSessionId,
              role: 'assistant',
              content: reply,
              source: src,
            }),
          }).then(() => fetchChatSessions());
        }
      }, 800);
    } finally {
      setIsBotTyping(false);
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsBotTyping(false);
    }
  };

  // Navegação direta do Dashboard Epidemiológico para o Chat com a SUSANNA
  const handleAskSuzannaFromDashboard = (promptText: string) => {
    navigateToTab(1);
    setInputQuery(promptText);
    setTimeout(() => {
      const inputEl = document.getElementById('in') as HTMLInputElement | null;
      if (inputEl) inputEl.focus();
    }, 150);
  };

  return (
    <>
      {/* =========================================================================
          LANDING PAGE (#L)
      ========================================================================= */}
      <div id="L" style={{ display: viewMode === 'landing' ? 'block' : 'none' }}>
        {/* Floating Glass Navigation */}
        <nav className="glass">
          <b>
            SUS <span>Digital</span>
          </b>
          <a
            className="btn"
            href="#/assistente"
            onClick={(e) => {
              e.preventDefault();
              enterApp(1);
            }}
          >
            Falar com a SUSANNA
          </a>
        </nav>

        {/* Hero Section */}
        <section className="hero">
          <div className="rv">
            <div className="eyebrow">Saúde pública · Distrito Federal</div>
            <h1>
              Saúde pública, <em>clara</em> como água.
            </h1>
            <p>
              Agende consultas, acompanhe exames e tire dúvidas com a SUSANNA, assistente de IA que consulta dados atualizados da rede pública de todas as 33 Regiões Administrativas do DF.
            </p>
            <a
              className="btn"
              href="#/inicio"
              onClick={(e) => {
                e.preventDefault();
                enterApp(0);
              }}
            >
              Acessar Plataforma
            </a>
          </div>

          {/* Mascot Stage */}
          <div className="stage rv">
            <img
              src="/images/suzanna-hero.webp"
              alt="SUSANNA, a assistente virtual do SUS Digital, acenando"
            />
            <div className="tag glass t1">
              Vacinação em andamento
              <small>{citizen ? citizen.ra_display : 'Distrito Federal'}</small>
            </div>
            <div className="tag glass t2">
              Próxima consulta
              <small>Clínico geral · UBS 14h</small>
            </div>
          </div>
        </section>

        {/* 3 Pillars / Feature Cards */}
        <section className="feat">
          <div className="f glass rv">
            <i>01</i>
            <h3>Atendimento por IA</h3>
            <p>Respostas fundamentadas em 383 unidades e diretrizes clínicas oficiais do SUS.</p>
          </div>
          <div className="f glass rv">
            <i>02</i>
            <h3>Histórico e Vacinas</h3>
            <p>Guia Oficial do PNI por ciclo de vida, consultas e exames unificados.</p>
          </div>
          <div className="f glass rv">
            <i>03</i>
            <h3>33 Regiões do DF</h3>
            <p>Mapa interativo das UBSs, UPAs 24h e Hospitais Regionais de Brasília.</p>
          </div>
        </section>

        {/* Chat CTA Banner */}
        <section id="chat">
          <div className="wrap rv" style={{ textAlign: 'center' }}>
            <h2>
              Pronto para <b>começar</b>?
            </h2>
            <p className="sub">Identifique-se ou faça perguntas sobre a saúde pública do DF.</p>
            <a
              className="btn"
              href="#/inicio"
              onClick={(e) => {
                e.preventDefault();
                enterApp(0);
              }}
            >
              Acessar Plataforma
            </a>
          </div>
        </section>

        {/* Footer */}
        <footer>SUS Digital · Secretaria de Saúde do Distrito Federal</footer>
      </div>

      {/* =========================================================================
          PLATAFORMA (#A)
      ========================================================================= */}
      <div id="A" style={{ display: viewMode === 'app' ? 'block' : 'none' }}>
        <div className="app">
          {/* Sidebar Navigation */}
          <aside className="g" id="nav">
            <div className="lg" style={{ cursor: 'pointer' }} onClick={() => enterApp(0)}>
              <img
                src="/images/suzanna-avatar.webp"
                alt="SUS Digital"
              />
              SUS Digital
            </div>

            {/* Cartão do cidadão: visitante ou conta opcional */}
            <button
              type="button"
              className="who"
              onClick={() => (citizen ? setProfileOpen(true) : openAuth('login'))}
              aria-label={citizen ? 'Abrir meu perfil' : 'Entrar ou criar conta'}
            >
              <span className={`av${citizen ? '' : ' anon'}`} aria-hidden>
                {citizen ? citizen.primeiro_nome.charAt(0) : '?'}
              </span>
              <span style={{ minWidth: 0 }}>
                <b>{citizen ? citizen.primeiro_nome : 'Visitante'}</b>
                <small>{citizen ? citizen.ra_display : 'Entrar ou criar conta'}</small>
                {citizen && !citizen.perfil_completo && <span className="chip">Perfil incompleto</span>}
              </span>
            </button>

            {[
              'Início',
              'Assistente',
              'Agenda',
              'Serviços e Vacinas',
              'Monitoramento',
              'Histórico',
            ].map((label, i) => (
              <button
                key={label}
                className={activeTab === i ? 'on' : ''}
                onClick={() => navigateToTab(i)}
                aria-current={activeTab === i ? 'page' : undefined}
              >
                {label}
                {i === TAB_AGENDA && agenda.pendencias > 0 && (
                  <span className="badge" aria-label={`${agenda.pendencias} pendências`}>
                    {agenda.pendencias}
                  </span>
                )}
              </button>
            ))}

            {/* No celular a barra vira pílula: acesso compacto ao perfil */}
            <button
              type="button"
              className="who-m"
              onClick={() => (citizen ? setProfileOpen(true) : openAuth('login'))}
              aria-label={citizen ? 'Abrir meu perfil' : 'Entrar ou criar conta'}
            >
              {citizen ? citizen.primeiro_nome : 'Entrar'}
            </button>

            {citizen && (
              <button type="button" style={{ marginTop: 'auto' }} onClick={() => logout()}>
                Sair da conta
              </button>
            )}
            <button
              id="out"
              style={{ marginTop: citizen ? undefined : 'auto' }}
              onClick={exitApp}
            >
              ← Voltar ao início
            </button>
          </aside>

          {/* Main Content Area */}
          <main>
            {/* ----------------- SECTION 0: INÍCIO ----------------- */}
            <section className={activeTab === 0 ? 'on' : ''}>
              <h1>
                Olá, <b>{citizen ? citizen.primeiro_nome : 'Cidadão'}</b>
              </h1>
              <p className="sub">
                {citizen
                  ? `${citizen.ra_display}${citizen.idade_anos != null ? ` · ${citizen.idade_anos} anos` : ''}. Seu resumo de saúde pública no DF.`
                  : 'Seu resumo de saúde e serviços da rede pública do Distrito Federal. Use sem cadastro ou crie uma conta opcional.'}
              </p>

              {/* Banner de Recomendação em Destaque */}
              {myRecAlert && (
                <div
                  className="pill"
                  style={{
                    marginBottom: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    background: 'rgba(37,99,235,0.1)',
                    border: '1px solid rgba(37,99,235,0.25)',
                    color: '#1e3a8a',
                    fontWeight: 500,
                  }}
                >
                  <span>📢</span>
                  <span>{myRecAlert}</span>
                </div>
              )}

              <div className="grid">
                <div
                  className="c g hv q"
                  onClick={() => {
                    setServiceSubTab('mapa');
                    navigateToTab(3);
                  }}
                >
                  <b>Agendar na sua UBS</b>
                  <span>{citizen ? `Unidades em ${citizen.ra_display}` : 'Rede de Atenção Primária'}</span>
                </div>
                <div
                  className="c g hv q"
                  onClick={() => {
                    setServiceSubTab('vacinas');
                    navigateToTab(3);
                  }}
                >
                  <b>Guia de Vacinação PNI</b>
                  <span>{myRecVaccines.length > 0 ? `${myRecVaccines.length} doses indicadas para seu perfil` : 'Calendário por idade'}</span>
                </div>
                <div
                  className="c g hv q"
                  onClick={() => {
                    navigateToTab(1);
                    handleSendMessage('Quais são as vacinas e serviços recomendados para a minha idade?');
                  }}
                >
                  <b>Falar com a SUSANNA</b>
                  <span>Tire dúvidas com IA</span>
                </div>
              </div>

              <div className="grid" style={{ marginTop: '24px' }}>
                <UpcomingCard onOpenAgenda={() => navigateToTab(TAB_AGENDA)} />
              </div>
            </section>

            {/* ----------------- SECTION 1: ASSISTENTE (MULTI-SESSÃO) ----------------- */}
            <section className={activeTab === 1 ? 'on' : ''}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <h1 style={{ margin: 0 }}>
                    Fale com a <b>SUSANNA</b>
                  </h1>
                  <p className="sub" style={{ margin: '4px 0 0' }}>
                    Respostas em streaming fundamentadas em 383 unidades e diretrizes clínicas oficiais do SUS-DF.
                  </p>
                </div>

                {/* Barra de Ações Multi-Sessão */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    type="button"
                    className="btn"
                    onClick={createNewSession}
                    style={{
                      fontSize: '12px',
                      padding: '8px 14px',
                      background: '#2563eb',
                      color: '#ffffff',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <span>+</span> Nova Conversa
                  </button>

                  <button
                    type="button"
                    className="btn"
                    onClick={() => setIsSessionsDrawerOpen(!isSessionsDrawerOpen)}
                    style={{
                      fontSize: '12px',
                      padding: '8px 14px',
                      background: isSessionsDrawerOpen ? '#1e40af' : 'rgba(255,255,255,0.7)',
                      color: isSessionsDrawerOpen ? '#ffffff' : '#1e40af',
                      border: '1px solid var(--b2)',
                    }}
                  >
                    💬 Conversas ({sessions.length})
                  </button>
                </div>
              </div>

              {/* Drawer de Conversas Passadas (Janelas Separadas) */}
              {isSessionsDrawerOpen && (
                <div
                  className="g"
                  style={{
                    marginTop: '12px',
                    marginBottom: '16px',
                    padding: '12px',
                    borderRadius: '16px',
                    background: 'rgba(255, 255, 255, 0.75)',
                    border: '1px solid var(--b2)',
                    maxHeight: '220px',
                    overflowY: 'auto',
                  }}
                >
                  <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', marginBottom: '8px' }}>
                    Histórico de Conversas Salvas
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {sessions.map((s) => {
                      const isCurrent = s.id === currentSessionId;
                      return (
                        <div
                          key={s.id}
                          onClick={() => loadSessionMessages(s.id)}
                          style={{
                            padding: '8px 12px',
                            borderRadius: '10px',
                            background: isCurrent ? 'rgba(37,99,235,0.12)' : 'rgba(255,255,255,0.5)',
                            border: isCurrent ? '1px solid #2563eb' : '1px solid var(--b1)',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            transition: 'all 0.15s ease',
                          }}
                        >
                          <div style={{ minWidth: 0, flex: 1 }}>
                            <div style={{ fontWeight: 600, fontSize: '12px', color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {s.title}
                            </div>
                            {s.last_preview && (
                              <div style={{ fontSize: '11px', color: '#64748b', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {s.last_preview}
                              </div>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={(e) => deleteSession(s.id, e)}
                            title="Excluir conversa"
                            style={{
                              marginLeft: '8px',
                              background: 'transparent',
                              border: 'none',
                              cursor: 'pointer',
                              color: '#94a3b8',
                              fontSize: '14px',
                            }}
                            onMouseEnter={(e) => (e.currentTarget.style.color = '#ef4444')}
                            onMouseLeave={(e) => (e.currentTarget.style.color = '#94a3b8')}
                          >
                            🗑️
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Chat Container */}
              <div className="chat g" style={{ marginTop: '12px' }}>
                <div id="msgs">
                  {messages.map((m) => (
                    <div key={m.id} className={`m ${m.isUser ? 'me' : 'bot'}`}>
                      {!m.isUser && (
                        <img
                          src="/images/suzanna-avatar.webp"
                          alt="SUSANNA"
                        />
                      )}
                      <div className="b">
                        <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                          {m.text.replace(/\*\*(.+?)\*\*/g, '$1')}
                        </div>

                        {/* Proposta de lembrete: só vira evento após confirmação */}
                        {m.proposal && !(m.proposalState === 'dismissed' && m.proposal.faltando.length > 0) && (
                          <AgendaProposalCard
                            proposal={m.proposal}
                            state={m.proposalState || 'open'}
                            onStateChange={(st) =>
                              setMessages((prev) => prev.map((x) => (x.id === m.id ? { ...x, proposalState: st } : x)))
                            }
                            onOpenAgenda={() => navigateToTab(TAB_AGENDA)}
                          />
                        )}

                        {/* Chips de Opções Interativas (Possíveis dúvidas) */}
                        {m.options && m.options.length > 0 && (
                          <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid rgba(0,0,0,0.06)', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {m.options.map((opt, oi) => (
                              <button
                                key={oi}
                                type="button"
                                onClick={() => (opt.action === 'open_auth' ? openAuth('login') : opt.query && handleSendMessage(opt.query))}
                                style={{
                                  cursor: 'pointer',
                                  fontSize: '13px',
                                  fontWeight: 500,
                                  padding: '8px 16px',
                                  borderRadius: '99px',
                                  background: '#ffffff',
                                  color: '#1e40af',
                                  border: '1px solid #bfdbfe',
                                  boxShadow: '0 2px 6px rgba(37,99,235,0.08)',
                                  transition: 'all 0.2s ease',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = '#2563eb';
                                  e.currentTarget.style.color = '#ffffff';
                                  e.currentTarget.style.borderColor = '#2563eb';
                                  e.currentTarget.style.transform = 'translateY(-1px)';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = '#ffffff';
                                  e.currentTarget.style.color = '#1e40af';
                                  e.currentTarget.style.borderColor = '#bfdbfe';
                                  e.currentTarget.style.transform = 'none';
                                }}
                              >
                                {opt.label}
                              </button>
                            ))}
                          </div>
                        )}

                        {/* Dropdown de Referências e Fontes Oficiais */}
                        {((m.citations && m.citations.length > 0) || m.source) && (
                          <details
                            style={{
                              marginTop: '10px',
                              padding: '6px 12px',
                              borderRadius: '8px',
                              background: '#f8fafc',
                              border: '1px solid #e2e8f0',
                              fontSize: '12px',
                              color: '#334155',
                            }}
                          >
                            <summary
                              style={{
                                cursor: 'pointer',
                                fontWeight: 600,
                                color: '#2563eb',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '6px',
                                userSelect: 'none',
                              }}
                            >
                              <span>Referências</span>
                              {m.citations && m.citations.length > 0 && (
                                <span
                                  style={{
                                    fontSize: '11px',
                                    background: '#dbeafe',
                                    color: '#1d4ed8',
                                    padding: '1px 7px',
                                    borderRadius: '99px',
                                    fontWeight: 700,
                                  }}
                                >
                                  {m.citations.length}
                                </span>
                              )}
                            </summary>

                            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px', paddingTop: '8px', borderTop: '1px dashed #cbd5e1' }}>
                              {m.citations && m.citations.length > 0 ? (
                                m.citations.map((c, ci) => {
                                  const effectiveUrl =
                                    c.url ||
                                    (/vacina/i.test(c.title)
                                      ? 'https://www.gov.br/saude/pt-br/vacinacao/calendario'
                                      : /farmacia|medicamento/i.test(c.title)
                                      ? 'https://www.saude.df.gov.br/componente-especializado'
                                      : /ubs|unidade|hospital/i.test(c.title)
                                      ? 'https://www.saude.df.gov.br/unidades-de-saude'
                                      : /samu|emergencia/i.test(c.title)
                                      ? 'https://www.saude.df.gov.br/samu-192'
                                      : 'https://www.saude.df.gov.br');
                                  return (
                                    <a
                                      key={ci}
                                      href={effectiveUrl}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      style={{
                                        fontSize: '12px',
                                        color: '#1d4ed8',
                                        textDecoration: 'none',
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '6px',
                                        padding: '5px 9px',
                                        borderRadius: '6px',
                                        background: '#ffffff',
                                        border: '1px solid #e2e8f0',
                                        width: 'fit-content',
                                        maxWidth: '100%',
                                      }}
                                      onMouseEnter={(e) => {
                                        e.currentTarget.style.textDecoration = 'underline';
                                        e.currentTarget.style.background = '#f1f5f9';
                                      }}
                                      onMouseLeave={(e) => {
                                        e.currentTarget.style.textDecoration = 'none';
                                        e.currentTarget.style.background = '#ffffff';
                                      }}
                                    >
                                      <span>{c.title}</span>
                                      <span style={{ fontSize: '10px', color: '#64748b' }}>↗</span>
                                    </a>
                                  );
                                })
                              ) : (
                                <span style={{ fontSize: '12px', color: '#64748b' }}>
                                  {m.source}
                                </span>
                              )}
                            </div>
                          </details>
                        )}
                      </div>
                    </div>
                  ))}
                  {isBotTyping && (
                    <div className="m bot">
                      <img src="/images/suzanna-avatar.webp" alt="SUSANNA" />
                      <div className="b" style={{ fontStyle: 'italic', color: '#64748b' }}>
                        SUSANNA está pesquisando dados da SES-DF…
                      </div>
                    </div>
                  )}
                  <div ref={msgsEndRef} />
                </div>

                {/* Suggestion Chips */}
                <div className="chips" id="chips">
                  {[
                    `Onde tomar vacina em ${citizen ? citizen.ra_display : 'Ceilândia'}?`,
                    'Quais vacinas um idoso de 65 anos deve tomar?',
                    'Sou gestante, quando tomo a vacina dTpa?',
                    'Qual a UPA 24 horas mais próxima?',
                    'Como funciona o acolhimento na UBS?',
                  ].map((chip, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(chip)}
                    >
                      {chip}
                    </button>
                  ))}
                </div>

                {/* Input form */}
                <div className="in">
                  <input
                    id="q"
                    placeholder="Digite sua dúvida de saúde sobre o DF…"
                    aria-label="Pergunta"
                    value={inputQuery}
                    onChange={(e) => setInputQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                  />
                  <button
                    className="btn"
                    id="go"
                    onClick={() => {
                      if (isBotTyping) {
                        handleStopGeneration();
                      } else {
                        handleSendMessage();
                      }
                    }}
                    style={{
                      background: isBotTyping ? '#ef4444' : undefined,
                      color: isBotTyping ? '#ffffff' : undefined,
                      borderColor: isBotTyping ? '#dc2626' : undefined,
                    }}
                  >
                    {isBotTyping ? '⏹ Parar' : 'Enviar'}
                  </button>
                </div>
              </div>
            </section>

            {/* ----------------- SECTION 2: AGENDA PERSONALIZADA ----------------- */}
            <section className={activeTab === TAB_AGENDA ? 'on' : ''}>
              <h1>
                Minha <b>agenda</b>
              </h1>
              <p className="sub">
                {citizen
                  ? 'Vacinas pendentes para o seu perfil e lembretes de consultas, exames e medicamentos.'
                  : 'Lembretes e vacinas personalizados para quem cria uma conta opcional.'}
              </p>
              <AgendaView onAskSusanna={handleAskSuzannaFromDashboard} />
            </section>

            {/* ----------------- SECTION 3: SERVIÇOS & VACINAS ----------------- */}
            <section className={activeTab === 3 ? 'on' : ''}>
              <h1>
                Serviços, <b>Unidades e Vacinação</b>
              </h1>
              <p className="sub">
                Explore as {units.length > 0 ? units.length : 383} unidades de saúde nas 33 RAs do Distrito Federal e consulte o Guia Oficial do PNI.
              </p>

              {/* Sub-Tabs: Mapa vs. Guia Vacinal */}
              <div className="tabs g" style={{ marginBottom: '16px' }}>
                <button
                  className={serviceSubTab === 'mapa' ? 'on' : ''}
                  onClick={() => setServiceSubTab('mapa')}
                >
                  🗺️ Mapa de Unidades do DF ({units.length})
                </button>
                <button
                  className={serviceSubTab === 'vacinas' ? 'on' : ''}
                  onClick={() => setServiceSubTab('vacinas')}
                >
                  💉 Guia de Vacinação por Idade (PNI)
                </button>
              </div>

              {/* ---------------- SUBVIEW 1: MAPA DE UNIDADES ---------------- */}
              {serviceSubTab === 'mapa' && (
                <>
                  {geo.status !== 'granted' && geo.status !== 'unavailable' && (
                    <div className="ag-banner" role="note">
                      <Navigation size={18} aria-hidden />
                      <span style={{ flex: 1 }}>
                        {geo.status === 'denied'
                          ? 'Localização bloqueada no navegador. Libere nas configurações do site para ver as unidades mais próximas.'
                          : 'Veja as unidades mais próximas de você. A localização fica só neste aparelho.'}
                      </span>
                      {geo.status !== 'denied' && (
                        <button type="button" className="sx-btn sm" onClick={() => geo.request()}>
                          Usar minha localização
                        </button>
                      )}
                    </div>
                  )}
                  {/* Novo Mapa Interativo Estilizado com Busca em Tempo Real e Card Flutuante */}
                  <HealthUnitsInteractiveMap
                    userCoords={geo.coords}
                    units={units}
                    raList={raList}
                    selectedRA={selectedRA}
                    onSelectRA={setSelectedRA}
                    activeType={activeUnitTab}
                    onSelectType={setActiveUnitTab}
                    searchQuery={mapSearchQuery}
                    onSearchChange={setMapSearchQuery}
                    selectedUnit={selectedPin}
                    onSelectUnit={setSelectedPin}
                    onAskSuzanna={(unit) => {
                      if (isBotTyping) {
                        handleStopGeneration();
                      }
                      navigateToTab(1);
                      setTimeout(() => {
                        handleSendMessage(`Quais serviços e vacinas estão disponíveis na ${unit.nome} em ${unit.ra_display}?`);
                      }, 50);
                    }}
                  />

                </>
              )}

              {/* ---------------- SUBVIEW 2: GUIA DE VACINAÇÃO PNI ---------------- */}
              {serviceSubTab === 'vacinas' && (
                <>
                  {/* Banner de Recomendação Personalizada do Cidadão */}
                  {citizen?.data_nascimento && (
                    <div
                      className="c g"
                      style={{
                        marginBottom: '16px',
                        background: 'linear-gradient(135deg, rgba(37,99,235,0.1) 0%, rgba(255,255,255,0.7) 100%)',
                        border: '1px solid rgba(37,99,235,0.3)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                        <div>
                          <div style={{ fontSize: '11px', fontWeight: 600, color: '#2563eb', textTransform: 'uppercase' }}>
                            Recomendação para {citizen.primeiro_nome}{citizen.idade_anos != null ? ` (${citizen.idade_anos} anos)` : ''}
                          </div>
                          <div style={{ fontSize: '13px', fontWeight: 500, color: '#0f172a', marginTop: '2px' }}>
                            {myRecAlert || 'Suas vacinas estão de acordo com o calendário nacional de imunizações do Ministério da Saúde.'}
                          </div>
                        </div>

                        <button
                          type="button"
                          className="btn"
                          onClick={() => setShowOnlyRecs(!showOnlyRecs)}
                          style={{
                            fontSize: '11px',
                            padding: '6px 12px',
                            background: showOnlyRecs ? '#2563eb' : '#ffffff',
                            color: showOnlyRecs ? '#ffffff' : '#2563eb',
                            border: '1px solid #bfdbfe',
                          }}
                        >
                          {showOnlyRecs ? 'Mostrar Todas as Vacinas' : 'Filtrar Só Minhas Vacinas'}
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Filtros por Ciclo de Vida */}
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
                    {[
                      { id: 'todas', label: 'Todas as Idades' },
                      { id: 'recem_nascido', label: 'Ao Nascer' },
                      { id: 'crianca', label: 'Criança' },
                      { id: 'adolescente', label: 'Adolescente' },
                      { id: 'adulto', label: 'Adulto' },
                      { id: 'idoso', label: 'Idoso (60+)' },
                      { id: 'gestante', label: 'Gestante' },
                    ].map((f) => (
                      <button
                        key={f.id}
                        type="button"
                        onClick={() => {
                          setShowOnlyRecs(false);
                          setVaccineFilter(f.id);
                        }}
                        style={{
                          fontSize: '12px',
                          fontWeight: 500,
                          padding: '6px 14px',
                          borderRadius: '99px',
                          cursor: 'pointer',
                          background: vaccineFilter === f.id && !showOnlyRecs ? '#2563eb' : 'rgba(255,255,255,0.7)',
                          color: vaccineFilter === f.id && !showOnlyRecs ? '#ffffff' : '#1e40af',
                          border: '1px solid var(--b2)',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>

                  {/* Grid de Vacinas Oficiais */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                      gap: '14px',
                    }}
                  >
                    {(showOnlyRecs && myRecVaccines.length > 0 ? myRecVaccines : vaccines).map((vac) => (
                      <div
                        key={vac.id}
                        className="c g"
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'space-between',
                          padding: '14px',
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                            <b style={{ fontWeight: 600, color: '#0a1b3d', fontSize: '13px' }}>
                              {vac.nome}
                            </b>
                            {vac.sigla && (
                              <span
                                style={{
                                  fontSize: '10px',
                                  padding: '2px 6px',
                                  borderRadius: '6px',
                                  background: 'rgba(37,99,235,0.1)',
                                  color: '#1e40af',
                                  fontWeight: 600,
                                }}
                              >
                                {vac.sigla}
                              </span>
                            )}
                          </div>

                          <div style={{ fontSize: '11px', color: '#2563eb', fontWeight: 500, marginTop: '4px' }}>
                            🗓️ {vac.faixa_etaria_display}
                          </div>

                          <div style={{ fontSize: '11px', color: '#475569', marginTop: '6px' }}>
                            <b>Idade:</b> {vac.idade_recomendada}
                          </div>

                          <div style={{ fontSize: '11px', color: '#475569', marginTop: '2px' }}>
                            <b>Esquema:</b> {vac.doses}
                          </div>

                          <div style={{ fontSize: '11px', color: '#166534', marginTop: '4px' }}>
                            <b>Previne:</b> {vac.doencas_prevenidas}
                          </div>

                          <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px', fontStyle: 'italic' }}>
                            {vac.orientacoes}
                          </div>
                        </div>

                        <button
                          type="button"
                          className="btn"
                          onClick={() => {
                            navigateToTab(1);
                            handleSendMessage(`Quais UBSs em ${citizen ? citizen.ra_display : 'DF'} têm a vacina ${vac.nome}?`);
                          }}
                          style={{
                            marginTop: '12px',
                            fontSize: '11px',
                            padding: '4px 10px',
                            background: 'white',
                            color: '#2563eb',
                            border: '1px solid #bfdbfe',
                            width: '100%',
                          }}
                        >
                          Perguntar onde tomar esta vacina
                        </button>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </section>

            {/* ----------------- SECTION 4: MONITORAMENTO ----------------- */}
            <section className={activeTab === 4 ? 'on' : ''}>
              <EpidemiologicalDashboard onAskSuzanna={handleAskSuzannaFromDashboard} />
            </section>

            {/* ----------------- SECTION 5: HISTÓRICO ----------------- */}
            <section className={activeTab === 5 ? 'on' : ''}>
              <h1>
                Histórico <b>clínico</b>
              </h1>
              <p className="sub">
                {citizen
                  ? `Prontuário unificado de ${citizen.nome_completo} (CPF: ${citizen.cpf_mascarado})`
                  : 'Seu prontuário digital unificado.'}
              </p>

              <div id="acs">
                {RECORDS.map((rec, i) => {
                  const isOpen = openAccordion === i;
                  return (
                    <div key={i} className={`ac g ${isOpen ? 'on' : ''}`}>
                      <button
                        type="button"
                        onClick={() => setOpenAccordion(isOpen ? null : i)}
                      >
                        {rec.title}
                      </button>
                      <div>
                        <p>
                          {rec.desc}
                          <br />
                          <br />
                          <span
                            className="btn"
                            style={{ display: 'inline-block', marginBottom: 16 }}
                            onClick={() => {
                              setDownloadNotice(`Arquivo ${rec.file} baixado com sucesso.`);
                              setTimeout(() => setDownloadNotice(null), 3000);
                            }}
                          >
                            ↓ {rec.file}
                          </span>
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {downloadNotice && (
                <div className="pill" style={{ marginTop: 12 }}>
                  ✓ {downloadNotice}
                </div>
              )}
            </section>
          </main>
        </div>
      </div>

      {/* Conta opcional: entrada/cadastro, perfil e lembretes */}
      <AuthDialog onOpenAgenda={() => enterApp(TAB_AGENDA)} />
      <ProfileSheet />
      <ReminderToast onOpenAgenda={() => enterApp(TAB_AGENDA)} />
    </>
  );
}
