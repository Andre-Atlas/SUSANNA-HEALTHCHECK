# 3. Frontend — a tela do chat (`susana-ui/`)

## Tecnologias

| Pacote | Versão | Para que |
| --- | --- | --- |
| Next.js | 16.4 (App Router, Turbopack) | Servidor de desenvolvimento, roteamento e build |
| React | 19.3 | Componentes e estado |
| Tailwind CSS | 4 | Estilos via classes utilitárias |
| framer-motion | 13.5 | Animação de entrada dos balões |
| lucide-react | 1.53 | Ícones (`Info`, `ShieldAlert`, `AlertTriangle`) |
| TypeScript | 5.9 | Tipagem |

## Arquivos

```text
susana-ui/src/
├── app/
│   ├── layout.tsx       → HTML raiz: lang="pt-BR", fonte Inter, título da aba
│   ├── page.tsx         → A página do chat inteira (estado + streaming + layout)
│   └── globals.css      → Importa o Tailwind e define as cores da marca (variáveis CSS)
└── components/Chat/
    └── MessageBubble.tsx → Um balão de mensagem (+ citação de fonte)
```

A aplicação tem **uma única página** (`/`). Não há roteamento, login nem banco de dados no frontend. Todo o histórico vive na memória do navegador e se perde ao recarregar a página.

## `layout.tsx` — o esqueleto HTML

- Define `<html lang="pt-BR">`, importante para leitores de tela pronunciarem em português.
- Carrega a fonte **Inter** via `next/font/google` e a expõe como `--font-inter`.
- Define o título da aba: "Susana — Assistente de Saúde SUS-DF".

## `globals.css` — paleta

| Variável | Cor | Uso |
| --- | --- | --- |
| `--susana-blue` | `#1A5699` | Avatar "S", título "Fonte Oficial" |
| `--susana-blue-light` | `#EAF2F8` | Fundo do balão do usuário |
| `--susana-bg-alt` | `#F4F9FA` | Fundo da página |
| `--text` | `#2D3748` | Texto padrão |
| `--warning` | `#FFC107` | Borda/selo "Informação Ausente" |
| `--danger` | `#DC3545` | Borda/selo "Fora de Escopo" |

O `page.tsx` também usa algumas cores fixas no código (`#0284C7`, `#E0F2FE`, `#F8FAFC`) que não seguem essa paleta, então há dois tons de azul na tela.

## `page.tsx` — a lógica do chat

### Estado

```ts
messages: ChatMessage[]   // histórico; começa com a saudação da Susana
input: string             // texto da caixa de digitação
isLoading: boolean        // mostra o skeleton enquanto a resposta não começou
```

Cada `ChatMessage` tem:

```ts
{
  text: string;
  isUser: boolean;          // true = balão à direita, do cidadão
  isBlocked?: boolean;      // pergunta clínica bloqueada
  isWarning?: boolean;      // sem fonte / erro de conexão
  source?: { title: string; url?: string };
  citations?: { ref: number; title: string; url?: string | null }[];  // desde 08/10/2026
}
```

### Ciclo de `sendMessage()`

```text
1. input vazio? → não faz nada
2. adiciona balão do usuário
3. adiciona balão VAZIO da Susana (placeholder)
4. isLoading = true  → skeleton aparece
5. fetch POST http://localhost:8000/api/chat/stream
6. resposta chegou → isLoading = false
7. loop: lê pedaços do corpo
      decodifica bytes → texto
      divide por "\n", ignora linhas vazias
      cada linha → JSON.parse
         type "chunk" → acumula texto e reescreve o último balão
         type "done"  → grava isBlocked / isWarning / source no último balão
8. erro de rede → último balão vira mensagem de erro com borda amarela
```

O efeito de "digitando" vem do passo 7: a cada `chunk` o React re-renderiza o último balão com o texto acumulado.

### Regra de classificação visual (evento `done`)

| Condição no `done` | Resultado na tela |
| --- | --- |
| `status: "emergency"` | Fundo e borda vermelhos + "Possível emergência — ligue 192" (`role="alert"`) |
| `is_blocked: true` | Borda vermelha + "Fora de Escopo / Não Clínico" |
| `is_blocked: false` e sem `source` | Borda amarela + "Informação Ausente" |
| `citations` com itens | Rodapé "Fonte(s) Oficial(is):" com uma linha `[n] título` por citação, como **link** quando há URL |
| só `source` presente | Rodapé "Fonte Oficial: <source>" em texto (compatibilidade) |

Desde a integração com a `develop_gui_sam` (08/10/2026), o backend envia `citations` com título e URL separados, e o componente `CitationList` mostra cada fonte citada como link. Os diretórios de unidades (CSV) não têm URL e aparecem como texto, ex. "[CSV] Unidade Básica de Saúde (Unidade_Básica_de_Saúde.csv, registro 1)".

### Layout (de cima para baixo)

1. **Cabeçalho**: avatar "S", "Susana", "Assistente de Saúde SUS-DF".
2. **Faixa amarela de escopo**: "A Susana fornece apenas informações administrativas e institucionais. Não realiza diagnósticos ou avaliações clínicas."
3. **Área de mensagens**: `role="log"` e `aria-live="polite"`, para leitores de tela anunciarem mensagens novas.
4. **Caixa de texto + botão Enviar**: Enter também envia; o `<label>` é visível só para leitores de tela.

## `MessageBubble.tsx` — o balão

- Alinha à direita (usuário, avatar "U" cinza) ou à esquerda (Susana, avatar "S" azul).
- Anima a entrada (opacidade 0→1, sobe 10 px, 0,3 s) com `framer-motion`.
- Aplica a borda e o selo conforme `isBlocked` / `isWarning`.
- `whitespace-pre-wrap` preserva as quebras de linha que o LLM gera.
- `CitationList` desenha o rodapé com todas as citações (`[1]`, `[3]`…), como links quando há `url`.
- `SourceCitation` desenha o rodapé antigo (uma fonte), usado só se não vierem `citations`.

## Limitações conhecidas do frontend

Detalhes e prioridades em [10-problemas-conhecidos.md](10-problemas-conhecidos.md):

- URL do backend fixa no código (`http://localhost:8000`), sem variável de ambiente.
- Não verifica `res.ok`: um erro 503/422 do backend vira um balão vazio, sem mensagem.
- Uma linha JSON que chegue dividida entre dois pedaços de rede falha no `JSON.parse` e aquele trecho do texto é perdido (só aparece um `console.error`).
- O botão "Enviar" não é desabilitado durante a resposta; enviar de novo no meio do streaming mistura as atualizações dos balões.
- Sem rolagem automática para a última mensagem.
- Usa `key={i}` (índice) nos balões.
- O título das citações vem do cabeçalho do bloco (`[JSON] …`, `[CSV] …`) e ainda não está "limpo" para o cidadão.
