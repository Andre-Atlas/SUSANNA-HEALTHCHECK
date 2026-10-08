import nbformat as nbf

nb = nbf.v4.new_notebook()

# Markdown Introdução
nb.cells.append(nbf.v4.new_markdown_cell("""# EDA - SUS Digital DF

Este notebook tem como objetivo a limpeza, normalização e cruzamento de dados de diversas bases da saúde do Distrito Federal.
Bases incluídas:
- Óbitos
- SAMU
- Exames de Internação
- Atendimentos e Consultas
- Cirurgias"""))

# Imports
nb.cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import plotly.express as px
import os
import glob
import scipy.stats as stats

# Configurações para exibição
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

os.makedirs('../data/processed', exist_ok=True)"""))

# Data Cleaning Section
nb.cells.append(nbf.v4.new_markdown_cell("""## 1. Carregamento e Limpeza (Data Cleaning)
A leitura dos arquivos precisa lidar com encoding `latin1` ou `iso-8859-1` e padronizar os nomes das colunas."""))

nb.cells.append(nbf.v4.new_code_cell("""def load_and_clean_csv(file_path, sep=';', encoding='iso-8859-1'):
    try:
        df = pd.read_csv(file_path, sep=sep, encoding=encoding, on_bad_lines='skip')
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return None
    
    # Limpar nomes das colunas
    df.columns = [col.strip().lower() for col in df.columns]
    return df

# Carregando as bases de 2022
obitos = load_and_clean_csv('../CORPUS/obitos-ocorridos-no-df/Óbitos Ocorridos no DF - 2022.csv')
samu = load_and_clean_csv('../CORPUS/Samu/dados_producao_samu-29092026-.csv', sep=',', encoding='utf-8')
atendimentos = load_and_clean_csv('../CORPUS/atendimentos-e-consultas/2022 - Atendimentos e Consultas _ambulatório e emergência_.csv')
cirurgias = load_and_clean_csv('../CORPUS/cirurgias-producao-ambulatorial/2022 - Cirurgias Produção Ambulatorial.csv')

print(f"Óbitos: {obitos.shape[0]} registros")
print(f"SAMU: {samu.shape[0]} registros")"""))

# Demografia
nb.cells.append(nbf.v4.new_markdown_cell("""## 2. Ingestão de Dados Externos (IBGE)
Para fazer a análise espacial corretamente, não podemos comparar Regiões populosas com as menos populosas apenas por volume. Abaixo, carregamos o de-para de População por Região de Saúde."""))

nb.cells.append(nbf.v4.new_code_cell("""import sys
sys.path.append('.')
from auxiliary_data import df_pop_regiao, populacao_ra_2022

display(df_pop_regiao)"""))

# Análise Multivariada Temporal
nb.cells.append(nbf.v4.new_markdown_cell("""## 3. Análise Multivariada: Eixo Temporal
Comparando o volume de atendimentos SAMU vs. Óbitos reportados no mesmo mês."""))

nb.cells.append(nbf.v4.new_code_cell("""# Agrupando por Mês
o_mes = obitos.groupby('i_mes_obito')['i_qtd_obitos'].sum().reset_index()
s_mes = samu[samu['i_ano_compt'] == 2022].groupby('i_mes_compt')['i_qtd_aprovada'].sum().reset_index()

merged_mes = pd.merge(o_mes, s_mes, left_on='i_mes_obito', right_on='i_mes_compt', how='inner')

# Correlações
pearson_m, p_pm = stats.pearsonr(merged_mes['i_qtd_obitos'], merged_mes['i_qtd_aprovada'])
spearman_m, p_sm = stats.spearmanr(merged_mes['i_qtd_obitos'], merged_mes['i_qtd_aprovada'])
print(f"Pearson (Linear): {pearson_m:.3f} | Spearman (Monotônica): {spearman_m:.3f}")

# Gráfico
fig = px.line(merged_mes, x='i_mes_obito', y=['i_qtd_obitos', 'i_qtd_aprovada'], 
              title='Evolução Mensal (2022): Óbitos vs Chamados SAMU',
              labels={'value': 'Volume', 'i_mes_obito': 'Mês', 'variable': 'Métrica'})
fig.show()"""))

# Análise Multivariada Espacial
nb.cells.append(nbf.v4.new_markdown_cell("""## 4. Análise Multivariada: Eixo Espacial
A base do SAMU tem problema na coluna `i_desc_regiao_saude` (tudo = "SAMU"). A solução é usar regex para extrair a localização a partir da sigla do estabelecimento."""))

nb.cells.append(nbf.v4.new_code_cell("""# Tratando Região do SAMU via texto do CNES
import re

def extrator_regiao_samu(sigla):
    sigla = str(sigla).lower()
    if 'sob' in sigla: return 'Norte'
    if 'ceil' in sigla or 'braz' in sigla: return 'Oeste'
    if 'samam' in sigla or 'tagu' in sigla: return 'Sudoeste'
    if 'gama' in sigla or 'maria' in sigla: return 'Sul'
    if 'guar' in sigla or 'nucleo' in sigla: return 'Centro-Sul'
    if 'paran' in sigla or 'sebast' in sigla: return 'Leste'
    if 'plano' in sigla or 'asa' in sigla or 'norte' in sigla: return 'Central'
    return 'Desconhecida'

samu['regiao_saude_inferida'] = samu['i_desc_sigla_estab_cnes'].apply(extrator_regiao_samu)

s_reg = samu[samu['regiao_saude_inferida'] != 'Desconhecida'].groupby('regiao_saude_inferida')['i_qtd_aprovada'].sum().reset_index()
o_reg = obitos.groupby('i_desc_regiao_saude_res')['i_qtd_obitos'].sum().reset_index()
o_reg['regiao_saude_inferida'] = o_reg['i_desc_regiao_saude_res'].str.replace('Região ', '', regex=False).str.strip()

merged_reg = pd.merge(o_reg, s_reg, on='regiao_saude_inferida', how='inner')

# Aplicar Taxa Populacional (Regiões de Saúde)
df_pop_regiao['regiao_saude_inferida'] = df_pop_regiao['Regiao_Saude']
merged_reg = pd.merge(merged_reg, df_pop_regiao, on='regiao_saude_inferida', how='inner')
merged_reg['taxa_obitos_100k'] = (merged_reg['i_qtd_obitos'] / merged_reg['Populacao_2022']) * 100000
merged_reg['taxa_samu_100k'] = (merged_reg['i_qtd_aprovada'] / merged_reg['Populacao_2022']) * 100000

fig2 = px.scatter(merged_reg, x='taxa_samu_100k', y='taxa_obitos_100k', text='regiao_saude_inferida',
                  title='Dispersão Espacial (Taxas por 100k hab.): SAMU vs Óbitos',
                  size='Populacao_2022', color='regiao_saude_inferida')
fig2.update_traces(textposition='top center')
fig2.show()"""))

# Exportação Parquet
nb.cells.append(nbf.v4.new_markdown_cell("""## 5. Exportação para RAG (Parquet)
Salvando os dados limpos e com as inferências espaciais corrigidas."""))

nb.cells.append(nbf.v4.new_code_cell("""# Selecionar colunas úteis e exportar
samu_clean = samu[['i_ano_compt', 'i_mes_compt', 'regiao_saude_inferida', 'i_desc_sigla_estab_cnes', 'i_desc_proc_realizado', 'i_qtd_aprovada']]
obitos_clean = obitos[['i_ano_obito', 'i_mes_obito', 'i_desc_regiao_saude_res', 'i_desc_cid_obito', 'i_qtd_obitos']]

samu_clean.to_parquet('../data/processed/samu_2022.parquet')
obitos_clean.to_parquet('../data/processed/obitos_2022.parquet')

print("Bases tratadas exportadas para data/processed/ com sucesso.")"""))

nbf.write(nb, 'notebooks/EDA_SUS_Digital.ipynb')
