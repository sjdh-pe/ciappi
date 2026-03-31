# ─────────────────────────────────────────────────────────────────────────────
# MODEL: Usuario — tabela tbciappiusuario
# ─────────────────────────────────────────────────────────────────────────────
# Representa a pessoa idosa atendida pelo programa.
# (Não confundir com Tecnico — o técnico é quem OPERA o sistema;
#  o usuário é quem é ATENDIDO pelo sistema.)
#
# Esta tabela tem muitos campos porque captura um perfil socioeconômico
# completo da pessoa: dados pessoais, saúde, moradia, família, trabalho etc.
# Todos os campos (exceto os obrigatórios) são opcionais (nullable por padrão).
#
# Cada usuário está vinculado a um caso (tbcaso → TbCIAPPICaso.TbCasoNumCaso).

from sqlalchemy import Column, Integer, String, DateTime, Text, VARCHAR
from app.database import Base


class Usuario(Base):
    __tablename__ = "tbciappiusuario"  # nome em minúsculo — como está no banco

    # ── Chave primária ────────────────────────────────────────────────────────
    tbnumerocadastro = Column(Integer, primary_key=True, autoincrement=True)

    # ── Vínculo com o caso ────────────────────────────────────────────────────
    tbcaso = Column(Integer)       # FK lógica → TbCIAPPICaso.TbCasoNumCaso
    tbdtcadastro = Column(DateTime)

    # ── Dados pessoais ────────────────────────────────────────────────────────
    tbnomesocial = Column(Text)    # nome social (identidade de gênero)
    tbnome = Column(Text)          # nome completo (armazenado em maiúsculas)
    tbcelular = Column(Text)
    tbnomepai = Column(Text)
    tbnomemae = Column(Text)
    tbcpf = Column(Text)
    tbrgnumero = Column(Text)
    tborgaoemissor = Column(Text)  # órgão emissor do RG (ex: SSP/PE)
    tbufemissor = Column(Text)     # UF do órgão emissor
    tbdtexpedicao = Column(DateTime)
    tbctps = Column(Text)          # número da CTPS
    tbseriectps = Column(Text)
    tbnis = Column(Integer)        # NIS (Número de Identificação Social)
    # VARCHAR(1) porque sexo é "M" ou "F" — economiza espaço e documenta a regra
    tbsexo = Column(VARCHAR(1))
    tborientacaosexual = Column(Text)
    tbidentidadesexual = Column(Text)
    tbracacor = Column(Text)
    tbdtnascimento = Column(DateTime)
    tbidade = Column(Integer)
    tbnacionalidade = Column(Text)
    tbnaturalidade = Column(Text)

    # ── Saúde e perfil ────────────────────────────────────────────────────────
    tbreligiao = Column(Text)
    tbdeficiente = Column(Text)        # "Sim" / "Não"
    tbdeficiencia = Column(Text)       # descrição da deficiência
    tbusuariodrogas = Column(Text)     # "Sim" / "Não"
    tbtipodrogas = Column(Text)
    tbhiv = Column(Text)               # "Sim" / "Não"
    tbusopreservativo = Column(Text)
    tbdoencacronica = Column(Text)     # "Sim" / "Não"
    tbdoenca = Column(Text)
    tbmedicamentocontinuo = Column(Text)  # "Sim" / "Não"
    tbmedicamentos = Column(Text)
    tbmonitorasaude = Column(Text)
    tbfrequenciaexame = Column(Text)
    tbegresso = Column(Text)           # "Sim" / "Não" — ex-detento
    tbmoradorrua = Column(Text)        # "Sim" / "Não"

    # ── Endereço e contato ────────────────────────────────────────────────────
    tblogradouro = Column(Text)
    tbnumero = Column(Text)
    tbcomplemento = Column(Text)
    tbbairro = Column(Text)
    tbmunicipio = Column(Text)
    tbuf = Column(VARCHAR(2))          # UF com 2 caracteres: "PE", "SP" etc.
    tbcepres = Column(Text)
    tbfone = Column(Text)
    tbpontodereferencia = Column(Text)
    tbemail = Column(Text)

    # ── Escolaridade e trabalho ───────────────────────────────────────────────
    tbescolaridade = Column(Text)
    tbestudante = Column(Text)         # "Sim" / "Não"
    tbocupacao = Column(Text)
    tbsitprofissional = Column(Text)   # situação profissional
    tbinteressetrabalho = Column(Text)
    tbhabilidades1 = Column(Text)      # até 3 habilidades profissionais
    tbexperiencia1 = Column(Text)
    tbhabilidades2 = Column(Text)
    tbexperiencia2 = Column(Text)
    tbhabilidades3 = Column(Text)
    tbexperiencia3 = Column(Text)
    tbregistroctps = Column(Text)
    tbprevidencia = Column(Text)       # tipo de benefício previdenciário
    tbfaixarenda = Column(Text)
    tblocaltrabalho = Column(Text)
    tbmunicipiotrabalho = Column(Text)
    tbuftrabalho = Column(VARCHAR(2))
    tbbeneficiosocial = Column(Text)   # benefícios sociais recebidos

    # ── Família e moradia ─────────────────────────────────────────────────────
    tbpossuifilhos = Column(Text)      # "Sim" / "Não"
    tbnumfilhos = Column(Integer)
    tbrendafamiliar = Column(Text)
    tbestadocivil = Column(Text)
    tbsituacaoconujugal = Column(Text)
    tbtecnicoresponsavel = Column(Text)  # técnico responsável pelo usuário
    tbsitmoradia = Column(Text)          # situação de moradia
    tbcomquemmora = Column(Text)
    tbnumpessoascasa = Column(Integer)
    tbvinculofamilar = Column(Text)      # vínculo com família (atenção: typo original "familar")
    tboutroservico = Column(Text)        # outros serviços que a pessoa acessa
