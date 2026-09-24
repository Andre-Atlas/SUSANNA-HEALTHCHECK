// DOM e rede simulados: testes de estado, sem substituir verificação visual.
class Element {
  constructor() { this.textContent = ''; this.children = []; this.value = ''; this.listeners = {}; this.classList = {add() {}}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  setAttribute() {}
  removeAttribute() {}
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
