# `govbr_search.py`

Implementa a recuperação online de fontes. Pode selecionar páginas oficiais específicas para certos temas ou consultar a busca do portal SERPRO; valida os endereços, busca as páginas HTTPS em domínios gov.br, extrai texto HTML e limita o número de fontes e o tamanho dos trechos.

`server.py` chama este módulo para cada pergunta do chat. SERPRO fornece resultados de busca; o conteúdo usado como evidência é extraído das páginas gov.br aceitas. A busca lexical pode selecionar páginas irrelevantes ou não encontrar uma página adequada.
