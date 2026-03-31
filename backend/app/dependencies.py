# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCIES.PY — Injeção de dependências do FastAPI
# ─────────────────────────────────────────────────────────────────────────────
# "Dependências" no FastAPI são funções reutilizáveis que podem ser injetadas
# nos endpoints com o parâmetro Depends().
#
# Por exemplo, em vez de cada endpoint abrir e fechar a sessão do banco
# manualmente, todos usam:
#   db: Session = Depends(get_db)
# ...e o FastAPI cuida do resto automaticamente.
#
# Este arquivo define três dependências principais:
#   1. get_db           → abre/fecha uma sessão de banco por requisição
#   2. get_current_user → valida o token JWT e retorna o técnico logado
#   3. require_nivel    → verifica se o técnico tem nível mínimo de acesso

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decode_token
from app.core.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# OAUTH2 SCHEME — extrai o token JWT do cabeçalho da requisição
# ─────────────────────────────────────────────────────────────────────────────
# OAuth2PasswordBearer instrui o FastAPI a procurar um token Bearer no
# cabeçalho HTTP "Authorization: Bearer <token>".
#
# tokenUrl="/auth/login" → URL onde o token pode ser obtido (usado no Swagger UI).
# auto_error=not settings.DEV_MODE → em modo dev, não lança erro se não tiver token
#   (permite testar a API sem autenticação).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=not settings.DEV_MODE)


# ─────────────────────────────────────────────────────────────────────────────
# DEPENDÊNCIA 1: get_db — sessão de banco por requisição
# ─────────────────────────────────────────────────────────────────────────────
def get_db():
    """
    Abre uma sessão de banco de dados e a fecha ao final da requisição.

    A palavra-chave "yield" transforma esta função em um "context manager":
    - Tudo antes do yield roda ANTES do endpoint (setup).
    - O yield "entrega" o db para o endpoint usar.
    - Tudo depois do yield (o finally) roda DEPOIS do endpoint (teardown).

    O bloco try/finally garante que db.close() seja chamado mesmo se o
    endpoint levantar uma exceção — evitando conexões abertas acumuladas.
    """
    db = SessionLocal()   # abre a sessão
    try:
        yield db          # entrega para o endpoint usar
    finally:
        db.close()        # fecha sempre, independente de erro


# ─────────────────────────────────────────────────────────────────────────────
# DEPENDÊNCIA 2: get_current_user — autentica o técnico via JWT
# ─────────────────────────────────────────────────────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Valida o token JWT da requisição e retorna o objeto Tecnico correspondente.

    Fluxo:
      1. oauth2_scheme extrai o token do cabeçalho Authorization
      2. Em modo DEV sem token → retorna o primeiro técnico admin disponível
      3. decode_token() valida a assinatura e expiration do JWT
      4. O payload["sub"] contém o CodTecnico (ID do técnico)
      5. Busca o técnico no banco e o retorna

    Se qualquer etapa falhar, lança HTTP 401 Unauthorized.
    """
    # Importação local para evitar import circular entre dependências e models
    from app.models.tecnico import Tecnico

    if settings.DEV_MODE and not token:
        # Em desenvolvimento, se não tiver token, usa o primeiro admin disponível.
        # Isso permite testar endpoints protegidos sem fazer login.
        user = db.query(Tecnico).filter(Tecnico.TbNivel >= 3).first() or db.query(Tecnico).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nenhum usuário encontrado no banco para o modo Dev",
            )
        return user

    # Valida o token JWT
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    # Extrai o ID do técnico do payload ("sub" = subject = identificador)
    cod = payload.get("sub")

    # Busca o técnico no banco pelo ID
    user = db.query(Tecnico).filter(Tecnico.CodTecnico == cod).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return user


# ─────────────────────────────────────────────────────────────────────────────
# DEPENDÊNCIA 3: require_nivel — controle de acesso por nível
# ─────────────────────────────────────────────────────────────────────────────
def require_nivel(nivel_minimo: int = 2):
    """
    Fábrica de dependências que exige um nível mínimo de acesso.

    Por que é uma "fábrica" (função que retorna função)?
    → Porque precisamos passar um parâmetro (nivel_minimo) para a dependência.
      No FastAPI, Depends() não aceita parâmetros diretamente, então usamos
      este padrão: require_nivel(2) retorna a função checker, que é a dependência real.

    Níveis do sistema:
      1 → usuário comum (somente leitura)
      2 → operador (pode criar e editar registros)
      3 → administrador (acesso total)

    Exemplo de uso em um endpoint:
      @router.post("/casos")
      def criar(data: CasoCreate, _=Depends(require_nivel(2))):
          ...
    """
    def checker(current_user=Depends(get_current_user)):
        # TbNivel pode ser None no banco — usa 1 como padrão (menor nível)
        if (current_user.TbNivel or 1) < nivel_minimo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado",
            )
        return current_user
    return checker
