# Escopo e manutenção da base documental

Versão de trabalho: 2026-09-24. Escopo inicial adotado para desenvolvimento, sujeito ao ajuste pela equipe. Seis sínteses de fontes oficiais; todas com revisão documental por IA. A revisão documental por IA foi concluída; a confiabilidade das respostas geradas é avaliada separadamente.

## Temas e cobertura

| Tema | Documentos em `sources/` | Perguntas atendidas pelo conteúdo |
| --- | --- | --- |
| Análise de desinformação | `desinformacao.json`, `identificar-boatos.json` | O que é Saúde com Ciência? Onde informar conteúdo suspeito? Como identificar fake news e conferir origem e data? |
| Dengue | `dengue.json` | Como ocorre a transmissão? Quais medidas documentadas reduzem criadouros? |
| Antibióticos e antimicrobianos | `antibioticos.json`, `antimicrobianos-cuidados.json` | Antibióticos combatem vírus? Como o uso inadequado se relaciona à resistência? Pode compartilhar sobras? |
| Segurança geral das vacinas | `vacinas-seguranca.json` | Como a segurança é avaliada? Todas as reações são graves? |

Fora deste recorte: diagnóstico, prescrição, doses, interpretação de sintomas individuais, calendário e elegibilidade vacinal atual, tratamentos de outras doenças e verificação ao vivo de notícias. A fonte geral sobre segurança não responde, por exemplo, a alegações específicas sobre DNA. Os cumprimentos também não são resolvidos pela ampliação documental.

“Cobertura” significa existência de conteúdo para essas perguntas delimitadas, não cobertura completa do tema. O conjunto de desenvolvimento tem 18 casos, incluindo seis novos. Critério técnico inicial: recuperar a fonte esperada e manter os casos sem evidência. A equipe ainda precisa avaliar respostas geradas, perguntas independentes e suficiência do conteúdo antes do piloto.

## Novas fontes consultadas

| Síntese | Fonte e trecho utilizado | Publicação / atualização da página |
| --- | --- | --- |
| Identificar boatos | [Anvisa — Desinformação](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/desinformacao), seção “Como identificar” | Não identificadas; registradas como `null` |
| Segurança de vacinas | [Ministério da Saúde — As vacinas são seguras?](https://www.gov.br/saude/pt-br/vacinacao/faq/vacinas/as-vacinas-sao-seguras), resposta da FAQ | 2023-10-05 / 2023-10-05 |
| Cuidados com antimicrobianos | [Anvisa — Campanha de resistência microbiana](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2021/campanha-saiba-mais-sobre-resistencia-microbiana-e-como-combate-la), perguntas sobre causas e prevenção | 2021-11-22 / 2022-11-01 |

Conferência documental: Codex (IA), 2026-09-24. Cada JSON registra instituição, URL, datas, seção consultada e pendências. Os textos são sínteses, não transcrições. As páginas indicam CC BY-ND 3.0; aplicar a análise de reutilização descrita em [revisão das fontes](revisao-fontes.md), sem presumir autorização para adaptações.

Os três documentos adicionais têm status **Revisado por IA**, com conferência por Codex (IA) em 2026-09-24. A revisão humana não é requisito deste fluxo. A reutilização permanece uma avaliação separada. Consulte o registro consolidado em [revisão das fontes](revisao-fontes.md).

## Rotina manual de manutenção

Validação desta ampliação: 23 testes automatizados passaram e 18/18 casos de recuperação passaram; relatório em [evaluation/ampliacao.json](../evaluation/ampliacao.json). A primeira execução encontrou uma falha lexical na pergunta sobre fonte e data; a síntese foi ajustada para usar esses termos, presentes na fonte, e a avaliação foi repetida. Isso reforça que os casos são de desenvolvimento. Os seis documentos foram importados no SQLite local experimental. Não foi executada avaliação de geração pela LLM nesta etapa.

Frequência inicial: mensal, com próxima conferência do conjunto em **2026-10-24**, e antes de cada piloto. Conferir imediatamente quando surgir correção oficial, conflito de informações ou relato de erro. A data é um prazo interno proposto, não um prazo científico de validade. Não há agendamento nem expiração automáticos.

1. Abrir cada URL; conferir disponibilidade, autoria, datas, seção de origem e licença. Página acessível não garante conteúdo atualizado.
2. Comparar cada afirmação com a fonte. Não trocar a data de conferência sem efetivamente conferir. Manter datas desconhecidas como `null`.
3. Em caso de mudança, atualizar a síntese e seus metadados, marcar a revisão documental como pendente até nova conferência por IA e registrar decisão, responsável e motivo. Se a URL mudar, retirar a antiga para evitar duplicidade.
4. Executar `python -m unittest discover -s tests -v` e `python evaluate.py --output evaluation/ampliacao.json`. Revisar as respostas antes de aprovação; recuperação correta não comprova fidelidade.
5. Para o ambiente experimental local, importar com `python seed_knowledge.py`. Para publicação, resolver previamente as pendências de reutilização. A importação atual não impõe esse controle automaticamente.

### Retirar conteúdo desatualizado

Uma fonte contradita, incorreta ou sem respaldo suficiente deve sair da busca enquanto a equipe resolve a pendência. Um link temporariamente indisponível requer investigação, não prova falsidade.

1. Arquivar o JSON em `sources/retiradas/` e registrar motivo, data, responsável e eventual substituta na tabela abaixo. O carregador e o avaliador leem somente os JSONs diretamente em `sources/`.
2. Executar `python knowledge.py --remove-url "URL_EXATA_DO_DOCUMENTO"`. O comando remove somente os trechos dessa URL no SQLite, em transação. Não é necessário reiniciar o servidor para novas consultas.
3. Conferir a retirada pela busca e atualizar os casos de avaliação afetados, justificando a mudança. Conversas ou gerações já iniciadas podem conter trechos antigos; iniciar nova conversa após a retirada.

Mover o JSON sozinho não limpa o SQLite. Remover só do SQLite permite que a próxima carga reintroduza o documento. Por isso, executar ambos os passos. Para recuperar uma retirada equivocada, restaurar o JSON revisado em `sources/` e reimportá-lo.

| Data | URL / arquivo | Motivo | Responsável | Substituta / decisão |
| --- | --- | --- | --- | --- |
| — | Nenhuma retirada nesta ampliação | — | — | — |
