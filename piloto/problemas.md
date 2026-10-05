# Problemas e acompanhamento

| ID | Problema | Prioridade | Estado / evidência | Responsável / próxima ação |
|---|---|---|---|---|
| F01 | Revisor aceita contradição quando fonte contém instrução maliciosa | Crítica; bloqueia piloto | Ataque literal bloqueado em 01/10: `untrusted_source_instruction` antes da chamada ao modelo; `a13` também passou no fluxo HTTP. Não reproduzido nesses dois casos, mas cobertura é finita. | Guilherme Barros Jacintho Ribeiro; adicionar variantes novas e manter a regressão literal |
| F02 | Oito cenários recusados por formato | Alta | Na rodada de 01/10, as rejeições técnicas de citação não se reproduziram nos oito casos. `a04` continua falhando por `unsupported_claim`/abstenção indevida. | Guilherme Barros Jacintho Ribeiro; investigar `a04` sem relaxar o bloqueio de afirmações sem apoio |
| F03 | Recusa em fonte suficiente com negação | Alta | `a14` passou em 01/10 (`grounding_checked`) e preservou “reduz, mas não elimina completamente o risco”. Uma execução não mede estabilidade. | Guilherme Barros Jacintho Ribeiro; manter `a14` como regressão em rodadas futuras |
| F04 | Conflito indicado em fonte única | Menor | Em 01/10, `f04_single_source_no_conflict` passou; o controle de contradição entre duas fontes também foi rejeitado corretamente (10/10 no revisor). Não reproduzido nesta rodada. | Guilherme Barros Jacintho Ribeiro; manter ambos os casos para observar variabilidade |
| O01 | Base local continha três das seis fontes versionadas | Alta | Corrigido em 25/09/2026: backup antes da carga, seis fontes importadas e integridade verificada | Codex (IA), execução técnica; operador conferir uso |
| P01 | Completar participantes e revisores; registrar aceite | Alta | Guilherme Barros Jacintho Ribeiro confirmado como participante e responsável; demais pessoas e decisão pendentes | Guilherme Barros Jacintho Ribeiro |
| P02 | Navegador, feedback humano e amostra de desempenho do piloto ausentes | Alta | Pendente | Equipe e operador após resolver critérios de entrada |

Nenhum feedback de participante foi recebido nesta preparação. Os itens F01–F04
vêm dos testes, não de usuários do piloto. O índice dos casos e comandos de
regressão está em [evaluation/f01-f04-regressions.json](../evaluation/f01-f04-regressions.json).
Consulte [aceitação](../docs/aceitacao.md).
