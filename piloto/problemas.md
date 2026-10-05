# Problemas e acompanhamento

| ID | Problema | Prioridade | Estado / evidência | Responsável / próxima ação |
|---|---|---|---|---|
| F01 | Instruções maliciosas podem influenciar a revisão | Crítica; ainda bloqueia piloto | Em 05/10, os padrões cobertos foram barrados antes do modelo; `verificador-hardening` passou 10/10 e `a13` passou por quarentena no fluxo HTTP. A detecção é heurística e finita; ataques inéditos e revisão humana seguem pendentes. | Guilherme Barros Jacintho Ribeiro; manter regressões e ampliar avaliação independente |
| F02 | Recusas por formato e citações | Alta | A avaliação HTTP sintética de 05/10 passou 14/14; isso mede critérios automáticos nesta rodada, não estabilidade nem qualidade geral. | Guilherme Barros Jacintho Ribeiro; manter cenários e revisar respostas com duas pessoas |
| F03 | Recusa em fonte suficiente com negação | Alta | O caso `a14` passou na avaliação de 05/10; uma execução não mede estabilidade. | Guilherme Barros Jacintho Ribeiro; manter `a14` como regressão em rodadas futuras |
| F04 | Conflito indicado em fonte única | Menor | Os casos de conflito do revisor passaram na rodada 10/10 de 05/10; uma execução não mede estabilidade. | Guilherme Barros Jacintho Ribeiro; manter ambos os casos para observar variabilidade |
| O01 | Base local continha três das seis fontes versionadas | Alta | Corrigido em 25/09/2026: backup antes da carga, seis fontes importadas e integridade verificada | Codex (IA), execução técnica; operador conferir uso |
| P01 | Completar participantes e revisores; registrar aceite | Alta | Guilherme Barros Jacintho Ribeiro confirmado como participante e responsável; demais pessoas e decisão pendentes | Guilherme Barros Jacintho Ribeiro |
| P02 | Revisão em navegador e feedback humano ausentes | Alta | Benchmark sintético ao vivo concluído (20 casos, 1 repetição); revisão real em navegador, feedback humano e repetição maior seguem pendentes | Equipe e operador após resolver critérios de entrada |

Nenhum feedback de participante foi recebido nesta preparação. Os itens F01–F04
vêm dos testes, não de usuários do piloto. O índice dos casos e comandos de
regressão está em [evaluation/f01-f04-regressions.json](../evaluation/f01-f04-regressions.json).
Consulte [aceitação](../docs/aceitacao.md).
