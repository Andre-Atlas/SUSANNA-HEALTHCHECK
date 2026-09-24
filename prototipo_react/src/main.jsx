import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const SUSANA_AVATAR = '/susana-avatar.jpeg';

const NAV_ITEMS = [
  ['home', 'Início'],
  ['apps', 'Aplicações'],
  ['health', 'Minha saúde'],
  ['content', 'Conteúdos'],
  ['profile', 'Meu perfil'],
  ['help', 'Dúvidas frequentes'],
];

const HEALTH_ITEMS = [
  ['medical', 'Médicos especialistas', 'Consultas e acompanhamento'],
  ['vaccine', 'Vacinas', 'Histórico e orientações'],
  ['exam', 'Exames', 'Resultados e informações'],
  ['medicine', 'Medicamentos', 'Uso e acesso'],
  ['menstrual', 'Dignidade menstrual', 'Informações e serviços'],
  ['network', 'Rede de saúde', 'Unidades e serviços'],
  ['schedule', 'Agendamentos', 'Consultas e atendimentos'],
  ['care', 'Atendimentos e internação', 'Acompanhamento'],
];

const MINI_APPS = [
  ['Acolhe Mais+', 'Saúde mental', 'purple', 'Informações e caminhos para cuidado em saúde mental.'],
  ['Não Aposte Sua Saúde', 'Prevenção', 'blue', 'Conteúdos educativos para decisões mais seguras.'],
  ['Modera Brasil', 'Cuidado e prevenção', 'cyan', 'Orientações de prevenção e hábitos de saúde.'],
  ['Peso Saudável', 'Hábitos e saúde', 'soft', 'Conteúdos de alimentação e hábitos saudáveis.'],
  ['Hemovida', 'Doação de sangue', 'pink', 'Informações para doadores e hemocentros.'],
  ['Transplantes', 'Transplantes', 'green', 'Informações e orientações sobre transplantes.'],
];

const QUICK_QUESTIONS = [
  'Como encontro uma unidade de saúde?',
  'Onde posso consultar informações de vacinação?',
  'Como encontro informações sobre medicamentos?',
];

const FAQS = [
  ['Como encontro uma unidade de saúde?', 'Use a busca por serviços ou converse com a Susana para fazer uma pergunta mais específica sobre a rede do Distrito Federal.'],
  ['Onde posso consultar informações sobre vacinação?', 'A área de vacinação reúne orientações e o histórico disponível. A Susana também pode ajudar a localizar informações específicas.'],
  ['Como encontro informações sobre medicamentos?', 'Consulte a área de medicamentos ou informe à Susana o nome do medicamento para que ela possa orientar a busca.'],
  ['A Susana substitui um profissional de saúde?', 'Não. A Susana ajuda a encontrar e compreender informações do SUS. Ela não realiza diagnóstico nem prescreve tratamentos.'],
  ['A Susana responde sobre o Brasil inteiro?', 'Neste protótipo, o escopo está concentrado no Distrito Federal.'],
  ['Como vejo a origem de uma resposta?', 'Quando uma resposta possui fonte, use a opção Fonte para consultar a origem e abrir a referência oficial.'],
];

const CONTENTS = [
  ['Acesso à rede de saúde', 'Entenda como localizar serviços e unidades do SUS-DF.'],
  ['Vacinação', 'Consulte orientações e caminhos para informações de vacinação.'],
  ['Medicamentos', 'Veja como encontrar informações sobre medicamentos e assistência farmacêutica.'],
  ['Consultas e exames', 'Conheça os principais caminhos para acessar consultas e serviços.'],
];

function Icon({ name, size = 24 }) {
  const paths = {
    home: <><path d="M3 10.6 12 3l9 7.6"/><path d="M5.2 9.6v10h5.2v-6.2h3.2v6.2h5.2v-10"/></>,
    apps: <><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></>,
    health: <><path d="M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7z"/></>,
    content: <><path d="M5 3h14a2 2 0 0 1 2 2v15H7a3 3 0 0 1-3-3V5a2 2 0 0 1 2-2Z"/><path d="M7 20V6.5A2.5 2.5 0 0 0 4.5 4"/><path d="M9 8h7M9 12h7"/></>,
    profile: <><circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4.2 3.4-6 8-6s7.2 1.8 8 6"/></>,
    help: <><circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.6 2.6 0 1 1 4.4 2c-.8.8-2.1 1.2-2.1 2.6"/><path d="M12 17h.01"/></>,
    bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
    search: <><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 5 5"/></>,
    arrow: <><path d="M5 12h13"/><path d="m13 6 6 6-6 6"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>,
    send: <><path d="m3 4 17 8-17 8 3-8z"/><path d="M6 12h14"/></>,
    chevron: <path d="m6 9 6 6 6-6"/>,
    external: <><path d="M14 5h5v5"/><path d="m19 5-8 8"/><path d="M19 13v5a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/></>,
    medical: <><path d="M12 4c-3 0-5 2.5-5 5.5V17h10V9.5C17 6.5 15 4 12 4Z"/><path d="M9 17v3M15 17v3M8 9h8"/></>,
    vaccine: <><path d="M5 5h9"/><path d="M8 5v13M5 9h6"/><path d="m14 10 6-6"/><path d="m13 13 5 5"/><path d="M11 15 9 21"/></>,
    exam: <><path d="M5 5h4v14H5zM10 8h4v11h-4zM15 11h4v8h-4z"/><path d="M4 19h16"/></>,
    medicine: <><rect x="6" y="4" width="12" height="16" rx="4"/><path d="M8 12h8M12 8v8"/></>,
    menstrual: <path d="M12 3c0 4-5 7-5 11a5 5 0 0 0 10 0c0-4-5-7-5-11Z"/>,
    network: <><path d="M4 20V9h16v11"/><path d="M2 20h20M8 9V5h8v4"/><path d="M8 13h2M14 13h2M8 17h2M14 17h2"/></>,
    schedule: <><circle cx="12" cy="12" r="8"/><path d="M12 8v5l3 2"/></>,
    care: <><path d="M6 19v-5a6 6 0 0 1 12 0v5"/><path d="M8 8a4 4 0 0 1 8 0"/><path d="M5 20h14"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] ?? paths.help}</svg>;
}

function Sidebar({ active, onNavigate, open, onClose }) {
  return (
    <>
      <aside className={`sidebar ${open ? 'is-open' : ''}`} aria-label="Navegação principal">
        <div className="brand-lockup">
          <div className="brand-mark">SUS<span>+</span></div>
          <div className="brand-copy"><strong>Meu<br/>SUS</strong><span>Digital</span></div>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(([icon, label]) => (
            <button key={label} className={`nav-item ${active === label ? 'active' : ''}`} type="button" onClick={() => { onNavigate(label); onClose(); }}>
              <Icon name={icon} size={27} /><span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="gov-mark">gov.br</div>
      </aside>
      {open && <button className="mobile-overlay" type="button" aria-label="Fechar menu" onClick={onClose}/>}
    </>
  );
}

function Header({ onMenu, onSearch, onNotifications, notificationsOpen, onProfile }) {
  return (
    <header className="topbar">
      <button className="mobile-menu" type="button" aria-label="Abrir menu" onClick={onMenu}><Icon name="apps" size={23}/></button>
      <div className="greeting">Olá, <strong>usuário</strong></div>
      <div className="topbar-right">
        <button className="top-search" type="button" onClick={onSearch} aria-label="Pesquisar"><Icon name="search" size={21}/></button>
        <button className="top-icon" type="button" onClick={onNotifications} aria-label="Notificações" aria-expanded={notificationsOpen}><Icon name="bell" size={22}/></button>
        <button className="profile-pill" type="button" onClick={onProfile} aria-label="Abrir perfil">
          <div className="profile-copy"><strong>Usuário do Meu SUS Digital</strong><span>CPF: •••.•••.•••-••</span></div>
          <div className="profile-icon"><Icon name="profile" size={27}/></div>
        </button>
      </div>
      {notificationsOpen && (
        <div className="notification-popover" role="dialog" aria-label="Notificações">
          <strong>Notificações</strong>
          <p>Você não possui novas notificações neste protótipo.</p>
        </div>
      )}
    </header>
  );
}

function ServiceCard({ item, onOpen }) {
  const [icon, title, desc] = item;
  return <button className="health-card" type="button" onClick={() => onOpen(title, desc)}><span className="health-icon"><Icon name={icon} size={34}/></span><strong>{title}</strong><small>{desc}</small></button>;
}

function MiniApp({ item, onOpen }) {
  const [title, subtitle, theme, description] = item;
  return <button className="mini-app" type="button" onClick={() => onOpen(title, description)}><div className={`mini-art mini-${theme}`}>{title}</div><strong>{title}</strong><span>{subtitle}</span></button>;
}

function Home({ onAskSusana, onNavigate, onOpenDetail }) {
  const [query, setQuery] = useState('');
  const filtered = useMemo(() => HEALTH_ITEMS.filter(([, title, desc]) => `${title} ${desc}`.toLowerCase().includes(query.toLowerCase())), [query]);
  return (
    <main className="content">
      <section className="dashboard-intro">
        <div><p className="eyebrow">MEU SUS DIGITAL</p><h1>Minha saúde</h1><p>Encontre serviços, acompanhe informações e acesse orientações em um só lugar.</p></div>
        <button className="assistant-shortcut" type="button" onClick={onAskSusana}><img src={SUSANA_AVATAR} alt=""/><span>Falar com Susana</span><Icon name="arrow" size={16}/></button>
      </section>
      <div className="search-bar" id="globalSearch">
        <Icon name="search" size={22}/><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Busque por um serviço ou informação" aria-label="Buscar serviço ou informação"/><kbd>/</kbd>
      </div>
      <section className="section-block">
        <div className="section-title-row"><h2>Minha Saúde</h2><button type="button" className="see-all" onClick={() => onNavigate('Minha saúde')}>Ver tudo <Icon name="plus" size={17}/></button></div>
        <div className="health-grid">
          {filtered.map((item) => <ServiceCard key={item[1]} item={item} onOpen={onOpenDetail}/>)}
          {!filtered.length && <div className="empty-state">Nenhum serviço corresponde à sua busca.</div>}
        </div>
      </section>
      <section className="section-block mini-section">
        <div className="section-title-row"><h2>Mini apps</h2><button type="button" className="text-button" onClick={() => onNavigate('Aplicações')}>Ver tudo <Icon name="arrow" size={15}/></button></div>
        <div className="mini-grid">{MINI_APPS.map((item) => <MiniApp key={item[0]} item={item} onOpen={onOpenDetail}/>)}</div>
      </section>
      <section className="faq-strip">
        <div><p className="eyebrow">PRECISA DE AJUDA?</p><h2>Não encontrou o que precisava?</h2><p>Converse com a Susana e faça sua pergunta em linguagem natural.</p></div>
        <button type="button" className="faq-cta" onClick={onAskSusana}>Abrir Susana <Icon name="arrow" size={18}/></button>
      </section>
    </main>
  );
}

function Applications({ onOpenDetail }) {
  return <main className="content page-content"><div className="page-heading"><p className="eyebrow">APLICAÇÕES</p><h1>Mini apps</h1><p>Recursos complementares para acesso a conteúdos e serviços de saúde.</p></div><div className="mini-grid mini-grid-large">{MINI_APPS.map((item) => <MiniApp key={item[0]} item={item} onOpen={onOpenDetail}/>)}</div></main>;
}

function MyHealth({ onOpenDetail }) {
  return <main className="content page-content"><div className="page-heading"><p className="eyebrow">MEU SUS DIGITAL</p><h1>Minha saúde</h1><p>Acesse os principais serviços e informações de saúde disponíveis no protótipo.</p></div><div className="health-grid health-grid-expanded">{HEALTH_ITEMS.map((item) => <ServiceCard key={item[1]} item={item} onOpen={onOpenDetail}/>)}</div></main>;
}

function Contents() {
  return <main className="content page-content"><div className="page-heading"><p className="eyebrow">CONTEÚDOS</p><h1>Informações de saúde</h1><p>Conteúdos organizados para facilitar a navegação pelo SUS.</p></div><div className="content-list">{CONTENTS.map(([title, text]) => <article className="content-card" key={title}><div><p className="eyebrow">SAÚDE PÚBLICA</p><h2>{title}</h2><p>{text}</p></div><Icon name="arrow" size={18}/></article>)}</div></main>;
}

function Profile() {
  return <main className="content page-content"><div className="page-heading"><p className="eyebrow">MEU PERFIL</p><h1>Dados do usuário</h1><p>Área demonstrativa do perfil dentro do protótipo.</p></div><section className="profile-card"><div className="profile-large"><Icon name="profile" size={42}/></div><div><h2>Usuário do Meu SUS Digital</h2><p>CPF: •••.•••.•••-••</p><p className="muted">Os dados apresentados nesta prototipagem são demonstrativos.</p></div></section></main>;
}

function FAQPage({ onAskSusana }) {
  const [open, setOpen] = useState(null);
  return <main className="content page-content"><div className="page-heading"><p className="eyebrow">AJUDA</p><h1>Dúvidas frequentes</h1><p>Respostas rápidas para perguntas comuns. Para uma dúvida específica, use a Susana.</p></div><div className="faq-list">{FAQS.map(([q, a], index) => <article className={`faq-item ${open === index ? 'open' : ''}`} key={q}><button type="button" className="faq-question" aria-expanded={open === index} onClick={() => setOpen(open === index ? null : index)}><span>{q}</span><span className="faq-icon"><Icon name="chevron" size={17}/></span></button>{open === index && <div className="faq-answer"><p>{a}</p></div>}</article>)}</div><button className="faq-cta page-faq-cta" type="button" onClick={onAskSusana}>Ainda tenho uma dúvida <Icon name="arrow" size={18}/></button></main>;
}

function DetailModal({ detail, onClose }) {
  if (!detail) return null;
  return <div className="modal-backdrop" role="presentation" onMouseDown={onClose}><section className="detail-modal" role="dialog" aria-modal="true" aria-labelledby="detail-title" onMouseDown={(e) => e.stopPropagation()}><button type="button" className="modal-close" onClick={onClose} aria-label="Fechar"><Icon name="close" size={19}/></button><p className="eyebrow">MEU SUS DIGITAL</p><h2 id="detail-title">{detail.title}</h2><p>{detail.description}</p><div className="modal-note">Conteúdo demonstrativo do protótipo. No produto final, esta área poderá direcionar para o serviço correspondente.</div><button type="button" className="modal-primary" onClick={onClose}>Fechar</button></section></div>;
}

function Source({ source }) {
  const [open, setOpen] = useState(false);
  return <div className={`source ${open ? 'open' : ''}`}><button className="source-toggle" type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)}><span>Fonte</span><Icon name="chevron" size={14}/></button>{open && <div className="source-body"><strong>{source.label}</strong><span>{source.detail}</span><a href={source.url} target="_blank" rel="noreferrer">Abrir fonte oficial <Icon name="external" size={13}/></a></div>}</div>;
}

function TypingState({ label }) {
  return <div className="typing"><div className="msg-avatar"><img src={SUSANA_AVATAR} alt=""/></div><div className="typing-bubble"><span className="dot"/><span className="dot"/><span className="dot"/><span className="typing-label">{label}</span></div></div>;
}

function AssistantMessage({ message }) {
  if (message.role === 'user') return <div className="msg-row user"><div className="msg-content"><div className="bubble user-bubble">{message.text}</div><small>{message.time}</small></div></div>;
  return <div className="msg-row"><div className="msg-avatar"><img src={SUSANA_AVATAR} alt=""/></div><div className="msg-content"><div className="bubble bot-bubble">{message.text.split('\n').filter(Boolean).map((line, index) => <p key={index}>{line}</p>)}{message.source && <Source source={message.source}/>}</div><small>{message.time}</small></div></div>;
}

function createReply(text, context) {
  const normalized = text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const hasRA = /(ceil[aâ]ndia|samambaia|taguatinga|plano piloto|sobradinho|gama|guara|aguas claras|recanto das emas|planaltina|brazlandia|riacho fundo)/i.test(text);
  const ra = hasRA ? text.match(/(Ceil[aâ]ndia|Samambaia|Taguatinga|Plano Piloto|Sobradinho|Gama|Guar[aá]|Águas Claras|Recanto das Emas|Planaltina|Brazlândia|Riacho Fundo)/i)?.[0] : context.ra;
  const source = { label: 'Secretaria de Saúde do Distrito Federal', detail: 'Fonte oficial usada como referência no protótipo', url: 'https://info.saude.df.gov.br/' };

  if (/(diagnostico|qual doenca|o que eu tenho|dosagem|prescrev|tratamento)/.test(normalized)) {
    return { text: 'Posso ajudar com informações sobre serviços e acesso ao SUS, mas não faço diagnóstico nem prescrevo tratamentos. Posso ajudar você a encontrar o serviço adequado no Distrito Federal.', source, suggestions: ['Encontrar uma unidade de saúde', 'Informações sobre atendimento'] };
  }
  if (/(capital|futebol|filme|receita culinaria|programar|politica)/.test(normalized)) {
    return { text: 'Posso ajudar com informações relacionadas ao SUS e aos serviços públicos de saúde do Distrito Federal.', suggestions: ['Encontrar uma unidade de saúde', 'Informações sobre vacinação'] };
  }
  if (/vacina|vacinacao|imuniz/.test(normalized)) {
    if (!ra) return { text: 'Claro. Para localizar a informação correta, em qual Região Administrativa do Distrito Federal você está?', source, suggestions: ['Ceilândia', 'Samambaia', 'Taguatinga'] };
    return { text: `Entendi. Vou considerar ${ra} como contexto da nossa conversa. A informação disponível indica caminhos para vacinação pela rede de saúde do Distrito Federal.`, source, suggestions: ['Quero consultar meu histórico', 'Quero saber sobre vacina infantil'] };
  }
  if (/medic|remedio|farmacia/.test(normalized)) {
    if (!context.medicine && !/onde retirar|tenho receita/.test(normalized)) return { text: 'Claro. Para eu procurar a informação correta, qual é o nome do medicamento?', source, suggestions: ['Quero saber onde retirar', 'Tenho uma receita'] };
    if (/onde retirar|farmacia/.test(normalized) && context.medicine) return { text: `Certo. Vou considerar o medicamento ${context.medicine}. Posso orientar a busca por informações de assistência farmacêutica no DF.`, source, suggestions: ['Quero saber onde retirar', 'Preciso de outra informação'] };
    return { text: 'Entendi. Com o nome do medicamento consigo direcionar melhor a busca nas fontes disponíveis.', source, suggestions: ['Quero saber onde retirar', 'Tenho uma receita'] };
  }
  if (/consulta|agendar|agendamento|especialista|exame/.test(normalized)) {
    return { text: 'Posso orientar sobre o acesso a consultas e serviços especializados. Você quer saber como solicitar ou já possui um atendimento marcado?', source, suggestions: ['Quero solicitar uma consulta', 'Já tenho uma consulta marcada'] };
  }
  if (/ubs|unidade|posto|localizar|onde.*atend/.test(normalized)) {
    if (!ra) return { text: 'Posso ajudar a localizar uma unidade. Em qual Região Administrativa do Distrito Federal você está?', source, suggestions: ['Ceilândia', 'Samambaia', 'Taguatinga'] };
    return { text: `Certo. Vou considerar ${ra}. Posso ajudar a localizar uma unidade ou verificar um serviço disponível na região.`, source, suggestions: ['Quero vacinação', 'Quero saber os serviços da UBS'] };
  }
  if (hasRA) return { text: `Perfeito. Vou considerar ${ra} como contexto desta conversa. Agora me diga o que você precisa encontrar no SUS.`, source, suggestions: ['Vacinação', 'Medicamentos', 'Unidade de saúde'] };
  return { text: 'Posso ajudar com informações sobre serviços, unidades, vacinação, medicamentos, consultas e outros assuntos relacionados ao SUS no Distrito Federal. O que você precisa encontrar?', source, suggestions: QUICK_QUESTIONS };
}

function extractContext(text, context) {
  const next = { ...context };
  const normalized = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const raMatch = normalized.match(/(Ceilandia|Samambaia|Taguatinga|Plano Piloto|Sobradinho|Gama|Guara|Aguas Claras|Recanto das Emas|Planaltina|Brazlandia|Riacho Fundo)/i);
  if (raMatch) next.ra = raMatch[0];
  const medicineMatch = text.match(/(?:medicamento|remedio)\s+([\p{L}\d-]+)/iu);
  if (medicineMatch) next.medicine = medicineMatch[1];
  return next;
}

function Assistant({ open, setOpen }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(null);
  const [suggestions, setSuggestions] = useState(QUICK_QUESTIONS);
  const [context, setContext] = useState({});
  const messagesRef = useRef(null);
  const inputRef = useRef(null);
  const timers = useRef([]);

  const now = () => new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(new Date());
  const clearTimers = () => timers.current.splice(0).forEach((timer) => window.clearTimeout(timer));

  const startConversation = () => {
    clearTimers();
    setContext({});
    setTyping(null);
    setMessages([
      { role: 'bot', text: 'Olá! Eu sou a Susana. Posso ajudar você a encontrar informações sobre serviços e atendimento do SUS no Distrito Federal.', time: now() },
      { role: 'bot', text: 'Escreva sua dúvida do jeito que você falaria normalmente. Quando faltar alguma informação, eu pergunto para continuar a conversa.', time: now() },
    ]);
    setSuggestions(QUICK_QUESTIONS);
  };

  useEffect(() => { if (open && !messages.length) startConversation(); }, [open]);
  useEffect(() => { messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight, behavior: 'smooth' }); }, [messages, typing]);
  useEffect(() => { if (open) window.setTimeout(() => inputRef.current?.focus(), 180); }, [open]);
  useEffect(() => () => clearTimers(), []);

  const send = (raw) => {
    const text = raw.trim();
    if (!text || typing) return;
    const nextContext = extractContext(text, context);
    setContext(nextContext);
    setMessages((prev) => [...prev, { role: 'user', text, time: now() }]);
    setInput('');
    setSuggestions([]);
    setTyping('Entendendo sua pergunta');

    const reply = createReply(text, nextContext);
    clearTimers();
    timers.current.push(window.setTimeout(() => setTyping('Consultando informações'), 450));
    timers.current.push(window.setTimeout(() => setTyping('Preparando a resposta'), 950));
    timers.current.push(window.setTimeout(() => {
      setTyping(null);
      setMessages((prev) => [...prev, { role: 'bot', text: reply.text, time: now(), source: reply.source }]);
      setSuggestions(reply.suggestions || []);
    }, 1450));
  };

  const onKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      send(input);
    }
  };

  return <aside className={`assistant ${open ? 'is-open' : ''}`} aria-label="Assistente Susana">
    {open && <section className="assistant-panel" role="dialog" aria-modal="true" aria-labelledby="susana-title">
      <header className="assistant-header">
        <div className="assistant-identity"><img src={SUSANA_AVATAR} alt=""/><div><strong id="susana-title">Susana</strong><span>Assistente do SUS · Distrito Federal</span></div></div>
        <div className="assistant-actions"><button type="button" onClick={startConversation}>Nova conversa</button><button type="button" className="icon-only" aria-label="Fechar" onClick={() => setOpen(false)}><Icon name="close" size={18}/></button></div>
      </header>
      <div className="assistant-messages" ref={messagesRef} aria-live="polite" aria-busy={Boolean(typing)}>
        <div className="day-label">Hoje</div>
        {messages.map((message, index) => <AssistantMessage key={`${message.time}-${index}`} message={message}/>) }
        {typing && <TypingState label={typing}/>}
      </div>
      {suggestions.length > 0 && <div className="assistant-suggestions">{suggestions.map((item) => <button key={item} type="button" onClick={() => send(item)}>{item}</button>)}</div>}
      <div className="assistant-limit">A Susana não faz diagnósticos nem prescreve tratamentos. Em emergências, procure atendimento imediato.</div>
      <form className="composer" onSubmit={(event) => { event.preventDefault(); send(input); }}>
        <label className="sr-only" htmlFor="assistantInput">Mensagem para Susana</label>
        <textarea id="assistantInput" ref={inputRef} value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={onKeyDown} placeholder="Escreva sua dúvida…" rows="1" aria-describedby="assistantInputHelp"/>
        <span className="sr-only" id="assistantInputHelp">Pressione Enter para enviar. Use Shift mais Enter para quebrar a linha.</span>
        <button type="submit" disabled={!input.trim() || Boolean(typing)} aria-label="Enviar mensagem"><Icon name="send" size={18}/></button>
      </form>
    </section>}
    {!open && <div className="assistant-preview" aria-hidden="true"><div className="preview-row"><img src={SUSANA_AVATAR} alt=""/><div><strong>Susana</strong><span>Assistente do SUS</span></div></div><p>Estou aqui para ajudar com dúvidas específicas.</p></div>}
    <button className="assistant-toggle" type="button" aria-expanded={open} aria-label={open ? 'Fechar Susana' : 'Abrir Susana'} onClick={() => setOpen((value) => !value)}>{open ? <Icon name="close" size={23}/> : <img src={SUSANA_AVATAR} alt=""/>}</button>
  </aside>;
}

function App() {
  const [active, setActive] = useState('Início');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [detail, setDetail] = useState(null);
  const searchInputRef = useRef(null);

  const navigate = (label) => { setActive(label); setNotificationsOpen(false); };
  const askSusana = () => { setAssistantOpen(true); setNotificationsOpen(false); };

  useEffect(() => {
    const onKey = (event) => {
      if (event.key === 'Escape') {
        setMobileOpen(false);
        setNotificationsOpen(false);
        setDetail(null);
        setAssistantOpen(false);
        return;
      }
      if (event.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        event.preventDefault();
        document.querySelector('.search-bar input')?.focus();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    const onClick = (event) => {
      if (!event.target.closest('.notification-popover') && !event.target.closest('.top-icon')) setNotificationsOpen(false);
    };
    document.addEventListener('click', onClick);
    return () => document.removeEventListener('click', onClick);
  }, []);

  let view;
  if (active === 'Aplicações') view = <Applications onOpenDetail={(title, description) => setDetail({ title, description })}/>;
  else if (active === 'Minha saúde') view = <MyHealth onOpenDetail={(title, description) => setDetail({ title, description })}/>;
  else if (active === 'Conteúdos') view = <Contents/>;
  else if (active === 'Meu perfil') view = <Profile/>;
  else if (active === 'Dúvidas frequentes') view = <FAQPage onAskSusana={askSusana}/>;
  else view = <Home onAskSusana={askSusana} onNavigate={navigate} onOpenDetail={(title, description) => setDetail({ title, description })}/>;

  return <div className="app">
    <Sidebar active={active} onNavigate={navigate} open={mobileOpen} onClose={() => setMobileOpen(false)}/>
    <div className="main-shell">
      <Header onMenu={() => setMobileOpen(true)} onSearch={() => document.querySelector('.search-bar input')?.focus()} onNotifications={(event) => { event.stopPropagation(); setNotificationsOpen((value) => !value); }} notificationsOpen={notificationsOpen} onProfile={() => navigate('Meu perfil')}/>
      {view}
      <footer className="footer"><span>Meu SUS Digital · Protótipo de interface</span><span>Brasil · Distrito Federal</span></footer>
    </div>
    <Assistant open={assistantOpen} setOpen={setAssistantOpen}/>
    <DetailModal detail={detail} onClose={() => setDetail(null)}/>
  </div>;
}

createRoot(document.getElementById('root')).render(<App/>);
