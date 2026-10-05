# Arquivos do projeto

Este índice explica os arquivos visíveis na raiz do repositório. Cada item tem um documento próprio com sua função e como participa do projeto.

## Aplicação do chat

- [index.html](arquivo-index-html.md)
- [styles.css](arquivo-styles-css.md)
- [app.js](arquivo-app-js.md)
- [server.py](arquivo-server-py.md)
- [jobs.py](arquivo-jobs-py.md)
- [conversation.py](arquivo-conversation-py.md)
- [answer_policy.py](arquivo-answer-policy-py.md)
- [ollama_transport.py](arquivo-ollama-transport-py.md)
- [govbr_search.py](arquivo-govbr-search-py.md)

## Avaliação e análise

- [evaluate.py](arquivo-evaluate-py.md)
- [evaluate_search.py](arquivo-evaluate-search-py.md)
- [evaluate_grounding.py](arquivo-evaluate-grounding-py.md)
- [evaluate_acceptance.py](arquivo-evaluate-acceptance-py.md)
- [benchmark_performance.py](arquivo-benchmark-performance-py.md)
- [audit_interface.py](arquivo-audit-interface-py.md)
- [analyze_evaluations.py](arquivo-analyze-evaluations-py.md)
- [requirements-analytics.txt](arquivo-requirements-analytics-txt.md)
- [mlflow.db](arquivo-mlflow-db.md)

## Fontes locais e manutenção

- [knowledge.py](arquivo-knowledge-py.md)
- [seed_knowledge.py](arquivo-seed-knowledge-py.md)
- [operations.py](arquivo-operations-py.md)

## Demonstração temporária pela internet

- [internet_demo.py](arquivo-internet-demo-py.md)
- [internet_app.py](arquivo-internet-app-py.md)
- [internet_state.py](arquivo-internet-state-py.md)
- [configurar_ngrok.py](arquivo-configurar-ngrok-py.md)
- [requirements-internet.txt](arquivo-requirements-internet-txt.md)

## Referência e controle do repositório

- [README.md](arquivo-readme.md)
- [LICENSE](arquivo-license.md)
- [.gitignore](arquivo-gitignore.md)

As ferramentas de avaliação, manutenção e demonstração são executadas separadamente. Em uma conversa normal, o servidor usa os módulos da seção “Aplicação do chat”; o SQLite local é destinado aos fluxos offline descritos nos arquivos correspondentes.
