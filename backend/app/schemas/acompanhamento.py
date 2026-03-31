# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: Acompanhamento
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, date
from typing import Optional
from app.schemas.common import ZeroDatetime


class AcompanhamentoBase(BaseModel):
    """Campos comuns. Validators de negócio ficam apenas em Create."""
    TbAcomCaso: int
    TbAcompdata: datetime
    TbAcompAcao: str
    TbCaraterAtendimento: str
    TbRelato: str
    TbTecnicoResponsavel: str
    TbAcompOrgao: Optional[str] = None
    TbAcompStatus: Optional[str] = None
    TbAcompPrazo: ZeroDatetime = None       # usa ZeroDatetime — pode ser "0000-00-00 00:00:00"


class AcompanhamentoCreate(AcompanhamentoBase):
    """Schema de criação — aqui ficam as regras de negócio."""

    @model_validator(mode="after")
    def validar_encaminhamento(self):
        """
        Validação cruzada: ação "Encaminhamento" exige que o órgão seja informado.
        model_validator(mode="after") roda depois de todos os campos serem validados,
        ideal para regras que dependem de mais de um campo simultaneamente.
        """
        if self.TbAcompAcao == "Encaminhamento" and not self.TbAcompOrgao:
            raise ValueError("Órgão é obrigatório quando a ação é Encaminhamento")
        return self

    @field_validator("TbAcompdata")
    @classmethod
    def data_nao_futura(cls, v):
        """Data do atendimento não pode ser no futuro."""
        if v.date() > date.today():
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
