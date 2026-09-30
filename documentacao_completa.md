# Documentação consolidada — SUSANNA-HEALTHCHECK

Preparei a etapa 7 para **uso somente neste computador**.

- Proteção de acesso local e cabeçalhos de segurança.
- `/api/ready` para verificar base e modelo.
- Comando de backup com verificação de integridade.
- Guia com limites, métricas e recuperação.
- README e `documentacao.md` atualizados.

**Validação:** 67 testes passaram; a base atual passou na verificação de integridade.

Consulte o [guia de disponibilização local](/Users/aluno2/Desktop/saude-gov-br/docs/disponibilizacao.md). O exercício completo de recuperação e os bloqueadores de qualidade do piloto continuam pendentes.

Consolidei a documentação da etapa 8:

- [Instalação, uso e manutenção](/Users/aluno2/Desktop/saude-gov-br/docs/guia-projeto.md).
- [Versões e licenças](/Users/aluno2/Desktop/saude-gov-br/docs/componentes.md).
- [Privacidade e retenção de dados](/Users/aluno2/Desktop/saude-gov-br/docs/privacidade.md).
- [Responsabilidades por função](/Users/aluno2/Desktop/saude-gov-br/docs/responsabilidades.md).

README e `documentacao.md` atualizados; links locais verificados.

Preparei o [pacote candidato para entrega local](/Users/aluno2/Desktop/saude-gov-br/dist/susanna-candidata-20260925.zip), com roteiro, formulário de feedback, critérios de aceite e manutenção. Registrei Guilherme Barros Jacintho Ribeiro como responsável.

- **67 testes passaram.**
- Base atualizada para seis fontes, com backup.
- Revisor real: **4/5**, reproduzindo a falha de aceitar uma resposta contraditória.

**O piloto e a publicação final continuam pendentes:** é necessário corrigir esse bloqueador e coletar avaliações reais da equipe. Nenhum feedback ou aceite foi preenchido em nome dos participantes.

Sim — você está falando da pasta **`sources/`**. Hoje, as peças se integram assim:

```text
Arquivos JSON em sources/
          ↓ python3 seed_knowledge.py
Base pesquisável SQLite
          ↑
Sua pergunta → busca RAG → trechos relevantes
                                  ↓
                      Pergunta + trechos → Ollama
                                              ↓
                                     Modelo gera resposta
                                              ↓
                                  Código e IA revisam
                                              ↓
                               Resposta + fontes na tela
```

**O RAG é esse processo de buscar informações e entregá-las ao modelo antes de ele responder.** O Ollama executa o modelo de IA; ele não lê automaticamente a pasta `sources/`.

Os arquivos em `sources/` guardam o conteúdo e sua origem. O comando de importação coloca esse conteúdo no banco SQLite. Quando você pergunta, o sistema busca até três trechos relacionados e os fornece ao modelo. Isso **não treina o modelo**: fornece material de consulta para aquela resposta.

Sobre juntar o trabalho da equipe: **se seus amigos têm os conteúdos em arquivos `.md`, podemos transformá-los no mesmo formato JSON usado pelo projeto.** Hoje o importador aceita JSON, não Markdown diretamente.

O caminho seria:

1. Cada pessoa entrega seus documentos `.md`, com título, conteúdo e links das fontes originais.
2. Conferimos duplicidades, contradições e origem das informações.
3. Convertemos os documentos para JSON, preservando os metadados de fonte e revisão.
4. Colocamos os JSONs aprovados na mesma pasta `sources/`.
5. Fazemos backup e executamos `python3 seed_knowledge.py` para atualizar a base compartilhada.

**Não precisamos juntar tudo em um arquivo enorme.** Podemos manter um documento por fonte ou assunto, com nomes diferentes. O RAG procura entre todos os documentos importados.

Um cuidado: arquivos `.md` que explicam instalação, código ou reuniões são documentação do projeto; não devem entrar automaticamente na base de evidências de saúde. Precisamos identificar quais contêm material que o chatbot deve consultar.

Como o sistema está local, cada colega que executar sua própria cópia precisará receber os JSONs e importá-los. Podemos compartilhar esses arquivos pelo Git; o banco SQLite é gerado em cada computador.

**Os `.md` dos seus amigos contêm informações de saúde com fontes ou são documentação dos projetos deles?** Isso define como vamos integrar o material.


==================

1. **Corrigir a revisão das respostas — prioridade máxima**
   - Há uma falha conhecida: o revisor aceitou uma resposta contraditória quando a fonte continha uma instrução maliciosa.
   - Precisamos reforçar a separação entre documentos e instruções e testar novamente.
   - Quando faltar apoio nas fontes, o chatbot deve dizer que não consegue confirmar.

=====================

Implementei a correção:

- Separei os documentos das instruções de sistema.
- Comandos explícitos de manipulação nas fontes agora bloqueiam a geração e a revisão.
- Nesses casos, o chatbot informa que não encontrou evidência suficiente.

**Validação:** 73 testes automatizados, 5/5 casos de regressão e 8/8 casos complementares passaram.

O servidor local já está atualizado: **[abrir chatbot](http://127.0.0.1:8002)**. A sessão antiga do ngrok precisa ser reiniciada para carregar a correção.

Registrei os resultados na documentação. A falha conhecida está bloqueada, mas o filtro não detecta toda manipulação e a IA ainda pode errar.

===================

2. **Melhorar a base de fontes**
   - Hoje existem apenas seis sínteses experimentais, revisadas por IA.
   - Conferir o conteúdo com as publicações originais e ampliar os temas que você quer perguntar.
   - Registrar título, instituição, link e data de revisão de cada fonte.

========================

Ampliei a base de **6 para 12 documentos**, já disponíveis no chatbot.

- Reconferi cinco fontes anteriores e substituí a referência de antibióticos por uma publicação da SBI.
- Acrescentei **gripe, tuberculose, hipertensão, HIV, raiva e SAMU 192**.
- Registrei título, instituição, link, data de revisão e seções consultadas.
- Fiz backup e corrigi uma confusão da busca entre doenças.

**Validação:** 75 testes passaram; busca com continuidade: 38/38. Isso verifica recuperação das fontes, não garante a correção de todas as respostas.

[Consultar fontes e revisão](/Users/aluno2/Desktop/saude-gov-br/docs/revisao-fontes-20260929.md) · [Testar chatbot](http://127.0.0.1:8002)

===================

3. **Garantir que a busca encontre o trecho certo**
   - Testar perguntas informais, erros de digitação e diferentes formas de perguntar.
   - Melhorar perguntas de continuidade, como “e em crianças?”.
   - Pedir esclarecimento quando a pergunta for ambígua.

=====================

Ampliei a base de **6 para 12 documentos**, já disponíveis no chatbot.

- Reconferi cinco fontes anteriores e substituí a referência de antibióticos por uma publicação da SBI.
- Acrescentei **gripe, tuberculose, hipertensão, HIV, raiva e SAMU 192**.
- Registrei título, instituição, link, data de revisão e seções consultadas.
- Fiz backup e corrigi uma confusão da busca entre doenças.

**Validação:** 75 testes passaram; busca com continuidade: 38/38. Isso verifica recuperação das fontes, não garante a correção de todas as respostas.

[Consultar fontes e revisão](/Users/aluno2/Desktop/saude-gov-br/docs/revisao-fontes-20260929.md) · [Testar chatbot](http://127.0.0.1:8002)

=======================

4. **Exibir fontes que realmente sustentem a resposta**
   - Vincular as afirmações aos trechos utilizados.
   - Mostrar título e link da publicação.
   - Não tratar a presença de uma referência como prova de que a resposta está correta.

========================

Ampliei a base de **6 para 12 documentos**, já disponíveis no chatbot.

- Reconferi cinco fontes anteriores e substituí a referência de antibióticos por uma publicação da SBI.
- Acrescentei **gripe, tuberculose, hipertensão, HIV, raiva e SAMU 192**.
- Registrei título, instituição, link, data de revisão e seções consultadas.
- Fiz backup e corrigi uma confusão da busca entre doenças.

**Validação:** 75 testes passaram; busca com continuidade: 38/38. Isso verifica recuperação das fontes, não garante a correção de todas as respostas.

[Consultar fontes e revisão](/Users/aluno2/Desktop/saude-gov-br/docs/revisao-fontes-20260929.md) · [Testar chatbot](http://127.0.0.1:8002)

======================


Atualizei o projeto para oferecer um caminho de execução no **Windows e no macOS**:

- O servidor tolera a ausência de `resource` no Python do Windows; a métrica de memória fica sem valor nessa plataforma.
- Os guias principais agora trazem comandos separados para PowerShell e Terminal do macOS.
- O modo de demonstração procura `cloudflared` e `ngrok` no PATH e aceita executáveis `.exe` no Windows. Senhas, tokens e logs da demonstração ficam no diretório de dados do usuário, fora da pasta do projeto.
- A interface aponta para o README quando não encontra o servidor.

Comece pelas instruções em [README.md](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/README.md), [guia do projeto](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/docs/guia-projeto.md) e [guia de demonstração pela internet](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/docs/internet-demo.md).

**Não consegui executar os comandos nem validar o projeto nos dois sistemas nesta sessão**, pois Python não está disponível no terminal de trabalho. `git diff --check` não apontou erros de whitespace. Portanto, as instruções foram atualizadas, mas a execução em Windows e macOS ainda precisa ser confirmada na prática.

A documentação também registra a falha F01 na revisão de respostas. Ela continua pendente; a adaptação multiplataforma não resolve esse problema, então o projeto ainda não deve ser tratado como aprovado para um piloto de saúde.

======================


A resposta foi **bloqueada pela validação de citações**, não simplesmente por falta de fontes. A base já tinha trechos sobre automedicação e avaliação profissional. Um relatório anterior registra uma falha semelhante: o modelo respondeu, mas omitiu a citação obrigatória no fim do parágrafo; o sistema descartou a resposta. Isso torna provável que tenha ocorrido o mesmo aqui, embora o registro desta tentativa não esteja disponível para confirmar o motivo exato.

Fiz uma alteração em [server.py](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/server.py): se o modelo esquecer ou errar o formato das citações, o servidor tenta gerar a resposta mais uma vez. A resposta ainda precisa passar pela revisão de apoio nas fontes; se falhar nessa revisão, continua bloqueada.

Quanto à cobertura: os trechos sustentam uma resposta geral de que não se deve começar antibiótico por conta própria. A SBI orienta que antibióticos sem avaliação profissional são uma prática de risco e que a decisão de usá-los exige avaliação de um profissional de saúde. Como a fonte trata principalmente de infecções respiratórias, o chatbot deve deixar esse limite claro ao responder sobre “uma infecção” em geral. [Orientação da SBI](https://infectologia.org.br/noticias/antibiotico-nao-trata-gripe-riscos-da-automedicacao-e-resistencia-bacteriana/)

Não executei testes nem uma nova conversa com o Ollama nesta sessão, então a correção ainda precisa ser confirmada rodando o projeto.

======================


Analisei o código e a documentação. **O projeto já funciona como protótipo**, com chat, busca em fontes locais, integração com Ollama, interface, documentação para Windows e macOS e um modo de demonstração pela internet. Mas os próprios registros do projeto indicam que ele **ainda não está aprovado para um piloto com público**.

## O que falta primeiro

1. **Resolver os problemas de confiabilidade das respostas.** A avaliação documentada registra um caso crítico em que o revisor aceitou uma resposta contraditória após receber uma fonte com instruções maliciosas. Também registra respostas recusadas por problemas de formato e um caso de recusa apesar de haver fonte suficiente. Esses pontos estão em [docs/aceitacao.md](/C:/Users/dida0/OneDrive/%C3%81rea%20de%20Trabalho/SUSANNA-HEALTHCHECK/docs/aceitacao.md:11). O relatório cita 5 de 14 cenários aprovados; a rodada isolada do revisor ficou em 4 de 5.

2. **Fazer revisão humana do conteúdo e das respostas.** As 12 fontes atuais são sínteses experimentais revisadas por IA. O projeto ainda registra revisores humanos e aceite como pendentes. Como é um chatbot sobre saúde, as fontes e exemplos de resposta precisam ser avaliados por pessoas com experiência adequada antes de apresentá-los como confiáveis.

3. **Ampliar e revisar a cobertura da busca.** Os problemas recentes com perguntas como “Recebi uma mensagem suspeita” mostram que uma fonte relevante pode não aparecer para uma formulação comum. As recusas podem ser a decisão mais segura quando falta evidência, mas muitas falhas de recuperação tornam o chatbot pouco útil. É preciso revisar casos reais de busca e adicionar conteúdo confiável para as perguntas que o projeto quer atender.

4. **Validar a experiência em dispositivos reais.** A documentação registra verificações pendentes em navegador, celular, teclado e leitor de tela. Também é preciso confirmar a instalação e o funcionamento em máquinas Windows e macOS, não apenas manter instruções para esses sistemas.

## Antes de divulgar pela internet

O modo atual é uma demonstração temporária que depende do seu computador e de um túnel; não é uma hospedagem permanente. A documentação também descreve uma credencial compartilhada e informa que perguntas passam pela infraestrutura do provedor do túnel. Para uso público contínuo, ainda faltariam hospedagem estável, controle de acesso adequado, uma decisão documentada sobre dados e registros, monitoramento e um procedimento de recuperação. Veja [docs/internet-demo.md](/C:/Users/dida0/OneDrive/%C3%81rea%20de%20Trabalho/SUSANNA-HEALTHCHECK/docs/internet-demo.md:3) e [docs/privacidade.md](/C:/Users/dida0/OneDrive/%C3%81rea%20de%20Trabalho/SUSANNA-HEALTHCHECK/docs/privacidade.md:1).

## Documentação a organizar

Há informações que precisam ser reconciliadas antes de compartilhar o repositório: o README anuncia um link temporário como ativo, enquanto o guia da demonstração registra falhas de conexão em datas posteriores à criação do link. Confirme o estado atual antes de divulgá-lo. Além disso, [documentacao_completa.md](/C:/Users/dida0/OneDrive/%C3%81rea%20de%20Trabalho/SUSANNA-HEALTHCHECK/documentacao_completa.md:24) contém um caminho local de outro computador, que não funcionará para quem receber o projeto.

**Em resumo:** para uma apresentação acadêmica, o principal é explicar claramente os limites e mostrar uma demonstração revisada. Para convidar pessoas a usar o chatbot, primeiro é necessário resolver o bloqueador de confiabilidade, revisar o conteúdo com pessoas qualificadas e validar o fluxo em dispositivos reais. Para mantê-lo disponível na internet, também será necessário substituir o túnel temporário por uma implantação apropriada.

Não executei testes nem alterei arquivos nesta análise; os resultados citados são os registrados na documentação do projeto.

============================

Corrigi a causa da recusa e confirmei a pergunta original pelo servidor local **e pela demonstração pública**.

O banco ainda continha a antiga síntese da Anvisa, apesar de ela ter sido substituída pela fonte da SBI. O modelo citava as duas; o revisor só confirmava evidência para a SBI, e o sistema bloqueava a resposta por `unchecked_citation`. A carga agora remove a fonte antiga quando a nova declara `replaces_url`. Também ajustei as instruções para preferir apenas as citações necessárias.

**Resultado após as mudanças:** as três perguntas avaliadas — automedicação, antibiótico para gripe e uso de sobras — passaram como `grounding_checked`, sem erros de validação. A pergunta original também passou pelo endpoint HTTP local e pelo link público. Uma resposta gerada foi: “Não pode tomar antibiótico por conta própria quando estiver com uma infecção. O uso exige avaliação de um profissional de saúde. [1]” Essa orientação está de acordo com a [SBI](https://infectologia.org.br/noticias/antibiotico-nao-trata-gripe-riscos-da-automedicacao-e-resistencia-bacteriana/) e a [Anvisa](https://www.gov.br/anvisa/pt-br/assuntos/noticias-anvisa/2021/campanha-saiba-mais-sobre-resistencia-microbiana-e-como-combate-la).

A suíte terminou com **76 testes aprovados e 8 ignorados**; os ignorados dependem de JavaScriptCore nativo do macOS. As três respostas levaram cerca de **21 segundos cada** nesta máquina.

Atualizei [server.py](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/server.py), [sources/antibioticos.json](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/sources/antibioticos.json) e a rotina de carga em [seed_knowledge.py](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/seed_knowledge.py). Registrei o diagnóstico e os resultados em [docs/avaliacao-respostas-20260930.md](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/docs/avaliacao-respostas-20260930.md) e [evaluation/antibiotics-focused-20260930-final.json](/C:/Users/dida0/OneDrive/Área%20de%20Trabalho/SUSANNA-HEALTHCHECK/evaluation/antibiotics-focused-20260930-final.json). Fiz backup do banco antes de atualizá-lo.

O link público agora é [what-attended-saturday-equity.trycloudflare.com](https://what-attended-saturday-equity.trycloudflare.com); a reinicialização renovou também a senha. O usuário continua `equipe`; consulte a senha no arquivo privado `%LOCALAPPDATA%\SUSANNA-HEALTHCHECK\internet\access.json`.

Essa melhora foi confirmada para três perguntas, mas não torna o chatbot clinicamente validado nem resolve todos os bloqueios gerais do piloto. A revisão foi automatizada pelo mesmo modelo; ainda falta avaliação humana independente.