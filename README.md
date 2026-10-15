# Projeto SUSANA — Assistente Virtual Oficial da SES-DF

> **Sistema Único de Saúde com Atendimento e Navegação Aumentada (SES-DF)**  
> **Programa:** Residência em Inteligência Artificial — Instituto Eldorado  
> **Metodologia:** Challenge-Based Learning (CBL) — Challenge 1: Fake News / Desinformação  
> **Branch Oficial de Entrega:** `entrega-final`  

---

## 📖 Visão Geral do Projeto

O **SUSANA** é um assistente virtual conversacional concebido para orientar os cidadãos do Distrito Federal na navegação pelos serviços públicos de saúde da **Secretaria de Saúde do Distrito Federal (SES-DF)** e do **Meu SUS Digital**.

O projeto responde diretamente à *Essential Question* do Challenge 1:
> *"Como sistemas de IA podem ajudar as pessoas a avaliar a confiabilidade de informações sem substituir seu pensamento crítico?"*

A solução adota a IA como ferramenta de apoio à tomada de decisão cidadã, ancorando 100% das respostas fatuais em um **Corpus Oficial Controlado** e implementando **Guardrails de Segurança Clínica** com tempo de bloqueio determinístico em milissegundos ($< 10\text{ ms}$) contra tentativas de automedicação ou prescrições não autorizadas.

---

## 🗂️ Estrutura Arquitetural do Portfólio

Cada diretório do repositório foi organizado para refletir com rigor técnico e rastreabilidade os entregáveis formais da Residência:

```text
.
├── datasets/             # Catálogo de fontes oficiais, corpus RAG (2.283 blocos), tabelas raw e eval
├── requisitos/           # Especificação formal (15 RFs, 12 RNFs) e Matriz de Rastreabilidade CBL
├── eda/                  # 3 Notebooks de Análise Exploratória (Cartilha, Vacinas APS e SUS Digital)
├── guiding-questions/    # Perguntas norteadoras do Trello, questões complementares e entrevista
├── scrum-organizacao/    # Metodologia ágil (Scrum/Kanban), papéis da equipe, matriz RACI e DoR/DoD
├── modelo-ia-relatorio/  # Relatório Técnico de IA (RAG Híbrido, MLflow, Guardrails e Benchmark)
├── produto/              # Visão de produto, personas, proposta de valor e limites éticos
└── codigo/               # Arquitetura dos módulos da aplicação (Backend FastAPI + Frontend Next.js)
```

---

## 🧭 Mapa de Navegação dos Módulos

| Módulo | Documento Principal | Descrição Sintética |
| :--- | :--- | :--- |
| **📁 [datasets/](datasets/)** | [`catalogo_do_corpus.md`](datasets/catalogo_do_corpus.md) | Inventário das 9 fontes oficiais, 2.283 blocos indexados, dicionário de tags e LGPD. |
| **📋 [requisitos/](requisitos/)** | [`requisitos_susana.md`](requisitos/requisitos_susana.md) | 27 requisitos funcionais/não funcionais e vínculo direto com os critérios do CBL. |
| **📊 [eda/](eda/)** | [`README.md`](eda/README.md) | Análises estruturais e epidemiológicas dos serviços da SES-DF e séries de vacinas. |
| **❓ [guiding-questions/](guiding-questions/)** | [`guiding_questions_susana.md`](guiding-questions/guiding_questions_susana.md) | 20 cartas do Trello, 6 complementares de engenharia e entrevista de validação. |
| **🔄 [scrum-organizacao/](scrum-organizacao/)** | [`metodologia_e_sprints.md`](scrum-organizacao/metodologia_e_sprints.md) | Dinâmica das 4 sprints, papéis multidisciplinares, matriz RACI e rituais. |
| **🧠 [modelo-ia-relatorio/](modelo-ia-relatorio/)** | [`relatorio_tecnico_ia.md`](modelo-ia-relatorio/relatorio_tecnico_ia.md) | RAG Híbrido (ChromaDB + BM25 Okapi com RRF), Guardrails no MLflow e 18 testes. |
| **🎯 [produto/](produto/)** | [`visao_do_produto.md`](produto/visao_do_produto.md) | Personas (Camila, Seu Raimundo, Felipe), proposta de valor e fronteiras do produto. |
| **📦 [codigo/](codigo/)** | [`README.md`](codigo/README.md) | Especificação técnica dos componentes de software (FastAPI e Next.js 16). |

---

## 👥 Equipe Multidisciplinar

* **André Alves Acioli:** Engenharia de IA & MLOps
* **Samuel de Souza Rodrigues:** Engenharia de Software Fullstack
* **Ingrid Hanna Nóbrega:** Product Owner & Validação Clínica
* **Guilherme Barros Jr.:** Ciência de Dados & Scrum Master

---

## 🔗 Links e Recursos Oficiais

* **Repositório GitHub:** [https://github.com/Andre-Atlas/SUSANNA-HEALTHCHECK](https://github.com/Andre-Atlas/SUSANNA-HEALTHCHECK)
* **Secretaria de Saúde do DF (SES-DF):** [https://www.saude.df.gov.br](https://www.saude.df.gov.br)
* **Meu SUS Digital (Ministério da Saúde):** [https://www.gov.br/saude/pt-br/composicao/seidigi/meu-sus-digital](https://www.gov.br/saude/pt-br/composicao/seidigi/meu-sus-digital)
