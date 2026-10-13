# 10. Perguntas prováveis do professor, com respostas

As respostas estão no tamanho de uma fala. Cada uma aponta o arquivo onde o assunto é detalhado. Quando a resposta honesta inclui uma limitação, ela está na resposta: é melhor dizê-la do que ser corrigido.

## Visão geral

**1. O que o projeto faz?**
É uma assistente virtual administrativa do SUS-DF. Responde perguntas sobre serviços (telefones de hospitais, farmácia de alto custo, SAMU, ouvidoria, vacinação) com base em páginas oficiais, citando a fonte, e recusa perguntas clínicas. Roda inteiramente na máquina local. → [README](README.md)

**2. O que é RAG e por que usar em vez de só um LLM?**
RAG é buscar trechos relevantes em uma base própria e entregá-los ao modelo junto com a pergunta. Um LLM sozinho responde de memória: pode inventar um telefone, não conhece dados recentes e não cita fonte. Com RAG, a resposta se apoia em um texto que eu controlo e posso atualizar sem retreinar o modelo. → [04](04-rag.md)

**3. Por que não fazer *fine-tuning* do modelo com os dados do SUS?**
Três motivos. O conteúdo muda (endereços, horários, campanhas) e retreinar a cada mudança é caro; com RAG basta reindexar. *Fine-tuning* não dá citação de fonte. E *fine-tuning* não impede alucinação: o modelo ainda gera texto de memória.

**4. Por que rodar localmente?**
Soberania de dados e LGPD. Uma pergunta sobre saúde é dado pessoal sensível, e a proposta do projeto é que ela não saia para um provedor de nuvem. O custo é precisar de hardware e usar um modelo menor. → [01](01-arquitetura.md), seção 1.6

**5. Quais são os componentes?**
Frontend em Next.js; API em FastAPI; guardrail em scikit-learn; modelo de embeddings via sentence-transformers; ChromaDB como banco vetorial; Llama 3.1 8B servido pelo Ollama; MLflow para experimentos e versões de modelo. Guardrail, embeddings e ChromaDB rodam dentro do processo da API; o Ollama é um processo à parte. → [01](01-arquitetura.md)

## Embeddings e busca

**6. O que é um embedding?**
Um vetor de números que representa o significado de um texto. Aqui são 384 números por texto. Textos de sentido parecido geram vetores próximos, mesmo com palavras diferentes.

**7. Como o modelo gera esse vetor?**
É um Transformer codificador de 12 camadas. O texto vira tokens, cada token passa pelas camadas de atenção e sai como um vetor contextualizado, e a média desses vetores (*mean pooling*) é o embedding da frase. O modelo foi treinado para aproximar frases que são paráfrases.

**8. Por que esse modelo de embeddings?**
`paraphrase-multilingual-MiniLM-L12-v2` é multilíngue, o que importa porque o conteúdo é em português, e é pequeno (118 milhões de parâmetros), rodando rápido em CPU. A alternativa testada no benchmark, `all-MiniLM-L6-v2`, é treinada principalmente em inglês.

**9. Como é medida a semelhança?**
Distância de cosseno: `1 − cosseno do ângulo` entre os vetores. Zero é significado igual, 1 é sem relação. Usa-se cosseno porque interessa a direção do vetor, não o tamanho. Como os vetores são normalizados, o cosseno é só um produto escalar.

**10. Como o ChromaDB acha os mais próximos?**
Com um índice HNSW, um grafo em camadas em que cada vetor se liga a vizinhos próximos. A busca desce pelas camadas aproximando-se do alvo, sem comparar com todos. É uma busca **aproximada**, com custo logarítmico. Com 27 vetores não faz diferença; com milhões, é o que viabiliza.

**11. O que é *chunking* e como foi feito?**
É dividir os documentos em pedaços para indexar. Aqui: blocos de até 900 caracteres, cortando em fim de frase. **Limitação:** o modelo de embeddings só lê 128 tokens, e 16 dos 27 blocos passam disso, então o vetor representa só o início do bloco. O certo seria blocos menores. → [04](04-rag.md), seção 4.2

**12. Por que k = 3?**
É um equilíbrio. Poucos trechos podem deixar a resposta de fora; muitos enchem o prompt de ruído, aumentam a latência e confundem um modelo pequeno. Três é uma escolha comum de partida. Não foi feito experimento variando k.

**13. E se a pergunta não tiver nada a ver com a base?**
A intenção era: se a distância do melhor trecho passar de um limiar, responder "não encontrei" sem chamar o LLM. **Na prática o limiar está em 1,2 e nunca dispara**: medi 1,004 para "como fazer bolo de chocolate". A pergunta chega ao LLM, que recusa por causa do prompt. Um limiar em torno de 0,65 separaria bem, pelas minhas medições. → [04](04-rag.md), seção 4.3

## LLM

**14. Que modelo é e o que significa "8B" e "Q4_K_M"?**
Llama 3.1, da Meta, um Transformer *decoder-only*. 8B são 8 bilhões de parâmetros. Q4_K_M é a quantização: os pesos são guardados com cerca de 4 bits em vez de 16, reduzindo o modelo para 4,9 GB com pequena perda de qualidade.

**15. Como o LLM gera texto?**
Um token por vez. Dado o texto até ali, ele calcula a probabilidade de cada token possível, escolhe um, acrescenta ao texto e repete. É por isso que o streaming é natural: cada token pode ser enviado assim que sai.

**16. O que é temperatura e por que 0,1?**
Controla a aleatoriedade na escolha do token. Baixa concentra a escolha nos mais prováveis; alta diversifica. Para um serviço que deve repetir fielmente a fonte, quero o mínimo de criatividade. A semente fixa (42) reforça a reprodutibilidade.

**17. Como evitam alucinação?**
Três medidas: o prompt manda responder só com os trechos fornecidos e dá uma frase exata para quando não houver resposta; a temperatura é baixa; e a fonte é exibida para o usuário conferir. **Não é garantia**: depende de o modelo obedecer. E 7 dos 27 blocos são dados simulados, o que precisa ser dito. → [09](09-limitacoes-e-divergencias.md), seção 9.2

**18. O que é o Ollama?**
Um servidor local de modelos. Baixa o modelo, carrega na memória, usa a GPU se houver e expõe uma API HTTP. O backend fala com ele como falaria com uma API de nuvem, só que em `localhost:11434`.

**19. E se o Ollama cair?**
O adaptador lança `LLMUnavailable` e o sistema entra em **fallback extrativo**: devolve o texto bruto dos trechos recuperados. O usuário recebe a informação sem o resumo. A busca vetorial não depende do Ollama.

**20. O que é o *warm-up*?**
Na subida, o backend manda um prompt vazio ao Ollama para forçar o carregamento do modelo na memória. Sem isso, o primeiro usuário esperaria o carregamento de 4,9 GB.

## Guardrail

**21. Como as perguntas clínicas são bloqueadas?**
Em três camadas: uma regex que libera termos administrativos; um classificador TF-IDF com regressão logística que bloqueia se a probabilidade de "clínica" passar de 0,65; e regex clínicas de reserva, usadas só se o classificador não carregar. → [05](05-guardrails.md)

**22. Explique TF-IDF.**
Transforma texto em vetor. O peso de cada termo é a frequência dele na frase multiplicada por um fator que cresce quando o termo é raro no conjunto. Termos comuns a tudo pesam pouco; termos distintivos pesam muito. Usei palavras isoladas e pares de palavras.

**23. Explique regressão logística.**
É um classificador linear. Faz a soma ponderada das entradas e aplica a função sigmoide, que transforma o resultado em probabilidade entre 0 e 1. Cada termo tem um peso aprendido: positivo empurra para "clínica", negativo para "administrativa".

**24. Por que não usar o próprio LLM para classificar?**
Custo e determinismo. O classificador responde em milissegundos e dá sempre a mesma saída para a mesma entrada. Um LLM levaria segundos, poderia ser convencido por um texto malicioso (*prompt injection*) e é mais difícil de auditar.

**25. O guardrail funciona bem?**
**Não.** O F1 registrado é 0,571 e o teste automatizado de sintomas falha. Identifiquei quatro causas: dataset de 57 frases; um erro de rótulos que treina 7 frases clínicas como administrativas; a lógica não combina regex e modelo com OU, então o modelo "vence" a regex; e a liberação administrativa tem prioridade absoluta e serve de atalho. As correções das três últimas são de poucas linhas. → [05](05-guardrails.md), seção 5.6

**26. Então o sistema é inseguro?**
O filtro principal é fraco, mas há defesa em profundidade: o prompt proíbe orientação clínica e o corpus é administrativo. No teste que fiz, a pergunta de sintomas passou pelo guardrail e foi recusada pelo LLM. O problema é que a camada determinística é a que falha, e a segurança fica dependendo da obediência do modelo. Não está pronto para uso real.

**27. Qual métrica importa para o guardrail?**
O *recall* da classe clínica: das perguntas clínicas, quantas foram barradas. Um falso negativo (clínica que passa) é muito mais grave que um falso positivo (administrativa recusada). O F1 trata os dois erros como equivalentes.

**28. O que é *fail-closed*?**
Na falha ou na dúvida, bloquear. O oposto, *fail-open*, é liberar. Os documentos do projeto dizem que o guardrail é *fail-closed*; o código atual não é, porque uma probabilidade baixa do modelo libera sem consultar as regex.

## MLOps

**29. Para que serve o MLflow aqui?**
Três usos: registrar o treino do guardrail (parâmetros, F1, modelo); guardar versões do modelo no *Model Registry*; e apontar a versão em uso com o alias `@champion`. O backend carrega o modelo pelo alias. → [06](06-mlops.md)

**30. Como fariam *rollback* de um modelo ruim?**
Reaponto o alias `@champion` para a versão anterior no MLflow e reinicio o backend. Nenhuma linha de código muda, porque o backend conhece só o alias.

**31. O que é um *promotion gate*?**
Uma condição mínima de qualidade para um modelo novo virar o de produção. **No código atual o gate é `F1 ≥ 0`, que sempre aprova.** É um marcador de posição; deveria ser um limite real sobre o *recall* clínico.

**32. Como escolheram os modelos?**
Há scripts de benchmark: para embeddings, *Hit Rate* no top-3 sobre 6 perguntas; para LLMs, latência, tokens por segundo e uma nota de fidelidade por palavras-chave sobre 3 cenários. **Os conjuntos são pequenos demais para conclusão estatística, e não há runs desses benchmarks no banco MLflow desta cópia.** Servem como estrutura de avaliação a ser ampliada.

**33. E o DVC?**
Estava previsto para versionar os datasets, mas **não foi inicializado**. Os dados estão no git. É um item pendente.

## Backend e frontend

**34. Por que FastAPI?**
Validação automática com Pydantic, documentação gerada em `/docs`, suporte a respostas em streaming e é o padrão de fato para servir modelos em Python.

**35. Como funciona o streaming?**
O backend devolve uma `StreamingResponse` alimentada por um gerador Python. Cada pedaço vindo do Ollama vira uma linha JSON. No navegador, leio o corpo da resposta com `getReader()`, decodifico, separo por linha e acrescento o texto ao balão. O formato é NDJSON; **não é Server-Sent Events**, apesar de um documento do projeto dizer isso. → [02](02-frontend.md), seção 2.4

**36. Qual a vantagem do streaming?**
Reduz o tempo até a primeira palavra aparecer. O tempo total é o mesmo, mas o usuário não fica olhando uma tela parada por quatro segundos.

**37. O que é arquitetura hexagonal e o projeto segue?**
O núcleo depende de interfaces e as tecnologias entram como adaptadores. **Segue parcialmente:** o LLM tem interface (`LLMPort`) e adaptador (`OllamaAdapter`), com injeção pelo construtor. O guardrail, o retriever e o embedder são usados como classes concretas. → [01](01-arquitetura.md), seção 1.5

**38. O que é o cache semântico?**
Guarda o vetor da pergunta e a resposta. Uma pergunta nova com distância até 0,08 de uma anterior reaproveita a resposta, sem chamar o LLM. **Só está ligado na rota sem streaming**, que a tela não usa; é uma pendência de integração.

**39. O sistema aguenta muitos usuários?**
Não na forma atual. As rotas são `async` mas fazem chamadas bloqueantes, então uma pergunta trava as outras. O cache é em memória de um processo. E um único Ollama processa uma geração por vez em hardware comum. Para escalar: rotas em *thread pool* ou cliente assíncrono, cache em Redis e um servidor de inferência com *batching*.

**40. Qual a latência?**
Nas amostras do MLflow, 3,4 a 4,8 segundos para a resposta completa, quase tudo no LLM. Embedding e busca somam centésimos de segundo. A proposta falava em menos de 1,5 s; isso não se confirmou nesta máquina.

## Testes

**41. Como o projeto é testado?**
14 testes de integração com pytest, subindo a aplicação inteira: saúde, guardrail, recuperação, cache, validação de entrada e latência. 13 passam e 1 falha, justamente o do guardrail. **Não há testes unitários com componentes falsos nem teste da rota de streaming.** → [08](08-como-rodar-e-testar.md), seção 8.7

**42. Qual a diferença entre teste unitário e de integração?**
O unitário testa uma peça isolada, com as dependências substituídas por falsas; é rápido e determinístico. O de integração testa as peças reais juntas; é mais lento e pode variar. Os deste projeto são de integração e dependem de um LLM real.

## Dados e estatística

**43. Qual a diferença entre Pearson e Spearman?**
Pearson mede relação linear entre os valores e é sensível a extremos. Spearman mede relação monotônica usando os postos e é robusto a extremos. Divergência grande entre os dois sugere valores atípicos ou relação não linear. → [07](07-dados-e-eda.md)

**44. O que as correlações mostraram?**
Por mês, em 2022: SAMU × óbitos com Pearson 0,60 e Spearman 0,29; atendimentos × cirurgias com Pearson 0,64 e Spearman 0,78. **São só 12 pontos:** o Spearman de 0,29 não se distingue de zero, e nada disso indica causalidade.

**45. Por que a análise por região falhou?**
A base do SAMU registra a região como "SAMU" em todas as linhas. A saída foi inferir a região pelo nome da base da ambulância e normalizar pela população, em taxa por 100 mil habitantes.

**46. Os dados dos CSVs alimentam o chat?**
Não. São duas metades independentes. O chat usa texto de páginas institucionais. Integrar as estatísticas ao chat é trabalho futuro.

## Ética e LGPD

**47. Que cuidados com LGPD foram tomados?**
Processamento local, sem envio a terceiros; nenhuma conta de usuário nem histórico persistente; e a recusa de assuntos clínicos reduz a exposição de dados de saúde. **Pendências:** o registro no MLflow grava o texto da pergunta, contrariando o contrato do próprio projeto, e a API não tem autenticação.

**48. Qual o maior risco ético?**
Uma resposta clínica errada tomada como orientação oficial. Por isso existem o guardrail, a regra no prompt e o aviso fixo na tela. O segundo risco é atribuir a uma "fonte oficial" um conteúdo que não é: os blocos simulados precisam sair antes de qualquer uso real.

## Fechamento

**49. O que você faria diferente ou faria a seguir?**
Primeiro as quatro correções baratas de segurança: regra OU no guardrail, rótulos do dataset, gate real de promoção e limiar de distância. Depois: retirar os dados simulados, unificar as duas rotas para o streaming ter cache e telemetria, ampliar o dataset do guardrail e reduzir o tamanho dos blocos. → [09](09-limitacoes-e-divergencias.md), seção 9.8

**50. Qual foi a principal lição?**
Que em um sistema com LLM a parte difícil não é gerar texto, é **controlar** o que entra e o que sai: qualidade do corpus, limiares calibrados com medição e um filtro de segurança avaliado pela métrica certa. A arquitetura fica pronta rápido; a validação é o trabalho.

## Se você não souber responder

Diga o que sabe e onde verificaria: "não medi isso; eu verificaria rodando X" é uma resposta de engenharia. Evite afirmar o que está nas notas de release sem ter conferido: várias afirmações de lá não batem com o código, e a lista está em [09](09-limitacoes-e-divergencias.md).
