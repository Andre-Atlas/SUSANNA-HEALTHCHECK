# 🧭 Guiding Questions — Projeto SUSANA (SES-DF)

> **Documento Consolidado de Questões Norteadoras, Hipóteses e Respostas Técnicas**  
> **Origem:** Quadro Ágil de Concepção (*Challenge 1 / Trello*)  
> **Status:** Homologado e Atualizado com a Arquitetura em Produção  
> **Categorias Temáticas (Labels):** `DADOS` 🔵 | `USUÁRIO` 🟢 | `MODELO` 🟣 | `PRODUÇÃO` ⚫  

---

## 📌 Sumário Executivo e Metodologia de Priorização

Durante a fase de descoberta e especificação do projeto **SUSANA**, a equipe mapeou um conjunto de perguntas norteadoras (*Guiding Questions*) para balizar o desenvolvimento do produto. 

Para assegurar foco e viabilidade de entrega dentro do cronograma ágil, as questões foram organizadas em quatro faixas de priorização:
1. **RESPONDER JÁ:** Decisões estruturais e hipóteses de valor indispensáveis para o núcleo funcional da assistente.
2. **PLANEJAR:** Questões arquiteturais, de governança de dados e de mitigação de riscos que exigem desenho técnico detalhado.
3. **SE SOBRAR TEMPO:** Questões analíticas, investigações secundárias e expansões de escopo após a estabilização do MVP.
4. **CORTAR SEM DÓ (Fora de Escopo):** Complexidades descartadas de forma consciente no MVP para evitar armadilhas de over-engineering e travas burocráticas.

---

## 1. 🚨 RESPONDER JÁ (Decisões Críticas do Core do Produto)

### 1.1. Avaliação com Evidências vs. Classificação Binária (Verdadeiro/Falso)
* **Pergunta Original:** *É mais adequado classificar uma notícia como “verdadeira/falsa” ou avaliar a alegação apresentada com base nas evidências disponíveis?*
* **Label:** `MODELO` 🟣
* **Status:** **Respondida e Implementada**
* **Fundamentação Técnica:**  
  Avaliar a alegação com base em evidências verificadas é tecnicamente superior e eticamente mais seguro, especialmente em saúde pública. A desinformação raramente é 100% falsa; costuma se apoiar em descontextualização, meias-verdades e falácias de correlação vs. causalidade.
  - **Abordagem BDD:** *Dado* que o cidadão questiona sobre a dispensação de um medicamento ou vacina, *Quando* o pipeline consultar a base de conhecimento oficial da SES-DF, *Então* ele deve retornar as evidências textuais exatas que sustentam a resposta.
  - **Redução de Risco Editorial:** Classificadores binários rígidos atraem passivos éticos e risco de judicialização. Apresentar o trecho normativo com a fonte oficial (portal da SES-DF, Diário Oficial, REME) transfere autoridade ao órgão público e transparência ao cidadão.

---

### 1.2. Formato de Produto com Maior Valor para o Usuário
* **Pergunta Original:** *Qual formato de produto apresenta maior valor para o usuário: ferramenta de consulta ativa, extensão de navegador, chatbot ou sistema integrado ao fluxo de consumo de notícias?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Respondida e Implementada**
* **Fundamentação Técnica:**  
  O formato com menor atrito e maior alcance para a população do SUS é o **Chatbot Conversacional em Web App Responsivo** (com arquitetura preparada para mensageria como WhatsApp).
  - **Fricção do Usuário:** Ferramentas passivas como extensões de navegador atendem apenas usuários de desktop, excluindo mais de 80% dos usuários do SUS que navegam exclusivamente via smartphone.
  - **Arquitetura Desacoplada:** O backend do SUSANA foi projetado em API REST/Streaming (FastAPI), desacoplado do frontend (Next.js). Toda a inteligência de RAG, NLU e Guardrails é exposta em endpoints padronizados, permitindo que a mesma infraestrutura atenda à interface web atual e futuros bots no WhatsApp ou Telegram sem refatoração do motor.

---

### 1.3. Discriminação de Opinião vs. Alegação Factual Verificável
* **Pergunta Original:** *O usuário consegue diferenciar uma opinião, uma interpretação e uma alegação factual verificável?*
* **Label:** `USUÁRIO` 🟢
* **Status:** **Respondida e Implementada**
* **Fundamentação Técnica:**  
  O cidadão médio não faz essa distinção ao interagir com assistentes virtuais. Expressões com forte carga emocional (*"achei o atendimento péssimo"*, *"ouvi dizer que o postinho não presta"*) misturam-se com perguntas factuais (*"qual horário da UBS?"*).
  - **Tratamento no SUSANA:** Implementamos uma esteira de triagem de NLU e classificação de intenção (*IntentRouter*) que isola desabafos e saudações, direcionando apenas perguntas operacionais e factuais para o banco vetorial, evitando que o modelo tente 'responder' a opiniões subjetivas como se fossem fatos.

---

### 1.4. Usuário Prioritário e Situações Críticas de Atendimento
* **Pergunta Original:** *Quem é o usuário prioritário da solução e em quais situações ele precisa verificar uma informação de saúde?*
* **Label:** `USUÁRIO` 🟢
* **Status:** **Respondida e Mapeada (Personas)**
* **Fundamentação Técnica:**  
  Identificamos três perfis centrais e momentos críticos de necessidade:
  1. **Mãe Trabalhadora com Filho Pequeno (Persona Camila):** Demanda imunização infantil fora do horário comercial regular. *Cenário Crítico:* saber quais UBSs ofertam o programa *Saúde na Hora* (atendimento até as 22h).
  2. **Idoso Polimedicado / Doença Crônica (Persona Seu Raimundo):** Necessita de medicamentos especializados (alto custo) ou básicos contínuos. *Cenário Crítico:* entender o passo a passo documental do CEAF/LME para não perder viagem.
  3. **Trabalhador Autônomo com Sintoma Agudo (Persona Felipe):** Dúvida na porta de entrada entre postinho de saúde e pronto atendimento 24h. *Cenário Crítico:* saber a diferença de perfil entre UBS e UPA em horário noturno.

---

### 1.5. Representatividade dos Datasets Brasileiros de Saúde
* **Pergunta Original:** *Os datasets brasileiros disponíveis são representativos o suficiente para desenvolver uma solução de detecção/verificação de desinformação em saúde?*
* **Label:** `DADOS` 🔵
* **Status:** **Respondida e Mitigada**
* **Fundamentação Técnica:**  
  Datasets genéricos pré-existentes (como Fake.br ou corpora acadêmicos de fact-checking) são insuficientes para a realidade operacional do SUS. Eles carecem de termos locais (nomes de quadras, UBSs, regionais de saúde) e da linguagem popular do cidadão brasiliense (*"postinho do Setor O"*, *"remédio pra diabetes no alto custo"*).
  - **Decisão no Projeto:** Em vez de depender de bases abertas desatualizadas, construímos um corpus próprio e higienizado com mais de **2.280 blocos oficiais** da SES-DF e do Ministério da Saúde, além de um dicionário toponímico específico do Distrito Federal.

---

### 1.6. Desafio dos Conteúdos Multimodais no MVP
* **Pergunta Original:** *Quais tipos de conteúdo representam maior desafio para a verificação automatizada: texto, imagem, áudio, vídeo ou conteúdos multimodais?*
* **Label:** `DADOS` 🔵
* **Status:** **Respondida (Decisão de Escopo)**
* **Fundamentação Técnica:**  
  Vídeos curtos (TikTok, Reels) e áudios de mensageiros (WhatsApp) representam o pico de complexidade computacional, exigindo alinhamento de timestamps, transcrição via Whisper e análise de frames visuais.
  - **Definição para o MVP:** Foco 100% em processamento de texto e queries em linguagem natural. A multimodalidade de áudio foi documentada como evolução futura, garantindo que o núcleo conversacional tivesse latência baixa e alta precisão.

---

### 1.7. [NOVA] Prevenção de Alucinação e Risco Clínico (Fail-Closed)
* **Pergunta:** *Como garantir que a assistente nunca atue como médica, nunca prescreva remédios e não invente telefones ou procedimentos inexistentes?*
* **Label:** `MODELO` 🟣 / `PRODUÇÃO` ⚫
* **Status:** **Respondida e Implementada**
* **Fundamentação Técnica:**  
  Implementação de **dupla camada de proteção**:
  1. **Guardrail Clínico Pré-LLM:** Avaliação via regex semântico e classificador MLflow. Se o cidadão relatar sintomas graves ou pedir dosagem de remédio, o sistema bloqueia em menos de **10 milissegundos** e emite resposta padrão com encaminhamento ao SAMU 192 ou acolhimento na UBS.
  2. **Validador Sintático Anti-Alucinação:** O pipeline proíbe números de telefone que não correspondam aos canais oficiais auditados (Ouvidoria 160 e Disque Saúde 136). Se o telefone local da unidade não constar no corpus, o sistema admite a ausência e fornece o endereço físico.

---

### 1.8. [NOVA] Resolução de Toponímia e Regionalismos do Distrito Federal
* **Pergunta:** *Como garantir que a IA compreenda o endereçamento e a divisão territorial única de Brasília (RAs, Quadras, Entorno) sem misturar regiões?*
* **Label:** `DADOS` 🔵 / `MODELO` 🟣
* **Status:** **Respondida e Implementada**
* **Fundamentação Técnica:**  
  Brasília não utiliza o padrão tradicional de ruas e bairros. Desenvolvemos o módulo `DF_TOPONYMY_EXPANSIONS`, que mapeia automaticamente:
  - *"Setor O"* e *"P Sul"* ➔ Ceilândia (QNO / QNP);
  - Siglas de quadras (*QNM, QNL, QNG, QS*) ➔ suas respectivas Regiões Administrativas;
  - Desacoplamento conversacional: se o usuário perguntou sobre Ceilândia e depois muda para Taguatinga, o histórico anterior é isolado para evitar contaminação geográfica.

---

## 2. 📋 PLANEJAR (Arquitetura, Fontes e Engenharia de Produção)

### 2.1. Resposta diante de Evidências Insuficientes ou em Evolução
* **Pergunta Original:** *Como o sistema deve responder quando as evidências científicas forem insuficientes, contraditórias ou estiverem em evolução?*
* **Label:** `MODELO` 🟣
* **Status:** **Planejada e Implementada**
* **Resposta Técnica:**  
  O sistema adota o princípio de **Fail-Closed**. Quando o limiar de similaridade semântica não atinge o score de corte confiável, a assistente não especula:
  > *"Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta. Tente reformular ou pergunte sobre unidades de saúde, vacinação, ou serviços da SES-DF."*

---

### 2.2. Padrões Linguísticos da Desinformação em Saúde no Brasil
* **Pergunta Original:** *Quais características distinguem, com maior frequência, conteúdos verdadeiros, falsos e enganosos sobre saúde no contexto brasileiro?*
* **Label:** `DADOS` 🔵
* **Status:** **Planejada e Documentada**
* **Resposta Técnica:**  
  - **Falsos:** Apelos de urgência (*"compartilhe antes que apaguem"*), conspirações institucionais (*"a Anvisa esconde a cura"*), ingredientes caseiros milagrosos e ausência de CRM ou órgão emissor.
  - **Enganosos:** Manipulação de probabilidades reais (ex: pegar um efeito colateral raro de bula e tratá-lo como regra certa).
  - **Verdadeiros/Oficiais:** Linguagem técnica equilibrada, referência a protocolos clínicos (PCDT), dosagens atreladas a diagnóstico presencial e fontes governamentais.

---

### 2.3. Disponibilidade de Dados Científicos e Oficiais Brasileiros
* **Pergunta Original:** *Qual é a disponibilidade de dados científicos e oficiais que poderiam alimentar um sistema de verificação de alegações sobre saúde?*
* **Label:** `DADOS` 🔵
* **Status:** **Planejada e Integrada**
* **Resposta Técnica:**  
  A disponibilidade no Brasil é alta, porém descentralizada e muitas vezes em formatos não amigáveis (PDFs de portarias, tabelas complexas). O projeto SUSANA estruturou um pipeline de ingestão que consumiu:
  - Dados abertos da SES-DF e InfoSaúde;
  - Relação de Medicamentos do DF (REME-DF 2025);
  - Diretórios do Componente Especializado da Assistência Farmacêutica (CEAF);
  - Calendário Nacional de Imunização do Ministério da Saúde.

---

### 2.4. Redução de Vieses de Modelos e Datasets
* **Pergunta Original:** *Como reduzir o risco de o próprio sistema reproduzir vieses das fontes, datasets ou modelos de IA utilizados?*
* **Label:** `MODELO` 🟣
* **Status:** **Planejada e Implementada**
* **Resposta Técnica:**  
  - **Isolamento de Conhecimento (Zero-Shot RAG):** O LLM é instruído com *system prompts* estritos a não responder utilizando conhecimento pré-treinado livre sobre tratamentos clínicos, atuando como sintetizador exclusivo dos trechos oficiais recuperados.
  - **Citações com Link Direto:** Todas as respostas trazem a referência e o link oficial da Secretaria de Saúde ou do Ministério da Saúde.

---

### 2.5. Atualização Contínua da Base de Conhecimento
* **Pergunta Original:** *Como manter automaticamente atualizada a base de evidências utilizada pelo sistema?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Planejada e Estruturada**
* **Resposta Técnica:**  
  Arquitetura baseada em ingestão orientada a eventos:
  - Módulos `IngestionProcessor` e `ScopedOnlineSearchComplementer`;
  - Auto-sincronização no *startup* do backend (verifica se novos arquivos foram depositados no Corpus e recalcula embeddings de blocos alterados);
  - Invalidação automática do cache semântico sempre que a base é reindexada.

---

### 2.6. Apresentação Progressiva de Evidências (UX)
* **Pergunta Original:** *Como o sistema deve apresentar evidências para que o usuário consiga compreender por que determinada alegação foi considerada falsa, enganosa ou não verificável?*
* **Label:** `MODELO` 🟣 / `USUÁRIO` 🟢
* **Status:** **Planejada e Implementada**
* **Resposta Técnica:**  
  Uso do padrão **Progressive Disclosure**:
  1. **Resposta Direta:** Texto claro e acessível em linguagem cidadã no topo da bolha de chat.
  2. **Chips Interativos de Próximos Passos:** Botões com ações sugeridas (ex: *"Documentos necessários"*, *"Horários de atendimento"*).
  3. **Dropdown de Fontes Oficiais:** Lista colapsável contendo título do documento, trecho utilizado e link oficial para verificação.

---

### 2.7. Escolha Arquitetural: RAG Local vs. Fine-Tuning
* **Pergunta Original:** *Qual arquitetura de IA apresenta melhor equilíbrio entre precisão, explicabilidade, custo e facilidade de implementação para o MVP?*
* **Label:** `MODELO` 🟣
* **Status:** **Planejada e Implementada**
* **Resposta Técnica:**  
  A arquitetura escolhida foi **RAG Híbrido com LLM Local**:
  - *Por que não Fine-Tuning?* O fine-tuning 'congela' dados na rede neural, tornando a atualização de novos horários ou vacinas cara e demorada, além de manter o risco de alucinação sem rastreabilidade.
  - *Vantagem do RAG:* Atualização imediata de dados (basta atualizar o documento no disco), explicabilidade ponta a ponta e custo computacional previsível.

---

### 2.8. [NOVA] Adoção da Busca Híbrida (Dense Vector + BM25 com RRF)
* **Pergunta:** *Por que modelos densos de embedding falham em termos farmacêuticos e códigos exatos, e como a busca híbrida resolve?*
* **Label:** `MODELO` 🟣
* **Status:** **Planejada e Implementada**
* **Resposta Técnica:**  
  Embeddings densos são excelentes para semântica (*"estou com tosse" ➔ sintomas gripais*), mas sofrem com códigos alfanuméricos e nomes de princípios ativos (*"PCDT"*, *"LME"*, *"Dolutegravir"*, *"UBS 12"*).
  - Implementamos o **BM25 Okapi** em conjunto com a busca densa do ChromaDB, combinando os resultados via **Reciprocal Rank Fusion (RRF)** com constante $k=60$. O resultado garantiu **100% de precisão** na recuperação de medicamentos especializados.

---

### 2.9. [NOVA] Privacidade e Conformidade com a LGPD
* **Pergunta:** *Como tratar dados de saúde de cidadãos sem violar a Lei Geral de Proteção de Dados (LGPD)?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Planejada e Implementada**
* **Resposta Técnica:**  
  - Todo o pipeline de inferência (Ollama `llama3.1:8b` e Sentence-Transformers) roda **localmente na infraestrutura do projeto**, sem envio de prompts ou telemetria para servidores de terceiros no exterior.
  - Armazenamento de sessões com IDs anonimizados (UUIDv4) e descarte de dados sensíveis na camada de logging.

---

## 3. ⏳ SE SOBRAR TEMPO (Melhorias e Expansões de Valor)

### 3.1. Literacia Digital e Comportamento de Verificação
* **Pergunta Original:** *O nível de conhecimento digital / analfabetismo digital está relacionado ao comportamento de verificação de informações?*
* **Label:** `USUÁRIO` 🟢
* **Status:** **Respondida em Pesquisa**
* **Resposta Técnica:**  
  Estudos de inclusão digital demonstram correlação direta: cidadãos com baixa literacia digital dependem fortemente de interfaces conversacionais guiadas e botões visuais, pois têm dificuldade de formular *queries* complexas por texto. Essa constatação motivou a inclusão dos *chips* automáticos de sugestão após cada resposta da Susana.

---

### 3.2. Riscos Éticos e Jurídicos na Validação de Conteúdos
* **Pergunta Original:** *Quais são os riscos éticos e jurídicos de uma IA afirmar que determinado conteúdo é falso?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Respondida e Mitigada**
* **Resposta Técnica:**  
  Afirmações taxativas podem gerar processos por danos morais ou acusações de censura arbitrária. A SUSANA mitiga esse risco posicionando-se não como 'juíza da verdade', mas como **guia informativa oficial**: em vez de dizer *"você está mentindo"*, a assistente responde *"conforme a Portaria SES-DF nº X e o protocolo PCDT, o procedimento oficial é..."*.

---

### 3.3. [NOVA] Integração com Mensageria Popular (WhatsApp / Telegram)
* **Pergunta:** *Como disponibilizar o mesmo motor de inteligência para o cidadão via canais de mensagens instantâneas?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Estruturada para Próximas Sprints**
* **Resposta Técnica:**  
  Como os endpoints da API SUSANA já recebem JSON padronizado e geram respostas limpas em texto plano (ou streaming), a integração exige apenas um serviço de webhook intermediário (como Evolution API ou Twilio), sem necessidade de reescrever o RAG ou os Guardrails.

---

## 4. ✂️ CORTAR SEM DÓ (Descartadas Conscientemente no MVP)

### 4.1. Adaptação Dinâmica a Níveis Extremos de Literacia Científica
* **Pergunta Original:** *Como tornar a solução compreensível para usuários com diferentes níveis de literacia digital e científica?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Cortada do MVP (Substituída por Tom Único Acessível)**
* **Motivo do Corte:** Criar múltiplos motores de geração adaptativa de linguagem (ex: modo acadêmico vs. modo popular infantil) geraria complexidade excessiva de prompts e risco de inconsistência. Padronizou-se um tom de fala institucional, claro, empático e de fácil compreensão para todos os públicos (nível de leitura fundamental).

---

### 4.2. Integração Federativa e Governança Multi-Hospitalar Complexa
* **Pergunta Original:** *Quais condições técnicas, institucionais e de governança seriam necessárias para que a solução pudesse ser adotada por uma universidade pública ou organização de saúde?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Cortada do MVP**
* **Motivo do Corte:** Exigiria acordos de cooperação técnica, comitês de ética interinstitucionais e homologações em instâncias federais que paralisariam a entrega técnica. Focou-se 100% no escopo público do Distrito Federal (SES-DF).

---

### 4.3. [NOVA] Agendamento Transacional Direto no SISREG / e-SUS
* **Pergunta:** *A assistente deve permitir que o cidadão marque consultas e exames diretamente pelo chat?*
* **Label:** `PRODUÇÃO` ⚫
* **Status:** **Cortada do MVP (Mantida Orientação de Fluxo)**
* **Motivo do Corte:** Integração direta com sistemas legados do Ministério da Saúde envolve credenciamento restrito, certificação digital ICP-Brasil e APIs governamentais de alta latência e instabilidade. A assistente agrega imenso valor orientando sobre o comparecimento à UBS de referência para acolhimento e regulação, sem travar o projeto em integrações de terceiros.

---

## 📊 Matriz de Rastreabilidade e Cobertura das Questões

| Bloco | Total de Questões | Status de Atendimento |
| :--- | :---: | :--- |
| **RESPONDER JÁ** | 8 | **100% Implementadas no Core do SUSANA** |
| **PLANEJAR** | 12 | **100% Arquitetadas e Validadas em Homologação** |
| **SE SOBRAR TEMPO** | 3 | **Documentadas e Prontas para Evolução** |
| **CORTAR SEM DÓ** | 3 | **Delimitadas e Justificadas Fora de Escopo** |
| **TOTAL GERAL** | **26 Questões** | **Alinhamento completo entre Descoberta e Produção** |
