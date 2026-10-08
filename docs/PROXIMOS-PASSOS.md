# Próximos passos

Lista viva do que falta para concluir o projeto, em ordem de prioridade. **Atualizada ao fim de cada rodada de trabalho.** O histórico do que já foi feito está em [registro/](registro/).

**Última atualização:** 08/10/2026 (última avaliação: [avaliacoes/2026-10-08-1720.md](avaliacoes/2026-10-08-1720.md), 41% sem problemas; 56% ignorando lentidão nas categorias comparáveis), depois da análise de **todas as branches** e da integração das ideias delas ([doc 13](13-todas-as-branches.md)). Situação de cada requisito: [doc 14](14-rastreabilidade-requisitos.md). ([avaliacoes/2026-10-08-1512.md](avaliacoes/2026-10-08-1512.md)): 49% das perguntas sem problemas.

**Como medir o progresso:** rodar `python -m ml.eval.run_eval` (mesma `--seed 0`) e comparar a porcentagem "sem problemas" com a última avaliação, além do `pytest`.

---

## 👉 Passo 1 — Reduzir o bloqueio indevido do guardrail (próximo a fazer)

**Problema:** 29 de 72 perguntas não clínicas foram bloqueadas na avaliação, 27 delas pelo modelo de ML. Para qualquer texto diferente do treino, o modelo dá p ≈ 0,5, e o limiar 0,40 bloqueia.

**Plano:**

1. Acrescentar ao dataset do guardrail frases administrativas e **fora do tema** variadas (o modelo nunca viu "piada", "ENEM", "MEI"), aproveitando as categorias `admin_dificil`, `fora_do_tema` e `corpus` do banco de perguntas, sem copiar as mesmas frases usadas no teste.
2. Acrescentar a regra forte "qual remédio (eu) tomo" (caso da ouvidoria + febre).
3. Mudar o gate do treino para avaliar também em um **conjunto separado** (held-out) de perguntas reais, e não só na validação cruzada.
4. Retreinar e testar limiares maiores (0,5–0,7).
5. Conferir com `run_eval --seed 0`: meta de **0 clínicas liberadas** e **≤ 5% administrativas bloqueadas**.

## ✅ Passo 2 — Integrar o melhor da branch `develop_gui_sam` (concluído em 08/10/2026)

Corpus de unidades (1.948 blocos), carregador multiformato, busca híbrida (com ranking intercalado e peso por raridade), 256 tokens por bloco, citações com link, limpeza de dependências, 25 testes do Sam, correção da página do SAMU. Detalhes: [registro/2026-10-08-integracao-develop_gui_sam.md](registro/2026-10-08-integracao-develop_gui_sam.md).

**Pendências que ficaram desta integração** (itens A9–A12 de [10-problemas-conhecidos.md](10-problemas-conhecidos.md)):

1. Perguntar ao Sam a origem (URL/data) dos 14 CSVs de unidades e avisá-lo sobre a página errada do SAMU.
2. Reduzir o tamanho dos trechos enviados ao LLM (respostas ficaram ~4 s mais lentas).
3. Refinar quando a busca trata a pergunta como "específica" (casos insulina/CEAF e HPV).
4. Decidir como responder sobre medicamentos da REME (nome e local, sem concentração?).
5. Títulos de citação amigáveis para o cidadão.

## ✅ Passo 2b — Aproveitar as demais branches (concluído em 08/10/2026)

Emergência (RNF06), diretório de unidades por tipo + região, estados explícitos e `/health/dependencies` (da `develop_sam`); filtro de instruções, detecção de links e revisor de fidelidade na avaliação (da `develop_gui`); requisitos, escopo, personas e Carta de Serviços 2026 (da `docs`); 35 perguntas curadas + 10 de personas + 6 de emergência no banco. Detalhes: [registro/2026-10-08-analise-todas-as-branches.md](registro/2026-10-08-analise-todas-as-branches.md).

## Passo 2c — Requisitos ainda não atendidos (do doc 14)

1. **RF07 — pedir esclarecimento** em perguntas vagas ("Onde devo ir?", "Tem atendimento perto de mim?"): pergunta curta sem tipo de serviço nem região → responder com uma pergunta ("Qual serviço você procura e em qual região?"). Medir com `curado` C.
2. **RF06 — resposta parcial**: instrução no prompt para responder só a parte sustentada e dizer o que faltou; medir com `--grounding`.
3. **RF11 — "ver mais"**: mostrar o trecho citado na tela (o backend já envia o `id` do bloco).
4. **RNF04 — data e prioridade das fontes**: registrar a data de verificação de cada fonte e exibir/considerar.
5. **RNF11 — disponibilidade**: supervisão do processo (reinício automático) e monitoramento do `/health/dependencies`.

## Passo 3 — Investigar "não respondeu" e "fonte errada"

O passo 2 já resolveu parte destes casos. Para cada caso que restar da avaliação ("A UBS distribui preservativo?", "A UBS faz nebulização?"…), descobrir se a falha está na **busca** (o bloco certo não veio entre os 3) ou no **LLM** (veio, mas ele disse "não encontrei"). Ferramenta: `run_eval --question "…"` + inspeção das distâncias. Possíveis correções: mais siglas e sinônimos no glossário, blocos menores ou mais trechos (`TOP_K`).

**Novo (08/10):** o benchmark de embeddings deu hit rate 1,00 para `all-MiniLM-L6-v2` contra 0,67 do modelo atual, mas com só 6 perguntas. Ampliar `ml/retrieval/eval_set.jsonl` com as perguntas `corpus` do banco de avaliação (que têm URL esperada), trocar o critério de "tag" para "URL da página" e repetir antes de decidir trocar o modelo.

## Passo 4 — Melhorar a divisão do corpus em blocos (A1)

Dividir as páginas pelos subtítulos (`h2`/`h3`) e colocar o subtítulo no cabeçalho do bloco. Isso resolve o "SAMU 192 (parte 5)" que na verdade lista telefones da Atenção Domiciliar. Depois: recalibrar o limiar e regenerar o banco de perguntas.

## Passo 5 — Fidelidade das respostas do LLM (A2)

**Novo:** o LLM copia "clique aqui" e URLs dos próprios trechos oficiais (6 casos de `LINK_GERADO`). Limpar essas expressões do texto dos blocos antes de enviá-los ao LLM, e rodar `run_eval --grounding` para medir a fidelidade.


- Reforçar o prompt: copiar números e nomes exatamente como estão nos trechos; não acrescentar serviços.
- Rodar o benchmark de LLMs (`ml/llm/benchmark_llms.py`) com o `qwen2.5:7b`, que já está baixado, e comparar no `run_eval`.
- Avaliar uma checagem automática de fidelidade no próprio pipeline.

## Passo 6 — Frontend (P7, P11, P19)

Tratar `res.ok`, buffer de linhas NDJSON partidas, desabilitar "Enviar" durante a resposta, rolagem automática, fonte como link clicável, URL do backend por variável de ambiente e paleta única.

## Passo 7 — Desempenho (prioridade aumentada)

Na última avaliação a mediana subiu para 15,0 s e o p90 para 28,9 s, por causa de prompts maiores (listas do diretório, trechos da Carta). Medir o tamanho do prompt por pergunta; limitar a lista do diretório (ex.: 8 unidades + "e mais N"); cortar trechos longos; medir o tempo até o 1º token; avaliar `qwen2.5:3b`/`llama3.2:3b` para respostas curtas.

5 de 87 respostas passaram de 15 s. Medir o tempo até o primeiro token, testar modelos menores e avaliar respostas mais curtas (`LLM_NUM_PREDICT`).

## Passo 8 — Preparação para produção

CORS restrito (P10), cache persistente (Redis, A5), CI rodando `pytest` + `run_eval` reduzido, atualizar RELEASE_NOTES e PDF de arquitetura para refletir o estado real (P16). Usar os **gates de produto** do `production-readiness-plan.md` do Sam (trazido no passo 2) como critério de "projeto concluído".

## Passo 9 — Integrar a trilha de dados (opcional)

A branch do Sam já tem um leitor que consolida os CSVs mensais do SIA por mês (veja o doc 12). Decidir em equipe se os dados processados (SAMU, óbitos, SIA) devem alimentar o chat (ex.: "quantos atendimentos o SAMU fez na Região Oeste?") e, se sim, corrigir o parquet (P17) e criar blocos ou uma ferramenta de consulta.

---

## Concluídos

| Data | O que | Registro |
| --- | --- | --- |
| 08/10/2026 | Ambiente rodando, versões atualizadas, documentação inicial | [setup-e-documentacao-inicial](registro/2026-10-08-setup-e-documentacao-inicial.md) |
| 08/10/2026 | Guardrail híbrido, corpus só oficial (52 blocos), limiar calibrado, rotas unificadas, siglas, LGPD | [correcoes-guardrail-corpus-limiar-rotas](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md) |
| 08/10/2026 | Gerador de perguntas + avaliador + 1ª avaliação (49% sem problemas) | [gerador-de-perguntas](registro/2026-10-08-gerador-de-perguntas.md) |
| 08/10/2026 | Demonstração: MLflow em localhost:5001, 1º benchmark de embeddings, `rodar_testes.command` | [demonstracao-mlflow-e-testes](registro/2026-10-08-demonstracao-mlflow-e-testes.md) |
| 08/10/2026 | Análise e comparação da branch `develop_gui_sam` | [analise-branch-develop_gui_sam](registro/2026-10-08-analise-branch-develop_gui_sam.md) |
| 08/10/2026 | Integração da `develop_gui_sam` na `develop_gui2` | [integracao-develop_gui_sam](registro/2026-10-08-integracao-develop_gui_sam.md) |
| 08/10/2026 | Análise de todas as branches e integração das ideias | [analise-todas-as-branches](registro/2026-10-08-analise-todas-as-branches.md) |
