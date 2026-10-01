# Avaliação focal de respostas — 30/09/2026

## Pergunta sobre antibióticos

A pergunta “Posso tomar antibiótico por conta própria quando estou com uma
infecção?” recuperava a fonte atual da SBI e uma síntese antiga da Anvisa que já
havia sido substituída. O banco local ainda tinha os dois registros porque o
carregador não aplicava o metadado `replaces_url`. O modelo citava ambos; o revisor
confirmava o apoio da fonte da SBI, mas não devolvia evidência para a citação
redundante. O código então recusava a resposta com `unchecked_citation`.

Em outra pergunta, sobre antibióticos e gripe, o revisor marcou como não apoiada
uma conclusão expressamente presente nas fontes. Isso produzia uma abstenção
indevida. Os rascunhos e pareceres foram examinados apenas durante a depuração e
não foram adicionados ao histórico da conversa; o relatório final contém somente
as respostas controladas e seus estados.

## Mudanças realizadas

- A síntese da SBI explicita que antibióticos não devem ser tomados por conta
  própria e que a decisão depende de avaliação profissional.
- `seed_knowledge.py` aplica `replaces_url` depois que a fonte substituta é
  importada, preservando outros documentos da base.
- As instruções pedem o menor número de citações necessário e dão ao revisor um
  exemplo curto de paráfrase fiel sobre antibióticos e gripe. A revisão continua
  obrigatória.
- Leituras de arquivos JSON, HTML, CSS e JavaScript usadas pelos avaliadores
  especificam UTF-8. Isso evita que o Windows transforme acentos de perguntas em
  caracteres incorretos durante os testes.
- Foi corrigido o tratamento de uma tentativa de citação quando uma chamada de
  teste fornece um prompt vazio.

## Resultados

O relatório da rodada com `qwen2.5:7b` está em
[`evaluation/antibiotics-focused-20260930-final.json`](../evaluation/antibiotics-focused-20260930-final.json).
Os três cenários — automedicação, antibiótico para gripe e uso de sobras —
terminaram em `grounding_checked`, com uma fonte SBI e sem erros de validação.
Os tempos desta rodada ficaram entre 20,86 e 21,62 segundos; são medições desta
máquina e não uma garantia de latência.

Depois, a pergunta original foi enviada à API HTTP local reiniciada e à URL
pública autenticada. Ambas retornaram `grounding_checked`, com a fonte SBI e sem
erros de validação. A demonstração pública está em
<https://what-attended-saturday-equity.trycloudflare.com>.

A suíte automatizada terminou com **76 testes aprovados e 8 ignorados**. Os
ignorados dependem de JavaScriptCore nativo do macOS, indisponível nesta máquina
Windows. A avaliação é focalizada e automatizada; não é revisão clínica nem
validação independente. O piloto geral continua sujeito aos bloqueios e à revisão
humana descritos em [aceitação](aceitacao.md).

Fontes conferidas: [Sociedade Brasileira de Infectologia — antibiótico não
trata gripe](https://infectologia.org.br/noticias/antibiotico-nao-trata-gripe-riscos-da-automedicacao-e-resistencia-bacteriana/)
e [Anvisa — resistência microbiana](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2021/campanha-saiba-mais-sobre-resistencia-microbiana-e-como-combate-la).
