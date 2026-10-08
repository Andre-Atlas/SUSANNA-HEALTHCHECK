# 6. Corpus e indexação — de onde vêm as respostas

O "conhecimento" da Susana não está no LLM. Está num conjunto de **textos e tabelas oficiais** (o corpus), quebrados em blocos, transformados em vetores e guardados no ChromaDB. O LLM só reescreve o que a busca encontra nesses blocos.

> Atualizado em 08/10/2026, depois da integração da branch `develop_gui_sam`: corpus curado `CORPUS/Arquivos/`, carregador multiformato, 256 tokens por bloco e correção da página do SAMU.
> Passo a passo: [registro/2026-10-08-integracao-develop_gui_sam.md](registro/2026-10-08-integracao-develop_gui_sam.md).

```text
 (offline, manual)                                  (automático, no startup do backend)
 ┌──────────────────────────┐                       ┌──────────────────────────────────────────────────┐
 │ collect_corpus.py        │──► data/corpus/       │ discover_corpus_files (recursivo)                 │
 │ (raspa saude.df.gov.br)  │    sesdf_public.txt ──┤   → load_corpus (txt/md/csv/json/html/pdf)        │
 │                          │                       │   → blocos → embeddings (384-d, 256 tokens)       │
 │ CORPUS/Arquivos/         │──► 26 CSV/JSON ───────┤   → ChromaDB (data/chroma_db), sincronizado       │
 │ (curado na develop_gui_sam)                      │                                                   │
 └──────────────────────────┘                       └──────────────────────────────────────────────────┘
```

## 1. Onde fica o corpus

As pastas varridas estão em `Settings.corpus_roots` ([config.py](../susana_rag_backend/app/config.py)):

| Pasta | Conteúdo |
| --- | --- |
| `susana_rag_backend/data/corpus/` | Páginas oficiais raspadas (`sesdf_public.txt`) |
| `CORPUS/Arquivos/` | Corpus curado vindo da `develop_gui_sam`: diretórios de unidades (CSV), REME, FAQ, páginas estruturadas (JSON) |

**Não são indexados** (de propósito):

| Caminho | Motivo |
| --- | --- |
| Bases de análise (`Samu/`, `obitos-…/`, `atendimentos-…/`, `Exames-…/`, `cirurgias-…/` na raiz) | Estatística, não informação de serviço; somariam ~104 mil blocos (veja o [doc 12](12-comparacao-develop_gui_sam.md)) |
| `CORPUS/nao_indexado/` | Matéria do Jornal de Brasília: não é fonte oficial |
| `CORPUS/Arquivos/relatorio_exportacao.log` | Log da exportação dos CSVs (extensão `.log` não é lida) |
| `data/mock/`, `data/sus_docs.txt` | Dados de exemplo ou fictícios |
| Arquivos/pastas que começam com `.` e `manifest.json` | Ignorados pelo `discover_corpus_files` |

## 2. O conteúdo atual (1.979 blocos de 28 arquivos)

| Origem | Blocos | Exemplos |
| --- | --- | --- |
| **REME-DF 2025** (lista de medicamentos da rede) | 1.234 | "dipirona comprimido 500mg — UBS (farmácia ambulatorial…)" |
| **Diretórios de unidades** (14 CSV) | 414 | 182 UBS (endereço, CEP, horário, sala de vacina, farmácia, coleta), centros especializados, CAPS, policlínicas, hospitais, UPAs, UBS prisionais/indígenas/consultório na rua, regiões |
| **Páginas estruturadas** (JSON) | 212 | Saúde Mental, Farmácias Vivas, Farmácia Escola, UBS, CEAF, Práticas Integrativas, Maternidades, CTA, CEPAV, Urgência e Emergência |
| **FAQ Meu SUS Digital** | 41 | Exames, vacinas, prescrições no app |
| **Carta de Serviços ao Cidadão 2026** (SES-DF, da branch `docs`) | 28 | LAI, e-Protocolo/Ouvidoria, SISPE, UBS, Policlínicas, Centros Especializados/CAPS/SAMU/UPAs/Hospitais, Farmácias, Banco de Leite, Atenção Domiciliar, Cuidados Paliativos, Terapia Renal, Vigilância, Órteses |
| **Páginas raspadas** (`sesdf_public.txt`) | 50 | Atenção Domiciliar 14, UBS 12, CEAF 5, SAMU 5, Hospitais 3, Calendário de vacinação 3… |

1.565 blocos têm URL de origem. Os **414 dos CSVs não têm** (a origem da exportação ainda precisa ser confirmada com o Sam) e aparecem nas citações como referência textual.

### Carta de Serviços ao Cidadão 2026

Vem da EDA feita na branch `docs` (`EDA\`s/EDAcartilha`), que extraiu o PDF oficial em 14 seções. O script [import_carta_servicos.py](../susana_rag_backend/ml/corpus/import_carta_servicos.py):

1. lê a extração original, guardada em `CORPUS/nao_indexado/carta_servicos_2026_secoes.jsonl` (não indexada);
2. remove resíduos de HTML e Markdown (`<u>`, `**`, `<br>`, comentários da extração);
3. descarta a capa/sumário;
4. **corrige rótulos**: a seção da p. 7 é e-Protocolo/Ouvidoria (a EDA a chamava de "UPAs"); a seção da p. 14 vai até a p. 23 e cobre Centros Especializados, CAPS, SAMU-DF 192, UPAs e Hospitais;
5. grava `CORPUS/Arquivos/carta_servicos_sesdf_2026.json` no esquema `chunks`, com o serviço e o intervalo de páginas.

A citação mostra o serviço, ex. "Carta de Serviços ao Cidadão 2026 — SES-DF — Atendimento em Unidade Básica de Saúde (UBS)". A URL é a da página onde a SES-DF publica a Carta.

### Diretório de unidades (uso estruturado)

Além de virarem blocos da busca, os 10 CSVs de unidades são carregados como **tabela** pelo [unit_directory.py](../susana_rag_backend/app/rag/unit_directory.py) (340 unidades, 43 regiões) para listar unidades por tipo e região. Veja [07-busca-e-geracao.md](07-busca-e-geracao.md#2b-diretório-de-unidades-busca-estruturada).

### Correção da página do SAMU

Os 7 blocos antigos "[EMERGENCIA] SAMU 192" eram, na verdade, conteúdo da **Atenção Domiciliar**: a página `saude.df.gov.br/samu` tem pouco texto próprio, e o raspador escolheu a área com mais texto, que era um menu da Atenção Domiciliar. Era daí que vinha o "telefone do SAMU (61) 2017-1145". O `sources.yaml` agora usa a página dedicada **`/samu-192-df`**: 5 blocos com o conteúdo real ("chamada gratuita pelo telefone 192", classificação de risco, frota).

## 3. Os formatos lidos — `app/rag/corpus.py`

Carregador da `develop_gui_sam`. `discover_corpus_files` varre as pastas recursivamente; `load_corpus` escolhe o leitor pela extensão. Se um arquivo estiver corrompido, **falha** com erro (não pula em silêncio).

| Formato | Como vira bloco |
| --- | --- |
| `.txt` / `.md` no formato `[TAG] Título` + `Fonte: url` | Um bloco por cabeçalho (formato original) |
| `.txt` / `.md` sem cabeçalhos | Trechos de até 900 caracteres, tag `TEXTO` |
| `.csv` | Detecta encoding (`utf-8`/`iso-8859-1`) e separador pelo cabeçalho; **um bloco por registro** em tabelas pequenas ("Estabelecimento: UBS 01 CANDANGOLANDIA; Endereço: …; Horário: …"); agrupa linhas repetidas e soma colunas de quantidade; ignora colunas de geometria |
| `.csv` mensais `SIA######` | Consolidados numa série mensal (não usados hoje, porque as bases de análise estão fora) |
| `.json` | No esquema `chunks`, o contexto da seção (ex.: o serviço) vai em **todos** os trechos e no cabeçalho, e não só no primeiro. Três esquemas reconhecidos (`chunks`, `documentos` de FAQ e `conteudo` com metadata) + um genérico que "achata" o JSON; a URL vem de `url`, `fonte`, `source_url` ou `fonte_principal` |
| `.html` | Texto sem `script`/`style`, quebrado em trechos |
| `.pdf` | Texto extraído com `pypdf` |

Cabeçalho dos blocos de CSV (ajuste feito na integração, para a citação ficar legível):

```text
[CSV] Unidade Básica de Saúde (Unidade_Básica_de_Saúde.csv, registro 1)
```

Cada bloco vira um `CorpusBlock` com `id` (hash do arquivo de origem + texto + URL), `header`, `tag`, `text` e `url`.

## 4. Coleta das páginas oficiais — `ml/corpus/collect_corpus.py`

Roda manualmente: `cd susana_rag_backend && .venv/bin/python ml/corpus/collect_corpus.py`.

1. **Lê as fontes** de [sources.yaml](../susana_rag_backend/ml/corpus/sources.yaml) e descarta as que têm tag inválida ou URL que não começa com `http`.
2. **Baixa cada página** com `httpx` (User-Agent "SusanaCorpusBot/1.0 … projeto acadêmico", timeout de 15 s, 1 s entre páginas).
3. **Limpa o HTML**: remove scripts, menus e rodapés; escolhe a área principal **pelo candidato com mais texto** (foi isso que pegou o menu errado no SAMU); extrai `p`, `li`, `h2`–`h4` e `td`; descarta textos curtos, duplicados ou com mais de 60% de texto de link.
4. **Descarta a página** se sobrarem menos de 200 caracteres úteis.
5. **Quebra em blocos** de até 900 caracteres e grava `[TAG] Título (parte N)` + texto + `Fonte: URL` em `sesdf_public.txt`, com metadados no `manifest.json`.

O arquivo é **sobrescrito** a cada execução.

## 5. Dados abertos — `ml/corpus/collect_opendata.py`

```bash
.venv/bin/python ml/corpus/collect_opendata.py          # real: grava data/corpus/dados_abertos.txt
.venv/bin/python ml/corpus/collect_opendata.py --mock   # exemplo: grava data/mock/ (NÃO indexado)
```

Se a API CKAN falhar, termina com erro e não grava nada. Situação em 08/10/2026: **HTTP 404**, então não há dados abertos no corpus.

## 6. Embeddings — `app/rag/embeddings.py`

- Modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilíngue, 384 dimensões, CPU), com vetores **normalizados**.
- **`EMBEDDING_MAX_SEQ_LENGTH=256`** (vindo da `develop_gui_sam`). O padrão do modelo é 128 tokens, o que cortava 41 dos 52 blocos raspados. 256 e 512 deram o mesmo resultado no benchmark de entidades (Recall@1 0,946; Recall@3 1,0), e 256 fica mais perto do tamanho de treino do modelo.
- Prefixos `query: `/`passage: ` só para modelos E5.
- O `slug` inclui o tamanho (`…-minilm-l12-v2-seq256`): mudar o tamanho cria uma **coleção nova**, sem misturar vetores incompatíveis.

## 7. Indexação no ChromaDB — `app/rag/retriever.py`

- `chromadb.PersistentClient(path="data/chroma_db")`, coleção `sus_df_<slug>` em espaço de cosseno.
- `index(blocks)` **sincroniza** o índice: calcula embeddings só dos blocos novos (lotes de 256) e **remove** os que saíram do corpus.
- Indexação do corpus completo: **1.979 blocos em ~25 s** (CPU).
- A busca (vetorial + palavras) está descrita em [07-busca-e-geracao.md](07-busca-e-geracao.md).

## Como atualizar o corpus

```bash
cd susana_rag_backend
.venv/bin/python ml/corpus/collect_corpus.py           # páginas oficiais (sources.yaml)
# e/ou copie arquivos .csv/.json/.txt/.pdf para CORPUS/Arquivos/
.venv/bin/python -m ml.retrieval.calibrate_threshold    # recalibra o limiar para o corpus novo
.venv/bin/python -m ml.retrieval.benchmark_corpus       # Recall@1/@3 por entidade (índice temporário)
# reinicie o backend: ele sincroniza o índice no startup
```
