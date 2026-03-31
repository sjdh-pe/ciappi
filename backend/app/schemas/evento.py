# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: Evento — validação dos dados de eventos
# ─────────────────────────────────────────────────────────────────────────────
# REGRA: validators de negócio (data não pode ser no passado) ficam SOMENTE
# em EventoCreate e EventoUpdate — nunca em EventoBase ou EventoOut.
# Motivo: EventoBase é herdado por EventoOut (response), então validators
# rodariam na saída e bloqueariam eventos antigos do banco com datas passadas.

from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import Optional
from app.schemas.common import ZeroDatetime   # trata "0000-00-00 00:00:00" → None


class EventoBase(BaseModel):
    """
    Campos comuns lidos/escritos. Sem validators de negócio aqui.
    Todos os campos de data usam ZeroDatetime para tolerar datas zeradas legadas.
    """
    tbtipoevento: str
    tbnomeevento: Optional[str] = None
    Tbobjetivoevento: Optional[str] = None
    Tbdataprevista: ZeroDatetime = None         # data prevista (pode ser zerada no legado)
    Tbpublicoalvo: Optional[str] = None
    TbPublicoEstimado: Optional[int] = None
    Tblocalevento: Optional[str] = None
    TbMunicipioevento: Optional[str] = None
    TbTecnicoResponsavel: Optional[int] = None


class EventoCreate(EventoBase):
    """
    Schema de criação — aqui ficam os validators de regra de negócio.
    Só rodam na ENTRADA (POST /eventos), não na leitura.
    """
    @field_validator("Tbdataprevista")
    @classmethod
    def data_prevista_nao_no_passado(cls, v):
        """Data prevista de evento não pode ser no passado (regra FrmCadEvento do Access)."""
        if v and v.date() < date.today():
            raise ValueError("A data prevista do evento não pode ser menor que a data de hoje.")
        return v


class EventoUpdate(BaseModel):
    """
    Schema de atualização — usado para registrar resultado do evento.
    Todos os campos opcionais. Validator de data só para Tbdataprevista.
    """
    Tbdataprevista: ZeroDatetime = None
    TbPublicoPresente: Optional[int] = None
    TbRelato: Optional[str] = None
    TbDataRealizacao: ZeroDatetime = None       # data real — pode ser passada (já aconteceu)
    TbTempoDuracao: ZeroDatetime = None
    Tbtecnicosenvolvidos: Optional[int] = None

    @field_validator("Tbdataprevista")
    @classmethod
    def data_prevista_nao_no_passado(cls, v):
        """Ao reagendar, a nova data também não pode ser no passado."""
        if v and v.date() < date.today():
            raise ValueError("A data prevista do evento não pode ser menor que a data de hoje.")
        return v


class EventoOut(EventoBase):
    """Schema de resposta — inclui ID e campos de resultado. Sem validators restritivos."""
    Codigo: int
    TbPublicoPresente: Optional[int] = None
    TbRelato: Optional[str] = None
    TbDataRealizacao: ZeroDatetime = None

    class Config:
        from_attributes = True
