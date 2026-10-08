# Documentação do Projeto Susana (SUS-DF)

A **Susana** é uma assistente virtual **administrativa** da Secretaria de Saúde do Distrito Federal. Ela responde perguntas como "onde fica a UBS?", "como retiro remédio na Farmácia de Alto Custo?" ou "qual o telefone do SAMU?", usando **somente** trechos de documentos oficiais, e se recusa a dar orientação clínica (diagnóstico, remédio, dose).

Tudo roda localmente: o modelo de linguagem (LLM) roda no Ollama, a busca vetorial no ChromaDB e o registro de experimentos no MLflow. Nenhuma pergunta é enviada para APIs externas.

## Mapa do repositório

```text
SUSANNA-HEALTHCHECK/
├── susana-ui/                 → Frontend (Next.js + React): a tela do chat
├── susana_rag_backend/        → Backend (FastAPI): guardrail + busca + LLM
│   ├── app/                   → código que roda no servidor
│   │   ├── main.py            → cria a API, inicializa tudo no startup
│   │   ├── routers_stream.py  → rota /api/chat/stream (usada pelo frontend)
│   │   ├── config.py          → configurações (lidas do .env)
│   │   ├── ports.py           → interfaces (contratos) entre as peças
│   │   ├── llm/               → conversa com o Ollama + prompt
│   │   └── rag/               → corpus, embeddings, busca, cache, guardrail
│   ├── ml/                    → scripts offline: coleta, treino, calibração, benchmarks, avaliação do chat
│   ├── data/                  → corpus de texto, dataset do guardrail, ChromaDB
│   └── tests/                 → testes pytest
├── notebooks/ + *.py (raiz)   → análise exploratória dos dados abertos (EDA)
├── Samu/, obitos-.../, ...    → CSVs brutos de dados abertos do SUS-DF
├── openspec/                  → propostas, decisões de design e contratos
└── docs/                      → esta documentação (+ registro/, avaliacoes/, PROXIMOS-PASSOS.md)
```

## Os documentos

Leia na ordem, se for a primeira vez:

| # | Documento | O que explica |
| --- | --- | --- |
| 1 | [01-como-rodar.md](01-como-rodar.md) | Instalar, configurar e subir os três serviços (Ollama, backend, frontend) |
| 2 | [02-fluxo-de-uma-pergunta.md](02-fluxo-de-uma-pergunta.md) | **O documento central.** Passo a passo do que acontece desde o clique em "Enviar" até a resposta aparecer na tela |
| 3 | [03-frontend.md](03-frontend.md) | A tela do chat: estado, leitura do streaming, balões, cores de alerta |
| 4 | [04-backend-api.md](04-backend-api.md) | FastAPI: inicialização (lifespan), rotas, configuração, arquitetura hexagonal |
| 5 | [05-guardrails.md](05-guardrails.md) | Como a Susana decide que uma pergunta é clínica e a bloqueia |
| 6 | [06-corpus-e-indexacao.md](06-corpus-e-indexacao.md) | De onde vêm os textos oficiais, como viram blocos e vetores no ChromaDB |
| 7 | [07-busca-e-geracao.md](07-busca-e-geracao.md) | Busca vetorial, limiar de relevância, cache semântico, prompt e LLM |
| 8 | [08-mlops.md](08-mlops.md) | MLflow, treino do guardrail, benchmarks de embeddings e de LLMs |
| 9 | [09-analise-de-dados.md](09-analise-de-dados.md) | A parte de ciência de dados: CSVs, notebook, correlações, parquet |
| 10 | [10-problemas-conhecidos.md](10-problemas-conhecidos.md) | Problemas resolvidos e em aberto, com prioridade |
| 11 | [11-avaliacao-do-chat.md](11-avaliacao-do-chat.md) | Gerador de perguntas de teste e relatório automático de qualidade |

## Acompanhamento do projeto

| Onde | O que tem |
| --- | --- |
| [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md) | **O que fazer a seguir**, em ordem. É atualizado a cada rodada de trabalho |
| [registro/](registro/) | Diário passo a passo de tudo o que foi feito, um arquivo por rodada |
| [avaliacoes/](avaliacoes/) | Relatórios do avaliador do chat (histórico de qualidade) |

O documento [analysis_process.md](analysis_process.md), que já existia, traz os resultados numéricos da análise de correlação e continua válido. O [09-analise-de-dados.md](09-analise-de-dados.md) explica o código que gerou esses resultados.

## Visão de 30 segundos

```text
 Navegador (localhost:3000)
   │  POST /api/chat/stream  {"message": "..."}
   ▼
 FastAPI (localhost:8000)
   │
   ├─ 1. Guardrail ── é pergunta clínica? (regras + ML) ──► SIM → "não posso ajudar; procure UBS / SAMU 192" (fim)
   │                                                 NÃO ↓
   ├─ 2. Embedding ── expande siglas (UBS, SAMU...) e transforma a pergunta num vetor de 384 números
   ├─ 3. Cache ────── pergunta quase idêntica respondida há pouco? → devolve a mesma resposta (fim)
   ├─ 4. ChromaDB ─── acha os 3 trechos oficiais mais parecidos (52 blocos de saude.df.gov.br)
   │                  nenhum perto o bastante (distância > 0,70)? → "não encontrei" (fim)
   ├─ 5. Ollama ───── LLM (llama3.1:8b) escreve a resposta usando só esses 3 trechos
   │                  token a token; a fonte exibida é o trecho que ele citou
   ▼
 Resposta em streaming (NDJSON) → o frontend vai montando o texto na tela
                                   e mostra a "Fonte Oficial" no final
```
