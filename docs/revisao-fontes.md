# Revisão das três sínteses da base

Conferência documental por IA (Codex): 2026-09-24. Revisão e aprovação humanas: pendentes. Esta conferência compara os textos locais com as páginas indicadas; não certifica adequação clínica nem autoriza sua publicação.

## Resultado da conferência

| Documento | Evidência na fonte | Resultado e pendência |
| --- | --- | --- |
| [Antibióticos](../sources/antibioticos.json) | Seção “Pandemia”: uso inadequado, resistência e distinção entre infecções virais e bacterianas. | Conteúdo central sustentado. Tornar explícita a condição de infecção bacteriana diagnosticada, em vez de apenas “associada”. |
| [Dengue](../sources/dengue.json) | Seções “Transmissão” e “Prevenção”: vias de transmissão e medidas contra criadouros. | Síntese compatível com o recorte. Manter fora do escopo critérios atuais de vacinação e diagnóstico individual. |
| [Desinformação](../sources/desinformacao.json) | Seções “Sobre o Saúde com Ciência”, “Estrutura de atuação” e “Envio de conteúdos para análise”. | Síntese compatível; canal FalaBr identificado na página. O envio não comprova que um conteúdo foi checado. |

### Antibióticos

Fonte: [Anvisa — Pandemia pode aumentar o risco de resistência microbiana](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2020/pandemia-pode-aumentar-o-risco-de-resistencia-microbiana).

Publicação confirmada: 2020-11-20. Modificação confirmada: 2022-11-03. É uma notícia do contexto da pandemia, não um protocolo atualizado de prescrição. A extração inicial trouxe apenas cabeçalho e rodapé; o corpo foi recuperado pelo resultado de busca da mesma URL oficial. A equipe deve conferir o corpo diretamente antes da aprovação.

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

## Registro de revisão humana

Preencher somente após a conferência real. “Pendente” não equivale a reprovação nem aprovação. Registrar separadamente revisor e aprovador, mesmo quando forem a mesma pessoa. Não incluir CPF, contato ou outros dados pessoais desnecessários.

| Documento | Revisor e função | Data da revisão | Parecer e correções | Base para reutilização | Aprovador | Data da aprovação | Decisão |
| --- | --- | --- | --- | --- | --- | --- | --- |
| antibioticos.json | A definir | — | Pendente | Pendente | A definir | — | Pendente |
| dengue.json | A definir | — | Pendente | Pendente | A definir | — | Pendente |
| desinformacao.json | A definir | — | Pendente | Pendente | A definir | — | Pendente |

Ao concluir cada revisão, registrar aqui o identificador do commit ou hash SHA-256 do JSON aprovado. Uma alteração posterior do texto exige nova conferência. Guardar o parecer ou sua referência junto ao registro.

## Como concluir esta etapa

1. Cada revisor lê o JSON e a fonte, confere cada afirmação, contexto e ressalvas e decide sobre a correção proposta.
2. A equipe registra as condições de reutilização e resolve eventuais dúvidas antes da aprovação para publicação.
3. Preenche o registro acima com nomes, datas, parecer e versão efetivamente revisada; atualiza `human_review` no JSON correspondente somente após a decisão.
4. Se o conteúdo mudar, reimporta explicitamente com `python seed_knowledge.py` e executa a avaliação existente antes do uso. A importação substitui os documentos pela URL e preserva os demais.

Os campos de conferência nos JSONs são metadados documentais. O importador atual não aplica bloqueio por aprovação humana nem armazena esses campos adicionais no SQLite. Nenhuma importação ou alteração da base em execução foi realizada nesta etapa.

**Estado: conferência por IA registrada; revisão humana e decisão sobre reutilização pendentes.**
