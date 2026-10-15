# 06 - Modelo de IA, Arquitetura e Relatório Técnico

Documentação técnica profunda da arquitetura do sistema inteligente da SUSANA.

## 🧠 Arquitetura Técnica
- **LLM Local:** `llama3.1:8b` executado via Ollama com prompts orientados a atendimento administrativo e restrição anti-alucinação.
- **Modelo de Embedding:** `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensões).
- **Mecanismo de Recuperação Híbrida:**
  - Recuperação Vetorial Densa via **ChromaDB**.
  - Recuperação Léxica Exata via **BM25 Okapi** ($k_1=1.5, b=0.75$).
  - Fusão de Ranks via **Reciprocal Rank Fusion (RRF)** com constante $k=60$.
- **Camada de Segurança (Guardrails):**
  - Classificação híbrida (Regex e Modelo Supervisionado no MLflow) para bloqueio clínico imediato (< 10ms).
  - Validador sintático de telefones para impedir números falsos não cadastrados nos canais oficiais (160, 136).
- **Métricas e Avaliação:** Suíte de benchmark com 18 cenários ponta a ponta e 100% de precisão registrada.
