# 7. Dados abertos e análise exploratória (EDA)

Esta é a outra metade do repositório, feita antes da Susana. Ela **não participa do chat**: é um estudo estatístico de bases públicas de produção do SUS-DF.

Os resultados numéricos desta seção vêm de [analysis_process.md](analysis_process.md), que já existia. Eu não reexecutei os scripts de análise.

## 7.1 As bases

| Pasta | Conteúdo | Tamanho |
|---|---|---|
| `atendimentos-e-consultas/` | Atendimentos ambulatoriais e de emergência. 23 arquivos mensais `SIAmmaaaa.csv` (2017 e 2018), 5 arquivos anuais (2019 a 2023), um PDF de metadados e um dicionário de dados em HTML | 868 MB |
| `Exames-Internação/` | Exames em internações, 2022 e 2023 | 7,8 MB |
| `cirurgias-producao-ambulatorial/` | Cirurgias ambulatoriais, 2022 e 2023 | 824 KB |
| `obitos-ocorridos-no-df/` | Óbitos ocorridos no DF, 2022 e 2023 | 8 MB |
| `Samu/` | Produção do SAMU | 3 MB |

**SIA** é o Sistema de Informações Ambulatoriais do SUS.

Características dos arquivos que o código precisa tratar:

| Característica | Maioria das bases | SAMU |
|---|---|---|
| Separador | `;` | `,` |
| Codificação | ISO-8859-1 (Latin-1) | UTF-8 |

Ler um arquivo Latin-1 como UTF-8 corrompe os acentos ou gera erro. Por isso todos os scripts passam `encoding='iso-8859-1'` e normalizam os nomes das colunas para minúsculas sem espaços.

Colunas do SAMU, como exemplo do padrão: `i_ano_compt`, `i_mes_compt` (ano e mês de competência), `i_desc_proc_realizado` (procedimento), `i_desc_regiao_saude`, `i_desc_sigla_estab_cnes` (sigla do estabelecimento), `i_qtd_aprovada`, `i_val_aprovado`.

## 7.2 Os scripts

| Arquivo | Função |
|---|---|
| [run_correlations.py](../run_correlations.py) | Rascunho inicial: carrega óbitos e SAMU e tenta correlacionar por região e por mês |
| [analysis_tests.py](../analysis_tests.py) | Versão mais completa: quatro bases, Pearson e Spearman com `scipy` |
| [notebooks/auxiliary_data.py](../notebooks/auxiliary_data.py) | População por Região Administrativa (Censo 2022) e mapeamento RA → Região de Saúde |
| [build_notebook.py](../build_notebook.py) | **Gera** o notebook por código, com `nbformat` |
| [notebooks/EDA_SUS_Digital.ipynb](../notebooks/EDA_SUS_Digital.ipynb) | O notebook gerado: limpeza, correlações, gráficos e exportação |
| [gerar_pdf_arquitetura.py](../gerar_pdf_arquitetura.py) | Gera `Projeto_Susana_Visao_Geral.pdf` com a biblioteca `fpdf` |

O notebook não foi escrito à mão: `build_notebook.py` monta as células e grava o `.ipynb`. A vantagem é que o conteúdo fica em um arquivo Python comum, fácil de versionar e revisar.

O PDF de visão geral cita o modelo de embeddings `all-MiniLM-L6-v2`. O código usa `paraphrase-multilingual-MiniLM-L12-v2`. O PDF está desatualizado nesse ponto.

## 7.3 Os dois coeficientes de correlação

| | Pearson (r) | Spearman (ρ) |
|---|---|---|
| Mede | Relação **linear** | Relação **monotônica** (uma sobe quando a outra sobe, não necessariamente em linha reta) |
| Usa | Os valores | Os **postos** (posição no ranking) |
| Sensível a valores extremos | Sim | Pouco |
| Faixa | −1 a +1 | −1 a +1 |

Fórmula de Pearson:

```
r = Σ(xᵢ − x̄)(yᵢ − ȳ) / √[ Σ(xᵢ − x̄)² × Σ(yᵢ − ȳ)² ]
```

Spearman é o Pearson aplicado aos postos das observações.

Quando os dois divergem muito, é sinal de que um ou dois pontos extremos estão dominando o Pearson, ou de que a relação existe mas não é linear.

## 7.4 Resultados no eixo temporal (por mês, 2022)

| Cruzamento | Pearson | Spearman | Leitura do documento original |
|---|---|---|---|
| Chamados do SAMU × Óbitos | 0,604 | 0,294 | Picos coincidem em volume, mas o ranking dos meses não bate |
| Atendimentos ambulatoriais × Cirurgias | 0,637 | 0,776 | Relação monotônica forte: meses com mais consultas têm mais cirurgias |

### Cuidados ao apresentar esses números

- **São 12 pontos** (um por mês). Com n = 12, uma correlação precisa ser de aproximadamente 0,58 em módulo para ser significativa a 5%. O Pearson de 0,604 está no limite; o Spearman de 0,294 **não é estatisticamente distinguível de zero**. Os scripts calculam o p-valor, mas não o exibem nem o registram.
- **Correlação não é causalidade.** SAMU e óbitos podem subir juntos por um terceiro fator, como uma onda de doenças respiratórias no inverno.
- **A diferença entre 0,604 e 0,294** sugere que um ou dois meses atípicos sustentam o Pearson. Olhar o gráfico de dispersão resolveria a dúvida.

## 7.5 O problema do eixo espacial

A ideia era repetir a análise por **Região de Saúde** (Central, Centro-Sul, Norte, Sul, Leste, Oeste, Sudoeste). Não funcionou diretamente:

- A base de **óbitos** tem 8 valores coerentes em `i_desc_regiao_saude_res` (região de residência).
- A base do **SAMU** tem **um único valor** em `i_desc_regiao_saude`: a palavra "SAMU". O serviço é registrado de forma centralizada, sem a localidade do atendimento.

O cruzamento dá um conjunto vazio e o cálculo da correlação lança `ValueError: x and y must have length at least 2`.

### Solução adotada no notebook

**1. Inferir a região do SAMU pelo nome da base.** A coluna `i_desc_sigla_estab_cnes` traz textos como "SAMU USB Sob. I". Uma função procura fragmentos:

| Fragmento | Região atribuída |
|---|---|
| `sob` | Norte |
| `ceil`, `braz` | Oeste |
| `samam`, `tagu` | Sudoeste |
| `gama`, `maria` | Sul |
| `guar`, `nucleo` | Centro-Sul |
| `paran`, `sebast` | Leste |
| `plano`, `asa`, `norte` | Central |

É uma heurística frágil: a ordem dos testes importa e fragmentos curtos podem casar por acidente. Registros sem correspondência viram "Desconhecida" e são excluídos.

**2. Normalizar pela população.** Comparar volumes absolutos favorece as regiões mais populosas. O notebook calcula **taxa por 100 mil habitantes**:

```
taxa = (quantidade ÷ população da região) × 100.000
```

A população vem de `auxiliary_data.py`, que soma as Regiões Administrativas de cada Região de Saúde.

Há ainda uma diferença conceitual que a análise não resolve: óbitos são contados pela região de **residência** do falecido, e o SAMU pela localização da **base da ambulância**. Não são a mesma geografia.

## 7.6 Exportação em Parquet

O notebook grava `data/processed/samu_2022.parquet` e `obitos_2022.parquet`.

**Parquet** é um formato **colunar** e comprimido: guarda os dados por coluna, com os tipos preservados. É muito menor e mais rápido de ler que CSV para análises que usam poucas colunas.

A última seção do notebook chama isso de "Exportação para RAG". **O RAG da Susana não lê esses arquivos.** O chat responde a partir de textos de páginas institucionais, não de estatísticas. Conectar as duas metades (por exemplo, permitir perguntas como "quantos atendimentos do SAMU houve em março de 2022?") é um trabalho futuro que exigiria outra técnica, como geração de consultas a tabelas.

## 7.7 Arquivo sem uso

`data/knowledge.sqlite3` é um banco SQLite com uma tabela de busca textual (`chunks`, do tipo FTS5) **vazia**. Nenhum código do projeto o referencia e ele não está versionado no git. Parece ser resto de uma abordagem anterior de busca por palavras-chave.
