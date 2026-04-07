# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: Acompanhamento
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date
from typing import Optional
from app.schemas.common import ZeroDatetime


class AcompanhamentoBase(BaseModel):
    """
    Campos comuns. Validators de negócio ficam apenas em Create.

    TODOS os campos que podem ter NULL no banco legado (Access) são Optional aqui.
    AcompanhamentoCreate redeclara os obrigatórios como não-opcionais para novas entradas.
    """
    # Optional em Base para tolerar NULLs do legado; obrigatórios somente no Create
    TbAcomCaso: Optional[int] = None
    TbAcompdata: ZeroDatetime = None        # ZeroDatetime: trata "0000-00-00" → None
    TbAcompAcao: Optional[str] = None
    TbCaraterAtendimento: Optional[str] = None
    TbRelato: Optional[str] = None
    TbTecnicoResponsavel: Optional[str] = None
    TbAcompOrgao: Optional[str] = None
    TbAcompStatus: Optional[str] = None
    TbAcompPrazo: ZeroDatetime = None       # usa ZeroDatetime — pode ser "0000-00-00 00:00:00"


class AcompanhamentoCreate(AcompanhamentoBase):
    """
    Schema de criação — campos obrigatórios redeclarados como não-opcionais
    e validators de regra de negócio ficam aqui.
    """
    # Redeclara como obrigatórios (override do Optional da Base)
    TbAcomCaso: int
    TbAcompdata: datetime
    TbAcompAcao: str
    TbCaraterAtendimento: str
    TbRelato: str
    TbTecnicoResponsavel: str

    @model_validator(mode="after")
    def validar_encaminhamento(self):
        """
        Validação cruzada: ações de encaminhamento exigem órgão de destino.
        Usa checagem parcial (case-insensitive) porque o banco legado tem
        variações como "Encaminhamento para outro órgão", "Encaminhamento", etc.
        """
        if (self.TbAcompAcao
                and "encaminhamento" in self.TbAcompAcao.lower()
                and not self.TbAcompOrgao):
            raise ValueError("Órgão é obrigatório quando a ação é de encaminhamento")
        return self

    @field_validator("TbAcompdata")
    @classmethod
    def data_nao_futura(cls, v):
        """Data do atendimento não pode ser no futuro."""
        if v and v.date() > date.today():
            raise ValueError("Data não pode ser maior que hoje")
        return v


class AcompanhamentoUpdate(BaseModel):
    """Schema de atualização — todos os campos opcionais."""
    TbAcompdata: Optional[datetime] = None
    TbAcompAcao: Optional[str] = None
    TbAcompOrgao: Optional[str] = None
    TbAcompStatus: Optional[str] = None
    TbAcompPrazo: ZeroDatetime = None
    TbCaraterAtendimento: Optional[str] = None
    TbRelato: Optional[str] = None
    TbTecnicoResponsavel: Optional[str] = None


class AcompanhamentoOut(AcompanhamentoBase):
    """Schema de resposta — inclui o ID gerado pelo banco."""
    tbcodigo: int

    class Config:
        from_attributes = True
