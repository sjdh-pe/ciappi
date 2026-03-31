# ─────────────────────────────────────────────────────────────────────────────
# MODELS: Tabelas Auxiliares / Lookup Tables
# ─────────────────────────────────────────────────────────────────────────────
# Este arquivo agrupa todas as tabelas de domínio — listas fixas de valores
# que alimentam dropdowns e validações em todo o sistema.
#
# Exemplos de uso:
#   - MotivoAtendimento → opções do campo "Motivo do Atendimento" no cadastro de caso
#   - TipoEvento        → opções do campo "Tipo de Evento" no cadastro de evento
#   - Municipio         → lista de municípios de Pernambuco com AIS e RD
#
# Todas seguem o mesmo padrão: chave primária inteira + campo de descrição.
# Nenhuma tem relacionamentos complexos — são tabelas simples de referência.

from sqlalchemy import Column, Integer, String
from app.database import Base


class MotivoAtendimento(Base):
    """Motivos pelos quais um caso foi aberto. Ex: 'Violência Física', 'Abandono'."""
    __tablename__ = "TbMotivoAtendimento"
    # Coluna "Código" no banco, mapeada como "Codigo" no Python (sem acento)
    Codigo = Column("Código", Integer, primary_key=True, autoincrement=True)
    TbDescricaoMotivo = Column(String(255))


class MotivoEncerramento(Base):
    """Motivos de encerramento de um caso. Ex: 'Resolvido', 'Óbito'."""
    __tablename__ = "TbMotivoEncerramento"
    Codigo = Column("Código", Integer, primary_key=True, autoincrement=True)
    descricaomotivo = Column(String(255))


class MotivoRestauracao(Base):
    """Motivos para reabrir um caso que havia sido encerrado."""
    __tablename__ = "tbmotivorestauracao"
    Codigo = Column("Código", Integer, primary_key=True, autoincrement=True)
    # Coluna "DescriçãoRestauração" no banco → "DescricaoRestauracao" no Python
    DescricaoRestauracao = Column("DescriçãoRestauração", String(255))


class MotivoVisita(Base):
    """Motivos de visita domiciliar. Ex: 'Acompanhamento', 'Denúncia'."""
    __tablename__ = "TbMotivoVisita"
    Codigo = Column("Código", Integer, primary_key=True, autoincrement=True)
    motivovisita = Column(String(255))


class TipoAcao(Base):
    """Tipos de ação em acompanhamentos. Ex: 'Encaminhamento', 'Orientação'."""
    __tablename__ = "TbTipoAcao"
    CodAcao = Column("CodAção", Integer, primary_key=True, autoincrement=True)
    DescricaoAcao = Column(String(255))


class TipoEvento(Base):
    """Tipos de eventos. Ex: 'Palestra', 'Capacitação', 'Reunião'."""
    __tablename__ = "TbTipoEvento"
    codigo = Column(Integer, primary_key=True, autoincrement=True)
    # nullable=False → todo tipo de evento precisa ter um nome
    tipoevento = Column(String(255), nullable=False)


class ChegouPrograma(Base):
    """Como a pessoa chegou ao programa. Ex: 'Denúncia', 'OUvidoria da SJDH'."""
    __tablename__ = "TbChegouPrograma"
    Codigo = Column("Código", Integer, primary_key=True, autoincrement=True)
    descricaochegouprograma = Column(String(255))


class Orgao(Base):
    """Órgãos parceiros para encaminhamento. Ex: 'CREAS', 'Delegacia do Idoso'."""
    __tablename__ = "TbOrgao"
    CodigoOrgao = Column(Integer, primary_key=True, autoincrement=True)
    TbNomeOrgao = Column(String(255))
    TbSiglaOrgao = Column(String(255))   # sigla curta: "CREAS", "MP", "SSP"


class Municipio(Base):
    """
    Municípios de Pernambuco com regionalização.
    AIS = Área Integrada de Saúde
    RD  = Região de Desenvolvimento
    """
    __tablename__ = "TbMunicipio"
    codigo = Column(Integer, primary_key=True, autoincrement=True)
    # A coluna no banco tem acento: "município" → mapeada como "municipio" no Python
    municipio = Column("município", String(255), nullable=False)
    AIS = Column(String(255))   # área de saúde integrada
    RD = Column(String(255))    # região de desenvolvimento
