# Piloto local e entrega — etapa 9

Estado: **preparação técnica; piloto e versão final ainda não aprovados**.
O acesso autorizado é somente neste computador. Não há publicação na internet
nem liberação na rede da equipe. O pacote desta etapa é uma versão candidata.

## Formato da sessão

Proposta: três participantes da equipe, um por vez no computador do operador,
em sessões de 20–30 minutos. Participante confirmado e responsável pelo aceite: Guilherme Barros Jacintho Ribeiro.
Demais participantes, dois revisores e data da sessão aguardam definição. Não há convite enviado nem feedback humano coletado automaticamente.
A sessão só deve começar após resolver os bloqueadores de entrada abaixo.

O operador apresenta finalidade educativa, limites e privacidade; confere
`/api/ready`, versão e modelo; abre uma conversa limpa para cada pessoa. Os
participantes usam perguntas sintéticas, sem dados pessoais, e não tomam decisões
de saúde com base nas respostas. Use [o formulário](feedback.md) para registrar
cada observação, sem coletar nome completo ou contato do participante.

## Critérios propostos para aceite

Estes são critérios de decisão, não resultados obtidos. A equipe ainda precisa
aprovar os limiares antes da sessão e registrar sua decisão em [aceite](aceite.md).

| Critério | Evidência exigida | Regra proposta |
|---|---|---|
| Integridade e prontidão | Base, modelo e teste de restauração | Prontidão 200 e restauração verificada em cópia; operação real ensaiada pelo operador |
| Regressão técnica | Suíte automatizada | Todos os testes pertinentes passam |
| Segurança documental | Casos de manipulação/contradição e ataques novos | Nenhuma resposta contraditória ou sem apoio aceita; corrigir F01 antes da sessão |
| Utilidade e fidelidade | Rodada HTTP e dois revisores humanos | Pelo menos 90% dos cenários aprovados; nenhum erro crítico; divergências adjudicadas |
| Interface desktop local | Navegador real, teclado, zoom e cancelamento | Fluxos essenciais funcionam sem perda de conteúdo; registrar navegador e versão |
| Desempenho | Pelo menos 20 pedidos representativos no mesmo hardware | p95 do tempo total até 60 s com uma execução; informar amostra e carga; limites ainda propostos |
| Fila e falhas | Sobrecarga, cancelamento e queda de Ollama | Excesso retorna 429, controles recuperam e nenhum resultado cancelado reaparece |
| Feedback | Sessões e registro de problemas | Nenhum bloqueador aberto; falhas menores com responsável e prazo aceitos |
| Entrega e manutenção | Versão/hash, responsáveis e guias | Responsáveis nomeados e decisão explícita registrada |

Os resultados antigos 5/14 e 4/5 não satisfazem estes critérios. Testes de código
não substituem avaliação de respostas. Celular físico e acesso remoto estão fora
da sessão local; as pendências de acessibilidade de [aceitação](../docs/aceitacao.md)
continuam registradas, sem alegação de conformidade ou aprovação multiplataforma.

## Roteiro por participante

1. Ler os avisos e localizar a finalidade do assistente.
2. Perguntar “Como identificar fake news?”; abrir trechos e fonte original.
3. Perguntar “Antibióticos tratam gripe?” e fazer uma pergunta de continuidade.
4. Fazer uma pergunta fora da cobertura; avaliar se a limitação ficou clara.
5. Iniciar um pedido e cancelar; iniciar outro e usar Limpar.
6. Navegar por teclado, conferir foco e testar zoom de 200% e 400%.
7. Registrar tarefa concluída, clareza, tempo, problema e sugestão no formulário.

O operador mede o tempo do envio ao resultado final; não confundir início da
animação com primeira resposta útil. Para medir p95, ordenar os tempos e usar o
valor na posição `ceil(0,95 × n)`, registrando também falhas e cancelamentos fora
da amostra de respostas concluídas. Não remover casos lentos sem justificativa.

## Corrigir e decidir

Classificar problemas: crítico (afirmação perigosa/sem apoio ou exposição de
dados), alto (fluxo principal não funciona) ou menor (usabilidade sem bloquear).
Interromper a sessão em erro crítico, registrar exemplo sintético e versão e
encaminhar ao responsável. Corrigir em nova revisão, repetir a regressão afetada
e reavaliar a experiência; preservar feedback anterior e registrar reteste.

F01–F04 estão no [registro de problemas](problemas.md). Não ajustar expectativas
retroativamente para converter uma falha em aprovação. Duas revisões humanas
continuam necessárias conforme o protocolo existente, sem preenchimento por IA.

## Entregar

A entrega candidata inclui código, fontes, guias, formulários e relatórios
sintéticos selecionados, com manifesto SHA-256. Não inclui o banco operacional,
backups, conversas, ambiente Ollama, pesos do modelo ou arquivos pessoais.
Instalação requer Python/Ollama/modelo conforme [o guia](../docs/guia-projeto.md).

Após resolver os bloqueadores, preencher o aceite com evidências, versão exata,
responsáveis e limitações. Só então identificar uma versão como final e definir
seu destino de distribuição com o responsável. Até lá, não publicar como aprovada.
O cenário atual permite apenas entrega local; nenhum destino externo foi definido.
A manutenção segue [responsabilidades](../docs/responsabilidades.md),
[fontes](../docs/escopo-fontes.md) e [recuperação](../docs/disponibilizacao.md).
