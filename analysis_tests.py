import pandas as pd
import scipy.stats as stats

obitos = pd.read_csv('CORPUS/obitos-ocorridos-no-df/Óbitos Ocorridos no DF - 2022.csv', sep=';', encoding='iso-8859-1', on_bad_lines='skip')
obitos.columns = [c.strip().lower() for c in obitos.columns]

samu = pd.read_csv('CORPUS/Samu/dados_producao_samu-29092026-.csv', sep=',', encoding='utf-8', on_bad_lines='skip')
samu.columns = [c.strip().lower() for c in samu.columns]

atend = pd.read_csv('CORPUS/atendimentos-e-consultas/2022 - Atendimentos e Consultas _ambulatório e emergência_.csv', sep=';', encoding='iso-8859-1', on_bad_lines='skip')
atend.columns = [c.strip().lower() for c in atend.columns]

cirurgias = pd.read_csv('CORPUS/cirurgias-producao-ambulatorial/2022 - Cirurgias Produção Ambulatorial.csv', sep=';', encoding='iso-8859-1', on_bad_lines='skip')
cirurgias.columns = [c.strip().lower() for c in cirurgias.columns]

print("# Teste 1: Temporal (Agrupado por Mês)")
o_mes = obitos.groupby('i_mes_obito')['i_qtd_obitos'].sum().reset_index()
s_mes = samu[samu['i_ano_compt'] == 2022].groupby('i_mes_compt')['i_qtd_aprovada'].sum().reset_index()
a_mes = atend.groupby('i_mes_compt')['i_qtd'].sum().reset_index()
c_mes = cirurgias.groupby('i_mes_compt')['i_qtd'].sum().reset_index()

# SAMU vs Obitos
merged_m = pd.merge(o_mes, s_mes, left_on='i_mes_obito', right_on='i_mes_compt', how='inner')
if len(merged_m) > 2:
    pm, p_pm = stats.pearsonr(merged_m['i_qtd_obitos'], merged_m['i_qtd_aprovada'])
    sm, p_sm = stats.spearmanr(merged_m['i_qtd_obitos'], merged_m['i_qtd_aprovada'])
    print(f"SAMU vs Óbitos (Mês) -> Pearson: {pm:.3f}, Spearman: {sm:.3f}")
else:
    print(f"SAMU vs Óbitos (Mês) -> Sem sobreposição de dados no mesmo ano (len={len(merged_m)})")

# Atendimentos vs Cirurgias
merged_ac = pd.merge(a_mes, c_mes, on='i_mes_compt', how='inner')
if len(merged_ac) > 2:
    pac, p_pac = stats.pearsonr(merged_ac['i_qtd_x'], merged_ac['i_qtd_y'])
    sac, p_sac = stats.spearmanr(merged_ac['i_qtd_x'], merged_ac['i_qtd_y'])
    print(f"Atendimentos vs Cirurgias (Mês) -> Pearson: {pac:.3f}, Spearman: {sac:.3f}")

print("\n# Teste 2: Espacial (Agrupado por Região de Saúde)")
o_reg = obitos.groupby('i_desc_regiao_saude_res')['i_qtd_obitos'].sum().reset_index()
o_reg['region'] = o_reg['i_desc_regiao_saude_res'].str.replace('Região ', '', regex=False).str.strip().str.lower()
a_reg = atend.groupby('i_desc_complex_proc')['i_qtd'].sum().reset_index() # Atendimentos doesnt seem to have region easily accessible, let's use estab_cnes
print(f"Óbitos agrupados espacialmente geram {len(o_reg)} regiões únicas.")

# Show SAMU centralizado
s_reg_unique = samu['i_desc_regiao_saude'].unique()
print(f"SAMU Regiões Únicas na coluna 'i_desc_regiao_saude': {s_reg_unique}")

