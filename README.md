> **Demonstração pela internet:** modo temporário autenticado disponível; veja [como iniciar e encerrar](docs/internet-demo.md). A configuração local continua disponível.

# SUSANNA-HEALTHCHECK — projeto acadêmico

Chatbot educativo sobre desinformação em saúde. Interface independente, sem vínculo oficial com o SUS. Desenvolvido para apresentação na Eldorado.

## Guias do projeto

- [Instalação, uso e manutenção](docs/guia-projeto.md).
- [Dados processados, registros e privacidade](docs/privacidade.md).
- [Versões e licenças dos componentes](docs/componentes.md).
- [Responsáveis e rotina de manutenção](docs/responsabilidades.md).
- [Operação local, métricas, backup e recuperação](docs/disponibilizacao.md).

## Executar localmente

Ambiente verificado: macOS; Windows nativo não suportado atualmente. Requer Python 3.10+ com SQLite FTS5 e [Ollama](https://ollama.com/download). Sem pacotes pip, chave de API ou serviços pagos. O processamento usa os recursos do computador.

1. Inicie o Ollama pelo aplicativo ou, em um terminal, com `ollama serve`.
2. Se o modelo ainda não estiver instalado, execute `ollama pull qwen2.5:7b` (download de aproximadamente 4,7 GB, uma única vez).
3. Na primeira instalação, importe a base e inicie o servidor (em instalações existentes, faça backup antes de reimportar):

```bash
python3 seed_knowledge.py
python3 operations.py check
python3 server.py
```

4. Abra **http://127.0.0.1:8002**.

Use o servidor `server.py`, não `python3 -m http.server` nem o Live Server: eles não executam a API do chatbot. Não é necessário encerrar o servidor antigo da porta 8001.

Outra porta: `python3 server.py --port 8003`.
Outro modelo local instalado: `OLLAMA_MODEL=nome:tag python3 server.py`.

## Ambiente de disponibilização

Configurado para uso somente neste computador, sem publicação na rede. Veja
[o guia de operação local](docs/disponibilizacao.md) para prontidão, limites,
métricas, backup e recuperação. Verifique a base com `python3 operations.py check`
e o conjunto base/modelo em `http://127.0.0.1:8002/api/ready`.

## Organização

- `index.html`: página e chat.
- `styles.css`: aparência responsiva.
- `app.js`: conversa, histórico, espera e tratamento de falhas.
- `server.py`: arquivos públicos e API local que conversa com o Ollama.
- `jobs.py`: fila limitada, cancelamento, expiração e métricas em memória.
- `ollama_transport.py`: stream privado e conexão cancelável com o Ollama.

A conversa existe apenas em memória. O navegador envia até as últimas seis trocas e a nova pergunta ao servidor local. O servidor pode remover trocas antigas para respeitar seu orçamento conservador de contexto. Limpar ou recarregar reinicia o histórico e solicita cancelamento do pedido; o servidor fecha sua conexão com o Ollama. Históricos em processamento são liberados ao término; resultados ficam em memória por até 60 segundos, com limite de quantidade. O servidor do chat não grava conversas em disco. Scripts de avaliação gravam relatórios com casos e respostas; logs próprios do Ollama e do sistema não foram auditados. Os logs HTTP estão desativados. Veja [retenção e limites de privacidade](docs/privacidade.md).

O chat mostra fila, geração e revisão em andamento. O texto aparece progressivamente somente após a validação completa. Há botão **Cancelar**, uma execução por vez e até três pedidos em espera por padrão. Para configurar: `python3 server.py --concurrency 1 --queue-size 3`. Veja [desempenho, limites e medições](docs/desempenho-experiencia.md).

## Limites desta etapa

O chatbot consulta uma base documental local usando SQLite FTS5. O repositório inclui seis sínteses experimentais de fontes oficiais em `sources/`, com revisão documental por IA. Para carregar esse conjunto, execute `python3 seed_knowledge.py`. Veja [como cadastrar fontes e testar](docs/base-documental.md) e [escopo e manutenção](docs/escopo-fontes.md).

Os trechos enviados ao modelo são apresentados com suas referências. A busca lexical inclui expansão controlada de termos, correção simples de digitação e continuidade em formas como “e nesse caso?”. Veja [funcionamento e comparação da busca](docs/busca-conversa.md). Recuperar um trecho não comprova uma alegação. Ainda precisamos avaliar relevância, fidelidade das respostas e citações. Não se deve apresentar as respostas como checagem factual ou orientação médica.

Sem fontes, o servidor responde sem chamar a LLM. Com fontes, valida referências
e faz uma segunda revisão por IA do apoio documental, exigindo evidências literais
nas fontes citadas antes de exibir a resposta. A revisão pode errar e acrescenta
tempo de processamento. Veja [controle de respostas](docs/controle-respostas.md).

Depois de atualizar o código, reinicie `python3 server.py` e recarregue a página. Importar novos documentos não exige reinício.

## Avaliar a base inicial

```bash
python3 -m unittest discover -s tests -v
python3 evaluate.py
python3 evaluate_search.py
# Medições reais de tempo, memória e cancelamento (requer Ollama)
python3 benchmark_performance.py
# Opcional: também gerar respostas com o Ollama local
python3 evaluate.py --llm --output evaluation/llm.json
```

A avaliação usa uma base temporária com o conjunto versionado, sem alterar seus documentos locais. Veja [fontes e critérios de avaliação](docs/avaliacao-inicial.md).

## Piloto e entrega

[Pacote do piloto local](piloto/README.md): roteiro, formulário, critérios propostos,
problemas e aceite. Pré-piloto em 25/09/2026: 67 testes passaram; regressão real
do revisor 4/5, com F01 reproduzido. Versão candidata, sem aprovação final.

## Aceitação e revisão humana

Novos cenários e instruções de revisão estão em [aceitação e testes adversariais](docs/aceitacao.md).
A rodada real obteve **5/14** nos critérios automáticos do fluxo HTTP e **4/5** no
revisor isolado. Foi observada aceitação indevida de uma resposta contraditória
quando a fonte incluía uma instrução maliciosa ao revisor; isso bloqueia a aprovação
do piloto. Revisões humanas e verificação real de navegador/celular permanecem pendentes.

O [pacote de revisão](evaluation/acceptance.human.md) contém as perguntas, respostas
exibidas, fontes e campos pendentes para duas pessoas. Os relatórios são de testes
sintéticos, sem gravação de conversas reais de usuários.

```bash
python3 audit_interface.py --output evaluation/interface-nova-rodada.json
python3 evaluate_acceptance.py --output evaluation/acceptance-nova-rodada.json
python3 evaluate_grounding.py --cases evaluation/review-acceptance-cases.json --output evaluation/review-nova-rodada.json
```

## Referências técnicas

- [API de conversa do Ollama](https://docs.ollama.com/api/chat)
- [Modelo Qwen2.5](https://ollama.com/library/qwen2.5)

# 👤 Autor

**Guilherme Barros**

<img src="https://github.com/dida0982.png" width="150" alt="Foto de perfil">

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/guilherme-barros-6a0369209/)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dida0982)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/guilherme_barros_jr/)
