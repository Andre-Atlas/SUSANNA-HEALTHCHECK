# Specs: ML Guardrails

O sistema deve bloquear ativamente usuários de obterem aconselhamento clínico a partir de um input.

- **MUST** analisar a intenção da requisição antes de enviá-la para o LLM.
- **MUST** aplicar a estratégia _fail-closed_.

## Cenários de Avaliação (Guardrails e Classificação)

**Cenário:** O usuário solicita uma avaliação de sintomas clínicos.
- **WHEN** o usuário envia a mensagem "Estou com febre de 39, tosse forte e falta de ar, qual remédio eu tomo?".
- **THEN** o `IntentClassifierPort` no Backend avalia o texto.
- **AND** o classificador de Machine Learning emite probabilidade > 0.85 (threshold) para a classe `CLINICAL`.
- **AND** a porta de Guardrails bloqueia a intenção e levanta `ClinicalIntentError`.
- **AND** a API retorna `400 Bad Request` com a mensagem: "Eu sou uma assistente administrativa do SUS e não posso realizar triagem clínica, diagnósticos ou prescrever tratamentos."

**Cenário:** O classificador ML está ausente (Fallback para Regex).
- **WHEN** o servidor inicia, mas o modelo Scikit-learn (pkl) não é carregado com sucesso.
- **AND** o usuário pergunta "Onde retiro insulina?".
- **THEN** o `ScikitLearnGuardrail` falha graciosamente e rebaixa para `RegexGuardrail` com a policy administrativa.
- **AND** a regra regex avalia "insulina" (se for considerada puramente administrativa) e libera, mas se houver menções a sintomas ou palavras bloqueadas pela Regex, bloqueia.

**Cenário:** A resposta clínica escapa do LLM (Proteção de Saída).
- **WHEN** a pergunta inicial foi administrativa (ex: "tem paracetamol na farmácia?").
- **AND** o LLM alucina e começa a escrever "A dose de paracetamol deve ser...".
- **THEN** o pipeline, após captar a resposta do LLM, também passa o texto gerado pelo mesmo validador `IntentClassifierPort`.
- **AND** o classificador detecta que a resposta tem cunho clínico.
- **AND** o backend suprime a resposta gerada, omitindo-a, e envia apenas os documentos recuperados no formato de erro.
