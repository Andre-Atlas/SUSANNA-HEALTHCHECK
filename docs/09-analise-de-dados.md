# 9. Análise de dados (EDA) — a trilha de ciência de dados

Além do chatbot, o repositório tem uma trilha de **análise exploratória** das bases de dados abertos da saúde do DF. Ela é **independente** do chatbot: nenhum resultado desta etapa é lido pelo backend da Susana hoje.

Os resultados numéricos (correlações e diagnósticos) estão em [analysis_process.md](analysis_process.md). Este documento explica **o código e os dados** que os produziram.

## As bases brutas (raiz do repositório)

| Pasta | Conteúdo | Tamanho | Formato |
| --- | --- | --- | --- |
| `Samu/` | Produção do SAMU (`dados_producao_samu-29092026-.csv`) | 3 MB | `,` UTF-8 |
| `obitos-ocorridos-no-df/` | Óbitos 2022 e 2023 | 8 MB | `;` ISO-8859-1 |
| `atendimentos-e-consultas/` | SIA mensal 2017–2018 + anual 2019–2023, metadados (PDF) e dicionário (HTML) | 868 MB | `;` ISO-8859-1 |
| `Exames-Internação/` | 2022 e 2023 | 8 MB | `;` ISO-8859-1 |
| `cirurgias-producao-ambulatorial/` | 2022 e 2023 | 0,8 MB | `;` ISO-8859-1 |

As colunas seguem o padrão `i_<nome>` (ex.: `i_mes_obito`, `i_qtd_aprovada`, `i_desc_regiao_saude_res`). Todos os scripts convertem os nomes de colunas para minúsculas e removem espaços.

## Os scripts

| Arquivo | O que faz | Como rodar |
| --- | --- | --- |
| [run_correlations.py](../run_correlations.py) | Primeira versão ("scratch"): correlação Óbitos × SAMU por região e por mês, com `pandas.corr` | `python run_correlations.py` |
| [analysis_tests.py](../analysis_tests.py) | Versão usada no `analysis_process.md`: Pearson e Spearman com `scipy.stats` para Óbitos × SAMU e Atendimentos × Cirurgias por mês; mostra o problema espacial | `python analysis_tests.py` |
| [notebooks/auxiliary_data.py](../notebooks/auxiliary_data.py) | Tabela de **população por Região Administrativa** (Censo IBGE 2022) e o de-para **RA → Região de Saúde** | importado pelo notebook |
| [build_notebook.py](../build_notebook.py) | **Gera** o notebook `notebooks/EDA_SUS_Digital.ipynb` programaticamente (via `nbformat`) | `python build_notebook.py` |
| `notebooks/EDA_SUS_Digital.ipynb` | O notebook de EDA (12 células) | Jupyter, a partir de `notebooks/` |
| [gerar_pdf_arquitetura.py](../gerar_pdf_arquitetura.py) | Gera o `Projeto_Susana_Visao_Geral.pdf` (visão arquitetural em texto) | `python gerar_pdf_arquitetura.py` (precisa de `fpdf2`) |

Todos precisam ser executados **a partir da raiz** do repositório, porque usam caminhos relativos. A exceção é o notebook, que usa `../` e roda de dentro de `notebooks/`. Dependências: `pandas`, `scipy`, `plotly`, `nbformat`, `pyarrow` e `fpdf2`. Não existe um `requirements.txt` para esta parte.

## O que o notebook faz, célula a célula

1. **Introdução:** lista as bases.
2. **Imports e configuração:** pandas, numpy, plotly, scipy; cria `data/processed/`.
3. **Carregamento:** a função `load_and_clean_csv` lê com o encoding/separador certo, pula linhas quebradas e padroniza as colunas. Carrega Óbitos, SAMU, Atendimentos e Cirurgias de 2022.
4. **Dados externos (IBGE):** importa `df_pop_regiao` de `auxiliary_data.py`, com a população somada por Região de Saúde (Central, Centro-Sul, Norte, Oeste, Sul, Sudoeste, Leste).
5. **Eixo temporal:** soma óbitos por mês e chamados do SAMU de 2022 por mês, junta pelo mês, calcula Pearson e Spearman e plota a linha "Óbitos vs Chamados SAMU".
6. **Eixo espacial:** a coluna de região do SAMU vem sempre como "SAMU". A função `extrator_regiao_samu` deduz a região a partir da sigla do estabelecimento (`sob` → Norte, `ceil`/`braz` → Oeste, `tagu`/`samam` → Sudoeste…). Depois junta com os óbitos por região, divide pela população e plota a dispersão **taxa por 100 mil habitantes** (SAMU × Óbitos).
7. **Exportação:** salva `data/processed/samu_2022.parquet` e `data/processed/obitos_2022.parquet` com as colunas úteis.

## Principais conclusões (resumo do `analysis_process.md`)

| Cruzamento (2022, por mês) | Pearson | Spearman | Leitura |
| --- | --- | --- | --- |
| SAMU × Óbitos | 0,604 | 0,294 | Os volumes andam juntos, mas a ordem dos meses mais intensos difere |
| Atendimentos × Cirurgias | 0,637 | 0,776 | Relação forte e monotônica: mais consultas → mais cirurgias |

**Por região**, o cruzamento direto é impossível sem tratamento: os óbitos têm 8 regiões, e o SAMU reporta tudo como uma única região "SAMU".

## Pontos de atenção nos dados processados

Verificados nos arquivos `.parquet` atuais:

- **`samu_2022.parquet` não é só de 2022.** Ele tem 10.109 linhas de **2015 a 2026**, porque a exportação no notebook não filtra o ano (o filtro `== 2022` só é aplicado no gráfico temporal).
- **46% das linhas do SAMU ficaram com região "Desconhecida"** (4.690 de 10.109). A regra por palavras-chave na sigla do estabelecimento cobre pouco.
- O motivo principal são as **abreviações**. As siglas reais usam formas que as palavras-chave não pegam: `SAMU USA P. Piloto` (a regra procura "plano"), `SAMU USB Plan. I` (Planaltina não tem regra), `SAMU USA Recanto das Emas` (sem regra). Além delas, ficam sem região as centrais `SAMU CRDF`, `NUSAM`, `Neo` e `Aeromédico`, que de fato não têm região única.
- `obitos_2022.parquet` tem 17.228 linhas com CID do óbito e região de residência.
- O título da seção 5 do notebook diz "Exportação para RAG", mas **o backend da Susana não lê esses parquets**. O RAG usa só os textos em `susana_rag_backend/data/corpus/`.

## Relação com o chatbot

Hoje, nenhuma. A intenção declarada (seção 5 do notebook e `analysis_process.md`) é que os dados tratados alimentem o RAG no futuro, por exemplo para responder "quantos atendimentos o SAMU fez na Região Oeste?". Para isso, seria preciso converter os agregados em blocos de texto no formato `[TAG] Título` (veja [06-corpus-e-indexacao.md](06-corpus-e-indexacao.md)) ou criar uma ferramenta de consulta estruturada.
