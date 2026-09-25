# Disponibilização local — etapa 7

Cenário escolhido: somente neste computador. O servidor escuta em
`127.0.0.1:8002`; o Ollama é acessado em `127.0.0.1:11434`. Não há publicação,
encaminhamento de portas nem autenticação de usuários. Pessoas e programas com
acesso à sessão do computador podem usar a aplicação e as métricas.

## Inicialização e verificação

Requer Python 3.10+ com SQLite FTS5 e Ollama com o modelo `qwen2.5:7b`.
Na pasta do projeto:

```bash
# Terminal 1, se o aplicativo Ollama não estiver em execução:
ollama serve
# Terminal 2, somente se ainda faltar o modelo:
ollama pull qwen2.5:7b
# Somente para importar/atualizar as fontes versionadas:
python3 seed_knowledge.py
python3 operations.py check
python3 server.py --port 8002 --concurrency 1 --queue-size 3
```

Abra http://127.0.0.1:8002. Em outro terminal:

```bash
curl --fail http://127.0.0.1:8002/api/ready
curl --fail http://127.0.0.1:8002/api/metrics
```

`/api/ready` retorna 200 apenas quando o banco está íntegro, tem trechos, permite
consulta FTS e o modelo consta no Ollama; caso contrário retorna 503.
Não executa uma geração nem certifica a qualidade das respostas.
`/api/health` continua verificando apenas o Ollama/modelo por compatibilidade.

O processo fica no terminal, sem inicialização automática. Encerre com Ctrl+C.
Para atualizar o código, pare, aplique a versão desejada, execute os testes e
reinicie. A configuração do comando deve ser mantida no reinício.

## Acesso e conexões

HTTP é usado somente no loopback, sem tráfego do chat pela rede. Não há TLS
neste cenário. Não abra túneis nem exponha a porta do Ollama. O servidor valida
Host e Origin para os endereços locais e aplica política de conteúdo, bloqueio de
incorporação em frames e ausência de Referer. Somente os quatro arquivos públicos
listados no servidor podem ser servidos; o banco e os fontes Python não são rotas.
As APIs usam `Cache-Control: no-store`. Os logs HTTP foram desativados para evitar
registro de URLs, parâmetros ou identificadores de pedidos.

Isso não substitui autenticação nem protege contra programas locais maliciosos.
O servidor atual é apropriado à execução local experimental. O módulo
[`http.server` não é recomendado para produção](https://docs.python.org/3/library/http.server.html).
Rede da equipe e internet ficam fora desta configuração; exigiriam servidor de
produção, autenticação, HTTPS, controle por usuário e nova validação operacional.

## Limites e métricas

| Controle | Configuração atual |
|---|---|
| Execuções simultâneas | 1; `--concurrency` aceita 1 a 4 |
| Fila de espera | 3; `--queue-size` aceita 0 a 16; excesso recebe 429 |
| Espera na fila | Até 120 s |
| Execução | Até 360 s; cancelamento cooperativo |
| Pedido sem acompanhamento | Cancelado após aproximadamente 20 s |
| Resultado concluído | Até 60 s em memória; limite adicional de quantidade |
| Corpo de requisição | Até 150.000 bytes |
| Pergunta | Até 3.000 caracteres; histórico até 13 mensagens |
| Leitura do socket HTTP | Timeout de 10 s |

A fila limita trabalhos de IA, não conexões HTTP. Não há limite de requisições por
minuto nem proteção de carga hostil. Por isso a exposição permanece local.

`/api/metrics` informa execuções ativas, espera, capacidade e os últimos 100
trabalhos concluídos: estado, tempos por etapa, motivo de cancelamento e pico de
memória do Python durante sua vida. Não contém perguntas, respostas ou IDs.
As métricas são voláteis e reiniciam com o processo; não incluem a memória do modelo.

Antes de cada demonstração, confira `/api/ready`. Durante uso, confira as métricas
se houver lentidão. Investigue prontidão 503, fila continuamente cheia, erros ou
cancelamentos por timeout repetidos. Não aumente concorrência sem medir tempo e
memória com `benchmark_performance.py`. Não há alertas automáticos nesta etapa.

## Backup e recuperação

Faça backup antes de cada importação ou atualização da base. Use um nome novo:

```bash
mkdir -p backups
python3 operations.py backup --destination backups/knowledge-antes-da-atualizacao.sqlite3
```

O comando usa a [API de backup SQLite](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup),
que permite cópia consistente com a base em uso, verifica a cópia e cria o arquivo
com permissão 600. Recusa sobrescrever arquivos. `backups/` não entra no Git.
Mantenha as últimas três cópias válidas e copie uma para mídia separada, sob
controle do responsável pelo computador; a pasta local não protege contra perda
do disco. A seleção e remoção das cópias antigas são manuais.

Para restaurar, **pare o servidor e qualquer importação**. Preserve o diretório
atual, incluindo eventuais arquivos auxiliares SQLite. Use um nome de diretório
que ainda não exista:

```bash
python3 operations.py check --source backups/knowledge-antes-da-atualizacao.sqlite3
mv data data-antes-da-recuperacao
mkdir data
python3 operations.py backup --source backups/knowledge-antes-da-atualizacao.sqlite3 --destination data/knowledge.sqlite3
python3 operations.py check
python3 server.py --port 8002 --concurrency 1 --queue-size 3
```

Confira `/api/ready` e uma pergunta de referência após o reinício. Em falha,
preserve os arquivos e investigue antes de retomar o uso. Sem backup, é possível
recriar a base com `seed_knowledge.py`, mas documentos locais não versionados
precisam de seus JSONs originais. Versione fontes revisadas e código juntos.

Reiniciar perde trabalhos, resultados e métricas em memória; o usuário deve
reenviar a pergunta. Em falha do Ollama, reinicie-o e confira o modelo. Porta
ocupada: use `--port 8003` e ajuste as URLs. Meta operacional proposta: recuperar
em até 30 minutos com cópia disponível, perdendo no máximo as alterações desde
o último backup; esse tempo ainda não foi medido em exercício completo.

## Validação e pendências

Testes automatizados cobrem cópia e restauração em banco temporário, recusa de
sobrescrita, origem/Host externos, arquivos privados e prontidão sem modelo/base.
Execute `python3 -m unittest discover -s tests -v`.
A restauração de produção e a geração real não são executadas pelos novos testes.

A preparação local não aprova o piloto: continuam os bloqueadores documentados em
[aceitação](aceitacao.md), incluindo fidelidade e revisão humana.

## Documentação complementar

Consulte [instalação e uso](guia-projeto.md), [dados e retenção](privacidade.md),
[componentes](componentes.md) e [responsabilidades](responsabilidades.md).
