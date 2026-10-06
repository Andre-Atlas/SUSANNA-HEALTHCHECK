## Purpose
Fornece a interface visual de chat (Frontend React/Next.js) para que os cidadãos do DF interajam com a Susana, exibindo informações claras e citações das fontes.

## ADDED Requirements

### Requirement: Interação no chat
O sistema SHALL fornecer uma interface de chat onde os usuários possam digitar perguntas e receber respostas do assistente de IA.

#### Scenario: Usuário recebe resposta
- **WHEN** o usuário faz uma pergunta administrativa
- **THEN** o sistema exibe a resposta do assistente dentro do SLA de 15 segundos

### Requirement: Renderização de citação de fonte
O sistema SHALL renderizar citações de fontes oficiais (links ou referências) associadas à resposta do assistente.

#### Scenario: A resposta inclui a fonte
- **WHEN** o backend retorna uma resposta com um documento fonte
- **THEN** a UI exibe um componente de citação clicável dentro do balão de mensagem do assistente

### Requirement: Aviso visual fora de escopo
O sistema SHALL distinguir visualmente respostas que estão fora do escopo permitido (por exemplo, questões clínicas).

#### Scenario: Usuário faz uma pergunta clínica
- **WHEN** o backend retorna uma resposta fora do escopo
- **THEN** a UI exibe o balão de resposta com uma borda vermelha e ícone de aviso
