# Catálogo do Corpus e dos Datasets — SUSANA

> **Projeto:** Meu SUS Brasília / SUSANA  
> **Programa:** Residência em Inteligência Artificial — Instituto Eldorado (CBL — Challenge 1)  
> **Escopo deste catálogo:** tudo o que está em [`datasets/`](.) — base de conhecimento do RAG, tabelas cadastrais, conjuntos de avaliação e insumos das EDAs.  
> **Estado:** corpus congelado exatamente como usado no benchmark de homologação (branch `homologacao`, commit `e7ed446`). As pendências de qualidade estão na [seção 7](#7-pendências-de-qualidade-antes-da-apresentação).

---

## 1. Estrutura de pastas

```text
datasets/
├── catalogo_do_corpus.md       # este documento
├── corpus/   (21 arquivos)     # base de conhecimento: JSON estruturados e TXT
├── raw/      (14 arquivos CSV) # tabelas cadastrais da rede de saúde do DF
├── eval/     (5 arquivos)      # avaliação de recuperação, abstenção e guardrail
└── eda_inputs/ (4 arquivos)    # insumos do notebook eda_sus_digital (não vão para o RAG)
```

> `eda_inputs/` fica propositalmente **fora** de `corpus/` e `raw/`: essas pastas são lidas pelo indexador do RAG, e as bases epidemiológicas não devem entrar no índice.

---

## 2. Como o corpus vira blocos indexados

O indexador do backend (`app/rag/corpus.py`, branch `homologacao`) percorre as pastas recursivamente, aceita `.csv .json .txt .md .html .pdf`, ignora arquivos chamados `manifest.json` e divide cada fonte em blocos de até ~900 caracteres.

**Resultado verificado:** aplicando esse mesmo indexador sobre `corpus/` + `raw/` desta pasta, o total é de **2.283 blocos** (mesmo número do relatório técnico). A equivalência com a configuração do backend é:

| Configuração do backend (`config.py`) | Equivalente em `datasets/` |
| :--- | :--- |
| `data/corpus/` (`docs_dir`) | `corpus/` |
| `CORPUS/Arquivos/` (`project_corpus_dir`) | JSONs em `corpus/` + CSVs em `raw/` |
| `data/sus_docs.txt` (`legacy_docs_file`) | `corpus/sus_docs.txt` |

Cada bloco recebe metadados (`cluster`, `ra`, `tipo_unidade`, `servicos`) por regras de palavras-chave (`extract_block_metadata`) e uma URL de origem quando disponível.

---

## 3. Composição do índice por nível de confiança

| Camada | Blocos | % | Origem | Situação |
| :--- | :---: | :---: | :--- | :--- |
| **A. Tabelas cadastrais (CSV)** | 414 | 18,1% | Camadas cadastrais da rede de saúde do DF (UBS, UPA, hospitais, policlínicas, CAPS, regiões) | Estruturada; colunas de geometria removidas (ver `corpus/relatorio_exportacao.txt`) |
| **B. Páginas oficiais transcritas** | 265 | 11,6% | `saude.df.gov.br`, `info.saude.df.gov.br`, `gov.br/hubrasil`, Meu SUS Digital | Fonte oficial; algumas marcadas como revisão parcial (detalhe abaixo) |
| **C. REME-DF 2025** | 1.232 | 54,0% | PDF oficial da SES-DF, transcrito por OCR | **Revisão pendente** (`review_status: pending`) |
| **D. Diretório gerado por região** | 346 | 15,2% | Script `generate_health_directory.py` | **Não validado** — ver [seção 4](#4-diretório-por-região-diretorio_saude_dfjson) |
| **E. Itens sem valor de fonte** | 26 | 1,1% | Material legado, notícia, fixture de teste e logs | **Recomendado remover** — ver [seção 7](#7-pendências-de-qualidade-antes-da-apresentação) |
| **Total** | **2.283** | 100% | | |

### 3.1 Camada A — tabelas em `raw/` (414 blocos)

| Arquivo | Linhas | Conteúdo |
| :--- | :---: | :--- |
| `Unidade_Básica_de_Saúde.csv` | 182 | Estabelecimento, CNES, endereço, CEP, horário, sala de vacina, farmácia, região administrativa |
| `Centros_Especializados.csv` | 41 | Centros especializados |
| `Regiões_Administrativas.csv` | 35 | Regiões administrativas com sua região e macrorregião de saúde |
| `Região_Integrada_de_Desen.csv` | 33 | Municípios da Região Integrada de Desenvolvimento (RIDE) |
| `Outras_Unidades_de_Saúde.csv` | 29 | Outras unidades |
| `Centros_de_Atenção_Psicos.csv` | 19 | CAPS |
| `Policlínicas.csv` | 18 | Policlínicas |
| `Hospitais.csv` | 16 | Hospitais |
| `Unidades_de_Pronto_Atendi.csv` | 13 | UPAs |
| `Regiões_de_Saúde.csv` | 7 | Regiões de saúde |
| `UBS_-_Consultório_na_rua.csv` | 7 | UBS — Consultório na Rua |
| `UBS_-_Saúde_Indígena.csv` | 7 | UBS — Saúde Indígena |
| `UBS_-_Unidades_Prisionais.csv` | 5 | UBS — unidades prisionais |
| `Macrorregiões_de_Saúde.csv` | 3 | Macrorregiões de saúde |

> Os arquivos usam `;` como separador e UTF-8. As contagens de linhas acima são de registros (sem o cabeçalho).

### 3.2 Camada B — páginas oficiais e documentos em `corpus/` (265 blocos)

| Arquivo | Blocos | Fonte | Observação |
| :--- | :---: | :--- | :--- |
| `Saúde-Mental-Secretaria-de-Saúde-do-Distrito-Federal.json` | 41 | `saude.df.gov.br/diretoria-saude-mental` | — |
| `meu_sus_digital_faq_estruturado.json` | 41 | `gov.br/saude/.../meu-sus-digital` | Transcrição manual da página; campo `origem` registra "texto fornecido pelo usuário" |
| `Unidades-Básicas-de-Saúde-(UBS)-...json` | 29 | `saude.df.gov.br/unidades-basicas` | — |
| `04_Farmacias_Vivas_Fitoterapicos.json` | 35 | `saude.df.gov.br/farmacias-vivas-fitoterapicos` | `ingestion_status: partial_review` |
| `02_HUB_Farmacia_Escola.json` | 24 | `gov.br/hubrasil/.../farmacia-escola` | `ingestion_status: review_required` |
| `03_Componente_Especializado_Alto_Custo.json` | 21 | `saude.df.gov.br/componente-especializado` | `ingestion_status: partial_review` |
| `sesdf_public.txt` | 20 | Páginas da SES-DF (telefones de hospitais regionais) | Gerado por `ml/corpus/collect_corpus.py` |
| `Práticas-Integrativas-em-Saúde-...json` | 18 | `saude.df.gov.br/praticas-integrativas-em-saude` | — |
| `Maternidades.json` | 13 | `info.saude.df.gov.br/maternidades` | Publicado em 11/05/2024 |
| `dados_abertos.txt` | 8 | Citações de `dados.df.gov.br` | URLs de datasets não verificadas |
| `Centro-de-Testagem-e-Aconselhamento-CTA.json` | 6 | `info.saude.df.gov.br/centro-de-testagem-...` | Publicado em 11/05/2024 |
| `Busca-Saúde-CEPAV.json` | 5 | `info.saude.df.gov.br/busca-saude-cepav` | Publicado em 11/05/2024 |
| `Atendimento-médico-de-Urgência-...(UPAs)-Secr.json` | 4 | `saude.df.gov.br/hospitais-e-upas` | — |

### 3.3 Camada C — REME-DF 2025

`01_REME_DF_2025_Medicamentos.json` (3,5 MB) contém 1.123 registros e 1.150 chunks (1.232 blocos após a segmentação do indexador) transcritos do PDF oficial da SES-DF. Os próprios metadados do arquivo declaram:

* `review_status: pending` e `ingestion_status: blocked_for_automatic_import`;
* nota de qualidade: *"Transcrição com evidências de erros de OCR e deslocamento em códigos e descrições"*.

É a maior fonte do índice (54%) e a que sustenta as respostas sobre medicamentos; por isso é o principal risco de qualidade do corpus.

---

## 4. Diretório por região (`diretorio_saude_df.json`)

O arquivo (schema 2.0) tem **346 blocos**, não 346 unidades:

| Tag | Blocos |
| :--- | :---: |
| `UNIDADE_UBS` | 70 |
| `VACINACAO` | 70 |
| `MATERNO_INFANTIL` | 70 |
| `FARMACIA_BASICA` | 70 |
| `UNIDADE_REGIONAL` | 33 |
| `URGENCIA_EMERGENCIA` | 33 |

Cobre 33 regiões administrativas. O cadastro oficial em `raw/Regiões_Administrativas.csv` lista 35: **Água Quente** e **Arapoanga** não têm bloco próprio no diretório. Os textos são escritos em código no script `ml/corpus/generate_health_directory.py` (estrutura de dados em Python), e não extraídos de uma base oficial.

**Verificações feitas na revisão:**

| Verificação | Resultado |
| :--- | :--- |
| 2 URLs de origem testadas (`saude.df.gov.br/ubs-plano_piloto`, `.../ubs-ceilandia`) | Ambas retornam **HTTP 404**. A URL de controle `.../componente-especializado` abre normalmente. |
| URLs distintas no arquivo | 165, todas no padrão `saude.df.gov.br/<tema>-<região>` — as demais não foram testadas |
| 70 blocos `UNIDADE_UBS` × `raw/Unidade_Básica_de_Saúde.csv` | 34 têm nome correspondente (comparação por prefixo) e **apenas 11** têm endereço correspondente |

**Consequência:** endereços, horários e links "Ver mais" gerados a partir deste arquivo não são rastreáveis a uma fonte oficial. As tabelas da camada A (CNES/cadastro) são a referência confiável para endereço e horário.

> **Correção de nomenclatura:** os documentos da branch `homologacao` (README, `docs/ARQUITETURA_E_FUNCIONAMENTO.md`, `docs/MLOPS_E_MODELAGEM.md`) descrevem "346 unidades", "176 UBS" e "dados georreferenciados reais". O dado verificado é de 346 *blocos* (70 UBS). Esta entrega usa os números verificados.

---

## 5. Conjuntos de avaliação (`eval/`)

| Arquivo | Itens | Uso |
| :--- | :---: | :--- |
| `guardrails_dataset.csv` | 283 (150 `ADMINISTRATIVE` + 133 `CLINICAL`) | Treino e validação do classificador de risco clínico |
| `in_domain_dev.json` | 20 | Calibração da recuperação (dentro do domínio) |
| `in_domain_test.json` | 20 | Teste final de recuperação |
| `ood_dev.json` | 15 | Calibração do limiar de abstenção (fora do domínio) |
| `ood_test.json` | 15 | Teste final contra vazamento fora do domínio |

> O `docs/MLOPS_E_MODELAGEM.md` da `homologacao` cita 40/60/30/50 itens nessas partições. Os arquivos acima têm 20/20/15/15; o Recall@1 de 95% reportado corresponde a 19 de 20 consultas, coerente com os arquivos.

---

## 6. Insumos das EDAs (`eda_inputs/`)

| Arquivo | Tamanho | Usado em | Descrição |
| :--- | :---: | :--- | :--- |
| `obitos_df_2022.csv` | 4,5 MB | `eda_sus_digital` | Óbitos ocorridos no DF em 2022 (linhas com coluna de quantidade, por CID, faixa etária, região de saúde e mês) |
| `samu_producao_2026-09-29.csv` | 3,1 MB | `eda_sus_digital` | Produção do SAMU (exportação de 29/09/2026) |
| `atendimentos_consultas_2022.csv` | 0,7 MB | `eda_sus_digital` | Atendimentos e consultas (ambulatório e emergência), 2022 |
| `cirurgias_producao_ambulatorial_2022.csv` | 0,4 MB | `eda_sus_digital` | Cirurgias — produção ambulatorial, 2022 |

**Não versionados** (fora desta entrega): a série SIA 2017–2018 (~1 GB), exames de internação 2022–2023, atendimentos 2019–2021 e 2023, cirurgias e óbitos 2023 — permanecem na branch `homologacao` em `CORPUS/`.  
**Insumos externos das outras EDAs:** `eda_cartilha` lê `cartilha_secoes.csv` e o PDF da Carta de Serviços; `eda_vacinas_aplicadas` lê a exportação mensal do InfoSaúde-DF. Nenhum dos dois estava disponível para versionar; as saídas já calculadas permanecem salvas nos notebooks.

---

## 7. Pendências de qualidade antes da apresentação

| # | Item | Risco | Ação recomendada |
| :---: | :--- | :--- | :--- |
| 1 | `corpus/ingested_sus.txt` e `corpus/ingestion_manifest.json` (4 blocos) | Contêm o "Aviso Oficial: Ponto de Atendimento Rápido Especial em Santa Maria", que é um **dado de teste** (`tests/test_online_search_scoped.py`) gravado no corpus. É um comunicado inexistente indexado como oficial. | Remover do corpus e reindexar |
| 2 | `corpus/sus_docs.txt` (10 blocos) | Material legado de exemplo, com telefones fictícios (ex.: `(61) 3345-1234`) e endereços que divergem do diretório (UBS 1 Asa Sul: `SGAS 602` aqui, `SGAS 612` no diretório). O validador de telefones aceita números presentes no contexto recuperado, portanto não barraria esses telefones. | Remover do corpus e reindexar |
| 3 | `corpus/Hran-dá-assistência-...-Jornal-de-Brasília.json` (7 blocos) | Matéria de jornal; contradiz o requisito RF-13 (somente fontes oficiais) | Substituir pela página oficial da SES-DF ou remover |
| 4 | `corpus/relatorio_exportacao.txt` (5 blocos) | Log técnico de exportação, não é conteúdo para o cidadão | Mover para fora da pasta indexada |
| 5 | `corpus/diretorio_saude_df.json` (346 blocos) | Links 404 e endereços divergentes do cadastro | Regenerar a partir de `raw/*.csv`, ou apresentar explicitamente como diretório de apoio não validado |
| 6 | `corpus/01_REME_DF_2025_Medicamentos.json` (1.232 blocos) | OCR com erros e revisão pendente | Revisar por amostragem e registrar a taxa de erro; até lá, manter o aviso de verificação nas respostas de medicamentos |
| 7 | `ingestion_manifest.json` é indexado | O indexador só ignora `manifest.json` | Ignorar também `ingestion_manifest.json` |

> Os itens 1–4 somam 26 blocos (camada E; o item 7 trata do mesmo bloco de `ingestion_manifest.json` já contado no item 1). Removê-los leva o índice a **2.257** blocos; o benchmark de 18 cenários precisaria ser reexecutado para o relatório refletir o novo número.

---

## 8. Governança e privacidade

* Os arquivos de `corpus/`, `raw/` e `eval/` não contêm registros individuais de pacientes; são textos institucionais, cadastros de estabelecimentos e exemplos de perguntas.
* Os arquivos de `eda_inputs/` são bases públicas do DF em formato agregado (cada linha traz uma coluna de quantidade, sem identificação de pessoas).
* A rastreabilidade por bloco depende do campo `url`; para as camadas B e C ele aponta para páginas oficiais, e para a camada D não é confiável (seção 4).
