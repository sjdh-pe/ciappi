import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from typing import Optional
from app.dependencies import get_db, get_current_user
from app.models.caso import Caso
from app.models.acompanhamento import Acompanhamento
from app.models.usuario import Usuario
from app.models.evento import Evento
from app.models.visita_inst import VisitaInst
from app.models.visita_ilpi import VisitaILPI


def _to_csv(rows: list[dict], filename: str) -> StreamingResponse:
    """Converte lista de dicts para resposta CSV com download."""
    if not rows:
        buf = io.StringIO()
        buf.write("sem_dados\n")
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


# ──────────────────────────────────────────────────────────────
# Casos
# ──────────────────────────────────────────────────────────────

@router.get("/casos-ativos")
def casos_ativos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Casos ativos com último acompanhamento (CnCasoAtivo do Access).
    Retorna caso + última ação + data do último acompanhamento + total.
    """
    # Subquery: último acompanhamento de cada caso
    subq = (
        db.query(
            Acompanhamento.TbAcomCaso,
            func.max(Acompanhamento.TbAcompdata).label("ultima_data"),
        )
        .group_by(Acompanhamento.TbAcomCaso)
        .subquery()
    )

    # Ultimo acompanhamento com ação
    ultimo_acomp = (
        db.query(Acompanhamento)
        .join(subq, and_(
            Acompanhamento.TbAcomCaso == subq.c.TbAcomCaso,
            Acompanhamento.TbAcompdata == subq.c.ultima_data,
        ))
        .subquery()
    )

    casos = (
        db.query(Caso)
        .filter(
            (Caso.TbCasoEncerrado.is_(None)) | (Caso.TbCasoEncerrado == "Não")
        )
        .all()
    )

    # Monta dicionário de último acompanhamento por caso
    ult_map = {}
    for row in db.query(
        Acompanhamento.TbAcomCaso,
        Acompanhamento.TbAcompAcao,
        Acompanhamento.TbAcompdata,
    ).join(subq, and_(
        Acompanhamento.TbAcomCaso == subq.c.TbAcomCaso,
        Acompanhamento.TbAcompdata == subq.c.ultima_data,
    )).all():
        ult_map[row.TbAcomCaso] = {
            "ultima_acao": row.TbAcompAcao,
            "ultima_data_acomp": row.TbAcompdata,
        }

    resultado = []
    for c in casos:
        item = {
            "TbCasoNumCaso": c.TbCasoNumCaso,
            "TbCasoDtinicio": c.TbCasoDtinicio,
            "tbnomeidoso": c.tbnomeidoso,
            "TbCasoTecnicoResp": c.TbCasoTecnicoResp,
            "TbCasoMunicipio": c.TbCasoMunicipio,
            "TbCasoMotivoAtendimento": c.TbCasoMotivoAtendimento,
            **ult_map.get(c.TbCasoNumCaso, {"ultima_acao": None, "ultima_data_acomp": None}),
        }
        resultado.append(item)

    return {"total": len(resultado), "casos": resultado}


@router.get("/casos-parados")
def casos_parados(
    dias: int = Query(30, description="Casos sem acompanhamento há pelo menos N dias"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Casos ativos sem acompanhamento há pelo menos `dias` dias (CnParados do Access).
    """
    corte = datetime.now() - timedelta(days=dias)

    # Subquery: data do último acompanhamento por caso
    subq = (
        db.query(
            Acompanhamento.TbAcomCaso,
            func.max(Acompanhamento.TbAcompdata).label("ultima_data"),
        )
        .group_by(Acompanhamento.TbAcomCaso)
        .subquery()
    )

    # Casos ativos cujo último acompanhamento é antes do corte (ou não têm nenhum)
    casos_ativos_ids = (
        db.query(Caso.TbCasoNumCaso)
        .filter(
            (Caso.TbCasoEncerrado.is_(None)) | (Caso.TbCasoEncerrado == "Não")
        )
    )

    resultado = []
    for caso in (
        db.query(Caso)
        .filter(
            (Caso.TbCasoEncerrado.is_(None)) | (Caso.TbCasoEncerrado == "Não")
        )
        .all()
    ):
        ult = (
            db.query(func.max(Acompanhamento.TbAcompdata))
            .filter(Acompanhamento.TbAcomCaso == caso.TbCasoNumCaso)
            .scalar()
        )
        if ult is None or ult < corte:
            resultado.append({
                "TbCasoNumCaso": caso.TbCasoNumCaso,
                "TbCasoDtinicio": caso.TbCasoDtinicio,
                "tbnomeidoso": caso.tbnomeidoso,
                "TbCasoMotivoAtendimento": caso.TbCasoMotivoAtendimento,
                "TbCasoTecnicoResp": caso.TbCasoTecnicoResp,
                "ultima_data_acomp": ult,
                "dias_sem_acomp": (datetime.now() - ult).days if ult else None,
            })

    return {"total": len(resultado), "dias_filtro": dias, "casos": resultado}


@router.get("/encerrados")
def encerrados(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Lista casos encerrados dentro do período informado.

    Problema do legado Access: muitos casos têm TbCasoEncerrado = "Sim"
    mas TbCasoDtencer = NULL (a data zerada "0000-00-00" virou NULL na migração).
    Solução: COALESCE(TbCasoDtencer, TbCasoDtinicio) — se não tiver data de
    encerramento, usa a data de abertura do caso como referência para o filtro.
    Assim os casos antigos continuam aparecendo nos relatórios por período.
    """
    # COALESCE: usa TbCasoDtencer se preenchida, senão usa TbCasoDtinicio
    data_ref = func.coalesce(Caso.TbCasoDtencer, Caso.TbCasoDtinicio)

    q = db.query(Caso).filter(Caso.TbCasoEncerrado == "Sim")
    if dt_ini:
        q = q.filter(data_ref >= dt_ini)
    if dt_fim:
        q = q.filter(data_ref <= dt_fim)
    return q.all()


@router.get("/encerrados-resolutividade")
def encerrados_resolutividade(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Casos encerrados com motivo de encerramento (CnEncerradoResolutividade do Access).
    Agrupa por motivo para medir resolutividade.
    """
    # Mesma lógica de COALESCE: fallback para TbCasoDtinicio quando TbCasoDtencer é NULL
    data_ref = func.coalesce(Caso.TbCasoDtencer, Caso.TbCasoDtinicio)

    q = (
        db.query(
            Caso.TbCasoMotivoEncerramento,
            func.count(Caso.TbCasoNumCaso).label("total"),
        )
        .filter(Caso.TbCasoEncerrado == "Sim")
        .filter(Caso.TbCasoMotivoEncerramento.isnot(None))
        .group_by(Caso.TbCasoMotivoEncerramento)
    )
    if dt_ini:
        q = q.filter(data_ref >= dt_ini)
    if dt_fim:
        q = q.filter(data_ref <= dt_fim)

    # Detalhe dos casos também
    q_detalhe = db.query(
        Caso.TbCasoNumCaso,
        Caso.tbnomeidoso,
        Caso.TbCasoDtencer,
        Caso.TbCasoDtinicio,
        Caso.TbCasoMotivoAtendimento,
        Caso.TbCasoMotivoEncerramento,
    ).filter(Caso.TbCasoEncerrado == "Sim")
    if dt_ini:
        q_detalhe = q_detalhe.filter(data_ref >= dt_ini)
    if dt_fim:
        q_detalhe = q_detalhe.filter(data_ref <= dt_fim)

    return {
        "resumo_por_motivo": [
            {"motivo_encerramento": r.TbCasoMotivoEncerramento, "total": r.total}
            for r in q.all()
        ],
        "casos": [
            {
                "TbCasoNumCaso": r.TbCasoNumCaso,
                "tbnomeidoso": r.tbnomeidoso,
                # Mostra a data de encerramento real; se NULL, mostra a data de abertura
                "TbCasoDtencer": r.TbCasoDtencer or r.TbCasoDtinicio,
                "TbCasoMotivoAtendimento": r.TbCasoMotivoAtendimento,
                "TbCasoMotivoEncerramento": r.TbCasoMotivoEncerramento,
            }
            for r in q_detalhe.all()
        ],
    }


# ──────────────────────────────────────────────────────────────
# Municípios / Geografia
# ──────────────────────────────────────────────────────────────

@router.get("/municipio")
def por_municipio(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Ranking de casos por município (CnMunicipio2 do Access)."""
    return (
        db.query(Caso.TbCasoMunicipio, func.count(Caso.TbCasoNumCaso).label("total"))
        .group_by(Caso.TbCasoMunicipio)
        .order_by(func.count(Caso.TbCasoNumCaso).desc())
        .all()
    )


@router.get("/municipio-idoso")
def municipio_idoso(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Ranking de municípios de residência dos idosos atendidos (CnMunicipio2 do Access).
    Cruza com TbCIAPPIUsuario.tbmunicipio.
    """
    return (
        db.query(Usuario.tbmunicipio, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbmunicipio.isnot(None))
        .group_by(Usuario.tbmunicipio)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


# ──────────────────────────────────────────────────────────────
# Violência
# ──────────────────────────────────────────────────────────────

@router.get("/violencia")
def por_tipo_violencia(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(
        Caso.TbCasoMotivoAtendimento,
        func.count(Caso.TbCasoNumCaso).label("total")
    ).group_by(Caso.TbCasoMotivoAtendimento)
    if dt_ini:
        q = q.filter(Caso.TbCasoDtinicio >= dt_ini)
    if dt_fim:
        q = q.filter(Caso.TbCasoDtinicio <= dt_fim)
    return q.all()


@router.get("/violencia-bairro")
def violencia_por_bairro(
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Violência por bairro de residência do idoso (CnBairroTotal do Access).
    Cruza TbCIAPPICaso com TbCIAPPIUsuario via TbCaso → TbCasoNumCaso.
    """
    q = (
        db.query(
            Usuario.tbbairro,
            Usuario.tbmunicipio,
            func.count(Usuario.tbnumerocadastro).label("total"),
        )
        .join(Caso, Caso.TbCasoNumCaso == Usuario.tbcaso)
        .filter(Usuario.tbbairro.isnot(None))
    )
    if municipio:
        q = q.filter(Usuario.tbmunicipio.ilike(f"%{municipio}%"))
    if dt_ini:
        q = q.filter(Caso.TbCasoDtinicio >= dt_ini)
    if dt_fim:
        q = q.filter(Caso.TbCasoDtinicio <= dt_fim)

    return (
        q.group_by(Usuario.tbbairro, Usuario.tbmunicipio)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


# ──────────────────────────────────────────────────────────────
# Acompanhamentos
# ──────────────────────────────────────────────────────────────

@router.get("/acompanhamentos")
def acompanhamentos_periodo(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Acompanhamentos por período com agregações (CnAcomp11/12/13 do Access).
    Retorna lista, contagem por caráter e contagem por tipo de ação.
    """
    q = db.query(Acompanhamento)
    if dt_ini:
        q = q.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q = q.filter(Acompanhamento.TbAcompdata <= dt_fim)

    registros = q.all()

    # CnAcomp12 — agrega por caráter de atendimento
    q_carater = db.query(
        Acompanhamento.TbCaraterAtendimento,
        func.count(Acompanhamento.tbcodigo).label("total"),
    ).group_by(Acompanhamento.TbCaraterAtendimento)
    if dt_ini:
        q_carater = q_carater.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q_carater = q_carater.filter(Acompanhamento.TbAcompdata <= dt_fim)

    # CnAcomp13 — agrega por tipo de ação
    q_acao = db.query(
        Acompanhamento.TbAcompAcao,
        func.count(Acompanhamento.tbcodigo).label("total"),
    ).group_by(Acompanhamento.TbAcompAcao)
    if dt_ini:
        q_acao = q_acao.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q_acao = q_acao.filter(Acompanhamento.TbAcompdata <= dt_fim)

    return {
        "total": len(registros),
        "por_carater": [
            {"carater": r.TbCaraterAtendimento, "total": r.total}
            for r in q_carater.all()
        ],
        "por_acao": [
            {"acao": r.TbAcompAcao, "total": r.total}
            for r in q_acao.all()
        ],
        "registros": registros,
    }


@router.get("/acomp-por-tecnico")
def acomp_por_tecnico(
    tecnico: str = Query(..., description="Nome do técnico"),
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Acompanhamentos de um técnico específico por período (CnAcompEspec do Access).
    Retorna lista e contagem por tipo de ação.
    """
    q = db.query(Acompanhamento).filter(
        Acompanhamento.TbTecnicoResponsavel.ilike(f"%{tecnico}%")
    )
    if dt_ini:
        q = q.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q = q.filter(Acompanhamento.TbAcompdata <= dt_fim)

    registros = q.all()

    # Agrega por tipo de ação (CnAcompEspec2)
    q_acao = (
        db.query(
            Acompanhamento.TbAcompAcao,
            func.count(Acompanhamento.tbcodigo).label("total"),
        )
        .filter(Acompanhamento.TbTecnicoResponsavel.ilike(f"%{tecnico}%"))
        .group_by(Acompanhamento.TbAcompAcao)
    )
    if dt_ini:
        q_acao = q_acao.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q_acao = q_acao.filter(Acompanhamento.TbAcompdata <= dt_fim)

    return {
        "tecnico": tecnico,
        "total": len(registros),
        "por_acao": [
            {"acao": r.TbAcompAcao, "total": r.total}
            for r in q_acao.all()
        ],
        "registros": registros,
    }


@router.get("/encaminhamentos")
def encaminhamentos(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Última movimentação (encaminhamento) de cada caso (CnUltMovimentacao do Access).
    Retorna casos com última ação = encaminhamento para outro órgão.
    """
    # Subquery: último acompanhamento de cada caso
    subq = (
        db.query(
            Acompanhamento.TbAcomCaso,
            func.max(Acompanhamento.TbAcompdata).label("ultima_data"),
        )
        .filter(Acompanhamento.TbAcompAcao.ilike("%encaminhamento%"))
        .group_by(Acompanhamento.TbAcomCaso)
        .subquery()
    )

    q = (
        db.query(
            Caso.TbCasoNumCaso,
            Caso.tbnomeidoso,
            Acompanhamento.TbAcompdata,
            Acompanhamento.TbAcompOrgao,
            Acompanhamento.TbAcompAcao,
        )
        .join(Caso, Caso.TbCasoNumCaso == Acompanhamento.TbAcomCaso)
        .join(subq, and_(
            Acompanhamento.TbAcomCaso == subq.c.TbAcomCaso,
            Acompanhamento.TbAcompdata == subq.c.ultima_data,
        ))
    )
    if dt_ini:
        q = q.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q = q.filter(Acompanhamento.TbAcompdata <= dt_fim)

    return [
        {
            "TbCasoNumCaso": r.TbCasoNumCaso,
            "tbnomeidoso": r.tbnomeidoso,
            "TbAcompdata": r.TbAcompdata,
            "TbAcompOrgao": r.TbAcompOrgao,
            "TbAcompAcao": r.TbAcompAcao,
        }
        for r in q.order_by(Acompanhamento.TbAcompdata).all()
    ]


# ──────────────────────────────────────────────────────────────
# Origem
# ──────────────────────────────────────────────────────────────

@router.get("/origem")
def por_origem(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(Caso.TbCasoChegouPrograma, func.count(Caso.TbCasoNumCaso).label("total"))
        .group_by(Caso.TbCasoChegouPrograma)
        .all()
    )


# ──────────────────────────────────────────────────────────────
# Eventos
# ──────────────────────────────────────────────────────────────

@router.get("/eventos")
def eventos_periodo(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Evento)
    if dt_ini:
        q = q.filter(Evento.TbDataRealizacao >= dt_ini)
    if dt_fim:
        q = q.filter(Evento.TbDataRealizacao <= dt_fim)
    return q.all()


@router.get("/eventos-por-municipio")
def eventos_por_municipio(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Ranking de eventos realizados por município."""
    return (
        db.query(
            Evento.TbMunicipioevento,
            func.count(Evento.Codigo).label("total"),
        )
        .filter(Evento.TbMunicipioevento.isnot(None))
        .group_by(Evento.TbMunicipioevento)
        .order_by(func.count(Evento.Codigo).desc())
        .all()
    )


# ──────────────────────────────────────────────────────────────
# Perfil dos Atendidos
# ──────────────────────────────────────────────────────────────

@router.get("/perfil/escolaridade")
def perfil_escolaridade(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por escolaridade."""
    return (
        db.query(Usuario.tbescolaridade, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbescolaridade.isnot(None))
        .group_by(Usuario.tbescolaridade)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


@router.get("/perfil/faixa-etaria")
def perfil_faixa_etaria(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por faixa etária (calculada a partir de tbidade)."""
    from sqlalchemy import case

    faixa = case(
        (Usuario.tbidade < 65, "Até 64 anos"),
        (Usuario.tbidade.between(65, 74), "65 a 74 anos"),
        (Usuario.tbidade.between(75, 84), "75 a 84 anos"),
        (Usuario.tbidade >= 85, "85 anos ou mais"),
        else_="Não informado",
    )

    return (
        db.query(faixa.label("faixa_etaria"), func.count(Usuario.tbnumerocadastro).label("total"))
        .group_by(faixa)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


@router.get("/perfil/renda")
def perfil_renda(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por faixa de renda familiar."""
    return (
        db.query(Usuario.tbfaixarenda, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbfaixarenda.isnot(None))
        .group_by(Usuario.tbfaixarenda)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


@router.get("/perfil/sexo")
def perfil_sexo(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por sexo."""
    return (
        db.query(Usuario.tbsexo, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbsexo.isnot(None))
        .group_by(Usuario.tbsexo)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


@router.get("/perfil/raca-cor")
def perfil_raca_cor(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por raça/cor."""
    return (
        db.query(Usuario.tbracacor, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbracacor.isnot(None))
        .group_by(Usuario.tbracacor)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )


@router.get("/perfil/mobilidade")
def perfil_mobilidade(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por situação de moradia e mobilidade social."""
    return {
        "situacao_moradia": [
            {"situacao": r.tbsitmoradia, "total": r.total}
            for r in db.query(
                Usuario.tbsitmoradia,
                func.count(Usuario.tbnumerocadastro).label("total"),
            )
            .filter(Usuario.tbsitmoradia.isnot(None))
            .group_by(Usuario.tbsitmoradia)
            .order_by(func.count(Usuario.tbnumerocadastro).desc())
            .all()
        ],
        "morador_rua": [
            {"morador_rua": r.tbmoradorrua, "total": r.total}
            for r in db.query(
                Usuario.tbmoradorrua,
                func.count(Usuario.tbnumerocadastro).label("total"),
            )
            .filter(Usuario.tbmoradorrua.isnot(None))
            .group_by(Usuario.tbmoradorrua)
            .all()
        ],
        "beneficio_social": [
            {"beneficio": r.tbbeneficiosocial, "total": r.total}
            for r in db.query(
                Usuario.tbbeneficiosocial,
                func.count(Usuario.tbnumerocadastro).label("total"),
            )
            .filter(Usuario.tbbeneficiosocial.isnot(None))
            .group_by(Usuario.tbbeneficiosocial)
            .order_by(func.count(Usuario.tbnumerocadastro).desc())
            .all()
        ],
    }


# ──────────────────────────────────────────────────────────────
# Visitas
# ──────────────────────────────────────────────────────────────

@router.get("/visitas-ilpi")
def visitas_ilpi(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Relatório de visitas a ILPIs realizadas no período."""
    q = db.query(VisitaILPI).filter(VisitaILPI.dtvisita.isnot(None))
    if dt_ini:
        q = q.filter(VisitaILPI.dtvisita >= dt_ini)
    if dt_fim:
        q = q.filter(VisitaILPI.dtvisita <= dt_fim)
    return q.order_by(VisitaILPI.dtvisita).all()


@router.get("/visitas-inst")
def visitas_inst(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Relatório de visitas institucionais realizadas no período."""
    q = db.query(VisitaInst)
    if dt_ini:
        q = q.filter(VisitaInst.datavista >= dt_ini)
    if dt_fim:
        q = q.filter(VisitaInst.datavista <= dt_fim)
    return q.order_by(VisitaInst.datavista).all()


# ──────────────────────────────────────────────────────────────
# Exports CSV
# ──────────────────────────────────────────────────────────────

@router.get("/csv/casos-ativos", response_class=StreamingResponse)
def csv_casos_ativos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Download CSV de casos ativos com último acompanhamento."""
    dados = casos_ativos(db=db, _=_)
    rows = dados.get("casos", [])
    for r in rows:
        for k, v in r.items():
            if hasattr(v, "isoformat"):
                r[k] = v.isoformat()
    return _to_csv(rows, "casos_ativos.csv")


@router.get("/csv/casos-parados", response_class=StreamingResponse)
def csv_casos_parados(
    dias: int = Query(30),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Download CSV de casos parados há N dias."""
    dados = casos_parados(dias=dias, db=db, _=_)
    rows = dados.get("casos", [])
    for r in rows:
        for k, v in r.items():
            if hasattr(v, "isoformat"):
                r[k] = v.isoformat()
    return _to_csv(rows, f"casos_parados_{dias}dias.csv")


@router.get("/csv/encaminhamentos", response_class=StreamingResponse)
def csv_encaminhamentos(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Download CSV de encaminhamentos."""
    rows = encaminhamentos(dt_ini=dt_ini, dt_fim=dt_fim, db=db, _=_)
    for r in rows:
        for k, v in r.items():
            if hasattr(v, "isoformat"):
                r[k] = v.isoformat()
    return _to_csv(rows, "encaminhamentos.csv")


@router.get("/csv/municipio", response_class=StreamingResponse)
def csv_municipio(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Download CSV de ranking por município."""
    rows = [{"municipio": r[0], "total": r[1]} for r in por_municipio(db=db, _=_)]
    return _to_csv(rows, "municipios.csv")


@router.get("/csv/violencia", response_class=StreamingResponse)
def csv_violencia(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Download CSV de tipos de violência."""
    rows = [{"tipo_violencia": r[0], "total": r[1]}
            for r in por_tipo_violencia(dt_ini=dt_ini, dt_fim=dt_fim, db=db, _=_)]
    return _to_csv(rows, "violencia.csv")
