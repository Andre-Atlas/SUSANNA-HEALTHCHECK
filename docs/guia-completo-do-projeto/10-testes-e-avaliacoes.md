# 10. Testes e avaliações

Os arquivos em `tests/` contêm testes automatizados de módulos, contratos e casos de segurança. A suíte pode ser executada com `python -m unittest discover -s tests -v`, sujeito a Python acessível. Alguns testes precisam de rede simulada; os avaliadores que chamam Ollama exigem o serviço/modelo. O harness JS é auxiliar para os testes frontend Python, não uma suíte completa independente.

Ferramentas independentes na raiz:

| Arquivo | O que mede/inspeciona | Requer Ollama/rede? |
|---|---|---|
| `evaluate.py` | Busca local; `--llm` adiciona geração e validação com modelo. | Ollama só com `--llm`; sem rede gov.br no modo padrão. |
| `evaluate_search.py` | Compara busca lexical local e resolução de pergunta. | Não chama LLM nem busca externa. |
| `evaluate_grounding.py` | Casos sintéticos do revisor documental. | Sim, Ollama. |
| `evaluate_acceptance.py` | Fluxo HTTP/jobs e casos de aceitação com banco temporário. | Sim, Ollama e a busca definida nos casos. |
| `benchmark_performance.py` | Latência, estado/versionamento do Ollama e métricas de execução. | Ollama; internet se `--live-search`. |
| `audit_interface.py` | Análise estática de HTML/CSS. | Não precisa navegador nem Ollama. |
| `analyze_evaluations.py` | Consolida relatórios JSON com pandas; opcionalmente registra agregados no MLflow. | Dependências analytics; não faz inferência. |

Relatórios em `evaluation/` são artefatos persistentes. Um relatório histórico só descreve os hashes, versão e condições que registrou; não confirma automaticamente código atual. Avaliações automatizadas verificam critérios programados, não substituem revisão humana de conteúdo de saúde.
