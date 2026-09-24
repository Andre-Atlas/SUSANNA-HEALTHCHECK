// DOM e rede simulados: testes de estado, sem substituir verificação visual.
class Element {
  constructor() { this.writes = []; this.textContent = ''; this.children = []; this.value = ''; this.listeners = {}; this.attrs = {}; this.classList = {add() {}}; this.submissions = 0; }
  set textContent(value) {this.text = value; this.children = []; this.writes?.push(value);}
  get textContent() {return this.text;}
  set innerHTML(value) {throw new Error('HTML não deve ser interpretado no chat');}
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  setAttribute(name, value) {this.attrs[name] = value;}
  removeAttribute(name) {delete this.attrs[name];}
  requestSubmit() {this.submissions++;}
  focus() {}
  addEventListener(name, fn) { this.listeners[name] = fn; }
  querySelectorAll() { return []; }
}
const elements = new Map();
globalThis.document = {
  querySelector(selector) {
    if (!elements.has(selector)) elements.set(selector, new Element());
    return elements.get(selector);
  },
  querySelectorAll() { return []; },
  createElement() { return new Element(); },
};
globalThis.window = {matchMedia() {return {matches: false};}, addEventListener() {}};
globalThis.setTimeout = (fn, ms) => {if (ms <= 500) Promise.resolve().then(fn); return 1;};
globalThis.clearTimeout = () => {};
globalThis.AbortController = class {
  constructor() {this.signal = {aborted: false, throwIfAborted() {if (this.aborted) throw new Error('abort');}};}
  abort() {this.signal.aborted = true;}
};
globalThis.AbortSignal = {timeout() {return {};}};
globalThis.URL = class {constructor(url) {this.href = url; this.protocol = url.split(':')[0] + ':';}};
let route = async () => {throw new Error('Unexpected request');};
const requests = [];
const response = data => ({ok: true, json: async () => data});
globalThis.fetch = async (url, options = {}) => {
  if (url === '/api/health') return response({ready: true, model: 'test'});
  requests.push({url, method: options.method || 'GET'});
  if (options.method === 'DELETE') return response({state: 'cancelled'});
  return route(url, options);
};
const assert = (condition, text) => {if (!condition) throw new Error(text);};
