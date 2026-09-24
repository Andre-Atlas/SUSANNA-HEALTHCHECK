# Busca e continuidade da conversa

A busca padrão continua local, com Python e SQLite FTS5. Não foram adicionados
modelos, pacotes pip ou chamadas de IA para a recuperação.

## Funcionamento

1. `conversation.resolve_question` identifica formas limitadas de continuidade,
   como “e nesse caso?”, “e as reações?” e “pode explicar melhor?”. Usa até três
   perguntas anteriores do usuário, parando na mais recente que define um assunto.
   Uma pergunta independente, incluindo “E diabetes?”, inicia uma nova consulta.
2. Sem antecedente reconhecido, ou com contexto acima de 3.000 caracteres, o
   servidor pede o assunto e não chama a LLM. A resolução não é compreensão geral
   de linguagem: formas não reconhecidas são pesquisadas como perguntas independentes.
3. `knowledge.query_groups` agrupa variações como vacina/vacinas/imunizante,
   reconhecer/identificar e prevenir/evitar. São alternativas de recuperação,
   não equivalências clínicas. Palavras informais comuns são desconsideradas.
4. Palavras desconhecidas entre 5 e 40 caracteres admitem uma edição ou uma
   transposição adjacente, apenas quando existe uma única correção no vocabulário
   do índice e nos grupos. Termos curtos como DNA não são corrigidos.
5. FTS5 recupera até 30 candidatos por BM25. O filtro exige dois conceitos distintos
   quando há mais de um na consulta; sinônimos do mesmo grupo não contam duas vezes.
   Até três trechos são enviados ao modelo. O filtro não comprova relevância nem verdade.
6. Para continuidade, a última mensagem entregue à geração contém um JSON com
   a pergunta atual e as perguntas anteriores usadas como contexto. Esse mesmo
   conteúdo chega ao revisor e permanece quando o orçamento remove mensagens antigas.
   Respostas da IA não entram na consulta de busca e não são tratadas como fontes.

O texto digitado permanece inalterado na interface e no histórico do navegador.
Limpar a conversa remove o antecedente. Novas importações são reconhecidas sem
reinício porque o vocabulário é lido do índice em cada consulta.

## Comparação reproduzível

Execute `python3 evaluate_search.py`. O script cria um banco temporário com as
seis sínteses versionadas e grava `evaluation/search-comparison.json`, com casos,
URLs recuperadas, tempos locais e hashes do código, fontes e perguntas.
Não modifica o banco do usuário e não chama o Ollama.

Resultados de desenvolvimento em 24/09/2026: 18 perguntas originais e 20 novas,
incluindo sinônimos, digitação, linguagem informal, continuidade e mudança de assunto.

| Variante | Casos corretos | Fonte esperada em primeiro | Falsos positivos nos 9 negativos |
|---|---:|---:|---:|
| Busca original | 27/38 | 18/29 | 0 |
| Expansão, sem contexto | 36/38 | 27/29 | 0 |
| Expansão com contexto (padrão) | 38/38 | 29/29 | 0 |
| Contexto + reordenação por cobertura | 38/38 | 29/29 | 0 |

Caso correto significa encontrar a URL esperada entre os três trechos ou não
retornar fontes em um caso negativo. Não mede precisão de todos os outros trechos,
qualidade da resposta, segurança clínica nem desempenho em perguntas independentes.
Os casos foram usados no desenvolvimento; os números não são validação externa.

## Decisão sobre seleção e busca semântica

A reordenação experimental (`retrieve(..., rerank=True)`) prioriza o número de
conceitos cobertos, usando BM25 como desempate. Um teste sintético verifica seu
funcionamento, mas ela não trouxe ganho no conjunto documental; fica desativada
por padrão. A expansão e a continuidade explicam o ganho observado.

Embeddings não foram implementados nem medidos. Antes de adotá-los, ampliar o
conjunto com paráfrases independentes e comparar recuperação, fontes irrelevantes,
latência e consumo de memória contra esta referência. Não há evidência aqui de
superioridade da busca lexical sobre uma busca semântica.

Limitações: dicionário manual e pequeno, correção de um único erro, referências
conversacionais limitadas, possibilidade de recuperar um tema sem responder à
pergunta específica e leitura do vocabulário inteiro por consulta. Reavaliar o
custo desta leitura quando a base crescer. As verificações de referências e apoio
documental continuam obrigatórias. Os testes desta etapa simulam geração/revisão;
não validam respostas reais do Ollama em conversas completas.
