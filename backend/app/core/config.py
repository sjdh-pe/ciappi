import os
from pydantic_settings import BaseSettings

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG.PY — Configurações centrais da aplicação
# ─────────────────────────────────────────────────────────────────────────────
# Este arquivo usa pydantic-settings para carregar variáveis de ambiente
# do arquivo .env e disponibilizá-las como um objeto Python tipado.
#
# Por que usar isso em vez de os.environ.get() diretamente?
# → Tipagem: você sabe que DATABASE_URL é sempre str, DEV_MODE é bool etc.
# → Validação automática: se uma variável obrigatória não existir, a aplicação
#   falha com um erro claro ao iniciar — não no meio da execução.
# → Centralização: todas as configs ficam aqui, fácil de encontrar.

# ─────────────────────────────────────────────────────────────────────────────
# LOCALIZAÇÃO DO ARQUIVO .ENV
# ─────────────────────────────────────────────────────────────────────────────
# Calcula o caminho absoluto até o arquivo .env mesmo que o Python seja
# executado de qualquer diretório.
#
# __file__  →  .../backend/app/core/config.py
# dirname   →  .../backend/app/core/
# dirname   →  .../backend/app/
# dirname   →  .../backend/          ← BASE_DIR
# join      →  .../backend/.env      ← ENV_PATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")


# ─────────────────────────────────────────────────────────────────────────────
# CLASSE DE CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────────────────────
# Cada atributo da classe corresponde a uma variável no arquivo .env.
# O pydantic-settings lê o .env automaticamente e preenche os valores.
class Settings(BaseSettings):
    # URL completa de conexão com o banco MySQL.
    # Exemplo: mysql+pymysql://ciappi_urs:ciappi_pwd@localhost:3309/ciappi
    DATABASE_URL: str

    # Chave secreta usada para assinar e verificar tokens JWT.
    # Deve ser uma string longa e aleatória — nunca exposta publicamente.
    SECRET_KEY: str

    # Algoritmo de criptografia do JWT. HS256 é o padrão mais usado.
    ALGORITHM: str = "HS256"

    # Tempo de validade do token em minutos. 480 = 8 horas (um dia de trabalho).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Modo de desenvolvimento: quando True, requisições sem token são aceitas
    # e o FastAPI ativa o modo debug (respostas de erro mais detalhadas).
    DEV_MODE: bool = False

    class Config:
        # Diz ao pydantic onde encontrar o arquivo .env
        env_file = ENV_PATH
        # Se houver variáveis extras no .env que não estão na classe,
        # simplesmente ignora (não lança erro).
        extra = "ignore"


# ─────────────────────────────────────────────────────────────────────────────
# INSTÂNCIA GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
# Cria uma única instância de Settings que é importada em todo o projeto.
# Ex: from app.core.config import settings
#     print(settings.DATABASE_URL)
settings = Settings()
