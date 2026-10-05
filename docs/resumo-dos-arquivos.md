Os arquivos têm funções diferentes: alguns participam do **chat em uso**, enquanto outros servem para **testes, avaliações, manutenção ou demonstração pela internet**.

## Interface e servidor local

- [`index.html`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/index.html>) — estrutura da página que o navegador exibe.
- [`styles.css`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/styles.css>) — aparência e layout da interface.
- [`app.js`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/app.js>) — comportamento do chat: envia perguntas, consulta o estado do pedido, mostra resposta e fontes e permite cancelar. **Há um texto inicial que diz que o chat consulta documentos locais e não pesquisa na internet; isso parece desatualizado em relação ao servidor atual, que busca no gov.br.**
- [`server.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/server.py>) — backend local. Recebe as solicitações, coordena a busca, o Ollama e a revisão da resposta, além de servir os arquivos da interface.
- [`jobs.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/jobs.py>) — fila de pedidos, concorrência, cancelamento, limites de espera e métricas de duração.
- [`conversation.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/conversation.py>) — identifica certos tipos de pergunta complementar e resolve o contexto anterior.
- [`answer_policy.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/answer_policy.py>) — valida citações e aplica verificações de segurança e apoio documental antes de liberar a resposta.
- [`ollama_transport.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/ollama_transport.py>) — comunicação entre o servidor Python e a API local do Ollama.
- [`govbr_search.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/govbr_search.py>) — busca páginas gov.br e extrai os trechos que podem ser enviados ao modelo.

## Avaliação e acompanhamento

Esses arquivos **não são chamados a cada pergunta normal do chat**. São ferramentas executadas separadamente para avaliar ou inspecionar o projeto.

- [`evaluate.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/evaluate.py>) — avalia a busca local com casos e documentos de teste; com `--llm`, também executa o modelo.
- [`evaluate_search.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/evaluate_search.py>) — compara métodos de busca local sem chamar o modelo.
- [`evaluate_grounding.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/evaluate_grounding.py>) — avalia o revisor documental com casos de teste.
- [`evaluate_acceptance.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/evaluate_acceptance.py>) — executa avaliações de aceitação pelo fluxo HTTP e Ollama, isolando os dados de teste.
- [`benchmark_performance.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/benchmark_performance.py>) — mede tempos e recursos do pipeline. Pode usar busca local ou, com opção específica, busca ao vivo; também pode registrar métricas no MLflow.
- [`audit_interface.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/audit_interface.py>) — inspeciona HTML e CSS de forma estática. Não abre a página como um navegador nem certifica acessibilidade.
- [`analyze_evaluations.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/analyze_evaluations.py>) — usa pandas para resumir relatórios em CSV; opcionalmente, registra métricas agregadas no MLflow.
- [`requirements-analytics.txt`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/requirements-analytics.txt>) — lista as dependências opcionais de análise, pandas e MLflow. Não são necessárias para executar o chat local.

## Busca local e manutenção

- [`knowledge.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/knowledge.py>) — importa documentos para o SQLite e faz busca lexical local. É usado por avaliações offline e manutenção; **não é a busca usada atualmente pelo chat ao vivo**.
- [`seed_knowledge.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/seed_knowledge.py>) — carrega os JSON de `sources/` na base SQLite local.
- [`operations.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/operations.py>) — verifica a integridade do banco local e cria cópias de segurança.
- [`mlflow.db`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/mlflow.db>) — arquivo de banco do MLflow que aparece na raiz. O código e a documentação atuais apontam o tracking para `.mlflow/mlflow.db`, não para esse caminho. Como este arquivo está versionado no Git, vale revisar sua origem e confirmar se ainda é necessário antes de apagá-lo ou alterá-lo. Ele não é a base documental do chatbot.

## Demonstração externa opcional

- [`internet_demo.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/internet_demo.py>) — inicia o túnel e o servidor protegido para uma demonstração temporária pela internet.
- [`internet_app.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/internet_app.py>) — aplicação WSGI que recebe as requisições externas autenticadas e as encaminha ao fluxo do servidor.
- [`internet_state.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/internet_state.py>) — determina onde guardar, fora do repositório, credenciais e registros privados dessa demonstração.
- [`configurar_ngrok.py`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/configurar_ngrok.py>) — salva o token do ngrok no diretório privado do usuário, sem colocá-lo no repositório ou exibi-lo no terminal.
- [`requirements-internet.txt`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/requirements-internet.txt>) — lista o Waitress, dependência da demonstração externa. Não é necessário no modo local.

## Arquivos de referência e controle

- [`README.md`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/README.md>) — instruções principais de instalação, execução e avaliação.
- [`LICENSE`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/LICENSE>) — licença de uso e distribuição do código.
- [`.gitignore`](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/.gitignore>) — informa ao Git quais arquivos locais e gerados deve ignorar, como `.venv`, caches, backups e `.mlflow`.

Em resumo: **o chat normal usa principalmente `app.js`, `server.py`, `jobs.py`, `conversation.py`, `govbr_search.py`, `ollama_transport.py` e `answer_policy.py`**. Os demais arquivos apoiam avaliação, análise, manutenção, configuração ou compartilhamento temporário.