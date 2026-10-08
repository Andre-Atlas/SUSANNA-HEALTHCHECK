# 6. Corpus e indexação — de onde vêm as respostas

O "conhecimento" da Susana não está no LLM. Está num conjunto de **textos oficiais** (o corpus), quebrados em blocos, transformados em vetores e guardados no ChromaDB. O LLM só reescreve o que a busca encontra nesses blocos.

```text
 (offline, manual)                          (automático, no startup do backend)
 ┌──────────────────────┐                   ┌────────────────────────────────────────────┐
 │ collect_corpus.py    │──► sesdf_public.txt ─┐                                         │
 │ (raspa saude.df.gov) │                   │  ├─► corpus.py ──► blocos ──► embeddings ──► ChromaDB
 │ collect_opendata.py  │──► dados_abertos.txt┘   (parse)        (384-d)     (data/chroma_db)
 │ (CKAN ou mock)       │                   │                                            │
 └──────────────────────┘                   └────────────────────────────────────────────┘
```

## 1. O formato dos arquivos do corpus

Tudo que está em `susana_rag_backend/data/corpus/*.txt` é indexado. Cada **bloco** começa com uma linha `[TAG] Título`, tem texto livre e, opcionalmente, uma linha `Fonte: <url>`:

```text
[EMERGENCIA] SAMU 192 (parte 5)
...texto...
Fonte: https://www.saude.df.gov.br/samu

[DADOS_ABERTOS] Unidades Básicas de Saúde do DF
Lista de UBS em funcionamento. ...
Fonte: https://dados.df.gov.br/dataset/ubs-df-lista
```

Tags usadas: `UNIDADE`, `SERVICO`, `VACINACAO`, `EMERGENCIA`, `INSTITUCIONAL`, `DADOS_ABERTOS`.

## 2. O conteúdo atual (52 blocos, todos oficiais)

> Atualizado em 08/10/2026. Os 7 blocos fictícios de "dados abertos" foram retirados do corpus e
> as URLs quebradas do `sources.yaml` foram trocadas pelas atuais. Detalhes em
> [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

| Arquivo | Blocos | Origem |
| --- | --- | --- |
| `data/corpus/sesdf_public.txt` | 52 | Raspagem de 12 páginas oficiais em 08/10/2026 |
| `data/corpus/manifest.json` | — | Metadados da raspagem (URL, data, SHA-256, nº de blocos) |
| `data/mock/dados_abertos_EXEMPLO.txt` | 7 | Textos **escritos à mão** para testes. **Não é indexado** |
| `data/sus_docs.txt` | 10 | Exemplos da primeira versão. **Não é indexado** |

Páginas no corpus:

| Página | Tag | Blocos |
| --- | --- | --- |
| Unidades Básicas de Saúde | UNIDADE | 12 |
| Atenção Domiciliar | SERVICO | 14 |
| SAMU 192 | EMERGENCIA | 7 |
| Farmácia de Alto Custo (CEAF) | SERVICO | 5 |
| Hospitais Regionais | UNIDADE | 3 |
| Calendário Nacional de Vacinação (gov.br) | VACINACAO | 3 |
| Ouvidoria SES-DF | INSTITUCIONAL | 2 |
| Carta de Serviços | SERVICO | 2 |
| Unidades de Referência Distrital | UNIDADE | 1 |
| Locais de vacinação | VACINACAO | 1 |
| Campanhas de vacinação | VACINACAO | 1 |
| Farmácias da SES-DF | SERVICO | 1 |

Ficaram de fora por terem menos de 200 caracteres úteis (o conteúdo provavelmente é carregado por JavaScript ou está em PDF): Vacinação de rotina, Vacina antirrábica humana e Serviços ao Cidadão.

**Atenção a um efeito da raspagem:** a página do SAMU contém uma lista de telefones das equipes de Atenção Domiciliar. Esse trecho fica rotulado como `[EMERGENCIA] SAMU 192 (parte 5)`, e o rótulo pode levar o LLM a atribuir ao SAMU um telefone que não é dele. A expansão de siglas (veja [07-busca-e-geracao.md](07-busca-e-geracao.md)) reduziu o problema, mas a solução definitiva é melhorar a divisão em blocos (veja [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md)).

## 3. Coleta — `ml/corpus/collect_corpus.py` (raspagem das páginas oficiais)

Roda manualmente: `cd susana_rag_backend && .venv/bin/python ml/corpus/collect_corpus.py`. As dependências (`pyyaml`, `beautifulsoup4`, `requests`) estão no `requirements.txt`.

Passo a passo:

1. **Lê as fontes** de [sources.yaml](../susana_rag_backend/ml/corpus/sources.yaml) e descarta as que têm tag inválida ou URL que não começa com `http`.
2. **Baixa cada página** com `httpx`: User-Agent identificado ("SusanaCorpusBot/1.0 … projeto acadêmico"), timeout de 15 s, 1 s de pausa entre páginas. Respostas diferentes de 200 contam como falha.
3. **Limpa o HTML** (`extract_paragraphs`):
   - remove `script`, `style`, `nav`, `footer`, `header`, `aside`, `form`, `iframe`, `svg`, `button`;
   - remove menus, breadcrumbs e botões de compartilhar por seletor CSS;
   - escolhe a área principal (`.journal-content-article`, `#main-content`, `main`, `article`…) pegando o candidato com mais texto;
   - extrai `p`, `li`, `h2`–`h4` e `td`, normaliza espaços e descarta textos com menos de 40 caracteres, duplicados ou com mais de 60% de texto de link (listas de links).
4. **Descarta a página** se sobrarem menos de 200 caracteres úteis.
5. **Quebra em blocos** (`chunk`) de no máximo **900 caracteres**, juntando parágrafos. Parágrafos maiores são cortados no último ". " antes do limite.
6. **Escreve** cada bloco como `[TAG] Título (parte N)` + texto + `Fonte: URL` em `sesdf_public.txt`, e registra URL, data, SHA-256 e contagens no `manifest.json`.

O arquivo de saída é **sobrescrito** a cada execução. Se o portal estiver fora do ar, o corpus anterior é perdido.

## 4. Coleta — `ml/corpus/collect_opendata.py` (portal de dados abertos)

```bash
.venv/bin/python ml/corpus/collect_opendata.py          # real: grava data/corpus/dados_abertos.txt
.venv/bin/python ml/corpus/collect_opendata.py --mock   # exemplo: grava data/mock/ (NÃO indexado)
```

1. Consulta `https://dados.df.gov.br/api/3/action/package_search?q=saude&rows=100` (API CKAN).
2. **Se a API falhar, o script termina com erro (código 1) e não grava nada.** Antes, ele caía silenciosamente nos dados inventados e os gravava no corpus.
3. Para cada dataset com descrição, escreve `[DADOS_ABERTOS] <title>`, o campo `notes` sem HTML e `Fonte: https://dados.df.gov.br/dataset/<name>`.

Situação em 08/10/2026: a API responde **HTTP 404**, então não há dados abertos no corpus. Mesmo quando ela voltar, o campo `notes` do CKAN é a *descrição* do dataset, não os dados em si.

## 5. Parsing — `app/rag/corpus.py`

[parse_corpus_text](../susana_rag_backend/app/rag/corpus.py#L27-L52) lê o texto linha a linha:

- uma linha `[TAG] Título` fecha o bloco anterior e abre um novo;
- uma linha `Fonte: <url>` guarda a URL **sem** incluí-la no texto do bloco;
- as demais linhas não vazias são acumuladas no bloco;
- linhas antes do primeiro cabeçalho são ignoradas.

Cada bloco vira um `CorpusBlock`:

| Campo | Exemplo |
| --- | --- |
| `id` | `sha256(texto)[:16]`: o id depende **do conteúdo** |
| `header` | `[EMERGENCIA] SAMU 192 (parte 5)` |
| `tag` | `EMERGENCIA` |
| `text` | cabeçalho + corpo (é o que vai para o LLM) |
| `url` | `https://www.saude.df.gov.br/samu` |

`load_corpus` junta vários arquivos e remove blocos de texto idêntico.

## 6. Embeddings — `app/rag/embeddings.py`

- Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. É multilíngue (entende português), gera vetores de **384 dimensões** e roda em CPU.
- Os vetores saem **normalizados** (`normalize_embeddings=True`), então a comparação por cosseno equivale ao produto escalar.
- Modelos da família **E5** exigem os prefixos `query: ` e `passage: `. O código aplica esses prefixos automaticamente se o nome do modelo contiver "e5". Para o modelo atual, não há prefixo.
- `slug` (ex.: `paraphrase-multilingual-minilm-l12-v2`) serve para nomear a coleção no Chroma.

## 7. Indexação no ChromaDB — `app/rag/retriever.py`

- `chromadb.PersistentClient(path="data/chroma_db")`: o índice fica salvo em disco e sobrevive a reinícios.
- Coleção: `sus_df_<slug do modelo>` com `hnsw:space = cosine`. **Uma coleção por modelo de embedding**, para não misturar vetores de modelos diferentes.
- `index(blocks)`:
  1. pergunta ao Chroma quais ids já existem e **apaga os que saíram do corpus**;
  2. calcula embeddings **só dos blocos novos**, em lotes de 64;
  3. grava `id`, `document` (texto), `embedding` e `metadata = {source: header, tag, url}`.

Como o id é o hash do conteúdo, **editar** um bloco cria um id novo. Por isso o `index()` também **remove do índice os ids que não estão mais no corpus** (`prune=True`). Assim, o ChromaDB sempre espelha exatamente os arquivos de `data/corpus/`.

## Como atualizar o corpus

```bash
cd susana_rag_backend
.venv/bin/python ml/corpus/collect_corpus.py      # páginas oficiais (sources.yaml)
.venv/bin/python ml/corpus/collect_opendata.py    # dados abertos (falha se a API estiver fora)
.venv/bin/python -m ml.retrieval.calibrate_threshold   # recalibra o limiar para o corpus novo
# reinicie o backend: ele sincroniza o índice no startup
```

Para adicionar conteúdo manualmente, crie um `.txt` em `data/corpus/` no formato `[TAG] Título` / texto / `Fonte: url`.
