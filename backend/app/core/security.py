# ─────────────────────────────────────────────────────────────────────────────
# SECURITY.PY — Funções de segurança: senhas e tokens JWT
# ─────────────────────────────────────────────────────────────────────────────
# Este arquivo centraliza tudo que tem a ver com autenticação:
#   1. Hash de senha (bcrypt)
#   2. Criação de token JWT
#   3. Decodificação e validação de token JWT

from datetime import datetime, timedelta
from jose import JWTError, jwt          # biblioteca para criar/ler tokens JWT
from passlib.context import CryptContext  # biblioteca para hash de senhas
from app.core.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXTO DE HASH DE SENHAS
# ─────────────────────────────────────────────────────────────────────────────
# O CryptContext configura qual algoritmo usar para hash de senhas.
# "bcrypt" é considerado muito seguro: é lento propositalmente para dificultar
# ataques de força bruta.
# deprecated="auto" significa: se existirem senhas com algoritmos mais antigos,
# elas ainda funcionam mas são automaticamente marcadas para atualização.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se uma senha em texto plano corresponde ao hash armazenado.

    Internamente, o bcrypt aplica a mesma função de hash na senha recebida
    e compara com o hash salvo no banco — nunca compara texto com texto.

    Nota: neste projeto, as senhas do Access original são texto plano,
    então este método é usado apenas para senhas bcrypt quando houver.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Converte uma senha em texto plano para um hash bcrypt.
    Use esta função ao cadastrar ou alterar senhas antes de salvar no banco.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """
    Cria um token JWT assinado com a SECRET_KEY do projeto.

    O que é JWT?
    → JWT (JSON Web Token) é uma string codificada que carrega informações
      (claims) e é assinada digitalmente. Quem tem a SECRET_KEY pode verificar
      se o token é legítimo e lê seu conteúdo.

    Fluxo:
      1. Usuário faz login → recebe um JWT
      2. Nas próximas requisições, envia o JWT no cabeçalho Authorization
      3. A API valida o JWT e sabe quem é o usuário sem consultar o banco

    Parâmetros:
      data → dict com informações a incluir no token.
               Aqui usamos {"sub": str(tecnico.CodTecnico)} onde "sub" (subject)
               é o identificador do usuário logado.

    O campo "exp" (expiration) é adicionado automaticamente baseado em
    ACCESS_TOKEN_EXPIRE_MINUTES (padrão: 480 min = 8 horas).
    """
    to_encode = data.copy()  # copia para não modificar o dict original
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # jwt.encode() serializa o dict para JSON e assina com a chave secreta
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    Decodifica e valida um token JWT.

    → Se o token for válido e não estiver expirado, retorna o payload (dict).
    → Se o token for inválido, adulterado ou expirado, retorna None.

    O bloco try/except captura JWTError que o python-jose levanta em qualquer
    problema de validação (assinatura errada, token expirado, formato inválido).
    Retornamos None em vez de lançar exceção — quem chama decide o que fazer.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
