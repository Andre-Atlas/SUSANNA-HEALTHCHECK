"""Executa o JavaScript real com DOM/rede simulados no JavaScriptCore do macOS."""
import ctypes
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform == 'darwin', 'JavaScriptCore nativo disponível no macOS')
class FrontendTests(unittest.TestCase):
    def setUp(self):
        self.js = ctypes.CDLL('/System/Library/Frameworks/JavaScriptCore.framework/JavaScriptCore')
        ptr = ctypes.c_void_p
        functions = {
            'JSGlobalContextCreate': (ptr, [ptr]), 'JSGlobalContextRelease': (None, [ptr]),
            'JSStringCreateWithUTF8CString': (ptr, [ctypes.c_char_p]), 'JSStringRelease': (None, [ptr]),
            'JSEvaluateScript': (ptr, [ptr, ptr, ptr, ptr, ctypes.c_int, ctypes.POINTER(ptr)]),
            'JSValueToStringCopy': (ptr, [ptr, ptr, ctypes.POINTER(ptr)]),
            'JSStringGetMaximumUTF8CStringSize': (ctypes.c_size_t, [ptr]),
            'JSStringGetUTF8CString': (ctypes.c_size_t, [ptr, ctypes.c_void_p, ctypes.c_size_t]),
        }
        for name, (result, args) in functions.items():
            fn = getattr(self.js, name)
            fn.restype, fn.argtypes = result, args
        self.context = self.js.JSGlobalContextCreate(None)
        self.addCleanup(self.js.JSGlobalContextRelease, self.context)

    def evaluate(self, code):
        source = self.js.JSStringCreateWithUTF8CString(code.encode())
        error = ctypes.c_void_p()
        try:
            value = self.js.JSEvaluateScript(self.context, source, None, None, 1, ctypes.byref(error))
            string = self.js.JSValueToStringCopy(self.context, error.value or value, None)
            try:
                buffer = ctypes.create_string_buffer(self.js.JSStringGetMaximumUTF8CStringSize(string))
                self.js.JSStringGetUTF8CString(string, buffer, len(buffer))
                text = buffer.value.decode()
            finally:
                self.js.JSStringRelease(string)
            self.assertFalse(error.value, text)
            return text
        finally:
            self.js.JSStringRelease(source)

    def run_case(self, script):
        code = (ROOT / 'tests/frontend_harness.js').read_text() + '\n' + (ROOT / 'app.js').read_text()
        code += '\n(async () => {' + script + "\n})().then(() => globalThis.outcome = 'OK', e => globalThis.outcome = String(e));"
        self.evaluate(code)
        self.assertEqual(self.evaluate('globalThis.outcome'), 'OK')

    def test_progress_never_displays_draft_and_preserves_approved_text(self):
        self.run_case('''
          const approved = 'Resposta aprovada com acentuação. '.repeat(8) + '\\n\\nOutro parágrafo [1].';
          const states = ['generation', 'review', 'done'];
          route = async (url, options) => {
            if (options.method === 'POST') return response({id:'abc', state:'queued', queue_position:1});
            assert(!messages.children.at(-1).children[1].textContent.includes('Resposta aprovada'), 'Texto antes da validação');
            const stage = states.shift();
            return response(stage === 'done'
              ? {id:'abc', state:'done', elapsed_seconds:3, result:{message:approved, sources:[], model:'test'}}
              : {id:'abc', state:'running', stage});
          };
          await send('Pergunta de teste');
          assert(history.at(-1).content === approved, 'Histórico incorreto');
          assert(messages.children.at(-1).children[1].textContent === approved, 'Texto progressivo alterado');
          assert(!activeRequest && cancelButton.hidden && !input.disabled, 'Controles não liberados');
        ''')

    def test_clear_before_creation_response_cancels_old_job_without_overwriting_new(self):
        self.run_case('''
          let finishOld;
          route = async () => new Promise(resolve => {finishOld = resolve;});
          const old = send('Pergunta antiga');
          document.querySelector('#clear').listeners.click();
          route = async () => response({id:'new', state:'done', result:{message:'Nova resposta.', sources:[], model:'test'}});
          const fresh = send('Nova pergunta');
          finishOld(response({id:'old', state:'queued'}));
          await Promise.all([old, fresh]);
          assert(requests.some(item => item.url === '/api/jobs/old' && item.method === 'DELETE'), 'Pedido antigo não cancelado');
          assert(history.length === 2 && history[0].content === 'Nova pergunta', 'Histórico antigo reapareceu');
          assert(!messages.children.some(item => item.children[1]?.textContent === 'Pergunta antiga'), 'Mensagem antiga reapareceu');
        ''')

    def test_cancel_button_and_queue_full_restore_input(self):
        self.run_case('''
          route = async () => ({ok:false, json:async()=>({error:'Fila cheia.'})});
          await send('Tentar novamente');
          assert(input.value === 'Tentar novamente' && !input.disabled, 'Erro não restaurou campo');
          let finish;
          route = async () => new Promise(resolve => {finish = resolve;});
          const task = send('Cancelar agora');
          cancelButton.listeners.click();
          finish(response({id:'cancel', state:'queued'}));
          await task;
          assert(messages.children.at(-1).children[1].textContent === 'Pedido cancelado.', 'Cancelamento não exibido');
          assert(history.length === 0, 'Falha ou cancelamento entrou no histórico');
        ''')
