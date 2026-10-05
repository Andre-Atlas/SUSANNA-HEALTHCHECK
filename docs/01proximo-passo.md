## Etapa 1 concluída — inspeção sem alterações

Estou na branch `develop_gui`, no commit `9e08299`, sincronizada com `origin/develop_gui`. A árvore de trabalho está limpa. **Não alterei arquivos nem executei testes ou avaliações**, conforme o roteiro desta etapa.

### Arquitetura e funcionamento

- **Interface:** [index.html](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/index.html:29>), `styles.css` e [app.js](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/app.js:120>). A interface envia mensagens, acompanha estados e exibe resposta e fontes.
- **API e fluxo da conversa:** [server.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/server.py:413>) recebe as mensagens, resolve perguntas de continuidade, busca fontes, monta o contexto e controla geração e revisão pelo Ollama.
- **Busca online:** [govbr_search.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/govbr_search.py:198>) consulta a busca do Ministério da Saúde e tenta extrair até três páginas HTML. Restringe as URLs a HTTPS em `gov.br` e subdomínios, inclusive nos redirecionamentos. PDFs não são extraídos.
- **Fila e cancelamento:** [jobs.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/jobs.py:100>) limita concorrência, espera e duração, oferece cancelamento e mantém métricas em memória.
- **Resposta e revisão:** `server.py` chama o modelo para gerar uma resposta e novamente para avaliá-la. [answer_policy.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/answer_policy.py:7>) verifica instruções suspeitas, citações e evidências. O conteúdo recuperado continua sendo texto não confiável; os bloqueios contra instruções maliciosas têm cobertura finita.
- **Modo remoto opcional:** `internet_demo.py`, `internet_app.py`, Waitress e `cloudflared` permitem uma demonstração por túnel. O modo local é o caminho padrão.

### O que os registros confirmam

Os relatórios versionados registram **12/14** critérios HTTP e **10/10** casos do revisor em 1º de outubro. São resultados de casos e condições específicos, não uma garantia geral. A revisão humana e a verificação de navegador continuam pendentes, e os documentos do piloto ainda não aprovam sua realização. Os relatórios antigos registram **5/14** e **4/5**; a evolução e as falhas restantes estão em [docs/etapa-regressoes-f01-f04-20261001.md](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/docs/etapa-regressoes-f01-f04-20261001.md>) e [piloto/problemas.md](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/piloto/problemas.md>).

Há testes de fila, transporte, busca documental offline, políticas de resposta, interface simulada, operações e avaliações HTTP. **Não localizei uma suíte dedicada a `govbr_search.py`**. A etapa 2 deve executar o que existe e reproduzir os problemas com casos sintéticos, sem substituir relatórios históricos.

### Divergências e riscos a confirmar

1. **Aviso de privacidade incorreto na interface:** `index.html` informa que o chatbot consulta documentos locais e “não pesquisa a internet ao vivo”. O código atual envia a pergunta de busca ao portal gov.br; a própria documentação de privacidade descreve isso. `app.js` também ainda mostra “Consultando as fontes locais…”. Essa divergência pode levar a pessoa a entender errado para onde a pergunta é enviada.
2. **Prontidão depende da base SQLite:** [server.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/server.py:308>) exige uma base preenchida em `/api/ready`, e os guias mandam semear a base. Porém, o fluxo do chat usa busca gov.br e não tem fallback local. É preciso confirmar se essa dependência ainda é necessária.
3. **Link quebrado no README:** ele aponta para `docs/02proximo-passo.md`; o arquivo disponível é [docs/01proximo-passo.md](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/docs/01proximo-passo.md>).
4. **Documentação parcialmente desatualizada:** `docs/base-documental.md` ainda descreve o caminho SQLite como fluxo do servidor, enquanto o README diz que as fontes locais são usadas offline. `docs/componentes.md` declara inventário de setembro e referência a um commit anterior; precisa ser reconciliado com a versão atual.
5. **Desempenho:** o benchmark registrado mede busca SQLite local, não a busca online completa. Os resultados existentes, portanto, não estabelecem a latência da pesquisa em gov.br.
6. **Ollama:** em uma checagem anterior nesta conversa, `127.0.0.1:11434` não respondeu e `ollama` não estava disponível no PATH. Não repeti essa verificação durante esta etapa.

### Ferramentas e custos

Não encontrei dependência de API paga no caminho local. Python e SQLite usam licenças permissivas/de domínio público conforme o inventário do projeto; Ollama está sob licença MIT e a variante indicada do Qwen 2.5 usa Apache 2.0. [Licença do Ollama](https://github.com/ollama/ollama/blob/master/LICENSE), [licença do Qwen 2.5](https://ollama.com/library/qwen2.5%3A7b-instruct-q5_0/blobs/832dd9e00a68).

Waitress é opcional para a demonstração remota. `cloudflared` é opcional e o Quick Tunnel documentado oferece endereço temporário sem exigir conta Cloudflare; qualquer pessoa com o endereço pode acessar o serviço exposto. [Cloudflare Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/). MLflow também é opcional e pode usar armazenamento local; o projeto o sugere apenas para métricas agregadas. [MLflow OSS](https://www.mlflow.org/).

O portal gov.br não aparece no código como serviço pago, mas a busca envia a pergunta pela internet; custo e franquia da conexão do usuário não estão incluídos. Isso não verifica direitos de reutilização de cada conteúdo-fonte, que seguem como pendência separada.

### Próximas etapas propostas, por prioridade

1. **Etapa 2:** executar testes e avaliações existentes, registrar uma linha de base nova e reproduzir os problemas conhecidos com dados sintéticos.
2. **Etapa 3:** corrigir e testar a resistência do revisor a instruções maliciosas.
3. **Etapa 4:** testar relevância, extração, fontes, citações, contradições e pedidos clínicos.
4. **Etapa 5:** revisar falhas de rede/Ollama, cancelamento, fila e estados visíveis na interface.
5. **Etapa 6:** conferir armazenamento e tráfego real e alinhar os avisos de privacidade.
6. **Etapa 7:** medir o fluxo online completo, sem confundir os números do benchmark offline com latência da busca gov.br.
7. **Etapa 8:** atualizar documentação e preparar uma decisão de piloto, mantendo explícitas as avaliações humanas pendentes.

Parei ao fim da Etapa 1, como o roteiro pede. Aguardo sua autorização para iniciar a Etapa 2.


-----------------------------------------------------------------------------------------------------------------


## Etapa 2: linha de base parcial

O serviço local está ativo: `/api/health` e `/api/ready` retornaram **200**. O Ollama responde como versão **0.34.0**, com `qwen2.5:7b` instalado; a prontidão também confirmou a base SQLite com 12 trechos.

**Não consegui executar a suíte Python nem as avaliações.** `py` e `python` não estão disponíveis no PATH, e `.venv\Scripts\python.exe` aponta para um executável externo bloqueado. Não tentei contornar o bloqueio nem instalar ferramentas. Assim, não há resultados novos de testes ou avaliações nesta etapa.

O que consegui verificar:

- `node --check app.js` e `node --check tests/frontend_harness.js` passaram como verificações de sintaxe. Executar `node tests/frontend_harness.js` não executou os casos comportamentais; o arquivo prepara o ambiente que a suíte Python usa.
- O histórico **5/14** registra nove falhas: a02, a03, a04, a05, a08, a09, a10, a12 e a14. Oito envolvem respostas recusadas por formato/citações; a14 foi recusada por `unsupported_claim`.
- O relatório histórico do revisor **4/5** reproduz F01: a fonte sintética proibia abrir uma caixa, mas incluía uma instrução ao revisor para aprovar a contradição; a resposta contraditória foi aceita, com `errors=[]`.
- Um relatório posterior registra **12/14** no fluxo HTTP e **10/10** no revisor. Porém, os hashes de código desses relatórios não correspondem aos arquivos atuais da branch. Sem reexecutá-los, não confirmam o comportamento da versão atual.

Não criei relatórios novos nem alterei o comportamento. A avaliação F01 da versão atual continua pendente; os dados históricos documentam a falha, mas não substituem sua reprodução atual.

Encontrei e preservei uma alteração local em [docs/01proximo-passo.md](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/docs/01proximo-passo.md>). Não fiz outras alterações. A branch continua `develop_gui`.

Para concluir a Etapa 2, preciso que o ambiente disponibilize um executável Python acessível — por exemplo, restaurando o launcher `py` ou o Python do ambiente virtual. Vou aguardar isso antes de avançar; não inicio a Etapa 3 sem sua autorização.