# ============================================
# Makefile - CIAPPI
# ============================================

include .env

COMPOSE_FILE=ciappi_db/docker-compose.yml
SERVICE=db-ciappi

DB_NAME=$(MYSQL_DATABASE)
DB_USER=$(MYSQL_USER)
DB_PASS=$(MYSQL_PASSWORD)

PYTHON_BACKEND=venv-backend/bin/python3
PYTHON_FRONTEND=venv-frontend/bin/python3
PIP_BACKEND=venv-backend/bin/pip
PIP_FRONTEND=venv-frontend/bin/pip

PYTHON_SYS=$(shell which python3.12 || which python3)

.PHONY: up down restart logs bash mysql status backup restore clean \
        venv-backend venv-frontend install-backend install-frontend setup \
        run-backend run-frontend restart-backend restart-frontend \
        migrate migrate-status migrate-history migrate-new migrate-stamp \
        test test-cov help

# --------------------------------------------
# Docker & Banco de Dados
# --------------------------------------------

up:
	@echo "Subindo containers..."
	docker compose -f $(COMPOSE_FILE) up -d

down:
	@echo "Parando containers..."
	docker compose -f $(COMPOSE_FILE) down

restart:
	@echo "Reiniciando containers..."
	docker compose -f $(COMPOSE_FILE) down && docker compose -f $(COMPOSE_FILE) up -d

logs:
	docker compose -f $(COMPOSE_FILE) logs -f $(SERVICE)

bash:
	docker exec -it $(SERVICE) bash

mysql:
	docker exec -it $(SERVICE) mysql -u $(DB_USER) -p$(DB_PASS) $(DB_NAME)

status:
	@docker ps --filter "name=$(SERVICE)"

# --------------------------------------------
# Backup & Restore
# --------------------------------------------

backup:
	@echo "Gerando backup do banco $(DB_NAME)..."
	docker exec $(SERVICE) mysqldump -u $(DB_USER) -p$(DB_PASS) $(DB_NAME) > backup_`date +%Y%m%d_%H%M`.sql

restore:
	@echo "Restaurando backup no banco $(DB_NAME)..."
	cat $(FILE) | docker exec -i $(SERVICE) mysql -u $(DB_USER) -p$(DB_PASS) $(DB_NAME)

# --------------------------------------------
# Utilitários
# --------------------------------------------

clean:
	@echo "Removendo volumes e dados persistidos..."
	docker compose -f $(COMPOSE_FILE) down -v

# --------------------------------------------
# Python & Ambientes Virtuais
# --------------------------------------------

venv-backend:
	@echo "Criando venv do backend com $(PYTHON_SYS)..."
	$(PYTHON_SYS) -m venv venv-backend

venv-frontend:
	@echo "Criando venv do frontend com $(PYTHON_SYS)..."
	$(PYTHON_SYS) -m venv venv-frontend

install-backend:
	@echo "Instalando dependências do backend..."
	$(PIP_BACKEND) install --upgrade pip && $(PIP_BACKEND) install -r backend/requirements.txt

install-frontend:
	@echo "Instalando dependências do frontend..."
	$(PIP_FRONTEND) install --upgrade pip && $(PIP_FRONTEND) install -r frontend/requirements.txt

setup:
	@echo "Setup completo do projeto..."
	$(MAKE) venv-backend
	$(MAKE) venv-frontend
	$(MAKE) install-backend
	$(MAKE) install-frontend
	@echo "Setup concluido! Leia QUICKSTART.md para proximos passos."

# --------------------------------------------
# Execução
# --------------------------------------------

run-backend:
	. venv-backend/bin/activate && uvicorn backend.app.main:app --reload --port 8000

run-frontend:
	. venv-frontend/bin/activate && streamlit run frontend/app.py

restart-backend:
	-pkill -f "uvicorn backend.app.main:app"
	$(MAKE) run-backend

restart-frontend:
	-pkill -f "streamlit run frontend/app.py"
	$(MAKE) run-frontend

# --------------------------------------------
# Migrações Alembic
# --------------------------------------------

migrate:
	cd backend && ../venv-backend/bin/alembic upgrade head

migrate-status:
	cd backend && ../venv-backend/bin/alembic current

migrate-history:
	cd backend && ../venv-backend/bin/alembic history --verbose

migrate-new:
	cd backend && ../venv-backend/bin/alembic revision --autogenerate -m "$(MSG)"

migrate-stamp:
	cd backend && ../venv-backend/bin/alembic stamp $(REV)

# --------------------------------------------
# Testes
# --------------------------------------------

test:
	cd backend && ../venv-backend/bin/pytest tests/ -v

test-cov:
	cd backend && ../venv-backend/bin/pytest tests/ -v --cov=app --cov-report=term-missing

# --------------------------------------------
# Help
# --------------------------------------------

help:
	@echo ""
	@echo "Comandos disponiveis:"
	@echo ""
	@echo "  SETUP:"
	@echo "    make setup                Setup completo (venv + dependencias)"
	@echo "    make venv-backend         Cria venv do backend"
	@echo "    make venv-frontend        Cria venv do frontend"
	@echo "    make install-backend      Instala dependencias do backend"
	@echo "    make install-frontend     Instala dependencias do frontend"
	@echo ""
	@echo "  EXECUCAO:"
	@echo "    make run-backend          Inicia o backend (porta 8000)"
	@echo "    make run-frontend         Inicia o frontend (porta 8501)"
	@echo "    make restart-backend      Reinicia o backend"
	@echo "    make restart-frontend     Reinicia o frontend"
	@echo ""
	@echo "  DOCKER & BANCO:"
	@echo "    make up                   Sobe o banco de dados"
	@echo "    make down                 Para os containers"
	@echo "    make restart              Reinicia os containers"
	@echo "    make logs                 Logs do MySQL"
	@echo "    make status               Status dos containers"
	@echo "    make mysql                Shell interativo do MySQL"
	@echo "    make bash                 Shell do container"
	@echo "    make clean                Remove volumes e dados"
	@echo ""
	@echo "  BACKUP:"
	@echo "    make backup               Gera dump do banco"
	@echo "    make restore FILE=...     Restaura backup"
	@echo ""
	@echo "  MIGRACOES:"
	@echo "    make migrate              Aplica migracoes pendentes"
	@echo "    make migrate-status       Revisao atual"
	@echo "    make migrate-history      Historico de migracoes"
	@echo "    make migrate-new MSG=...  Cria nova migracao"
	@echo "    make migrate-stamp REV=.. Marca revisao no banco"
	@echo ""
	@echo "  TESTES:"
	@echo "    make test                 Roda os testes"
	@echo "    make test-cov             Testes com cobertura"
	@echo ""