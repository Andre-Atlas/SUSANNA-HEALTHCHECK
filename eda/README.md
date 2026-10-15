# Análise Exploratória de Dados (EDA)

Este diretório reúne as análises exploratórias que subsidiaram as decisões de dados e de RAG do projeto **SUSANA**. Cada subpasta traz um notebook autocontido, com as saídas já executadas.

---

## 📂 Notebooks

### 1. `eda_cartilha/`
* **Notebook:** [`eda_cartilha.ipynb`](eda_cartilha/eda_cartilha.ipynb)
* **Pergunta central:** a Carta de Serviços ao Cidadão 2026 (cartilha da SES-DF) está pronta para ser base de conhecimento do chatbot?
* **O que faz:** análise descritiva de um único documento — qualidade da extração, tamanho das seções, telefones/horários/endereços/links, siglas, similaridade (TF-IDF e cosseno), cobertura de serviços e simulação de chunking para o RAG.
* **Entradas externas (não versionadas):** `cartilha_secoes.csv` (extraído do PDF) e o PDF da Carta de Serviços, procurados em `data/raw/` ou na raiz do notebook.

### 2. `eda_vacinas_aplicadas/`
* **Notebook:** [`eda_vacinas_aplicadas.ipynb`](eda_vacinas_aplicadas/eda_vacinas_aplicadas.ipynb)
* **Fonte:** InfoSaúde-DF (e-SUS/SIES), exportação de 22/09/2026.
* **O que faz:** perfil das vacinações aplicadas na Atenção Primária **em agosto de 2026** (um corte mensal): volume diário, vacinas e estratégias, doses, faixa etária, sexo, distribuição por região administrativa e qualidade dos dados.
* **Entrada externa (não versionada):** `dados_vacinas_aplicadas-24092026-anos_2026-meses_08.csv`, lido a partir do diretório do notebook.
* **Observação:** os gráficos são gravados em `/tmp/` durante a execução.

### 3. `eda_sus_digital/`
* **Notebook:** [`eda_sus_digital.ipynb`](eda_sus_digital/eda_sus_digital.ipynb)
* **O que faz:** limpeza e cruzamento de bases públicas de saúde do DF — óbitos 2022, produção do SAMU, atendimentos e consultas 2022 e cirurgias 2022 — com população por região (Censo 2022, em [`auxiliary_data.py`](eda_sus_digital/auxiliary_data.py)). Calcula correlação mensal entre óbitos e chamados do SAMU, infere a região de saúde do SAMU a partir da sigla do estabelecimento e exporta tabelas limpas em Parquet.
* **Entradas versionadas:** [`datasets/eda_inputs/`](../datasets/eda_inputs/). Saídas em `datasets/processed/` (criada na execução).
* **Dependências:** `pandas`, `numpy`, `plotly`, `scipy`, `pyarrow`.

> A célula inicial do notebook menciona também "Exames de Internação", mas essa base não é carregada nas células seguintes.

---

## 🔗 Relação com o restante do repositório

Os notebooks desta pasta são a versão organizada para entrega. Versões de trabalho anteriores (incluindo a avaliação do modelo de guardrails) estão em [`notebooks/`](../notebooks/), e os scripts que os geram em [`scripts/notebooks/`](../scripts/notebooks/).
