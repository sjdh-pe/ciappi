# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: ILPI — validação dos dados de instituições de longa permanência
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.common import ZeroDatetime


class ILPIBase(BaseModel):
    """Campos obrigatórios e comuns. Sem validators de negócio."""
    NOMEILPI: str
    RESPONSAVELILPI: str
    TIPOENTIDADE: str
    CAPACIDADEIDOSOS: int
    IDOSOSRESIDENTES: int
    LOGRADOURO: str
    BAIRRO: str
    MUNICIPIO: str
    PERSONALIDADEJURIDICA: Optional[str] = None
    FONEFIXO: Optional[str] = None
    CELULAR: Optional[str] = None
    NUMEROIMOVEL: Optional[str] = None
    COMPLEMENTO: Optional[str] = None
    PONTODEREFERENCIA: Optional[str] = None
    STATUS: Optional[str] = None
    AVALIACAO: Optional[str] = None

    @field_validator("NOMEILPI", "RESPONSAVELILPI", "LOGRADOURO", "BAIRRO", "MUNICIPIO")
    @classmethod
    def to_upper(cls, v):
        """Padroniza campos de texto em maiúsculas."""
        return v.upper() if v else v


class ILPICreate(ILPIBase):
    """Schema de criação — adiciona data de cadastro opcional."""
    DATACADASTRO: ZeroDatetime = None


class ILPIUpdate(BaseModel):
    """Schema de atualização — apenas campos operacionais."""
    RESPONSAVELILPI: Optional[str] = None
    CAPACIDADEIDOSOS: Optional[int] = None
    IDOSOSRESIDENTES: Optional[int] = None
    FONEFIXO: Optional[str] = None
    CELULAR: Optional[str] = None
    STATUS: Optional[str] = None
    AVALIACAO: Optional[str] = None
    DATAFECHAMENTO: ZeroDatetime = None
    DATAREABERTURA: ZeroDatetime = None


class ILPIOut(ILPIBase):
    """Schema de resposta — inclui ID e datas."""
    CODIGOILPI: int
    DATACADASTRO: ZeroDatetime = None

    class Config:
        from_attributes = True
