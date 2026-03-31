# ─────────────────────────────────────────────────────────────────────────────
# MODEL: VisitaInst — tabela TbVisitaInst
# ─────────────────────────────────────────────────────────────────────────────
# Registra visitas a instituições parceiras e órgãos externos
# (prefeituras, delegacias, conselhos, etc.) — diferente das visitas a ILPIs.
#
# Enquanto VisitaILPI (TBAcompEntidade) foca no acompanhamento de ILPIs,
# VisitaInst é para reuniões e visitas a qualquer outra instituição.

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class VisitaInst(Base):
    __tablename__ = "TbVisitaInst"

    # ── Chave primária ────────────────────────────────────────────────────────
    codigovisita = Column(Integer, primary_key=True, autoincrement=True)

    # ── Dados da visita ───────────────────────────────────────────────────────
    nomeinstituicao = Column(String(255))       # nome da instituição visitada
    datavista = Column(DateTime)                # data da visita (note: "datavista" sem "i" — legado)
    assuntovisita = Column(String(255))         # assunto/pauta principal
    responsavelinstituicao = Column(String(255)) # quem recebeu a visita na instituição

    lembrete = Column(DateTime)                 # lembrete de retorno/follow-up

    relatorio = Column(Text)                    # relatório completo da visita

    # FK lógica → TbTecnico.CodTecnico (armazenado como Integer, não String)
    tecnicoresponsavel = Column(Integer)
