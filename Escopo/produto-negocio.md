```markdown
# Produto e Negócio — Susana

## 1. Visão geral

A **Susana** é uma assistente conversacional voltada exclusivamente para fornecer informações sobre os serviços, estabelecimentos, formas de acesso e fluxos do **SUS no Distrito Federal (SUS-DF)**.

O produto foi concebido para atuar como uma interface de acesso à informação: em vez de exigir que o usuário saiba previamente em qual página, documento ou canal oficial deve procurar, a Susana permite que a dúvida seja expressa em linguagem natural e busca, nas fontes oficiais autorizadas pelo projeto, as informações necessárias para construir uma resposta.

A proposta não é criar uma ferramenta de diagnóstico ou tratamento. A função da Susana é facilitar o acesso a informações confiáveis sobre o funcionamento e a utilização dos serviços públicos de saúde do Distrito Federal.

A definição funcional detalhada do sistema estabelece que suas respostas devem ser fundamentadas exclusivamente em informações recuperadas de fontes oficiais e que informações ausentes não devem ser substituídas por suposições. :chatgpt-content-reference{index="0"}

---

# 2. Problema de negócio

## 2.1 Problema central

Pessoas que precisam utilizar serviços do SUS-DF podem encontrar dificuldades para **localizar, compreender e confirmar informações confiáveis** sobre onde procurar atendimento, quais serviços estão disponíveis, como funciona determinado acesso e quais informações administrativas são necessárias.

O problema não consiste apenas na ausência de informação.

Em muitos casos, a informação existe, mas encontra-se distribuída entre diferentes páginas, documentos, sistemas e canais institucionais. O usuário, portanto, precisa descobrir:

1. onde procurar;
2. qual informação é relevante;
3. como interpretar essa informação;
4. se ela realmente corresponde ao serviço que procura;
5. se a informação pode ser considerada confiável e atual.

Isso cria um problema de **acessibilidade informacional**, e não necessariamente de inexistência de dados.

---

## 2.2 Problemas associados

O problema central pode ser dividido em diferentes dificuldades:

### Localização da informação

O usuário pode não saber em qual unidade, página, documento ou canal a informação está disponível.

### Fragmentação

Informações relacionadas a um mesmo problema podem estar distribuídas em diferentes fontes.

### Complexidade

Informações institucionais podem exigir que o usuário compreenda previamente a estrutura ou os termos utilizados pelo sistema de saúde.

### Assimetria de conhecimento

O usuário pode não saber previamente como funciona o fluxo administrativo do SUS-DF.

### Verificação

Mesmo quando encontra uma resposta na internet, o usuário pode ter dificuldade para determinar se ela é oficial, atual ou aplicável ao Distrito Federal.

### Tradução da necessidade para uma busca

A pessoa pode saber o que precisa resolver, mas não saber como transformar sua dúvida em termos adequados para encontrar a informação correta.

---

# 3. Problema que a Susana pretende resolver

A Susana pretende reduzir a distância entre:

> **a necessidade de informação do cidadão**

e

> **a informação oficial necessária para resolver essa necessidade.**

A proposta pode ser representada da seguinte maneira:

```text
Usuário possui uma necessidade
            ↓
Não sabe exatamente onde procurar
            ↓
Informa sua dúvida em linguagem natural
            ↓
Susana interpreta a necessidade
            ↓
Busca informações nas fontes oficiais autorizadas
            ↓
Seleciona informações relevantes
            ↓
Gera uma resposta compreensível
            ↓
Permite verificar a origem da informação
```

Dessa maneira, a Susana funciona como uma camada de interação entre o cidadão e o conjunto de informações oficiais do SUS-DF.

---

# 4. Problema sob a perspectiva do usuário

Do ponto de vista do usuário, o problema pode ser descrito como:

> "Eu preciso de uma informação sobre o SUS-DF, mas não sei exatamente onde encontrá-la, como interpretá-la ou como confirmar se a informação que encontrei é confiável."

A necessidade do usuário não é necessariamente conversar com uma inteligência artificial.

A necessidade real é **resolver uma dúvida relacionada ao acesso ou funcionamento do SUS-DF de forma simples e confiável**.

A Susana é o meio utilizado para atender essa necessidade.

---

# 5. Oportunidade do produto

A oportunidade do produto surge da combinação de três necessidades:

```text
Necessidade de informação
          +
Dificuldade de navegação entre fontes
          +
Necessidade de confiabilidade
          =
Oportunidade para a Susana
```

Existe espaço para uma interface conversacional capaz de transformar perguntas feitas em linguagem natural em consultas fundamentadas nas informações oficiais disponíveis.

A oportunidade não está em substituir os canais institucionais, mas em **tornar seu conteúdo mais acessível e compreensível por meio de uma interface conversacional**.

---

# 6. Público-alvo

## 6.1 Público-alvo principal

O público-alvo principal da Susana é:

> **Cidadãos do Distrito Federal que precisam obter informações sobre serviços, estabelecimentos, atendimento e fluxos do SUS-DF.**

A característica central desse público não é uma faixa etária específica, profissão ou perfil socioeconômico.

O principal critério de identificação é a existência de uma **necessidade de informação relacionada ao SUS-DF**.

---

## 6.2 Público potencial

Dentro do público principal, podem existir diferentes perfis de utilização.

A Susana pode ser utilizada por pessoas que:

- precisam localizar uma unidade;
- precisam descobrir quais serviços uma unidade oferece;
- procuram informações sobre vacinação;
- precisam encontrar informações sobre medicamentos e farmácias;
- querem entender como funciona um encaminhamento;
- precisam compreender um fluxo administrativo;
- procuram horários ou contatos;
- desejam confirmar uma informação relacionada ao SUS-DF;
- precisam de informação para outra pessoa.

---

# 7. Usuários fora do público principal

A Susana não tem como público principal:

- profissionais de saúde buscando suporte à decisão clínica;
- pesquisadores buscando análise epidemiológica;
- gestores utilizando o sistema como ferramenta de análise gerencial;
- usuários procurando diagnóstico;
- usuários procurando tratamento personalizado;
- usuários procurando recomendação clínica individual.

Esses casos não representam o objetivo principal do produto.

Além disso, diagnóstico, prescrição, recomendação individual de medicamentos, tratamento personalizado e orientação clínica individualizada estão explicitamente fora do escopo funcional da Susana. :chatgpt-content-reference{index="1"}

---

# 8. Necessidades dos usuários

As necessidades dos usuários podem ser organizadas em quatro grupos principais.

## 8.1 Encontrar

O usuário precisa descobrir:

- onde determinado serviço está disponível;
- qual unidade deve consultar para determinada informação;
- quais estabelecimentos existem em determinada região;
- onde encontrar determinado serviço público.

## 8.2 Entender

O usuário precisa compreender:

- como determinado serviço funciona;
- como ocorre determinado fluxo administrativo;
- quais são os procedimentos de acesso;
- quais informações são relevantes para utilizar determinado serviço.

## 8.3 Confirmar

O usuário precisa verificar:

- se a informação é oficial;
- qual é a origem da informação;
- qual documento ou fonte sustenta a resposta;
- quando a informação foi atualizada, quando esse dado estiver disponível.

## 8.4 Resolver

O objetivo final não é simplesmente obter uma resposta textual.

É permitir que o usuário consiga **tomar uma ação informacional mais clara**, como identificar uma unidade, compreender um fluxo ou localizar o canal adequado.

---

# 9. Principais necessidades funcionais do público

As necessidades dos usuários podem ser traduzidas em capacidades que o produto deve oferecer:

| Necessidade | Resposta do produto |
|---|---|
| Localizar uma unidade | Informar unidades relacionadas à necessidade apresentada |
| Descobrir serviços | Informar serviços disponíveis quando documentados |
| Entender funcionamento | Explicar informações administrativas oficiais |
| Entender fluxos | Apresentar fluxos documentados pelas fontes autorizadas |
| Encontrar vacinação | Localizar informações oficiais relacionadas à vacinação |
| Encontrar farmácias/medicamentos | Apresentar informações administrativas disponíveis |
| Encontrar contatos | Informar contatos presentes nas fontes |
| Confirmar uma informação | Associar a resposta à fonte correspondente |
| Esclarecer uma dúvida ambígua | Solicitar informações adicionais quando necessário |
| Não encontrar informação | Informar explicitamente a ausência de informação suficiente |

---

# 10. Personas

As personas abaixo representam perfis de usuários relevantes para o desenvolvimento e avaliação do produto.

As personas não representam indivíduos reais. São modelos de comportamento utilizados para orientar decisões de produto, interface, requisitos e testes.

---

## 10.1 Persona 1 — Cidadão procurando um serviço

**Nome:** Mariana  
**Idade:** 34 anos  
**Perfil:** cidadã do Distrito Federal que utiliza serviços públicos de saúde, mas não conhece detalhadamente a estrutura da rede.

### Contexto

Mariana precisa encontrar determinado serviço público de saúde e não sabe qual unidade procurar.

### Objetivo

Encontrar rapidamente uma unidade ou serviço adequado à sua necessidade informacional.

### Dificuldade

Ela não sabe exatamente em qual canal oficial procurar a informação e não conhece previamente a estrutura do SUS-DF.

### Necessidade

Receber uma resposta objetiva e compreensível, fundamentada em uma fonte oficial.

### Expectativa em relação à Susana

A Susana deve ajudá-la a localizar a informação sem exigir conhecimento prévio sobre a organização do sistema.

### Necessidade de produto representada

**Encontrar.**

---

## 10.2 Persona 2 — Usuário tentando entender um fluxo

**Nome:** João  
**Idade:** 52 anos  
**Perfil:** cidadão que sabe que precisa acessar determinado serviço, mas não compreende o fluxo administrativo.

### Contexto

João precisa entender como funciona determinado encaminhamento ou acesso a um serviço especializado.

### Objetivo

Compreender quais são os procedimentos administrativos documentados para acessar o serviço.

### Dificuldade

Ele conhece sua necessidade, mas não conhece a organização do processo.

### Necessidade

Receber uma explicação clara do fluxo oficial.

### Expectativa em relação à Susana

A Susana deve traduzir uma informação institucional para uma linguagem mais compreensível, sem alterar o conteúdo oficial.

### Necessidade de produto representada

**Entender.**

---

## 10.3 Persona 3 — Familiar ou responsável

**Nome:** Carlos  
**Idade:** 41 anos  
**Perfil:** pessoa que busca informação relacionada ao SUS-DF para auxiliar outra pessoa.

### Contexto

Carlos está tentando localizar informações sobre determinado serviço ou unidade para um familiar.

### Objetivo

Encontrar uma informação prática de forma rápida.

### Dificuldade

Não possui conhecimento detalhado sobre a rede pública de saúde nem sobre os diferentes canais institucionais.

### Necessidade

Localização, contato, horário, serviço ou fluxo administrativo.

### Expectativa em relação à Susana

Conseguir obter a informação sem precisar pesquisar em múltiplas fontes manualmente.

### Necessidade de produto representada

**Encontrar e resolver.**

---

## 10.4 Persona 4 — Usuário fora do escopo

**Nome:** Lucas  
**Idade:** 27 anos  
**Perfil:** usuário que procura a Susana buscando uma orientação clínica individual.

### Contexto

Lucas apresenta uma dúvida relacionada a sintomas, medicamentos ou tratamento e espera uma recomendação personalizada.

### Objetivo

Obter uma orientação clínica.

### Problema

Essa necessidade não corresponde ao objetivo funcional da Susana.

### Comportamento esperado

A Susana deve reconhecer que a solicitação está fora do escopo, não fornecer diagnóstico, prescrição ou tratamento personalizado e, quando apropriado, indicar a busca por um profissional ou canal oficial.

### Necessidade de produto representada

**Controle de escopo.**

Essa persona é particularmente importante para a avaliação de segurança e dos limites funcionais do sistema.

---

# 11. Jobs to Be Done

Além das personas, o produto pode ser entendido por meio de suas principais tarefas que o usuário deseja realizar.

## Job 1 — Encontrar um serviço

> "Quando preciso de um serviço do SUS-DF, quero descobrir onde ele está disponível para conseguir localizar a unidade ou serviço relevante."

## Job 2 — Entender como acessar

> "Quando preciso acessar um serviço do SUS-DF, quero entender o fluxo oficial para saber quais são os procedimentos necessários."

## Job 3 — Confirmar uma informação

> "Quando encontro uma informação sobre o SUS-DF, quero saber de onde ela veio para conseguir verificar sua confiabilidade."

## Job 4 — Resolver uma dúvida administrativa

> "Quando tenho uma dúvida sobre uma unidade ou serviço, quero obter uma resposta objetiva sem precisar procurar manualmente em vários canais."

## Job 5 — Identificar limites da informação

> "Quando não existe informação suficiente, quero saber que a informação não foi encontrada em vez de receber uma resposta presumida."

---

# 12. Proposta de valor

A proposta de valor da Susana pode ser definida como:

> **Facilitar o acesso do cidadão a informações confiáveis sobre o SUS-DF por meio de uma interface conversacional capaz de localizar, contextualizar e apresentar informações provenientes de fontes oficiais.**

A proposta possui quatro elementos principais:

### Acessibilidade

Permitir que o usuário faça perguntas utilizando linguagem natural.

### Centralização da busca

Reduzir a necessidade de procurar manualmente informações distribuídas em diferentes fontes.

### Fundamentação

Relacionar a resposta às informações recuperadas das fontes oficiais autorizadas.

### Clareza

Apresentar a informação em linguagem mais compreensível sem alterar o conteúdo sustentado pela fonte.

---

# 13. O que diferencia a Susana

A principal característica diferencial do produto não deve ser simplesmente:

> "possui inteligência artificial."

A utilização de IA, por si só, não define o valor do produto.

O diferencial está na combinação de:

```text
Linguagem natural
        +
Recuperação de informação
        +
Fontes oficiais
        +
Rastreabilidade
        +
Controle de escopo
```

A Susana deve permitir que o usuário interaja de maneira simples com informações institucionais sem perder a possibilidade de verificar sua origem.

---

# 14. Relação com confiabilidade da informação

O projeto está diretamente relacionado ao problema de avaliar a confiabilidade das informações.

A Susana não deve exigir que o usuário simplesmente "confie na IA".

O sistema deve favorecer um modelo em que:

```text
Resposta
   ↓
Informação recuperada
   ↓
Fonte identificável
   ↓
Possibilidade de verificação
```

Portanto, a confiança no produto deve estar relacionada à **transparência da origem da informação**, e não apenas à aparência de autoridade da resposta.

A própria especificação funcional estabelece que as respostas devem ser baseadas nas informações recuperadas e que o sistema não deve atribuir às fontes informações que elas não apresentam. :chatgpt-content-reference{index="2"}

---

# 15. Objetivo do produto

O objetivo do produto é:

> **Criar uma interface conversacional capaz de facilitar o acesso a informações confiáveis sobre serviços e atendimento do SUS-DF, utilizando fontes oficiais autorizadas e apresentando respostas compreensíveis e rastreáveis.**

Esse objetivo pode ser dividido em objetivos menores:

1. reduzir a dificuldade de localização das informações;
2. reduzir a necessidade de navegar manualmente por múltiplos canais;
3. facilitar a compreensão de informações institucionais;
4. permitir verificação da origem das respostas;
5. reduzir a geração de informações sem evidência;
6. manter o sistema dentro de um escopo funcional bem definido.

---

# 16. Objetivo de negócio

O objetivo de negócio do projeto é:

> **Melhorar o acesso do cidadão à informação relacionada aos serviços públicos de saúde do Distrito Federal, utilizando tecnologia conversacional para reduzir a complexidade da busca e aumentar a transparência sobre a origem das respostas.**

O valor de negócio não está necessariamente em substituir canais existentes.

Está em oferecer uma camada adicional de acesso que torne as informações mais fáceis de encontrar e compreender.

---

# 17. Valor gerado para o usuário

O produto busca gerar os seguintes valores:

### Menor esforço de busca

O usuário pode expressar diretamente sua necessidade em linguagem natural.

### Menor complexidade

O usuário não precisa necessariamente conhecer a organização dos canais institucionais antes de realizar a busca.

### Maior clareza

Informações institucionais podem ser apresentadas em uma linguagem conversacional.

### Maior rastreabilidade

A origem da informação pode ser apresentada junto à resposta.

### Maior transparência sobre limitações

Quando não houver informação suficiente, o sistema deve comunicar essa condição.

---

# 18. Valor gerado para o projeto

Do ponto de vista acadêmico e tecnológico, o produto também permite investigar:

- aplicação prática de RAG;
- recuperação semântica de informações;
- uso de LLMs locais;
- controle de escopo;
- fundamentação de respostas;
- rastreabilidade;
- comportamento diante da ausência de evidência;
- avaliação de respostas geradas por IA;
- relação entre IA e confiabilidade da informação.

Assim, a Susana não deve ser avaliada apenas pela capacidade de conversar.

Ela deve ser avaliada pela capacidade de **recuperar informação relevante e produzir respostas sustentadas por evidências disponíveis**.

---

# 19. Contextos principais de uso

Os principais contextos de utilização do produto são:

### Busca por unidades

Usuário deseja localizar uma unidade ou identificar informações sobre determinado estabelecimento.

### Busca por serviços

Usuário quer saber quais serviços estão disponíveis em uma determinada unidade ou região.

### Busca por vacinação

Usuário procura informações sobre locais, horários ou outros aspectos administrativos da vacinação.

### Busca por medicamentos e farmácias

Usuário procura informações administrativas relacionadas à disponibilidade, localização ou acesso.

### Fluxos de atendimento

Usuário precisa entender como acessar determinado serviço ou encaminhamento.

### Verificação

Usuário quer confirmar a origem de uma informação encontrada ou recebida.

---

# 20. Experiência esperada

A experiência da Susana deve seguir uma lógica simples:

```text
Perguntar
   ↓
Entender
   ↓
Buscar
   ↓
Responder
   ↓
Verificar
```

Quando necessário:

```text
Pergunta ambígua
       ↓
Solicitar esclarecimento
       ↓
Buscar novamente
       ↓
Responder
```

Quando não houver informação:

```text
Pergunta
   ↓
Busca
   ↓
Informação insuficiente
   ↓
Informar limitação
```

Quando estiver fora do escopo:

```text
Pergunta
   ↓
Identificação de conteúdo não permitido
   ↓
Não fornecer orientação solicitada
   ↓
Redirecionar adequadamente
```

Esses comportamentos correspondem aos casos definidos no escopo funcional da Susana. :chatgpt-content-reference{index="3"}

---

# 21. Relação entre produto e tecnologia

A tecnologia deve atender ao problema identificado, e não definir o problema.

A arquitetura tecnológica prevista funciona como meio para implementar a proposta de valor:

```text
Problema
Dificuldade de acesso a informação confiável
             ↓
Produto
Susana
             ↓
Interface
Conversação em linguagem natural
             ↓
RAG
Recuperação de informações relevantes
             ↓
PostgreSQL + pgvector
Armazenamento e busca vetorial
             ↓
Ollama
Execução local do modelo de linguagem
             ↓
Fontes oficiais
Base de evidências
```

Nesse modelo, o LLM não é a fonte primária da informação.

Ele atua como componente de geração e interpretação das informações recuperadas.

---

# 22. Premissas do produto

O desenvolvimento da Susana parte das seguintes premissas:

1. Existem fontes oficiais suficientemente relevantes para formar o corpus inicial.
2. O usuário consegue expressar sua necessidade em linguagem natural.
3. As informações utilizadas pelo sistema podem ser associadas às suas respectivas fontes.
4. O sistema será utilizado dentro do território e contexto do Distrito Federal.
5. A qualidade da resposta depende diretamente da qualidade e atualização das fontes utilizadas.
6. A IA deve atuar como ferramenta de acesso e interpretação da informação, e não como autoridade independente da evidência.

---

# 23. Restrições do produto

As principais restrições são:

### Escopo territorial

O produto é orientado exclusivamente ao Distrito Federal.

### Escopo informacional

O produto está limitado a informações relacionadas aos serviços e atendimento do SUS-DF.

### Fundamentação

Respostas factuais devem ser sustentadas pelas informações recuperadas das fontes autorizadas.

### Limite clínico

O produto não deve realizar diagnóstico, prescrição, recomendação clínica individual ou tratamento personalizado.

### Dependência das fontes

A qualidade das respostas depende da disponibilidade, qualidade e atualização das informações oficiais utilizadas.

---

# 24. Não objetivos do produto

Para evitar expansão excessiva do projeto, os seguintes objetivos não fazem parte da proposta:

- criar um sistema de diagnóstico;
- criar um sistema de prescrição;
- substituir profissionais de saúde;
- substituir integralmente os canais oficiais do SUS;
- atuar como ferramenta de decisão clínica;
- produzir conhecimento médico novo;
- responder livremente qualquer assunto;
- utilizar a IA para preencher lacunas de informação sem evidência;
- transformar o sistema em um assistente geral.

---

# 25. Hipóteses do produto

O desenvolvimento da Susana pode ser orientado por hipóteses que posteriormente serão avaliadas.

## Hipótese 1

> Usuários conseguem formular dúvidas sobre serviços do SUS-DF de maneira mais natural em uma interface conversacional do que em uma navegação tradicional por múltiplas páginas.

## Hipótese 2

> A recuperação de informações de fontes oficiais permite produzir respostas mais rastreáveis do que respostas geradas exclusivamente a partir do conhecimento interno do modelo.

## Hipótese 3

> A apresentação da origem da informação facilita a verificação da resposta pelo usuário.

## Hipótese 4

> A combinação de controle de escopo e recuperação de evidências reduz respostas inadequadas fora do domínio definido.

## Hipótese 5

> Informar explicitamente quando não existe evidência suficiente é preferível à tentativa de produzir uma resposta completa sem sustentação.

Essas hipóteses não devem ser tratadas como fatos antes da avaliação. Elas representam suposições que o desenvolvimento e os testes deverão investigar.

---

# 26. Riscos de produto

## Informação desatualizada

Uma fonte pode mudar depois de ter sido incorporada ao corpus.

### Impacto

A resposta pode continuar correta em estrutura, mas apresentar informação que não corresponde mais ao estado atual do serviço.

### Tratamento

O produto deve manter metadados de atualização e estabelecer posteriormente regras de atualização e priorização das fontes.

---

## Informação insuficiente

O sistema pode não possuir os dados necessários para responder determinada pergunta.

### Impacto

O usuário pode não conseguir concluir sua busca.

### Tratamento

A Susana deve informar explicitamente a ausência de informação suficiente, em vez de gerar uma resposta especulativa.

---

## Recuperação inadequada

O mecanismo de recuperação pode selecionar trechos que não são os mais relevantes para a pergunta.

### Impacto

A resposta gerada pode ser incompleta ou incorreta mesmo quando o corpus possui a informação necessária.

### Tratamento

O processo de recuperação deverá ser avaliado independentemente da qualidade textual do LLM.

---

## Geração inadequada

O modelo pode produzir conteúdo que não está sustentado pelo contexto recuperado.

### Impacto

O sistema pode apresentar informações sem evidência.

### Tratamento

Devem existir regras de geração, testes específicos e avaliação de fundamentação.

---

## Expansão excessiva do escopo

Durante o desenvolvimento, novas funcionalidades podem ser adicionadas sem relação direta com o problema inicial.

### Impacto

Aumenta a complexidade e dificulta a implementação e avaliação.

### Tratamento

Toda nova funcionalidade deve ser comparada ao problema, objetivo e escopo definidos neste documento.

---

# 27. Métricas e critérios de sucesso

O sucesso do produto não deve ser medido apenas pela capacidade de responder.

Alguns critérios relevantes são:

### Relevância

A informação recuperada deve estar relacionada à pergunta realizada.

### Fundamentação

A resposta deve estar sustentada pelos trechos recuperados.

### Correção da fonte

A fonte apresentada deve corresponder à informação utilizada.

### Controle de alucinação

O sistema deve minimizar a apresentação de informações não sustentadas.

### Controle de escopo

Perguntas fora do domínio devem ser corretamente identificadas.

### Transparência

O sistema deve informar quando não possui evidência suficiente.

### Clareza

A resposta deve ser compreensível para usuários não técnicos.

### Consistência

Perguntas semanticamente equivalentes devem apresentar comportamento compatível quando submetidas às mesmas informações disponíveis.

---

# 28. Indicadores para avaliação do MVP

Para a avaliação inicial do produto, podem ser acompanhados indicadores como:

```text
Taxa de respostas fundamentadas
Taxa de fontes corretas
Taxa de recuperação relevante
Taxa de respostas fora do escopo corretamente bloqueadas
Taxa de respostas sem evidência
Taxa de solicitações de esclarecimento adequadas
Taxa de respostas parcialmente corretas
```

Esses indicadores devem ser calculados a partir de um conjunto de perguntas previamente definido.

---

# 29. Cenários de sucesso

Um cenário de sucesso ocorre quando:

```text
Usuário possui uma dúvida
        ↓
Formula a pergunta naturalmente
        ↓
Sistema identifica o contexto
        ↓
Recupera informação relevante
        ↓
LLM produz resposta baseada no contexto
        ↓
Usuário compreende a resposta
        ↓
Usuário consegue verificar a origem
```

---

# 30. Cenários de falha controlada

Um sistema confiável não precisa responder todas as perguntas.

Ele também precisa **falhar corretamente**.

### Falha controlada por ausência de informação

```text
Pergunta
   ↓
Não existe evidência suficiente
   ↓
Sistema informa a limitação
```

### Falha controlada por escopo

```text
Pergunta
   ↓
Solicitação fora do escopo
   ↓
Sistema não fornece a orientação solicitada
```

### Falha controlada por ambiguidade

```text
Pergunta
   ↓
Informação insuficiente para identificar a intenção
   ↓
Sistema solicita esclarecimento
```

Esse comportamento faz parte da proposta de confiabilidade do produto.

---

# 31. Stakeholders

Os principais stakeholders relacionados ao produto são:

| Stakeholder | Interesse |
|---|---|
| Cidadão | Encontrar e compreender informações sobre o SUS-DF |
| Usuário do SUS-DF | Acessar informações sobre serviços e atendimento |
| Equipe de desenvolvimento | Construir e manter o sistema |
| Equipe do projeto acadêmico | Demonstrar a aplicação prática de IA e RAG |
| Responsáveis pelo corpus | Selecionar, organizar e atualizar fontes |
| Instituições responsáveis pelas fontes | Disponibilizar informações oficiais |
| Avaliadores do projeto | Verificar funcionamento, fundamentação e resultados |

---

# 32. Visão de produto

A visão de produto da Susana é:

> **Tornar mais simples a busca por informações confiáveis sobre o SUS-DF, transformando a necessidade do cidadão em uma interação conversacional fundamentada em fontes oficiais.**

A Susana deve funcionar como uma ponte entre:

```text
Cidadão
   ↕
Informação
   ↕
Fontes oficiais
```

Essa ponte deve preservar a origem da informação e deixar claro quando a evidência disponível não é suficiente.

---

# 33. Declaração de problema

Para fins de documentação do projeto, o problema pode ser formalmente registrado da seguinte maneira:

> **Cidadãos do Distrito Federal podem encontrar dificuldades para localizar, compreender e verificar informações sobre serviços e atendimento do SUS-DF devido à distribuição dessas informações em diferentes canais e à dificuldade de determinar quais informações são relevantes e confiáveis. Isso pode aumentar o esforço necessário para encontrar uma resposta e favorecer a utilização de informações inadequadas ou não verificadas.**

---

# 34. Declaração de público-alvo

> **A Susana tem como público-alvo principal cidadãos do Distrito Federal que precisam localizar, compreender ou verificar informações relacionadas aos serviços, estabelecimentos, atendimento e fluxos administrativos do SUS-DF.**

---

# 35. Declaração de proposta de valor

> **A Susana facilita o acesso a informações sobre o SUS-DF por meio de uma interface conversacional que recupera informações de fontes oficiais autorizadas e as apresenta de forma compreensível, mantendo a possibilidade de verificar a origem da informação.**

---

# 36. Declaração de objetivo de negócio

> **Reduzir a dificuldade de acesso e compreensão de informações sobre os serviços públicos de saúde do Distrito Federal, utilizando tecnologia conversacional para aproximar o cidadão das informações oficiais e facilitar sua verificação.**

---

# 37. Declaração de objetivo do produto

> **Desenvolver uma assistente conversacional capaz de responder dúvidas sobre serviços e atendimento do SUS-DF com base em informações recuperadas de fontes oficiais, mantendo controle de escopo, transparência sobre as fontes e comportamento adequado diante da ausência de evidências.**

---

# 38. Relação entre problema, usuário, produto e tecnologia

A lógica completa do projeto pode ser resumida em:

```text
PROBLEMA
Dificuldade de encontrar, compreender e verificar
informações do SUS-DF
                ↓
PÚBLICO
Cidadãos que precisam dessas informações
                ↓
NECESSIDADES
Encontrar + entender + confirmar + resolver
                ↓
PRODUTO
Susana
                ↓
PROPOSTA DE VALOR
Informação oficial em linguagem conversacional
com possibilidade de verificação
                ↓
TECNOLOGIA
RAG + PostgreSQL/pgvector + Ollama
                ↓
RESULTADO ESPERADO
Acesso mais simples e transparente à informação
```

---

# 39. Definição final do produto

A **Susana** é uma assistente conversacional de informação sobre o SUS-DF criada para facilitar a localização, compreensão e verificação de informações relacionadas a unidades, serviços, atendimento e fluxos administrativos.

Seu principal valor está em combinar uma experiência conversacional simples com recuperação de informações oficiais e rastreabilidade das fontes.

A Susana não deve ser entendida como uma autoridade independente capaz de produzir qualquer resposta sobre saúde. Sua função é atuar como uma **interface de acesso às informações oficiais disponíveis**, respeitando os limites definidos para o sistema.

---

# 40. Critérios de alinhamento do produto

Antes de adicionar qualquer nova funcionalidade à Susana, a equipe deve verificar:

1. A funcionalidade resolve o problema identificado?
2. Atende uma necessidade real do público-alvo?
3. Está relacionada ao objetivo do produto?
4. Está dentro do escopo do SUS-DF?
5. Pode ser sustentada por informações oficiais?
6. Permite avaliação objetiva?
7. Aumenta o valor do produto sem criar uma expansão desnecessária do escopo?

Caso a resposta seja negativa para a maior parte desses critérios, a funcionalidade deve ser reconsiderada.

---

# 41. Resumo executivo

### Problema

Cidadãos podem ter dificuldade para encontrar, compreender e verificar informações confiáveis sobre serviços e atendimento do SUS-DF.

### Público-alvo

Cidadãos do Distrito Federal que precisam de informações sobre o SUS-DF.

### Principais necessidades

Encontrar serviços, entender fluxos, obter informações administrativas e verificar a origem das informações.

### Produto

Assistente conversacional denominada Susana.

### Proposta de valor

Facilitar o acesso a informações oficiais do SUS-DF por meio de linguagem natural, recuperação de evidências e transparência sobre as fontes.

### Objetivo de negócio

Reduzir a dificuldade de acesso e compreensão de informações sobre os serviços públicos de saúde do Distrito Federal.

### Objetivo do produto

Fornecer respostas fundamentadas em informações recuperadas de fontes oficiais, mantendo controle de escopo e transparência.

### Diferencial

Não é simplesmente um chatbot com IA. É uma interface conversacional orientada à recuperação e apresentação de informações oficiais com rastreabilidade.

### Limite principal

A Susana informa sobre o sistema de saúde e seus serviços; não realiza diagnóstico, prescrição ou tratamento personalizado.

### Princípio central

> **A informação apresentada pela Susana deve ser sustentada pelas fontes disponíveis; quando não houver evidência suficiente, o sistema deve informar essa limitação em vez de inventar uma resposta.**
```
