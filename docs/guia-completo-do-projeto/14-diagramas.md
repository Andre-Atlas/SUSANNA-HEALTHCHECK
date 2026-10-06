# 14. Diagramas

## Pergunta no modo local

```mermaid
sequenceDiagram
    actor Pessoa
    participant UI as Navegador (app.js)
    participant API as server.py
    participant Fila as JobQueue (jobs.py)
    participant Busca as SERPRO/gov.br
    participant LLM as Ollama local
    Pessoa->>UI: Envia pergunta
    UI->>API: POST /api/jobs
    API->>API: Valida JSON e mensagens
    API->>Fila: Enfileira trabalho
    API-->>UI: 202 + ID do job
    loop polling
        UI->>API: GET /api/jobs/{id}
        API-->>UI: queued/running/done
    end
    Fila->>API: process_messages
    API->>API: Resolve contexto
    API->>Busca: Consulta lexical e URLs
    Busca-->>API: Trechos HTML gov.br
    API->>LLM: Gera resposta citada
    LLM-->>API: Rascunho completo
    API->>API: Valida referências
    API->>LLM: Revisa suporte/IDs
    LLM-->>API: Parecer JSON
    API->>Fila: Guarda resultado/status
    UI->>API: GET final do job
    API-->>UI: Resposta + fontes
    UI-->>Pessoa: Exibe resultado aprovado ou abstenção
```

## Dependências do modo local

```mermaid
flowchart LR
    Browser[Navegador] -->|HTTP loopback| Server[server.py]
    Server --> Queue[jobs.py / fila]
    Server -->|HTTPS| Search[API SERPRO]
    Search -->|URLs| Gov[HTML HTTPS gov.br]
    Server -->|HTTP loopback| Ollama[Ollama :11434]
    Ollama --> Model[Modelo local]
    Server -. avaliação offline .-> SQLite[data/knowledge.sqlite3]
```

Linha pontilhada indica uso auxiliar: o chat online atual não consulta o SQLite.

## Modo externo opcional

```mermaid
flowchart LR
    Guest[Pessoa convidada] -->|HTTPS + Basic Auth| Provider[Cloudflare ou ngrok]
    Provider --> Tunnel[Cliente de túnel no computador]
    Tunnel -->|loopback :8010| Waitress[Waitress + internet_app.py]
    Waitress --> Shared[process_messages em server.py]
    Shared --> Search[Busca SERPRO/gov.br]
    Shared -->|loopback :11434| Ollama[Ollama local]
```

O provedor externo faz parte desse caminho; ele não aparece no modo local.
