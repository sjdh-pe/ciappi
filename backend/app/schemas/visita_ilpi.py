# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: VisitaILPI — validação de visitas a ILPIs
# ─────────────────────────────────────────────────────────────────────────────
# Validator de "data não pode ser no passado" fica somente em VisitaILPICreate,
# não em VisitaILPIBase — para não bloquear visitas antigas na resposta.
#
# Campos obrigatórios também ficam somente no Create: Base tem tudo Optional
# para tolerar NULLs do banco legado (Access). O field_validator to_upper foi
# movido do Base para o Create pelo mesmo motivo.

from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import Optional
from app.schemas.common import ZeroDatetime


class VisitaILPIBase(BaseModel):
    """
    Campos comuns entre criação e resposta.
    Todos Optional para tolerar NULLs do legado. Validator to_upper movido para Create.
    """
    codigoilpi: Optional[int] = None
    nomeentidade: Optional[str] = None
    tecnicoresponsavel: Optional[str] = None
    dtprevistavisita: ZeroDatetime = None
    motivovisita: Optional[str] = None
    observacoes: Optional[str] = None


class VisitaILPICreate(VisitaILPIBase):
    """
    Schema de agendamento — campos obrigatórios redeclarados como não-opcionais,
    validator to_upper e validação de data prevista não-passada.
    """
    codigoilpi: int
    nomeentidade: str
    tecnicoresponsavel: str

    @field_validator("nomeentidade", "tecnicoresponsavel")
    @classmethod
    def to_upper(cls, v):
        """Padroniza em maiúsculas. Só roda na criação."""
        return v.upper() if v else v

    @field_validator("dtprevistavisita")
    @classmethod
    def data_prevista_nao_passada(cls, v):
        if v and v.date() < date.today():
            raise ValueError("A data prevista da visita não pode ser no passado.")
        return v


class VisitaILPIRealizar(BaseModel):
    """
    Schema para registrar a realização de uma visita agendada.
    Operação de negócio distinta: requer data + relato e a data não pode ser futura.
    """
    dtvisita: datetime
    relato: str
    motivovisita: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator("dtvisita")
    @classmethod
    def data_realizacao_nao_futura(cls, v):
        if v.date() > date.today():
            raise ValueError("A data de realização não pode ser maior que hoje.")
        return v


class VisitaILPIUpdate(BaseModel):
    """Schema de atualização genérica — todos os campos opcionais."""
    dtprevistavisita: ZeroDatetime = None
    dtvisita: ZeroDatetime = None
    motivovisita: Optional[str] = None
    relato: Optional[str] = None
    tecnicoresponsavel: Optional[str] = None
    observacoes: Optional[str] = None


class VisitaILPIOut(VisitaILPIBase):
    """Schema de resposta — inclui ID e campos de realização."""
    Codigoentidade: int
    dtvisita: ZeroDatetime = None
    relato: Optional[str] = None

    class Config:
        from_attributes = True
