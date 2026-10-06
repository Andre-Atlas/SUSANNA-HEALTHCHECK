# 12. Mapa de arquivos e pastas

## Código da conversa

`index.html`, `styles.css`, `app.js`, `server.py`, `jobs.py`, `conversation.py`, `govbr_search.py`, `ollama_transport.py` e `answer_policy.py` formam o caminho principal do chat local. Veja [interface](04-interface.md) e [fluxo](03-fluxo-completo-do-chat.md).

## Ferramentas auxiliares

- `evaluate*.py`, `benchmark_performance.py`, `audit_interface.py`, `analyze_evaluations.py`: avaliações/análises manuais.
- `knowledge.py`, `seed_knowledge.py`, `operations.py`: busca e manutenção offline.
- `internet_demo.py`, `internet_app.py`, `internet_state.py`, `configurar_ngrok.py`: acesso remoto temporário opcional.
- `requirements-analytics.txt`, `requirements-internet.txt`: dependências opcionais desses fluxos.
- `README.md`, `docs/`, `LICENSE`, `.gitignore`: orientação, documentação, licença e controle de arquivos.

## Diretórios

| Diretório | Uso |
|---|---|
| `docs/` | Documentação humana. |
| `sources/` | Fontes JSON do conjunto experimental offline. |
| `sources/retiradas/` | Fontes arquivadas fora do carregamento automático do seed. |
| `data/` | SQLite documental local, ignorado pelo Git. |
| `evaluation/` | Casos e resultados de avaliações; relatórios podem persistir/versionar. |
| `tests/` | Testes automatizados e harness frontend. |
| `piloto/` | Materiais de piloto. |
| `backups/` | Cópias locais, ignoradas pelo Git. |
| `.venv/`, `__pycache__/` | Ambiente e caches locais/gerados. |
| `.internet/` | Local opcional para binários de túnel. |
| `.mlflow/` | Tracking MLflow configurado pelos scripts. |
| `.git/` | Metadados internos do Git; não editar manualmente. |
| `.vscode/` | Preferências do editor. |

As regras efetivas de exclusão estão em [`.gitignore`](../../.gitignore). Ser ignorado não apaga arquivo já versionado: por exemplo, `mlflow.db` na raiz aparece versionado, embora o tracking atual use `.mlflow/mlflow.db`.
