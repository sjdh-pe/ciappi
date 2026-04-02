# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: ILPI — validação dos dados de instituições de longa permanência
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.common import ZeroDatetime


class ILPIBase(BaseModel):
    """
    Campos comuns entre criação e resposta.

    TODOS os campos são Optional aqui para tolerar NULLs do banco legado (Access).
    O field_validator to_upper foi movido para ILPICreate — se ficasse na Base,
    rodaria também na resposta (ILPIOut) e causaria erro ao ler registros com NULL.
    ILPICreate redeclara os campos obrigatórios como não-opcionais.
    """
    NOMEILPI: Optional[str] = None
    RESPONSAVELILPI: Optional[str] = None
    TIPOENTIDADE: Optional[str] = None
    CAPACIDADEIDOSOS: Optional[int] = None
    IDOSOSRESIDENTES: Optional[int] = None
    LOGRADOURO: Optional[str] = None
    BAIRRO: Optional[str] = None
    MUNICIPIO: Optional[str] = None
    PERSONALIDADEJURIDICA: Optional[str] = None
    FONEFIXO: Optional[str] = None
    CELULAR: Optional[str] = None
    NUMEROIMOVEL: Optional[str] = None
    COMPLEMENTO: Optional[str] = None
    PONTODEREFERENCIA: Optional[str] = None
    STATUS: Optional[str] = None
    AVALIACAO: Optional[str] = None


class ILPICreate(ILPIBase):
    """
    Schema de criação — campos obrigatórios redeclarados como não-opcionais
    e validator de maiúsculas movido aqui para não rodar na leitura.
    """
    # Redeclara como obrigatórios (override do Optional da Base)
    NOMEILPI: str
    RESPONSAVELILPI: str
    TIPOENTIDADE: str
    CAPACIDADEIDOSOS: int
    IDOSOSRESIDENTES: int
    LOGRADOURO: str
    BAIRRO: str
    MUNICIPIO: str
    DATACADASTRO: ZeroDatetime = None

    @field_validator("NOMEILPI", "RESPONSAVELILPI", "LOGRADOURO", "BAIRRO", "MUNICIPIO")
    @classmethod
    def to_upper(cls, v):
        """Padroniza campos de texto em maiúsculas. Só roda na criação."""
        return v.upper() if v else v


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
