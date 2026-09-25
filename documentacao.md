# Documentação do projeto — SUSANNA-HEALTHCHECK

> **Demonstração pela internet:** modo temporário autenticado disponível; veja [como iniciar e encerrar](docs/internet-demo.md). A configuração local continua disponível.
>
> **Guias atuais:** [instalação, uso e manutenção](docs/guia-projeto.md),
> [privacidade](docs/privacidade.md), [componentes](docs/componentes.md) e
> [responsabilidades](docs/responsabilidades.md). Os registros históricos abaixo
> descrevem o estado de cada etapa e podem conter limitações já resolvidas.

Abra **dois terminais**.

## 1. Primeiro terminal: iniciar o Ollama

Se ainda não estiver instalado, instale pelo [site oficial](https://ollama.com/download). Depois execute:

```bash
ollama serve
```

Deixe esse terminal aberto. Se aparecer que a porta `11434` já está em uso, o Ollama pode já estar rodando pelo aplicativo.

## 2. Segundo terminal: baixar o modelo

```bash
ollama pull qwen2.5:7b
```

O download só é necessário na primeira vez. Para testar a LLM diretamente:

```bash
ollama run qwen2.5:7b
```

Digite uma pergunta. Para sair da conversa, use `/bye`.

## 3. Iniciar o servidor do projeto

No segundo terminal:

```bash
cd /Users/aluno2/Desktop/saude-gov-br
python3 server.py
```

O projeto atual não precisa de instalação de pacotes com `pip`.

## 4. Abrir o chatbot

Acesse: [http://127.0.0.1:8002](http://127.0.0.1:8002)

Para conferir a conexão entre o servidor e a LLM, abra: [http://127.0.0.1:8002/api/health](http://127.0.0.1:8002/api/health). O resultado esperado inclui `"ready": true`.

Se a porta `8002` estiver ocupada:

```bash
python3 server.py --port 8003
```

Nesse caso, acesse [http://127.0.0.1:8003](http://127.0.0.1:8003).

**Nas próximas vezes:** basta garantir que o Ollama esteja aberto e executar `python3 server.py`. Para parar o servidor, pressione `Ctrl+C` no terminal correspondente.

====================================

DETALHES DO PASSO A PASSO, TOPICO A TOPICO DO PROJETO

## Plano do projeto — Chatbot educativo sobre desinformação em saúde

**Objetivo:** desenvolver um chatbot com componentes open source, capaz de consultar uma base de fontes confiáveis, apresentar referências e reconhecer quando não houver evidências suficientes.

1. **Definir o escopo**
   - Estabelecer público-alvo, dúvidas atendidas e funcionalidades.
   - Definir limites: uso educativo, sem diagnóstico ou prescrição.
   - Distribuir responsabilidades entre desenvolvimento, conteúdo e testes.

2. **Levantar os requisitos**
   - Identificar hardware disponível e quantidade esperada de usuários simultâneos.
   - Definir onde o sistema será executado e disponibilizado.
   - Estabelecer critérios de qualidade, tempo de resposta e privacidade.

3. **Organizar a base atual**
   - Revisar o código existente e organizar configurações.
   - Documentar instalação, versões e licenças dos componentes.
   - Definir o fluxo de colaboração e revisão de código no Git.

4. **Selecionar as fontes confiáveis**
   - Escolher documentos de instituições como Ministério da Saúde, Fiocruz e OMS.
   - Definir critérios de inclusão, atualização e revisão dos conteúdos.
   - Registrar origem, título, URL, data e condições de uso.

5. **Construir a base de conhecimento**
   - Extrair e organizar o conteúdo dos documentos.
   - Dividir os textos em trechos pesquisáveis.
   - Criar um índice local, preservando as referências de cada trecho.

6. **Implementar a busca com evidências — RAG**
   - Recuperar os trechos relevantes para cada pergunta.
   - Fornecer esses trechos ao modelo para fundamentar as respostas.
   - Apresentar as fontes utilizadas e indicar quando a evidência for insuficiente.

7. **Aprimorar o comportamento do chatbot**
   - Padronizar respostas claras em português.
   - Separar alegações, evidências e pontos que ainda precisam de verificação.
   - Ajustar o histórico ao limite de contexto do modelo.
   - Tratar instruções maliciosas presentes em mensagens ou documentos.

8. **Melhorar desempenho e experiência**
   - Exibir a resposta progressivamente.
   - Implementar cancelamento, controle de concorrência e tratamento de falhas.
   - Ajustar o modelo ao hardware disponível.
   - Revisar acessibilidade, uso em celular e apresentação das referências.

9. **Testar e avaliar**
   - Criar um conjunto de perguntas com respostas e fontes esperadas.
   - Testar afirmações falsas, ambíguas, desatualizadas e fora do escopo.
   - Avaliar fidelidade às fontes, referências e reconhecimento de incerteza.
   - Medir velocidade, consumo de memória e comportamento com acessos simultâneos.

10. **Preparar a disponibilização**
    - Configurar o ambiente de execução e um servidor adequado.
    - Definir acesso, proteção das conexões e limites de uso.
    - Documentar o tratamento de dados e configurar métricas operacionais.
    - Preparar atualização e recuperação da base documental.

11. **Realizar um piloto com a equipe**
    - Disponibilizar uma versão para um grupo pequeno.
    - Coletar avaliações e registrar problemas.
    - Corrigir os pontos encontrados e validar os critérios de entrega.

12. **Entregar e manter**
    - Publicar a versão aprovada e os guias de uso e instalação.
    - Apresentar resultados dos testes e limitações conhecidas.
    - Definir responsáveis pela manutenção.
    - Atualizar fontes e componentes e repetir as avaliações periodicamente.

**Entregáveis:** chatbot funcional, base documental rastreável, código versionado, documentação técnica, guia de uso e relatório de avaliação.

=============================================

## Atualização do projeto — primeira versão da base documental do chatbot

Registro histórico da primeira versão. Para o funcionamento atual, consulte
[busca e continuidade](docs/busca-conversa.md) e [desempenho e experiência](docs/desempenho-experiencia.md).

Implementamos a estrutura inicial para o chatbot consultar documentos locais antes de responder. Essa abordagem é chamada de **RAG**, ou geração aumentada por recuperação: o sistema procura informações na base e entrega os trechos encontrados à LLM para apoiar a resposta.

A implementação continua usando **Python, SQLite e Ollama**, sem API paga e sem novos pacotes `pip`. O Python precisa ter suporte à extensão FTS5 do SQLite.

### 1. Criamos o módulo de base documental: `knowledge.py`

Esse arquivo permite importar documentos revisados pela equipe para uma base local.

Cada documento deve ser fornecido em um arquivo JSON com quatro campos:

- `title`: título do documento.
- `url`: endereço da fonte original.
- `reviewed_at`: data em que a equipe revisou o conteúdo.
- `text`: texto que será disponibilizado ao chatbot.

A importação verifica campos obrigatórios, formato da data e endereço HTTPS. Também rejeita datas de revisão futuras e URLs com credenciais.

O sistema **não baixa o conteúdo da URL**. Nesta versão, a equipe precisa selecionar, revisar e inserir o texto no arquivo.

O comando de importação é:

```bash
python3 knowledge.py /caminho/para/documento.json
```

### 2. Implementamos armazenamento e divisão dos documentos

Os documentos importados são divididos em trechos de até **1.200 caracteres**, sem cortar palavras.

Esses trechos são armazenados em:

```text
data/knowledge.sqlite3
```

Cada trecho mantém o título, a URL e a data de revisão do documento original.

Se um documento for importado novamente com a mesma URL, seus trechos anteriores serão substituídos em uma transação. Isso permite atualizar o conteúdo sem acumular versões duplicadas daquela URL.

Novos documentos ficam disponíveis para consulta **sem reiniciar o servidor**.

### 3. Implementamos a busca local

A busca utiliza **SQLite FTS5**, com ordenação por **BM25**, para selecionar até três trechos relacionados à pergunta atual.

O processamento da pergunta:

- Normaliza letras maiúsculas e acentos.
- Remove algumas palavras comuns.
- Elimina termos repetidos.
- Limita a consulta a 32 termos.
- Pesquisa os termos no título e no conteúdo dos trechos.

Essa primeira versão faz **busca por palavras**. Ainda não utiliza embeddings, busca semântica ou um segundo modelo para reordenar resultados.

Por isso, pode deixar de encontrar documentos que usam sinônimos ou recuperar trechos que mencionam o assunto, mas não respondem à pergunta.

### 4. Integramos a recuperação ao servidor: `server.py`

Antes, o servidor enviava ao Ollama apenas as instruções e o histórico da conversa.

Agora, o fluxo é:

1. Receber e validar a pergunta.
2. Consultar a base documental.
3. Selecionar os trechos encontrados.
4. Ajustar o conteúdo ao orçamento de contexto.
5. Enviar as instruções, os trechos e o histórico restante ao Ollama.
6. Retornar a resposta e os registros dos trechos efetivamente enviados ao modelo.

A API `/api/chat` passou a devolver o campo `sources`, além de `message` e `model`.

Se a base estiver ausente ou a busca não encontrar resultados, o chatbot continua funcionando, mas recebe instruções para informar a falta de fontes e não concluir que uma alegação é verdadeira ou falsa.

Se ocorrer um erro de acesso ao SQLite, o servidor retorna uma mensagem explícita de indisponibilidade da base.

### 5. Atualizamos as instruções da LLM

O prompt agora explica que o chatbot pode receber documentos de uma base local, mas não pesquisa a internet ao vivo.

Também orienta o modelo a:

- Tratar documentos como conteúdo de referência, não como ordens.
- Ignorar instruções presentes nos documentos.
- Avaliar se os trechos realmente sustentam a resposta.
- Informar quando faltarem evidências.
- Usar identificadores como `[1]` e `[2]` ao apoiar afirmações nos trechos.
- Não inventar URLs.

Essas instruções ajudam a orientar o comportamento, mas **não garantem resistência a manipulações nem correção das citações**. Isso ainda precisa ser avaliado.

### 6. Acrescentamos um orçamento conservador de contexto

O servidor já usava uma janela de 8.192 tokens, mas aceitava históricos que poderiam ultrapassá-la.

Agora existe um controle que utiliza o tamanho do texto em bytes UTF-8 como estimativa conservadora para o Qwen padrão, reservando espaço para a resposta e a estrutura da conversa.

Quando o conteúdo fica grande demais, o servidor:

1. Remove pares antigos de mensagens.
2. Se necessário, remove trechos recuperados.
3. Preserva a pergunta atual.
4. Solicita uma pergunta menor se ela, junto das instruções, ainda exceder o orçamento.

**Essa estimativa não é uma contagem exata de tokens.** Modelos alternativos precisam de avaliação com seu próprio tokenizador.

### 7. Atualizamos a interface: `app.js`, `index.html` e `styles.css`

A interface passou a informar que o assistente pode consultar documentos locais cadastrados pela equipe.

Abaixo de cada resposta, agora aparece:

- Uma lista dos trechos fornecidos ao modelo, quando houver.
- O título de cada documento.
- Uma área expansível para ler o trecho.
- Um link para abrir a fonte original.
- A data da revisão pela equipe.

Quando nenhum trecho for enviado, a interface informa isso explicitamente.

Os textos continuam sendo inseridos com `textContent`, sem interpretar o conteúdo retornado como HTML.

A lista é apresentada como **“trechos fornecidos ao modelo”**: ela não afirma que todas as fontes sustentam todas as conclusões da resposta.

### 8. Atualizamos a documentação e o controle de arquivos

Criamos:

- `docs/base-documental.md`: instruções de cadastro, funcionamento, limitações e testes.
- `tests/test_knowledge.py`: testes automatizados da nova implementação.

Atualizamos:

- `README.md`: funcionamento da base, ajuste do histórico e instruções de reinício.
- `.gitignore`: exclusão do banco SQLite e seus arquivos auxiliares do versionamento.

O arquivo `documentacao.dm`, que já continha os comandos de execução, foi preservado.

### 9. Executamos os testes

Os **10 testes automatizados passaram**, cobrindo:

1. Base ausente, sem criação automática de arquivo.
2. Busca com acentos e consultas sem resultados.
3. Atualização de documento pela mesma URL.
4. Preservação do conteúdo anterior quando uma importação é inválida.
5. Rejeição de URL insegura.
6. Tratamento de operadores de busca como texto.
7. Divisão dos documentos, preservação do conteúdo e limite de resultados.
8. Redução de histórico grande, mantendo a pergunta atual.
9. Rejeição de pergunta que excede o orçamento.
10. Integração da API com os trechos enviados ao modelo, usando uma resposta simulada da LLM.

Também fizemos uma chamada real ao Ollama usando um servidor temporário local. Ela retornou **HTTP 200**, uma resposta do `qwen2.5:7b` e a lista de fontes vazia, conforme o estado atual da base.

A interface ainda não passou por validação visual no navegador nesta etapa. A checagem de sintaxe JavaScript pelo Node não pôde ser executada porque o Node não estava disponível no ambiente.

### 10. O que ainda não está concluído

A estrutura está implementada, mas **a base real ainda está vazia**. Os testes usaram documentos sintéticos temporários, que não foram adicionados à base do chatbot.

Ainda precisamos:

- Selecionar e revisar as primeiras fontes oficiais.
- Registrar condições de uso, datas de publicação e versões dos documentos.
- Avaliar a relevância dos trechos recuperados.
- Verificar se as respostas e citações correspondem às fontes.
- Testar perguntas ambíguas, maliciosas e fora do escopo.
- Avaliar perguntas de continuidade, pois a busca considera apenas a pergunta atual.
- Implementar streaming, cancelamento da geração, controle de concorrência e métricas.
- Preparar e validar o ambiente de disponibilização.

**Próxima etapa:** cadastrar um conjunto inicial de documentos oficiais e criar perguntas de referência para avaliar a recuperação e a fidelidade das respostas antes do piloto com a equipe.

============================

## O que falta para concluir o chatbot

Já temos a interface, integração com Ollama, base documental local, busca de trechos, validação de referências e avaliação automatizada. As etapas restantes são:

1. **Revisar o conteúdo da base**
   - Conferência documental por IA registrada em 24/09/2026: [evidências e registro de revisão por IA](docs/revisao-fontes.md). Status dos seis documentos: Revisado por IA.
   - Conferência documental das seis sínteses realizada por IA.
   - Validar informações, contexto, datas e condições de reutilização.
   - Registrar responsável, data e resultado da revisão por IA.

2. **Ampliar as fontes**
   - Escopo inicial e seis documentos cadastrados: [cobertura e rotina de manutenção](docs/escopo-fontes.md). Documentos revisados por IA; suficiência para o piloto ainda em avaliação.
   - Definir quais temas o chatbot deve atender.
   - Cadastrar documentos suficientes para esses temas.
   - Estabelecer uma rotina para atualizar ou retirar conteúdos desatualizados.

3. **Melhorar a fidelidade das respostas — prioridade principal**
   - Implementada revisão por IA antes da exibição: apoio por parágrafo, evidência literal por citação, abstenção e normalização de referências. Veja [controle de respostas](docs/controle-respostas.md). É uma mitigação, não garantia de fidelidade.
   - Reduzir afirmações que não estão nos documentos.
   - Conferir se cada citação realmente sustenta a afirmação.
   - Melhorar o reconhecimento de evidências insuficientes.
   - Reduzir bloqueios causados apenas por problemas de formato.

4. **Melhorar a busca e a continuidade da conversa**
   - Implementadas expansão controlada de termos, correção conservadora de digitação e remoção de expressões informais comuns.
   - Perguntas reconhecidas, como “e nesse caso?” e “e as reações?”, usam até três perguntas anteriores. Sem antecedente, o chatbot pede esclarecimento.
   - Comparação de 38 casos: busca original 27/38; expansão 36/38; expansão com contexto 38/38. A reordenação adicional não trouxe ganho e permanece desativada por padrão. Embeddings ainda não foram medidos.
   - Veja [implementação, avaliação e limitações](docs/busca-conversa.md). Próximo passo: perguntas independentes e avaliação de conversas completas com a LLM.

5. **Melhorar desempenho e experiência**
   - Implementados estados de progresso e apresentação gradual do texto somente após a validação completa.
   - Cancelar e Limpar removem pedidos da fila ou fecham a conexão com o Ollama durante geração/revisão. Pedidos sem acompanhamento expiram.
   - Implementada fila FIFO limitada: uma execução e três pedidos em espera por padrão, configuráveis. Fila cheia retorna HTTP 429.
   - Medição real no Apple M4 com 24 GiB: respostas em 12,22 s e 16,66 s na rodada registrada; pico amostrado do Python 35,47 MiB e alocação do modelo informada pelo Ollama 5,08 GiB. São medidas distintas, não devem ser somadas.
   - Veja [implementação, reprodução e limites](docs/desempenho-experiencia.md). Verificação visual no navegador e testes prolongados de carga continuam pendentes.

6. **Ampliar os testes**
   - Criados 14 cenários inéditos após desenvolvimento e 5 casos novos do revisor, sem ajustar a busca ou os prompts para esta rodada. Autoria por IA; não equivalem a validação independente por pessoas.
   - Executados 16 turnos pela API HTTP com Ollama real: 5/14 cenários atenderam aos critérios automáticos. Oito foram bloqueados por formato e um por apoio documental; investigar antes do piloto.
   - Revisor isolado: 4/5. Uma resposta contraditória foi aceita quando a fonte continha uma instrução maliciosa ao revisor. Falha registrada como bloqueador do piloto.
   - Preparado [pacote de revisão humana](evaluation/acceptance.human.md) com respostas e fontes; avaliações de duas pessoas permanecem pendentes.
   - Ampliados testes de API e JavaScript e corrigidos acesso por teclado, anúncios de progresso e alvos de toque. Inspeção estática: 10/10 verificações e quatro pares de contraste aprovados no escopo medido, sem certificação de acessibilidade.
   - Navegador real, leitor de tela e celular continuam pendentes por indisponibilidade das ferramentas. Veja [resultados, problemas e roteiro de aceite](docs/aceitacao.md).

7. **Preparar o ambiente de disponibilização**
   - Cenário escolhido: somente neste computador, em `127.0.0.1:8002`, com Ollama local.
   - Proteção de Host/Origin e cabeçalhos de segurança; logs HTTP desativados. Sem exposição à rede.
   - Prontidão conjunta em `/api/ready`, limites e métricas documentados; comando de backup consistente com verificação e roteiro de recuperação.
   - Veja [operação e disponibilização local](docs/disponibilizacao.md). Validação automatizada com bancos temporários; exercício de recuperação completo e aprovação do piloto continuam pendentes.

8. **Consolidar documentação e privacidade**
   - Consolidado o [guia de instalação, uso e manutenção](docs/guia-projeto.md), com operação somente neste computador.
   - Registrados [versões, identificação do modelo e licenças](docs/componentes.md), preservando os créditos existentes.
   - Documentados [dados processados, retenção, relatórios e limites de privacidade](docs/privacidade.md).
   - Definidas [atribuições de código, base documental e operação](docs/responsabilidades.md); responsável confirmado: Guilherme Barros Jacintho Ribeiro.

9. **Executar o piloto e entregar**
   - Preparado [pacote do piloto local](piloto/README.md), com roteiro, feedback, critérios propostos e registro de aceite.
   - Participante e responsável pelo aceite, código, base e operação: Guilherme Barros Jacintho Ribeiro. Demais participantes e revisores ainda não indicados.
   - Pré-piloto: 67 testes passaram; base local corrigida de três para seis fontes, com backup; regressão real do revisor 4/5, reproduzindo F01.
   - Piloto com equipe e publicação final ainda não realizados: bloqueador F01 aberto, feedback e aprovação humana pendentes. Entrega disponível somente como candidata para revisão.

**Ordem recomendada:** revisão das fontes → fidelidade das respostas → testes independentes → desempenho e disponibilização → piloto.

O principal ponto pendente é **a confiabilidade das respostas**: os testes de código passaram, mas isso ainda não significa que o conteúdo esteja aprovado para uso pelo público.

==============================

Seu projeto é o **SUSANNA-HEALTHCHECK**, um chatbot educativo sobre desinformação em saúde. Ele recebe perguntas pelo navegador, consulta documentos armazenados no computador e usa uma IA local para tentar responder com base nesses documentos.

## O fluxo principal é este:

```text
Você escreve uma pergunta
          ↓
JavaScript envia ao servidor Python
          ↓
Python busca trechos na base SQLite
          ↓
IA local elabora uma resposta usando esses trechos
          ↓
Código confere citações e IA revisa o apoio documental
          ↓
Navegador mostra a resposta e as fontes
```

Se não encontrar trechos, o sistema pula a IA e mostra uma mensagem pronta de falta de evidências.

## O papel de cada arquivo:

| Arquivo | Responsabilidade |
| --- | --- |
| `index.html` | Estrutura da página, campo de pergunta e chat. |
| `styles.css` | Cores, tamanhos, posicionamento e adaptação às telas. |
| `app.js` | Envia perguntas, mostra respostas e controla o histórico. |
| `server.py` | Recebe requisições e coordena busca, geração e revisão. |
| `knowledge.py` | Importa documentos e pesquisa na base SQLite. |
| `answer_policy.py` | Confere referências e o resultado da revisão por IA. |
| `sources/` | Documentos JSON disponíveis para importação. |
| `seed_knowledge.py` | Carrega esses documentos no banco. |

## Acompanhando uma pergunta, passo a passo:

1. **Você envia a mensagem.**  
   No [app.js](/Users/aluno2/Desktop/saude-gov-br/app.js), a função `send()` recebe o texto, mostra sua pergunta na tela e cria um pedido com `POST /api/jobs`. Junto, envia até seis pares anteriores de pergunta e resposta. Enquanto espera, acompanha o estado do pedido, desativa os controles de envio e mantém Cancelar e Limpar disponíveis.

2. **O servidor valida a entrada.**  
   No [server.py](/Users/aluno2/Desktop/saude-gov-br/server.py), `validate_messages()` verifica o formato do histórico, a ordem das mensagens e os limites de tamanho. Cada pergunta pode ter até 3.000 caracteres.

3. **O sistema procura documentos relacionados.**  
   A função `retrieve()`, em [knowledge.py](/Users/aluno2/Desktop/saude-gov-br/knowledge.py), pesquisa em `data/knowledge.sqlite3`. Ela remove acentos, desconsidera palavras comuns e busca coincidências em títulos e textos usando SQLite FTS5.

   Retorna **até três trechos**. Essa busca é por palavras, com expansão controlada e correção simples de digitação: não usa embeddings nem pesquisa a internet. Formas reconhecidas de continuidade usam perguntas anteriores por meio de `conversation.py`; o mesmo contexto chega à geração e à revisão.

4. **O Python prepara as instruções para a IA.**  
   `build_prompt()` junta as regras do assistente, os trechos encontrados e a conversa. Se ficar grande demais, remove primeiro mensagens antigas e depois trechos.

   A IA é instruída a responder em português, usar apenas o material fornecido e citar os trechos com números como `[1]`.

5. **O Ollama gera a resposta.**  
   O servidor chama o Ollama local em `127.0.0.1:11434`. O modelo padrão é `qwen2.5:7b`. O Python organiza o trabalho; quem produz o texto é esse modelo.

6. **A resposta passa por verificações.**  
   Primeiro, o código verifica se há citações válidas, se cada parágrafo termina com uma referência e se a IA inventou links.

   Depois, faz **uma segunda chamada ao mesmo modelo**, agora como revisor. Ele avalia se as fontes citadas sustentam a resposta. O código também confere se as evidências textuais apresentadas pelo revisor realmente existem nos documentos.

   Se alguma etapa reprovar, o texto gerado é substituído por uma mensagem de insuficiência de evidências ou falha na validação.

7. **A resposta aparece na tela.**  
   Após a validação completa, o JavaScript apresenta a mensagem progressivamente e mostra os trechos utilizados, com links para as fontes. O usuário pode expandi-los para conferir o conteúdo.

## Alguns detalhes importantes para entender o comportamento atual:

- Os documentos de `sources/` só entram no banco quando você executa `python3 seed_knowledge.py`. Alterar um JSON não atualiza automaticamente o SQLite.
- Esses documentos são sínteses experimentais produzidas por IA, com referências a páginas oficiais; não são cópias integrais dessas páginas.
- O histórico fica na memória do navegador. Recarregar a página ou clicar em limpar apaga a conversa.
- A revisão usa IA e pode errar; passar pelas verificações não comprova que a resposta é verdadeira.
- `tests/` e os scripts `evaluate.py` e `evaluate_grounding.py` servem para testar a recuperação de documentos e as verificações.

Essa explicação descreve o caminho implementado no código. Não executei o chatbot nem os testes nesta leitura.
