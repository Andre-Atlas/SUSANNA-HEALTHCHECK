window.CUES = {
"visao-01": [
[
0.0,
"Esta cena resume o README."
],
[
1.54,
"Você está vendo duas plataformas lado a lado."
],
[
4.14,
"A da esquerda, esverdeada, é a assistente Susana."
],
[
7.08,
"Os dois cubos sobre ela estão brilhando:"
],
[
9.56,
"o azul é a interface de chat e o verde é o backend."
],
[
12.44,
"A Susana responde perguntas administrativas da Secretaria de Saúde do Distrito Federal usando um modelo de linguagem que roda na própria máquina,"
],
[
19.78,
"sempre citando a fonte."
]
],
"visao-02": [
[
0.0,
"Os cubos da esquerda continuam acesos."
],
[
2.36,
"Juntos eles formam a primeira metade do repositório:"
],
[
5.28,
"o chat na web, a API, o motor de busca e geração, e o controle de modelos."
],
[
9.63,
"Perguntas clínicas devem ser barradas antes de chegar ao modelo."
]
],
"visao-03": [
[
0.0,
"Agora o brilho passa para a plataforma da direita."
],
[
2.46,
"A pilha de placas lilases representa os arquivos com dados abertos do SUS do Distrito Federal,"
],
[
7.48,
"e o cubo amarelo são os notebooks e scripts de análise."
],
[
11.4,
"Essa é a segunda metade:"
],
[
12.92,
"a análise exploratória, que foi a primeira etapa do trabalho."
]
],
"visao-04": [
[
0.0,
"Observe a bolinha amarela saindo da pilha de dados, à direita, em direção à Susana."
],
[
4.7,
"Ela representa os arquivos exportados pela análise."
],
[
7.46,
"No meio do caminho ela fica vermelha e cai no vão entre as plataformas."
],
[
11.42,
"É isso que acontece no projeto:"
],
[
13.3,
"esses arquivos foram descritos como sendo para a assistente, mas ela nunca os lê."
],
[
17.5,
"As duas metades não se conectam."
]
],
"visao-05": [
[
0.0,
"Abaixo das plataformas aparece um resumo em números."
],
[
2.76,
"São vinte e sete trechos de texto indexados,"
],
[
5.42,
"cada um representado por um vetor de trezentas e oitenta e quatro dimensões,"
],
[
9.28,
"e três trechos recuperados a cada pergunta."
]
],
"visao-06": [
[
0.0,
"Os números mudam para o filtro de segurança e os testes."
],
[
2.85,
"O classificador teve nota de zero vírgula cinquenta e sete, treinado com apenas cinquenta e sete frases."
],
[
9.32,
"E de catorze testes automatizados, treze passam e um falha."
]
],
"visao-07": [
[
0.0,
"Para fechar:"
],
[
0.72,
"se o tempo for curto, a leitura recomendada são os documentos um, quatro, cinco, nove e dez."
],
[
6.06,
"O nove, sobre limitações, é o mais importante para apresentar a uma banca."
]
],
"fluxo-01": [
[
0.0,
"Esta cena mostra o caminho de uma pergunta pelo sistema."
],
[
2.72,
"Há seis peças em linha:"
],
[
3.87,
"à esquerda a placa azul do navegador, depois o cubo verde da API,"
],
[
7.72,
"o losango amarelo do filtro de segurança, a esfera facetada roxa que gera os vetores,"
],
[
12.44,
"o cilindro azul claro do banco vetorial e, isolada à direita, a esfera rosa do Ollama,"
],
[
17.26,
"que roda o modelo de linguagem."
],
[
19.14,
"A moldura verde indica que as quatro peças do meio vivem no mesmo processo."
],
[
23.0,
"Repare na bolinha branca:"
],
[
24.38,
"ela sai do navegador e salta até a API."
],
[
26.48,
"É a pergunta sobre o telefone do Hospital de Taguatinga sendo enviada."
]
],
"fluxo-02": [
[
0.0,
"A bolinha salta da API para o losango amarelo."
],
[
2.4,
"É o filtro de segurança perguntando:"
],
[
4.28,
"isto é uma pergunta clínica?"
],
[
5.76,
"Como não é, o losango acende e a pergunta segue adiante."
]
],
"fluxo-03": [
[
0.0,
"Agora a bolinha, verde porque foi aprovada, vai até a esfera roxa."
],
[
3.78,
"Ali o texto da pergunta é transformado em uma lista de trezentos e oitenta e quatro números,"
],
[
8.24,
"que representa o seu significado."
]
],
"fluxo-04": [
[
0.0,
"A bolinha roxa carrega esse vetor até o cilindro do banco vetorial."
],
[
3.46,
"O banco compara com os vinte e sete trechos guardados e devolve os três mais parecidos."
],
[
8.26,
"O melhor deles é o trecho dos hospitais regionais."
]
],
"fluxo-05": [
[
0.0,
"A bolinha sai da moldura verde e atravessa até a esfera rosa."
],
[
3.44,
"Isso mostra que o Ollama é um processo separado:"
],
[
5.84,
"a API envia para ele as instruções, os três trechos e a pergunta."
]
],
"fluxo-06": [
[
0.0,
"Veja a fila de bolinhas rosas voltando por cima, do Ollama até a API e depois até o navegador."
],
[
5.14,
"Cada bolinha é um pedaço da resposta."
],
[
7.42,
"O modelo escreve palavra por palavra e a API repassa cada pedaço assim que ele sai,"
],
[
11.74,
"por isso o texto aparece aos poucos na tela."
]
],
"fluxo-07": [
[
0.0,
"Começa o segundo cenário, agora com uma pergunta clínica:"
],
[
3.0,
"que remédio tomar para dor de cabeça."
],
[
4.94,
"A bolinha sai do navegador e chega à API pelo mesmo caminho."
]
],
"fluxo-08": [
[
0.0,
"A bolinha vai até o losango do filtro de segurança, e desta vez ele bloqueia."
],
[
3.75,
"Repare que as três peças seguintes ficam apagadas:"
],
[
7.14,
"o gerador de vetores, o banco e o modelo de linguagem nem são chamados."
]
],
"fluxo-09": [
[
0.0,
"A bolinha fica vermelha e volta do filtro para a API, que monta a mensagem de recusa sozinha,"
],
[
4.62,
"sem usar o modelo."
]
],
"fluxo-10": [
[
0.0,
"Por fim, a bolinha vermelha retorna ao navegador."
],
[
2.52,
"A tela mostra um pedido de desculpas e marca a resposta como bloqueada."
]
],
"frontend-01": [
[
0.0,
"Esta cena mostra o frontend."
],
[
1.68,
"O painel escuro à esquerda é a tela do chat no navegador, e o bloco verde à direita é o backend."
],
[
6.96,
"Repare no balão azul claro que acabou de surgir no painel:"
],
[
9.96,
"é a mensagem do cidadão sendo acrescentada ao histórico, logo depois de ele apertar Enter."
]
],
"frontend-02": [
[
0.0,
"Agora aparece um balão branco pulsando, logo abaixo."
],
[
3.04,
"É o balão vazio da assistente, que será preenchido aos poucos."
],
[
6.32,
"O efeito pulsante é o indicador de carregamento."
]
],
"frontend-03": [
[
0.0,
"Veja a bolinha branca saindo do balão do cidadão e voando até o bloco verde."
],
[
3.98,
"É a requisição saindo do navegador direto para o backend."
],
[
7.06,
"Como ela parte do navegador, e não do servidor da página,"
],
[
10.18,
"o backend precisa liberar esse acesso entre origens diferentes."
]
],
"frontend-04": [
[
0.0,
"Agora os retângulos rosas vêm do backend, um de cada vez, e entram no balão branco."
],
[
4.7,
"Cada retângulo é uma linha com um pedacinho de texto."
],
[
7.32,
"Observe o balão:"
],
[
8.3,
"a frase vai crescendo a cada chegada."
],
[
10.22,
"É assim que a leitura em fluxo funciona:"
],
[
12.38,
"a primeira palavra aparece assim que é gerada."
]
],
"frontend-05": [
[
0.0,
"A resposta ficou completa e apareceu um rodapé azul embaixo do balão:"
],
[
4.04,
"fonte oficial, hospitais regionais."
],
[
6.58,
"Ele vem da última linha enviada pelo backend, que traz os dados finais da resposta."
]
],
"frontend-06": [
[
0.0,
"O balão mudou:"
],
[
0.92,
"a borda ficou vermelha e o rodapé diz fora de escopo, não clínico."
],
[
4.64,
"É a aparência usada quando o filtro de segurança barra a pergunta, como a do remédio para dor de cabeça."
]
],
"frontend-07": [
[
0.0,
"Agora a borda está amarela, com o aviso informação ausente."
],
[
2.57,
"Esse é o terceiro visual:"
],
[
4.6,
"a pergunta não foi bloqueada, mas a resposta veio sem nenhuma fonte."
]
],
"frontend-08": [
[
0.0,
"Atenção a este defeito."
],
[
1.5,
"Dois retângulos vermelhos saem do backend e desaparecem antes de chegar ao balão."
],
[
5.62,
"Eles representam uma linha que chegou cortada em dois pacotes de rede."
],
[
8.98,
"O código não junta as duas metades, então esse pedaço se perde, e a frase no balão fica com um buraco."
]
],
"frontend-09": [
[
0.0,
"O balão volta ao normal para o resumo das outras fragilidades:"
],
[
3.28,
"a página não confere se o servidor respondeu com erro, o endereço do backend está fixo no código,"
],
[
8.46,
"e o histórico existe só na memória do navegador."
],
[
10.85,
"Recarregou a página, a conversa some."
]
],
"backend-01": [
[
0.0,
"Esta cena tem duas partes."
],
[
1.78,
"A primeira mostra a subida do backend."
],
[
3.54,
"Você vê oito cubos cinzas numerados, um para cada etapa da inicialização,"
],
[
7.52,
"e acima deles um aviso em vermelho:"
],
[
9.82,
"enquanto a preparação não termina, as rotas de chat respondem com erro quinhentos e três."
],
[
14.52,
"Antes mesmo dessas etapas, o programa já carregou as configurações e o filtro de segurança."
]
],
"backend-02": [
[
0.0,
"Os dois primeiros cubos ficam verdes."
],
[
2.22,
"O primeiro é a configuração do registro de experimentos."
],
[
4.92,
"O segundo é o carregamento do modelo que gera os vetores, a etapa mais lenta, de dois a cinco segundos."
]
],
"backend-03": [
[
0.0,
"Agora acendem os cubos três, quatro, cinco e seis:"
],
[
3.66,
"o banco vetorial é aberto, o cliente do modelo de linguagem é criado, o cache de respostas também,"
],
[
8.9,
"e tudo é montado em um único orquestrador."
]
],
"backend-04": [
[
0.0,
"O cubo sete acende."
],
[
1.34,
"É a leitura dos textos da base."
],
[
3.14,
"Só entram trechos que ainda não existiam, por isso o registro mostra zero novos de vinte e sete."
]
],
"backend-05": [
[
0.0,
"O último cubo acende e o aviso lá em cima fica verde:"
],
[
2.74,
"sistema pronto."
],
[
3.33,
"Essa etapa final é o aquecimento,"
],
[
5.84,
"uma chamada vazia que obriga o modelo de quase cinco gigabytes a já ficar carregado na memória,"
],
[
10.8,
"para o primeiro usuário não esperar."
]
],
"backend-06": [
[
0.0,
"A cena muda para a segunda parte:"
],
[
1.78,
"duas fileiras de cubos, que são as duas rotas de chat."
],
[
4.68,
"Na fileira de cima, a bolinha branca atravessa cinco etapas:"
],
[
8.06,
"filtro de segurança, cache, busca, modelo de linguagem e registro."
],
[
12.24,
"É a rota de resposta completa."
],
[
13.96,
"Só que quem a usa são os testes automatizados."
]
],
"backend-07": [
[
0.0,
"Agora a bolinha percorre a fileira de baixo, que é a rota usada pela tela."
],
[
3.65,
"Repare nos dois cubos vermelhos transparentes:"
],
[
6.52,
"eles marcam o que falta nesse caminho."
],
[
8.36,
"Não há cache e não há registro."
]
],
"backend-08": [
[
0.0,
"Os dois cubos fantasmas piscam para reforçar a consequência:"
],
[
3.48,
"o caminho que o usuário realmente usa não aproveita o cache,"
],
[
6.6,
"não deixa registro e não é coberto por nenhum teste."
]
],
"backend-09": [
[
0.0,
"Veja a bolinha vermelha parada no começo da fileira de cima, pulsando, enquanto a branca anda na de baixo."
],
[
5.38,
"Ela mostra o bloqueio:"
],
[
6.6,
"as rotas são declaradas como assíncronas, mas fazem trabalho pesado por dentro."
],
[
10.94,
"Enquanto uma pergunta é processada, as outras ficam esperando."
]
],
"backend-10": [
[
0.0,
"Para terminar, os códigos de resposta:"
],
[
1.71,
"duzentos para respostas normais, inclusive as bloqueadas;"
],
[
5.03,
"quatrocentos e vinte e dois para mensagem inválida;"
],
[
7.97,
"quinhentos para erro interno;"
],
[
9.76,
"e quinhentos e três enquanto o sistema ainda está subindo."
]
],
"vetores-01": [
[
0.0,
"Esta cena mostra a busca por significado."
],
[
2.44,
"A esfera de linhas finas, girando devagar, é o espaço dos vetores."
],
[
6.28,
"Cada ponto colorido é um dos vinte e sete trechos da base, e as cores agrupam os assuntos:"
],
[
11.14,
"unidades, emergência, serviços, vacinação."
],
[
14.32,
"Repare na linha branca crescendo do centro até a superfície:"
],
[
17.46,
"é a pergunta sobre o telefone do hospital virando um ponto na esfera."
],
[
20.98,
"As posições aqui são ilustrativas."
]
],
"vetores-02": [
[
0.0,
"Agora saem três linhas verdes do ponto branco até os três trechos mais próximos, que crescem e pulsam."
],
[
5.4,
"O ângulo entre eles é pequeno, o que significa assunto parecido."
],
[
8.96,
"A distância medida foi de zero vírgula vinte e cinco."
]
],
"vetores-03": [
[
0.0,
"A pergunta muda para:"
],
[
0.94,
"como fazer bolo de chocolate."
],
[
2.84,
"Veja a nova linha branca:"
],
[
4.38,
"ela aponta para o outro lado da esfera, longe de todos os pontos coloridos."
]
],
"vetores-04": [
[
0.0,
"Mesmo assim, três linhas vermelhas ligam a pergunta aos três trechos menos distantes."
],
[
4.28,
"Sempre existem três mais próximos, ainda que não tenham nada a ver."
],
[
7.78,
"A distância agora é de um vírgula zero, vetores quase perpendiculares."
]
],
"vetores-05": [
[
0.0,
"As linhas ficam laranjas para marcar o problema."
],
[
2.34,
"O limite configurado era um vírgula dois, acima dessa distância, então ele nunca barrava nada,"
],
[
7.92,
"e os trechos sem relação seguiam para o modelo de linguagem."
],
[
10.49,
"Um limite entre zero vírgula seis e zero vírgula sete separaria os dois casos."
]
],
"guardrail-01": [
[
0.0,
"Esta cena mostra o filtro de segurança por dentro."
],
[
2.74,
"Há três argolas em linha, que são as três camadas de decisão:"
],
[
5.92,
"a azul, das palavras administrativas;"
],
[
8.18,
"a amarela, do classificador estatístico;"
],
[
10.62,
"e a cinza apagada, das palavras clínicas, que quase nunca é usada."
],
[
14.29,
"Embaixo ficam duas placas:"
],
[
16.2,
"a verde, libera, e a vermelha, bloqueia."
],
[
18.8,
"A bolinha branca que entra pela esquerda é a pergunta sobre o horário de funcionamento da U B S,"
],
[
23.24,
"chegando à primeira argola."
]
],
"guardrail-02": [
[
0.0,
"A bolinha fica verde e desce direto da argola azul para a placa verde."
],
[
3.64,
"A palavra horário é administrativa, então a mensagem é liberada na hora."
],
[
7.54,
"Decisão correta."
]
],
"guardrail-03": [
[
0.0,
"Nova mensagem:"
],
[
0.96,
"que remédio devo tomar para dor de cabeça."
],
[
3.16,
"A bolinha chega à argola azul e não encontra nenhuma palavra administrativa."
]
],
"guardrail-04": [
[
0.0,
"Ela segue até a argola amarela, onde o classificador calcula a chance de ser uma pergunta clínica:"
],
[
4.42,
"sessenta e seis por cento."
]
],
"guardrail-05": [
[
0.0,
"A bolinha fica vermelha e desce para a placa de bloqueio."
],
[
2.92,
"O limite era sessenta e cinco por cento, então ela foi barrada, mas por apenas um ponto de diferença."
]
],
"guardrail-06": [
[
0.0,
"Terceira mensagem:"
],
[
1.08,
"estou sentindo muita febre e dor no corpo."
],
[
3.44,
"De novo a bolinha passa pela argola azul sem encontrar nada."
]
],
"guardrail-07": [
[
0.0,
"Na argola amarela, o classificador dá sessenta por cento, abaixo do limite."
]
],
"guardrail-08": [
[
0.0,
"Repare no erro:"
],
[
0.88,
"a bolinha fica laranja e desce para a placa verde."
],
[
3.46,
"A mensagem foi liberada."
],
[
4.96,
"A argola cinza, que reconheceria a expressão estou sentindo,"
],
[
8.18,
"nunca é consultada quando o classificador está funcionando."
],
[
11.28,
"É exatamente o teste automatizado que falha."
]
],
"guardrail-09": [
[
0.0,
"Última mensagem:"
],
[
1.12,
"qual a dose de dipirona e onde fica a U B S."
],
[
3.94,
"Ela mistura um pedido clínico com um administrativo, e chega à argola azul."
]
],
"guardrail-10": [
[
0.0,
"A bolinha fica laranja e desce direto para a placa verde."
],
[
3.14,
"As palavras onde fica bastaram para liberar tudo, e a parte clínica chega intacta ao modelo de linguagem."
],
[
8.78,
"É a segunda falha do filtro."
]
],
"mlops-01": [
[
0.0,
"Esta cena acompanha o treino do classificador de segurança."
],
[
3.02,
"As peças estão em linha:"
],
[
4.38,
"a placa azul clara é o arquivo com as cinquenta e sete frases;"
],
[
7.8,
"depois vêm a divisão dos dados, o treino, a nota, o portão de promoção em forma de argola laranja e,"
],
[
13.54,
"no fim, a caixa verde do registro de modelos, com a etiqueta amarela champion."
],
[
17.92,
"A bolinha branca sai do arquivo e vai para a divisão."
],
[
20.78,
"Há um detalhe grave aqui:"
],
[
22.12,
"sete frases clínicas estavam com o rótulo em outro formato e acabaram tratadas como administrativas."
]
],
"mlops-02": [
[
0.0,
"A bolinha passa da divisão para o treino."
],
[
1.98,
"Das cinquenta e sete frases,"
],
[
3.85,
"quarenta e duas servem para ensinar o modelo e quinze ficam guardadas para a prova,"
],
[
7.94,
"sempre com a mesma divisão, para o experimento poder ser repetido."
]
],
"mlops-03": [
[
0.0,
"Do treino, a bolinha vai até a esfera rosa, que é a nota."
],
[
3.08,
"O resultado foi zero vírgula cinquenta e sete, medido em apenas quinze exemplos."
],
[
7.13,
"Com tão pouco, uma única frase a mais ou a menos muda bastante a nota."
]
],
"mlops-04": [
[
0.0,
"Agora a bolinha laranja atravessa a argola."
],
[
2.13,
"Esse é o portão de promoção, que deveria barrar modelos ruins."
],
[
5.56,
"Só que a condição escrita era nota maior ou igual a zero, que é sempre verdadeira."
],
[
10.2,
"Qualquer modelo passava."
]
],
"mlops-05": [
[
0.0,
"A bolinha chega à caixa verde, o registro de modelos."
],
[
2.39,
"Cada treino cria uma versão nova, e a etiqueta champion passa a apontar para ela."
],
[
7.06,
"Neste banco existia só a versão um."
]
],
"mlops-06": [
[
0.0,
"Veja a bolinha descendo da caixa do registro para a caixa de baixo, que é o backend."
],
[
4.34,
"Ao iniciar, ele pede o modelo pela etiqueta champion, sem saber o número da versão."
]
],
"mlops-07": [
[
0.0,
"Aparece uma caixa cinza transparente acima da versão um:"
],
[
3.26,
"uma versão dois hipotética."
],
[
4.94,
"Acompanhe a etiqueta amarela:"
],
[
6.6,
"ela sobe para a versão dois e depois desce de volta para a um."
],
[
9.58,
"Isso é a reversão:"
],
[
10.72,
"se a versão nova for ruim, basta reapontar a etiqueta e reiniciar o backend, sem mexer em código."
]
],
"mlops-08": [
[
0.0,
"No canto inferior esquerdo surgem duas barras quase do mesmo tamanho."
],
[
3.11,
"A azul é o tempo total de uma resposta, três segundos e quarenta e cinco centésimos."
],
[
8.62,
"A rosa é só o modelo de linguagem, três segundos e quarenta e três."
],
[
12.72,
"Ou seja, quase todo o tempo de espera vem da geração do texto."
]
],
"mlops-09": [
[
0.0,
"Para fechar, as pendências:"
],
[
1.64,
"a ferramenta de versionamento de dados foi instalada mas nunca inicializada,"
],
[
5.42,
"não há comparações de modelos registradas neste banco, e só uma das duas rotas grava essas medições."
]
],
"eda07-01": [
[
0.0,
"Esta cena é sobre a análise exploratória dos dados."
],
[
3.26,
"Você vê um gráfico de dispersão:"
],
[
5.04,
"cada um dos doze pontos azuis é um mês de dois mil e vinte e dois."
],
[
8.6,
"No eixo de baixo estão os chamados do SAMU, e no eixo lateral, os óbitos."
],
[
12.62,
"A linha amarela mostra a tendência."
],
[
14.46,
"Os pontos são ilustrativos;"
],
[
16.06,
"os resultados são os do estudo."
]
],
"eda07-02": [
[
0.0,
"Repare nos dois pontos laranjas pulsando no canto superior direito."
],
[
3.76,
"São meses fora do padrão, e são eles que puxam a linha para cima."
],
[
7.18,
"Por isso uma medida de correlação dá zero vírgula sessenta e a outra, que olha só a ordem dos meses,"
],
[
12.34,
"dá zero vírgula vinte e nove."
],
[
13.97,
"Com apenas doze pontos, essa segunda não se distingue de zero."
]
],
"eda07-03": [
[
0.0,
"Os pontos se rearranjam e agora ficam bem alinhados com a linha amarela."
],
[
4.02,
"O gráfico passou a comparar atendimentos ambulatoriais com cirurgias."
],
[
7.8,
"Meses com mais consultas têm mais cirurgias, e as duas medidas concordam."
],
[
12.02,
"Ainda assim são doze pontos, e correlação não prova causa."
]
],
"eda07-04": [
[
0.0,
"A cena muda para a comparação por região."
],
[
2.22,
"À esquerda, sete caixas azuis com as regiões de saúde, vindas da base de óbitos."
],
[
7.22,
"À direita, uma única caixa rosa pulsando, escrito SAMU:"
],
[
10.84,
"nessa base a coluna de região tem sempre o mesmo valor."
],
[
13.98,
"No meio aparece o aviso de cruzamento vazio."
],
[
16.68,
"Não há como comparar."
]
],
"eda07-05": [
[
0.0,
"Veja a caixa rosa se dividindo em sete, uma para cada região, e as linhas verdes ligando os dois lados."
],
[
5.64,
"Essa foi a solução:"
],
[
6.98,
"descobrir a região pelo nome da base da ambulância."
],
[
9.9,
"Por exemplo, a abreviação de Sobradinho indica a região Norte."
],
[
13.32,
"Depois, comparar por taxa a cada cem mil habitantes."
],
[
16.22,
"É uma regra frágil, que pode errar."
]
],
"eda07-06": [
[
0.0,
"Com as regiões ligadas, ficam duas ressalvas."
],
[
2.72,
"Os óbitos são contados pelo lugar onde a pessoa morava, e o SAMU pelo lugar da base da ambulância,"
],
[
7.86,
"que não são a mesma geografia."
],
[
9.66,
"E os arquivos exportados no final não são lidos pelo chat."
]
],
"run08-01": [
[
0.0,
"Esta cena mostra como colocar tudo no ar."
],
[
2.34,
"À esquerda há quatro colunas, uma para cada serviço, que começam achatadas."
],
[
6.46,
"À direita, pequenas pilhas de blocos cinzas, que são os catorze testes separados por grupo."
],
[
11.17,
"Repare na primeira coluna, a rosa, subindo:"
],
[
14.1,
"é o Ollama, que precisa estar rodando com o modelo já baixado."
]
],
"run08-02": [
[
0.0,
"Sobe a coluna verde, o backend, na porta oito mil."
],
[
2.88,
"Ele está pronto quando o registro mostra a mensagem de sistema pronto, com vinte e sete documentos."
]
],
"run08-03": [
[
0.0,
"Agora sobe a coluna azul, o frontend, na porta três mil."
],
[
3.1,
"É nesse endereço que o chat abre no navegador."
]
],
"run08-04": [
[
0.0,
"A quarta coluna, roxa, é o painel do registro de experimentos."
],
[
3.44,
"Ela é opcional:"
],
[
4.68,
"o sistema funciona sem ela."
]
],
"run08-05": [
[
0.0,
"Com tudo no ar, uma bolinha branca passa por cima das colunas, do frontend ao backend e ao Ollama."
],
[
5.3,
"É o roteiro de demonstração:"
],
[
7.02,
"uma pergunta de telefone que funciona, uma de remédio que é bloqueada,"
],
[
10.74,
"a do bolo de chocolate e a de febre, que expõe a falha do filtro."
]
],
"run08-06": [
[
0.0,
"Olhe para a direita:"
],
[
0.96,
"os blocos dos testes vão ficando verdes um a um, conforme os testes rodam."
],
[
5.02,
"Um deles, na pilha do filtro de segurança, fica vermelho."
],
[
8.0,
"O resultado é treze aprovados e um reprovado, em pouco mais de um minuto,"
],
[
12.04,
"porque os testes usam os serviços reais."
]
],
"run08-07": [
[
0.0,
"O bloco vermelho está pulsando."
],
[
1.84,
"É o teste que envia a frase estou sentindo muita febre e dor no corpo e espera um bloqueio que não acontece."
],
[
7.28,
"O teste está certo:"
],
[
8.56,
"ele denuncia um defeito real."
]
],
"run08-08": [
[
0.0,
"Um último cuidado:"
],
[
1.14,
"alguns comandos mudam o estado do projeto."
],
[
3.6,
"O treino troca o modelo em uso, a coleta sobrescreve os textos da base,"
],
[
7.3,
"e a comparação de modelos baixa dezenas de gigabytes."
],
[
10.78,
"Depois de qualquer um deles, é preciso reiniciar o backend."
]
],
"limites-01": [
[
0.0,
"Esta cena é um mural das limitações do projeto."
],
[
2.96,
"São seis colunas de plaquinhas, cada coluna uma categoria e cada plaquinha um problema numerado."
],
[
8.02,
"Agora só a primeira coluna, vermelha, está acesa e saltada para a frente:"
],
[
12.04,
"é a segurança clínica, com sete itens, os mais graves."
],
[
15.58,
"Entre eles, o classificador fraco e o portão de promoção que aprovava qualquer modelo."
]
],
"limites-02": [
[
0.0,
"O destaque passa para a coluna laranja, das fontes."
],
[
2.55,
"Sete dos vinte e sete trechos eram texto de demonstração com endereços fictícios,"
],
[
7.72,
"e a fonte mostrada na tela é sempre a do trecho mais próximo, mesmo que o modelo tenha usado outro."
]
],
"limites-03": [
[
0.0,
"Acende a coluna amarela, o caminho que o usuário realmente percorre."
],
[
3.64,
"A rota usada pela tela não tinha cache, não deixava registro e não tinha nenhum teste."
]
],
"limites-04": [
[
0.0,
"Agora a coluna roxa, do controle de modelos."
],
[
2.66,
"As notas de versão falavam em quarta versão e em comparações entre modelos,"
],
[
6.78,
"mas neste banco só havia a versão um e nenhuma comparação registrada."
]
],
"limites-05": [
[
0.0,
"A coluna azul é a maior, com dez itens de arquitetura e código:"
],
[
3.84,
"lógica duplicada entre as duas rotas, chamadas que travam o servidor,"
],
[
7.6,
"e um tempo de resposta medido bem acima do prometido."
]
],
"limites-06": [
[
0.0,
"Por último, a coluna azul clara, da análise de dados:"
],
[
2.77,
"correlações calculadas com apenas doze pontos e regiões do SAMU deduzidas a partir de pedaços de texto."
]
],
"limites-07": [
[
0.0,
"Agora preste atenção:"
],
[
1.38,
"seis plaquinhas vão ficando verdes, uma após a outra, quase todas na coluna da segurança."
],
[
6.14,
"São as correções prioritárias:"
],
[
8.0,
"combinar palavras-chave e classificador, corrigir os rótulos,"
],
[
11.64,
"criar um portão de verdade e baixar o limite de distância."
],
[
14.52,
"Quatro mudanças pequenas que atacam o risco clínico."
]
],
"limites-08": [
[
0.0,
"O mural inteiro volta a acender."
],
[
1.86,
"A leitura honesta é esta:"
],
[
3.32,
"uma prova de conceito com a arquitetura certa e a execução incompleta,"
],
[
6.94,
"em que os defeitos mais graves são baratos de corrigir."
]
],
"perguntas-01": [
[
0.0,
"Esta cena reúne as perguntas prováveis do professor."
],
[
2.94,
"As cinquenta cartas formam um anel, e as cores indicam os temas."
],
[
6.54,
"A cada pergunta o anel gira, e a carta escolhida vem para a frente, sobe e cresce."
],
[
10.9,
"A primeira é a carta dois:"
],
[
12.3,
"o que é RAG, e por que usar em vez de só um modelo de linguagem?"
],
[
15.46,
"A resposta:"
],
[
15.84,
"é buscar trechos relevantes em uma base própria e entregá-los ao modelo junto com a pergunta."
],
[
21.06,
"Sozinho, o modelo responde de memória, pode inventar um telefone e não cita fonte."
]
],
"perguntas-02": [
[
0.0,
"O anel gira até a carta nove, do tema de busca:"
],
[
2.52,
"como é medida a semelhança?"
],
[
4.06,
"Pela distância de cosseno, que olha o ângulo entre dois vetores."
],
[
7.54,
"Zero quer dizer mesmo significado, e um, nenhuma relação."
]
],
"perguntas-03": [
[
0.0,
"Sobe a carta treze:"
],
[
1.18,
"e se a pergunta não tiver nada a ver com a base?"
],
[
3.58,
"A ideia era responder não encontrei quando a distância passasse de um limite."
],
[
7.24,
"Mas o limite estava alto demais e nunca disparava;"
],
[
10.16,
"a pergunta do bolo de chocolate chegava ao modelo."
]
],
"perguntas-04": [
[
0.0,
"Carta dezesseis, já no tema do modelo de linguagem:"
],
[
2.9,
"o que é temperatura, e por que tão baixa?"
],
[
4.96,
"Ela controla o quanto o modelo arrisca na escolha das palavras."
],
[
8.14,
"Para repetir fielmente uma fonte oficial, queremos o mínimo de criatividade."
]
],
"perguntas-05": [
[
0.0,
"Carta dezenove:"
],
[
1.0,
"e se o Ollama cair?"
],
[
1.96,
"O sistema não devolve erro."
],
[
3.34,
"Ele entrega o texto bruto dos trechos encontrados, porque a busca não depende do modelo de linguagem."
]
],
"perguntas-06": [
[
0.0,
"O anel gira para a parte amarela, do filtro de segurança, e sobe a carta vinte e cinco:"
],
[
4.54,
"o filtro funciona bem?"
],
[
6.04,
"A resposta honesta é não."
],
[
7.47,
"A nota era baixa e o teste de sintomas falhava, por causa de poucos dados,"
],
[
11.83,
"rótulos errados e uma lógica que deixava o classificador vencer as palavras-chave."
]
],
"perguntas-07": [
[
0.0,
"Carta vinte e sete:"
],
[
1.22,
"qual medida importa para o filtro?"
],
[
2.78,
"De todas as perguntas clínicas, quantas foram barradas."
],
[
5.94,
"Deixar passar uma pergunta clínica é muito mais grave que recusar uma administrativa."
]
],
"perguntas-08": [
[
0.0,
"Carta trinta, no tema de operações:"
],
[
2.08,
"como desfazer a troca por um modelo ruim?"
],
[
4.24,
"Basta reapontar a etiqueta champion para a versão anterior e reiniciar o backend."
],
[
8.36,
"Nenhuma linha de código muda."
]
],
"perguntas-09": [
[
0.0,
"Carta trinta e cinco:"
],
[
1.14,
"como funciona a resposta em fluxo?"
],
[
3.16,
"O backend envia uma linha para cada pedaço de texto gerado,"
],
[
6.06,
"e o navegador vai lendo e acrescentando ao balão."
],
[
8.72,
"É um formato simples, de um objeto por linha, e não o padrão de eventos que um documento antigo citava."
]
],
"perguntas-10": [
[
0.0,
"Carta quarenta e um, sobre testes:"
],
[
2.02,
"como o projeto é testado?"
],
[
3.54,
"Com catorze testes que sobem a aplicação inteira."
],
[
5.93,
"Treze passam e um falha, justamente o do filtro de segurança."
]
],
"perguntas-11": [
[
0.0,
"Carta quarenta e quatro, de estatística:"
],
[
2.06,
"o que as correlações mostraram?"
],
[
3.72,
"Relações moderadas entre SAMU e óbitos, e entre atendimentos e cirurgias."
],
[
8.14,
"Mas são só doze pontos, e nada disso indica causa."
]
],
"perguntas-12": [
[
0.0,
"Carta quarenta e sete, de ética:"
],
[
1.94,
"que cuidados com a lei de proteção de dados foram tomados?"
],
[
4.92,
"Tudo é processado localmente, sem contas nem histórico."
],
[
7.29,
"Ficaram pendentes o registro do texto das perguntas e a falta de autenticação."
]
],
"perguntas-13": [
[
0.0,
"E a última carta, a cinquenta:"
],
[
1.9,
"qual foi a principal lição?"
],
[
3.6,
"Em um sistema com modelo de linguagem, o difícil não é gerar texto, é controlar o que entra e o que sai."
],
[
9.16,
"A arquitetura fica pronta rápido;"
],
[
10.94,
"a validação é o trabalho."
]
],
"arq-01": [
[
0.0,
"Esta cena mostra a arquitetura da segunda versão do sistema."
],
[
3.12,
"Há duas fileiras de caixas ligadas por linhas finas."
],
[
6.06,
"Em cima, da esquerda para a direita:"
],
[
7.98,
"o cidadão, a interface, a API, o filtro de segurança, o interpretador de linguagem e o cache."
],
[
13.64,
"Embaixo:"
],
[
14.32,
"o banco de sessões, o gerador de respostas, a busca online, o banco vetorial e a ingestão."
],
[
20.08,
"A bolinha branca sai do cidadão e chega à interface:"
],
[
22.48,
"é a pergunta, onde tomo vacina da gripe em Taguatinga."
]
],
"arq-02": [
[
0.0,
"A bolinha vai da interface para a API, levando a mensagem, a sessão e o histórico da conversa."
]
],
"arq-03": [
[
0.0,
"Da API ela salta para a caixa amarela, o filtro de segurança, que tem duas partes:"
],
[
4.25,
"regras de palavras e um classificador treinado."
],
[
7.22,
"Na dúvida ou no erro, ele bloqueia."
]
],
"arq-04": [
[
0.0,
"Aprovada, a bolinha fica verde e segue para a caixa laranja."
],
[
3.44,
"O interpretador extrai da frase a intenção, vacina;"
],
[
6.4,
"a região, Taguatinga;"
],
[
7.56,
"e o público, adulto."
],
[
9.22,
"Tudo com regras rápidas, sem chamar nenhum modelo."
]
],
"arq-05": [
[
0.0,
"A bolinha chega ao cache, no canto superior direito."
],
[
2.76,
"Se uma pergunta igual já tivesse sido respondida, a resposta sairia daqui na hora."
],
[
7.28,
"Desta vez não há."
]
],
"arq-06": [
[
0.0,
"Então ela desce para o banco vetorial, logo abaixo."
],
[
2.96,
"A busca é filtrada pelos dados que o interpretador extraiu:"
],
[
6.22,
"tema de vacinas e região de Taguatinga, mais a base geral do Distrito Federal."
]
],
"arq-07": [
[
0.0,
"Com os trechos encontrados, a bolinha atravessa a fileira de baixo até a caixa rosa, o gerador,"
],
[
4.96,
"que escreve a resposta com as citações oficiais."
]
],
"arq-08": [
[
0.0,
"A bolinha sobe do gerador de volta para a API, e a resposta é guardada no cache para a próxima vez."
]
],
"arq-09": [
[
0.0,
"Da API, a bolinha desce para a caixa cinza:"
],
[
2.84,
"a conversa é gravada no banco de sessões, junto com o cadastro do cidadão."
]
],
"arq-10": [
[
0.0,
"E finalmente volta para a interface, onde o texto aparece aos poucos,"
],
[
3.8,
"com as fontes e as opções para clicar."
]
],
"arq-11": [
[
0.0,
"Segundo cenário:"
],
[
1.08,
"e quando o banco local não tem a resposta?"
],
[
3.34,
"A bolinha roxa sai do banco vetorial para a busca online,"
],
[
6.0,
"que só consulta páginas oficiais de saúde e do governo, e recusa qualquer endereço interno."
]
],
"arq-12": [
[
0.0,
"O conteúdo encontrado segue para a caixa verde da ingestão, que roda em segundo plano,"
],
[
4.42,
"confere a conexão segura e evita gravar o mesmo conteúdo duas vezes."
]
],
"arq-13": [
[
0.0,
"A bolinha verde volta para o banco vetorial:"
],
[
1.95,
"o conhecimento novo passa a fazer parte da base, e o cache esquece as respostas antigas de não encontrei."
]
],
"arq-14": [
[
0.0,
"Terceiro cenário, uma pergunta clínica."
],
[
2.02,
"A bolinha vermelha vai da API ao filtro de segurança e para ali."
]
],
"arq-15": [
[
0.0,
"Ela volta para a API com a resposta padrão:"
],
[
2.3,
"a assistente não faz diagnóstico nem prescreve remédios,"
],
[
5.14,
"e orienta procurar a unidade de saúde mais próxima."
]
],
"build-01": [
[
0.0,
"Esta cena acompanha o guia de instalação e testes da segunda versão."
],
[
3.8,
"À esquerda, três colunas ainda achatadas:"
],
[
5.69,
"backend, frontend e Ollama."
],
[
8.02,
"À direita, nove pilhas de blocos cinzas, uma para cada arquivo de testes,"
],
[
11.86,
"com a quantidade escrita em cima."
],
[
13.82,
"Antes de tudo, os requisitos:"
],
[
15.64,
"Python, Node, o gerenciador de pacotes e o Git."
]
],
"build-02": [
[
0.0,
"A coluna verde sobe:"
],
[
1.22,
"é o backend."
],
[
2.1,
"O guia manda criar o ambiente Python, instalar as dependências,"
],
[
5.36,
"copiar o arquivo de configuração e iniciar o servidor na porta oito mil."
]
],
"build-03": [
[
0.0,
"Agora sobe a coluna azul, o frontend:"
],
[
2.24,
"instalar os pacotes e iniciar em modo de desenvolvimento, na porta três mil."
]
],
"build-04": [
[
0.0,
"A terceira coluna, rosa, é o Ollama."
],
[
2.32,
"Segundo o guia ele é opcional, porque o backend consegue responder mesmo sem ele."
]
],
"build-05": [
[
0.0,
"Olhe para a direita:"
],
[
0.98,
"os blocos vão ficando verdes, pilha por pilha, enquanto os testes rodam."
],
[
4.7,
"São oitenta e um ao todo, cobrindo cadastro, interpretação de linguagem, conversas de várias mensagens,"
],
[
10.09,
"busca online, concorrência, ingestão, respostas, busca vetorial e citações."
]
],
"build-06": [
[
0.0,
"Quatro pilhas estão pulsando:"
],
[
1.56,
"são as maiores."
],
[
2.7,
"A mais alta, com dezesseis testes, cobre as respostas e as citações."
],
[
7.0,
"Depois vêm a da busca vetorial, com doze, e as de interpretação de linguagem e de ingestão, com dez cada."
]
],
"build-07": [
[
0.0,
"Por fim, as dicas para problemas comuns:"
],
[
2.52,
"se a porta estiver ocupada, encerrar o processo antigo;"
],
[
5.72,
"se o banco vetorial acusar bloqueio, garantir que só um backend esteja aberto;"
],
[
9.72,
"e se a tela ficar estranha, apagar a pasta temporária do frontend."
]
],
"mlopsm-01": [
[
0.0,
"Esta cena resume o documento de operações e modelagem da segunda versão."
],
[
4.1,
"São três fileiras de caixas."
],
[
5.78,
"A de cima, azul clara, é o caminho dos dados."
],
[
8.76,
"A do meio, amarela, é o treino do filtro de segurança."
],
[
11.76,
"A de baixo, roxa, é a avaliação."
],
[
13.94,
"Comece pela de cima:"
],
[
15.16,
"a bolinha vai da coleta oficial até o diretório de saúde,"
],
[
18.3,
"que mapeia trezentas e quarenta e seis unidades nas trinta e três regiões administrativas."
]
],
"mlopsm-02": [
[
0.0,
"A bolinha segue para a terceira caixa."
],
[
1.98,
"Cada unidade é dividida em trechos, e cada trecho recebe etiquetas:"
],
[
5.72,
"região, tema, tipo de unidade, serviços e horário."
]
],
"mlopsm-03": [
[
0.0,
"No fim da fileira, os trechos entram no banco vetorial:"
],
[
2.39,
"dois mil trezentos e sessenta e cinco blocos."
]
],
"mlopsm-04": [
[
0.0,
"Agora a fileira do meio."
],
[
1.34,
"A bolinha sai do conjunto de frases rotuladas e vai para a validação cruzada em cinco partes,"
],
[
6.34,
"que treina e testa cinco vezes, cada vez com uma fatia diferente."
]
],
"mlopsm-05": [
[
0.0,
"A bolinha laranja chega à caixa laranja, o portão de promoção."
],
[
3.28,
"Um modelo novo só assume se não for pior que o atual e se barrar pelo menos noventa e cinco por cento das perguntas clínicas."
]
],
"mlopsm-06": [
[
0.0,
"Passando pelo portão, vem a calibração,"
],
[
2.36,
"que ajusta as probabilidades para que sessenta por cento signifique mesmo sessenta por cento de confiança."
]
],
"mlopsm-07": [
[
0.0,
"A bolinha verde chega à caixa verde:"
],
[
1.82,
"o modelo aprovado é salvo e passa a ser usado."
]
],
"mlopsm-08": [
[
0.0,
"Fileira de baixo."
],
[
1.02,
"A bolinha sai das partições congeladas,"
],
[
3.4,
"que são conjuntos de perguntas separados e nunca usados para ajustar o sistema,"
],
[
7.44,
"e vai para o programa de avaliação."
]
],
"mlopsm-09": [
[
0.0,
"Os resultados informados no documento:"
],
[
2.18,
"o trecho certo aparece em primeiro lugar em noventa e cinco por cento dos casos,"
],
[
6.62,
"nenhuma pergunta fora do assunto é aceita, e a busca responde em poucas dezenas de milissegundos."
]
],
"mlopsm-10": [
[
0.0,
"A última caixa, azul, é o registro de experimentos,"
],
[
2.84,
"onde ficam guardados os parâmetros e as medidas de cada rodada."
]
],
"mlopsm-11": [
[
0.0,
"A caixa do banco vetorial, lá em cima à direita, está pulsando."
],
[
3.88,
"Ela lembra a ingestão contínua:"
],
[
5.64,
"conteúdo novo entra sem reiniciar o sistema, páginas atualizadas substituem as antigas,"
],
[
10.46,
"e o cache descarta só as respostas de não encontrei."
]
],
"analysis-01": [
[
0.0,
"Esta cena resume o documento original da análise exploratória."
],
[
3.3,
"O gráfico mostra doze pontos azuis, um para cada mês de dois mil e vinte e dois,"
],
[
7.94,
"com os chamados do SAMU no eixo de baixo e os óbitos no eixo lateral."
],
[
11.7,
"O documento compara dois jeitos de agrupar os dados, e agrupar por mês é o mais limpo."
],
[
16.18,
"Os pontos são ilustrativos."
]
],
"analysis-02": [
[
0.0,
"Repare nos dois pontos laranjas pulsando lá no alto."
],
[
2.84,
"A correlação linear é moderada, zero vírgula sessenta, mas a que considera só a ordem dos meses é fraca,"
],
[
8.43,
"zero vírgula vinte e nove."
],
[
10.1,
"Os picos de chamados acompanham os óbitos em volume, mas a ordem dos meses mais intensos não é a mesma."
]
],
"analysis-03": [
[
0.0,
"Os pontos se movem e se alinham à linha amarela."
],
[
2.72,
"Agora são atendimentos ambulatoriais contra cirurgias."
],
[
5.66,
"As duas medidas são altas:"
],
[
7.26,
"meses com mais consultas geram mais cirurgias, como um funil."
]
],
"analysis-04": [
[
0.0,
"O gráfico dá lugar às regiões."
],
[
1.8,
"À esquerda, as caixas azuis das regiões de saúde, que vêm da base de óbitos."
],
[
6.3,
"À direita, uma só caixa rosa:"
],
[
8.3,
"o SAMU registra tudo em uma única região."
],
[
10.54,
"O aviso no centro mostra o resultado:"
],
[
12.17,
"cruzamento vazio e erro no cálculo."
]
],
"analysis-05": [
[
0.0,
"A caixa rosa se desdobra em sete, e as linhas verdes ligam cada uma à sua região."
],
[
4.46,
"É a primeira solução:"
],
[
5.8,
"abandonar a coluna de região e deduzi-la pelo nome do estabelecimento."
]
],
"analysis-06": [
[
0.0,
"A segunda solução é calcular a taxa por cem mil habitantes, usando a população de cada região,"
],
[
5.16,
"para que as regiões mais populosas não dominem os gráficos."
]
],
"refin-01": [
[
0.0,
"Esta cena mostra o plano de refinamento feito depois do primeiro teste de qualidade."
],
[
4.22,
"Em cima, cinco caixas vermelhas pulsando:"
],
[
6.8,
"os problemas encontrados."
],
[
8.36,
"Embaixo, cinco caixas verdes:"
],
[
10.3,
"a ação planejada para cada um."
],
[
12.04,
"O sistema estava funcionando, mas precisava melhorar na busca,"
],
[
15.34,
"na fidelidade às fontes e no contexto da conversa."
]
],
"refin-02": [
[
0.0,
"A bolinha desce da primeira caixa vermelha para a verde logo abaixo."
],
[
3.24,
"O problema:"
],
[
3.94,
"o modelo juntou dois endereços diferentes do mesmo hospital."
],
[
7.08,
"A ação:"
],
[
7.84,
"instruir o modelo a avisar da inconsistência e citar as duas fontes."
]
],
"refin-03": [
[
0.0,
"Segunda coluna."
],
[
1.04,
"A pergunta, onde posso tomar vacina, trouxe o calendário de vacinação, e não as unidades."
],
[
6.12,
"A ação é combinar busca por significado com busca por palavras,"
],
[
9.3,
"e dar prioridade a unidades de saúde quando a pergunta tem onde ou perto."
]
],
"refin-04": [
[
0.0,
"Terceira coluna."
],
[
0.98,
"A pergunta, qual a unidade de pronto atendimento mais perto de mim, gerava um erro genérico."
],
[
5.64,
"A ação:"
],
[
6.3,
"explicar que o sistema não vê a localização e pedir a região administrativa."
]
],
"refin-05": [
[
0.0,
"Quarta coluna."
],
[
0.92,
"A assistente explicou como uma doença é transmitida, o que é saúde em geral, e não um serviço."
],
[
6.1,
"A decisão foi restringir o escopo e bloquear perguntas enciclopédicas."
]
],
"refin-06": [
[
0.0,
"Quinta coluna."
],
[
0.86,
"Dez perguntas de teste eram muito pouco."
],
[
2.92,
"A ação:"
],
[
3.64,
"ampliar para quarenta, divididas em cinco categorias,"
],
[
6.84,
"com medidas de acerto da busca e de fidelidade da resposta."
]
],
"refin-07": [
[
0.0,
"Duas caixas verdes pulsam:"
],
[
1.58,
"a primeira e a terceira."
],
[
2.88,
"São os próximos passos sugeridos, por serem ajustes rápidos que não exigem refazer o índice."
]
],
"planrel-01": [
[
0.0,
"Esta cena mostra o plano do relatório técnico."
],
[
2.38,
"As cinco caixas azuis de cima são as seções do relatório, em ordem."
],
[
6.1,
"As seis de baixo são os assuntos das duas seções centrais:"
],
[
9.46,
"três azuis claras sobre dados e três rosas sobre modelos."
],
[
12.86,
"A primeira caixa está pulsando:"
],
[
14.4,
"é a introdução, que apresenta a assistente e o desafio de informar sem inventar conteúdo clínico."
]
],
"planrel-02": [
[
0.0,
"A bolinha vai da introdução para a segunda seção, sobre a preparação dos dados."
]
],
"planrel-03": [
[
0.0,
"Ela desce para o primeiro assunto:"
],
[
1.74,
"coleta e limpeza, ou seja, como os dados brutos foram filtrados."
]
],
"planrel-04": [
[
0.0,
"Depois desce para o segundo:"
],
[
1.46,
"a divisão dos textos em trechos e a geração dos vetores."
]
],
"planrel-05": [
[
0.0,
"E para o terceiro:"
],
[
1.08,
"o banco vetorial local, onde a busca por significado acontece."
]
],
"planrel-06": [
[
0.0,
"A bolinha avança na fileira de cima para a terceira seção, sobre a abordagem de inteligência artificial."
]
],
"planrel-07": [
[
0.0,
"Desce para a primeira caixa rosa:"
],
[
1.78,
"o modelo de linguagem local, escolhido para manter os dados na própria máquina."
]
],
"planrel-08": [
[
0.0,
"Depois para a segunda:"
],
[
1.2,
"o classificador clínico, mais rápido que um modelo de linguagem para moderar as perguntas."
]
],
"planrel-09": [
[
0.0,
"E para a terceira:"
],
[
1.06,
"o roteador de intenções,"
],
[
2.62,
"que usa regras simples para encaminhar perguntas vagas sem gastar tempo do modelo."
]
],
"planrel-10": [
[
0.0,
"De volta à fileira de cima, a bolinha chega à quarta seção:"
],
[
3.2,
"como as instruções dadas ao modelo garantem que ele não invente fatos e cite as fontes."
]
],
"planrel-11": [
[
0.0,
"E termina na quinta seção, a conclusão, com os próximos passos."
]
],
"planrel-12": [
[
0.0,
"O plano fecha com perguntas para confirmar antes de escrever:"
],
[
3.0,
"qual modelo de vetores, qual modelo de linguagem, qual algoritmo do classificador,"
],
[
8.2,
"se houve balanceamento dos dados e se o relatório deve trazer trechos de código."
]
],
"prod-01": [
[
0.0,
"Esta cena mostra o plano para levar a assistente a produto."
],
[
2.86,
"São nove caixas, da fase zero à fase oito, ligadas pelas dependências."
],
[
7.16,
"As cores indicam o andamento na época do plano:"
],
[
9.66,
"amarelo é parcial, azul é em progresso e cinza é pendente."
],
[
13.22,
"A fase zero, à esquerda, está pulsando:"
],
[
15.74,
"é o ponto de partida."
]
],
"prod-02": [
[
0.0,
"A bolinha sai da fase zero para a fase um."
],
[
3.08,
"A fase zero define o contrato do produto e mede o estado inicial,"
],
[
5.7,
"alinhando documentos antigos à arquitetura real."
]
],
"prod-03": [
[
0.0,
"Da fase um para a dois."
],
[
1.54,
"A fase um cuida da base de textos:"
],
[
3.58,
"inventário, validação por formato e data de cada informação,"
],
[
6.96,
"para que uma leitura errada não vire um fato falso."
]
],
"prod-04": [
[
0.0,
"Da fase dois para a três."
],
[
1.64,
"A fase dois é o índice e a busca."
],
[
4.04,
"Em um subconjunto os resultados foram muito bons, mas o índice completo,"
],
[
8.08,
"com cerca de cento e seis mil blocos, ainda não tinha sido construído."
]
],
"prod-05": [
[
0.0,
"Da fase três para a quatro."
],
[
1.6,
"A fase três, em azul, trata do modelo de linguagem e do filtro de segurança."
],
[
6.04,
"No teste rápido, a pergunta clínica foi bloqueada antes do modelo, mas pelo conjunto de regras,"
],
[
11.26,
"porque o classificador não foi encontrado."
]
],
"prod-06": [
[
0.0,
"Da fase quatro para a cinco."
],
[
1.66,
"A fase quatro unifica as duas rotas de chat e padroniza as citações."
]
],
"prod-07": [
[
0.0,
"A fase cinco pulsa sozinha:"
],
[
1.68,
"é a interface, com endereço configurável, leitura correta do fluxo e acessibilidade."
]
],
"prod-08": [
[
0.0,
"Agora a bolinha desce da fase três para a seis, a caixa amarela de baixo:"
],
[
4.32,
"avaliação e integração contínua, com centenas de casos de teste rotulados."
]
],
"prod-09": [
[
0.0,
"Da seis para a sete:"
],
[
1.2,
"desempenho e resiliência."
],
[
2.7,
"Medir o tempo de partida, fazer cópias de segurança e simular falhas."
]
],
"prod-10": [
[
0.0,
"E da sete para a oito, a última:"
],
[
1.92,
"empacotar, documentar a operação e rodar um piloto controlado."
]
],
"prod-11": [
[
0.0,
"Todas as caixas acendem juntas para lembrar os critérios de aprovação:"
],
[
3.98,
"todos os casos clínicos críticos bloqueados antes do modelo, busca com alto acerto,"
],
[
9.02,
"toda resposta com fonte real e tempo de resposta dentro do limite."
]
],
"prod-12": [
[
0.0,
"E continuam acesas para os riscos que impedem o lançamento:"
],
[
3.14,
"resposta clínica não bloqueada, dado atribuído à unidade errada, citação inexistente,"
],
[
7.57,
"ou o sistema dizendo que está saudável sem o modelo carregado."
]
],
"relatorio-01": [
[
0.0,
"Esta cena resume o relatório técnico."
],
[
2.1,
"À esquerda, três pares de barras comparam algoritmos para o filtro de segurança."
],
[
6.18,
"À direita, quatro placas formam a matriz de confusão,"
],
[
9.46,
"que mostra os acertos e os erros do modelo escolhido."
],
[
12.12,
"O desafio central do relatório é separar o que é informação administrativa do que é clínica."
]
],
"relatorio-02": [
[
0.0,
"Antes da busca existe um roteador de intenções, feito de regras simples."
],
[
3.61,
"Ele separa mensagens muito curtas, perguntas vagas que pedem esclarecimento, pedidos como explique melhor,"
],
[
9.74,
"que dependem da conversa anterior, e dúvidas específicas, que seguem para o banco vetorial."
]
],
"relatorio-03": [
[
0.0,
"Olhe para as barras."
],
[
1.26,
"O primeiro par, da regressão logística, está pulsando."
],
[
4.3,
"A barra rosa é a proporção de perguntas clínicas barradas, e a azul é a nota geral."
],
[
9.04,
"Ela ficou com oitenta e quatro por cento nas duas, acima dos outros dois algoritmos."
]
],
"relatorio-04": [
[
0.0,
"Agora as quatro placas da direita acendem."
],
[
2.36,
"Na prova com quinze exemplos separados, sete administrativas foram liberadas e quatro clínicas bloqueadas,"
],
[
8.38,
"que são as placas verdes."
],
[
9.84,
"Houve um bloqueio indevido, na placa amarela, e três perguntas clínicas que passaram, na vermelha."
]
],
"relatorio-05": [
[
0.0,
"Só a placa vermelha pulsa."
],
[
1.38,
"São os erros mais perigosos:"
],
[
2.55,
"frases como, posso tomar um remédio junto com outro, que usam palavras que o modelo nunca viu no treino."
],
[
8.96,
"O relatório propõe treinar com todos os dados e manter as regras de palavras como reforço."
]
],
"relatorio-06": [
[
0.0,
"Agora a placa amarela."
],
[
1.36,
"É uma pergunta administrativa sobre documentos para retirar remédio,"
],
[
4.9,
"bloqueada por causa da palavra remédio."
],
[
7.14,
"A regra de palavras administrativas corrige esse caso."
]
],
"relatorio-07": [
[
0.0,
"Para fechar, a geração:"
],
[
1.66,
"o modelo de linguagem roda localmente, cita os trechos numerados quando informa dados críticos,"
],
[
6.78,
"e só pode usar conhecimento geral para explicar conceitos básicos."
]
]
};
