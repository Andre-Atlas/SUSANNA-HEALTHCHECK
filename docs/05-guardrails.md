# 5. Guardrails — o bloqueio de perguntas clínicas

**Arquivo:** [app/rag/guardrails.py](../susana_rag_backend/app/rag/guardrails.py)

> Atualizado em 08/10/2026. A lógica foi refeita: regras e modelo de ML agora **somam** proteção, e antes o ML substituía as regras.
> Passo a passo da mudança: [registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](registro/2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md).

## Por que existe

A Susana é **administrativa**. Ela não pode sugerir remédio, dose, diagnóstico ou tratamento. O guardrail roda **antes** de qualquer busca ou chamada ao LLM: uma pergunta bloqueada nunca chega ao modelo de linguagem.

Há duas camadas de proteção:

1. **Guardrail (este documento):** decide antes de gerar.
2. **Prompt de sistema** (regra 3 em [prompts.py](../susana_rag_backend/app/llm/prompts.py)): manda o LLM nunca dar orientação clínica. É a rede de segurança para o que passar pela camada 1.

## A decisão, em ordem

A função pura `decide(texto, p_clinica, limiar)` aplica as regras abaixo. A primeira que se aplica decide:

| # | Regra | Resultado | Exemplos |
| --- | --- | --- | --- |
| 1 | **Regra clínica FORTE** (pede conduta) | 🔴 bloqueia | "me prescreva", "que remédio devo tomar", "remédio que cura", "sem receita", "dose de", "quantas gotas", "diagnóstico", "o que eu tenho" |
| 2 | **Termo administrativo** | 🟢 libera | horário, endereço, telefone, agendar, marcar (um) exame, onde fica/posso, farmácia do SUS, cartão do SUS, campanha de vacinação |
| 3 | **Regra clínica FRACA** (relato) | 🔴 bloqueia | "estou com", "estou sentindo", "sinto dor", "meu filho está doente", "como tratar", "é grave" |
| 4 | **Modelo de ML**: p(clínica) ≥ 0,40 | 🔴 bloqueia | perguntas clínicas sem palavra-chave óbvia ("Essa dor de barriga pode ser apendicite?") |
| 5 | nenhuma das anteriores | 🟢 libera | — |

Por que essa ordem:

- **Regras fortes vêm antes do override.** Antes, "**Onde posso** comprar antibiótico sem receita?" era liberada só por conter "onde posso". Agora "sem receita" bloqueia primeiro.
- **Regras fracas vêm depois do override.** "Estou com dúvida sobre o **horário** da UBS" contém "estou com", mas é administrativa.
- **O ML é a última camada e só acrescenta bloqueios.** Ele pega o que as palavras-chave não cobrem, mas nunca libera algo que uma regra bloqueou. Se o modelo não carregar, as regras continuam funcionando sozinhas.

As regras fortes têm exceções para não bloquear perguntas administrativas legítimas:

| Frase | Por que não bloqueia |
| --- | --- |
| "Onde **posso tomar** a vacina?" | `(posso\|devo) tomar` ignora quando o que vem depois é "vacina" ou "dose" |
| "Segunda **dose da** vacina" | `dose de/da` ignora "vacina" e "reforço" |
| "O que **eu tenho** que levar?" | `o que eu tenho` ignora "que"/"de" em seguida |
| "Me **indique** a UBS mais próxima" | "me indique" só bloqueia seguido de remédio/medicamento/antibiótico/tratamento |

## O modelo de ML

- **Pipeline:** `TfidfVectorizer(analyzer="char_wb", ngram_range=(2,5))` → `LogisticRegression(class_weight="balanced", C=4)`.
  - *n-gramas de caracteres* toleram erros de digitação e variações ("remedio", "remédios", "receitar").
- **Carregado de:** `models:/susana-guardrail@champion` no MLflow (hoje a **versão 4**).
- **Limiar:** `GUARDRAIL_THRESHOLD` (padrão **0,40**), calibrado no treino.
- **Treinado por:** [ml/guardrails/train.py](../susana_rag_backend/ml/guardrails/train.py); detalhes em [08-mlops.md](08-mlops.md).

## Desempenho medido (decisão híbrida completa)

Validação cruzada estratificada de 5 partes, média de 3 repetições, sobre 111 frases:

| Métrica | Versão 1 (antes) | **Versão 4 (atual)** | Mínimo exigido |
| --- | --- | --- | --- |
| Perguntas clínicas bloqueadas (recall clínico) | 0,40 | **0,987** | 0,98 |
| Precisão administrativa | — | **0,986** | 0,95 |
| Perguntas administrativas liberadas | — | **0,828** | 0,80 |

Leitura: de cada 100 perguntas clínicas, cerca de 1 passa pelo guardrail (e ainda encontra o prompt). De cada 100 administrativas, cerca de 17 são bloqueadas sem necessidade. Num guardrail de segurança, errar para o lado do bloqueio é o erro menos grave, mas esse número deve cair com mais dados (veja [PROXIMOS-PASSOS.md](PROXIMOS-PASSOS.md)).

Erros remanescentes na validação:

- **Clínica que passou:** "Quanto tempo dura a dengue?"
- **Administrativas bloqueadas:** "Tem paracetamol no posto?", "Quais os sintomas do sarampo?", "Como evitar a dengue?", "Quanto tempo de espera para pulseira verde?", entre outras.

## O que acontece com uma pergunta bloqueada

As duas rotas devolvem a mesma mensagem (constante `BLOCKED_MESSAGE` em [pipeline.py](../susana_rag_backend/app/rag/pipeline.py)):

> Desculpe, não posso ajudar com essa questão. A Susana fornece apenas informações administrativas e institucionais da SES-DF. Para orientações clínicas, procure uma Unidade Básica de Saúde (UBS) ou ligue para o SAMU 192.

No frontend, o balão ganha borda vermelha e o selo "Fora de Escopo / Não Clínico". No MLflow fica registrado o **motivo** do bloqueio (ex.: `regex:prescricao`, `ml:p=0.71`), sem o texto da pergunta.

## Configuração

| Variável | Padrão | Efeito |
| --- | --- | --- |
| `GUARDRAIL_ENABLED_ML` | `true` | `false` = só regras (passos 1, 2, 3, 5) |
| `GUARDRAIL_THRESHOLD` | `0.4` | p(clínica) a partir da qual o ML bloqueia |
| `GUARDRAIL_MODEL_URI` | `models:/susana-guardrail@champion` | Versão do modelo a carregar |

## Testes

Em [tests/test_rag.py](../susana_rag_backend/tests/test_rag.py):

- `TestGuardrailRules`: testa as regras **sem** o modelo (bloqueios esperados, exceções administrativas, ML somando proteção);
- `TestGuardrails`: testa a API completa, incluindo as 4 perguntas clínicas que antes vazavam;
- `TestStreaming::test_blocked_message_points_to_ubs_and_samu`: confere a mensagem na rota do frontend.
