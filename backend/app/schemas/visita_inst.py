# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: VisitaInst — validação de visitas a instituições parceiras
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import Optional
from app.schemas.common import ZeroDatetime


class VisitaInstBase(BaseModel):
    """Campos comuns. ZeroDatetime trata '0000-00-00 00:00:00' automaticamente."""
    nomeinstituicao: str
    assuntovisita: Optional[str] = None
    responsavelinstituicao: Optional[str] = None
    datavista: ZeroDatetime = None
    lembrete: ZeroDatetime = None
    relatorio: Optional[str] = None
    tecnicoresponsavel: Optional[int] = None


class VisitaInstCreate(VisitaInstBase):
    pass


class VisitaInstUpdate(BaseModel):
    """Schema de atualização — todos os campos opcionais."""
    nomeinstituicao: Optional[str] = None
    assuntovisita: Optional[str] = None
    responsavelinstituicao: Optional[str] = None
    datavista: ZeroDatetime = None
    lembrete: ZeroDatetime = None
    relatorio: Optional[str] = None
    tecnicoresponsavel: Optional[int] = None


class VisitaInstOut(VisitaInstBase):
    codigovisita: int

    class Config:
        from_attributes = True
