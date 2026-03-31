# ─────────────────────────────────────────────────────────────────────────────
# MODEL: Evento — tabela TbEvento
# ─────────────────────────────────────────────────────────────────────────────
# Representa eventos realizados pela equipe: palestras, capacitações,
# reuniões e outras atividades externas ao atendimento individual.
#
# Um evento tem duas fases:
#   1. Planejamento → campos de previsão (Tbdataprevista, TbPublicoEstimado...)
#   2. Realização   → campos de resultado (TbDataRealizacao, TbPublicoPresente, TbRelato)

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class Evento(Base):
    __tablename__ = "TbEvento"

    # ── Chave primária ────────────────────────────────────────────────────────
    # A coluna no banco chama "Código" (com acento e maiúscula).
    # O SQLAlchemy permite mapear um nome diferente no Python:
    # Column("nome_no_banco", tipo, ...)
    Codigo = Column("Código", Integer, primary_key=True, autoincrement=True)

    # ── Planejamento do evento ────────────────────────────────────────────────
    tbtipoevento = Column(String(255))          # FK lógica → TbTipoEvento
    tbnomeevento = Column(String(255))          # nome/título do evento
    Tbobjetivoevento = Column(String(255))      # objetivo principal
    Tbdataprevista = Column(DateTime)           # data planejada (não pode ser no passado)
    Tbpublicoalvo = Column(String(255))         # público-alvo (ex: "Idosos", "Cuidadores")
    TbPublicoEstimado = Column(Integer)         # estimativa de participantes
    Tblocalevento = Column(String(255))         # local de realização
    TbMunicipioevento = Column(String(255))     # município do evento
    TbTecnicoResponsavel = Column(Integer)      # FK lógica → TbTecnico.CodTecnico

    # ── Resultado / realização ────────────────────────────────────────────────
    TbPublicoPresente = Column(Integer)         # participantes reais
    TbRelato = Column(Text)                     # relato pós-evento
    TbDataRealizacao = Column(DateTime)         # data real de realização
    TbTempoDuracao = Column(DateTime)           # duração (armazenado como DateTime — legado)
    Tbtecnicosenvolvidos = Column(Integer)      # número de técnicos envolvidos
