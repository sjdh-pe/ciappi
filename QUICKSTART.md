# ⚡ Quick Start — CIAPPI em 5 Minutos
**Quer começar AGORA?** Execute um dos comandos abaixo:
---
## 🚀 Opção 1: Automatizado (Recomendado)
```bash
./setup.sh
```
Pronto! Ele faz tudo.
---
## 🔧 Opção 2: Com Make
```bash
make setup
make up
```
---
## 🏃 Rodar o Projeto

### Usando Make (Recomendado)
```bash
# Em um terminal
make run-backend

# Em outro terminal
make run-frontend
```

### Manualmente
#### Terminal 1 — Backend
```bash
source venv-backend/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```
→ http://localhost:8000/docs

#### Terminal 2 — Frontend
```bash
source venv-frontend/bin/activate
streamlit run frontend/app.py
```
→ http://localhost:8501
---
## 📖 Documentação
- **[QUICKSTART.md](./QUICKSTART.md)** — Este arquivo
- **[AMBIENTE_ISOLADO.md](./AMBIENTE_ISOLADO.md)** — Tudo sobre isolamento
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** — Problemas & soluções
---
**Pronto! 🎉**
