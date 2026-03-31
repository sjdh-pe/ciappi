# ─────────────────────────────────────────────────────────────────────────────
# MODEL: Acompanhamento — tabela TbCIAPPIAcompanhamento
# ─────────────────────────────────────────────────────────────────────────────
# Registra cada atendimento/ação realizada em um caso.
# Um caso pode ter muitos acompanhamentos (relação 1:N com TbCIAPPICaso).
#
# Equivale ao formulário FrmCadAcomp do sistema Access original.

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class Acompanhamento(Base):
    __tablename__ = "TbCIAPPIAcompanhamento"

    # ── Chave primária ────────────────────────────────────────────────────────
    # autoincrement=True → o banco gera o ID automaticamente a cada inserção.
    # Diferente de Caso, aqui não precisamos definir o número manualmente.
    tbcodigo = Column(Integer, primary_key=True, autoincrement=True)

    # ── Vínculo com o caso ────────────────────────────────────────────────────
    # FK lógica: este campo aponta para TbCIAPPICaso.TbCasoNumCaso.
    # Não há ForeignKey() declarado aqui porque o banco Access original
    # não tinha constraints formais — o vínculo é feito por convenção.
    # nullable=False → todo acompanhamento precisa estar ligado a um caso.
    TbAcomCaso = Column(Integer, nullable=False)

    # ── Dados do acompanhamento ───────────────────────────────────────────────
    TbAcompdata = Column(DateTime)              # data do atendimento/contato
    TbAcompOrgao = Column(String(255))          # órgão envolvido (obrigatório se ação = Encaminhamento)
    TbAcompAcao = Column(String(255))           # tipo de ação (ex: "Encaminhamento", "Concluída para Ouvidoria")
    TbAcompStatus = Column(String(255))         # status do acompanhamento
    TbAcompPrazo = Column(DateTime)             # prazo para resolução da ação
    TbCaraterAtendimento = Column(String(255))  # caráter (ex: "Social", "Jurídico")
    TbRelato = Column(Text)                     # descrição completa do que foi feito
    TbTecnicoResponsavel = Column(String(255))  # técnico que realizou o atendimento
