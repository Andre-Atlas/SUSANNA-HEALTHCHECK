# 8. MLOps — treino, benchmarks e MLflow

Tudo nesta seção roda **offline**, por comando manual. Nada aqui é executado quando o cidadão usa o chat, com uma exceção: o guardrail **carrega** o modelo que foi treinado aqui.

## MLflow: o que é e onde fica

O MLflow guarda o histórico de experimentos (parâmetros + métricas de cada execução) e um **registro de modelos** com versões e apelidos (*aliases*).

| Item | Local |
| --- | --- |
| Banco de metadados | `susana_rag_backend/mlflow.db` (SQLite) |
| Artefatos (modelos serializados) | `susana_rag_backend/mlruns/` |
| Interface web | `.venv/bin/mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001` → http://localhost:5001 |

Experimentos existentes:

| Experimento | Criado por | Conteúdo |
| --- | --- | --- |
| `susana-guardrails-train` | `ml/guardrails/train.py` | Um run por treino do guardrail |
| `susana-rag` | backend (as duas rotas) | Um run por pergunta (desfecho, latência, distância; sem o texto) |
| `susana-threshold-calibration` | `ml/retrieval/calibrate_threshold.py` | Um run por calibração do limiar de relevância |
| `susana-embeddings-benchmark` | `ml/retrieval/benchmark_embeddings.py` | 1ª execução em 08/10/2026 (veja o registro da demonstração) |
| `susana-llm-benchmark` | `ml/llm/benchmark_llms.py` | Ainda não executado nesta máquina |

`mlflow.db` e `mlruns/` estão no `.gitignore`. **Cada máquina precisa treinar o guardrail localmente**, senão o backend cai para o modo Regex.

---

## 1. Treino do guardrail — `ml/guardrails/train.py`

> Reescrito em 08/10/2026. Passo a passo da mudança em
> [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

```bash
cd susana_rag_backend && .venv/bin/python -m ml.guardrails.train
# código de saída 0 = gate aprovado e modelo promovido; 1 = reprovado (@champion não muda)
```

### O dataset — `data/guardrails_dataset.csv`

| Coluna | Valores |
| --- | --- |
| `text` | A pergunta |
| `label` | `1` = clínica, `0` = administrativa (formato do contrato) |
| `source` | `seed` (57 frases originais) ou `synthetic` (54 escritas em 08/10/2026 para cobrir casos difíceis) |

São 111 frases: 53 clínicas e 58 administrativas. O script **recusa** rótulos desconhecidos e frases duplicadas, o que evita repetir o bug antigo em que linhas `1`/`0` eram lidas como administrativas.

### Passo a passo

1. Carrega e valida o dataset.
2. **Validação cruzada estratificada de 5 partes, repetida 3 vezes** (sementes 0, 1, 2). Cada frase recebe uma probabilidade de um modelo que **não a viu** no treino.
3. Para cada frase, aplica a **decisão híbrida de produção** (`app.rag.guardrails.decide`: regras + ML), e não só o modelo. O gate mede o que vai ao ar.
4. Calcula a média das 3 repetições para:

| Métrica | O que mede | Gate |
| --- | --- | --- |
| `cv_hybrid_recall_clinical` | % das clínicas bloqueadas | ≥ 0,98 (contrato) |
| `cv_hybrid_precision_admin` | Das liberadas, % que eram mesmo administrativas | ≥ 0,95 (contrato) |
| `cv_hybrid_admin_allowed` | % das administrativas liberadas | ≥ 0,80 (**novo**) |

   Registra também as mesmas métricas para o ML isolado (`cv_ml_only_*`), para comparação.
5. Lista no log cada erro (clínica liberada / administrativa bloqueada), o que orienta a curadoria do dataset.
6. Treina o modelo final com **todas** as frases e registra uma nova versão de `susana-guardrail` no MLflow, com parâmetros, métricas e `gate_passed`.
7. **Só se as 3 métricas passarem**, aplica o alias `@champion` à nova versão. Se reprovar, a versão fica registrada mas a produção continua com o `@champion` anterior.

**Por que a terceira métrica?** As duas do contrato só penalizam perguntas clínicas liberadas. Um modelo que bloqueasse quase tudo passaria com nota máxima. Na prática, a configuração que parecia perfeita (1,000/1,000) bloqueava cerca de metade das perguntas administrativas.

### Modelo e calibração

- `TfidfVectorizer(analyzer="char_wb", ngram_range=(2,5), sublinear_tf=True)` → `LogisticRegression(class_weight="balanced", C=4)`.
- Comparamos n-gramas de caracteres × palavras × ambos, `C` ∈ {0,5; 1; 2; 4; 16} e limiar ∈ {0,35 … 0,5}. A combinação escolhida (caracteres, C=4, limiar **0,40**) foi a que passou nas três métricas com melhor equilíbrio.

### Histórico de versões

| Versão | Data | Recall clínico | Admin liberadas | Situação |
| --- | --- | --- | --- | --- |
| 1 | 08/10/2026 | 0,40 (split único) | — | Promovida sem gate (`f1 >= 0.0`) |
| 2 | 08/10/2026 | 0,887 | — | Reprovada |
| 3 | 08/10/2026 | 0,987 | 0,810 | Aprovada |
| **4** | 08/10/2026 | **0,987** | **0,828** | **`@champion`** (override "marcar um exame" corrigido) |

---

## 1b. Calibração do limiar de relevância — `ml/retrieval/calibrate_threshold.py`

```bash
cd susana_rag_backend && .venv/bin/python -m ml.retrieval.calibrate_threshold
# imprime SUGGESTED_SIMILARITY_THRESHOLD=0.74
```

1. Lê [threshold_set.jsonl](../susana_rag_backend/ml/retrieval/threshold_set.jsonl) (40 perguntas do tema, incluindo unidades, FAQ e medicamentos, + 20 de fora).
2. Monta um **índice Chroma temporário** com o corpus atual e roda **a mesma busca de produção** (híbrida, siglas expandidas); a aceitação usa `is_relevant` (menor distância entre os 3 trechos + exceção por unidade numerada).
3. Escolhe o limiar que aceita 100% das perguntas do tema e, entre esses, recusa mais perguntas de fora.
4. Lista os erros e registra tudo no experimento `susana-threshold-calibration`.

O valor sugerido **não é aplicado sozinho**: copie para `SIMILARITY_THRESHOLD` (no `.env` ou no padrão do `config.py`). Rode de novo sempre que o corpus mudar.

---

## 1c. Benchmark de recuperação por entidade — `ml/retrieval/benchmark_corpus.py` (da `develop_gui_sam`)

```bash
cd susana_rag_backend && .venv/bin/python -m ml.retrieval.benchmark_corpus
```

Gera perguntas automaticamente a partir dos diretórios de unidades (331 entidades) e do FAQ (41), indexa `CORPUS/Arquivos` num índice temporário e mede Recall@1/@3, perguntas fora do tema aceitas e latência. Resultado em 08/10/2026 (256 tokens): **Recall@1 0,946 / Recall@3 1,0** (entidades), **1,0 / 1,0** (FAQ), 1 de 12 fora do tema aceita, p95 de 137 ms. Foi usado para escolher `EMBEDDING_MAX_SEQ_LENGTH` (128 × 256 × 512).

---

## 2. Benchmark de embeddings — `ml/retrieval/benchmark_embeddings.py`

```bash
cd susana_rag_backend && .venv/bin/python -m ml.retrieval.benchmark_embeddings
```

Compara modelos de embedding para escolher o que melhor encontra o trecho certo.

1. Carrega o conjunto de avaliação [eval_set.jsonl](../susana_rag_backend/ml/retrieval/eval_set.jsonl): **6 perguntas**, cada uma com a tag esperada (ex.: `{"query": "Qual o horário do SAMU?", "expected_tag": "EMERGENCIA"}`).
2. Carrega só `data/corpus/sesdf_public.txt`.
3. Para cada candidato (`all-MiniLM-L6-v2` e `paraphrase-multilingual-MiniLM-L12-v2`):
   - indexa numa coleção separada (`bench_<modelo>`), sem afetar a coleção de produção;
   - para cada pergunta, busca top-3 e conta acerto se algum resultado tiver `[TAG esperada]` na fonte;
   - registra `hit_rate_top3` no MLflow.
4. Imprime `BENCHMARK_WINNER=<modelo>`.

O vencedor **não é aplicado automaticamente**: é preciso mudar `EMBEDDING_MODEL` no `.env`.

Limitações: 6 perguntas é pouco para uma decisão; acertar a **tag** é um critério frouxo (qualquer bloco `SERVICO` conta como acerto); o contrato pede `recall_at_3 ≥ 0,85` e latência p95, que o script não mede.

---

## 3. Benchmark de LLMs — `ml/llm/benchmark_llms.py`

```bash
cd susana_rag_backend && .venv/bin/python -m ml.llm.benchmark_llms
```

> ⚠️ Faz `ollama pull` de **6 modelos** (`qwen2.5:7b`, `llama3.1`, `mistral`, `phi3.5`, `qwen2.5:3b`, `gemma2`),
> o que soma até ~23 GB de download (os que já estiverem baixados são reaproveitados).

1. Carrega [benchmark_dataset.json](../susana_rag_backend/ml/llm/benchmark_dataset.json): cada item tem `question`, um `context` fixo (não usa a busca real), `expected_keywords` e `forbidden_keywords`.
2. Para cada modelo: faz o pull, aquece e responde todas as perguntas com timeout de 45 s.
3. Métricas por modelo, registradas no MLflow:

| Métrica | Como é calculada |
| --- | --- |
| `avg_latency_s` | Média do tempo de resposta completo |
| `avg_tps` | Tokens/segundo, estimando **1 token ≈ 4 caracteres** |
| `groundedness` | Começa em 1,0; perde até 0,5 por palavras esperadas ausentes; perde 0,5 por **cada** palavra proibida presente |
| `error_rate` | Fração de perguntas que deram erro |
| `pull_duration_s` | Tempo do download |

O "TTFT" (tempo até o primeiro token) citado nas notas de release **não é medido**: o script usa `generate()`, sem streaming. A `groundedness` por palavra-chave é uma aproximação grosseira. Por exemplo, uma resposta que diga "não vou falar de diagnóstico" é penalizada por conter "diagnóstico".

---

## 4. Notas de release vs. código

O [RELEASE_NOTES_MLOPS.md](../RELEASE_NOTES_MLOPS.md) e o [llm_evaluation_playbook.md](../llm_evaluation_playbook.md) descrevem algumas coisas como prontas que, no código, estão só projetadas:

| Afirmação | Situação no código |
| --- | --- |
| "Guardrail versão `v4` com alias `@champion`" | Hoje há de fato uma v4 `@champion`, treinada em 08/10/2026 com gate; antes dessa data não havia modelo registrado |
| "Semantic Cache… distância < 0.08" | Existe e, desde 08/10/2026, vale para as duas rotas |
| "Versionamento com DVC" | `dvc` está no requirements, mas não há `dvc.yaml` nem `.dvc/` no repositório |
| "Alerta se o corpus divergir > 20%" | Não implementado; o `manifest.json` só guarda o SHA-256 |
| "Shadow Deployment / re-treino por amostragem" | Não implementado |
| PDF de arquitetura: embedding `all-MiniLM-L6-v2` | O backend usa `paraphrase-multilingual-MiniLM-L12-v2` |
| "Benchmark validou TTFT" | O benchmark não mede TTFT |
