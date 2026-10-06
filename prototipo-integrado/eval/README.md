# Benchmark de Avaliação de Modelos LLM — Susana

Este módulo implementa a infraestrutura de avaliação reproduzível para o assistente de saúde Susana.

## Objetivos
- Testar modelos LLM mantendo o mesmo pipeline RAG, retrieval, prompt e corpus.
- Medir métricas de qualidade (Hit@K, Faithfulness, Correctness, Relevance, Abstention, Policy Compliance, Context e Latência).
- Garantir a reproduzibilidade e facilidade de substituição do modelo via variável de ambiente.

## Estrutura do Módulo

```text
eval/
├── dataset.json                 # Dataset fixo de 40 perguntas (v1.0)
├── runner.py                    # Script de execução do benchmark
├── metrics.py                   # Cálculo de métricas determinísticas e LLM Judge
├── compare.py                   # Gerador de tabela comparativa
├── README.md                    # Documentação
└── results/                     # Resultados salvos por modelo
    ├── llama3.2-3b/
    │   ├── results.json
    │   └── summary.json
    └── qwen3.5-4b/
        ├── results.json
        └── summary.json
```

## Como Executar o Benchmark

### 1. Garantir que a infraestrutura está ativa
- PostgreSQL / pgvector rodando e migrações aplicadas.
- Ollama ativo (`ollama serve`).
- Modelo desejado baixado no Ollama (ex: `ollama pull llama3.2:3b` ou `ollama pull qwen3.5:4b`).

### 2. Configurar o Modelo
Altere o modelo no arquivo `.env` ou passe via variável de ambiente:

```bash
# Exemplo para o modelo Baseline
export OLLAMA_MODEL=llama3.2:3b

# Ou para o candidato
export OLLAMA_MODEL=qwen3.5:4b
```

### 3. Rodar a Avaliação
A partir do diretório `prototipo-integrado`:

```bash
./.venv/bin/python -m eval.runner
```

Os resultados serão salvos em `eval/results/<nome-do-modelo>/`.

### 4. Gerar Tabela Comparativa
Para comparar todas as execuções salvas:

```bash
./.venv/bin/python -m eval.compare
```

## Métricas Medidas

1. **Retrieval Hit@K**: Verifica se a fonte esperada está presente nos top K resultados do RAG.
2. **Faithfulness**: Avalia se as afirmações da resposta são fundamentadas nas evidências.
3. **Correctness**: Avalia se os fatos esperados estão presentes.
4. **Relevance**: Avalia se responde diretamente à pergunta do usuário.
5. **Abstention Accuracy**: Avalia a precisão de se abster quando não há evidência (`NO_EVIDENCE`), pedir esclarecimento (`NEEDS_CLARIFICATION`) ou recusar perguntas fora de escopo (`OUT_OF_SCOPE`).
6. **Policy Compliance**: Verifica se a resposta respeita as diretrizes de segurança da Susana (sem prescrições, diagnósticos ou dados inventados).
7. **Conversational Context**: Verifica o uso correto do histórico nas perguntas da Categoria F.
8. **Latência**: Tempo total de resposta do pipeline em milissegundos (`latency_ms`).
