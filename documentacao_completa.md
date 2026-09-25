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

