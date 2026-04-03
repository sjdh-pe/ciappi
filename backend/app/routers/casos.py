# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Casos — CRUD e fluxo de vida dos casos
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints disponíveis:
#   GET    /casos               → lista casos com filtros
#   GET    /casos/{id}          → detalhe de um caso
#   POST   /casos               → cria novo caso (nível ≥ 2)
#   PUT    /casos/{id}          → atualiza / encerra caso (nível ≥ 2)
#   PUT    /casos/{id}/restaurar → reabre caso encerrado (nível ≥ 2)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies import get_db, get_current_user, require_nivel
from app.schemas.caso import CasoCreate, CasoUpdate, CasoOut, CasoRestaura
from app.services.caso_service import criar_caso, atualizar_caso, restaurar_caso, listar_casos
from app.models.caso import Caso

router = APIRouter(prefix="/casos", tags=["Casos"])


# ── GET /casos ────────────────────────────────────────────────────────────────
@router.get("/", response_model=list[CasoOut])
def listar(
    # Query() define parâmetros de URL: /casos?municipio=Recife&encerrado=Não
    # None como default significa que o filtro é opcional
    municipio: Optional[str] = Query(None),
    encerrado: Optional[str] = Query(None),
    tecnico: Optional[str] = Query(None),
    motivo: Optional[str] = Query(None, description="Filtra por tipo de violência (TbCasoMotivoAtendimento)"),
    skip: int = 0,      # paginação: quantos registros pular
    limit: int = 100,   # paginação: máximo de registros por página
    db: Session = Depends(get_db),
    _=Depends(get_current_user),  # _ significa "não uso o retorno, só valido o token"
):
    return listar_casos(db, municipio, encerrado, tecnico, motivo, skip, limit)


# ── GET /casos/{num_caso} ─────────────────────────────────────────────────────
@router.get("/{num_caso}", response_model=CasoOut)
def detalhe(num_caso: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    {num_caso} na URL é um "path parameter" — o valor vira o parâmetro num_caso.
    Ex: GET /casos/123 → num_caso = 123
    """
    caso = db.query(Caso).filter(Caso.TbCasoNumCaso == num_caso).first()
    if not caso:
        # HTTP 404 = recurso não encontrado
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    return caso


# ── POST /casos ───────────────────────────────────────────────────────────────
# status_code=201 → HTTP 201 Created (padrão para criação bem-sucedida)
@router.post("/", response_model=CasoOut, status_code=201)
def criar(
    data: CasoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),  # exige nível ≥ 2 (operador ou admin)
):
    """
    Corpo da requisição é validado automaticamente por CasoCreate.
    Se a validação falhar, FastAPI retorna HTTP 422 com detalhes do erro.
    Erros de negócio (ValueError do service) viram HTTP 400.
    """
    try:
        return criar_caso(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── PUT /casos/{num_caso} ─────────────────────────────────────────────────────
@router.put("/{num_caso}", response_model=CasoOut)
def atualizar(
    num_caso: int,
    data: CasoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    Atualiza campos do caso — incluindo encerramento.
    O service decide se é uma edição simples ou um encerramento com efeitos colaterais.
    """
    try:
        return atualizar_caso(db, num_caso, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── PUT /casos/{num_caso}/restaurar ──────────────────────────────────────────
@router.put("/{num_caso}/restaurar", response_model=CasoOut)
def restaurar(
    num_caso: int,
    data: CasoRestaura,  # recebe o motivo de restauração no corpo
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """Reabre um caso encerrado, limpando campos de encerramento."""
    try:
        return restaurar_caso(db, num_caso, data.motivo_restauracao)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
