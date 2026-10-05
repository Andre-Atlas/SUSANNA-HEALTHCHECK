# Pasta `tests/`

Contém os testes automatizados do projeto, organizados por área: busca gov.br, política de citações, grounding, fila de pedidos, base SQLite, interface, demonstração externa e outros componentes.

`frontend_harness.js` oferece um ambiente auxiliar para testes da interface acionados pela suíte Python; executá-lo sozinho não equivale a executar todos os testes comportamentais.

Os testes verificam o código, mas seus arquivos não são usados pelo servidor para responder perguntas. Resultados de teste devem ser associados ao código e ambiente em que foram executados.
