O projeto funciona como um chatbot local com busca de informações em páginas oficiais. O navegador mostra a interface, mas o processamento acontece no servidor Python que você inicia no computador.

```text
Navegador → servidor Python → busca em fontes gov.br
                           → Ollama gera a resposta
                           → Ollama revisa o apoio nas fontes
Navegador ← resposta e links das fontes
```

1. **Você envia uma pergunta.** A interface a encaminha ao servidor local em `http://127.0.0.1:8002`. Se a pergunta depender do contexto anterior, o servidor considera as mensagens anteriores relevantes; caso contrário, trata-a como uma pergunta independente.

2. **O servidor procura fontes.** Para alguns assuntos — como vacinação, hepatite B, transmissão de HIV/AIDS e acesso a medicamentos — há páginas oficiais selecionadas diretamente. Para outras perguntas, o projeto consulta a busca do gov.br e tenta obter o conteúdo das páginas encontradas. Ele limita a quantidade de páginas e texto usado.

3. **O Ollama redige uma resposta.** O servidor envia a pergunta e os trechos encontrados ao Ollama, que roda localmente com o modelo `qwen2.5:7b`. A busca usa a internet; a geração da resposta acontece no seu computador.

4. **O Ollama revisa a resposta.** Uma segunda chamada verifica se as afirmações têm apoio nas fontes e se as citações correspondem às páginas apresentadas. Essa revisão também é feita pelo modelo. A interface espera a geração e a revisão terminarem antes de mostrar a resposta.

5. **Você vê a resposta e pode abrir as fontes.** Quando os trechos são insuficientes, irrelevantes ou contraditórios, o sistema pode responder que não encontrou informação suficiente. Isso pode acontecer mesmo com o Ollama funcionando normalmente: significa que a busca ou a revisão não considerou as fontes adequadas para responder com segurança.

**Limitação atual:** a busca combina páginas escolhidas para assuntos conhecidos com resultados de busca mais gerais. Ela ainda pode encontrar uma página oficial que não responde à pergunta. Além disso, a revisão é uma avaliação do próprio modelo, não uma confirmação humana ou uma checagem factual independente. O projeto é educativo e não substitui orientação de profissionais de saúde.