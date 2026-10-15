# Specs: MLOps Pipeline

O sistema deve garantir o rastreamento, controle de versão e reprodutibilidade do classificador ML utilizado para os guardrails.

- **MUST** utilizar DVC para o controle de versão dos datasets de treino e validação.
- **MUST** utilizar MLflow para registrar métricas dos experimentos (ex: F1-Score, precisão, recall).
- **MUST** carregar o classificador ativo utilizando a URI do registry do MLflow, preferencialmente buscando pelo alias `@champion`.

## Cenários de MLOps

**Cenário:** O treinamento é executado, mas a acurácia é baixa (Promotion Gates).
- **WHEN** o cientista de dados ou pipeline CI/CD executa `python ml/guardrails/train.py`.
- **AND** a precisão (precision) do modelo treinado é menor que 0.90 (threshold).
- **THEN** o modelo falha na avaliação e um novo modelo não é promovido a `@champion` no MLflow.

**Cenário:** Rastreabilidade dos dados de treino.
- **WHEN** a versão em produção do classificador de guardrails bloqueia erroneamente uma intenção legítima (Falso Positivo).
- **THEN** a equipe consegue puxar os artefatos de treinamento (dataset `.csv` versionado no DVC) referenciados na run do MLflow associada à versão `@champion`.
- **AND** é possível adicionar o novo exemplo como caso administrativo e re-treinar o modelo com versionamento sem perder o histórico.
