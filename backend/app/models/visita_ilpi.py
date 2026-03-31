# ─────────────────────────────────────────────────────────────────────────────
# MODEL: VisitaILPI — tabela TBAcompEntidade
# ─────────────────────────────────────────────────────────────────────────────
# Registra visitas (agendadas e realizadas) a ILPIs.
# Equivale ao formulário FrmCadVisitaEnt / FrmAtuRelVisitaEnt do Access.
#
# Uma visita tem duas etapas:
#   1. Agendamento → preenche dtprevistavisita, motivovisita, tecnicoresponsavel
#   2. Realização  → preenche dtvisita e relato (quando a visita acontece de fato)
#
# Se dtvisita == None, a visita ainda não foi realizada (está agendada).
# Se dtvisita != None, a visita já aconteceu.

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.database import Base


class VisitaILPI(Base):
    """
    Tabela TBAcompEntidade — registra visitas agendadas e realizadas a ILPIs.
    """
    __tablename__ = "TBAcompEntidade"

    # ── Chave primária ────────────────────────────────────────────────────────
    Codigoentidade = Column(Integer, primary_key=True, autoincrement=True)

    # ── Vínculo com a ILPI ────────────────────────────────────────────────────
    # ForeignKey() aqui cria uma constraint REAL no banco (diferente dos outros
    # models que usam FKs apenas lógicas). Isso garante integridade referencial:
    # não é possível criar uma visita para uma ILPI que não existe.
    codigoilpi = Column(Integer, ForeignKey("TbCIAPPIILPI.CODIGOILPI"), nullable=False)

    nomeentidade = Column(String(255), nullable=False)  # nome da ILPI (desnormalizado para histórico)

    # ── Agendamento ───────────────────────────────────────────────────────────
    dtprevistavisita = Column(DateTime)             # data planejada para a visita
    motivovisita = Column(String(255))              # motivo / objetivo da visita
    tecnicoresponsavel = Column(String(255))        # técnico que vai realizar (ou realizou)
    observacoes = Column(Text)                      # observações gerais

    # ── Realização ────────────────────────────────────────────────────────────
    # Estes campos só são preenchidos quando a visita é realizada.
    # Enquanto dtvisita é NULL, a visita está "agendada".
    dtvisita = Column(DateTime)     # data real de realização da visita
    relato = Column(Text)           # relato do que foi observado/discutido
