# EDA da Carta de Serviços ao Cidadão 2026

Este projeto faz uma análise exploratória e diagnóstica da Carta de Serviços ao Cidadão 2026, da Secretaria de Saúde do Distrito Federal, para preparar uma base de conhecimento de um chatbot RAG sobre o SUS.

## Ambiente

Requer Python 3.10 ou superior. O ambiente observado neste projeto foi Python 3.14.6. A instalação é local e não exige permissões administrativas:

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Se a instalação local não for possível, o notebook pode ser executado no Google Colab após o upload da pasta e dos arquivos de entrada.

## Como executar

Os arquivos brutos devem ficar em `data/raw/`. Nesta entrega, os arquivos originais permanecem na raiz para compatibilidade com a configuração inicial; copie-os para `data/raw/` antes de uma execução independente:

```bash
mkdir -p data/raw
cp cartasus.pdf cartilha.md cartilha_secoes.csv cartilha_secoes.json data/raw/
source .venv/bin/activate
jupyter nbconvert --to notebook --execute --inplace notebooks/02_eda_cartilha.ipynb --ExecutePreprocessor.timeout=600
jupyter nbconvert --to html notebooks/02_eda_cartilha.ipynb --output-dir=.
```

O PDF disponível nesta execução chama-se `cartasus.pdf`; a configuração do notebook aceita esse nome e também `cartilha.pdf`.

## Estrutura

- `data/raw/`: cópias dos arquivos originais, nunca alteradas pelo notebook.
- `data/processed/`: CSV, JSON e JSONL limpos e prontos para inspeção/pipeline.
- `notebooks/02_eda_cartilha.ipynb`: análise executada, em português do Brasil.
- `reports/figures/`: gráficos PNG em 150 dpi.
- `requirements.txt`: versões do ambiente usadas na execução.

## Decisões provisórias

A extração possui 124 linhas, muitos títulos genéricos repetidos e textos vazios. Por isso, a divisão original é preservada para auditoria, mas a versão recomendada para RAG agrupa os blocos por serviço do sumário, mantendo página e metadados de cada bloco. Seções longas são candidatas a subdivisão sem perder o título do serviço; títulos órfãos e resíduos de QR code devem passar por validação humana antes de exclusão.

O notebook mede telefones, horários, links, e-mails e endereços por regex, calcula TF-IDF, similaridade, agrupamentos exploratórios e simula chunking. Os números e gráficos são sempre recalculados na execução; não há resultados preenchidos manualmente.

## Limitações

O corpus é um único documento, com amostra pequena de seções. A conversão PDF pode ter perdido a ordem de tabelas e colunas. Tokens são estimados a partir de palavras, regexes podem gerar falsos positivos e tópicos/clusters são exploratórios. Antes de colocar a base em produção, valide links, horários, telefones, cobertura por serviço e atualidade das informações.
