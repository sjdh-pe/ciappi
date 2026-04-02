# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Ouvidoria — consultas e controle de prazos da Ouvidoria da SJDH
# ─────────────────────────────────────────────────────────────────────────────
# Casos que chegam via "OUvidoria da SJDH" têm prazo formal de resposta.
# Este router reproduz as consultas do Access (queries "Cn...") para
# monitorar e encerrar esses prazos.
#
# Endpoints disponíveis:
#   GET /ouvidoria/avencer           → casos com prazo futuro
#   GET /ouvidoria/vencidas          → casos com prazo já ultrapassado
#   GET /ouvidoria/ambiente          → todos os casos ativos da Ouvidoria SJDH
#   GET /ouvidoria/concluidas        → casos com ouvidoria encerrada
#   PUT /ouvidoria/{id}/encerrar     → encerra manualmente a ouvidoria de um caso

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional
from app.dependencies import get_db, get_current_user, require_nivel
from app.models.caso import Caso
from app.schemas.caso import CasoOut

router = APIRouter(prefix="/ouvidoria", tags=["Ouvidoria"])

# Constante: valor exato que identifica casos da Ouvidoria da SJDH no banco.
# Note o "U" maiúsculo em "OUvidoria" — é assim que está armazenado no Access.
ORIGEM_OUVIDORIA = "OUvidoria da SJDH"


def _base_aberta(db: Session):
    """
    Função auxiliar (privada) que retorna a query base para casos de ouvidoria
    que ainda estão abertos (prazo definido e ouvidoria não encerrada).

    Por que extrair em função separada?
    → DRY (Don't Repeat Yourself): /avencer e /vencidas usam a mesma base.
      Sem isso, teríamos o mesmo filtro duplicado em dois lugares.

    .filter() pode ser encadeado — cada .filter() adiciona um AND no SQL.
    .is_(None) gera IS NULL no SQL.
    Condição com | (pipe) → OR no SQLAlchemy.
    """
    return (
        db.query(Caso)
        .filter(Caso.TbPrazoOuvidoria.isnot(None))   # deve ter prazo definido
        .filter(
            (Caso.TbEncerradoOuvidoria.is_(None)) |   # ouvidoria sem status OU
            (Caso.TbEncerradoOuvidoria != "Sim")       # não encerrada
        )
    )


# ── GET /ouvidoria/avencer ────────────────────────────────────────────────────
@router.get("/avencer", response_model=list[CasoOut])
def casos_a_vencer(
    # dias é opcional: se informado, filtra casos que vencem nos próximos N dias
    dias: Optional[int] = Query(None, description="Prazo vence nos próximos N dias"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Casos com prazo de ouvidoria AINDA NÃO VENCIDO.
    Reproduz a query CnPrazoOuvidoriaAVencer do Access.

    datetime.combine(data, datetime.min.time()) converte um date para datetime
    com hora 00:00:00 — necessário porque TbPrazoOuvidoria é DateTime no banco.
    """
    hoje = date.today()
    q = _base_aberta(db).filter(
        Caso.TbPrazoOuvidoria >= datetime.combine(hoje, datetime.min.time())
    )
    if dias is not None:
        # Adiciona filtro de janela de tempo: prazo ≤ hoje + N dias
        limite = datetime.combine(hoje + timedelta(days=dias), datetime.min.time())
        q = q.filter(Caso.TbPrazoOuvidoria <= limite)

    return q.order_by(Caso.TbPrazoOuvidoria).all()


# ── GET /ouvidoria/vencidas ───────────────────────────────────────────────────
@router.get("/vencidas", response_model=list[CasoOut])
def casos_vencidos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Casos com prazo de ouvidoria JÁ VENCIDO e ainda em aberto.
    Reproduz CnPrazoOuvidoriaVencido do Access.
    Atenção máxima: esses casos precisam de ação imediata.
    """
    hoje = date.today()
    return (
        _base_aberta(db)
        .filter(Caso.TbPrazoOuvidoria < datetime.combine(hoje, datetime.min.time()))
        .order_by(Caso.TbPrazoOuvidoria)  # mais antigos primeiro (mais urgentes)
        .all()
    )


# ── GET /ouvidoria/ambiente ───────────────────────────────────────────────────
@router.get("/ambiente", response_model=list[CasoOut])
def casos_ouvidoria_sjdh(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Todos os casos ativos que chegaram via Ouvidoria da SJDH, após set/2019.
    Reproduz o formulário Frmambiente do Access.
    O corte em 30/09/2019 coincide com a implantação do módulo de ouvidoria.
    """
    corte = datetime(2019, 9, 30)
    return (
        db.query(Caso)
        .filter(Caso.TbCasoChegouPrograma == ORIGEM_OUVIDORIA)
        .filter(Caso.TbCasoDtinicio > corte)
        .filter(Caso.TbCasoDtencer.is_(None))  # só casos ainda abertos
        .order_by(Caso.TbCasoDtinicio)
        .all()
    )


# ── GET /ouvidoria/concluidas ─────────────────────────────────────────────────
@router.get("/concluidas", response_model=list[CasoOut])
def casos_concluidos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    """
    Ouvidorias já encerradas, ordenadas da mais recente para a mais antiga.
    Reproduz CnOuvidoriaConcluidas do Access.
    """
    return (
        db.query(Caso)
        .filter(Caso.TbEncerradoOuvidoria == "Sim")
        .order_by(Caso.TbDtEncerradoOuvidoria.desc())
        .all()
    )


# ── PUT /ouvidoria/{num_caso}/encerrar ────────────────────────────────────────
@router.put("/{num_caso}/encerrar", response_model=CasoOut)
def encerrar_ouvidoria(
    num_caso: int,
    # Query(...) → parâmetro obrigatório de URL: /ouvidoria/123/encerrar?num_oficio=OF-001
    # O ... (Ellipsis) indica que o campo é obrigatório (sem default)
    num_oficio: str = Query(..., description="Número do ofício de encerramento"),
    db: Session = Depends(get_db),
    _=Depends(require_nivel(2)),
):
    """
    Encerra manualmente a ouvidoria de um caso registrando o número do ofício.

    Validações:
      - Caso deve existir
      - Ouvidoria não pode já estar encerrada (evita duplicar)
      - Caso deve ter prazo de ouvidoria definido (não é caso de ouvidoria)
    """
    caso = db.query(Caso).filter(Caso.TbCasoNumCaso == num_caso).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    if caso.TbEncerradoOuvidoria == "Sim":
        raise HTTPException(status_code=400, detail="Ouvidoria deste caso já foi encerrada")
    if not caso.TbPrazoOuvidoria:
        raise HTTPException(status_code=400, detail="Este caso não possui prazo de ouvidoria")

    caso.TbEncerradoOuvidoria = "Sim"
    caso.TbDtEncerradoOuvidoria = datetime.now()
    caso.TbNumOfOuvidoria = num_oficio

    db.commit()
    db.refresh(caso)
    return caso
