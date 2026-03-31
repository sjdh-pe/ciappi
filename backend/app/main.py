import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
# AJUSTE DE PATH
# ─────────────────────────────────────────────────────────────────────────────
# Python precisa saber onde está o pacote "app" para conseguir importá-lo.
# Aqui garantimos que a pasta "backend/" está no sys.path — que é a lista de
# diretórios onde o Python procura módulos.
# Isso funciona independente de onde você roda o servidor (da raiz do projeto,
# da pasta backend, etc.).
current_dir = os.path.dirname(os.path.abspath(__file__))  # pasta app/
parent_dir = os.path.dirname(current_dir)                 # pasta backend/
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurações da aplicação (DATABASE_URL, SECRET_KEY etc.)
from app.core.config import settings

# Cada "router" é um grupo de rotas (endpoints) de um assunto específico.
# Por exemplo: auth.router tem as rotas de login,
#              casos.router tem as rotas de /casos, etc.
from app.routers import (
    auth,
    casos,
    usuarios,
    acompanhamentos,
    ilpis,
    eventos,
    visitas,
    ouvidoria,
    relatorios,
    tabelas,
)

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTAÇÃO EXPLÍCITA DE MODELS
# ─────────────────────────────────────────────────────────────────────────────
# O SQLAlchemy só "conhece" uma tabela se a classe Model for importada em algum
# momento antes de criar/usar o banco. Aqui forçamos a importação do model
# VisitaILPI (tabela TBAcompEntidade) que não é importado em nenhum outro lugar
# automaticamente. O comentário "# noqa: F401" diz ao linter para ignorar o
# aviso de "importado mas não usado" — o efeito colateral de registrar o model
# É o objetivo aqui.
import app.models.visita_ilpi  # noqa: F401 — registra TBAcompEntidade no SQLAlchemy

# ─────────────────────────────────────────────────────────────────────────────
# CRIAÇÃO DA APLICAÇÃO FASTAPI
# ─────────────────────────────────────────────────────────────────────────────
# FastAPI() cria a aplicação principal. Os parâmetros aparecem na documentação
# automática que o FastAPI gera em /docs (Swagger UI) e /redoc.
# debug=settings.DEV_MODE ativa modo de debug se DEV_MODE=true no .env
app = FastAPI(
    title="CIAPPI API",
    description="Sistema de gestão de casos de proteção ao idoso — SJDH/PE",
    version="1.0.0",
    debug=settings.DEV_MODE,
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS — Cross-Origin Resource Sharing
# ─────────────────────────────────────────────────────────────────────────────
# Por segurança, os navegadores bloqueiam requisições de um domínio para outro
# (ex: frontend em localhost:8501 chamando a API em localhost:8000).
# O middleware de CORS configura quais origens têm permissão para acessar a API.
#
# allow_origins    → lista de origens permitidas (aqui, apenas o Streamlit dev)
# allow_credentials → permite enviar cookies/tokens junto com as requisições
# allow_methods    → quais métodos HTTP são permitidos ("*" = todos: GET, POST, PUT...)
# allow_headers    → quais cabeçalhos HTTP são aceitos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit em desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# REGISTRO DOS ROUTERS
# ─────────────────────────────────────────────────────────────────────────────
# Cada router carrega um conjunto de endpoints no aplicativo.
# O prefixo de cada rota já está definido dentro do próprio router
# (ex: router = APIRouter(prefix="/casos", ...)).
app.include_router(auth.router)           # POST /auth/login
app.include_router(casos.router)          # GET/POST/PUT /casos
app.include_router(usuarios.router)       # GET/POST/PUT /usuarios
app.include_router(acompanhamentos.router)# GET/POST/PUT /acompanhamentos
app.include_router(ilpis.router)          # GET/POST/PUT /ilpis
app.include_router(eventos.router)        # GET/POST/PUT /eventos
app.include_router(visitas.router)        # GET/POST/PUT /visitas
app.include_router(ouvidoria.router)      # GET/PUT /ouvidoria
app.include_router(relatorios.router)     # GET /relatorios
app.include_router(tabelas.router)        # GET/POST/PUT/DELETE /tabelas


# ─────────────────────────────────────────────────────────────────────────────
# ROTA RAIZ — healthcheck
# ─────────────────────────────────────────────────────────────────────────────
# Rota simples em GET / para verificar se a API está no ar.
# O decorador @app.get("/") registra a função como handler do GET em "/".
@app.get("/")
def root():
    return {"sistema": "CIAPPI", "versao": "1.0.0", "status": "online"}
