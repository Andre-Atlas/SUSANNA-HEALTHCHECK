# Controle de respostas e referências

## Comportamento implementado

- Sem trechos após a busca e o corte de contexto: resposta fixa explicando a falta
  de evidências, sem chamar o Ollama. A ausência de documento não decide a veracidade
  de uma alegação.
- Com trechos: a LLM recebe instrução para usar apenas o conteúdo fornecido,
  preservar ressalvas e escrever até três parágrafos, cada um encerrado por citação.
- O modelo pode responder `SEM_EVIDENCIA` se considerar os trechos insuficientes;
  o servidor substitui esse marcador pela mensagem fixa de limitação.
- O módulo `answer_policy.py` verifica citações numéricas, IDs existentes e citação
  no fim de cada parágrafo. Rejeita padrões de links/URLs/domínios gerados, mensagens
  vazias e respostas que o Ollama identifica como truncadas pelo limite de geração.
- Em caso de rejeição, o texto gerado não é enviado ao navegador. O servidor exibe
  uma mensagem controlada e mantém disponíveis os trechos recuperados.
- Links clicáveis continuam vindo dos registros da base, não da resposta da LLM.

Não há nova dependência, chamada externa ou segunda inferência de verificação.
Erros de conexão com o Ollama continuam sendo tratados como erros HTTP quando
a geração é necessária; a ausência de evidência dispensa a conexão.

## API e avaliação

`generate_answer` é compartilhada pela rota `/api/chat` e por `evaluate.py`.
Assim, a avaliação observa a mesma política de resposta utilizada no chatbot.

Além de `message`, `model` e `sources`, a API informa:

| Campo | Significado |
|---|---|
| `answer_status` | `no_evidence`, `insufficient_evidence`, `reference_rejected` ou `references_valid` |
| `llm_called` | Indica se houve chamada ao modelo |
| `validation_errors` | Motivos técnicos da rejeição; não contém o texto bloqueado |
| `done_reason` | Motivo de término informado pelo Ollama, quando houver geração |

`references_valid` significa apenas que as regras formais foram atendidas.
Não significa “conteúdo verdadeiro”, “fonte oficial validada” ou “resposta aprovada”.

```bash
python3 -m unittest discover -s tests -v
python3 evaluate.py --llm --output evaluation/controlled.json
```

O relatório anterior está preservado em `evaluation/llm.json`. O novo relatório
inclui os estados da política e hashes dos arquivos de código usados na avaliação.
O código de saída do avaliador verifica recuperação e erros de execução; ainda é
necessário inspecionar rejeições, abstenções e fidelidade no relatório.

## Limites

As regras não verificam semanticamente se o parágrafo é sustentado pela citação.
Uma afirmação incorreta acompanhada de um ID existente pode passar. O filtro de
links reconhece padrões comuns; não é um detector universal de endereços ofuscados.
A regra de citação por parágrafo também não mede suporte de cada frase individual.

O controle conservador pode rejeitar uma resposta útil por formato. Não inserimos
citações automaticamente, pois isso atribuiria evidência sem verificar a relação.
As sínteses da base ainda têm revisão humana pendente. Antes do piloto, é necessário
avaliar fidelidade com pessoas da equipe e perguntas independentes.

## Resultado da rodada local

Após ajustar as instruções de formato e o tratamento do marcador de abstenção:

- **21 testes automatizados aprovados.**
- **12/12 casos de recuperação aprovados**, no mesmo conjunto de desenvolvimento.
- **7 respostas** atenderam às regras formais de referências.
- **3 casos sem fontes** receberam a resposta fixa, sem inferência.
- **1 resposta** foi bloqueada por parágrafo sem citação (`antibioticos-gripe`).
- **1 caso** recebeu abstenção do modelo (`injecao`), convertida em mensagem controlada.
- Tempo acumulado da rodada: aproximadamente **31 segundos**, contra 137 segundos
  da rodada anterior. As respostas ficaram menores e três chamadas foram eliminadas;
  essa comparação não isola efeitos de cache, carga ou variabilidade do modelo.

Inspeção inicial por IA: a resposta sobre transmissão deixou de apresentar o
mecanismo indevido observado antes. Os casos sem fonte deixaram de receber
conclusões livres do modelo. Porém, `dengue-sem-acento` ainda acrescentou uma
explicação sobre ovos que não estava explicitamente na síntese; o validador formal
não detecta esse tipo de extrapolação. **Fidelidade semântica continua pendente.**

Relatório final desta etapa: `evaluation/controlled.json`. A primeira tentativa
com o controle, antes dos dois ajustes, está em `evaluation/controlled-first.json`.
Não houve edição das respostas nos relatórios. A aprovação humana continua pendente.
