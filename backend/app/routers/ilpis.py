# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: ILPIs — CRUD de instituições de longa permanência
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints disponíveis:
#   GET  /ilpis        → lista todas as ILPIs
#   GET  /ilpis/{id}   → detalhe de uma ILPI
#   POST /ilpis        → cadastra ILPI (nível ≥ 2)
#   PUT  /ilpis/{id}   → atualiza dados (nível ≥ 2)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_nivel
from app.schemas.ilpi import ILPICreate, ILPIUpdate, ILPIOut
from app.models.ilpi import ILPI

router = APIRouter(prefix="/ilpis", tags=["ILPIs"])


# ── GET /ilpis ────────────────────────────────────────────────────────────────
@router.get("/", response_model=list[ILPIOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(ILPI).order_by(ILPI.CODIGOILPI.desc()).all()


# ── GET /ilpis/{codigo} ───────────────────────────────────────────────────────
@router.get("/{codigo}", response_model=ILPIOut)
def detalhe(codigo: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    i = db.query(ILPI).filter(ILPI.CODIGOILPI == codigo).first()
    if not i:
        raise HTTPException(status_code=404, detail="ILPI não encontrada")
    return i


# ── POST /ilpis ───────────────────────────────────────────────────────────────
@router.post("/", response_model=ILPIOut, status_code=201)
def criar(data: ILPICreate, db: Session = Depends(get_db), _=Depends(require_nivel(2))):
    ilpi = ILPI(**data.model_dump())
    db.add(ilpi)
    db.commit()
    db.refresh(ilpi)
    return ilpi


# ── PUT /ilpis/{codigo} ───────────────────────────────────────────────────────
@router.put("/{codigo}", response_model=ILPIOut)
def atualizar(
    codigo: int,
    data: ILPIUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    Permite atualizar campos operacionais da ILPI:
    responsável, capacidade, status, fechamento/reabertura.

    ILPIUpdate não inclui nome nem endereço (dados cadastrais estáveis)
    — se precisar mudar, seria necessário um endpoint específico ou
    um nível de acesso mais alto.
    """
    ilpi = db.query(ILPI).filter(ILPI.CODIGOILPI == codigo).first()
    if not ilpi:
        raise HTTPException(status_code=404, detail="ILPI não encontrada")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(ilpi, campo, valor)

    db.commit()
    db.refresh(ilpi)
    return ilpi
