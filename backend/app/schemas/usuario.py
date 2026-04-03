# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: Usuário — validação dos dados da pessoa atendida
# ─────────────────────────────────────────────────────────────────────────────
# Campos de data usam ZeroDatetime para tolerar "0000-00-00 00:00:00" do legado.
# Validators de negócio (nome maiúsculo, sexo válido, data não futura) ficam
# em UsuarioCreate para não bloquear a leitura de dados históricos.

from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.common import ZeroDatetime


class UsuarioBase(BaseModel):
    # Optional em Base para tolerar NULLs do banco legado (Access).
    # UsuarioCreate redeclara esses campos como obrigatórios para novas entradas.
    tbcaso: Optional[int] = None
    tbnome: Optional[str] = None
    tbsexo: Optional[str] = None
    tbtecnicoresponsavel: Optional[str] = None

    # Datas — ZeroDatetime converte "0000-00-00 00:00:00" para None automaticamente
    tbdtcadastro: ZeroDatetime = None
    tbdtnascimento: ZeroDatetime = None
    tbidade: Optional[int] = None

    # Documentos
    tbnomesocial: Optional[str] = None
    tbnomepai: Optional[str] = None
    tbnomemae: Optional[str] = None
    tbcpf: Optional[str] = None
    tbrgnumero: Optional[str] = None
    tborgaoemissor: Optional[str] = None
    tbufemissor: Optional[str] = None
    tbdtexpedicao: ZeroDatetime = None
    tbctps: Optional[str] = None
    tbseriectps: Optional[str] = None
    tbnis: Optional[int] = None

    # Dados pessoais
    tborientacaosexual: Optional[str] = None
    tbidentidadesexual: Optional[str] = None
    tbracacor: Optional[str] = None
    tbnacionalidade: Optional[str] = None
    tbnaturalidade: Optional[str] = None
    tbreligiao: Optional[str] = None

    # Saúde
    tbdeficiente: Optional[str] = None
    tbdeficiencia: Optional[str] = None
    tbusuariodrogas: Optional[str] = None
    tbtipodrogas: Optional[str] = None
    tbhiv: Optional[str] = None
    tbusopreservativo: Optional[str] = None
    tbdoencacronica: Optional[str] = None
    tbdoenca: Optional[str] = None
    tbmedicamentocontinuo: Optional[str] = None
    tbmedicamentos: Optional[str] = None
    tbmonitorasaude: Optional[str] = None
    tbfrequenciaexame: Optional[str] = None

    # Situação social
    tbegresso: Optional[str] = None
    tbmoradorrua: Optional[str] = None
    tbsitmoradia: Optional[str] = None
    tbnumpessoascasa: Optional[int] = None
    tbvinculofamilar: Optional[str] = None

    # Endereço
    tblogradouro: Optional[str] = None
    tbnumero: Optional[str] = None
    tbcomplemento: Optional[str] = None
    tbbairro: Optional[str] = None
    tbmunicipio: Optional[str] = None
    tbuf: Optional[str] = None
    tbcepres: Optional[str] = None
    tbfone: Optional[str] = None
    tbcelular: Optional[str] = None
    tbemail: Optional[str] = None
    tbpontodereferencia: Optional[str] = None

    # Família
    tbestadocivil: Optional[str] = None
    tbsituacaoconujugal: Optional[str] = None
    tbpossuifilhos: Optional[str] = None
    tbnumfilhos: Optional[int] = None

    # Trabalho e renda
    tbescolaridade: Optional[str] = None
    tbestudante: Optional[str] = None
    tbocupacao: Optional[str] = None
    tbsitprofissional: Optional[str] = None
    tbregistroctps: Optional[str] = None
    tbprevidencia: Optional[str] = None
    tbinteressetrabalho: Optional[str] = None
    tbhabilidades1: Optional[str] = None
    tbexperiencia1: Optional[str] = None
    tbhabilidades2: Optional[str] = None
    tbexperiencia2: Optional[str] = None
    tbhabilidades3: Optional[str] = None
    tbexperiencia3: Optional[str] = None
    tbfaixarenda: Optional[str] = None
    tblocaltrabalho: Optional[str] = None
    tbmunicipiotrabalho: Optional[str] = None
    tbuftrabalho: Optional[str] = None
    tbrendafamiliar: Optional[str] = None
    tbbeneficiosocial: Optional[str] = None

    # Outros
    tboutroservico: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    """
    Schema de criação — campos obrigatórios redeclarados e validators de negócio.
    Redeclara tbcaso, tbnome, tbsexo, tbtecnicoresponsavel como não-opcionais.
    """
    tbcaso: int
    tbnome: str
    tbsexo: str
    tbtecnicoresponsavel: str

    @field_validator("tbnome")
    @classmethod
    def nome_maiusculo(cls, v):
        """Padroniza nome em maiúsculas antes de salvar."""
        return v.upper() if v else v

    @field_validator("tbsexo")
    @classmethod
    def sexo_valido(cls, v):
        """Aceita M ou F (maiúsculo ou minúsculo), converte para maiúsculo."""
        permitidos = {"M", "F", "m", "f"}
        if v and v not in permitidos:
            raise ValueError("tbsexo deve ser 'M' ou 'F'")
        return v.upper() if v else v


class UsuarioUpdate(BaseModel):
    """Schema de atualização — apenas campos comumente editados."""
    tbnome: Optional[str] = None
    tbsexo: Optional[str] = None
    tbtecnicoresponsavel: Optional[str] = None
    tbdtnascimento: ZeroDatetime = None
    tbidade: Optional[int] = None
    tbnomesocial: Optional[str] = None
    tbnomepai: Optional[str] = None
    tbnomemae: Optional[str] = None
    tbcpf: Optional[str] = None
    tbrgnumero: Optional[str] = None
    tblogradouro: Optional[str] = None
    tbnumero: Optional[str] = None
    tbcomplemento: Optional[str] = None
    tbbairro: Optional[str] = None
    tbmunicipio: Optional[str] = None
    tbuf: Optional[str] = None
    tbcepres: Optional[str] = None
    tbfone: Optional[str] = None
    tbcelular: Optional[str] = None
    tbemail: Optional[str] = None
    tbsitmoradia: Optional[str] = None
    tbestadocivil: Optional[str] = None
    tbrendafamiliar: Optional[str] = None
    tbbeneficiosocial: Optional[str] = None
    tbescolaridade: Optional[str] = None
    tbocupacao: Optional[str] = None
    tbfaixarenda: Optional[str] = None
    tboutroservico: Optional[str] = None


class UsuarioOut(UsuarioBase):
    """
    Schema de resposta — inclui o ID gerado pelo banco.
    Redeclara campos de data com ZeroDatetime para garantir que datas zeradas
    do legado (0000-00-00 00:00:00) sejam convertidas para None na serialização.
    """
    tbnumerocadastro: int
    # Redeclaração de campos de data com ZeroDatetime — CRUCIAL para resposta
    tbdtcadastro: ZeroDatetime = None
    tbdtnascimento: ZeroDatetime = None
    tbdtexpedicao: ZeroDatetime = None

    class Config:
        from_attributes = True
