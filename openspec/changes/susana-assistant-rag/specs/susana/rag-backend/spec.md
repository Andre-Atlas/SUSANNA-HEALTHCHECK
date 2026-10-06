## Purpose
Processa as requisições do usuário usando RAG (Retrieval-Augmented Generation), garantindo respostas institucionais extraídas exclusivamente de fontes oficiais em menos de 15 segundos.

## ADDED Requirements

### Requirement: Recuperação de Documentos
O sistema SHALL recuperar o contexto relevante de documentos oficiais indexados do SUS-DF para as consultas dos usuários.

#### Scenario: Recuperação de consulta administrativa
- **WHEN** o usuário pergunta sobre a localização de uma clínica
- **THEN** o sistema busca o texto relevante do índice oficial

### Requirement: Geração de Resposta sem Alucinação
O sistema SHALL gerar uma resposta baseada APENAS no contexto recuperado, retornando uma mensagem de fallback específica se nenhuma informação for encontrada.

#### Scenario: Informação ausente
- **WHEN** o contexto recuperado não contém a resposta
- **THEN** o sistema responde indicando que não possui informações oficiais suficientes para responder

### Requirement: Cache Semântico
O sistema SHALL interceptar consultas frequentes usando um cache semântico para reduzir a latência e atingir o SLA de < 15s.

#### Scenario: Consulta em cache
- **WHEN** o usuário faz uma pergunta previamente em cache
- **THEN** o sistema retorna a resposta em cache em menos de 2 segundos sem chamar o LLM

#### Scenario: Cache Redis indisponível
- **WHEN** o Redis está inativo
- **THEN** o sistema faz fallback para chamada direta ao LLM

#### Scenario: Timeout do LLM
- **WHEN** o LLM não responde dentro de 14 segundos
- **THEN** o sistema retorna uma mensagem de fallback de timeout

#### Scenario: Mensagem vazia
- **WHEN** o usuário envia uma string vazia
- **THEN** o sistema retorna um erro de validação
