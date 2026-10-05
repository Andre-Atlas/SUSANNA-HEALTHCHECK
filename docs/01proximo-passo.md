## Etapa 1 concluída — inspeção sem alterações

Estou na branch `develop_gui`, no commit `9e08299`, sincronizada com `origin/develop_gui`. A árvore de trabalho está limpa. **Não alterei arquivos nem executei testes ou avaliações**, conforme o roteiro desta etapa.

### Arquitetura e funcionamento

- **Interface:** [index.html](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/index.html:29>), `styles.css` e [app.js](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/app.js:120>). A interface envia mensagens, acompanha estados e exibe resposta e fontes.
- **API e fluxo da conversa:** [server.py](</C:/Users/dida0/OneDrive/Área de Trabalho/SUSANNA-HEALTHCHECK/server.py:413>) recebe as mensagens, resolve perguntas de continuidade, busca fontes, monta o contexto e controla geração e revisão pelo Ollama.
- **Busca online:** `govbr_search.py` usa rotas temáticas diretas ou a API SERPRO do portal gov.br, consultada por termos e tipos `Servico|Tema`. A API pode retornar páginas de diferentes órgãos públicos; URLs candidatas só são aceitas sob HTTPS em `gov.br`, e o servidor lê até três páginas HTML, inclusive após redirecionamentos. PDFs não são extraídos.
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


## Etapas 2–9 — trabalho técnico concluído em 05/10/2026

### Linha de base, correções e resultados

- A linha de base documentada registra 5/14 critérios HTTP e 4/5 no revisor. A falha F01 foi reproduzida: uma instrução maliciosa na fonte influenciou a revisão de uma resposta contraditória.
- A suíte Python final passou: **83 testes; 8 ignorados** porque os testes de interface usam JavaScriptCore nativo do macOS, indisponível neste Windows. Não foram instalados pacotes.
- A busca offline contextual passou **38/38**; a avaliação de recuperação, **18/18**. O avaliador isolado do revisor passou **10/10** após o endurecimento.
- A rodada HTTP com Ollama passou **14/14** critérios automáticos. O cenário de injeção foi barrado antes da geração e contado como caminho de quarentena exercitado. Isso não demonstra resistência a todas as variantes nem é aprovação humana.
- A auditoria estática da interface passou **10/10**; quatro pares de contraste avaliados passaram 4,5:1. Os oito testes JavaScript não executaram nesta máquina.
- A inspeção interativa no navegador também ficou pendente: o runtime de automação disponível falhou ao iniciar (`os error 3`).
- Benchmark online: **20/20** pedidos concluídos, uma repetição mais aquecimento. Busca p50/p95: 0,7061/0,7655 s (19 consultas); total: 1,5622/8,5115 s (20 pedidos). Uma amostra chegou à revisão (40,2402 s), 18 respostas abstiveram-se e uma pediu esclarecimento. A amostra não mede fidelidade e ainda é pequena para comparação estável.

### Alterações implementadas

O fluxo do revisor agora rejeita padrões adversariais detectados antes de chamar o modelo; testes cobrem ordens ao revisor, comandos de sistema falsos e caracteres invisíveis. A defesa continua heurística e precisa de ataques independentes novos.

A busca gov.br ganhou validação estrita dos rótulos de host, testes locais de redirecionamento/conteúdo/limites e rejeita páginas maiores que o limite em vez de usar texto truncado. A busca offline ignora palavras genéricas da consulta que antes podiam selecionar uma fonte apenas por “nesta base”.

`/api/ready` verifica Ollama e modelo, sem depender da base SQLite, já que o chat pesquisa gov.br por pergunta. Interface, privacidade e guias agora explicam que a pergunta contextualizada segue para gov.br, que o histórico completo não vai à busca e que o modelo roda localmente. A demonstração por túnel volta a inserir seu aviso específico de provedor.

### Relatórios e arquivos de referência

- Aceitação HTTP: [evaluation/acceptance-20261005-final.json](../evaluation/acceptance-20261005-final.json).
- Revisor após endurecimento: [evaluation/verificador-hardening-20261005.json](../evaluation/verificador-hardening-20261005.json).
- Busca: [evaluation/search-comparison-20261005.json](../evaluation/search-comparison-20261005.json).
- Interface: [evaluation/interface-static-final-20261005.json](../evaluation/interface-static-final-20261005.json).
- Desempenho ao vivo: [evaluation/performance-live-20261005.json](../evaluation/performance-live-20261005.json).

As alterações principais estão em `answer_policy.py`, `govbr_search.py`, `knowledge.py`, `server.py`, `evaluate_acceptance.py`, `benchmark_performance.py`, `internet_app.py`, `index.html`, `app.js` e testes. README, guias, privacidade, aceitação e materiais de piloto foram alinhados aos comportamentos medidos. Os relatórios históricos foram preservados.

### Estado e pendências

O piloto **não está aprovado**. Faltam revisão independente de duas pessoas sobre respostas e fontes, teste interativo em navegador real (incluindo teclado/zoom), feedback de participantes e decisão formal de aceite. A detecção de injeção não é universal; a rodada 14/14 é sintética e automática. As respostas abstiveram-se em 18 dos 20 pedidos do benchmark, então utilidade permanece em aberto.

O ambiente observado usou Python 3.13.5, Ollama local 0.34.0 e `qwen2.5:7b`. Não foram contratados serviços, usadas APIs pagas ou adicionados serviços externos de monitoramento. A pesquisa gov.br requer internet e pode variar com a disponibilidade do portal e a conexão do operador.
