# Proposal: Modelos de ML e LLM Local (Susana)

## Por Que (Why)
O Governo do Distrito Federal exige **Soberania de Dados**. Dados da saúde não podem ser enviados para provedores de LLM na nuvem (como OpenAI ou Google Gemini) devido aos riscos de vazamento, aderência à LGPD (dados sensíveis) e dependência de fornecedores externos com custos flutuantes (lock-in). 
Além disso, as respostas do sistema precisam ter fortes proteções clínicas: a IA não pode atuar como médica (risco de exercício ilegal da medicina). Regras baseadas apenas em Regex são fáceis de burlar, exigindo um classificador de ML para atuar como guardrail semântico.

## O Que (What)
Implementaremos um pipeline RAG totalmente on-premise com:
1. **LLM Local (Llama 3.1 8B):** Rodando via Ollama no servidor local.
2. **Embeddings Locais:** Usando a biblioteca `sentence-transformers` com o modelo `all-MiniLM-L6-v2` (ou outro otimizado) e persistência via ChromaDB.
3. **ML Guardrails (scikit-learn):** Um classificador ML leve, treinado com um pipeline DVC (Data Version Control) e registrado no MLflow, rodando no backend para bloquear intents de cunho clínico.
4. **Design Hexagonal:** O sistema será desacoplado por contratos (Ports & Adapters) para que a troca de LLM, Retriever ou Embedder seja trivial e altamente testável via mocks.

## Impacto / Riscos
- **Risco de Performance:** A geração local (LLM) tem latência maior (esperado: < 1.5s após warm-up). A mitigação será feita via Streaming e caches semânticos.
- **Risco de Erro Médico (Alucinação):** Se o Guardrail falhar e o LLM gerar prescrições. Mitigação: Design "fail-closed" onde falhas no Guardrail ativam o bloqueio, e a configuração foca em uso puramente administrativo (coleta do corpus SES-DF e MS).
- **Risco de Infraestrutura:** Requer aceleração Apple Silicon/Metal, vRAM suficiente, ou CUDA. Configurações de timeout agressivas para prevenir travamentos (fallback para resposta extrativa direta se o LLM falhar).
