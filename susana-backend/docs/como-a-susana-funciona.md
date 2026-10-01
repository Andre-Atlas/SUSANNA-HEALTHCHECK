# Como a Susana funciona

Este guia explica, em linguagem simples, o que acontece desde que uma pessoa envia uma pergunta até receber uma resposta. Ele separa o que já existe no protótipo daquilo que ainda precisa ser construído para o produto final.

Os caminhos da seção final são relativos à pasta `susana-backend`, exceto o caminho do frontend, que começa na raiz do repositório.

## A ideia em uma frase

A Susana não é o Ollama sozinho. Ela é um sistema que recebe a pergunta, procura informação aprovada, entrega os trechos encontrados ao modelo e devolve uma resposta com referências.

```text
Pessoa pergunta
      ↓
React envia ao backend
      ↓
Backend entende o tipo de pedido
      ↓
Busca dados estruturados e/ou documentos
      ↓
Se encontrar evidências, Ollama redige a resposta
      ↓
Pessoa recebe resposta, estado e fontes
```

O princípio mais importante é: **o modelo deve explicar o que as fontes dizem, não completar lacunas com o que ele imagina saber**.

## Quem faz o quê

| Parte | Explicação simples |
|---|---|
| Protótipo React | A tela: conversa, envia a pergunta e apresenta resposta, estado e links de fontes. |
| FastAPI | A recepção e coordenação: valida a mensagem e decide quais partes do sistema chamar. |
| PostgreSQL | As tabelas que guardam fontes, documentos, unidades, serviços e trechos indexados. |
| pgvector | Uma extensão do PostgreSQL que permite encontrar trechos com significado parecido com a pergunta. |
| Ollama | Executa modelos localmente: um modelo transforma texto em vetores de busca; outro redige a resposta. |
| Fontes oficiais | Os sites, APIs e arquivos aprovados de onde os dados devem vir. |

O Ollama **não navega pelos sites**. Ele só trabalha com o material que a aplicação lhe envia. Uma URL cadastrada, por si só, não significa que seu conteúdo já foi baixado ou está disponível para o chat.

## Caminho de uma pergunta

Imagine que a pessoa pergunte: “Quais UBS existem em Samambaia?”.

1. A tela cria ou reutiliza um identificador da conversa e envia a mensagem ao `POST /api/v1/chat`.
2. O backend valida o formato da mensagem e considera o contexto mantido nessa conversa. Hoje esse histórico é temporário e fica na memória do processo.
3. O classificador procura sinais simples de assunto e escopo. Ele tenta distinguir, por exemplo, uma busca por unidade de uma pergunta clínica. Essa etapa usa regras programadas; não é uma compreensão perfeita de linguagem.
4. A busca estruturada procura unidades no PostgreSQL usando critérios encontrados, como tipo e Região Administrativa.
5. Para usar um registro estruturado como evidência, o backend exige uma fonte associada. Isso permite indicar de onde veio a informação.
6. A busca RAG transforma a pergunta em um vetor com o modelo de embeddings do Ollama. O PostgreSQL compara esse vetor com os vetores dos trechos de documentos indexados e devolve os mais próximos que passam pelo limite de similaridade configurado.
7. O backend prepara um prompt com a pergunta, contexto da conversa, instruções de segurança e evidências recuperadas.
8. O modelo de chat do Ollama redige uma resposta com base nesse material.
9. O backend devolve a resposta, um estado, as fontes e os trechos usados. A tela mostra a resposta e permite abrir os links.

Nem toda pergunta percorre todos os passos. Uma pergunta claramente fora do escopo pode ser recusada antes de consultar o Ollama. Uma pergunta vaga pode receber um pedido de esclarecimento. Se não houver evidência, o backend deve responder que não encontrou informação suficiente, sem pedir ao modelo para adivinhar.

## Dois tipos de busca

### Busca em tabelas

É indicada para fatos com campos definidos, como nome da unidade, tipo, Região Administrativa, endereço ou serviços cadastrados.

Exemplo: “Quais UBS há em Samambaia?”. O backend filtra registros estruturados por tipo e território. Esse caminho só será confiável se a base estiver preenchida com dados aprovados, atualizados e com origem registrada.

### Busca em documentos, ou RAG

RAG significa que o sistema busca trechos de documentos relacionados à pergunta e os entrega ao modelo como evidência. É indicado para textos, por exemplo, páginas que explicam um fluxo administrativo ou documentos com orientações institucionais.

O RAG **não atualiza os dados por conta própria** e não garante que um trecho seja verdadeiro ou atual. A qualidade depende dos documentos selecionados, de suas datas, da divisão em trechos e da busca. Por isso, as respostas precisam mostrar referências e o corpus precisa ser mantido.

## Como um documento entra no RAG

Hoje, o fluxo manual funciona assim:

```text
Fonte aprovada
    ↓
Cadastrar documento e texto no backend
    ↓
Dividir o texto em trechos menores
    ↓
Ollama cria um vetor para cada trecho
    ↓
Guardar texto, vetor, origem e estado no PostgreSQL/pgvector
    ↓
A busca pode recuperar esses trechos em perguntas futuras
```

A ingestão usa o endpoint `POST /api/v1/rag/documents/{id}/ingest`. O documento só passa a participar da busca quando seu estado é `indexed`. Se a geração de vetores falhar, ele não deve ser tratado como indexado.

**Importante:** o projeto ainda não tem um coletor geral de sites nem sincronização automática de catálogos. Hoje, alguém precisa selecionar e cadastrar o conteúdo. No produto final, esse trabalho pode ser automatizado por conectores específicos para portais/API/arquivos aprovados, com regras para detectar atualizações e reindexar somente o que mudou.

## O papel dos dois modelos

O projeto usa dois modelos, com trabalhos diferentes:

- **Modelo de embeddings (`nomic-embed-text`)**: converte a pergunta e os trechos em números que representam significado. Isso permite procurar assuntos parecidos, mesmo sem as mesmas palavras.
- **Modelo de chat (`llama3.2:3b`)**: recebe a pergunta e os trechos encontrados e escreve a resposta em português.

A dimensão dos embeddings deve coincidir com a coluna vetorial do banco. Nesta instalação, ambos estão configurados para 768 dimensões. Trocar o modelo de embeddings no futuro exige confirmar sua dimensão e planejar a reindexação dos documentos existentes.

## O que significam os estados devolvidos

| Estado | O que a pessoa deve entender |
|---|---|
| `answered` | O sistema encontrou evidências e o modelo gerou uma resposta. Ainda é importante conferir a fonte. |
| `needs_clarification` | Falta saber melhor qual serviço ou situação a pessoa quer consultar. |
| `out_of_scope` | O pedido é clínico ou não pertence ao escopo informacional definido para a Susana. |
| `no_evidence` | A busca não achou material suficiente para responder com segurança. |
| `error` | O backend, banco, busca ou modelo falhou durante a consulta. É diferente de “a fonte não tem a resposta”. |

O endpoint `/api/v1/health/dependencies` ajuda a separar problemas técnicos de falta de conteúdo. Ele informa estado do PostgreSQL, pgvector, modelo de chat, modelo de embeddings e quantidade de documentos indexados. Ter Ollama pronto não significa ter corpus: `indexed_documents: 0` quer dizer que ainda não há documentos RAG indexados.

## Exemplo de ponta a ponta

Pergunta: “Qual é o horário desta unidade em Samambaia?”

1. Se a base estruturada tiver a unidade, seu horário e uma fonte aprovada, essa informação pode servir como evidência direta.
2. Se a pergunta pedir uma explicação que esteja em documentos, o RAG procura trechos relevantes.
3. Se a fonte não informar horário, a Susana deve dizer que não encontrou essa informação. Não deve deduzir o horário pelo tipo de unidade.
4. Se a unidade nem estiver identificada, deve pedir o nome ou mais contexto.
5. Se o Ollama ou banco estiver fora do ar, deve informar falha técnica, sem disfarçar o erro como ausência de dados.

## Como deve funcionar quando estiver finalizada

O fluxo esperado para o produto final é parecido com o protótipo atual, mas com conteúdo oficial mantido automaticamente e controles mais fortes:

```text
Fontes autorizadas pela equipe
      ↓
Conectores consultam APIs, catálogos e arquivos aprovados
      ↓
Validar formato, licença, órgão responsável, data e qualidade
      ↓
Guardar dados tabulares em tabelas e documentos em coleção documental
      ↓
Detectar alterações e reprocessar somente itens atualizados
      ↓
Pessoa pergunta pela interface
      ↓
Buscar dados por filtro e/ou trechos de documentos
      ↓
Verificar evidências e atualidade
      ↓
Ollama redige uma resposta curta com referências
      ↓
Registrar métricas e permitir correção/avaliação
```

No fluxo final, não é desejável baixar tudo que aparece num catálogo sem revisão. O conector pode descobrir muitos conjuntos automaticamente, mas a equipe deve aprovar quais são apropriados e para que tipos de resposta. Estatísticas de atendimentos, por exemplo, são diferentes de uma lista atual de unidades e não devem ser usadas como se fossem a mesma coisa.

Também será necessário decidir como operar e manter o serviço: autenticação para administração, atualização programada das fontes, retenção de conversas, monitoramento, política para dados pessoais e processo de revisão de respostas incorretas. Essas decisões ainda não estão todas implementadas nem definidas.

## O que já está funcionando e o que falta

### Já existe

- Interface React integrada ao endpoint de chat.
- API que valida a mensagem e classifica alguns tipos de pedido.
- Busca estruturada para unidades e serviços cadastrados.
- Busca semântica de documentos indexados no PostgreSQL/pgvector.
- Geração de embeddings e respostas via Ollama local.
- Estados explícitos para esclarecimento, fora de escopo, falta de evidência e erro.
- Resposta com referências e evidências recuperadas.

### Ainda não significa que esteja pronto para cidadãos

- **O corpus oficial ainda precisa ser escolhido, importado e validado.** No estado atual, não há documentos oficiais indexados.
- A fonte cadastrada não é automaticamente lida; cadastrar uma fonte apenas registra sua identificação e endereço.
- Não existe ainda um sincronizador completo que percorra catálogos e mantenha recursos atualizados.
- A busca estruturada só pode responder sobre unidades/serviços que tenham sido carregados nas tabelas.
- O classificador de intenção é baseado em regras e precisa de avaliação com perguntas reais e ambíguas.
- A sessão é temporária: reiniciar a API a apaga, e vários processos não compartilham o mesmo histórico.
- Autenticação/autorização para as operações administrativas ainda precisa ser criada antes de expor a API.
- Respostas do modelo precisam ser avaliadas contra fontes e casos de teste. Instruções no prompt ajudam, mas não garantem precisão por si só.

## O que observar durante um teste

1. Abra o chat e confira o indicador de modelos e corpus.
2. Faça uma pergunta que esteja claramente respondível pelas fontes disponíveis.
3. Abra as referências e confira se elas realmente sustentam a resposta.
4. Faça uma pergunta sem resposta no material: a resposta correta é declarar a limitação.
5. Faça uma pergunta ambígua: a Susana deve pedir esclarecimento, não escolher um serviço ao acaso.
6. Faça uma pergunta clínica individual: deve permanecer fora do escopo.
7. Se aparecer `error`, verifique `/api/v1/health/dependencies`; se aparecer `no_evidence`, verifique se o documento existe, está `indexed` e tem conteúdo relacionado.

Para abrir as ferramentas durante o desenvolvimento, a interface React fica em `http://127.0.0.1:5174` e a documentação interativa da API em `http://127.0.0.1:8000/docs`. O frontend encaminha chamadas `/api` ao backend local.

## Referências no código

- Interface e chamada HTTP: `prototipo-integrado/src/main.jsx`.
- Rota do chat: `app/api/v1/chat.py`.
- Orquestração da conversa: `app/services/chat_service.py`.
- Classificação de escopo e intenção: `app/services/scope_service.py`.
- Busca em unidades e serviços: `app/services/structured_search_service.py`.
- Busca documental: `app/services/retrieval_service.py`.
- Ingestão e criação de vetores: `app/services/rag_service.py`.
- Instruções enviadas ao modelo: `app/services/prompt_builder.py`.
- Comunicação com Ollama: `app/providers/ollama.py`.
- Estado das dependências e documentos: `app/api/v1/health.py`.
