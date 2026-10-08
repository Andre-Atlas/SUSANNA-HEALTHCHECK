# Projeto Susana - Assistente RAG do SUS-DF

Bem-vindo ao repositório do projeto Susana.

## 🛠 Como rodar o projeto localmente

Se você estiver recebendo o erro `address already in use` (porta ocupada), significa que o servidor já está rodando em segundo plano. Use o comando abaixo para forçar o encerramento antes de iniciar:

### 1. Parar tudo que estiver rodando (Kill)
Copie e cole no terminal para derrubar qualquer backend ou frontend travado:
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

---

### 2. Rodar o Backend (API)
Abra um terminal e execute:
```bash
cd /Users/aluno2/SUSANA/susana_rag_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*O backend vai auto-indexar os documentos do `CORPUS` se for a primeira vez.*

---

### 3. Rodar o Frontend (Interface)
Abra **outro** terminal e execute:
```bash
cd /Users/aluno2/SUSANA/susana-ui
npm install
npm run dev
```

Após iniciar, acesse no navegador: **http://localhost:3000**
