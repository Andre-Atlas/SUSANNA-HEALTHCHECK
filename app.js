const messages = document.querySelector('#messages');
const input = document.querySelector('#question');
const form = document.querySelector('#chat-form');
const status = document.querySelector('#model-status');
const cancelButton = document.querySelector('#cancel');
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
  cancelButton.hidden = !busy;
  cancelButton.disabled = false;
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

const pause = ms => new Promise(resolve => setTimeout(resolve, ms));

function cancelRequest(request, reason = 'user') {
  if (!request) return;
  request.reason = reason;
  if (activeRequest === request && request.pending) {
    request.pending.content.textContent = 'Cancelando o pedido…';
    cancelButton.disabled = true;
  }
  request.controller.abort();
  if (request.id) {
    // keepalive permite enviar o cancelamento também ao sair/recarregar a página.
    fetch(`/api/jobs/${request.id}`, { method: 'DELETE', keepalive: true }).catch(() => {});
  }
}

async function showApprovedText(pending, text, request) {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const chunks = text.match(/.{1,100}(?:\s|$)|.{1,100}/gs) || [text];
  pending.content.textContent = '';
  for (const chunk of chunks) {
    request.controller.signal.throwIfAborted();
    if (activeRequest !== request) return;
    pending.content.textContent += chunk;
    messages.scrollTop = messages.scrollHeight;
    if (!reducedMotion) await pause(35);
  }
}

async function send(text) {
  const question = text.trim();
  if (!question || activeRequest || question.length > 3000) return;
  const request = { controller: new AbortController(), id: null, reason: null };
  activeRequest = request;
  const pendingHistory = [...history.slice(-12), { role: 'user', content: question }];
  addMessage(question, true);
  input.value = '';
  setBusy(true);
  const pending = addMessage('Enviando sua pergunta…');
  request.pending = pending;
  pending.bubble.setAttribute('aria-busy', 'true');
  const timer = setTimeout(() => cancelRequest(request, 'timeout'), 490000);
  try {
    // Não abortar a criação ao clicar Limpar: precisamos receber o ID para cancelá-lo.
    const response = await fetch('/api/jobs', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: pendingHistory }), signal: AbortSignal.timeout(10000),
    });
    let job = await response.json();
    if (!response.ok) throw new Error(job.error || 'Não foi possível enviar a pergunta.');
    request.id = job.id;
    if (request.controller.signal.aborted) {
      cancelRequest(request, request.reason);
      request.controller.signal.throwIfAborted();
    }
    const stages = {
      retrieval: 'Consultando as fontes locais…',
      generation: 'Preparando a resposta… O primeiro carregamento pode levar mais tempo.',
      review: 'Conferindo a resposta nas fontes antes de exibi-la…',
    };
    while (!['done', 'error', 'cancelled'].includes(job.state)) {
      request.controller.signal.throwIfAborted();
      if (activeRequest !== request) return;
      const progress = job.state === 'queued'
        ? `Aguardando na fila · posição ${job.queue_position || 1}`
        : stages[job.stage] || 'Processando sua pergunta…';
      pending.content.textContent = `${progress} (${Math.floor(job.elapsed_seconds || 0)} s)`;
      await pause(500);
      const poll = await fetch(`/api/jobs/${request.id}`, { signal: request.controller.signal });
      job = await poll.json();
      if (!poll.ok) throw new Error(job.error || 'Não foi possível acompanhar o pedido.');
    }
    if (job.state === 'error') throw new Error(job.error);
    if (job.state === 'cancelled') {
      throw new Error(job.cancel_reason === 'queue_timeout'
        ? 'O tempo de espera na fila terminou. Tente novamente.'
        : 'Pedido interrompido. Envie a pergunta novamente para continuar.');
    }
    const data = job.result;
    if (typeof data?.message !== 'string' || !data.message.trim()) throw new Error('Resposta vazia do servidor.');
    if (activeRequest !== request) return;
    // Apenas o resultado final aprovado (ou a mensagem segura de recusa) chega aqui.
    await showApprovedText(pending, data.message, request);
    request.controller.signal.throwIfAborted();
    addSources(pending.bubble, Array.isArray(data.sources) ? data.sources : []);
    history = [...pendingHistory, { role: 'assistant', content: data.message }];
    status.textContent = `Local · ${data.model} · ${job.elapsed_seconds} s`;
  } catch (error) {
    // Falha de rede também cancela a execução; a expiração cobre pedidos inacessíveis.
    if (!request.reason) cancelRequest(request, 'network_error');
    if (activeRequest !== request) return;
    pending.content.textContent = request.reason === 'user'
      ? 'Pedido cancelado.'
      : request.reason === 'timeout' ? 'O tempo de espera terminou. Tente novamente.'
      : error instanceof TypeError ? 'Sem conexão com o servidor. Execute python3 server.py.' : error.message;
    pending.bubble.classList.add('error');
    input.value = question;
  } finally {
    clearTimeout(timer);
    pending.bubble.removeAttribute('aria-busy');
    if (activeRequest === request) {
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
  cancelRequest(previous);
  history = [];
  messages.replaceChildren();
  input.value = '';
  setBusy(false);
  addMessage(welcome);
  input.focus();
  checkHealth();
});
cancelButton.addEventListener('click', () => cancelRequest(activeRequest));
window.addEventListener('pagehide', () => cancelRequest(activeRequest));
addMessage(welcome);
checkHealth();
