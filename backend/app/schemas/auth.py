# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA: Auth — modelos de dados para autenticação
# ─────────────────────────────────────────────────────────────────────────────
# Schemas são classes Pydantic que definem a estrutura dos dados que ENTRAM
# e SAEM da API. São diferentes dos Models (SQLAlchemy), que mapeiam o banco.
#
# Analogia: Model = "como os dados vivem no banco"
#           Schema = "como os dados viajam pela API (request/response)"
#
# O Pydantic valida automaticamente os dados: se o frontend mandar um campo
# errado ou faltando, a API retorna um erro 422 descritivo sem você precisar
# escrever nenhuma validação manual.

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    Dados que o frontend envia no corpo do POST /auth/login.

    Exemplo de JSON enviado:
    {
        "nome": "ANA SILVA",
        "senha": "minha_senha123"
    }
    """
    nome: str   # nome do técnico (deve bater com TbNomeTecnico no banco)
    senha: str  # senha em texto plano (legado do Access)


class Token(BaseModel):
    """
    Resposta retornada após login bem-sucedido.

    O frontend deve salvar o access_token e enviá-lo nas próximas
    requisições no cabeçalho:  Authorization: Bearer <access_token>

    Exemplo de resposta JSON:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
        "token_type": "bearer",
        "nivel": 2,
        "nome": "ANA SILVA"
    }
    """
    access_token: str           # o token JWT assinado
    token_type: str = "bearer"  # tipo do token — sempre "bearer" (padrão OAuth2)
    nivel: int                  # nível de acesso: 1, 2 ou 3
    nome: str                   # nome do técnico logado (para exibir na interface)
