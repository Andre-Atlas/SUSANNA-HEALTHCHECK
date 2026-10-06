# 7. Ollama, geração e revisão

## Endereço e modelo

`server.py` configura Ollama em `http://127.0.0.1:11434` e modelo padrão `qwen2.5:7b`; `OLLAMA_MODEL` pode substituir o nome. O chat manda parâmetros `temperature: 0`, `num_predict: 700` e `num_ctx: 8192` na geração e na revisão. Veja [`server.py`](../../server.py#L24-L26), [`generate_answer()`](../../server.py#L280-L292) e [`verify_grounding()`](../../server.py#L264-L275).

`ollama_transport.py` chama `/api/chat` e lê o stream internamente, juntando fragmentos antes de devolver o resultado. “Streaming” aqui descreve o transporte Ollama; a interface não recebe esses rascunhos token a token. Veja [`chat_stream()`](../../ollama_transport.py#L11-L58).

## Etapa 1: geração

O prompt combina regras do assistente, pergunta e textos recuperados. Ele instrui o modelo a responder em português, não inventar fonte, não responder além dos documentos, citar IDs e abster-se se os trechos não responderem. `build_prompt()` reserva orçamento em relação a um contexto de 8.192 tokens usando comprimento em bytes como estimativa conservadora, não tokenizer real.

Se não houver fontes, ou houver instrução maliciosa detectada na fonte, o servidor pode responder sem chamar o modelo. Se o modelo se abstém com `SEM_EVIDENCIA`, o backend converte para a resposta padrão de insuficiência. Citações de formato inválido podem provocar uma única nova geração restrita à correção de citação.

## Etapa 2: revisão de apoio

Se a resposta não foi recusada e as referências passam as regras, `verify_grounding()` manda outra requisição ao Ollama com pergunta, parágrafos e apenas as fontes citadas. O revisor retorna JSON estruturado indicando se as fontes respondem à pergunta, se há conflito, se cada parágrafo está apoiado e quais IDs sustentam cada parágrafo.

O código valida que o JSON está bem formado, existe uma avaliação por parágrafo e os IDs citados são válidos. **A existência e correspondência do ID são verificadas pelo programa; o julgamento semântico de que o trecho realmente sustenta cada afirmação é feito pelo próprio modelo revisor.** Isso não é citação de avaliador humano nem verificação independente.

## Estados de resposta e limites

Uma resposta aceita recebe `answer_status: grounding_checked`. Falta de suporte, conflito, citação rejeitada, truncamento ou falha da revisão mudam o estado e podem substituir o texto por mensagem cautelosa. Ver [`generate_answer()`](../../server.py#L280-L336) e as validações em [`answer_policy.py`](../../answer_policy.py#L57-L120).

Há uma divergência dentro do próprio código: uma instrução antiga do prompt do revisor descreve `evidence` com trechos textuais, mas a instrução final e o schema efetivamente enviados exigem uma lista de IDs inteiros. O backend valida IDs, não verifica trechos literais copiados. Há também comentário antigo em `generate_answer()` que ainda fala em evidência literal; o formato atual descrito aqui segue o schema final e `grounding_errors()`.

O mesmo modelo escreve e revisa, logo pode errar nas duas etapas. A revisão reduz alguns riscos de formato/apoio, mas não prova verdade factual, atualidade clínica nem completude das fontes.
