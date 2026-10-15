# Análise Exploratória e Correlações (SUS Digital)

Este documento centraliza os resultados e os gargalos encontrados na análise multivariada das bases do SUS-DF (Óbitos, SAMU, Atendimentos e Cirurgias). O foco da etapa atual é identificar as diferenças nos resultados analíticos ao variar o parâmetro de agrupamento (Temporal vs. Espacial).

## Resultados dos Parâmetros de Correlação

A mudança do eixo de análise revela discrepâncias nos métodos de correlação (Pearson vs. Spearman) e no formato dos dados de origem.

### Parâmetro Temporal (Mês)

O agrupamento mensal (sazonalidade) é o parâmetro mais limpo para cruzamento, pois as colunas `i_mes_obito` e `i_mes_compt` possuem integridade alta em todas as bases.

*   **SAMU vs. Óbitos (2022)**
    *   `Pearson (Linear)`: 0.604 (Correlação positiva moderada)
    *   `Spearman (Monotônica)`: 0.294 (Correlação positiva fraca)
    *   **Diagnóstico**: Picos sazonais de chamados no SAMU acompanham razoavelmente o aumento de óbitos absolutos naquele mês (Pearson reflete a escala), mas a ordenação (ranking dos meses mais intensos) não é idêntica (Spearman menor).

*   **Atendimentos Ambulatoriais vs. Cirurgias (2022)**
    *   `Pearson (Linear)`: 0.637
    *   `Spearman (Monotônica)`: 0.776
    *   **Diagnóstico**: Existe uma relação temporal forte. Meses com mais triagens/consultas geram monotonicamente mais cirurgias ambulatoriais (Spearman alto captura bem esse funil operacional, ignorando "outliers" de volume bruto).

### Parâmetro Espacial (Região de Saúde)

O agrupamento espacial é problemático e expõe inconsistências sistêmicas entre os domínios, bloqueando cruzamentos diretos sem pré-processamento.

*   **Regiões em Óbitos**: A base gera **8 regiões** consistentes na coluna `i_desc_regiao_saude_res` (ex: Sudoeste, Central, Sul).
*   **Regiões em SAMU**: A base reporta apenas **1 região** fixa na coluna correspondente (`i_desc_regiao_saude` = "SAMU"). A operação do SAMU é reportada de forma centralizada pelo CNPJ/CNES gestor, ignorando a localidade do evento na coluna principal.
*   **Diagnóstico**: O cruzamento espacial direto resulta em erro (`ValueError: x and y must have length at least 2`) por ausência de intersecção geográfica limpa.

## Resoluções de Engenharia para o Jupyter Notebook

Para que a análise multivariada no notebook prossiga e os modelos `.parquet` fiquem consistentes para a futura arquitetura RAG:

1.  **Dedução Espacial do SAMU**: Abandonar a coluna `i_desc_regiao_saude`. Em vez disso, extrair a região aplicando Regex na coluna de texto livre do estabelecimento (`i_desc_sigla_estab_cnes`), que contém marcações como "SAMU USB Sob. I" (Sobradinho -> Região Norte).
2.  **Métrica de Taxa**: Aplicar o dicionário de População (IBGE 2022) cruzado no script `auxiliary_data.py` sobre os agrupamentos de Região de Saúde para calcular *Taxa por 100 mil habitantes*, evitando que a Região de Ceilândia/Sudoeste (mais populosas) dominem os gráficos de volume absoluto.
