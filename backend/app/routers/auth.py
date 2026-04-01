# ─────────────────────────────────────────────────────────────────────────────
# ROUTER: Auth — endpoints de autenticação
# ─────────────────────────────────────────────────────────────────────────────
# Um "router" no FastAPI é como um mini-app que agrupa endpoints relacionados.
# Ele é criado com APIRouter() e depois registrado no app principal (main.py)
# com app.include_router().
#
# Por que usar routers em vez de colocar tudo em main.py?
# → Organização: cada assunto (auth, casos, usuários...) tem seu próprio arquivo.
# → Reusabilidade: um router pode ser incluído em múltiplos apps.
# → Testabilidade: você pode testar um router isoladamente.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # ← NOVO
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.auth import Token  # ← removido LoginRequest (não precisamos mais)
from app.services.auth_service import autenticar

# ── Criação do router ─────────────────────────────────────────────────────────
# prefix="/auth"  → todos os endpoints deste router começam com /auth
#                    Ex: /auth/login
# tags=["Autenticação"] → agrupamento no Swagger UI (docs em /docs)
router = APIRouter(prefix="/auth", tags=["Autenticação"])


# ── POST /auth/login ──────────────────────────────────────────────────────────
# @router.post() registra esta função como handler do método POST em /auth/login.
# response_model=Token → define a estrutura da resposta (validada e serializada
#                         automaticamente pelo Pydantic).
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # ← substituiu LoginRequest
    db: Session = Depends(get_db)
):
    """
    Autentica um técnico e retorna um token JWT.

    Parâmetros (injetados automaticamente pelo FastAPI):
      payload → corpo da requisição, validado pelo schema LoginRequest
      db      → sessão de banco, injetada por Depends(get_db)

    Fluxo:
      1. FastAPI deserializa o JSON do corpo em LoginRequest
      2. Chama autenticar() para verificar credenciais
      3. Se bloqueado → 403 Forbidden
      4. Se credenciais erradas → 401 Unauthorized
      5. Se OK → retorna o Token (access_token + nível + nome)
    """

    try:
        # form_data.username → nome do técnico
        # form_data.password → senha
        resultado = autenticar(db, form_data.username, form_data.password)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome do Técnico e Senha não conferem",
        )
        # FastAPI serializa automaticamente o dict retornado usando o schema Token
    return resultado

    #
    # try:
    #     resultado = autenticar(db, payload.nome, payload.senha)
    # except PermissionError as e:
    #     # Técnico encontrado mas bloqueado → HTTP 403 (proibido, mas autenticado)
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    #
    # if not resultado:
    #     # Credenciais incorretas → HTTP 401 (não autorizado)
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Nome do Técnico e Senha não conferem",
    #     )
    #
    #
    # return resultado
