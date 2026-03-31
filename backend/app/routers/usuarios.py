# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Usuários — CRUD das pessoas atendidas pelo programa
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints disponíveis:
#   GET  /usuarios               → lista com paginação e busca por nome
#   GET  /usuarios/{id}          → detalhe de um usuário
#   POST /usuarios               → cadastra novo usuário (nível ≥ 2)
#   PUT  /usuarios/{id}          → atualiza dados (nível ≥ 2)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.dependencies import get_db, get_current_user, require_nivel
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioOut
from app.services.usuario_service import criar_usuario, atualizar_usuario, buscar_por_nome

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


# ── GET /usuarios ─────────────────────────────────────────────────────────────
@router.get("/", response_model=list[UsuarioOut])
def listar(
    nome: Optional[str] = Query(None),
    # ge=0 → "greater or equal 0" — validação do Query: não aceita skip negativo
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    # ge=1, le=500 → entre 1 e 500 registros por página
    limit: int = Query(50, ge=1, le=500, description="Máximo de registros por página"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Lista usuários com paginação. Use skip/limit para navegar nas páginas.
    Se 'nome' for informado, faz busca por nome (ignora skip/limit).
    """
    if nome:
        # Se buscou por nome, usa o service de busca (retorna todos os que combinam)
        return buscar_por_nome(db, nome)
    # Sem filtro → paginação padrão
    return db.query(Usuario).offset(skip).limit(limit).all()


# ── GET /usuarios/{num_cadastro} ──────────────────────────────────────────────
@router.get("/{num_cadastro}", response_model=UsuarioOut)
def detalhe(num_cadastro: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    u = db.query(Usuario).filter(Usuario.tbnumerocadastro == num_cadastro).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u


# ── POST /usuarios ────────────────────────────────────────────────────────────
@router.post("/", response_model=UsuarioOut, status_code=201)
def criar(data: UsuarioCreate, db: Session = Depends(get_db), _=Depends(require_nivel(2))):
    """
    data.model_dump() converte o schema Pydantic em dict Python antes de
    passar para o service, que espera um dict (usa **kwargs internamente).
    """
    try:
        return criar_usuario(db, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── PUT /usuarios/{num_cadastro} ──────────────────────────────────────────────
@router.put("/{num_cadastro}", response_model=UsuarioOut)
def atualizar(
    num_cadastro: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    model_dump(exclude_unset=True) → só converte para dict os campos
    que foram realmente enviados na requisição. Campos com default None
    que não vieram no JSON são excluídos — evita apagar dados existentes.
    """
    try:
        return atualizar_usuario(db, num_cadastro, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
