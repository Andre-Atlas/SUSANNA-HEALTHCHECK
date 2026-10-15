# Especificação de Requisitos Funcionais e Não Funcionais — Meu SUS Brasília (SUSANA)

> **Projeto:** Meu SUS Brasília / SUSANA  
> **Programa:** Residência em Inteligência Artificial — Instituto Eldorado  
> **Metodologia:** Challenge-Based Learning (CBL) — Challenge 1: Fake News / Desinformação  
> **Status:** Documento Homologado / Especificação Oficial — **revisado para a versão final** (conta opcional, agenda e implantação; ver [seção 7](#7-revisão-da-versão-final))  

---

## 1. Introdução

### 1.1 Contexto e Objetivo do Documento
Este documento especifica os **Requisitos Funcionais (RF)** e **Requisitos Não Funcionais (RNF)** do sistema **Meu SUS Brasília (SUSANA)**, desenvolvido no âmbito do Challenge 1 da Residência em Inteligência Artificial do Instituto Eldorado, sob a metodologia *Challenge-Based Learning (CBL)*.

O objetivo deste documento é definir, de forma estruturada e verificável, o que o sistema deve fazer (requisitos funcionais) e sob quais condições e restrições deve operar (requisitos não funcionais). Serve como referência técnica para o desenvolvimento, como artefato formal do portfólio do challenge e como base para avaliação dos entregáveis na Semana 6.

### 1.2 Escopo do Sistema
O **Meu SUS Brasília (SUSANA)** é um assistente virtual baseado em Inteligência Artificial destinado a cidadãos do Distrito Federal. O sistema auxilia na busca e compreensão de informações sobre serviços de saúde pública do DF, utilizando arquitetura RAG (*Retrieval-Augmented Generation*) com corpus controlado de fontes oficiais.

O sistema **não realiza diagnósticos**, **não prescreve medicamentos** e **não substitui profissionais de saúde**. O usuário permanece como julgador final de todas as informações recebidas.

### 1.3 Definições e Siglas

| Termo / Sigla | Definição |
| :--- | :--- |
| **RAG** | *Retrieval-Augmented Generation* — arquitetura que combina recuperação de documentos com geração de texto por LLM |
| **LLM** | *Large Language Model* — modelo de linguagem de grande escala |
| **Embedding** | Representação vetorial de texto gerada por um modelo de linguagem para possibilitar busca semântica |
| **Banco vetorial** | Sistema de armazenamento e recuperação de embeddings (ex.: ChromaDB, Qdrant, pgvector) |
| **Corpus** | Conjunto de documentos indexados na base de conhecimento do sistema |
| **CNES** | Cadastro Nacional de Estabelecimentos de Saúde |
| **DATASUS** | Departamento de Informática do SUS |
| **UBS** | Unidade Básica de Saúde |
| **UPA** | Unidade de Pronto Atendimento |
| **CAPS** | Centro de Atenção Psicossocial |
| **DF** | Distrito Federal |
| **RF** | Requisito Funcional — descreve uma funcionalidade que o sistema deve executar |
| **RNF** | Requisito Não Funcional — descreve uma característica de qualidade ou restrição do sistema |
| **CBL** | *Challenge-Based Learning* — metodologia pedagógica de aprendizagem baseada em desafios |

---

## 2. Visão Geral do Sistema

### 2.1 Descrição do Produto
O **Meu SUS Brasília** é um chatbot web que permite ao cidadão do DF realizar perguntas em linguagem natural sobre serviços de saúde pública. O sistema recupera informações de fontes oficiais indexadas e apresenta respostas fundamentadas, acompanhadas das evidências utilizadas para sua geração.

A solução está alinhada à *Essential Question* do Challenge 1: *como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações sem substituir seu pensamento crítico?* O design do Meu SUS Brasília posiciona a IA como ferramenta de apoio, e não como autoridade informacional.

### 2.2 Arquitetura de Referência
A arquitetura prevista é composta pelas seguintes camadas:

| Camada | Componente | Função |
| :--- | :--- | :--- |
| **Entrada** | Interface web (chat) | Recebe a pergunta do usuário e exibe a resposta |
| **Processamento** | Pipeline de pergunta | Pré-processa a pergunta e aciona o modelo de embeddings |
| **Representação** | Modelo de embeddings (local) | Converte a pergunta em vetor para busca semântica |
| **Recuperação** | Banco de dados vetorial (local) | Recupera os trechos mais relevantes do corpus oficial |
| **Geração** | LLM local (código aberto) | Gera a resposta com base no contexto recuperado |
| **Rastreabilidade** | Módulo de fontes ("Ver mais") | Exibe os trechos e metadados utilizados na resposta |
| **Base de dados** | Corpus oficial indexado | Secretaria de Saúde DF, CNES/DATASUS, bases de saúde pública |

### 2.3 Restrições e Premissas
* **Restrições:**
  1. Utilização de ferramentas gratuitas ou de código aberto;
  2. Escopo temático restrito à saúde pública do Distrito Federal (SES-DF);
  3. Uso do assistente **sem identificação**: nenhum dado pessoal é exigido para consultar o chat, o mapa, o guia de vacinas ou o monitoramento. Dados pessoais só existem se o cidadão **optar** por criar uma conta, sob as salvaguardas de RNF-05, RNF-13, RNF-14 e RNF-15 (conformidade com a LGPD).
* **Premissas:**
  1. As fontes oficiais listadas estão publicamente disponíveis para acesso e indexação;
  2. O grupo terá acesso ao ambiente de desenvolvimento durante todo o período do challenge;
  3. A qualidade das respostas depende diretamente da qualidade e atualidade dos documentos indexados.

---

## 3. Requisitos Funcionais

Os requisitos funcionais estão organizados em quatro grupos temáticos. A prioridade de cada requisito segue a escala: **Essencial** (deve estar presente no MVP), **Importante** (deve estar presente na versão final) e **Desejável** (incremento de valor, implementado se houver capacidade).

### 3.1 Consulta e Busca

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RF-01** | Entrada de pergunta em linguagem natural | O sistema deve aceitar perguntas digitadas pelo usuário em linguagem natural, sem exigir termos técnicos ou filtros pré-definidos, sobre serviços de saúde pública do DF. | **Essencial** |
| **RF-02** | Fornecimento de contexto geográfico pelo usuário | O usuário deve poder informar voluntariamente sua Região Administrativa ou endereço dentro da pergunta, e o sistema deve utilizar essa informação para refinar a resposta. O sistema não deve capturar localização sem permissão explícita do usuário (ver RF-24 e RNF-06). *(Revisado na versão final.)* | **Essencial** |
| **RF-03** | Recuperação semântica na base de conhecimento | O sistema deve transformar a pergunta do usuário em um vetor de embeddings e realizar busca semântica no banco vetorial, recuperando os trechos de documentos oficiais mais relevantes para compor o contexto da resposta. | **Essencial** |
| **RF-04** | Geração de resposta fundamentada em RAG | O modelo de linguagem deve gerar a resposta utilizando exclusivamente o contexto recuperado pela etapa de busca semântica. O sistema não deve produzir respostas baseadas apenas no conhecimento interno do modelo quando a informação estiver ausente na base. | **Essencial** |
| **RF-05** | Cobertura de serviços de saúde do DF | O sistema deve ser capaz de responder perguntas sobre: UBSs, UPAs, hospitais, CAPS, vacinação, medicamentos disponíveis, consultas especializadas, regulação e outros serviços públicos de saúde do Distrito Federal cobertos pelas fontes oficiais indexadas. | **Essencial** |
| **RF-06** | Orientação sobre fluxos de atendimento | O sistema deve ser capaz de orientar o usuário sobre o fluxo de atendimento adequado para situações descritas na pergunta (ex.: onde buscar atendimento de urgência, como agendar uma consulta especializada), desde que as informações estejam disponíveis na base de conhecimento. | **Importante** |

### 3.2 Rastreabilidade e Transparência

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RF-07** | Exibição de fontes via "Ver mais" | Ao lado de cada resposta, o sistema deve disponibilizar uma opção "Ver mais" (ou equivalente) que permita ao usuário consultar os trechos dos documentos oficiais utilizados como base para aquela resposta, incluindo a identificação da fonte (nome do documento ou URL, quando disponível). | **Essencial** |
| **RF-08** | Indicação de ausência de informação | Quando a base de conhecimento não contiver informação suficiente para responder à pergunta, o sistema deve informar explicitamente ao usuário que não encontrou dados relevantes nas fontes disponíveis, sem gerar uma resposta especulativa. | **Essencial** |
| **RF-09** | Declaração dos limites do sistema | O sistema deve exibir, de forma clara e permanente na interface, que não realiza diagnósticos, não prescreve medicamentos e não substitui profissionais de saúde. Essa declaração deve ser apresentada na primeira interação e acessível ao longo do uso. | **Essencial** |

### 3.3 Interface e Interação

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RF-10** | Interface web de chat | O sistema deve disponibilizar uma interface web no formato de chat, permitindo que o usuário envie perguntas e receba respostas em sequência, sem necessidade de instalação de software adicional. | **Essencial** |
| **RF-11** | Histórico de conversa por sessão | O sistema deve manter o histórico das perguntas e respostas durante a sessão ativa do usuário, permitindo que o contexto da conversa seja utilizado pelo modelo para respostas subsequentes dentro da mesma sessão. | **Importante** |
| **RF-12** | Resposta em português brasileiro | O sistema deve gerar todas as respostas em português brasileiro, independentemente da forma como a pergunta foi redigida. | **Essencial** |

### 3.4 Base de Conhecimento e Atualização

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RF-13** | Indexação de fontes oficiais do DF | A base de conhecimento deve ser composta por documentos e dados provenientes exclusivamente de fontes oficiais: Secretaria de Saúde do DF, CNES/DATASUS, informações sobre medicamentos e outras bases públicas de saúde do DF. Fontes não oficiais não devem ser indexadas. | **Essencial** |
| **RF-14** | Atualização incremental da base | A arquitetura deve permitir a incorporação de novos documentos e dados na base de conhecimento sem a necessidade de reconstruir toda a aplicação, possibilitando atualizações periódicas do corpus. | **Importante** |
| **RF-15** | Rastreabilidade do documento de origem por trecho | Cada trecho indexado na base vetorial deve preservar metadados de origem (fonte, data de publicação quando disponível, seção do documento), para que o sistema possa exibir essas informações ao usuário no recurso "Ver mais". | **Importante** |

### 3.5 Conta Opcional, Perfil e Agenda Pessoal *(versão final)*

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RF-16** | Cadastro opcional | O cidadão pode criar uma conta informando apenas nome, CPF (validado pelo módulo 11) e senha. Todo o restante é opcional e o assistente continua plenamente utilizável sem conta. | **Essencial** |
| **RF-17** | Login e permanência de sessão | O acesso é feito por CPF e senha. Com "Lembrar de mim" a sessão dura 30 dias (renovada a cada uso); sem a opção, 24 horas ou até fechar a aba. O cidadão pode sair do aparelho atual ou de todos os aparelhos. | **Essencial** |
| **RF-18** | Perfil de saúde editável e exclusão de conta | O cidadão pode informar data de nascimento, sexo biológico, Região Administrativa, telefone e um checklist de condições (ex.: diabetes, gestação), editar esses dados, alterar a senha e excluir a conta, o que apaga perfil, agenda, registros de vacina e conversas salvas. | **Importante** |
| **RF-19** | Personalização das respostas pelo perfil | Para cidadãos com conta, a Região Administrativa do perfil é usada como padrão na busca e o contexto de faixa etária, sexo e condições declaradas orienta o texto da resposta, sem diagnóstico (RNF-14). | **Importante** |
| **RF-20** | Vacinas pendentes por perfil | O sistema calcula, a partir de idade, sexo e condições, as vacinas do Calendário Nacional pendentes (atrasadas, para tomar agora ou próximas), permitindo marcar "já tomei" e agendar a dose. | **Importante** |
| **RF-21** | Agenda pessoal com lembretes | O cidadão mantém uma agenda de consultas, exames, vacinas e medicamentos (inclusive recorrentes), com calendário mensal, lista e conclusão de compromissos. A agenda é pessoal e **não** realiza agendamento em sistemas oficiais (SISREG, e-SUS). | **Importante** |
| **RF-22** | Criação de lembretes pelo chat com confirmação | Pedidos como "marca consulta no dentista terça às 14h" são interpretados de forma determinística (tipo, data, horário, unidade) e apresentados em um cartão editável. O evento só é gravado após o cidadão confirmar; o modelo de linguagem nunca grava na agenda. | **Importante** |
| **RF-23** | Avisos de lembrete | Lembretes vencidos são exibidos dentro do aplicativo e, mediante permissão, como notificação do navegador enquanto a aplicação estiver aberta. | **Desejável** |
| **RF-24** | Localização atual opcional | Mediante permissão, o sistema ordena as unidades de saúde por distância, mostra "você está aqui" no mapa e sugere a Região Administrativa no cadastro. | **Desejável** |

### 3.6 Monitoramento Epidemiológico *(versão final)*

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RF-25** | Painel de monitoramento epidemiológico | O sistema deve apresentar um painel de vigilância com dados oficiais por agravo e permitir levar o contexto de um indicador para o chat. | **Importante** |

---

## 4. Requisitos Não Funcionais

Os requisitos não funcionais descrevem atributos de qualidade, restrições operacionais e características sistêmicas que o Meu SUS Brasília deve respeitar independentemente da funcionalidade em questão.

### 4.1 Desempenho

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-01** | Tempo de resposta aceitável | O sistema deve gerar e exibir a resposta ao usuário em até 15 segundos para perguntas de complexidade padrão, considerando o ambiente de execução local (MacBook Air M4, 24 GB RAM). Respostas mais longas podem ser exibidas por streaming progressivo. | **Essencial** |
| **RNF-02** | Execução local sem dependência de API paga | O modelo de linguagem e o modelo de embeddings devem ser executados localmente, sem dependência de APIs externas pagas (ex.: OpenAI, Anthropic) para o funcionamento principal do sistema, priorizando modelos de código aberto. | **Essencial** |

### 4.2 Confiabilidade e Precisão

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-03** | Fundamentação das respostas na base indexada | O sistema deve minimizar respostas sem fundamentação documental (alucinações). Quando o modelo não encontrar suporte na base recuperada, deve declarar a ausência de informação (RF-08) em vez de gerar conteúdo sem respaldo. | **Essencial** |
| **RNF-04** | Cobertura temática controlada | O sistema não deve responder perguntas fora do escopo definido (saúde pública do DF). Perguntas sobre outros temas devem ser respondidas com uma mensagem informando que o assistente está limitado a serviços de saúde pública do Distrito Federal. | **Importante** |

### 4.3 Segurança e Privacidade

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-05** | Dados pessoais somente por opção do cidadão | O sistema não deve exigir identificação para nenhuma funcionalidade de consulta. Interações sem conta são anônimas (o histórico de conversa de visitantes fica apenas no navegador). Dados pessoais (nome, CPF, nascimento, sexo biológico, telefone, condições de saúde) só são coletados se o cidadão criar uma conta, e apenas os campos de acesso (nome, CPF, senha) são obrigatórios. *(Revisado na versão final.)* | **Essencial** |
| **RNF-06** | Localização somente com permissão e no aparelho | O sistema só deve usar a geolocalização do dispositivo após permissão explícita do usuário. As coordenadas permanecem no navegador, não são enviadas à API nem armazenadas no servidor; o servidor guarda no máximo a Região Administrativa escolhida pelo cidadão. *(Revisado na versão final.)* | **Essencial** |

### 4.4 Manutenibilidade e Escalabilidade

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-07** | Arquitetura modular e substituível | Os componentes da arquitetura (modelo de linguagem, modelo de embeddings, banco vetorial) devem ser implementados de forma desacoplada, permitindo a substituição de um componente sem reescrita das demais camadas. | **Importante** |
| **RNF-08** | Uso de ferramentas gratuitas ou de código aberto | Todos os componentes de software utilizados (frameworks, modelos, banco vetorial, interface) devem ser gratuitos ou de código aberto, evitando dependência de licenças comerciais. | **Essencial** |
| **RNF-09** | Compatibilidade com ambiente MacBook Air M4 | A aplicação deve ser desenvolvida e testada para execução no ambiente disponível: MacBook Air com chip Apple M4, 24 GB de memória RAM e 512 GB de armazenamento, sem exigir hardware adicional para funcionamento. | **Essencial** |

### 4.5 Usabilidade

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-10** | Interface acessível a usuários leigos | A interface deve ser simples o suficiente para ser utilizada por cidadãos sem experiência prévia com tecnologia avançada, não exigindo terminologia técnica de saúde ou de computação para formular perguntas. | **Importante** |
| **RNF-11** | Clareza sobre o papel do sistema | A interface deve comunicar de forma inequívoca que o assistente é uma ferramenta de apoio à busca de informações, e não uma fonte de decisão médica. O posicionamento visual e textual deve reforçar o papel do usuário como julgador final das informações recebidas. | **Essencial** |

### 4.6 Rastreabilidade e Auditabilidade

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-12** | Logs de uso para avaliação do sistema | O sistema deve registrar, de forma anônima, as perguntas realizadas e os trechos recuperados da base, permitindo que a equipe avalie a qualidade das respostas, identifique lacunas na base de conhecimento e itere sobre o sistema ao longo do challenge. | **Desejável** |

### 4.7 Segurança, Privacidade Reforçada e Operação *(versão final)*

| ID | Nome | Descrição | Prioridade |
| :---: | :--- | :--- | :---: |
| **RNF-13** | Segurança de credenciais e sessões | Senhas armazenadas apenas como hash PBKDF2-HMAC-SHA256 com sal; sessões por token opaco guardado como hash; limitação de tentativas de login; mensagem genérica de erro; cada cidadão acessa somente os próprios dados (perfil, agenda e conversas). | **Essencial** |
| **RNF-14** | Minimização de dados no modelo de linguagem | O contexto enviado ao LLM contém no máximo faixa etária, sexo biológico, condições declaradas, Região Administrativa e nomes de vacinas pendentes. CPF, telefone, nome completo, data exata de nascimento e coordenadas nunca são enviados. | **Essencial** |
| **RNF-15** | Direitos do titular (LGPD) | Consentimento explícito no cadastro, possibilidade de editar e de excluir a conta e os dados a qualquer momento, e dados hospedados em região do Brasil. | **Essencial** |
| **RNF-16** | Transporte seguro e implantação reprodutível | Em produção a aplicação é servida por HTTPS (requisito também de geolocalização e notificações do navegador), empacotada em contêineres (Docker Compose + proxy Caddy) e implantável na Oracle Cloud Always Free conforme o [guia de implantação](../docs/GUIA_DEPLOY_ORACLE_CLOUD.md). | **Importante** |
| **RNF-17** | Persistência e cópia de segurança | Contas, agenda e histórico em SQLite (modo WAL) em volume persistente, com cópia de segurança periódica. | **Importante** |
| **RNF-18** | Verificabilidade automatizada | O backend deve manter suíte de testes automatizados sem dados mockados (151 testes na versão final) e o frontend deve compilar para produção sem erros de tipagem. | **Importante** |

---

## 5. Tabela Consolidada de Requisitos

A tabela abaixo sintetiza todos os 43 requisitos do sistema (25 RF e 18 RNF), proporcionando uma visão consolidada de escopo e prioridade:

| ID | Tipo | Nome do Requisito | Prioridade |
| :---: | :---: | :--- | :---: |
| **RF-01** | RF | Entrada de pergunta em linguagem natural | **Essencial** |
| **RF-02** | RF | Fornecimento de contexto geográfico pelo usuário | **Essencial** |
| **RF-03** | RF | Recuperação semântica na base de conhecimento | **Essencial** |
| **RF-04** | RF | Geração de resposta fundamentada em RAG | **Essencial** |
| **RF-05** | RF | Cobertura de serviços de saúde do DF | **Essencial** |
| **RF-06** | RF | Orientação sobre fluxos de atendimento | **Importante** |
| **RF-07** | RF | Exibição de fontes via "Ver mais" | **Essencial** |
| **RF-08** | RF | Indicação de ausência de informação | **Essencial** |
| **RF-09** | RF | Declaração dos limites do sistema | **Essencial** |
| **RF-10** | RF | Interface web de chat | **Essencial** |
| **RF-11** | RF | Histórico de conversa por sessão | **Importante** |
| **RF-12** | RF | Resposta em português brasileiro | **Essencial** |
| **RF-13** | RF | Indexação de fontes oficiais do DF | **Essencial** |
| **RF-14** | RF | Atualização incremental da base de dados | **Importante** |
| **RF-15** | RF | Rastreabilidade do documento de origem por trecho | **Importante** |
| **RF-16** | RF | Cadastro opcional | **Essencial** |
| **RF-17** | RF | Login e permanência de sessão | **Essencial** |
| **RF-18** | RF | Perfil de saúde editável e exclusão de conta | **Importante** |
| **RF-19** | RF | Personalização das respostas pelo perfil | **Importante** |
| **RF-20** | RF | Vacinas pendentes por perfil | **Importante** |
| **RF-21** | RF | Agenda pessoal com lembretes | **Importante** |
| **RF-22** | RF | Criação de lembretes pelo chat com confirmação | **Importante** |
| **RF-23** | RF | Avisos de lembrete | **Desejável** |
| **RF-24** | RF | Localização atual opcional | **Desejável** |
| **RF-25** | RF | Painel de monitoramento epidemiológico | **Importante** |
| **RNF-01** | RNF | Tempo de resposta aceitável | **Essencial** |
| **RNF-02** | RNF | Execução local sem dependência de API paga | **Essencial** |
| **RNF-03** | RNF | Fundamentação das respostas na base indexada | **Essencial** |
| **RNF-04** | RNF | Cobertura temática controlada | **Importante** |
| **RNF-05** | RNF | Dados pessoais somente por opção do cidadão | **Essencial** |
| **RNF-06** | RNF | Localização somente com permissão e no aparelho | **Essencial** |
| **RNF-07** | RNF | Arquitetura modular e substituível | **Importante** |
| **RNF-08** | RNF | Uso de ferramentas gratuitas ou de código aberto | **Essencial** |
| **RNF-09** | RNF | Compatibilidade com ambiente MacBook Air M4 | **Essencial** |
| **RNF-10** | RNF | Interface acessível a usuários leigos | **Importante** |
| **RNF-11** | RNF | Clareza sobre o papel do sistema | **Essencial** |
| **RNF-12** | RNF | Logs de uso para avaliação do sistema | **Desejável** |
| **RNF-13** | RNF | Segurança de credenciais e sessões | **Essencial** |
| **RNF-14** | RNF | Minimização de dados no modelo de linguagem | **Essencial** |
| **RNF-15** | RNF | Direitos do titular (LGPD) | **Essencial** |
| **RNF-16** | RNF | Transporte seguro e implantação reprodutível | **Importante** |
| **RNF-17** | RNF | Persistência e cópia de segurança | **Importante** |
| **RNF-18** | RNF | Verificabilidade automatizada | **Importante** |

---

## 6. Rastreabilidade: Requisitos × Objetivos CBL

A matriz a seguir demonstra a vinculação direta entre os requisitos do Meu SUS Brasília e os objetivos e entregáveis formais do **Challenge 1 (CBL)**:

| Objetivo / Entregável CBL | Requisitos Relacionados |
| :--- | :--- |
| **Essential Question: IA que apoia sem substituir o pensamento crítico** | `RF-07` (Ver mais), `RF-08` (ausência de info), `RF-09` (limites do sistema), `RNF-03` (fundamentação RAG), `RNF-11` (clareza do papel) |
| **Portfólio de pesquisa: investigação das fontes e dados** | `RF-13` (fontes oficiais), `RF-15` (metadados de origem), `RNF-12` (logs de avaliação) |
| **Estrutura de avaliação de confiança** | `RF-07` (rastreabilidade), `RF-08` (ausência de info), `RF-09` (limites), `RNF-03` (anti-alucinação), `RNF-04` (escopo controlado) |
| **Solução/protótipo com suporte de IA** | `RF-01` a `RF-06` (consulta e busca), `RF-10` a `RF-12` (interface), `RF-16` a `RF-25` (conta, agenda e monitoramento), `RNF-01` (desempenho), `RNF-02` (execução local) |
| **Apresentação e reflexão** | `RNF-12` (logs para avaliação), `RF-08` (transparência de lacunas), `RF-09` (limites explícitos) |
| **Privacidade / LGPD (contexto DF)** | `RNF-05` (dados pessoais só por opção), `RNF-06` (localização com permissão e no aparelho), `RNF-13` (credenciais e sessões), `RNF-14` (minimização no LLM), `RNF-15` (direitos do titular) |
| **Operação e entrega do produto** | `RNF-16` (HTTPS e implantação), `RNF-17` (persistência e backup), `RNF-18` (testes automatizados) |
| **Restrição de ambiente (MacBook Air M4)** | `RNF-02` (execução local), `RNF-08` (ferramentas open source), `RNF-09` (compatibilidade M4) |

---

## 7. Revisão da Versão Final

Esta seção registra o que mudou desde a primeira versão da especificação e o estado de atendimento.

| Mudança | Motivo |
| :--- | :--- |
| RF-02, RNF-05 e RNF-06 reescritos | A primeira versão proibia qualquer coleta de dados pessoais e de localização. A versão final oferece **conta opcional**, perfil de saúde e localização, sempre por escolha do cidadão e com minimização de dados. |
| RF-16 a RF-25 e RNF-13 a RNF-18 acrescentados | Cadastro, agenda com lembretes criados pelo chat, vacinas pendentes por perfil, monitoramento epidemiológico, segurança, LGPD, HTTPS/implantação e testes. |
| Escopo preservado | O sistema continua sem diagnóstico, sem prescrição e **sem agendamento transacional** em sistemas oficiais; a agenda é pessoal. |

**Estado de atendimento:**
* **RF-01 a RF-15 e RNF-01 a RNF-12:** mantêm o estado da versão anterior da especificação.
* **RF-16 a RF-22, RF-24, RF-25 e RNF-13 a RNF-15 e RNF-18:** implementados e cobertos pela suíte automatizada do backend (151 testes) e/ou verificados na interface.
* **RF-23 (avisos de lembrete):** os avisos dentro do aplicativo estão implementados; a notificação do navegador depende de HTTPS e ainda precisa ser validada em produção.
* **RNF-16 e RNF-17:** o pacote de implantação existe (`docker-compose.yml`, `Caddyfile`, `scripts/`), mas a validação em produção (HTTPS e rotina de backup) está **em andamento**.
