# 6. MLOps: treino, avaliação e versionamento

**MLOps** é o conjunto de práticas para tratar modelos de aprendizado de máquina como software de produção: saber qual versão está no ar, com que dados foi treinada, que métricas atingiu, e poder voltar atrás.

Tudo desta seção fica em `susana_rag_backend/ml/` e são **scripts offline**: rodam quando alguém os executa, não junto com a API.

## 6.1 MLflow

O projeto usa três partes do MLflow:

| Parte | O que guarda | Uso no projeto |
|---|---|---|
| **Tracking** | Experimentos e *runs*: parâmetros, métricas, artefatos | Treino do guardrail, benchmarks, registro de cada pergunta |
| **Model Registry** | Versões numeradas de um modelo nomeado | Modelo `susana-guardrail` |
| **Aliases** | Um apelido que aponta para uma versão | `@champion` |

Vocabulário:

- **Experimento**: uma pasta lógica, como `susana-guardrails-train`.
- **Run**: uma execução dentro de um experimento, com seus parâmetros e métricas.
- **Artefato**: arquivo produzido pela run, como o modelo serializado.

O armazenamento é local: os metadados ficam em `mlflow.db` (SQLite) e os artefatos em `mlruns/`. Não há servidor. A interface web (`mlflow ui`) só lê esses arquivos.

### Estado atual do banco

Consultado em 13/10/2026:

| Experimento | Runs | Observação |
|---|---|---|
| `susana-guardrails-train` | 1 | F1 = 0,571 |
| `susana-rag` | 10 | Perguntas feitas pela suíte de testes que rodei hoje |
| `susana-llm-benchmark` | não existe | O benchmark de LLMs não foi executado neste banco |
| `susana-embeddings-benchmark` | não existe | O benchmark de embeddings não foi executado neste banco |

Modelo registrado: `susana-guardrail`, **versão 1**, com alias `champion`.

O arquivo `RELEASE_NOTES_MLOPS.md` fala em versão `v4` como campeã e em benchmark de Llama 3.1, Phi 3.5 e Qwen 2.5. **Esses registros não estão neste `mlflow.db`.** O arquivo é ignorado pelo git, então cada cópia do projeto tem o seu; os resultados citados podem ter sido gerados em outra máquina ou outra pasta. Diante de uma banca, o que você consegue mostrar é o que está na tabela acima.

## 6.2 Treino do guardrail ([train.py](../susana_rag_backend/ml/guardrails/train.py))

Passo a passo do script:

1. Configura o MLflow e o experimento `susana-guardrails-train`.
2. Lê `data/guardrails_dataset.csv` (57 linhas).
3. Cria a coluna-alvo: 1 se o rótulo for `"CLINICAL"`, senão 0. É aqui que 7 exemplos clínicos rotulados como `1` viram administrativos ([05](05-guardrails.md), problema 2).
4. Divide em treino e teste: 75% / 25%, estratificado, semente 42. Com 57 linhas, são **42 para treino e 15 para teste**.
5. Treina o pipeline TF-IDF + regressão logística.
6. Calcula o **F1** no teste.
7. Registra no MLflow os parâmetros, a métrica e o modelo, sob o nome `susana-guardrail`. Cada execução cria uma **nova versão**.
8. Aplica o *promotion gate* e, se aprovado, move o alias `@champion` para a versão nova.

### Conceitos do passo 4

- **Divisão treino/teste**: o modelo aprende com uma parte e é avaliado em outra que nunca viu. Avaliar nos dados de treino mediria memorização, não generalização.
- **Estratificado**: mantém a mesma proporção de classes nos dois conjuntos.
- **Semente fixa**: a divisão é sempre a mesma, o que torna o experimento reprodutível.

### A métrica F1

| | Previsto: clínica | Previsto: administrativa |
|---|---|---|
| **Real: clínica** | Verdadeiro positivo (VP) | Falso negativo (FN) |
| **Real: administrativa** | Falso positivo (FP) | Verdadeiro negativo (VN) |

```
Precisão = VP / (VP + FP)     das que bloqueei, quantas eram clínicas?
Recall   = VP / (VP + FN)     das clínicas, quantas bloqueei?
F1       = 2 × Precisão × Recall / (Precisão + Recall)
```

O F1 é a média harmônica de precisão e *recall*. Um F1 de 0,571 medido em 15 exemplos tem altíssima incerteza: um único exemplo a mais ou a menos muda o resultado em vários pontos.

Para um filtro de segurança, o **falso negativo** (pergunta clínica que passa) é muito mais grave que o falso positivo (pergunta administrativa recusada). Por isso o contrato do projeto define o gate em *recall* clínico ≥ 0,98, e não em F1.

### O *promotion gate* que não barra nada

Um *promotion gate* é uma condição mínima de qualidade para um modelo novo assumir a produção. No código:

```python
if f1 >= 0.0:
    # promove para @champion
```

F1 nunca é negativo, então a condição é **sempre verdadeira**. Qualquer modelo treinado, por pior que seja, vira `@champion`. As specs falam em precisão ≥ 0,90, e o playbook em F1 > 0,85; o modelo atual, com 0,571, não passaria em nenhum dos dois.

### Como o alias permite *rollback*

O backend carrega `models:/susana-guardrail@champion`. Ele não sabe o número da versão, só o alias. Para voltar a uma versão anterior, basta reapontar o alias no MLflow e reiniciar o backend. Nenhuma linha de código muda. Esse é o valor real do mecanismo, e ele está implementado corretamente.

## 6.3 Benchmark de embeddings ([benchmark_embeddings.py](../susana_rag_backend/ml/retrieval/benchmark_embeddings.py))

Objetivo: escolher o modelo de embeddings com base em medição, e não em opinião.

| Aspecto | Como é feito |
|---|---|
| Candidatos | `all-MiniLM-L6-v2` e `paraphrase-multilingual-MiniLM-L12-v2` |
| Conjunto de avaliação | `eval_set.jsonl`: **6 perguntas**, cada uma com a etiqueta esperada |
| Corpus | Só `sesdf_public.txt` |
| Métrica | *Hit Rate* no top-3 |
| Saída | Uma run por modelo no MLflow e `BENCHMARK_WINNER=<modelo>` |

***Hit Rate* no top-3**: fração das perguntas em que pelo menos um dos 3 trechos recuperados é "certo". Aqui, "certo" significa **ter a etiqueta esperada** (por exemplo, `SERVICO`).

Fragilidades:

- 6 perguntas é uma amostra pequena demais: cada pergunta vale 16,7 pontos percentuais.
- O critério por etiqueta é frouxo. A pergunta "Como retirar o cartão do SUS?" espera `SERVICO`, e os blocos de Farmácia de Alto Custo também são `SERVICO`: recuperar a farmácia conta como acerto, embora não responda à pergunta.
- O design cita quatro candidatos (incluindo `multilingual-e5-small` e `bge-m3`); o script testa dois.
- O playbook cita a métrica MRR; ela não está implementada.

Um detalhe bem pensado: o script usa o prefixo de coleção `bench`, então os vetores do benchmark não se misturam com os de produção.

## 6.4 Benchmark de LLMs ([benchmark_llms.py](../susana_rag_backend/ml/llm/benchmark_llms.py))

Objetivo: comparar modelos de linguagem em velocidade e fidelidade.

| Aspecto | Como é feito |
|---|---|
| Candidatos | `qwen2.5:7b`, `llama3.1`, `mistral`, `phi3.5`, `qwen2.5:3b`, `gemma2` |
| Cenários | `benchmark_dataset.json`: **3** perguntas, cada uma com contexto, palavras esperadas e palavras proibidas |
| Para cada modelo | `ollama pull`, *warm-up*, e as 3 perguntas |
| Métricas | Latência média, TPS médio, fidelidade média, taxa de erro |

**TPS (tokens por segundo)** é estimado como `(caracteres da resposta ÷ 4) ÷ segundos`. É uma aproximação: o Ollama devolve a contagem real de tokens (`eval_count`), que o script não usa.

**Fidelidade (*groundedness*)** começa em 1,0 e sofre descontos:

- Para cada palavra esperada ausente da resposta: desconta `0,5 ÷ número de esperadas`.
- Para cada palavra proibida presente: desconta 0,5.

É uma heurística de palavras-chave. Ela não mede se a resposta é verdadeira; mede se certas palavras aparecem. Uma resposta que diga "não tome xarope" seria punida por conter "xarope". Avaliações mais robustas usam um segundo LLM como juiz ou revisão humana.

Com 3 cenários, o resultado indica uma tendência, não uma conclusão. E o script baixa seis modelos de vários gigabytes cada: executá-lo consome dezenas de GB de disco e bastante tempo.

## 6.5 Telemetria das perguntas

`RAGPipeline.query` abre uma run chamada `query` no experimento `susana-rag` a cada pergunta, com:

| Registro | Tipo |
|---|---|
| `query` (até 200 caracteres) | parâmetro |
| `llm_used` | parâmetro |
| `source` | parâmetro |
| `latency_s` | métrica |
| `llm_latency_ms` | métrica |
| `top_distance` | métrica |

Duas amostras reais do banco:

| Pergunta | Latência total | Latência do LLM | Distância |
|---|---|---|---|
| "Horário da UBS" | 3,45 s | 3,43 s | 0,486 |
| "Endereço da UBS 1 Asa Sul" | 4,81 s | 4,75 s | 0,443 |

Leitura: **quase todo o tempo é do LLM**. Embedding e busca vetorial somam poucos centésimos de segundo. Qualquer otimização de latência tem de mirar a geração (modelo menor, menos tokens, cache).

Ressalvas:

- Só a rota `/api/chat` registra. A rota de streaming, usada pela tela, não.
- Perguntas bloqueadas e acertos de cache não são registrados.
- O texto da pergunta é gravado, contrariando o contrato do projeto.
- Usar o MLflow para registrar cada requisição é um improviso: ele foi feito para experimentos, e uma run por pergunta não escala. O adequado seria um sistema de observabilidade.

## 6.6 DVC

O **DVC** (*Data Version Control*) versiona arquivos de dados grandes fora do git, guardando no git apenas um ponteiro com o hash. A proposta era que cada versão de modelo no MLflow pudesse ser ligada à versão exata do dataset que a gerou.

Situação real: o pacote `dvc` está instalado e listado em `requirements.txt`, e o `.gitignore` cita `dvc-storage/`. Mas **o DVC não foi inicializado**: não existe pasta `.dvc/` nem arquivos `*.dvc` no repositório. O dataset do guardrail e o corpus estão versionados diretamente no git.

O arquivo `tasks.md` marca "Inicializar o DVC" como concluído. Não está.

## 6.7 Observabilidade: plano e realidade

O `llm_evaluation_playbook.md` descreve quatro dimensões de monitoramento. Comparando com o código:

| Item do playbook | Situação |
|---|---|
| Hash SHA-256 do corpus no `manifest.json` | Implementado |
| Validação de esquema com Pydantic (HTTP 422) | Implementado |
| Fallback extrativo quando o LLM falha | Implementado |
| Alias `@champion` para *rollback* | Implementado |
| Coleta recorrente do corpus (cron) | Não há agendamento |
| Alerta se o corpus variar mais de 20% | Não implementado |
| Latência p50/p95/p99 e TTFT | Só latência total por pergunta, e só em `/api/chat` |
| Taxa de fallback enviada ao MLflow | Só o parâmetro `llm_used` por run |
| Gate de promoção em F1 > 0,85 | O gate é F1 ≥ 0,0 |
| *Shadow deployment* para re-treino | Não implementado |

Trate o playbook como **projeto de observabilidade**, não como descrição do que existe.
