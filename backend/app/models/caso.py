# ─────────────────────────────────────────────────────────────────────────────
# MODEL: Caso — tabela TbCIAPPICaso
# ─────────────────────────────────────────────────────────────────────────────
# Um "Model" no SQLAlchemy é uma classe Python que representa uma tabela do
# banco de dados. Cada atributo da classe = uma coluna da tabela.
#
# A camada de Models é responsável por COMO os dados são armazenados.
# (A camada de Schemas, em app/schemas/, cuida de COMO os dados chegam e saem
# da API — são coisas distintas e separadas propositalmente.)
#
# Esta tabela é o CORAÇÃO do sistema: todo usuário, acompanhamento e registro
# de ouvidoria está vinculado a um caso.

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base  # classe base que todos os models herdam


class Caso(Base):
    # __tablename__ diz ao SQLAlchemy qual tabela do banco esta classe representa.
    # O nome precisa ser EXATO igual ao banco (case-sensitive no MySQL).
    __tablename__ = "TbCIAPPICaso"

    # ── Chave primária ────────────────────────────────────────────────────────
    # primary_key=True → esta coluna identifica unicamente cada linha.
    # No CIAPPI o número do caso é inserido manualmente (não auto-increment).
    TbCasoNumCaso = Column(Integer, primary_key=True)

    # ── Dados básicos do caso ─────────────────────────────────────────────────
    TbCasoDtinicio = Column(DateTime)               # data de abertura do caso
    tbnomeidoso = Column(String(255))               # nome da pessoa atendida
    TbCasoMotivoAtendimento = Column(String(255))   # motivo do atendimento (FK lógica → TbMotivoAtendimento)
    TbCasoChegouPrograma = Column(String(255))      # como chegou ao programa (ex: "OUvidoria da SJDH")
    Tbambienteviolencia = Column(String(255))       # "Intrafamiliar" ou "Extrafamiliar"
    TbCasoRelato = Column(Text)                     # texto livre com o relato do caso
    TbCasoMunicipio = Column(String(255), nullable=False)  # município — obrigatório

    # ── Dados opcionais do caso ───────────────────────────────────────────────
    TbCasoNumInquerito = Column(Integer)            # número do inquérito policial (se houver)
    TbCasoTecnicoResp = Column(String(255))         # técnico responsável pelo caso

    # ── Encerramento ─────────────────────────────────────────────────────────
    TbCasoDtencer = Column(DateTime)                # data de encerramento
    # TbObservacoes mapeia a coluna "TbObservações" (com acento) no banco.
    # O primeiro argumento de Column() pode ser o nome real da coluna no banco,
    # enquanto o atributo Python usa um nome sem acento — boa prática.
    TbObservacoes = Column("TbObservações", Text)
    TbCasoMotivoEncerramento = Column(Integer)      # FK lógica → TbMotivoEncerramento.Código
    TbCasoAvaliacaoUsuario = Column(Text)           # avaliação do usuário ao encerrar
    TbCasoEncerrado = Column(String(255))           # "Sim" ou "Não" (ou None = em aberto)

    # ── Denúncia / inquérito ──────────────────────────────────────────────────
    TbNumDenuncia = Column(Integer)                 # número da denúncia original

    # ── Campos de Ouvidoria ───────────────────────────────────────────────────
    # Casos que chegam via Ouvidoria da SJDH têm prazo para resposta.
    TbPrazoOuvidoria = Column(DateTime)             # prazo para encerrar o caso via ouvidoria
    TbEncerradoOuvidoria = Column(String(255))      # "Sim" quando ouvidoria encerrada
    TbDtEncerradoOuvidoria = Column(DateTime)       # data do encerramento da ouvidoria
    TbNumOfOuvidoria = Column(String(255))          # número do ofício de resposta
