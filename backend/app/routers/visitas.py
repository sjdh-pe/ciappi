# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Visitas — dois tipos de visita em um router só
# ─────────────────────────────────────────────────────────────────────────────
# Este router gerencia dois tipos distintos de visita, cada um com seu prefixo:
#
#   /visitas/inst → Visitas Institucionais (TbVisitaInst)
#                   Visitas a órgãos parceiros: delegacias, prefeituras, CREAS...
#
#   /visitas/ilpi → Visitas a ILPIs (TBAcompEntidade)
#                   Visitas de acompanhamento a instituições de longa permanência.
#                   Têm ciclo de vida: agendada → realizada.
#
# Por que um router só para dois tipos?
# → Ambos são "visitas" — faz sentido agrupá-los. Se ficarem muito grandes,
#   podem ser separados em arquivos distintos.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies import get_db, get_current_user, require_nivel
from app.models.visita_inst import VisitaInst
from app.models.visita_ilpi import VisitaILPI
from app.schemas.visita_inst import VisitaInstCreate, VisitaInstUpdate, VisitaInstOut
from app.schemas.visita_ilpi import (
    VisitaILPICreate, VisitaILPIUpdate, VisitaILPIRealizar, VisitaILPIOut
)
from app.services.visita_ilpi_service import (
    agendar_visita, realizar_visita, atualizar_visita, listar_visitas
)

router = APIRouter(prefix="/visitas", tags=["Visitas"])


# ═════════════════════════════════════════════════════════════════════════════
# VISITAS INSTITUCIONAIS — /visitas/inst
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/inst", response_model=list[VisitaInstOut])
def listar_inst(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """Lista todas as visitas institucionais."""
    return db.query(VisitaInst).all()


@router.get("/inst/{codigo}", response_model=VisitaInstOut)
def detalhe_inst(codigo: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    v = db.query(VisitaInst).filter(VisitaInst.codigovisita == codigo).first()
    if not v:
        raise HTTPException(status_code=404, detail="Visita institucional não encontrada")
    return v


@router.post("/inst", response_model=VisitaInstOut, status_code=201)
def criar_inst(
    data: VisitaInstCreate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """Registra uma visita institucional (sem ciclo agendado/realizado)."""
    visita = VisitaInst(**data.model_dump())
    db.add(visita)
    db.commit()
    db.refresh(visita)
    return visita


@router.put("/inst/{codigo}", response_model=VisitaInstOut)
def atualizar_inst(
    codigo: int,
    data: VisitaInstUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    v = db.query(VisitaInst).filter(VisitaInst.codigovisita == codigo).first()
    if not v:
        raise HTTPException(status_code=404, detail="Visita institucional não encontrada")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(v, campo, valor)
    db.commit()
    db.refresh(v)
    return v


# ═════════════════════════════════════════════════════════════════════════════
# VISITAS A ILPIs — /visitas/ilpi  (com ciclo agendada → realizada)
# ═════════════════════════════════════════════════════════════════════════════

@router.get("/ilpi", response_model=list[VisitaILPIOut])
def listar_ilpi(
    codigoilpi: Optional[int] = Query(None, description="Filtrar por ILPI"),
    # status pode ser "agendada" (pendente) ou "realizada" (concluída)
    status: Optional[str] = Query(None, description="'agendada' ou 'realizada'"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Lista visitas a ILPIs com filtros opcionais.
    - status=agendada  → visitas sem data de realização (dtvisita IS NULL)
    - status=realizada → visitas já realizadas (dtvisita IS NOT NULL)
    """
    apenas_agendadas = status == "agendada"
    apenas_realizadas = status == "realizada"
    return listar_visitas(
        db,
        codigoilpi=codigoilpi,
        apenas_agendadas=apenas_agendadas,
        apenas_realizadas=apenas_realizadas,
    )


@router.get("/ilpi/{codigo}", response_model=VisitaILPIOut)
def detalhe_ilpi(codigo: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    v = db.query(VisitaILPI).filter(VisitaILPI.Codigoentidade == codigo).first()
    if not v:
        raise HTTPException(status_code=404, detail="Visita à ILPI não encontrada")
    return v


@router.post("/ilpi", response_model=VisitaILPIOut, status_code=201)
def agendar(
    data: VisitaILPICreate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    FASE 1: Agenda uma visita a uma ILPI.
    Cria o registro sem data de realização (dtvisita = None).
    O service valida que a ILPI existe e que a data prevista não é passada.
    """
    try:
        return agendar_visita(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/ilpi/{codigo}/realizar", response_model=VisitaILPIOut)
def realizar(
    codigo: int,
    data: VisitaILPIRealizar,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    FASE 2: Registra a realização de uma visita agendada.
    Preenche dtvisita + relato. O service valida que:
      - A visita existe
      - Ainda não foi realizada (evita sobrescrever)
      - A data de realização não é futura
    """
    try:
        return realizar_visita(db, codigo, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/ilpi/{codigo}", response_model=VisitaILPIOut)
def atualizar_ilpi(
    codigo: int,
    data: VisitaILPIUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """Edição genérica de qualquer campo da visita à ILPI."""
    try:
        return atualizar_visita(db, codigo, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
