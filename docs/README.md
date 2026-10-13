# Documentação técnica do Projeto Susana (SUS-DF)

Este conjunto de arquivos explica o projeto do começo ao fim: o que ele faz, como cada parte funciona por dentro e onde o código diverge do que os documentos antigos prometem. Tudo foi escrito a partir da leitura do código e de medições feitas com o projeto rodando em 13/10/2026.

## O projeto em um parágrafo

A **Susana** é uma assistente virtual **administrativa** da Secretaria de Saúde do DF. O cidadão pergunta em linguagem natural ("qual o telefone do Hospital de Taguatinga?") e recebe uma resposta escrita por um modelo de linguagem que roda **na própria máquina**, baseada **somente** em trechos de páginas oficiais, com a fonte citada. Perguntas clínicas (sintomas, remédios, doses) devem ser barradas antes de chegar ao modelo. A técnica central chama-se **RAG** (*Retrieval-Augmented Generation*, geração aumentada por recuperação).

## As duas metades do repositório

O repositório contém dois trabalhos que **não se conectam em tempo de execução**:

| Metade | O que é | Onde está |
|---|---|---|
| Assistente Susana | Chat web + API + RAG + MLOps | `susana-ui/`, `susana_rag_backend/` |
| Análise exploratória (EDA) | Estudo estatístico de bases abertas do SUS-DF | CSVs na raiz, `notebooks/`, scripts `.py` na raiz |

A EDA foi a primeira etapa (commit de 10/09/2026). A Susana veio depois (commit de 06/10/2026). Os arquivos `.parquet` gerados pela EDA são descritos como "para o RAG", mas o RAG não os lê.

## Ordem de leitura

| # | Arquivo | Responde a |
|---|---|---|
| 1 | [01-arquitetura.md](01-arquitetura.md) | Quais são as peças e como conversam? |
| 2 | [02-frontend.md](02-frontend.md) | Como a tela de chat funciona e recebe o texto aos poucos? |
| 3 | [03-backend-api.md](03-backend-api.md) | Como a API sobe, quais rotas existem, o que cada uma devolve? |
| 4 | [04-rag.md](04-rag.md) | Como um texto vira vetor, como a busca acha o trecho, como o LLM responde? |
| 5 | [05-guardrails.md](05-guardrails.md) | Como as perguntas clínicas são barradas? |
| 6 | [06-mlops.md](06-mlops.md) | Como modelos são treinados, avaliados, versionados e promovidos? |
| 7 | [07-dados-e-eda.md](07-dados-e-eda.md) | O que são os CSVs e as correlações? |
| 8 | [08-como-rodar-e-testar.md](08-como-rodar-e-testar.md) | Como subir tudo e rodar os testes? |
| 9 | [09-limitacoes-e-divergencias.md](09-limitacoes-e-divergencias.md) | O que não funciona como anunciado? |
| 10 | [10-perguntas-do-professor.md](10-perguntas-do-professor.md) | Perguntas prováveis, com resposta pronta |

O arquivo [analysis_process.md](analysis_process.md) já existia e registra os resultados da EDA.

Se o tempo for curto, leia 1, 4, 5, 9 e 10. O arquivo 9 é o mais importante para uma banca: um professor que abrir o código vai encontrar aqueles pontos, e é melhor você apresentá-los antes.

## Explicação de dois minutos

> "A Susana é um chatbot administrativo do SUS-DF. O frontend em Next.js envia a pergunta para uma API em FastAPI. A API primeiro passa a pergunta por um filtro de segurança, o guardrail, que é um classificador de regressão logística com TF-IDF: se a pergunta for clínica, ela é recusada. Se passar, a pergunta é convertida em um vetor de 384 dimensões por um modelo de embeddings multilíngue. Esse vetor é comparado, por distância de cosseno, com os vetores de 27 trechos de páginas oficiais guardados no ChromaDB, e os 3 mais próximos são recuperados. Esses trechos entram no prompt de um LLM local, o Llama 3.1 de 8 bilhões de parâmetros servido pelo Ollama, com a instrução de responder só com base neles. A resposta volta para a tela token a token, por streaming. Nada sai da máquina, o que atende à exigência de soberania de dados. O treino e o versionamento do classificador são rastreados no MLflow."

## Números reais deste projeto

Medidos em 13/10/2026 nesta máquina:

| Item | Valor |
|---|---|
| Trechos indexados no banco vetorial | 27 |
| Dimensão do vetor de embedding | 384 |
| Trechos recuperados por pergunta (k) | 3 |
| Limite de distância para aceitar um trecho | 1,2 (cosseno, escala de 0 a 2) |
| Modelo de linguagem | `llama3.1:8b`, quantização Q4_K_M, 4,9 GB |
| Exemplos no dataset do guardrail | 57 |
| F1 do guardrail registrado no MLflow | 0,571 |
| Limiar de bloqueio do guardrail | probabilidade > 0,65 |
| Testes automatizados | 14 (13 passam, 1 falha) |
| Latência de uma resposta completa (sem streaming) | cerca de 3,4 a 4,8 s em duas amostras |

## Glossário

| Termo | Significado |
|---|---|
| **LLM** | *Large Language Model*. Rede neural que prevê o próximo token de um texto. Aqui, o Llama 3.1. |
| **Token** | Pedaço de palavra que o modelo lê e gera. Uma palavra em português costuma virar de 1 a 3 tokens. |
| **RAG** | Buscar trechos relevantes em uma base e entregá-los ao LLM junto com a pergunta, para que ele responda com base neles e não na memória. |
| **Embedding** | Vetor numérico que representa o significado de um texto. Textos parecidos ficam próximos no espaço vetorial. |
| **Banco vetorial** | Banco que guarda vetores e responde "quais são os mais próximos deste?". Aqui, o ChromaDB. |
| **Distância de cosseno** | `1 − cosseno do ângulo` entre dois vetores. 0 significa mesma direção; 1, sem relação; 2, opostos. |
| **HNSW** | Índice em grafo que o ChromaDB usa para achar vizinhos próximos sem comparar com todos os vetores. |
| **Top-k** | Os k resultados mais próximos. Aqui k = 3. |
| **Alucinação** | Quando o LLM afirma algo que não está nas fontes. |
| **Grounding / fidelidade** | Grau em que a resposta se apoia nos trechos fornecidos. |
| **Guardrail** | Filtro de segurança que decide se uma pergunta pode ou não seguir para o LLM. |
| **TF-IDF** | Forma de transformar texto em números: peso alto para palavras frequentes no texto e raras no conjunto. |
| **Regressão logística** | Classificador linear que devolve uma probabilidade entre 0 e 1. |
| **Fallback extrativo** | Se o LLM falhar, devolver o trecho recuperado sem reescrevê-lo. |
| **Cache semântico** | Cache que reaproveita a resposta de uma pergunta anterior **parecida**, e não só idêntica. |
| **Streaming** | Enviar a resposta em pedaços, à medida que é gerada. |
| **NDJSON** | *Newline-Delimited JSON*: um objeto JSON por linha. Formato usado no streaming daqui. |
| **Arquitetura hexagonal** | O núcleo depende de interfaces (*ports*); implementações concretas (*adapters*) são plugadas de fora. |
| **MLflow** | Ferramenta que registra experimentos (parâmetros, métricas) e versões de modelos. |
| **Model Registry / alias** | Catálogo de versões de modelo do MLflow. O alias `@champion` aponta para a versão em uso. |
| **DVC** | Versionamento de dados, análogo ao git. Está previsto no projeto, mas não foi inicializado. |
| **ASGI / Uvicorn** | Padrão de servidor assíncrono em Python e o servidor que roda o FastAPI. |
| **CORS** | Regra do navegador que controla quais origens podem chamar uma API. |
