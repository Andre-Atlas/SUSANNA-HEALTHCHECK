# Pastas do projeto

Este índice explica as pastas encontradas no repositório. Algumas são parte do código e dos dados versionados; outras são locais, geradas automaticamente ou usadas apenas em fluxos opcionais.

## Pastas do repositório

- [`docs/`](pasta-docs.md): documentação, guias e registros do projeto.
- [`evaluation/`](pasta-evaluation.md): casos e resultados de avaliações do chatbot.
- [`piloto/`](pasta-piloto.md): materiais da execução piloto e feedback.
- [`sources/`](pasta-sources.md): documentos JSON usados na base local de avaliação/offline.
- [`sources/retiradas/`](pasta-sources-retiradas.md): cópias arquivadas de fontes removidas do conjunto ativo.
- [`tests/`](pasta-tests.md): testes automatizados e apoio para teste da interface.
- [`backups/`](pasta-backups.md): cópias de segurança locais; não são a base em uso.
- [`data/`](pasta-data.md): arquivo SQLite local, usado por avaliações offline e manutenção.

## Pastas locais, opcionais ou geradas

- [`__pycache__/`](pasta-pycache.md): bytecode Python criado automaticamente.
- [`tests/__pycache__/`](pasta-tests-pycache.md): bytecode gerado ao importar os módulos de teste.
- [`.internet/`](pasta-internet.md): local opcional para executáveis de túnel da demonstração externa.
- [`.mlflow/`](pasta-mlflow.md): dados locais de acompanhamento de avaliações no MLflow.
- [`.venv/`](pasta-venv.md): ambiente virtual Python deste computador.
- [`.vscode/`](pasta-vscode.md): configurações locais do Visual Studio Code.
- [`.git/`](pasta-git.md): metadados e histórico do Git.

O `.gitignore` exclui do Git as pastas locais e artefatos que não devem ser compartilhados, como ambientes virtuais, caches, backups e dados locais. Não apague uma pasta só por ela estar ignorada: primeiro confirme se alguma ferramenta ou fluxo local depende dela.
