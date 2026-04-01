import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import Optional
from app.dependencies import get_db, get_current_user
from app.models.caso import Caso
from app.models.acompanhamento import Acompanhamento
from app.models.usuario import Usuario
from app.models.evento import Evento
from app.models.visita_inst import VisitaInst
from app.models.visita_ilpi import VisitaILPI

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _dt(v) -> str | None:
    """
    Converte datetime → string ISO 8601 para garantir serialização JSON segura.
    Retorna None se o valor for None.
    Objetos datetime dentro de dicts retornados diretamente pelo FastAPI
    precisam ser strings — sem response_model, o FastAPI não converte
    automaticamente.
    """
    if v is None:
        return None
    try:
        return v.isoformat()
    except Exception:
        return str(v)


def _caso_dict(c: Caso) -> dict:
    """
    Converte um objeto ORM Caso em dict JSON-seguro.
    Sem este helper, retornar q.all() de uma query de modelo ORM gera erro
    de serialização porque os objetos SQLAlchemy não são JSON-serializáveis.
    """
    return {
        "TbCasoNumCaso": c.TbCasoNumCaso,
        "TbCasoDtinicio": _dt(c.TbCasoDtinicio),
        "tbnomeidoso": c.tbnomeidoso,
        "TbCasoMotivoAtendimento": c.TbCasoMotivoAtendimento,
        "TbCasoChegouPrograma": c.TbCasoChegouPrograma,
        "Tbambienteviolencia": c.Tbambienteviolencia,
        "TbCasoMunicipio": c.TbCasoMunicipio,
        "TbCasoTecnicoResp": c.TbCasoTecnicoResp,
        "TbCasoEncerrado": c.TbCasoEncerrado,
        "TbCasoDtencer": _dt(c.TbCasoDtencer),
        "TbCasoMotivoEncerramento": c.TbCasoMotivoEncerramento,
        "TbNumDenuncia": c.TbNumDenuncia,
        "TbPrazoOuvidoria": _dt(c.TbPrazoOuvidoria),
        "TbEncerradoOuvidoria": c.TbEncerradoOuvidoria,
        "TbDtEncerradoOuvidoria": _dt(c.TbDtEncerradoOuvidoria),
        "TbNumOfOuvidoria": c.TbNumOfOuvidoria,
    }


def _acomp_dict(a: Acompanhamento) -> dict:
    """Converte objeto ORM Acompanhamento em dict JSON-seguro."""
    return {
        "tbcodigo": a.tbcodigo,
        "TbAcomCaso": a.TbAcomCaso,
        "TbAcompdata": _dt(a.TbAcompdata),
        "TbAcompAcao": a.TbAcompAcao,
        "TbAcompOrgao": a.TbAcompOrgao,
        "TbAcompStatus": a.TbAcompStatus,
        "TbAcompPrazo": _dt(a.TbAcompPrazo),
        "TbCaraterAtendimento": a.TbCaraterAtendimento,
        "TbRelato": a.TbRelato,
        "TbTecnicoResponsavel": a.TbTecnicoResponsavel,
    }


def _evento_dict(e: Evento) -> dict:
    """Converte objeto ORM Evento em dict JSON-seguro."""
    return {
        "Codigo": e.Codigo,
        "tbtipoevento": e.tbtipoevento,
        "tbnomeevento": e.tbnomeevento,
        "Tbobjetivoevento": e.Tbobjetivoevento,
        "Tbdataprevista": _dt(e.Tbdataprevista),
        "Tbpublicoalvo": e.Tbpublicoalvo,
        "TbPublicoEstimado": e.TbPublicoEstimado,
        "Tblocalevento": e.Tblocalevento,
        "TbMunicipioevento": e.TbMunicipioevento,
        "TbTecnicoResponsavel": e.TbTecnicoResponsavel,
        "TbPublicoPresente": e.TbPublicoPresente,
        "TbRelato": e.TbRelato,
        "TbDataRealizacao": _dt(e.TbDataRealizacao),
    }


def _visita_ilpi_dict(v: VisitaILPI) -> dict:
    """Converte objeto ORM VisitaILPI em dict JSON-seguro."""
    return {
        "Codigoentidade": v.Codigoentidade,
        "codigoilpi": v.codigoilpi,
        "nomeentidade": v.nomeentidade,
        "dtprevistavisita": _dt(v.dtprevistavisita),
        "dtvisita": _dt(v.dtvisita),
        "motivovisita": v.motivovisita,
        "relato": v.relato,
        "tecnicoresponsavel": v.tecnicoresponsavel,
        "observacoes": v.observacoes,
    }


def _visita_inst_dict(v: VisitaInst) -> dict:
    """Converte objeto ORM VisitaInst em dict JSON-seguro."""
    return {
        "codigovisita": v.codigovisita,
        "nomeinstituicao": v.nomeinstituicao,
        "datavista": _dt(v.datavista),
        "assuntovisita": v.assuntovisita,
        "responsavelinstituicao": v.responsavelinstituicao,
        "lembrete": _dt(v.lembrete),
        "relatorio": v.relatorio,
        "tecnicoresponsavel": v.tecnicoresponsavel,
    }


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


# ─────────────────────────────────────────────────────────────────────────────
# CASOS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/casos-ativos")
def casos_ativos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Casos ativos com último acompanhamento (CnCasoAtivo do Access).
    Retorna caso + última ação + data do último acompanhamento + total.
    """
    # Subquery: data do último acompanhamento de cada caso (uma única query no banco)
    subq = (
        db.query(
            Acompanhamento.TbAcomCaso,
            func.max(Acompanhamento.TbAcompdata).label("ultima_data"),
        )
        .group_by(Acompanhamento.TbAcomCaso)
        .subquery()
    )

    casos = (
        db.query(Caso)
        .filter(
            (Caso.TbCasoEncerrado.is_(None)) | (Caso.TbCasoEncerrado == "Não")
        )
        .all()
    )

    # Monta dict: num_caso → {ultima_acao, ultima_data_acomp}
    # Join com o subquery para pegar a ação do último acompanhamento
    ult_map = {}
    for row in (
        db.query(
            Acompanhamento.TbAcomCaso,
            Acompanhamento.TbAcompAcao,
            Acompanhamento.TbAcompdata,
        )
        .join(
            subq,
            and_(
                Acompanhamento.TbAcomCaso == subq.c.TbAcomCaso,
                Acompanhamento.TbAcompdata == subq.c.ultima_data,
            ),
        )
        .all()
    ):
        ult_map[row.TbAcomCaso] = {
            "ultima_acao": row.TbAcompAcao,
            "ultima_data_acomp": _dt(row.TbAcompdata),
        }

    resultado = []
    for c in casos:
        resultado.append({
            "TbCasoNumCaso": c.TbCasoNumCaso,
            "TbCasoDtinicio": _dt(c.TbCasoDtinicio),
            "tbnomeidoso": c.tbnomeidoso,
            "TbCasoTecnicoResp": c.TbCasoTecnicoResp,
            "TbCasoMunicipio": c.TbCasoMunicipio,
            "TbCasoMotivoAtendimento": c.TbCasoMotivoAtendimento,
            **ult_map.get(c.TbCasoNumCaso, {"ultima_acao": None, "ultima_data_acomp": None}),
        })

    return {"total": len(resultado), "casos": resultado}


@router.get("/casos-parados")
def casos_parados(
    dias: int = Query(30, description="Casos sem acompanhamento há pelo menos N dias"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Casos ativos sem acompanhamento há pelo menos N dias (CnParados do Access).

    Correção de N+1: a versão anterior fazia uma query por caso para buscar
    o último acompanhamento. Agora usamos um LEFT JOIN com subquery para
    resolver tudo em uma única consulta ao banco.
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

    # LEFT JOIN: inclui casos sem nenhum acompanhamento (ultima_data = NULL)
    # Filtra: ativos E (sem acompanhamento OU último acompanhamento antes do corte)
    rows = (
        db.query(Caso, subq.c.ultima_data)
        .outerjoin(subq, Caso.TbCasoNumCaso == subq.c.TbAcomCaso)
        .filter(
            (Caso.TbCasoEncerrado.is_(None)) | (Caso.TbCasoEncerrado == "Não")
        )
        .filter(
            (subq.c.ultima_data.is_(None)) | (subq.c.ultima_data < corte)
        )
        .all()
    )

    resultado = []
    for caso, ultima_data in rows:
        dias_parado = (datetime.now() - ultima_data).days if ultima_data else None
        resultado.append({
            "TbCasoNumCaso": caso.TbCasoNumCaso,
            "TbCasoDtinicio": _dt(caso.TbCasoDtinicio),
            "tbnomeidoso": caso.tbnomeidoso,
            "TbCasoMotivoAtendimento": caso.TbCasoMotivoAtendimento,
            "TbCasoTecnicoResp": caso.TbCasoTecnicoResp,
            "ultima_data_acomp": _dt(ultima_data),
            "dias_sem_acomp": dias_parado,
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

    COALESCE(TbCasoDtencer, TbCasoDtinicio): casos migrados do Access têm
    TbCasoEncerrado = "Sim" mas TbCasoDtencer = NULL (data zerada virou NULL).
    Fallback para TbCasoDtinicio garante que esses casos apareçam no relatório.
    """
    data_ref = func.coalesce(Caso.TbCasoDtencer, Caso.TbCasoDtinicio)

    q = db.query(Caso).filter(Caso.TbCasoEncerrado == "Sim")
    if dt_ini:
        q = q.filter(data_ref >= dt_ini)
    if dt_fim:
        q = q.filter(data_ref <= dt_fim)

    return [_caso_dict(c) for c in q.order_by(
        func.coalesce(Caso.TbCasoDtencer, Caso.TbCasoDtinicio).desc()
    ).all()]


@router.get("/encerrados-resolutividade")
def encerrados_resolutividade(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Casos encerrados agrupados por motivo de encerramento (CnEncerradoResolutividade).
    """
    data_ref = func.coalesce(Caso.TbCasoDtencer, Caso.TbCasoDtinicio)

    q_resumo = (
        db.query(
            Caso.TbCasoMotivoEncerramento,
            func.count(Caso.TbCasoNumCaso).label("total"),
        )
        .filter(Caso.TbCasoEncerrado == "Sim")
        .filter(Caso.TbCasoMotivoEncerramento.isnot(None))
        .group_by(Caso.TbCasoMotivoEncerramento)
    )
    if dt_ini:
        q_resumo = q_resumo.filter(data_ref >= dt_ini)
    if dt_fim:
        q_resumo = q_resumo.filter(data_ref <= dt_fim)

    q_detalhe = (
        db.query(Caso)
        .filter(Caso.TbCasoEncerrado == "Sim")
    )
    if dt_ini:
        q_detalhe = q_detalhe.filter(data_ref >= dt_ini)
    if dt_fim:
        q_detalhe = q_detalhe.filter(data_ref <= dt_fim)

    return {
        "resumo_por_motivo": [
            {"motivo_encerramento": r.TbCasoMotivoEncerramento, "total": r.total}
            for r in q_resumo.all()
        ],
        "casos": [
            {
                "TbCasoNumCaso": c.TbCasoNumCaso,
                "tbnomeidoso": c.tbnomeidoso,
                # Mostra TbCasoDtencer real; se NULL, exibe TbCasoDtinicio como referência
                "TbCasoDtencer": _dt(c.TbCasoDtencer or c.TbCasoDtinicio),
                "TbCasoMotivoAtendimento": c.TbCasoMotivoAtendimento,
                "TbCasoMotivoEncerramento": c.TbCasoMotivoEncerramento,
            }
            for c in q_detalhe.all()
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# MUNICÍPIOS / GEOGRAFIA
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/municipio")
def por_municipio(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Ranking de casos por município (CnMunicipio2 do Access).

    Correção: .all() em queries agregadas retorna Row tuples que serializam
    como arrays [[municipio, total]] em vez de [{municipio, total}].
    Convertemos explicitamente para dicts.
    """
    rows = (
        db.query(Caso.TbCasoMunicipio, func.count(Caso.TbCasoNumCaso).label("total"))
        .group_by(Caso.TbCasoMunicipio)
        .order_by(func.count(Caso.TbCasoNumCaso).desc())
        .all()
    )
    return [{"municipio": r.TbCasoMunicipio, "total": r.total} for r in rows]


@router.get("/municipio-idoso")
def municipio_idoso(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Ranking de municípios de residência dos idosos atendidos."""
    rows = (
        db.query(Usuario.tbmunicipio, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbmunicipio.isnot(None))
        .group_by(Usuario.tbmunicipio)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"municipio": r.tbmunicipio, "total": r.total} for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# VIOLÊNCIA
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/violencia")
def por_tipo_violencia(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Contagem de casos por tipo/motivo de violência no período."""
    q = (
        db.query(
            Caso.TbCasoMotivoAtendimento,
            func.count(Caso.TbCasoNumCaso).label("total"),
        )
        .group_by(Caso.TbCasoMotivoAtendimento)
    )
    if dt_ini:
        q = q.filter(Caso.TbCasoDtinicio >= dt_ini)
    if dt_fim:
        q = q.filter(Caso.TbCasoDtinicio <= dt_fim)
    return [{"tipo_violencia": r.TbCasoMotivoAtendimento, "total": r.total} for r in q.all()]


@router.get("/violencia-bairro")
def violencia_por_bairro(
    municipio: Optional[str] = Query(None, description="Filtrar por município"),
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Violência por bairro de residência do idoso (CnBairroTotal do Access)."""
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

    rows = (
        q.group_by(Usuario.tbbairro, Usuario.tbmunicipio)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"bairro": r.tbbairro, "municipio": r.tbmunicipio, "total": r.total} for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# ACOMPANHAMENTOS
# ─────────────────────────────────────────────────────────────────────────────

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

    # Agrega por caráter de atendimento
    q_carater = (
        db.query(
            Acompanhamento.TbCaraterAtendimento,
            func.count(Acompanhamento.tbcodigo).label("total"),
        )
        .group_by(Acompanhamento.TbCaraterAtendimento)
    )
    if dt_ini:
        q_carater = q_carater.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q_carater = q_carater.filter(Acompanhamento.TbAcompdata <= dt_fim)

    # Agrega por tipo de ação
    q_acao = (
        db.query(
            Acompanhamento.TbAcompAcao,
            func.count(Acompanhamento.tbcodigo).label("total"),
        )
        .group_by(Acompanhamento.TbAcompAcao)
    )
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
        # Converte ORM objects para dicts — objetos SQLAlchemy não são JSON-serializáveis
        "registros": [_acomp_dict(a) for a in registros],
    }


@router.get("/acomp-por-tecnico")
def acomp_por_tecnico(
    tecnico: str = Query(..., description="Nome do técnico"),
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Acompanhamentos de um técnico específico por período (CnAcompEspec do Access)."""
    q = db.query(Acompanhamento).filter(
        Acompanhamento.TbTecnicoResponsavel.ilike(f"%{tecnico}%")
    )
    if dt_ini:
        q = q.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q = q.filter(Acompanhamento.TbAcompdata <= dt_fim)

    registros = q.all()

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
        "registros": [_acomp_dict(a) for a in registros],
    }


@router.get("/encaminhamentos")
def encaminhamentos(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Última ação de encaminhamento por caso (CnUltMovimentacao do Access)."""
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
        .join(
            subq,
            and_(
                Acompanhamento.TbAcomCaso == subq.c.TbAcomCaso,
                Acompanhamento.TbAcompdata == subq.c.ultima_data,
            ),
        )
    )
    if dt_ini:
        q = q.filter(Acompanhamento.TbAcompdata >= dt_ini)
    if dt_fim:
        q = q.filter(Acompanhamento.TbAcompdata <= dt_fim)

    return [
        {
            "TbCasoNumCaso": r.TbCasoNumCaso,
            "tbnomeidoso": r.tbnomeidoso,
            "TbAcompdata": _dt(r.TbAcompdata),
            "TbAcompOrgao": r.TbAcompOrgao,
            "TbAcompAcao": r.TbAcompAcao,
        }
        for r in q.order_by(Acompanhamento.TbAcompdata).all()
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ORIGEM
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/origem")
def por_origem(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Contagem de casos por canal de origem (como chegou ao programa)."""
    rows = (
        db.query(
            Caso.TbCasoChegouPrograma,
            func.count(Caso.TbCasoNumCaso).label("total"),
        )
        .group_by(Caso.TbCasoChegouPrograma)
        .order_by(func.count(Caso.TbCasoNumCaso).desc())
        .all()
    )
    return [{"origem": r.TbCasoChegouPrograma, "total": r.total} for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# EVENTOS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/eventos")
def eventos_periodo(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Eventos realizados no período (filtra por TbDataRealizacao).
    Sem filtro de data retorna todos os eventos (planejados e realizados).
    """
    q = db.query(Evento)
    if dt_ini:
        q = q.filter(Evento.TbDataRealizacao >= dt_ini)
    if dt_fim:
        q = q.filter(Evento.TbDataRealizacao <= dt_fim)
    return [_evento_dict(e) for e in q.all()]


@router.get("/eventos-por-municipio")
def eventos_por_municipio(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Ranking de eventos realizados por município."""
    rows = (
        db.query(
            Evento.TbMunicipioevento,
            func.count(Evento.Codigo).label("total"),
        )
        .filter(Evento.TbMunicipioevento.isnot(None))
        .group_by(Evento.TbMunicipioevento)
        .order_by(func.count(Evento.Codigo).desc())
        .all()
    )
    return [{"municipio": r.TbMunicipioevento, "total": r.total} for r in rows]


# ─────────────────────────────────────────────────────────────────────────────
# PERFIL DOS ATENDIDOS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/perfil/escolaridade")
def perfil_escolaridade(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por escolaridade."""
    rows = (
        db.query(Usuario.tbescolaridade, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbescolaridade.isnot(None))
        .group_by(Usuario.tbescolaridade)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"escolaridade": r.tbescolaridade, "total": r.total} for r in rows]


@router.get("/perfil/faixa-etaria")
def perfil_faixa_etaria(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por faixa etária (calculada a partir de tbidade)."""
    faixa = case(
        (Usuario.tbidade < 65, "Até 64 anos"),
        (Usuario.tbidade.between(65, 74), "65 a 74 anos"),
        (Usuario.tbidade.between(75, 84), "75 a 84 anos"),
        (Usuario.tbidade >= 85, "85 anos ou mais"),
        else_="Não informado",
    )
    rows = (
        db.query(faixa.label("faixa_etaria"), func.count(Usuario.tbnumerocadastro).label("total"))
        .group_by(faixa)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"faixa_etaria": r.faixa_etaria, "total": r.total} for r in rows]


@router.get("/perfil/renda")
def perfil_renda(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por faixa de renda familiar."""
    rows = (
        db.query(Usuario.tbfaixarenda, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbfaixarenda.isnot(None))
        .group_by(Usuario.tbfaixarenda)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"faixa_renda": r.tbfaixarenda, "total": r.total} for r in rows]


@router.get("/perfil/sexo")
def perfil_sexo(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por sexo."""
    rows = (
        db.query(Usuario.tbsexo, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbsexo.isnot(None))
        .group_by(Usuario.tbsexo)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"sexo": r.tbsexo, "total": r.total} for r in rows]


@router.get("/perfil/raca-cor")
def perfil_raca_cor(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por raça/cor."""
    rows = (
        db.query(Usuario.tbracacor, func.count(Usuario.tbnumerocadastro).label("total"))
        .filter(Usuario.tbracacor.isnot(None))
        .group_by(Usuario.tbracacor)
        .order_by(func.count(Usuario.tbnumerocadastro).desc())
        .all()
    )
    return [{"raca_cor": r.tbracacor, "total": r.total} for r in rows]


@router.get("/perfil/mobilidade")
def perfil_mobilidade(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Distribuição dos atendidos por situação de moradia, morador de rua e benefício social."""
    def _agg(campo, label):
        rows = (
            db.query(campo, func.count(Usuario.tbnumerocadastro).label("total"))
            .filter(campo.isnot(None))
            .group_by(campo)
            .order_by(func.count(Usuario.tbnumerocadastro).desc())
            .all()
        )
        return [{label: r[0], "total": r[1]} for r in rows]

    return {
        "situacao_moradia": _agg(Usuario.tbsitmoradia, "situacao"),
        "morador_rua": _agg(Usuario.tbmoradorrua, "morador_rua"),
        "beneficio_social": _agg(Usuario.tbbeneficiosocial, "beneficio"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# VISITAS
# ─────────────────────────────────────────────────────────────────────────────

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
    return [_visita_ilpi_dict(v) for v in q.order_by(VisitaILPI.dtvisita).all()]


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
    return [_visita_inst_dict(v) for v in q.order_by(VisitaInst.datavista).all()]


# ─────────────────────────────────────────────────────────────────────────────
# EXPORTS CSV
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/csv/casos-ativos", response_class=StreamingResponse)
def csv_casos_ativos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Download CSV de casos ativos com último acompanhamento."""
    dados = casos_ativos(db=db, _=_)
    return _to_csv(dados.get("casos", []), "casos_ativos.csv")


@router.get("/csv/casos-parados", response_class=StreamingResponse)
def csv_casos_parados(
    dias: int = Query(30),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Download CSV de casos parados há N dias."""
    dados = casos_parados(dias=dias, db=db, _=_)
    return _to_csv(dados.get("casos", []), f"casos_parados_{dias}dias.csv")


@router.get("/csv/encaminhamentos", response_class=StreamingResponse)
def csv_encaminhamentos(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Download CSV de encaminhamentos."""
    rows = encaminhamentos(dt_ini=dt_ini, dt_fim=dt_fim, db=db, _=_)
    return _to_csv(rows, "encaminhamentos.csv")


@router.get("/csv/municipio", response_class=StreamingResponse)
def csv_municipio(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Download CSV de ranking por município."""
    rows = por_municipio(db=db, _=_)
    return _to_csv(rows, "municipios.csv")


@router.get("/csv/violencia", response_class=StreamingResponse)
def csv_violencia(
    dt_ini: Optional[datetime] = Query(None),
    dt_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Download CSV de tipos de violência."""
    rows = por_tipo_violencia(dt_ini=dt_ini, dt_fim=dt_fim, db=db, _=_)
    return _to_csv(rows, "violencia.csv")
