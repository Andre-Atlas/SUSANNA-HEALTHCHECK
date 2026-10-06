# 1. Visão geral

O SUSANNA-HEALTHCHECK é um protótipo educativo. A interface recebe uma pergunta, o servidor busca documentos em páginas oficiais gov.br, envia os trechos ao modelo local Ollama e submete a resposta a verificações de formato e uma revisão documental também feita pelo modelo.

## Componentes

| Componente | Função no chat local |
|---|---|
| Navegador | Exibe HTML/CSS e executa JavaScript para enviar e acompanhar pedidos. |
| `server.py` | Servidor HTTP local, validação de entrada e coordenação do fluxo. |
| `jobs.py` | Fila, concorrência, cancelamento e tempos por etapa. |
| `conversation.py` | Reconhece alguns acompanhamentos dependentes de contexto. |
| `govbr_search.py` | Consulta a busca gov.br/SERPRO e extrai páginas HTML gov.br. |
| Ollama | Executa localmente a geração e a revisão da resposta. |
| `answer_policy.py` | Verificações determinísticas de citações, estrutura e parecer recebido. |

O pipeline da conversa está resumido em [Fluxo completo](03-fluxo-completo-do-chat.md), e os processos opcionais estão em [Testes e avaliações](10-testes-e-avaliacoes.md), [Modo offline](09-fontes-sqlite-e-modos-offline.md) e [Demonstração externa](11-demonstracao-externa.md).

## O que significa “local” aqui

No uso local, a página e o backend rodam no computador, e o Ollama é acessado em `127.0.0.1:11434`. A busca é uma exceção importante: a pergunta reduzida a termos é enviada à API de busca SERPRO, e páginas encontradas são requisitadas em domínios HTTPS `gov.br`. Portanto, não é um sistema inteiramente sem rede.

## O que o sistema não garante

Domínio oficial não garante que a página encontrada responda à pergunta. A busca é limitada e lexical, e o revisor é uma segunda inferência do mesmo modelo, não um verificador humano independente. Respostas recusadas ou insuficientes podem refletir busca vazia, página irrelevante, citações inválidas ou reprovação do parecer.
