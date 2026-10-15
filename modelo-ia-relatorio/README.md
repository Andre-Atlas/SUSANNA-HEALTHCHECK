# Modelo de IA, Arquitetura e Relatório Técnico — SUSANA

Este diretório concentra a documentação detalhada da arquitetura de Inteligência Artificial, modelagem do RAG Híbrido, governança de MLOps com MLflow, engenharia de Guardrails de segurança clínica e os resultados do benchmark de homologação da assistente **SUSANA**.

---

## 📄 Documentação Técnica Oficial
* 📑 **[`relatorio_tecnico_ia.md`](relatorio_tecnico_ia.md)**: Relatório Técnico integral da solução, cobrindo o pipeline ponta a ponta, diagrama de sequência nativo Mermaid, recuperação vetorial com regras lexicais, validação cruzada estratificada do classificador clínico, aterramento do LLM, o registro histórico da bateria de 18 cenários e a evolução final (perfil e agenda).

---

## 🧠 Resumo dos Pilares Tecnológicos

| Componente | Tecnologia Selecionada | Papel no SUSANA |
| :--- | :--- | :--- |
| **LLM Local** | `Llama 3.1 8B Instruct` via Ollama | Geração fundamentada e fluida em português, com privacidade total (LGPD). |
| **Embeddings Densos** | `paraphrase-multilingual-MiniLM-L12-v2` | Representação semântica de 384 dimensões otimizada para consultas em saúde. |
| **Banco Vetorial** | `ChromaDB` (Persistência Local) | Armazenamento e busca por similaridade de cosseno em 2.283 blocos oficiais. |
| **Casamento Lexical** | Regras no `ChromaRetriever` | Recuperação de entidades numeradas (ex.: UBS 02) e termos raros (siglas, princípios ativos) nos blocos candidatos. |
| **Reordenação** | Chave lexicográfica por regras | RA, entidade, termo de saúde no título, sobreposição de termos e distância vetorial. |
| **Guardrails de Segurança** | `Scikit-Learn` + `Regex Semântico` | Interceptação em $< 10\text{ ms}$ de qualquer tentativa de diagnóstico ou automedicação. |
| **MLOps & Governança** | `MLflow` (Tracking & Model Registry) | Rastreamento de experimentos, curvas ROC e promoção do modelo campeão (`@champion`). |
| **Aterramento** | *System prompt* + filtro de relevância | Resposta restrita aos trechos oficiais; sem evidência relevante, devolve a mensagem padrão de ausência de informação. |

---

## 📊 Indicadores de Homologação (Benchmark Oficial)

* **Bateria de 18 cenários (registro histórico, script não versionado):** 18/18 aprovados segundo a equipe
* **Tempo de Interceptação Clínica:** **< 10 milissegundos**
* **Prescrições ou Dosagens Indevidas Emitidas:** **Zero**
* **Suíte de Testes do Backend:** **151 testes passando** (`pytest tests/`)
