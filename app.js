const messages = document.querySelector('#messages');
const input = document.querySelector('#question');
const form = document.querySelector('#chat-form');
const status = document.querySelector('#model-status');
const controls = [...form.querySelectorAll('button'), ...document.querySelectorAll('.suggestions button')];
const welcome = 'Olá! Sou o InspectorFakeNews. Posso ajudar a analisar uma mensagem e identificar o que precisa ser conferido. Consulto documentos locais cadastrados pela equipe, quando disponíveis, sem pesquisa na internet ao vivo. Posso cometer erros; uma resposta não equivale a uma checagem de fatos. Qual é sua dúvida?';
let history = [];
let activeRequest = null;

function addMessage(text, user = false) {
  const bubble = document.createElement('div');
  bubble.className = user ? 'bubble user' : 'bubble';
  const author = document.createElement('strong');
  author.textContent = user ? 'Você' : 'InspectorFakeNews · IA local';
  const content = document.createElement('span');
  content.textContent = text;
  bubble.append(author, content);
  messages.append(bubble);
  messages.scrollTop = messages.scrollHeight;
  return { bubble, content };
}

function setBusy(busy) {
  controls.forEach(button => { button.disabled = busy; });
  input.disabled = busy;
  form.setAttribute('aria-busy', String(busy));
}

function addSources(bubble, sources) {
  const section = document.createElement('div');
  section.className = 'sources';
  const heading = document.createElement('p');
  heading.textContent = sources.length
    ? 'Trechos fornecidos ao modelo — confira se sustentam a resposta:'
    : 'Nenhuma fonte local foi fornecida ao modelo para esta resposta.';
  section.append(heading);
  sources.forEach((source, index) => {
    const details = document.createElement('details');
    const summary = document.createElement('summary');
    summary.textContent = `[${index + 1}] ${source.title}`;
    const excerpt = document.createElement('p');
    excerpt.textContent = source.text;
    const link = document.createElement('a');
    const url = new URL(source.url);
    if (url.protocol !== 'https:') return;
    link.href = url.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = `Abrir fonte · consulta documental: ${source.reviewed_at}`;
    details.append(summary, excerpt, link);
    section.append(details);
  });
  bubble.append(section);
}

async function checkHealth() {
  try {
    const response = await fetch('/api/health', { signal: AbortSignal.timeout(6000) });
    const data = await response.json();
    status.textContent = data.ready ? `Local · ${data.model}` : data.message;
  } catch {
    status.textContent = 'Inicie python3 server.py e abra http://127.0.0.1:8002';
  }
}

async function send(text) {
  const question = text.trim();
  if (!question || activeRequest || question.length > 3000) return;
  const controller = new AbortController();
  activeRequest = controller;
  const pendingHistory = [...history.slice(-12), { role: 'user', content: question }];
  addMessage(question, true);
  input.value = '';
  setBusy(true);
  const pending = addMessage('Preparando resposta… O primeiro carregamento pode levar mais tempo.');
  const timer = setTimeout(() => controller.abort(), 190000);
  try {
    const response = await fetch('/api/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: pendingHistory }), signal: controller.signal,
    });
    let data;
    try { data = await response.json(); } catch { throw new Error('Abra o chat pelo servidor Python: http://127.0.0.1:8002.'); }
    if (!response.ok) throw new Error(data.error || 'Não foi possível gerar a resposta.');
    if (typeof data.message !== 'string' || !data.message.trim()) throw new Error('Resposta vazia do modelo.');
    if (activeRequest !== controller) return;
    pending.content.textContent = data.message;
    addSources(pending.bubble, Array.isArray(data.sources) ? data.sources : []);
    history = [...pendingHistory, { role: 'assistant', content: data.message }];
    status.textContent = `Local · ${data.model}`;
  } catch (error) {
    if (activeRequest !== controller) return;
    pending.content.textContent = error.name === 'AbortError'
      ? 'A resposta demorou demais. Tente novamente com uma mensagem menor.'
      : error instanceof TypeError ? 'Sem conexão com o servidor. Execute python3 server.py.' : error.message;
    pending.bubble.classList.add('error');
    input.value = question;
  } finally {
    clearTimeout(timer);
    if (activeRequest === controller) {
      activeRequest = null;
      setBusy(false);
      input.focus();
      messages.scrollTop = messages.scrollHeight;
    }
  }
}

form.addEventListener('submit', event => {
  event.preventDefault();
  send(input.value);
});
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    form.requestSubmit();
  }
});
document.querySelectorAll('.suggestions button').forEach(button => {
  button.addEventListener('click', () => send(button.textContent));
});
document.querySelector('#clear').addEventListener('click', () => {
  const previous = activeRequest;
  activeRequest = null;
  previous?.abort();
  history = [];
  messages.replaceChildren();
  input.value = '';
  setBusy(false);
  addMessage(welcome);
  input.focus();
  checkHealth();
});
addMessage(welcome);
checkHealth();
