## Purpose
Filtra ativamente requisições antes que atinjam o RAG/LLM principal, identificando e bloqueando perguntas de cunho clínico ou de diagnóstico individual.

## ADDED Requirements

### Requirement: Bloqueio de questões clínicas
O sistema SHALL classificar as consultas recebidas dos usuários e bloquear aquelas que buscam diagnósticos clínicos, tratamentos ou prescrições.

#### Scenario: Usuário pede diagnóstico
- **WHEN** o usuário digita "que remédio devo tomar para dor de cabeça"
- **THEN** o guardrail retorna uma resposta imediata de "Fora de escopo" rejeitando a consulta clínica

### Requirement: Roteamento rápido pré-LLM
O sistema SHALL executar a avaliação do guardrail rapidamente, adicionando sobrecarga mínima antes de atingir a recuperação de documentos ou geração principal.

#### Scenario: Consulta administrativa normal
- **WHEN** o usuário digita "quais são os horários da UBS"
- **THEN** o guardrail permite que a consulta prossiga para o pipeline RAG principal sem atraso significativo
