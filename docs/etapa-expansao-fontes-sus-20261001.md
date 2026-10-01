# Ampliação inicial das fontes do SUS — 2026-10-01

## Objetivo

Reduzir lacunas evidentes da base local do chatbot, começando pela pergunta
“Você tem remédio para HIV?” e por perguntas básicas sobre o SUS. A base atual
é pequena e não cobre “tudo sobre o SUS”; esta etapa acrescenta quatro sínteses
de páginas do Ministério da Saúde. O chatbot continua consultando somente os
documentos locais importados, não essas páginas ao vivo.

## Fontes consultadas e cobertura adicionada

| Arquivo | Fonte oficial | Cobertura pretendida |
| --- | --- | --- |
| `sources/sus-visao-geral.json` | [Sistema Único de Saúde (SUS)](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/sus) | O que é o SUS, tipos gerais de serviço, princípios e esferas de gestão. |
| `sources/hiv-tratamento-sus.json` | [Tratamento de HIV — Ministério da Saúde](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aids-hiv/tratamento/tratamento) | Existência de distribuição gratuita de antirretrovirais no SUS para pessoas que necessitam de tratamento. Não responde a estoque ou farmácia local. |
| `sources/sus-medicamentos-cesaf.json` | [Componente Estratégico da Assistência Farmacêutica](https://www.gov.br/saude/pt-br/composicao/sectics/daf/cesaf/componente-estrategico-da-assistencia-farmaceutica) | Enquadramento de HIV/aids no CESAF e fluxo de distribuição entre União, estados, DF e municípios. |
| `sources/sus-medicamentos-ceaf.json` | [Componente Especializado da Assistência Farmacêutica](https://www.gov.br/saude/pt-br/composicao/sectics/daf/ceaf) | Noções gerais sobre solicitação de medicamentos incluídos no CEAF, seus protocolos e organização estadual. A síntese explicita que isso não é o percurso específico dos ARV para HIV. |

As páginas de HIV e SUS afirmam a oferta gratuita de tratamento antirretroviral
e a abrangência geral do SUS. A síntese não copia listas de esquemas ou doses,
que exigem avaliação profissional e podem mudar. O chat não consulta estoque
local e não deve afirmar que uma unidade específica tem medicamento disponível.

O portal [Saúde de A a Z](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/)
serve como índice temático para novas ampliações. O [catálogo de publicações do
Ministério da Saúde](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes)
é outro lugar para localizar manuais, protocolos, boletins e notas técnicas.
Para futuras integrações de dados estruturados, existe o [Portal de Dados
Abertos do SUS](https://dadosabertos.saude.gov.br/); ele não é, por si só, uma
base pronta de respostas conversacionais.

## Alterações no projeto

- Adicionadas as quatro sínteses JSON acima, seguindo os metadados existentes.
- Adicionados sinônimos lexicais para medicamento/remédio e antirretroviral/
  ARV em `knowledge.py`, para perguntas em linguagem comum encontrarem os
  termos oficiais usados pela fonte.
- Adicionados casos de recuperação em `tests/test_source_catalog.py`, incluindo
  a frase exata “Você tem remédio para HIV?”.
- Atualizadas referências à contagem de fontes no README e na documentação da
  base.
- Os metadados indicam conferência por IA. A análise de reutilização/adaptação
  das fontes permanece pendente; a página de tratamento HIV declara licença
  CC BY-ND 3.0, por isso não se deve redistribuir esta adaptação antes de
  esclarecer as condições aplicáveis.

## Validação e operação local

Antes da importação, foi criado o backup
`backups/knowledge-before-sus-sources-20261001.sqlite3`. Depois, as 16 fontes
versionadas foram importadas por `seed_knowledge.py`; `operations.py check`
confirmou uma base íntegra com 16 trechos. A suíte completa passou: 76/76 testes.
Os casos específicos confirmam que “Você tem remédio para HIV?” inclui a nova
fonte de tratamento, distinta da fonte antiga sobre transmissão. Porém, a busca
lexical também inclui fontes adjacentes e, para essa frase exata, pode ordenar
primeiro o CEAF por coincidências em “medicamento”. A formulação “O SUS oferece
antirretroviral de graça?” coloca a fonte de HIV primeiro. Portanto, esta etapa
amplia cobertura, mas deixa registrada uma falha de ordenação para melhorar numa
próxima alteração focada em busca/ranking.

Estes resultados são cobertura de busca, não prova de que cada resposta gerada
pela LLM está fiel à fonte. Eles também não significam que o chatbot agora
responde sobre todos os serviços, medicamentos, regras estaduais ou situações
clínicas do SUS. As próximas ampliações devem partir de perguntas reais sem
resposta, priorizar fontes oficiais específicas e adicionar regressões para
cada novo tema.
