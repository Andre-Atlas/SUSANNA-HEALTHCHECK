# 12. Comparação: `develop_gui2` × `develop_gui_sam`

Análise feita em 08/10/2026 para decidir o que da branch `develop_gui_sam` (commit `a267606`, "commit inicial") vale trazer para a `develop_gui2`.
Método: leitura do diff, execução dos testes do Sam numa cópia isolada (git worktree) e medições com o código dele.

> **Status: integrado na `develop_gui2` em 08/10/2026** (só nesta branch; a `develop_gui_sam` não foi alterada).
> O que entrou, o que foi adaptado e as medições estão na seção [Resultado da integração](#resultado-da-integração) e em
> [registro/2026-10-08-integracao-develop_gui_sam.md](registro/2026-10-08-integracao-develop_gui_sam.md).

## Ponto de partida das duas branches

```text
7a260f0 (base comum: "integrar frontend streaming, RAG pipeline refatorado e MLflow guardrails")
   ├── develop_gui_sam: 1 commit (a267606) → foco em CORPUS e RECUPERAÇÃO
   └── develop_gui2:   37 commits          → foco em SEGURANÇA, PIPELINE, AVALIAÇÃO e DOCUMENTAÇÃO
```

As duas evoluíram **em paralelo, a partir do mesmo ponto**, e mexeram nos mesmos arquivos centrais (`corpus.py`, `retriever.py`, `pipeline.py`, `main.py`, `config.py`, `routers_stream.py`). Um `git merge` direto vai gerar conflitos nesses arquivos. A integração precisa ser feita **à mão, peça por peça** (plano no final).

## O que cada branch tem

| Área | `develop_gui2` (sua) | `develop_gui_sam` |
| --- | --- | --- |
| **Corpus** | 52 blocos de 12 páginas oficiais raspadas (`data/corpus/sesdf_public.txt`) | **28 arquivos curados** em `CORPUS/Arquivos/` (CSV/JSON): diretório de **182 UBS** com endereço, horário, sala de vacina e farmácia; UPAs, hospitais, policlínicas, CAPS, centros especializados; REME 2025 (lista de medicamentos); FAQ Meu SUS Digital; CTA, maternidades, saúde mental, práticas integrativas |
| **Formatos lidos** | Só `.txt` no formato `[TAG] Título` | `.txt`, `.md`, `.csv`, `.json` (3 esquemas), `.html`, `.pdf`, lidos recursivamente, com detecção de encoding e separador |
| **Bases de análise** (SIA, óbitos, exames) | Fora do chat (só EDA) | Movidas para `CORPUS/` e **indexadas** no startup (~104 mil blocos), com consolidação mensal do SIA |
| **Busca** | Vetorial pura + **expansão de siglas** | **Híbrida**: 300 candidatos vetoriais + busca textual (`$contains`) por termos raros e por entidades numeradas ("UBS 2"), reordenando por coincidência de palavras |
| **Relevância** | Limiar 0,70 **calibrado** por script | Limiar 0,55 fixo + exceção quando a entidade numerada bate (`is_relevant`) |
| **Embeddings** | `max_seq_length` 128 (padrão): **41 dos 52 blocos são cortados** | `EMBEDDING_MAX_SEQ_LENGTH=512` (texto inteiro); nome da coleção inclui o tamanho |
| **Guardrail** | Híbrido regras + ML, dataset de 111 frases, gate com 3 métricas, v4 `@champion` | Original (ML substitui regras; sem modelo, cai em regex) |
| **Pipeline / rotas** | Fluxo único para as 2 rotas; cache e MLflow no streaming; fonte = trecho citado | Rotas ainda separadas; **lista estruturada de citações** (`citations: [{ref, title, url}]`), só na rota `/api/chat` |
| **Índice** | Remove blocos que saíram do corpus | Também remove (implementação equivalente) |
| **LGPD** | MLflow grava só hash da pergunta | Texto da pergunta no MLflow |
| **Dados fictícios** | Removidos do corpus | `dados_abertos.txt` (fictício) ainda indexado |
| **Testes** | 38 (API, guardrail, streaming, citação, glossário) | 14 originais (`test_rag.py`) + **25 novos** de ingestão, busca e citações, rápidos (2 s) e sem Ollama |
| **Avaliação** | Gerador de 227 perguntas + avaliador + relatório | `benchmark_corpus.py`: Recall@k por entidade em CSV + perguntas fora do tema; +7 casos no benchmark de LLM |
| **Planejamento** | `PROXIMOS-PASSOS.md`, `registro/`, docs 01–11 | `docs/production-readiness-plan.md` (309 linhas: gates de produto, fases F0–F8, corte do MVP) |
| **Dependências** | Mantém `langchain`, `redis` (não usados) | Remove `langchain*` e `redis` (não usados); adiciona `pypdf` |

## Medições feitas nesta análise

### Testes do Sam

```text
tests/test_corpus_ingestion.py tests/test_retriever.py tests/test_pipeline_citations.py
25 passed in 2.23s
```

### Tamanho do corpus com o carregador dele

| Escopo | Arquivos | Blocos | Tempo de leitura |
| --- | --- | --- | --- |
| `CORPUS/Arquivos` (curado) | 28 | **1.910** (1.232 só da REME/medicamentos) | < 1 s |
| `CORPUS/` inteiro | 65 | **105.859** (104 mil das bases de análise) | 29 s (sem contar os embeddings) |

### Busca só vetorial × busca híbrida (1.962 blocos: corpus curado + seus 52)

| Pergunta | Só vetor (sua) | Híbrida (Sam) |
| --- | --- | --- |
| Onde fica a UBS 1 de Candangolândia? | ❌ | ✅ |
| Qual o horário da UBS 2 de Planaltina? | ❌ | ✅ |
| Endereço da UBS 01 do Riacho Fundo I | ❌ | ✅ |
| A UBS 5 de Ceilândia tem sala de vacina? | ❌ | ✅ |
| Onde fica o CAPS de Taguatinga? | ✅ | ✅ |
| Qual o endereço da UPA de Samambaia? | ✅ | ✅ |
| Onde faço teste de HIV no CTA? | ✅ | ✅ |
| Como ver meus exames no Meu SUS Digital? | ✅ | ✅ |
| A rede pública tem losartana? | ❌ | ❌ |
| Qual o telefone do SAMU? | ✅ | ✅ |

Conclusão: com um diretório de 182 UBS de nomes quase iguais, a busca vetorial sozinha não distingue "UBS 1" de "UBS 2". **A reordenação por palavras do Sam é necessária** para esse tipo de dado.

---

## O que aproveitar

### ✅ Trazer (alto valor, baixo risco)

| # | O quê | Por quê | Esforço |
| --- | --- | --- | --- |
| 1 | **`CORPUS/Arquivos/`** (os 28 arquivos curados) | Resolve a maior lacuna do seu corpus: endereço e horário de cada unidade. Ataca os problemas `NAO_RESPONDEU` da 1ª avaliação | Baixo: copiar a pasta |
| 2 | **Carregador multiformato** (`discover_corpus_files`, `_csv_blocks`, `_json_blocks`, HTML/PDF) em `corpus.py` | Necessário para ler o item 1; testado (25 testes); falha explicitamente se um arquivo estiver corrompido | Médio: substituir `load_corpus`, mantendo o formato `[TAG]` |
| 3 | **Busca híbrida** (`search` com `query_text`, `_numbered_entity`, `is_relevant`) em `retriever.py` | Ganho medido de 4/4 nas perguntas por unidade | Médio: encaixar no `RAGPipeline.query_stream` e combinar com o seu glossário de siglas |
| 4 | **`EMBEDDING_MAX_SEQ_LENGTH`** em `embeddings.py` | Seu índice ignora o fim de 41 dos 52 blocos | Baixo (exige recalibrar o limiar) |
| 5 | **Os 25 testes** (`test_corpus_ingestion.py`, `test_retriever.py`) | Rápidos, sem Ollama: bons para rodar a cada mudança | Baixo (ajustar ao seu pipeline) |
| 6 | **Limpeza do `requirements.txt`** (sai `langchain*` e `redis`; entra `pypdf`) | Menos dependências sem uso (era o item P13 dos seus problemas conhecidos) | Baixo |
| 7 | **`production-readiness-plan.md`** | Os gates de produto (segurança clínica 100%, Recall@3 ≥ 95%, groundedness, frescor de fonte, p95 ≤ 15 s) dão a definição de "projeto concluído" que falta no `PROXIMOS-PASSOS.md` | Baixo: copiar e referenciar |

### 🟡 Adaptar antes de trazer

| O quê | Ajuste necessário |
| --- | --- |
| **Citações estruturadas** (`citations: [{ref, title, url}]`) | Boa ideia, mas está só na rota `/api/chat`. Implementar no seu `query_stream` (evento `done`), combinando com o seu `pick_source`, e depois mostrar no frontend como links |
| **`benchmark_corpus.py`** | Útil (Recall@1/@3 por entidade). Transformar numa categoria do seu `run_eval` ou registrar no MLflow, para não ter duas ferramentas de avaliação |
| **REME (1.232 blocos de medicamentos)** | Útil para "a rede tem o remédio X?", mas são 64% do corpus e contêm concentração/forma farmacêutica. Avaliar com o `run_eval` se não "sequestram" a busca e se o LLM não transforma isso em orientação de dose |
| **CSVs sem URL** (14 diretórios de unidades) | A citação fica "Unidade_Básica_de_Saúde.csv". Descobrir com o Sam a origem (o `relatorio_exportacao.txt` sugere exportação de camadas do InfoSaúde/Geoportal) e colocar a URL e a data |
| **Limiar 0,55 + exceção de entidade** | Não trocar pelo seu 0,70 calibrado sem medir: recalibrar com o corpus novo e usar a exceção de entidade dele |

### ❌ Não trazer (ou decidir com a equipe antes)

| O quê | Motivo |
| --- | --- |
| **Indexar o `CORPUS/` inteiro** (SIA, óbitos, exames, cirurgias: ~104 mil blocos) | Startup muito lento (embeddings de 106 mil blocos no CPU); mistura estatística com informação de serviço; dados de óbito com CID não são administrativos. **O próprio plano do Sam recomenda deixar fora do MVP.** Indexar só `CORPUS/Arquivos` |
| **Mover as bases de análise para `CORPUS/`** | Quebra os caminhos dos scripts de EDA na sua branch. Só fazer junto com a decisão acima |
| **Matéria do Jornal de Brasília** (`Hran-dá-assistência-…json`) | Não é fonte oficial; o chat exibe "Fonte Oficial". Trocar por página da SES-DF ou marcar como "imprensa" |
| **`dados_abertos.txt`** fictício (ainda indexado na branch dele) | Já removido na sua branch pelo mesmo motivo |
| **Guardrail, pipeline e rotas da branch dele** | São a versão original; a sua já corrige os problemas de segurança (P1–P6) |
| `package-lock.json` na raiz | Arquivo solto de 6 linhas, sem `package.json` correspondente |

### O que a branch do Sam ganharia com a sua

Para conversar com ele: guardrail híbrido com gate (recall clínico 0,987 contra 0,40), pipeline único (cache e MLflow no streaming), remoção dos dados fictícios, LGPD no MLflow, glossário de siglas, limiar calibrado por script e o gerador e avaliador de perguntas.

## Plano de integração sugerido

Ordem pensada para cada passo poder ser medido com `pytest` + `run_eval --seed 0`:

1. Copiar `CORPUS/Arquivos/` (sem a matéria de jornal) e o `production-readiness-plan.md`.
2. Trazer o carregador multiformato + `test_corpus_ingestion.py`; indexar `data/corpus/` + `CORPUS/Arquivos/` (não o `CORPUS/` inteiro).
3. Trazer `EMBEDDING_MAX_SEQ_LENGTH` (testar 256 e 512).
4. Trazer a busca híbrida + `test_retriever.py`, combinada com o glossário de siglas.
5. Recalibrar o limiar (`calibrate_threshold.py`) e acrescentar perguntas por unidade ao `threshold_set.jsonl`.
6. Regenerar o banco (`generate_questions`) e rodar `run_eval`. Comparar com [avaliacoes/2026-10-08-1512.md](avaliacoes/2026-10-08-1512.md).
7. Citações estruturadas no `done` do streaming + frontend com links.
8. Limpeza do `requirements.txt`.

Cada passo vira um commit e um registro em [registro/](registro/). Este plano é o **passo 2** de [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md).

## Perguntas para o Sam

1. De onde vieram os 14 CSVs de unidades (URL e data da exportação)?
2. A ideia era o chat responder sobre as bases de análise (SIA, óbitos), ou só ler os arquivos?
3. A matéria do Jornal de Brasília pode ser trocada por uma página oficial sobre soro/animais peçonhentos?
4. O `meu_sus_digital_faq_estruturado.json` diz "texto fornecido pelo usuário". Qual é a página de origem e a data?

---

## Resultado da integração

| Item do plano | Situação | Observação |
| --- | --- | --- |
| `CORPUS/Arquivos/` | ✅ Integrado | 26 arquivos indexados; matéria de jornal movida para `CORPUS/nao_indexado/`; `relatorio_exportacao.txt` renomeado para `.log` (não indexado) |
| `production-readiness-plan.md` | ✅ Copiado | `docs/production-readiness-plan.md` |
| Carregador multiformato + 13 testes | ✅ Integrado | Cabeçalho legível para CSV ("Unidade Básica de Saúde (arquivo.csv, registro 1)"); só `data/corpus/` + `CORPUS/Arquivos/` são lidos |
| `EMBEDDING_MAX_SEQ_LENGTH` | ✅ Integrado com **256** | 256 e 512 empataram no `benchmark_corpus` (Recall@1 0,946; @3 1,0) |
| Busca híbrida + 11 testes | ✅ Integrado **com mudanças** | Veja abaixo |
| `is_relevant` | ✅ Integrado com mudança | Usa a menor distância entre os 3 trechos (o 1º pode vir do ranking por palavras) + exceção por unidade do Sam |
| Citações estruturadas + 1 teste | ✅ Integrado e estendido | Agora também no streaming, no cache e na rota `/api/chat`; frontend mostra como links |
| `benchmark_corpus.py` | ✅ Copiado | Usado para escolher o tamanho de sequência |
| Limpeza do `requirements.txt` | ✅ Feito | Sem `langchain*`/`redis`; com `pypdf` |
| +7 casos no benchmark de LLM | ✅ Copiado | `ml/llm/benchmark_dataset.json` |
| Indexar `CORPUS/` inteiro / mover bases de análise | ❌ Não feito (como planejado) | — |

### Mudanças em relação ao código do Sam (e por quê)

1. **Ranking intercalado em vez de "palavras primeiro".** O ranking original do Sam piorava perguntas gerais: "Quando devo ligar para o 192?" trazia "Saúde Mental", e "Perdi meu cartão de vacinação" trazia o FAQ do Meu SUS Digital. Agora, em perguntas específicas, os 3 trechos alternam entre o melhor por palavras e o melhor por significado. Em perguntas gerais, manda o significado. Em 16 perguntas de teste: **16/16**, contra 13/16 do ranking original e 10/16 da busca só vetorial.
2. **Peso por raridade (IDF)** na contagem de palavras: "telefone" (em dezenas de blocos) vale menos que "samu" ou "dipirona".
3. **Termos raros sem diferenciar maiúsculas e acentos:** o `$contains` do Chroma diferencia, e "dipirona" (minúscula na REME) não era encontrada. Agora o índice de termos é feito em memória.
4. **Cache semântico respeita números:** "UBS 1" e "UBS 2" ficam a 0,025 de distância. Sem essa regra, o cache devolveria o endereço da unidade errada.

### Descoberta durante a integração: a página do SAMU estava errada

Os 7 blocos "[EMERGENCIA] SAMU 192" raspados de `saude.df.gov.br/samu` eram conteúdo da **Atenção Domiciliar** (o raspador pegou um menu da página). A fonte foi trocada para `/samu-192-df`, com o conteúdo real ("chamada gratuita pelo telefone 192"). O problema existia nas **duas** branches; vale avisar o Sam.

