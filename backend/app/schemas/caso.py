# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: Caso — validação e serialização dos dados de caso
# ─────────────────────────────────────────────────────────────────────────────
# Este arquivo define como os dados de um Caso são validados ao ENTRAR na API
# (request) e serializados ao SAIR (response).
#
# Padrão de herança usado em todo o projeto:
#   Base    → campos comuns (usados em criação e leitura)
#   Create  → herda Base + campos obrigatórios para criar
#   Update  → todos os campos opcionais (para PATCH/PUT parcial)
#   Out     → herda Base + campos extras que só existem na resposta
#
# Por que separar Create e Update?
#   No Create: todos os campos obrigatórios devem estar presentes.
#   No Update: apenas os campos enviados são alterados (exclude_unset=True).

from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.common import ZeroDatetime   # trata "0000-00-00 00:00:00" → None

# Valores válidos para o campo de ambiente de violência
AMBIENTES_VALIDOS = {"Intrafamiliar", "Extrafamiliar"}


class CasoBase(BaseModel):
    """
    Campos presentes tanto na criação quanto na resposta.

    IMPORTANTE: NÃO colocar validators de regra de negócio aqui!
    CasoBase é herdado por CasoOut (resposta), então validators aqui
    rodariam também na SAÍDA — e quebrariam ao ler registros antigos do
    banco que têm valores fora do padrão (ex: 'ILPI' em Tbambienteviolencia).
    Validators de negócio ficam apenas em CasoCreate e CasoUpdate.
    """
    TbCasoNumCaso: int
    TbCasoDtinicio: ZeroDatetime    # usa nosso tipo customizado para datas zeradas
    tbnomeidoso: Optional[str] = None
    TbCasoMotivoAtendimento: Optional[str] = None
    TbCasoChegouPrograma: Optional[str] = None
    Tbambienteviolencia: Optional[str] = None   # pode conter valores legados (ex: 'ILPI')
    TbCasoRelato: Optional[str] = None
    # Optional em Base para tolerar NULLs do banco legado.
    # CasoCreate redeclara esses campos como str (obrigatórios) para novas entradas.
    TbCasoMunicipio: Optional[str] = None
    TbCasoTecnicoResp: Optional[str] = None


class CasoCreate(CasoBase):
    """
    Schema para criar um novo caso (POST /casos).
    Aqui ficam os validators de regra de negócio — só rodam na ENTRADA (request).
    Campos obrigatórios para criação são declarados sem default.
    """
    tbnomeidoso: str                # obrigatório na criação
    TbCasoMotivoAtendimento: str
    TbCasoChegouPrograma: str
    Tbambienteviolencia: str        # validado abaixo
    TbCasoRelato: str
    TbCasoMunicipio: str            # obrigatório na criação (Base permite NULL para leitura)
    TbCasoTecnicoResp: str

    @field_validator("tbnomeidoso", "TbCasoMunicipio", "TbCasoTecnicoResp")
    @classmethod
    def to_upper(cls, v):
        """
        Converte automaticamente para maiúsculas antes de salvar.
        @classmethod é obrigatório em field_validators do Pydantic v2.
        """
        return v.upper() if v else v

    @field_validator("Tbambienteviolencia")
    @classmethod
    def ambiente_valido(cls, v):
        """
        Garante que ambiente seja exatamente 'Intrafamiliar' ou 'Extrafamiliar'.
        Se não for, lança ValueError que o Pydantic transforma em HTTP 422.
        Fica SOMENTE no Create para não bloquear a leitura de dados legados.
        """
        if v not in AMBIENTES_VALIDOS:
            raise ValueError(
                f"Ambiente de violência deve ser 'Intrafamiliar' ou 'Extrafamiliar'. Recebido: '{v}'"
            )
        return v


class CasoUpdate(BaseModel):
    """
    Schema para atualizar um caso (PUT /casos/{id}).
    TODOS os campos são Optional — o cliente pode enviar apenas os que quer alterar.
    O service usa model_dump(exclude_unset=True) para só atualizar o que foi enviado.
    """
    tbnomeidoso: Optional[str] = None
    TbCasoDtinicio: ZeroDatetime = None
    TbCasoMotivoAtendimento: Optional[str] = None
    TbCasoChegouPrograma: Optional[str] = None
    Tbambienteviolencia: Optional[str] = None
    TbCasoRelato: Optional[str] = None
    TbCasoMunicipio: Optional[str] = None
    TbCasoTecnicoResp: Optional[str] = None
    # Campos de encerramento — só preenchidos ao encerrar o caso
    TbCasoDtencer: ZeroDatetime = None
    TbCasoMotivoEncerramento: Optional[int] = None
    TbObservacoes: Optional[str] = None
    TbCasoEncerrado: Optional[str] = None
    TbNumDenuncia: Optional[int] = None
    # Campos de ouvidoria
    TbPrazoOuvidoria: ZeroDatetime = None
    TbNumOfOuvidoria: Optional[str] = None

    @field_validator("Tbambienteviolencia")
    @classmethod
    def ambiente_valido(cls, v):
        # No Update, o campo é Optional — só valida se foi realmente enviado (não None).
        # Isso permite atualizar outros campos sem tocar no ambiente.
        if v is not None and v not in AMBIENTES_VALIDOS:
            raise ValueError(
                f"Ambiente de violência deve ser 'Intrafamiliar' ou 'Extrafamiliar'. Recebido: '{v}'"
            )
        return v


class CasoOut(CasoBase):
    """
    Schema de resposta (o que a API retorna ao cliente).
    Herda CasoBase + adiciona campos que só existem em casos já criados/encerrados.

    class Config com from_attributes=True permite que o Pydantic leia
    diretamente de um objeto SQLAlchemy (em vez de exigir um dict).
    Sem isso, response_model=CasoOut não funcionaria com o ORM.
    """
    TbCasoDtencer: ZeroDatetime = None
    TbCasoMotivoEncerramento: Optional[int] = None
    TbCasoEncerrado: Optional[str] = None
    TbObservacoes: Optional[str] = None
    TbNumDenuncia: Optional[int] = None
    TbPrazoOuvidoria: ZeroDatetime = None
    TbEncerradoOuvidoria: Optional[str] = None
    TbDtEncerradoOuvidoria: ZeroDatetime = None
    TbNumOfOuvidoria: Optional[str] = None

    class Config:
        from_attributes = True  # permite ler atributos de objetos ORM


class CasoRestaura(BaseModel):
    """Schema para reabrir um caso encerrado (PUT /casos/{id}/restaurar)."""
    motivo_restauracao: int  # código do motivo → TbMotivoRestauracao.Codigo
