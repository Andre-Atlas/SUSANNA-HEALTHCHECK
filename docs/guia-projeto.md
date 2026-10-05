# Guia de instalação, uso e manutenção

Consolidado em 25/09/2026 para execução somente neste computador.

## Instalar e iniciar

O projeto oferece execução local para Windows 10/11 e macOS com Python 3.10+
(incluindo SQLite FTS5), Ollama e modelo local. O chat não exige dependências pip,
npm, chave de API ou serviço pago. Consulte [versões e licenças](componentes.md).

1. Instale Python 3.10+ e Ollama pelos [sites oficiais](https://www.python.org/downloads/)
   e [Ollama](https://ollama.com/download). Abra a pasta do projeto no terminal.
2. Abra o aplicativo Ollama ou execute `ollama serve` em outro terminal. Instale o
   modelo uma vez com `ollama pull qwen2.5:7b`.
3. Inicie o servidor com os comandos da sua plataforma. A base SQLite é mantida para avaliações e manutenção offline; o chat pesquisa páginas oficiais gov.br por pergunta.

**Windows (PowerShell):**

```powershell
py -3 server.py --port 8002 --concurrency 1 --queue-size 3
```

**macOS (Terminal):**

```bash
python3 server.py --port 8002 --concurrency 1 --queue-size 3
```

Abra http://127.0.0.1:8002. Confira http://127.0.0.1:8002/api/ready antes do uso.
`ready: true` verifica Ollama/modelo; não consulta gov.br nem aprova o conteúdo
das respostas. Para cadastrar fontes na base offline, siga [base documental](base-documental.md)
e faça backup antes de reimportar.

Nas próximas vezes, abra o Ollama e inicie `py -3 server.py` (Windows) ou
`python3 server.py` (macOS). Não use Live Server nem `python -m http.server`:
eles não executam a API.
Não exponha as portas à rede. Para parar, pressione Ctrl+C no terminal do servidor.

## Usar o chatbot

Escreva uma pergunta geral sobre os temas da [base](escopo-fontes.md), sem nome,
CPF, identificação de terceiros ou relatos pessoais de saúde. Enter envia;
Shift+Enter quebra a linha. Cada pergunta aceita até 3.000 caracteres.

A interface mostra fila, geração e revisão. O texto aparece gradualmente após a
validação; não mostra o rascunho do modelo. Expanda os trechos e confira a fonte
original antes de interpretar uma conclusão. Abrir a fonte acessa um site externo.
Ausência de evidências e bloqueio da revisão não significam que a alegação é falsa.

**Cancelar** interrompe o pedido atual, preservando a conversa anterior.
**Limpar** solicita cancelamento, apaga a conversa exibida e inicia outra.
Recarregar também reinicia o histórico. O servidor recebe até seis trocas
anteriores e a pergunta atual. Consulte [dados e retenção](privacidade.md).

O assistente é experimental e educativo, sem vínculo oficial com o SUS. Não
oferece diagnóstico, prescrição ou checagem factual certificada. Os bloqueadores
do piloto estão em [aceitação](aceitacao.md).

## Resolver problemas

| Sintoma | Ação |
|---|---|
| Porta ocupada | Inicie com `--port 8003` e use essa porta no navegador e nas verificações. |
| Ollama indisponível | Abra o aplicativo ou execute `ollama serve`; confira `/api/ready`. |
| Modelo ausente | Execute `ollama pull qwen2.5:7b`; confira se `OLLAMA_MODEL` foi alterado. |
| Pesquisa gov.br indisponível | Tente novamente mais tarde; `/api/ready` não verifica o acesso externo. |
| Fila cheia | Aguarde ou cancele seu pedido; não aumente a concorrência sem medir o hardware. |
| Resposta bloqueada ou sem evidências | Confira a cobertura da base; registre um caso sintético para investigação. |
| Interface antiga | Reinicie o servidor depois de atualizar código e recarregue a página. |

## Manter e atualizar

Antes de atualizar, registre o commit (`git rev-parse HEAD`), versões e modelo;
faça backup da base e preserve alterações locais. Pare o servidor, aplique uma
versão revisada e execute:

Use `py -3` no lugar de `python3` nos comandos abaixo no Windows.

```bash
python3 -m unittest discover -s tests -v
python3 operations.py check  # valida apenas a base local de avaliação/manutenção
```

Reinicie, confira `/api/ready` e faça uma pergunta de referência. Para mudanças de
modelo ou resposta, execute também as avaliações descritas no [README](../README.md),
usando saídas novas quando houver suporte a `--output`. Avaliações podem gravar
perguntas, respostas e fontes; utilize casos sintéticos. Não sobrescreva os
relatórios históricos sem intenção de substituí-los.

Para atualizar fontes, siga [a rotina mensal e de retirada](escopo-fontes.md), com
backup antes da importação. O conteúdo e os metadados completos ficam em
`sources/`; editar o JSON não atualiza o SQLite automaticamente. Para recuperar,
siga [o procedimento operacional](disponibilizacao.md#backup-e-recuperação).

Atualize os guias quando mudarem comandos, dados, retenção ou componentes.
A [matriz de responsabilidades](responsabilidades.md) define quem executa e registra
cada atividade. Não há atualização, backup ou alerta automático nesta versão.
