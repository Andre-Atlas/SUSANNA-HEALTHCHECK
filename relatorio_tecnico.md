# Relatório Técnico: Arquitetura e Implementação da Assistente Susana RAG

## 1. Introdução e Objetivo Estratégico
O presente relatório descreve as decisões arquiteturais, o processo de preparação de dados e os critérios técnicos que embasaram o desenvolvimento da **Susana**, uma assistente virtual administrativa focada nos serviços do SUS-DF. 

O maior desafio técnico do projeto foi garantir uma separação rígida entre **informação administrativa** (horários, unidades, documentos, programas) e **informação clínica** (diagnósticos, dosagens, conselhos médicos), exigindo a construção de um pipeline que aliasse flexibilidade conversacional com segurança de dados e proveniência estrita (aterramento).

---

## 2. Processo de Preparação de Dados e Indexação (RAG)

### 2.1 Fontes de Dados (Corpus)
A estratégia adotada para o RAG (Retrieval-Augmented Generation) priorizou dados abertos oficiais e guias estruturados. A base incluiu:
* Arquivos `.csv` abertos contendo o registro de Unidades Básicas de Saúde (UBS), Unidades de Pronto Atendimento (UPAs) e metadados de produção.
* Transformação de páginas web oficiais (URLs do Ministério da Saúde e SES-DF) em arquivos `.json` estruturados.
* Documentos textuais de perguntas frequentes (FAQs), como os direcionados ao Meu SUS Digital e Campanhas de Vacinação.

### 2.2 Curadoria e Limpeza
Para maximizar a precisão vetorial (Evitar *Retrieve* de informações mórbidas irrelevantes ao atendimento primário), foi realizado um corte manual de escopo. Documentos como bases de óbitos foram purgados do Corpus para evitar contaminação semântica durante as interações diárias.

### 2.3 Indexação e Vetorização
Os dados brutos passam por uma rotina automatizada (`index_corpus.py`) de *chunking* (segmentação de textos) antes de serem inseridos no banco vetorial.
* **Banco de Dados Vetorial:** Utilizamos o **ChromaDB** pela capacidade de rodar localmente e em memória/persistência simples, garantindo isolamento da aplicação.
* **Modelo de Embeddings:** Optou-se pelo modelo `paraphrase-multilingual-MiniLM-L12-v2`. Esse modelo foi selecionado por possuir uma latência de processamento curtíssima com altíssima performance para língua portuguesa, mapeando semântica de 512 tokens por bloco.

---

## 3. Seleção de Modelos e Processamento Inteligente

### 3.1 O Roteador de Intenções (Intent Router)
Antes de realizar qualquer busca, o sistema processa a intenção do cidadão usando um **Roteador Léxico (Heurísticas)**. Em vez de usar a lentidão de um Large Language Model (LLM) para descobrir o que o usuário quer, o sistema resolve jargões e mensagens vagas em ~0.001 milissegundos usando Regex e Processamento de Linguagem Natural clássico.
Ele divide as chamadas em quatro caminhos rápidos:
1. *Mensagens curtas (ex: "tudo bem?")* → Bloqueadas sem gastar tokenização pesada.
2. *Intenções Vagas (ex: "o que é o programa do SUS?")* → Exige clarificação.
3. *Perguntas Relativas (ex: "me explique melhor")* → Aciona memória para mesclar contexto anterior.
4. *Dúvidas Específicas* → Aciona o Banco Vetorial.

### 3.2 O Classificador Clínico (ML Guardrails)
O SUS exige tolerância zero com prescrições feitas por Inteligência Artificial. Para esse controle rigoroso:
* **Algoritmo:** Foi treinado um classificador **Regressão Logística** associado a um vetorizador **TF-IDF**, consumindo um dataset predefinido de frases tabuladas. 
* **Por que não um LLM para Guardrail?** Modelos baseados em Árvores ou Regressão oferecem tempo de resposta na casa dos microssegundos e probabilidades matemáticas estritas, ao passo que modelos generativos (LLMs) possuem alto custo computacional de validação e viés de "alucinação do bem".
* **MLOps:** O modelo é traçado via **MLflow**, promovido com o alias de `@champion`, garantindo governança técnica do guardrail com taxa de precisão comprovada.

### 3.3 A Geração Fundamentada (Local LLM)
A interpretação dos dados recuperados é feita usando uma arquitetura LLM local:
* **Modelo Base:** Foi utilizado o motor **Ollama** rodando o modelo `Llama 3.1 (8B)`.
* **Critério de Adoção:** O modelo foi escolhido para assegurar a **Privacidade Total de Dados** (zero cloud APIs), rodando de forma soberana *on-premise*, ao mesmo tempo em que a linha "3" da Meta provou imenso refinamento lógico para o idioma Português.
* **Prompting e Aterramento:** O sistema opera em "regime misto", também conhecido como *Opção B*. O Llama foi rigidamente instruído (System Prompt) a gerar citações diretas de proveniência (`[1]`, `[2]`) quando informar dados críticos como fluxos, horários e endereços, bloqueando invenções. Simultaneamente, o LLM possui permissão estratégica para usar o "conhecimento do mundo" unicamente para explicar conceitos estáticos, caso as fontes não o tragam (ex: Explicar o acrônimo do SUS).

---

## 4. Conclusão
A arquitetura da Susana transcende o simples conceito de "chatbot de IA", consolidando-se como um pipeline RAG defensivo. Com um balanceamento perfeito entre Modelos de Linguagem para inferência humana, Regressão Logística para bloqueio de responsabilidade civil e Busca Semântica (`MiniLM`) para recuperação de informações do SUS, alcançamos uma arquitetura escalável, econômica e responsiva.
