# Modelo de IA, Arquitetura e Relatório Técnico — SUSANA

Este diretório concentra a documentação profunda da arquitetura de Inteligência Artificial, modelagem de RAG Híbrido, governança de MLOps com MLflow, engenharia de Guardrails de segurança clínica e os resultados do benchmark de homologação da assistente **SUSANA**.

---

## 📄 Documentação Técnica Oficial
* 📑 **[`relatorio_tecnico_ia.md`](relatorio_tecnico_ia.md)**: Relatório Técnico integral da solução, cobrindo o pipeline ponta a ponta, formulação matemática do RRF, validação cruzada estratificada do classificador clínico, aterramento do LLM e a bateria de testes automatizados com 100% de aprovação.

---

## 🖼️ Diagramas e Evidências Visuais
* 📊 **[`assets/diagrama_sequencia_susana.png`](assets/diagrama_sequencia_susana.png)**: Diagrama de sequência completo do fluxo síncrono e assíncrono (Frontend Next.js, Guardrail Clínico, Cache Semântico, Busca Híbrida ChromaDB/BM25 e streaming de tokens com Ollama Llama 3.1).
* 📈 **[`assets/painel_metricas_benchmark.jpg`](assets/painel_metricas_benchmark.jpg)**: Painel executivo de resultados e métricas de produção (100% de precisão nos testes de regressão, zero prescrições indevidas com bloqueio < 10ms e 2.280+ blocos oficiais indexados).

---

## 🧠 Resumo dos Pilares Tecnológicos

| Componente | Tecnologia Selecionada | Papel no SUSANA |
| :--- | :--- | :--- |
| **LLM Local** | `Llama 3.1 8B Instruct` via Ollama | Geração fundamentada e fluida em português, com privacidade total (LGPD). |
| **Embeddings Densos** | `paraphrase-multilingual-MiniLM-L12-v2` | Representação semântica de 384 dimensões otimizada para consultas em saúde. |
| **Banco Vetorial** | `ChromaDB` (Persistência Local) | Armazenamento e busca por similaridade de cosseno em 2.283 blocos oficiais. |
| **Busca Léxica Exata** | `BM25 Okapi` ($k_1=1.5, b=0.75$) | Recuperação determinística de princípios ativos (fármacos) e siglas do SUS. |
| **Fusão de Rankings** | `RRF (Reciprocal Rank Fusion)` ($k=60$) | Combinação ponderada de escores densos e esparsos para máxima relevância. |
| **Guardrails de Segurança** | `Scikit-Learn` + `Regex Semântico` | Interceptação em $< 10\text{ ms}$ de qualquer tentativa de diagnóstico ou automedicação. |
| **MLOps & Governança** | `MLflow` (Tracking & Model Registry) | Rastreamento de experimentos, curvas ROC e promoção do modelo campeão (`@champion`). |
