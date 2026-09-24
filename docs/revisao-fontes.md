# Revisão das três sínteses da base

Conferência documental por IA (Codex): 2026-09-24. Status: Revisado por IA. A pedido do responsável pelo projeto, revisão humana não é requisito deste fluxo. Esta conferência compara os textos locais com as páginas indicadas; não certifica adequação clínica nem autoriza sua publicação.

## Resultado da conferência

| Documento | Evidência na fonte | Resultado e pendência |
| --- | --- | --- |
| [Antibióticos](../sources/antibioticos.json) | Seção “Pandemia”: uso inadequado, resistência e distinção entre infecções virais e bacterianas. | Conteúdo central sustentado. Tornar explícita a condição de infecção bacteriana diagnosticada, em vez de apenas “associada”. |
| [Dengue](../sources/dengue.json) | Seções “Transmissão” e “Prevenção”: vias de transmissão e medidas contra criadouros. | Síntese compatível com o recorte. Manter fora do escopo critérios atuais de vacinação e diagnóstico individual. |
| [Desinformação](../sources/desinformacao.json) | Seções “Sobre o Saúde com Ciência”, “Estrutura de atuação” e “Envio de conteúdos para análise”. | Síntese compatível; canal FalaBr identificado na página. O envio não comprova que um conteúdo foi checado. |

### Antibióticos

Fonte: [Anvisa — Pandemia pode aumentar o risco de resistência microbiana](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2020/pandemia-pode-aumentar-o-risco-de-resistencia-microbiana).

Publicação confirmada: 2020-11-20. Modificação confirmada: 2022-11-03. É uma notícia do contexto da pandemia, não um protocolo atualizado de prescrição. A extração inicial trouxe apenas cabeçalho e rodapé; o corpo foi recuperado pelo resultado de busca da mesma URL oficial. Essa limitação da recuperação foi registrada na conferência por IA.

A ressalva sobre medicamento, dose e duração é um limite editorial do projeto. Não é uma orientação individual extraída da notícia. Sugestão para revisão: substituir “Uma infecção bacteriana associada pode justificar sua utilização após avaliação profissional” por “Quando uma infecção bacteriana também é diagnosticada, o uso de antibióticos depende de avaliação profissional”. O texto cadastrado ainda não foi alterado.

### Dengue

Fonte: [Ministério da Saúde — Dengue](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/dengue).

A página sustenta a transmissão principal pelo mosquito, as vias raras e as medidas preventivas listadas. A vacinação não substitui o controle vetorial. O resumo não promete eficácia imediata para interromper uma epidemia. As restrições sobre vacinação e diagnóstico são limites editoriais do projeto.

Datas de publicação e atualização não identificadas no conteúdo consultado: manter `null`. Datas históricas citadas no corpo e o ano do rodapé não são datas de atualização da página.

### Desinformação

Fonte: [Ministério da Saúde — Saúde com Ciência](https://www.gov.br/saude/pt-br/assuntos/saude-com-ciencia).

Coordenação, atividades e canal mencionados na síntese encontram apoio na página. A observação de que uma manifestação não equivale a uma checagem concluída é uma ressalva editorial. A iniciativa dá foco inicial à vacinação; a síntese não deve ser apresentada como promessa de análise de qualquer tema.

Datas de publicação e atualização não identificadas no conteúdo consultado: manter `null`.

## Condições de reutilização

As páginas indicam CC BY-ND 3.0 no rodapé. A [descrição oficial da licença](https://creativecommons.org/licenses/by-nd/3.0/deed.pt-br) prevê atribuição e restringe distribuição de material modificado. Também ressalva elementos em domínio público e usos abrangidos por exceções aplicáveis.

O aviso de licença, isoladamente, não resolve o enquadramento destas sínteses. A equipe precisa registrar a base para o uso pretendido: autorização, condição de reutilização aplicável ou outra justificativa verificada. Não presumir que citar a URL autoriza adaptações, nem que todo resumo factual é necessariamente uma obra derivada. A licença do código não licencia o conteúdo de terceiros. A decisão sobre reutilização permanece pendente para os três documentos.

## Registro de revisão por IA

Responsável: Codex (IA). Data: 2026-09-24. Status dos seis documentos: **Revisado por IA**. As evidências dos três documentos adicionais estão em [escopo e fontes](escopo-fontes.md).

Esta decisão substitui a exigência de revisão humana documental. Não registra aprovação humana, clínica ou institucional. A análise de reutilização permanece separada do status documental.

| Documento | Resultado |
| --- | --- |
| antibioticos.json | Revisado por IA; melhoria de precisão sugerida acima |
| dengue.json | Revisado por IA |
| desinformacao.json | Revisado por IA |
| identificar-boatos.json | Revisado por IA |
| vacinas-seguranca.json | Revisado por IA |
| antimicrobianos-cuidados.json | Revisado por IA |

Os JSONs registram `review_status`, `reviewed_at` e o responsável em `documentary_check.checked_by`. Alterações no conteúdo exigem nova conferência por IA. O índice SQLite mantém apenas título, texto, URL e data; o restante fica nos JSONs versionados. Os hashes dos documentos desta versão estão em `evaluation/revisao-ia.json`.
