# 🧭 Guiding Questions & Caderno Pedagógico CBL — Projeto SUSANA

> **Documento Oficial de Alinhamento Metodológico: Challenge Based Learning (CBL)**  
> **Desafio:** Challenge 1 — Fake News / Desinformação em Saúde Pública  
> **Projeto:** SUSANA (Sistema Único de Saúde com Atendimento e Navegação Aumentada — SES-DF)  
> **Ciclo Metodológico:** Engage → Investigate → Act → Reflect & Share  
> **Repositório:** [https://github.com/Andre-Atlas/SUSANNA-HEALTHCHECK](https://github.com/Andre-Atlas/SUSANNA-HEALTHCHECK) (Branch: `entrega-final`)  

---

# PARTE 1 — DIAGNÓSTICO DO DOCUMENTO E DO DESAFIO

### 1. Contexto e Enquadramento Pedagógico
O material original de partida originou-se de duas fontes complementares:
1. **Diretrizes Oficiais do Desafio:** Estabelece a **Big Idea** ("distinguir fatos, evidências e opiniões através de IA para fortalecer o pensamento crítico"), a **Essential Question** ("Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações sem substituir seu pensamento crítico?") e o **Challenge Roadmap** de 6 semanas (Engage, Investigate, Act e Showcase).
2. **Quadro Operacional de Trabalho (`Challenge 1 - Trello`):** Reuniu 20 cartões investigativos com categorização temática (`DADOS`, `USUÁRIO`, `MODELO`, `PRODUÇÃO`) e faixas de priorização ágil (*RESPONDER JÁ*, *PLANEJAR*, *SE SOBRAR TEMPO*, *CORTAR SEM DÓ*).

### 2. Pontos Fortes Identificados
- **Aderência ao problema real do SUS:** As perguntas não se perderam em abstrações teóricas; abordaram o cidadão vulnerável diante de desinformação médica, surtos epidemiológicos, hesitação vacinal e desorientação na rede de saúde.
- **Raciocínio baseado em evidências (Evidence-Based):** Desde a concepção inicial, rejeitou-se a ideia ingênua de que a IA deveria agir como "árbitro autoritário da verdade", optando pelo fornecimento transparente de evidências oficiais verificáveis.
- **Pragmatismo de engenharia:** A equipe reconheceu cedo limitações de viabilidade (descartando fine-tuning custoso de LLMs e priorizando arquitetura RAG com fontes primárias do SUS-DF).

### 3. Oportunidades de Melhoria e Lacunas Superadas
- **Lacuna entre Desinformação Abstrata e Operação em Saúde Pública:** O desafio geral falava de "fake news em geral"; a equipe precisou especializar as questões para o contexto da Atenção Primária do Distrito Federal, onde a desinformação afeta receitas, horários de UBSs e dispensação de fármacos de alto custo.
- **Segurança Clínica & Guardrails:** Faltava nas questões iniciais uma investigação explícita sobre como evitar que a IA alucinasse prescrições médicas de risco (tratado via Guardrails *fail-closed* na solução SUSANA).
- **Especificidade Territorial (Toponímia DF):** A verificação de serviços de saúde em Brasília exige decodificar Regiões Administrativas e quadras (Setor O, P Sul, Taguatinga, Gama), aspecto não previsto em datasets genéricos.

---

# PARTE 2 — CRITÉRIOS E DECISÕES DE REVISÃO METODOLÓGICA

Para assegurar alinhamento integral com o framework CBL (Nichols & Cator, *Challenge Based Learning Guide*), adotamos as seguintes decisões estruturais:

1. **Preservação Integral das 20 Questões Originais:** Nenhuma das perguntas do quadro ágil original foi excluída. Suas formulações e discussões originais foram mantidas e enriquecidas.
2. **Dupla Matriz de Classificação:**
   - **Eixo CBL:** Identificação da contribuição de cada pergunta nas fases de *Engage* (Problema/Usuário), *Investigate* (Dados/Fontes/Arquitetura) e *Act* (Governança/Produção/Solução).
   - **Eixo Ágil (Trello):** Manutenção explícita das faixas *RESPONDER JÁ*, *PLANEJAR*, *SE SOBRAR TEMPO* e *CORTAR SEM DÓ*.
3. **Formalização das Perguntas Complementares da Equipe (Identificadas com tag [COMPLEMENTAR]):** Foram introduzidas 6 questões que sintetizam os aprendizados das semanas 4, 5 e 6 do projeto (Busca Híbrida BM25+RRF, Segurança Clínica Fail-Closed, Toponímia do DF, LGPD e limites de integração governamental).
4. **Estrutura Pedagógica Padronizada por Pergunta:** Cada questão apresenta:
   - *Pergunta Oficial*;
   - *Etapa CBL & Label Temático*;
   - *Objetivo de Aprendizagem / Investigação*;
   - *Resposta Fundamentada & Evidências no Projeto SUSANA*.

---

# PARTE 3 — DOCUMENTO CBL REVISADO (CADERNO DE INVESTIGAÇÃO)

## 🎯 1. Alinhamento com as Fases do Challenge 1

### A. Big Idea
> *"Em um mundo com excesso de informação, como distinguir fatos, evidências e opiniões? A IA pode apoiar a investigação da confiabilidade das informações, fortalecendo o pensamento crítico em vez de substituí-lo."*

### B. Essential Question
> *"Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações sem substituir seu pensamento crítico?"*  
> **Pilares:** Investigar evidências • Identificar vieses • Construir critérios de confiança.

### C. The Challenge
> **Desafio:** Desenvolver uma solução inteligente (SUSANA) capaz de orientar cidadãos sobre a rede de saúde do SUS-DF, validando informações com dados oficiais, mitigando a automedicação e desmistificando o acesso a remédios, vacinas e postos de saúde de forma rastreável e ética.

### D. Roadmap & Cronograma Executado
* **Semana 1 (Engage • 07/09 a 11/09):** Investigação de casos reais de desinformação, formulação das Guiding Questions iniciais e exploração dos dados abertos de saúde.
* **Semanas 2-3 (Investigate • 14/09 a 25/09):** Definição do produto (Chatbot SUSANA), divisão dos papéis Scrum, EDA dos dados do SUS e auditoria de fontes oficiais (SES-DF / Ministério da Saúde).
* **Semanas 4-5 (Act • 28/09 a 09/10):** Construção da arquitetura RAG Híbrida (BM25 + ChromaDB), engenharia de Guardrails Clínicos e desenvolvimento da interface.
* **Semana 6 (Showcase • 12/10 a 16/10):** Execução do benchmark automatizado (18/18 testes aprovados), consolidação do repositório final e produção do vídeo pitch.

---

## 🗂️ 2. Guiding Questions por Faixa de Priorização

### FAIXA 1: 🚨 RESPONDER JÁ (Investigações Fundamentais do Core)

#### GQ 1.1 — Evidências vs. Classificação Binária (Card #11)
* **Pergunta Original:** *É mais adequado classificar uma notícia como “verdadeira/falsa” ou avaliar a alegação apresentada com base nas evidências disponíveis?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `MODELO` 🟣
* **Objetivo Investigativo:** Avaliar o impacto ético e técnico de modelos classificadores binários em comparação a sistemas de inferência em linguagem natural (NLI) fundamentados em fontes.
* **Resposta & Evidências no SUSANA:**  
  A classificação puramente binária ("Verdadeiro/Falso") é pedagogicamente reducionista e juridicamente arriscada em saúde pública. A desinformação opera através de descontextualização de dados reais (ex.: citar uma reação adversa rara para condenar uma vacina inteira).  
  No SUSANA, adotamos o princípio da **Verificação Centrada em Evidências**: o modelo não emite carimbos acusatórios de "Fake"; em vez disso, recupera o trecho oficial da Portaria ou Nota Técnica da SES-DF, apresenta as evidências textuais e fornece o link direto para que o próprio cidadão ejerça seu pensamento crítico.

---

#### GQ 1.2 — Formato de Produto de Maior Valor e Menor Fricção (Card #16)
* **Pergunta Original:** *Qual formato de produto apresenta maior valor para o usuário: ferramenta de consulta ativa, extensão de navegador, chatbot ou sistema integrado ao fluxo de consumo de notícias?*
* **Fase CBL:** `Engage` ➔ `Act` | **Label:** `PRODUÇÃO` ⚫
* **Objetivo Investigativo:** Analisar a jornada do paciente e identificar qual canal de entrega oferece menor barreira de acesso à informação pública de saúde.
* **Resposta & Evidências no SUSANA:**  
  Extensões de navegador restringem o acesso a desktops, excluindo a maioria dos usuários do SUS que acessam a internet prioritariamente via smartphones. Ferramentas ativas de busca em tabelas geram sobrecarga cognitiva.  
  Definiu-se o **Chatbot Conversacional Web Responsivo** com linguagem natural humanizada e botões interativos (*chips*), desacoplado em arquitetura REST/Streaming (FastAPI + Next.js), permitindo reutilização imediata em canais de mensageria como WhatsApp.

---

#### GQ 1.3 — Discriminação entre Opinião, Interpretação e Fato (Card #8)
* **Pergunta Original:** *O usuário consegue diferenciar uma opinião, uma interpretação e uma alegação factual verificável?*
* **Fase CBL:** `Engage` ➔ `Investigate` | **Label:** `USUÁRIO` 🟢
* **Objetivo Investigativo:** Investigar o comportamento psicológico do usuário ao expressar queixas versus dúvidas técnicas de atendimento.
* **Resposta & Evidências no SUSANA:**  
  O usuário médio mescla desabafos subjetivos (*"não gosto daquele postinho"*) com demandas factuais (*"onde tem vacina da dengue?"*).  
  O SUSANA implementou um módulo de **NLU e Roteamento de Intenção (`IntentRouter`)** que identifica quando a entrada é uma mera opinião ou saudação e quando há uma alegação que exige recuperação de documentos no banco vetorial, evitando respostas inadequadas ou desperdício de tokens.

---

#### GQ 1.4 — Mapeamento do Usuário Prioritário e Situações Críticas (Card #6)
* **Pergunta Original:** *Quem é o usuário prioritário da solução e em quais situações ele precisa verificar uma informação de saúde?*
* **Fase CBL:** `Engage` | **Label:** `USUÁRIO` 🟢
* **Objetivo Investigativo:** Delinear os perfis de cidadãos mais vulneráveis à desinformação ou com maiores dificuldades de navegação no SUS.
* **Resposta & Evidências no SUSANA:**  
  O projeto modelou três personas representativas:
  1. **Camila (Mãe Jovem - 24 anos):** Necessita de vacinação infantil fora do expediente regular (demanda por UBSs do programa *Saúde na Hora* abertas até as 22h).
  2. **Seu Raimundo (Idoso Crônico - 68 anos):** Precisa de medicamentos contínuos e laudos do Componente Especializado (CEAF/LME) sem retrabalho documental.
  3. **Felipe (Autônomo - 35 anos):** Busca atendimento de urgência noturna e precisa discernir a função de uma UPA 24h versus uma UBS.

---

#### GQ 1.5 — Representatividade dos Datasets Brasileiros (Card #2)
* **Pergunta Original:** *Os datasets brasileiros disponíveis são representativos o suficiente para desenvolver uma solução de detecção/verificação de desinformação em saúde?*
* **Fase CBL:** `Investigate` | **Label:** `DADOS` 🔵
* **Objetivo Investigativo:** Mapear a viabilidade de treinar modelos supervisionados a partir de bases públicas de desinformação no Brasil.
* **Resposta & Evidências no SUSANA:**  
  Datasets existentes (Fake.br, bases de agências de fact-checking) são genéricos e não cobrem regionalismos da saúde no DF nem termos farmacêuticos específicos do SUS.  
  A solução foi construir um **Corpus Territorializado Próprio**, saneando e indexando 2.283 blocos oficiais (REME-DF, diretórios de UBSs/UPAs, cartilhas da Atenção Primária e protocolos de medicamentos).

---

#### GQ 1.6 — Complexidade Multimodal: Texto, Áudio e Vídeo (Card #5)
* **Pergunta Original:** *Quais tipos de conteúdo representam maior desafio para a verificação automatizada: texto, imagem, áudio, vídeo ou conteúdos multimodais?*
* **Fase CBL:** `Investigate` | **Label:** `DADOS` 🔵
* **Objetivo Investigativo:** Analisar custos computacionais, latência e viabilidade técnica no processamento de diferentes mídias no escopo de um MVP acadêmico.
* **Resposta & Evidências no SUSANA:**  
  Áudios de WhatsApp e vídeos curtos possuem descontextualização cruzada e demandam transcrição pesada (Speech-to-Text), multiplicando o tempo de resposta e o consumo de hardware.  
  **Decisão de Escopo do MVP:** O time priorizou a excelência no processamento textual de alta precisão e consultas em linguagem natural, postergando o processamento multimodal pesado para iterações futuras.

---

#### GQ 1.7 [COMPLEMENTAR] — Salvaguarda Clínica Instantânea e Princípio Fail-Closed
* **Pergunta:** *Como garantir que a IA nunca realize diagnósticos, não prescreva remédios e adote comportamento estritamente seguro em situações de emergência?*
* **Fase CBL:** `Act` | **Label:** `MODELO` 🟣 / `PRODUÇÃO` ⚫
* **Objetivo Investigativo:** Formular e testar salvaguardas éticas e regulatórias para impedir automedicação incentivada por modelos generativos.
* **Resposta & Evidências no SUSANA:**  
  Implementação de um **Guardrail Clínico Pré-LLM** que atua em menos de **10 milissegundos** via regex e modelo supervisionado. Qualquer menção a dosagens de remédios controlados ou sintomas graves de emergência é bloqueada instantaneamente, orientando o encaminhamento ao SAMU 192 ou acolhimento na UBS mais próxima.

---

#### GQ 1.8 [COMPLEMENTAR] — Desambiguação da Toponímia do Distrito Federal
* **Pergunta:** *Como fazer com que a IA compreenda as peculiaridades do endereçamento de Brasília (Regiões Administrativas, quadras e setores) sem alucinar cidades de outros estados?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `DADOS` 🔵 / `MODELO` 🟣
* **Objetivo Investigativo:** Resolver a barreira geográfica local em modelos de linguagem pré-treinados globalmente.
* **Resposta & Evidências no SUSANA:**  
  Criação do módulo `DF_TOPONYMY_EXPANSIONS` e isolamento anafórico contextual: a assistente sabe que *Setor O* e *P Sul* pertencem a Ceilândia, correlaciona siglas de quadras com UBSs correspondentes e não mistura RAs ao longo de conversas multi-turn.

---

### FAIXA 2: 📋 PLANEJAR (Arquitetura, Governança e Engenharia de Evidências)

#### GQ 2.1 — Tratamento de Evidências Insuficientes ou Contraditórias (Card #14)
* **Pergunta Original:** *Como o sistema deve responder quando as evidências científicas forem insuficientes, contraditórias ou estiverem em evolução?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `MODELO` 🟣
* **Objetivo Investigativo:** Modelar o comportamento de abstenção da IA (*abstention policy*) para evitar que invente respostas plausíveis na ausência de fatos.
* **Resposta & Evidências no SUSANA:**  
  Configurou-se uma regra de *fail-closed* baseada em limiar de similaridade semântica: quando o corpus não contém informação oficial suficiente, o modelo se recusa a conjeturar e declara: *"Não encontrei informação suficiente nas fontes oficiais disponíveis para responder a essa pergunta."*, orientando a Ouvidoria 160.

---

#### GQ 2.2 — Marcadores de Desinformação em Saúde no Brasil (Card #1)
* **Pergunta Original:** *Quais características distinguem, com maior frequência, conteúdos verdadeiros, falsos e enganosos sobre saúde no contexto brasileiro?*
* **Fase CBL:** `Investigate` | **Label:** `DADOS` 🔵
* **Objetivo Investigativo:** Analisar a morfologia textual da desinformação em saúde no ecossistema digital brasileiro.
* **Resposta & Evidências no SUSANA:**  
  - **Falsos:** Apelos emocionais extremados de medo ou urgência, promessa de curas fáceis e teorias da conspiração contra agências reguladoras (Anvisa/Ministério da Saúde).
  - **Enganosos:** Hiperbolização de dados estatísticos reais retirados de contexto.
  - **Oficiais:** Linguagem técnica e cautelosa, amparada em portarias, leis e comitês científicos colegiados.

---

#### GQ 2.3 — Mapeamento e Ingestão de Fontes Oficiais de Saúde (Card #4)
* **Pergunta Original:** *Qual é a disponibilidade de dados científicos e oficiais que poderiam alimentar um sistema de verificação de alegações sobre saúde?*
* **Fase CBL:** `Investigate` | **Label:** `DADOS` 🔵
* **Objetivo Investigativo:** Catalogar a dispersão dos repositórios governamentais e planejar rotinas de extração e tratamento de dados.
* **Resposta & Evidências no SUSANA:**  
  A disponibilidade de dados é abundante, mas fragmentada em formatos hostis (tabelas soltas, PDFs digitalizados). O projeto executou o saneamento do corpus oficial da SES-DF, convertendo a Carta de Serviços, painéis do InfoSaúde e a lista da REME-DF em blocos semânticos estruturados com metadados de procedência.

---

#### GQ 2.4 — Prevenção de Vieses nos Modelos de IA (Card #15)
* **Pergunta Original:** *Como reduzir o risco de o próprio sistema reproduzir vieses das fontes, datasets ou modelos de IA utilizados?*
* **Fase CBL:** `Investigate` | **Label:** `MODELO` 🟣
* **Objetivo Investigativo:** Isolar o viés cognitivo nativo de modelos fundacionais generalistas através de restrições de ancoragem em contexto.
* **Resposta & Evidências no SUSANA:**  
  Adoção estrita de **RAG com Ancoragem Exclusiva**: o LLM é parametrizado com temperatura controlada e instruções de sistema que o proíbem de usar memória pré-treinada para inventar dados clínicos, operando como sumarizador e explicador das fontes recuperadas do banco vetorial.

---

#### GQ 2.5 — Automação da Atualização da Base de Evidências (Card #19)
* **Pergunta Original:** *Como manter automaticamente atualizada a base de evidências utilizada pelo sistema?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `PRODUÇÃO` ⚫
* **Objetivo Investigativo:** Desenhar a arquitetura de MLOps para sincronização e versionamento do banco de dados vetorial.
* **Resposta & Evidências no SUSANA:**  
  Desenvolveu-se um pipeline de auto-indexação inteligente no boot da API: o sistema audita os hashes dos arquivos locais do Corpus, sincroniza automaticamente novos blocos no ChromaDB e invalida o cache semântico de consultas prévias.

---

#### GQ 2.6 — Apresentação Transparente de Evidências na Interface (Card #13)
* **Pergunta Original:** *Como o sistema deve apresentar evidências para que o usuário consiga compreender por que determinada alegação foi considerada falsa, enganosa ou não verificável?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `MODELO` 🟣 / `USUÁRIO` 🟢
* **Objetivo Investigativo:** Criar padrões visuais de explicabilidade que aumentem a confiança do cidadão sem sobrecarregá-lo com jargões técnicos.
* **Resposta & Evidências no SUSANA:**  
  Aplicação do conceito de **Divulgação Progressiva (*Progressive Disclosure*)**: resposta em linguagem direta no topo, chips interativos com perguntas frequentes e um card retrátil com citações textuais exatas e links para o portal da Secretaria de Saúde do DF.

---

#### GQ 2.7 — Arquitetura de IA para o MVP: RAG vs. Fine-Tuning (Card #12)
* **Pergunta Original:** *Qual arquitetura de IA apresenta melhor equilíbrio entre precisão, explicabilidade, custo e facilidade de implementação para o MVP?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `MODELO` 🟣
* **Objetivo Investigativo:** Avaliar trade-offs de infraestrutura, custo de GPU e explicabilidade entre ajuste fino e recuperação contextualizada.
* **Resposta & Evidências no SUSANA:**  
  A equipe optou por **RAG Híbrido com LLM Local** (`llama3.1:8b` via Ollama). O Fine-tuning congelaria pesos e exigiria novo treino a cada mudança de endereço de UBS; o RAG garante explicabilidade imediata, auditabilidade e atualização sem custo de re-treinamento.

---

#### GQ 2.8 — UX Empática e Design Não Conflituoso (Card #7)
* **Pergunta Original:** *Quais características da interface facilitam ou dificultam a compreensão de uma classificação de desinformação?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `USUÁRIO` 🟢
* **Objetivo Investigativo:** Investigar o "efeito bumerangue" na psicologia da comunicação (reação defensiva ao ser corrigido de forma agressiva).
* **Resposta & Evidências no SUSANA:**  
  Evitou-se o uso de termos estigmatizantes como "Burrice" ou "Fake News!". A interface da Susana acolhe a dúvida, valida a preocupação do cidadão e orienta o caminho correto de forma respeitosa e institucional.

---

#### GQ 2.9 — Whitelist de Fontes Fidedignas Brasileiras (Card #3)
* **Pergunta Original:** *Quais fontes brasileiras podem ser consideradas referências confiáveis para verificar alegações de saúde?*
* **Fase CBL:** `Investigate` | **Label:** `DADOS` 🔵
* **Objetivo Investigativo:** Definir a cadeia de custódia e os critérios de aceitação de documentos no banco de conhecimento do projeto.
* **Resposta & Evidências no SUSANA:**  
  Estruturou-se uma whitelist institucional rigorosa: Diário Oficial do DF (DODF), Portal da SES-DF, Ministério da Saúde, Fiocruz, Anvisa e Biblioteca Virtual em Saúde (BVS/BIREME). Blogs informais e notícias sem validação científica foram excluídos da indexação.

---

#### GQ 2.10 — Fatores Psicológicos de Compartilhamento Desatento (Card #9)
* **Pergunta Original:** *Quais fatores influenciam a decisão de compartilhar uma informação de saúde sem verificar sua veracidade?*
* **Fase CBL:** `Engage` ➔ `Investigate` | **Label:** `USUÁRIO` 🟢
* **Objetivo Investigativo:** Compreender os gatilhos emocionais (medo de epidemias, desejo de proteger a família) que reduzem o pensamento crítico.
* **Resposta & Evidências no SUSANA:**  
  A desinformação em saúde prospera na ansiedade e no medo de escassez (ex.: *"vai faltar vacina"*). A SUSANA combate essa ansiedade oferecendo respostas rápidas sobre a disponibilidade real de vacinas e medicamentos, reduzindo a sensação de desamparo que leva ao compartilhamento desesperado.

---

#### GQ 2.11 [COMPLEMENTAR] — Busca Híbrida: BM25 Okapi + ChromaDB com RRF
* **Pergunta:** *Por que buscas exclusivamente semânticas falham em nomes exatos de remédios e siglas do SUS, e como resolver essa lacuna?*
* **Fase CBL:** `Act` | **Label:** `MODELO` 🟣
* **Objetivo Investigativo:** Otimizar o pipeline de recuperação de informação para termos específicos da farmacopeia e legislação de saúde pública.
* **Resposta & Evidências no SUSANA:**  
  Implementação de **Busca Híbrida com Reciprocal Rank Fusion (RRF, k=60)**, combinando a representação densa do modelo multilingue com o índice esparso BM25 Okapi. Isso garantiu 100% de precisão em termos como *Dolutegravir*, *Tenofovir*, *LME* e *PCDT*.

---

#### GQ 2.12 [COMPLEMENTAR] — Proteção de Dados Sensíveis e Conformidade com a LGPD
* **Pergunta:** *Como garantir que a operação de uma IA no setor público preserve a privacidade dos dados de saúde dos usuários?*
* **Fase CBL:** `Act` | **Label:** `PRODUÇÃO` ⚫
* **Objetivo Investigativo:** Adequar a arquitetura técnica às exigências da Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018).
* **Resposta & Evidências no SUSANA:**  
  Toda a computação de inferência de linguagem e busca vetorial ocorre **on-premises / localmente** na infraestrutura do backend, sem envio de conversas para APIs comerciais fechadas fora do país, com sessões anônimas efêmeras.

---

### FAIXA 3: ⏳ SE SOBRAR TEMPO (Investigações de Extensão e Escalabilidade)

#### GQ 3.1 — Literacia Digital e Inclusão Social (Card #10)
* **Pergunta Original:** *O nível de conhecimento digital / analfabetismo digital está relacionado ao comportamento de verificação de informações?*
* **Fase CBL:** `Investigate` ➔ `Act` | **Label:** `USUÁRIO` 🟢
* **Objetivo Investigativo:** Analisar como diferentes níveis de escolaridade e fluência digital impactam a capacidade de navegar em serviços eletrônicos de saúde.
* **Resposta & Evidências no SUSANA:**  
  Populações com menor escolaridade têm dificuldade em preencher formulários web tradicionais, mas dominam interfaces conversacionais de áudio e texto. A interface foi mantida simples, com tipografia legível, contraste acessível e botões de atalho para dúvidas comuns.

---

#### GQ 3.2 — Riscos Éticos e Jurídicos de Assertivas Automatizadas (Card #18)
* **Pergunta Original:** *Quais são os riscos éticos e jurídicos de uma IA afirmar que determinado conteúdo é falso?*
* **Fase CBL:** `Act` | **Label:** `PRODUÇÃO` ⚫
* **Objetivo Investigativo:** Avaliar a responsabilidade civil do Estado e de desenvolvedores perante a curadoria algorítmica de conteúdos.
* **Resposta & Evidências no SUSANA:**  
  Afirmações de falsidade sem respaldo podem ensejar litígios judiciais. A SUSANA mitiga esse passivo mantendo um papel consultivo e informativo: em vez de julgar opiniões, apresenta o posicionamento normativo oficial da SES-DF e direciona os casos ambíguos para o canal da Ouvidoria 160.

---

#### GQ 3.3 [COMPLEMENTAR] — Arquitetura Omnichannel para Mensageria Instantânea
* **Pergunta:** *Como transportar a solução para aplicativos de mensagens de uso massivo sem reescrever a inteligência central?*
* **Fase CBL:** `Act` | **Label:** `PRODUÇÃO` ⚫
* **Objetivo Investigativo:** Garantir modularidade arquitetural para que o backend RAG atue como hub de múltiplos canais.
* **Resposta & Evidências no SUSANA:**  
  A API FastAPI do SUSANA expõe endpoints REST stateless e stream via Server-Sent Events/NDJSON. Essa separação permite conectar um bot de WhatsApp (via Baileys/Evolution API) simplesmente repassando as requisições ao pipeline existente sem qualquer alteração na lógica de negócio.

---

### FAIXA 4: ✂️ CORTAR SEM DÓ (Delimitação Consciente de Fronteiras / Fora de Escopo)

#### GQ 4.1 — Adaptação Dinâmica de Múltiplos Registros Científicos (Card #17)
* **Pergunta Original:** *Como tornar a solução compreensível para usuários com diferentes níveis de literacia digital e científica?*
* **Fase CBL:** `Act` | **Label:** `PRODUÇÃO` ⚫
* **Status:** **Cortada do MVP (Substituída por Tom Único Acessível)**
* **Justificativa Metodológica do Corte:**  
  Desenvolver motores que alteram o registro de fala (modo especialista vs. modo popular) aumentaria a complexidade de avaliação e aumentaria a variabilidade de respostas. Decidiu-se padronizar a persona da assistente em uma linguagem acolhedora, clara e acessível a qualquer nível de escolaridade.

---

#### GQ 4.2 — Condições Federativas para Adoção Institucional em Larga Escala (Card #20)
* **Pergunta Original:** *Quais condições técnicas, institucionais e de governança seriam necessárias para que a solução pudesse ser adotada por uma universidade pública ou organização de saúde?*
* **Fase CBL:** `Act` | **Label:** `PRODUÇÃO` ⚫
* **Status:** **Cortada do MVP (Foco Restrito ao Distrito Federal)**
* **Justificativa Metodológica do Corte:**  
  A expansão federativa exigiria acordos de governança interministeriais, homologação em múltiplos estados e infraestrutura distribuída de alta complexidade. O time delimitou a atuação ao escopo da Secretaria de Saúde do DF (SES-DF), assegurando validação profunda em um território delimitado.

---

#### GQ 4.3 [COMPLEMENTAR] — Agendamento Transacional Direto no SISREG / e-SUS
* **Pergunta:** *O assistente deve permitir a marcação ativa e cancelamento de consultas no sistema de regulação de leitos e ambulatórios?*
* **Fase CBL:** `Act` | **Label:** `PRODUÇÃO` ⚫
* **Status:** **Cortada do MVP (Foco na Orientação de Acolhimento)**
* **Justificativa Metodológica do Corte:**  
  A integração direta com os bancos de dados do SISREG e Prontuário Eletrônico do Cidadão (e-SUS PEC) demanda credenciamento institucional restrito do Ministério da Saúde, certificado digital ICP-Brasil e risco de indisponibilidade de rede. A assistente resolve a dor do cidadão orientando sobre o acolhimento presencial na UBS e os documentos para inserção na fila de regulação.

---

# PARTE 4 — REGISTRO DAS ALTERAÇÕES E RASTREABILIDADE

| ID Original | Pergunta Resumida | Ação Realizada | Justificativa Pedagógica & Técnica |
| :---: | :--- | :---: | :--- |
| **Card #1** | Distinção de conteúdos verdadeiros/falsos | **Mantida e Fundamentada** | Essencial para compreender a anatomia da desinformação em saúde. |
| **Card #2** | Representatividade de datasets brasileiros | **Mantida e Complementada** | Demonstra a necessidade de criar o corpus proprietário de 2.283 blocos. |
| **Card #3** | Fontes confiáveis brasileiras (Whitelist) | **Mantida e Mapeada** | Estabeleceu os limites institucionais dos documentos indexados. |
| **Card #4** | Disponibilidade de dados oficiais no Brasil | **Mantida e Fundamentada** | Justifica o esforço de engenharia de dados e ETL do projeto. |
| **Card #5** | Desafio de conteúdos multimodais | **Mantida e Delimitada** | Explica por que o MVP focou em texto e queries em linguagem natural. |
| **Card #6** | Usuário prioritário e situações críticas | **Mantida e Detalhada** | Conecta as perguntas às personas reais (Camila, Raimundo, Felipe). |
| **Card #7** | Características de interface e empatia | **Mantida e Implementada** | Guiou o design visual da Susana sem carimbos agressivos de "Fake". |
| **Card #8** | Discriminação de opinião vs. fato verificável | **Mantida e Resolvida** | Fundamenta a criação da esteira de triagem de NLU e Intent Router. |
| **Card #9** | Fatores de compartilhamento desatento | **Mantida e Analisada** | Ancora o entendimento psicológico da ansiedade do paciente. |
| **Card #10**| Literacia digital e verificação | **Mantida (Se Sobrar Tempo)** | Justifica a inclusão de chips e navegação guiada por botões. |
| **Card #11**| Verificação por evidências vs. binária | **Mantida e Priorizada** | Pilar ético do projeto: apresentar trechos oficiais com fontes. |
| **Card #12**| Arquitetura MVP: RAG vs. Fine-Tuning | **Mantida e Documentada** | Justificativa formal da escolha por RAG Híbrido com LLM local. |
| **Card #13**| Apresentação progressiva de evidências | **Mantida e Implementada** | Padrão UX aplicado no frontend Next.js (dropdowns e fontes). |
| **Card #14**| Evidências insuficientes ou em evolução | **Mantida e Implementada** | Estabelece a regra de fail-closed para perguntas sem dados no corpus. |
| **Card #15**| Mitigação de vieses em modelos e dados | **Mantida e Implementada** | Fundamenta a proibição de alucinação livre pelo modelo gerador. |
| **Card #16**| Formato de maior valor (Chatbot) | **Mantida e Implementada** | Decisão de arquitetura: API FastAPI desacoplada com streaming. |
| **Card #17**| Adaptação dinâmica de literacia | **Cortada com Justificativa** | Complexidade desnecessária no MVP; unificou-se em tom acessível. |
| **Card #18**| Riscos éticos e jurídicos da verificação | **Mantida (Se Sobrar Tempo)** | Fundamenta a postura consultiva e institucional do assistente. |
| **Card #19**| Atualização automatizada da base | **Mantida e Implementada** | Rotinas de auto-indexação no startup e invalidação de cache. |
| **Card #20**| Governança federativa multi-hospitalar | **Cortada com Justificativa** | Risco burocrático; foco estratégico mantido exclusivamente no DF. |
| **NOVA 1** | Salvaguarda Clínica Fail-Closed (<10ms) | **Adicionada pela Equipe** | Proteção contra automedicação e garantia de segurança do paciente. |
| **NOVA 2** | Desambiguação da Toponímia do DF | **Adicionada pela Equipe** | Resolução de regionalismos de Brasília (RAs, quadras e setores). |
| **NOVA 3** | Busca Híbrida BM25 + ChromaDB (RRF) | **Adicionada pela Equipe** | Superação da falha vetorial em termos exatos de remédios (LME/PCDT). |
| **NOVA 4** | Privacidade e Conformidade LGPD | **Adicionada pela Equipe** | Garantia de inferência local sem vazamento de dados de cidadãos. |
| **NOVA 5** | Arquitetura Omnichannel (WhatsApp) | **Adicionada pela Equipe** | Planejamento da evolução do motor para canais de mensageria. |
| **NOVA 6** | Agendamento Direto no SISREG | **Adicionada e Cortada** | Delimitação consciente: manter foco na orientação de acolhimento. |

---

## 4. Evidências Empíricas e Entrevistas de Campo

Como parte do processo investigativo da fase *Investigate* da metodologia CBL, a equipe realizou levantamentos e entrevistas com foco na experiência do usuário e na validação das dores da atenção primária:

* 📄 **Entrevista Acadêmica e Levantamento de Campo:** [`entrevista_academica_meusus.pdf`](entrevista_academica_meusus.pdf) — Síntese das percepções sobre o Meu SUS Digital, barreiras de literacia da população e a necessidade de canais conversacionais oficiais orientados a evidências.
