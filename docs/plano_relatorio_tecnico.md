# Plano de Criação: Relatório Técnico - Susana RAG

## Objetivo do Documento
Descrever tecnicamente o pipeline de desenvolvimento da Susana, focando na preparação de dados (Corpus), treinamento/implementação do classificador de segurança (Guardrails) e a arquitetura RAG (LLM + Vetores), justificando as escolhas de tecnologia.

## Estrutura Proposta para o Relatório

### 1. Introdução
* Visão geral da Susana (Assistente Administrativa do SUS-DF).
* O desafio: Fornecer informações corretas sem alucinação clínica.

### 2. Processo de Preparação de Dados (Ingestão e Indexação)
* **Coleta e Limpeza:** Como os dados brutos (CSV, JSON, Manuais) foram filtrados (ex: remoção de dados de óbitos para focar em atendimento).
* **Chunking e Indexação:** Processo de particionamento dos textos e geração de embeddings.
* **Banco Vetorial:** O uso do ChromaDB como repositório persistente local para busca semântica veloz.

### 3. Abordagem de Inteligência Artificial (Modelos e Treinamento)
* **Modelo RAG Base (LLM):** Uso de LLM local via Ollama.
  * *Critério de Seleção:* Manter os dados sensíveis localmente (Data Privacy), controle de custo e capacidade de rodar offline/on-premise.
* **Classificador Clínico (ML Guardrails):**
  * O treinamento do modelo Scikit-Learn gerenciado via MLflow para detecção de intenções clínicas.
  * *Critério de Seleção:* Latência reduzida (Machine Learning clássico vs LLM) e precisão estatística para moderação.
* **Intent Router Híbrido:** Uso de NLP e Heurísticas (Regex) para rotear perguntas vagas, contextuais e de localização em ~0.001s sem bater no LLM.

### 4. Arquitetura de Prompting e Grounding (Aterramento)
* Como garantimos que a Susana não inventa fatos (Opção B - restrição mista).
* Injeção dinâmica de contexto (memória conversacional reativa).
* Validação de Proveniência (mapeamento dinâmico de citações exatas).

### 5. Conclusão
* Resumo da robustez da arquitetura alcançada e próximos passos.

---

## Perguntas de Alinhamento (Para preenchermos os detalhes)
Antes de eu redigir o relatório completo, preciso confirmar alguns pontos para não escrevermos inverdades:

1. **Qual foi o modelo exato de Embedding usado no projeto?** (Ex: `paraphrase-multilingual-MiniLM-L12-v2`?)
2. **Qual é o LLM principal que está configurado no Ollama?** (Llama 3 8B, Qwen, etc?)
3. **Para o treinamento do MLflow (Guardrails), qual algoritmo de classificação clássica foi usado?** (Foi Regressão Logística, Random Forest, SVM?)
4. **Houve algum processo de Data Augmentation ou balanceamento** nos dados que treinaram o classificador de guardrails?
5. **Você quer que eu inclua trechos de código como exemplo no relatório final ou apenas a explicação descritiva/arquitetural?**
