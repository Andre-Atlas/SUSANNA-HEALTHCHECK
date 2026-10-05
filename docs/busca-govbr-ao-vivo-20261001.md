# Protótipo de busca ao vivo em páginas gov.br — 2026-10-01

## Objetivo e fluxo

O servidor consulta páginas oficiais ao vivo. Para perguntas sobre vacinação, acessa diretamente a página [Vacinação](https://www.gov.br/saude/pt-br/vacinacao); para perguntas sobre fontes, boatos ou desinformação em saúde, acessa [Saúde com Ciência](https://www.gov.br/saude/pt-br/assuntos/saude-com-ciencia); para perguntas sobre hepatite B, acessa a página [Hepatite B](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/h/hepatites-virais/hepatite-b) do Ministério da Saúde. São páginas HTTPS `gov.br`.

Para os demais temas, envia os termos de busca à API oficial SERPRO usada pelo portal gov.br, em `https://portalunico.estaleiro.serpro.gov.br/api/search/`, solicitando relevância e tipos `Servico|Tema`. O filtro de site do Ministério foi removido porque eliminava resultados válidos; a API pode retornar conteúdo de outros órgãos públicos. A resposta JSON serve somente para localizar URLs candidatas. O servidor aceita URLs HTTPS sob `gov.br`, segue redirecionamentos somente nesse domínio e baixa cada página com o leitor HTML; texto ou resumos retornados pela API não são usados como evidência.

O fluxo: pergunta atual (já contextualizada pela conversa) → extração dos termos de busca (removendo expressões interrogativas comuns) → rota temática direta ou busca SERPRO por tipos `Servico|Tema` → leitura de até cinco resultados candidatos e
extração de no máximo três páginas HTML gov.br → geração e revisão por evidências literais → resposta com
links e horário local da consulta informado pelo servidor. A resposta não usa os documentos locais em
`sources/`; esses continuam úteis para avaliação offline e manutenção do projeto.

## Restrição de domínio

`govbr_search.py` aceita apenas URLs HTTPS sem credenciais cujo host seja
`gov.br` ou termine em `.gov.br`. Cada redirecionamento é verificado antes de
seguir, a URL final é conferida novamente, e a interface também só cria links
para esses domínios. Resultado fora da regra é descartado. O conteúdo retornado
por uma página é tratado como dado não confiável, não como instrução para o
modelo.

Nesta primeira etapa são aceitas páginas HTML/XHTML. PDFs, documentos anexos,
resultados ilegíveis e páginas com pouco texto ficam de fora. A busca do portal
pode não cobrir toda página do governo; mesmo quando o host é permitido, isso
não comprova que o conteúdo seja apropriado, atual ou clinicamente validado. A
resposta ainda precisa ser sustentada pelo trecho e passar pela revisão
automática existente.

## Falhas e latência

Uma indisponibilidade da API SERPRO ou das páginas-fonte retorna erro de busca e
não consulta a LLM. Uma busca concluída sem trecho extraível leva à abstenção
sem fontes. A busca lê no
máximo três resultados e usa timeout por requisição; pode acrescentar alguns
segundos de espera antes da geração. Cancelar o pedido fecha a conexão de leitura
quando ela já está aberta. O modo fica dependente de uma conexão de internet e
das regras técnicas do portal gov.br.

Não há fallback silencioso aos JSONs locais: isso mantém a condição “responder
somente com fontes gov.br consultadas ao vivo”. Também não se consulta estoque
local de medicamentos nem se garante que toda pergunta tenha resposta no portal.

## Privacidade

Apenas os termos de busca extraídos da pergunta atual são enviados à API em
`portalunico.estaleiro.serpro.gov.br`; portanto, não fica somente no computador.
A aplicação não envia o histórico completo para a busca, apenas a pergunta atual
após a resolução de continuidade. A LLM permanece local via Ollama. Retenção,
logs e processamento do lado da API e do portal não foram auditados; não envie
dados pessoais ou detalhes identificadores de saúde.

## Próximas melhorias

1. Registrar um conjunto de perguntas representativas e verificar fontes, taxa
   de extração, respostas apoiadas e tempo de ponta a ponta.
2. Inspecionar falhas de HTML real e resultados duplicados; melhorar o extrator
   mantendo apenas dados públicos de páginas permitidas.
3. Considerar suporte a PDFs oficiais com uma biblioteca local gratuita, depois
   de medir tamanho, qualidade de extração e impacto de latência.
4. Ampliar a pesquisa para outros portais e serviços do governo somente se o
   host das páginas fonte continuar validado por `.gov.br`.

Esta é uma primeira integração técnica, não uma afirmação de cobertura de todo o
SUS. Hospedagem em gov.br, por si só, não atesta a correção da resposta.
