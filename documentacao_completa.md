# Documentação consolidada — SUSANNA-HEALTHCHECK

Preparei a etapa 7 para **uso somente neste computador**.

- Proteção de acesso local e cabeçalhos de segurança.
- `/api/ready` para verificar base e modelo.
- Comando de backup com verificação de integridade.
- Guia com limites, métricas e recuperação.
- README e `documentacao.md` atualizados.

**Validação:** 67 testes passaram; a base atual passou na verificação de integridade.

Consulte o [guia de disponibilização local](/Users/aluno2/Desktop/saude-gov-br/docs/disponibilizacao.md). O exercício completo de recuperação e os bloqueadores de qualidade do piloto continuam pendentes.

Consolidei a documentação da etapa 8:

- [Instalação, uso e manutenção](/Users/aluno2/Desktop/saude-gov-br/docs/guia-projeto.md).
- [Versões e licenças](/Users/aluno2/Desktop/saude-gov-br/docs/componentes.md).
- [Privacidade e retenção de dados](/Users/aluno2/Desktop/saude-gov-br/docs/privacidade.md).
- [Responsabilidades por função](/Users/aluno2/Desktop/saude-gov-br/docs/responsabilidades.md).

README e `documentacao.md` atualizados; links locais verificados.

Preparei o [pacote candidato para entrega local](/Users/aluno2/Desktop/saude-gov-br/dist/susanna-candidata-20260925.zip), com roteiro, formulário de feedback, critérios de aceite e manutenção. Registrei Guilherme Barros Jacintho Ribeiro como responsável.

- **67 testes passaram.**
- Base atualizada para seis fontes, com backup.
- Revisor real: **4/5**, reproduzindo a falha de aceitar uma resposta contraditória.

**O piloto e a publicação final continuam pendentes:** é necessário corrigir esse bloqueador e coletar avaliações reais da equipe. Nenhum feedback ou aceite foi preenchido em nome dos participantes.

Sim — você está falando da pasta **`sources/`**. Hoje, as peças se integram assim:

```text
Arquivos JSON em sources/
          ↓ python3 seed_knowledge.py
Base pesquisável SQLite
          ↑
Sua pergunta → busca RAG → trechos relevantes
                                  ↓
                      Pergunta + trechos → Ollama
                                              ↓
                                     Modelo gera resposta
                                              ↓
                                  Código e IA revisam
                                              ↓
                               Resposta + fontes na tela
```

**O RAG é esse processo de buscar informações e entregá-las ao modelo antes de ele responder.** O Ollama executa o modelo de IA; ele não lê automaticamente a pasta `sources/`.

Os arquivos em `sources/` guardam o conteúdo e sua origem. O comando de importação coloca esse conteúdo no banco SQLite. Quando você pergunta, o sistema busca até três trechos relacionados e os fornece ao modelo. Isso **não treina o modelo**: fornece material de consulta para aquela resposta.

Sobre juntar o trabalho da equipe: **se seus amigos têm os conteúdos em arquivos `.md`, podemos transformá-los no mesmo formato JSON usado pelo projeto.** Hoje o importador aceita JSON, não Markdown diretamente.

O caminho seria:

1. Cada pessoa entrega seus documentos `.md`, com título, conteúdo e links das fontes originais.
2. Conferimos duplicidades, contradições e origem das informações.
3. Convertemos os documentos para JSON, preservando os metadados de fonte e revisão.
4. Colocamos os JSONs aprovados na mesma pasta `sources/`.
5. Fazemos backup e executamos `python3 seed_knowledge.py` para atualizar a base compartilhada.

**Não precisamos juntar tudo em um arquivo enorme.** Podemos manter um documento por fonte ou assunto, com nomes diferentes. O RAG procura entre todos os documentos importados.

Um cuidado: arquivos `.md` que explicam instalação, código ou reuniões são documentação do projeto; não devem entrar automaticamente na base de evidências de saúde. Precisamos identificar quais contêm material que o chatbot deve consultar.

Como o sistema está local, cada colega que executar sua própria cópia precisará receber os JSONs e importá-los. Podemos compartilhar esses arquivos pelo Git; o banco SQLite é gerado em cada computador.

**Os `.md` dos seus amigos contêm informações de saúde com fontes ou são documentação dos projetos deles?** Isso define como vamos integrar o material.


==================

1. **Corrigir a revisão das respostas — prioridade máxima**
   - Há uma falha conhecida: o revisor aceitou uma resposta contraditória quando a fonte continha uma instrução maliciosa.
   - Precisamos reforçar a separação entre documentos e instruções e testar novamente.
   - Quando faltar apoio nas fontes, o chatbot deve dizer que não consegue confirmar.

=====================

Implementei a correção:

- Separei os documentos das instruções de sistema.
- Comandos explícitos de manipulação nas fontes agora bloqueiam a geração e a revisão.
- Nesses casos, o chatbot informa que não encontrou evidência suficiente.

**Validação:** 73 testes automatizados, 5/5 casos de regressão e 8/8 casos complementares passaram.

O servidor local já está atualizado: **[abrir chatbot](http://127.0.0.1:8002)**. A sessão antiga do ngrok precisa ser reiniciada para carregar a correção.

Registrei os resultados na documentação. A falha conhecida está bloqueada, mas o filtro não detecta toda manipulação e a IA ainda pode errar.

===================

2. **Melhorar a base de fontes**
   - Hoje existem apenas seis sínteses experimentais, revisadas por IA.
   - Conferir o conteúdo com as publicações originais e ampliar os temas que você quer perguntar.
   - Registrar título, instituição, link e data de revisão de cada fonte.

========================

Ampliei a base de **6 para 12 documentos**, já disponíveis no chatbot.

- Reconferi cinco fontes anteriores e substituí a referência de antibióticos por uma publicação da SBI.
- Acrescentei **gripe, tuberculose, hipertensão, HIV, raiva e SAMU 192**.
- Registrei título, instituição, link, data de revisão e seções consultadas.
- Fiz backup e corrigi uma confusão da busca entre doenças.

**Validação:** 75 testes passaram; busca com continuidade: 38/38. Isso verifica recuperação das fontes, não garante a correção de todas as respostas.

[Consultar fontes e revisão](/Users/aluno2/Desktop/saude-gov-br/docs/revisao-fontes-20260929.md) · [Testar chatbot](http://127.0.0.1:8002)

===================

3. **Garantir que a busca encontre o trecho certo**
   - Testar perguntas informais, erros de digitação e diferentes formas de perguntar.
   - Melhorar perguntas de continuidade, como “e em crianças?”.
   - Pedir esclarecimento quando a pergunta for ambígua.

=====================

Ampliei a base de **6 para 12 documentos**, já disponíveis no chatbot.

- Reconferi cinco fontes anteriores e substituí a referência de antibióticos por uma publicação da SBI.
- Acrescentei **gripe, tuberculose, hipertensão, HIV, raiva e SAMU 192**.
- Registrei título, instituição, link, data de revisão e seções consultadas.
- Fiz backup e corrigi uma confusão da busca entre doenças.

**Validação:** 75 testes passaram; busca com continuidade: 38/38. Isso verifica recuperação das fontes, não garante a correção de todas as respostas.

[Consultar fontes e revisão](/Users/aluno2/Desktop/saude-gov-br/docs/revisao-fontes-20260929.md) · [Testar chatbot](http://127.0.0.1:8002)

=======================

4. **Exibir fontes que realmente sustentem a resposta**
   - Vincular as afirmações aos trechos utilizados.
   - Mostrar título e link da publicação.
   - Não tratar a presença de uma referência como prova de que a resposta está correta.

========================

Ampliei a base de **6 para 12 documentos**, já disponíveis no chatbot.

- Reconferi cinco fontes anteriores e substituí a referência de antibióticos por uma publicação da SBI.
- Acrescentei **gripe, tuberculose, hipertensão, HIV, raiva e SAMU 192**.
- Registrei título, instituição, link, data de revisão e seções consultadas.
- Fiz backup e corrigi uma confusão da busca entre doenças.

**Validação:** 75 testes passaram; busca com continuidade: 38/38. Isso verifica recuperação das fontes, não garante a correção de todas as respostas.

[Consultar fontes e revisão](/Users/aluno2/Desktop/saude-gov-br/docs/revisao-fontes-20260929.md) · [Testar chatbot](http://127.0.0.1:8002)

======================

Entendi a estrutura atual da branch **`develop_gui`** e já consigo continuar com você sem reconstruir o projeto do zero. Vou sempre considerar essa branch como nossa referência. 

O fluxo principal hoje é este:

```text
USUÁRIO
  ↓
index.html
  ↓
app.js
  ↓
POST /api/jobs
  ↓
server.py
  ↓
conversation.py
  ↓
knowledge.py
  ↓
SQLite FTS5 / base documental
  ↓
sources/*.json
  ↓
server.py monta o prompt
  ↓
ollama_transport.py
  ↓
Ollama
  ↓
qwen2.5:7b
  ↓
answer_policy.py
  ↓
segunda revisão / grounding
  ↓
server.py
  ↓
jobs.py
  ↓
app.js consulta o resultado
  ↓
RESPOSTA + FONTES NA INTERFACE
```

### O que cada parte faz

`index.html` é a interface principal. É a página visual inspirada no Meu SUS Digital, com área educativa, chatbot, sugestões de perguntas e avisos de que é um protótipo acadêmico.

`styles.css` cuida exclusivamente da aparência.

`app.js` controla o chatbot no navegador. Quando você envia uma pergunta, ele não chama diretamente o Ollama. Ele cria um pedido em:

```text
POST /api/jobs
```

Depois fica consultando:

```text
GET /api/jobs/<id>
```

e mostra etapas como:

```text
Consultando as fontes locais…
Preparando a resposta…
Conferindo a resposta nas fontes…
```

Também permite cancelar o processamento.

---

### O `server.py` é o coração do sistema

É nele que praticamente todo o fluxo se conecta.

Ele recebe a pergunta, valida o histórico da conversa e chama a busca da base documental.

Depois prepara os documentos que serão enviados ao modelo.

O modelo configurado atualmente é:

```text
qwen2.5:7b
```

rodando localmente pelo:

```text
Ollama
```

em:

```text
127.0.0.1:11434
```

O servidor do SUSANNA roda normalmente em:

```text
http://127.0.0.1:8002
```

---

### A base de conhecimento

Os documentos versionados ficam em:

```text
sources/
```

Por exemplo:

```text
sources/
├── antibioticos.json
├── antimicrobianos-cuidados.json
├── dengue.json
├── desinformacao.json
├── gripe-prevencao.json
├── hipertensao.json
├── hiv-transmissao.json
├── identificar-boatos.json
├── raiva-prevencao.json
├── samu-192.json
├── tuberculose.json
└── vacinas-seguranca.json
```

Esses arquivos são importados por:

```text
seed_knowledge.py
```

que chama:

```text
knowledge.import_document()
```

A base efetivamente utilizada pela busca é um banco SQLite com **FTS5**.

Então não é simplesmente:

```text
pergunta → LLM
```

É aproximadamente:

```text
pergunta
   ↓
busca lexical
   ↓
documentos relevantes
   ↓
LLM
```

---

### Existe uma camada importante de segurança

Depois que o Qwen produz uma resposta, ela **ainda não é exibida imediatamente**.

Existe uma política em:

```text
answer_policy.py
```

e o próprio `server.py` faz outra chamada ao modelo para conferir se a resposta realmente está apoiada pelas fontes.

Simplificando:

```text
Qwen gera resposta
      ↓
verifica citações
      ↓
verifica se os parágrafos têm suporte
      ↓
segunda análise pelo Qwen
      ↓
se aprovado
      ↓
mostra ao usuário
```

Se a resposta não estiver suficientemente apoiada, o sistema pode retornar algo equivalente a:

```text
SEM_EVIDENCIA
```

em vez de inventar uma resposta.

Isso é uma parte importante da arquitetura atual.

---

### `jobs.py`

É a camada de processamento assíncrono do próprio servidor.

Controla:

```text
fila
cancelamento
tempo de espera
requisições em execução
resultados temporários
métricas
```

Por padrão, a própria documentação indica algo semelhante a:

```text
1 execução simultânea
até 3 pedidos aguardando
```

Por isso o frontend consegue mostrar:

```text
Aguardando na fila · posição 2
```

---

### Conversação

Existe também:

```text
conversation.py
```

Ele ajuda a interpretar continuidade de conversa, principalmente perguntas como:

```text
"E nesse caso?"
"E para crianças?"
"E essa vacina?"
```

O histórico enviado pelo navegador também é limitado. O `app.js` mantém as últimas trocas e o servidor ainda pode reduzir esse contexto se ficar grande demais.

---

### O que temos além da aplicação

O projeto também já possui uma estrutura considerável de testes:

```text
tests/
```

com testes de:

```text
answer_policy
frontend
grounding
internet
jobs
knowledge
operations
search
streaming
```

E também:

```text
evaluation/
```

onde ficam várias rodadas de avaliação da IA.

Por exemplo:

```text
acceptance.json
controlled.json
fidelidade.json
performance.json
search-comparison.json
clarity-20260929-final.json
```

Então devemos tomar cuidado para não alterar uma parte central e quebrar os testes existentes.

---

### Situação atual importante

A documentação atual deixa explícito que o sistema:

- é **educativo**;
- combate desinformação em saúde;
- não representa oficialmente o SUS;
- não pesquisa a internet ao vivo no fluxo normal;
- usa documentos locais;
- roda com Ollama;
- não deve fazer diagnóstico ou prescrição;
- exige suporte documental para afirmações;
- possui segunda verificação da resposta.

Também vi que há trabalho recente de **29/09/2026** relacionado à revisão das fontes e avaliações, portanto essa branch está ativa e recebeu mudanças recentes.

===========================

