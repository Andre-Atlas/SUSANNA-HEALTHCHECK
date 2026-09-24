# Desempenho e experiência

## Fluxo e apresentação

O navegador cria um pedido com `POST /api/jobs` e acompanha `GET /api/jobs/{id}`
a cada 500 ms. Os estados públicos incluem fila, execução, cancelamento, erro e
conclusão; a etapa informa consulta às fontes, geração ou revisão. A posição na
fila e o tempo decorrido aparecem no chat.

O Ollama transmite tokens ao Python em um stream NDJSON **privado**. A aplicação
acumula o rascunho, confere referências e faz a revisão documental completa. Os
rascunhos, inclusive tokens de revisão, não entram no estado público do pedido.
Só `state=done` inclui `result`, contendo a resposta aprovada ou uma mensagem segura
de recusa. Stream incompleto ou com erro nunca libera uma resposta parcial.

Após receber o resultado final, o navegador apresenta o texto em blocos de até
aproximadamente 100 caracteres, com intervalos de 35 ms, preservando o conteúdo.
Com `prefers-reduced-motion`, a apresentação é imediata. `aria-busy` evita anunciar
cada bloco como uma nova resposta. Isso é apresentação progressiva **após** a
validação, não transmissão antecipada de tokens nem redução do tempo de inferência.

## Cancelamento

Cancelar, Limpar e sair/recarregar a página enviam `DELETE /api/jobs/{id}`. Se o
usuário limpar antes de receber o ID, o código aguarda a resposta de criação para
cancelar aquele pedido, sem restaurar mensagens antigas ou alterar uma conversa nova.

Na fila, o pedido é removido imediatamente. Durante geração ou revisão, o servidor
marca o cancelamento e executa `shutdown` no socket exclusivo daquele pedido ao
Ollama, interrompendo inclusive leituras bloqueadas. O worker descarta o conteúdo
e só então libera a vaga. Não mata o processo Ollama nem descarrega o modelo global.

O transporte utiliza o [stream de chat do Ollama](https://github.com/ollama/ollama/blob/v0.32.5/docs/api.md).
O [servidor do Ollama 0.32.5](https://github.com/ollama/ollama/blob/v0.32.5/server/routes.go)
propaga o contexto HTTP à execução do modelo. Fechar essa conexão solicita o
cancelamento upstream; o tempo de liberação do dispositivo depende do Ollama.
O benchmark mede o encerramento do worker local, não uma confirmação da GPU.

Se o cancelamento explícito não chegar, 20 segundos sem consultas de acompanhamento
cancelam o pedido por desconexão. Abas suspensas podem atingir esse limite.
Limites adicionais: 120 s na fila e 360 s em execução, verificados a cada 250 ms.
O navegador limita a espera total a 490 s. Uma conexão inicial ao Ollama tem timeout
de 5 s; leituras têm limite de 180 s, além do limite total controlado pelo worker.

## Concorrência e memória

Padrão: uma execução por vez, com até três pedidos adicionais. A fila é FIFO;
geração e revisão compartilham a mesma vaga. Ao atingir o limite, a API responde
HTTP 429 e o navegador preserva a pergunta para nova tentativa.

```bash
python3 server.py --concurrency 1 --queue-size 3
```

`--concurrency` aceita 1–4 e `--queue-size` aceita 0–16. Aumentar concorrência exige
nova medição de memória/latência. O controle vale por processo deste servidor,
não por todas as aplicações que usam o mesmo Ollama. `/api/chat` permanece
compatível e usa a mesma fila; não é um atalho para contornar o limite.

Históricos em processamento são liberados ao término. Resultados ficam apenas em
memória por até 60 s, com limite adicional de resultados recentes (até 32, mais
pedidos que já estavam em andamento). O identificador aleatório dá acesso ao
pedido; as rotas individuais não são gravadas nos logs HTTP. Nada disso fornece
autenticação para uma instalação pública: o servidor permanece vinculado a localhost.

## Métricas e reprodução

`GET /api/metrics` mostra ocupação e os últimos 100 registros de tempo/estado,
sem perguntas, respostas ou IDs dos pedidos. Os tempos incluem fila, busca,
geração, primeiro token de cada etapa, revisão e total. Primeiro token é uma
medida interna; não significa que o texto já foi liberado ao usuário.
`python_lifetime_peak_rss_mib` é o pico histórico de RSS do processo Python,
não o consumo incremental de uma requisição nem a memória do Ollama.

```bash
python3 -m unittest discover -s tests -v
python3 benchmark_performance.py
```

O benchmark usa as seis fontes versionadas em banco temporário e o Ollama real.
Não modifica a base do usuário nem descarrega um modelo que já esteja carregado.
Executa duas respostas e duas interrupções, aguardando tokens antes de cancelar
na geração e na revisão. Amostra RSS de Python e dos processos Ollama a cada 500 ms
e registra a alocação informada por `/api/ps` depois de cada execução.

O relatório `evaluation/performance.json` contém equipamento, versões, hashes,
estado inicial dos modelos e resultados. A pergunta de referência é sintética:
“Como a segurança das vacinas é avaliada?”. O relatório não armazena respostas.

Medição registrada em 24/09/2026: Apple M4, 24 GiB de RAM, Python 3.14.6,
Ollama 0.32.5, `qwen2.5:7b`. O modelo já estava carregado no início desta rodada.

| Execução | Geração | Revisão | Total do pipeline | Resultado |
|---|---:|---:|---:|---|
| Primeira da rodada | 1,83 s | 10,39 s | 12,22 s | Aprovação documental |
| Repetição | 6,31 s | 10,34 s | 16,66 s | Aprovação documental |

O tempo varia com cache e mudanças de contexto entre geração (8.192) e revisão
(16.384). Duas execuções não permitem estimar percentis ou estabelecer metas de
produção. Os números excluem HTTP do navegador, polling e apresentação progressiva.

- Pico amostrado de RSS Python, incluindo o benchmark: **35,47 MiB**.
- Pico amostrado da soma de RSS dos processos Ollama nesta rodada: **145,22 MiB**.
- Alocação informada pelo Ollama para o modelo após revisão: **5,08 GiB**.
- Cancelamento depois do primeiro token: worker encerrou em **0,4 ms** na geração
  e **0,5 ms** na revisão. Isso não mede quando a GPU ficou ociosa.

Em Apple Silicon, RSS não descreve toda a memória alocada ao modelo no dispositivo.
A soma de RSS pode contar páginas compartilhadas; não some RSS à alocação de
`/api/ps`. A amostragem pode perder picos. Não houve comparação controlada de
velocidade com a versão anterior; o ganho comprovado desta etapa é o controle do
fluxo, não uma aceleração da inferência.

## Verificação e pendências

Os testes cobrem fila/concorrência, sobrecarga, expiração, cancelamento nas duas
etapas com um servidor HTTP simulado, streams incompletos/com erro, proteção de
rascunhos, API e descarte de mensagens antigas. No macOS, JavaScriptCore executa
o `app.js` real com DOM/rede simulados para testar progresso, Cancelar e Limpar
durante a criação do pedido. Esses testes não verificam layout nem acessibilidade
real em um navegador.

A verificação visual ficou pendente: `agent-browser` não estava instalado e a
ferramenta de controle do computador não encontrou navegador disponível. Também
faltam testes prolongados de carga, dispositivo móvel e medições com perguntas
independentes. A aprovação documental automática continua sujeita a erros.
