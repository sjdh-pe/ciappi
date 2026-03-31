# ─────────────────────────────────────────────────────────────────────────────
# SERVICE: Auth — lógica de autenticação
# ─────────────────────────────────────────────────────────────────────────────
# A camada de Services contém a lógica de negócio da aplicação.
# Ela fica entre os Routers (que recebem requests HTTP) e os Models (que
# acessam o banco), mantendo cada camada com responsabilidade única:
#
#   Router  → "como a requisição HTTP chega e sai"
#   Service → "o que fazer com os dados" (regras de negócio)
#   Model   → "como os dados ficam no banco"
#
# Separar em services torna o código testável: você pode testar a lógica
# sem precisar subir um servidor web completo.

from sqlalchemy.orm import Session
from app.models.tecnico import Tecnico
from app.core.security import create_access_token


def autenticar(db: Session, nome: str, senha: str) -> dict | None:
    """
    Valida as credenciais do técnico e retorna os dados do token.

    Parâmetros:
      db   → sessão de banco (injetada pelo FastAPI via Depends)
      nome → nome do técnico (campo TbNomeTecnico)
      senha → senha em texto plano (legado do Access original)

    Retorna:
      dict com access_token, nivel e nome → em caso de sucesso
      None → se nome/senha não conferem

    Lança:
      PermissionError → se o técnico estiver com status "bloqueado"

    NOTA SOBRE SEGURANÇA:
    A comparação é feita em texto plano porque o banco Access original
    armazenava senhas assim. Em novos cadastros, o ideal é usar bcrypt
    (ver get_password_hash em security.py).
    """
    # Consulta o banco procurando um técnico com exatamente este nome E esta senha.
    # .first() retorna o primeiro resultado ou None se não encontrar.
    tecnico = (
        db.query(Tecnico)
        .filter(Tecnico.TbNomeTecnico == nome)
        .filter(Tecnico.TbSenha == senha)
        .first()
    )

    # Se não achou, credenciais inválidas
    if not tecnico:
        return None

    # Verifica se o técnico está bloqueado
    # .strip().lower() garante que "Bloqueado ", "BLOQUEADO" etc. também são detectados
    if tecnico.TbStatus and tecnico.TbStatus.strip().lower() == "bloqueado":
        raise PermissionError("Usuário bloqueado. Procure a Coordenação.")

    # Cria o token JWT com o ID do técnico como "subject" (sub)
    # O router vai retornar este token para o cliente armazenar
    token = create_access_token({"sub": str(tecnico.CodTecnico)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "nivel": tecnico.TbNivel or 1,  # se TbNivel for None, assume nível 1 (mais restrito)
        "nome": tecnico.TbNomeTecnico,
    }
