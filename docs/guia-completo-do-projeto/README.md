# Guia completo do SUSANNA-HEALTHCHECK

Este guia descreve o comportamento que foi possível confirmar no código e nas configurações atuais. Ele separa o chat local, os comandos de avaliação/manutenção e a demonstração externa opcional.

## Roteiro de leitura

1. [Visão geral e arquitetura](01-visao-geral.md)
2. [Inicialização](02-inicializacao.md)
3. [Fluxo completo do chat](03-fluxo-completo-do-chat.md)
4. [Interface](04-interface.md)
5. [Servidor e API](05-servidor-e-api.md)
6. [Busca e fontes](06-busca-e-fontes.md)
7. [Ollama, geração e revisão](07-ollama-geracao-e-revisao.md)
8. [Fila, tempos e cancelamento](08-fila-tempos-e-cancelamento.md)
9. [Fontes, SQLite e modo offline](09-fontes-sqlite-e-modos-offline.md)
10. [Testes e avaliações](10-testes-e-avaliacoes.md)
11. [Demonstração externa](11-demonstracao-externa.md)
12. [Mapa de arquivos e pastas](12-mapa-de-arquivos-e-pastas.md)
13. [Segurança, privacidade e limitações](13-seguranca-privacidade-e-limitacoes.md)
14. [Diagramas](14-diagramas.md)

## Como ler as referências

Os links de implementação apontam para arquivos na raiz do repositório e, quando possível, para linhas específicas. As referências ajudam a localizar o código; elas não substituem a leitura do fluxo relacionado.

“Chat local” significa o processo iniciado por `server.py`. “Demonstração externa” significa o modo opcional iniciado por `internet_demo.py`. Os dois chegam ao processamento compartilhado em `server.py`, mas têm entradas e proteções diferentes.

## Limites da documentação

O guia descreve o código presente no workspace e não prova disponibilidade contínua de SERPRO, gov.br ou Ollama. Relatórios antigos podem representar outro estado do código. A avaliação semântica da revisão é feita por outro pedido ao modelo; não é uma validação humana ou clínica.
