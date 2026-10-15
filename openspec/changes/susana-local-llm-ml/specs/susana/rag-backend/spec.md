# Specs: RAG Backend

O módulo de RAG deve interagir com os LLMs e a base de vetores de forma agnóstica através de portas.

- **MUST** suportar requisições assíncronas ao provedor de LLM.
- **MUST** implementar fallback se o LLM não estiver disponível.
- **MUST** garantir que as fontes sejam rastreadas e expostas ao frontend.

## Cenários de Falha (LLM e Retriever)

**Cenário:** O serviço local do LLM cai (Timeout).
- **WHEN** o pipeline de RAG tenta acionar o `OllamaAdapter` para gerar a resposta.
- **AND** a conexão falha ou dá timeout (>10 segundos).
- **THEN** o adaptador de LLM levanta a exceção `LLMUnavailable`.
- **AND** o RAG Pipeline captura o erro e entra em **Fallback Extrativo**.
- **AND** o backend retorna o texto dos documentos recuperados concatenados (como resposta final), omitindo a geração de texto.

**Cenário:** A base de vetores ChromaDB está vazia ou sem documentos para o domínio.
- **WHEN** o usuário faz uma pergunta sobre um assunto que não consta nos documentos (ex: "Qual a receita para bolo?").
- **AND** o `ChromaRetriever` não recupera nenhum documento acima do threshold de similaridade.
- **THEN** o pipeline injeta um prompt de controle instruindo o LLM a responder "Não encontrei informações nos canais oficiais da SES-DF sobre esse tema".
