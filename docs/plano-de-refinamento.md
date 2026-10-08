# Plano de Refinamento: Pós-Benchmark

A análise diagnóstica revelou que o pipeline atual está operacional e seguro, mas necessita de refinamentos em 3 pilares fundamentais: **Recuperação (Retrieval)**, **Aterramento (Grounding)** e **Contexto Conversacional**. 

Este plano detalha as próximas implementações para elevar a qualidade da Susana.

## 1. Melhorias no Prompt e Grounding (Resolução de Conflitos)
**Problema:** A LLM concatenou endereços conflitantes do HRT recuperados de documentos diferentes.
**Ação:**
- Atualizar o prompt do sistema no `OllamaAdapter` para incluir a regra de resolução de conflitos:
  > *"Se as fontes apresentarem informações conflitantes (ex: endereços diferentes para a mesma unidade), não tente adivinhar. Informe a inconsistência ao usuário e cite as duas fontes."*
- Avaliar a limpeza dos dados (ex: remover CSVs antigos se o endereço oficial atual estiver em um JSON mais novo).

## 2. Refinamento de Retrieval (Intenção vs Semântica)
**Problema:** "Onde posso tomar vacina?" retornou o Calendário de Vacinação, não as UBS.
**Ação:**
- Implementar **Híbrido de Busca** (Semantic + Keyword) ou Metadados.
- Criar filtros por intenção. Exemplo simples: Se a pergunta contém "onde", "qual", "perto", injetar um boost em documentos da categoria `UNIDADE_DE_SAUDE` (Hospitais, UPAs, UBS).

## 3. Comportamento Conversacional (Falta de Contexto)
**Problema:** "Qual UPA mais perto de mim?" gera um erro genérico de falta de informação.
**Ação:**
- Melhorar a mensagem de fallback. Em vez de um estático `NO_RESULT_MESSAGE`, a pipeline deve classificar o motivo da falha.
- Se a pergunta envolver distâncias ou localização ("perto de mim", "onde moro"), a IA deve responder: *"Posso ajudar a encontrar uma unidade, mas não tenho acesso à sua localização automática. Por favor, me diga em qual Região Administrativa (ex: Taguatinga, Samambaia) você está."*

## 4. Rigor no Escopo Institucional vs Clínico Geral
**Problema:** A Susana explicou como o HIV é transmitido, o que é uma informação geral de saúde, não uma informação institucional do SUS-DF.
**Ação:**
- Decisão de Produto (Opção B adotada): A Susana deve focar estritamente em **serviços, acesso e administração do SUS-DF**.
- Atualizar o modelo de Guardrails (`GuardrailsClassifier`) para bloquear perguntas puramente enciclopédicas ou gerais de saúde que não estejam atreladas a um serviço prestado.

## 5. Expansão e Estruturação do Benchmark
**Problema:** 10 perguntas é apenas um *Smoke Test*.
**Ação:**
- Expandir `benchmark.py` para 40 perguntas separadas por categoria:
  1. Respondíveis (Fatos diretos e locais)
  2. Territoriais (Exigem RA/Endereço)
  3. Ambíguas
  4. Fora do Escopo Institucional (Enfermidades gerais)
  5. Clínicas / Perigosas
- Adicionar métricas explícitas de `Hit@5` (Retrieval) e `Groundedness` (Geração).

---
**Próximo Passo Imediato sugerido:** Começar pela etapa 1 (Prompt de Conflitos) e etapa 3 (Mensagens de Fallback Dinâmicas), pois são ajustes rápidos (Low Hanging Fruits) que melhoram a experiência instantaneamente sem exigir reindexação.
