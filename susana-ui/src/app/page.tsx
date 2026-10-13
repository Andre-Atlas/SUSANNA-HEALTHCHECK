'use client';

import React, { useState, useEffect, useRef } from 'react';

// =========================================================================
// Tipos e Interfaces da Plataforma SUS Digital
// =========================================================================
interface InteractiveOption {
  label: string;
  query: string;
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
}

interface CitizenProfile {
  id: string;
  nome_completo: string;
  primeiro_nome: string;
  cpf_mascarado: string;
  cns_mascarado?: string;
  data_nascimento: string;
  idade_anos: number;
  faixa_etaria: string;
  sexo_biologico: string;
  gestante: boolean;
  ra_residencia: string;
  ra_display: string;
  bairro_ou_setor?: string;
  telefone?: string;
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

function formatApiError(detail: unknown, fallback: string): string {
  if (typeof detail === 'string' && detail.trim()) return detail;

  if (Array.isArray(detail)) {
    const fieldLabels: Record<string, string> = {
      bairro_ou_setor: 'Bairro ou setor',
      cns: 'Cartão SUS',
      cpf: 'CPF',
      data_nascimento: 'Data de nascimento',
      gestante: 'Gestação',
      nome_completo: 'Nome completo',
      ra_residencia: 'Região Administrativa',
      sexo_biologico: 'Sexo biológico',
      telefone: 'Telefone',
    };
    const messages = detail.flatMap((item: unknown) => {
      if (typeof item === 'string') return [item];
      if (!item || typeof item !== 'object') return [];

      const issue = item as { loc?: unknown[]; msg?: unknown };
      if (typeof issue.msg !== 'string' || !issue.msg.trim()) return [];

      const field = issue.loc
        ?.filter((part): part is string => typeof part === 'string' && part !== 'body')
        .at(-1);
      const rawMessage = issue.msg === 'Field required'
        ? 'campo obrigatório'
        : issue.msg.replace(/^Value error,\s*/, '');
      const message = rawMessage.replace(/[.!?\s]+$/, '');
      return [field ? `${fieldLabels[field] ?? field}: ${message}` : message];
    });

    if (messages.length) return `${messages.join('. ')}.`;
  }

  if (detail && typeof detail === 'object') {
    const issue = detail as { message?: unknown; msg?: unknown };
    if (typeof issue.message === 'string') return issue.message;
    if (typeof issue.msg === 'string') return issue.msg;
  }

  return fallback;
}

// Epidemiological Data for Dengue
const DENGUE_CASES = [22, 30, 28, 41, 55, 49, 62, 58, 44, 36];
const REGION_BARS = [
  { name: 'Ceilândia', cases: 88 },
  { name: 'Samambaia', cases: 64 },
  { name: 'Taguatinga', cases: 52 },
  { name: 'Plano Piloto', cases: 31 },
  { name: 'Lago Sul', cases: 12 },
];

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

export default function Home() {
  // Navigation State
  const [viewMode, setViewMode] = useState<'landing' | 'app'>('landing');
  const [activeTab, setActiveTab] = useState<number>(0);

  // Citizen Profile & Auth State
  const [citizen, setCitizen] = useState<CitizenProfile | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'cadastro' | 'login'>('login');
  const [chatRegistrationDismissed, setChatRegistrationDismissed] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);

  // Citizen Registration Form
  const [formNome, setFormNome] = useState('');
  const [formCpf, setFormCpf] = useState('');
  const [formCns, setFormCns] = useState('');
  const [formDataNasc, setFormDataNasc] = useState('');
  const [formSexo, setFormSexo] = useState('');
  const [formGestante, setFormGestante] = useState(false);
  const [formRa, setFormRa] = useState('');
  const [formBairro, setFormBairro] = useState('');
  const [formTelefone, setFormTelefone] = useState('');

  // Citizen Login Form
  const [loginDoc, setLoginDoc] = useState('');
  const [loginDataNasc, setLoginDataNasc] = useState('');

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
  const [activeUnitTab, setActiveUnitTab] = useState<string>('UBS');
  const [units, setUnits] = useState<HealthUnitItem[]>([]);
  const [raList, setRaList] = useState<RADistribution[]>([]);
  const [selectedRA, setSelectedRA] = useState<string>('todas');
  const [selectedPin, setSelectedPin] = useState<HealthUnitItem | null>(null);
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [appointmentNotice, setAppointmentNotice] = useState<string | null>(null);

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
    // O perfil não é restaurado do cache; é carregado somente após login ou cadastro.
    localStorage.removeItem('susana_citizen');

    // Carregar lista de RAs oficiais do DF
    fetchRasList();

    // Carregar sessões de chat
    fetchChatSessions();

    // Carregar guia oficial de vacinas
    fetchVaccineGuide('todas');
  }, []);

  const fetchRasList = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/units/ras');
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
  const fetchChatSessions = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/chat/sessions');
      if (res.ok) {
        const list: ChatSessionItem[] = await res.json();
        setSessions(list);
        if (list.length > 0 && !currentSessionId) {
          loadSessionMessages(list[0].id);
        } else if (list.length === 0) {
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
      const res = await fetch('http://localhost:8000/api/chat/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'Nova conversa',
          citizen_id: citizen?.id || null,
        }),
      });

      if (res.ok) {
        const s: ChatSessionItem = await res.json();
        setSessions((prev) => [s, ...prev]);
        setCurrentSessionId(s.id);
        setIsSessionsDrawerOpen(false);

        // Mensagem de boas-vindas personalizada
        const welcomeText = `Olá, ${
          citizen ? citizen.primeiro_nome : 'Cidadão'
        }! Sou a Suzanna, assistente virtual oficial da Secretaria de Saúde do DF. Como posso ajudar com vacinas, unidades de saúde ou agendamentos na sua região?`;

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
          }! Sou a Suzanna. Como posso orientar você hoje?`,
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
      const res = await fetch(`http://localhost:8000/api/chat/sessions/${sessionId}/messages`);
      if (res.ok) {
        const msgs = await res.json();
        if (msgs.length === 0) {
          const welcomeText = `Olá, ${
            citizen ? citizen.primeiro_nome : 'Cidadão'
          }! Sou a Suzanna. Como posso ajudar nesta conversa?`;
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
      await fetch(`http://localhost:8000/api/chat/sessions/${sessionId}`, { method: 'DELETE' });
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
    const fetchUnits = async () => {
      try {
        let tipoParam = '';
        if (activeUnitTab === 'UBS') tipoParam = 'ubs';
        else if (activeUnitTab === 'Hospitais') tipoParam = 'hospital';
        else if (activeUnitTab === 'UPA') tipoParam = 'upa';

        const url = new URL('http://localhost:8000/api/units');
        if (selectedRA && selectedRA !== 'todas') {
          url.searchParams.set('ra', selectedRA);
        }
        if (tipoParam) {
          url.searchParams.set('tipo', tipoParam);
        }

        const res = await fetch(url.toString());
        if (res.ok) {
          const data = await res.json();
          setUnits(data.units || []);
        }
      } catch (err) {
        console.warn('Erro ao carregar unidades de saúde:', err);
      }
    };

    fetchUnits();
  }, [activeUnitTab, selectedRA]);

  // -------------------------------------------------------------------------
  // Carregamento do Guia Oficial de Vacinação e Recomendações
  // -------------------------------------------------------------------------
  const fetchVaccineGuide = async (faixa: string) => {
    try {
      const url = new URL('http://localhost:8000/api/vaccines/guide');
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
        const url = new URL('http://localhost:8000/api/vaccines/recommendations');
        url.searchParams.set('data_nascimento', citizen.data_nascimento);
        url.searchParams.set('gestante', String(citizen.gestante));

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

  // -------------------------------------------------------------------------
  // Sync com Hash Routing
  // -------------------------------------------------------------------------
  useEffect(() => {
    let isInitialRoute = true;

    const handleHash = () => {
      const hash = window.location.hash.replace('#/', '').replace('#', '');
      if (!hash || hash === 'landing') {
        setViewMode('landing');
      } else {
        setViewMode('app');
        const tabMap: Record<string, number> = {
          inicio: 0,
          assistente: 1,
          servicos: 2,
          monitoramento: 3,
          historico: 4,
        };
        if (tabMap[hash] !== undefined) {
          setActiveTab(tabMap[hash]);
          if (isInitialRoute && !citizen) {
            setAuthMode(hash === 'assistente' ? 'cadastro' : 'login');
            setIsAuthModalOpen(true);
          }
        }
      }
      isInitialRoute = false;
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
    if (index === 1 && !citizen && !chatRegistrationDismissed) {
      setAuthMode('cadastro');
      setAuthError(null);
      setAuthSuccess(null);
      setIsAuthModalOpen(true);
    }
    const tabs = ['inicio', 'assistente', 'servicos', 'monitoramento', 'historico'];
    window.location.hash = `#/${tabs[index]}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const enterApp = (tabIndex: number = 0) => {
    setViewMode('app');
    if (!citizen && tabIndex !== 1) {
      setAuthMode('login');
      setAuthError(null);
      setAuthSuccess(null);
      setIsAuthModalOpen(true);
    }
    navigateToTab(tabIndex);
  };

  const closeAuthModal = () => {
    if (activeTab === 1) {
      setChatRegistrationDismissed(true);
    }
    setIsAuthModalOpen(false);
    setAuthError(null);
    setAuthSuccess(null);
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
      fetch('http://localhost:8000/api/chat/sessions/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSessionId,
          role: 'user',
          content: q,
        }),
      }).catch(() => {});
    }

    try {
      const res = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

      setMessages((prev) => [
        ...prev,
        { id: botMsgId, text: '', isUser: false, source: 'Consultando base SES-DF…' },
      ]);
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          let jsonStr = trimmed;
          if (trimmed.startsWith('data: ')) {
            jsonStr = trimmed.slice(6).trim();
          }
          if (jsonStr === '[DONE]') continue;
          try {
            const data = JSON.parse(jsonStr);
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
            if (!trimmed.startsWith('{')) {
              accumulatedText += jsonStr;
            }
          }
        }

        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMsgId
              ? {
                  ...msg,
                  text: accumulatedText || 'Processando resposta…',
                  source: botSources || 'Fonte: Ministério da Saúde / SES-DF',
                  options: botOptions.length > 0 ? botOptions : msg.options,
                  citations: botCitations.length > 0 ? botCitations : msg.citations,
                }
              : msg
          )
        );
      }

      // Salva mensagem do bot na sessão ativa
      if (currentSessionId && accumulatedText) {
        fetch('http://localhost:8000/api/chat/sessions/messages', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
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
          fetch('http://localhost:8000/api/chat/sessions/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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

  // -------------------------------------------------------------------------
  // Handlers de Cadastro e Login do Cidadão
  // -------------------------------------------------------------------------
  const handleRegisterCitizen = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthSuccess(null);

    try {
      const cleanCpf = formCpf.replace(/\D/g, '');
      const cleanCns = formCns.replace(/\D/g, '') || null;

      const payload = {
        nome_completo: formNome.trim(),
        cpf: cleanCpf,
        cns: cleanCns,
        data_nascimento: formDataNasc,
        sexo_biologico: formSexo,
        gestante: formGestante,
        ra_residencia: formRa,
        bairro_ou_setor: formBairro.trim() || null,
        telefone: formTelefone.trim() || null,
      };

      const res = await fetch('http://localhost:8000/api/citizen/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiError(data.detail, 'Erro ao realizar cadastro.'));
      }

      setCitizen(data);
      setAuthSuccess('Cadastro realizado com sucesso!');
      setTimeout(() => {
        setIsAuthModalOpen(false);
        setAuthSuccess(null);
      }, 1200);
    } catch (err: any) {
      setAuthError(err.message || 'Falha na validação dos dados.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLoginCitizen = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthSuccess(null);

    try {
      const cleanDoc = loginDoc.replace(/\D/g, '');
      const res = await fetch('http://localhost:8000/api/citizen/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cpf_or_cns: cleanDoc,
          data_nascimento: loginDataNasc,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(formatApiError(data.detail, 'Documento ou data de nascimento incorretos.'));
      }

      setCitizen(data);
      setAuthSuccess(`Bem-vindo de volta, ${data.primeiro_nome}!`);
      setTimeout(() => {
        setIsAuthModalOpen(false);
        setAuthSuccess(null);
      }, 1000);
    } catch (err: any) {
      setAuthError(err.message || 'Falha ao autenticar.');
    } finally {
      setAuthLoading(false);
    }
  };

  // Generate SVG Spline path for Dengue chart
  const renderSpline = () => {
    const w = 600;
    const h = 170;
    const mx = 70;
    const pts = DENGUE_CASES.map((v, i) => [
      i * (w / (DENGUE_CASES.length - 1)),
      h - (v / mx) * h,
    ]);

    let d = `M${pts[0][0]},${pts[0][1]}`;
    for (let i = 1; i < pts.length; i++) {
      const mid = (pts[i - 1][0] + pts[i][0]) / 2;
      d += ` C${mid},${pts[i - 1][1]} ${mid},${pts[i][1]} ${pts[i][0]},${pts[i][1]}`;
    }

    return (
      <svg id="ln" viewBox="0 0 600 200">
        <defs>
          <linearGradient id="gr" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#60a5fa" stopOpacity="0.45" />
            <stop offset="1" stopColor="#60a5fa" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={`${d} L${w},${h} L0,${h}Z`} fill="url(#gr)" />
        <path d={d} fill="none" stroke="#2563eb" strokeWidth="3" strokeLinecap="round" />
        {pts.map((q, idx) => (
          <text key={idx} x={q[0]} y={192} textAnchor="middle">
            {`S${idx + 36}`}
          </text>
        ))}
      </svg>
    );
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
            Falar com a Suzanna
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
              Agende consultas, acompanhe exames e tire dúvidas com a Suzanna, assistente de IA que consulta dados atualizados da rede pública de todas as 33 Regiões Administrativas do DF.
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
              alt="Suzanna, a assistente virtual do SUS Digital, acenando"
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
            <p>Respostas fundamentadas em 346 unidades e diretrizes clínicas oficiais do SUS.</p>
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

            {/* Cartão de Identificação do Cidadão no Sidebar */}
            <div
              className="citizen-card"
              style={{
                padding: '10px 12px',
                margin: '0 0 16px',
                borderRadius: '14px',
                background: 'rgba(255, 255, 255, 0.45)',
                border: '1px solid var(--b2)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
              }}
            >
              <div
                style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  color: '#64748b',
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}
              >
                {citizen ? 'Cidadão do DF' : 'Acesso ao cidadão'}
              </div>
              <div
                style={{
                  fontWeight: 600,
                  fontSize: '13px',
                  color: '#0f172a',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  marginTop: '2px',
                }}
              >
                {citizen ? citizen.nome_completo : 'Entrar ou fazer cadastro'}
              </div>
              <div style={{ fontSize: '11px', color: '#2563eb', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>📍</span>
                <span style={{ fontWeight: 500 }}>{citizen ? citizen.ra_display : 'Distrito Federal'}</span>
              </div>
              {citizen?.cpf_mascarado && (
                <div style={{ fontSize: '10px', color: '#64748b', marginTop: '2px' }}>
                  CPF: {citizen.cpf_mascarado}
                </div>
              )}
              <button
                type="button"
                className="citizen-card-action"
                onClick={() => {
                  setAuthMode(citizen ? 'cadastro' : 'login');
                  setIsAuthModalOpen(true);
                }}
                style={{
                  marginTop: '8px',
                  width: '100%',
                  fontSize: '11px',
                  fontWeight: 500,
                  padding: '5px 8px',
                  borderRadius: '8px',
                  border: '1px solid rgba(37,99,235,0.2)',
                  background: 'rgba(255,255,255,0.85)',
                  cursor: 'pointer',
                  color: '#1e40af',
                  transition: 'all 0.2s ease',
                }}
              >
                {citizen ? '👤 Alterar dados / Perfil' : 'Entrar'}
              </button>
            </div>

            <button
              className={activeTab === 0 ? 'on' : ''}
              onClick={() => navigateToTab(0)}
            >
              Início
            </button>
            <button
              className={activeTab === 1 ? 'on' : ''}
              onClick={() => navigateToTab(1)}
            >
              Assistente
            </button>
            <button
              className={activeTab === 2 ? 'on' : ''}
              onClick={() => navigateToTab(2)}
            >
              Serviços e Vacinas
            </button>
            <button
              className={activeTab === 3 ? 'on' : ''}
              onClick={() => navigateToTab(3)}
            >
              Monitoramento
            </button>
            <button
              className={activeTab === 4 ? 'on' : ''}
              onClick={() => navigateToTab(4)}
            >
              Histórico
            </button>

            <button
              id="out"
              style={{ marginTop: 'auto' }}
              onClick={exitApp}
            >
              ← Sair
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
                  ? `Prontuário ativo em ${citizen.ra_display} · ${citizen.faixa_etaria.toUpperCase()} (${citizen.idade_anos} anos). Resumo de saúde pública oficial do DF.`
                  : 'Seu resumo de saúde e serviços da rede pública do Distrito Federal.'}
              </p>

              {/* Banner de Recomendação em Destaque */}
              {recAlert && (
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
                  <span>{recAlert}</span>
                </div>
              )}

              <div className="grid">
                <div
                  className="c g hv q"
                  onClick={() => {
                    setServiceSubTab('mapa');
                    navigateToTab(2);
                  }}
                >
                  <b>Agendar na sua UBS</b>
                  <span>{citizen ? `Unidades em ${citizen.ra_display}` : 'Rede de Atenção Primária'}</span>
                </div>
                <div
                  className="c g hv q"
                  onClick={() => {
                    setServiceSubTab('vacinas');
                    navigateToTab(2);
                  }}
                >
                  <b>Guia de Vacinação PNI</b>
                  <span>{recVaccines.length > 0 ? `${recVaccines.length} doses indicadas para seu perfil` : 'Calendário por idade'}</span>
                </div>
                <div
                  className="c g hv q"
                  onClick={() => {
                    navigateToTab(1);
                  }}
                >
                  <b>Falar com a Suzanna</b>
                  <span>Tire dúvidas com IA</span>
                </div>
              </div>

              <div className="grid" style={{ marginTop: '24px' }}>
                <div className="c g" style={{ gridColumn: '1 / -1' }}>
                  <h3>Próximos agendamentos e acompanhamento</h3>
                  <ul className="tl">
                    <li>
                      Acolhimento Primário · UBS de referência ({citizen ? citizen.ra_display : 'DF'})
                      <br />
                      <small>Segunda a sexta-feira · Atendimento por ordem de chegada ou agendamento</small>
                    </li>
                    <li>
                      Campanhas de Vacinação Ativas
                      <br />
                      <small>Influenza, COVID-19 e rotina nas salas de vacina de todas as UBSs</small>
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            {/* ----------------- SECTION 1: ASSISTENTE (MULTI-SESSÃO) ----------------- */}
            <section className={activeTab === 1 ? 'on' : ''}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <h1 style={{ margin: 0 }}>
                    Fale com a <b>Suzanna</b>
                  </h1>
                  <p className="sub" style={{ margin: '4px 0 0' }}>
                    Respostas em streaming fundamentadas em 346 unidades e diretrizes clínicas oficiais do SUS-DF.
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
                          alt="Suzanna"
                        />
                      )}
                      <div className="b">
                        <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>
                          {m.text}
                        </div>

                        {/* Citações Estruturadas com Links Oficiais */}
                        {m.citations && m.citations.length > 0 && (
                          <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {m.citations.map((c, ci) => (
                              <a
                                key={ci}
                                href={c.url || '#'}
                                target={c.url ? '_blank' : undefined}
                                rel="noopener noreferrer"
                                style={{
                                  fontSize: '11px',
                                  color: '#1e40af',
                                  background: 'rgba(37,99,235,0.08)',
                                  padding: '4px 10px',
                                  borderRadius: '99px',
                                  textDecoration: 'none',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '4px',
                                  border: '1px solid rgba(37,99,235,0.18)',
                                  fontWeight: 400,
                                }}
                              >
                                📄 {c.title.slice(0, 35)}{c.title.length > 35 ? '...' : ''}
                              </a>
                            ))}
                          </div>
                        )}

                        {/* Chips de Opções Interativas */}
                        {m.options && m.options.length > 0 && (
                          <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid rgba(0,0,0,0.06)', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {m.options.map((opt, oi) => (
                              <button
                                key={oi}
                                type="button"
                                onClick={() => handleSendMessage(opt.query)}
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

                        {m.source && (
                          <small
                            className="mut"
                            style={{ display: 'block', marginTop: '6px', fontSize: '11px' }}
                          >
                            {m.source}
                          </small>
                        )}
                      </div>
                    </div>
                  ))}
                  {isBotTyping && (
                    <div className="m bot">
                      <img src="/images/suzanna-avatar.webp" alt="Suzanna" />
                      <div className="b" style={{ fontStyle: 'italic', color: '#64748b' }}>
                        Suzanna está pesquisando dados da SES-DF…
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

            {/* ----------------- SECTION 2: SERVIÇOS & VACINAS ----------------- */}
            <section className={activeTab === 2 ? 'on' : ''}>
              <h1>
                Serviços, <b>Unidades e Vacinação</b>
              </h1>
              <p className="sub">
                Explore as 346 unidades de saúde nas 33 RAs do Distrito Federal e consulte o Guia Oficial do PNI.
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
                  {/* Seletor de Região Administrativa (33 RAs Reais) e Tipo de Unidade */}
                  <div
                    style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '12px',
                      alignItems: 'center',
                      marginBottom: '16px',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: '#1e3a8a' }}>Região Administrativa:</span>
                      <select
                        value={selectedRA}
                        onChange={(e) => setSelectedRA(e.target.value)}
                        style={{
                          padding: '8px 14px',
                          borderRadius: '12px',
                          border: '1px solid var(--b2)',
                          background: 'rgba(255,255,255,0.85)',
                          fontSize: '13px',
                          color: '#0f172a',
                          fontWeight: 500,
                          cursor: 'pointer',
                        }}
                      >
                        <option value="todas">Todas as 33 Regiões do DF</option>
                        {raList.map((r) => (
                          <option key={r.ra} value={r.ra}>
                            {r.ra_display} ({r.unit_count} unidades)
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Filtro de Tipo: UBS, Hospitais, UPA */}
                    <div className="tabs g" style={{ margin: 0 }}>
                      {['UBS', 'Hospitais', 'UPA'].map((tabKey) => (
                        <button
                          key={tabKey}
                          className={activeUnitTab === tabKey ? 'on' : ''}
                          onClick={() => {
                            setActiveUnitTab(tabKey);
                            setSelectedPin(null);
                          }}
                        >
                          {tabKey}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid">
                    {/* Vector Map com Pins Reais */}
                    <div>
                      <div className="map g" id="map">
                        <svg viewBox="0 0 400 300">
                          {/* Estrutura visual da malha viária do DF */}
                          <path
                            d="M-10 210C80 170 140 240 230 190S350 120 420 150"
                            fill="none"
                            stroke="#fff"
                            strokeWidth="14"
                            opacity="0.8"
                          />
                          <path
                            d="M120 -10C150 80 110 160 160 310"
                            fill="none"
                            stroke="#fff"
                            strokeWidth="10"
                            opacity="0.8"
                          />

                          {/* Pins Reais das Unidades de Saúde */}
                          <g id="pins">
                            {(selectedRA === 'todas' ? units.slice(0, 60) : units).map((u, i) => {
                              const isSelected = selectedPin?.id === u.id;
                              // Mapeamento das coordenadas SVG percentuais (0-100) para o viewBox 400x300
                              const cx = (u.svg_x / 100) * 360 + 20;
                              const cy = (u.svg_y / 100) * 260 + 20;

                              return (
                                <g
                                  key={u.id || i}
                                  className="pin"
                                  onClick={() => setSelectedPin(u)}
                                  style={{ cursor: 'pointer' }}
                                >
                                  <circle
                                    cx={cx}
                                    cy={cy}
                                    r={isSelected ? 10 : 7}
                                    fill={isSelected ? '#dc2626' : '#2563eb'}
                                    stroke="#fff"
                                    strokeWidth="2.5"
                                  />
                                  <circle
                                    cx={cx}
                                    cy={cy}
                                    r={isSelected ? 18 : 14}
                                    fill={isSelected ? '#dc2626' : '#2563eb'}
                                    opacity="0.2"
                                  />
                                </g>
                              );
                            })}
                          </g>
                        </svg>

                        <div style={{ fontSize: '11px', color: '#64748b', padding: '6px 10px', background: 'rgba(255,255,255,0.4)', borderRadius: '8px', margin: '4px 8px 8px' }}>
                          📍 Mostrando {selectedRA === 'todas' ? Math.min(60, units.length) : units.length} de {units.length} unidades encontradas{selectedRA === 'todas' ? ' (selecione uma RA para focar e listar todas as unidades da região)' : ''}.
                        </div>

                        {/* Gaveta de Detalhes da Unidade Real */}
                        <div className={`det g ${selectedPin ? 'on' : ''}`} id="det">
                          {selectedPin ? (
                            <>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <b style={{ fontWeight: 600, color: '#0a1b3d', fontSize: '14px' }}>
                                  {selectedPin.nome}
                                </b>
                                <span
                                  style={{
                                    fontSize: '10px',
                                    padding: '2px 8px',
                                    borderRadius: '99px',
                                    background: '#2563eb',
                                    color: '#fff',
                                    fontWeight: 500,
                                  }}
                                >
                                  {selectedPin.tipo_display}
                                </span>
                              </div>
                              <div style={{ fontSize: '12px', color: '#2563eb', fontWeight: 500, marginTop: '4px' }}>
                                📍 Região: {selectedPin.ra_display}
                              </div>
                              <div style={{ fontSize: '11px', color: '#475569', marginTop: '4px' }}>
                                🏢 Endereço: {selectedPin.endereco}
                              </div>
                              <div style={{ fontSize: '11px', color: '#166534', marginTop: '2px', fontWeight: 500 }}>
                                ⏰ Horário: {selectedPin.horario}
                              </div>
                              {selectedPin.servicos && selectedPin.servicos.length > 0 && (
                                <div style={{ fontSize: '11px', color: '#475569', marginTop: '4px' }}>
                                  🩺 Serviços: {selectedPin.servicos.slice(0, 4).join(', ')}
                                </div>
                              )}
                              {selectedPin.referencia_emergencia && (
                                <div style={{ fontSize: '10px', color: '#b91c1c', marginTop: '4px' }}>
                                  🚨 Emergência: {selectedPin.referencia_emergencia}
                                </div>
                              )}
                              <button
                                type="button"
                                className="btn"
                                onClick={() => {
                                  navigateToTab(1);
                                  handleSendMessage(`Quais serviços e vacinas estão disponíveis na ${selectedPin.nome} em ${selectedPin.ra_display}?`);
                                }}
                                style={{
                                  marginTop: '8px',
                                  fontSize: '11px',
                                  padding: '4px 10px',
                                  background: 'white',
                                  color: '#2563eb',
                                  border: '1px solid #bfdbfe',
                                }}
                              >
                                Perguntar à Suzanna sobre esta unidade
                              </button>
                            </>
                          ) : (
                            <span className="mut">
                              Clique em um dos pontos no mapa para inspecionar endereço, horário e serviços oficiais.
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Calendário de Agendamentos */}
                    <div className="c g">
                      <h3>Outubro 2026 · Agendamento</h3>
                      <p className="mut" style={{ fontSize: '12px', margin: '0 0 12px' }}>
                        Dias livres para acolhimento e vacinação na sua região:
                      </p>
                      <div className="cal" id="cal">
                        {['D', 'S', 'T', 'Q', 'Q', 'S', 'S'].map((dayName, idx) => (
                          <span key={idx} className="h">
                            {dayName}
                          </span>
                        ))}

                        {/* 4 Empty offset days for Oct 1st 2026 */}
                        {[0, 1, 2, 3].map((pad) => (
                          <span key={`pad-${pad}`}></span>
                        ))}

                        {/* 1 to 31 */}
                        {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => {
                          const isAvailable = [8, 9, 13, 15, 16, 20, 22, 27, 29].includes(day);
                          const isSelected = selectedDay === day;
                          return (
                            <span
                              key={day}
                              onClick={() => isAvailable && setSelectedDay(day)}
                              className={isSelected ? 'a s' : isAvailable ? 'a' : ''}
                            >
                              {day}
                            </span>
                          );
                        })}
                      </div>

                      <div style={{ marginTop: '14px' }}>
                        {selectedDay ? (
                          <div>
                            <p style={{ margin: 0, fontSize: '13px', color: '#0f172a' }}>
                              Dia <b>{selectedDay} de outubro</b> selecionado.{' '}
                            </p>
                            <button
                              type="button"
                              className="btn"
                              onClick={() => {
                                const unitName = selectedPin ? selectedPin.nome : `UBS de ${citizen ? citizen.ra_display : 'referência'}`;
                                setAppointmentNotice(`Agendamento confirmado para o dia ${selectedDay}/10 às 14h na ${unitName}.`);
                                setTimeout(() => setAppointmentNotice(null), 5000);
                              }}
                              style={{
                                marginTop: '8px',
                                fontSize: '12px',
                                padding: '6px 12px',
                                background: '#2563eb',
                                color: '#ffffff',
                              }}
                            >
                              Confirmar Horário às 14h
                            </button>
                          </div>
                        ) : (
                          <p className="mut" style={{ margin: 0, fontSize: '12px' }}>
                            Selecione um dos dias azuis disponíveis no calendário.
                          </p>
                        )}

                        {appointmentNotice && (
                          <div
                            className="pill"
                            style={{
                              marginTop: '10px',
                              background: 'rgba(22,101,52,0.1)',
                              border: '1px solid rgba(22,101,52,0.25)',
                              color: '#166534',
                              fontWeight: 500,
                              fontSize: '12px',
                            }}
                          >
                            ✓ {appointmentNotice}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </>
              )}

              {/* ---------------- SUBVIEW 2: GUIA DE VACINAÇÃO PNI ---------------- */}
              {serviceSubTab === 'vacinas' && (
                <>
                  {/* Banner de Recomendação Personalizada do Cidadão */}
                  {citizen && (
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
                            Recomendação Personalizada para {citizen.primeiro_nome} ({citizen.idade_anos} anos · {citizen.faixa_etaria})
                          </div>
                          <div style={{ fontSize: '13px', fontWeight: 500, color: '#0f172a', marginTop: '2px' }}>
                            {recAlert || 'Suas vacinas estão de acordo com o calendário nacional de imunizações do Ministério da Saúde.'}
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
                    {(showOnlyRecs && recVaccines.length > 0 ? recVaccines : vaccines).map((vac) => (
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

            {/* ----------------- SECTION 3: MONITORAMENTO ----------------- */}
            <section className={activeTab === 3 ? 'on' : ''}>
              <h1>
                Monitoramento <b>epidemiológico</b>
              </h1>
              <p className="sub">Casos de dengue por semana (dados oficiais SES-DF).</p>

              <div className="grid">
                <div className="c g ch" style={{ gridColumn: '1 / -1' }}>
                  <h3>Casos por semana</h3>
                  {renderSpline()}
                </div>
              </div>

              <div className="grid">
                <div className="c g">
                  <h3>Por região administrativa</h3>
                  <div id="bars">
                    {REGION_BARS.map((r, idx) => (
                      <div key={idx} className="bar">
                        <span style={{ width: 96, fontWeight: 400 }}>{r.name}</span>
                        <i style={{ width: `${r.cases * 0.6}%` }}></i>
                        <span className="mut" style={{ fontWeight: 500 }}>
                          {r.cases}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="c g">
                  <h3>Dicas de prevenção</h3>
                  <ul className="tl">
                    <li>Elimine água parada em pratos e calhas.</li>
                    <li>Use repelente e roupas claras e compridas.</li>
                    <li>Febre alta e dor no corpo: procure uma UBS.</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* ----------------- SECTION 4: HISTÓRICO ----------------- */}
            <section className={activeTab === 4 ? 'on' : ''}>
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

      {/* =========================================================================
          MODAL DE CADASTRO / LOGIN DO CIDADÃO (DADOS 100% REAIS)
      ========================================================================= */}
      {isAuthModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(10, 27, 61, 0.45)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '16px',
          }}
        >
          <div
            className="g"
            role="dialog"
            aria-modal="true"
            aria-labelledby="citizen-auth-title"
            style={{
              width: '100%',
              maxWidth: '520px',
              padding: '24px',
              borderRadius: '24px',
              background: 'rgba(255, 255, 255, 0.95)',
              boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
              position: 'relative',
              maxHeight: '90vh',
              overflowY: 'auto',
            }}
          >
            {/* Fechar Modal */}
            <button
              type="button"
              onClick={closeAuthModal}
              aria-label="Fechar janela de identificação"
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'transparent',
                border: 'none',
                fontSize: '18px',
                cursor: 'pointer',
                color: '#64748b',
              }}
            >
              ✕
            </button>

            <h2 id="citizen-auth-title" style={{ margin: '0 0 6px', fontSize: '20px', color: '#0a1b3d' }}>
              {authMode === 'login' ? 'Entrar no SUS Digital' : <>Identificação do <b>Cidadão SUS-DF</b></>}
            </h2>
            <p style={{ margin: '0 0 16px', fontSize: '13px', color: '#64748b' }}>
              {authMode === 'login'
                ? 'Acesse com seu CPF ou Cartão SUS e data de nascimento.'
                : 'Validação algorítmica oficial de CPF (módulo 11) e Cartão SUS (DATASUS).'}
            </p>

            {/* Alternância de Abas: Cadastro vs Login */}
            <div className="auth-tabs" role="tablist" aria-label="Acesso do cidadão">
              <button
                type="button"
                role="tab"
                aria-selected={authMode === 'cadastro'}
                className={authMode === 'cadastro' ? 'auth-tab on' : 'auth-tab'}
                onClick={() => setAuthMode('cadastro')}
              >
                Novo Cadastro
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={authMode === 'login'}
                className={authMode === 'login' ? 'auth-tab on' : 'auth-tab'}
                onClick={() => setAuthMode('login')}
              >
                Entrar
              </button>
            </div>

            {/* Mensagens de Feedback */}
            {authError && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.3)',
                  color: '#b91c1c',
                  fontSize: '12px',
                  marginBottom: '14px',
                }}
              >
                ⚠️ {authError}
              </div>
            )}
            {authSuccess && (
              <div
                style={{
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: 'rgba(22,101,52,0.1)',
                  border: '1px solid rgba(22,101,52,0.3)',
                  color: '#15803d',
                  fontSize: '12px',
                  marginBottom: '14px',
                }}
              >
                ✓ {authSuccess}
              </div>
            )}

            {/* Formulário de Cadastro */}
            {authMode === 'cadastro' ? (
              <form onSubmit={handleRegisterCitizen} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                    Nome Completo *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Ex: Carlos Eduardo de Oliveira"
                    value={formNome}
                    onChange={(e) => setFormNome(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                      CPF (Módulo 11) *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="000.000.000-00"
                      value={formCpf}
                      onChange={(e) => setFormCpf(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                      Data de Nascimento *
                    </label>
                    <input
                      type="date"
                      required
                      value={formDataNasc}
                      onChange={(e) => setFormDataNasc(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                      Cartão SUS / CNS (Opcional)
                    </label>
                    <input
                      type="text"
                      placeholder="15 dígitos"
                      value={formCns}
                      onChange={(e) => setFormCns(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                    />
                  </div>
                  <div>
                    <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                      Sexo Biológico
                    </label>
                    <select
                      value={formSexo}
                      onChange={(e) => setFormSexo(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                    >
                      <option value="" disabled>Selecione</option>
                      <option value="F">Feminino</option>
                      <option value="M">Masculino</option>
                      <option value="N">Prefiro não informar</option>
                    </select>
                  </div>
                </div>

                {formSexo === 'F' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 0' }}>
                    <input
                      type="checkbox"
                      id="gestanteCheck"
                      checked={formGestante}
                      onChange={(e) => setFormGestante(e.target.checked)}
                      style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                    />
                    <label htmlFor="gestanteCheck" style={{ fontSize: '12px', color: '#1e3a8a', cursor: 'pointer', fontWeight: 500 }}>
                      Cidadã está gestante (ativa guia de imunização materna dTpa e pré-natal)
                    </label>
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                      Região Administrativa (RA) *
                    </label>
                    <select
                      required
                      value={formRa}
                      onChange={(e) => setFormRa(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                    >
                      <option value="" disabled>Selecione uma região</option>
                      {raList.map((r) => (
                        <option key={r.ra} value={r.ra}>
                          {r.ra_display}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                      Bairro ou Setor
                    </label>
                    <input
                      type="text"
                      placeholder="Ex: QNM 18 / Setor Sul"
                      value={formBairro}
                      onChange={(e) => setFormBairro(e.target.value)}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                    />
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                    Telefone para Contato
                  </label>
                  <input
                    type="text"
                    placeholder="(61) 98888-7777"
                    value={formTelefone}
                    onChange={(e) => setFormTelefone(e.target.value)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                  />
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="btn"
                  style={{
                    marginTop: '8px',
                    padding: '10px',
                    background: '#2563eb',
                    color: '#ffffff',
                    fontWeight: 600,
                    width: '100%',
                  }}
                >
                  {authLoading ? 'Validando documento…' : 'Salvar e Acessar'}
                </button>
              </form>
            ) : (
              /* Formulário de Login */
              <form onSubmit={handleLoginCitizen} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                    CPF ou Cartão Nacional de Saúde (CNS) *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Digite seu CPF ou CNS cadastrado"
                    value={loginDoc}
                    onChange={(e) => setLoginDoc(e.target.value)}
                    style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '11px', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '2px' }}>
                    Data de Nascimento (Confirmação 2FA) *
                  </label>
                  <input
                    type="date"
                    required
                    value={loginDataNasc}
                    onChange={(e) => setLoginDataNasc(e.target.value)}
                    style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--b2)', fontSize: '13px' }}
                  />
                </div>

                <button
                  type="submit"
                  disabled={authLoading}
                  className="btn"
                  style={{
                    marginTop: '8px',
                    padding: '10px',
                    background: '#2563eb',
                    color: '#ffffff',
                    fontWeight: 600,
                    width: '100%',
                  }}
                >
                  {authLoading ? 'Verificando…' : 'Entrar no SUS Digital'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
