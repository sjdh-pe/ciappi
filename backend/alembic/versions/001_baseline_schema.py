"""baseline schema — todas as tabelas do Access migradas

Revision ID: 001_baseline
Revises:
Create Date: 2026-03-31

Esta é a migração baseline que documenta o schema inicial do CIAPPI.
Se o banco já existe (migração manual via schema.sql), marque como aplicada:
    alembic stamp 001_baseline
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Caso o banco já exista via schema.sql, este bloco não precisa rodar.
    # Para banco do zero, garante a criação da tabela TBAcompEntidade.
    op.create_table(
        "TBAcompEntidade",
        sa.Column("Codigoentidade", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("codigoilpi", sa.Integer(), sa.ForeignKey("TbCIAPPIILPI.CODIGOILPI"), nullable=False),
        sa.Column("nomeentidade", sa.String(255), nullable=False),
        sa.Column("dtprevistavisita", sa.DateTime()),
        sa.Column("dtvisita", sa.DateTime()),
        sa.Column("motivovisita", sa.String(255)),
        sa.Column("relato", sa.Text()),
        sa.Column("tecnicoresponsavel", sa.String(255)),
        sa.Column("observacoes", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("TBAcompEntidade")
