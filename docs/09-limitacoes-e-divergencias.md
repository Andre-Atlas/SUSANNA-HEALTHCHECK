# 9. Limitações e divergências entre os documentos e o código

Este arquivo reúne tudo o que **não funciona como os documentos do projeto afirmam**. Cada item foi verificado no código ou medido com o sistema rodando em 13/10/2026.

Por que estudar isto com atenção: um professor que abrir o repositório vai comparar o `RELEASE_NOTES_MLOPS.md` com o código. Apresentar os problemas por conta própria, com a causa e a correção, demonstra domínio. Ser pego afirmando algo que o código não faz, não.

Uma forma honesta de enquadrar: **o projeto é uma prova de conceito com a arquitetura certa e a execução incompleta.** A estrutura (RAG local, guardrail antes do LLM, fallback, registro de modelos) está correta. Vários componentes estão em versão inicial.

## 9.1 Segurança clínica (os mais graves)

| # | O que os documentos dizem | O que o código faz | Evidência |
|---|---|---|---|
| S1 | O guardrail é *fail-closed*; a regra é `regex OU probabilidade` | Com o modelo de ML carregado, as regex clínicas **não são consultadas** | `guardrails.py`, método `is_clinical`: retorna `False` logo após o ML |
| S2 | O classificador bloqueia perguntas clínicas | F1 de **0,571**; libera "Tenho dor no peito" (0,54) e "Me prescreva um remédio" (0,53) | MLflow e medições em [05](05-guardrails.md) |
| S3 | Dataset rotulado como clínico/administrativo | 7 exemplos clínicos com rótulo `1` são treinados como **administrativos** | `train.py`: `df["label"] == "CLINICAL"`; CSV com rótulos mistos |
| S4 | A liberação administrativa evita falsos positivos | Também serve de atalho: "Qual a dose de dipirona e onde fica a UBS?" passa | Regex `ADMINISTRATIVE_OVERRIDES` com prioridade absoluta |
| S5 | O guardrail também valida a **saída** do LLM | Não existe verificação de saída | Nenhuma chamada após a geração |
| S6 | Gate de promoção exige qualidade mínima | `if f1 >= 0.0`: **sempre aprova** | `train.py`, linha do *promotion gate* |
| S7 | Pergunta sem contexto relevante não chega ao LLM | O limiar de 1,2 nunca dispara; "bolo de chocolate" tem distância 1,004 | Medições em [04](04-rag.md) |

Efeito combinado observado: a pergunta "Estou sentindo muita febre e dor no corpo" **passou pelo guardrail**. Quem recusou foi o LLM, obedecendo ao prompt, e a tela exibiu a recusa como resposta normal, com a fonte "Dados Epidemiológicos - Doenças e Dengue". A segurança clínica, hoje, depende da obediência do modelo de linguagem.

## 9.2 Confiabilidade das fontes

| # | O que os documentos dizem | O que o código faz |
|---|---|---|
| F1 | Respostas vêm exclusivamente de fontes oficiais | 7 dos 27 blocos (`dados_abertos.txt`) são **texto simulado**, escrito dentro de `collect_opendata.py` |
| F2 | A citação aponta para a fonte oficial | As URLs `dados.df.gov.br/dataset/...` desses 7 blocos foram montadas com nomes fictícios |
| F3 | A fonte exibida é a usada na resposta | É sempre a do trecho mais próximo, mesmo quando o LLM usou outro ou recusou a pergunta |
| F4 | Pergunta fora do domínio gera aviso de "Informação Ausente" | Como o limiar não dispara, a tela mostra uma fonte sem relação (ex.: Ouvidoria para "bolo de chocolate") |
| F5 | O corpus cobre os serviços da SES-DF | Só 5 das 11 páginas listadas foram coletadas; não há página real sobre UBS, vacinação no DF ou Farmácia Popular |
| F6 | O embedding representa o bloco | 16 dos 27 blocos passam do limite de 128 tokens e são truncados no cálculo do vetor |
| F7 | O corpus é atualizado | Blocos antigos nunca são removidos do índice quando o texto muda |

## 9.3 O caminho que o usuário realmente usa

| # | O que os documentos dizem | O que o código faz |
|---|---|---|
| U1 | Cache semântico reduz latência | Só em `/api/chat`. A rota de streaming, usada pela tela, **não usa cache** |
| U2 | Cada pergunta é registrada no MLflow | Só em `/api/chat`. O streaming **não registra nada** |
| U3 | Streaming testado com mock | **Nenhum teste** cobre `/api/chat/stream`; não há mock no arquivo de testes |
| U4 | Frontend usa Server-Sent Events | É NDJSON sobre HTTP com `fetch`, não SSE |
| U5 | Frontend trata 503 sem quebrar | Sem verificação de `res.ok`: um 503 deixa o balão vazio (leitura do código) |
| U6 | — | Uma linha JSON cortada entre pacotes de rede é descartada, perdendo texto |

## 9.4 MLOps

| # | O que os documentos dizem | O que existe |
|---|---|---|
| M1 | Classificador `v4` com alias `@champion` | Neste `mlflow.db`: **versão 1** |
| M2 | Benchmark de Llama 3.1, Phi 3.5 e Qwen 2.5 realizado | Nenhuma run de benchmark de LLM ou de embeddings neste banco |
| M3 | Datasets versionados com DVC | **DVC não inicializado**: sem `.dvc/` e sem arquivos `*.dvc` |
| M4 | Telemetria nunca grava a pergunta | `pipeline.py` grava os primeiros 200 caracteres como parâmetro |
| M5 | Benchmark de embeddings com 4 candidatos e MRR | 2 candidatos, só *Hit Rate*, 6 perguntas |
| M6 | Benchmark de LLM mede fidelidade | Heurística de palavras-chave com 3 cenários |
| M7 | Dependências "pinned" | `requirements.txt` usa `>=`, que não fixa versão |
| M8 | — | `requirements.txt` lista `langchain`, `langchain-google-genai` e `redis`, que o código não importa, e omite `scikit-learn`, `pandas`, `pydantic-settings`, `beautifulsoup4`, `pyyaml` e `requests`, que o código importa |

Sobre M1 e M2: o `mlflow.db` não é versionado. Os resultados citados nas notas podem existir em outra cópia. O que se pode afirmar é que **não estão neste repositório nem neste banco**.

Sobre M8: o ambiente virtual atual funciona porque esses pacotes vieram como dependências indiretas ou foram instalados à parte. Uma instalação limpa só com o `requirements.txt` pode falhar.

## 9.5 Arquitetura e código

| # | O que os documentos dizem | O que o código faz |
|---|---|---|
| A1 | Arquitetura hexagonal com ports para LLM, guardrail e retriever | Só o LLM tem port implementada. `IntentClassifierPort` está declarada e sem uso |
| A2 | Rotas assíncronas | `async def` com chamadas bloqueantes: uma pergunta trava o servidor para as demais |
| A3 | — | Lógica de RAG duplicada entre `pipeline.py` e `routers_stream.py`, com comportamentos diferentes |
| A4 | — | Importação circular entre `main.py` e `routers_stream.py` |
| A5 | — | `settings.top_k` nunca é lido; `k=3` está fixo em dois lugares |
| A6 | — | `if True:` na indexação: código de depuração que ficou |
| A7 | 100% local, sem chamadas externas | Na subida, `sentence-transformers` consulta o `huggingface.co` |
| A8 | PDF de visão geral: embedding `all-MiniLM-L6-v2` | O código usa `paraphrase-multilingual-MiniLM-L12-v2` |
| A9 | Latência esperada < 1,5 s após warm-up | Medido: 3,4 a 4,8 s para a resposta completa |
| A10 | API devolve 400 para pergunta clínica | Devolve 200 com `is_blocked: true` |

## 9.6 Requisitos de produção ausentes

Esperados em uma prova de conceito, mas necessários antes de uso real:

- Sem autenticação, autorização ou limite de requisições.
- CORS aberto para qualquer origem.
- Cache e estado em memória de um único processo: não escala horizontalmente.
- Sem histórico de conversa: cada pergunta é isolada.
- Sem contêiner, sem pipeline de CI/CD, sem deploy automatizado.
- Sem política de retenção ou anonimização dos registros.
- URL do backend fixa no frontend.

## 9.7 Análise de dados

| # | Ponto |
|---|---|
| D1 | Correlações calculadas sobre 12 pontos; p-valores calculados e não reportados |
| D2 | O Spearman de 0,294 (SAMU × óbitos) não é significativamente diferente de zero |
| D3 | Região do SAMU inferida por fragmentos de texto, sujeita a erros |
| D4 | Óbitos por residência × SAMU por localização da base: geografias diferentes |
| D5 | Parquets "para o RAG" não são lidos pelo RAG |

## 9.8 Ordem sugerida de correção

Se perguntarem "o que você faria primeiro?":

| Prioridade | Ação | Resolve | Esforço |
|---|---|---|---|
| 1 | Guardrail com regra `regex OU ML`, sem prioridade absoluta da liberação administrativa | S1, S4 | Poucas linhas |
| 2 | Padronizar rótulos do dataset e retreinar | S3 | Poucas linhas |
| 3 | Gate real de promoção, por *recall* clínico | S6 | Poucas linhas |
| 4 | Baixar o limiar de distância para cerca de 0,65 | S7, F4 | Uma linha de configuração |
| 5 | Retirar ou rotular os blocos simulados | F1, F2 | Remover um arquivo |
| 6 | Fazer a rota de streaming usar o `RAGPipeline` (cache, telemetria, uma só lógica) | U1, U2, A3 | Médio |
| 7 | Ampliar o dataset do guardrail para centenas de exemplos | S2 | Trabalho de dados |
| 8 | Reduzir o tamanho dos blocos para caber em 128 tokens | F6 | Recoleta e reindexação |
| 9 | Testes unitários com LLM falso e teste da rota de streaming | U3 | Médio |
| 10 | Registrar hash da pergunta em vez do texto | M4 | Poucas linhas |

As quatro primeiras são pequenas e atacam diretamente o risco clínico. Esse é o argumento: os defeitos mais graves são baratos de corrigir porque a arquitetura está certa.
