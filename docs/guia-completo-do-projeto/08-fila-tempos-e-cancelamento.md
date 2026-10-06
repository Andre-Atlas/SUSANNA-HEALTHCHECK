# 8. Fila, tempos e cancelamento

## Capacidade padrão

No comando normal, `--concurrency 1 --queue-size 3` permite um trabalho em execução e até três esperando. O valor de concorrência aceita 1–4; a capacidade da fila aceita 0–16. O limite de submissões é a concorrência mais a capacidade; pedidos além disso recebem 429. Configuração em [`server.py`](../../server.py#L547) e aplicação em [`JobQueue.submit()`](../../jobs.py#L100).

## Etapas medidas

O helper `stage()` marca durações, em especial `retrieval`, `generation` e `review`; a fila registra `queue` e `total`. `ollama_transport.py` registra também tempo até o primeiro fragmento de geração ou revisão. `/api/metrics` retorna os últimos 100 registros em memória e os contadores active/waiting; não inclui o texto do chat.

Os tempos não são todos Ollama: `retrieval` depende da rede SERPRO/gov.br; o total inclui espera da fila. Em logs do Ollama, `prompt eval` é processamento do prompt e `eval` é geração de saída. Uma chamada individual não mede necessariamente o fluxo inteiro, porque a geração e a revisão podem ser duas chamadas.

## Prazos e cancelamento

Defaults da fila em [`jobs.py`](../../jobs.py#L100-L112): 120 s em espera, 360 s em execução, lease de 20 s sem o cliente acompanhar e retenção do resultado por 60 s. Há limite adicional de no máximo 32 resultados finalizados guardados. Polling atualiza a atividade do job. Cancelar marca o job e tenta fechar o socket upstream, inclusive a chamada de Ollama; fechar uma conexão não é garantia de que toda operação de rede remota foi revertida instantaneamente.

## Como diagnosticar demora

Leia `timings.queue`, `timings.retrieval`, `timings.generation`, `timings.review` e `timings.total` no `/api/metrics` ou no estado do job. Se `retrieval` dominar, verifique rede/portal; se `generation` ou `review` dominar, verifique modelo e CPU/GPU; se `queue` dominar, há concorrência insuficiente para o número de pedidos. `benchmark_performance.py` mede amostras controladas, mas não representa disponibilidade permanente.
