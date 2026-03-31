# ─────────────────────────────────────────────────────────────────────────────
# MODEL: ILPI — tabela TbCIAPPIILPI
# ─────────────────────────────────────────────────────────────────────────────
# ILPI = Instituição de Longa Permanência para Idosos (casas de repouso,
# abrigos, asilos etc.).
#
# O programa acompanha essas instituições com visitas periódicas.
# As visitas são registradas na tabela TBAcompEntidade (model VisitaILPI).

from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base


class ILPI(Base):
    __tablename__ = "TbCIAPPIILPI"

    # ── Chave primária ────────────────────────────────────────────────────────
    CODIGOILPI = Column(Integer, primary_key=True, autoincrement=True)

    # ── Identificação ─────────────────────────────────────────────────────────
    DATACADASTRO = Column(DateTime)
    NOMEILPI = Column(String(255), nullable=False)      # nome da instituição (armazenado em maiúsculas)
    PERSONALIDADEJURIDICA = Column(String(255))         # "Pública", "Privada", "Filantrópica"
    RESPONSAVELILPI = Column(String(255))               # nome do responsável
    TIPOENTIDADE = Column(String(255))                  # tipo da entidade

    # ── Visitas ───────────────────────────────────────────────────────────────
    DATAVISITA = Column(DateTime)                       # data da última visita realizada
    MOTIVOVISITA = Column(String(255))                  # FK lógica → TbMotVisitaInst
    DATAPREVISTAVISITA = Column(DateTime)               # data prevista para próxima visita

    # ── Capacidade ───────────────────────────────────────────────────────────
    CAPACIDADEIDOSOS = Column(Integer)                  # vagas totais da instituição
    IDOSOSRESIDENTES = Column(Integer)                  # ocupação atual
    TIPOPUBLICO = Column(String(255))                   # tipo de público atendido

    # ── Contato ───────────────────────────────────────────────────────────────
    FONEFIXO = Column(String(255))
    CELULAR = Column(String(255))

    # ── Endereço ──────────────────────────────────────────────────────────────
    LOGRADOURO = Column(String(255))
    NUMEROIMOVEL = Column(String(255))
    COMPLEMENTO = Column(String(255))
    BAIRRO = Column(String(255))
    MUNICIPIO = Column(String(255))
    PONTODEREFERENCIA = Column(String(255))

    # ── Status ────────────────────────────────────────────────────────────────
    STATUS = Column(String(255))                        # "Ativo", "Inativo" etc.
    AVALIACAO = Column(String(255))                     # avaliação da instituição
    DATAFECHAMENTO = Column(DateTime)                   # quando foi fechada (se aplicável)
    DATAREABERTURA = Column(DateTime)                   # se reabriu
