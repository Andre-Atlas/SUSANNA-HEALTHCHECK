# Requisitos do Sistema — Susana (Assistente de Informação SUS-DF)

> Documento consolidado de Requisitos Funcionais (RF) e Requisitos Não Funcionais (RNF), fundindo as versões elaboradas anteriormente e eliminando redundâncias.

---

## 4.1 Requisitos Funcionais (RF)

| ID | Requisito | Descrição |
|----|-----------|-----------|
| RF01 | Entrada em linguagem natural | O sistema deve permitir que o usuário envie perguntas em linguagem natural, sem exigir sintaxe ou formato específico. |
| RF02 | Recuperação de informações na base de conhecimento | O sistema deve identificar e recuperar, na base de fontes oficiais, os trechos relevantes para a pergunta do usuário (etapa de *retrieval* do RAG). |
| RF03 | Geração de resposta a partir do contexto recuperado | O sistema deve utilizar exclusivamente as informações recuperadas como contexto para gerar a resposta (etapa de geração do RAG). |
| RF04 | Respostas dentro do escopo SUS-DF | O sistema deve responder perguntas relacionadas ao escopo definido: unidades e serviços de saúde (UBS, UPA, hospitais, CAPS), vacinação, medicamentos e farmácias, consultas e encaminhamentos, dados institucionais de estabelecimentos (endereço, horário, telefone, serviços) e informações territoriais (unidade × Região Administrativa), sempre limitado ao que estiver sustentado pelas fontes. |
| RF05 | Declaração de ausência de informação | Quando não houver informação suficiente nas fontes recuperadas, o sistema deve informar essa limitação explicitamente, sem especular. |
| RF06 | Resposta parcial controlada | Quando apenas parte da pergunta for sustentada pelas fontes, o sistema deve responder somente à parte fundamentada e indicar o que não foi encontrado. |
| RF07 | Esclarecimento em perguntas ambíguas | Quando a pergunta não permitir identificar com segurança o serviço, unidade ou contexto necessário, o sistema deve solicitar esclarecimento antes de responder. |
| RF08 | Tratamento de perguntas fora do escopo | O sistema deve identificar perguntas fora do escopo (diagnóstico, prescrição, tratamento personalizado, recomendação clínica individual) e deixar claro que a solicitação não pode ser atendida, sem produzir a orientação bloqueada mesmo indiretamente. |
| RF09 | Vedação de diagnóstico, prescrição ou recomendação individual | O sistema não deve, em nenhuma hipótese, realizar diagnóstico, prescrever ou recomendar individualmente medicamento/tratamento, mesmo quando a informação de disponibilidade estiver correta. |
| RF10 | Disponibilização das fontes utilizadas | O sistema deve indicar, junto à resposta, quais fontes foram utilizadas para elaborá-la. |
| RF11 | Consulta detalhada da fonte ("Ver mais") | O sistema deve oferecer uma funcionalidade para o usuário consultar o trecho/fonte completa que fundamentou a resposta. |
| RF12 | Uso de contexto informado pelo usuário | O sistema deve utilizar dados fornecidos pelo próprio usuário (Região Administrativa, endereço etc.) para contextualizar e refinar a pergunta, quando necessário. |

---

## 4.2 Requisitos Não Funcionais (RNF)

| ID | Requisito | Descrição |
|----|-----------|-----------|
| RNF01 | Fidelidade à fonte (anti-alucinação / confiabilidade) | As respostas devem ser geradas estritamente a partir do conteúdo recuperado; o modelo não pode usar conhecimento próprio para preencher lacunas. |
| RNF02 | Rastreabilidade | O sistema deve manter, internamente, a associação entre cada resposta e o trecho/fonte que a sustenta, permitindo auditoria. |
| RNF03 | Transparência | O usuário deve conseguir consultar as evidências utilizadas na resposta (base para o RF11). |
| RNF04 | Tratamento de conflito e atualização entre fontes | Diante de fontes divergentes ou desatualizadas, o sistema deve seguir uma política definida de priorização, sem escolha arbitrária. |
| RNF05 | Privacidade de dados sensíveis (LGPD) | Dados de saúde e informações pessoais fornecidas pelo usuário (endereço, RA etc.) devem ser tratados com minimização e conformidade com a LGPD. |
| RNF06 | Segurança em cenários críticos | O sistema deve reconhecer sinais de possível urgência/emergência e, nesses casos, nunca substituir orientação de emergência — direcionando sempre a canais oficiais apropriados. |
| RNF07 | Robustez e consistência | O sistema deve tolerar erros de digitação, informalidade e variações de fraseado na entrada, e perguntas equivalentes devem gerar respostas compatíveis quando as mesmas fontes as sustentam. |
| RNF08 | Equidade | As respostas devem ser consistentes e não discriminatórias entre diferentes Regiões Administrativas ou perfis de usuário, garantindo acesso equivalente à informação. |
| RNF09 | Usabilidade | A interação deve ser compreensível para usuários sem conhecimento técnico, com linguagem acessível a diferentes níveis de letramento. |
| RNF10 | Desempenho | A resposta deve ser produzida em tempo compatível com uma interação conversacional, respeitando as limitações do ambiente/protótipo. |
| RNF11 | Disponibilidade | O sistema deve manter alta disponibilidade, dado o caráter de acesso a informações de serviços públicos de saúde. |
| RNF12 | Manutenibilidade e atualidade do corpus | Fontes, dados e componentes (modelo, prompt) devem poder ser atualizados ou substituídos sem reconstrução completa da aplicação, e a base deve permitir atualização periódica. |
| RNF13 | Avaliação e monitoramento contínuos | Como o comportamento do sistema pode mudar sem alteração de código (troca de modelo, de dados ou de prompt), deve haver um pipeline de avaliação contínua — testes de regressão e métricas de fundamentação, escopo e limite clínico — a cada mudança de componente. |
| RNF14 | Custo | O protótipo deve priorizar tecnologias gratuitas ou de código aberto. |

---

## Notas sobre a fusão

Requisitos combinados por tratarem do mesmo conceito nas duas versões originais:

- **Ausência de informação** — RF05
- **Fontes utilizadas / rastreabilidade** — RF10, RNF02
- **Perguntas fora do escopo** — RF08
- **Fidelidade à fonte / confiabilidade** — RNF01
- **Usabilidade** — RNF09
- **Desempenho** — RNF10
- **Manutenibilidade / atualidade do corpus** — RNF12

Os demais itens de cada lista original, sem correspondente direto na outra, foram mantidos como requisitos independentes (ex.: RF01–RF03, RF07, RF11; RNF03, RNF07, RNF14).
