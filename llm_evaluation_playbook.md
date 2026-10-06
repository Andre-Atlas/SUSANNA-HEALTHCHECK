# Playbook de Avaliação e Observabilidade de LLMs (Susana)

Este documento mapeia como as 4 dimensões de observabilidade exigidas pelo framework `ml-adoption-playbook` e `mle-workflow` estão implementadas (ou projetadas) na arquitetura da Susana RAG.

## 1. Observabilidade de Dados e Modelo (Drift & Quality)

- **Data Drift (Desvio de Dados):**
  - *Como mitigamos:* O corpus da Secretaria de Saúde muda (ex: locais de vacinação mudam). O script `collect_corpus.py` roda de forma recorrente (cron) e gera um hash SHA-256 no `manifest.json`. O MLflow registrará versões de embeddings indexadas. Se o tamanho ou vocabulário do corpus divergir subitamente > 20%, um alerta é emitido para revisão humana.
- **Concept Drift (Desvio de Conceito):**
  - *Como mitigamos:* Monitoramos o comportamento dos usuários. Se os cidadãos começarem a usar gírias ou novas formas de pedir informações médicas que bypassam o limiar (`threshold = 0.65`) do Classificador de Guardrails, o F1-Score em produção cai. Usamos amostragem manual (Shadow Deployment) para re-treinar o classificador `scikit-learn`.
- **Model Decay (Degradação):**
  - *Como mitigamos:* Modelos menores (ex: `Llama 3.1 8B`) não "esquecem", pois seus pesos são congelados. A degradação vem do contexto injetado (Corpus obsoleto). O *Hit Rate @ Top-3* dos embeddings precisa ser re-avaliado via `ml/retrieval/benchmark_embeddings.py` a cada ciclo de atualização de RAG.
- **Integridade do Esquema (Schema Validation):**
  - *Como mitigamos:* Os Contratos do Backend FastAPI (`pydantic.BaseModel`) impõem `min_length=1` e `max_length=2000` em todo payload. Entradas corrompidas ou tipos errados disparam HTTP 422 *Unprocessable Entity* e são descartadas antes da inferência, protegendo a VRAM.

## 2. Observabilidade de Infraestrutura (Operacional)

- **Latência de Inferência (p50, p95, p99):**
  - *Como medimos:* Capturamos em `app/main.py` o Time-To-First-Token (TTFT) via `StreamingResponse` e logamos a latência total final no MLflow (`avg_latency_s`).
- **Throughput (Taxa de Transferência):**
  - *Como medimos:* RPS (Requisições por segundo). Se o tráfego exceder a capacidade de TPS local do Apple Silicon, o FastAPI enfileira as requisições. 
- **Saturação de Recursos:**
  - *Como medimos:* Em hardwares unificados (como Macs M-Series ou GPUs), rodar múltiplos LLMs estoira a VRAM. O Ollama gerencia o swap na CPU, causando picos de lentidão. Para evitar Out-Of-Memory (OOM), o `OllamaAdapter` usa a configuração `num_ctx=4096`.
- **Taxa de Erros:**
  - *Como medimos:* A exceção `LLMUnavailable` captura timeouts (> 45s). Isso rebaixa o sistema (Fallback) para exibir os dados textuais puros (Extrativo) sem quebrar o HTTP (retorna 200). A taxa de fallback é enviada ao MLflow.

## 3. Métricas de Pipeline de Dados e CI/CD

- **Duração do Pipeline (Lead Time):**
  - *Execução Automática:* O tempo desde rodar `collect_corpus.py`, até indexar no ChromaDB e reiniciar o Uvicorn (`lifespan`). Atualmente estimado em < 2 minutos.
- **Frequência de Deploy & Rollback:**
  - *Promotion Gates:* O script `ml/guardrails/train.py` usa o `MlflowClient` para promover o modelo com F1 > 0.85 (ou heurística similar) com a tag `@champion`. Para rollback instantâneo, basta reatribuir a tag `@champion` para a versão anterior no banco SQLite do MLflow, e o backend (ao recarregar) puxará o estável.
- **Taxa de Falha do Workflow:**
  - *Fail-fast:* Se o DVC não encontrar o CSV de treino, ou se a rede cair durante o `ollama pull`, o benchmark falha com saída limpa no CI, mantendo o modelo atual.

## 4. Métricas Específicas para LLMs (LLMOps)

- **Tokens por Segundo (TPS):**
  - Calculado heurísticamente no benchmark como: `(Tamanho da Resposta em Chars / 4) / Latência(s)`. Ajuda a escolher entre Qwen 3B (muito rápido) e Llama 3.1 8B.
- **Relevância do Contexto:**
  - Avaliado offline pelo `benchmark_embeddings.py` usando `Hit Rate @ Top-3` e `MRR`.
- **Fidelidade (Groundedness / Alucinação):**
  - Avaliado no `benchmark_llms.py`. Um score de 0.0 a 1.0 é gerado penalizando o modelo LLM caso ele (1) ignore as palavras-chave vitais do contexto recuperado, ou (2) alucine conselhos médicos (palavras "proibidas"). 
- **Custo de Inferência:**
  - Como não pagamos API, o custo = (Energia + CPU Time). Modelos de 3B parâmetros (como Phi-3.5 e Qwen 3B) reduzem o custo energético significativamente, mas dependem de manter um score alto de *Groundedness* para valer a pena.
