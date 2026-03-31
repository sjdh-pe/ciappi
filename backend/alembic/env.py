"""
Alembic env.py — CIAPPI
Usa os models SQLAlchemy para gerar migrações automaticamente (autogenerate).
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Garante que o pacote 'app' seja encontrado
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.core.config import settings

# Importa todos os models para que o Alembic os detecte no metadata
import app.models.caso           # noqa
import app.models.acompanhamento # noqa
import app.models.usuario        # noqa
import app.models.ilpi           # noqa
import app.models.evento         # noqa
import app.models.visita_inst    # noqa
import app.models.visita_ilpi    # noqa
import app.models.tecnico        # noqa
import app.models.tabelas_aux    # noqa

config = context.config

# Sobrescreve a URL do banco com a variável de ambiente
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera SQL sem conectar ao banco (útil para review)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica migrações conectando ao banco."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,      # detecta mudanças de tipo de coluna
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
