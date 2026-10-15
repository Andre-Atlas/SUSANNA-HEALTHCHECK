## Purpose
Gerencia o ciclo de vida dos modelos e dados do pipeline RAG.

## ADDED Requirements

### Requirement: Versionamento de Dados
O sistema SHALL versionar os conjuntos de dados de documentos usando DVC.

#### Scenario: Atualização de corpus
- **WHEN** novos documentos são adicionados ao corpus
- **THEN** o pipeline DVC rastreia as alterações e cria uma nova versão reproduzível

### Requirement: Rastreamento de Experimentos
O sistema SHALL registrar as métricas e parâmetros dos experimentos de LLM usando MLflow.

#### Scenario: Avaliação de prompt
- **WHEN** um novo prompt ou modelo é testado
- **THEN** o MLflow registra o experimento, latência e as métricas de qualidade

### Requirement: Reprodutibilidade de Artefatos
O sistema SHALL garantir que cada modelo em produção possa ser rastreado até o código, os dados e a configuração originais.

#### Scenario: Deploy do modelo
- **WHEN** um novo modelo RAG é promovido para produção
- **THEN** os artefatos do modelo estão vinculados a um commit específico e versão de dados no registro do MLflow
