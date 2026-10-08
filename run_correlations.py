import pandas as pd
import numpy as np

# This is a scratch script to run basic tests on the data for OpenSpec docs.
print("Loading data...")

# Helper to load safely
def load_csv(path):
    try:
        df = pd.read_csv(path, sep=';', encoding='iso-8859-1', on_bad_lines='skip')
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

obitos = load_csv('CORPUS/obitos-ocorridos-no-df/Óbitos Ocorridos no DF - 2022.csv')
samu = pd.read_csv('CORPUS/Samu/dados_producao_samu-29092026-.csv', encoding='utf-8', on_bad_lines='skip')
samu.columns = [c.strip().lower() for c in samu.columns]

# Print initial shapes
print(f"Obitos shape: {obitos.shape}")
print(f"SAMU shape: {samu.shape}")

# Test 1: Correlation by Region
print("\n--- Test 1: By Region ---")
try:
    o_reg = obitos.groupby('i_desc_regiao_saude_res')['i_qtd_obitos'].sum().reset_index()
    print("Obitos by region:\n", o_reg.head())
    
    s_reg = samu.groupby('i_desc_regiao_saude')['i_qtd_aprovada'].sum().reset_index()
    print("SAMU by region:\n", s_reg.head())
    
    # Normalizing names for merge
    o_reg['region'] = o_reg['i_desc_regiao_saude_res'].str.replace('Região ', '', regex=False).str.strip().str.lower()
    s_reg['region'] = s_reg['i_desc_regiao_saude'].str.strip().str.lower()
    
    merged = pd.merge(o_reg, s_reg, on='region', how='inner')
    
    corr_pearson = merged['i_qtd_obitos'].corr(merged['i_qtd_aprovada'], method='pearson')
    corr_spearman = merged['i_qtd_obitos'].corr(merged['i_qtd_aprovada'], method='spearman')
    
    print(f"Pearson Correlation (Obitos vs SAMU by Region): {corr_pearson:.3f}")
    print(f"Spearman Correlation (Obitos vs SAMU by Region): {corr_spearman:.3f}")
except Exception as e:
    print(f"Error in Test 1: {e}")

# Test 2: Correlation by Month
print("\n--- Test 2: By Month ---")
try:
    o_month = obitos.groupby('i_mes_obito')['i_qtd_obitos'].sum().reset_index()
    s_month = samu.groupby('i_mes_compt')['i_qtd_aprovada'].sum().reset_index()
    
    merged_m = pd.merge(o_month, s_month, left_on='i_mes_obito', right_on='i_mes_compt', how='inner')
    corr_pearson_m = merged_m['i_qtd_obitos'].corr(merged_m['i_qtd_aprovada'], method='pearson')
    corr_spearman_m = merged_m['i_qtd_obitos'].corr(merged_m['i_qtd_aprovada'], method='spearman')
    
    print(f"Pearson Correlation (Obitos vs SAMU by Month): {corr_pearson_m:.3f}")
    print(f"Spearman Correlation (Obitos vs SAMU by Month): {corr_spearman_m:.3f}")
except Exception as e:
    print(f"Error in Test 2: {e}")

print("\nTests complete.")
