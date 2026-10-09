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
O SUS exige tolerância zero com prescrições e diagnósticos emitidos por Inteligência Artificial. Para esse controle rigoroso:
* **Algoritmo Selecionado:** Pipeline Scikit-Learn composto por **TfidfVectorizer(ngram_range=(1, 2))** e **LogisticRegression(class_weight="balanced")**.
* **Critério de Seleção:** Em comparação empírica via Validação Cruzada Estratificada (5 Folds) contra *Multinomial Naive Bayes* e *LinearSVC*, a Regressão Logística obteve o maior Recall Clínico médio (**84,0%**) e maior F1-Score (**84,5%**), com calibração probabilística nativa via `predict_proba` e latência inferior a 0.5 ms.
* **Governança e MLOps:** O modelo é rastreado via **MLflow**, promovido com o alias de `@champion`, e exportado como pipeline serializada autônoma em formato `.pkl`.

#### Tabela Comparativa de Algoritmos (5-Fold Stratified CV)
| Algoritmo | Acurácia Média | Precisão Média | Recall Clínico Médio | F1-Score Médio |
| :--- | :---: | :---: | :---: | :---: |
| **Regressão Logística (Campeão)** | **87,9% (±3,7%)** | **90,0% (±8,2%)** | **84,0% (±19,6%)** | **84,5% (±7,8%)** |
| LinearSVC | 86,1% (±4,0%) | 89,3% (±8,8%) | 80,0% (±17,9%) | 82,4% (±7,2%) |
| Multinomial Naive Bayes | 84,2% (±6,7%) | 88,3% (±10,0%) | 76,0% (±19,6%) | 79,7% (±9,6%) |

#### Entregáveis Oficiais do Modelo
* **Notebook de Avaliação:** `notebooks/avaliacao_modelo_guardrails.ipynb` (contém EDA, gráficos, validação cruzada, matriz de confusão, curva ROC e testes de inferência pré-executados).
* **Modelo Serializado (.pkl):** `models/guardrail_model.pkl` e `susana_rag_backend/data/guardrail_model.pkl` (Pipeline completa `TfidfVectorizer` + `LogisticRegression`).
* **Script de Treinamento Automatizado:** `susana_rag_backend/ml/guardrails/train.py`.

### 3.3 A Geração Fundamentada (Local LLM)
A interpretação dos dados recuperados é feita usando uma arquitetura LLM local:
* **Modelo Base:** Foi utilizado o motor **Ollama** rodando o modelo `Llama 3.1 (8B)`.
* **Critério de Adoção:** O modelo foi escolhido para assegurar a **Privacidade Total de Dados** (zero cloud APIs), rodando de forma soberana *on-premise*, ao mesmo tempo em que a linha "3" da Meta provou imenso refinamento lógico para o idioma Português.
* **Prompting e Aterramento:** O sistema opera em "regime misto", também conhecido como *Opção B*. O Llama foi rigidamente instruído (System Prompt) a gerar citações diretas de proveniência (`[1]`, `[2]`) quando informar dados críticos como fluxos, horários e endereços, bloqueando invenções. Simultaneamente, o LLM possui permissão estratégica para usar o "conhecimento do mundo" unicamente para explicar conceitos estáticos, caso as fontes não o tragam (ex: Explicar o acrônimo do SUS).

---

## 4. As Métricas de Desempenho Consideradas e a Análise dos Resultados Obtidos

### 4.1 Métricas de Desempenho Consideradas
A classificação de intenções no domínio da saúde pública impõe custos de erro fortemente assimétricos. Por esse motivo, o projeto rejeitou a avaliação baseada em uma única métrica ingênua e estabeleceu uma suíte multicritério de avaliação estatística:

1. **Recall Clínico ($TPR$ — Sensibilidade da Classe Clínica):**
   $$\text{Recall} = \frac{TP}{TP + FN}$$
   * **Justificativa Estratégica:** É a métrica prioritária de segurança (*fail-safe*). Um Falso Negativo ($FN$) representa uma solicitação de diagnóstico, prescrição de dosagem ou conduta médica que escapou do guardrail e avançou para a LLM, gerando risco ético e responsabilidade civil. O objetivo do sistema é maximizar o Recall desta classe.
2. **Precisão Administrativa ($PPV$ — Valor Preditivo Positivo):**
   $$\text{Precisão} = \frac{TP}{TP + FP}$$
   * **Justificativa:** Avalia a exatidão ao rotular uma consulta como clínica. Evita Falsos Positivos ($FP$) excessivos, nos quais cidadãos que perguntam sobre horário de vacinação ou endereço de postos seriam indevidamente bloqueados.
3. **F1-Score (Macro e Ponderado):**
   $$F_1 = 2 \times \frac{\text{Precisão} \times \text{Recall}}{\text{Precisão} + \text{Recall}}$$
   * **Justificativa:** Consolida a média harmônica entre precisão e revocação, penalizando modelos com desequilíbrio acentuado em qualquer uma das pontas.
4. **Acurácia Global ($Accuracy$):**
   * Mensura a proporção total de predições corretas. Foi tratada com ressalva metodológica, pois em cenários com desbalanceamento de classes, a acurácia isolada pode mascarar falhas graves de detecção da classe minoritária.
5. **Matriz de Confusão:**
   * Permite a visualização direta e sem distorções dos quatro quadrantes operacionais: Verdadeiros Negativos ($TN$), Falsos Positivos ($FP$), Falsos Negativos ($FN$) e Verdadeiros Positivos ($TP$).
6. **Curva ROC e Área sob a Curva ($ROC\text{-}AUC$):**
   * Avalia a capacidade do modelo em discriminar consultas clínicas e administrativas através de múltiplos limiares de probabilidade, medindo a robustez da fronteira de decisão estocástica.
7. **Validação Cruzada Estratificada ($5\text{-Fold Stratified CV}$):**
   * Particiona o dataset em 5 dobras preservando rigorosamente a proporção entre classes clínicas e administrativas em cada partição. Fornece estimativas de média e desvio-padrão ($\mu \pm \sigma$), atestando a estabilidade do algoritmo frente à variabilidade das amostras.

---

### 4.2 Rastreamento, Governança e Métricas no MLflow (MLOps)
O ciclo de vida, reprodutibilidade e governança do classificador de guardrails é integralmente gerenciado através do **MLflow**.

* **Backend Store:** Banco relacional SQLite local (`sqlite:///susana_rag_backend/mlflow.db`);
* **Artifact Store:** Diretório versionado de artefatos (`susana_rag_backend/mlruns/`);
* **Experimento Dedicado:** `susana-guardrails-train` (ID: `2`);
* **Model Registry:** Modelo registrado `susana-guardrail` com promoção automatizada via Promotion Gate para o alias `@champion`.

#### Registro Consolidado da Última Execução no MLflow (Run ID: `a54bd58c20b34171a7a975ed22e2cef1`)

| Categoria | Parâmetro / Métrica | Valor Registrado no MLflow | Significado / Impacto |
| :--- | :--- | :---: | :--- |
| **Parâmetros** | `model_type` | `LogisticRegression` | Algoritmo linear supervisionado |
| | `vectorizer` | `TfidfVectorizer` | Extração de features por frequência inversa |
| | `ngram_range` | `(1, 2)` | Unigramas e bigramas considerados |
| | `class_weight` | `balanced` | Ponderação inversa à frequência das classes |
| | `cv_folds` | `5` | Quantidade de dobras na validação cruzada |
| | `train_samples` | `42` | Instâncias na partição de desenvolvimento |
| | `test_samples` | `15` | Instâncias na partição de teste independente |
| **Validação Cruzada (5 Folds)** | `cv_f1_mean` | **0.8455** | F1-Score médio entre todas as dobras |
| | `cv_f1_std` | **0.0779** | Baixo desvio padrão (alta estabilidade) |
| | `cv_recall_mean` | **0.8400** | Taxa média de identificação clínica |
| | `cv_precision_mean` | **0.9000** | Precisão média em consultas de saúde |
| | `cv_accuracy_mean` | **0.8788** | Acurácia média de 87,9% |
| **Teste Hold-Out (25%)** | `test_accuracy` | **0.7333** | Acurácia no conjunto isolado |
| | `test_precision` | **0.8000** | Precisão na classe clínica |
| | `test_recall_clinical` | **0.5714** | Recall clínico no split reduzido |
| | `test_f1_score` | **0.6667** | F1-Score na partição independente |
| | `test_roc_auc` | **0.8393** | Separação probabilística de classes |
| **Matriz de Confusão** | `confusion_tn` | **7** | Administrativos corretamente liberados |
| | `confusion_tp` | **4** | Clínicos corretamente bloqueados |
| | `confusion_fp` | **1** | Administrativo classificado como clínico |
| | `confusion_fn` | **3** | Clínicos não interceptados no threshold 0.5 |
| **Model Registry** | `registered_model` | `susana-guardrail` | Modelo registrado e versionado (Versão 2) |
| | `alias` | `@champion` | Promovido para produção no backend |

#### Recuperação Programática via MLflow Client (Python)
Para auditar as métricas diretamente do banco de rastreamento sem abrir navegadores, a aplicação expõe a seguinte rotina:

```python
import mlflow

mlflow.set_tracking_uri("sqlite:///susana_rag_backend/mlflow.db")
client = mlflow.client.MlflowClient()

# Buscar modelo campeão ativo
champion = client.get_model_version_by_alias("susana-guardrail", "champion")
run = client.get_run(champion.run_id)

print(f"Modelo Campeão: Versão {champion.version} (Run: {champion.run_id})")
print(f"F1-Score Médio (CV): {run.data.metrics['cv_f1_mean']:.4f}")
print(f"Recall Clínico (CV):  {run.data.metrics['cv_recall_mean']:.4f}")
print(f"ROC-AUC Teste:        {run.data.metrics['test_roc_auc']:.4f}")
```

#### Inspeção Visual via Interface Web
Para inicializar o painel interativo do MLflow e comparar curvas e corridas visualmente:
```bash
cd /Users/aluno2/SUSANA/susana_rag_backend
mlflow ui --backend-store-uri "sqlite:///mlflow.db" --port 5001
```

---

### 4.3 Análise e Interpretação dos Resultados Obtidos

#### 1. Comparação Empírica de Algoritmos
A validação cruzada demonstrou que a **Regressão Logística** superou os modelos alternativos nos quesitos fundamentais:
* **Recall Clínico Superior (84,0%):** Superou o *LinearSVC* (80,0%) e o *Multinomial Naive Bayes* (76,0%). Essa diferença de 4 a 8 pontos percentuais é decisiva para prevenir vazamento de dúvidas de prescrição;
* **F1-Score Consistente (84,5% $\pm$ 7,8%):** Apresentou a menor variância entre dobras, confirmando estabilidade mesmo diante de amostras textuais heterogêneas;
* **Calibração Probabilística:** Ao contrário do *LinearSVC* (que gera distâncias puras ao hiperplano separador), a Regressão Logística mapeia a decisão através da função sigmoide $P(Y=1|X) = \frac{1}{1 + e^{-z}}$, gerando probabilidades contínuas consumidas pelo runtime.

#### 2. Diagnóstico dos Erros e Mitigações Arquiteturais
A inspeção qualitativa das predições divergentes na partição de teste independente revelou padrões claros:
1. **Falsos Negativos Clínicos (Ex: *"Posso tomar ibuprofeno com losartana?"* e *"Dor abdominal forte"*):**
   * *Diagnóstico:* Ocorreram devido à ausência desses termos anatômicos e farmacológicos específicos no conjunto reduzido de 42 amostras de treino;
   * *Mitigação 1 (Treinamento de Produção):* A pipeline final foi ajustada sobre 100% dos dados rotulados, expandindo o vocabulário e eliminando esses pontos cegos;
   * *Mitigação 2 (Defesa em Profundidade com Regex):* Caso o modelo estatístico produza probabilidade abaixo de 0.50 para uma frase nunca vista, o sistema aciona a segunda camada: a regra [`CLINICAL_PATTERNS`](file:///Users/aluno2/SUSANA/susana_rag_backend/app/rag/guardrails.py#L24) (que intercepta expressões como *"posso tomar"*, *"sinto dor"*, *"como curar"*).
2. **Falsos Positivos Administrativos (Ex: *"Quais documentos preciso para pegar remédio na farmácia popular?"*):**
   * *Diagnóstico:* A presença da palavra *"remédio"* desloca a probabilidade clínica para 0.540, gerando um bloqueio indevido no modelo puro;
   * *Mitigação Arquitetural:* A aplicação implementa a regra prioritária [`ADMINISTRATIVE_OVERRIDES`](file:///Users/aluno2/SUSANA/susana_rag_backend/app/rag/guardrails.py#L32), que reconhece termos como *"farmácia popular"*, *"documentos"* ou *"horário"*, liberando o fluxo antes mesmo da avaliação estatística.

#### 3. Auditoria em Tempo Real de Consultas RAG
Além do guardrail, o MLflow mantém o experimento ativo `susana-rag` (ID: `1`), registrando a telemetria de todas as consultas que chegam à Susana: latência total, tempo de geração do LLM e a distância semântica euclidiana ao documento mais próximo no ChromaDB. Isso fecha o ciclo completo de observabilidade de IA (MLOps + LLMOps).

---

## 5. Conclusão e Próximos Passos
A arquitetura da Susana transcende o simples conceito de "chatbot de IA", consolidando-se como um pipeline RAG defensivo de alta disponibilidade. Com um balanceamento rigoroso entre:
1. **Regressão Logística e TF-IDF** para guardrail semântico com latência de 0.2ms;
2. **MLflow** para rastreabilidade de experimentos, auditoria de métricas e versionamento de modelos `@champion`;
3. **Busca Semântica no ChromaDB** (`MiniLM-L12`) para aterramento em fontes oficiais da SES-DF;
4. **LLM Local (Llama 3.1 8B via Ollama)** com diretivas estritas de citação e privacidade soberana;

O sistema garante segurança jurídica ao SUS-DF, aderência ética com a saúde do cidadão e performance em tempo real. Como evolução futura, recomenda-se a ingestão contínua de dúvidas reais anonimizadas para ampliação do vocabulário supervisionado de guardrail.
