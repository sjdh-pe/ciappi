# ─────────────────────────────────────────────────────────────────────────────
# DATABASE.PY — Configuração da conexão com o banco de dados
# ─────────────────────────────────────────────────────────────────────────────
# Este arquivo é o ponto central de conexão com o MySQL.
# Ele cria três coisas fundamentais que serão usadas em todo o projeto:
#   1. engine  → a "ponte" entre Python e o banco de dados
#   2. SessionLocal → fábrica de sessões (cada requisição abre e fecha uma)
#   3. Base    → classe base que todos os Models vão herdar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings  # lê DATABASE_URL do arquivo .env

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE — motor de conexão ao banco
# ─────────────────────────────────────────────────────────────────────────────
# create_engine() recebe a URL de conexão (ex: mysql+pymysql://user:pass@host/db)
# e cria o objeto que gerencia o pool de conexões com o MySQL.
#
# pool_pre_ping=True
#   → Antes de usar uma conexão do pool, verifica se ainda está ativa.
#   → Evita o erro "MySQL server has gone away" após longos períodos de inatividade.
#
# pool_recycle=3600
#   → Descarta e recria conexões após 1 hora (3600 segundos).
#   → O MySQL fecha conexões inativas por padrão após ~8h, então reciclar
#     periodicamente evita usar conexões "mortas".
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSIONLOCAL — fábrica de sessões de banco
# ─────────────────────────────────────────────────────────────────────────────
# Uma "sessão" no SQLAlchemy é como uma "transação": você abre, faz queries,
# e ao final commita (salva) ou fecha (descarta).
#
# sessionmaker() cria uma classe que, quando chamada (SessionLocal()), retorna
# uma nova sessão associada ao engine acima.
#
# autocommit=False → você precisa chamar db.commit() explicitamente para salvar.
#                    Isso evita salvar dados por acidente.
# autoflush=False  → o SQLAlchemy não envia SQL ao banco automaticamente antes
#                    de cada query — você controla quando isso acontece.
# bind=engine      → liga esta sessão ao engine criado acima.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─────────────────────────────────────────────────────────────────────────────
# BASE — classe base para todos os Models
# ─────────────────────────────────────────────────────────────────────────────
# Todos os models do projeto (Caso, Usuario, Tecnico etc.) vão herdar desta
# classe. Isso permite que o SQLAlchemy "saiba" quais tabelas existem e consiga
# criar/atualizar o schema, fazer queries etc.
#
# DeclarativeBase é a forma moderna (SQLAlchemy 2.0+) de definir a base.
class Base(DeclarativeBase):
    pass
