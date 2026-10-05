# SUSANNA-HEALTHCHECK — projeto acadêmico

Chatbot educativo sobre desinformação em saúde. Interface independente, sem vínculo oficial com o SUS. Desenvolvido para apresentação na Eldorado.

## Guias do projeto

- [Instalação, uso e manutenção](docs/guia-projeto.md).
- [Dados processados, registros e privacidade](docs/privacidade.md).
- [Versões e licenças dos componentes](docs/componentes.md).
- [Responsáveis e rotina de manutenção](docs/responsabilidades.md).
- [Operação local, métricas, backup e recuperação](docs/disponibilizacao.md).
- [Plano e progresso do projeto](docs/01proximo-passo.md).
- [Registro da etapa de regressões F01–F04](docs/etapa-regressoes-f01-f04-20261001.md).

## Executar localmente

Compatibilidade prevista: Windows 10/11 e macOS, com Python 3.10+ e [Ollama](https://ollama.com/download). O servidor executa localmente e usa a internet para pesquisar páginas oficiais `gov.br`; essa busca não exige pacote pip nem chave de API. O modo de demonstração pela internet instala Waitress; consulte o guia específico abaixo.

1. Inicie o Ollama pelo aplicativo ou, em um terminal, com `ollama serve`.
2. Se o modelo ainda não estiver instalado, execute `ollama pull qwen2.5:7b` (download de aproximadamente 4,7 GB, uma única vez).
3. Abra o terminal na pasta do projeto e inicie o servidor. A base SQLite é usada em avaliações e manutenção offline, não é necessária para conversar.

**Windows (PowerShell):**

```powershell
py -3 server.py --port 8002 --concurrency 1 --queue-size 3
```

**macOS (Terminal):**

```bash
python3 server.py --port 8002 --concurrency 1 --queue-size 3
```

4. Abra **http://127.0.0.1:8002**.

Use o servidor `server.py`, não `python -m http.server` nem o Live Server: eles não executam a API do chatbot. Não é necessário encerrar o servidor antigo da porta 8001. Nos comandos de manutenção abaixo, use `py -3` no Windows e `python3` no macOS.

Outra porta: `python3 server.py --port 8003` (macOS) ou `py -3 server.py --port 8003` (Windows).
Outro modelo local instalado: `OLLAMA_MODEL=nome:tag python3 server.py`.
No Windows PowerShell, use `$env:OLLAMA_MODEL="nome:tag"; py -3 server.py`.

## Compartilhar pela internet

Não há um link público permanente: cada inicialização gera um endereço temporário.
O link que já apareceu em versões anteriores deste README expirou. Para criar um
novo, mantenha o Ollama aberto com `qwen2.5:7b` instalado. Instale também o
`cloudflared`: no macOS, `brew install cloudflared`; no Windows, baixe o executável
pelas [instruções oficiais](https://developers.cloudflare.com/tunnel/downloads/)
e deixe-o disponível no PATH.

Execute estes comandos no terminal aberto na pasta do projeto. Eles instalam a
dependência da demonstração e iniciam juntos o servidor protegido e o túnel; não
execute `server.py` neste modo.

**macOS:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-internet.txt
.venv/bin/python internet_demo.py
```

**Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-internet.txt
.venv\Scripts\python.exe internet_demo.py
```

Quando o terminal mostrar `URL:`, compartilhe esse endereço e o usuário `equipe`;
consulte a senha atual no arquivo privado indicado pelo próprio terminal e envie-a
separadamente aos amigos. Deixe o terminal, o computador e a conexão ligados.
Pressione Ctrl+C para encerrar. O endereço e a senha deixam de valer ao parar a
demonstração. Se o túnel não conectar, consulte [alternativas e diagnóstico](docs/internet-demo.md);
algumas redes bloqueiam esse tipo de conexão. As perguntas passam pela infraestrutura
do provedor do túnel, e há uma falha conhecida na revisão automática que bloqueia a
aprovação do piloto. Use somente perguntas fictícias; consulte as [limitações e privacidade](docs/internet-demo.md)
e não use as respostas para decisões de saúde.

## Ambiente de disponibilização

Configurado para uso somente neste computador, sem publicação na rede. Veja
[o guia de operação local](docs/disponibilizacao.md) para prontidão, limites,
métricas, backup e recuperação. `/api/ready` verifica a disponibilidade do Ollama
e do modelo; a pesquisa gov.br é verificada quando cada pergunta é enviada.

## Organização

- `index.html`: página e chat.
- `styles.css`: aparência responsiva.
- `app.js`: conversa, histórico, espera e tratamento de falhas.
- `server.py`: arquivos públicos e API local que conversa com o Ollama.
- `govbr_search.py`: busca ao vivo e extração limitada a páginas HTTPS `gov.br`.
- `jobs.py`: fila limitada, cancelamento, expiração e métricas em memória.
- `ollama_transport.py`: stream privado e conexão cancelável com o Ollama.

A conversa existe apenas em memória. O navegador envia até as últimas seis trocas e a nova pergunta ao servidor local. O servidor pode remover trocas antigas para respeitar seu orçamento conservador de contexto. Limpar ou recarregar reinicia o histórico e solicita cancelamento do pedido; o servidor fecha sua conexão com o Ollama. Históricos em processamento são liberados ao término; resultados ficam em memória por até 60 segundos, com limite de quantidade. O servidor do chat não grava conversas em disco. Scripts de avaliação gravam relatórios com casos e respostas; logs próprios do Ollama e do sistema não foram auditados. Os logs HTTP estão desativados. Veja [retenção e limites de privacidade](docs/privacidade.md).

O chat mostra fila, geração e revisão em andamento. O texto aparece progressivamente somente após a validação completa. Há botão **Cancelar**, uma execução por vez e até três pedidos em espera por padrão. Para configurar: `python3 server.py --concurrency 1 --queue-size 3` (macOS) ou `py -3 server.py --concurrency 1 --queue-size 3` (Windows). Veja [desempenho, limites e medições](docs/desempenho-experiencia.md).

## Limites desta etapa

O chatbot busca conteúdo ao vivo pela pesquisa do Ministério da Saúde e extrai até três páginas HTML HTTPS de domínios `gov.br` por pergunta. A resposta usa apenas trechos dessas páginas; não há fallback para documentos locais nem para outros domínios. PDFs e páginas que não podem ser extraídas ficam de fora. A consulta depende de internet e pode aumentar o tempo de resposta. Veja [busca ao vivo gov.br](docs/busca-govbr-ao-vivo-20261001.md). Os 16 documentos em `sources/` continuam versionados para avaliação/offline, mas não são usados pelo servidor de chat neste modo.

Os trechos enviados ao modelo são apresentados com suas referências. A busca ao vivo usa o mecanismo lexical do portal do Ministério da Saúde; a resolução de continuidade usa a conversa para contextualizar a pergunta atual. A documentação da busca lexical local continua valendo para os scripts de avaliação/offline, não para a recuperação online do chat. Recuperar um trecho não comprova uma alegação. Ainda precisamos avaliar relevância, fidelidade das respostas e citações. Não se deve apresentar as respostas como checagem factual ou orientação médica.

Sem fontes, o servidor responde sem chamar a LLM. Com fontes, valida referências
e faz uma segunda revisão por IA do apoio documental, exigindo evidências literais
nas fontes citadas antes de exibir a resposta. A revisão pode errar e acrescenta
tempo de processamento. Veja [controle de respostas](docs/controle-respostas.md).

Depois de atualizar o código, reinicie `python3 server.py` (macOS) ou `py -3 server.py` (Windows) e recarregue a página. Importar novos documentos não exige reinício.

## Avaliar a base inicial

```bash
python3 -m unittest discover -s tests -v
python3 evaluate.py
python3 evaluate_search.py
# Latência offline do pipeline com SQLite temporário (requer Ollama)
python3 benchmark_performance.py
# Busca online gov.br com 20 casos sintéticos (requer Ollama e internet)
python3 benchmark_performance.py --live-search --warmup 1 --repetitions 1 --output evaluation/performance-live.json
# Opcional: salvar agregados de latência no MLflow local
python3 -m pip install mlflow
python3 benchmark_performance.py --mlflow
# Opcional: também gerar respostas com o Ollama local
python3 evaluate.py --llm --output evaluation/llm.json
```

A avaliação offline usa uma base temporária com o conjunto versionado, sem alterar seus documentos locais nem consultar a web. O benchmark padrão mede fila, busca lexical local, geração, revisão e total. `benchmark_performance.py --live-search` mede o fluxo com consultas sintéticas e pesquisa ao vivo em `gov.br`; isso exige internet e pode ser afetado pela disponibilidade ou limitação do portal. Os relatórios preservam métricas e IDs dos casos, não perguntas, respostas ou trechos recuperados. MLflow é opcional e registra somente agregados e parâmetros técnicos. Veja [fontes e critérios de avaliação](docs/avaliacao-inicial.md) e [desempenho e experiência](docs/desempenho-experiencia.md).

## Piloto e entrega

[Pacote do piloto local](piloto/README.md): roteiro, formulário, critérios propostos,
problemas e aceite. Pré-piloto em 25/09/2026: 67 testes passaram; regressão real
do revisor 4/5, com F01 reproduzido. Versão candidata, sem aprovação final.

## Aceitação e revisão humana

Novos cenários e instruções de revisão estão em [aceitação e testes adversariais](docs/aceitacao.md).
A rodada real obteve **5/14** nos critérios automáticos do fluxo HTTP e **4/5** no
revisor isolado. Foi observada aceitação indevida de uma resposta contraditória
quando a fonte incluía uma instrução maliciosa ao revisor; isso bloqueia a aprovação
do piloto. Revisões humanas e verificação real de navegador/celular permanecem pendentes.

Uma nova rodada local sintética em 05/10/2026 passou **14/14** critérios
automáticos ([relatório](evaluation/acceptance-20261005-final.json)). A rodada
exercitou a quarentena da fonte maliciosa; não substitui revisão humana nem
verificação real em navegador/celular.

A [avaliação focal de respostas de antibióticos](docs/avaliacao-respostas-20260930.md)
registrou uma correção de fonte substituída, **3/3** respostas revisadas por IA e
confirmação HTTP local e pública. Ela não substitui avaliação humana independente.

O [pacote de revisão](evaluation/acceptance.human.md) contém as perguntas, respostas
exibidas, fontes e campos pendentes para duas pessoas. Os relatórios são de testes
sintéticos, sem gravação de conversas reais de usuários.

```bash
python3 audit_interface.py --output evaluation/interface-nova-rodada.json
python3 evaluate_acceptance.py --output evaluation/acceptance-nova-rodada.json
python3 evaluate_grounding.py --cases evaluation/review-acceptance-cases.json --output evaluation/review-nova-rodada.json
```

## Referências técnicas

- [API de conversa do Ollama](https://docs.ollama.com/api/chat)
- [Modelo Qwen2.5](https://ollama.com/library/qwen2.5)

# 👤 Autor

**Guilherme Barros**

<img src="https://github.com/dida0982.png" width="150" alt="Foto de perfil">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/guilherme-barros-6a0369209/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dida0982)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/guilherme_barros_jr/)
