# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Acompanhamentos — endpoints para histórico de atendimentos
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints disponíveis:
#   GET  /acompanhamentos/caso/{num_caso} → histórico de um caso
#   GET  /acompanhamentos/{id}            → detalhe de um acompanhamento
#   POST /acompanhamentos                 → registra novo atendimento (nível ≥ 2)
#   PUT  /acompanhamentos/{id}            → atualiza acompanhamento (nível ≥ 2)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_nivel
from app.schemas.acompanhamento import AcompanhamentoCreate, AcompanhamentoUpdate, AcompanhamentoOut
from app.services.acomp_service import criar_acompanhamento, atualizar_acompanhamento, listar_por_caso
from app.models.acompanhamento import Acompanhamento

router = APIRouter(prefix="/acompanhamentos", tags=["Acompanhamentos"])


# ── GET /acompanhamentos/caso/{num_caso} ──────────────────────────────────────
@router.get("/caso/{num_caso}", response_model=list[AcompanhamentoOut])
def listar(num_caso: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Retorna todos os acompanhamentos de um caso, do mais recente ao mais antigo.
    Esta rota usa /caso/{num_caso} no prefixo para diferenciar da rota
    GET /acompanhamentos/{id} que busca por ID de acompanhamento.

    IMPORTANTE: a ordem das rotas importa no FastAPI!
    /caso/{num_caso} precisa estar definida ANTES de /{codigo} para que
    a URL /caso/123 não seja interpretada como acompanhamento de código "caso".
    """
    return listar_por_caso(db, num_caso)


# ── GET /acompanhamentos/{codigo} ─────────────────────────────────────────────
@router.get("/{codigo}", response_model=AcompanhamentoOut)
def detalhe(codigo: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    a = db.query(Acompanhamento).filter(Acompanhamento.tbcodigo == codigo).first()
    if not a:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    return a


# ── POST /acompanhamentos ─────────────────────────────────────────────────────
@router.post("/", response_model=AcompanhamentoOut, status_code=201)
def criar(
    data: AcompanhamentoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    Cria novo acompanhamento. O service valida:
      - Caso existe
      - Prazo não está no passado
      - Encaminhamento tem órgão
      - Se ação = "Concluída para Ouvidoria" → encerra ouvidoria automaticamente
    """
    try:
        return criar_acompanhamento(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── PUT /acompanhamentos/{codigo} ─────────────────────────────────────────────
@router.put("/{codigo}", response_model=AcompanhamentoOut)
def atualizar(
    codigo: int,
    data: AcompanhamentoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    try:
        return atualizar_acompanhamento(db, codigo, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
