# ============================================
# 🐳 Makefile - DB ciappi (MySQL)
# ============================================

# Carrega variáveis do .env
include .env

# Container principal
SERVICE=db-ciappi

# Mapeamento das variáveis do .env
DB_NAME=$(MYSQL_DATABASE)
DB_USER=$(MYSQL_USER)
DB_PASS=$(MYSQL_PASSWORD)

# --------------------------------------------
# 🧱 Comandos principais
# --------------------------------------------

up:
	@echo "🚀 Subindo containers..."
	docker compose up -d

down:
	@echo "🧹 Parando e removendo containers..."
	docker compose down

restart:
	@echo "🔄 Reiniciando containers..."
	docker compose down && docker compose up -d

logs:
	@echo "📜 Logs do MySQL..."
	docker compose logs -f $(SERVICE)

bash:
	@echo "🐚 Acessando shell do container MySQL..."
	docker exec -it $(SERVICE) bash

mysql:
	@echo "💻 Acessando MySQL como $(DB_USER)..."
	docker exec -it $(SERVICE) mysql -u $(DB_USER) -p$(DB_PASS) $(DB_NAME)

status:
	@echo "📊 Status dos containers..."
	@docker ps --filter "name=$(SERVICE)"

# --------------------------------------------
# 💾 Backup & Restore
# --------------------------------------------

backup:
	@echo "💾 Gerando backup do banco $(DB_NAME)..."
	docker exec $(SERVICE) mysqldump -u $(DB_USER) -p$(DB_PASS) $(DB_NAME) > backup_`date +%Y%m%d_%H%M`.sql

restore:
	@echo "📥 Restaurando backup no banco $(DB_NAME)..."
	cat $(FILE) | docker exec -i $(SERVICE) mysql -u $(DB_USER) -p$(DB_PASS) $(DB_NAME)

# --------------------------------------------
# 🧩 Utilidades
# --------------------------------------------

clean:
	@echo "🧼 Removendo volumes e dados persistidos..."
	docker compose down -v
	rm -rf ./docker/mysql/init/*.sql

port:
	@echo "🌐 MySQL disponível em: localhost:$(DB_PORT)"

PYTHON_BACKEND=venv-backend/bin/python3
PYTHON_FRONTEND=venv-frontend/bin/python3
PIP_BACKEND=venv-backend/bin/pip
PIP_FRONTEND=venv-frontend/bin/pip

# Tenta encontrar python3.12, se não existir usa python3
PYTHON_SYS=$(shell which python3.12 || which python3)

# --------------------------------------------
# 🐍 Python Virtual Environments
# --------------------------------------------

venv-backend:
	@echo "🐍 Criando virtual environment para backend com $(PYTHON_SYS)..."
	$(PYTHON_SYS) -m venv venv-backend
	@echo "✅ venv-backend criado!"

venv-frontend:
	@echo "🐍 Criando virtual environment para frontend com $(PYTHON_SYS)..."
	$(PYTHON_SYS) -m venv venv-frontend
	@echo "✅ venv-frontend criado!"

install-backend:
	@echo "📦 Instalando dependências do backend..."
	$(PIP_BACKEND) install --upgrade pip && $(PIP_BACKEND) install -r backend/requirements.txt
	@echo "✅ Backend dependencies instaladas!"

install-frontend:
	@echo "📦 Instalando dependências do frontend..."
	$(PIP_FRONTEND) install --upgrade pip && $(PIP_FRONTEND) install -r frontend/requirements.txt
	@echo "✅ Frontend dependencies instaladas!"

setup:
	@echo "🚀 Setup completo do projeto..."
	@make venv-backend
	@make venv-frontend
	@make install-backend
	@make install-frontend
	@echo ""
	@echo "✨ Setup concluído!"
	@echo "📖 Leia QUICKSTART.md para próximos passos"

# --------------------------------------------
# 🏃 Execution
# --------------------------------------------

run-backend:
	@echo "🚀 Iniciando Backend (FastAPI)..."
	. venv-backend/bin/activate && uvicorn backend.app.main:app --reload --port 8000

run-frontend:
	@echo "🚀 Iniciando Frontend (Streamlit)..."
	. venv-frontend/bin/activate && streamlit run frontend/app.py

restart-backend:
	@echo "🔄 Reiniciando Backend (Uvicorn)..."
	-pkill -f "uvicorn backend.app.main:app"
	@make run-backend

restart-frontend:
	@echo "🔄 Reiniciando Frontend (Streamlit)..."
	-pkill -f "streamlit run frontend/app.py"
	@make run-frontend

# --------------------------------------------
# 🗄️ Alembic Migrations
# --------------------------------------------

migrate:
	@echo "🗄️ Aplicando migrações pendentes..."
	cd backend && ../venv-backend/bin/alembic upgrade head

migrate-status:
	@echo "📋 Status das migrações:"
	cd backend && ../venv-backend/bin/alembic current

migrate-history:
	@echo "📜 Histórico de migrações:"
	cd backend && ../venv-backend/bin/alembic history --verbose

migrate-new:
	@echo "✏️  Criando nova migração (autogenerate)..."
	cd backend && ../venv-backend/bin/alembic revision --autogenerate -m "$(MSG)"

migrate-stamp:
	@echo "📌 Marcando banco como na revision $(REV)..."
	cd backend && ../venv-backend/bin/alembic stamp $(REV)

# --------------------------------------------
# 🧪 Tests
# --------------------------------------------

test:
	@echo "🧪 Rodando testes do backend..."
	cd backend && ../venv-backend/bin/pytest tests/ -v

test-cov:
	@echo "🧪 Rodando testes com cobertura..."
	cd backend && ../venv-backend/bin/pytest tests/ -v --cov=app --cov-report=term-missing

# --------------------------------------------
# 📋 Help
# --------------------------------------------

help:
	@echo ""
	@echo "📘 Comandos disponíveis:"
	@echo ""
	@echo "🐍 PYTHON & EXECUTION:"
	@echo "  make setup              -> Setup completo (venv + dependências)"
	@echo "  make run-backend        -> Inicia o backend na porta 8000"
	@echo "  make run-frontend       -> Inicia o frontend"
	@echo "  make restart-backend    -> Reinicia o backend (mata uvicorn e sobe de novo)"
	@echo "  make restart-frontend   -> Reinicia o frontend (mata streamlit e sobe de novo)"
	@echo "  make venv-backend       -> Criar venv do backend"
	@echo "  make venv-frontend      -> Criar venv do frontend"
	@echo "  make install-backend    -> Instalar deps backend"
	@echo "  make install-frontend   -> Instalar deps frontend"
	@echo ""
	@echo "🐳 DOCKER & DATABASE:"
	@echo "  make up         -> Sobe o banco de dados"
	@echo "  make down       -> Para containers"
	@echo "  make restart    -> Reinicia containers"
	@echo "  make logs       -> Mostra logs do MySQL"
	@echo "  make status     -> Mostra status dos containers"
	@echo "  make clean      -> Remove volumes/dados"
	@echo "  make port       -> Mostra porta do banco"
