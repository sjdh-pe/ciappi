# ─────────────────────────────────────────────────────────────────────────────
# MODEL: Tecnico — tabela TbTecnico
# ─────────────────────────────────────────────────────────────────────────────
# Representa os profissionais (técnicos) que usam o sistema.
# Esta tabela serve também como tabela de usuários para autenticação:
# o login é feito com TbNomeTecnico + TbSenha.
#
# Níveis de acesso (TbNivel):
#   1 → usuário comum (somente leitura)
#   2 → operador (criação e edição)
#   3 → administrador (acesso total)

from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class Tecnico(Base):
    __tablename__ = "TbTecnico"

    # ── Chave primária ────────────────────────────────────────────────────────
    CodTecnico = Column(Integer, primary_key=True, autoincrement=True)

    # ── Dados do técnico ──────────────────────────────────────────────────────
    TbNomeTecnico = Column(String(255), nullable=False)  # nome completo — obrigatório
    TBCargoTecnico = Column(String(255))                 # cargo (ex: "Assistente Social")
    TbDataCadastro = Column(DateTime)                    # quando foi cadastrado no sistema

    # TbDataSaida mapeia a coluna "TbDataSaída" (com acento) do banco.
    # Usamos String porque no Access original era armazenado como texto.
    TbDataSaida = Column("TbDataSaída", String(255))

    # ── Autenticação ──────────────────────────────────────────────────────────
    # ATENÇÃO: senha em texto plano — herdado do sistema Access original.
    # Em produção o ideal é usar bcrypt (ver security.py).
    TbSenha = Column(String(255))

    # ── Controle de acesso ────────────────────────────────────────────────────
    TbNivel = Column(Integer)       # nível de permissão: 1, 2 ou 3
    TbStatus = Column(String(255))  # "Ativo" ou "Bloqueado"
    Campo1 = Column(String(255))    # campo auxiliar legado do Access
