Abra **dois terminais**.

**1. Primeiro terminal: iniciar o Ollama**

Se ainda não estiver instalado, instale pelo [site oficial](https://ollama.com/download). Depois execute:

```bash
ollama serve
```

Deixe esse terminal aberto. Se aparecer que a porta `11434` já está em uso, o Ollama pode já estar rodando pelo aplicativo.

**2. Segundo terminal: baixar o modelo**

```bash
ollama pull qwen2.5:7b
```

O download só é necessário na primeira vez. Para testar a LLM diretamente:

```bash
ollama run qwen2.5:7b
```

Digite uma pergunta. Para sair da conversa, use `/bye`.

**3. Iniciar o servidor do projeto**

No segundo terminal:

```bash
cd /Users/aluno2/Desktop/saude-gov-br
python3 server.py
```

O projeto atual não precisa de instalação de pacotes com `pip`.

**4. Abrir o chatbot**

Acesse: [http://127.0.0.1:8002](http://127.0.0.1:8002)

Para conferir a conexão entre o servidor e a LLM, abra: [http://127.0.0.1:8002/api/health](http://127.0.0.1:8002/api/health). O resultado esperado inclui `"ready": true`.

Se a porta `8002` estiver ocupada:

```bash
python3 server.py --port 8003
```

Nesse caso, acesse [http://127.0.0.1:8003](http://127.0.0.1:8003).

**Nas próximas vezes:** basta garantir que o Ollama esteja aberto e executar `python3 server.py`. Para parar o servidor, pressione `Ctrl+C` no terminal correspondente.