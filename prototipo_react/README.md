# Susana — Meu SUS Digital

Protótipo React/Vite de uma interface conceitual do Meu SUS Digital com a assistente Susana.

## Executar

Requisito: Node.js `20.19+` ou `22.12+`.

No terminal, entre na pasta do protótipo, que contém o `package.json`. Se estiver na raiz do repositório, execute:

```bash
cd prototipo_react
npm install
npm run dev
```

Se o terminal estiver em `Documents` e a pasta do repositório se chamar `SUSANNA-HEALTHCHECK`, use `cd SUSANNA-HEALTHCHECK/prototipo_react` antes dos comandos `npm`.

O Vite exibirá um endereço local no terminal (por exemplo, `http://localhost:5173/`). Abra esse endereço no navegador.

> Não execute `npm install` ou `npm run dev` em uma pasta que não contenha o `package.json` do protótipo. Entre em `prototipo_react` antes de executar os comandos `npm`.

Se aparecer `vite: command not found`, confirme que está na pasta do protótipo e execute `npm install` novamente antes de `npm run dev`.

## Escopo

O chatbot é uma simulação frontend. As respostas atuais são locais e servem para demonstrar UX, contexto, estados de recuperação e fontes. A integração real com RAG + LLM deve substituir a função `createReply` por uma chamada ao backend.
