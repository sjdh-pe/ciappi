# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Eventos — CRUD de eventos realizados pela equipe
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints disponíveis:
#   GET  /eventos        → lista todos os eventos
#   GET  /eventos/{id}   → detalhe de um evento
#   POST /eventos        → cria evento (nível ≥ 2)
#   PUT  /eventos/{id}   → atualiza evento / registra realização (nível ≥ 2)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_nivel
from app.schemas.evento import EventoCreate, EventoUpdate, EventoOut
from app.models.evento import Evento

router = APIRouter(prefix="/eventos", tags=["Eventos"])


# ── GET /eventos ──────────────────────────────────────────────────────────────
@router.get("/", response_model=list[EventoOut])
def listar(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Retorna todos os eventos sem paginação.
    Eventos tendem a ser poucos — sem necessidade de skip/limit aqui.
    """
    return db.query(Evento).all()


# ── GET /eventos/{codigo} ─────────────────────────────────────────────────────
@router.get("/{codigo}", response_model=EventoOut)
def detalhe(codigo: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    e = db.query(Evento).filter(Evento.Codigo == codigo).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return e


# ── POST /eventos ─────────────────────────────────────────────────────────────
@router.post("/", response_model=EventoOut, status_code=201)
def criar(data: EventoCreate, db: Session = Depends(get_db), _=Depends(require_nivel(2))):
    """
    Este router não usa um service separado para eventos — a lógica é simples:
    apenas cria o objeto e persiste. Regras mais complexas ficam nos validators
    do schema (ex: data prevista não pode ser no passado).

    Evento(**data.model_dump()) → cria o objeto ORM com os dados do schema.
    """
    evento = Evento(**data.model_dump())
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


# ── PUT /eventos/{codigo} ─────────────────────────────────────────────────────
@router.put("/{codigo}", response_model=EventoOut)
def atualizar(
    codigo: int,
    data: EventoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    Usado tanto para editar dados do planejamento quanto para registrar
    o resultado após a realização do evento (TbPublicoPresente, TbRelato...).

    data.model_dump(exclude_unset=True) → só altera os campos enviados.
    .items() → itera sobre pares (chave, valor) do dict.
    setattr(evento, campo, valor) → define evento.campo = valor dinamicamente.
    """
    evento = db.query(Evento).filter(Evento.Codigo == codigo).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(evento, campo, valor)

    db.commit()
    db.refresh(evento)
    return evento
