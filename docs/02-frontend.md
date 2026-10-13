# 2. Frontend (`susana-ui/`)

## 2.1 O que é

Uma aplicação **Next.js 16** com **React 19** e **TypeScript**, de uma única página. São três arquivos de código relevantes:

| Arquivo | Função |
|---|---|
| [src/app/layout.tsx](../susana-ui/src/app/layout.tsx) | Casca HTML: `lang="pt-BR"`, fonte Inter, título da aba |
| [src/app/page.tsx](../susana-ui/src/app/page.tsx) | Toda a lógica do chat |
| [src/components/Chat/MessageBubble.tsx](../susana-ui/src/components/Chat/MessageBubble.tsx) | Desenho de um balão e da citação de fonte |

O Next.js usa o **App Router**: a pasta `src/app/` define as rotas, e `page.tsx` na raiz dela é a rota `/`.

## 2.2 Componente de cliente

A primeira linha de `page.tsx` é `'use client'`. No App Router, os componentes são por padrão renderizados no servidor. Essa diretiva marca o componente como **de cliente**: ele é enviado ao navegador e roda lá, o que é obrigatório para usar `useState` e tratar eventos de teclado e clique.

Consequência prática: a chamada `fetch` para o backend parte **do navegador do usuário**, não do servidor Next.js. Por isso o backend precisa de CORS liberado, e por isso a URL `http://localhost:8000` só funciona quando o navegador está na mesma máquina do backend.

## 2.3 Estado

Três variáveis de estado controlam a tela:

| Estado | Tipo | Uso |
|---|---|---|
| `messages` | lista de `ChatMessage` | Histórico exibido. Começa com a saudação da Susana |
| `input` | texto | Conteúdo da caixa de digitação |
| `isLoading` | booleano | Mostra o "esqueleto" pulsante enquanto a resposta não começa |

Cada `ChatMessage` tem `text`, `isUser` e, opcionalmente, `isBlocked`, `isWarning` e `source`.

O histórico vive **só na memória do navegador**. Recarregar a página apaga a conversa. O backend também não guarda histórico: cada pergunta é independente e o LLM não vê as mensagens anteriores.

## 2.4 Envio da mensagem e leitura do streaming

A função `sendMessage` faz, em ordem:

1. Ignora entrada vazia.
2. Acrescenta a mensagem do usuário ao histórico e limpa a caixa.
3. Liga `isLoading` e acrescenta um **balão vazio** da assistente, que será preenchido aos poucos.
4. Faz `fetch` com `POST` para `http://localhost:8000/api/chat/stream`, enviando `{"message": "..."}`.
5. Obtém um leitor do corpo da resposta com `res.body.getReader()` e um `TextDecoder`.
6. Desliga `isLoading` e entra em um laço: lê bytes, decodifica, divide por quebra de linha e faz `JSON.parse` em cada linha.
7. Para cada objeto recebido:
   - `type: "chunk"` → concatena `content` ao texto acumulado e atualiza o último balão.
   - `type: "done"` → grava os metadados finais no último balão: `isBlocked`, `isWarning` e `source`.
8. Se o `fetch` lançar exceção (backend fora do ar), troca o último balão por "Desculpe, não consegui conectar aos servidores no momento."

### O formato na rede

A resposta é um fluxo de linhas, cada uma um JSON completo:

```
{"type": "chunk", "content": "O"}
{"type": "chunk", "content": " telefone"}
{"type": "chunk", "content": " é"}
...
{"type": "done", "source": "[UNIDADE] Hospitais Regionais (parte 1) — https://...", "is_blocked": false}
```

Esse formato chama-se **NDJSON** e o cabeçalho da resposta é `application/x-ndjson`. Alguns documentos do projeto chamam isso de "Server-Sent Events (SSE)". **Não é SSE.** SSE é um padrão específico (`text/event-stream`, linhas iniciadas por `data:`, consumido com `EventSource`). Aqui é uma resposta HTTP comum lida em pedaços com a API de *streams* do `fetch`.

### Por que fazer streaming

O LLM leva alguns segundos para escrever a resposta inteira. Com streaming, o usuário vê a primeira palavra assim que ela é gerada. A métrica associada é o **TTFT** (*time to first token*). O tempo total é o mesmo; o que melhora é a percepção de espera.

## 2.5 Regras visuais do balão

`MessageBubble` decide a aparência a partir de três sinais:

| Condição | Aparência | Quando acontece |
|---|---|---|
| `isUser` | Balão azul-claro à direita | Mensagem do cidadão |
| `isBlocked` | Borda vermelha + "Fora de Escopo / Não Clínico" | O guardrail barrou a pergunta |
| `isWarning` | Borda amarela + "Informação Ausente" | Não bloqueada, mas sem fonte |
| nenhuma | Balão branco + rodapé "Fonte Oficial: ..." | Resposta normal com fonte |

A regra do aviso amarelo está em `page.tsx`: `isWarning = !data.is_blocked && !data.source`.

A entrada de cada balão é animada com `framer-motion` (sobe 10 px e aparece em 0,3 s).

## 2.6 Acessibilidade

| Recurso | Onde | Efeito |
|---|---|---|
| `role="log"` e `aria-live="polite"` | Área de mensagens | Leitores de tela anunciam mensagens novas |
| `role="status"` e `aria-label="Carregando"` | Esqueleto | Anuncia a espera |
| `<label class="sr-only">` | Caixa de texto | Rótulo invisível, lido por leitor de tela |
| `aria-label="Enviar mensagem"` | Botão | Nome acessível |
| `lang="pt-BR"` | `<html>` | Pronúncia correta |
| Tecla Enter | Caixa de texto | Envia sem usar o mouse |

O banner amarelo fixo ("apenas informações administrativas e institucionais") funciona como aviso permanente de escopo.

## 2.7 Estilo

O Tailwind CSS 4 é ativado por `@import "tailwindcss"` em [globals.css](../susana-ui/src/app/globals.css). O mesmo arquivo define as cores do design system como variáveis CSS (`--susana-blue: #1A5699`, `--danger`, `--warning` etc.).

Há uma inconsistência: `MessageBubble.tsx` usa essas variáveis, mas `page.tsx` usa cores fixas diferentes (`#0284C7`, `#E0F2FE`). O azul do cabeçalho e o azul do avatar dentro do balão não são o mesmo.

## 2.8 Fragilidades do frontend

Pela leitura do código (não reproduzi cada uma no navegador):

| Ponto | Explicação | Correção típica |
|---|---|---|
| Linha JSON cortada entre dois pacotes | O código faz `split('\n')` em cada pacote recebido. Se um pacote terminar no meio de uma linha, o `JSON.parse` falha e aquele pedaço de texto é descartado | Manter um *buffer* com a sobra e só processar linhas completas |
| Sem verificação de `res.ok` | Se o backend responder 503 (pipeline iniciando) ou 422, o corpo é `{"detail": ...}`, que não tem `type`. Nada é exibido e o balão fica vazio | Checar `res.ok` antes de ler o corpo |
| URL do backend fixa | `http://localhost:8000` está escrito no código | Usar variável `NEXT_PUBLIC_API_URL` |
| Fonte nunca é clicável | O componente aceita `source.url`, mas `page.tsx` só preenche `source.title` com a string inteira | Separar título e URL no backend ou no frontend |
| Envios simultâneos | Não há bloqueio do botão durante a resposta; duas perguntas seguidas escrevem no "último balão" e podem se misturar | Desabilitar o envio enquanto houver resposta em curso |
| `key={i}` na lista | Índice como chave; aceitável aqui porque a lista só cresce | Usar um id por mensagem |

## 2.9 O aviso em `AGENTS.md`

O arquivo `susana-ui/AGENTS.md` é gerado pelo próprio `next dev` e avisa assistentes de IA de que esta versão do Next.js tem mudanças em relação às anteriores. Não afeta o funcionamento do sistema.
