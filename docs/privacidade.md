> **Novo modo de demonstração:** quando iniciado por `internet_demo.py`, o tráfego passa pela Cloudflare. Consulte [fluxo externo, autenticação e logs](internet-demo.md). A descrição local abaixo aplica-se a `server.py`.

# Dados processados e registros mantidos

Registro técnico conferido no código em 25/09/2026. Escopo: aplicação local com
Ollama em `127.0.0.1`, sem conta de usuário, autenticação gov.br ou acesso a dados
do SUS. Este documento descreve a implementação, sem declarar conformidade jurídica.

## Fluxo e finalidade

A pergunta e até seis trocas anteriores passam do navegador ao servidor Python.
A busca usa a pergunta e, quando aplicável, perguntas anteriores para recuperar
fontes. O servidor envia instruções, contexto e trechos ao Ollama local. Quando
há evidências, o modelo gera a resposta e recebe uma segunda solicitação para
revisar seu apoio documental. Sem fontes, o fluxo pode responder sem chamar a IA.
A resposta validada e os trechos retornam ao navegador.

Não envie nome, CPF, contato, identificação de terceiros ou informações pessoais
de saúde. O texto é livre: a aplicação não anonimiza nem impede a inserção desses
dados. Não há uso das conversas para treinamento implementado pelo projeto.

## Inventário e retenção

| Dados | Onde / para quê | Retenção e remoção |
|---|---|---|
| Perguntas, respostas e conversa visível | Memória JavaScript e página, para conversa e continuidade | Limpar ou recarregar reinicia o histórico; não há cookies, localStorage ou sessionStorage implementados |
| Histórico recebido e prompt | Memória Python e processamento do Ollama, para busca, geração e revisão | Referência ao histórico do trabalho liberada ao término; não há gravação intencional pelo servidor |
| ID aleatório, estado e resultado do pedido, fontes e erros | Memória da fila, para acompanhar/cancelar e obter resposta | Resultado por aproximadamente até 60 s após conclusão; limpeza periódica e descarte adicional por quantidade; cancelamento descarta o resultado |
| Tempos por etapa, estado, motivo de cancelamento e pico de memória Python | `/api/metrics`, diagnóstico operacional | Últimos 100 trabalhos, sem perguntas, respostas ou IDs; perdidos ao encerrar o processo |
| Documentos e metadados de fontes | `sources/*.json` e Git; cadastro e rastreabilidade | Persistem até manutenção explícita; histórico Git pode preservar versões removidas |
| Título, texto, URL e data de revisão dos trechos | `data/knowledge.sqlite3`, busca documental | Persistem até substituição ou retirada; não são histórico de conversas |
| Cópias da base | `backups/` ou destino escolhido, recuperação | Retenção manual proposta de três cópias válidas; mídia separada também precisa de gestão |
| Perguntas sintéticas, respostas geradas, fontes, critérios e medições | `evaluation/`, produzidos por scripts executados pelo operador | Arquivos persistentes, alguns versionados; sem exclusão automática |

Pedidos sem acompanhamento expiram em aproximadamente 20 s; há limites de espera
e execução descritos em [disponibilização](disponibilizacao.md). Cancelar ou
Limpar não apaga instantaneamente todas as referências de memória. Limpar não
remove relatórios de avaliação, documentos nem backups. Remover uma referência
em Python/JavaScript não equivale a sobrescrever a memória fisicamente.

## Logs, acesso e conexões externas

O servidor desativa logs HTTP em `Handler.log_message`; a inicialização mostra
endereço e modelo. A fila usa mensagens genéricas para falhas internas. Não há
arquivo de logs de conversa implementado. Falhas fora desse tratamento podem
produzir diagnóstico no terminal; revise antes de compartilhar.

Não foi auditada a retenção dos logs próprios do Ollama, do sistema operacional,
do navegador ou de extensões. Histórico de navegação, cache de página, memória
virtual, diagnósticos e ferramentas de desenvolvimento não são geridos pelo
botão Limpar. Não se promete ausência absoluta de vestígios no computador.

A API não autentica pessoas. Programas e pessoas com acesso local podem consultá-la;
o ID do pedido concede acesso ao resultado enquanto existir. Não compartilhe
IDs, capturas do painel de rede ou dumps de memória. Os arquivos locais dependem
das permissões da conta e do disco; o projeto não criptografa o SQLite ou backups.

O fluxo configurado do chat usa apenas loopback e modelo local. Downloads de
Python/Ollama/modelos e atualizações precisam de acesso externo. Clicar em uma
fonte abre o site da instituição, sujeito às práticas desse site. A aplicação
não consulta as páginas ao responder nem inclui analytics externos no frontend.

## Cuidados operacionais e incidentes

Use conta protegida e bloqueie a sessão ao se afastar. Restrinja acesso aos
arquivos. Nos testes, utilize exemplos sintéticos, sem reaproveitar conversas
pessoais nos relatórios. Ao comunicar um erro, informe sintoma, horário, versão e
um exemplo fictício suficiente para reproduzir; não cole dados pessoais.

Se inserir informação pessoal por engano, use Limpar. Caso necessário, encerre o
servidor e o Ollama para interromper processamento. Verifique se houve cópia em
relatórios, capturas ou arquivos e encaminhe ao responsável pela operação para
remoção controlada. Se houver material no Git, apagar o arquivo atual não elimina
seu histórico: o responsável pelo código deve avaliar o alcance e a correção.
Não destrua fontes ou evidências de diagnóstico sem avaliar o que foi afetado.

Responsáveis e canal de encaminhamento estão em [responsabilidades](responsabilidades.md).
Qualquer mudança para rede, nuvem, contas ou novos registros exige atualizar este
inventário antes do uso nesse cenário.
