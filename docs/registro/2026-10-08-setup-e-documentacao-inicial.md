# 08/10/2026 — Ambiente, atualizações e documentação inicial

**Objetivo:** fazer o projeto rodar nesta máquina, atualizar dependências e documentar como ele funciona.

## 1. Fazer o projeto rodar

| Passo | O que foi feito | Por quê |
| --- | --- | --- |
| 1.1 | Criado `susana_rag_backend/.venv` e instalado o `requirements.txt` | Não havia ambiente Python |
| 1.2 | Instalado `pydantic-settings` | Usado em `config.py`, mas ausente do `requirements.txt` |
| 1.3 | Node.js 24 LTS instalado em `~/.local/node` (binário oficial, sem `sudo`) | Node ausente e Homebrew sem permissão de escrita para o usuário |
| 1.4 | `npm ci` em `susana-ui/` | Dependências do frontend |
| 1.5 | `ollama pull llama3.1:8b` (4,9 GB) | Modelo padrão do projeto não estava baixado |
| 1.6 | Instalados `pandas` e `scikit-learn`; rodado `ml/guardrails/train.py` | O modelo do guardrail não existia no MLflow |

Arquivos alterados: `susana_rag_backend/requirements.txt` (+ `pydantic-settings`, `scikit-learn`, `pandas`).

## 2. Atualização de versões (frontend)

Atualizações sem trocar de versão major: `next` e `eslint-config-next` 16.3.8 → 16.4.0, `react`/`react-dom` 19.2.8 → 19.3.0, `lucide-react` → 1.53, `framer-motion` → 13.5.1, `@types/node` → ^24 (alinhado ao Node 24). O `npm run build` passou.

**Não atualizados de propósito** (mudanças que quebram compatibilidade): TypeScript 7, ESLint 10, framer-motion 14.

## 3. Documentação

Criados os documentos `docs/README.md` e `docs/01` a `docs/10`, explicando cada parte do projeto. A análise encontrou 20 problemas, registrados em `docs/10-problemas-conhecidos.md`.

## Verificação

- `GET /health` → `{"status":"ok","pipeline_ready":true}`.
- Pergunta clínica bloqueada e pergunta administrativa respondida com fonte, via `/api/chat/stream`.
- `pytest`: 13 passaram, **1 falhou** (`test_blocks_symptom_report`). A falha revelou que o modelo de ML treinado no passo 1.6 era mais fraco que as regras. Foi corrigido no registro seguinte.

**Próximo registro:** [2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md](2026-10-08-correcoes-guardrail-corpus-limiar-rotas.md)
